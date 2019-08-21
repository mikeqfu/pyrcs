"""

Data source: http://www.railwaycodes.org.uk

Railway viaducts (Reference: http://www.railwaycodes.org.uk/tunnels/tunnels0.shtm)

"""

import os
import re

import bs4
import fuzzywuzzy.process
import pandas as pd
import requests
from pyhelpers.dir import regulate_input_data_dir
from pyhelpers.store import load_pickle

from pyrcs.utils import cd_dat, get_last_updated_date, parse_tr
from pyrcs.utils import save_pickle


class Viaducts:
    def __init__(self, data_dir=None):
        self.HomeURL = 'http://www.railwaycodes.org.uk'
        self.Name = 'Viaducts'
        self.URL = self.HomeURL + '/viaducts/viaducts0.shtm'
        self.Date = get_last_updated_date(self.URL, parsed=True, date_type=False)
        self.DataDir = regulate_input_data_dir(data_dir) if data_dir else cd_dat("Other assets", "Viaducts")

    # Change directory to "dat\\Other assets\\Viaducts\\"
    def cd_viaducts(self, *sub_dir):
        path = self.DataDir
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    # Change directory to "dat\\Other assets\\Viaducts\\dat"
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
    def collect_railway_viaducts(self, page_no, update=False):
        """
        :param page_no: [int] page number; valid values include 1, 2, 3, 4, 5, and 6
        :param update:
        :return:
        """
        page_headers = self.get_page_titles()
        pickle_filename = fuzzywuzzy.process.extractOne(str(page_no), page_headers)[0] + ".pickle"

        path_to_file = self.cd_viaducts("Page 1-6", pickle_filename)

        if os.path.isfile(path_to_file) and not update:
            viaducts_data = load_pickle(path_to_file)
        else:
            url = self.URL.replace('viaducts0', 'viaducts{}'.format(page_no))
            last_updated_date = get_last_updated_date(url)
            source = requests.get(url)

            try:
                parsed_text = bs4.BeautifulSoup(source.text, 'lxml')  # Optional parsers:, 'html5lib', 'html.parser'

                # Column names
                header = [x.text for x in parsed_text.find_all('th')]

                # Table data
                temp_tables = parsed_text.find_all('table', attrs={'width': '1100px'})
                tbl_lst = parse_tr(header, trs=temp_tables[1].find_all('tr'))
                tbl_lst = [[item.replace('\r', ' ').replace('\xa0', '') for item in record] for record in tbl_lst]

                # Create a DataFrame
                viaducts = pd.DataFrame(data=tbl_lst, columns=header)

            except Exception as e:
                print("Failed to collect viaducts data for Page \"{}.\" {}".format(page_no, e))
                viaducts = None

            viaducts_keys = [s + str(page_no) for s in ('Viaducts_', 'Last_updated_date_')]
            viaducts_data = dict(zip(viaducts_keys, [viaducts, last_updated_date]))

            save_pickle(viaducts_data, path_to_file)

        return viaducts_data

    # Fetch all of the collected viaducts data
    def fetch_railway_viaducts(self, update=False, pickle_it=False, data_dir=None):

        data = [self.collect_railway_viaducts(page_no, update) for page_no in range(1, 7)]

        viaducts_data = [dat[k] for dat in data for k, v in dat.items() if re.match('^Viaducts.*', k)]
        last_updated_dates = [dat[k] for dat in data for k, v in dat.items()
                              if re.match('^Last_updated_date.*', k)]

        viaducts = pd.concat(viaducts_data, ignore_index=True, sort=False)
        viaducts = viaducts[list(viaducts_data[0].columns)]
        viaducts_data = {'Viaducts': viaducts, 'Latest_update_date': max(last_updated_dates)}

        if pickle_it:
            dat_dir = regulate_input_data_dir(data_dir) if data_dir else self.DataDir
            path_to_pickle = os.path.join(dat_dir, "Railway-viaducts.pickle")
            save_pickle(viaducts_data, path_to_pickle)

        return viaducts_data
