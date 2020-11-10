"""
Utilities - Helper functions.
"""

import collections
import datetime
import os
import re
import socket
import urllib.parse

import bs4
import dateutil.parser
import measurement.measures
import numpy as np
import pandas as pd
import pkg_resources
import requests
from pyhelpers.ops import confirmed, fake_requests_headers
from pyhelpers.store import load_json, load_pickle, save_json, save_pickle


# -- Specification of resource homepage ------------------------------------------------

def homepage_url():
    """
    Specify the homepage URL of the data source.

    :return: URL of the data source homepage
    :rtype: str
    """

    return 'http://www.railwaycodes.org.uk/'


# -- Specification of directory/file paths ---------------------------------------------

def cd_dat(*sub_dir, dat_dir="dat", mkdir=False, **kwargs):
    """
    Change directory to `dat_dir/` and sub-directories within a package.

    :param sub_dir: name of directory; names of directories (and/or a filename)
    :type sub_dir: str
    :param dat_dir: name of a directory to store data, defaults to ``"dat"``
    :type dat_dir: str
    :param mkdir: whether to create a directory, defaults to ``False``
    :type mkdir: bool
    :param kwargs: optional parameters of `os.makedirs`_, e.g. ``mode=0o777``
    :return: a full path to a directory (or a file) under ``data_dir``
    :rtype: str

    .. _`os.makedirs`: https://docs.python.org/3/library/os.html#os.makedirs

    **Example**::

        >>> import os
        >>> from pyrcs.utils import cd_dat

        >>> path_to_dat_dir = cd_dat("line-data", dat_dir="dat", mkdir=False)
        >>> print(os.path.relpath(path_to_dat_dir))
        pyrcs\\dat\\line-data

    :meta private:
    """

    path = pkg_resources.resource_filename(__name__, dat_dir)
    for x in sub_dir:
        path = os.path.join(path, x)

    if mkdir:
        path_to_file, ext = os.path.splitext(path)
        if ext == '':
            os.makedirs(path_to_file, exist_ok=True, **kwargs)
        else:
            os.makedirs(os.path.dirname(path_to_file), exist_ok=True, **kwargs)

    return path


# -- Data converters -------------------------------------------------------------------

def mile_chain_to_nr_mileage(miles_chains):
    """
    Convert mileage data in the form '<miles>.<chains>' to Network Rail mileage.

    :param miles_chains: mileage data presented in the form '<miles>.<chains>'
    :type miles_chains: str or numpy.nan or None
    :return: Network Rail mileage in the form '<miles>.<yards>'
    :rtype: str

    **Examples**::

        >>> from pyrcs.utils import mile_chain_to_nr_mileage

        >>> miles_chains_dat = '0.18'  # AAM 0.18 Tewkesbury Junction with ANZ (84.62)
        >>> mileage_data = mile_chain_to_nr_mileage(miles_chains_dat)
        >>> print(mileage_data)
        0.0396

        >>> miles_chains_dat = None  # or np.nan, or ''
        >>> mileage_data = mile_chain_to_nr_mileage(miles_chains_dat)
        >>> print(mileage_data)

    """

    if pd.notna(miles_chains) and miles_chains != '':
        miles, chains = str(miles_chains).split('.')
        yards = measurement.measures.Distance(chain=chains).yd
        network_rail_mileage = '%.4f' % (int(miles) + round(yards / (10 ** 4), 4))
    else:
        network_rail_mileage = ''

    return network_rail_mileage


def nr_mileage_to_mile_chain(str_mileage):
    """
    Convert Network Rail mileage to the form '<miles>.<chains>'.

    :param str_mileage: Network Rail mileage data presented in the form '<miles>.<yards>'
    :type str_mileage: str or numpy.nan or None
    :return: '<miles>.<chains>'
    :rtype: str

    **Examples**::

        >>> from pyrcs.utils import nr_mileage_to_mile_chain

        >>> str_mileage_dat = '0.0396'
        >>> miles_chains_dat = nr_mileage_to_mile_chain(str_mileage_dat)
        >>> print(miles_chains_dat)
        0.18

        >>> str_mileage_dat = None  # or np.nan, or ''
        >>> miles_chains_dat = nr_mileage_to_mile_chain(str_mileage_dat)
        >>> print(miles_chains_dat)

    """

    if pd.notna(str_mileage) and str_mileage != '':
        miles, yards = str(str_mileage).split('.')
        chains = measurement.measures.Distance(yard=yards).chain
        miles_chains = '%.2f' % (int(miles) + round(chains / (10 ** 2), 2))
    else:
        miles_chains = ''

    return miles_chains


def nr_mileage_str_to_num(str_mileage):
    """
    Convert string-type Network Rail mileage to numerical-type one.

    :param str_mileage: string-type Network Rail mileage in the form '<miles>.<yards>'
    :type str_mileage: str
    :return: numerical-type Network Rail mileage
    :rtype: float

    **Examples**::

        >>> from pyrcs.utils import nr_mileage_str_to_num

        >>> str_mileage_dat = '0.0396'
        >>> num_mileage_dat = nr_mileage_str_to_num(str_mileage_dat)
        >>> print(num_mileage_dat)
        0.0396

        >>> str_mileage_dat = ''
        >>> num_mileage_dat = nr_mileage_str_to_num(str_mileage_dat)
        >>> print(num_mileage_dat)
        nan
    """

    num_mileage = np.nan if str_mileage == '' else round(float(str_mileage), 4)

    return num_mileage


def nr_mileage_num_to_str(num_mileage):
    """
    Convert numerical-type Network Rail mileage to string-type one.

    :param num_mileage: numerical-type Network Rail mileage
    :type num_mileage: float
    :return: string-type Network Rail mileage in the form '<miles>.<yards>'
    :rtype: str

    **Examples**::

        >>> import numpy as np_
        >>> from pyrcs.utils import nr_mileage_num_to_str

        >>> num_mileage_dat = 0.0396
        >>> str_mileage_dat = nr_mileage_num_to_str(num_mileage_dat)
        >>> print(str_mileage_dat)
        0.0396
        >>> type(str_mileage_dat)
        <class 'str'>

        >>> num_mileage_dat = np_.nan
        >>> str_mileage_dat = nr_mileage_num_to_str(num_mileage_dat)
        >>> print(str_mileage_dat)

        >>> type(str_mileage_dat)
        <class 'str'>
    """

    if (num_mileage or num_mileage == 0) and pd.notna(num_mileage):
        nr_mileage = '%.4f' % round(float(num_mileage), 4)
    else:
        nr_mileage = ''

    return nr_mileage


def nr_mileage_to_yards(nr_mileage):
    """
    Convert Network Rail mileages to yards.

    :param nr_mileage: Network Rail mileage
    :type nr_mileage: float or str
    :return: yards
    :rtype: int

    **Examples**::

        >>> from pyrcs.utils import nr_mileage_to_yards

        >>> nr_mileage_dat = '0.0396'
        >>> yards_dat = nr_mileage_to_yards(nr_mileage_dat)
        >>> print(yards_dat)
        396

        >>> nr_mileage_dat = 0.0396
        >>> yards_dat = nr_mileage_to_yards(nr_mileage_dat)
        >>> print(yards_dat)
        396
    """

    if isinstance(nr_mileage, (float, np.float, int, np.integer)):
        nr_mileage = nr_mileage_num_to_str(nr_mileage)

    miles = int(nr_mileage.split('.')[0])
    yards = int(nr_mileage.split('.')[1])
    yards += int(measurement.measures.Distance(mi=miles).yd)

    return yards


def yards_to_nr_mileage(yards):
    """
    Convert yards to Network Rail mileages.

    :param yards: yards
    :type yards: int or float or numpy.nan or None
    :return: Network Rail mileage in the form '<miles>.<yards>'
    :rtype: str

    **Examples**::

        >>> from pyrcs.utils import yards_to_nr_mileage

        >>> yards_dat = 396
        >>> mileage_dat = yards_to_nr_mileage(yards_dat)
        >>> print(mileage_dat)
        0.0396
        >>> type(mileage_dat)
        <class 'str'>

        >>> yards_dat = 396.0
        >>> mileage_dat = yards_to_nr_mileage(yards_dat)
        >>> print(mileage_dat)
        0.0396
        >>> type(mileage_dat)
        <class 'str'>

        >>> yards_dat = None
        >>> mileage_dat = yards_to_nr_mileage(yards_dat)
        >>> print(mileage_dat)

        >>> type(mileage_dat)
        <class 'str'>
    """

    if pd.notnull(yards) and yards != '':
        mileage_mi = np.floor(measurement.measures.Distance(yd=yards).mi)
        mileage_yd = yards - int(measurement.measures.Distance(mi=mileage_mi).yd)
        # Example: "%.2f" % round(2606.89579999999, 2)
        mileage = str('%.4f' % round((mileage_mi + mileage_yd / (10 ** 4)), 4))
    else:
        mileage = ''

    return mileage


def shift_num_nr_mileage(nr_mileage, shift_yards):
    """
    Shift Network Rail mileage by given yards.

    :param nr_mileage: Network Rail mileage
    :type nr_mileage: float or int or str
    :param shift_yards: yards by which the given ``nr_mileage`` is shifted
    :type shift_yards: int or float
    :return: shifted numerical Network Rail mileage
    :rtype: float

    **Examples**::

        >>> from pyrcs.utils import shift_num_nr_mileage

        >>> num_mileage_dat = shift_num_nr_mileage(nr_mileage='0.0396', shift_yards=220)
        >>> print(num_mileage_dat)
        0.0616

        >>> shift_num_nr_mileage(nr_mileage='0.0396', shift_yards=220.99)
        >>> print(num_mileage_dat)
        0.0617

        >>> shift_num_nr_mileage(nr_mileage=10, shift_yards=220)
        >>> print(num_mileage_dat)
        10.022
    """

    yards = nr_mileage_to_yards(nr_mileage) + shift_yards
    shifted_nr_mileage = yards_to_nr_mileage(yards)
    shifted_num_mileage = nr_mileage_str_to_num(shifted_nr_mileage)

    return shifted_num_mileage


def year_to_financial_year(date):
    """
    Convert calendar year of a given date to Network Rail financial year.

    :param date: date
    :type date: datetime.datetime
    :return: Network Rail financial year of the given ``date``
    :rtype: int

    **Example**::

        >>> import datetime
        >>> from pyrcs.utils import year_to_financial_year

        >>> financial_year = year_to_financial_year(datetime.datetime.now())
        >>> print(financial_year)
        2020
    """

    financial_date = date + pd.DateOffset(months=-3)

    return financial_date.year


# -- Data parsers ----------------------------------------------------------------------

def parse_tr(header, trs):
    """
    Parse a list of parsed HTML <tr> elements.

    .. _parse-tr:

    See also [`PT-1 <https://stackoverflow.com/questions/28763891/>`_].

    :param header: list of column names of a requested table
    :type header: list
    :param trs: contents under <tr> tags (bs4.Tag) of a web page
    :type trs: bs4.ResultSet
    :return: list of lists with each comprising a row of the requested table
    :rtype: list

    **Example**::

        >>> import bs4
        >>> import requests
        >>> from pyrcs.utils import fake_requests_headers, parse_tr

        >>> source = requests.get('http://www.railwaycodes.org.uk/elrs/elra.shtm',
        ...                       headers=fake_requests_headers())
        >>> parsed_text = bs4.BeautifulSoup(source.text, 'lxml')
        >>> header_ = []
        >>> for th in parsed_text.find_all('th'):
        ...     header_.append(th.text)
        >>> trs_dat = parsed_text.find_all('tr')

        >>> tables_list = parse_tr(header_, trs_dat)  # returns a list of lists
        >>> type(tables_list)
        <class 'list'>
        >>> print(tables_list[-1])
        ['AYT', 'Aberystwyth Branch', '0.00 - 41.15', 'Pencader Junction', '\xa0']
    """

    tbl_lst = []
    for row in trs:
        data = []
        for dat in row.find_all('td'):
            txt = dat.get_text()
            if '\n' in txt:
                t = txt.split('\n')
                txt = '%s (%s)' % (t[0], t[1:]) if '(' not in txt and ')' not in txt \
                    else '%s %s' % (t[0], t[1:])
                data.append(txt)
            else:
                data.append(txt)
        tbl_lst.append(data)

    row_spanned = []
    for no, tr in enumerate(trs):
        for td_no, rho in enumerate(tr.find_all('td')):
            # print(data.has_attr("rowspan"))
            if rho.has_attr('rowspan'):
                row_spanned.append((no, int(rho['rowspan']), td_no, rho.text))

    if row_spanned:
        d = collections.defaultdict(list)
        for k, *v in row_spanned:
            d[k].append(v)
        row_spanned = list(d.items())

        for x in row_spanned:
            i, to_repeat = x[0], x[1]
            for y in to_repeat:
                for j in range(1, y[0]):
                    if y[2] in tbl_lst[i] and y[2] != '\xa0':
                        y[1] += np.abs(tbl_lst[i].index(y[2]) - y[1])
                    tbl_lst[i + j].insert(y[1], y[2])

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

    for k in range(len(tbl_lst)):
        n = len(header) - len(tbl_lst[k])
        if n > 0:
            tbl_lst[k].extend(['\xa0'] * n)
        elif n < 0 and tbl_lst[k][2] == '\xa0':
            del tbl_lst[k][2]

    return tbl_lst


def parse_table(source, parser='lxml'):
    """
    Parse HTML <tr> elements for creating a data frame.

    :param source: response object to connecting a URL to request a table
    :type source: requests.Response
    :param parser: ``'lxml'`` (default), ``'html5lib'`` or ``'html.parser'``
    :type parser: str
    :return: a list of lists each comprising a row of the requested table
        (see also :ref:`parse_tr() <parse-tr>`) and
        a list of column names of the requested table
    :rtype: tuple

    **Examples**::

        >>> from pyrcs.utils import fake_requests_headers, parse_table

        >>> source_ = requests.get('http://www.railwaycodes.org.uk/elrs/elra.shtm',
        ...                        headers=fake_requests_headers())

        >>> parsed_contents = parse_table(source_, parser='lxml')
        >>> type(parsed_contents)
        <class 'tuple'>
        >>> type(parsed_contents[0])
        <class 'list'>
        >>> type(parsed_contents[1])
        <class 'list'>
    """

    # Get plain text from the source URL
    web_page_text = source.text
    # Parse the text
    parsed_text = bs4.BeautifulSoup(web_page_text, parser)
    # Get all data under the HTML label 'tr'
    table_temp = parsed_text.find_all('tr')
    # Get a list of column names for output DataFrame
    headers = table_temp[0]
    header = [header.text for header in headers.find_all('th')]
    # Get a list of lists, each of which corresponds to a piece of record
    trs = table_temp[1:]

    # Return a list of parsed tr's, each of which corresponds to one df row
    return parse_tr(header, trs), header


def parse_location_name(location_name):
    """
    Parse location name (and its associated note).

    :param location_name: location name (in raw data)
    :type location_name: str or None
    :return: location name and, if any, note
    :rtype: tuple

    **Examples**::

        >>> from pyrcs.utils import parse_location_name

        >>> location_dat = 'Abbey Wood'
        >>> dat_and_note = parse_location_name(location_dat)
        >>> print(dat_and_note)
        ('Abbey Wood', '')

        >>> location_dat = None
        >>> dat_and_note = parse_location_name(location_dat)
        >>> print(dat_and_note)
        ('', '')

        >>> location_dat = 'Abercynon (formerly Abercynon South)'
        >>> dat_and_note = parse_location_name(location_dat)
        >>> print(dat_and_note)
        ('Abercynon', 'formerly Abercynon South')

        >>> location_dat = 'Allerton (reopened as Liverpool South Parkway)'
        >>> dat_and_note = parse_location_name(location_dat)
        >>> print(dat_and_note)
        ('Allerton', 'reopened as Liverpool South Parkway')

        >>> location_dat = 'Ashford International [domestic portion]'
        >>> dat_and_note = parse_location_name(location_dat)
        >>> print(dat_and_note)
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


def parse_date(str_date, as_date_type=False):
    """
    Parse a date.

    :param str_date: string-type date
    :type str_date: str
    :param as_date_type: whether to return the date as `datetime.date`_,
        defaults to ``False``
    :type as_date_type: bool
    :return: parsed date as a string or `datetime.date`_
    :rtype: str or datetime.date

    .. _`datetime.date`: https://docs.python.org/3/library/datetime.html#datetime.date

    **Examples**::

        >>> from pyrcs.utils import parse_date

        >>> str_date_dat = '2020-01-01'

        >>> parsed_date_dat = parse_date(str_date_dat, as_date_type=True)
        >>> print(parsed_date_dat)
        2020-01-01
        >>> type(parsed_date_dat)
        <class 'datetime.date'>
    """

    temp_date = dateutil.parser.parse(str_date, fuzzy=True)
    # or, temp_date = datetime.strptime(last_update_date[12:], '%d %B %Y')

    parsed_date = temp_date.date() if as_date_type else str(temp_date.date())

    return parsed_date


# -- Retrieval of useful information ---------------------------------------------------

def get_site_map(update=False, confirmation_required=True, verbose=False):
    """
    Fetch the `site map <http://www.railwaycodes.org.uk/misc/sitemap.shtm>`_
    from the package data.

    :param update: whether to check on update and proceed to update the package data,
        defaults to ``False``
    :type update: bool
    :param confirmation_required: whether to prompt a message for confirmation to proceed,
        defaults to ``True``
    :type confirmation_required: bool
    :param verbose: whether to print relevant information in console as the function runs,
        defaults to ``False``
    :type verbose: bool or int
    :return: dictionary of site map data
    :rtype: dict or None

    **Examples**::

        >>> from pyrcs.utils import get_site_map

        >>> site_map_dat = get_site_map()

        >>> type(site_map_dat)
        <class 'dict'>
        >>> print(list(site_map_dat.keys()))
        ['Home', 'Line data', 'Other assets', '"Legal/financial" lists', 'Miscellaneous']
        >>> print(site_map_dat['Home'])
        http://www.railwaycodes.org.uk/index.shtml

        >>> site_map_dat = get_site_map(update=True, verbose=2)
    """

    path_to_pickle = cd_dat("site-map.pickle", mkdir=True)

    if os.path.isfile(path_to_pickle) and not update:
        site_map = load_pickle(path_to_pickle)

    else:
        site_map = None

        if confirmed("To collect the site map?",
                     confirmation_required=confirmation_required):

            if verbose == 2:
                print("Updating the package data", end=" ... ")

            url = urllib.parse.urljoin(homepage_url(), '/misc/sitemap.shtm')

            try:
                source = requests.get(url, headers=fake_requests_headers())
            except requests.exceptions.ConnectionError:
                print_conn_err(update=update, verbose=True if update else verbose)

            else:
                try:
                    soup = bs4.BeautifulSoup(source.text, 'lxml')

                    # <h3>
                    h3 = [x.get_text(strip=True) for x in soup.find_all('h3')]

                    site_map = {}

                    # Next <ol>
                    next_ol = soup.find('h3').find_next('ol')

                    for i in range(len(h3)):

                        li_tag = next_ol.findChildren('li')
                        ol_tag = next_ol.findChildren('ol')

                        if not ol_tag:
                            dat_ = [x.find('a').get('href') for x in li_tag]
                            if len(dat_) == 1:
                                dat = urllib.parse.urljoin(homepage_url(), dat_[0])
                            else:
                                dat = [urllib.parse.urljoin(homepage_url(), x) for x in dat_]
                            site_map.update({h3[i]: dat})

                        else:
                            site_map_ = {}
                            for ol in ol_tag:
                                k = ol.find_parent('ol').find_previous('li').get_text(
                                    strip=True)

                                if k not in site_map_.keys():
                                    sub_li = ol.findChildren('li')
                                    sub_ol = ol.findChildren('ol')

                                    if sub_ol:
                                        cat0 = [x.get_text(strip=True) for x in sub_li
                                                if not x.find('a')]
                                        dat0 = [[urllib.parse.urljoin(homepage_url(),
                                                                      a.get('href'))
                                                 for a in x.find_all('a')] for x in sub_ol]
                                        cat_name = ol.find_previous('li').get_text(strip=True)
                                        if cat0:
                                            site_map_.update(
                                                {cat_name: dict(zip(cat0, dat0))})
                                        else:
                                            site_map_.update(
                                                {cat_name: [x_ for x in dat0 for x_ in x]})
                                        # cat_ = [x for x in cat_ if x not in cat0]

                                    else:
                                        cat_name_ = ol.find_previous('li').get_text(
                                            strip=True)
                                        pat = r'.+(?= \(the thousands of mileage files)'
                                        cat_name = re.search(pat, cat_name_).group(0) \
                                            if re.match(pat, cat_name_) else cat_name_

                                        dat0 = [urllib.parse.urljoin(homepage_url(),
                                                                     x.a.get('href'))
                                                for x in sub_li]

                                        site_map_.update({cat_name: dat0})

                            site_map.update({h3[i]: site_map_})

                        if i < len(h3) - 1:
                            next_ol = next_ol.find_next('h3').find_next('ol')

                    print("Done. ") if verbose == 2 else ""

                    if site_map is not None:
                        save_pickle(site_map, path_to_pickle, verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(e))

        else:
            print("Cancelled. ") if verbose == 2 else ""
            site_map = load_pickle(path_to_pickle)

    return site_map


def get_last_updated_date(url, parsed=True, as_date_type=False, verbose=False):
    """
    Get last update date.

    :param url: URL link of a requested web page
    :type url: str
    :param parsed: whether to reformat the date, defaults to ``True``
    :type parsed: bool
    :param as_date_type: whether to return the date as `datetime.date`_,
        defaults to ``False``
    :type as_date_type: bool
    :param verbose: whether to print relevant information in console as the function runs,
        defaults to ``False``
    :type verbose: bool or int
    :return: date of when the specified web page was last updated
    :rtype: str or datetime.date or None

    .. _`datetime.date`: https://docs.python.org/3/library/datetime.html#datetime.date

    **Examples**::

        >>> from pyrcs.utils import get_last_updated_date

        >>> last_upd_date = get_last_updated_date(
        ...     url='http://www.railwaycodes.org.uk/crs/CRSa.shtm', parsed=True,
        ...     as_date_type=False)
        >>> type(last_upd_date)
        <class 'str'>

        >>> last_upd_date = get_last_updated_date(
        ...     url='http://www.railwaycodes.org.uk/crs/CRSa.shtm', parsed=True,
        ...     as_date_type=True)
        >>> type(last_upd_date)
        <class 'datetime.date'>

        >>> last_upd_date = get_last_updated_date(
        ...     url='http://www.railwaycodes.org.uk/linedatamenu.shtm')
        >>> print(last_upd_date)
        None
    """

    last_update_date = None

    # Request to get connected to the given url
    try:
        source = requests.get(url, headers=fake_requests_headers())
    except requests.exceptions.ConnectionError:
        print_connection_error(verbose=verbose)

    else:
        web_page_text = source.text

        # Parse the text scraped from the requested web page
        parsed_text = bs4.BeautifulSoup(web_page_text, 'lxml')
        # Find 'Last update date'
        update_tag = parsed_text.find('p', {'class': 'update'})

        if update_tag is not None:
            last_update_date = update_tag.text

            # Decide whether to convert the date's format
            if parsed:
                # Convert the date to "yyyy-mm-dd" format
                last_update_date = parse_date(last_update_date, as_date_type)

        # else:
        #     last_update_date = None  # print('Information not available.')

    return last_update_date


def get_catalogue(page_url, update=False, confirmation_required=True, json_it=True,
                  verbose=False):
    """
    Get the catalogue for a class.

    :param page_url: URL of the main page of a code category
    :type page_url: str
    :param update: whether to check on update and proceed to update the package data,
        defaults to ``False``
    :type update: bool
    :param confirmation_required: whether to prompt a message for confirmation to proceed,
        defaults to ``True``
    :type confirmation_required: bool
    :param json_it: whether to save the catalogue as a .json file, defaults to ``True``
    :type json_it: bool
    :param verbose: whether to print relevant information in console as the function runs,
        defaults to ``False``
    :type verbose: bool or int
    :return: catalogue in the form {'<title>': '<URL>'}
    :rtype: dict or None

    **Examples**::

        >>> from pyrcs.utils import get_catalogue

        >>> url = 'http://www.railwaycodes.org.uk/elrs/elr0.shtm'
        >>> catalog = get_catalogue(url)
        >>> type(catalog)
        <class 'dict'>
        >>> print(list(catalog.keys())[:5])
        ['Introduction', 'A', 'B', 'C', 'D']

        >>> url = 'http://www.railwaycodes.org.uk/linedatamenu.shtm'
        >>> catalog = get_catalogue(url)
        >>> print(list(catalog.keys())[:5])
        ['Line data']

        >>> line_data_catalog = catalog['Line data']
        >>> type(line_data_catalog)
        <class 'dict'>
    """

    cat_json = '-'.join(x for x in urllib.parse.urlparse(page_url).path.replace(
        '.shtm', '.json').split('/') if x)
    path_to_cat_json = cd_dat("catalogue", cat_json, mkdir=True)

    if os.path.isfile(path_to_cat_json) and not update:
        catalogue = load_json(path_to_cat_json)

    else:
        catalogue = None

        if confirmed("To collect/update catalogue?",
                     confirmation_required=confirmation_required):

            try:
                source = requests.get(page_url, headers=fake_requests_headers())
            except requests.exceptions.ConnectionError:
                print_connection_error(verbose=verbose)

            else:
                try:
                    source_text = source.text
                    source.close()

                    try:
                        cold_soup = bs4.BeautifulSoup(
                            source_text, 'lxml').find('div', attrs={'class': 'fixed'})
                        catalogue = {
                            a.get_text(strip=True):
                                urllib.parse.urljoin(page_url, a.get('href'))
                            for a in cold_soup.find_all('a')}
                    except AttributeError:
                        cold_soup = bs4.BeautifulSoup(
                            source_text, 'lxml').find('h1').find_all_next('a')
                        catalogue = {
                            a.get_text(strip=True):
                                urllib.parse.urljoin(page_url, a.get('href'))
                            for a in cold_soup}

                    if json_it and catalogue is not None:
                        save_json(catalogue, path_to_cat_json, verbose=verbose)

                except Exception as e:
                    print("Failed to get the category menu. {}".format(e))

        else:
            print("The catalogue for the requested data has not been acquired.")

    return catalogue


def get_category_menu(menu_url, update=False, confirmation_required=True, json_it=True,
                      verbose=False):
    """
    Get a menu of the available classes.

    :param menu_url: URL of the menu page
    :type menu_url: str
    :param update: whether to check on update and proceed to update the package data,
        defaults to ``False``
    :type update: bool
    :param confirmation_required: whether to prompt a message for confirmation to proceed,
        defaults to ``True``
    :type confirmation_required: bool
    :param json_it: whether to save the catalogue as a .json file, defaults to ``True``
    :type json_it: bool
    :param verbose: whether to print relevant information in console as the function runs,
        defaults to ``False``
    :type verbose: bool or int
    :return: a category menu
    :rtype: dict or None

    **Example**::

        >>> from pyrcs.utils import get_category_menu

        >>> url = 'http://www.railwaycodes.org.uk/linedatamenu.shtm'
        >>> menu = get_category_menu(url)

        >>> type(menu)
        <class 'dict'>
        >>> print(list(menu.keys()))
        ['Line data']
    """

    menu_json = '-'.join(x for x in urllib.parse.urlparse(menu_url).path.replace(
        '.shtm', '.json').split('/') if x)
    path_to_menu_json = cd_dat("catalogue", menu_json, mkdir=True)

    if os.path.isfile(path_to_menu_json) and not update:
        cls_menu = load_json(path_to_menu_json)

    else:
        cls_menu = None

        if confirmed("To collect/update category menu?",
                     confirmation_required=confirmation_required):

            try:
                source = requests.get(menu_url, headers=fake_requests_headers())
            except requests.exceptions.ConnectionError:
                print_connection_error(verbose=verbose)

            else:
                try:
                    soup = bs4.BeautifulSoup(source.text, 'lxml')
                    h1, h2s = soup.find('h1'), soup.find_all('h2')

                    cls_name = h1.text.replace(' menu', '')

                    if len(h2s) == 0:
                        cls_elem = dict(
                            (x.text, urllib.parse.urljoin(menu_url, x.get('href')))
                            for x in h1.find_all_next('a'))

                    else:
                        all_next = [x.replace(':', '')
                                    for x in h1.find_all_next(string=True)
                                    if x != '\n' and x != '\xa0'][2:]
                        h2s_list = [x.text.replace(':', '') for x in h2s]
                        all_next_a = [
                            (x.text, urllib.parse.urljoin(menu_url, x.get('href')))
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
                        save_json(cls_menu, path_to_menu_json, verbose=verbose)

                except Exception as e:
                    print("Failed to get the category menu. {}".format(e))

        else:
            print("The category menu has not been acquired.")

    return cls_menu


# -- Rectification of location names ---------------------------------------------------

def fetch_loc_names_repl_dict(k=None, regex=False, as_dataframe=False):
    """
    Create a dictionary for rectifying location names.

    :param k: key of the created dictionary, defaults to ``None``
    :type k: str or int or float or bool or None
    :param regex: whether to create a dictionary for replacement
        based on regular expressions, defaults to ``False``
    :type regex: bool
    :param as_dataframe: whether to return the created dictionary as a pandas.DataFrame,
        defaults to ``False``
    :type as_dataframe: bool
    :return: dictionary for rectifying location names
    :rtype: dict or pandas.DataFrame

    **Examples**::

        >>> from pyrcs.utils import fetch_loc_names_repl_dict

        >>> repl_dict = fetch_loc_names_repl_dict()
        >>> type(repl_dict)
        <class 'dict'>
        >>> print(list(repl_dict.keys())[:5])
        ['"Tyndrum Upper" (Upper Tyndrum)',
         'AISH EMERGENCY CROSSOVER',
         'ATLBRJN',
         'Aberdeen Craiginches',
         'Aberdeen Craiginches T.C.']

        >>> repl_dict = fetch_loc_names_repl_dict(regex=True, as_dataframe=True)
        >>> type(repl_dict)
        <class 'pandas.core.frame.DataFrame'>
        >>> print(repl_dict.head())
                                         new_value
        re.compile(' \\(DC lines\\)')   [DC lines]
        re.compile(' And | \\+ ')               &
        re.compile('-By-')                    -by-
        re.compile('-In-')                    -in-
        re.compile('-En-Le-')              -en-le-
    """

    json_filename = "location-names-repl{}.json".format("" if not regex else "-regex")
    location_name_repl_dict = load_json(cd_dat(json_filename))

    if regex:
        location_name_repl_dict = {re.compile(k): v
                                   for k, v in location_name_repl_dict.items()}

    replacement_dict = {k: location_name_repl_dict} if k else location_name_repl_dict

    if as_dataframe:
        replacement_dict = pd.DataFrame.from_dict(replacement_dict, orient='index',
                                                  columns=['new_value'])

    return replacement_dict


def update_loc_names_repl_dict(new_items, regex, verbose=False):
    """
    Update the location-names replacement dictionary in the package data.

    :param new_items: new items to replace
    :type new_items: dict
    :param regex: whether this update is for regular-expression dictionary
    :type regex: bool
    :param verbose: whether to print relevant information in console as the function runs,
        defaults to ``False``
    :type verbose: bool or int

    **Example**:

        >>> from pyrcs.utils import update_loc_names_repl_dict

        >>> new_items_ = {}
        >>> update_loc_names_repl_dict(new_items_, regex=False)
    """

    json_filename = "location-names-repl{}.json".format("" if not regex else "-regex")

    new_items_keys = list(new_items.keys())

    if confirmed("To update \"{}\" with {{\"{}\"... }}?".format(
            json_filename, new_items_keys[0])):
        path_to_json = cd_dat(json_filename)
        location_name_repl_dict = load_json(path_to_json)

        if any(isinstance(k, re.Pattern) for k in new_items_keys):
            new_items = {k.pattern: v for k, v in new_items.items()
                         if isinstance(k, re.Pattern)}

        location_name_repl_dict.update(new_items)

        save_json(location_name_repl_dict, path_to_json, verbose=verbose)


# -- Data fixers -----------------------------------------------------------------------

def fix_num_stanox(stanox_code):
    """
    Fix 'STANOX' if it is loaded as numbers.

    :param stanox_code: STANOX code
    :type stanox_code: str or int
    :return: standard STANOX code
    :rtype: str

    **Examples**::

        >>> from pyrcs.utils import fix_num_stanox

        >>> stanox = 65630
        >>> stanox_ = fix_num_stanox(stanox)
        >>> type(stanox_)
        <class 'str'>

        >>> stanox = 2071
        >>> stanox_ = fix_num_stanox(stanox)
        >>> print(stanox_)
        02071
    """

    if isinstance(stanox_code, (int or float)):
        stanox_code = '' if pd.isna(stanox_code) else str(int(stanox_code))

    if len(stanox_code) < 5 and stanox_code != '':
        stanox_code = '0' * (5 - len(stanox_code)) + stanox_code

    return stanox_code


def fix_nr_mileage_str(nr_mileage):
    """
    Fix Network Rail mileage.

    :param nr_mileage: NR mileage
    :type nr_mileage: str or float
    :return: conventional NR mileage code
    :rtype: str

    **Examples**::

        >>> from pyrcs.utils import fix_nr_mileage_str

        >>> mileage = 29.011
        >>> mileage_ = fix_nr_mileage_str(mileage)
        >>> print(mileage_)
        29.0110

        >>> mileage = '.1100'
        >>> mileage_ = fix_nr_mileage_str(mileage)
        >>> print(mileage_)
        0.1100
    """

    if isinstance(nr_mileage, float):
        nr_mileage_ = fix_nr_mileage_str(str(nr_mileage))

    elif nr_mileage and nr_mileage != '0':
        if '.' in nr_mileage:
            miles, yards = nr_mileage.split('.')
            if miles == '':
                miles = '0'
        else:
            miles, yards = nr_mileage, '0'
        if len(yards) < 4:
            yards += '0' * (4 - len(yards))
        nr_mileage_ = '.'.join([miles, yards])

    else:
        nr_mileage_ = nr_mileage

    return nr_mileage_


# -- Miscellaneous helpers -------------------------------------------------------------

def print_connection_error(verbose=False):
    """
    Print a message about unsuccessful attempts to establish a connection to the Internet.

    :param verbose: whether to print relevant information in console as the function runs,
        defaults to ``False``
    :type verbose: bool or int
    """

    if verbose:
        print("Failed to establish an Internet connection. "
              "The current instance relies on local backup.")


def print_conn_err(update=False, verbose=False):
    """
    Print a message about unsuccessful attempts to establish a connection to the Internet
    for an instance of a class.

    :param update: defaults to ``False``
        (mostly complies with ``update`` in a parent function that uses this function)
    :type update: bool
    :param verbose: whether to print relevant information in console as the function runs,
        defaults to ``False``
    :type verbose: bool or int
    """

    msg = "The Internet connection is not available."
    if update and verbose:
        print(msg + " Failed to update the data.")
    elif verbose:
        print(msg)


def is_str_float(str_val):
    """
    Check if a string-type variable can express a float-type value.

    :param str_val: a string-type variable
    :type str_val: str
    :return: whether ``str_val`` can express a float value
    :rtype: bool

    **Examples**::

        >>> from pyrcs.utils import is_str_float

        >>> is_str_float('')
        False

        >>> is_str_float('a')
        False

        >>> is_str_float('1')
        True

        >>> is_str_float('1.1')
        True
    """

    try:
        float(str_val)  # float(re.sub('[()~]', '', text))
        test_res = True
    except ValueError:
        test_res = False

    return test_res


def is_internet_connected():
    """
    Check the Internet connection.

    :return: whether the machine is currently connected to the Internet
    :rtype: bool

    **Examples**::

        >>> from pyrcs.utils import is_internet_connected

        >>> is_internet_connected()
    """

    try:
        netloc = urllib.parse.urlparse(homepage_url()).netloc
        host = socket.gethostbyname(netloc)
        s = socket.create_connection((host, 80))
        s.close()
        return True
    except (socket.gaierror, OSError):
        return False
