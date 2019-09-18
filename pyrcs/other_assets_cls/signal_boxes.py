""" Signal box prefix codes """

import copy
import os
import string

import bs4
import pandas as pd
import requests
from pyhelpers.dir import regulate_input_data_dir
from pyhelpers.misc import confirmed
from pyhelpers.store import load_pickle

from pyrcs.utils import cd_dat, get_catalogue, get_last_updated_date, parse_table, parse_tr
from pyrcs.utils import save_pickle


class SignalBoxes:
    def __init__(self, data_dir=None):
        self.HomeURL = 'http://www.railwaycodes.org.uk'
        self.Name = 'Signal box prefix codes'
        self.URL = self.HomeURL + '/signal/signal_boxes0.shtm'
        self.Catalogue = get_catalogue(self.URL)
        self.Date = get_last_updated_date(self.URL, parsed=True, date_type=False)
        self.DataDir = regulate_input_data_dir(data_dir) if data_dir else cd_dat("other-assets", "signal-boxes")
        self.CurrentDataDir = copy.copy(self.DataDir)

    # Change directory to "dat\\other-assets\\signal-boxes\\"
    def cd_sigbox(self, *directories):
        path = self.DataDir
        for x in directories:
            path = os.path.join(path, x)
        return path

    # Change directory to "dat\\other-assets\\signal-boxes\\dat"
    def cdd_sigbox(self, *sub_dir):
        path = self.cd_sigbox("dat")
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    # Collect signal box prefix codes for the given 'keyword' (a starting letter)
    def collect_signal_box_prefix_codes(self, initial, update=False, verbose=False):
        """
        :param initial: [str]
        :param update: [bool]
        :param verbose: [bool]
        :return: [dict; None]
        """
        path_to_pickle = self.cd_sigbox("a-z", initial.lower() + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            signal_box_prefix_codes = load_pickle(path_to_pickle)

        else:
            sig_keys = [s + initial.upper() for s in ('Signal_boxes_', 'Last_updated_date_')]

            if initial.upper() not in list(self.Catalogue.keys()):
                print("No data is available for signal box codes beginning with \"{}\".".format(initial.upper()))
                signal_box_prefix_codes = dict(zip(sig_keys, [pd.DataFrame(), '']))

            else:
                url = self.URL.replace('0', initial.lower())

                try:
                    source = requests.get(url)
                    # Get table data and its column names
                    records, header = parse_table(source, parser='lxml')
                    header = [h.replace('Signal box', 'Signal Box') for h in header]
                    # Create a DataFrame of the requested table
                    signal_boxes_data_table = pd.DataFrame([[x.strip('\xa0') for x in i] for i in records],
                                                           columns=header)

                except IndexError:
                    print("Failed to collect signal box prefix codes beginning with \"{}\".".format(initial.upper()))
                    signal_boxes_data_table = pd.DataFrame()

                try:
                    last_updated_date = get_last_updated_date(url)
                except Exception as e:
                    print("Failed to find the last updated date of the signal boxes codes beginning with \"{}\". "
                          "{}".format(initial.upper(), e))
                    last_updated_date = ''

                signal_box_prefix_codes = dict(zip(sig_keys, [signal_boxes_data_table, last_updated_date]))

            save_pickle(signal_box_prefix_codes, path_to_pickle, verbose)

        return signal_box_prefix_codes

    # Fetch all of the collected signal box prefix codes
    def fetch_signal_box_prefix_codes(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        :param update: [bool]
        :param pickle_it: [bool]
        :param data_dir: [str; None]
        :param verbose: [bool]
        :return: [dict; None]
        """
        # Get every data table
        data = [self.collect_signal_box_prefix_codes(x, update, verbose=False if data_dir or not verbose else True)
                for x in string.ascii_lowercase]

        # Select DataFrames only
        signal_boxes_data = (item['Signal_boxes_{}'.format(x)] for item, x in zip(data, string.ascii_uppercase))
        signal_boxes_data_table = pd.concat(signal_boxes_data, axis=0, ignore_index=True, sort=False)

        # Get the latest updated date
        last_updated_dates = (item['Last_updated_date_{}'.format(x)] for item, x in zip(data, string.ascii_uppercase))
        latest_update_date = max(d for d in last_updated_dates if d != '')

        # Create a dict to include all information
        signal_box_prefix_codes = {'Signal_boxes': signal_boxes_data_table, 'Latest_update_date': latest_update_date}

        if pickle_it and data_dir:
            self.CurrentDataDir = regulate_input_data_dir(data_dir)
            path_to_pickle = os.path.join(self.CurrentDataDir, "signal_box_prefix_codes.pickle")
            save_pickle(signal_box_prefix_codes, path_to_pickle, verbose=True)

        return signal_box_prefix_codes

    # Collect non-national rail codes
    def collect_non_national_rail_codes(self, confirmation_required=True, verbose=False):
        if confirmed("To collect non-national rail signal box prefix codes?",
                     confirmation_required=confirmation_required):
            url = self.HomeURL + '/signal/signal_boxesX.shtm'
            try:
                source = requests.get(url)
                web_page_text = bs4.BeautifulSoup(source.text, 'lxml')
                non_national_rail, non_national_rail_codes = [], {}

                for h in web_page_text.find_all('h3'):
                    non_national_rail_name = h.text  # Get the name of the non-national rail

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

                save_pickle(non_national_rail_codes, self.cd_sigbox("non-national-rail-signals.pickle"), verbose)

            except Exception as e:
                print("Failed to collect non-national rail codes. {}".format(e))
                non_national_rail_codes = None

            return non_national_rail_codes

    # Fetch the collected non-national rail codes
    def fetch_non_national_rail_codes(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        pickle_filename = "non-national-rail-signals.pickle"
        path_to_pickle = self.cd_sigbox(pickle_filename)

        if os.path.isfile(path_to_pickle) and not update:
            non_national_rail_codes = load_pickle(path_to_pickle)

        else:
            non_national_rail_codes = self.collect_non_national_rail_codes(
                confirmation_required=False, verbose=False if data_dir or not verbose else True)

            if non_national_rail_codes:
                if pickle_it and data_dir:
                    self.CurrentDataDir = regulate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, pickle_filename)
                    save_pickle(non_national_rail_codes, path_to_pickle)
            else:
                print("No data of non-national rail codes has been collected.")

        return non_national_rail_codes
