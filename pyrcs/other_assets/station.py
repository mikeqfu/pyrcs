"""
Collect `railway station data <http://www.railwaycodes.org.uk/stations/station0.shtm>`_.
"""

import os
import re
import string
import urllib.parse

import bs4
import numpy as np
import pandas as pd
import requests
from pyhelpers.dirs import cd
from pyhelpers.ops import fake_requests_headers
from pyhelpers.store import load_data

from ..parser import get_catalogue, get_last_updated_date, parse_tr
from ..utils import cd_data, collect_in_fetch_verbose, home_page_url, init_data_dir, \
    is_home_connectable, print_conn_err, print_inst_conn_err, print_void_msg, save_data_to_file, \
    validate_initial


def _parse_degrees(x):
    if x.strip() == '':
        y = np.nan
    else:
        y = float(re.sub(r'(c\.)|≈', '', x))

    return y


def _parse_station(x):
    """
    x = stn_loc['Station'][3]
    """

    x_ = x.split(' / ')
    note_ = 'believed no CRS issued'

    if len(x_) > 1:
        stn_name, stn_note = x_
    elif f'[{note_}]' in x:
        stn_name, stn_note = re.sub(r'(\[)?{}(])?'.format(note_), '', x).strip(), note_
    else:
        stn_name, stn_note = x, ''

    crs_code = ''
    crs_code_ = stn_name[-6:]
    if crs_code_.startswith(' ('):
        crs_code = stn_name[-4:-1]  # stn_name[stn_name.find('(') + 1:stn_name.find(')')]
        stn_name = stn_name[:-6]

    return stn_name, crs_code, stn_note


def _parse_owner_and_operator(x):
    """
    x = stn_loc['Owner'][2]
    """

    sep = ' / '
    x_ = x.split(sep)

    if len(x_) > 1:
        owner_or_operator = x_[0]
        if len(x_[1:]) > 1:
            former_owners_or_operators = sep.join(x_[1:])
        else:
            former_owners_or_operators = x_[1:]

    else:
        owner_or_operator, former_owners_or_operators = x_[0], ''

    return owner_or_operator, former_owners_or_operators


class Stations:
    """A class for collecting `railway station data`_.

    .. _`railway station data`: http://www.railwaycodes.org.uk/stations/station0.shtm
    """

    #: Name of the data
    NAME = 'Railway station data'
    #: Key of the `dict <https://docs.python.org/3/library/stdtypes.html#dict>`_-type data
    KEY = 'Stations'

    #: Key of the dict-type data of '*Mileages, operators and grid coordinates*'
    KEY_TO_STN = 'Mileages, operators and grid coordinates'

    #: URL of the main web page of the data
    URL = urllib.parse.urljoin(home_page_url(), '/stations/station0.shtm')

    #: Key of the data of the last updated date
    KEY_TO_LAST_UPDATED_DATE = 'Last updated date'

    def __init__(self, data_dir=None, update=False, verbose=True):
        """
        :param data_dir: name of data directory, defaults to ``None``
        :type data_dir: str or None
        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console, defaults to ``True``
        :type verbose: bool or int

        :ivar dict catalogue: catalogue of the data
        :ivar str last_updated_date: last updated date
        :ivar str data_dir: path to the data directory
        :ivar str current_data_dir: path to the current data directory

        **Examples**::

            >>> from pyrcs.other_assets import Stations

            >>> stn = Stations()

            >>> print(stn.NAME)
            Railway station data

            >>> print(stn.URL)
            http://www.railwaycodes.org.uk/stations/station0.shtm
        """

        print_conn_err(verbose=verbose)

        self.catalogue = self._get_station_data_catalogue(update=update, verbose=False)

        self.last_updated_date = get_last_updated_date(url=self.URL, parsed=True, as_date_type=False)

        self.data_dir, self.current_data_dir = init_data_dir(self, data_dir, category="other-assets")

    def _get_station_data_catalogue(self, update=False, verbose=False):
        """
        Get catalogue of railway station data.

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: catalogue of railway station data
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Stations  # from pyrcs import Stations

            >>> stn = Stations()

            >>> stn_data_cat = stn._get_station_data_catalogue()
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

        data_name = urllib.parse.urlparse(self.URL).path.lstrip('/').rstrip('.shtm').replace('/', '-')
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
                        for a in cold_soup.find_all('a')
                    }

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
                    print("Failed. {}".format(e))

        return catalogue

    def _cdd(self, *sub_dir, **kwargs):
        """
        Change directory to package data directory and subdirectories (and/or a file).

        The directory for this module: ``"data\\other-assets\\stations"``.

        :param sub_dir: subdirectory or subdirectories (and/or a file)
        :type sub_dir: str
        :param kwargs: [optional] parameters of the function `pyhelpers.dir.cd`_
        :return: path to the backup data directory for the class
            :py:class:`~pyrcs.other_assets.station.Stations`
        :rtype: str

        .. _`pyhelpers.dir.cd`:
            https://pyhelpers.readthedocs.io/en/latest/_generated/pyhelpers.dir.cd.html
        """

        path = cd(self.data_dir, *sub_dir, mkdir=True, **kwargs)

        return path

    def collect_locations_by_initial(self, initial, update=False, verbose=False):
        """
        Collect `data of railway station locations
        <http://www.railwaycodes.org.uk/stations/station0.shtm>`_
        (mileages, operators and grid coordinates) for a given initial letter.

        :param initial: initial letter of locations of the railway station data
        :type initial: str
        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of railway station locations beginning with the given initial letter and
            date of when the data was last updated
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Stations  # from pyrcs import Stations

            >>> stn = Stations()

            >>> stn_locations_a = stn.collect_locations_by_initial(initial='a')
            >>> type(stn_locations_a)
            dict
            >>> list(stn_locations_a.keys())
            ['A', 'Last updated date']

            >>> stn_locations_a_codes = stn_locations_a['A']
            >>> type(stn_locations_a_codes)
            pandas.core.frame.DataFrame
            >>> stn_locations_a_codes.head()
                       Station  ...                                    Former Operator
            0       Abbey Wood  ...  London & South Eastern Railway from 1 April 20...
            1       Abbey Wood  ...
            2             Aber  ...  Keolis Amey Operations/Gweithrediadau Keolis A...
            3        Abercynon  ...  Keolis Amey Operations/Gweithrediadau Keolis A...
            4  Abercynon North  ...  [Cardiff Railway Company from 13 October 1996 ...

            [5 rows x 13 columns]
        """

        beginning_with = validate_initial(initial)
        initial_ = beginning_with.lower()

        ext = ".pickle"
        path_to_pickle = self._cdd("a-z", initial_ + ext)

        if os.path.isfile(path_to_pickle) and not update:
            location_codes_ = load_data(path_to_pickle)

        else:
            if verbose == 2:
                print("Collecting data of {} of stations beginning with '{}')".format(
                    self.KEY_TO_STN.lower(), beginning_with), end=" ... ")

            location_codes_ = {beginning_with: None, self.KEY_TO_LAST_UPDATED_DATE: None}

            try:
                url = self.URL.replace('station0', 'station{}'.format(initial_))
                # url = stn.URL.replace('station0', 'station{}'.format(beginning_with.lower()))
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
                            # f"There are no British towns starting with '{beginning_with}'.

                    else:
                        # Create a DataFrame of the requested table
                        trs = tbody.find_all(name='tr')
                        ths = [re.sub(r'\n?\r+\n?', ' ', h.text).strip() for h in thead.find_all('th')]
                        stn_loc = parse_tr(trs=trs, ths=ths, as_dataframe=True)

                        # Check 'row spans'
                        temp0 = stn_loc['Degrees Longitude'].str.split(' / ')
                        temp1 = stn_loc[temp0.map(len).map(lambda x: True if x > 1 else False)]
                        cols = [
                            'ELR', 'Mileage', 'Degrees Longitude', 'Degrees Latitude', 'Grid Reference']
                        cols_ = [x for x in temp1.columns if x not in cols]
                        temp_dat = []
                        for col in cols:
                            # noinspection PyUnresolvedReferences
                            temp2 = temp1[col].map(lambda x: x.split(' / '))
                            if cols.index(col) == 0:
                                # noinspection PyTypeChecker
                                temp_dat_ = temp1[cols_].join(temp2).explode(col)
                                temp_dat_.index = range(len(temp_dat_))
                            else:
                                temp_dat_ = temp2.explode(col).to_frame()
                            temp_dat.append(temp_dat_)

                        temp_data = pd.concat(temp_dat, axis=1)
                        temp_data = temp_data[stn_loc.columns.to_list()]

                        stn_loc = pd.concat(
                            [stn_loc.drop(index=temp1.index), temp_data], axis=0, ignore_index=True)

                        stn_loc.sort_values(['Station'], inplace=True)

                        # Convert data type of the longitudes and latitudes
                        ll_col_names = ['Degrees Longitude', 'Degrees Latitude']
                        stn_loc.loc[:, ll_col_names] = stn_loc[ll_col_names].applymap(_parse_degrees)

                        # Cleanse 'Station'
                        stn_col_name = 'Station'
                        stn_info = stn_loc[stn_col_name].map(_parse_station).apply(pd.Series)
                        stn_info.columns = [stn_col_name, 'CRS', 'Note']
                        del stn_loc[stn_col_name]
                        stn_loc = pd.concat([stn_info, stn_loc], axis=1)

                        # Parse 'Owner'
                        owner_operator = []
                        for col in ['Owner', 'Operator']:
                            temp_info = stn_loc[col].map(_parse_owner_and_operator).apply(pd.Series)
                            temp_info.columns = [col, 'Former ' + col]
                            del stn_loc[col]
                            owner_operator.append(temp_info)

                        location_codes_[beginning_with] = pd.concat([stn_loc] + owner_operator, axis=1)

                        last_updated_date = get_last_updated_date(url=url, parsed=True)
                        location_codes_[self.KEY_TO_LAST_UPDATED_DATE] = last_updated_date

                        if verbose == 2:
                            print("Done.")

                    save_data_to_file(
                        self, data=location_codes_, data_name=beginning_with, ext=ext,
                        dump_dir=self._cdd("a-z"), verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(e))

        return location_codes_

    def fetch_locations(self, update=False, dump_dir=None, verbose=False):
        """
        Fetch `data of railway station locations`_ (mileages, operators and grid coordinates).

        .. _`data of railway station locations`: http://www.railwaycodes.org.uk/stations/station0.shtm

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param dump_dir: name of a folder where the pickle file is to be saved, defaults to ``None``
        :type dump_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of railway station locations and date of when the data was last updated
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Stations  # from pyrcs import Stations

            >>> stn = Stations()

            >>> stn_location_codes = stn.fetch_locations()
            >>> type(stn_location_codes)
            dict
            >>> list(stn_location_codes.keys())
            ['Mileages, operators and grid coordinates', 'Last updated date']

            >>> stn.KEY_TO_STN
            'Mileages, operators and grid coordinates'

            >>> stn_location_codes_dat = stn_location_codes[stn.KEY_TO_STN]
            >>> type(stn_location_codes_dat)
            pandas.core.frame.DataFrame
            >>> stn_location_codes_dat.head()
                       Station  ...                                    Former Operator
            0       Abbey Wood  ...  London & South Eastern Railway from 1 April 20...
            1       Abbey Wood  ...
            2             Aber  ...  Keolis Amey Operations/Gweithrediadau Keolis A...
            3        Abercynon  ...  Keolis Amey Operations/Gweithrediadau Keolis A...
            4  Abercynon North  ...  [Cardiff Railway Company from 13 October 1996 ...

            [5 rows x 13 columns]
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
                self, data=railway_station_data, data_name=self.KEY_TO_STN, ext=".pickle",
                dump_dir=dump_dir, verbose=verbose)

        return railway_station_data
