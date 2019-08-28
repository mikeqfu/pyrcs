"""

Data source: http://www.railwaycodes.org.uk

Railway viaducts (http://www.railwaycodes.org.uk/tunnels/tunnels0.shtm)

"""

import copy
import os
import re

import bs4
import fuzzywuzzy.process
import pandas as pd
import requests
from pyhelpers.dir import regulate_input_data_dir
from pyhelpers.store import load_pickle

from pyrcs.utils import cd_dat, get_catalogue, get_last_updated_date
from pyrcs.utils import save_pickle


class Viaducts:
    def __init__(self, data_dir=None):
        self.HomeURL = 'http://www.railwaycodes.org.uk'
        self.Name = 'Viaducts'
        self.URL = self.HomeURL + '/viaducts/viaducts0.shtm'
        self.Catalogue = get_catalogue(self.URL)
        self.Date = get_last_updated_date(self.URL, parsed=True, date_type=False)
        self.DataDir = regulate_input_data_dir(data_dir) if data_dir else cd_dat("other_assets", "viaducts")
        self.CurrentDataDir = copy.copy(self.DataDir)

    # Change directory to "dat\\other_assets\\viaducts\\" and sub-directories
    def cd_viaducts(self, *sub_dir):
        path = self.DataDir
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    # Change directory to "dat\\other_assets\\viaducts\\dat" and sub-directories
    def cdd_viaducts(self, *sub_dir):
        path = self.cd_viaducts("dat")
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    # Get the titles for each page
    def get_page_titles(self):
        intro_page = requests.get(self.URL)
        pages = [x.text for x in bs4.BeautifulSoup(intro_page.text, 'lxml').find_all('a', text=re.compile('^Page.*'))]
        pages = pages[0:int(len(pages) / 2)]
        return pages

    # Collect viaducts data for a given page number
    def collect_railway_viaducts(self, page_no, update=False, verbose=False):
        """
        :param page_no: [int] page number; valid values include 1, 2, 3, 4, 5, and 6
        :param update: [bool]
        :param verbose: [bool]
        :return: [dict]
        """
        assert page_no in range(1, 7), "Valid \"page_no\" must be one of 1, 2, 3, 4, 5, and 6."
        page_headers = self.get_page_titles()
        filename = fuzzywuzzy.process.extractOne(str(page_no), page_headers)[0]
        pickle_filename = re.sub(r"[()]", "", re.sub(r"[ -]", "_", filename)).lower() + ".pickle"

        path_to_pickle = self.cd_viaducts(pickle_filename)

        if os.path.isfile(path_to_pickle) and not update:
            viaducts_codes = load_pickle(path_to_pickle)

        else:
            url = self.URL.replace('viaducts0', 'viaducts{}'.format(page_no))

            try:
                last_updated_date = get_last_updated_date(url)
            except Exception as e:
                print("Failed to find the last updated date for viaducts codes on \"{}\". {}".format(filename, e))
                last_updated_date = ''

            try:
                header, viaducts_table = pd.read_html(url, na_values=[''], keep_default_na=False)
                viaducts_table.columns = header.columns.to_list()
                viaducts_table.fillna('', inplace=True)
            except Exception as e:
                print("Failed to collect viaducts data for Page \"{}\". {}".format(page_no, e))
                viaducts_table = pd.DataFrame()

            viaducts_codes = {re.search(r'(?<=\()\w.*(?=\))', filename).group(0).replace('-', '_'): viaducts_table}
            viaducts_codes.update({'Last_updated_date': last_updated_date})

            save_pickle(viaducts_codes, path_to_pickle, verbose)

        return viaducts_codes

    # Fetch all of the collected viaducts data
    def fetch_railway_viaducts(self, update=False, pickle_it=False, data_dir=None, verbose=False):

        data_sets = [self.collect_railway_viaducts(page_no, update, verbose=False if data_dir or not verbose else True)
                     for page_no in range(1, 7)]

        viaducts_codes_tables = [dat[k] for dat in data_sets for k, v in dat.items() if k != 'Last_updated_date']
        viaducts_codes = pd.concat(viaducts_codes_tables, axis=0, ignore_index=True, sort=False)

        last_updated_dates = [dat[k] for dat in data_sets for k, v in dat.items() if k == 'Last_updated_date']
        latest_update_date = max(last_updated_dates)

        viaducts_codes = {'Viaducts': viaducts_codes, 'Latest_update_date': latest_update_date}

        if pickle_it and data_dir:
            self.CurrentDataDir = regulate_input_data_dir(data_dir)
            path_to_pickle = os.path.join(self.CurrentDataDir, "railway_viaducts.pickle")
            save_pickle(viaducts_codes, path_to_pickle, verbose=True)

        return viaducts_codes
