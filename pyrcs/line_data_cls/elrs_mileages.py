"""

Data source: http://www.railwaycodes.org.uk

Engineer's Line References (ELRs) (Reference: http://www.railwaycodes.org.uk/elrs/elr0.shtm)

"Mileages are given in the form miles.chains. Figures prefixed with a tilde (~) are approximate, items in parentheses
are not on this route but are given for reference."

"""

import os
import re
import string

import bs4
import pandas as pd
import requests
from pyhelpers.store import load_pickle, save_pickle

from pyrcs.utils import cd_dat
from pyrcs.utils import get_cls_catalogue, get_last_updated_date, regulate_input_data_dir
from pyrcs.utils import is_float, miles_chains_to_mileage, parse_table


class ELRMileages:
    def __init__(self, data_dir=None):
        self.HomeURL = 'http://www.railwaycodes.org.uk'
        self.Name = 'ELRs and mileages'
        self.URL = 'http://www.railwaycodes.org.uk/elrs/elr0.shtm'
        self.Catalogue = get_cls_catalogue(self.URL)
        self.Date = get_last_updated_date(self.URL, parsed=True, date_type=False)
        self.DataDir = regulate_input_data_dir(data_dir) if data_dir else cd_dat("Line data", "ELRs and mileages")

    # Change directory to "dat\\Line data\\ELRs and mileages" and sub-directories
    def cd_em(self, *sub_dir):
        path = self.DataDir
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    # Change directory to "dat\\Line data\\ELRs and mileages\\dat" and sub-directories
    def cdd_em(self, *sub_dir):
        path = self.cd_em("dat")
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    # Scrape Engineer's Line References (ELRs)
    def collect_elr_by_initial(self, initial, update=False):
        """
        :param initial: [str] initial letter of ELR, e.g. 'a', ..., 'z'
        :param update: [bool] whether to re-collect the data
        :return: [dict] {'initial': [pandas.DataFrame], 'Last_updated_date': [str]}
                    [pandas.DataFrame] data of ELRs whose names start with the given 'initial', incl. ELR names,
                    line name, mileages, datum and some notes
                    [str] date of when the data was last updated
        """
        assert initial in string.ascii_letters
        beginning_with = initial.upper()

        path_to_pickle = self.cd_em("A-Z", beginning_with + ".pickle")
        if os.path.isfile(path_to_pickle) and not update:
            elrs = load_pickle(path_to_pickle)
        else:
            # Specify the requested URL
            url = self.Catalogue[beginning_with]
            try:
                source = requests.get(url)  # Request to get connected to the url
                records, header = parse_table(source, parser='lxml')
                # Create a DataFrame of the requested table
                data = pd.DataFrame([[x.replace('=', 'See').strip('\xa0') for x in i] for i in records], columns=header)
                # Return a dictionary containing both the DataFrame and its last updated date
                elrs = {beginning_with: data, 'Last_updated_date': get_last_updated_date(url)}
                save_pickle(elrs, path_to_pickle)
            except Exception as e:  # e.g the requested URL is not available:
                print("Failed to scrape data of ELR beginning with \"{}\". {}.".format(beginning_with, e))
                elrs = {beginning_with: pd.DataFrame(), 'Last_updated_date': ''}
        return elrs

    # Get all ELRs and mileages
    def fetch_elr(self, update=False, pickle_it=False, data_dir=None):
        """
        :param update: [bool] whether to re-collect the data by initial letter
        :param pickle_it: [bool] whether to save the data as a .pickle file
        :param data_dir: [str; None] directory where the data will be stored
        :return [dict] {'ELRs_mileages': [DataFrame], 'Last_updated_date': [str]}
                    [DataFrame] data of (almost all) ELRs beginning with the given 'keyword', including ELR names,
                    line name, mileages, datum and some notes
                    [str] date of when the data was last updated
        """
        data = [self.collect_elr_by_initial(x, update) for x in string.ascii_lowercase]
        elrs_data = (item[x] for item, x in zip(data, string.ascii_uppercase))  # Select DataFrames only
        elrs_data_table = pd.concat(elrs_data, axis=0, ignore_index=True, sort=False)

        # Get the latest updated date
        last_updated_dates = (item['Last_updated_date'] for item, _ in zip(data, string.ascii_uppercase))
        last_updated_date = max(d for d in last_updated_dates if d is not None)

        elrs_data = {'ELRs_mileages': elrs_data_table, 'Last_updated_date': last_updated_date}

        if pickle_it:
            dat_dir = regulate_input_data_dir(data_dir) if data_dir else self.DataDir
            path_to_pickle = os.path.join(dat_dir, "ELRs_mileages.pickle")
            save_pickle(elrs_data, path_to_pickle)

        return elrs_data

    # Read (from online) the mileage file for the given ELR
    def collect_mileage_file_by_elr(self, elr, parsed=True, update=False):
        """
        :param elr: [str]
        :param parsed: [bool]
        :param update: [bool]
        :return: [dict]

        Note:
            - In some cases, mileages are unknown hence left blank, e.g. ANI2, Orton Junction with ROB (~3.05)
            - Mileages in parentheses are not on that ELR, but are included for reference,
              e.g. ANL, (8.67) NORTHOLT [London Underground]
            - As with the main ELR list, mileages preceded by a tilde (~) are approximate.

        """
        path_to_pickle = self.cd_em("mileage_files", elr[0].upper(), elr.upper() + ".pickle")
        if os.path.isfile(path_to_pickle) and not update:
            mileage_file = load_pickle(path_to_pickle)
        else:
            # The URL of the mileage file for the ELR
            url = 'http://www.railwaycodes.org.uk/elrs/_mileages/{}/{}.shtm'.format(elr[0].lower(), elr.lower())
            try:
                source = requests.get(url)
                source_text = bs4.BeautifulSoup(source.text, 'lxml')
                #
                line_name, sub_line_name = source_text.find('h3').text, source_text.find('h4')
                if line_name == '"404" error: page not found':
                    return None
                else:
                    line_name = line_name.split('\t')
                if sub_line_name:
                    sub_headers = sub_line_name.text.split('\t')
                    assert sub_headers[0] == elr
                else:
                    sub_headers = ['', '']
                    assert line_name[0] == elr
                line_info = {'ELR': elr, 'Line': line_name[1], 'Sub-Line': sub_headers[1]}
                #
                parsed_content = source_text.find('pre').text.splitlines()
                parsed_content = [x.strip().split('\t') for x in parsed_content if x != '']
                parsed_content = [[''] + x if len(x) == 1 and 'Note that' not in x[0] else x for x in parsed_content]
                #
                note_temp = min(parsed_content, key=len)
                note = note_temp[0] if len(note_temp) == 1 else ''
                if note:
                    parsed_content.remove(note_temp)
                note_dat = {'Note': note}
                #
                mileage_data = pd.DataFrame(parsed_content, columns=['Mileage', 'Node'])

                def identify_multiple_measures(mileage_dat):
                    node = mileage_dat.Node.tolist()
                    if sum(x in node for x in ('Current measure', 'Original measure', 'Former measure')) == 2:
                        if 'Original measure' in node:
                            measures = ['Current measure', 'Original measure']
                        else:
                            measures = ['Current measure', 'Former measure']
                        sep_rows_idx = [node.index(measures[0]), node.index(measures[1])]
                        data = [mileage_data.iloc[sep_rows_idx[0] + 1:sep_rows_idx[1]],
                                mileage_data.iloc[sep_rows_idx[1] + 1:]]
                        checked_mileage_dat = dict(zip(measures, data))
                    else:
                        checked_mileage_dat = mileage_dat
                    return checked_mileage_dat

                mileage_data = identify_multiple_measures(mileage_data)

                def parse_mileage_col(mileage):
                    if all(mileage.map(is_float)):
                        temp_mileage = mileage
                        mileage_note = [''] * len(temp_mileage)
                    else:
                        temp_mileage, mileage_note = [], []
                        for m in mileage:
                            if m == '':
                                temp_mileage.append(m)
                                mileage_note.append('Unknown')
                            elif m.startswith('(') and m.endswith(')'):
                                temp_mileage.append(m[m.find('(') + 1:m.find(')')])
                                mileage_note.append('Not on this route but given for reference')
                            elif m.startswith('≈'):
                                temp_mileage.append(m.strip('≈'))
                                mileage_note.append('Approximate')
                            else:
                                temp_mileage.append(m.strip(' '))
                                mileage_note.append('')
                    miles_chains = temp_mileage.copy()
                    temp_mileage = [miles_chains_to_mileage(m) for m in temp_mileage]
                    parsed_mileage = pd.DataFrame({'Mileage': temp_mileage, 'Mileage_Note': mileage_note,
                                                   'Miles_Chains': miles_chains})
                    return parsed_mileage

                def preprocess_node_x(node_x):
                    # node_x = node_x.replace(' with Freightliner terminal', ' & Freightliner Terminal'). \
                    #     replace(' with curve to', ' with'). \
                    #     replace(' (0.37 long)', '')
                    # pat = re.compile(r'\w+.*( \(\d+\.\d+\))?(/| and \w+)? with ([A-Z]){3}(\d)?( \(\d+\.\d+\))?')
                    pat = re.compile(r'\w+.*( \(\d+\.\d+\))?(/| and \w+)? with ([A-Z]).*(\d)?( \(\d+\.\d+\))?')
                    if re.match(pat, node_x):
                        node_name = [x.group() for x in re.finditer(r'\w+.*(?= with)', node_x)]
                        conn_node = [x.group() for x in re.finditer(r'(?<= with )[^*]+', node_x)]
                    else:
                        node_name, conn_node = [node_x], [None]
                    return node_name + conn_node

                def parse_nodes(prep_nodes):
                    conn_node_lst = []
                    for n in prep_nodes.Connection:
                        if n is not None:
                            if re.match(r'[A-Z]{3}(\d)?( \(\d+.\d+\))? ?/ ?[A-Z]{3}(\d)?( \(\d+.\d+\))?', n):
                                m = [x.strip() for x in n.split('/')]
                            else:
                                m = n.split(' and ')
                            if len(m) > 2:
                                m = [' and '.join(m[:2]), ' and '.join(m[2:])]
                        else:
                            m = [n]
                        conn_node_lst.append(m)
                    #
                    assert isinstance(conn_node_lst, list)
                    for i in [conn_node_lst.index(c) for c in conn_node_lst if len(c) > 1]:
                        temp_lst = [x.replace('later ', '').rstrip(',').split(' and ') for x in conn_node_lst[i]
                                    if isinstance(x, str)]
                        conn_node_lst[i] = [v for lst in temp_lst for v in lst]
                        temp_lst = [x.split(', ') for x in conn_node_lst[i]]
                        conn_node_lst[i] = [v for lst in temp_lst for v in lst]
                    most_conn = max(len(c) for c in conn_node_lst)
                    # conn_node_list = [c + [None] * (most_conn - len(c)) for c in conn_node_list]
                    return pd.DataFrame(conn_node_lst, columns=['Link_{}'.format(n + 1) for n in range(most_conn)])

                def uncouple_elr_mileage(node_x):
                    # e.g. x = 'ECM5 (44.64)' or x = 'DNT'
                    pat1 = re.compile(r'([A-Z]{3}(\d)?$)|(\w+ ?)*$')
                    pat2 = re.compile(r'([A-Z]{3}(\d)?$)|([\w\s&]?)*( \(\d+.\d+\))?$')
                    pat3 = re.compile(r'[A-Z]{3}(\d)?(\s\(\d+.\d+\))?\s\[.*?\]$')
                    if node_x is None:
                        y = ['', '']
                    elif re.match(pat1, node_x):
                        y = [node_x, '']
                    elif re.match(pat2, node_x):
                        y = [z[:-1] if re.match(r'\d+.\d+\)', z) else z.strip() for z in node_x.split('(')]
                    elif re.match(pat3, node_x):
                        y = [re.search(r'[A-Z]{3}(\d)?', node_x).group(0), re.search(r'\d+.\d+', node_x).group(0)]
                    else:
                        y = [node_x, 'Unknown']
                    return y

                def parse_node_col(node):
                    #
                    prep_node = pd.DataFrame((preprocess_node_x(n) for n in node), columns=['Node', 'Connection'])
                    #
                    conn_nodes = parse_nodes(prep_node)
                    #
                    link_cols = [x for x in conn_nodes.columns if re.match(r'^(Link_\d)', x)]
                    link_nodes = conn_nodes[link_cols].applymap(uncouple_elr_mileage)
                    link_elr_mileage = pd.concat([pd.DataFrame(link_nodes[col].values.tolist(),
                                                               columns=[col + '_ELR', col + '_Mile_Chain'])
                                                  for col in link_cols], axis=1)
                    #
                    parsed_node_and_conn = pd.concat([prep_node, conn_nodes, link_elr_mileage], axis=1)
                    return parsed_node_and_conn

                def parse_mileage_data(mileage_dat):
                    mileage, node = mileage_dat.iloc[:, 0], mileage_dat.iloc[:, 1]
                    parsed_mileage, parsed_node_and_conn = parse_mileage_col(mileage), parse_node_col(node)
                    parsed_dat = pd.concat([parsed_mileage, parsed_node_and_conn], axis=1)
                    return parsed_dat

                if parsed:
                    if isinstance(mileage_data, dict) and len(mileage_data) > 1:
                        mileage_data = {h: parse_mileage_data(dat) for h, dat in mileage_data.items()}
                    else:  # isinstance(dat, pd.DataFrame)
                        mileage_data = parse_mileage_data(mileage_data)

                mileage_file = dict(pair for x in [line_info, {elr: mileage_data}, note_dat] for pair in x.items())

                save_pickle(mileage_file, path_to_pickle)

            except Exception as e:
                print("Failed to collect the mileage file for \"{}\". {}.".format(elr, e))
                mileage_file = None

        return mileage_file

    # Get the mileage file for the given ELR (firstly try to load the local data file if available)
    def fetch_mileage_file(self, elr, update=False):
        """
        :param elr: [str]
        :param update: [bool] indicate whether to re-scrape the data from online
        :return: [dict] {elr: [DataFrame] mileage file data,
                        'Line': [str] line name,
                        'Note': [str] additional information/notes, or None}
        """
        path_to_file = self.cd_em("mileage_files", elr[0].upper(), elr + ".pickle")
        if os.path.isfile(path_to_file) and not update:
            mileage_file = load_pickle(path_to_file)
        else:
            mileage_file = self.collect_mileage_file_by_elr(elr, parsed=True, update=update)
        return mileage_file

    # Get to end and start mileages for StartELR and EndELR, respectively, for the connection point
    def get_conn_end_start_mileages(self, start_elr, end_elr, update=False):
        """
        :param start_elr: [str] e.g. start_elr = 'ECM5'
        :param end_elr: [str] e.g. end_elr = 'KBF'
        :param update: [bool]
        :return: [iterable]
        """
        start_mileage_file, end_mileage_file = \
            self.fetch_mileage_file(start_elr, update), self.fetch_mileage_file(end_elr, update)
        start_mileage_data, end_mileage_data = start_mileage_file[start_elr], end_mileage_file[end_elr]

        def justify_mileage_data(mileage_data):
            if isinstance(mileage_data, dict):
                for key in mileage_data.keys():
                    if re.match('^(Usual)|^(New)|^(Current)', key):
                        mileage_data = mileage_data[key]
            mileage_data.dropna(subset=['Connection'], inplace=True)

        justify_mileage_data(start_mileage_data)
        justify_mileage_data(end_mileage_data)

        temp = start_mileage_data.where(start_mileage_data == end_elr).dropna(how='all', axis=1)
        if not temp.empty:
            # Get exact location
            temp = temp.where(temp == end_elr).dropna(how='all')
            idx, elr_col = temp.index[0], temp.columns[0]
            # Mileage of the start ELR
            start_conn_mileage = start_mileage_data.Mileage[idx]
            # Mileage of the end ELR
            mc_col = elr_col.replace('ELR', 'Mile_Chain')
            end_conn_mc = start_mileage_data.loc[idx, mc_col]
            end_conn_mileage = miles_chains_to_mileage(end_conn_mc)

            return start_conn_mileage, end_conn_mileage
