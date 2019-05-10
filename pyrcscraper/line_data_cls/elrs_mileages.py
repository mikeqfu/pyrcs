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

from pyrcscraper.utils import cdd, load_pickle, save_pickle
from pyrcscraper.utils import get_cls_catalogue, get_last_updated_date, is_float, miles_chains_to_mileage, parse_table


class ELRMileages:
    def __init__(self):
        self.Name = 'ELRs and mileages'
        self.URL = 'http://www.railwaycodes.org.uk/elrs/elr0.shtm'
        self.Catalogue = get_cls_catalogue(self.URL)
        self.Date = get_last_updated_date(self.URL, parsed=True, date_type=False)

    # Change directory to "Line data\\ELRs and mileages"
    @staticmethod
    def cdd_elr_mileage(*sub_dir):
        path = cdd("Line data", "ELRs and mileages")
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    # Parse mileage data
    @staticmethod
    def parse_mileage(mileage):
        """
        :param mileage: Mileage column
        :return:
        """
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
                elif m.startswith('~'):
                    temp_mileage.append(m.strip('~'))
                    mileage_note.append('Approximate')
                else:
                    if isinstance(m, str):
                        temp_mileage.append(m.strip(' '))
                    else:
                        temp_mileage.append(m)
                    mileage_note.append('')

        temp_mileage = [miles_chains_to_mileage(m) for m in temp_mileage]

        parsed_mileage = pd.DataFrame({'Mileage': temp_mileage, 'Mileage_Note': mileage_note})

        return parsed_mileage

    # Parse node and its connecting node
    @staticmethod
    def parse_node_and_connection(node):
        """
        :param node:
        :return:
        """

        def preprocess_node(node_x):
            if re.match(r'\w+.*( \(\d+\.\d+\))?(/| and )\w+ with[ A-Z0-9]( \(\d+\.\d+\))?', node_x):
                init_conn_info = [match.group() for match in re.finditer(r' with \w+( \(\d+\.\d+\))?', node_x)]
                if '/' in node_x:
                    node_info = [y.replace(conn_inf, '') for y, conn_inf in zip(node_x.split('/'), init_conn_info)]
                else:
                    node_info = [y.replace(conn_inf, '') for y, conn_inf in zip(node_x.split(' and '), init_conn_info)]
                conn_info = [conn_inf.replace(' with ', '') for conn_inf in init_conn_info]
                return '/'.join(node_info) + ' with ' + ' and '.join(conn_info)
            else:
                return node_x

        parsed_node_info = [preprocess_node(n) for n in node]

        temp_node = pd.DataFrame([n.replace(' with Freightliner terminal', ' & Freightliner Terminal').
                                 replace(' with curve to', ' with').
                                 replace(' (0.37 long)', '').split(' with ')
                                  for n in parsed_node_info], columns=['Node', 'Connection'])
        conn_node_list = []
        x = 2  # x-th occurrence
        for c in temp_node.Connection:
            if c is not None:
                c_node = c.split(' and ')
                if len(c_node) > 2:
                    c_node = [' and '.join(c_node[:x]), ' and '.join(c_node[x:])]
            else:
                c_node = [c]
            conn_node_list.append(c_node)

        if all(len(c) == 1 for c in conn_node_list):
            conn_node = pd.DataFrame([c + [None] for c in conn_node_list], columns=['Connection1', 'Connection2'])
        else:
            assert isinstance(conn_node_list, list)
            for i in [conn_node_list.index(c) for c in conn_node_list if len(c) > 1]:
                conn_node_list[i] = [v for lst in [x.rstrip(',').lstrip('later ').split(' and ')
                                                   for x in conn_node_list[i]] for v in lst]
                conn_node_list[i] = [v for lst in [x.split(', ') for x in conn_node_list[i]] for v in lst]

            no_conn = max(len(c) for c in conn_node_list)
            conn_node_list = [c + [None] * (no_conn - len(c)) for c in conn_node_list]
            conn_node = pd.DataFrame(conn_node_list, columns=['Connection' + str(n + 1) for n in range(no_conn)])

        return temp_node.loc[:, ['Node']].join(conn_node)

    #
    @staticmethod
    def parse_mileage_node_and_connection(dat):
        """
        :param dat:
        :return:
        """
        mileage, node = dat.iloc[:, 0], dat.iloc[:, 1]
        parsed_mileage = parse_mileage(mileage)
        parsed_node_and_connection = parse_node_and_connection(node)
        parsed_dat = parsed_mileage.join(parsed_node_and_connection)
        return parsed_dat

    #
    @staticmethod
    def parse_mileage_file(mileage_file, elr):
        """
        :param mileage_file:
        :param elr:
        :return:
        """
        dat = mileage_file[elr]
        if isinstance(dat, dict) and len(dat) > 1:
            dat = {h: parse_mileage_node_and_connection(d) for h, d in dat.items()}
        else:  # isinstance(dat, pd.DataFrame)
            dat = parse_mileage_node_and_connection(dat)
        mileage_file[elr] = dat
        return mileage_file

    # ================================================================================================================
    """ ELRs and mileages data """

    # Scrape Engineer's Line References (ELRs)
    def collect_elrs(self, keyword, update=False):
        """
        :param keyword: [str] usually an initial letter of ELR, e.g. 'a', 'b'
        :param update: [bool] indicate whether to re-scrape the data from online
        :return: [dict] {'ELRs_mileages_keyword': [DataFrame] data of ELRs whose names start with the given 'keyword',
                                                    including ELR names, line name, mileages, datum and some notes,
                         'Last_updated_date_keyword': [str] date of when the data was last updated}
        """
        pickle_filename = keyword.title() + ".pickle"
        path_to_pickle = self.cdd_elr_mileage("A-Z", pickle_filename)
        if os.path.isfile(path_to_pickle) and not update:
            elrs = load_pickle(path_to_pickle)
        else:
            # Specify the requested URL
            elr_keys = [s + keyword.title() for s in ('ELRs_mileages_', 'Last_updated_date_')]
            url = 'http://www.railwaycodes.org.uk/elrs/elr{}.shtm'.format(keyword.lower())
            try:
                last_updated_date = get_last_updated_date(url)
                source = requests.get(url)  # Request to get connected to the url
                records, header = parse_table(source, parser='lxml')
                # Create a DataFrame of the requested table
                data = pd.DataFrame([[x.replace('=', 'See').strip('\xa0') for x in i] for i in records], columns=header)
                # Return a dictionary containing both the DataFrame and its last updated date
                elrs = dict(zip(elr_keys, [data, last_updated_date]))
            except Exception as e:  # e.g the requested URL is not available:
                print("Failed to scrape data of ELR starting with \"{}\" due to \"{}\".".format(keyword.upper(), e))
                elrs = dict(zip(elr_keys, [pd.DataFrame(), None]))
            save_pickle(elrs, path_to_pickle)
        return elrs


    # Get all ELRs and mileages
    def fetch_elrs(update=False):
        """
        :param update: [bool]
        :return [dict] {'ELRs_mileages': [DataFrame] data of (almost all) ELRs whose names start with the given 'keyword',
                                            including ELR names, line name, mileages, datum and some notes,
                        'Last_updated_date': [str] date of when the data was last updated}
        """
        pickle_filename = "ELRs.pickle"
        path_to_pickle = cdd_elr_mileage(pickle_filename)
        if os.path.isfile(path_to_pickle) and not update:
            elrs_data = load_pickle(path_to_pickle)
        else:
            try:
                data = [collect_elrs(i, update) for i in string.ascii_lowercase]
                # Select DataFrames only
                elrs_data = (item['ELRs_mileages_{}'.format(x)] for item, x in zip(data, string.ascii_uppercase))
                elrs_data_table = pd.concat(elrs_data, axis=0, ignore_index=True, sort=False)

                # Get the latest updated date
                last_updated_dates = (d['Last_updated_date_{}'.format(x)] for d, x in zip(data, string.ascii_uppercase))
                last_updated_date = max(d for d in last_updated_dates if d is not None)

                elrs_data = {'ELRs_mileages': elrs_data_table, 'Last_updated_date': last_updated_date}

            except Exception as e:
                print("Failed to get \"ELRs\" data due to \"{}\".".format(e))
                elrs_data = {'ELRs_mileages': pd.DataFrame(), 'Last_updated_date': None}

            save_pickle(elrs_data, path_to_pickle)

        return elrs_data


    # Read (from online) the mileage file for the given ELR
    def collect_mileage_file(elr, update=False):
        """
        :param elr:
        :param update:
        :return:

        Note:
            - In some cases, mileages are unknown hence left blank, e.g. ANI2, Orton Junction with ROB (~3.05)
            - Mileages in parentheses are not on that ELR, but are included for reference,
              e.g. ANL, (8.67) NORTHOLT [London Underground]
            - As with the main ELR list, mileages preceded by a tilde (~) are approximate.

        """
        pickle_filename = elr + ".pickle"
        path_to_pickle = cdd_elr_mileage("mileage_files", elr[0].title(), pickle_filename)

        if os.path.isfile(path_to_pickle) and not update:
            mileage_file = load_pickle(path_to_pickle)
        else:
            url = 'http://www.railwaycodes.org.uk/elrs'
            # The URL of the mileage file for the ELR
            mileage_file_url = '/'.join([url, '_mileages', elr[0].lower(), elr.lower() + '.shtm'])

            try:
                source = requests.get(mileage_file_url)
                source_text = bs4.BeautifulSoup(source.text, 'lxml')

                parsed_headers = source_text.find('h3').text.split('\t')
                assert parsed_headers[0] == elr

                parsed_content = source_text.find('pre').text.splitlines()
                parsed_content = [x.strip().split('\t') for x in parsed_content if x != '']
                parsed_content = [[''] + x if len(x) == 1 and 'Note that' not in x[0] else x for x in parsed_content]

                note = {'Note': min(parsed_content, key=len)[0]}
                parsed_content.remove(min(parsed_content, key=len))

                mileage_data = pd.DataFrame(parsed_content, columns=['Mileage', 'Node'])

                # check_idx = mileage_data.Mileage.map(is_float)
                # to_check = mileage_data[~check_idx]
                # if to_check.empty:
                #     dat = {elr: mileage_data[check_idx]}
                #     note = {'Note': None}
                # else:
                #     if len(to_check) == 1:
                #         note = {'Note': to_check[elr].iloc[0]}
                #         dat = {elr: mileage_data[check_idx]}
                #         dat[elr].index = range(len(dat[elr]))
                #     else:
                #         idx = to_check.index.get_values()
                #         diff = list(pd.np.diff(idx)) + [len(mileage_data) - pd.np.diff(idx)[-1]]
                #         sliced_dat = {mileage_data[elr][i]: mileage_data[i + 1:i + d] for i, d in zip(idx, diff)}
                #         if len(idx) == 2:
                #             note = {'Note': None}
                #         else:
                #             note = {'Note': k for k, v in sliced_dat.items() if v.empty}
                #             del sliced_dat[note['Note']]
                #         for _, dat in sliced_dat.items():
                #             dat.index = range(len(dat))
                #         dat = {elr: sliced_dat}

                line_name = {'Line': parsed_headers[1]}
                mileage_file = dict(pair for d in [mileage_data, line_name, note] for pair in d.items())
                mileage_file = parse_mileage_file(mileage_file, elr)

                save_pickle(mileage_file, path_to_pickle)

            except Exception as e:
                print("Scraping the mileage file for '{}' ... failed due to '{}'.".format(elr, e))
                mileage_file = None

        return mileage_file


    # Get the mileage file for the given ELR (firstly try to load the local data file if available)
    def fetch_mileage_file(elr, update=False):
        """
        :param elr: [str]
        :param update: [bool] indicate whether to re-scrape the data from online
        :return: [dict] {elr: [DataFrame] mileage file data,
                        'Line': [str] line name,
                        'Note': [str] additional information/notes, or None}
        """
        path_to_file = cdd_elr_mileage("mileage_files", elr[0].title(), elr + ".pickle")

        file_exists = os.path.isfile(path_to_file)
        mileage_file = load_pickle(path_to_file) if file_exists and not update else collect_mileage_file(elr)

        return mileage_file


    # Get to end and start mileages for StartELR and EndELR, respectively, for the connection point
    def get_conn_end_start_mileages(start_elr, end_elr, update=False):
        """
        :param start_elr:
        :param end_elr:
        :param update:
        :return:
        """
        start_elr_mileage_file = fetch_mileage_file(start_elr, update)[start_elr]
        if isinstance(start_elr_mileage_file, dict):
            for k in start_elr_mileage_file.keys():
                if re.match('^Usual|^New', k):
                    start_elr_mileage_file = start_elr_mileage_file[k]

        start_conn_cols = [c for c in start_elr_mileage_file.columns if re.match('^Connection', c)]

        start_conn_mileage, end_conn_mileage = None, None

        for start_conn_col in start_conn_cols:
            start_conn = start_elr_mileage_file[start_conn_col].dropna()
            for i in start_conn.index:
                if end_elr in start_conn[i]:
                    start_conn_mileage = start_elr_mileage_file.Mileage.loc[i]
                    if re.match(r'\w+(?= \(\d+\.\d+\))', start_conn[i]):
                        end_conn_mileage = miles_chains_to_mileage(re.search(r'(?<=\w \()\d+\.\d+', start_conn[i]).group())
                        break
                    elif end_elr == start_conn[i]:

                        end_elr_mileage_file = fetch_mileage_file(end_elr, update)[end_elr]
                        if isinstance(end_elr_mileage_file, dict):
                            for k in end_elr_mileage_file.keys():
                                if re.match('^Usual|^New', k):
                                    end_elr_mileage_file = end_elr_mileage_file[k]

                        end_conn_cols = [c for c in end_elr_mileage_file.columns if re.match('^Connection', c)]
                        for end_conn_col in end_conn_cols:
                            end_conn = end_elr_mileage_file[end_conn_col].dropna()
                            for j in end_conn.index:
                                if start_elr in end_conn[j]:
                                    end_conn_mileage = end_elr_mileage_file.Mileage.loc[j]
                                    break
                            if start_conn_mileage is not None and end_conn_mileage is not None:
                                break
                        if start_conn_mileage is not None and end_conn_mileage is not None:
                            break

                else:
                    try:
                        link_elr = re.search(r'\w+(?= \(\d+\.\d+\))', start_conn[i]).group()
                    except AttributeError:
                        link_elr = start_conn[i]

                    if re.match('[A-Z]{3}(0-9)?$', link_elr):
                        try:
                            link_elr_mileage_file = fetch_mileage_file(link_elr, update)[link_elr]

                            if isinstance(link_elr_mileage_file, dict):
                                for k in link_elr_mileage_file.keys():
                                    if re.match('^Usual|^New', k):
                                        link_elr_mileage_file = link_elr_mileage_file[k]

                            link_conn_cols = [c for c in link_elr_mileage_file.columns if re.match('^Connection', c)]
                            for link_conn_col in link_conn_cols:
                                link_conn = link_elr_mileage_file[link_conn_col].dropna()
                                for l in link_conn.index:
                                    if start_elr in link_conn[l]:
                                        start_conn_mileage = link_elr_mileage_file.Mileage.loc[l]
                                        break
                                for l in link_conn.index:
                                    if end_elr in link_conn[l]:
                                        if re.match(r'\w+(?= \(\d+\.\d+\))', link_conn[l]):
                                            end_conn_mileage = miles_chains_to_mileage(
                                                re.search(r'(?<=\w \()\d+\.\d+', link_conn[l]).group())
                                        elif end_elr == link_conn[l]:
                                            end_conn_mileage = link_elr_mileage_file.Mileage.loc[l]
                                        break
                                if start_conn_mileage is not None and end_conn_mileage is not None:
                                    break
                        except (TypeError, AttributeError):
                            pass
                    else:
                        pass

                if start_conn_mileage is not None and end_conn_mileage is not None:
                    break
            if start_conn_mileage is not None and end_conn_mileage is not None:
                break

        if start_conn_mileage is None or end_conn_mileage is None:
            start_conn_mileage, end_conn_mileage = None, None

        return start_conn_mileage, end_conn_mileage
