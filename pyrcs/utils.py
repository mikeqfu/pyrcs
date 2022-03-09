"""
Provide a number of utilities (helper functions).
"""

import calendar
import collections
import copy
import datetime
import numbers
import os
import re
import string
import urllib.parse

import bs4
import dateutil.parser
import numpy as np
import pandas as pd
import pkg_resources
import requests
from pyhelpers.dir import validate_dir
from pyhelpers.ops import confirmed, fake_requests_headers, is_url_connectable
from pyhelpers.store import load_data, save_data
from pyhelpers.text import find_similar_str

""" == Specifications ======================================================================== """


def home_page_url():
    """
    Specify the homepage URL of the data source.

    :return: URL of the data source homepage
    :rtype: str

    **Example**::

        >>> from pyrcs.utils import home_page_url

        >>> home_page_url()
        'http://www.railwaycodes.org.uk/'
    """

    return 'http://www.railwaycodes.org.uk/'


def cd_data(*sub_dir, data_dir="data", mkdir=False, **kwargs):
    """
    Specify (or change to) a directory (or any subdirectories) for backup data of the package.

    :param sub_dir: [optional] name of a directory; names of directories (and/or a filename)
    :type sub_dir: str
    :param data_dir: name of a directory to store data, defaults to ``"data"``
    :type data_dir: str
    :param mkdir: whether to create a directory, defaults to ``False``
    :type mkdir: bool
    :param kwargs: [optional] parameters (e.g. ``mode=0o777``) of `os.makedirs`_
    :return: a full pathname of a directory or a file under the specified data directory ``data_dir``
    :rtype: str

    .. _`os.makedirs`: https://docs.python.org/3/library/os.html#os.makedirs

    **Example**::

        >>> from pyrcs.utils import cd_data
        >>> import os

        >>> path_to_dat_dir = cd_data(data_dir="data")
        >>> os.path.relpath(path_to_dat_dir)
        'pyrcs\\data'
    """

    path = pkg_resources.resource_filename(__name__, data_dir)
    for x in sub_dir:
        path = os.path.join(path, x)

    if mkdir:
        path_to_file, ext = os.path.splitext(path)
        if ext == '':
            os.makedirs(path_to_file, exist_ok=True, **kwargs)
        else:
            os.makedirs(os.path.dirname(path_to_file), exist_ok=True, **kwargs)

    return path


def init_data_dir(cls, data_dir, category, cluster=None, **kwargs):
    """
    Specify an initial data directory for (an instance of) a class for a data cluster.

    :param cls: (an instance of) a class for a certain data cluster
    :type cls: object
    :param data_dir: name of a folder where the pickle file is to be saved
    :type data_dir: str or None
    :param category: name of a data category, e.g. ``"line-data"``
    :type category: str
    :param cluster: replacement for ``cls.KEY``
    :type cluster: str or None
    :param kwargs: [optional] parameters of the function :py:func:`~pyrcs.utils.cd_data`
    :return: pathnames of a default data directory and a current data directory
    :rtype: tuple[str, os.PathLike[str]]

    **Example**::

        >>> from pyrcs.utils import init_data_dir
        >>> from pyrcs.line_data import Bridges
        >>> import os

        >>> bridges = Bridges()

        >>> dat_dir, current_dat_dir = init_data_dir(bridges, data_dir="data", category="line-data")
        >>> os.path.relpath(dat_dir)
        'data'
        >>> os.path.relpath(current_dat_dir)
        'data'
    """

    if data_dir:
        cls.data_dir = validate_dir(data_dir)

    else:
        cluster_ = cls.__getattribute__('KEY') if cluster is None else copy.copy(cluster)
        cls.data_dir = cd_data(category, cluster_.lower().replace(" ", "-"), **kwargs)

    cls.current_data_dir = copy.copy(cls.data_dir)

    return cls.data_dir, cls.current_data_dir


def make_file_pathname(cls, data_name, ext=".pickle", data_dir=None):
    """
    Make a pathname for saving data as a file of a certain format (e.g. ".pickle").

    :param cls: (an instance of) a class for a certain data cluster
    :type cls: object
    :param data_name: key to the dict-type data of a certain code cluster
    :type data_name: str
    :param ext: file extension, defaults to ``".pickle"``
    :type ext: str
    :param data_dir: name of a folder where the data is saved, defaults to ``None``
    :type data_dir: str or None
    :return: a pathname for saving the data
    :rtype: str

    **Example**::

        >>> from pyrcs.utils import make_file_pathname
        >>> from pyrcs.line_data import Bridges
        >>> import os

        >>> bridges = Bridges()

        >>> example_pathname = make_file_pathname(bridges, data_name="example-data", ext=".pickle")
        >>> os.path.relpath(example_pathname)
        'pyrcs\\data\\line-data\\bridges\\example-data.pickle'
    """

    filename = data_name.lower().replace(" ", "-") + ext

    if data_dir is not None:
        cls.current_data_dir = validate_dir(path_to_dir=data_dir)
        file_pathname = os.path.join(cls.current_data_dir, filename)

    else:  # data_dir is None or data_dir == ""
        # func = [x for x in dir(cls) if x.startswith('_cdd')][0]
        file_pathname = getattr(cls, '_cdd')(filename)

    return file_pathname


""" Converters =============================================================================== """


def fix_stanox(stanox):
    """
    Fix the format of a given
    `STANOX (station number) <https://wiki.openraildata.com/index.php?title=STANOX_Areas>`_ code.

    :param stanox: STANOX code
    :type stanox: str or int or None
    :return: standard STANOX code
    :rtype: str

    **Examples**::

        >>> from pyrcs.utils import fix_stanox

        >>> fixed_stanox = fix_stanox(stanox=65630)
        >>> fixed_stanox
        '65630'

        >>> fixed_stanox = fix_stanox(stanox='2071')
        >>> fixed_stanox
        '02071'

        >>> fixed_stanox = fix_stanox(stanox=2071)
        >>> fixed_stanox
        '02071'
    """

    if isinstance(stanox, str):
        stanox_ = copy.copy(stanox)
    else:  # isinstance(stanox, (int, float)) or stanox is None
        stanox_ = '' if pd.isna(stanox) else str(int(stanox))

    if len(stanox_) < 5 and stanox_ != '':
        stanox_ = '0' * (5 - len(stanox_)) + stanox_

    return stanox_


def fix_mileage(mileage):
    """
    Fix mileage data (associated with an ELR).

    :param mileage: Network Rail mileage
    :type mileage: str or float or None
    :return: fixed mileage data in the conventional format used by Network Rail
    :rtype: str

    **Examples**::

        >>> from pyrcs.utils import fix_mileage

        >>> fixed_mileage = fix_mileage(mileage=29.011)
        >>> fixed_mileage
        '29.0110'

        >>> fixed_mileage = fix_mileage(mileage='.1100')
        >>> fixed_mileage
        '0.1100'
    """

    if isinstance(mileage, float):
        mileage_ = fix_mileage(str(mileage))

    elif mileage and mileage != '0':
        if '.' in mileage:
            miles, yards = mileage.split('.')
            if miles == '':
                miles = '0'
        else:
            miles, yards = mileage, '0'
        if len(yards) < 4:
            yards += '0' * (4 - len(yards))
        mileage_ = '.'.join([miles, yards])

    else:
        mileage_ = copy.copy(mileage)

    return mileage_


def kilometer_to_yard(km):
    """
    Make kilometer-to-yard conversion.

    :param km: kilometer
    :type km: int or float or None
    :return: yard
    :rtype: float

    **Example**::

        >>> from pyrcs.utils import kilometer_to_yard

        >>> kilometer_to_yard(1)
        1093.6132983377079
    """

    yards = np.nan if km is None else km * 1093.6132983377079

    return yards


def yard_to_mileage(yard, as_str=True):
    """
    Convert yards to Network Rail mileages.

    :param yard: yard data
    :type yard: int or float or None
    :param as_str: whether to return as a string value, defaults to ``True``
    :type as_str: bool
    :return: Network Rail mileage in the form '<miles>.<yards>' or <miles>.<yards>
    :rtype: str or float

    **Examples**::

        >>> from pyrcs.utils import yard_to_mileage

        >>> mileage_dat = yard_to_mileage(yard=396)
        >>> mileage_dat
        '0.0396'

        >>> mileage_dat = yard_to_mileage(yard=396, as_str=False)
        >>> mileage_dat
        0.0396

        >>> mileage_dat = yard_to_mileage(yard=None)
        >>> mileage_dat
        ''

        >>> mileage_dat = yard_to_mileage(yard=12320)
        >>> mileage_dat
        '7.0000'
    """

    if pd.notnull(yard) and yard != '':
        yd = int(yard)
        # mileage_mi = measurement.measures.Distance(yd=yards).mi
        mileage_mi = np.floor(yd / 1760)
        # mileage_yd = measurement.measures.Distance(mi=mileage_mi).yd
        mileage_yd = yd - int(mileage_mi * 1760)

        if mileage_yd == 1760:
            mileage_mi += 1
            mileage_yd = 0

        mileage = mileage_mi + round(mileage_yd / (10 ** 4), 4)
        if as_str:
            mileage = str('%.4f' % mileage)

    else:
        mileage = '' if as_str else np.nan

    return mileage


def mileage_to_yard(mileage):
    """
    Convert Network Rail mileages to yards.

    :param mileage: Network Rail mileage
    :type mileage: float or int or str
    :return: yards
    :rtype: int

    **Examples**::

        >>> from pyrcs.utils import mileage_to_yard

        >>> yards_dat = mileage_to_yard(mileage='0.0396')
        >>> yards_dat
        396

        >>> yards_dat = mileage_to_yard(mileage=0.0396)
        >>> yards_dat
        396

        >>> yards_dat = mileage_to_yard(mileage=1.0396)
        >>> yards_dat
        2156
    """

    if isinstance(mileage, (int, float, numbers.Integral, numbers.Rational)):
        mileage = mileage_num_to_str(mileage)

    miles, yards = map(float, mileage.split('.'))

    yards += int(miles * 1760)  # int(measurement.measures.Distance(mi=miles).yd)

    return int(yards)


def mile_chain_to_mileage(mile_chain):
    """
    Convert mileage data in the form '<miles>.<chains>' to Network Rail mileage.

    :param mile_chain: mileage data presented in the form '<miles>.<chains>'
    :type mile_chain: str or numpy.nan or None
    :return: Network Rail mileage in the form '<miles>.<yards>'
    :rtype: str

    **Examples**::

        >>> from pyrcs.utils import mile_chain_to_mileage

        >>> # AAM 0.18 Tewkesbury Junction with ANZ (84.62)
        >>> mileage_data = mile_chain_to_mileage(mile_chain='0.18')
        >>> mileage_data
        '0.0396'

        >>> # None, nan or ''
        >>> mileage_data = mile_chain_to_mileage(mile_chain=None)
        >>> mileage_data
        ''
    """

    if pd.notna(mile_chain) and mile_chain != '':
        miles, chains = map(float, str(mile_chain).split('.'))
        yards = chains * 22.0  # measurement.measures.Distance(chain=chains).yd
        network_rail_mileage = '%.4f' % (miles + round(yards / (10 ** 4), 4))
    else:
        network_rail_mileage = ''

    return network_rail_mileage


def mileage_to_mile_chain(mileage):
    """
    Convert Network Rail mileage to the form '<miles>.<chains>'.

    :param mileage: Network Rail mileage data presented in the form '<miles>.<yards>'
    :type mileage: str or numpy.nan or None
    :return: data presented in the form '<miles>.<chains>'
    :rtype: str

    **Examples**::

        >>> from pyrcs.utils import mileage_to_mile_chain

        >>> mile_chain_data = mileage_to_mile_chain(mileage='0.0396')
        >>> mile_chain_data
        '0.18'

        >>> mile_chain_data = mileage_to_mile_chain(mileage=1.0396)
        >>> mile_chain_data
        '1.18'

        >>> # None, nan or ''
        >>> miles_chains_dat = mileage_to_mile_chain(mileage=None)
        >>> miles_chains_dat
        ''
    """

    if pd.notna(mileage) and mileage != '':
        miles, yards = map(float, str(mileage).split('.'))
        chains = yards / 22.0  # measurement.measures.Distance(yard=yards).chain
        miles_chains = '%.2f' % (miles + round(chains / (10 ** 2), 2))
    else:
        miles_chains = ''

    return miles_chains


def mile_yard_to_mileage(mile, yard, as_numeric=True):
    """
    Convert mile and yard to Network Rail mileage.

    :param mile: mile
    :type mile: float or int
    :param yard: yard
    :type yard: float or int
    :param as_numeric: whether to return a numeric value, defaults to ``True``
    :type as_numeric: bool
    :return: Network Rail mileage
    :rtype: str or float

    **Examples**::

        >>> from utils import mile_yard_to_mileage

        >>> m, y = 10, 1500

        >>> mileage_data = mile_yard_to_mileage(mile=m, yard=y)
        >>> mileage_data
        10.15

        >>> mileage_data = mile_yard_to_mileage(mile=m, yard=y, as_numeric=False)
        >>> mileage_data
        '10.1500'
    """

    mile_, yard_ = map(str, (mile, yard))
    if len(yard_) < 4:
        yard_ = '0' * (4 - len(yard_)) + yard_

    mileage = mile_ + '.' + yard_

    if as_numeric:
        mileage = mileage_str_to_num(mileage)

    return mileage


def mileage_str_to_num(mileage):
    """
    Convert string-type Network Rail mileage to numerical-type one.

    :param mileage: string-type Network Rail mileage in the form '<miles>.<yards>'
    :type mileage: str
    :return: numerical-type Network Rail mileage
    :rtype: float

    **Examples**::

        >>> from pyrcs.utils import mileage_str_to_num

        >>> mileage_num = mileage_str_to_num(mileage='0.0396')
        >>> mileage_num
        0.0396

        >>> mileage_num = mileage_str_to_num(mileage='')
        >>> mileage_num
        nan
    """

    mileage_ = np.nan if mileage == '' else round(float(mileage), 4)

    return mileage_


def mileage_num_to_str(mileage):
    """
    Convert numerical-type Network Rail mileage to string-type one.

    :param mileage: numerical-type Network Rail mileage
    :type mileage: float or None
    :return: string-type Network Rail mileage in the form '<miles>.<yards>'
    :rtype: str

    **Examples**::

        >>> from pyrcs.utils import mileage_num_to_str

        >>> mileage_str = mileage_num_to_str(mileage=0.0396)
        >>> mileage_str
        '0.0396'

        >>> mileage_str = mileage_num_to_str(mileage=None)
        >>> mileage_str
        ''
    """

    if pd.notnull(mileage) or mileage == 0:
        mileage_ = '%.4f' % round(float(mileage), 4)
    else:
        mileage_ = ''

    return mileage_


def shift_mileage_by_yard(mileage, shift_yards, as_numeric=True):
    """
    Shift Network Rail mileage by given yards.

    :param mileage: mileage (associated with an ELR) used by Network Rail
    :type mileage: float or int or str
    :param shift_yards: yards by which the given ``mileage`` is shifted
    :type shift_yards: int or float
    :param as_numeric: whether to return a numeric type result, defaults to ``True``
    :type as_numeric: bool
    :return: shifted mileage
    :rtype: float or str

    **Examples**::

        >>> from pyrcs.utils import shift_mileage_by_yard

        >>> n_mileage = shift_mileage_by_yard(mileage='0.0396', shift_yards=220)
        >>> n_mileage
        0.0616

        >>> n_mileage = shift_mileage_by_yard(mileage='0.0396', shift_yards=220.99)
        >>> n_mileage
        0.0617

        >>> n_mileage = shift_mileage_by_yard(mileage=10, shift_yards=220)
        >>> n_mileage
        10.022
    """

    yards = mileage_to_yard(mileage=mileage) + shift_yards
    shifted_mileage = yard_to_mileage(yard=yards)

    if as_numeric:
        shifted_mileage = mileage_str_to_num(mileage=shifted_mileage)

    return shifted_mileage


def get_financial_year(date):
    """
    Convert calendar year of a given date to Network Rail financial year.

    :param date: date
    :type date: datetime.datetime
    :return: Network Rail financial year of the given ``date``
    :rtype: int

    **Example**::

        >>> from pyrcs.utils import get_financial_year
        >>> import datetime

        >>> financial_year = get_financial_year(date=datetime.datetime(2021, 3, 31))
        >>> financial_year
        2020
    """

    financial_date = date + pd.DateOffset(months=-3)

    return financial_date.year


""" == Parsers =============================================================================== """


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

        >>> from pyrcs.utils import parse_tr
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

    for k in range(len(records)):
        n = n_columns - len(records[k])
        if n == n_columns:
            empty_rows.append(k)
        elif n > 0:
            records[k].extend(['\xa0'] * n)
        elif n < 0 and records[k][2] == '\xa0':
            del records[k][2]

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

        >>> from pyrcs.utils import parse_table
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


def parse_location_name(location_name):
    """
    Parse location name (and its associated note).

    :param location_name: location name (in raw data)
    :type location_name: str or None
    :return: location name and note (if any)
    :rtype: tuple

    **Examples**::

        >>> from pyrcs.utils import parse_location_name

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

        >>> from pyrcs.utils import parse_date

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


""" == Assistant scrapers ==================================================================== """


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

        >>> from pyrcs.utils import get_site_map

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
                print_conn_err(update=update, verbose=True if update else verbose)

            else:
                try:
                    site_map = _get_site_map(source=source)

                    if verbose == 2:
                        print("Done. ")

                    if site_map is not None:
                        save_data(site_map, path_to_file, indent=4, verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(e))

        else:
            print("Cancelled. ") if verbose == 2 else ""
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

        >>> from pyrcs.utils import get_last_updated_date

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
        print_connection_error(verbose=verbose)

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

        >>> from pyrcs.utils import get_catalogue

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
                print_connection_error(verbose=verbose)

            else:
                try:
                    soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

                    try:
                        # try:
                        #     cold_soup = soup.find('div', attrs={'class': "background"}).find('nav')
                        #
                        #     if cold_soup is None:
                        #         cold_soup = soup.find_all('span', attrs={'class': "background"})[-1]
                        #
                        # except AttributeError:
                        #     cold_soup = soup.find('div', attrs={'class': 'fixed'})

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

        >>> from pyrcs.utils import get_category_menu

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
                print_connection_error(verbose=verbose)

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
                        all_next = [x.replace(':', '')
                                    for x in h1.find_all_next(string=True)
                                    if x != '\n' and x != '\xa0'][2:]
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


def get_heading(heading, elem_tag='em'):
    """

    :param heading:
    :param elem_tag:
    :return:
    """

    heading_x = []

    for elem in heading.contents:
        if elem.name == elem_tag:
            heading_x.append('[' + elem.text + ']')
        else:
            heading_x.append(elem.text)
    heading = ''.join(heading_x)

    return heading


def get_page_catalogue(url, head_tag='nav', head_txt='Jump to: ', feature_tag='h3', verbose=False):
    """
    Get the catalogue of the main page of a data cluster.

    :param url: URL of the main page of a data cluster
    :type url: str
    :param head_tag: tag name of the feature list at the top of the page, defaults to ``'nav'``
    :type head_tag: str
    :param head_txt: text that is contained in the ``head_tag``, defaults to ``'Jump to: '``
    :type head_txt: str
    :param feature_tag: tag name of the headings of each feature, defaults to ``'h3'``
    :type feature_tag: str
    :param verbose: whether to print relevant information in console, defaults to ``False``
    :type verbose: bool or int
    :return: catalogue of the main page of a data cluster
    :rtype: pandas.DataFrame

    **Example**::

        >>> from pyrcs.utils import get_page_catalogue
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
        print_conn_err(verbose=verbose)

    else:
        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

        page_catalogue = pd.DataFrame({'Feature': [], 'URL': [], 'Heading': []})

        for nav in soup.find_all(head_tag):
            nav_text = nav.text.replace('\r\n', '').strip()
            if re.match(r'^({})'.format(head_txt), nav_text):
                feature_names = nav_text.replace(head_txt, '').split('\xa0| ')
                page_catalogue['Feature'] = feature_names

                feature_urls = []
                for item_name in feature_names:
                    text_pat = re.compile(r'.*{}.*'.format(item_name), re.IGNORECASE)
                    a = nav.find('a', text=text_pat)
                    feature_urls.append(urllib.parse.urljoin(url, a.get('href')))

                page_catalogue['URL'] = feature_urls

        feature_headings = []
        for h3 in soup.find_all(feature_tag):
            sub_heading = get_heading(heading=h3, elem_tag='em')
            feature_headings.append(sub_heading)

        page_catalogue['Heading'] = feature_headings

        return page_catalogue


def get_hypertext(hypertext, hyperlink_tag='a', md_style=True):
    """
    Get hypertext (i.e. text with a hyperlink).

    :param hypertext:
    :param hyperlink_tag:
    :param md_style:
    :return:


    """

    hypertext_x = []
    for x in hypertext.contents:
        if x.name == hyperlink_tag:
            href = x.get('href')
            if md_style:
                x_text = '[' + x.text + ']' + f'({href})'
            else:
                x_text = x.text + f' ({href})'
            hypertext_x.append(x_text)
        else:
            hypertext_x.append(x.text)

    hypertext = ''.join(hypertext_x).replace('\xa0', '').replace('  ', ' ')

    return hypertext


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

        >>> from pyrcs.utils import get_introduction

        >>> bridges_url = 'http://www.railwaycodes.org.uk/bridges/bridges0.shtm'

        >>> intro_text = get_introduction(url=bridges_url)
        >>> intro_text
        "There are thousands of bridges over and under the railway system. These pages attempt to...
    """

    introduction = None

    try:
        source = requests.get(url=url, headers=fake_requests_headers())
    except requests.exceptions.ConnectionError:
        print_conn_err(verbose=verbose)

    else:
        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

        intro_h3 = [h3 for h3 in soup.find_all('h3') if h3.get_text(strip=True).startswith('Intro')][0]

        intro_paras = _parse_h3_paras(intro_h3)

        introduction = delimiter.join(intro_paras)

    return introduction


""" == Testers =============================================================================== """


# -- Data rectification ----------------------------------------------------------------------

def fetch_loc_names_repl_dict(k=None, regex=False, as_dataframe=False):
    """
    Create a dictionary for rectifying location names.

    :param k: key of the created dictionary, defaults to ``None``
    :type k: str or int or float or bool or None
    :param regex: whether to create a dictionary for replacement based on regular expressions,
        defaults to ``False``
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
        dict
        >>> list(repl_dict.keys())[:5]
        ['"Tyndrum Upper" (Upper Tyndrum)',
         'AISH EMERGENCY CROSSOVER',
         'ATLBRJN',
         'Aberdeen Craiginches',
         'Aberdeen Craiginches T.C.']

        >>> repl_dict = fetch_loc_names_repl_dict(regex=True, as_dataframe=True)

        >>> type(repl_dict)
        pandas.core.frame.DataFrame
        >>> repl_dict.head()
                                         new_value
        re.compile(' \\(DC lines\\)')   [DC lines]
        re.compile(' And | \\+ ')               &
        re.compile('-By-')                    -by-
        re.compile('-In-')                    -in-
        re.compile('-En-Le-')              -en-le-
    """

    json_filename = "location-names-repl{}.json".format("" if not regex else "-regex")
    location_name_repl_dict = load_data(cd_data(json_filename))

    if regex:
        location_name_repl_dict = {
            re.compile(k): v for k, v in location_name_repl_dict.items()}

    replacement_dict = {k: location_name_repl_dict} if k else location_name_repl_dict

    if as_dataframe:
        replacement_dict = pd.DataFrame.from_dict(
            replacement_dict, orient='index', columns=['new_value'])

    return replacement_dict


def _update_loc_names_repl_dict(new_items, regex, verbose=False):
    """
    Update the location-names replacement dictionary in the package data.

    :param new_items: new items to replace
    :type new_items: dict
    :param regex: whether this update is for regular-expression dictionary
    :type regex: bool
    :param verbose: whether to print relevant information in console, defaults to ``False``
    :type verbose: bool or int
    """

    json_filename = "location-names-repl{}.json".format("" if not regex else "-regex")

    new_items_keys = list(new_items.keys())

    if confirmed("To update \"{}\" with {{\"{}\"... }}?".format(json_filename, new_items_keys[0])):
        path_to_json = cd_data(json_filename)
        location_name_repl_dict = load_data(path_to_json)

        if any(isinstance(k, re.Pattern) for k in new_items_keys):
            new_items = {k.pattern: v for k, v in new_items.items() if isinstance(k, re.Pattern)}

        location_name_repl_dict.update(new_items)

        save_data(location_name_repl_dict, path_to_json, verbose=verbose)


def is_str_float(x):
    """
    Check if a string-type variable can express a float-type value.

    :param x: a string-type variable
    :type x: str
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
        float(x)  # float(re.sub('[()~]', '', text))
        test_res = True
    except ValueError:
        test_res = False

    return test_res


def validate_initial(x, as_is=False):
    """
    Validate an input initial letter.

    :param x: any string variable (which is supposed to be an initial letter)
    :type x: str
    :param as_is: whether to return the validated letter as is the input
    :type as_is: bool
    :return: validated initial letter
    :rtype: str

    **Examples**::

        >>> from pyrcs.utils import validate_initial

        >>> validate_initial('x')
        'X'

        >>> validate_initial('x', as_is=True)
        'x'

        >>> validate_initial('xyz')
        AssertionError: `x` must be a single letter.
    """

    assert x in set(string.ascii_letters), "`x` must be a single letter."

    valid_initial = x if as_is else x.upper()

    return valid_initial


# -- Network connections ---------------------------------------------------------------------


def is_home_connectable():
    """
    Check whether the Railway Codes website is connectable.

    :return: whether the Railway Codes website is connectable
    :rtype: bool

    **Example**::

        >>> from pyrcs.utils import is_home_connectable

        >>> is_home_connectable()
        True
    """

    url = home_page_url()

    rslt = is_url_connectable(url=url)

    return rslt


def print_connection_error(verbose=False):
    """
    Print a message about unsuccessful attempts to establish a connection to the Internet.

    :param verbose: whether to print relevant information in console, defaults to ``False``
    :type verbose: bool or int

    **Example**::

        >>> from pyrcs.utils import print_connection_error

        >>> # If Internet connection is ready, nothing would be printed
        >>> print_connection_error(verbose=True)

    """

    if not is_home_connectable():
        if verbose:
            print("Failed to establish an Internet connection. "
                  "The current instance relies on local backup.")


def print_conn_err(update=False, verbose=False, e=None):
    """
    Print a message about unsuccessful attempts to establish a connection to the Internet
    (for an instance of a class).

    :param update: defaults to ``False``
        (mostly complies with ``update`` in a parent function that uses this function)
    :type update: bool
    :param verbose: whether to print relevant information in console, defaults to ``False``
    :type verbose: bool or int
    :param e: error message
    :type e: Exception or None

    **Example**::

        >>> from pyrcs.utils import print_conn_err

        >>> print_conn_err(verbose=True)
        The Internet connection is not available.
    """

    if e is None:
        msg = "The Internet connection is not available."
    else:
        msg = "{}".format(e)

    if update and verbose:
        print(msg + " Failed to update the data.")
    elif verbose:
        print(msg)


""" == Miscellaneous helpers ================================================================= """


def get_page_name(cls, page_no, valid_page_no):
    assert page_no in valid_page_no, f"Valid `page_no` must be one of {valid_page_no}."

    page_name = [k for k in cls.catalogue.keys() if str(page_no) in k][0]

    return page_name


def confirm_msg(data_name):
    """
    Create a confirmation message (for data collection).

    :param data_name: name of data, e.g. "Railway Codes"
    :type data_name: str
    :return: a confirmation message
    :rtype: str

    **Example**::

        >>> from pyrcs.utils import confirm_msg

        >>> msg = confirm_msg(data_name="Railway Codes")
        >>> print(msg)
        To collect data of Railway Codes
        ?
    """

    cfm_msg = "To collect data of {}\n?".format(data_name)

    return cfm_msg


def print_collect_msg(data_name, verbose, confirmation_required, end=" ... "):
    """
    Print a message about the status of collecting data.

    :param data_name: name of the data being collected
    :type data_name: str
    :param verbose: whether to print relevant information in console
    :type verbose: bool or int
    :param confirmation_required: whether to confirm before proceeding
    :type confirmation_required: bool
    :param end: string appended after the last value, defaults to ``" ... "``.
    :type end: str

    **Example**::

        >>> from pyrcs.utils import print_collect_msg

        >>> print_collect_msg("Railway Codes", verbose=2, confirmation_required=False)
        Collecting the data of "Railway Codes" ...
    """

    if verbose == 2:
        if confirmation_required:
            print(f"Collecting the data", end=end)
        else:
            print(f"Collecting the data of \"{data_name}\"", end=end)


def print_void_msg(data_name, verbose):
    """
    Print a message about the status of collecting data
    (only when the data collection process fails).

    :param data_name: name of the data being collected
    :type data_name: str
    :param verbose: whether to print relevant information in console
    :type verbose: bool or int

    **Example**::

        >>> from pyrcs.utils import print_void_msg

        >>> print_void_msg(data_name="Railway Codes", verbose=True)
        No data of "Railway Codes" has been freshly collected.
    """

    if verbose:
        print("No data of \"{}\" has been freshly collected.".format(data_name.title()))


def collect_in_fetch_verbose(data_dir, verbose):
    """
    Create a new parameter that indicates whether to print relevant information in console
    (used only if it is necessary to re-collect data when trying to fetch the data).

    :param data_dir: name of a folder where the pickle file is to be saved
    :type data_dir: str or None
    :param verbose: whether to print relevant information in console
    :type verbose: bool or int
    :return: whether to print relevant information in console when collecting data
    :rtype: bool or int

    **Example**::

        >>> from pyrcs.utils import collect_in_fetch_verbose

        >>> collect_in_fetch_verbose(data_dir="data", verbose=True)
        False
    """

    verbose_ = False if (data_dir or not verbose) else (2 if verbose == 2 else True)

    return verbose_


def fetch_all_verbose(data_dir, verbose):
    """
    Create a new parameter that indicates whether to print relevant information in console
    (used only when trying to fetch all data of a cluster).

    :param data_dir: name of a folder where the pickle file is to be saved
    :type data_dir: str or None
    :param verbose: whether to print relevant information in console
    :type verbose: bool or int
    :return: whether to print relevant information in console when collecting data
    :rtype: bool or int

    **Example**::

        >>> from pyrcs.utils import fetch_all_verbose

        >>> fetch_all_verbose(data_dir="data", verbose=True)
        False
    """

    if is_home_connectable():
        verbose_ = collect_in_fetch_verbose(data_dir=data_dir, verbose=verbose)
    else:
        verbose_ = False

    return verbose_


def save_data_to_file(cls, data, data_name, ext, dump_dir=None, verbose=False, **kwargs):
    """
    Save the collected data as a file, depending on the given parameters.

    :param cls: (an instance of) a class for a certain data cluster
    :type cls: object
    :param data: data collected for a certain cluster
    :type data: pandas.DataFrame or list or dict
    :param data_name: key to the dict-type data of a certain cluster
    :type data_name: str
    :param ext: whether to save the data as a file, or file extension
    :type ext: bool or str
    :param dump_dir: pathname of a directory where the data file is to be dumped, defaults to ``None``
    :type dump_dir: str or None
    :param verbose: whether to print relevant information in console, defaults to ``False``
    :type verbose: bool or int
    :param kwargs: [optional] parameters of the function `pyhelpers.store.save_data()`_

    .. _`pyhelpers.store.save_data()`:
        https://pyhelpers.readthedocs.io/en/latest/_generated/pyhelpers.store.save_data.html
    """

    data_has_contents = bool(data) if not isinstance(data, pd.DataFrame) else True

    if data_has_contents:
        if isinstance(ext, str):
            file_ext = "." + ext if not ext.startswith(".") else copy.copy(ext)
        else:
            file_ext = ".pickle"

        path_to_file = make_file_pathname(cls=cls, data_name=data_name, ext=file_ext, data_dir=dump_dir)

        kwargs.update({'data': data, 'path_to_file': path_to_file, 'verbose': verbose})
        save_data(**kwargs)

    else:
        print_void_msg(data_name=data_name, verbose=verbose)


def fetch_data_from_file(cls, method, data_name, ext, update, dump_dir, verbose, data_dir=None,
                         save_data_kwargs=None, **kwargs):
    """
    Fetch/load desired data from a backup file, depending on the given parameters.

    :param cls: (an instance of) a class for a certain data cluster
    :type cls: object
    :param method: name of a method of the ``cls``, which is used for collecting the data
    :type method: str
    :param data_name: key to the dict-type data of a certain cluster
    :type data_name: str
    :param ext: whether to save the data as a file, or file extension
    :type ext: bool or str
    :param update: whether to do an update check (for the package data), defaults to ``False``
    :type update: bool
    :param dump_dir: pathname of a directory where the data file is to be dumped, defaults to ``None``
    :type dump_dir: str or os.PathLike[str] or None
    :param verbose: whether to print relevant information in console
    :type verbose: bool or int
    :param data_dir: pathname of a directory where the data is fetched, defaults to ``None``
    :type data_dir: str or os.PathLike[str] or None
    :param save_data_kwargs: equivalent of ``kwargs`` used by the function
        :py:func:`pyrcs.utils.save_data_to_file`, defaults to ``None``
    :type save_data_kwargs: dict or None
    :param kwargs: [optional] parameters of the ``cls``.``method`` being called
    :type kwargs: any
    :return: data fetched for the desired cluster
    :rtype: dict or None
    """

    try:
        path_to_file = make_file_pathname(cls=cls, data_name=data_name, ext=ext, data_dir=data_dir)
        if os.path.isfile(path_to_file) and not update:
            data = load_data(path_to_file)

        else:
            verbose_ = collect_in_fetch_verbose(data_dir=dump_dir, verbose=verbose)

            kwargs.update({'confirmation_required': False, 'verbose': verbose_})
            data = getattr(cls, method)(**kwargs)

        if dump_dir is not None:
            if save_data_kwargs is None:
                save_data_kwargs = {}

            save_data_to_file(
                cls=cls, data=data, data_name=data_name, ext=ext, dump_dir=dump_dir, verbose=verbose,
                **save_data_kwargs)

    except Exception as e:
        if verbose:
            print("Some errors occurred when fetching the data. {}".format(e))
        data = None

    return data
