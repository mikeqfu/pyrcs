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
import unicodedata
import urllib.parse

import bs4
import numpy as np
import pandas as pd
import requests
from pyhelpers.dir import cd, validate_input_data_dir
from pyhelpers.ops import confirmed, fake_requests_headers
from pyhelpers.store import load_pickle, save_pickle

from pyrcs.line_data.elec import Electrification
from pyrcs.utils import cd_dat, get_catalogue, get_last_updated_date, homepage_url


class Features:
    """
    A class for collecting codes of infrastructure features.

    :param data_dir: name of data directory, defaults to ``None``
    :type data_dir: str or None
    :param update: whether to check on update and proceed to update the package data, 
        defaults to ``False``
    :type update: bool

    **Example**::

        >>> from pyrcs.other_assets import Features

        >>> features = Features()

        >>> print(features.Name)
        Infrastructure features
    """

    def __init__(self, data_dir=None, update=False):
        """
        Constructor method.
        """
        self.Name = 'Infrastructure features'
        self.HomeURL = homepage_url()
        self.Key = 'Features'
        self.LUDKey = 'Last updated date'  # key to last updated date

        self.Catalogue = get_catalogue(
            urllib.parse.urljoin(self.HomeURL, '/misc/habdwild.shtm'),
            update=update, confirmation_required=False)

        self.HabdWildKey = 'HABD and WILD'
        self.HabdWildPickle = self.HabdWildKey.replace(" ", "-").lower()
        self.OLENeutralNetworkKey = 'OLE neutral sections'
        self.WaterTroughsKey = 'Water troughs'
        self.WaterTroughsPickle = self.WaterTroughsKey.replace(" ", "-").lower()
        self.TelegraphKey = 'Telegraphic codes'
        self.TelegraphPickle = self.TelegraphKey.lower().replace(" ", "-")
        self.BuzzerKey = 'Buzzer codes'
        self.BuzzerPickle = self.BuzzerKey.lower().replace(" ", "-")

        self.DataDir = validate_input_data_dir(data_dir) if data_dir \
            else cd_dat("other-assets", self.Name.lower())

        self.CurrentDataDir = copy.copy(self.DataDir)

    def cdd_features(self, *sub_dir, **kwargs):
        """
        Change directory to package data directory and sub-directories (and/or a file).

        The directory for this module: ``"\\dat\\other-assets\\features"``.

        :param sub_dir: sub-directory or sub-directories (and/or a file)
        :type sub_dir: str
        :param kwargs: optional parameters of
            `os.makedirs <https://docs.python.org/3/library/os.html#os.makedirs>`_,
            e.g. ``mode=0o777``
        :return: path to the backup data directory for ``Features``
        :rtype: str

        :meta private:
        """

        path = cd(self.DataDir, *sub_dir, mkdir=True, **kwargs)

        return path

    @staticmethod
    def parse_vulgar_fraction_in_length(x):
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
        Collect codes of `HABDs and WILDs
        <http://www.railwaycodes.org.uk/misc/habdwild.shtm>`_ from source web page.

            - HABDs - Hot axle box detectors
            - WILDs - Wheel impact load detectors

        :param confirmation_required: whether to prompt a message 
            for confirmation to proceed, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console 
            as the function runs, defaults to ``False``
        :type verbose: bool or int
        :return: data of HABDs and WILDs, and date of when the data was last updated
        :rtype: dict or None

        **Example**::

            >>> from pyrcs.other_assets import Features

            >>> features = Features()

            >>> habds_and_wilds_codes_dat = features.collect_habds_and_wilds()
            # To collect data of HABD and WILD? [No]|Yes: yes

            >>> type(habds_and_wilds_codes_dat)
            <class 'dict'>
            >>> print(list(habds_and_wilds_codes_dat.keys()))
            ['HABD and WILD', 'Last updated date']
        """

        if confirmed("To collect data of {}?".format(self.HabdWildKey),
                     confirmation_required=confirmation_required):

            url = self.Catalogue[self.HabdWildKey]

            if verbose == 2:
                print("Collecting data of {}".format(self.HabdWildKey), end=" ... ")

            try:
                sub_keys = self.HabdWildKey.split(' and ')
            except ValueError:
                sub_keys = [self.HabdWildKey + ' 1', self.HabdWildKey + ' 2']

            try:
                habds_and_wilds_codes = iter(
                    pd.read_html(url, na_values=[''], keep_default_na=False))

                habds_and_wilds_codes_list = []
                for x in habds_and_wilds_codes:
                    header, data = x, next(habds_and_wilds_codes)
                    data.columns = header.columns.to_list()
                    data.fillna('', inplace=True)
                    habds_and_wilds_codes_list.append(data)

                habds_and_wilds_codes_data = {
                    self.HabdWildKey: dict(zip(sub_keys, habds_and_wilds_codes_list)),
                    self.LUDKey: get_last_updated_date(url)}

                print("Done. ") if verbose == 2 else ""

                pickle_filename = self.HabdWildPickle + ".pickle"
                path_to_pickle = self.cdd_features(pickle_filename)
                save_pickle(habds_and_wilds_codes_data, path_to_pickle, verbose=verbose)

            except Exception as e:
                print("Failed. {}".format(e))
                habds_and_wilds_codes_data = None

            return habds_and_wilds_codes_data

    def fetch_habds_and_wilds(self, update=False, pickle_it=False, data_dir=None,
                              verbose=False):
        """
        Fetch codes of `HABDs and WILDs
        <http://www.railwaycodes.org.uk/misc/habdwild.shtm>`_ from local backup.

        :param update: whether to check on update and proceed to update the package data, 
            defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data 
            with newly collected data, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console 
            as the function runs, defaults to ``False``
        :type verbose: bool
        :return: data of hot axle box detectors (HABDs) and
            wheel impact load detectors (WILDs),
            and date of when the data was last updated
        :rtype: dict

        **Example**::

            >>> from pyrcs.other_assets import Features

            >>> features = Features()

            >>> habds_and_wilds_codes_dat = features.fetch_habds_and_wilds()

            >>> habds_and_wilds_codes = habds_and_wilds_codes_dat['HABD and WILD']
            >>> type(habds_and_wilds_codes)
            <class 'dict'>
            >>> print(list(habds_and_wilds_codes.keys()))
            ['HABD', 'WILD']

            >>> habd = habds_and_wilds_codes['HABD']
            >>> print(habd.head())
                ELR  ...                                              Notes
            0  BAG2  ...
            1  BAG2  ...  installed 29 September 1997, later adjusted to...
            2  BAG2  ...                             previously at 74m 51ch
            3  BAG2  ...                          removed 29 September 1997
            4  BAG2  ...            present in 1969, later moved to 89m 0ch

            [5 rows x 5 columns]
        """

        pickle_filename = self.HabdWildPickle + ".pickle"
        path_to_pickle = self.cdd_features(pickle_filename)

        if os.path.isfile(path_to_pickle) and not update:
            habds_and_wilds_codes_data = load_pickle(path_to_pickle)

        else:
            habds_and_wilds_codes_data = self.collect_habds_and_wilds(
                confirmation_required=False,
                verbose=False if data_dir or not verbose else True)

            if habds_and_wilds_codes_data:
                if pickle_it and data_dir:
                    self.CurrentDataDir = validate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(
                        self.CurrentDataDir, pickle_filename)

                    save_pickle(habds_and_wilds_codes_data, path_to_pickle,
                                verbose=verbose)

            else:
                print("No data of {} has been collected.".format(
                    self.HabdWildKey.replace("and", "or")))

        return habds_and_wilds_codes_data

    def collect_water_troughs(self, confirmation_required=True, verbose=False):
        """
        Collect codes of `water troughs
        <http://www.railwaycodes.org.uk/misc/troughs.shtm>`_ from source web page.

        :param confirmation_required: whether to prompt a message 
            for confirmation to proceed, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console 
            as the function runs, defaults to ``False``
        :type verbose: bool or int
        :return: data of water troughs, and date of when the data was last updated
        :rtype: dict or None

        **Example**::

            >>> from pyrcs.other_assets import Features

            >>> features = Features()

            >>> water_troughs_dat = features.collect_water_troughs()
            To collect data of water troughs? [No]|Yes: yes

            >>> type(water_troughs_dat)
            <class 'dict'>
            >>> print(water_troughs_dat)
            ['Water troughs', 'Last updated date']
        """

        url = self.Catalogue[self.WaterTroughsKey]

        if confirmed("To collect data of {}?".format(self.WaterTroughsKey.lower()),
                     confirmation_required=confirmation_required):

            if verbose == 2:
                print("Collecting data of {}".format(self.WaterTroughsKey.lower()),
                      end=" ... ")

            try:
                header, water_troughs_codes = pd.read_html(url)

                water_troughs_codes.columns = header.columns.to_list()
                water_troughs_codes.fillna('', inplace=True)
                water_troughs_codes.Length = water_troughs_codes.Length.map(
                    self.parse_vulgar_fraction_in_length)
                water_troughs_codes.rename(
                    columns={'Length': 'Length_yard'}, inplace=True)

                last_updated_date = get_last_updated_date(url)

                water_troughs_data = {self.WaterTroughsKey: water_troughs_codes,
                                      self.LUDKey: last_updated_date}

                print("Done. ") if verbose == 2 else ""

                path_to_pickle = self.cdd_features(self.WaterTroughsPickle + ".pickle")
                save_pickle(water_troughs_data, path_to_pickle, verbose=verbose)

            except Exception as e:
                print("Failed. {}".format(e))
                water_troughs_data = None

            return water_troughs_data

    def fetch_water_troughs(self, update=False, pickle_it=False, data_dir=None,
                            verbose=False):
        """
        Fetch codes of water troughs from local backup.

        :param update: whether to check on update and proceed to update the package data, 
            defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data 
            with newly collected data, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console 
            as the function runs, defaults to ``False``
        :type verbose: bool
        :return: data of water troughs, and date of when the data was last updated
        :rtype: dict

        **Example**::

            >>> from pyrcs.other_assets import Features

            >>> features = Features()

            >>> water_troughs_dat = features.fetch_water_troughs()

            >>> water_troughs_codes = water_troughs_dat['Water troughs']

            >>> type(water_troughs_codes)
            <class 'pandas.core.frame.DataFrame'>
            >>> print(water_troughs_codes.head())
                ELR  Trough Name  ... Length_yard                        Notes
            0   BEI    Eckington  ...         NaN
            1   BHL  Aldermaston  ...  620.000000            Installed by 1904
            2  CGJ2        Moore  ...  506.666667
            3  CGJ6     Lea Road  ...  561.000000  Taken out of use 8 May 1967
            4  CGJ6        Brock  ...  560.000000

            [5 rows x 5 columns]
        """

        path_to_pickle = self.cdd_features(self.WaterTroughsPickle + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            water_troughs_data = load_pickle(path_to_pickle)

        else:
            water_troughs_data = self.collect_water_troughs(
                confirmation_required=False,
                verbose=False if data_dir or not verbose else True)

            if water_troughs_data:
                if pickle_it and data_dir:
                    self.CurrentDataDir = validate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(
                        self.CurrentDataDir, os.path.basename(path_to_pickle))

                    save_pickle(water_troughs_data, path_to_pickle, verbose=verbose)

            else:
                print("No data of {} has been collected.".format(
                    self.WaterTroughsKey.lower()))

        return water_troughs_data

    def collect_telegraph_codes(self, confirmation_required=True, verbose=False):
        """
        Collect `telegraph code words
        <http://www.railwaycodes.org.uk/misc/telegraph.shtm>`_ from source web page.

        :param confirmation_required: whether to prompt a message 
            for confirmation to proceed, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console 
            as the function runs, defaults to ``False``
        :type verbose: bool or int
        :return: data of telegraph code words, and date of when the data was last updated
        :rtype: dict or None

        **Example**::

            >>> from pyrcs.other_assets import Features

            >>> features = Features()

            >>> telegraph_codes_dat = features.collect_telegraph_codes()
            To collect data of telegraphic codes? [No]|Yes: yes

            >>> type(telegraph_codes_dat)
            <class 'dict'>
            >>> print(list(telegraph_codes_dat.keys()))
            ['Telegraphic codes', 'Last updated date']
        """

        url = self.Catalogue[self.TelegraphKey]

        if confirmed("To collect data of {}?".format(self.TelegraphKey.lower()),
                     confirmation_required=confirmation_required):

            if verbose == 2:
                print("Collecting data of {}".format(self.TelegraphKey.lower()),
                      end=" ... ")

            try:
                source = requests.get(url, headers=fake_requests_headers())
                #
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

                print("Done. ") if verbose == 2 else ""

                path_to_pickle = self.cdd_features(self.TelegraphPickle + ".pickle")
                save_pickle(telegraph_code_words, path_to_pickle, verbose=verbose)

            except Exception as e:
                print("Failed. {}".format(e))
                telegraph_code_words = None

            return telegraph_code_words

    def fetch_telegraph_codes(self, update=False, pickle_it=False, data_dir=None,
                              verbose=False):
        """
        Fetch `telegraph code words
        <http://www.railwaycodes.org.uk/misc/telegraph.shtm>`_ from local backup.

        :param update: whether to check on update and proceed to update the package data, 
            defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data 
            with newly collected data, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console 
            as the function runs, defaults to ``False``
        :type verbose: bool
        :return: data of telegraph code words, and date of when the data was last updated
        :rtype: dict

        **Example**::

            >>> from pyrcs.other_assets import Features

            >>> features = Features()

            >>> telegraph_codes_dat = features.fetch_telegraph_codes()

            >>> telegraph_codes = telegraph_codes_dat['Telegraphic codes']
            >>> type(telegraph_codes)
            <class 'dict'>
            >>> print(list(telegraph_codes.keys()))
            ['Official codes', 'Unofficial codes']

            >>> official_codes = telegraph_codes['Official codes']
            >>> type(official_codes)
            <class 'pandas.core.frame.DataFrame'>
            >>> print(official_codes.head())
                Code  ...               In use
            0    ACK  ...            BR, 1980s
            1   ADEX  ...  GWR, 1939 BR, 1980s
            2   AJAX  ...            BR, 1980s
            3  ALERT  ...            BR, 1980s
            4  AMBER  ...            BR, 1980s

            [5 rows x 3 columns]
        """

        path_to_pickle = self.cdd_features(self.TelegraphPickle + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            telegraph_code_words = load_pickle(path_to_pickle)

        else:
            telegraph_code_words = self.collect_telegraph_codes(
                confirmation_required=False,
                verbose=False if data_dir or not verbose else True)

            if telegraph_code_words:
                if pickle_it and data_dir:
                    self.CurrentDataDir = validate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(
                        self.CurrentDataDir, os.path.basename(path_to_pickle))
                    save_pickle(telegraph_code_words, path_to_pickle, verbose=verbose)

            else:
                print("No data of {} has been collected.".format(
                    self.TelegraphKey.lower()))

        return telegraph_code_words

    def collect_buzzer_codes(self, confirmation_required=True, verbose=False):
        """
        Collect `buzzer codes
        <http://www.railwaycodes.org.uk/misc/buzzer.shtm>`_ from source web page.

        :param confirmation_required: whether to prompt a message 
            for confirmation to proceed, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console 
            as the function runs, defaults to ``False``
        :type verbose: bool or int
        :return: data of buzzer codes, and date of when the data was last updated
        :rtype: dict or None

        **Example**::

            >>> from pyrcs.other_assets import Features

            >>> features = Features()

            >>> buzzer_codes_dat = features.collect_buzzer_codes()
            To collect data of buzzer codes? [No]|Yes:  yes

            >>> type(buzzer_codes_dat)
            <class 'dict'>
            >>> print(list(buzzer_codes_dat.keys()))
            ['Buzzer codes', 'Last updated date']
        """

        url = self.Catalogue[self.BuzzerKey]

        if confirmed("To collect data of {}?".format(self.BuzzerKey.lower()),
                     confirmation_required=confirmation_required):

            if verbose == 2:
                print("Collecting data of {}".format(self.BuzzerKey), end=" ... ")

            try:
                header, buzzer_codes = pd.read_html(url)
                buzzer_codes.columns = header.columns.to_list()
                buzzer_codes.fillna('', inplace=True)

                last_updated_date = get_last_updated_date(url)

                buzzer_codes_data = {self.BuzzerKey: buzzer_codes,
                                     self.LUDKey: last_updated_date}

                print("Done. ") if verbose == 2 else ""

                path_to_pickle = self.cdd_features(self.BuzzerPickle + ".pickle")
                save_pickle(buzzer_codes_data, path_to_pickle, verbose=verbose)

            except Exception as e:
                print("Failed. {}".format(e))
                buzzer_codes_data = None

            return buzzer_codes_data

    def fetch_buzzer_codes(self, update=False, pickle_it=False, data_dir=None,
                           verbose=False):
        """
        Fetch `buzzer codes
        <http://www.railwaycodes.org.uk/misc/buzzer.shtm>`_ from local backup.

        :param update: whether to check on update and proceed to update the package data, 
            defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data 
            with newly collected data, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console 
            as the function runs, defaults to ``False``
        :type verbose: bool
        :return: data of buzzer codes, and date of when the data was last updated
        :rtype: dict

        **Example**::

            >>> from pyrcs.other_assets import Features

            >>> features = Features()

            >>> buzzer_codes_dat = features.fetch_buzzer_codes()

            >>> buzzer_codes = buzzer_codes_dat['Buzzer codes']
            >>> type(buzzer_codes)
            <class 'pandas.core.frame.DataFrame'>
            >>> print(buzzer_codes.head())
             Code (number of buzzes or groups separated by pauses)             Meaning
            0                                                   1                 Stop
            1                                                 1-2          Close doors
            2                                                   2       Ready to start
            3                                                 2-2    Do not open doors
            4                                                   3             Set back
        """

        path_to_pickle = self.cdd_features(self.BuzzerPickle + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            buzzer_codes_data = load_pickle(path_to_pickle)

        else:
            buzzer_codes_data = self.collect_buzzer_codes(
                confirmation_required=False,
                verbose=False if data_dir or not verbose else True)

            if buzzer_codes_data:
                if pickle_it and data_dir:
                    self.CurrentDataDir = validate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(
                        self.CurrentDataDir, os.path.basename(path_to_pickle))

                    save_pickle(buzzer_codes_data, path_to_pickle, verbose=verbose)

            else:
                print("No data of {} has been collected.".format(self.BuzzerKey.lower()))

        return buzzer_codes_data

    def fetch_features_codes(self, update=False, pickle_it=False, data_dir=None,
                             verbose=False):
        """
        Fetch features codes from local backup.

        :param update: whether to check on update and proceed to update the package data, 
            defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data 
            with newly collected data, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console 
            as the function runs, defaults to ``False``
        :type verbose: bool
        :return: data of features codes and date of when the data was last updated
        :rtype: dict

        **Example**::

            >>> from pyrcs.other_assets import Features

            >>> features = Features()

            >>> features_codes_dat = features.fetch_features_codes()

            >>> type(features_codes_dat)
            <class 'dict'>
            >>> print(list(features_codes_dat.keys()))
            ['Features', 'Last updated date']
        """

        features_codes = []
        for func in dir(self):
            if func.startswith('fetch_') and func != 'fetch_features_codes':
                features_codes.append(getattr(self, func)(update=update, verbose=verbose))

        elec = Electrification()
        ohns_codes = elec.fetch_ohns_codes(update=update, verbose=verbose)
        features_codes.append(ohns_codes)

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
