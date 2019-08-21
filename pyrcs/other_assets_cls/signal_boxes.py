""" Signal box prefix codes """

import os
import string

import bs4
import pandas as pd
import requests
from pyhelpers.dir import regulate_input_data_dir
from pyhelpers.store import load_pickle

from pyrcs.utils import cd_dat, get_cls_catalogue, get_last_updated_date, parse_table, parse_tr
from pyrcs.utils import save_pickle


class SignalBoxes:
    def __init__(self, data_dir=None):
        self.HomeURL = 'http://www.railwaycodes.org.uk'
        self.Name = 'Signal box prefix codes'
        self.URL = self.HomeURL + '/signal/signal_boxes0.shtm'
        self.Catalogue = get_cls_catalogue(self.URL)
        self.Date = get_last_updated_date(self.URL, parsed=True, date_type=False)
        self.DataDir = regulate_input_data_dir(data_dir) if data_dir else cd_dat("Other assets", "Signal boxes")

    # Change directory to "dat\\Other assets\\Signal Boxes\\"
    def cd_sigbox(self, *directories):
        path = self.DataDir
        for x in directories:
            path = os.path.join(path, x)
        return path

    # Change directory to "dat\\Other assets\\Signal Boxes\\dat"
    def cdd_sigbox(self, *sub_dir):
        path = self.cd_sigbox("dat")
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    # Collect signal box prefix codes for the given 'keyword' (a starting letter)
    def collect_signal_box_prefix_codes(self, keyword, update=False):
        """
        :param keyword: [str]
        :param update: [bool]
        :return:
        """
        path_to_file = self.cd_sigbox("A-Z", keyword.title() + ".pickle")

        if os.path.isfile(path_to_file) and not update:
            signal_box_prefix_codes = load_pickle(path_to_file)
        else:
            url = self.URL.replace('0', keyword)
            last_updated_date = get_last_updated_date(url)
            source = requests.get(url)
            try:
                # Get table data and its column names
                records, header = parse_table(source, parser='lxml')
                header = [h.replace('Signal box', 'Signal Box') for h in header]
                # Create a DataFrame of the requested table
                data = pd.DataFrame([[x.strip('\xa0') for x in i] for i in records], columns=header)
            except IndexError:
                data = None
                print("No data is available for the keyword '{}'.".format(keyword))

            sig_keys = [s + keyword.title() for s in ('Signal_boxes_', 'Last_updated_date_')]
            signal_box_prefix_codes = dict(zip(sig_keys, [data, last_updated_date]))
            save_pickle(signal_box_prefix_codes, path_to_file)

        return signal_box_prefix_codes

    # Fetch all of the collected signal box prefix codes
    def fetch_signal_box_prefix_codes(self, update=False, pickle_it=False, data_dir=None):
        """
        :param update: [bool]
        :param pickle_it: [bool]
        :param data_dir: [str; None]
        :return:
        """
        # Get every data table
        data = [self.collect_signal_box_prefix_codes(i, update) for i in string.ascii_lowercase]

        # Select DataFrames only
        signal_boxes_data = (item['Signal_boxes_{}'.format(x)] for item, x in zip(data, string.ascii_uppercase))
        signal_boxes_data_table = pd.concat(signal_boxes_data, axis=0, ignore_index=True)

        # Get the latest updated date
        last_updated_dates = (item['Last_updated_date_{}'.format(x)]
                              for item, x in zip(data, string.ascii_uppercase))
        last_updated_date = max(d for d in last_updated_dates if d is not None)

        # Create a dict to include all information
        signal_box_prefix_codes = {'Signal_boxes': signal_boxes_data_table,
                                   'Latest_updated_date': last_updated_date}

        if pickle_it:
            dat_dir = regulate_input_data_dir(data_dir) if data_dir else self.DataDir
            path_to_pickle = os.path.join(dat_dir, "Signal-box-prefix-codes.pickle")
            save_pickle(signal_box_prefix_codes, path_to_pickle)

        return signal_box_prefix_codes

    # Collect non-national rail codes
    @staticmethod
    def collect_non_national_rail_codes():
        url = 'http://www.railwaycodes.org.uk/signal/signal_boxesX.shtm'
        source = requests.get(url)
        web_page_text = bs4.BeautifulSoup(source.text, 'lxml')
        non_national_rail, non_national_rail_codes = [], {}

        for h in web_page_text.find_all('h3'):
            # Get the name of the non-national rail
            non_national_rail_name = h.text

            # Find text descriptions
            desc = h.find_next('p')
            desc_text, more_desc = desc.text.replace('\xa0', ''), desc.find_next('p')
            while more_desc.find_previous('h3') == h:
                desc_text = '\n'.join([desc_text, more_desc.text.replace('\xa0', '')])
                more_desc = more_desc.find_next('p')
                if more_desc is None:
                    break

            # Get table data
            tbl_dat = desc.find_next('table')
            if tbl_dat.find_previous('h3').text == non_national_rail_name:
                header = [th.text for th in tbl_dat.find_all('th')]  # header
                data = pd.DataFrame(parse_tr(header, tbl_dat.find_next('table').find_all('tr')), columns=header)
            else:
                data = None

            # Update data dict
            non_national_rail_codes.update(
                {non_national_rail_name: {'Codes': data, 'Note': desc_text.replace('\xa0', '')}})

        return non_national_rail_codes

    # Fetch the collected non-national rail codes
    def fetch_non_national_rail_codes(self, update=False):
        pickle_filename = "Non-national-rail-signals.pickle"
        path_to_pickle = self.cd_sigbox(pickle_filename)
        if os.path.isfile(path_to_pickle) and not update:
            non_national_rail_codes = load_pickle(path_to_pickle)
        else:
            try:
                non_national_rail_codes = self.collect_non_national_rail_codes()
            except Exception as e:
                print("Getting non-national rail signal codes ... failed due to '{}'.".format(e))
                non_national_rail_codes = None

            save_pickle(non_national_rail_codes, path_to_pickle)

        return non_national_rail_codes
