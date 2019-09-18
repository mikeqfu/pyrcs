""" Depots """

import os
import re

import bs4
import pandas as pd
import requests
from pyhelpers.dir import regulate_input_data_dir
from pyhelpers.misc import confirmed
from pyhelpers.store import load_pickle

from pyrcs.utils import cd_dat, get_catalogue, get_last_updated_date
from pyrcs.utils import save_pickle


class Depots:
    def __init__(self, data_dir=None):
        self.HomeURL = 'http://www.railwaycodes.org.uk'
        self.Name = 'Depot codes'
        self.URL = self.HomeURL + '/depots/depots0.shtm'
        self.Catalogue = get_catalogue(self.URL)
        self.Date = get_last_updated_date(self.URL, parsed=True, date_type=False)
        self.DataDir = regulate_input_data_dir(data_dir) if data_dir else cd_dat("other-assets", "depots")
        self.CurrentDataDir = self.DataDir

    # Change directory to "dat\\other-assets\\depots\\"
    def cd_depots(self, *directories):
        path = self.DataDir
        for x in directories:
            path = os.path.join(path, x)
        return path

    # Change directory to "dat\\other-assets\\depots\\dat"
    def cdd_sigbox(self, *sub_dir):
        path = self.cd_depots("dat")
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    # Collect 'Two character TOPS codes'
    def collect_two_char_tops_codes(self, confirmation_required=True, verbose=False):
        if confirmed("To collect two character TOPS codes?", confirmation_required=confirmation_required):
            title_name = list(self.Catalogue.keys())[1]
            url = self.Catalogue[title_name]

            try:
                header, two_char_tops_codes = pd.read_html(url, na_values=[''], keep_default_na=False)
                two_char_tops_codes.columns = header.columns.to_list()
                two_char_tops_codes.fillna('', inplace=True)

                last_updated_date = get_last_updated_date(url)

                two_char_tops_codes_data = {title_name.replace(' ', '_'): two_char_tops_codes,
                                            'Last_updated_date': last_updated_date}

                path_to_pickle = self.cd_depots(title_name.replace(" ", "-").lower() + ".pickle")
                save_pickle(two_char_tops_codes_data, path_to_pickle, verbose)

            except Exception as e:
                print("Failed to collect \"{}\". {}".format(title_name, e))
                two_char_tops_codes_data = None

            return two_char_tops_codes_data

    # Fetch 'Two character TOPS codes'
    def fetch_two_char_tops_codes(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        title_name = list(self.Catalogue.keys())[1]
        path_to_pickle = self.cd_depots(title_name.replace(" ", "-").lower() + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            two_char_tops_codes_data = load_pickle(path_to_pickle)

        else:
            two_char_tops_codes_data = self.collect_two_char_tops_codes(
                confirmation_required=False, verbose=False if data_dir or not verbose else True)
            if two_char_tops_codes_data:
                if pickle_it and data_dir:
                    self.CurrentDataDir = regulate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, os.path.basename(path_to_pickle))
                    save_pickle(two_char_tops_codes_data, path_to_pickle, verbose=True)
            else:
                print("No data of \"{}\" has been collected.".format(title_name))
        return two_char_tops_codes_data

    # Collect 'Four digit pre-TOPS codes'
    def collect_four_digit_pre_tops_codes(self, confirmation_required=True, verbose=False):
        if confirmed("To collect four digit pre-TOPS codes?", confirmation_required=confirmation_required):
            title_name = list(self.Catalogue.keys())[2]
            path_to_pickle = self.cd_depots(re.sub(r'[ -]', '-', title_name).lower() + ".pickle")

            url = self.Catalogue[title_name]

            try:
                source = requests.get(url)
                p_tags = bs4.BeautifulSoup(source.text, 'lxml').find_all('p')
                region_names = [x.text.replace('Jump to: ', '').strip().split(' | ')
                                for x in p_tags if x.text.startswith('Jump to: ')][0]

                data_sets = iter(pd.read_html(source.text, na_values=[''], keep_default_na=False))

                four_digit_pre_tops_codes_list = []
                for x in data_sets:
                    header, four_digit_pre_tops_codes = x, next(data_sets)
                    four_digit_pre_tops_codes.columns = header.columns.to_list()
                    four_digit_pre_tops_codes_list.append(four_digit_pre_tops_codes)

                last_updated_date = get_last_updated_date(url)

                four_digit_pre_tops_codes_data = {
                    re.sub(r'[ \-]', '_', title_name): dict(zip(region_names, four_digit_pre_tops_codes_list)),
                    'Last_updated_date': last_updated_date}
                save_pickle(four_digit_pre_tops_codes_data, path_to_pickle, verbose)

            except Exception as e:
                print("Failed to collect \"{}\". {}".format(title_name, e))
                four_digit_pre_tops_codes_data = None

            return four_digit_pre_tops_codes_data

    # Fetch 'Four digit pre-TOPS codes'
    def fetch_four_digit_pre_tops_codes(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        title_name = list(self.Catalogue.keys())[2]
        path_to_pickle = self.cd_depots(re.sub(r'[ -]', '-', title_name).lower() + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            four_digit_pre_tops_codes_data = load_pickle(path_to_pickle)

        else:
            four_digit_pre_tops_codes_data = self.collect_four_digit_pre_tops_codes(
                confirmation_required=False, verbose=False if data_dir or not verbose else True)
            if four_digit_pre_tops_codes_data:
                if pickle_it and data_dir:
                    self.CurrentDataDir = regulate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, os.path.basename(path_to_pickle))
                    save_pickle(four_digit_pre_tops_codes_data, path_to_pickle, verbose=True)
            else:
                print("No data of \"{}\" has been collected.".format(title_name))

        return four_digit_pre_tops_codes_data

    # Collect '1950 system (pre-TOPS) codes'
    def collect_1950_system_codes(self, confirmation_required=True, verbose=False):
        if confirmed("To collect 1950 system (pre-TOPS) codes?", confirmation_required=confirmation_required):
            title_name = list(self.Catalogue.keys())[3]
            url = self.Catalogue[title_name]

            try:
                header, system_1950_codes = pd.read_html(url, na_values=[''], keep_default_na=False)
                system_1950_codes.columns = header.columns.to_list()

                title_name_ = re.sub(r'[ -]', '_', re.sub(r'[()]', '', title_name))
                path_to_pickle = self.cd_depots(title_name_.replace("_", "-").lower() + ".pickle")

                last_updated_date = get_last_updated_date(url)

                system_1950_codes_data = {title_name_: system_1950_codes, 'Last_updated_date': last_updated_date}

                save_pickle(system_1950_codes_data, path_to_pickle, verbose)

            except Exception as e:
                print("Failed to collect the data of \"{}\". {}".format(title_name, e))
                system_1950_codes_data = None

            return system_1950_codes_data

    # Fetch '1950 system (pre-TOPS) codes'
    def fetch_1950_system_codes(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        title_name = list(self.Catalogue.keys())[3]
        title_name_ = re.sub(r'[ -]', '_', re.sub(r'[()]', '', title_name))
        path_to_pickle = self.cd_depots(title_name_.lower() + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            system_1950_codes_data = load_pickle(path_to_pickle)

        else:
            system_1950_codes_data = self.collect_1950_system_codes(
                confirmation_required=False, verbose=False if data_dir or not verbose else True)
            if system_1950_codes_data:
                if pickle_it and data_dir:
                    self.CurrentDataDir = regulate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, os.path.basename(path_to_pickle))
                    save_pickle(system_1950_codes_data, path_to_pickle, verbose=True)
            else:
                print("No data of \"{}\" has been collected.".format(title_name))

        return system_1950_codes_data

    # Collect 'GWR codes' - Great Western Railway depot codes
    def collect_gwr_codes(self, confirmation_required=True, verbose=False):
        if confirmed("To collect Great Western Railway depot codes?", confirmation_required=confirmation_required):
            title_name = list(self.Catalogue.keys())[4]
            url = self.Catalogue[title_name]

            try:
                header, gwr_codes = pd.read_html(url)
                gwr_codes.columns = header.columns.to_list()

                last_updated_date = get_last_updated_date(url)
                gwr_codes_data = {title_name.replace(' ', '_'): gwr_codes, 'Last_updated_date': last_updated_date}

                path_to_pickle = self.cd_depots(title_name.replace(" ", "-").lower() + ".pickle")
                save_pickle(gwr_codes_data, path_to_pickle, verbose)

            except Exception as e:
                print("Failed to collect the data of \"{}.\" {}".format(title_name, e))
                gwr_codes_data = None

            return gwr_codes_data

    #
    def fetch_gwr_codes(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        title_name = list(self.Catalogue.keys())[4]
        path_to_pickle = self.cd_depots(title_name.replace(" ", "-").lower() + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            gwr_codes_data = load_pickle(path_to_pickle)

        else:
            gwr_codes_data = self.collect_gwr_codes(
                confirmation_required=False, verbose=False if data_dir or not verbose else True)
            if gwr_codes_data:
                if pickle_it and data_dir:
                    self.CurrentDataDir = regulate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, os.path.basename(path_to_pickle))
                    save_pickle(gwr_codes_data, path_to_pickle, verbose=True)
            else:
                print("No data of \"{}\" has been collected.".format(title_name))

        return gwr_codes_data

    # Fetch all the collected depots codes
    def fetch_depot_codes(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        two_char_tops_codes_data = self.fetch_two_char_tops_codes(update, verbose=verbose)
        four_digit_pre_tops_codes_data = self.fetch_four_digit_pre_tops_codes(update, verbose=verbose)
        system_1950_codes_data = self.fetch_1950_system_codes(update, verbose=verbose)
        gwr_codes_data = self.fetch_gwr_codes(update, verbose=verbose)

        depot_codes = {}
        for x in (two_char_tops_codes_data, four_digit_pre_tops_codes_data, system_1950_codes_data, gwr_codes_data):
            old_key = list(x.keys())[0]
            x['Data'] = x.pop(old_key)
            depot_codes.update({old_key: x})

        if pickle_it and data_dir:
            self.CurrentDataDir = regulate_input_data_dir(data_dir)
            path_to_pickle = os.path.join(self.CurrentDataDir, "depot-codes.pickle")
            save_pickle(depot_codes, path_to_pickle)

        return depot_codes
