""" Utilities - Helper functions """

import collections
import datetime
import os
import re
import urllib.parse

import bs4
import dateutil.parser
import fake_useragent
import measurement.measures
import numpy as np
import pandas as pd
import pkg_resources
import requests
from pyhelpers.ops import confirmed
from pyhelpers.store import load_json, load_pickle, save_json, save_pickle


def homepage_url():
    """
    Specify the homepage URL of the data source.

    :return: URL of the data source homepage
    :rtype: str
    """
    return 'http://www.railwaycodes.org.uk/'


# -- Directory ----------------------------------------------------------------------------------------

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

        from pyrcs.utils import cd_dat

        dat_dir = "dat"
        mkdir = False

        cd_dat("line-data", dat_dir=dat_dir, mkdir=mkdir)
        # "\\dat\\line-data"
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


# -- Converters ---------------------------------------------------------------------------------------

def mile_chain_to_nr_mileage(miles_chains):
    """
    Convert mileage data in the form '<miles>.<chains>' to Network Rail mileage.

    :param miles_chains: mileage data presented in the form '<miles>.<chains>'
    :type miles_chains: str, numpy.nan, None
    :return: Network Rail mileage in the form '<miles>.<yards>'
    :rtype: str

    **Examples**::

        from pyrcs.utils import mile_chain_to_nr_mileage

        miles_chains = '0.18'  # AAM 0.18 Tewkesbury Junction with ANZ (84.62)
        mile_chain_to_nr_mileage(miles_chains)  # '0.0396'

        miles_chains = None  # or np.nan, or ''
        mile_chain_to_nr_mileage(miles_chains)  # ''
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
    :type str_mileage: str, numpy.nan, None
    :return: '<miles>.<chains>'
    :rtype: str

    **Examples**::

        from pyrcs.utils import nr_mileage_to_mile_chain

        str_mileage = '0.0396'
        nr_mileage_to_mile_chain(str_mileage)  # '0.18'

        str_mileage = None  # or np.nan, or ''
        nr_mileage_to_mile_chain(str_mileage)  # ''
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

        from pyrcs.utils import nr_mileage_str_to_num

        str_mileage = '0.0396'
        nr_mileage_str_to_num(str_mileage)  # 0.0396

        str_mileage = ''
        nr_mileage_str_to_num(str_mileage)  # nan
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

        import numpy as np
        from pyrcs.utils import nr_mileage_num_to_str

        num_mileage = 0.0396
        nr_mileage_num_to_str(num_mileage)  # '0.0396'

        num_mileage = np.nan
        nr_mileage_num_to_str(num_mileage)  # ''
    """

    nr_mileage = '%.4f' % round(float(num_mileage), 4) if num_mileage and pd.notna(num_mileage) else ''
    return nr_mileage


def nr_mileage_to_yards(nr_mileage):
    """
    Convert Network Rail mileages to yards.

    :param nr_mileage: Network Rail mileage
    :type nr_mileage: float, str
    :return: yards
    :rtype: int

    **Examples**::

        from pyrcs.utils import nr_mileage_to_yards

        nr_mileage = '0.0396'
        nr_mileage_to_yards(nr_mileage)  # 396

        nr_mileage = 0.0396
        nr_mileage_to_yards(nr_mileage)  # 396
    """

    if isinstance(nr_mileage, (float, np.float, int, np.integer)):
        nr_mileage = nr_mileage_num_to_str(nr_mileage)
    else:
        pass
    miles = int(nr_mileage.split('.')[0])
    yards = int(nr_mileage.split('.')[1])
    yards += int(measurement.measures.Distance(mi=miles).yd)
    return yards


def yards_to_nr_mileage(yards):
    """
    Convert yards to Network Rail mileages.

    :param yards: yards
    :type yards: int, float, numpy.nan, None
    :return: Network Rail mileage in the form '<miles>.<yards>'
    :rtype: str

    **Examples**::

        from pyrcs.utils import yards_to_nr_mileage

        yards = 396
        yards_to_nr_mileage(yards)  # '0.0396'

        yards = 396.0
        yards_to_nr_mileage(yards)  # '0.0396'

        yards = None
        yards_to_nr_mileage(yards)  # ''
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
    :type nr_mileage: float, int, str
    :param shift_yards: yards by which the given ``nr_mileage`` is shifted
    :type shift_yards: int, float
    :return: shifted numerical Network Rail mileage
    :rtype: float

    **Examples**::

        from pyrcs.utils import shift_num_nr_mileage

        nr_mileage = '0.0396'  # or 0.0396
        shift_yards = 220
        shift_num_nr_mileage(nr_mileage, shift_yards)  # 0.0616

        nr_mileage = '0.0396'
        shift_yards = 220.99
        shift_num_nr_mileage(nr_mileage, shift_yards)  # 0.0617

        nr_mileage = 10
        shift_yards = 220
        shift_num_nr_mileage(nr_mileage, shift_yards)  # 10.022
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

        from pyrcs.utils import year_to_financial_year

        date = datetime.datetime.now()

        year_to_financial_year(date)  # 2020
    """

    financial_date = date + pd.DateOffset(months=-3)
    return financial_date.year


# -- Parsers ------------------------------------------------------------------------------------------

def parse_tr(header, trs):
    """
    Parse a list of parsed HTML <tr> elements.

    .. _parse-tr:

    See also [`PT-1 <https://stackoverflow.com/questions/28763891/>`_].

    :param header: list of column names of a requested table
    :type header: list
    :param trs: contents under <tr> tags of a web page
    :type trs: bs4.ResultSet - list of bs4.Tag
    :return: list of lists with each comprising a row of the requested table
    :rtype: list

    **Example**::

        import bs4
        import fake_useragent
        from pyrcs.utils import fake_requests_headers, parse_tr

        source = requests.get(
            'http://www.railwaycodes.org.uk/elrs/elra.shtm',
            headers=fake_requests_headers())
        parsed_text = bs4.BeautifulSoup(source.text, 'lxml')
        header = [x.text for x in parsed_text.find_all('th')]  # Column names
        trs = parsed_text.find_all('tr')

        parse_tr(header, trs)  # returns a list of lists
    """

    tbl_lst = []
    for row in trs:
        data = []
        for dat in row.find_all('td'):
            txt = dat.get_text()
            if '\n' in txt:
                t = txt.split('\n')
                txt = '%s (%s)' % (t[0], t[1:]) if '(' not in txt and ')' not in txt else '%s %s' % (t[0], t[1:])
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
    :return:
        - a list of lists each comprising a row of the requested table (see also :ref:`parse_tr() <parse-tr>`) and
        - a list of column names of the requested table
    :rtype: tuple

    **Examples**::

        import bs4
        import fake_useragent
        from pyrcs.utils import fake_requests_headers, parse_table

        source = requests.get(
            'http://www.railwaycodes.org.uk/elrs/elra.shtm',
            headers=fake_requests_headers())
        parser = 'lxml'

        parse_table(source, parser)
    """

    # Get plain text from the source URL
    web_page_text = source.text  # (If source.status_code == 200, the requested URL is available.)
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
    :type location_name: str, None
    :return: location name and, if any, note
    :rtype: tuple

    **Examples**::

        from pyrcs.utils import parse_location_name

        location_dat = 'Abbey Wood'
        parse_location_name(location_dat)
        # ('Abbey Wood', '')

        location_dat = None
        parse_location_name(location_dat)
        # ('', '')

        location_dat = 'Abercynon (formerly Abercynon South)'
        parse_location_name(location_dat)
        # ('Abercynon', 'formerly Abercynon South')

        location_dat = 'Allerton (reopened as Liverpool South Parkway)'
        parse_location_name(location_dat)
        # ('Allerton', 'reopened as Liverpool South Parkway')

        location_dat = 'Ashford International [domestic portion]'
        parse_location_name(location_dat)
        # ('Ashford International', 'domestic portion')
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
                r'[Oo]riginally |[Ff]ormerly |[Ll]ater |[Pp]resumed | \(was | \(in | \(at | \(also |'
                r' \(second code |\?|\n| \(\[\'| \(definition unknown\)| \(reopened |( portion])$')
            x_tmp = re.search(r'(?=[\[(]).*(?<=[\])])|(?=\().*(?<=\) \[)', location_name)
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
                n = re.search(r'(?<=(\[[\'\"]\()|(\([\'\"]\[)|(\) \[)).*(?=(\)[\'\"]\])|(\][\'\"]\))|\])', y)
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
    :param as_date_type: whether to return the date as `datetime.date`_, defaults to ``False``
    :type as_date_type: bool
    :return: parsed date as a string or `datetime.date`_
    :rtype: str, datetime.date

    .. _`datetime.date`: https://docs.python.org/3/library/datetime.html#datetime.date

    **Examples**::

        from pyrcs.utils import parse_date

        str_date = '2020-01-01'

        as_date_type = True
        parse_date(str_date, as_date_type)  # datetime.date(2020, 1, 1)
    """

    temp_date = dateutil.parser.parse(str_date, fuzzy=True)
    # or, temp_date = datetime.strptime(last_update_date[12:], '%d %B %Y')

    parsed_date = temp_date.date() if as_date_type else str(temp_date.date())

    return parsed_date


# -- Get useful information ---------------------------------------------------------------------------

def fake_requests_headers(random=False):
    """
    Make a fake HTTP headers for `requests.get`_.

    .. _`requests.get`: https://requests.readthedocs.io/en/master/user/advanced/#request-and-response-objects

    :param random: whether to go for a random agent, defaults to ``False``
    :type random: bool
    :return: fake HTTP headers
    :rtype: dict
    """

    fake_user_agent = fake_useragent.UserAgent()
    fake_header = {'User-Agent': fake_user_agent.random if random else fake_user_agent.chrome}
    return fake_header


def get_last_updated_date(url, parsed=True, as_date_type=False):
    """
    Get last update date.

    :param url: URL link of a requested web page
    :type url: str
    :param parsed: whether to reformat the date, defaults to ``True``
    :type parsed: bool
    :param as_date_type: whether to return the date as `datetime.date`_, defaults to ``False``
    :type as_date_type: bool
    :return: date of when the specified web page was last updated
    :rtype: str, datetime.date, None

    .. _`datetime.date`: https://docs.python.org/3/library/datetime.html#datetime.date

    **Examples**::

        from pyrcs.utils import get_last_updated_date

        parsed = True

        url = 'http://www.railwaycodes.org.uk/crs/CRSa.shtm'

        date_type = False
        get_last_updated_date(url, parsed, date_type)
        # '<year>-<month>-<day>'

        date_type = True
        get_last_updated_date(url, parsed, date_type)
        # datetime.date(<year>, <month>, <day>)

        url = 'http://www.railwaycodes.org.uk/linedatamenu.shtm'
        get_last_updated_date(url, parsed, date_type)
        # None
    """

    # Request to get connected to the given url
    source = requests.get(url, headers=fake_requests_headers())
    web_page_text = source.text
    # Parse the text scraped from the requested web page
    parsed_text = bs4.BeautifulSoup(web_page_text, 'lxml')  # (Alternative parsers: 'html5lib', 'html.parser')
    # Find 'Last update date'
    update_tag = parsed_text.find('p', {'class': 'update'})
    if update_tag is not None:
        last_update_date = update_tag.text
        # Decide whether to convert the date's format
        if parsed:
            # Convert the date to "yyyy-mm-dd" format
            last_update_date = parse_date(last_update_date, as_date_type)
    else:
        last_update_date = None  # print('Information not available.')
    return last_update_date


def get_catalogue(page_url, update=False, confirmation_required=True, json_it=True, verbose=False):
    """
    Get the catalogue for a class.

    :param page_url: URL of the main page of a code category
    :type page_url: str
    :param update: whether to check on update and proceed to update the package data, defaults to ``False``
    :type update: bool
    :param confirmation_required: whether to prompt a message for confirmation to proceed, defaults to ``True``
    :type confirmation_required: bool
    :param json_it: whether to save the catalogue as a .json file, defaults to ``True``
    :type json_it: bool
    :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
    :type verbose: bool
    :return: catalogue in the form {'<title>': '<URL>'}
    :rtype: dict

    **Examples**::

        from pyrcs.utils import get_catalogue

        update = False
        verbose = True

        page_url = 'http://www.railwaycodes.org.uk/elrs/elr0.shtm'
        confirmation_required = True
        catalogue = get_catalogue(page_url, update, confirmation_required, verbose)

        page_url = 'http://www.railwaycodes.org.uk/linedatamenu.shtm'
        confirmation_required = False
        catalogue = get_catalogue(page_url, update, confirmation_required, verbose)
    """

    cat_json = '-'.join(x for x in urllib.parse.urlparse(page_url).path.replace('.shtm', '.json').split('/') if x)
    path_to_cat_json = cd_dat("catalogue", cat_json)

    if os.path.isfile(path_to_cat_json) and not update:
        catalogue = load_json(path_to_cat_json, verbose=verbose)

    else:
        if confirmed("To collect/update catalogue? ", confirmation_required=confirmation_required):

            source = requests.get(page_url, headers=fake_requests_headers())
            source_text = source.text
            source.close()

            try:
                cold_soup = bs4.BeautifulSoup(source_text, 'lxml').find('div', attrs={'class': 'fixed'})
                catalogue = {a.get_text(strip=True): urllib.parse.urljoin(page_url, a.get('href'))
                             for a in cold_soup.find_all('a')}
            except AttributeError:
                cold_soup = bs4.BeautifulSoup(source_text, 'lxml').find('h1').find_all_next('a')
                catalogue = {a.get_text(strip=True): urllib.parse.urljoin(page_url, a.get('href'))
                             for a in cold_soup}

            if json_it:
                save_json(catalogue, path_to_cat_json, verbose=verbose)

        else:
            print("The catalogue for the requested data has not been acquired.")
            catalogue = None

    return catalogue


def get_category_menu(menu_url, update=False, confirmation_required=True, json_it=True, verbose=False):
    """
    Get a menu of the available classes.

    :param menu_url: URL of the menu page
    :type menu_url: str
    :param update: whether to check on update and proceed to update the package data, defaults to ``False``
    :type update: bool
    :param confirmation_required: whether to prompt a message for confirmation to proceed, defaults to ``True``
    :type confirmation_required: bool
    :param json_it: whether to save the catalogue as a .json file, defaults to ``True``
    :type json_it: bool
    :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
    :type verbose: bool
    :return:
    :rtype: dict

    **Example**::

        from pyrcs.utils import get_category_menu

        update = False
        confirmation_required = True
        verbose = True

        menu_url = 'http://www.railwaycodes.org.uk/linedatamenu.shtm'
        cls_menu = get_category_menu(menu_url)

        print(cls_menu)
        # {'<category name>': {'<title>': '<URL>'}}
    """

    menu_json = '-'.join(x for x in urllib.parse.urlparse(menu_url).path.replace('.shtm', '.json').split('/') if x)
    path_to_menu_json = cd_dat("catalogue", menu_json)

    if os.path.isfile(path_to_menu_json) and not update:
        cls_menu = load_json(path_to_menu_json, verbose=verbose)

    else:
        if confirmed("To collect/update category menu? ", confirmation_required=confirmation_required):

            source = requests.get(menu_url, headers=fake_requests_headers())

            soup = bs4.BeautifulSoup(source.text, 'lxml')
            h1, h2s = soup.find('h1'), soup.find_all('h2')

            cls_name = h1.text.replace(' menu', '')

            if len(h2s) == 0:
                cls_elem = dict((x.text, urllib.parse.urljoin(menu_url, x.get('href'))) for x in h1.find_all_next('a'))

            else:
                all_next = [x.replace(':', '') for x in h1.find_all_next(string=True) if x != '\n' and x != '\xa0'][2:]
                h2s_list = [x.text.replace(':', '') for x in h2s]
                all_next_a = [(x.text, urllib.parse.urljoin(menu_url, x.get('href')))
                              for x in h1.find_all_next('a', href=True)]

                idx = [all_next.index(x) for x in h2s_list]
                for i in idx:
                    all_next_a.insert(i, all_next[i])

                cls_elem, i = {}, 0
                while i <= len(idx):
                    if i == 0:
                        d = dict(all_next_a[i:idx[i]])
                    elif i < len(idx):
                        d = {h2s_list[i - 1]: dict(all_next_a[idx[i - 1] + 1:idx[i]])}
                    else:
                        d = {h2s_list[i - 1]: dict(all_next_a[idx[i - 1] + 1:])}
                    i += 1
                    cls_elem.update(d)

            cls_menu = {cls_name: cls_elem}

            if json_it:
                save_json(cls_menu, path_to_menu_json, verbose=verbose)

        else:
            print("The category menu has not been acquired.")
            cls_menu = None

    return cls_menu


def get_station_data_catalogue(source_url, source_key, update=False):
    """
    Get catalogue of railway station data.

    :param source_url: URL to the source web page
    :type source_url: str
    :param source_key: key of the returned catalogue (which is a dictionary)
    :type source_key: str
    :param update: whether to check on update and proceed to update the package data, defaults to ``False``
    :type update: bool
    :return: catalogue of railway station data
    :rtype: dict
    """

    cat_json = '-'.join(x for x in urllib.parse.urlparse(source_url).path.replace('.shtm', '.json').split('/') if x)
    path_to_cat = cd_dat("catalogue", cat_json)

    if os.path.isfile(path_to_cat) and not update:
        catalogue = load_json(path_to_cat)

    else:
        source = requests.get(source_url, headers=fake_requests_headers())
        cold_soup = bs4.BeautifulSoup(source.text, 'lxml').find('p', {'class': 'appeal'}).find_next('p').find_next('p')
        hot_soup = {a.text: urllib.parse.urljoin(source_url, a.get('href')) for a in cold_soup.find_all('a')}

        catalogue = {source_key: None}
        for k, v in hot_soup.items():
            sub_cat = get_catalogue(v, update=True, confirmation_required=False, json_it=False)
            if sub_cat != hot_soup:
                if k == 'Introduction':
                    catalogue.update({source_key: {k: v, **sub_cat}})
                else:
                    catalogue.update({k: sub_cat})
            else:
                if k in ('Bilingual names', 'Not served by SFO'):
                    catalogue[source_key].update({k: v})
                else:
                    catalogue.update({k: v})

        save_json(catalogue, path_to_cat)

    return catalogue


def get_track_diagrams_items(source_url, source_key, update=False):
    """
    Get catalogue of track diagrams.

    :param source_url: URL to the source web page
    :type source_url: str
    :param source_key: key of the returned catalogue (which is a dictionary)
    :type source_key: str
    :param update: whether to check on update and proceed to update the package data, defaults to ``False``
    :type update: bool
    :return: catalogue of railway station data
    :rtype: dict
    """

    cat_json = '-'.join(x for x in urllib.parse.urlparse(source_url).path.replace('.shtm', '.json').split('/') if x)
    path_to_cat = cd_dat("catalogue", cat_json)

    if os.path.isfile(path_to_cat) and not update:
        items = load_pickle(path_to_cat)

    else:
        source = requests.get(source_url, headers=fake_requests_headers())
        soup = bs4.BeautifulSoup(source.text, 'lxml')
        h3 = {x.get_text(strip=True) for x in soup.find_all('h3', text=True, attrs={'class': None})}
        items = {source_key: h3}

        save_pickle(items, path_to_cat)

    return items


# -- Rectification of location names ------------------------------------------------------------------

def fetch_location_names_repl_dict(k=None, regex=False, as_dataframe=False):
    """
    Create a dictionary for rectifying location names.

    :param k: key of the created dictionary, defaults to ``None``
    :type k: str, int, float, bool, None
    :param regex: whether to create a dictionary for replacement based on regular expressions, defaults to ``False``
    :type regex: bool
    :param as_dataframe: whether to return the created dictionary as a pandas.DataFrame, defaults to ``False``
    :type as_dataframe: bool
    :return: dictionary for rectifying location names
    :rtype: dict, pandas.DataFrame

    **Examples**::

        from pyrcs.utils import fetch_location_names_repl_dict

        k = None
        regex = False
        as_dataframe = True
        fetch_location_names_repl_dict(k, regex, as_dataframe)

        regex = True
        as_dataframe = False
        fetch_location_names_repl_dict(k, regex, as_dataframe)
    """

    json_filename = "location-names-repl{}.json".format("" if not regex else "-regex")
    location_name_repl_dict = load_json(cd_dat(json_filename))

    if regex:
        location_name_repl_dict = {re.compile(k): v for k, v in location_name_repl_dict.items()}

    replacement_dict = {k: location_name_repl_dict} if k else location_name_repl_dict

    if as_dataframe:
        replacement_dict = pd.DataFrame.from_dict(replacement_dict, orient='index', columns=['new_value'])

    return replacement_dict


def update_location_name_repl_dict(new_items, regex, verbose=False):
    """
    Update the location-name replacement dictionary in the package data.

    :param new_items: new items to replace
    :type new_items: dict
    :param regex: whether this update is for regular-expression dictionary
    :type regex: bool
    :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
    :type verbose: bool

    **Example**:

        from pyrcs.utils import update_location_name_repl_dict

        verbose = True

        new_items = {}
        regex = False
        update_location_name_repl_dict(new_items, regex, verbose)
    """

    json_filename = "location-names-repl{}.json".format("" if not regex else "-regex")

    new_items_keys = list(new_items.keys())

    if confirmed("To update \"{}\" with {{\"{}\"... }}?".format(json_filename, new_items_keys[0])):
        path_to_json = cd_dat(json_filename)
        location_name_repl_dict = load_json(path_to_json)

        if any(isinstance(k, re.Pattern) for k in new_items_keys):
            new_items = {k.pattern: v for k, v in new_items.items() if isinstance(k, re.Pattern)}

        location_name_repl_dict.update(new_items)

        save_json(location_name_repl_dict, path_to_json, verbose=verbose)


# -- Fixers -------------------------------------------------------------------------------------------

def fix_num_stanox(stanox_code):
    """
    Fix 'STANOX' if it is loaded as numbers.

    :param stanox_code: STANOX code
    :type stanox_code: str, int
    :return: standard STANOX code
    :rtype: str

    **Examples**::

        stanox_code = 65630
        fix_num_stanox(stanox_code)  # '65630'

        stanox_code = 2071
        fix_num_stanox(stanox_code)  # '02071'
    """

    if isinstance(stanox_code, (int, float)):
        stanox_code = '' if pd.isna(stanox_code) else str(int(stanox_code))

    if len(stanox_code) < 5 and stanox_code != '':
        stanox_code = '0' * (5 - len(stanox_code)) + stanox_code

    return stanox_code


# -- Misc ---------------------------------------------------------------------------------------------

def is_str_float(str_val):
    """
    Check if a string-type variable can express a float value.

    :param str_val: a string-type variable
    :type str_val: str
    :return: whether ``str_val`` can express a float value
    :rtype: bool

    **Examples**::

        str_val = ''
        is_str_float(str_val)  # False

        str_val = 'a'
        is_str_float(str_val)  # False

        str_val = '1'
        is_str_float(str_val)  # True

        str_val = '1.1'
        is_str_float(str_val)  # True
    """

    try:
        float(str_val)  # float(re.sub('[()~]', '', text))
        test_res = True
    except ValueError:
        test_res = False
    return test_res
