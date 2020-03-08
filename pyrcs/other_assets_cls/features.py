""" Features """

import copy
import os
import re
import unicodedata
import urllib.parse

import bs4
import numpy as np
import pandas as pd
import requests
from pyhelpers.dir import regulate_input_data_dir
from pyhelpers.ops import confirmed
from pyhelpers.store import load_pickle

from pyrcs.utils import cd_dat, get_last_updated_date
from pyrcs.utils import save_pickle


# Decode vulgar fraction
def decode_vulgar_fraction(string):
    for s in string:
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


# Parse 'VULGAR FRACTION'
def parse_vulgar_fraction_in_length(x):
    if x == '':
        yd = np.nan
    elif re.match(r'\d+yd', x):  # e.g. '620yd'
        yd = int(re.search(r'\d+(?=yd)', x).group(0))
    elif re.match(r'\d+&frac\d+;yd', x):  # e.g. '506&frac23;yd'
        yd, frac = re.search(r'([0-9]+)&frac([0-9]+)(?=;yd)', x).groups()
        yd = int(yd) + int(frac[0]) / int(frac[1])
    else:  # e.g. '557½yd'
        yd = decode_vulgar_fraction(x)
    return yd


class Features:
    def __init__(self, data_dir=None):
        self.HomeURL = 'http://www.railwaycodes.org.uk'
        self.Name = 'Infrastructure features'
        self.DataDir = regulate_input_data_dir(data_dir) if data_dir else cd_dat("other-assets", "features")
        self.CurrentDataDir = copy.copy(self.DataDir)

    # Change directory to "dat\\other-assets\\features\\"
    def cd_features(self, *directories):
        path = self.DataDir
        for x in directories:
            path = os.path.join(path, x)
        return path

    # Change directory to "dat\\other-assets\\features\\dat"
    def cdd_features(self, *sub_dir):
        path = self.cd_features("dat")
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    # Collect 'hot axle box detectors (HABDs)' and 'wheel impact load detectors (WILDs)'
    def collect_habds_and_wilds(self, confirmation_required=True, verbose=False):

        if confirmed("To collect codes for HABDs and WILDs?", confirmation_required=confirmation_required):

            url = self.HomeURL + '/misc/habdwild.shtm'
            source = requests.get(url)
            titles = [x.text for x in bs4.BeautifulSoup(source.text, 'lxml').find_all('h3')]

            try:
                titles = [x[x.index('(') + 1:x.index(')')] for x in titles]
            except ValueError:
                pass

            try:
                habds_and_wilds_codes = iter(pd.read_html(url, na_values=[''], keep_default_na=False))

                habds_and_wilds_codes_list = []
                for x in habds_and_wilds_codes:
                    header, data = x, next(habds_and_wilds_codes)
                    data.columns = header.columns.to_list()
                    data.fillna('', inplace=True)
                    habds_and_wilds_codes_list.append(data)

                habds_and_wilds_codes_data = dict(zip(titles, habds_and_wilds_codes_list))

                last_updated_date = get_last_updated_date(url)
                habds_and_wilds_codes_data.update({'Last_updated_date': last_updated_date})

                path_to_pickle = self.cd_features("habds-and-wilds.pickle")
                save_pickle(habds_and_wilds_codes_data, path_to_pickle, verbose)

            except Exception as e:
                print("Failed to collect the data of \"{}\". {}".format(' and '.join(titles), e))
                habds_and_wilds_codes_data = None

            return habds_and_wilds_codes_data

    # Fetch HABDs and WILDs
    def fetch_habds_and_wilds(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        pickle_filename = "habds-and-wilds.pickle"
        path_to_pickle = self.cd_features(pickle_filename)

        if os.path.isfile(path_to_pickle) and not update:
            habds_and_wilds_codes_data = load_pickle(path_to_pickle)

        else:
            habds_and_wilds_codes_data = self.collect_habds_and_wilds(
                confirmation_required=False, verbose=False if data_dir or not verbose else True)

            if habds_and_wilds_codes_data:
                if pickle_it and data_dir:
                    self.CurrentDataDir = regulate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, pickle_filename)
                    save_pickle(habds_and_wilds_codes_data, path_to_pickle, verbose=True)
            else:
                print("No data of \"HABDs or WILDs\" has been collected.")

        return habds_and_wilds_codes_data

    # Collect 'Water troughs'
    def collect_water_troughs(self, confirmation_required=True, verbose=False):
        title_name = 'Water trough'

        if confirmed("To collect codes for \"{}\"?".format(title_name.lower()),
                     confirmation_required=confirmation_required):

            url = urllib.parse.urljoin(self.HomeURL, '/misc/troughs.shtm')

            try:
                header, water_troughs = pd.read_html(url)
                water_troughs.columns = header.columns.to_list()
                water_troughs.fillna('', inplace=True)
                water_troughs.Length = water_troughs.Length.map(parse_vulgar_fraction_in_length)
                water_troughs.rename(columns={'Length': 'Length_yard'}, inplace=True)

                last_updated_date = get_last_updated_date(url)
                water_troughs_data = {title_name.replace(' ', '_'): water_troughs,
                                      'Last_updated_date': last_updated_date}

                path_to_pickle = self.cd_features(title_name.lower().replace(" ", "-") + ".pickle")
                save_pickle(water_troughs_data, path_to_pickle, verbose)

            except Exception as e:
                print("Failed to collect the data of \"{}\". {}".format(title_name.lower(), e))
                water_troughs_data = None

            return water_troughs_data

    # Fetch 'Water troughs'
    def fetch_water_troughs(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        title_name = 'Water trough'
        path_to_pickle = self.cd_features(title_name.lower().replace(" ", "-") + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            water_troughs_data = load_pickle(path_to_pickle)

        else:
            water_troughs_data = self.collect_water_troughs(
                confirmation_required=False, verbose=False if data_dir or not verbose else True)

            if water_troughs_data:
                if pickle_it and data_dir:
                    self.CurrentDataDir = regulate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, os.path.basename(path_to_pickle))
                    save_pickle(water_troughs_data, path_to_pickle, verbose=True)
            else:
                print("No data of \"{}\" has been collected.".format(title_name.lower()))

        return water_troughs_data

    # Collect 'Telegraph code words'
    def collect_telegraph_codes(self, confirmation_required=True, verbose=False):
        title_name = 'Telegraph code words'

        if confirmed("To collect codes for \"{}\"?".format(title_name.lower()),
                     confirmation_required=confirmation_required):

            url = urllib.parse.urljoin(self.HomeURL, '/misc/telegraph.shtm')

            try:
                source = requests.get(url)
                #
                sub_titles = [x.text for x in bs4.BeautifulSoup(source.text, 'lxml').find_all('h3')]
                #
                data_sets = iter(pd.read_html(source.text))
                telegraph_codes_list = []
                for x in data_sets:
                    header, telegraph_codes = x, next(data_sets)
                    telegraph_codes.columns = header.columns.to_list()
                    telegraph_codes_list.append(telegraph_codes)

                telegraph_codes_data = dict(zip(sub_titles, telegraph_codes_list))

                last_updated_date = get_last_updated_date(url)
                telegraph_codes_data.update({'Last_updated_date': last_updated_date})

                path_to_pickle = self.cd_features(title_name.lower().replace(" ", "-") + ".pickle")
                save_pickle(telegraph_codes_data, path_to_pickle, verbose)

            except Exception as e:
                print("Failed to collect the data of \"{}.\" {}".format(title_name.lower(), e))
                telegraph_codes_data = None

            return telegraph_codes_data

    # Fetch 'Telegraph code words'
    def fetch_telegraph_codes(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        title_name = 'Telegraph code words'
        path_to_pickle = self.cd_features(title_name.lower().replace(" ", "-") + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            telegraph_codes_data = load_pickle(path_to_pickle)

        else:
            telegraph_codes_data = self.collect_telegraph_codes(
                confirmation_required=False, verbose=False if data_dir or not verbose else True)

            if telegraph_codes_data:
                if pickle_it and data_dir:
                    self.CurrentDataDir = regulate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, os.path.basename(path_to_pickle))
                    save_pickle(telegraph_codes_data, path_to_pickle, verbose=True)
            else:
                print("No data of \"{}\" has been collected.".format(title_name.lower()))

        return telegraph_codes_data

    # Collect 'Buzzer codes'
    def collect_buzzer_codes(self, confirmation_required=True, verbose=False):
        title_name = 'Buzzer codes'

        if confirmed("To collect codes for \"{}\"?".format(title_name.lower()),
                     confirmation_required=confirmation_required):

            url = urllib.parse.urljoin(self.HomeURL, '/misc/buzzer.shtm')

            try:
                header, buzzer_codes = pd.read_html(url)
                buzzer_codes.columns = header.columns.to_list()
                buzzer_codes.fillna('', inplace=True)

                last_updated_date = get_last_updated_date(url)

                buzzer_codes_data = {'Codes': buzzer_codes, 'Last_updated_data': last_updated_date}

                path_to_pickle = self.cd_features(title_name.lower().replace(" ", "-") + ".pickle")
                save_pickle(buzzer_codes_data, path_to_pickle, verbose)

            except Exception as e:
                print("Failed to collect the data of \"{}\". {}".format(title_name.lower(), e))
                buzzer_codes_data = None

            return buzzer_codes_data

    # Fetch 'Buzzer codes'
    def fetch_buzzer_codes(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        title_name = 'Buzzer codes'
        path_to_pickle = self.cd_features(title_name.lower().replace(" ", "-") + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            buzzer_codes_data = load_pickle(path_to_pickle)

        else:
            buzzer_codes_data = self.collect_buzzer_codes(
                confirmation_required=False, verbose=False if data_dir or not verbose else True)

            if buzzer_codes_data:
                if pickle_it and data_dir:
                    self.CurrentDataDir = regulate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, os.path.basename(path_to_pickle))
                    save_pickle(buzzer_codes_data, path_to_pickle, verbose=True)
            else:
                print("No data of \"{}\" has been collected.".format(title_name.lower()))

        return buzzer_codes_data
