"""
Collects `railway station data <http://www.railwaycodes.org.uk/stations/station0.shtm>`_.
"""

import os
import re
import string
import urllib.parse

import bs4
import pandas as pd
import requests
from pyhelpers.dirs import cd
from pyhelpers.ops import fake_requests_headers
from pyhelpers.store import load_data
from pyhelpers.text import remove_punctuation

from ..parser import get_catalogue, get_last_updated_date, parse_tr
from ..utils import cd_data, collect_in_fetch_verbose, format_err_msg, home_page_url, \
    init_data_dir, is_home_connectable, print_conn_err, print_inst_conn_err, print_void_msg, \
    save_data_to_file, validate_initial


class Stations:
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

        print_conn_err(verbose=verbose)

        self.catalogue = self.get_catalogue(update=update, verbose=False)

        self.last_updated_date = get_last_updated_date(url=self.URL)

        self.data_dir, self.current_data_dir = init_data_dir(self, data_dir, "other-assets")

    def _cdd(self, *sub_dir, mkdir=True, **kwargs):
        """
        Changes the current directory to the package's data directory,
        or its specified subdirectories (or file).

        The default data directory for this class is: ``"data\\other-assets\\stations"``.

        :param sub_dir: One or more subdirectories and/or a file to navigate to
            within the data directory.
        :type sub_dir: str
        :param mkdir: Whether to create the specified directory if it doesn't exist;
            defaults to ``True``.
        :type mkdir: bool
        :param kwargs: [Optional] Additional parameters for the `pyhelpers.dir.cd()`_ function.
        :return: The path to the backup data directory or its specified subdirectories (or file).
        :rtype: str

        .. _`pyhelpers.dir.cd()`:
            https://pyhelpers.readthedocs.io/en/latest/_generated/pyhelpers.dir.cd.html
        """

        kwargs.update({'mkdir': mkdir})
        path = cd(self.data_dir, *sub_dir, **kwargs)

        return path

    def get_catalogue(self, update=False, verbose=False):
        """
        Gets the catalogue of railway station data.

        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the catalogue of railway station data,
            or ``None`` if no data catalogue is collected.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.other_assets import Stations  # from pyrcs import Stations
            >>> stn = Stations()
            >>> stn_data_cat = stn.get_catalogue()
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
        ext = ".json"
        path_to_cat = cd_data("catalogue", data_name + ext)

        if os.path.isfile(path_to_cat) and not update:
            catalogue = load_data(path_to_cat)

        else:
            if verbose == 2:
                print("Collecting the catalogue of {}".format(self.NAME.lower()), end=" ... ")

            catalogue = None

            try:
                source = requests.get(url=self.URL, headers=fake_requests_headers())

            except Exception as e:
                if verbose == 2:
                    print("Failed. ", end="")
                print_inst_conn_err(update=update, verbose=verbose, e=e)

            else:
                try:
                    soup = bs4.BeautifulSoup(markup=source.text, features='html.parser')

                    cold_soup = soup.find_all('nav')[1]

                    hot_soup = {
                        a.text: urllib.parse.urljoin(self.URL, a.get('href'))
                        for a in cold_soup.find_all('a')}

                    catalogue = {}
                    for k, v in hot_soup.items():
                        sub_cat = get_catalogue(
                            v, update=True, confirmation_required=False, json_it=False)

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

                    if verbose == 2:
                        print("Done.")

                    save_data_to_file(
                        self, data=catalogue, data_name=data_name, ext=ext,
                        dump_dir=cd_data("catalogue"), verbose=verbose, indent=4)

                except Exception as e:
                    print(f"Failed. {format_err_msg(e)}")

        return catalogue

    @staticmethod
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

    @staticmethod
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

        dat0.sort_values(['Station'], ignore_index=True, inplace=True)

        return dat0

    @staticmethod
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

    @staticmethod
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

        temp1 = dat['Station'].str.split('\t\t', n=1, expand=True)
        temp1.columns = ['Station', 'CRS']
        dat['Station'] = temp1['Station'].str.rstrip(' / ').str.strip()

        # Get notes for stations
        stn_note_ = pd.Series('', index=dat.index)
        for i, x in enumerate(temp1['Station']):
            if '[' in x and ']' in x:
                y = re.search(r' \[(.*)](✖.*)?', x).group(0)  # Station Note
                dat.loc[i, 'Station'] = x.replace(y, '').strip()
                if '✖' in y:
                    stn_note_[i] = '; '.join([y_.strip(' []') for y_ in y.split('✖')])
                else:
                    stn_note_[i] = y.strip(' []')

        dat.insert(loc=dat.columns.get_loc('Station') + 1, column='Station Note', value=stn_note_)

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

        dat = pd.concat([dat, temp2], axis=1)

        return dat

    @staticmethod
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

    def _parse_owner_and_operator_columns(self, dat):
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
                dat[col].map(self._parse_owner_and_operator).to_list(),
                columns=[col, 'Former ' + col], index=dat.index)
            del dat[col]
            owner_operator.append(temp)

        dat = pd.concat([dat] + owner_operator, axis=1)

        return dat

    def collect_locations_by_initial(self, initial, update=False, verbose=False):
        """
        Collects data of `railway station locations
        <http://www.railwaycodes.org.uk/stations/station0.shtm>`_
        (mileages, operators and grid coordinates) for a given initial letter.

        :param initial: The initial letter (e.g. ``'a'``, ``'z'``) of railway station names.
        :type initial: str
        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``True``.
        :type verbose: bool | int
        :return: A dictionary containing the data of railway station locations whose initial letters
            are the given ``initial`` and date of when the data was last updated.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Stations  # from pyrcs import Stations
            >>> stn = Stations()
            >>> stn_loc_a_codes = stn.collect_locations_by_initial(initial='a')
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

        beginning_with = validate_initial(initial)
        initial_ = beginning_with.lower()

        ext = ".pkl"
        path_to_pickle = self._cdd("a-z", initial_ + ext)

        if os.path.isfile(path_to_pickle) and not update:
            data = load_data(path_to_pickle)

        else:
            if verbose == 2:
                print("Collecting data of {} of stations beginning with '{}')".format(
                    self.KEY_TO_STN.lower(), beginning_with), end=" ... ")

            data = {beginning_with: None, self.KEY_TO_LAST_UPDATED_DATE: None}

            # url = stn.URL.replace('station0', 'station{}'.format(initial_))
            url = self.URL.replace('station0', 'station{}'.format(initial_))
            try:
                source = requests.get(url=url, headers=fake_requests_headers())
            except Exception as e:
                if verbose == 2:
                    print("Failed. ", end="")
                print_inst_conn_err(verbose=verbose, e=e)

            else:
                try:
                    soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')
                    thead, tbody = soup.find('thead'), soup.find('tbody')

                    if any(x is None for x in {thead, tbody}):
                        if verbose == 2:
                            print(f"There are no stations starting with '{beginning_with}'.")

                    else:
                        # Create a DataFrame of the requested table
                        trs = tbody.find_all(name='tr')
                        ths = [
                            re.sub(r'\n?\r+\n?', ' ', h.text).strip() for h in thead.find_all('th')]
                        dat_ = parse_tr(trs=trs, ths=ths, as_dataframe=True)

                        dat = dat_.copy()

                        parser_funcs = [
                            self._split_elr_mileage_column,
                            self._check_row_spans,
                            self._parse_coordinates_columns,
                            self._parse_station_column,
                            self._parse_owner_and_operator_columns,
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

                        errata_ = {
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
                        # dat['Station'].replace(errata_, regex=True, inplace=True)
                        dat['Station'] = dat['Station'].replace(errata_, regex=True)

                        data = {
                            beginning_with: dat.sort_values('Station', ignore_index=True),
                            self.KEY_TO_LAST_UPDATED_DATE: get_last_updated_date(url, parsed=True)
                        }

                        if verbose == 2:
                            print("Done.")

                    save_data_to_file(
                        self, data=data, data_name=beginning_with, ext=ext,
                        dump_dir=self._cdd("a-z"), verbose=verbose)

                except Exception as e:
                    print(f"Failed. {format_err_msg(e)}")

        return data

    def fetch_locations(self, update=False, dump_dir=None, verbose=False):
        """
        Fetches the data of `railway station locations`_ (mileages, operators and grid coordinates).

        .. _`railway station locations`:
            http://www.railwaycodes.org.uk/stations/station0.shtm

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

        verbose_1 = collect_in_fetch_verbose(data_dir=dump_dir, verbose=verbose)
        verbose_2 = verbose_1 if is_home_connectable() else False

        data_sets = [
            self.collect_locations_by_initial(initial=x, update=update, verbose=verbose_2)
            for x in string.ascii_lowercase]

        if all(d[x] is None for d, x in zip(data_sets, string.ascii_uppercase)):
            if update:
                print_inst_conn_err(verbose=verbose)
                print_void_msg(data_name=self.KEY_TO_STN, verbose=verbose)

            data_sets = [
                self.collect_locations_by_initial(x, update=False, verbose=verbose_1)
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
            save_data_to_file(
                self, data=railway_station_data, data_name=self.KEY_TO_STN, ext=".pkl",
                dump_dir=dump_dir, verbose=verbose)

        return railway_station_data
