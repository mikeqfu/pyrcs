"""
Collect `Engineer's Line References (ELRs)
<http://www.railwaycodes.org.uk/elrs/elr0.shtm>`_ codes.
"""

import copy
import itertools
import os
import re
import string
import urllib.parse

import bs4
import measurement.measures
import numpy as np
import pandas as pd
import requests
from pyhelpers.dir import cd, validate_input_data_dir
from pyhelpers.ops import confirmed, fake_requests_headers
from pyhelpers.store import load_pickle, save_pickle
from pyhelpers.text import remove_punctuation

from pyrcs.utils import cd_dat, homepage_url, get_catalogue, get_last_updated_date, \
    is_str_float, parse_table, mile_chain_to_nr_mileage, nr_mileage_to_mile_chain, \
    yards_to_nr_mileage, print_conn_err, is_internet_connected, print_connection_error


class ELRMileages:
    """
    A class for collecting Engineer's Line References (ELRs) codes.

    :param data_dir: name of data directory, defaults to ``None``
    :type data_dir: str or None
    :param update: whether to check on update and proceed to update the package data, 
        defaults to ``False``
    :type update: bool
    :param verbose: whether to print relevant information in console as the function runs,
        defaults to ``True``
    :type verbose: bool or int

    :ivar str Name: name of the data
    :ivar str Key: key of the dict-type data
    :ivar str HomeURL: URL of the main homepage
    :ivar str SourceURL: URL of the data web page
    :ivar str LUDKey: key of the last updated date
    :ivar str LUD: last updated date
    :ivar dict Catalogue: catalogue of the data
    :ivar str DataDir: path to the data directory
    :ivar str CurrentDataDir: path to the current data directory

    **Example**::

        >>> from pyrcs.line_data import ELRMileages

        >>> em = ELRMileages()

        >>> print(em.Name)
        ELRs and mileages

        >>> print(em.SourceURL)
        http://www.railwaycodes.org.uk/elrs/elr0.shtm
    """

    def __init__(self, data_dir=None, update=False, verbose=True):
        """
        Constructor method.
        """
        if not is_internet_connected():
            print_connection_error(verbose=verbose)

        self.Name = "ELRs and mileages"
        self.Key = 'ELRs'  # key to ELRs and mileages

        self.HomeURL = homepage_url()
        self.SourceURL = urllib.parse.urljoin(self.HomeURL, '/elrs/elr0.shtm')

        self.LUDKey = 'Last updated date'  # key to last updated date
        self.LUD = get_last_updated_date(url=self.SourceURL, parsed=True, as_date_type=False)

        self.Catalogue = get_catalogue(page_url=self.SourceURL, update=update,
                                       confirmation_required=False)

        if data_dir:
            self.DataDir = validate_input_data_dir(data_dir)
        else:
            self.DataDir = cd_dat("line-data", self.Name.lower().replace(" ", "-"))
        self.CurrentDataDir = copy.copy(self.DataDir)

    def _cdd_em(self, *sub_dir, mkdir=False, **kwargs):
        """
        Change directory to package data directory and sub-directories (and/or a file).

        The directory for this module: ``"\\dat\\line-data\\elrs-and-mileages"``.

        :param sub_dir: sub-directory or sub-directories (and/or a file)
        :type sub_dir: str
        :param mkdir: whether to create a directory, defaults to ``False``
        :type mkdir: bool
        :param kwargs: optional parameters of `os.makedirs`_, e.g. ``mode=0o777``
        :return: path to the backup data directory for ``ELRMileages``
        :rtype: str

        .. _`os.makedirs`: https://docs.python.org/3/library/os.html#os.makedirs

        :meta private:
        """

        path = cd(self.DataDir, *sub_dir, mkdir=mkdir, **kwargs)

        return path

    @staticmethod
    def _parse_multi_measures(mileage_data):
        """
        Process data of mileage file with multiple measures.

        :param mileage_data: scraped raw mileage file from source web page
        :type: pandas.DataFrame

        :meta private:
        """

        test_temp = mileage_data[~mileage_data.Mileage.astype(bool)]
        if not test_temp.empty:
            test_temp_node, sep_rows_idx = test_temp.Node.tolist(), test_temp.index[-1]

            if '1949 measure' in test_temp_node:
                mileage_data.Node = \
                    mileage_data.Node.str.replace('1949 measure', 'Current measure')
                test_temp_node = [re.sub(r'1949 ', 'Current ', x) for x in test_temp_node]

            if 'Distances in km' in test_temp_node:
                temp_mileage_data = mileage_data[~mileage_data.Node.str.contains('Distances in km')]
                temp_mileages = temp_mileage_data.Mileage.map(
                    lambda x: nr_mileage_to_mile_chain(
                        yards_to_nr_mileage(measurement.measures.Distance(km=x).yd)))
                temp_mileage_data.Mileage = temp_mileages.tolist()
                checked_mileage_data = temp_mileage_data

            elif 'One measure' in test_temp_node:
                sep_rows_idx = mileage_data[
                    mileage_data.Node.str.contains('Alternative measure')].index[0]
                mileage_data_1, mileage_data_2 = np.split(mileage_data, [sep_rows_idx], axis=0)
                checked_mileage_data = {
                    'One measure': mileage_data_1[~mileage_data_1.Node.str.contains('One measure')],
                    'Alternative measure':
                        mileage_data_2[~mileage_data_2.Node.str.contains('Alternative measure')]}

            elif 'This line has two \'legs\':' in test_temp_node:
                temp_mileage_data = mileage_data.iloc[1:].drop_duplicates()
                temp_mileage_data.index = range(len(temp_mileage_data))
                checked_mileage_data = temp_mileage_data

            else:
                test_temp_text = [' '.join(x) for x in itertools.product(
                    *(('Current', 'Later', 'One', 'Original', 'Former', 'Alternative', 'Usual',
                       'Earlier'), ('measure', 'route')))]
                alt_sep_rows_idx = [x in test_temp_node for x in test_temp_text]
                num_of_measures = sum(alt_sep_rows_idx)

                if num_of_measures == 1:  #
                    mileage_data_1, mileage_data_2 = np.split(mileage_data, [sep_rows_idx], axis=0)

                    if re.match(r'(Original)|(Former)|(Alternative)|(Usual)', test_temp_node[0]):
                        measure_ = re.sub(r'(Original)|(Former)|(Alternative)|(Usual)', r'Current',
                                          test_temp_node[0])
                    else:
                        measure_ = re.sub(
                            r'(Current)|(Later)|(One)', r'Previous', test_temp_node[0])

                    checked_mileage_data = {
                        measure_: mileage_data_1.loc[0:sep_rows_idx, :],
                        test_temp_node[0]: mileage_data_2.loc[sep_rows_idx + 1:, :]}

                elif num_of_measures == 2:  # e.g. elr='BTJ'
                    sep_rows_idx_items = [test_temp_text[x] for x in np.where(alt_sep_rows_idx)[0]]

                    sep_rows_idx = \
                        mileage_data[mileage_data.Node.isin(sep_rows_idx_items)].index[-1]

                    mileage_data_1, mileage_data_2 = np.split(mileage_data, [sep_rows_idx], axis=0)

                    sep_rows_idx_items_checked = [
                        mileage_data_1[mileage_data_1.Node.isin(sep_rows_idx_items)].Node.iloc[0],
                        mileage_data_2[mileage_data_2.Node.isin(sep_rows_idx_items)].Node.iloc[0]]

                    mileage_data_1 = mileage_data_1[~mileage_data_1.Node.isin(sep_rows_idx_items)]
                    mileage_data_2 = mileage_data_2[~mileage_data_2.Node.isin(sep_rows_idx_items)]

                    checked_mileage_data = dict(zip(sep_rows_idx_items_checked,
                                                    [mileage_data_1, mileage_data_2]))

                else:
                    if mileage_data.loc[sep_rows_idx, 'Mileage'] == '':
                        mileage_data.loc[sep_rows_idx, 'Mileage'] = \
                            mileage_data.loc[sep_rows_idx - 1, 'Mileage']
                    checked_mileage_data = mileage_data

        else:
            checked_mileage_data = mileage_data

        return checked_mileage_data

    @staticmethod
    def _parse_mileage_col(mileage):
        """
        Parse column of mileage data.

        :param mileage: column of mileage data
        :type mileage: pandas.Series
        :return: parsed mileages
        :rtype: pandas.DataFrame

        :meta private:
        """

        mileage.index = range(len(mileage))

        if any(mileage.str.match('.*km')):
            if all(mileage.str.match('.*km')):
                temp_mileage = mileage.str.replace('km', '').map(
                    lambda x: yards_to_nr_mileage(
                        measurement.measures.Distance(km=x.replace('≈', '')).british_yd))

                # Might be wrong!
                miles_chains = temp_mileage.map(lambda x: nr_mileage_to_mile_chain(x))

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
    def _parse_node_col(node):
        """
        Parse column of node data.

        :param node: column of node data
        :type node: pandas.Series
        :return: parsed nodes
        :rtype: pandas.DataFrame

        :meta private:
        """

        def preprocess_node_x(node_x):
            # node_x = node_x.replace(
            #     ' with Freightliner terminal', ' & Freightliner Terminal').replace(
            #     ' with curve to', ' with').replace(
            #     ' (0.37 long)', '')
            # pat = re.compile(
            #     r'\w+.*( \(\d+\.\d+\))?(/| and \w+)? with '
            #     r'([A-Z]){3}(\d)?( \(\d+\.\d+\))?')
            pat = re.compile(
                r'\w+.*( \(\d+\.\d+\))?(/| and \w+)? with ([A-Z]).*(\d)?( \(\d+\.\d+\))?')

            if re.match(pat, node_x):
                node_name = [x.group() for x in re.finditer(r'\w+.*(?= with)', node_x)]
                conn_node = [x.group() for x in re.finditer(r'(?<= with )[^*]+', node_x)]

            else:
                node_name, conn_node = [node_x], [None]

            return node_name + conn_node

        prep_node = pd.DataFrame((preprocess_node_x(n) for n in node),
                                 columns=['Node', 'Connection'])

        def parse_nodes(prep_nodes):
            conn_node_lst = []
            for n in prep_nodes.Connection:
                if n is not None:
                    if re.match(r'[A-Z]{3}(\d)?( \(\d+.\d+\))? ?/ ?[A-Z]{3}(\d)?'
                                r'( \(\d+.\d+\))?', n):
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
                temp_lst = [x.replace('later ', '').rstrip(',').split(' and ')
                            for x in conn_node_lst[i] if isinstance(x, str)]

                conn_node_lst[i] = [v for lst in temp_lst for v in lst]
                temp_lst = [x.split(', ') for x in conn_node_lst[i]]
                conn_node_lst[i] = [v for lst in temp_lst for v in lst]

            most_conn = max(len(c) for c in conn_node_lst)
            # conn_node_list = [c + [None] * (most_conn - len(c)) for c in conn_node_list]

            return pd.DataFrame(conn_node_lst,
                                columns=['Link_{}'.format(n + 1) for n in range(most_conn)])

        conn_nodes = parse_nodes(prep_node)

        def uncouple_elr_mileage(node_x):
            # e.g. x = 'ECM5 (44.64)' or x = 'DNT'
            if node_x is None:
                y = ['', '']
            else:
                # pat0 = re.compile(r'\w+.*(( lines)|( terminal))$')
                pat1 = re.compile(r'([A-Z]{3}(\d)?$)|((\w\s?)*\w$)')
                pat2 = re.compile(r'([A-Z]{3}(\d)?$)|(([\w\s&]?)*(\s\(\d+\.\d+\))?$)')
                # pat3 = re.compile(r'[A-Z]{3}(\d)?(\s\(\d+.\d+\))?\s\[.*?\]$')
                pat3 = re.compile(r'[A-Z]{3}(\d)?(\s\(\d+.\d+\))?\s\[.*?]$')
                pat4 = re.compile(r'[A-Z]{3}(\d)?\s\(\d+\.\d+km\)')
                # if re.match(pat0, node_x):
                #     y = ['', '']
                if re.match(pat1, node_x):
                    y = [node_x, '']
                elif re.match(pat2, node_x):
                    y = [z[:-1] if re.match(r'\d+.\d+\)', z) else z.strip()
                         for z in node_x.split('(')]
                    y[0] = '' if len(y[0]) > 4 else y[0]
                elif re.match(pat3, node_x):
                    try:
                        y = [re.search(r'[A-Z]{3}(\d)?', node_x).group(0),
                             re.search(r'\d+\.\d+', node_x).group(0)]
                    except AttributeError:
                        y = [re.search(r'[A-Z]{3}(\d)?', node_x).group(0), '']
                elif re.match(pat4, node_x):
                    y = [re.search(r'[A-Z]{3}(\d)?', node_x).group(0),
                         nr_mileage_to_mile_chain(yards_to_nr_mileage(
                             measurement.measures.Distance(
                                 km=re.search(r'\d+\.\d+', node_x).group(0)).yd))]
                else:
                    y = [node_x, ''] if len(node_x) <= 4 else ['', '']
                y[0] = y[0] if len(y[0]) <= 4 else ''
            return y

        #
        link_cols = [x for x in conn_nodes.columns if re.match(r'^(Link_\d)', x)]
        link_nodes = conn_nodes[link_cols].applymap(lambda x: uncouple_elr_mileage(x))
        link_elr_mileage = pd.concat(
            [pd.DataFrame(link_nodes[col].values.tolist(),
                          columns=[col + '_ELR', col + '_Mile_Chain'])
             for col in link_cols], axis=1, sort=False)
        parsed_node_and_conn = pd.concat([prep_node, conn_nodes, link_elr_mileage],
                                         axis=1, sort=False)

        return parsed_node_and_conn

    def _parse_mileage_data(self, mileage_data):
        """
        Parse scraped data of mileage file.

        :param mileage_data: preprocessed data of mileage file scraped from source web page
        :type mileage_data: pandas.DataFrame
        :return: parsed data of mileage file
        :rtype: pandas.DataFrame
        """

        mileage, node = mileage_data.iloc[:, 0], mileage_data.iloc[:, 1]

        parsed_mileage = self._parse_mileage_col(mileage)
        parsed_node_and_conn = self._parse_node_col(node)

        parsed_dat = pd.concat([parsed_mileage, parsed_node_and_conn], axis=1, sort=False)

        return parsed_dat

    def collect_elr_by_initial(self, initial, update=False, verbose=False):
        """
        Collect Engineer's Line References (ELRs) for the given initial letter from source web page.

        :param initial: initial letter of an ELR, e.g. ``'a'``, ``'z'``
        :type initial: str
        :param update: whether to check on update and proceed to update the package data, 
            defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console as the function runs,
            defaults to ``False``
        :type verbose: bool or int
        :return: data of ELRs whose names start with the given ``initial`` and
            date of when the data was last updated
        :rtype: dict

        **Example**::

            >>> from pyrcs.line_data import ELRMileages

            >>> em = ELRMileages()

            >>> # elrs_a = em.collect_elr_by_initial(initial='a', update=True, verbose=True)
            >>> elrs_a = em.collect_elr_by_initial(initial='a')

            >>> type(elrs_a)
            <class 'dict'>
            >>> print(list(elrs_a.keys()))
            ['A', 'Last updated date']

            >>> print(elrs_a['A'].head())
               ELR  ...         Notes
            0  AAL  ...      Now NAJ3
            1  AAM  ...  Formerly AML
            2  AAV  ...
            3  ABB  ...       Now AHB
            4  ABB  ...
            [5 rows x 5 columns]
        """

        assert initial in string.ascii_letters
        beginning_with = initial.upper()

        path_to_pickle = self._cdd_em("a-z", beginning_with.lower() + ".pickle")
        if os.path.isfile(path_to_pickle) and not update:
            elrs = load_pickle(path_to_pickle)

        else:
            url = self.Catalogue[beginning_with]  # Specify the requested URL

            elrs = {beginning_with: None, self.LUDKey: None}

            if verbose == 2:
                print("Collecting data of {} beginning with \"{}\"".format(
                    self.Key, beginning_with), end=" ... ")

            try:
                source = requests.get(url, headers=fake_requests_headers())
            except requests.exceptions.ConnectionError:
                print("Failed.") if verbose == 2 else ""
                print_conn_err(verbose=verbose)

            else:
                try:
                    records, header = parse_table(source, parser='lxml')
                    # Create a DataFrame of the requested table
                    dat = [[x.replace('=', 'See').strip('\xa0') for x in i] for i in records]
                    data = pd.DataFrame(dat, columns=header)

                    # Update the dict with both the DataFrame and its last updated date
                    elrs.update({beginning_with: data, self.LUDKey: get_last_updated_date(url)})

                    print("Done.") if verbose == 2 else ""

                    os.makedirs(os.path.dirname(path_to_pickle), exist_ok=True)
                    save_pickle(elrs, path_to_pickle, verbose=verbose)

                except Exception as e:  # e.g the requested URL is not available:
                    print("Failed. {}".format(e))

        return elrs

    def fetch_elr(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch ELRs and mileages from local backup.

        :param update: whether to check on update and proceed to update the package data, 
            defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data with newly collected data,
            defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console as the function runs,
            defaults to ``False``
        :type verbose: bool or int
        :return: data of all available ELRs and date of when the data was last updated
        :rtype: dict

        **Example**::

            >>> from pyrcs.line_data import ELRMileages

            >>> em = ELRMileages()

            >>> elrs_dat = em.fetch_elr()

            >>> type(elrs_dat)
            <class 'dict'>
            >>> print(list(elrs_dat.keys()))
            ['ELRs', 'Last updated date']

            >>> print(elrs_dat['ELRs'])
               ELR  ...         Notes
            0  AAL  ...      Now NAJ3
            1  AAM  ...  Formerly AML
            2  AAV  ...
            3  ABB  ...       Now AHB
            4  ABB  ...
            [5 rows x 5 columns]
        """

        verbose_ = False if (data_dir or not verbose) else (2 if verbose == 2 else True)

        data = [
            self.collect_elr_by_initial(
                x, update, verbose=verbose_ if is_internet_connected() else False)
            for x in string.ascii_lowercase]

        if all(d[x] is None for d, x in zip(data, string.ascii_uppercase)):
            if update:
                print_conn_err(verbose=verbose)
                print("No data of the {} has been freshly collected.".format(self.Key))
            data = [self.collect_elr_by_initial(x, update=False, verbose=verbose_)
                    for x in string.ascii_lowercase]

        # Select DataFrames only
        elrs_data = (item[x] for item, x in zip(data, string.ascii_uppercase))
        elrs_data_table = pd.concat(elrs_data, axis=0, ignore_index=True, sort=False)

        # Get the latest updated date
        last_updated_dates = (item[self.LUDKey]
                              for item, _ in zip(data, string.ascii_uppercase))
        latest_update_date = max(d for d in last_updated_dates if d is not None)

        elrs_data = {self.Key: elrs_data_table, self.LUDKey: latest_update_date}

        if pickle_it and data_dir:
            pickle_filename = self.Name.lower().replace(" ", "-") + ".pickle"
            self.CurrentDataDir = validate_input_data_dir(data_dir)
            path_to_pickle = os.path.join(self.CurrentDataDir, pickle_filename)
            save_pickle(elrs_data, path_to_pickle, verbose=verbose)

        return elrs_data

    def collect_mileage_file(self, elr, parsed=True, confirmation_required=True,
                             pickle_it=False, verbose=False):
        """
        Collect mileage file for the given ELR from source web page.

        :param elr: ELR, e.g. ``'CJD'``, ``'MLA'``, ``'FED'``
        :type elr: str
        :param parsed: whether to parse the scraped mileage data
        :type parsed: bool
        :param confirmation_required: whether to prompt a message for confirmation to proceed,
            defaults to ``True``
        :type confirmation_required: bool
        :param pickle_it: whether to replace the current package data with newly collected data,
            defaults to ``False``
        :type pickle_it: bool
        :param verbose: whether to print relevant information in console as the function runs,
            defaults to ``False``
        :type verbose: bool or int
        :return: mileage file for the given ``elr``
        :rtype: dict

        .. note::

            - In some cases, mileages are unknown hence left blank,
              e.g. ANI2, Orton Junction with ROB (~3.05)
            - Mileages in parentheses are not on that ELR, but are included for reference,
              e.g. ANL, (8.67) NORTHOLT [London Underground]
            - As with the main ELR list, mileages preceded by a tilde (~) are approximate.

        **Examples**::

            >>> from pyrcs.line_data import ELRMileages

            >>> em = ELRMileages()

            >>> mileage_dat = em.collect_mileage_file(elr='CJD')
            To collect mileage file for "CJD"? [No]|Yes: yes
            >>> type(mileage_dat)
            dict
            >>> print(list(mileage_dat.keys()))
            ['ELR', 'Line', 'Sub-Line', 'Mileage', 'Notes']

            >>> mileage_dat = em.collect_mileage_file(elr='GAM')
            To collect mileage file of "GAM"? [No]|Yes: yes
            >>> print(mileage_dat['Mileage'])
               Mileage Mileage_Note Miles_Chains  ... Link_1 Link_1_ELR Link_1_Mile_Chain
            0   8.1518                      8.69  ...   None
            1  10.0264                     10.12  ...   None
            [2 rows x 8 columns]

            >>> mileage_dat = em.collect_mileage_file(elr='SLD')
            To collect mileage file of "SLD"? [No]|Yes: yes
            >>> print(mileage_dat['Mileage'])
               Mileage Mileage_Note Miles_Chains  ... Link_1 Link_1_ELR Link_1_Mile_Chain
            0  30.1694                     30.77  ...   None
            1  32.1210                     32.55  ...   None
            [2 rows x 8 columns]

            >>> mileage_dat = em.collect_mileage_file(elr='ELR')
            To collect mileage file of "ELR"? [No]|Yes: yes
            >>> print(mileage_dat['Mileage'].head())
                Mileage Mileage_Note  ... Link_1_ELR Link_1_Mile_Chain
            0  122.0044               ...       GRS3
            1  122.0682               ...                         0.00
            2  122.0726               ...        SPI              0.00
            3  122.0836               ...
            4  124.0792               ...
            [5 rows x 8 columns]
        """

        elr = remove_punctuation(elr)

        if elr != '':

            mileage_file = None

            if confirmed("To collect mileage file of \"{}\"?".format(elr.upper()),
                         confirmation_required=confirmation_required):

                # The URL of the mileage file for the ELR
                url = self.HomeURL + f'/elrs/_mileages/{elr[0].lower()}/{elr.lower()}.shtm'

                if verbose == 2:
                    print("Collecting mileage file of \"{}\"".format(elr.upper()), end=" ... ")

                try:
                    source = requests.get(url, headers=fake_requests_headers())
                except requests.ConnectionError:
                    print("Failed.") if verbose == 2 else ""
                    print_conn_err(verbose=verbose)

                else:
                    try:
                        source_text = bs4.BeautifulSoup(source.text, 'lxml')

                        line_name = source_text.find('h3').text
                        sub_line_name_ = source_text.find('h4')
                        sub_line_name = sub_line_name_.text if sub_line_name_ else sub_line_name_

                        err404 = '"404" error: page not found'

                        if line_name == err404 or sub_line_name == err404:
                            elr_dat = self.collect_elr_by_initial(elr[0])[elr[0]]
                            elr_dat = elr_dat[elr_dat.ELR == elr]

                            notes = elr_dat.Notes.values[0]
                            if re.match(r'(Now( part of)? |= |See )[A-Z]{3}(\d)?$', notes):
                                new_elr = re.search(r'(?<= )[A-Z]{3}(\d)?', notes).group(0)
                                mileage_file = self.collect_mileage_file(
                                    elr=new_elr, parsed=parsed,
                                    confirmation_required=confirmation_required,
                                    pickle_it=pickle_it, verbose=verbose)

                                return mileage_file

                            else:
                                line_name, mileages, datum = elr_dat[
                                    ['Line name', 'Mileages', 'Datum']].values[0]

                                if re.match(r'(\w ?)+ \((\w+ \w+)+.\)', line_name):
                                    line_name_ = re.search(
                                        r'(?<=\w \()(\w+ \w+)+.(?=\))', line_name).group(0)
                                    try:
                                        location_a, _, location_b = re.split(
                                            r' (and|&|to) ', line_name_)
                                        line_name = re.search(
                                            r'(\w+ \w+)+.(?= \((\w ?)+\))', line_name).group(0)
                                    except ValueError:
                                        location_a, _, location_b = re.split(
                                            r' (and|&|to) ', notes)
                                        line_name = line_name_

                                elif elr_dat.Mileages.values[0].startswith('0.00') and \
                                        elr_dat.Datum.values[0] != '':
                                    location_a = elr_dat.Datum.values[0]
                                    location_b = re.split(r' (and|&|to) ', line_name)[2] \
                                        if location_a in line_name else line_name

                                elif re.match(r'(\w ?)+ to (\w ?)+', notes):
                                    location_a, location_b = notes.split(' to ')

                                else:
                                    try:
                                        location_a, _, location_b = re.split(
                                            r' (and|&|to|-) ', notes)
                                    except (ValueError, TypeError):
                                        pass

                                    try:
                                        location_a, _, location_b = re.split(
                                            r' (and|&|to|-) ', line_name)
                                    except (ValueError, TypeError):
                                        pass

                                    if line_name:
                                        location_a, location_b = line_name, line_name
                                    else:
                                        location_a, location_b = '', ''

                                # location_b_ = re.sub(r' Branch| Curve', '', location_b) \
                                #     if re.match(r'.*( Branch| Curve)$', location_b) \
                                #     else location_b

                                miles_chains = mileages.split(' - ')
                                locations = [location_a, location_b]
                                parsed_content = [[m, l] for m, l in zip(miles_chains, locations)]

                        else:
                            line_name = line_name.split('\t')[1]
                            parsed_content = [x.strip().split('\t', 1)
                                              for x in source_text.find('pre').text.splitlines()
                                              if x != '']
                            parsed_content = [[y.replace('  ', ' ').replace('\t', ' ') for y in x]
                                              for x in parsed_content]
                            parsed_content = [[''] + x if (len(x) == 1) & ('Note that' not in x[0])
                                              else x
                                              for x in parsed_content]

                        # assert sub_headers[0] == elr
                        if sub_line_name and sub_line_name != err404:
                            sub_headers = sub_line_name.split('\t')[1]
                        else:
                            sub_headers = ''

                        # Make a dict of line information
                        line_info = {'ELR': elr, 'Line': line_name, 'Sub-Line': sub_headers}

                        # Search for note
                        note_temp = min(parsed_content, key=len)
                        notes = note_temp[0] if len(note_temp) == 1 else ''
                        if notes:
                            if ' Revised distances are thus:' in notes:
                                parsed_content[parsed_content.index(note_temp)] = [
                                    '', 'Current measure']
                                notes = notes.replace(' Revised distances are thus:', '')
                            else:
                                parsed_content.remove(note_temp)

                        # Create a table of the mileage data
                        mileage_data = pd.DataFrame(parsed_content, columns=['Mileage', 'Node'])

                        # Check if there is any missing note
                        if mileage_data.iloc[-1].Mileage == '':
                            notes = [notes, mileage_data.iloc[-1].Node] if notes \
                                else mileage_data.iloc[-1].Node
                            mileage_data = mileage_data[:-1]

                        if len(mileage_data.iloc[-1].Mileage) > 6:
                            notes = [notes, mileage_data.iloc[-1].Mileage] if notes \
                                else mileage_data.iloc[-1].Mileage
                            mileage_data = mileage_data[:-1]

                        # Make a dict of note
                        note_dat = {'Notes': notes}

                        # Identify if there are multiple measures in 'mileage_data'
                        # e.g current and former measures
                        mileage_data = self._parse_multi_measures(mileage_data)

                        if parsed:
                            if isinstance(mileage_data, dict) and len(mileage_data) > 1:
                                mileage_data = {h: self._parse_mileage_data(dat)
                                                for h, dat in mileage_data.items()}
                            else:  # isinstance(dat, pd.DataFrame)
                                mileage_data = self._parse_mileage_data(mileage_data)

                        mileage_file = dict(
                            pair for x in [line_info, {'Mileage': mileage_data}, note_dat]
                            for pair in x.items())

                        print("Done.") if verbose == 2 else ""

                        if pickle_it:
                            path_to_pickle = self._cdd_em(
                                "mileage-files", elr[0].lower(), elr + ".pickle", mkdir=True)

                            if os.path.basename(path_to_pickle) == "prn.pickle":
                                path_to_pickle = \
                                    path_to_pickle.replace("prn.pickle", "prn_x.pickle")

                            save_pickle(mileage_file, path_to_pickle, verbose=verbose)

                    except Exception as e:
                        print("Failed. {}.".format(e))

            return mileage_file

    def fetch_mileage_file(self, elr, update=False, pickle_it=False, data_dir=None,
                           verbose=False):
        """
        Fetch mileage file for the given ELR from local backup.

        :param elr: elr: ELR, e.g. ``'CJD'``, ``'MLA'``, ``'FED'``
        :type elr: str
        :param update: whether to check on update and proceed to update the package data, 
            defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data with newly collected data,
            defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console as the function runs,
            defaults to ``False``
        :type verbose: bool or int
        :return: mileage file (codes), line name and, if any, additional information/notes
        :rtype: dict

        **Example**::

            >>> from pyrcs.line_data import ELRMileages

            >>> em = ELRMileages()

            >>> mileage_dat = em.fetch_mileage_file('MLA')

            >>> type(mileage_dat)
            dict
            >>> list(mileage_dat.keys())
            ['ELR', 'Line', 'Sub-Line', 'Mileage', 'Notes']

            >>> type(mileage_dat['Mileage'])
            dict
            >>> list(mileage_dat['Mileage'].keys())
            ['Current measure', 'Original measure']
            >>> print(mileage_dat['Mileage']['Current measure'])
              Mileage Mileage_Note Miles_Chains  ...       Link_1 Link_1_ELR Link_1_Mile_Chain
            0  0.0000                      0.00  ...  MRL2 (4.44)       MRL2              4.44
            1  0.0572                      0.26  ...         None
            2  0.1540                      0.70  ...         None
            3  0.1606                      0.73  ...         None
            [4 rows x 8 columns]
        """

        path_to_pickle = self._cdd_em("mileage-files", elr[0].lower(), elr + ".pickle")

        if os.path.basename(path_to_pickle) == "prn.pickle":
            path_to_pickle = path_to_pickle.replace("prn.pickle", "prn_x.pickle")

        if os.path.isfile(path_to_pickle) and not update:
            mileage_file = load_pickle(path_to_pickle)

        else:
            verbose_ = False if data_dir or not verbose else (2 if verbose == 2 else True)
            mileage_file = self.collect_mileage_file(
                elr, parsed=True, confirmation_required=False, pickle_it=pickle_it,
                verbose=verbose_)

            if mileage_file:
                if pickle_it and data_dir:
                    self.CurrentDataDir = validate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(
                        self.CurrentDataDir, os.path.basename(path_to_pickle))
                    save_pickle(mileage_file, path_to_pickle, verbose=verbose)

            else:
                print("No mileage file of \"{}\" has been {}collected.".format(
                    elr.upper(), "freshly " if update else ""))

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
        :return: connection, in the form
            (<end mileage of the start ELR>, <start mileage of the end ELR>)
        :rtype: tuple

        **Example**::

            >>> from pyrcs.line_data import ELRMileages

            >>> em = ELRMileages()

            >>> s_elr = 'AAM'
            >>> s_m_file = em.collect_mileage_file(s_elr, confirmation_required=False)
            >>> s_m_data = s_m_file['Mileage']

            >>> e_elr = 'ANZ'
            >>> e_m_file = em.collect_mileage_file(e_elr, confirmation_required=False)
            >>> e_m_data = e_m_file['Mileage']

            >>> s_dest_mileage, e_orig_mileage = em.search_conn(s_elr, s_m_data, e_elr, e_m_data)

            >>> print(s_dest_mileage)
            0.0396
            >>> print(e_orig_mileage)
            84.1364
        """

        start_mask = start_em.apply(
            lambda x: x.str.contains(end_elr, case=False).any(), axis=1)
        start_temp = start_em[start_mask]
        assert isinstance(start_temp, pd.DataFrame)

        if not start_temp.empty:
            # Get exact location
            key_idx = start_temp.index[0]
            mile_chain_col = [x for x in start_temp.columns
                              if re.match(r'.*_Mile_Chain', x)][0]
            # Mileage of the Start ELR
            start_dest_mileage = start_em.loc[key_idx, 'Mileage']
            # Mileage of the End ELR
            end_orig_mile_chain = start_temp.loc[key_idx, mile_chain_col]

            if end_orig_mile_chain and end_orig_mile_chain != 'Unknown':
                end_orig_mileage = mile_chain_to_nr_mileage(end_orig_mile_chain)
            else:  # end_conn_mile_chain == '':
                end_mask = end_em.apply(
                    lambda x: x.str.contains(start_elr, case=False).any(), axis=1)
                end_temp = end_em[end_mask]

                if not end_temp.empty:
                    end_orig_mileage = end_temp.Mileage.iloc[0]
                else:
                    end_orig_mileage = start_dest_mileage

        else:
            start_dest_mileage, end_orig_mileage = '', ''

        return start_dest_mileage, end_orig_mileage

    def get_conn_mileages(self, start_elr, end_elr, update=False, pickle_mileage_file=False,
                          data_dir=None, verbose=False):
        """
        Get a connection point between two ELR-and-mileage pairs.

        Namely, find the end and start mileages for the start and end ELRs, respectively.

        .. note::

            This function may not be able find the connection for every pair of ELRs.
            See the :ref:`Example 2<get_conn_mileages-example-2>` below.

        :param start_elr: start ELR
        :type start_elr: str
        :param end_elr: end ELR
        :type end_elr: str
        :param update: whether to check on update and proceed to update the package data, 
            defaults to ``False``
        :type update: bool
        :param pickle_mileage_file: whether to replace the current mileage file,
            defaults to ``False``
        :type pickle_mileage_file: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console as the function runs,
            defaults to ``False``
        :type verbose: bool or int
        :return: connection ELR and mileages between the given ``start_elr`` and ``end_elr``
        :rtype: tuple

        **Example 1**::

            >>> from pyrcs.line_data import ELRMileages

            >>> em = ELRMileages()

            >>> conn = em.get_conn_mileages('NAY', 'LTN2')
            >>> (s_dest_mileage, c_elr, c_orig_mileage, c_dest_mileage, e_orig_mileage) = conn

            >>> print(s_dest_mileage)
            5.1606
            >>> print(c_elr)
            NOL
            >>> print(c_orig_mileage)
            5.1606
            >>> print(c_dest_mileage)
            0.0638
            >>> print(e_orig_mileage)
            123.1320

        .. _get_conn_mileages-example-2:

        **Example 2**::

            >>> from pyrcs.line_data import ELRMileages

            >>> em = ELRMileages()

            >>> conn = em.get_conn_mileages('MAC3', 'DBP1')
            >>> print(conn)
            ('', '', '', '', '')
        """

        start_file = self.fetch_mileage_file(start_elr, update, pickle_mileage_file, data_dir,
                                             verbose=verbose)
        end_file = self.fetch_mileage_file(end_elr, update, pickle_mileage_file, data_dir,
                                           verbose=verbose)

        if start_file is not None and end_file is not None:
            start_elr, end_elr = start_file['ELR'], end_file['ELR']
            start_em, end_em = start_file['Mileage'], end_file['Mileage']
            key_pat = re.compile(r'(Current\s)|(One\s)|(Later\s)|(Usual\s)')
            if isinstance(start_em, dict):
                start_em = start_em[[k for k in start_em.keys() if re.match(key_pat, k)][0]]
            if isinstance(end_em, dict):
                end_em = end_em[[k for k in end_em.keys() if re.match(key_pat, k)][0]]
            #
            start_dest_mileage, end_orig_mileage = self.search_conn(
                start_elr, start_em, end_elr, end_em)

            conn_elr, conn_orig_mileage, conn_dest_mileage = '', '', ''

            if not start_dest_mileage and not end_orig_mileage:
                link_cols = [x for x in start_em.columns if re.match(r'Link_\d_ELR.?', x)]
                conn_elrs = start_em[link_cols]

                i = 0
                while i < len(link_cols):
                    link_col = link_cols[i]
                    conn_temp = conn_elrs[
                        conn_elrs.astype(bool)].dropna(how='all')[link_col].dropna()

                    j = 0
                    while j < len(conn_temp):
                        conn_elr = conn_temp.iloc[j]
                        conn_em = self.fetch_mileage_file(conn_elr, update=update)
                        if conn_em is not None:
                            conn_elr = conn_em['ELR']
                            conn_em = conn_em['Mileage']
                            if isinstance(conn_em, dict):
                                conn_em = conn_em[[k for k in conn_em.keys()
                                                   if re.match(key_pat, k)][0]]
                            #
                            start_dest_mileage, conn_orig_mileage = \
                                self.search_conn(start_elr, start_em, conn_elr, conn_em)
                            #
                            conn_dest_mileage, end_orig_mileage = \
                                self.search_conn(conn_elr, conn_em, end_elr, end_em)

                            if conn_dest_mileage and end_orig_mileage:
                                if not start_dest_mileage:
                                    start_dest_mileage = start_em[
                                        start_em[link_col] == conn_elr].Mileage.values[0]
                                if not conn_orig_mileage:
                                    link_col_conn = conn_em.where(conn_em == start_elr).dropna(
                                        axis=1, how='all').columns[0]
                                    temp = conn_em[conn_em[link_col_conn] == start_elr].Mileage
                                    conn_orig_mileage = temp.values[0]
                                break

                            else:
                                conn_elr = ''
                        j += 1

                    if conn_elr != '':
                        break
                    else:
                        i += 1

            if conn_orig_mileage and not conn_elr:
                start_dest_mileage, conn_orig_mileage = '', ''

        else:
            (start_dest_mileage,
             conn_elr,
             conn_orig_mileage,
             conn_dest_mileage,
             end_orig_mileage) = [''] * 5

        return (start_dest_mileage,
                conn_elr,
                conn_orig_mileage,
                conn_dest_mileage,
                end_orig_mileage)
