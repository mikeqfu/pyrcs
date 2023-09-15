"""
Collect `Engineer's Line References (ELRs) <http://www.railwaycodes.org.uk/elrs/elr0.shtm>`_.
"""

import copy
import functools
import itertools
import os
import re
import string
import urllib.parse

import bs4
import numpy as np
import pandas as pd
import requests
from pyhelpers.dirs import cd
from pyhelpers.ops import confirmed, fake_requests_headers, loop_in_pairs
from pyhelpers.store import load_data, save_data
from pyhelpers.text import remove_punctuation

from ..converter import kilometer_to_yard, mile_chain_to_mileage, mileage_to_mile_chain, yard_to_mileage
from ..parser import get_catalogue, get_last_updated_date, parse_table
from ..utils import collect_in_fetch_verbose, format_err_msg, home_page_url, init_data_dir, \
    is_home_connectable, is_str_float, print_conn_err, print_inst_conn_err, print_void_msg, \
    save_data_to_file, validate_initial


class ELRMileages:
    """
    A class for collecting data of
    `Engineer's Line References (ELRs) <http://www.railwaycodes.org.uk/elrs/elr0.shtm>`_.
    """

    #: str: Name of the data.
    NAME = "Engineer's Line References (ELRs)"
    #: str: Key of the `dict <https://docs.python.org/3/library/stdtypes.html#dict>`_-type data.
    KEY = 'ELRs and mileages'
    #: str: URL of the main web page of the data.
    URL = urllib.parse.urljoin(home_page_url(), '/elrs/elr0.shtm')
    #: str: Key of the data of the last updated date.
    KEY_TO_LAST_UPDATED_DATE = 'Last updated date'

    def __init__(self, data_dir=None, update=False, verbose=True):
        """
        :param data_dir: The name of a folder for the data directory, defaults to ``None``.
        :type data_dir: str or None
        :param update: Whether to do an update check (for the package data), defaults to ``False``.
        :type update: bool
        :param verbose: Whether to print relevant information in console, defaults to ``True``.
        :type verbose: bool or int

        :ivar dict catalogue: The catalogue of the data.
        :ivar str last_updated_date: The last updated date.
        :ivar str data_dir: An absolute path to the data directory.
        :ivar str current_data_dir: An absolute path to the current data directory.
        :ivar list measure_headers: A list of possible headers for different measures.

        **Examples**::

            >>> from pyrcs.line_data import ELRMileages  # from pyrcs import ELRMileages

            >>> em = ELRMileages()

            >>> em.NAME
            "Engineer's Line References (ELRs)"

            >>> em.URL
            'http://www.railwaycodes.org.uk/elrs/elr0.shtm'
        """

        print_conn_err(verbose=verbose)

        self.catalogue = get_catalogue(url=self.URL, update=update, confirmation_required=False)

        self.last_updated_date = get_last_updated_date(url=self.URL, parsed=True, as_date_type=False)

        self.data_dir, self.current_data_dir = init_data_dir(
            self, data_dir=data_dir, category="line-data")

        self.measure_headers = [' '.join(x) for x in itertools.product(
            *(('Current', 'Later', 'Earlier', 'One', 'Original', 'Former', 'Alternative', 'Usual',
               'New', 'Old'),
              ('measure', 'route', 'diversion')))]

    def _cdd(self, *sub_dir, mkdir=True, **kwargs):
        """
        Change directory to package data directory and subdirectories (and/or a file).

        The directory for this module: ``"data\\line-data\\elrs-and-mileages"``.

        :param sub_dir: subdirectory or subdirectories (and/or a file)
        :type sub_dir: str
        :param mkdir: whether to create the specified directory, defaults to ``True``
        :type mkdir: bool
        :param kwargs: [optional] parameters of the function `pyhelpers.dir.cd`_
        :return: path to the backup data directory for the class
            :py:class:`~pyrcs.line_data.elr_mileage.ELRMileages`
        :rtype: str

        .. _`pyhelpers.dir.cd`:
            https://pyhelpers.readthedocs.io/en/latest/_generated/pyhelpers.dir.cd.html
        """

        kwargs.update({'mkdir': mkdir})
        path = cd(self.data_dir, *sub_dir, **kwargs)

        return path

    def _split_measures(self, mileage_data, measure_headers_indices):
        """
        Process data of mileage file with multiple measures.

        :param mileage_data: scraped raw mileage file from source web page
        :type: pandas.DataFrame
        """

        dat = mileage_data.copy()

        if len(measure_headers_indices) >= 1:

            if len(measure_headers_indices) == 1 and measure_headers_indices[0] != 0:
                j = measure_headers_indices[0]
                m_key, _ = dat.loc[j, 'Node'].split(maxsplit=1)
                d = {
                    'Earlier': 'Later',
                    'Later': 'Earlier',
                    'Alternative': 'One',
                    'Alternate': 'One',
                    'One': 'Alternative',
                    'Original': 'Current',
                    'Current': 'Original',
                    'Former': 'Current',
                    'Old': 'Current',
                    'New': 'Old',
                }
                if m_key in d:
                    measure_headers_indices = [0] + [j + 1]
                    new_m_key = d[m_key] + ' measure'
                    dat.loc[-1] = ['', new_m_key]  # adding a row
                    dat.index = dat.index + 1
                    dat.sort_index(inplace=True)

            # if measure_headers_indices[-1] != dat.index[-1] - 1:
            #     sep_rows_idx = loop_in_pairs(measure_headers_indices + [dat.index[-1]])
            # else:
            sep_rows_idx = loop_in_pairs(measure_headers_indices + [dat.index[-1] + 1])
            dat_ = {dat.loc[i, 'Node']: dat.loc[i + 1:j - 1] for i, j in sep_rows_idx}

        else:
            test_temp = dat[~dat['Mileage'].astype(bool)]
            if not test_temp.empty:
                test_temp_node, sep_rows_idx = test_temp['Node'].tolist(), test_temp.index[-1]

                if '1949 measure' in test_temp_node:
                    dat['Node'] = dat['Node'].str.replace('1949 measure', 'Current measure')
                    test_temp_node = [re.sub(r'1949 ', 'Current ', x) for x in test_temp_node]

                # if 'Distances in km' in test_temp_node:
                #     dat_ = dat[~dat['Node'].str.contains('Distances in km')]
                #     temp_mileages = dat_['Mileage'].map(
                #         lambda x: mileage_to_mile_chain(yard_to_mileage(kilometer_to_yard(km=x))))
                #     dat_['Mileage'] = temp_mileages.tolist()

                if 'One measure' in test_temp_node:
                    sep_rows_idx = dat[dat['Node'].str.contains('Alternative measure')].index[0]
                    m_dat_1, m_dat_2 = np.split(dat, [sep_rows_idx], axis=0)
                    dat_ = {
                        'One measure':
                            m_dat_1[~m_dat_1['Node'].str.contains('One measure')],
                        'Alternative measure':
                            m_dat_2[~m_dat_2['Node'].str.contains('Alternative measure')],
                    }

                elif 'Later measure' in test_temp_node:
                    sep_rows_idx = dat[dat['Node'].str.contains('Later measure')].index[0]
                    m_dat_1, m_dat_2 = np.split(dat, [sep_rows_idx], axis=0)
                    dat_ = {
                        'Original measure': m_dat_1[~m_dat_1['Node'].str.contains('Original measure')],
                        'Later measure': m_dat_2[~m_dat_2['Node'].str.contains('Later measure')],
                    }

                elif "This line has two 'legs':" in test_temp_node:
                    dat_ = dat.iloc[1:].drop_duplicates(ignore_index=True)

                elif 'Measure sometimes used' in test_temp_node:
                    sep_rows_idx = test_temp.index.tolist() + [dat.index[-1]]
                    dat_ = {
                        dat.loc[j, 'Node']: dat.loc[j + 1:k] for j, k in loop_in_pairs(sep_rows_idx)}

                else:
                    alt_sep_rows_idx = [x in test_temp_node for x in self.measure_headers]
                    num_of_measures = sum(alt_sep_rows_idx)

                    if num_of_measures == 1:  #
                        m_name = self.measure_headers[alt_sep_rows_idx.index(True)]  # measure name
                        sep_rows_idx = dat[dat['Node'].str.contains(m_name)].index[0]
                        m_dat_1, m_dat_2 = np.split(dat, [sep_rows_idx], axis=0)

                        x = [x_ for x_ in test_temp_node if 'measure' in x_ or 'route' in x_][0]
                        if re.match(r'(Original)|(Former)|(Alternative)|(Usual)', x):
                            measure_ = re.sub(
                                r'(Original)|(Former)|(Alternative)|(Usual)', 'Current', x)
                        else:
                            measure_ = re.sub(r'(Current)|(Later)|(One)', 'Previous', x)

                        dat_ = {
                            measure_: m_dat_1.loc[0:sep_rows_idx, :],
                            test_temp_node[0]: m_dat_2.loc[sep_rows_idx + 1:, :],
                        }

                    elif num_of_measures == 2:  # e.g. elr='BTJ'
                        sep_rows_idx_items = [
                            self.measure_headers[x] for x in np.where(alt_sep_rows_idx)[0]]
                        sep_rows_idx = dat[dat['Node'].isin(sep_rows_idx_items)].index[-1]

                        m_dat_list = np.split(dat, [sep_rows_idx], axis=0)  # m_dat_1, m_dat_2
                        sep_rows_idx_items_checked = map(
                            lambda x: x[x['Node'].isin(sep_rows_idx_items)]['Node'].iloc[0],
                            m_dat_list)
                        m_dat_list_ = map(
                            lambda x: x[~x['Node'].isin(sep_rows_idx_items)],
                            m_dat_list)

                        dat_ = dict(zip(sep_rows_idx_items_checked, m_dat_list_))

                    else:
                        if dat.loc[sep_rows_idx, 'Mileage'] == '':
                            dat.loc[sep_rows_idx, 'Mileage'] = dat.loc[sep_rows_idx - 1, 'Mileage']
                        dat_ = dat

            else:
                dat_ = dat

        return dat_

    @staticmethod
    def _parse_mileage(mileage):
        """
        Parse column of mileage data.

        :param mileage: column of mileage data
        :type mileage: pandas.Series
        :return: parsed mileages
        :rtype: pandas.DataFrame
        """

        mileage.index = range(len(mileage))

        if any(mileage.str.match('.*km')):
            if all(mileage.str.match('.*km')):
                mileage_ = mileage.str.replace(r'km|\(|\)', '', regex=True).map(
                    lambda x: yard_to_mileage(kilometer_to_yard(km=x.replace('≈', ''))))

                # Warning: This might not be correct!
                miles_chains = mileage_.map(mileage_to_mile_chain)

            else:
                miles_chains = mileage.map(lambda x: re.sub(r'/?\d+\.\d+km/?', '', x))
                mileage_ = miles_chains.map(mile_chain_to_mileage)
            mileage_note = [x + ' (Approximate)' if x.startswith('≈') else x for x in list(mileage)]

        else:
            if all(mileage.map(is_str_float)):
                miles_chains = mileage
                mileage_note = [''] * len(miles_chains)

            else:
                miles_chains, mileage_note = [], []
                for m in mileage:
                    if m == '':
                        miles_chains.append(m)
                        mileage_note.append('')
                    elif m.startswith('(') and m.endswith(')'):
                        miles_chains.append(re.search(r'\d+\.\d+', m).group(0))
                        mileage_note.append('Not on this route but given for reference')
                    elif m.startswith('≈') or m.endswith('?'):
                        miles_chains.append(m.strip('≈').strip('?'))
                        mileage_note.append('Approximate')
                    elif re.match(r'\d+\.\d+/\s?\d+\.\d+', m):
                        m1, m2 = m.split('/')
                        miles_chains.append(m1)
                        mileage_note.append(m2.strip() + ' (Alternative)')
                    elif ' + ' in m or 'private portion' in m:
                        m1 = re.search(r'\d+\.\d+', m).group(0)
                        miles_chains.append(m1)
                        mileage_note.append(m.replace(m1, '').strip())
                    elif '†' in m:
                        miles_chains.append(m.replace('†', '').strip())
                        mileage_note.append("(See 'Notes')")
                    else:
                        if re.match(r'\d+,\d+', m):
                            miles_chains.append(m.strip(' ').replace(',', '.'))
                        else:
                            miles_chains.append(m.strip(' ').replace(' ', '.'))
                        mileage_note.append('')

            mileage_ = [mile_chain_to_mileage(m) for m in miles_chains]

        parsed_mileage_ = {
            'Mileage': mileage_,
            'Mileage_Note': mileage_note,
            'Miles_Chains': miles_chains,
        }
        parsed_mileage = pd.DataFrame(parsed_mileage_)

        return parsed_mileage

    @staticmethod
    def _preprocess_node_x(node_x):
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

    @staticmethod
    def _parse_prep_nodes(prep_nodes):
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
            temp_lst = [
                x.replace('later ', '').rstrip(',').split(' and ')
                for x in conn_node_lst[i] if isinstance(x, str)]

            conn_node_lst[i] = [v for lst in temp_lst for v in lst]
            temp_lst = [x.split(', ') for x in conn_node_lst[i]]
            conn_node_lst[i] = [v for lst in temp_lst for v in lst]

        most_conn = max(len(c) for c in conn_node_lst)
        # conn_node_list = [c + [None] * (most_conn - len(c)) for c in conn_node_list]

        prep_nodes_ = pd.DataFrame(
            conn_node_lst, columns=['Link_{}'.format(n + 1) for n in range(most_conn)])

        return prep_nodes_

    @staticmethod
    def _uncouple_elr_mileage(node_x):
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
                y = [z[:-1] if re.match(r'\d+.\d+\)', z) else z.strip() for z in node_x.split('(')]
                y[0] = '' if len(y[0]) > 4 else y[0]
            elif re.match(pat3, node_x):
                try:
                    y = [
                        re.search(r'[A-Z]{3}(\d)?', node_x).group(0),
                        re.search(r'\d+\.\d+', node_x).group(0)]
                except AttributeError:
                    y = [re.search(r'[A-Z]{3}(\d)?', node_x).group(0), '']
            elif re.match(pat4, node_x):
                y = [
                    re.search(r'[A-Z]{3}(\d)?', node_x).group(0),
                    mileage_to_mile_chain(yard_to_mileage(
                        kilometer_to_yard(km=re.search(r'\d+\.\d+', node_x).group(0))))]
            else:
                y = [node_x, ''] if len(node_x) <= 4 else ['', '']
            y[0] = y[0] if len(y[0]) <= 4 else ''

        return y

    def _parse_node(self, node):
        """
        Parse column of node data.

        :param node: column of node data
        :type node: pandas.Series
        :return: parsed nodes
        :rtype: pandas.DataFrame
        """

        prep_node = pd.DataFrame(
            (self._preprocess_node_x(n) for n in node), columns=['Node', 'Connection'])

        conn_nodes = self._parse_prep_nodes(prep_node)

        link_cols = [x for x in conn_nodes.columns if re.match(r'^(Link_\d)', x)]
        link_nodes = conn_nodes[link_cols].map(self._uncouple_elr_mileage)

        dat = [
            pd.DataFrame(link_nodes[col].values.tolist(), columns=[col + '_ELR', col + '_Mile_Chain'])
            for col in link_cols]
        link_elr_mileage = pd.concat(dat, axis=1, sort=False)

        parsed_node_and_conn = pd.concat([prep_node, conn_nodes, link_elr_mileage], axis=1)

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

        parsed_mileage = self._parse_mileage(mileage=mileage)
        parsed_node_and_conn = self._parse_node(node=node)

        parsed_dat = pd.concat([parsed_mileage, parsed_node_and_conn], axis=1)

        return parsed_dat

    def collect_elr_by_initial(self, initial, update=False, verbose=False):
        """
        Collect Engineer's Line References (ELRs) for a given initial letter from source web page.

        :param initial: initial letter of an ELR, e.g. ``'a'``, ``'z'``
        :type initial: str
        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console, defaults to ``True``
        :type verbose: bool or int
        :return: data of ELRs whose names start with the given initial letter and
            date of when the data was last updated
        :rtype: dict

        **Examples**::

            >>> from pyrcs.line_data import ELRMileages  # from pyrcs import ELRMileages

            >>> em = ELRMileages()

            >>> elrs_a_codes = em.collect_elr_by_initial(initial='a')
            >>> type(elrs_a_codes)
            dict
            >>> list(elrs_a_codes.keys())
            ['A', 'Last updated date']

            >>> elrs_a_codes_dat = elrs_a_codes['A']
            >>> type(elrs_a_codes_dat)
            pandas.core.frame.DataFrame
            >>> elrs_a_codes_dat.head()
               ELR  ...         Notes
            0  AAL  ...      Now NAJ3
            1  AAM  ...  Formerly AML
            2  AAV  ...
            3  ABB  ...       Now AHB
            4  ABB  ...
            [5 rows x 5 columns]

            >>> elrs_q_codes = em.collect_elr_by_initial(initial='Q')
            >>> elrs_q_codes_dat = elrs_q_codes['Q']
            >>> elrs_q_codes_dat.head()
                ELR  ...            Notes
            0   QAB  ...  Duplicates ALB?
            1   QBL  ...
            2   QDS  ...
            3   QLT  ...
            4  QLT1  ...
            [5 rows x 5 columns]
        """

        beginning_with = validate_initial(x=initial)

        path_to_pickle = self._cdd("a-z", beginning_with.lower() + ".pkl")
        if os.path.isfile(path_to_pickle) and not update:
            elrs = load_data(path_to_pickle)

        else:
            if verbose == 2:
                print(f"Collecting data of {self.KEY} beginning with '{beginning_with}'", end=" ... ")

            elrs = {beginning_with: None, self.KEY_TO_LAST_UPDATED_DATE: None}

            try:
                url = self.catalogue[beginning_with]
                # url = em.catalogue[beginning_with]
                source = requests.get(url=url, headers=fake_requests_headers())

            except Exception as e:
                if verbose == 2:
                    print("Failed.", end=" ")
                print_inst_conn_err(verbose=verbose, e=e)

            else:
                try:
                    columns, records = parse_table(source=source, parser='html.parser')
                    data = [[x.replace('=', 'See').strip('\xa0') for x in i] for i in records]

                    # Create a DataFrame of the requested table
                    elrs_codes = pd.DataFrame(data=data, columns=columns)

                    last_updated_date = get_last_updated_date(url=url, parsed=True)

                    # Update the dict with both the DataFrame and its last updated date
                    elrs = {
                        beginning_with: elrs_codes,
                        self.KEY_TO_LAST_UPDATED_DATE: last_updated_date,
                    }

                    if verbose == 2:
                        print("Done.")

                    os.makedirs(os.path.dirname(path_to_pickle), exist_ok=True)
                    save_data(elrs, path_to_pickle, verbose=verbose)

                except Exception as e:  # e.g. the requested URL is not available:
                    print(f"Failed. {format_err_msg(e)}")

        return elrs

    def fetch_elr(self, update=False, dump_dir=None, verbose=False):
        """
        Fetch data of ELRs and their associated mileages.

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param dump_dir: pathname of a directory where the data file is dumped, defaults to ``None``
        :type dump_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of all available ELRs and date of when the data was last updated
        :rtype: dict

        **Examples**::

            >>> from pyrcs.line_data import ELRMileages  # from pyrcs import ELRMileages

            >>> em = ELRMileages()

            >>> elrs_codes = em.fetch_elr()
            >>> type(elrs_codes)
            dict
            >>> list(elrs_codes.keys())
            ['ELRs and mileages', 'Last updated date']

            >>> em.KEY
            'ELRs and mileages'

            >>> elrs_codes_dat = elrs_codes[em.KEY]
            >>> type(elrs_codes_dat)
            pandas.core.frame.DataFrame
            >>> elrs_codes_dat.head()
               ELR  ...         Notes
            0  AAL  ...      Now NAJ3
            1  AAM  ...  Formerly AML
            2  AAV  ...
            3  ABB  ...       Now AHB
            4  ABB  ...
            [5 rows x 5 columns]
        """

        verbose_1 = False if (dump_dir or not verbose) else (2 if verbose == 2 else True)
        verbose_2 = verbose_1 if is_home_connectable() else False

        data = [
            self.collect_elr_by_initial(initial=x, update=update, verbose=verbose_2)
            for x in string.ascii_lowercase]

        if all(d[x] is None for d, x in zip(data, string.ascii_uppercase)):
            if update:
                print_inst_conn_err(verbose=verbose)
                print_void_msg(data_name=self.KEY, verbose=verbose)
            data = [
                self.collect_elr_by_initial(initial=x, update=False, verbose=verbose_1)
                for x in string.ascii_lowercase]

        # Select DataFrames only
        elrs_data = (item[x] for item, x in zip(data, string.ascii_uppercase))
        elrs_data_table = pd.concat(elrs_data, axis=0, ignore_index=True, sort=False)

        # Get the latest updated date
        last_updated_dates = (
            item[self.KEY_TO_LAST_UPDATED_DATE] for item, _ in zip(data, string.ascii_uppercase))
        latest_update_date = max(d for d in last_updated_dates if d is not None)

        elrs_data = {self.KEY: elrs_data_table, self.KEY_TO_LAST_UPDATED_DATE: latest_update_date}

        if dump_dir is not None:
            save_data_to_file(
                self, data=elrs_data, data_name=self.NAME, ext=".pkl", dump_dir=dump_dir,
                verbose=False)

        return elrs_data

    def _mileage_file_dump_names(self, elr):
        data_name = remove_punctuation(elr).lower()

        if data_name == "prn":
            data_name += "_"

        dump_dir = self._cdd("mileage-files", data_name[0])

        return data_name, dump_dir

    def _dump_mileage_file(self, elr, mileage_file, dump_it, verbose):
        if dump_it:
            data_name, dump_dir = self._mileage_file_dump_names(elr)

            save_data_to_file(
                self, data=mileage_file, data_name=data_name, ext=".pkl", dump_dir=dump_dir,
                verbose=verbose)

    @staticmethod
    def _get_parsed_contents(elr_dat, notes):
        val_cols = ['Line name', 'Mileages', 'Datum']
        line_name, mileages, _ = elr_dat[val_cols].values[0]

        if re.match(r'(\w ?)+ \((\w ?)+\)', line_name):
            line_name_ = re.search(r'(?<=\w \()(\w ?)+.(?=\))', line_name).group(0)

            try:
                loc_a, _, loc_b = re.split(r' (and|&|to) ', line_name_)
                line_name = re.search(r'(\w ?)+.(?= \((\w ?)+\))', line_name).group(0)
            except ValueError:
                try:
                    loc_a, _, loc_b = re.split(r' (and|&|to) ', notes)
                    line_name = line_name_
                except ValueError:
                    loc_a, loc_b = '', ''

        elif elr_dat.Mileages.values[0].startswith('0.00') and elr_dat.Datum.values[0] != '':
            loc_a = elr_dat.Datum.values[0]
            if loc_a in line_name:
                loc_b = re.split(r' (and|&|to) ', line_name)[2]
            else:
                loc_b = line_name

        elif re.match(r'(\w ?)+ to (\w ?)+', notes):
            loc_a, loc_b = notes.split(' to ')

        else:
            loc_a, loc_b = '', ''

            try:
                loc_a, _, loc_b = re.split(r' (and|&|to|-) ', notes)
            except (ValueError, TypeError):
                pass

            try:
                loc_a, _, loc_b = re.split(r' (and|&|to|-) ', line_name)
            except (ValueError, TypeError):
                pass

            if line_name:
                loc_a, loc_b = line_name, line_name

        # if re.match(r'.*( Branch| Curve)$', loc_b):
        #     loc_b = re.sub(r' Branch| Curve', '', loc_b)
        # else:
        #     loc_b = loc_b

        miles_chains = mileages.split(' - ')
        locations = [loc_a, loc_b]
        parsed_content = [[m, l] for m, l in zip(miles_chains, locations)]

        return line_name, parsed_content

    def collect_mileage_file(self, elr, parsed=True, confirmation_required=True, dump_it=False,
                             verbose=False):
        """
        Collect mileage file for the given ELR from source web page.

        :param elr: ELR, e.g. ``'CJD'``, ``'MLA'``, ``'FED'``
        :type elr: str
        :param parsed: whether to parse the scraped mileage data
        :type parsed: bool
        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param dump_it: whether to save the collected data as a pickle file, defaults to ``False``
        :type dump_it: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
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

            >>> from pyrcs.line_data import ELRMileages  # from pyrcs import ELRMileages

            >>> em = ELRMileages()

            >>> gam_mileage_file = em.collect_mileage_file(elr='GAM')
            To collect mileage file of "GAM"
            ? [No]|Yes: yes
            >>> type(gam_mileage_file)
            dict
            >>> list(gam_mileage_file.keys())
            ['ELR', 'Line', 'Sub-Line', 'Mileage', 'Notes']
            >>> gam_mileage_file['Mileage']
               Mileage Mileage_Note Miles_Chains  ... Link_1 Link_1_ELR Link_1_Mile_Chain
            0   8.1518                      8.69  ...   None
            1  10.0264                     10.12  ...   None
            [2 rows x 8 columns]

            >>> xrc2_mileage_file = em.collect_mileage_file(elr='XRC2')
            To collect mileage file of "XRC2"
            ? [No]|Yes: yes
            >>> xrc2_mileage_file['Mileage']
              Mileage Mileage_Note  ... Link_1_ELR Link_1_Mile_Chain
            0  9.0158     14.629km  ...
            1  9.0447     14.893km  ...
            2  9.0557     14.994km  ...
            [3 rows x 8 columns]

            >>> xre_mileage_file = em.collect_mileage_file(elr='XRE')
            To collect mileage file of "XRE"
            ? [No]|Yes: yes
            >>> xre_mileage_file['Mileage']
              Mileage Mileage_Note  ... Link_2_ELR Link_2_Mile_Chain
            0  7.0073     11.333km  ...
            1  7.0174     11.425km  ...
            2  9.0158     14.629km  ...
            3  9.0198     14.666km  ...
            4  9.0389     14.840km  ...
            5  9.0439   (14.886)km  ...
            6  9.0540   (14.978)km  ...
            [7 rows x 11 columns]

            >>> mor_mileage_file = em.collect_mileage_file(elr='MOR')
            To collect mileage file of "MOR"
            ? [No]|Yes: yes
            >>> type(mor_mileage_file['Mileage'])
            dict
            >>> list(mor_mileage_file['Mileage'].keys())
            ['Original measure', 'Later measure']
            >>> mor_mileage_file['Mileage']['Original measure']
              Mileage Mileage_Note Miles_Chains  ...        Link_1 Link_1_ELR Link_1_Mile_Chain
            0  0.0000                      0.00  ...  SWA (215.18)        SWA            215.18
            1  0.0792                      0.36  ...          None
            2  0.1716                      0.78  ...          None
            3  1.1166                      1.53  ...          None
            4  2.0066                      2.03  ...          None
            5  2.0836                      2.38  ...          None
            6                                    ...          None
            7  3.0462                      3.21  ...   SDI2 (2.79)       SDI2              2.79
            [8 rows x 8 columns]
            >>> mor_mileage_file['Mileage']['Later measure']
              Mileage Mileage_Note Miles_Chains  ...        Link_1 Link_1_ELR Link_1_Mile_Chain
            0  0.0000                      0.00  ...  SWA (215.26)        SWA            215.26
            1  0.0176                      0.08  ...  SWA (215.18)        SWA            215.18
            2  0.0968                      0.44  ...          None
            3  1.0132                      1.06  ...          None
            4  1.1342                      1.61  ...          None
            5  2.0242                      2.11  ...          None
            6  2.1012                      2.46  ...          None
            7                                    ...          None
            8  3.0638                      3.29  ...   SDI2 (2.79)       SDI2              2.79
            [9 rows x 8 columns]

            >>> fed_mileage_file = em.collect_mileage_file(elr='FED')
            To collect mileage file of "FED"
            ? [No]|Yes: yes
            >>> type(fed_mileage_file['Mileage'])
            dict
            >>> list(fed_mileage_file['Mileage'].keys())
            ['Current route', 'Original route']
            >>> fed_mileage_file['Mileage']['Current route']
               Mileage Mileage_Note  ... Link_1_ELR Link_1_Mile_Chain
            0  83.1254               ...        FEL
            1  84.0198               ...
            2  84.1430               ...
            3  84.1540               ...
            4  85.0484               ...
            5  85.1122               ...
            6  85.1188               ...        TFN              2.13
            [7 rows x 8 columns]
            >>> fed_mileage_file['Mileage']['Original route']
              Mileage Mileage_Note Miles_Chains  ...       Link_1 Link_1_ELR Link_1_Mile_Chain
            0  0.0000                      0.00  ...  FEL (84.22)        FEL             84.22
            1  1.0176                      1.08  ...         None
            2  1.1540                      1.70  ...         None
            3  1.1694                      1.77  ...         None
            [4 rows x 8 columns]
        """

        elr_ = remove_punctuation(elr).upper()

        if elr_ != '':

            mileage_file = None

            if confirmed(f"To collect mileage file of \"{elr_}\"\n?", confirmation_required):

                if verbose == 2:
                    print(f"Collecting mileage file of \"{elr_}\"", end=" ... ")

                try:
                    url = home_page_url() + f'/elrs/_mileages/{elr_[0]}/{elr_}.shtm'.lower()
                    source = requests.get(url=url, headers=fake_requests_headers())

                except Exception as e:
                    if verbose == 2:
                        print("Failed.", end=" ")
                    print_inst_conn_err(verbose=verbose, e=e)

                else:
                    try:
                        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

                        line_name = soup.find(name='h3').text

                        sub_line_name_ = soup.find(name='h4')
                        if sub_line_name_ is not None:
                            sub_line_name = sub_line_name_.get_text()
                        else:
                            sub_line_name = ''

                        err404 = {'"404" error: page not found', '404 error: page not found'}
                        if any(x in err404 for x in {line_name, sub_line_name}):
                            elr_data = self.collect_elr_by_initial(elr_[0])[elr_[0]]
                            elr_data = elr_data[elr_data['ELR'] == elr_]

                            notes_dat = elr_data['Notes'].iloc[0]
                            if re.match(r'(Now( part of)? |= |See )[A-Z]{3}(\d)?$', notes_dat):
                                elr_alt = re.search(r'(?<= )[A-Z]{3}(\d)?', notes_dat).group(0)
                                mileage_file_alt = self.collect_mileage_file(
                                    elr=elr_alt, parsed=parsed, confirmation_required=False,
                                    dump_it=False, verbose=verbose)

                                if notes_dat.startswith('Now'):
                                    mileage_file_former = copy.copy(mileage_file_alt)

                                    mileage_file_alt.update({'Formerly': elr_})
                                    self._dump_mileage_file(
                                        elr_alt, mileage_file_alt, dump_it=dump_it, verbose=verbose)

                                    mileage_file_former.update(({'Now': elr_alt}))
                                    self._dump_mileage_file(
                                        elr_, mileage_file_former, dump_it=dump_it, verbose=verbose)

                                return mileage_file_alt

                            else:
                                line_name, content = self._get_parsed_contents(elr_data, notes_dat)

                        else:
                            ln_temp = line_name.split('\t')
                            line_name = ln_temp[0] if len(ln_temp) == 1 else ln_temp[1]

                            content = [
                                x.strip().split('\t', 1) for x in soup.find('pre').text.splitlines()
                                if x != '']
                            content = [
                                [y.replace('  ', ' ').replace('\t', ' ') for y in x] for x in content]
                            content = [
                                [''] + x if (len(x) == 1) & ('Note that' not in x[0]) else x
                                for x in content]

                        # assert sub_headers[0] == elr
                        if sub_line_name and (sub_line_name not in err404):
                            sub_ln_temp = sub_line_name.split('\t')
                            sub_headers = sub_ln_temp[0] if len(sub_ln_temp) == 1 else sub_ln_temp[1]
                        else:
                            sub_headers = ''

                        # Make a dict of line information
                        line_info = {'ELR': elr_, 'Line': line_name, 'Sub-Line': sub_headers}

                        # Search for notes
                        notes_dat = []
                        parsed_content = content.copy()
                        # measure_headers = []
                        measure_headers_indices = []

                        for _, x in enumerate(content):
                            if len(x) == 1:
                                if x[0].endswith(tuple(string.ascii_letters)):
                                    x_ = x[0] + '.'
                                else:
                                    x_ = x[0]
                                notes_dat.append(x_)
                                parsed_content.remove(x)
                            else:
                                mil_dat, txt_dat = x
                                if mil_dat == '':
                                    if txt_dat in self.measure_headers or any(
                                            mh in txt_dat for mh in self.measure_headers):
                                        # measure_headers.append(txt_dat)
                                        measure_headers_indices.append(parsed_content.index(x))
                                    elif 'Revised distances are thus:' in txt_dat:
                                        txt_dat = 'Current measure'
                                        j = parsed_content.index(x)
                                        parsed_content[j] = [mil_dat, txt_dat]
                                        # measure_headers.append(txt_dat)
                                        measure_headers_indices.append(j)
                                    elif 'Later (post-preservation measure)' in txt_dat:
                                        txt_dat = 'Later measure (post-preservation measure)'
                                        j = parsed_content.index(x)
                                        parsed_content[j] = [mil_dat, txt_dat]
                                        measure_headers_indices.append(j)
                                    elif 'Distances in km' in txt_dat or \
                                            'measured from accurate mapping systems' in txt_dat or \
                                            len(txt_dat) >= 25:
                                        notes_dat.append(txt_dat)
                                        parsed_content.remove(x)
                                    elif re.search(r'\b[Mm]easure\b', txt_dat):
                                        # measure_headers.append(txt_dat)
                                        measure_headers_indices.append(parsed_content.index(x))

                        if any('Distances in km' in x for x in notes_dat):
                            parsed_content = [
                                [x[0] + 'km', x[1]] if not x[0].endswith('km') else x
                                for x in parsed_content]

                        # Make a dict of note
                        notes_data = {'Notes': ' '.join(notes_dat).strip()}

                        # Create a table of the mileage data
                        mileage_data = pd.DataFrame(parsed_content, columns=['Mileage', 'Node'])

                        # If there are multiple measures in 'mileage_data',
                        # e.g. current/former measures
                        mileage_data = self._split_measures(
                            mileage_data=mileage_data, measure_headers_indices=measure_headers_indices)

                        if parsed:
                            if isinstance(mileage_data, dict) and len(mileage_data) > 1:
                                mileage_data = {
                                    h: self._parse_mileage_data(mileage_data=dat)
                                    for h, dat in mileage_data.items()}
                            else:  # isinstance(dat, pd.DataFrame)
                                mileage_data = self._parse_mileage_data(mileage_data=mileage_data)

                        mileage_file = dict(
                            pair for x in [line_info, {'Mileage': mileage_data}, notes_data]
                            for pair in x.items())

                        if verbose == 2:
                            print("Done.")

                        self._dump_mileage_file(
                            elr=elr_, mileage_file=mileage_file, dump_it=dump_it, verbose=verbose)

                    except Exception as e:
                        print(f"Failed. {format_err_msg(e)}")

            return mileage_file

    def fetch_mileage_file(self, elr, update=False, dump_dir=None, verbose=False):
        """
        Fetch the mileage file for a given ELR.

        :param elr: elr: ELR, e.g. ``'CJD'``, ``'MLA'``, ``'FED'``
        :type elr: str
        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param dump_dir: pathname of a directory where the data file is dumped, defaults to ``None``
        :type dump_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: mileage file (codes), line name and, if any, additional information/notes
        :rtype: dict

        **Examples**::

            >>> from pyrcs.line_data import ELRMileages  # from pyrcs import ELRMileages

            >>> em = ELRMileages()

            >>> # Get the mileage file of 'AAL' (Now 'NAJ3')
            >>> aal_mileage_file = em.fetch_mileage_file(elr='AAL')
            >>> type(aal_mileage_file)
            dict
            >>> list(aal_mileage_file.keys())
            ['ELR', 'Line', 'Sub-Line', 'Mileage', 'Notes', 'Formerly']
            >>> aal_mileage_file['ELR']
            'NAJ3'
            >>> aal_mileage_file['Notes']
            'Note that Ashendon Junction up line junction is on NAJ2'
            >>> aal_mileage_file['Mileage']
                Mileage Mileage_Note  ... Link_1_ELR Link_1_Mile_Chain
            0    0.0000               ...       NAJ2             33.69
            1    0.0594               ...        GUA            164.75
            2    1.0396               ...
            3    3.0682               ...
            4    6.0704               ...
            5    8.0572               ...        BSG              0.00
            6    8.0990               ...        WEJ
            7    9.0594               ...
            8   13.0264               ...
            9   17.0858               ...
            10  17.0968               ...
            11  18.0572               ...        DCL             81.10
            12  18.0638               ...        DCL             81.12
            [13 rows x 8 columns]

            >>> # Get the mileage file of 'MLA'
            >>> mla_mileage_file = em.fetch_mileage_file(elr='MLA')
            >>> type(mla_mileage_file)
            dict
            >>> list(mla_mileage_file.keys())
            ['ELR', 'Line', 'Sub-Line', 'Mileage', 'Notes']
            >>> mla_mileage_file_mileages = mla_mileage_file['Mileage']
            >>> type(mla_mileage_file_mileages)
            dict
            >>> list(mla_mileage_file_mileages.keys())
            ['Current measure', 'Original measure']
            >>> mla_mileage_file_mileages['Original measure']
              Mileage Mileage_Note  ... Link_3_ELR Link_3_Mile_Chain
            0  4.1386               ...       NEM4              0.00
            1  5.0616               ...
            2  5.1122               ...
            [3 rows x 14 columns]
            >>> mla_mileage_file_mileages['Current measure']
              Mileage Mileage_Note Miles_Chains  ...       Link_1 Link_1_ELR Link_1_Mile_Chain
            0  0.0000                      0.00  ...  MRL2 (4.44)       MRL2              4.44
            1  0.0572                      0.26  ...         None
            2  0.1540                      0.70  ...         None
            3  0.1606                      0.73  ...         None
            [4 rows x 8 columns]

            >>> # Get the mileage file of 'LCG'
            >>> mla_mileage_file = em.fetch_mileage_file(elr='LCG')

        """

        try:
            elr_ = remove_punctuation(elr)
            data_name, _ = self._mileage_file_dump_names(elr_)
            ext = ".pkl"
            path_to_pickle = self._cdd("mileage-files", data_name[0], data_name + ext, mkdir=False)

            if os.path.isfile(path_to_pickle) and not update:
                mileage_file = load_data(path_to_pickle)

            else:
                verbose_ = collect_in_fetch_verbose(data_dir=dump_dir, verbose=verbose)
                mileage_file = self.collect_mileage_file(
                    elr=elr_, parsed=True, confirmation_required=False, dump_it=True, verbose=verbose_)

            if dump_dir is not None:
                save_data_to_file(
                    cls=self, data=mileage_file, data_name=data_name, ext=ext, dump_dir=dump_dir,
                    verbose=verbose)

        except Exception as e:
            if verbose:
                print("Some errors occurred when fetching the data. {}".format(e))
            mileage_file = None

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
        :return: connection (<end mileage of the start ELR>, <start mileage of the end ELR>)
        :rtype: tuple

        **Examples**::

            >>> from pyrcs.line_data import ELRMileages  # from pyrcs import ELRMileages

            >>> em = ELRMileages()

            >>> elr_1 = 'AAM'
            >>> mileage_file_1 = em.collect_mileage_file(elr_1, confirmation_required=False)
            >>> mf_1_mileages = mileage_file_1['Mileage']
            >>> mf_1_mileages.head()
              Mileage Mileage_Note  ... Link_2_ELR Link_2_Mile_Chain
            0  0.0000               ...
            1  0.0154               ...
            2  0.0396               ...
            3  1.1012               ...
            4  1.1408               ...
            [5 rows x 11 columns]

            >>> elr_2 = 'ANZ'
            >>> mileage_file_2 = em.collect_mileage_file(elr_2, confirmation_required=False)
            >>> mf_2_mileages = mileage_file_2['Mileage']
            >>> mf_2_mileages.head()
               Mileage Mileage_Note Miles_Chains  ...      Link_1 Link_1_ELR Link_1_Mile_Chain
            0  84.0924                     84.42  ...         BEA        BEA
            1  84.1364                     84.62  ...  AAM (0.18)        AAM              0.18
            [2 rows x 8 columns]

            >>> elr_1_dest, elr_2_orig = em.search_conn(elr_1, mf_1_mileages, elr_2, mf_2_mileages)
            >>> elr_1_dest
            '0.0396'
            >>> elr_2_orig
            '84.1364'
        """

        start_mask = start_em.apply(lambda x: x.str.contains(end_elr, case=False).any(), axis=1)
        start_temp = start_em[start_mask]
        assert isinstance(start_temp, pd.DataFrame)

        if not start_temp.empty:
            # Get exact location
            key_idx = start_temp.index[0]
            mile_chain_col = [x for x in start_temp.columns if re.match(r'.*_Mile_Chain', x)][0]

            start_dest_mileage = start_em.loc[key_idx, 'Mileage']  # Mileage of the Start ELR
            end_orig_mile_chain = start_temp.loc[key_idx, mile_chain_col]  # Mileage of the End ELR

            if end_orig_mile_chain and end_orig_mile_chain != 'Unknown':
                end_orig_mileage = mile_chain_to_mileage(end_orig_mile_chain)

            else:  # end_conn_mile_chain == '':
                end_mask = end_em.apply(lambda x: x.str.contains(start_elr, case=False).any(), axis=1)
                end_temp = end_em[end_mask]

                if not end_temp.empty:
                    end_orig_mileage = end_temp['Mileage'].iloc[0]
                else:
                    end_orig_mileage = start_dest_mileage

        else:
            start_dest_mileage, end_orig_mileage = '', ''

        return start_dest_mileage, end_orig_mileage

    @staticmethod
    def _select_measure(em_dat, key_pat):
        if isinstance(em_dat, dict):
            em_ks = [k for k in em_dat.keys() if re.match(key_pat, k)]
            if not em_ks:
                em_dat_ = em_dat[list(em_dat.keys())[0]]
            else:
                em_dat_ = em_dat[em_ks[0]]

        else:
            em_dat_ = em_dat

        return em_dat_

    def get_conn_mileages(self, start_elr, end_elr, update=False, **kwargs):
        """
        Get a connection point between two ELR-and-mileage pairs.

        Namely, find the end and start mileages for the start and end ELRs, respectively.

        .. note::

            This function may not be able to find the connection for every pair of ELRs.
            See :ref:`Example 2<get_conn_mileages-example-2>` below.

        :param start_elr: start ELR
        :type start_elr: str
        :param end_elr: end ELR
        :type end_elr: str
        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param kwargs: [optional] parameters of the method
            :py:meth:`ELRMileages.fetch_mileage_file()
            <pyrcs.line_data.elr_mileage.ELRMileages.fetch_mileage_file>`
        :return: connection ELR and mileages between the given ``start_elr`` and ``end_elr``
        :rtype: tuple

        **Example 1**::

            >>> from pyrcs.line_data import ELRMileages  # from pyrcs import ELRMileages

            >>> em = ELRMileages()

            >>> conn = em.get_conn_mileages(start_elr='NAY', end_elr='LTN2')
            >>> (s_dest_mlg, c_elr, c_orig_mlg, c_dest_mlg, e_orig_mlg) = conn

            >>> s_dest_mlg
            '5.1606'
            >>> c_elr
            'NOL'
            >>> c_orig_mlg
            '5.1606'
            >>> c_dest_mlg
            '0.0638'
            >>> e_orig_mlg
            '123.1320'

        .. _get_conn_mileages-example-2:

        **Example 2**::

            >>> from pyrcs.line_data import ELRMileages  # from pyrcs import ELRMileages

            >>> em = ELRMileages()

            >>> conn = em.get_conn_mileages(start_elr='MAC3', end_elr='DBP1', dump_dir="tests")
            >>> conn
            ('', '', '', '', '')
        """

        kwargs.update({'update': update})

        start_file, end_file = map(
            functools.partial(self.fetch_mileage_file, **kwargs), [start_elr, end_elr])

        if start_file is not None and end_file is not None:
            start_elr, end_elr = start_file['ELR'], end_file['ELR']
            start_em, end_em = start_file['Mileage'], end_file['Mileage']
            key_pat = re.compile(r'(Current\s)|(One\s)|(Later\s)|(Usual\s)|(Measure used by\s)')

            start_em = self._select_measure(start_em, key_pat)
            end_em = self._select_measure(end_em, key_pat)

            start_dest_mileage, end_orig_mileage = self.search_conn(
                start_elr=start_elr, start_em=start_em, end_elr=end_elr, end_em=end_em)

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
                        # print(i, j)
                        conn_elr = conn_temp.iloc[j]
                        conn_em = self.fetch_mileage_file(elr=conn_elr, update=update)
                        if conn_em is not None:
                            conn_elr, conn_em = conn_em['ELR'], conn_em['Mileage']
                            if isinstance(conn_em, dict):
                                conn_em = self._select_measure(conn_em, key_pat)

                            start_dest_mileage, conn_orig_mileage = self.search_conn(
                                start_elr, start_em, conn_elr, conn_em)

                            conn_dest_mileage, end_orig_mileage = self.search_conn(
                                conn_elr, conn_em, end_elr, end_em)

                            if conn_dest_mileage and end_orig_mileage:
                                if not start_dest_mileage:
                                    start_dest_mileage = start_em[
                                        start_em[link_col] == conn_elr]['Mileage'].values[0]
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
                    # else:
                    i += 1

            if conn_orig_mileage and not conn_elr:
                start_dest_mileage, conn_orig_mileage = '', ''

        else:
            start_dest_mileage, conn_elr, conn_orig_mileage, conn_dest_mileage, end_orig_mileage = \
                [''] * 5

        return start_dest_mileage, conn_elr, conn_orig_mileage, conn_dest_mileage, end_orig_mileage
