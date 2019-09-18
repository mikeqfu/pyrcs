""" Railway tunnel lengths """

import copy
import itertools
import operator
import os
import re

import bs4
import fuzzywuzzy.process
import measurement.measures
import pandas as pd
import requests
from pyhelpers.dir import regulate_input_data_dir
from pyhelpers.store import load_pickle

from pyrcs.utils import cd_dat, get_catalogue, get_last_updated_date, parse_tr
from pyrcs.utils import save_pickle


class Tunnels:
    def __init__(self, data_dir=None):
        self.HomeURL = 'http://www.railwaycodes.org.uk'
        self.Name = 'Tunnels'
        self.URL = self.HomeURL + '/tunnels/tunnels0.shtm'
        self.Catalogue = get_catalogue(self.URL)
        self.Date = get_last_updated_date(self.URL, parsed=True, date_type=False)
        self.DataDir = regulate_input_data_dir(data_dir) if data_dir else cd_dat("other-assets", 'tunnels')
        self.CurrentDataDir = copy.copy(self.DataDir)

    # Change directory to "dat\\other-assets\\tunnels" and sub-directories
    def cd_tunnels(self, *directories):
        path = self.DataDir
        for x in directories:
            path = os.path.join(path, x)
        return path

    # Change directory to "dat\\other-assets\\tunnels\\dat" and sub-directories
    def cdd_tunnels(self, *sub_dir):
        path = self.cd_tunnels("dat")
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    # Find page headers
    def find_page_headers(self):
        intro_page = requests.get(self.URL)
        pages = [x.text for x in bs4.BeautifulSoup(intro_page.text, 'lxml').find_all('a', text=re.compile('^Page.*'))]
        return pages[:int(len(pages) / 2)]

    # Parse data in 'Length' column, i.e. convert miles/yards to metres
    @staticmethod
    def parse_tunnel_length(x):
        """
        :param x:
        :return:

        Examples:
            '' or Unknown
            1m 182y; 0m111y; c0m 150y; 0m 253y without avalanche shelters
            0m 56ch
            formerly 0m236y
            0.325km (0m 356y); 0.060km ['(0m 66y)']
            0m 48yd- (['0m 58yd'])
        """
        if re.match(r'[Uu]nknown', x):
            length = pd.np.nan
            add_info = 'Unknown'
        elif x == '':
            length = pd.np.nan
            add_info = 'Unavailable'
        elif re.match(r'\d+m \d+yd-.*\d+m \d+yd.*', x):
            miles_a, yards_a, miles_b, yards_b = re.findall(r'\d+', x)
            length_a = measurement.measures.Distance(mi=miles_a).m + measurement.measures.Distance(yd=yards_a).m
            length_b = measurement.measures.Distance(mi=miles_b).m + measurement.measures.Distance(yd=yards_b).m
            length = (length_a + length_b) / 2
            add_info = '-'.join([str(round(length_a, 2)), str(round(length_b, 2))]) + ' metres'
        else:
            if re.match(r'(formerly )?c?\d+m ?\d+y?(ch)?.*', x):
                miles, yards = re.findall(r'\d+', x)
                if re.match(r'.*\d+ch$', x):
                    yards = measurement.measures.Distance(chain=yards).yd
                if re.match(r'^c.*', x):
                    add_info = 'Approximate'
                elif re.match(r'\d+y$', x):
                    add_info = re.search(r'(?<=\dy).*$', x).group()
                elif re.match(r'^(formerly).*', x):
                    add_info = 'Formerly'
                else:
                    add_info = None
            elif re.match(r'\d+\.\d+km .*\(\d+m \d+y\).*', x):
                miles, yards = re.findall(r'\d+', re.search(r'(?<=\()\d+.*(?=\))', x).group())
                add_info = re.search(r'.+(?= (\[\')?\()', x).group()
            else:
                print(x)
                miles, yards = 0, 0
                add_info = ''
            length = measurement.measures.Distance(mi=miles).m + measurement.measures.Distance(yd=yards).m
        return length, add_info

    # Collect the data of railway tunnel lengths for a given page number
    def collect_railway_tunnel_lengths(self, page_no, update=False, verbose=False):
        """
        :param page_no: [int] page number; valid values include 1, 2, and 3
        :param update: [bool] indicate whether to re-scrape the tunnel lengths data for the given page_no
        :param verbose: [bool]
        :return [dict] containing:
                    [DataFrame] tunnel lengths data of the given 'page'
                    [str] date of when the data was last updated
        """
        assert page_no in range(1, 4)
        page_headers = self.find_page_headers()
        filename = fuzzywuzzy.process.extractOne(str(page_no), page_headers)[0]
        pickle_filename = re.sub(r"[()]", "", re.sub(r"[ -]", "-", filename)).lower() + ".pickle"

        path_to_pickle = self.cd_tunnels(pickle_filename)

        if os.path.isfile(path_to_pickle) and not update:
            tunnel_lengths_codes = load_pickle(path_to_pickle)

        else:
            url = self.URL.replace('tunnels0', 'tunnels{}'.format(page_no))

            try:
                last_updated_date = get_last_updated_date(url)
            except Exception as e:
                print("Failed to find the last updated date for tunnel lengths data on \"{}\". {}".format(filename, e))
                last_updated_date = ''

            try:
                source = requests.get(url)
                parsed_text = bs4.BeautifulSoup(source.text, 'lxml')  # Optional parsers:, 'html5lib', 'html.parser'

                header = [x.text for x in parsed_text.find_all('th')]  # Column names

                crossed = [re.match(r'^Between.*', x) for x in header]
                if any(crossed):
                    idx = list(itertools.compress(range(len(crossed)), crossed))
                    assert len(idx) == 1
                    header.remove(header[idx[0]])
                    header[idx[0]:idx[0]] = ['Station_O', 'Station_D']

                # Table data
                temp_tables = parsed_text.find_all('table', attrs={'width': '1100px'})
                tbl_lst = parse_tr(header, trs=temp_tables[1].find_all('tr'))
                tbl_lst = [[item.replace('\r', ' ').replace('\xa0', '') for item in record] for record in tbl_lst]

                # Create a DataFrame
                tunnel_lengths_table = pd.DataFrame(data=tbl_lst, columns=header)
                tunnel_lengths_table[['Length_m', 'Length_note']] = \
                    tunnel_lengths_table.Length.map(self.parse_tunnel_length).apply(pd.Series)

            except Exception as e:
                print("Failed to collect tunnel lengths data on \"{}\". {}".format(filename, e))
                tunnel_lengths_table = pd.DataFrame()

            code_key = re.search(r'(?<=\()\w.*(?=\))', filename).group(0).replace('-', '_')
            tunnel_lengths_codes = {code_key: tunnel_lengths_table, 'Last_updated_date': last_updated_date}

            save_pickle(tunnel_lengths_codes, path_to_pickle, verbose)

        return tunnel_lengths_codes

    # Collect the data of minor lines and other odds / ends
    def collect_page4_others(self, update=False, verbose=False):
        """
        Page 4 (others) contains more than one table on the web page
        """
        page_headers = self.find_page_headers()
        filename = fuzzywuzzy.process.extractOne('others', page_headers)[0]
        pickle_filename = re.sub(r"[()]", "", re.sub(r"[ -]", "-", filename)).lower() + ".pickle"
        path_to_pickle = self.cd_tunnels(pickle_filename)

        if os.path.isfile(path_to_pickle) and not update:
            tunnel_lengths_data = load_pickle(path_to_pickle)

        else:
            url = self.HomeURL + '/tunnels/tunnels4.shtm'

            try:
                last_updated_date = get_last_updated_date(url)
            except Exception as e:
                print("Failed to find the last updated date for tunnel lengths data on \"{}\". {}".format(filename, e))
                last_updated_date = ''

            try:
                source = requests.get(url)
                parsed_text = bs4.BeautifulSoup(source.text, 'lxml')  # Optional parsers:, 'html5lib', 'html.parser'
                headers = []
                temp_header = parsed_text.find('table')
                while temp_header.find_next('th'):
                    header = [x.text for x in temp_header.find_all('th')]
                    if len(header) > 0:
                        crossed = [re.match('^Between.*', x) for x in header]
                        if any(crossed):
                            idx = list(itertools.compress(range(len(crossed)), crossed))
                            assert len(idx) == 1
                            header.remove(header[idx[0]])
                            header[idx[0]:idx[0]] = ['Station_O', 'Station_D']
                        headers.append(header)
                    temp_header = temp_header.find_next('table')

                tbl_lst = parsed_text.find_all('table', attrs={'width': '1100px'})
                tbl_lst = operator.itemgetter(1, 3)(tbl_lst)
                tbl_lst = [parse_tr(header, x.find_all('tr')) for header, x in zip(headers, tbl_lst)]
                tbl_lst = [[[item.replace('\xa0', '') for item in record] for record in tbl] for tbl in tbl_lst]

                tunnel_lengths = [pd.DataFrame(tbl, columns=header) for tbl, header in zip(tbl_lst, headers)]
                for i in range(len(tunnel_lengths)):
                    tunnel_lengths[i][['Length_m', 'Length_note']] = \
                        tunnel_lengths[i].Length.map(self.parse_tunnel_length).apply(pd.Series)

                other_types = [x.text for x in parsed_text.find_all('h3')]

            except Exception as e:
                print("Failed to collect tunnel lengths data on \"{}\". {}".format(filename, e))
                other_types, tunnel_lengths = ['None'], pd.DataFrame()

            tunnel_lengths_data = dict(zip(other_types + ['Last_updated_date'], tunnel_lengths + [last_updated_date]))

            save_pickle(tunnel_lengths_data, path_to_pickle, verbose)

        return tunnel_lengths_data

    # Fetch all the collected data of railway tunnel lengths
    def fetch_railway_tunnel_lengths(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        :param update: [bool]
        :param pickle_it: [bool]
        :param data_dir: [str; None]
        :param verbose: [bool]
        :return [dict] containing:
                    [DataFrame] railway tunnel lengths data, including the name,
                                length, owner and relative location
                    [str] date of when the data was last updated
        """
        data_sets = [self.collect_railway_tunnel_lengths(
            page_no, update, verbose=False if data_dir or not verbose else True) for page_no in range(1, 4)]
        other_data_set = self.collect_page4_others(update, verbose=False if data_dir or not verbose else True)

        tunnel_lengths_tables = [d[k] for d in data_sets for k, v in d.items() if k != 'Last_updated_date']
        others_tables = [v for k, v in other_data_set.items() if k != 'Last_updated_date']
        tunnel_lengths_tables += others_tables
        tunnel_lengths_codes = pd.concat(tunnel_lengths_tables, axis=0, ignore_index=True, sort=False)

        last_updated_dates = [d[k] for d in data_sets for k, v in d.items() if k == 'Last_updated_date']
        latest_update_date = max(last_updated_dates)

        tunnel_lengths = {'Tunnels': tunnel_lengths_codes, 'Latest_update_date': latest_update_date}

        if pickle_it and data_dir:
            self.CurrentDataDir = regulate_input_data_dir(data_dir)
            path_to_pickle = os.path.join(self.CurrentDataDir, "tunnel_lengths.pickle")
            save_pickle(tunnel_lengths, path_to_pickle, verbose=True)

        return tunnel_lengths
