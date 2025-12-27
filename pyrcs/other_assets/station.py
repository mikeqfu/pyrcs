"""
Collects `railway station data <http://www.railwaycodes.org.uk/stations/station0.shtm>`_.
"""

import re
import string
import urllib.parse

import bs4
import pandas as pd
from pyhelpers.text import remove_punctuation

from .._base import _Base
from ..parser import _get_last_updated_date, get_catalogue, parse_tr
from ..utils import cd_data, get_collect_verbosity_for_fetch, home_page_url, is_home_connectable, \
    print_instance_connection_error, print_void_collection_message, validate_initial


def _split_elr_mileage_column(dat):
    if 'ELRMileage' in dat.columns:
        temp = dat['ELRMileage'].str.split(r'\t\t / | / \[', n=1, regex=True, expand=True)
        temp.columns = ['ELR', 'Mileage']

        # elr_dat = temp['ELR'].str.strip().str.replace(' ', ' &&& ')
        # elr_dat = temp['ELR'].str.strip().str.replace('  /  ', ' &&& ')

        def _to_repl(x, repl=' &&& '):
            if '  /  ' in x:
                y = x.replace('  /  ', repl)
            elif ' / ' in x:
                y = x.replace(' / ', repl)
            elif ' ' in x:
                y = x.replace(' ', repl)
            else:
                y = x
            return y

        elr_dat = temp['ELR'].str.strip().map(_to_repl)

        temp['Mileage'] = temp['Mileage'].str.split('\t\t / ').fillna('').map(
            lambda x: [' / '.join(x_.strip(' []').split('  ')) for x_ in x])
        mil_dat = temp['Mileage'].map(lambda x: x[0] if len(x) == 1 else ' &&& '.join(x))

        dat.drop(columns=['ELRMileage'], inplace=True)
        dat.insert(1, 'ELR', elr_dat)
        dat.insert(2, 'Mileage', mil_dat)

    return dat


def _check_row_spans(dat):
    """
    Checks data in which there are row spans.

    :param dat: Preprocessed data of the station locations.
    :type dat: pandas.DataFrame
    :return: Data with row spans (if there is any).
    :rtype: pandas.DataFrame
    """

    # temp0 = dat['Degrees Longitude'].str.split(' / ')
    temp0 = dat['Degrees Longitude'].str.split(r' / |\r', regex=True)
    temp1 = dat[temp0.map(lambda x: True if len(x) > 1 else False)]

    cols = ['ELR', 'Mileage', 'Degrees Longitude', 'Degrees Latitude', 'Grid Reference']
    cols_ = [x for x in temp1.columns if x not in cols]

    temp_dat = []
    for col in cols:
        temp2 = temp1[col].str.split(r' &&& |\r| / ', regex=True)

        if cols.index(col) == 0:
            temp_dat_ = temp1[cols_].join(temp2).explode(col, ignore_index=True)
        else:
            temp_dat_ = temp2.explode(ignore_index=True).to_frame(name=col)

        temp_dat.append(temp_dat_)

    temp_data = pd.concat(temp_dat, axis=1)
    temp_data = temp_data[dat.columns.to_list()]

    dat0 = pd.concat([dat.drop(index=temp1.index), temp_data], axis=0, ignore_index=True)

    dat0[['ELR', 'Mileage']] = dat0[['ELR', 'Mileage']].map(lambda x: x.split(' &&& '))
    dat0 = dat0.explode(['ELR', 'Mileage'], ignore_index=True)

    return dat0


def _parse_coordinates_columns(dat):
    """
    Parses ``'Degrees Longitude'`` and ``'Degrees Latitude'`` of the station locations data.

    :param dat: Preprocessed data of the station locations.
    :type dat: pandas.DataFrame
    :return: Data with parsed coordinates.
    :rtype: pandas.DataFrame
    """

    ll_col_names = ['Degrees Longitude', 'Degrees Latitude']

    dat[ll_col_names] = dat[ll_col_names].map(
        lambda x: None if x.strip() == '' else float(re.sub(r'(c\.)|≈', '', x)))

    return dat


def _parse_station_column(dat):
    """
    Parses ``'Station'`` of the station locations data.

    :param dat: Preprocessed data of the station locations.
    :type dat: pandas.DataFrame
    :return: Data with parsed station names and their corresponding CRS.
    :rtype: pandas.DataFrame

    **Tests**::

        x = 'Hythe Road\t\t / [CRS awaited]'
        x = 'Heathrow Junction [sometimes referred to as Heathrow Interchange]\t\t / [no CRS?]'
    """

    stn_col_name = [col for col in dat.columns if 'Station' in col][0]
    temp1 = dat[stn_col_name].str.split('\t\t', n=1, expand=True)

    if stn_col_name != 'Station':
        dat.rename(columns={stn_col_name: 'Station'}, inplace=True)
        stn_col_name = 'Station'

    temp1.columns = [stn_col_name, 'CRS']
    dat[stn_col_name] = temp1[stn_col_name].str.rstrip(' / ').str.strip()

    # Get notes for stations
    stn_note_ = pd.Series('', index=dat.index)
    for i, x in enumerate(temp1[stn_col_name]):
        if '[' in x and ']' in x:
            y = re.search(r' \[(.*)](✖.*)?', x).group(0)  # Station Note
            dat.loc[i, stn_col_name] = str(x).replace(y, '').strip()
            if '✖' in y:
                stn_note_[i] = '; '.join([y_.strip(' []') for y_ in y.split('✖')])
            else:
                stn_note_[i] = y.strip(' []')

    dat.insert(loc=dat.columns.get_loc(stn_col_name) + 1, column='Station Note', value=stn_note_)

    temp2 = temp1['CRS'].str.replace(' / /', ' &&& ').str.split(
        r'  | / ', regex=True, expand=True).fillna('')

    if temp2.shape[1] == 1:
        temp2.columns = ['CRS']
        temp2 = pd.concat(
            [temp2, pd.DataFrame('', index=temp2.index, columns=['CRS Note'])], axis=1)
    else:
        temp2.columns = ['CRS', 'CRS Note']
        temp2['CRS Note'] = temp2['CRS Note'].str.strip('[]')

    temp2['CRS'] = temp2['CRS'].str.replace(r'[()]', '', regex=True).map(
        lambda z: ' and '.join(['{} [{}]'.format(*z_.split('✖')) for z_ in z.split(' &&& ')])
        if ' &&& ' in z else z).str.strip()

    dat = pd.concat([dat, temp2], axis=1).sort_values(stn_col_name)

    return dat


def _parse_owner_and_operator(x):
    """
    x = dat['Owner'][0]
    x = dat['Owner'][1]
    """

    if ' / and / ' in x:
        y, y_ = x.replace(' / and / ', ' &&& '), ''

    elif ' / ' in x or '\r' in x:
        x_ = re.split(r' / |\r', x)

        # y - Owners or operators; y_ - Former owners or operators
        if len(x_) > 1:
            y = x_[0]
            y_ = x_[1] if len(x_[1:]) == 1 else ' / '.join(x_[1:])
        else:
            y, y_ = x_[0], ''

    else:
        y, y_ = x, ''

    if '✖' in y and ' &&& ' in y:
        y = ' and '.join(['{} [{}]'.format(*z.split('✖')) for z in y.split(' &&& ')])

    if ' [from' in y:
        y = remove_punctuation(y)

    return y, y_


def _parse_owner_and_operator_columns(dat):
    """
    Parses ``'Owner'`` and ``'Operator'`` of the station locations data.

    :param dat: Preprocessed data of the station locations.
    :type dat: pandas.DataFrame
    :return: Data with parsed information of owners and operators.
    :rtype: pandas.DataFrame
    """

    owner_operator = []
    for col in ['Owner', 'Operator']:
        temp = pd.DataFrame(
            dat[col].map(_parse_owner_and_operator).to_list(), columns=[col, 'Former ' + col],
            index=dat.index)

        del dat[col]

        owner_operator.append(temp)

    dat = pd.concat([dat] + owner_operator, axis=1)

    return dat


class Stations(_Base):
    """
    A class for collecting
    `railway station data <http://www.railwaycodes.org.uk/stations/station0.shtm>`_.
    """

    #: The name of the data.
    NAME: str = 'Railway station data'
    #: The key for accessing the data.
    KEY: str = 'Stations'
    #: The key for accessing the data of *Mileages, operators and grid coordinates*.
    KEY_TO_STN: str = 'Mileages, operators and grid coordinates'

    #: The URL of the main web page for the data.
    URL: str = urllib.parse.urljoin(home_page_url(), '/stations/station0.shtm')

    #: The key used to reference the last updated date in the data.
    KEY_TO_LAST_UPDATED_DATE: str = 'Last updated date'

    def __init__(self, data_dir=None, update=False, verbose=True):
        """
        :param data_dir: The name of the directory for storing the data; defaults to ``None``.
        :type data_dir: str | None
        :param update: Whether to check for updates to the catalogue; defaults to ``False``.
        :type update: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``True``.
        :type verbose: bool | int

        :ivar dict catalogue: The catalogue of the data.
        :ivar str last_updated_date: The date when the data was last updated.
        :ivar str data_dir: The path to the directory containing the data.
        :ivar str current_data_dir: The path to the current data directory.

        **Examples**::

            >>> from pyrcs.other_assets import Stations  # from pyrcs import Stations
            >>> stn = Stations()
            >>> stn.NAME
            'Railway station data'
            >>> stn.URL
            'http://www.railwaycodes.org.uk/stations/station0.shtm'
        """

        super().__init__(
            data_dir=data_dir, data_category="other-assets", update=update, verbose=verbose)

        self.catalogue = self.fetch_catalogue(update=update, verbose=False)

        self.station_names_errata = {
                "-By-": "-by-",
                "-In-": "-in-",
                "-En-Le-": "-en-le-",
                "-La-": "-la-",
                "-Le-": "-le-",
                "-On-": "-on-",
                "-The-": "-the-",
                " Of ": " of ",
                "-Super-": "-super-",
                "-Upon-": "-upon-",
                "-Under-": "-under-",
                "-Y-": "-y-",
            }

    def _collect_catalogue(self, source, verbose=False):
        soup = bs4.BeautifulSoup(markup=source.text, features='html.parser')

        cold_soup = soup.find_all('nav')[1]

        hot_soup = {
            a.text: urllib.parse.urljoin(self.URL, a.get('href'))
            for a in cold_soup.find_all('a')}

        catalogue = {}
        for k, v in hot_soup.items():
            sub_cat = get_catalogue(url=v, update=True, json_it=False)

            if sub_cat != hot_soup:
                if k in sub_cat.keys():
                    sub_cat.pop(k)
                elif 'Introduction' in sub_cat.keys():
                    sub_cat.pop('Introduction')
                if v in sub_cat.values():
                    catalogue[k] = sub_cat
                else:
                    catalogue[k] = {'Introduction': v, **sub_cat}

            else:
                catalogue.update({k: v})

        if verbose in {True, 1}:
            print("Done.")

        data_name = urllib.parse.urlparse(
            self.URL).path.lstrip('/').rstrip('.shtm').replace('/', '-')
        self._save_data_to_file(
            data=catalogue, data_name=data_name, ext=".json", dump_dir=cd_data("catalogue"),
            verbose=verbose, indent=4)

        return catalogue

    def collect_catalogue(self, confirmation_required=True, verbose=False, raise_error=False):
        """
        Collects the catalogue of `railway station data`_ from the source web page.

        .. _`railway station data`: http://www.railwaycodes.org.uk/stations/station0.shtm

        :param confirmation_required: Whether user confirmation is required;
            if ``confirmation_required=True`` (default), prompts the user for confirmation
            before proceeding with data collection.
        :type confirmation_required: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :param raise_error: Whether to raise the provided exception;
            if ``raise_error=False`` (default), the error will be suppressed.
        :type raise_error: bool
        :return: A dictionary containing the catalogue of railway station data,
            or ``None`` if no data catalogue is collected.
        :rtype: dict | None
        """

        catalogue = self._collect_data_from_source(
            data_name=f'{self.NAME.lower()} catalogue', method=self._collect_catalogue,
            url=self.URL, confirmation_required=confirmation_required, verbose=verbose,
            raise_error=raise_error)

        return catalogue

    def fetch_catalogue(self, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetches the catalogue of `railway station data`_.

        .. _`railway station data`: http://www.railwaycodes.org.uk/stations/station0.shtm

        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the catalogue of railway station data,
            or ``None`` if no data catalogue is collected.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.other_assets import Stations  # from pyrcs import Stations
            >>> stn = Stations()
            >>> stn_data_cat = stn.fetch_catalogue()
            >>> type(stn_data_cat)
            dict
            >>> list(stn_data_cat.keys())
            ['Mileages, operators and grid coordinates',
             'Bilingual names',
             'Sponsored signs',
             'Not served by SFO',
             'International',
             'Trivia',
             'Access rights',
             'Barrier error codes',
             'London Underground',
             'Railnet']
        """

        data_name = urllib.parse.urlparse(
            self.URL).path.lstrip('/').rstrip('.shtm').replace('/', '-')

        args = {
            'data_name': data_name,
            'method': self.collect_catalogue,
            'ext': ".json",
            'data_dir': cd_data("catalogue"),
        }
        kwargs.update(args)

        catalogue = self._fetch_data_from_file(
            update=update, dump_dir=dump_dir, verbose=verbose, **kwargs)

        return catalogue

    def _collect_locations(self, initial, source, verbose=False):
        initial_ = validate_initial(initial)

        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')
        thead, tbody = soup.find('thead'), soup.find('tbody')

        # Create a DataFrame of the requested table
        trs = tbody.find_all(name='tr')
        ths = [re.sub(r'\n?\r+\n?', ' ', h.text).strip() for h in thead.find_all('th')]
        dat_ = parse_tr(trs=trs, ths=ths, as_dataframe=True)

        dat = dat_.copy()

        parser_funcs = [
            _split_elr_mileage_column,
            _check_row_spans,
            _parse_coordinates_columns,
            _parse_station_column,
            _parse_owner_and_operator_columns,
        ]
        for parser_func in parser_funcs:
            dat = parser_func(dat)

        # # Debugging
        # for parser_func in parser_funcs:
        #     try:
        #         dat_ = parser_func(dat_)
        #     except Exception:
        #         print(parser_func)
        #         break

        # Explode by ELR and Mileage
        dat = dat.explode(column=['ELR', 'Mileage'], ignore_index=True)

        # dat['Station'].replace(self.station_names_errata, regex=True, inplace=True)
        dat['Station'] = dat['Station'].replace(self.station_names_errata, regex=True)

        data = {
            initial_: dat.sort_values('Station', ignore_index=True),
            self.KEY_TO_LAST_UPDATED_DATE: _get_last_updated_date(soup=soup)
        }

        if verbose in {True, 1}:
            print("Done.")

        self._save_data_to_file(data=data, data_name=initial_, sub_dir="a-z", verbose=verbose)

        return data

    def collect_locations(self, initial, confirmation_required=True, verbose=False,
                          raise_error=False):
        """
        Collects data of `railway station locations
        <http://www.railwaycodes.org.uk/stations/station0.shtm>`_
        (mileages, operators and grid coordinates) for a given initial letter.

        :param initial: The initial letter (e.g. ``'a'``, ``'z'``) of railway station names.
        :type initial: str
        :param confirmation_required: Whether user confirmation is required;
            if ``confirmation_required=True`` (default), prompts the user for confirmation
            before proceeding with data collection.
        :type confirmation_required: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``True``.
        :type verbose: bool | int
        :param raise_error: Whether to raise the provided exception;
            if ``raise_error=False`` (default), the error will be suppressed.
        :type raise_error: bool
        :return: A dictionary containing the data of railway station locations whose initial letters
            are the given ``initial`` and date of when the data was last updated.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Stations  # from pyrcs import Stations
            >>> stn = Stations()
            >>> stn_loc_a_codes = stn.collect_locations(initial='a')
            >>> type(stn_loc_a_codes)
            dict
            >>> list(stn_loc_a_codes.keys())
            ['A', 'Last updated date']
            >>> stn_loc_a_codes_dat = stn_loc_a_codes['A']
            >>> type(stn_loc_a_codes_dat)
            pandas.core.frame.DataFrame
            >>> stn_loc_a_codes_dat.head()
                  Station  ...                                    Former Operator
            0  Abbey Wood  ...  London & South Eastern Railway from 1 April 20...
            1  Abbey Wood  ...  London & South Eastern Railway from 1 April 20...
            2        Aber  ...  Keolis Amey Operations/Gweithrediadau Keolis A...
            3   Abercynon  ...  Keolis Amey Operations/Gweithrediadau Keolis A...
            4   Abercynon  ...  Keolis Amey Operations/Gweithrediadau Keolis A...
            [5 rows x 14 columns]
            >>> stn_loc_a_codes_dat.columns.to_list()
            ['Station',
             'Station Note',
             'ELR',
             'Mileage',
             'Status',
             'Degrees Longitude',
             'Degrees Latitude',
             'Grid Reference',
             'CRS',
             'CRS Note',
             'Owner',
             'Former Owner',
             'Operator',
             'Former Operator']
            >>> stn_loc_a_codes_dat[['Station', 'ELR', 'Mileage']].head()
                  Station  ELR   Mileage
            0  Abbey Wood  NKL  11m 43ch
            1  Abbey Wood  XRS  24.458km
            2        Aber  CAR   8m 69ch
            3   Abercynon  CAM  16m 28ch
            4   Abercynon  ABD  16m 28ch
        """

        initial_ = validate_initial(initial=initial)

        data = self._collect_data_from_source(
            data_name=self.KEY_TO_STN.lower(), method=self._collect_locations, initial=initial_,
            url=self.catalogue[self.KEY_TO_STN].get(initial_),
            confirmation_required=confirmation_required, verbose=verbose, raise_error=raise_error)

        return data

    def fetch_locations(self, initial=None, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetches data of `railway station locations`_ (mileages, operators and grid coordinates).

        .. _`railway station locations`:
            http://www.railwaycodes.org.uk/stations/station0.shtm

        :param initial: The initial letter (e.g. ``'a'``, ``'z'``) of railway station names.
        :type initial: str
        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the data of railway station locations and
            the date of when the data was last updated.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Stations  # from pyrcs import Stations
            >>> stn = Stations()
            >>> stn_loc_codes = stn.fetch_locations()
            >>> type(stn_loc_codes)
            dict
            >>> list(stn_loc_codes.keys())
            ['Mileages, operators and grid coordinates', 'Last updated date']
            >>> stn.KEY_TO_STN
            'Mileages, operators and grid coordinates'
            >>> stn_loc_codes_dat = stn_loc_codes[stn.KEY_TO_STN]
            >>> type(stn_loc_codes_dat)
            pandas.core.frame.DataFrame
            >>> stn_loc_codes_dat.head()
                  Station  ...                                    Former Operator
            0  Abbey Wood  ...  London & South Eastern Railway from 1 April 20...
            1  Abbey Wood  ...  London & South Eastern Railway from 1 April 20...
            2        Aber  ...  Keolis Amey Operations/Gweithrediadau Keolis A...
            3   Abercynon  ...  Keolis Amey Operations/Gweithrediadau Keolis A...
            4   Abercynon  ...  Keolis Amey Operations/Gweithrediadau Keolis A...
            [5 rows x 14 columns]
            >>> stn_loc_codes_dat.columns.to_list()
            ['Station',
             'Station Note',
             'ELR',
             'Mileage',
             'Status',
             'Degrees Longitude',
             'Degrees Latitude',
             'Grid Reference',
             'CRS',
             'CRS Note',
             'Owner',
             'Former Owner',
             'Operator',
             'Former Operator']
            >>> stn_loc_codes_dat[['Station', 'ELR', 'Mileage']].head()
                  Station  ELR   Mileage
            0  Abbey Wood  NKL  11m 43ch
            1  Abbey Wood  XRS  24.458km
            2        Aber  CAR   8m 69ch
            3   Abercynon  CAM  16m 28ch
            4   Abercynon  ABD  16m 28ch
        """

        if initial:
            args = {
                'data_name': validate_initial(initial),
                'method': self.collect_locations,
                'sub_dir': "a-z",
                'initial': initial,
            }
            kwargs.update(args)

            railway_station_data = self._fetch_data_from_file(
                update=update, dump_dir=dump_dir, verbose=verbose, **kwargs)

        else:
            verbose_1 = get_collect_verbosity_for_fetch(data_dir=dump_dir, verbose=verbose)
            verbose_2 = verbose_1 if is_home_connectable() else False

            data_sets = [
                self.fetch_locations(initial=x, update=update, verbose=verbose_2)
                for x in string.ascii_lowercase]

            if all(d[x] is None for d, x in zip(data_sets, string.ascii_uppercase)):
                if update:
                    print_instance_connection_error(verbose=verbose)
                    print_void_collection_message(data_name=self.KEY_TO_STN, verbose=verbose)

                data_sets = [
                    self.fetch_locations(x, update=False, verbose=verbose_1)
                    for x in string.ascii_lowercase
                ]

            stn_dat_tbl_ = (item[x] for item, x in zip(data_sets, string.ascii_uppercase))
            stn_dat_tbl = sorted(
                [x for x in stn_dat_tbl_ if x is not None], key=lambda x: x.shape[1], reverse=True)
            stn_data = pd.concat(stn_dat_tbl, axis=0, ignore_index=True, sort=False)

            stn_data = stn_data.where(pd.notna(stn_data), None)
            stn_data.sort_values(['Station'], inplace=True)

            stn_data.index = range(len(stn_data))

            last_updated_dates = (d[self.KEY_TO_LAST_UPDATED_DATE] for d in data_sets)
            latest_update_date = max(d for d in last_updated_dates if d is not None)

            railway_station_data = {
                self.KEY_TO_STN: stn_data,
                self.KEY_TO_LAST_UPDATED_DATE: latest_update_date,
            }

        if dump_dir is not None:
            self._save_data_to_file(
                data=railway_station_data, data_name=self.KEY_TO_STN, dump_dir=dump_dir,
                verbose=verbose)

        return railway_station_data
