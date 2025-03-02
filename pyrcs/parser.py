"""
Parses web-page contents.
"""

import calendar
import collections
import copy
import os
import re
import urllib.parse

import bs4
import dateutil.parser
import pandas as pd
import requests
from pyhelpers._cache import _print_failure_message
from pyhelpers.ops import confirmed, fake_requests_headers, update_dict_keys
from pyhelpers.store import load_data, save_data
from pyhelpers.text import find_similar_str

from .utils import cd_data, home_page_url, print_conn_err, print_inst_conn_err


# == Preprocess contents ===========================================================================


def _parse_other_tags_in_td_contents(x):
    if isinstance(x, str):
        td_text = x.strip(' ')

    else:
        tag_name, td_text = x.name, x.text

        if tag_name == 'em':
            td_text = f'[{td_text}]'

        elif tag_name == 'q':
            td_text = f'"{td_text}"'

        elif tag_name in {'span', 'a'}:
            td_class, td_class_child = x.get('class'), x.find('span')

            if td_class == ['r']:
                if td_text == 'no CRS?':
                    td_text = f'\t\t / [{td_text}]'
                elif '\n ' in td_text:
                    td_text = ' '.join(
                        [f'\t\t{y}' if y.startswith('(') and y.endswith(')') else f' / [{y}]'
                         for y in td_text.split('\n ')])
                elif '(' not in td_text and ')' not in td_text:
                    td_text = f'\t\t / [{td_text}]'
                else:
                    td_text = f'\t\t{td_text}'

            elif not td_class and td_class_child:
                td_text = f'\t\t{td_text}'

    return td_text


def _move_element_to_end(text_, char='\t\t'):
    for i, x in enumerate(text_):
        if char in x:
            text_.append(text_.pop(i))
            # break


def _prep_records(trs, ths, sep=' / '):
    ths_len = len(ths)

    records = []
    row_spanned = []

    for no, tr in enumerate(trs):
        data = []
        tds = tr.find_all(name='td')

        if len(tds) != ths_len:
            tds = tds[:ths_len]

        for td_no, td in enumerate(tds):
            if td.find('td'):
                text_ = td.find('a').contents + ["\t\t / "]
            else:
                text_ = [_parse_other_tags_in_td_contents(x) for x in td.contents]
            # _move_element_to_end(text_, char='\t\t')
            text = ' '.join(sorted([x for x in text_ if x.strip(' ')], key=lambda x: '\t\t' in x))

            if sep:
                old_sep = re.compile(r'/?\r?\n')
                if len(re.findall(old_sep, text)) > 0:
                    text = re.sub(r'/?\r?\n', sep, text)

            if td.has_attr('rowspan'):
                row_spanned.append((no, int(td['rowspan']), td_no, text))

            data.append(text)

        records.append(data)

    return records, row_spanned


def _check_row_spanned(records, row_spanned):
    if row_spanned:
        records_ = records.copy()

        row_spanned_dict = collections.defaultdict(list)
        for i, *to_repeat in row_spanned:
            row_spanned_dict[i].append(to_repeat)

        for i, to_repeat in row_spanned_dict.items():
            for no_spans, idx, dat in to_repeat:
                for j in range(1, no_spans):
                    k = i + j
                    # if (dat in records[i]) and (dat != '\xa0'):  # and (idx < len(records[i]) - 1):
                    #     idx += np.abs(records[i].index(dat) - idx, dtype='int64')
                    k_len = len(records_[k])
                    if k_len < len(records_[i]):
                        if k_len == idx:
                            records_[k].insert(idx, dat)
                        elif k_len > idx:
                            if records_[k][idx] != '':
                                records_[k].insert(idx, dat)
                            else:  # records[k][idx] == '':
                                records_[k][idx] = dat

    else:
        records_ = records

    return records_


def parse_tr(trs, ths, sep=' / ', as_dataframe=False):
    # noinspection PyUnresolvedReferences
    """
    Parses a list of HTML ``<tr>`` elements and extracts data from a table.

    This function processes the rows from a table (``<tr>`` tags) and assigns them to corresponding
    column headers (``<th>`` tags). It can return the data either as a list of lists or as a
    dataframe.

    See also [`PT-1 <https://stackoverflow.com/questions/28763891/>`_].

    :param trs: The content of ``<tr>`` tags from a web page table.
    :type trs: bs4.ResultSet | list
    :param ths: A list of column names (typically from ``<th>`` tags) for the table.
    :type ths: list | bs4.element.Tag
    :param sep: The separator to replace any separators found in the raw data;
        defaults to ``' / '``.
    :type sep: str | None
    :param as_dataframe: If ``True``, returns the data as a Pandas DataFrame; defaults to ``False``.
    :type as_dataframe: bool
    :return: A list of lists representing rows of the table,
        or a dataframe if ``as_dataframe`` is ``True``.
    :rtype: pandas.DataFrame | list[list]

    **Examples**::

        >>> from pyrcs.parser import parse_tr
        >>> import requests
        >>> import bs4
        >>> example_url = 'http://www.railwaycodes.org.uk/elrs/elra.shtm'
        >>> source = requests.get(example_url)
        >>> parsed_text = bs4.BeautifulSoup(source.content, 'html.parser')
        >>> ths_dat = [th.text for th in parsed_text.find_all('th')]
        >>> trs_dat = parsed_text.find_all(name='tr')
        >>> tables_list = parse_tr(trs=trs_dat, ths=ths_dat)  # returns a list of lists
        >>> type(tables_list)
        list
        >>> len(tables_list) // 100
        1
        >>> tables_list[0]
        ['AAL',
         'Ashendon and Aynho Line',
         '0.00 - 18.29',
         'Ashendon Junction',
         'Now NAJ3']
    """

    records, row_spanned = _prep_records(trs=trs, ths=ths, sep=sep)

    records = _check_row_spanned(records, row_spanned)

    if isinstance(ths, bs4.Tag):
        column_names = [th.get_text(strip=True) for th in ths.find_all('th')]
    elif all(isinstance(x, bs4.Tag) for x in ths):
        column_names = [th.get_text(strip=True) for th in ths]
    else:
        column_names = copy.copy(ths)

    n_columns = len(column_names)
    empty_rows = []

    for k, record in enumerate(records):
        n = n_columns - len(record)
        if n == n_columns:
            empty_rows.append(k)
        elif n > 0:
            record.extend(['\xa0'] * n)
        elif n < 0 and record[2] == '\xa0':
            del record[2]

    if len(empty_rows) > 0:
        for k in empty_rows:
            del records[k]

    if as_dataframe:
        records = pd.DataFrame(data=records, columns=column_names)

    return records


def parse_table(source, parser='html.parser', as_dataframe=False):
    """
    Parses HTML ``<tr>`` elements to create a table from the given source.

    This function extracts data from the ``<thead>`` and ``<tbody>`` elements of an HTML table
    and processes it into a list of lists (rows of the table) or a dataframe.

    :param source: The response object containing the HTML table from a requested URL.
    :type source: requests.Response
    :param parser: The parser to use for processing the HTML;
        options are ``'html.parser'`` (default), ``'html5lib'`` or ``'lxml'``.
    :type parser: str
    :param as_dataframe: If ``True``, the parsed data is returned as a dataframe.
        If ``False``, it returns a list of lists and column names; defaults to ``False``.
    :type as_dataframe: bool
    :return: A tuple containing a list of column names and a list of lists representing
        rows of the table; if ``as_dataframe=True``, returns a dataframe.
    :rtype: tuple[list, list] | pandas.DataFrame | list

    **Examples**::

        >>> from pyrcs.parser import parse_table
        >>> import requests
        >>> source_dat = requests.get(url='http://www.railwaycodes.org.uk/elrs/elra.shtm')
        >>> columns_dat, records_dat = parse_table(source_dat)
        >>> columns_dat
        ['ELR', 'Line name', 'Mileages', 'Datum', 'Notes']
        >>> type(records_dat)
        list
        >>> len(records_dat) // 100
        1
        >>> records_dat[0]
        ['AAL',
         'Ashendon and Aynho Line',
         '0.00 - 18.29',
         'Ashendon Junction',
         'Now NAJ3']
    """

    soup = bs4.BeautifulSoup(markup=source.content, features=parser)

    theads, tbodies = soup.find_all(name='thead'), soup.find_all(name='tbody')

    tables = []
    for thead, tbody in zip(theads, tbodies):
        ths = [th.get_text(strip=True) for th in thead.find_all(name='th')]
        trs = tbody.find_all(name='tr')

        if as_dataframe:
            dat = parse_tr(trs=trs, ths=ths, as_dataframe=as_dataframe)
        else:
            dat = ths, parse_tr(trs=trs, ths=ths)

        tables.append(dat)

    if len(tables) == 1:
        tables = tables[0]

    return tables, soup


def parse_date(str_date, as_date_type=False):
    """
    Parses a string representation of a date into a formatted date.

    This function attempts to parse a string date (even with slight errors or non-standard formats)
    into either a string in the "YYYY-MM-DD" format or a `datetime.date`_ object.

    .. _`datetime.date`: https://docs.python.org/3/library/datetime.html#datetime.date

    :param str_date: The date as a string, whose format can vary and may include month names
        or other elements.
    :type str_date: str
    :param as_date_type: If ``True``, returns the result as a `datetime.date` object;
        if ``False`` (default), returns the result as a formatted string.
    :type as_date_type: bool
    :return: The parsed date either as a string in "YYYY-MM-DD" format or as a date object.
    :rtype: str | datetime.date

    **Examples**::

        >>> from pyrcs.parser import parse_date
        >>> str_date_dat = '2020-01-01'
        >>> parse_date(str_date_dat)
        '2020-01-01'
        >>> str_date_dat = '2020-jan-01'
        >>> parse_date(str_date_dat)
        '2020-01-01'
        >>> parse_date(str_date_dat, as_date_type=True)
        datetime.date(2020, 1, 1)
    """

    try:
        temp_date = dateutil.parser.parse(timestr=str_date, fuzzy=True)
        # or, temp_date = datetime.datetime.strptime(str_date[12:], '%d %B %Y')
    except (TypeError, calendar.IllegalMonthError):
        month_name = find_similar_str(x=str_date, lookup_list=calendar.month_name)
        err_month_ = find_similar_str(x=month_name, lookup_list=str_date.split(' '))
        temp_date = dateutil.parser.parse(
            timestr=str_date.replace(err_month_, month_name), fuzzy=True)

    parsed_date = temp_date.date() if as_date_type else str(temp_date.date())

    return parsed_date


# == Extract information ===========================================================================


def _parse_dd_or_dt(dd_or_dt):
    """
    Extracts text and href attributes from dt or dd elements.
    """

    dd_or_dt_contents = dd_or_dt.contents

    if len(dd_or_dt_contents) == 1:
        content = dd_or_dt_contents[0]
        if isinstance(content, str):
            text, href = content, None
        else:
            text = content.get_text(strip=True)
            href = content.get(key='href') if content.name == 'a' else None

    # Case 2: Two elements (text with a hyperlink reference)
    else:
        a_href, text = dd_or_dt_contents
        if not isinstance(text, str):
            text, a_href = dd_or_dt_contents
        # if re.search(r'\((.*?)\)', text) and text[1].islower():
        #     text = f'{text[1].upper()}{text[2:-1]}'
        href = a_href.find('a').get('href')

    return text.replace("–", "-"), href


def _get_site_map_h3_dl_dt_dds(h3_dl_dt, next_dd=None):
    if next_dd is None:
        next_dd = h3_dl_dt.find_next('dd')

    prev_dt = next_dd.find_previous(name='dt')

    h3_dl_dt_dds = {}
    while prev_dt == h3_dl_dt:
        next_dd_sub_dl_ = next_dd.find('dl')

        if next_dd_sub_dl_ is None:
            next_dd_contents = [x for x in next_dd.contents if x != '\n']

            if len(next_dd_contents) == 1:
                next_dd_content = next_dd_contents[0]
                text = next_dd_content.get_text(strip=True)
                href = next_dd_content.get(key='href')

            else:  # len(next_dd_contents) == 2:
                a_href, text = next_dd_contents
                if not isinstance(text, str):
                    text, a_href = next_dd_contents

                href = a_href.find(name='a').get(key='href')

            h3_dl_dt_dds.update(
                {text.replace("–", "-"): urllib.parse.urljoin(home_page_url(), href)})

        else:
            sub_dts = next_dd_sub_dl_.find_all(name='dt')

            for sub_dt in sub_dts:
                sub_dt_text, _ = _parse_dd_or_dt(sub_dt)
                sub_dt_dds = sub_dt.find_next_siblings(name='dd')
                sub_dt_dds_dict = _get_site_map_sub_dl(h3_dl_dts=sub_dt_dds)

                h3_dl_dt_dds.update({sub_dt_text.replace("–", "-"): sub_dt_dds_dict})

        try:
            next_dd = next_dd.find_next_sibling(name='dd')
            prev_dt = next_dd.find_previous_sibling(name='dt')
        except AttributeError:
            break

    return h3_dl_dt_dds


def _get_site_map_sub_dl(h3_dl_dts):
    """
    Recursively processes nested dl/dt/dd elements to build a structured dictionary.
    """

    h3_dl_dt_dd_dict = {}

    for h3_dl_dt in h3_dl_dts:
        dt_text, dt_href = _parse_dd_or_dt(dd_or_dt=h3_dl_dt)

        if dt_href:
            h3_dl_dt_dd_dict.update({dt_text: urllib.parse.urljoin(home_page_url(), dt_href)})

        else:
            next_dd = h3_dl_dt.find_next('dd')
            next_dd_sub_dl = next_dd.find(name='dd')

            if next_dd_sub_dl:
                # next_dd_sub_dl_dts = next_dd_sub_dl.find_all(name='dt')
                next_dd_sub_dl_dts = [
                    dt for dt in next_dd.find_all(name='dt') if dt.has_attr('class')]
                h3_dl_dt_dd_dict.update({dt_text: _get_site_map_sub_dl(next_dd_sub_dl_dts)})

            else:
                h3_dl_dt_dds = _get_site_map_h3_dl_dt_dds(h3_dl_dt=h3_dl_dt, next_dd=next_dd)
                h3_dl_dt_dd_dict.update({dt_text: h3_dl_dt_dds})

    return h3_dl_dt_dd_dict


def _get_site_map(source, parser='html.parser'):
    """
    Parses the site map from the given HTML source and returns a structured dictionary.
    """

    soup = bs4.BeautifulSoup(markup=source.content, features=parser)
    site_map = {}

    h3s = soup.find_all(name='h3', attrs={"class": "site"})

    for h3 in h3s:
        h3_title = h3.get_text(strip=True)
        h3_dl_dts = h3.find_next(name='dl').find_all(name='dt')  # h3 > dl > dt

        if len(h3_dl_dts) == 1:
            dd_dict = {}  # h3 > dl > dt > dd

            h3_dl_dt = h3_dl_dts[0]
            h3_dl_dt_text = h3_dl_dt.get_text(strip=True)

            if h3_dl_dt_text == '':
                for dd in h3_dl_dt.find_next_siblings('dd'):
                    text, href = _parse_dd_or_dt(dd)
                    dd_dict.update({text: urllib.parse.urljoin(home_page_url(), href)})

        else:
            dd_dict = _get_site_map_sub_dl(h3_dl_dts=h3_dl_dts)

        site_map.update({h3_title: dd_dict})

    # noinspection SpellCheckingInspection
    site_map = update_dict_keys(
        site_map, replacements={"(all ogher languages)": "(all other languages)"})

    return site_map


def get_site_map(update=False, confirmation_required=True, verbose=False, raise_error=True):
    # noinspection PyShadowingNames
    """
    Gets the `site map <http://www.railwaycodes.org.uk/misc/sitemap.shtm>`_.

    :param update: Whether to check for updates to the package data; defaults to ``False``.
    :type update: bool
    :param confirmation_required: Whether user confirmation is required before proceeding;
        defaults to ``True``.
    :type confirmation_required: bool
    :param verbose: Whether to print relevant information to the console; defaults to ``False``.
    :type verbose: bool | int
    :param raise_error: Whether to raise the provided exception;
        if ``raise_error=False``, the error will be suppressed; defaults to ``True``.
    :type raise_error: bool
    :return: An ordered dictionary containing the data of site map.
    :rtype: collections.OrderedDict | None

    **Examples**::

        >>> from pyrcs.parser import get_site_map
        >>> site_map = get_site_map()
        >>> type(site_map)
        collections.OrderedDict
        >>> list(site_map.keys())
        ['Home',
         'Line data',
         'Other assets',
         '"Legal/financial" lists',
         'Miscellaneous']
        >>> site_map['Home']
        {'index.shtml': 'http://www.railwaycodes.org.uk/index.shtml'}
    """

    path_to_file = cd_data("site-map.json", mkdir=True)

    if os.path.isfile(path_to_file) and not update:
        return load_data(path_to_file, object_pairs_hook=dict)

    else:
        if confirmed("To collect the site map\n?", confirmation_required=confirmation_required):
            if verbose in {True, 1}:
                print("Updating the package data", end=" ... ")

            try:
                url = urllib.parse.urljoin(home_page_url(), '/misc/sitemap.shtm')
                source = requests.get(url=url, headers=fake_requests_headers())

            except requests.exceptions.ConnectionError:
                print_inst_conn_err(update=update, verbose=True if update else verbose)
                return None

            try:
                site_map = _get_site_map(source=source)

                if verbose in {True, 1}:
                    print("Done.")

                if site_map:
                    save_data(site_map, path_to_file, indent=4, verbose=(verbose == 2 or False))

                return site_map

            except Exception as e:
                _print_failure_message(
                    e, prefix="Failed. Error:", verbose=verbose, raise_error=raise_error)
        else:
            if verbose in {True, 1}:
                print("Cancelled. ")
            # site_map = load_data(path_to_file)


def _get_last_updated_date(soup, parsed=True, as_date_type=False):
    # Find 'Last update date'
    update_tag = soup.find(name='p', attrs={'class': 'update'})

    if update_tag is not None:
        last_updated_date = update_tag.get_text(strip=True)
        # Decide whether to convert the date's format
        if parsed:
            # Convert the date to "yyyy-mm-dd" format
            last_updated_date = parse_date(str_date=last_updated_date, as_date_type=as_date_type)

    else:
        last_updated_date = None

    return last_updated_date


def get_last_updated_date(url, parsed=True, as_date_type=False, verbose=False):
    # noinspection PyShadowingNames
    """
    Gets the last update date of a specified web page.

    This function extracts the date when the given web page was last updated.
    The date can be returned as a string or a date object.

    :param url: The URL of the web page for which the last update date is requested.
    :type url: str
    :param parsed: Whether to reformat the date into a standardized format (``YYYY-MM-DD``);
        defaults to ``True``.
    :type parsed: bool
    :param as_date_type: If ``True``, the date is returned as a `datetime.date`_ object;
        if ``False`` (default), it's returned as a string.
    :type as_date_type: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
    :return: The last update date of the specified web page,
        or ``None`` if this information is not available on the web page.
    :rtype: str | datetime.date | None

    .. _`datetime.date`: https://docs.python.org/3/library/datetime.html#datetime.date

    **Examples**::

        >>> from pyrcs.parser import get_last_updated_date
        >>> url = 'http://www.railwaycodes.org.uk/crs/CRSa.shtm'
        >>> last_upd_date = get_last_updated_date(url=url, parsed=True, as_date_type=False)
        >>> type(last_upd_date)
        str
        >>> last_upd_date = get_last_updated_date(url=url, parsed=True, as_date_type=True)
        >>> type(last_upd_date)
        datetime.date
        >>> url = 'http://www.railwaycodes.org.uk/linedatamenu.shtm'
        >>> last_upd_date = get_last_updated_date(url=url, verbose=True)
        Information of the last update date not available.
    """

    try:  # Request to get connected to the given url
        source = requests.get(url=url, headers=fake_requests_headers())

    except requests.exceptions.ConnectionError:
        print_conn_err(verbose=verbose)

    else:
        # Parse the text scraped from the requested web page
        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

        last_updated_date = _get_last_updated_date(
            soup=soup, parsed=parsed, as_date_type=as_date_type)

        if last_updated_date is None and verbose:
            print('Information of the last update date not available.')

        return last_updated_date


def get_financial_year(date):
    """
    Gets the financial year of a given date.

    The financial year runs from 1st April to 31st March of the following year.
    This function takes a date and determines the financial year it falls into.

    :param date: The date for which the financial year is to be determined.
    :type date: datetime.datetime
    :return: The financial year of the given ``date``.
    :rtype: int

    **Examples**::

        >>> from pyrcs.parser import get_financial_year
        >>> import datetime
        >>> financial_year = get_financial_year(date=datetime.datetime(2021, 3, 31))
        >>> financial_year
        2020
    """

    financial_date = date + pd.DateOffset(months=-3)

    return financial_date.year


def _parse_introduction(source, delimiter='\n'):
    soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

    intro_h3 = [h3 for h3 in soup.find_all('h3') if h3.get_text(strip=True).startswith('Intro')][0]

    p = intro_h3.find_next(name='p')
    prev_h3, prev_h4 = p.find_previous(name='h3'), p.find_previous(name='h4')

    intro_paras = []
    while prev_h3 == intro_h3 and prev_h4 is None:
        para_text = p.text.replace('  ', ' ')
        intro_paras.append(para_text)

        p = p.find_next(name='p')
        prev_h3, prev_h4 = p.find_previous(name='h3'), p.find_previous(name='h4')

    introduction = delimiter.join(intro_paras)

    return introduction


def get_introduction(url, delimiter='\n', update=False, verbose=True, raise_error=False):
    """
    Gets the introduction section of a specified web page.

    This function scrapes the introduction text from the given URL, typically used to
    summarise data clusters.

    :param url: The URL of the web page (usually the main page of a data cluster).
    :type url: str
    :param delimiter: The delimiter used to separate paragraphs in the returned content;
        defaults to ``'\\n'`` (newline).
    :type delimiter: str
    :param update: Whether to check for updates to the package data; defaults to ``False``.
    :type update: bool
    :param verbose: Whether to print relevant information to the console; defaults to ``True``.
    :type verbose: bool | int
    :param raise_error: Whether to raise the provided exception;
        if ``raise_error=False`` (default), the error will be suppressed.
    :type raise_error: bool
    :return: The introductory text from the web page, formatted with the specified delimiter.
    :rtype: str

    **Examples**::

        >>> from pyrcs.parser import get_introduction
        >>> bridges_url = 'http://www.railwaycodes.org.uk/bridges/bridges0.shtm'
        >>> intro_text = get_introduction(url=bridges_url)
        >>> intro_text
        "There are thousands of bridges over and under the railway system. These pages attempt to...
    """

    intro_filename = '-'.join(x for x in urllib.parse.urlparse(url).path.replace(
        '.shtm', '.pkl').split('/') if x)
    path_to_file = cd_data("introduction", intro_filename, mkdir=True)

    if os.path.isfile(path_to_file) and not update:
        return load_data(path_to_file)

    try:
        source = requests.get(url=url, headers=fake_requests_headers())
    except requests.exceptions.ConnectionError:
        print_conn_err(verbose=verbose)
        return None

    try:
        introduction = _parse_introduction(source=source, delimiter=delimiter)

        if introduction:
            save_data(introduction, path_to_file=path_to_file, verbose=verbose)

        return introduction

    except Exception as e:
        _print_failure_message(e=e, prefix="Failed.", verbose=verbose, raise_error=raise_error)


def _parse_catalogue(source, url):
    """
    Extracts a catalogue of links from the provided ``BeautifulSoup4`` object.

    :param source: HTML content.
    :param url: Base (page) URL to resolve relative links.
    :return: Typically, a dictionary mapping link text to absolute URLs.
    """

    soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

    # Try to find the primary container, fallback to alternative
    cold_soup = soup.find(name='div', attrs={'class': 'fixed'}) or soup.find(name='h1')

    # Extract anchor tags (if fallback is used, get all following <a> tags)
    links = cold_soup.find_all('a') if cold_soup else []

    if len(links) > 0:
        catalogue = {
            a.text.replace('\xa0', ' ').strip(): urllib.parse.urljoin(url, a.get('href'))
            for a in links}
    else:
        catalogue = None

    return catalogue


def get_catalogue(url, update=False, json_it=True, verbose=False, raise_error=False):
    """
    Gets the catalogue of items from the main page of a data cluster.

    This function scrapes a catalogue of entries (typically hyperlinks) from a specified URL.
    It offers the option to save the catalogue as a JSON file.

    :param url: The URL of the main page of a data cluster.
    :type url: str
    :param update: Whether to check for updates to the package data; defaults to ``False``.
    :type update: bool
    :param json_it: Whether to save the catalogue as a JSON file; defaults to ``True``.
    :type json_it: bool
    :param verbose: Whether to print relevant information to the console; defaults to ``False``.
    :type verbose: bool | int
    :param raise_error: Whether to raise the provided exception;
        if ``raise_error=False`` (default), the error will be suppressed.
    :type raise_error: bool
    :return: The catalogue in the form of a dictionary, where keys are entry titles and
        values are URLs, or ``None`` if the operation is unsuccessful.
    :rtype: dict | None

    **Examples**::

        >>> from pyrcs.parser import get_catalogue
        >>> elr_cat = get_catalogue(url='http://www.railwaycodes.org.uk/elrs/elr0.shtm')
        >>> type(elr_cat)
        dict
        >>> list(elr_cat.keys())[:5]
        ['Introduction', 'A', 'B', 'C', 'D']
        >>> list(elr_cat.keys())[-5:]
        ['Lines without codes',
         'ELR/LOR converter',
         'LUL system',
         'DLR system',
         'Canals']
        >>> location_code_cat = get_catalogue(url='http://www.railwaycodes.org.uk/crs/crs0.shtm')
        >>> type(location_code_cat)
        dict
        >>> list(location_code_cat.keys())[:5]
        ['Introduction', 'A', 'B', 'C', 'D']
        >>> list(location_code_cat.keys())[-5:]
        ['W', 'X', 'Y', 'Z', 'Other systems']
    """

    cat_filename = '-'.join(x for x in urllib.parse.urlparse(url).path.replace(
        '.shtm', '.json').split('/') if x)
    path_to_file = cd_data("catalogue", cat_filename, mkdir=True)

    if os.path.isfile(path_to_file) and not update:
        return load_data(path_to_file)

    try:
        source = requests.get(url=url, headers=fake_requests_headers())
        source.raise_for_status()
    except Exception as e:
        print_inst_conn_err(verbose=verbose, e=e)
        return None

    try:
        catalogue = _parse_catalogue(source=source, url=url)

        if catalogue and json_it:
            save_data(catalogue, path_to_file=path_to_file, verbose=verbose, indent=4)

        return catalogue

    except Exception as e:
        _print_failure_message(e=e, prefix="Failed.", verbose=verbose, raise_error=raise_error)
        # print("The catalogue for the requested data has not been acquired.")


def get_category_menu(name, update=False, confirmation_required=True, verbose=False,
                      raise_error=False):
    """
    Gets a menu of the available classes from the specified URL.

    This function scrapes a web page for available classes (typically categorised hyperlinks) and
    returns them as a dictionary. It also provides options to update the catalogue and
    save it as a JSON file.

    :param name: The name of the data category.
    :type name: str
    :param update: Whether to check for updates to the package data; defaults to ``False``.
    :type update: bool
    :param confirmation_required: Whether user confirmation is required before proceeding;
        defaults to ``True``.
    :type confirmation_required: bool
    :param verbose: Whether to print relevant information to the console; defaults to ``False``.
    :type verbose: bool | int
    :param raise_error: Whether to raise the provided exception;
        if ``raise_error=False`` (default), the error will be suppressed.
    :type raise_error: bool
    :return: A category menu in dictionary form,
        where keys are data cluster names and values are URLs.
    :rtype: dict | None

    **Examples**::

        >>> from pyrcs.parser import get_category_menu
        >>> menu = get_category_menu(name='Line data')
        >>> type(menu)
        dict
        >>> list(menu.keys())
        ['Line data']
        >>> len(menu['Line data'])
        7
    """

    path_to_menu_json = cd_data(
        "catalogue", f"{name.lower().replace(' ', '-')}-menu.json", mkdir=True)

    if os.path.isfile(path_to_menu_json) and not update:
        return load_data(path_to_menu_json)

    if confirmed("To collect/update category menu?", confirmation_required=confirmation_required):
        try:
            source = requests.get(url=home_page_url(), headers=fake_requests_headers())
        except requests.exceptions.ConnectionError:
            print_conn_err(verbose=verbose)
            return None

        try:
            soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

            drop_btn_ = soup.select(f'button:-soup-contains("{name}")')
            drop_btn = drop_btn_[0]

            a_href_list = drop_btn.find_next_sibling('div').find_all('a')

            cls_menu_ = [
                (a.get_text(), urllib.parse.urljoin(home_page_url(), a['href']))
                for a in a_href_list]

            cls_menu = {name: dict(cls_menu_)}

            save_data(cls_menu, path_to_menu_json, indent=4, verbose=(verbose == 2 or False))

            return cls_menu

        except Exception as e:
            _print_failure_message(
                e, prefix="Failed. Error:", verbose=verbose, raise_error=raise_error)

    else:
        print("The category menu has not been acquired.")


def get_heading_text(heading_tag, elem_tag_name='em'):
    """
    Gets the text from a given HTML heading tag.

    :param heading_tag: The HTML tag of a heading element.
    :type heading_tag: bs4.element.Tag
    :param elem_tag_name: The tag name of an inner element within the heading; defaults to ``'em'``.
    :type elem_tag_name: str
    :return: Cleaned text of the heading tag.
    :rtype: str

    **Examples**::

        >>> from pyrcs.parser import get_heading_text
        >>> from pyrcs.line_data import Electrification
        >>> elec = Electrification()
        >>> url = elec.catalogue[elec.KEY_TO_INDEPENDENT_LINES]
        >>> source = requests.get(url=url, headers=fake_requests_headers())
        >>> soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')
        >>> h3 = soup.find('h3')
        >>> h3_text = get_heading_text(heading_tag=h3, elem_tag_name='em')
        >>> h3_text
        'Beamish Tramway'
    """

    heading_x = []

    for elem in heading_tag.contents:
        # noinspection PyUnresolvedReferences
        if elem.name == elem_tag_name:
            heading_x.append('[' + elem.text + ']')
        else:
            heading_x.append(elem.text)

    heading_text = ''.join(heading_x)

    return heading_text


def get_page_catalogue(url, head_tag_name='nav', head_tag_txt='Jump to: ', feature_tag_name='h3',
                       verbose=False, raise_error=False):
    """
    Gets the catalogue of features from the main page of a data cluster.

    This function extracts structured data (features) from a web page by parsing specific tags,
    typically used for features like headings and links in railway-related databases.

    :param url: The URL of the main page of a data cluster.
    :type url: str
    :param head_tag_name: The tag name of the feature list at the top of the page;
        defaults to ``'nav'``.
    :type head_tag_name: str
    :param head_tag_txt: Text contained in the head tag; defaults to ``'Jump to: '``.
    :type head_tag_txt: str
    :param feature_tag_name: The tag name of the headings of each feature; defaults to ``'h3'``.
    :type feature_tag_name: str
    :param verbose: Whether to print relevant information to the console; defaults to ``False``.
    :type verbose: bool | int
    :param raise_error: Whether to raise the provided exception;
        if ``raise_error=False`` (default), the error will be suppressed.
    :type raise_error: bool
    :return: A dataframe containing the page's feature catalogue with columns for feature, URL and
        heading.
    :rtype: pandas.DataFrame

    **Examples**::

        >>> from pyrcs.parser import get_page_catalogue
        >>> from pyhelpers.settings import pd_preferences
        >>> pd_preferences(max_columns=1)
        >>> elec_url = 'http://www.railwaycodes.org.uk/electrification/mast_prefix2.shtm'
        >>> elec_catalogue = get_page_catalogue(elec_url)
        >>> elec_catalogue
                                                      Feature  ...
        0                                     Beamish Tramway  ...
        1                                  Birkenhead Tramway  ...
        2                         Black Country Living Museum  ...
        3                                   Blackpool Tramway  ...
        4   Brighton and Rottingdean Seashore Electric Rai...  ...
        ..                                                ...  ...
        17                                     Seaton Tramway  ...
        18                                Sheffield Supertram  ...
        19                          Snaefell Mountain Railway  ...
        20  Summerlee, Museum of Scottish Industrial Life ...  ...
        21                                  Tyne & Wear Metro  ...
        [22 rows x 3 columns]
        >>> elec_catalogue.columns.to_list()
        ['Feature', 'URL', 'Heading']
    """

    try:
        source = requests.get(url=url, headers=fake_requests_headers())

    except requests.exceptions.ConnectionError:
        print_inst_conn_err(verbose=verbose)
        return None

    try:
        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

        page_catalogue = pd.DataFrame({'Feature': [], 'URL': [], 'Heading': []})

        for nav in soup.find_all(head_tag_name):
            nav_text = nav.text.replace('\r\n', '').strip()

            if re.match(r'^({})'.format(head_tag_txt), nav_text):
                feature_names = nav_text.replace(head_tag_txt, '').split('\xa0| ')
                page_catalogue['Feature'] = feature_names

                feature_urls = []
                for item_name in feature_names:
                    text_pat = re.compile(r'.*{}.*'.format(item_name), re.IGNORECASE)
                    a = nav.find('a', string=text_pat)

                    feature_urls.append(urllib.parse.urljoin(url, a.get('href')))

                page_catalogue['URL'] = feature_urls

        feature_headings = []
        for h3 in soup.find_all(feature_tag_name):
            sub_heading = get_heading_text(heading_tag=h3, elem_tag_name='em')
            feature_headings.append(sub_heading)

        page_catalogue['Heading'] = feature_headings

        return page_catalogue

    except Exception as e:
        _print_failure_message(e, verbose=verbose, raise_error=raise_error)


def get_hypertext(hypertext_tag, hyperlink_tag_name='a', md_style=True):
    """
    Gets hyperlinked text from a specified HTML tag.

    This function scrapes hypertext content, optionally returning it in Markdown format if
    requested.

    :param hypertext_tag: The tag containing hyperlinked text.
    :type hypertext_tag: bs4.element.Tag | bs4.element.PageElement
    :param hyperlink_tag_name: The tag name of the hyperlink within the hypertext;
        defaults to ``'a'``.
    :type hyperlink_tag_name: str
    :param md_style: Whether to return the hypertext in Markdown style, defaults to ``True``.
    :type md_style: bool
    :return: The hypertext.
    :rtype: str

    **Examples**::

        >>> from pyrcs.parser import get_hypertext
        >>> from pyrcs.line_data import Electrification
        >>> import bs4
        >>> import requests
        >>> elec = Electrification()
        >>> url = elec.catalogue[elec.KEY_TO_INDEPENDENT_LINES]
        >>> source = requests.get(url)
        >>> soup = bs4.BeautifulSoup(source.content, 'html.parser')
        >>> h3 = soup.find('h3')
        >>> p = h3.find_all_next('p')[8]
        >>> p
        <p>Croydon Tramlink mast references can be found on the <a href="http://www.croydon-traml...
        >>> hyper_txt = get_hypertext(hypertext_tag=p, md_style=True)
        >>> hyper_txt
        'Croydon Tramlink mast references can be found on the [Croydon Tramlink Unofficial Site](...
    """

    hypertext_x = []

    for x in hypertext_tag.contents:
        # noinspection PyUnresolvedReferences
        if x.name == hyperlink_tag_name:
            # noinspection PyUnresolvedReferences
            href = x.get('href')

            if md_style:
                x_text = '[' + x.text + ']' + f'({href})'
            else:
                x_text = x.text + f' ({href})'
            hypertext_x.append(x_text)

        else:
            hypertext_x.append(x.text)

    hypertext_tag = ''.join(hypertext_x).replace('\xa0', '').replace('  ', ' ')

    return hypertext_tag
