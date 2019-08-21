""" Depots """

import os

import bs4
import pandas as pd
import requests
from pyhelpers.dir import regulate_input_data_dir
from pyhelpers.store import load_pickle

from pyrcs.utils import cd_dat, get_cls_catalogue, get_last_updated_date
from pyrcs.utils import save_pickle


class Depots:
    def __init__(self, data_dir=None):
        self.HomeURL = 'http://www.railwaycodes.org.uk'
        self.Name = 'Depot codes'
        self.URL = self.HomeURL + '/depots/depots0.shtm'
        self.Catalogue = get_cls_catalogue(self.URL)
        self.Date = get_last_updated_date(self.URL, parsed=True, date_type=False)
        self.DataDir = regulate_input_data_dir(data_dir) if data_dir else cd_dat("Other assets", "Depots")

    # Change directory to "dat\\Other assets\\Signal Boxes\\"
    def cd_depots(self, *directories):
        path = self.DataDir
        for x in directories:
            path = os.path.join(path, x)
        return path

    # Change directory to "dat\\Other assets\\Signal Boxes\\dat"
    def cdd_sigbox(self, *sub_dir):
        path = self.cd_depots("dat")
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    # Collect 'Two character TOPS codes'
    def collect_two_char_tops_codes(self, update=False):
        title_name = list(self.Catalogue.keys())[1]
        path_to_pickle = self.cd_depots(title_name.replace(" ", "-") + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            two_char_tops_codes_data = load_pickle(path_to_pickle)

        else:
            url = self.Catalogue[title_name]

            try:
                last_updated_date = get_last_updated_date(url)
            except Exception as e:
                print("Failed to find the last update date for \"{}.\" {}".format(title_name, e))
                last_updated_date = ''

            try:
                header, two_char_tops_codes = pd.read_html(url, na_values=[''], keep_default_na=False)
                two_char_tops_codes.columns = header.columns.to_list()
                two_char_tops_codes.fillna('', inplace=True)
            except Exception as e:
                print("Failed to collect \"{}.\" {}".format(title_name, e))
                two_char_tops_codes = None

            two_char_tops_codes_data = {title_name.replace(' ', '_'): two_char_tops_codes,
                                        'Last_updated_date': last_updated_date}
            save_pickle(two_char_tops_codes_data, path_to_pickle)

        return two_char_tops_codes_data

    # Collect 'Four digit pre-TOPS codes'
    def collect_four_digit_pre_tops_codes(self, update=False):
        title_name = list(self.Catalogue.keys())[2]
        path_to_pickle = self.cd_depots(title_name.replace(" ", "-") + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            four_digit_pre_tops_codes_data = load_pickle(path_to_pickle)

        else:
            url = self.Catalogue[title_name]

            try:
                last_updated_date = get_last_updated_date(url)
            except Exception as e:
                print("Failed to find the last update date for \"{}.\" {}".format(title_name, e))
                last_updated_date = ''

            try:
                source = requests.get(url)
                source_text = source.text
                p_tags = bs4.BeautifulSoup(source_text, 'lxml').find_all('p')
                region_names = [x.text.replace('Jump to: ', '').strip().split(' | ')
                                for x in p_tags if x.text.startswith('Jump to: ')][0]

                data_sets = iter(pd.read_html(source.text, na_values=[''], keep_default_na=False))

                four_digit_pre_tops_codes_list = []
                for x in data_sets:
                    header, four_digit_pre_tops_codes = x, next(data_sets)
                    four_digit_pre_tops_codes.columns = header.columns.to_list()
                    four_digit_pre_tops_codes_list.append(four_digit_pre_tops_codes)

            except Exception as e:
                print("Failed to collect \"{}.\" {}".format(title_name, e))
                region_names, four_digit_pre_tops_codes_list = [], []

            four_digit_pre_tops_codes_data = {
                title_name.replace(' ', '_').replace('-', '_'): dict(zip(region_names, four_digit_pre_tops_codes_list)),
                'Last_updated_date': last_updated_date}
            save_pickle(four_digit_pre_tops_codes_data, path_to_pickle)

        return four_digit_pre_tops_codes_data

    # Collect '1950 system (pre-TOPS) codes'
    def collect_1950_system_codes(self, update=False):
        title_name = list(self.Catalogue.keys())[3]
        path_to_pickle = self.cd_depots(title_name.replace(" ", "-").replace('(', '').replace(')', '') + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            system_1950_codes_data = load_pickle(path_to_pickle)

        else:
            url = self.Catalogue[title_name]

            try:
                last_updated_date = get_last_updated_date(url)
            except Exception as e:
                print("Failed to find the last update date for \"{}.\" {}".format(title_name, e))
                last_updated_date = ''

            try:
                header, system_1950_codes = pd.read_html(url, na_values=[''], keep_default_na=False)
                system_1950_codes.columns = header.columns.to_list()
            except Exception as e:
                print("Failed to collect the data of \"{}.\" {}".format(title_name, e))
                system_1950_codes = None

            system_1950_codes_data = {
                title_name.replace(' ', '_').replace('-', '_').replace('(', '').replace(')', ''): system_1950_codes,
                'Last_updated_date': last_updated_date}
            save_pickle(system_1950_codes_data, path_to_pickle)

        return system_1950_codes_data

    # Collect 'GWR codes' - Great Western Railway depot codes
    def collect_gwr_codes(self, update=False):
        title_name = list(self.Catalogue.keys())[4]
        path_to_pickle = self.cd_depots(title_name.replace(" ", "-") + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            gwr_codes_data = load_pickle(path_to_pickle)

        else:
            url = self.Catalogue[title_name]

            try:
                last_updated_date = get_last_updated_date(url)
            except Exception as e:
                print("Failed to find the last update date for \"{}.\" {}".format(title_name, e))
                last_updated_date = ''

            try:
                header, gwr_codes = pd.read_html(url)
                gwr_codes.columns = header.columns.to_list()
            except Exception as e:
                print("Failed to collect the data of \"{}.\" {}".format(title_name, e))
                gwr_codes = None

            gwr_codes_data = {title_name.replace(' ', '_'): gwr_codes, 'Last_updated_date': last_updated_date}
            save_pickle(gwr_codes_data, path_to_pickle)

        return gwr_codes_data

    # Fetch all the collected depots codes
    def fetch_depot_codes(self, update=False, pickle_it=False, data_dir=None):
        two_char_tops_codes_data = self.collect_two_char_tops_codes(update)
        four_digit_pre_tops_codes_data = self.collect_four_digit_pre_tops_codes(update)
        system_1950_codes_data = self.collect_1950_system_codes(update)
        gwr_codes_data = self.collect_gwr_codes(update)

        depot_codes = {}
        for x in (two_char_tops_codes_data, four_digit_pre_tops_codes_data, system_1950_codes_data, gwr_codes_data):
            old_key = list(x.keys())[0]
            x['Data'] = x.pop(old_key)
            depot_codes.update({old_key: x})

        if pickle_it:
            dat_dir = regulate_input_data_dir(data_dir) if data_dir else self.DataDir
            path_to_pickle = os.path.join(dat_dir, "Depot-codes.pickle")
            save_pickle(depot_codes, path_to_pickle)

        return depot_codes
