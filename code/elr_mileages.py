""" Engineer's Line References (ELRs) """

import os
import string

import measurement.measures
import numpy as np
import pandas as pd
import requests

from utils import cdd_rc_dat, save_pickle, load_pickle, get_last_updated_date, parse_table, isfloat


def cdd_elr_mileage(*directories):
    path = cdd_rc_dat("Line data", "ELRs and mileages")
    for directory in directories:
        path = os.path.join(path, directory)
    return path


# Scrape Engineer's Line References (ELRs) ===========================================================================
def scrape_elrs(keyword, update=False):
    """
    :param keyword: [str]
    :param update: [bool] 
    :return: 
    """
    path_to_file = cdd_elr_mileage("A-Z", keyword.title() + ".pickle")
    if os.path.isfile(path_to_file) and not update:
        elrs = load_pickle(path_to_file)
    else:
        # Specify the requested URL
        url = 'http://www.railwaycodes.org.uk/elrs/ELR{}.shtm'.format(keyword.lower())
        last_updated_date = get_last_updated_date(url)
        try:
            source = requests.get(url)  # Request to get connected to the url
            records, header = parse_table(source, parser='lxml')
            # Create a DataFrame of the requested table
            data = pd.DataFrame([[x.replace('=', 'See').strip('\xa0') for x in i] for i in records], columns=header)
        except IndexError:  # If the requested URL is not available:
            data = None

        # Return a dictionary containing both the DataFrame and its last updated date
        elr_keys = [s + keyword.title() for s in ('ELRs_mileages_', 'Last_updated_date_')]
        elrs = dict(zip(elr_keys, [data, last_updated_date]))
        save_pickle(elrs, path_to_file)

    return elrs


# Get all ELRs and mileages ==========================================================================================
def get_elrs(update=False):
    """
    :param update: [bool]
    :return [dict] containing
                [DataFrame] general data of (almost all) ELRs whose names start with the given 'initial', including 
                            ELR names, line name, mileages, datum and some notes
                [str] date of when the data was last updated
    """
    path_to_file = cdd_elr_mileage("ELRs.pickle")
    if os.path.isfile(path_to_file) and not update:
        elrs = load_pickle(path_to_file)
    else:
        data = [scrape_elrs(i, update) for i in string.ascii_lowercase]
        # Select DataFrames only
        elrs_data = (item['ELRs_mileages_{}'.format(x)] for item, x in zip(data, string.ascii_uppercase))
        elrs_data_table = pd.concat(elrs_data, axis=0, ignore_index=True)

        # Get the latest updated date
        last_updated_dates = (item['Last_updated_date_{}'.format(x)] for item, x in zip(data, string.ascii_uppercase))
        last_updated_date = max(d for d in last_updated_dates if d is not None)

        elrs = {'ELRs_mileages': elrs_data_table, 'Last_updated_date': last_updated_date}

        save_pickle(elrs, path_to_file)

    return elrs


# Convert miles to Network Rail mileages =====================================
def miles_chains_to_mileage(miles_chains):
    if not pd.isnull(miles_chains):
        mc = str(miles_chains)
        miles = int(mc.split('.')[0])
        chains = float(mc.split('.')[1])
        yards = measurement.measures.Distance(chain=chains).yd
        miles_chains = '%.4f' % (miles + round(yards / (10 ** 4), 4))
    return miles_chains


def parse_mileage(mileage):
    if mileage.dtype == np.float64:
        temp_mileage = mileage
        mileage_note = [''] * len(temp_mileage)
    else:
        temp_mileage, mileage_note = [], []
        for m in mileage:
            if m.startswith('(') and m.endswith(')'):
                temp_mileage.append(m[m.find('(') + 1:m.find(')')])
                mileage_note.append('Reference')
            elif m.startswith('~'):
                temp_mileage.append(m[1:])
                mileage_note.append('Approximate')
            else:
                if pd.isnull(m):
                    mileage_note.append('Unknown')
                else:
                    mileage_note.append('')
                temp_mileage.append(m)
    temp_mileage = [miles_chains_to_mileage(m) for m in temp_mileage]
    return pd.DataFrame({'Mileage': temp_mileage, 'Mileage_Note': mileage_note})


def parse_node_and_connection(node):
    temp_node = pd.DataFrame([n.split(' with ') for n in node], columns=['Node', 'Connection'])
    conn_node_list = []
    x = 2  # x-th occurrence
    for c in temp_node.Connection:
        if c is not None:
            cnode = c.split(' and ')
            if len(cnode) > 2:
                cnode = [' and '.join(cnode[:x]), ' and '.join(cnode[x:])]
        else:
            cnode = [c]
        conn_node_list.append(cnode)

    if all(len(c) == 1 for c in conn_node_list):
        conn_node = pd.DataFrame([c + [None] for c in conn_node_list], columns=['Connection1', 'Connection2'])
    else:
        conn_node = pd.DataFrame(conn_node_list, columns=['Connection1', 'Connection2'])
    return temp_node.loc[:, ['Node']].join(conn_node)


def parse_mileage_node_and_connection(dat):
    mileage, node = dat.iloc[:, 0], dat.iloc[:, 1]
    parsed_mileage = parse_mileage(mileage)
    parsed_node_and_connection = parse_node_and_connection(node)
    parsed_dat = parsed_mileage.join(parsed_node_and_connection)
    return parsed_dat


def parse_mileage_file(mileage_file, elr):
    dat = mileage_file[elr]
    if isinstance(dat, dict) and len(dat) > 1:
        dat = {h: parse_mileage_node_and_connection(d) for h, d in dat.items()}
    else:  # isinstance(dat, pd.DataFrame)
        dat = parse_mileage_node_and_connection(dat)
    mileage_file[elr] = dat
    return mileage_file


#
def scrape_mileage_file(elr):
    """
    Note:
        - In some cases, mileages are unknown hence left blank, e.g. ANI2, Orton Junction with ROB (~3.05)
        - Mileages in parentheses are not on that ELR, but are included for reference, e.g. ANL, (8.67) NORTHOLT [
        London Underground]
        - As with the main ELR list, mileages preceded by a tilde (~) are approximate.

    """
    try:
        url = 'http://www.railwaycodes.org.uk/elrs'
        # The URL of the mileage file for the ELR
        mileage_file_url = '/'.join([url, '_mileages', elr[0], elr + '.txt'])

        # Request to get connected to the given url
        mileages = pd.read_table(mileage_file_url)

        line = {'Line': mileages.columns[1]}

        check_idx = mileages[elr].map(isfloat)
        to_check = mileages[~check_idx]
        if to_check.empty:
            dat = {elr: mileages[check_idx]}
            note = {'Note': None}
        else:
            if len(to_check) == 1:
                note = {'Note': to_check[elr].iloc[0]}
                dat = {elr: mileages[check_idx]}
                dat[elr].index = range(len(dat[elr]))
            else:
                idx_vals = to_check.index.get_values()
                diff = list(np.diff(idx_vals)) + [len(mileages) - np.diff(idx_vals)[-1]]
                sliced_dat = {mileages[elr][i]: mileages[i + 1:i + d] for i, d in zip(idx_vals, diff)}
                if len(idx_vals) == 2:
                    note = {'Note': None}
                else:
                    note = {'Note': k for k, v in sliced_dat.items() if v.empty}
                    del sliced_dat[note['Note']]
                for _, dat in sliced_dat.items():
                    dat.index = range(len(dat))
                dat = {elr: sliced_dat}

        mileage_file = dict(pair for d in [dat, line, note] for pair in d.items())
        mileage_file = parse_mileage_file(mileage_file, elr)

        path_to_file = cdd_elr_mileage("mileage_files", elr[0].title(), elr + ".pickle")
        save_pickle(mileage_file, path_to_file)

    except Exception as e:
        print("Scraping the mileage file for {} ... failed due to {}.".format(elr, e))
        mileage_file = None

    return mileage_file


def get_mileage_file(elr, update=False):
    path_to_file = cdd_elr_mileage("mileage_files", elr[0].title(), elr + ".pickle")

    if os.path.isfile(path_to_file) and not update:
        mileage_file = load_pickle(path_to_file)
    else:
        mileage_file = scrape_mileage_file(elr)

    return mileage_file
