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

from .utils import cd_data, handle_connection_error, homepage_url


# == Preprocess contents ===========================================================================

def _parse_details_tag(details_tag, sep=' / '):
    """
    Parse a station owner or operator HTML details element into a single string.

    This function extracts the summary and sibling history nodes from a ``<details>``
    HTML tag, formatting emphasis nodes into parenthesised text and joining entries
    with a designated separator.

    :param details_tag: The HTML details element or string fragment.
    :type details_tag: bs4.element.Tag | str
    :param sep: The separator used to join extracted lines; defaults to ``' / '``.
    :type sep: str
    :return: Formatted ownership string joined by the separator.
    :rtype: str

    **Examples**::

        >>> html_str = '''
        ...     <details><summary>Transport for Wales <em>from 28 March 2020</em></summary>
        ...     Network Rail Infrastructure <em>from 3 February 2003 to 27 March 2020</em>
        ...     Railtrack <em>from 1 April 1994 to 2 February 2003</em></details>
        ...     '''
        >>> _parse_details_tag(html_str)
        'Transport for Wales (from 28 March 2020); Network Rail Infrastructure (from 3 February...
    """

    if isinstance(details_tag, str):
        soup = bs4.BeautifulSoup(details_tag, 'html.parser')
        details_tag = soup.find('details')

    if not details_tag:
        return ''

    # Replace all <em> elements with parenthesised text directly in the DOM
    for em in details_tag.find_all('em'):
        em_text = em.get_text(strip=True)
        em.replace_with(f' ({em_text})')

    entries = []

    # Process <summary> as the first entry
    summary = details_tag.find('summary')
    if summary:
        summary_text = re.sub(r'\s+', ' ', summary.get_text()).strip()
        if summary_text:
            entries.append(summary_text)
        summary.decompose()  # Remove summary so remaining text nodes can be processed

    # Extract remaining text lines (historical entries)
    remaining_text = details_tag.get_text()
    for line in remaining_text.splitlines():
        line_clean = re.sub(r'\s+', ' ', line).strip()
        if line_clean:
            entries.append(line_clean)

    return sep.join(entries)


def _parse_td_content_element(x):
    """
    Parse a single HTML element from a table cell's contents.

    This function converts specific HTML elements (like ``<em>``, ``<q>``, ``<span>``
    and ``<details>``) into formatted text representations, handling standard layout
    classes natively.

    :param x: The BeautifulSoup element or string extracted from the table cell.
    :type x: bs4.element.Tag | bs4.element.NavigableString | str
    :return: Parsed and formatted string.
    :rtype: str
    """

    if isinstance(x, str) or isinstance(x, bs4.NavigableString):
        return str(x).strip(' ')

    tag_name = x.name
    td_text = x.get_text(separator=' ', strip=True)

    if tag_name == 'em':
        return f'[{td_text}]'

    if tag_name == 'q':
        return f'"{td_text}"'

    if tag_name in {'span', 'a'}:
        td_class = x.get('class', [])
        has_span_child = x.find('span') is not None

        if td_class == ['r']:
            if td_text == 'no CRS?':
                return f'\t\t / [{td_text}]'
            if '\n ' in td_text:
                parts = [
                    f'\t\t{y}' if y.startswith('(') and y.endswith(')') else f' / [{y}]'
                    for y in td_text.split('\n ')
                ]
                return ' '.join(parts)
            if '(' not in td_text and ')' not in td_text:
                return f'\t\t / [{td_text}]'
            return f'\t\t{td_text}'

        if td_class == ['popup']:
            clean_text = td_text.replace('✖', '').strip()
            return f'({clean_text})'

        if not td_class and has_span_child:
            return f'\t\t{td_text}'

    if tag_name == 'div':
        return ''

    if tag_name == 'details':
        return _parse_details_tag(x)

    return td_text


def _prep_records(trs, ths, sep=' / '):
    """
    Prepare raw row records and track row-spanned cells from table rows.

    :param trs: A list or result set of ``<tr>`` tags.
    :type trs: bs4.element.ResultSet | list[bs4.element.Tag]
    :param ths: The table headers to determine the correct number of columns.
    :type ths: list | bs4.element.Tag
    :param sep: The separator to replace newlines; defaults to ``' / '``.
    :type sep: str
    :return: A tuple containing the raw string records and a list of rowspan metadata.
    :rtype: tuple[list[list[str]], list[tuple[int, int, int, str]]]
    """

    ths_len = len(ths)
    records = []
    row_spanned = []
    newline_pattern = re.compile(r'/?\r?\n')

    for row_idx, tr in enumerate(trs):
        data = []
        tds = tr.find_all('td')

        if len(tds) != ths_len:
            tds = tds[:ths_len]

        for col_idx, td in enumerate(tds):
            if td.find('td'):
                # Handle nested tables
                a_tag = td.find('a')
                # noinspection string-conversion-without-dunder-method
                text_parts = [str(x) for x in a_tag.contents] + ['\t\t / '] if a_tag else ['']
            else:
                text_parts = [_parse_td_content_element(x) for x in td.contents]

            # Sort elements containing '\t\t' to the end of the text
            valid_parts = [str(x) for x in text_parts if str(x).strip(' ')]
            valid_parts.sort(key=lambda x: '\t\t' in x)
            text = ' '.join(valid_parts)

            if sep:
                text = newline_pattern.sub(sep, text)

            if td.has_attr('rowspan'):
                try:
                    span_val = int(td['rowspan'])
                    row_spanned.append((row_idx, span_val, col_idx, text))
                except ValueError:
                    pass

            data.append(text)

        records.append(data)

    return records, row_spanned


def _apply_row_spans(records, row_spanned):
    """
    Apply rowspan values to subsequent rows to standardise the data grid.

    :param records: The parsed list of row data.
    :type records: list[list[str]]
    :param row_spanned: Metadata detailing row indices, span counts, column indices,
        and cell text.
    :type row_spanned: list[tuple[int, int, int, str]]
    :return: Standardised records with rowspans duplicated.
    :rtype: list[list[str]]
    """

    if not row_spanned:
        return records

    records_ = copy.deepcopy(records)
    row_spanned_dict = collections.defaultdict(list)

    for row_idx, span_count, col_idx, text_val in row_spanned:
        row_spanned_dict[row_idx].append((span_count, col_idx, text_val))

    for row_idx, spans in row_spanned_dict.items():
        for span_count, col_idx, text_val in spans:
            for j in range(1, span_count):
                target_row = row_idx + j

                # Defend against malformed HTML spanning past table bounds
                if target_row >= len(records_):
                    continue

                row_len = len(records_[target_row])
                if row_len < len(records_[row_idx]):
                    if row_len == col_idx:
                        records_[target_row].insert(col_idx, text_val)
                    elif row_len > col_idx:
                        if records_[target_row][col_idx] != '':
                            records_[target_row].insert(col_idx, text_val)
                        else:
                            records_[target_row][col_idx] = text_val

    return records_


def parse_tr(trs, ths, sep=' / ', as_dataframe=False):
    # noinspection PyUnresolvedReferences
    """
    Parse a list of HTML ``<tr>`` elements and extract data matching column headers.

    This function processes the rows from a table (``<tr>`` tags) and aligns them to the
    corresponding column headers (``<th>`` tags). It correctly manages HTML ``rowspan``
    attributes and resolves missing items.

    See also [`PT-1 <https://stackoverflow.com/questions/28763891/>`_].

    :param trs: The content of ``<tr>`` tags from a web page table.
    :type trs: bs4.element.ResultSet | list[bs4.element.Tag]
    :param ths: A list of column names or ``<th>`` tags for the table.
    :type ths: list | bs4.element.Tag
    :param sep: The separator to replace line breaks. Defaults to ``' / '``.
    :type sep: str | None
    :param as_dataframe: If ``True``, returns the data as a Pandas DataFrame. Defaults to ``False``.
    :type as_dataframe: bool
    :return: A list of lists representing rows of the table, or a dataframe if requested.
    :rtype: pandas.DataFrame | list[list[str]]

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

    records = _apply_row_spans(records, row_spanned)

    if isinstance(ths, bs4.element.Tag):
        column_names = [th.get_text(strip=True) for th in ths.find_all('th')]
    elif ths and all(isinstance(x, bs4.element.Tag) for x in ths):
        column_names = [th.get_text(strip=True) for th in ths]
    else:
        column_names = copy.copy(ths)

    n_columns = len(column_names)
    empty_rows = []

    for k, record in enumerate(records):
        diff = n_columns - len(record)
        if diff == n_columns:
            empty_rows.append(k)
        elif diff > 0:
            record.extend(['\xa0'] * diff)
        elif diff < 0 and len(record) > 2 and record[2] == '\xa0':
            del record[2]

    # Iterate in reverse to avoid index shifting when elements are removed
    for k in reversed(empty_rows):
        del records[k]

    if as_dataframe:
        return pd.DataFrame(data=records, columns=column_names)

    return records


def _parse_th_tag(th_tag):
    """
    Parse a table header tag and format emphasis elements for column names.

    This function extracts text from a ``<th>`` tag, converting any nested ``<em>``
    tags into parenthesised text and standardising internal whitespace to produce
    clean DataFrame column headers.

    :param th_tag: The table header element or HTML string fragment.
    :type th_tag: bs4.element.Tag | str
    :return: Formatted column header string suitable for a DataFrame.
    :rtype: str

    **Examples**::

        >>> raw_html = '<th>Code <em>number of buzzes or groups separated by pauses</em></th>'
        >>> _parse_th_tag(raw_html)
        'Code (number of buzzes or groups separated by pauses)'
        >>> _parse_th_tag('<th>Location</th>')
        'Location'
    """

    if isinstance(th_tag, str):
        soup = bs4.BeautifulSoup(th_tag, 'html.parser')
        th_tag = soup.find('th') or soup

    if not th_tag:
        return ''

    # Copy tag to prevent mutating the caller's parsed BeautifulSoup DOM tree
    tag_copy = copy.copy(th_tag)

    for em in tag_copy.find_all('em'):
        em_text = em.get_text(strip=True)
        em.replace_with(f' ({em_text})' if em_text else '')

    header_text = tag_copy.get_text(separator=' ')
    return re.sub(r'\s+', ' ', header_text).strip()


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

    theads, tbodies = soup.find_all('thead'), soup.find_all('tbody')

    tables = []
    for thead, tbody in zip(theads, tbodies):
        ths = [_parse_th_tag(th) for th in thead.find_all('th')]
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
    # noinspection PyShadowingNames
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

        >>> str_date = '2020-01-01'
        >>> parse_date(str_date)
        '2020-01-01'

        >>> str_date = '2020-jan-01'
        >>> parse_date(str_date)
        '2020-01-01'

        >>> parse_date(str_date, as_date_type=True)
        datetime.date(2020, 1, 1)
    """

    try:
        parsed_date = dateutil.parser.parse(timestr=str_date, fuzzy=True)
        # or, parsed_date = datetime.datetime.strptime(str_date[12:], '%d %B %Y')

    except (TypeError, ValueError, calendar.IllegalMonthError):
        # noinspection PyBroadException
        try:
            month_name = find_similar_str(str_date, lookup_list=calendar.month_name)
            if not month_name:
                return None

            err_month_ = find_similar_str(month_name, lookup_list=str_date.split(' '))
            if not err_month_:
                return None

            parsed_date = dateutil.parser.parse(
                timestr=str_date.replace(err_month_, month_name), fuzzy=True)

        except Exception:
            return None

    return parsed_date.date() if as_date_type else parsed_date.date().isoformat()


def _align_column_list_lengths(df, target_cols, fill_value='', repeat_single=True):
    # noinspection shadowing-names
    """
    Equalise list lengths across target columns for each row in a DataFrame.

    This function ensures all specified target columns contain lists of identical
    length for every row. Non-list entries are wrapped into single-element lists,
    single-element lists are optionally repeated and shorter lists are padded with
    a custom fill value prior to multi-column explosion.

    :param df: Target DataFrame containing list or scalar elements.
    :type df: pandas.DataFrame
    :param target_cols: Column names whose list lengths should be equalised.
    :type target_cols: list[str]
    :param fill_value: Value used to pad lists shorter than the maximum list length
        in a given row. Defaults to ``''``.
    :type fill_value: Any
    :param repeat_single: Whether single-element lists should be repeated to match
        the maximum list length. If ``False``, they are padded with ``fill_value``.
        Defaults to ``True``.
    :type repeat_single: bool
    :return: A copy of the DataFrame with aligned list lengths across target columns.
    :rtype: pandas.DataFrame

    **Examples**::

        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'A': [['x', 'y']],
        ...     'B': ['z'],
        ...     'C': [[1]]
        ... })

        >>> _align_column_list_lengths(df, ['A', 'B', 'C'], fill_value=None, repeat_single=True)
               A       B       C
        0  [x, y]  [z, z]  [1, 1]

        >>> _align_column_list_lengths(df, ['A', 'B', 'C'], fill_value=None, repeat_single=False)
               A          B          C
        0  [x, y]  [z, None]  [1, None]
    """

    cols = [c for c in target_cols if c in df.columns]
    if not cols or df.empty:
        return df

    res_df = df.copy()

    for col in cols:
        res_df[col] = res_df[col].map(lambda x: x if isinstance(x, list) else [x])

    def _align_row(row):
        lengths = [len(row[c]) for c in cols]
        max_len = max(lengths) if lengths else 1

        if max_len <= 1 or all(length == max_len for length in lengths):
            return row

        for c in cols:
            curr_len = len(row[c])
            if curr_len < max_len:
                if curr_len == 1 and repeat_single:
                    row[c] = row[c] * max_len
                else:
                    row[c] = row[c] + [fill_value] * (max_len - curr_len)
        return row

    return res_df.apply(_align_row, axis=1)


# == Extract information ===========================================================================


def _clean_key(k_text):
    return k_text.replace("–", "-").strip("()").removesuffix(".shtml").removesuffix(".shtm")


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

    return _clean_key(text), href


def _get_site_map_h3_dl_dt_dds(h3_dl_dt, next_dd=None):
    if next_dd is None:
        next_dd = h3_dl_dt.find_next('dd')

    prev_dt = next_dd.find_previous('dt')

    h3_dl_dt_dds = {}
    while prev_dt == h3_dl_dt:
        next_dd_sub_dl_ = next_dd.find('dl')

        if next_dd_sub_dl_:
            sub_dts = next_dd_sub_dl_.find_all('dt')

            for sub_dt in sub_dts:
                sub_dt_text, _ = _parse_dd_or_dt(sub_dt)
                sub_dt_dds = sub_dt.find_next_siblings('dd')
                sub_dt_dds_dict = _get_site_map_sub_dl(h3_dl_dts=sub_dt_dds)

                h3_dl_dt_dds.update({_clean_key(sub_dt_text): sub_dt_dds_dict})

        else:
            a = next_dd.find('a')
            text, href = _clean_key(a.get_text(strip=True)), a.get(key='href')
            h3_dl_dt_dds.update({text: urllib.parse.urljoin(homepage_url(), href)})

        try:
            next_dd = next_dd.find_next_sibling('dd')
            prev_dt = next_dd.find_previous_sibling('dt')
        except AttributeError:
            break

    return h3_dl_dt_dds


def _get_site_map_sub_dl(h3_dl_dts):
    """
    Recursively processes nested dl/dt/dd elements to build a structured dictionary.
    """

    h3_dl_dt_dd_dict = {}

    for h3_dl_dt in h3_dl_dts:
        dt_text_, dt_href = _parse_dd_or_dt(dd_or_dt=h3_dl_dt)
        dt_text = _clean_key(dt_text_)

        if dt_href:
            h3_dl_dt_dd_dict.update({dt_text: urllib.parse.urljoin(homepage_url(), dt_href)})

        else:
            next_dd = h3_dl_dt.find_next('dd')
            next_dd_sub_dl = next_dd.find('dl')

            if next_dd_sub_dl:
                # next_dd_sub_dl_dts = next_dd_sub_dl.find_all(name='dt')
                next_dd_sub_dl_dts = [
                    dt for dt in next_dd.find_all('dt') if dt.has_attr('class')]
                h3_dl_dt_dd_dict.update({dt_text: _get_site_map_sub_dl(next_dd_sub_dl_dts)})

            else:
                h3_dl_dt_dds = _get_site_map_h3_dl_dt_dds(h3_dl_dt=h3_dl_dt, next_dd=next_dd)
                h3_dl_dt_dd_dict.update({dt_text: h3_dl_dt_dds})

    return h3_dl_dt_dd_dict


def _get_site_map(source, parser='html.parser'):
    """
    Parse the site map from the given HTML source and return a structured dictionary.

    This internal utility extracts section categories, links, and sub-lists from the structure of
    the primary railway codes site layout page.

    :param source: HTTP response context containing the sitemap configuration file.
    :type source: requests.Response
    :param parser: Soup parsing feature engine to use. Defaults to ``'html.parser'``.
    :type parser: str
    :return: A structured map containing clean keys linked to absolute domain targets.
    :rtype: dict
    """

    soup = bs4.BeautifulSoup(markup=source.content, features=parser)
    site_map = {}

    h3s = soup.find_all('h3', attrs={'class': 'site'})

    for h3 in h3s:
        h3_title = h3.get_text(strip=True)  # h3 > dl > dt
        dl_element = h3.find_next('dl')
        if not dl_element:
            continue

        h3_dl_dts = dl_element.find_all('dt')
        if not h3_dl_dts:
            continue

        if len(h3_dl_dts) == 1:
            dd_dict = {}  # h3 > dl > dt > dd

            h3_dl_dt = h3_dl_dts[0]
            h3_dl_dt_text = h3_dl_dt.get_text(strip=True)

            if h3_dl_dt_text == '':
                for dd in h3_dl_dt.find_next_siblings('dd'):
                    text, href = _parse_dd_or_dt(dd)
                    dd_dict.update({_clean_key(text): urllib.parse.urljoin(homepage_url(), href)})

        else:
            dd_dict = _get_site_map_sub_dl(h3_dl_dts=h3_dl_dts)

        site_map.update({_clean_key(h3_title): dd_dict})

    # noinspection SpellCheckingInspection
    site_map = update_dict_keys(
        site_map, replacements={"(all ogher languages)": "(all other languages)"})

    return site_map


def get_site_map(update=False, confirmation_required=True, verbose=False, raise_error=True):
    # noinspection PyShadowingNames
    """
    Get the railway codes project `site map <http://www.railwaycodes.org.uk/misc/sitemap.shtm>`_
    representation data.

    Retrieves database structure configuration values from a cached copy if available, or shifts to
    live web extraction streams depending on user parameter profiles.

    :param update: Whether to check for updates to the package data. Defaults to ``False``.
    :type update: bool
    :param confirmation_required: Whether user confirmation is required before proceeding.
        Defaults to ``True``.
    :type confirmation_required: bool
    :param verbose: Whether to print relevant information to the console. Defaults to ``False``.
    :type verbose: bool | int
    :param raise_error: Whether to raise the provided exception;
        if ``raise_error=False``, the error will be suppressed. Defaults to ``True``.
    :type raise_error: bool
    :return: A dictionary containing the data of site map, or ``None`` if retrieval failed.
    :rtype: dict | None

    **Examples**::

        >>> from pyrcs.parser import get_site_map

        >>> site_map = get_site_map()

        >>> type(site_map)
        dict
        >>> list(site_map.keys())
        ['Home',
         'Line data',
         'Other assets',
         '"Legal/financial" lists',
         'Miscellaneous']

        >>> site_map['Home']
        {'index': 'http://www.railwaycodes.org.uk/index.shtml'}
    """

    path_to_file = cd_data("site-map.json", mkdir=True)

    if os.path.isfile(path_to_file) and not update:
        return load_data(path_to_file)

    else:
        if not confirmed("To collect the site map\n?", confirmation_required=confirmation_required):
            if verbose in {True, 1}:
                print("Cancelled.")
            return None

        if verbose in {True, 1}:
            print("Updating the package data", end=" ... ")

        try:
            url = urllib.parse.urljoin(homepage_url(), "/misc/sitemap.shtm")
            source = requests.get(url=url, headers=fake_requests_headers())
            source.raise_for_status()
        except Exception as e:
            handle_connection_error(
                update=update, verbose=True if update else verbose, e=e, raise_error=raise_error)
            return None

        try:
            site_map = _get_site_map(source=source)

            if verbose in {True, 1}:
                print("Done.")

            if site_map:
                save_data(site_map, path_to_file, indent=4, verbose=(verbose == 2 or False))

            return site_map

        except Exception as e:
            _print_failure_message(e, "Failed. Error:", verbose=verbose, raise_error=raise_error)

        return None


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


def get_last_updated_date(url, parsed=True, as_date_type=False, verbose=False, raise_error=True):
    # noinspection PyShadowingNames
    """
    Gets the last update date of a specified web page.

    This function extracts the date when the given web page was last updated.
    The date can be returned as a string or a date object.

    :param url: The URL of the web page for which the last update date is requested.
    :type url: str
    :param parsed: Whether to reformat the date into a standardised format (``YYYY-MM-DD``);
        defaults to ``True``.
    :type parsed: bool
    :param as_date_type: If ``True``, the date is returned as a `datetime.date`_ object;
        if ``False`` (default), it's returned as a string.
    :type as_date_type: bool
    :param verbose: Whether to print relevant information to the console; defaults to ``False``.
    :type verbose: bool | int
    :param raise_error: Whether to raise the provided exception;
        if ``raise_error=False``, the error will be suppressed; defaults to ``True``.
    :type raise_error: bool
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
        source = requests.get(url=url.lower(), headers=fake_requests_headers(), timeout=5)
        source.raise_for_status()
    except Exception as e:
        _print_failure_message(e, verbose=verbose, raise_error=raise_error)

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
    """
    Parse the introduction section paragraphs from the provided HTML source content.

    This internal helper extracts sequential paragraphs following the introductory header element
    until a new header breakdown boundary is encountered.

    :param source: HTTP response context containing the target webpage text.
    :type source: requests.Response
    :param delimiter: The structural character separator used to join paragraphs.
        Defaults to ``'\\n'``.
    :type delimiter: str
    :return: A single text string combining all sequential introductory paragraphs.
    :rtype: str | None
    """

    soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

    # Seek the target introduction header element
    h3_elements = soup.find_all('h3')
    intro_h3 = None
    for h3 in h3_elements:
        if h3.get_text(strip=True).startswith('Intro'):
            intro_h3 = h3
            break

    if not intro_h3:
        return None

    p = intro_h3.find_next(name='p')
    intro_paras = []

    # Cycle through siblings while validating paragraph layout boundaries
    while p is not None:
        prev_h3 = p.find_previous(name='h3')
        prev_h4 = p.find_previous(name='h4')

        # Terminate traversal if we drift outside the introductory header segment context
        if prev_h3 != intro_h3 or prev_h4 is not None:
            break

        para_text = p.text.replace('  ', ' ')
        if para_text.strip():
            intro_paras.append(para_text)

        p = p.find_next(name='p')

    introduction = delimiter.join(intro_paras)

    return introduction


def get_introduction(url, delimiter='\n', update=False, verbose=False, raise_error=False):
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
    :param verbose: Whether to print relevant information to the console; defaults to ``False``.
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
    except Exception as e:
        handle_connection_error(
            update=update, verbose=True if update else verbose, e=e, raise_error=raise_error)
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
    # noinspection PyShadowingNames
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

        >>> url = 'http://www.railwaycodes.org.uk/elrs/elr0.shtm'
        >>> elr_cat: dict = get_catalogue(url)

        >>> list(elr_cat.keys())[:5]
        ['Introduction', 'A', 'B', 'C', 'D']
        >>> list(elr_cat.keys())[-5:]
        ['Lines without codes',
         'ELR/LOR converter',
         'LUL system',
         'DLR system',
         'Canals']

        >>> url = 'http://www.railwaycodes.org.uk/crs/crs0.shtm'
        >>> location_code_cat: dict = get_catalogue(url)

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
        _print_failure_message(e=e, verbose=verbose, raise_error=raise_error)
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
    Get a menu of the available data classes from the specified site home URL.

    This function scrapes the home web page for available dropdown classes (typically categorised
    hyperlinks) and returns them as a dictionary. It provides configurations to update the local
    catalogue file copy.

    :param name: The name of the target data category.
    :type name: str
    :param update: Whether to check for updates to the package data. Defaults to ``False``.
    :type update: bool
    :param confirmation_required: Whether user confirmation is required before proceeding.
        Defaults to ``True``.
    :type confirmation_required: bool
    :param verbose: Whether to print relevant information to the console. Defaults to ``False``.
    :type verbose: bool | int
    :param raise_error: Whether to raise the provided exception;
        if ``raise_error=False`` (default), the error is suppressed.
    :type raise_error: bool
    :return: A category menu in dictionary form, or ``None`` if retrieval failed.
    :rtype: dict | None

    **Examples**::

        >>> from pyrcs.parser import get_category_menu

        >>> menu: dict = get_category_menu(name='Line data')

        >>> list(menu.keys())
        ['Line data']
        >>> len(menu['Line data'])
        7
    """

    path_to_file = cd_data("catalogue", f"{name.lower().replace(' ', '-')}-menu.json", mkdir=True)

    if os.path.isfile(path_to_file) and not update:
        return load_data(path_to_file)

    if not confirmed("To collect/update category menu?\n", confirmation_required):
        if verbose in {True, 1}:
            print("Cancelled.")
        return None

    if verbose:
        print(f"Collecting category menu for \"{name.title()}\"", end=" ... ")

    try:
        source = requests.get(url=homepage_url(), headers=fake_requests_headers())
        source.raise_for_status()
    except Exception as e:
        handle_connection_error(
            update=update, verbose=True if update else verbose, e=e, raise_error=raise_error)
        return None

    try:
        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

        # Find the designated category button
        drop_btn_ = soup.select(f'button:-soup-contains("{name}")')
        if not drop_btn_:
            return None

        drop_btn = drop_btn_[0]

        # Extract targeted sub-links from sibling container
        sibling_div = drop_btn.find_next_sibling('div')
        if not sibling_div:
            return None

        a_href_list = sibling_div.find_all('a')

        cls_menu_ = [
            (a.get_text(), urllib.parse.urljoin(homepage_url(), a['href']))
            for a in a_href_list if 'href' in a.attrs
        ]

        # Process and write file strictly when data elements exist
        if cls_menu_:
            cls_menu = {name: dict(cls_menu_)}

            if verbose:
                print("Done.")

            save_data(cls_menu, path_to_file, indent=4, verbose=(verbose == 2 or False))
            return cls_menu

    except Exception as e:
        _print_failure_message(e, "Failed. Error:", verbose=verbose, raise_error=raise_error)

    return None


def get_heading_text(heading_tag, elem_tag_name='em'):
    # noinspection PyShadowingNames,PyUnresolvedReferences
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
        >>> source = requests.get(url, headers=fake_requests_headers())

        >>> soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')
        >>> heading_tag = soup.find('h3')

        >>> h3_text = get_heading_text(heading_tag, elem_tag_name='em')
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


def get_page_catalogue(url, head_tag_name='nav', head_tag_txt='Jump to:', feature_tag_name='h3',
                       verbose=False, raise_error=False):
    # noinspection PyUnresolvedReferences
    """
    Get the catalogue of features from the main page of a data cluster.

    This function extracts structured data (features) from a web page by parsing specific tags,
    typically used for features like headings and links in railway-related databases.

    :param url: The URL of the main page of a data cluster.
    :type url: str
    :param head_tag_name: The tag name of the feature list at the top. Defaults to ``'nav'``.
    :type head_tag_name: str
    :param head_tag_txt: Text contained in the head tag. Defaults to ``'Jump to:'``.
    :type head_tag_txt: str
    :param feature_tag_name: The tag name of the feature headings. Defaults to ``'h3'``.
    :type feature_tag_name: str
    :param verbose: Whether to print relevant information to the console. Defaults to ``False``.
    :type verbose: bool | int
    :param raise_error: Whether to raise the provided exception;
        if ``raise_error=False``, the error will be suppressed. Defaults to ``False``.
    :type raise_error: bool
    :return: A dataframe containing the feature catalogue, or ``None`` if parsing fails.
    :rtype: pandas.DataFrame | None

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
        ['feature', 'url', 'heading']
    """

    try:
        source = requests.get(url=url, headers=fake_requests_headers())
        source.raise_for_status()
    except Exception as e:
        handle_connection_error(verbose=verbose, e=e, raise_error=raise_error)
        return None

    try:
        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

        # Parse categorical headings up front
        feature_headings = []
        for h3 in soup.find_all(feature_tag_name):
            sub_heading = get_heading_text(heading_tag=h3, elem_tag_name='em')
            feature_headings.append(sub_heading)

        feature_records = []

        for nav in soup.find_all(head_tag_name):
            nav_text = nav.text.replace('\r\n', '').strip()

            if re.match(r'^({})'.format(re.escape(head_tag_txt)), nav_text):
                sep = '\xa0| ' if '\xa0| ' in nav_text else '\n'
                feature_names = nav_text.replace(f'{head_tag_txt}{sep}', '').split(sep)

                for idx, item_name in enumerate(feature_names):
                    text_pat = re.compile(r'.*{}.*'.format(re.escape(item_name)), re.IGNORECASE)
                    a = nav.find('a', string=text_pat)

                    # Safe fallbacks if tag matches are missing
                    feature_url = urllib.parse.urljoin(url, a.get('href')) if a else None
                    heading_val = feature_headings[idx] if idx < len(feature_headings) else None

                    feature_records.append({
                        'feature': item_name,
                        'url': feature_url,
                        'heading': heading_val
                    })

        if not feature_records:
            return pd.DataFrame({'feature': [], 'url': [], 'heading': []})

        return pd.DataFrame(feature_records)

    except Exception as e:
        _print_failure_message(e, verbose=verbose, raise_error=raise_error)

    return None


def get_hypertext(hypertext_tag, hyperlink_tag_name='a', md_style=True):
    # noinspection PyShadowingNames
    """
    Extract text content from an HTML tag while preserving and formatting hyperlinks.

    This function iterates through the child nodes of a BeautifulSoup tag element, converting
    hyperlink tags into standardised Markdown format or plain-text web link references.

    :param hypertext_tag: The tag containing text and hyperlinked element targets.
    :type hypertext_tag: bs4.element.Tag | bs4.element.PageElement
    :param hyperlink_tag_name: The target tag name of the hyperlink. Defaults to ``'a'``.
    :type hyperlink_tag_name: str
    :param md_style: Whether to return the hyperlinks in Markdown style. Defaults to ``True``.
    :type md_style: bool
    :return: The fully combined text string with formatted hyperlink references.
    :rtype: str

    **Examples**::

        >>> from pyrcs.parser import get_hypertext
        >>> from pyrcs.line_data import Electrification
        >>> import bs4
        >>> import requests

        >>> elec = Electrification()

        >>> assert isinstance(elec.catalogue, dict)
        >>> url = elec.catalogue[elec.KEY_TO_INDEPENDENT_LINES]

        >>> source = requests.get(url)
        >>> soup = bs4.BeautifulSoup(source.content, 'html.parser')
        >>> h3 = soup.find('h3')

        >>> assert isinstance(h3, bs4.Tag)
        >>> hypertext_tag = h3.find_all_next('p')[9]
        <p>Croydon Tramlink mast references can be found on the <a href="http://www.croydon-tra...

        >>> result_text = get_hypertext(hypertext_tag, md_style=True)
        >>> result_text
        'Croydon Tramlink mast references can be found on the [Croydon Tramlink Unofficial Site...
    """

    if not isinstance(hypertext_tag, bs4.element.Tag):
        return hypertext_tag.get_text() if hasattr(hypertext_tag, 'get_text') else ""

    hypertext_parts = []

    # Handle text fragments vs elements gracefully without throwing attribute errors
    for node in hypertext_tag.contents:
        if isinstance(node, bs4.element.Tag) and node.name == hyperlink_tag_name:
            href = node.get('href')
            node_text = node.get_text()

            if href:
                formatted_link = f"[{node_text}]({href})" if md_style else f"{node_text} ({href})"
                hypertext_parts.append(formatted_link)
            else:
                hypertext_parts.append(node_text)

        else:  # Use native soup text extraction methods to satisfy type checks completely
            if hasattr(node, 'get_text'):
                hypertext_parts.append(node.get_text())
            elif isinstance(node, bs4.element.NavigableString):
                hypertext_parts.append(node.string or '')
            else:
                hypertext_parts.append('')

    result_text = "".join(hypertext_parts).replace("\xa0", "").replace("  ", " ")

    return result_text
