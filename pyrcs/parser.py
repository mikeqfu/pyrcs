"""Parse web-page contents."""

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
from pyhelpers.ops import confirmed, fake_requests_headers
from pyhelpers.store import load_data, save_data
from pyhelpers.text import find_similar_str

from .utils import cd_data, format_err_msg, home_page_url, print_conn_err, print_inst_conn_err


# == Preprocess contents ===========================================================================


def _parse_other_tags_in_td_contents(td_content):
    if not isinstance(td_content, str):
        td_text = td_content.get_text()

        if td_content.name == 'em':
            td_text = f'[{td_text}]'
        elif td_content.name == 'q':
            td_text = f'"{td_text}"'

    else:
        td_text = td_content

    return td_text


def parse_tr(trs, ths, as_dataframe=False):
    """
    Parse a list of parsed HTML <tr> elements.

    See also [`PT-1 <https://stackoverflow.com/questions/28763891/>`_].

    :param trs: contents under ``<tr>`` tags of a web page
    :type trs: bs4.ResultSet
    :param ths: list of column names (usually under a ``<th>`` tag) of a requested table
    :type ths: list or bs4.element.Tag
    :param as_dataframe: whether to return the parsed data in tabular form
    :type as_dataframe: bool
    :return: a list of lists that each comprises a row of the requested table
    :rtype: pandas.DataFrame or typing.List[list]

    **Example**::

        >>> from pyrcs.parser import parse_tr
        >>> import requests
        >>> import bs4

        >>> example_url = 'http://www.railwaycodes.org.uk/elrs/elra.shtm'
        >>> source = requests.get(example_url)
        >>> parsed_text = bs4.BeautifulSoup(markup=source.content, features='html.parser')
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

    ths_len = len(ths)
    records = []
    row_spanned = []

    for no, tr in enumerate(trs):
        data = []
        tds = tr.find_all(name='td')

        if len(tds) != ths_len:
            tds = tds[:ths_len]

        for td_no, td in enumerate(tds):
            text = ''.join([_parse_other_tags_in_td_contents(x) for x in td.contents])
            # if '/\r\n' in text or '\r\n' in text:
            #     txt = text.replace('/\r\n', ' / ').replace('\r\n', ' / ')
            # elif '\n' in text:
            #     txt_ = text.split('\n')
            #     txt0, txt1 = txt_[0], ''.join(txt_[1:])
            #     if all(re.match(r'(\w+ )+\[.*]', x) for x in {txt0, txt1}):
            #         txt = '; '.join(txt_)  # new_separator.join(txt_)
            #     else:
            #         txt = ('{} ({})' if not set(text) & {'(', ')'} else '{} {}').format(txt0, txt1)
            old_sep, new_sep = re.compile(r'/?\r?\n'), ' / '
            if len(re.findall(old_sep, text)) > 0:
                txt = re.sub(r'/?\r?\n', new_sep, text)
            else:
                txt = text

            if td.has_attr('rowspan'):
                row_spanned.append((no, int(td['rowspan']), td_no, txt))

            data.append(txt)

        records.append(data)

    if row_spanned:
        row_spanned_dict = collections.defaultdict(list)
        for i, *to_repeat in row_spanned:
            row_spanned_dict[i].append(to_repeat)

        for i, to_repeat in row_spanned_dict.items():
            for no_spans, idx, dat in to_repeat:
                for j in range(1, no_spans):
                    k = i + j
                    # if (dat in records[i]) and (dat != '\xa0'):  # and (idx < len(records[i]) - 1):
                    #     idx += np.abs(records[i].index(dat) - idx, dtype='int64')
                    k_len = len(records[k])
                    if k_len < len(records[i]):
                        if k_len == idx:
                            records[k].insert(idx, dat)
                        elif k_len > idx:
                            if records[k][idx] != '':
                                records[k].insert(idx, dat)
                            else:  # records[k][idx] == '':
                                records[k][idx] = dat

    # if row_spanned:
    #     for x in row_spanned:
    #         for j in range(1, x[2]):
    #             # Add value in next tr
    #             idx = x[0] + j
    #             # assert isinstance(idx, int)
    #             if x[1] >= len(tbl_lst[idx]):
    #                 tbl_lst[idx].insert(x[1], x[3])
    #             elif x[3] in tbl_lst[x[0]]:
    #                 tbl_lst[idx].insert(tbl_lst[x[0]].index(x[3]), x[3])
    #             else:
    #                 tbl_lst[idx].insert(x[1] + 1, x[3])

    if isinstance(ths, bs4.element.Tag):
        column_names = [th.text.strip() for th in ths.find_all('th')]
    elif all(isinstance(x, bs4.element.Tag) for x in ths):
        column_names = [th.text.strip() for th in ths]
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
    Parse HTML <tr> elements for creating a data frame.

    :param source: response object to connecting a URL to request a table
    :type source: requests.Response
    :param parser: ``'html.parser'`` (default), ``'html5lib'`` or ``'lxml'``
    :type parser: str
    :param as_dataframe: whether to return the parsed data in tabular form
    :type as_dataframe: bool
    :return: a list of lists each comprising a row of the requested table
        (see also :py:func:`pyrcs.utils.parse_tr`) and a list of column names of the requested table
    :rtype: tuple[list, list] or pandas.DataFrame or list

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
        ths = [th.text.strip() for th in thead.find_all(name='th')]
        trs = tbody.find_all(name='tr')

        if as_dataframe:
            dat = parse_tr(trs=trs, ths=ths, as_dataframe=as_dataframe)
        else:
            dat = ths, parse_tr(trs=trs, ths=ths)

        tables.append(dat)

    if len(tables) == 1:
        tables = tables[0]

    return tables


def parse_date(str_date, as_date_type=False):
    """
    Parse a date.

    :param str_date: string-type date
    :type str_date: str
    :param as_date_type: whether to return the date as `datetime.date`_, defaults to ``False``
    :type as_date_type: bool
    :return: parsed date as a string or `datetime.date`_
    :rtype: str or datetime.date

    .. _`datetime.date`: https://docs.python.org/3/library/datetime.html#datetime.date

    **Examples**::

        >>> from pyrcs.parser import parse_date

        >>> str_date_dat = '2020-01-01'

        >>> parsed_date_dat = parse_date(str_date_dat)
        >>> parsed_date_dat
        '2020-01-01'

        >>> parsed_date_dat = parse_date(str_date_dat, as_date_type=True)
        >>> parsed_date_dat
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


def parse_location_name(location_name):
    """
    Parse location name (and its associated note).

    :param location_name: location name (in raw data)
    :type location_name: str or None
    :return: location name and note (if any)
    :rtype: tuple

    **Examples**::

        >>> from pyrcs.parser import parse_location_name

        >>> dat_and_note = parse_location_name('Abbey Wood')
        >>> dat_and_note
        ('Abbey Wood', '')

        >>> dat_and_note = parse_location_name(None)
        >>> dat_and_note
        ('', '')

        >>> dat_and_note = parse_location_name('Abercynon (formerly Abercynon South)')
        >>> dat_and_note
        ('Abercynon', 'formerly Abercynon South')

        >>> location_dat = 'Allerton (reopened as Liverpool South Parkway)'
        >>> dat_and_note = parse_location_name(location_dat)
        >>> dat_and_note
        ('Allerton', 'reopened as Liverpool South Parkway')

        >>> location_dat = 'Ashford International [domestic portion]'
        >>> dat_and_note = parse_location_name(location_dat)
        >>> dat_and_note
        ('Ashford International', 'domestic portion')
    """

    if location_name is None:
        dat, note = '', ''

    else:
        # Location name
        d = re.search(r'.*(?= \[[\"\']\()', location_name)
        if d is not None:
            dat = d.group()
        elif ' [unknown feature, labelled "do not use"]' in location_name:
            dat = re.search(r'\w+(?= \[unknown feature, )', location_name).group()
        elif ') [formerly' in location_name:
            dat = re.search(r'.*(?= \[formerly)', location_name).group()
        else:
            m_pattern = re.compile(
                r'[Oo]riginally |'
                r'[Ff]ormerly |'
                r'[Ll]ater |'
                r'[Pp]resumed |'
                r' \(was |'
                r' \(in |'
                r' \(at |'
                r' \(also |'
                r' \(second code |'
                r'\?|'
                r'\n|'
                r' \(\[\'|'
                r' \(definition unknown\)|'
                r' \(reopened |'
                r'( portion])$')
            x_tmp = re.search(r'(?=[\[(]).*(?<=[])])|(?=\().*(?<=\) \[)', location_name)
            x_tmp = x_tmp.group() if x_tmp is not None else location_name
            if re.search(m_pattern, location_name):
                dat = ' '.join(location_name.replace(x_tmp, '').split())
            else:
                dat = location_name

        # Note
        y = location_name.replace(dat, '', 1).strip()
        if y == '':
            note = ''
        else:
            n = re.search(r'(?<=[\[(])[\w ,?]+(?=[])])', y)
            if n is None:
                n = re.search(
                    r'(?<=(\[[\'\"]\()|(\([\'\"]\[)|(\) \[)).*'
                    r'(?=(\)[\'\"]])|(][\'\"]\))|])', y)
            elif '"now deleted"' in y and y.startswith('(') and y.endswith(')'):
                n = re.search(r'(?<=\().*(?=\))', y)
            note = n.group() if n is not None else ''
            if note.endswith('\'') or note.endswith('"'):
                note = note[:-1]

        if 'STANOX ' in dat and 'STANOX ' in location_name and note == '':
            dat = location_name[0:location_name.find('STANOX')].strip()
            note = location_name[location_name.find('STANOX'):]

    return dat, note


# == Extract information ===========================================================================


def _parse_dd_or_dt_contents(dd_or_dt_contents):
    if len(dd_or_dt_contents) == 1:
        content = dd_or_dt_contents[0]
        if isinstance(content, str):
            text = content
            href = None
        else:
            text = content.get_text(strip=True)
            href = content.get(key='href') if content.name == 'a' else ''

    else:  # len(dd_or_dt_contents) == 2:
        a_href, text = dd_or_dt_contents
        if not isinstance(text, str):
            text, a_href = dd_or_dt_contents

        text = re.search(r'\((.*?)\)', text).group(1)
        text = text[0].capitalize() + text[1:]
        href = a_href.find(name='a').get(key='href')

    return text, href


def _get_site_map_sub_dl(h3_dl_dts):
    h3_dl_dt_dd_dict = {}

    for h3_dl_dt in h3_dl_dts:

        dt_text, dt_href = _parse_dd_or_dt_contents(h3_dl_dt.contents)

        if dt_href is not None:
            dt_link = urllib.parse.urljoin(home_page_url(), dt_href)
            h3_dl_dt_dd_dict.update({dt_text: dt_link})

        else:
            next_dd = h3_dl_dt.find_next('dd')
            prev_dt = next_dd.find_previous(name='dt')
            next_dd_sub_dl = next_dd.findChild(name='dl')

            if next_dd_sub_dl is not None:
                next_dd_sub_dl_dts = next_dd_sub_dl.find_all(name='dt')
                h3_dl_dt_dd_dict = _get_site_map_sub_dl(next_dd_sub_dl_dts)

            else:
                h3_dl_dt_dds = {}
                while prev_dt == h3_dl_dt:
                    next_dd_sub_dl_ = next_dd.findChild('dl')

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

                            text = re.search(r'\((.*?)\)', text).group(1)
                            text = text[0].capitalize() + text[1:]
                            href = a_href.find(name='a').get(key='href')

                        link = urllib.parse.urljoin(home_page_url(), href)
                        h3_dl_dt_dds.update({text: link})

                    else:
                        sub_dts = next_dd_sub_dl_.find_all(name='dt')

                        for sub_dt in sub_dts:
                            sub_dt_text, _ = _parse_dd_or_dt_contents(sub_dt.contents)
                            sub_dt_dds = sub_dt.find_next_siblings(name='dd')
                            sub_dt_dds_dict = _get_site_map_sub_dl(sub_dt_dds)

                            h3_dl_dt_dds.update({sub_dt_text: sub_dt_dds_dict})

                    try:
                        next_dd = next_dd.find_next_sibling(name='dd')
                        prev_dt = next_dd.find_previous_sibling(name='dt')
                    except AttributeError:
                        break

                h3_dl_dt_dd_dict.update({dt_text: h3_dl_dt_dds})

    return h3_dl_dt_dd_dict


def _get_site_map(source):
    soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

    h3s = soup.find_all(name='h3', attrs={"class": "site"})

    site_map = collections.OrderedDict()

    for h3 in h3s:
        h3_title = h3.get_text(strip=True)

        h3_dl = h3.find_next_sibling(name='dl')

        h3_dl_dts = h3_dl.find_all(name='dt')

        if len(h3_dl_dts) == 1:
            h3_dl_dt_dd_dict = {}

            h3_dl_dt = h3_dl_dts[0]
            h3_dl_dt_text = h3_dl_dt.get_text(strip=True)

            if h3_dl_dt_text == '':
                h3_dl_dt_dds = h3_dl_dt.find_next_siblings('dd')

                for h3_dl_dt_dd in h3_dl_dt_dds:
                    text, href = _parse_dd_or_dt_contents(h3_dl_dt_dd.contents)
                    link = urllib.parse.urljoin(home_page_url(), href)
                    h3_dl_dt_dd_dict.update({text: link})

        else:
            h3_dl_dt_dd_dict = _get_site_map_sub_dl(h3_dl_dts)

        site_map.update({h3_title: h3_dl_dt_dd_dict})

    return site_map


def get_site_map(update=False, confirmation_required=True, verbose=False):
    """
    Fetch the `site map <http://www.railwaycodes.org.uk/misc/sitemap.shtm>`_ from the package data.

    :param update: whether to do an update check (for the package data), defaults to ``False``
    :type update: bool
    :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
    :type confirmation_required: bool
    :param verbose: whether to print relevant information in console, defaults to ``False``
    :type verbose: bool or int
    :return: dictionary of site map data
    :rtype: collections.OrderedDict or None

    **Examples**::

        >>> from pyrcs.parser import get_site_map

        >>> site_map_dat = get_site_map()

        >>> type(site_map_dat)
        collections.OrderedDict
        >>> list(site_map_dat.keys())
        ['Home',
         'Line data',
         'Other assets',
         '"Legal/financial" lists',
         'Miscellaneous']
        >>> site_map_dat['Home']
        {'index.shtml': 'http://www.railwaycodes.org.uk/index.shtml'}
    """

    path_to_file = cd_data("site-map.json", mkdir=True)

    if os.path.isfile(path_to_file) and not update:
        # site_map = load_data(path_to_file)
        site_map = load_data(path_to_file, object_pairs_hook=collections.OrderedDict)

    else:
        site_map = None

        if confirmed("To collect the site map\n?", confirmation_required=confirmation_required):

            if verbose == 2:
                print("Updating the package data", end=" ... ")

            try:
                url = urllib.parse.urljoin(home_page_url(), '/misc/sitemap.shtm')
                source = requests.get(url=url, headers=fake_requests_headers())
            except requests.exceptions.ConnectionError:
                print_inst_conn_err(update=update, verbose=True if update else verbose)

            else:
                try:
                    site_map = _get_site_map(source=source)

                    if verbose == 2:
                        print("Done. ")

                    if site_map is not None:
                        save_data(site_map, path_to_file, indent=4, verbose=verbose)

                except Exception as e:
                    print(f"Failed. {format_err_msg(e)}")

        else:
            if verbose == 2:
                print("Cancelled. ")
            # site_map = load_data(path_to_file)

    return site_map


def get_last_updated_date(url, parsed=True, as_date_type=False, verbose=False):
    """
    Get last update date.

    :param url: URL link of a requested web page
    :type url: str
    :param parsed: whether to reformat the date, defaults to ``True``
    :type parsed: bool
    :param as_date_type: whether to return the date as `datetime.date`_, defaults to ``False``
    :type as_date_type: bool
    :param verbose: whether to print relevant information in console, defaults to ``False``
    :type verbose: bool or int
    :return: date of when the specified web page was last updated
    :rtype: str or datetime.date or None

    .. _`datetime.date`: https://docs.python.org/3/library/datetime.html#datetime.date

    **Examples**::

        >>> from pyrcs.parser import get_last_updated_date

        >>> url_a = 'http://www.railwaycodes.org.uk/crs/CRSa.shtm'
        >>> last_upd_date = get_last_updated_date(url_a, parsed=True, as_date_type=False)
        >>> type(last_upd_date)
        str

        >>> last_upd_date = get_last_updated_date(url_a, parsed=True, as_date_type=True)
        >>> type(last_upd_date)
        datetime.date

        >>> ldm_url = 'http://www.railwaycodes.org.uk/linedatamenu.shtm'
        >>> last_upd_date = get_last_updated_date(url=ldm_url)
        >>> print(last_upd_date)
        None
    """

    last_update_date = None

    # Request to get connected to the given url
    try:
        source = requests.get(url=url, headers=fake_requests_headers())
    except requests.exceptions.ConnectionError:
        print_conn_err(verbose=verbose)

    else:
        # Parse the text scraped from the requested web page
        parsed_text = bs4.BeautifulSoup(markup=source.content, features='html.parser')
        # Find 'Last update date'
        update_tag = parsed_text.find(name='p', attrs={'class': 'update'})

        if update_tag is not None:
            last_update_date = update_tag.text

            # Decide whether to convert the date's format
            if parsed:
                # Convert the date to "yyyy-mm-dd" format
                last_update_date = parse_date(str_date=last_update_date, as_date_type=as_date_type)

        # else:
        #     last_update_date = None  # print('Information not available.')

    return last_update_date


def get_financial_year(date):
    """
    Convert calendar year of a given date to Network Rail financial year.

    :param date: date
    :type date: datetime.datetime
    :return: Network Rail financial year of the given ``date``
    :rtype: int

    **Example**::

        >>> from pyrcs.parser import get_financial_year
        >>> import datetime

        >>> financial_year = get_financial_year(date=datetime.datetime(2021, 3, 31))
        >>> financial_year
        2020
    """

    financial_date = date + pd.DateOffset(months=-3)

    return financial_date.year


def _parse_h3_paras(h3):
    p = h3.find_next(name='p')
    prev_h3, prev_h4 = p.find_previous(name='h3'), p.find_previous(name='h4')

    paras = []
    while prev_h3 == h3 and prev_h4 is None:
        para_text = p.text.replace('  ', ' ')
        paras.append(para_text)

        p = p.find_next(name='p')
        prev_h3, prev_h4 = p.find_previous(name='h3'), p.find_previous(name='h4')

    return paras


def get_introduction(url, delimiter='\n', verbose=True):
    """
    Get contents of the Introduction page.

    :param url: URL of a web page (usually the main page of a data cluster)
    :type url: str
    :param delimiter: delimiter used for separating paragraphs, defaults to ``'\\n'``
    :type delimiter: str
    :param verbose: whether to print relevant information in console, defaults to ``True``
    :type verbose: bool or int
    :return: introductory texts on the given web page
    :rtype: str

    **Examples**::

        >>> from pyrcs.parser import get_introduction

        >>> bridges_url = 'http://www.railwaycodes.org.uk/bridges/bridges0.shtm'

        >>> intro_text = get_introduction(url=bridges_url)
        >>> intro_text
        "There are thousands of bridges over and under the railway system. These pages attempt to...
    """

    introduction = None

    try:
        source = requests.get(url=url, headers=fake_requests_headers())
    except requests.exceptions.ConnectionError:
        print_inst_conn_err(verbose=verbose)

    else:
        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

        intro_h3 = [h3 for h3 in soup.find_all('h3') if h3.get_text(strip=True).startswith('Intro')][0]

        intro_paras = _parse_h3_paras(intro_h3)

        introduction = delimiter.join(intro_paras)

    return introduction


def get_catalogue(url, update=False, confirmation_required=True, json_it=True, verbose=False):
    """
    Get the catalogue for a class.

    :param url: URL of the main page of a data cluster
    :type url: str
    :param update: whether to do an update check (for the package data), defaults to ``False``
    :type update: bool
    :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
    :type confirmation_required: bool
    :param json_it: whether to save the catalogue as a JSON file, defaults to ``True``
    :type json_it: bool
    :param verbose: whether to print relevant information in console, defaults to ``False``
    :type verbose: bool or int
    :return: catalogue in the form {'<title>': '<URL>'}
    :rtype: dict or None

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

        >>> line_data_cat = get_catalogue(url='http://www.railwaycodes.org.uk/linedatamenu.shtm')
        >>> type(line_data_cat)
        dict
        >>> list(line_data_cat.keys())
        ['ELRs and mileages',
         'Electrification masts and related features',
         'CRS, NLC, TIPLOC and STANOX Codes',
         'Line of Route (LOR/PRIDE) codes',
         'Line names',
         'Track diagrams']
    """

    cat_json = '-'.join(x for x in urllib.parse.urlparse(url).path.replace(
        '.shtm', '.json').split('/') if x)
    path_to_cat_json = cd_data("catalogue", cat_json, mkdir=True)

    if os.path.isfile(path_to_cat_json) and not update:
        catalogue = load_data(path_to_cat_json)

    else:
        catalogue = None

        if confirmed("To collect/update catalogue?", confirmation_required=confirmation_required):

            try:
                source = requests.get(url=url, headers=fake_requests_headers())
            except requests.exceptions.ConnectionError:
                print_conn_err(verbose=verbose)

            else:
                try:
                    soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

                    try:
                        cold_soup = soup.find(name='div', attrs={'class': 'fixed'})

                        catalogue = {
                            a.text.replace('\xa0', ' ').strip(): urllib.parse.urljoin(url, a.get('href'))
                            for a in cold_soup.find_all('a')}

                    except AttributeError:
                        cold_soup = soup.find(name='h1').find_all_next(name='a')
                        catalogue = {
                            a.text.replace('\xa0', ' ').strip(): urllib.parse.urljoin(url, a.get('href'))
                            for a in cold_soup}

                    if json_it and catalogue is not None:
                        save_data(catalogue, path_to_cat_json, verbose=verbose, indent=4)

                except Exception as e:
                    print("Failed to get the catalogue. {}".format(e))

        else:
            print("The catalogue for the requested data has not been acquired.")

    return catalogue


def get_category_menu(url, update=False, confirmation_required=True, json_it=True, verbose=False):
    """
    Get a menu of the available classes.

    :param url: URL of the menu page
    :type url: str
    :param update: whether to do an update check (for the package data), defaults to ``False``
    :type update: bool
    :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
    :type confirmation_required: bool
    :param json_it: whether to save the catalogue as a .json file, defaults to ``True``
    :type json_it: bool
    :param verbose: whether to print relevant information in console, defaults to ``False``
    :type verbose: bool or int
    :return: a category menu
    :rtype: dict or None

    **Example**::

        >>> from pyrcs.parser import get_category_menu

        >>> menu = get_category_menu('http://www.railwaycodes.org.uk/linedatamenu.shtm')

        >>> type(menu)
        dict
        >>> list(menu.keys())
        ['Line data']
    """

    menu_json = '-'.join(x for x in urllib.parse.urlparse(url).path.replace(
        '.shtm', '.json').split('/') if x)
    path_to_menu_json = cd_data("catalogue", menu_json, mkdir=True)

    if os.path.isfile(path_to_menu_json) and not update:
        cls_menu = load_data(path_to_menu_json)

    else:
        cls_menu = None

        if confirmed("To collect/update category menu?",
                     confirmation_required=confirmation_required):

            try:
                source = requests.get(url=url, headers=fake_requests_headers())
            except requests.exceptions.ConnectionError:
                print_conn_err(verbose=verbose)

            else:
                try:
                    soup = bs4.BeautifulSoup(source.content, 'html.parser')
                    h1, h2s = soup.find('h1'), soup.find_all('h2')

                    cls_name = h1.text.replace(' menu', '')

                    if len(h2s) == 0:
                        cls_elem = dict(
                            (x.text, urllib.parse.urljoin(url, x.get('href')))
                            for x in h1.find_all_next('a'))

                    else:
                        all_next = [
                            x.replace(':', '') for x in h1.find_all_next(string=True)
                            if x != '\n' and x != '\xa0']
                        all_next = all_next[2:]
                        h2s_list = [x.text.replace(':', '') for x in h2s]
                        all_next_a = [
                            (x.text, urllib.parse.urljoin(url, x.get('href')))
                            for x in h1.find_all_next('a', href=True)]

                        idx = [all_next.index(x) for x in h2s_list]
                        for i in idx:
                            all_next_a.insert(i, all_next[i])

                        cls_elem, i = {}, 0
                        while i <= len(idx):
                            if i == 0:
                                d = dict(all_next_a[i:idx[i]])
                            elif i < len(idx):
                                d = {h2s_list[i - 1]: dict(
                                    all_next_a[idx[i - 1] + 1:idx[i]])}
                            else:
                                d = {h2s_list[i - 1]: dict(
                                    all_next_a[idx[i - 1] + 1:])}
                            i += 1
                            cls_elem.update(d)

                    cls_menu = {cls_name: cls_elem}

                    if json_it and cls_menu is not None:
                        save_data(cls_menu, path_to_menu_json, verbose=verbose)

                except Exception as e:
                    print("Failed to get the category menu. {}".format(e))

        else:
            print("The category menu has not been acquired.")

    return cls_menu


def get_heading_text(heading_tag, elem_tag_name='em'):
    """
    Get the text of a given heading tag.

    :param heading_tag: tag of a heading
    :type heading_tag: bs4.element.Tag
    :param elem_tag_name: tag name of an element in the ``heading_tag``, defaults to ``'em'``
    :type elem_tag_name: str
    :return: cleansed text of the given ``heading_tag``
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
        if elem.name == elem_tag_name:
            heading_x.append('[' + elem.text + ']')
        else:
            heading_x.append(elem.text)

    heading_text = ''.join(heading_x)

    return heading_text


def get_page_catalogue(url, head_tag_name='nav', head_tag_txt='Jump to: ', feature_tag_name='h3',
                       verbose=False):
    """
    Get the catalogue of the main page of a data cluster.

    :param url: URL of the main page of a data cluster
    :type url: str
    :param head_tag_name: tag name of the feature list at the top of the page, defaults to ``'nav'``
    :type head_tag_name: str
    :param head_tag_txt: text that is contained in the head_tag, defaults to ``'Jump to: '``
    :type head_tag_txt: str
    :param feature_tag_name: tag name of the headings of each feature, defaults to ``'h3'``
    :type feature_tag_name: str
    :param verbose: whether to print relevant information in console, defaults to ``False``
    :type verbose: bool or int
    :return: catalogue of the main page of a data cluster
    :rtype: pandas.DataFrame

    **Example**::

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

    else:
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


def get_hypertext(hypertext_tag, hyperlink_tag_name='a', md_style=True):
    """
    Get text that is with a hyperlink.

    :param hypertext_tag: tag of hypertext (i.e. text that is with a hyperlink)
    :type hypertext_tag: bs4.element.Tag or bs4.element.PageElement
    :param hyperlink_tag_name:
    :type hyperlink_tag_name: str
    :param md_style: whether to return the obtained hypertext in markdown style, defaults to ``True``
    :type md_style: bool
    :return: hypertext
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
