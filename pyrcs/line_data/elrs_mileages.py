""" Collecting Engineer's Line References (ELRs) codes.

Data source: http://www.railwaycodes.org.uk/elrs/elr0.shtm
"""

import copy
import itertools
import os
import re
import string

import bs4
import measurement.measures
import numpy as np
import pandas as pd
import requests
from pyhelpers.dir import regulate_input_data_dir
from pyhelpers.ops import confirmed
from pyhelpers.store import load_pickle, save_pickle

from pyrcs.utils import cd_dat, fake_requests_headers, homepage_url
from pyrcs.utils import get_catalogue, get_last_updated_date, is_str_float, parse_table
from pyrcs.utils import mile_chain_to_nr_mileage, nr_mileage_to_mile_chain, yards_to_nr_mileage


class ELRMileages:
    """
    A class for collecting Engineer's Line References (ELRs) codes.

    :param data_dir: name of data directory, defaults to ``None``
    :type data_dir: str, None

    **Example**::

        from pyrcs.line_data import ELRMileages

        em = ELRMileages()

        print(em.Name)
        # Engineer's Line References (ELRs)

        print(em.SourceURL)
        # http://www.railwaycodes.org.uk/elrs/elr0.shtm
    """

    def __init__(self, data_dir=None):
        """
        Constructor method.
        """
        self.Name = "ELRs and mileages"
        self.HomeURL = homepage_url()
        self.SourceURL = self.HomeURL + '/elrs/elr0.shtm'
        self.Catalogue = get_catalogue(self.SourceURL, confirmation_required=False)
        self.Date = get_last_updated_date(self.SourceURL, parsed=True, as_date_type=False)
        self.Key = 'ELRs'  # key to ELRs and mileages
        self.LUDKey = 'Last updated date'  # key to last updated date
        if data_dir:
            self.DataDir = regulate_input_data_dir(data_dir)
        else:
            self.DataDir = cd_dat("line-data", self.Name.lower().replace(" ", "-"))
        self.CurrentDataDir = copy.copy(self.DataDir)

    def cdd_em(self, *sub_dir):
        """
        Change directory to "dat\\line-data\\elrs-and-mileages" and sub-directories (and/or a file)

        :param sub_dir: sub-directory or sub-directories (and/or a file)
        :type sub_dir: str
        :return: path to the backup data directory for ``ELRMileages``
        :rtype: str

        :meta private:
        """

        path = self.DataDir
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    @staticmethod
    def identify_multiple_measures(mileage_data):
        """
        Identify the scraped data of mileage file if it has multiple measures and, if so, preprocess it.

        :param mileage_data: scraped raw mileage file from source web page
        :type: pandas.DataFrame
        """

        test_temp = mileage_data[~mileage_data.Mileage.astype(bool)]
        if not test_temp.empty:
            test_temp_node, sep_rows_idx = test_temp.Node.tolist(), test_temp.index[-1]
            if '1949 measure' in test_temp_node:
                mileage_data.Node = mileage_data.Node.str.replace('1949 measure', 'Current measure')
                test_temp_node = [re.sub(r'1949 ', 'Current ', x) for x in test_temp_node]
            if 'Distances in km' in test_temp_node:
                temp_mileage_data = mileage_data[~mileage_data.Node.str.contains('Distances in km')]
                temp_mileages = temp_mileage_data.Mileage.map(
                    lambda x: nr_mileage_to_mile_chain(yards_to_nr_mileage(measurement.measures.Distance(km=x).yd)))
                temp_mileage_data.Mileage = temp_mileages.tolist()
                checked_mileage_data = temp_mileage_data
            elif 'One measure' in test_temp_node:
                sep_rows_idx = mileage_data[mileage_data.Node.str.contains('Alternative measure')].index[0]
                mileage_data_1, mileage_data_2 = np.split(mileage_data, [sep_rows_idx], axis=0)
                checked_mileage_data = {
                    'One measure': mileage_data_1[~mileage_data_1.Node.str.contains('One measure')],
                    'Alternative measure': mileage_data_2[~mileage_data_2.Node.str.contains('Alternative measure')]}
            elif 'This line has two \'legs\':' in test_temp_node:
                temp_mileage_data = mileage_data.iloc[1:].drop_duplicates()
                temp_mileage_data.index = range(len(temp_mileage_data))
                checked_mileage_data = temp_mileage_data
            else:
                test_temp_text = [' '.join(x) for x in itertools.product(
                    *(('Current', 'Later', 'One', 'Original', 'Former', 'Alternative', 'Usual', 'Earlier'),
                      ('measure', 'route')))]
                alt_sep_rows_idx = [x in test_temp_node for x in test_temp_text]
                num_of_measures = sum(alt_sep_rows_idx)
                if num_of_measures == 1:  #
                    mileage_data_1, mileage_data_2 = np.split(mileage_data, [sep_rows_idx], axis=0)
                    if re.match(r'(Original)|(Former)|(Alternative)|(Usual)', test_temp_node[0]):
                        measure_ = re.sub(r'(Original)|(Former)|(Alternative)|(Usual)', r'Current',
                                          test_temp_node[0])
                    else:
                        measure_ = re.sub(r'(Current)|(Later)|(One)', r'Previous', test_temp_node[0])
                    checked_mileage_data = {measure_: mileage_data_1.loc[0:sep_rows_idx, :],
                                            test_temp_node[0]: mileage_data_2.loc[sep_rows_idx + 1:, :]}
                elif num_of_measures == 2:  # e.g. elr='BTJ'
                    sep_rows_idx_items = [test_temp_text[x] for x in np.where(alt_sep_rows_idx)[0]]
                    sep_rows_idx = mileage_data[mileage_data.Node.isin(sep_rows_idx_items)].index[-1]
                    mileage_data_1, mileage_data_2 = np.split(mileage_data, [sep_rows_idx], axis=0)
                    sep_rows_idx_items_checked = [
                        mileage_data_1[mileage_data_1.Node.isin(sep_rows_idx_items)].Node.iloc[0],
                        mileage_data_2[mileage_data_2.Node.isin(sep_rows_idx_items)].Node.iloc[0]]
                    mileage_data_1 = mileage_data_1[~mileage_data_1.Node.isin(sep_rows_idx_items)]
                    mileage_data_2 = mileage_data_2[~mileage_data_2.Node.isin(sep_rows_idx_items)]
                    checked_mileage_data = dict(zip(sep_rows_idx_items_checked, [mileage_data_1, mileage_data_2]))
                else:
                    if mileage_data.loc[sep_rows_idx, 'Mileage'] == '':
                        mileage_data.loc[sep_rows_idx, 'Mileage'] = mileage_data.loc[sep_rows_idx - 1, 'Mileage']
                    checked_mileage_data = mileage_data
        else:
            checked_mileage_data = mileage_data
        return checked_mileage_data

    @staticmethod
    def parse_mileage_col(mileage):
        mileage.index = range(len(mileage))
        if any(mileage.str.match('.*km')):
            if all(mileage.str.match('.*km')):
                temp_mileage = mileage.str.replace('km', '').map(
                    lambda x: yards_to_nr_mileage(measurement.measures.Distance(km=x.replace('≈', '')).british_yd))
                miles_chains = temp_mileage.map(lambda x: nr_mileage_to_mile_chain(x))  # Might be wrong!
            else:
                miles_chains = mileage.map(lambda x: re.sub(r'/?\d+\.\d+km/?', '', x))
                temp_mileage = miles_chains.map(lambda x: mile_chain_to_nr_mileage(x))
            mileage_note = [x + ' (Approximate)' if x.startswith('≈') else x for x in list(mileage)]
        else:
            if all(mileage.map(is_str_float)):
                temp_mileage = mileage
                mileage_note = [''] * len(temp_mileage)
            else:
                temp_mileage, mileage_note = [], []
                for m in mileage:
                    if m == '':
                        temp_mileage.append(m)
                        mileage_note.append('Unknown')
                    elif m.startswith('(') and m.endswith(')'):
                        temp_mileage.append(re.search(r'\d+\.\d+', m).group(0))
                        mileage_note.append('Not on this route but given for reference')
                    elif m.startswith('≈') or m.endswith('?'):
                        temp_mileage.append(m.strip('≈').strip('?'))
                        mileage_note.append('Approximate')
                    elif re.match(r'\d+\.\d+/\s?\d+\.\d+', m):
                        m1, m2 = m.split('/')
                        temp_mileage.append(m1)
                        mileage_note.append(m2.strip() + ' (Alternative)')
                    else:
                        temp_mileage.append(m.strip(' ').replace(' ', '.'))
                        mileage_note.append('')
            miles_chains = temp_mileage.copy()
            temp_mileage = [mile_chain_to_nr_mileage(m) for m in temp_mileage]
        parsed_mileage = pd.DataFrame({'Mileage': temp_mileage,
                                       'Mileage_Note': mileage_note,
                                       'Miles_Chains': miles_chains})
        return parsed_mileage

    @staticmethod
    def parse_node_col(node):

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

        prep_node = pd.DataFrame((preprocess_node_x(n) for n in node), columns=['Node', 'Connection'])

        #
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

        conn_nodes = parse_nodes(prep_node)

        #
        def uncouple_elr_mileage(node_x):
            # e.g. x = 'ECM5 (44.64)' or x = 'DNT'
            if node_x is None:
                y = ['', '']
            else:
                # pat0 = re.compile(r'\w+.*(( lines)|( terminal))$')
                pat1 = re.compile(r'([A-Z]{3}(\d)?$)|((\w\s?)*\w$)')
                pat2 = re.compile(r'([A-Z]{3}(\d)?$)|(([\w\s&]?)*(\s\(\d+\.\d+\))?$)')
                pat3 = re.compile(r'[A-Z]{3}(\d)?(\s\(\d+.\d+\))?\s\[.*?\]$')
                pat4 = re.compile(r'[A-Z]{3}(\d)?\s\(\d+\.\d+km\)')
                # if re.match(pat0, node_x):
                #     y = ['', '']
                if re.match(pat1, node_x):
                    y = [node_x, '']
                elif re.match(pat2, node_x):
                    y = [z[:-1] if re.match(r'\d+.\d+\)', z) else z.strip() for z in node_x.split('(')]
                    y[0] = '' if len(y[0]) > 4 else y[0]
                elif re.match(pat3, node_x):
                    try:
                        y = [re.search(r'[A-Z]{3}(\d)?', node_x).group(0), re.search(r'\d+\.\d+', node_x).group(0)]
                    except AttributeError:
                        y = [re.search(r'[A-Z]{3}(\d)?', node_x).group(0), '']
                elif re.match(pat4, node_x):
                    y = [re.search(r'[A-Z]{3}(\d)?', node_x).group(0),
                         nr_mileage_to_mile_chain(yards_to_nr_mileage(
                             measurement.measures.Distance(km=re.search(r'\d+\.\d+', node_x).group(0)).yd))]
                else:
                    y = [node_x, ''] if len(node_x) <= 4 else ['', '']
                y[0] = y[0] if len(y[0]) <= 4 else ''
            return y

        #
        link_cols = [x for x in conn_nodes.columns if re.match(r'^(Link_\d)', x)]
        link_nodes = conn_nodes[link_cols].applymap(lambda x: uncouple_elr_mileage(x))
        link_elr_mileage = pd.concat(
            [pd.DataFrame(link_nodes[col].values.tolist(), columns=[col + '_ELR', col + '_Mile_Chain'])
             for col in link_cols], axis=1, sort=False)
        parsed_node_and_conn = pd.concat([prep_node, conn_nodes, link_elr_mileage], axis=1, sort=False)

        return parsed_node_and_conn

    def parse_mileage_data(self, mileage_data):
        """
        Parse scraped data of mileage file.

        :param mileage_data: preprocessed data of mileage file scraped from source web page
        :type mileage_data: pandas.DataFrame
        :return: parsed data of mileage file
        :rtype: pandas.DataFrame
        """

        mileage, node = mileage_data.iloc[:, 0], mileage_data.iloc[:, 1]
        parsed_mileage, parsed_node_and_conn = self.parse_mileage_col(mileage), self.parse_node_col(node)
        parsed_dat = pd.concat([parsed_mileage, parsed_node_and_conn], axis=1, sort=False)
        return parsed_dat

    def collect_elr_by_initial(self, initial, update=False, verbose=False):
        """
        Collect Engineer's Line References (ELRs) for the given initial letter from source web page.

        :param initial: initial letter of an ELR, e.g. ``'a'``, ``'z'``
        :type initial: str
        :param update: whether to check on update and proceed to update the package data, defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool, int
        :return: data of ELRs whose names start with the given ``initial`` and date of when the data was last updated
        :rtype: dict

        **Example**::

            from pyrcs.line_data import ELRMileages

            em = ELRMileages()

            initial = 'a'
            update  = False
            verbose = True

            elrs_a = em.collect_elr_by_initial(initial, update, verbose)

            print(elrs_a)
            # {'A': <codes>,
            #  'Last updated date': <date>}
        """

        assert initial in string.ascii_letters
        beginning_with = initial.upper()

        path_to_pickle = self.cdd_em("a-z", beginning_with.lower() + ".pickle")
        if os.path.isfile(path_to_pickle) and not update:
            elrs = load_pickle(path_to_pickle, verbose=verbose)

        else:
            url = self.Catalogue[beginning_with]  # Specify the requested URL

            if verbose == 2:
                print("Collecting data of ELRs beginning with \"{}\"".format(beginning_with.upper()), end=" ... ")

            try:
                source = requests.get(url, headers=fake_requests_headers())  # Request to get connected to the url
                records, header = parse_table(source, parser='lxml')
                # Create a DataFrame of the requested table
                data = pd.DataFrame([[x.replace('=', 'See').strip('\xa0') for x in i] for i in records], columns=header)
                # Return a dictionary containing both the DataFrame and its last updated date
                elrs = {beginning_with: data, self.LUDKey: get_last_updated_date(url)}

                print("Done. ") if verbose == 2 else ""

                save_pickle(elrs, path_to_pickle, verbose=verbose)

            except Exception as e:  # e.g the requested URL is not available:
                print("Failed. {}".format(e))
                elrs = {beginning_with: None, self.LUDKey: None}

        return elrs

    def fetch_elr(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch ELRs and mileages from local backup.

        :param update: whether to check on update and proceed to update the package data, defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data with newly collected data, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str, None
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool, int
        :return: data of all available ELRs and date of when the data was last updated
        :rtype: dict

        **Example**::

            from pyrcs.line_data import ELRMileages

            em = ELRMileages()

            update = False
            pickle_it = False
            data_dir = None
            verbose = True

            elrs_data = em.fetch_elr(update, pickle_it, data_dir, verbose)

            print(elrs_data)
            # {'ELRs': <codes>,
            #  'Latest update date': <date>}
        """

        data = [self.collect_elr_by_initial(x, update, verbose=False if data_dir or not verbose else True)
                for x in string.ascii_lowercase]
        elrs_data = (item[x] for item, x in zip(data, string.ascii_uppercase))  # Select DataFrames only
        elrs_data_table = pd.concat(elrs_data, axis=0, ignore_index=True, sort=False)

        # Get the latest updated date
        last_updated_dates = (item[self.LUDKey] for item, _ in zip(data, string.ascii_uppercase))
        latest_update_date = max(d for d in last_updated_dates if d is not None)

        elrs_data = {self.Key: elrs_data_table, self.LUDKey: latest_update_date}

        if pickle_it and data_dir:
            pickle_filename = self.Name.lower().replace(" ", "-") + ".pickle"
            self.CurrentDataDir = regulate_input_data_dir(data_dir)
            path_to_pickle = os.path.join(self.CurrentDataDir, pickle_filename)
            save_pickle(elrs_data, path_to_pickle, verbose=verbose)

        return elrs_data

    def collect_mileage_file_by_elr(self, elr, parsed=True, confirmation_required=True, pickle_it=False, verbose=False):
        """
        Collect mileage file for the given ELR from source web page.

        :param elr: ELR, e.g. 'CJD', 'MLA', 'FED'
        :type elr: str
        :param parsed: whether to parse the scraped mileage data
        :type parsed: bool
        :param confirmation_required: whether to prompt a message for confirmation to proceed, defaults to ``True``
        :type confirmation_required: bool
        :param pickle_it: whether to replace the current package data with newly collected data, defaults to ``False``
        :type pickle_it: bool
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool, int
        :return: mileage file for the given ``elr``
        :rtype: dict

        .. note::
            - In some cases, mileages are unknown hence left blank,
                e.g. ANI2, Orton Junction with ROB (~3.05)
            - Mileages in parentheses are not on that ELR, but are included for reference,
                e.g. ANL, (8.67) NORTHOLT [London Underground]
            - As with the main ELR list, mileages preceded by a tilde (~) are approximate.

        **Example**::

            from pyrcs.line_data import ELRMileages

            em = ELRMileages()

            parsed = True
            confirmation_required = True
            pickle_it = False
            verbose = True

            elr = 'CJD'
            mileage_file = em.collect_mileage_file_by_elr(elr, parsed, confirmation_required, pickle_it,
                                                          verbose)
            # To collect mileage file for "CJD"? [No]|Yes:
            # >? yes

            print(mileage_file)
            # {'ELR': 'CJD',
            #  'Line': 'Challoch Junction to Dumfries Line',
            #  'Sub-Line': '',
            #  'CJD': <codes>,
            #  'Notes': <notes>}
        """

        if confirmed("To collect mileage file of {}?".format(elr.upper()), confirmation_required=confirmation_required):

            if verbose == 2:
                print("Collecting mileage file of {}".format(elr.upper()), end=" ... ")
            try:
                # The URL of the mileage file for the ELR
                url = self.HomeURL + '/elrs/_mileages/{}/{}.shtm'.format(elr[0].lower(), elr.lower())
                source = requests.get(url, headers=fake_requests_headers())
                source_text = bs4.BeautifulSoup(source.text, 'lxml')

                line_name, sub_line_name = source_text.find('h3').text, source_text.find('h4')

                if line_name == '"404" error: page not found':
                    initial = elr[0]
                    elr_dat = self.collect_elr_by_initial(initial, verbose=verbose)[initial]
                    elr_dat = elr_dat[elr_dat.ELR == elr]

                    notes = elr_dat.Notes.values[0]
                    if re.match(r'(Now( part of)? |= |See )[A-Z]{3}(\d)?$', notes):
                        new_elr = re.search(r'(?<= )[A-Z]{3}(\d)?', notes).group(0)
                        mileage_file = self.fetch_mileage_file(elr=new_elr, pickle_it=pickle_it)
                        return mileage_file

                    else:
                        line_name, mileages = elr_dat[['Line name', 'Mileages']].values[0]
                        if re.match(r'(\w ?)+ \((\w+ \w+)+.\)', line_name):
                            line_name_ = re.search(r'(?<=\w \()(\w+ \w+)+.(?=\))', line_name).group(0)
                            try:
                                location_a, _, location_b = re.split(r' (and|&|to) ', line_name_)
                                line_name = re.search(r'(\w+ \w+)+.(?= \((\w ?)+\))', line_name).group(0)
                            except ValueError:
                                location_a, _, location_b = re.split(r' (and|&|to) ', notes)
                                line_name = line_name_
                        elif elr_dat.Mileages.values[0].startswith('0.00') and elr_dat.Datum.values[0] != '':
                            location_a = elr_dat.Datum.values[0]
                            location_b = re.split(r' (and|&|to) ', line_name)[
                                2] if location_a in line_name else line_name
                        else:
                            try:
                                location_a, _, location_b = re.split(r' (and|&|to) ', notes)
                            except (ValueError, TypeError):
                                location_a, _, location_b = re.split(r' (and|&|to) ', line_name)
                            else:
                                location_a, location_b = '', ''
                        location_b_ = re.sub(r' Branch| Curve', '', location_b) \
                            if re.match(r'.*( Branch| Curve)$', location_b) else location_b

                        miles_chains, locations = mileages.split(' - '), [location_a, location_b_]
                        parsed_content = [[m, l] for m, l in zip(miles_chains, locations)]

                else:
                    line_name = line_name.split('\t')[1]
                    parsed_content = [x.strip().split('\t', 1)
                                      for x in source_text.find('pre').text.splitlines() if x != '']
                    parsed_content = [[y.replace('  ', ' ').replace('\t', ' ') for y in x]
                                      for x in parsed_content]
                    parsed_content = [[''] + x if (len(x) == 1) & ('Note that' not in x[0]) else x
                                      for x in parsed_content]

                # assert sub_headers[0] == elr
                sub_headers = sub_line_name.text.split('\t')[1] if sub_line_name else ''

                # Make a dict of line information
                line_info = {'ELR': elr, 'Line': line_name, 'Sub-Line': sub_headers}

                # Search for note
                note_temp = min(parsed_content, key=len)
                notes = note_temp[0] if len(note_temp) == 1 else ''
                if notes:
                    if ' Revised distances are thus:' in notes:
                        parsed_content[parsed_content.index(note_temp)] = ['', 'Current measure']
                        notes = notes.replace(' Revised distances are thus:', '')
                    else:
                        parsed_content.remove(note_temp)

                # Create a table of the mileage data
                mileage_data = pd.DataFrame(parsed_content, columns=['Mileage', 'Node'])

                # Check if there is any missing note
                if mileage_data.iloc[-1].Mileage == '':
                    notes = [notes, mileage_data.iloc[-1].Node] if notes else mileage_data.iloc[-1].Node
                    mileage_data = mileage_data[:-1]

                if len(mileage_data.iloc[-1].Mileage) > 6:
                    notes = [notes, mileage_data.iloc[-1].Mileage] if notes else mileage_data.iloc[-1].Mileage
                    mileage_data = mileage_data[:-1]

                # Make a dict of note
                note_dat = {'Notes': notes}

                # Identify if there are multiple (both current and former) measures in 'mileage_data'
                mileage_data = self.identify_multiple_measures(mileage_data)

                if parsed:
                    if isinstance(mileage_data, dict) and len(mileage_data) > 1:
                        mileage_data = {h: self.parse_mileage_data(dat) for h, dat in mileage_data.items()}
                    else:  # isinstance(dat, pd.DataFrame)
                        mileage_data = self.parse_mileage_data(mileage_data)

                mileage_file = dict(pair for x in [line_info, {elr: mileage_data}, note_dat] for pair in x.items())

                print("Done. ") if verbose == 2 else ""

                if pickle_it:
                    path_to_pickle = self.cdd_em("mileage-files", elr[0].lower(), elr + ".pickle")
                    if os.path.basename(path_to_pickle) == "prn.pickle":
                        path_to_pickle = path_to_pickle.replace("prn.pickle", "prn_x.pickle")
                    save_pickle(mileage_file, path_to_pickle, verbose=verbose)

            except Exception as e:
                print("Failed. {}.".format(e))
                mileage_file = None

            return mileage_file

    def fetch_mileage_file(self, elr, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch mileage file for the given ELR from local backup.

        :param elr: elr: ELR, e.g. 'CJD', 'MLA', 'FED'
        :type elr: str
        :param update: whether to check on update and proceed to update the package data, defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data with newly collected data, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str, None
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool, int
        :return: mileage file (codes), line name and, if any, additional information/notes
        :rtype: dict

        **Example**::

            from pyrcs.line_data import ELRMileages

            em = ELRMileages()

            update = False
            pickle_it = False
            data_dir = None
            verbose = True

            elr = 'MLA'
            mileage_file = em.fetch_mileage_file(elr, update, pickle_it, data_dir, verbose)

            print(mileage_file)
            # {'ELR': 'MLA',
            #  'Line': 'Maryhill Park Junction to Anniesland Line',
            #  'Sub-Line': '',
            #  'MLA': <codes>,
            #  'Notes': <notes>}
        """

        path_to_pickle = self.cdd_em("mileage-files", elr[0].lower(), elr + ".pickle")
        if os.path.basename(path_to_pickle) == "prn.pickle":
            path_to_pickle = path_to_pickle.replace("prn.pickle", "prn_x.pickle")

        if os.path.isfile(path_to_pickle) and not update:
            mileage_file = load_pickle(path_to_pickle, verbose=verbose)

        else:
            verbose_ = False if data_dir or not verbose else True
            mileage_file = self.collect_mileage_file_by_elr(elr, parsed=True, confirmation_required=False,
                                                            pickle_it=pickle_it, verbose=verbose_)

            if mileage_file:
                if pickle_it and data_dir:
                    self.CurrentDataDir = regulate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, os.path.basename(path_to_pickle))
                    save_pickle(mileage_file, path_to_pickle, verbose=verbose)
            else:
                print("No mileage file has been collected for \"{}\".".format(elr.upper()))

        return mileage_file

    @staticmethod
    def search_conn(start_elr, start_em, end_elr, end_em):
        """
        Search for connection between two ELR-and-mileage pairs.

        :param start_elr: start ELR
        :type start_elr: str
        :param start_em: mileage file of the start ELR
        :type start_em: pandas.DataFrame
        :param end_elr: end ELR
        :type end_elr: str
        :param end_em: mileage file of the end ELR
        :type end_em: pandas.DataFrame
        :return: connection, in the form (<end mileage of the start ELR>, <start mileage of the end ELR>)
        :rtype: tuple

        **Example**::

            from pyrcs.line_data import ELRMileages

            em = ELRMileages()

            start_elr = 'AAM'
            start_mileage_file = em.collect_mileage_file_by_elr(start_elr, verbose=True)
            # To collect mileage file for "AAM"? [No]|Yes: >? yes
            # Collecting mileage file for "AAM" ... Done.
            start_em = start_mileage_file[start_elr]

            end_elr = 'ANZ'
            end_mileage_file = em.collect_mileage_file_by_elr(end_elr, verbose=True)
            # To collect mileage file for "ANZ"? [No]|Yes: >? yes
            # Collecting mileage file for "ANZ" ... Done.
            end_em = end_mileage_file[end_elr]

            start_dest_mileage, end_orig_mileage = em.search_conn(start_elr, start_em, end_elr, end_em)
            print(start_dest_mileage)
            # 0.0396
            print(end_orig_mileage)
            # 84.1364
        """

        start_mask = start_em.apply(lambda x: x.str.contains(end_elr, case=False).any(), axis=1)
        start_temp = start_em[start_mask]
        assert isinstance(start_temp, pd.DataFrame)

        if not start_temp.empty:
            # Get exact location
            key_idx = start_temp.index[0]
            mile_chain_col = [x for x in start_temp.columns if re.match(r'.*_Mile_Chain', x)][0]
            # Mileage of the Start ELR
            start_dest_mileage = start_em.loc[key_idx, 'Mileage']
            # Mileage of the End ELR
            end_orig_mile_chain = start_temp.loc[key_idx, mile_chain_col]

            if end_orig_mile_chain and end_orig_mile_chain != 'Unknown':
                end_orig_mileage = mile_chain_to_nr_mileage(end_orig_mile_chain)
            else:  # end_conn_mile_chain == '':
                end_mask = end_em.apply(lambda x: x.str.contains(start_elr, case=False).any(), axis=1)
                end_temp = end_em[end_mask]

                if not end_temp.empty:
                    end_orig_mileage = end_temp.Mileage.iloc[0]
                else:
                    end_orig_mileage = start_dest_mileage

        else:
            start_dest_mileage, end_orig_mileage = '', ''

        return start_dest_mileage, end_orig_mileage

    def get_conn_mileages(self, start_elr, end_elr, update=False, pickle_mileage_file=False, data_dir=None,
                          verbose=False):
        """
        Get to end and start mileages for StartELR and EndELR, respectively, for the connection point

        :param start_elr: start ELR
        :type start_elr: str
        :param end_elr: end ELR
        :type end_elr: str
        :param update: whether to check on update and proceed to update the package data, defaults to ``False``
        :type update: bool
        :param pickle_mileage_file: whether to replace the current mileage file with newly collected data,
            defaults to ``False``
        :type pickle_mileage_file: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str, None
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool, int
        :return: connection ELR and mileages between the given ``start_elr`` and ``end_elr``
        :rtype: tuple

        **Example**::

            from pyrcs.line_data import ELRMileages

            em = ELRMileages()

            update = False
            pickle_mileage_file = False
            data_dir = None
            verbose = True

            start_elr = 'NAY'
            end_elr = 'LTN2'
            start_dest_mileage, conn_elr, conn_orig_mileage, conn_dest_mileage, end_orig_mileage = \
                em.get_conn_mileages(start_elr, end_elr, update, pickle_mileage_file, data_dir, verbose)

            print(start_dest_mileage)
            # 5.1606
            print(conn_elr)
            # NOL
            print(conn_orig_mileage)
            # 5.1606
            print(conn_dest_mileage)
            # 0.0638
            print(end_orig_mileage)
            # 123.1320
        """

        start_file = self.fetch_mileage_file(start_elr, update, pickle_mileage_file, data_dir, verbose=verbose)
        end_file = self.fetch_mileage_file(end_elr, update, pickle_mileage_file, data_dir, verbose=verbose)

        if start_file is not None and end_file is not None:
            start_elr, end_elr = start_file['ELR'], end_file['ELR']
            start_em, end_em = start_file[start_elr], end_file[end_elr]
            key_pat = re.compile(r'(Current\s)|(One\s)|(Later\s)|(Usual\s)')
            if isinstance(start_em, dict):
                start_em = start_em[[k for k in start_em.keys() if re.match(key_pat, k)][0]]
            if isinstance(end_em, dict):
                end_em = end_em[[k for k in end_em.keys() if re.match(key_pat, k)][0]]
            #
            start_dest_mileage, end_orig_mileage = self.search_conn(start_elr, start_em, end_elr, end_em)

            conn_elr, conn_orig_mileage, conn_dest_mileage = '', '', ''

            if not start_dest_mileage and not end_orig_mileage:
                link_cols = [x for x in start_em.columns if re.match(r'Link_\d_ELR.?', x)]
                conn_elrs = start_em[link_cols]

                i = 0
                while i < len(link_cols):
                    link_col = link_cols[i]
                    conn_temp = conn_elrs[conn_elrs.astype(bool)].dropna(how='all')[link_col].dropna()

                    j = 0
                    while j < len(conn_temp):
                        conn_elr = conn_temp.iloc[j]
                        conn_em = self.fetch_mileage_file(conn_elr, update=update)
                        if conn_em is not None:
                            conn_elr = conn_em['ELR']
                            conn_em = conn_em[conn_elr]
                            if isinstance(conn_em, dict):
                                conn_em = conn_em[[k for k in conn_em.keys() if re.match(key_pat, k)][0]]
                            #
                            start_dest_mileage, conn_orig_mileage = \
                                self.search_conn(start_elr, start_em, conn_elr, conn_em)
                            #
                            conn_dest_mileage, end_orig_mileage = \
                                self.search_conn(conn_elr, conn_em, end_elr, end_em)

                            if conn_dest_mileage and end_orig_mileage:
                                if not start_dest_mileage:
                                    start_dest_mileage = start_em[start_em[link_col] == conn_elr].Mileage.values[0]
                                if not conn_orig_mileage:
                                    link_col_conn = \
                                        conn_em.where(conn_em == start_elr).dropna(axis=1, how='all').columns[0]
                                    conn_orig_mileage = conn_em[conn_em[link_col_conn] == start_elr].Mileage.values[0]
                                break
                            else:
                                conn_elr = ''
                                j += 1
                        else:
                            j += 1

                    if conn_elr != '':
                        break
                    else:
                        i += 1

            if conn_orig_mileage and not conn_elr:
                start_dest_mileage, conn_orig_mileage = '', ''

        else:
            start_dest_mileage, conn_elr, conn_orig_mileage, conn_dest_mileage, end_orig_mileage = [''] * 5

        return start_dest_mileage, conn_elr, conn_orig_mileage, conn_dest_mileage, end_orig_mileage
