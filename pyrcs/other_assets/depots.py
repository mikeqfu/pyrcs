""" Collecting depots codes.

Data source: http://www.railwaycodes.org.uk/depots/depots0.shtm
"""

import copy
import os
import re
import urllib.parse

import bs4
import pandas as pd
import requests
from pyhelpers.dir import validate_input_data_dir
from pyhelpers.ops import confirmed
from pyhelpers.store import load_pickle, save_pickle

from pyrcs.utils import cd_dat, fake_requests_headers, get_catalogue, get_last_updated_date, homepage_url


class Depots:
    """
    A class for collecting depot codes.

    :param data_dir: name of data directory, defaults to ``None``
    :type data_dir: str, None
    :param update: whether to check on update and proceed to update the package data, defaults to ``False``
    :type update: bool

    **Example**::

        from pyrcs.other_assets import Depots

        depots = Depots()

        print(depots.Name)
        # Depot codes

        print(depots.SourceURL)
        # http://www.railwaycodes.org.uk/depots/depots0.shtm
    """

    def __init__(self, data_dir=None, update=False):
        """
        Constructor method.
        """
        self.Name = 'Depot codes'
        self.HomeURL = homepage_url()
        self.SourceURL = urllib.parse.urljoin(self.HomeURL, '/depots/depots0.shtm')
        self.Catalogue = get_catalogue(self.SourceURL, update=update, confirmation_required=False)
        self.Date = get_last_updated_date(self.SourceURL, parsed=True, as_date_type=False)
        self.Key = 'Depots'
        self.LUDKey = 'Last updated date'  # key to last updated date
        self.DataDir = validate_input_data_dir(data_dir) if data_dir else cd_dat("other-assets", self.Key.lower())
        self.CurrentDataDir = copy.copy(self.DataDir)
        self.TCTKey, self.FDPTKey, self.S1950Key, self.GWRKey = list(self.Catalogue.keys())[1:]
        self.TCTPickle = self.TCTKey.replace(" ", "-").lower()
        self.FDPTPickle = re.sub(r'[ -]', '-', self.FDPTKey).lower()
        self.S1950Pickle = re.sub(r' \(|\) | ', '-', self.S1950Key).lower()
        self.GWRPickle = self.GWRKey.replace(" ", "-").lower()

    def cdd_depots(self, *sub_dir):
        """
        Change directory to "dat\\other-assets\\depots\\" and sub-directories (and/or a file)

        :param sub_dir: sub-directory or sub-directories (and/or a file)
        :type sub_dir: str
        :return: path to the backup data directory for ``Depots``
        :rtype: str

        :meta private:
        """

        path = self.DataDir
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    def collect_two_char_tops_codes(self, confirmation_required=True, verbose=False):
        """
        Collect two-character TOPS codes from source web page.

        :param confirmation_required: whether to prompt a message for confirmation to proceed, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool, int
        :return: data of two-character TOPS codes and date of when the data was last updated
        :rtype: dict, None

        **Example**::

            from pyrcs.other_assets import Depots

            depots = Depots()

            confirmation_required = True

            two_char_tops_codes_data = depots.collect_two_char_tops_codes(confirmation_required)
            # To collect data of two character TOPS codes? [No]|Yes:
            # >? yes

            print(two_char_tops_codes_data)
            # {'Two character TOPS codes': <codes>,
            #  'Last updated date': <date>}
        """

        if confirmed("To collect data of {}?".format(self.TCTKey[:1].lower() + self.TCTKey[1:]),
                     confirmation_required=confirmation_required):

            url = self.Catalogue[self.TCTKey]

            if verbose == 2:
                print("Collecting data of {}".format(self.TCTKey[:1].lower() + self.TCTKey[1:]), end=" ... ")

            try:
                header, two_char_tops_codes = pd.read_html(url, na_values=[''], keep_default_na=False)
                two_char_tops_codes.columns = header.columns.to_list()
                two_char_tops_codes.fillna('', inplace=True)

                last_updated_date = get_last_updated_date(url)

                two_char_tops_codes_data = {self.TCTKey: two_char_tops_codes, self.LUDKey: last_updated_date}

                print("Done. ") if verbose == 2 else ""

                path_to_pickle = self.cdd_depots(self.TCTPickle + ".pickle")
                save_pickle(two_char_tops_codes_data, path_to_pickle, verbose=verbose)

            except Exception as e:
                print("Failed. {}".format(e))
                two_char_tops_codes_data = None

            return two_char_tops_codes_data

    def fetch_two_char_tops_codes(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch two-character TOPS codes from local backup.

        :param update: whether to check on update and proceed to update the package data, defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data with newly collected data, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str, None
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool
        :return: data of two-character TOPS codes and date of when the data was last updated
        :rtype: dict

        **Example**::

            from pyrcs.other_assets import Depots

            depots = Depots()

            update = False
            pickle_it = False
            data_dir = None

            two_char_tops_codes_data = depots.fetch_two_char_tops_codes(update, pickle_it, data_dir)

            print(two_char_tops_codes_data)
            # {'Two character TOPS codes': <codes>,
            #  'Last updated date': <date>}
        """

        path_to_pickle = self.cdd_depots(self.TCTPickle + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            two_char_tops_codes_data = load_pickle(path_to_pickle)

        else:
            two_char_tops_codes_data = self.collect_two_char_tops_codes(
                confirmation_required=False, verbose=False if data_dir or not verbose else True)

            if two_char_tops_codes_data:
                if pickle_it and data_dir:
                    self.CurrentDataDir = validate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, self.TCTPickle + ".pickle")
                    save_pickle(two_char_tops_codes_data, path_to_pickle, verbose=verbose)
            else:
                print("No data of {} has been collected.".format(self.TCTKey[:1].lower() + self.TCTKey[1:]))

        return two_char_tops_codes_data

    def collect_four_digit_pre_tops_codes(self, confirmation_required=True, verbose=False):
        """
        Collect four-digit pre-TOPS codes from source web page.

        :param confirmation_required: whether to prompt a message for confirmation to proceed, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool, int
        :return: data of two-character TOPS codes and date of when the data was last updated
        :rtype: dict, None

        **Example**::

            from pyrcs.other_assets import Depots

            depots = Depots()

            confirmation_required = True

            four_digit_pre_tops_codes = depots.collect_four_digit_pre_tops_codes(confirmation_required)
            # To collect data of four digit pre-TOPS codes? [No]|Yes:
            # >? yes

            print(four_digit_pre_tops_codes)
            # {'Four digit pre-TOPS codes': <codes>,
            #  'Last updated date': <date>}
        """

        if confirmed("To collect data of {}?".format(self.FDPTKey[:1].lower() + self.FDPTKey[1:]),
                     confirmation_required=confirmation_required):

            path_to_pickle = self.cdd_depots(self.FDPTPickle + ".pickle")

            url = self.Catalogue[self.FDPTKey]

            if verbose == 2:
                print("Collecting data of {}".format(self.FDPTKey[:1].lower() + self.FDPTKey[1:]), end=" ... ")

            try:
                source = requests.get(url, headers=fake_requests_headers())
                p_tags = bs4.BeautifulSoup(source.text, 'lxml').find_all('p')
                region_names = [x.text.replace('Jump to: ', '').strip().split(' | ')
                                for x in p_tags if x.text.startswith('Jump to: ')][0]

                data_sets = iter(pd.read_html(source.text, na_values=[''], keep_default_na=False))

                four_digit_pre_tops_codes_list = []
                for x in data_sets:
                    header, four_digit_pre_tops_codes_data = x, next(data_sets)
                    four_digit_pre_tops_codes_data.columns = header.columns.to_list()
                    four_digit_pre_tops_codes_list.append(four_digit_pre_tops_codes_data)

                last_updated_date = get_last_updated_date(url)

                four_digit_pre_tops_codes_data = {self.FDPTKey: dict(zip(region_names, four_digit_pre_tops_codes_list)),
                                                  self.LUDKey: last_updated_date}

                print("Done. ") if verbose == 2 else ""

                save_pickle(four_digit_pre_tops_codes_data, path_to_pickle, verbose=verbose)

            except Exception as e:
                print("Failed. {}".format(e))
                four_digit_pre_tops_codes_data = None

            return four_digit_pre_tops_codes_data

    def fetch_four_digit_pre_tops_codes(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch four-digit pre-TOPS codes from local backup.

        :param update: whether to check on update and proceed to update the package data, defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data with newly collected data, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str, None
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool
        :return: data of two-character TOPS codes and date of when the data was last updated
        :rtype: dict

        **Example**::

            from pyrcs.other_assets import Depots

            depots = Depots()

            update = False
            pickle_it = False
            data_dir = None

            four_digit_pretops_codes = depots.fetch_four_digit_pre_tops_codes(update, pickle_it, data_dir)

            print(four_digit_pretops_codes)
            # {'Four digit pre-TOPS codes': <codes>,
            #  'Last updated date': <date>}
        """

        path_to_pickle = self.cdd_depots(self.FDPTPickle + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            four_digit_pre_tops_codes_data = load_pickle(path_to_pickle)

        else:
            four_digit_pre_tops_codes_data = self.collect_four_digit_pre_tops_codes(
                confirmation_required=False, verbose=False if data_dir or not verbose else True)

            if four_digit_pre_tops_codes_data:
                if pickle_it and data_dir:
                    self.CurrentDataDir = validate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, os.path.basename(path_to_pickle))
                    save_pickle(four_digit_pre_tops_codes_data, path_to_pickle, verbose=verbose)

            else:
                print("No data of {} has been collected.".format(self.FDPTKey[:1].lower() + self.FDPTKey[1:]))

        return four_digit_pre_tops_codes_data

    def collect_1950_system_codes(self, confirmation_required=True, verbose=False):
        """
        Collect 1950 system (pre-TOPS) codes from source web page.

        :param confirmation_required: whether to prompt a message for confirmation to proceed, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool, int
        :return: data of 1950 system (pre-TOPS) codes and date of when the data was last updated
        :rtype: dict, None

        **Example**::

            from pyrcs.other_assets import Depots

            depots = Depots()

            confirmation_required = True

            system_1950_codes_data = depots.collect_1950_system_codes(confirmation_required)
            # To collect data of 1950 system (pre-TOPS) codes? [No]|Yes:
            # >? yes

            print(system_1950_codes_data)
            # {'1950 system (pre-TOPS) codes': <codes>,
            #  'Last updated date': <date>}
        """

        if confirmed("To collect data of {}?".format(self.S1950Key), confirmation_required=confirmation_required):

            url = self.Catalogue[self.S1950Key]

            if verbose == 2:
                print("Collecting data of {}".format(self.S1950Key), end=" ... ")

            try:
                header, system_1950_codes = pd.read_html(url, na_values=[''], keep_default_na=False)
                system_1950_codes.columns = header.columns.to_list()

                last_updated_date = get_last_updated_date(url)

                system_1950_codes_data = {self.S1950Key: system_1950_codes, self.LUDKey: last_updated_date}

                print("Done. ") if verbose == 2 else ""

                path_to_pickle = self.cdd_depots(self.S1950Pickle + ".pickle")
                save_pickle(system_1950_codes_data, path_to_pickle, verbose=verbose)

            except Exception as e:
                print("Failed. {}".format(e))
                system_1950_codes_data = None

            return system_1950_codes_data

    def fetch_1950_system_codes(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch 1950 system (pre-TOPS) codes from local backup.

        :param update: whether to check on update and proceed to update the package data, defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data with newly collected data, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str, None
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool
        :return: data of 1950 system (pre-TOPS) codes and date of when the data was last updated
        :rtype: dict

        **Example**::

            from pyrcs.other_assets import Depots

            depots = Depots()

            update = False
            pickle_it = False
            data_dir = None

            system_1950_codes_data = depots.fetch_1950_system_codes(update, pickle_it, data_dir)

            print(system_1950_codes_data)
            # {'1950 system (pre-TOPS) codes': <codes>,
            #  'Last updated date': <date>}
        """

        path_to_pickle = self.cdd_depots(self.S1950Pickle + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            system_1950_codes_data = load_pickle(path_to_pickle)

        else:
            system_1950_codes_data = self.collect_1950_system_codes(
                confirmation_required=False, verbose=False if data_dir or not verbose else True)

            if system_1950_codes_data:
                if pickle_it and data_dir:
                    self.CurrentDataDir = validate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, os.path.basename(path_to_pickle))
                    save_pickle(system_1950_codes_data, path_to_pickle, verbose=verbose)

            else:
                print("No data of {} has been collected.".format(self.S1950Key))

        return system_1950_codes_data

    def collect_gwr_codes(self, confirmation_required=True, verbose=False):
        """
        Collect Great Western Railway (GWR) depot codes from source web page.

        :param confirmation_required: whether to prompt a message for confirmation to proceed, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool, int
        :return: data of GWR depot codes and date of when the data was last updated
        :rtype: dict, None

        **Example**::

            from pyrcs.other_assets import Depots

            depots = Depots()

            confirmation_required = True

            gwr_codes_data = depots.collect_gwr_codes(confirmation_required)
            # To collect data of GWR codes? [No]|Yes:
            # >? yes

            print(gwr_codes_data)
            # {'GWR codes': <codes>,
            #  'Last updated date': <date>}
        """

        if confirmed("To collect data of {}?".format(self.GWRKey), confirmation_required=confirmation_required):

            url = self.Catalogue[self.GWRKey]

            if verbose == 2:
                print("Collecting data of {}".format(self.GWRKey), end=" ... ")

            try:
                header, alphabetical_codes, numerical_codes_1, _, numerical_codes_2 = pd.read_html(url)

                # Alphabetical codes
                alphabetical_codes.columns = header.columns.to_list()

                # Numerical codes
                numerical_codes_1.drop(1, axis=1, inplace=True)
                numerical_codes_1.columns = header.columns.to_list()
                numerical_codes_2.columns = header.columns.to_list()
                numerical_codes = pd.concat([numerical_codes_1, numerical_codes_2])

                source = requests.get(url)
                soup = bs4.BeautifulSoup(source.text, 'lxml')

                gwr_codes = dict(zip([x.text for x in soup.find_all('h3')], [alphabetical_codes, numerical_codes]))

                last_updated_date = get_last_updated_date(url)

                gwr_codes_data = {self.GWRKey: gwr_codes, self.LUDKey: last_updated_date}

                print("Done. ") if verbose == 2 else ""

                path_to_pickle = self.cdd_depots(self.GWRPickle + ".pickle")
                save_pickle(gwr_codes_data, path_to_pickle, verbose=verbose)

            except Exception as e:
                print("Failed. {}".format(e))
                gwr_codes_data = None

            return gwr_codes_data

    def fetch_gwr_codes(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch Great Western Railway (GWR) depot codes from local backup.

        :param update: whether to check on update and proceed to update the package data, defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data with newly collected data, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str, None
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool
        :return: data of GWR depot codes and date of when the data was last updated
        :rtype: dict

        **Example**::

            from pyrcs.other_assets import Depots

            depots = Depots()

            update = False
            pickle_it = False
            data_dir = None

            gwr_codes_data = depots.fetch_gwr_codes(update, pickle_it, data_dir)

            print(gwr_codes_data)
            # {'GWR codes': <codes>,
            #  'Last updated date': <date>}
        """

        path_to_pickle = self.cdd_depots(self.GWRPickle + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            gwr_codes_data = load_pickle(path_to_pickle)

        else:
            gwr_codes_data = self.collect_gwr_codes(
                confirmation_required=False, verbose=False if data_dir or not verbose else True)

            if gwr_codes_data:
                if pickle_it and data_dir:
                    self.CurrentDataDir = validate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, os.path.basename(path_to_pickle))
                    save_pickle(gwr_codes_data, path_to_pickle, verbose=verbose)

            else:
                print("No data of \"{}\" has been collected.".format(self.GWRKey))

        return gwr_codes_data

    def fetch_depot_codes(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch depots codes from local backup.

        :param update: whether to check on update and proceed to update the package data, defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data with newly collected data, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str, None
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool
        :return: data of depot codes and date of when the data was last updated
        :rtype: dict

        **Example**::

            from pyrcs.other_assets import Depots

            depots = Depots()

            update = False
            pickle_it = False
            data_dir = None

            depot_codes = depots.fetch_depot_codes(update, pickle_it, data_dir)

            print(depot_codes)
            # {'Depots': <codes>,
            #  'Last updated date': <date>}
        """

        codes = []
        for func in dir(self):
            if func.startswith('fetch_') and func != 'fetch_depot_codes':
                codes.append(getattr(self, func)(update=update, verbose=verbose))

        depot_codes = {self.Key: {next(iter(x)): next(iter(x.values())) for x in codes},
                       self.LUDKey: self.Date}

        if pickle_it and data_dir:
            self.CurrentDataDir = validate_input_data_dir(data_dir)
            path_to_pickle = os.path.join(self.CurrentDataDir, self.Key.lower() + ".pickle")
            save_pickle(depot_codes, path_to_pickle, verbose=verbose)

        return depot_codes
