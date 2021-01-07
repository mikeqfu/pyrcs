"""
Collect codes of infrastructure features.

This category includes:

    - `OLE neutral sections <http://www.railwaycodes.org.uk/electrification/neutral.shtm>`_
    - `HABD and WILD <http://www.railwaycodes.org.uk/misc/habdwild.shtm>`_
    - `Water troughs <http://www.railwaycodes.org.uk/misc/troughs.shtm>`_
    - `Telegraph codes <http://www.railwaycodes.org.uk/misc/telegraph.shtm>`_
    - `Driver/guard buzzer codes <http://www.railwaycodes.org.uk/misc/buzzer.shtm>`_
"""

import copy
import itertools
import os
import re
import socket
import unicodedata
import urllib.error
import urllib.parse

import bs4
import numpy as np
import pandas as pd
import requests
from pyhelpers.dir import cd, validate_input_data_dir
from pyhelpers.ops import confirmed, fake_requests_headers
from pyhelpers.store import load_pickle, save_pickle

from pyrcs.line_data.elec import Electrification
from pyrcs.utils import cd_dat, get_catalogue, get_last_updated_date, homepage_url, \
    is_internet_connected, print_connection_error, print_conn_err


class Features:
    """
    A class for collecting codes of infrastructure features.

    :param data_dir: name of data directory, defaults to ``None``
    :type data_dir: str or None
    :param update: whether to check on update and proceed to update the package data, 
        defaults to ``False``
    :type update: bool
    :param verbose: whether to print relevant information in console as the function runs,
        defaults to ``True``
    :type verbose: bool or int

    :ivar str Name: name of the data
    :ivar str Key: key of the dict-type data
    :ivar str HomeURL: URL of the main homepage
    :ivar str LUDKey: key of the last updated date
    :ivar dict Catalogue: catalogue of the data
    :ivar str DataDir: path to the data directory
    :ivar str CurrentDataDir: path to the current data directory

    :ivar str HabdWildKey: key of the dict-type data of HABD and WILD
    :ivar str HabdWildPickle: name of the pickle file of HABD and WILD
    :ivar str OLENeutralNetworkKey: key of the dict-type data of OLE neutral sections
    :ivar str WaterTroughsKey: key of the dict-type data of water troughs
    :ivar str WaterTroughsPickle: name of the pickle file of water troughs
    :ivar str TelegraphKey: key of the dict-type data of telegraphic codes
    :ivar str TelegraphPickle: name of the pickle file of telegraphic codes
    :ivar str BuzzerKey: key of the dict-type data of buzzer codes
    :ivar str BuzzerPickle: name of the pickle file of buzzer codes

    **Example**::

        >>> from pyrcs.other_assets import Features

        >>> features = Features()

        >>> print(features.Name)
        Infrastructure features
    """

    def __init__(self, data_dir=None, update=False, verbose=True):
        """
        Constructor method.
        """
        if not is_internet_connected():
            print_connection_error(verbose=verbose)

        self.Name = 'Infrastructure features'
        self.Key = 'Features'
        self.HomeURL = homepage_url()
        self.LUDKey = 'Last updated date'  # key to last updated date

        self.Catalogue = get_catalogue(
            urllib.parse.urljoin(self.HomeURL, '/features/habdwild.shtm'),
            update=update, confirmation_required=False)

        if data_dir:
            self.DataDir = validate_input_data_dir(data_dir)
        else:
            self.DataDir = cd_dat("other-assets", self.Name.lower())
        self.CurrentDataDir = copy.copy(self.DataDir)

        self.HabdWildKey = 'HABD and WILD'
        self.HabdWildPickle = self.HabdWildKey.replace(" ", "-").lower()
        self.OLENeutralNetworkKey = 'OLE neutral sections'
        self.WaterTroughsKey = 'Water troughs'
        self.WaterTroughsPickle = self.WaterTroughsKey.replace(" ", "-").lower()
        self.TelegraphKey = 'Telegraphic codes'
        self.TelegraphPickle = self.TelegraphKey.lower().replace(" ", "-")
        self.BuzzerKey = 'Buzzer codes'
        self.BuzzerPickle = self.BuzzerKey.lower().replace(" ", "-")

    def _cdd_feat(self, *sub_dir, **kwargs):
        """
        Change directory to package data directory and sub-directories (and/or a file).

        The directory for this module: ``"\\dat\\other-assets\\features"``.

        :param sub_dir: sub-directory or sub-directories (and/or a file)
        :type sub_dir: str
        :param kwargs: optional parameters of `os.makedirs`_, e.g. ``mode=0o777``
        :return: path to the backup data directory for ``Features``
        :rtype: str

        .. _`os.makedirs`: https://docs.python.org/3/library/os.html#os.makedirs

        :meta private:
        """

        path = cd(self.DataDir, *sub_dir, mkdir=True, **kwargs)

        return path

    @staticmethod
    def _parse_vulgar_fraction_in_length(x):
        """
        Parse 'VULGAR FRACTION' for 'Length' of water trough locations.
        """

        def decode_vulgar_fraction():
            """
            Decode vulgar fraction.
            """

            for s in x:
                try:
                    name = unicodedata.name(s)
                    if name.startswith('VULGAR FRACTION'):
                        # normalized = unicodedata.normalize('NFKC', s)
                        # numerator, _, denominator = normalized.partition('⁄')
                        # frac_val = int(numerator) / int(denominator)
                        frac_val = unicodedata.numeric(s)
                        return frac_val
                except (TypeError, ValueError):
                    pass

        if x == '':
            yd = np.nan

        elif re.match(r'\d+yd', x):  # e.g. '620yd'
            yd = int(re.search(r'\d+(?=yd)', x).group(0))

        elif re.match(r'\d+&frac\d+;yd', x):  # e.g. '506&frac23;yd'
            yd, frac = re.search(r'([0-9]+)&frac([0-9]+)(?=;yd)', x).groups()
            yd = int(yd) + int(frac[0]) / int(frac[1])

        else:  # e.g. '557½yd'
            yd = decode_vulgar_fraction()

        return yd

    def collect_habds_and_wilds(self, confirmation_required=True, verbose=False):
        """
        Collect codes of `HABDs and WILDs <http://www.railwaycodes.org.uk/misc/habdwild.shtm>`_ 
        from source web page.

            - HABDs - Hot axle box detectors
            - WILDs - Wheel impact load detectors

        :param confirmation_required: whether to prompt a message for confirmation to proceed, 
            defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console as the function runs,
            defaults to ``False``
        :type verbose: bool or int
        :return: data of HABDs and WILDs, and date of when the data was last updated
        :rtype: dict or None

        **Example**::

            >>> from pyrcs.other_assets import Features

            >>> features = Features()

            >>> hw_codes_dat = features.collect_habds_and_wilds()
            # To collect data of HABD and WILD? [No]|Yes: yes

            >>> type(hw_codes_dat)
            dict
            >>> list(hw_codes_dat.keys())
            ['HABD and WILD', 'Last updated date']

            >>> hw_codes = hw_codes_dat['HABD and WILD']

            >>> type(hw_codes)
            dict
            >>> list(hw_codes.keys())
            ['HABD', 'WILD']

            >>> habd = hw_codes['HABD']
            >>> print(habd.head())
                ELR  ...                                              Notes
            0  BAG2  ...
            1  BAG2  ...  installed 29 September 1997, later adjusted to...
            2  BAG2  ...                             previously at 74m 51ch
            3  BAG2  ...                          removed 29 September 1997
            4  BAG2  ...            present in 1969, later moved to 89m 0ch
            [5 rows x 5 columns]

            >>> wild = hw_codes['WILD']
            >>> print(wild.head())
                ELR  ...                                Notes
            0  AYR3  ...
            1  BAG2  ...
            2  BML1  ...
            3  BML1  ...
            4  CGJ3  ...  moved to 183m 68ch 8 September 2018
            [5 rows x 5 columns]
        """

        if confirmed("To collect data of {}?".format(self.HabdWildKey),
                     confirmation_required=confirmation_required):

            url = self.Catalogue[self.HabdWildKey]

            if verbose == 2:
                print("Collecting data of {}".format(self.HabdWildKey), end=" ... ")

            habds_and_wilds_codes_data = None

            try:
                habds_and_wilds_codes = iter(
                    pd.read_html(url, na_values=[''], keep_default_na=False))
            except (urllib.error.URLError, socket.gaierror):
                print("Failed. ") if verbose == 2 else ""
                print_conn_err(verbose=verbose)

            else:
                try:
                    sub_keys = self.HabdWildKey.split(' and ')
                except ValueError:
                    sub_keys = [self.HabdWildKey + ' 1', self.HabdWildKey + ' 2']

                try:
                    habds_and_wilds_codes_list = []
                    for x in habds_and_wilds_codes:
                        header, data = x, next(habds_and_wilds_codes)
                        data.columns = header.columns.to_list()
                        data.fillna('', inplace=True)
                        habds_and_wilds_codes_list.append(data)

                    last_updated_date = get_last_updated_date(url)

                    print("Done.") if verbose == 2 else ""

                    habds_and_wilds_codes_data = {
                        self.HabdWildKey: dict(zip(sub_keys, habds_and_wilds_codes_list)),
                        self.LUDKey: last_updated_date}

                    pickle_filename = self.HabdWildPickle + ".pickle"
                    path_to_pickle = self._cdd_feat(pickle_filename)
                    save_pickle(habds_and_wilds_codes_data, path_to_pickle, verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(e))

            return habds_and_wilds_codes_data

    def fetch_habds_and_wilds(self, update=False, pickle_it=False, data_dir=None,
                              verbose=False):
        """
        Fetch codes of `HABDs and WILDs <http://www.railwaycodes.org.uk/misc/habdwild.shtm>`_
        from local backup.

        :param update: whether to check on update and proceed to update the package data, 
            defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data with newly collected data,
            defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console as the function runs,
            defaults to ``False``
        :type verbose: bool
        :return: data of hot axle box detectors (HABDs) and wheel impact load detectors (WILDs),
            and date of when the data was last updated
        :rtype: dict

        **Example**::

            >>> from pyrcs.other_assets import Features

            >>> features = Features()

            >>> # hw_codes_dat = features.fetch_habds_and_wilds(update=True, verbose=True)
            >>> hw_codes_dat = features.fetch_habds_and_wilds()

            >>> hw_codes = hw_codes_dat['HABD and WILD']
            >>> type(hw_codes)
            dict
            >>> list(hw_codes.keys())
            ['HABD', 'WILD']

            >>> habd = hw_codes['HABD']
            >>> print(habd.head())
                ELR  ...                                              Notes
            0  BAG2  ...
            1  BAG2  ...  installed 29 September 1997, later adjusted to...
            2  BAG2  ...                             previously at 74m 51ch
            3  BAG2  ...                          removed 29 September 1997
            4  BAG2  ...            present in 1969, later moved to 89m 0ch
            [5 rows x 5 columns]

            >>> wild = hw_codes['WILD']
            >>> print(wild.head())
                ELR  ...                                Notes
            0  AYR3  ...
            1  BAG2  ...
            2  BML1  ...
            3  BML1  ...
            4  CGJ3  ...  moved to 183m 68ch 8 September 2018
            [5 rows x 5 columns]
        """

        pickle_filename = self.HabdWildPickle + ".pickle"
        path_to_pickle = self._cdd_feat(pickle_filename)

        if os.path.isfile(path_to_pickle) and not update:
            habds_and_wilds_codes_data = load_pickle(path_to_pickle)

        else:
            verbose_ = False if data_dir or not verbose else (2 if verbose == 2 else True)

            habds_and_wilds_codes_data = self.collect_habds_and_wilds(
                confirmation_required=False, verbose=verbose_)

            if habds_and_wilds_codes_data:
                if pickle_it and data_dir:
                    self.CurrentDataDir = validate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, pickle_filename)

                    save_pickle(habds_and_wilds_codes_data, path_to_pickle, verbose=verbose)

            else:
                print("No data of {} has been collected.".format(
                    self.HabdWildKey.replace("and", "or")))
                habds_and_wilds_codes_data = load_pickle(path_to_pickle)

        return habds_and_wilds_codes_data

    def collect_water_troughs(self, confirmation_required=True, verbose=False):
        """
        Collect codes of `water troughs <http://www.railwaycodes.org.uk/misc/troughs.shtm>`_
        from source web page.

        :param confirmation_required: whether to prompt a message for confirmation to proceed, 
            defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console as the function runs,
            defaults to ``False``
        :type verbose: bool or int
        :return: data of water troughs, and date of when the data was last updated
        :rtype: dict or None

        **Example**::

            >>> from pyrcs.other_assets import Features

            >>> features = Features()

            >>> wt_codes_dat = features.collect_water_troughs()
            To collect data of water troughs? [No]|Yes: yes

            >>> type(wt_codes_dat)
            dict
            >>> list(wt_codes_dat.keys())
            ['Water troughs', 'Last updated date']

            >>> wt_codes = wt_codes_dat['Water troughs']
            >>> print(wt_codes.head())
                ELR  Trough Name  ... Length_yard                                        Notes
            0   BEI    Eckington  ...         NaN                               Installed 1904
            1   BHL  Aldermaston  ...  620.000000                            Installed by 1904
            2  CGJ2        Moore  ...  506.666667                              Installed 1860s
            3  CGJ6     Lea Road  ...  561.000000  Installed 1885, taken out of use 8 May 1967
            4  CGJ6        Brock  ...  560.000000                              Installed 1860s
            [5 rows x 5 columns]
        """

        url = self.Catalogue[self.WaterTroughsKey]

        if confirmed("To collect data of {}?".format(self.WaterTroughsKey.lower()),
                     confirmation_required=confirmation_required):

            if verbose == 2:
                print("Collecting data of {}".format(self.WaterTroughsKey.lower()), end=" ... ")

            water_troughs_data = None

            try:
                header, water_troughs_codes = pd.read_html(url)
            except (urllib.error.URLError, socket.gaierror):
                print("Failed. ") if verbose == 2 else ""
                print_conn_err(verbose=verbose)

            else:
                try:
                    water_troughs_codes.columns = header.columns.to_list()
                    water_troughs_codes.fillna('', inplace=True)
                    water_troughs_codes.Length = water_troughs_codes.Length.map(
                        self._parse_vulgar_fraction_in_length)
                    water_troughs_codes.rename(columns={'Length': 'Length_yard'}, inplace=True)

                    last_updated_date = get_last_updated_date(url)

                    print("Done.") if verbose == 2 else ""

                    water_troughs_data = {self.WaterTroughsKey: water_troughs_codes,
                                          self.LUDKey: last_updated_date}

                    path_to_pickle = self._cdd_feat(self.WaterTroughsPickle + ".pickle")
                    save_pickle(water_troughs_data, path_to_pickle, verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(e))

            return water_troughs_data

    def fetch_water_troughs(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch codes of `water troughs <http://www.railwaycodes.org.uk/misc/troughs.shtm>`_
        from local backup.

        :param update: whether to check on update and proceed to update the package data, 
            defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data with newly collected data,
            defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console as the function runs,
            defaults to ``False``
        :type verbose: bool
        :return: data of water troughs, and date of when the data was last updated
        :rtype: dict

        **Example**::

            >>> from pyrcs.other_assets import Features

            >>> features = Features()

            >>> # wt_codes_dat = features.fetch_water_troughs(update=True, verbose=True)
            >>> wt_codes_dat = features.fetch_water_troughs()

            >>> type(wt_codes_dat)
            dict
            >>> list(wt_codes_dat.keys())
            ['Water troughs', 'Last updated date']

            >>> wt_codes = wt_codes_dat['Water troughs']
            >>> print(wt_codes.head())
                ELR  Trough Name  ... Length_yard                                        Notes
            0   BEI    Eckington  ...         NaN                               Installed 1904
            1   BHL  Aldermaston  ...  620.000000                            Installed by 1904
            2  CGJ2        Moore  ...  506.666667                              Installed 1860s
            3  CGJ6     Lea Road  ...  561.000000  Installed 1885, taken out of use 8 May 1967
            4  CGJ6        Brock  ...  560.000000                              Installed 1860s
            [5 rows x 5 columns]
        """

        path_to_pickle = self._cdd_feat(self.WaterTroughsPickle + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            water_troughs_data = load_pickle(path_to_pickle)

        else:
            verbose_ = False if data_dir or not verbose else (2 if verbose == 2 else True)

            water_troughs_data = self.collect_water_troughs(confirmation_required=False,
                                                            verbose=verbose_)

            if water_troughs_data:
                if pickle_it and data_dir:
                    self.CurrentDataDir = validate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(
                        self.CurrentDataDir, os.path.basename(path_to_pickle))

                    save_pickle(water_troughs_data, path_to_pickle, verbose=verbose)

            else:
                print("No data of {} has been collected.".format(self.WaterTroughsKey.lower()))
                water_troughs_data = load_pickle(path_to_pickle)

        return water_troughs_data

    def collect_telegraph_codes(self, confirmation_required=True, verbose=False):
        """
        Collect `telegraph code words <http://www.railwaycodes.org.uk/misc/telegraph.shtm>`_
        from source web page.

        :param confirmation_required: whether to prompt a message for confirmation to proceed, 
            defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console as the function runs,
            defaults to ``False``
        :type verbose: bool or int
        :return: data of telegraph code words, and date of when the data was last updated
        :rtype: dict or None

        **Example**::

            >>> from pyrcs.other_assets import Features

            >>> features = Features()

            >>> tel_codes_dat = features.collect_telegraph_codes()
            To collect data of telegraphic codes? [No]|Yes: yes

            >>> type(tel_codes_dat)
            dict
            >>> list(tel_codes_dat.keys())
            ['Telegraphic codes', 'Last updated date']

            >>> tel_codes = tel_codes_dat['Telegraphic codes']

            >>> type(tel_codes)
            dict
            >>> list(tel_codes.keys())
            ['Official codes', 'Unofficial codes']

            >>> print(tel_codes['Official codes'].head())
                 Code  ...               In use
            0  ACACIA  ...    'companies', 1939
            1     ACK  ...            BR, 1980s
            2    ADEX  ...  GWR, 1939 BR, 1980s
            3    AJAX  ...            BR, 1980s
            4   ALERT  ...            BR, 1980s
            [5 rows x 3 columns]
        """

        url = self.Catalogue[self.TelegraphKey]

        if confirmed("To collect data of {}?".format(self.TelegraphKey.lower()),
                     confirmation_required=confirmation_required):

            if verbose == 2:
                print("Collecting data of {}".format(self.TelegraphKey.lower()), end=" ... ")

            telegraph_code_words = None

            try:
                source = requests.get(url, headers=fake_requests_headers())
            except requests.ConnectionError:
                print("Failed. ") if verbose == 2 else ""
                print_conn_err(verbose=verbose)

            else:
                try:
                    sub_keys = [
                        x.text for x in bs4.BeautifulSoup(source.text, 'lxml').find_all('h3')]
                    #
                    data_sets = iter(pd.read_html(source.text))
                    telegraph_codes_list = []
                    for x in data_sets:
                        header, telegraph_codes = x, next(data_sets)
                        telegraph_codes.columns = header.columns.to_list()
                        telegraph_codes_list.append(telegraph_codes)

                    last_updated_date = get_last_updated_date(url)

                    telegraph_code_words = {
                        self.TelegraphKey: dict(zip(sub_keys, telegraph_codes_list)),
                        self.LUDKey: last_updated_date}

                    print("Done.") if verbose == 2 else ""

                    path_to_pickle = self._cdd_feat(self.TelegraphPickle + ".pickle")
                    save_pickle(telegraph_code_words, path_to_pickle, verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(e))

            return telegraph_code_words

    def fetch_telegraph_codes(self, update=False, pickle_it=False, data_dir=None,
                              verbose=False):
        """
        Fetch `telegraph code words <http://www.railwaycodes.org.uk/misc/telegraph.shtm>`_
        from local backup.

        :param update: whether to check on update and proceed to update the package data, 
            defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data with newly collected data,
            defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console as the function runs,
            defaults to ``False``
        :type verbose: bool
        :return: data of telegraph code words, and date of when the data was last updated
        :rtype: dict

        **Example**::

            >>> from pyrcs.other_assets import Features

            >>> features = Features()

            >>> # tel_codes_dat = features.fetch_telegraph_codes(update=True, verbose=True)
            >>> tel_codes_dat = features.fetch_telegraph_codes()

            >>> tel_codes = tel_codes_dat['Telegraphic codes']
            >>> type(tel_codes)
            dict
            >>> list(tel_codes.keys())
            ['Official codes', 'Unofficial codes']

            >>> official_codes = tel_codes['Official codes']
            >>> type(official_codes)
            pandas.core.frame.DataFrame
            >>> print(official_codes.head())
                 Code  ...               In use
            0  ACACIA  ...    'companies', 1939
            1     ACK  ...            BR, 1980s
            2    ADEX  ...  GWR, 1939 BR, 1980s
            3    AJAX  ...            BR, 1980s
            4   ALERT  ...            BR, 1980s
            [5 rows x 3 columns]
        """

        path_to_pickle = self._cdd_feat(self.TelegraphPickle + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            telegraph_code_words = load_pickle(path_to_pickle)

        else:
            verbose_ = False if data_dir or not verbose else (2 if verbose == 2 else True)

            telegraph_code_words = self.collect_telegraph_codes(
                confirmation_required=False, verbose=verbose_)

            if telegraph_code_words:
                if pickle_it and data_dir:
                    self.CurrentDataDir = validate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(
                        self.CurrentDataDir, os.path.basename(path_to_pickle))
                    save_pickle(telegraph_code_words, path_to_pickle, verbose=verbose)

            else:
                print("No data of {} has been collected.".format(self.TelegraphKey.lower()))
                telegraph_code_words = load_pickle(path_to_pickle)

        return telegraph_code_words

    def collect_buzzer_codes(self, confirmation_required=True, verbose=False):
        """
        Collect `buzzer codes <http://www.railwaycodes.org.uk/misc/buzzer.shtm>`_
        from source web page.

        :param confirmation_required: whether to prompt a message for confirmation to proceed, 
            defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console as the function runs,
            defaults to ``False``
        :type verbose: bool or int
        :return: data of buzzer codes, and date of when the data was last updated
        :rtype: dict or None

        **Example**::

            >>> from pyrcs.other_assets import Features

            >>> features = Features()

            >>> buz_codes_dat = features.collect_buzzer_codes()
            To collect data of buzzer codes? [No]|Yes:  yes

            >>> type(buz_codes_dat)
            dict
            >>> list(buz_codes_dat.keys())
            ['Buzzer codes', 'Last updated date']

            >>> buz_codes = buz_codes_dat['Buzzer codes']
            >>> print(buz_codes.head())
              Code number of buzzes or groups separated by pauses            Meaning
            0                                                  1                Stop
            1                                                1-2         Close doors
            2                                                  2      Ready to start
            3                                                2-2   Do not open doors
            4                                                  3            Set back
        """

        url = self.Catalogue[self.BuzzerKey]

        if confirmed("To collect data of {}?".format(self.BuzzerKey.lower()),
                     confirmation_required=confirmation_required):

            if verbose == 2:
                print("Collecting data of {}".format(self.BuzzerKey), end=" ... ")

            buzzer_codes_data = None

            try:
                header, buzzer_codes = pd.read_html(url)
            except (urllib.error.URLError, socket.gaierror):
                print("Failed. ") if verbose == 2 else ""
                print_conn_err(verbose=verbose)

            else:
                try:
                    buzzer_codes.columns = header.columns.to_list()
                    buzzer_codes.fillna('', inplace=True)

                    last_updated_date = get_last_updated_date(url)

                    buzzer_codes_data = {self.BuzzerKey: buzzer_codes,
                                         self.LUDKey: last_updated_date}

                    print("Done.") if verbose == 2 else ""

                    path_to_pickle = self._cdd_feat(self.BuzzerPickle + ".pickle")
                    save_pickle(buzzer_codes_data, path_to_pickle, verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(e))

            return buzzer_codes_data

    def fetch_buzzer_codes(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch `buzzer codes <http://www.railwaycodes.org.uk/misc/buzzer.shtm>`_ from local backup.

        :param update: whether to check on update and proceed to update the package data, 
            defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data with newly collected data,
            defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console as the function runs,
            defaults to ``False``
        :type verbose: bool
        :return: data of buzzer codes, and date of when the data was last updated
        :rtype: dict

        **Example**::

            >>> from pyrcs.other_assets import Features

            >>> features = Features()

            >>> # buz_codes_dat = features.fetch_buzzer_codes(verbose=True, update=True)
            >>> buz_codes_dat = features.fetch_buzzer_codes()

            >>> type(buz_codes_dat)
            dict
            >>> list(buz_codes_dat.keys())
            ['Buzzer codes', 'Last updated date']

            >>> buz_codes = buz_codes_dat['Buzzer codes']

            >>> type(buz_codes)
            pandas.core.frame.DataFrame
            >>> print(buz_codes.head())
             Code (number of buzzes or groups separated by pauses)             Meaning
            0                                                   1                 Stop
            1                                                 1-2          Close doors
            2                                                   2       Ready to start
            3                                                 2-2    Do not open doors
            4                                                   3             Set back
        """

        path_to_pickle = self._cdd_feat(self.BuzzerPickle + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            buzzer_codes_data = load_pickle(path_to_pickle)

        else:
            verbose_ = False if data_dir or not verbose else (2 if verbose == 2 else True)

            buzzer_codes_data = self.collect_buzzer_codes(confirmation_required=False,
                                                          verbose=verbose_)

            if buzzer_codes_data:
                if pickle_it and data_dir:
                    self.CurrentDataDir = validate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(
                        self.CurrentDataDir, os.path.basename(path_to_pickle))

                    save_pickle(buzzer_codes_data, path_to_pickle, verbose=verbose)

            else:
                print("No data of {} has been collected.".format(self.BuzzerKey.lower()))
                buzzer_codes_data = load_pickle(path_to_pickle)

        return buzzer_codes_data

    def fetch_features_codes(self, update=False, pickle_it=False, data_dir=None,
                             verbose=False):
        """
        Fetch features codes from local backup.

        :param update: whether to check on update and proceed to update the package data, 
            defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data with newly collected data,
            defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console as the function runs,
            defaults to ``False``
        :type verbose: bool
        :return: data of features codes and date of when the data was last updated
        :rtype: dict

        **Example**::

            >>> from pyrcs.other_assets import Features

            >>> features = Features()

            >>> # feat_codes_dat = features.fetch_features_codes(update=True, verbose=True)
            >>> feat_codes_dat = features.fetch_features_codes()

            >>> type(feat_codes_dat)
            dict
            >>> list(feat_codes_dat.keys())
            ['Features', 'Last updated date']

            >>> feat_codes = feat_codes_dat['Features']

            >>> type(feat_codes)
            dict
            >>> list(feat_codes.keys())
            ['National network neutral sections',
             'Buzzer codes',
             'HABD and WILD',
             'Telegraphic codes',
             'Water troughs']

             >>> print(feat_codes['National network neutral sections'].head())
                ELR         OHNS Name  Mileage    Tracks Dates
            0  ARG1        Rutherglen   0m 3ch
            1  ARG2   Finnieston East  4m 23ch      Down
            2  ARG2   Finnieston West  4m 57ch        Up
            3  AYR1  Shields Junction  0m 68ch    Up Ayr
            4  AYR1  Shields Junction  0m 69ch  Down Ayr
        """

        verbose_ = False if (data_dir or not verbose) else (2 if verbose == 2 else True)

        features_codes = []

        elec = Electrification(verbose=False)
        ohns_codes = elec.fetch_ohns_codes(update=update, verbose=verbose_)
        features_codes.append(ohns_codes)

        for func in dir(self):
            if func.startswith('fetch_') and func != 'fetch_features_codes':
                features_codes.append(getattr(self, func)(
                    update=update, verbose=verbose_ if is_internet_connected() else False))

        features_codes_data = {
            self.Key: {next(iter(x)): next(iter(x.values())) for x in features_codes},
            self.LUDKey: max(next(itertools.islice(iter(x.values()), 1, 2))
                             for x in features_codes)}

        if pickle_it and data_dir:
            self.CurrentDataDir = validate_input_data_dir(data_dir)
            path_to_pickle = os.path.join(
                self.CurrentDataDir, self.Key.lower().replace(" ", "-") + ".pickle")
            save_pickle(features_codes_data, path_to_pickle, verbose=verbose)

        return features_codes_data
