""" Features """

import os

import bs4
import pandas as pd
import requests
from pyhelpers.dir import regulate_input_data_dir
from pyhelpers.store import load_pickle

from pyrcs.utils import cd_dat, get_last_updated_date
from pyrcs.utils import save_pickle


class Features:
    def __init__(self, data_dir=None):
        self.HomeURL = 'http://www.railwaycodes.org.uk'
        self.Name = 'Infrastructure features'
        self.DataDir = regulate_input_data_dir(data_dir) if data_dir else cd_dat("Other assets", "Features")

    # Change directory to "dat\\Other assets\\Features\\"
    def cd_features(self, *directories):
        path = self.DataDir
        for x in directories:
            path = os.path.join(path, x)
        return path

    # Change directory to "dat\\Other assets\\Features\\dat"
    def cdd_features(self, *sub_dir):
        path = self.cd_features("dat")
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    # Collect Hot axle box detectors (HABDs) and wheel impact load detectors (WILDs)
    def collect_habds_and_wilds(self, update=False):
        path_to_pickle = self.cd_features("HABDs-and-WILDs.pickle")
        if os.path.isfile(path_to_pickle) and not update:
            habds_and_wilds_codes_data = load_pickle(path_to_pickle)
        else:
            url = self.HomeURL + '/misc/habdwild.shtm'
            source = requests.get(url)
            titles = [x.text for x in bs4.BeautifulSoup(source.text, 'lxml').find_all('h3')]
            try:
                titles = [x[x.index('(') + 1:x.index(')')] for x in titles]
            except ValueError:
                pass

            try:
                last_updated_date = get_last_updated_date(url)
            except Exception as e:
                print("Failed to find the last update date for \"{}.\" {}".format(' and '.join(titles), e))
                last_updated_date = ''

            try:
                habds_and_wilds_codes = iter(pd.read_html(url, na_values=[''], keep_default_na=False))

                habds_and_wilds_codes_list = []
                for x in habds_and_wilds_codes:
                    header, data = x, next(habds_and_wilds_codes)
                    data.columns = header.columns.to_list()
                    data.fillna('', inplace=True)
                    habds_and_wilds_codes_list.append(data)

            except Exception as e:
                print("Failed to collect the data of \"{}.\" {}".format(' and '.join(titles), e))
                habds_and_wilds_codes_list = [None] * len(titles)

            habds_and_wilds_codes_data = dict(zip(titles, habds_and_wilds_codes_list))
            habds_and_wilds_codes_data.update({'Last_updated_date': last_updated_date})

            save_pickle(habds_and_wilds_codes_data, path_to_pickle)

        return habds_and_wilds_codes_data

# To be updated.
