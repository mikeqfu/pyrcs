""" Signal box prefix codes """

import os
import string

import bs4
import pandas as pd
import requests

from utils import cdd, load_pickle, save_pickle, get_last_updated_date, parse_table, parse_tr


#
def cdd_sig_box(*directories):
    path = cdd("Other assets", "Signal boxes")
    for directory in directories:
        path = os.path.join(path, directory)
    return path


# Scrape signal box prefix codes for the given 'key word' (e.g. a starting letter) ===================================
def scrape_signal_box_prefix_codes(keyword, update=False):
    """
    :param keyword: [str]
    :param update: [bool]
    :return: 
    """
    path_to_file = cdd_sig_box("A-Z", keyword.title() + ".pickle")

    if os.path.isfile(path_to_file) and not update:
        signal_box_prefix_codes = load_pickle(path_to_file)
    else:
        url = 'http://www.railwaycodes.org.uk/signal/signal_boxes{}.shtm'.format(keyword)
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


# Get all of the available signal box prefix codes ===================================================================
def get_signal_box_prefix_codes(update=False):
    """
    :param update: [bool]
    :return: 
    """
    path_to_file = cdd_sig_box("Signal-box-prefix-codes.pickle")
    if os.path.isfile(path_to_file) and not update:
        signal_box_prefix_codes = load_pickle(path_to_file)
    else:
        # Get every data table
        data = [scrape_signal_box_prefix_codes(i, update) for i in string.ascii_lowercase]

        # Select DataFrames only
        signal_boxes_data = (item['Signal_boxes_{}'.format(x)] for item, x in zip(data, string.ascii_uppercase))
        signal_boxes_data_table = pd.concat(signal_boxes_data, axis=0, ignore_index=True)

        # Get the latest updated date
        last_updated_dates = (item['Last_updated_date_{}'.format(x)] for item, x in zip(data, string.ascii_uppercase))
        last_updated_date = max(d for d in last_updated_dates if d is not None)

        # Create a dict to include all information
        signal_box_prefix_codes = {'Signal_boxes': signal_boxes_data_table, 'Latest_updated_date': last_updated_date}

        save_pickle(signal_box_prefix_codes, path_to_file)

    return signal_box_prefix_codes


def scrape_non_national_rail_codes():
    url = 'http://www.railwaycodes.org.uk/signal/signal_boxesX.shtm'
    source = requests.get(url)
    web_page_text = bs4.BeautifulSoup(source.text, 'lxml')
    non_national_rail = [k.text for k in web_page_text.find_all('h3')]

    non_national_rail_codes = {}
    for n in non_national_rail:
        sub_source = web_page_text.find(text=n)

        # Find text descriptions
        desc = sub_source.find_next('p')
        desc_text = desc.text
        while desc.find_next('p').text != '\xa0' and ' | ' not in desc.find_next('p').text:
            desc_text = ' '.join([desc_text, desc.find_next('p').text])
            desc = desc.find_next('p')

        # Get table data
        tbl = sub_source.find_next('table')
        if tbl.find_previous('h3').text == n:
            # header, dat = [th.text for th in tbl.find_all('th')], [td.text for td in tbl.find_all('td')[2:]]
            # data = pd.DataFrame([dat[x:x + len(header)] for x in range(0, len(dat), len(header))], columns=header)
            header = [th.text for th in tbl.find_all('th')]
            dat = parse_tr(header, tbl.find_all('tr')[3:])
            data = pd.DataFrame(dat, columns=header)
        else:
            data = None

        non_national_rail_codes.update({n: {'Codes': data, 'Description': desc_text.replace('\xa0', '')}})

    return non_national_rail_codes


def get_non_national_rail_codes(update=False):
    path_to_file = cdd_sig_box("Non-national-rail-signals.pickle")
    if os.path.isfile(path_to_file) and not update:
        non_national_rail_codes = load_pickle(path_to_file)
    else:
        try:
            non_national_rail_codes = scrape_non_national_rail_codes()
        except Exception as e:
            print("Getting non-national rail signal codes ... failed due to '{}'.".format(e))
            non_national_rail_codes = None

        save_pickle(non_national_rail_codes, path_to_file)

    return non_national_rail_codes
