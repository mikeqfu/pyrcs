"""
Collect `railway station data <http://www.railwaycodes.org.uk/stations/station0.shtm>`_.
"""

import copy
import itertools
import os
import re
import string
import urllib.parse

import bs4
import numpy as np
import pandas as pd
import requests
from pyhelpers.dir import cd, validate_input_data_dir
from pyhelpers.ops import fake_requests_headers
from pyhelpers.store import load_pickle, save_pickle, save_json, load_json

from pyrcs.utils import cd_dat, get_catalogue, get_last_updated_date, homepage_url, \
    parse_location_name, parse_table, is_internet_connected, print_conn_err, print_connection_error


class Stations:
    """
    A class for collecting railway station data.

    :param data_dir: name of data directory, defaults to ``None``
    :type data_dir: str, None
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

    :ivar str StnKey: key of the dict-type data of railway stations
    :ivar str StnPickle: name of the pickle file of railway station data
    :ivar str BilingualKey: key of the dict-type data of bilingual names
    :ivar str SpStnNameSignKey: key of the dict-type data of sponsored station name signs
    :ivar str NSFOKey: key of the dict-type data of stations not served by SFO
    :ivar str IntlKey: key of the dict-type data of UK international railway stations
    :ivar str TriviaKey: key of the dict-type data of UK railway station trivia
    :ivar str ARKey: key of the dict-type data of UK railway station access rights
    :ivar str BarrierErrKey: key of the dict-type data of railway station barrier error codes

    **Example**::

        >>> from pyrcs.other_assets import Stations

        >>> stn = Stations()

        >>> print(stn.Name)
        Railway station data

        >>> print(stn.SourceURL)
        http://www.railwaycodes.org.uk/stations/station0.shtm
    """

    def __init__(self, data_dir=None, verbose=True):
        """
        Constructor method.
        """
        if not is_internet_connected():
            print_connection_error(verbose=verbose)

        self.Name = 'Railway station data'
        self.Key = 'Stations'

        self.HomeURL = homepage_url()
        self.SourceURL = urllib.parse.urljoin(self.HomeURL, '/stations/station0.shtm')

        self.LUDKey = 'Last updated date'  # key to last updated date
        self.LUD = get_last_updated_date(url=self.SourceURL, parsed=True, as_date_type=False)

        self.StnKey = 'Railway station data'
        self.StnPickle = self.StnKey.lower().replace(" ", "-")

        self.BilingualKey = 'Bilingual names'
        self.SpStnNameSignKey = 'Sponsored signs'
        self.NSFOKey = 'Not served by SFO'
        self.IntlKey = 'International'
        self.TriviaKey = 'Trivia'
        self.ARKey = 'Access rights'
        self.BarrierErrKey = 'Barrier error codes'

        if data_dir:
            self.DataDir = validate_input_data_dir(data_dir)
        else:
            self.DataDir = cd_dat("other-assets", self.Name.lower())
        self.CurrentDataDir = copy.copy(self.DataDir)

    def _cdd_stn(self, *sub_dir, **kwargs):
        """
        Change directory to package data directory and sub-directories (and/or a file).

        The directory for this module: ``"\\dat\\other-assets\\stations"``.

        :param sub_dir: sub-directory or sub-directories (and/or a file)
        :type sub_dir: str
        :param kwargs: optional parameters of `os.makedirs`_, e.g. ``mode=0o777``
        :return: path to the backup data directory for ``Stations``
        :rtype: str

        .. _`os.makedirs`: https://docs.python.org/3/library/os.html#os.makedirs

        :meta private:
        """

        path = cd(self.DataDir, *sub_dir, mkdir=True, **kwargs)

        return path

    def get_station_data_catalogue(self, update=False, verbose=False):
        """
        Get catalogue of railway station data.

        :param update: whether to check on update and proceed to update the package data,
            defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console as the function runs,
            defaults to ``False``
        :type verbose: bool or int
        :return: catalogue of railway station data
        :rtype: dict

        **Example**::

            >>> from pyrcs.other_assets import Stations

            >>> stn = Stations()

            >>> # stn_data_cat = stn.get_station_data_catalogue(update=True, verbose=True)
            >>> stn_data_cat = stn.get_station_data_catalogue()

            >>> type(stn_data_cat)
            dict
            >>> list(stn_data_cat.keys())
            ['Railway station data',
             'Sponsored signs',
             'International',
             'Trivia',
             'Access rights',
             'Barrier error codes']
        """

        cat_json = '-'.join(x for x in urllib.parse.urlparse(self.SourceURL).path.replace(
            '.shtm', '.json').split('/') if x)
        path_to_cat = cd_dat("catalogue", cat_json)

        if os.path.isfile(path_to_cat) and not update:
            catalogue = load_json(path_to_cat)

        else:
            if verbose == 2:
                print("Collecting a catalogue of {} data".format(self.StnKey.lower()),
                      end=" ... ")

            try:
                source = requests.get(self.SourceURL, headers=fake_requests_headers())
            except requests.exceptions.ConnectionError:
                print("Failed.") if verbose == 2 else ""
                print_conn_err(update=update, verbose=verbose)
                catalogue = load_json(path_to_cat)

            else:
                try:
                    soup = bs4.BeautifulSoup(source.text, 'lxml')

                    cold_soup = soup.find_all('nav')[1]

                    hot_soup = {a.text: urllib.parse.urljoin(self.SourceURL, a.get('href'))
                                for a in cold_soup.find_all('a')}

                    catalogue = {self.StnKey: None}
                    for k, v in hot_soup.items():
                        sub_cat = get_catalogue(v, update=True, confirmation_required=False,
                                                json_it=False)
                        if sub_cat != hot_soup:
                            if k == 'Introduction':
                                catalogue.update({self.StnKey: {k: v, **sub_cat}})
                            else:
                                catalogue.update({k: sub_cat})
                        else:
                            if k in ('Bilingual names', 'Not served by SFO'):
                                catalogue[self.StnKey].update({k: v})
                            else:
                                catalogue.update({k: v})

                    print("Done.") if verbose == 2 else ""

                    save_json(catalogue, path_to_cat, verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(e))
                    catalogue = None

        return catalogue

    @staticmethod
    def _parse_owner_and_operator(x):
        """
        Parse 'Operator' column
        """

        x_ = x.strip().replace('\'', '').replace('([, ', '').replace('])', '').replace('\xa0', '')

        # parsed_txt_ = re.split(r'\\r| \[\'|\\\\r| {2}\']|\', \'|\\n', x_)
        # parsed_text = [y for y in parsed_txt_ if remove_punctuation(y) != '']

        cname_pat = re.compile(r'(?=[A-Z]).*(?= from \d+ \w+ [0-9]{4})')
        cdate_pat = re.compile(r'(?<= from )\d+ \w+ [0-9]{4}')
        pdate_pat = re.compile(r'from\s\d+\s\w+\s[0-9]{4} to \d+ \w+ [0-9]{4}')

        try:
            current_op, past_op = [y.rstrip(', ').strip(',').strip() for y in x_.split('\\r')]
        except ValueError:
            try:
                current_op, past_op = [y.rstrip(', ').strip(',').strip() for y in x_.split('\r')]
            except ValueError:
                current_op, past_op = x_, None

        # Current operator
        current_name = re.search(cname_pat, current_op)
        if current_name and current_op != '':
            current_name = current_name.group(0)
        else:
            current_name = current_op
        current_from = re.search(cdate_pat, current_op)
        if current_from:
            current_from = current_from.group(0)

        current_operator = [(current_name, current_from)]

        if past_op:
            # Past operators
            past_dates = re.findall(pdate_pat, past_op)
            past_names = [y.strip().lstrip('([') for y in re.split(pdate_pat, past_op) if y.strip()]

            past_operators = [(n, d) for n, d in zip(past_names, past_dates)]

            # for z in parsed_text:
            #     # Operators names
            #     operator_name = re.search(r'.*(?= from \d+ \w+ \d+(.*)?)', z)
            #     operator_name = operator_name.group() if operator_name is not None else ''
            #     # Start dates
            #     start_date = re.search(r'(?<= from )\d+ \w+ \d+( to \d+ \w+ \d+(.*))?', z)
            #     start_date = start_date.group() if start_date is not None else ''
            #     # Form a tuple
            #     operators.append((operator_name, start_date))

        else:
            past_operators = []

        operators = current_operator + past_operators

        return operators

    def extended_info(self, info_dat, name):
        """
        Get extended information of the owners/operators.

        :param info_dat: raw data of owners/operators
        :type info_dat: pandas.Series
        :param name: original column name of the owners/operators data
        :type name: str
        :return: extended information of the owners/operators
        :rtype: pandas.DataFrame
        """

        temp = list(info_dat.map(self._parse_owner_and_operator))
        length = len(max(temp, key=len))
        col_names_current = [name, name + '_since']
        prev_no = list(
            itertools.chain.from_iterable(itertools.repeat(x, 2) for x in list(range(1, length))))
        col_names_ = zip(col_names_current * (length - 1), prev_no)
        col_names = col_names_current + ['_'.join(['Prev', x, str(d)]).replace('_since', '_Period')
                                         for x, d in col_names_]

        for i in range(len(temp)):
            if len(temp[i]) < length:
                temp[i] += [(None, None)] * (length - len(temp[i]))

        temp2 = pd.DataFrame(temp)
        extended_info = [temp2[c].apply(pd.Series) for c in temp2.columns]
        extended_info = pd.concat(extended_info, axis=1, sort=False)
        extended_info.columns = col_names

        return extended_info

    @staticmethod
    def _parse_degrees(x):
        if x == '':
            z = np.nan
        else:
            z = float(x.replace('c.', '') if x.startswith('c.') else x)
        return z

    def collect_station_data_by_initial(self, initial, update=False, verbose=False):
        """
        Collect `railway station data <http://www.railwaycodes.org.uk/stations/station0.shtm>`_
        for the given ``initial`` letter.

        :param initial: initial letter of station data
            (including the station name, ELR, mileage, status, owner, operator,
            degrees of longitude and latitude, and grid reference) for specifying URL
        :type initial: str
        :param update: whether to check on update and proceed to update the package data,
            defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console as the function runs,
            defaults to ``False``
        :type verbose: bool, int
        :return: railway station data for the given ``initial`` letter and
            date of when the data was last updated
        :rtype: dict

        **Example**::

            >>> from pyrcs.other_assets import Stations

            >>> stn = Stations()

            >>> # sa = stn.collect_station_data_by_initial('a', update=True, verbose=True)
            >>> sa = stn.collect_station_data_by_initial(initial='a')

            >>> type(sa)
            dict
            >>> list(sa.keys())
            ['A', 'Last updated date']

            >>> print(sa['A'].head())
                       Station   ELR  ... Prev_Operator_6 Prev_Operator_Period_6
            0       Abbey Wood   NKL  ...            None                   None
            1       Abbey Wood  XRS3  ...            None                   None
            2             Aber   CAR  ...            None                   None
            3  Abercynon North   ABD  ...            None                   None
            4                    ABD  ...            None                   None
            [5 rows x 28 columns]
        """

        path_to_pickle = self._cdd_stn("a-z", initial.lower() + ".pickle")

        beginning_with = initial.upper()

        if os.path.isfile(path_to_pickle) and not update:
            railway_station_data = load_pickle(path_to_pickle)

        else:
            url = self.SourceURL.replace('station0', 'station{}'.format(initial.lower()))

            railway_station_data = {beginning_with: None, self.LUDKey: None}

            if verbose == 2:
                print("Collecting data of {} beginning with \"{}\"".format(
                    self.StnKey.lower(), beginning_with), end=" ... ")

            stn_data_catalogue = self.get_station_data_catalogue()

            if beginning_with not in list(stn_data_catalogue[self.StnKey].keys()):
                if verbose == 2:
                    print("No data is available.")
                    # print("No data is available for signal box codes "
                    #       "beginning with \"{}\".".format(beginning_with))
                # railway_station_table, last_updated_date = None, None
                pass

            else:
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
                        col = [re.sub(r'\n?\r+\n?', ' ', h) for h in header]
                        stn_dat = pd.DataFrame(dat, columns=col)

                        temp_degree = stn_dat['Degrees Longitude'].str.split(' ')
                        temp_degree_len = temp_degree.map(len).sum()
                        temp_elr = stn_dat['ELR'].map(
                            lambda x: x.split(' ') if not re.match('^[Ss]ee ', x) else [x])
                        temp_elr_len = temp_elr.map(len).sum()
                        if max(temp_degree_len, temp_elr_len) > len(stn_dat):
                            temp_col = ['ELR', 'Degrees Longitude', 'Degrees Latitude',
                                        'Grid Reference']
                            idx = [j for j in stn_dat.index
                                   if max(len(temp_degree[j]), len(temp_elr[j])) > 1]

                            temp_vals = []

                            for i in idx:
                                t = max(len(temp_degree[i]), len(temp_elr[i]))
                                temp_val = []
                                for c in col:
                                    x_ = stn_dat.loc[i, c]
                                    if c in temp_col:
                                        y = x_.split(' ')
                                        if len(y) == 1:
                                            y = y * t
                                        temp_val.append(y)
                                    elif c == 'Mileage':
                                        y = re.findall(r'\d+m \d+ch|\d+\.\d+km|\w+', x_)
                                        if len(y) > t:
                                            y = re.findall(r'\d+m \d+ch', x_)
                                        temp_val.append(y)
                                    else:
                                        temp_val.append([x_] * t)

                                temp_vals.append(
                                    pd.DataFrame(np.array(temp_val, dtype=object).T, columns=col))

                            stn_dat.drop(idx, axis='index', inplace=True)
                            stn_dat = pd.concat(
                                [stn_dat] + temp_vals, axis=0, ignore_index=True)

                            stn_dat.sort_values(['Station'], inplace=True)

                            stn_dat.index = range(len(stn_dat))

                        degrees_col = ['Degrees Longitude', 'Degrees Latitude']
                        stn_dat[degrees_col] = stn_dat[degrees_col].applymap(self._parse_degrees)
                        stn_dat['Grid Reference'] = stn_dat['Grid Reference'].map(
                            lambda x: x.replace('c.', '') if x.startswith('c.') else x)

                        stn_dat[['Station', 'Station_Note']] = stn_dat.Station.map(
                            parse_location_name).apply(pd.Series)

                        # Owner
                        owners = self.extended_info(stn_dat.Owner, name='Owner')

                        stn_dat.drop('Owner', axis=1, inplace=True)
                        stn_dat = stn_dat.join(owners)

                        # Operator
                        # temp = list(stn_dat.Operator.map(self._parse_owner_and_operator))
                        # length = len(max(temp, key=len))
                        # col_names_current = ['Operator', 'Date']
                        # prev_no = list(itertools.chain.from_iterable(
                        #     itertools.repeat(x, 2) for x in list(range(1, length))))
                        # col_names = zip(col_names_current * (length - 1), prev_no)
                        # col_names = col_names_current + [
                        #     '_'.join(['Prev', x, str(d)]) for x, d in col_names]
                        #
                        # for i in range(len(temp)):
                        #     if len(temp[i]) < length:
                        #         temp[i] += [(None, None)] * (length - len(temp[i]))
                        #
                        # temp2 = pd.DataFrame(temp)
                        # operators = [temp2[c].apply(pd.Series) for c in temp2.columns]
                        # operators = pd.concat(operators, axis=1, sort=False)
                        # operators.columns = col_names

                        operators = self.extended_info(stn_dat.Operator, name='Operator')

                        stn_dat.drop('Operator', axis=1, inplace=True)
                        stn_dat = stn_dat.join(operators)

                        last_updated_date = get_last_updated_date(url)

                        railway_station_data.update({beginning_with: stn_dat,
                                                     self.LUDKey: last_updated_date})

                        print("Done.") if verbose == 2 else ""

                        save_pickle(railway_station_data, path_to_pickle, verbose=verbose)

                    except Exception as e:
                        print("Failed. {}".format(e))

        return railway_station_data

    def fetch_station_data(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch `railway station data <http://www.railwaycodes.org.uk/stations/station0.shtm>`_
        from local backup.

        :param update: whether to check on update and proceed to update the package data,
            defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data with newly collected data,
            defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str, None
        :param verbose: whether to print relevant information in console as the function runs,
            defaults to ``False``
        :type verbose: bool, int
        :return: railway station data
            (including the station name, ELR, mileage, status, owner, operator,
            degrees of longitude and latitude, and grid reference) and
            date of when the data was last updated
        :rtype: dict

        **Example**::

            >>> from pyrcs.other_assets import Stations

            >>> stn = Stations()

            >>> # rail_stn_data = stn.fetch_station_data(update=True, verbose=True)
            >>> rail_stn_data = stn.fetch_station_data()

            >>> type(rail_stn_data)
            dict
            >>> list(rail_stn_data.keys())
            ['Railway station data', 'Last updated date']

            >>> rail_stn_dat = rail_stn_data['Railway station data']

            >>> type(rail_stn_dat)
            pandas.core.frame.DataFrame
            >>> print(rail_stn_dat.head())
                     Station   ELR  ... Prev_Operator_6 Prev_Operator_Period_6
            2606              MRL1  ...            None                   None
            723                TAT  ...            None                   None
            89                 ABD  ...            None                   None
            90                 CAM  ...            None                   None
            85    Abbey Wood   NKL  ...            None                   None
            [5 rows x 32 columns]
        """

        verbose_ = False if (data_dir or not verbose) else (2 if verbose == 2 else True)

        data_sets = [
            self.collect_station_data_by_initial(
                x, update=update, verbose=verbose_ if is_internet_connected() else False)
            for x in string.ascii_lowercase]

        if all(d[x] is None for d, x in zip(data_sets, string.ascii_uppercase)):
            if update:
                print_conn_err(verbose=verbose)
                print("No data of the {} has been freshly collected.".format(self.StnKey.lower()))
            data_sets = [self.collect_station_data_by_initial(x, update=False, verbose=verbose_)
                         for x in string.ascii_lowercase]

        stn_dat_tbl_ = (item[x] for item, x in zip(data_sets, string.ascii_uppercase))
        stn_dat_tbl = sorted([x for x in stn_dat_tbl_ if x is not None], key=lambda x: x.shape[1],
                             reverse=True)
        stn_data = pd.concat(stn_dat_tbl, axis=0, ignore_index=True, sort=False)

        stn_data = stn_data.where(pd.notna(stn_data), None)
        stn_data.sort_values(['Station'], inplace=True)

        last_updated_dates = (d[self.LUDKey] for d in data_sets)
        latest_update_date = max(d for d in last_updated_dates if d is not None)

        railway_station_data = {self.StnKey: stn_data, self.LUDKey: latest_update_date}

        if pickle_it and data_dir:
            self.CurrentDataDir = validate_input_data_dir(data_dir)
            path_to_pickle = os.path.join(self.CurrentDataDir, self.StnPickle + ".pickle")
            save_pickle(railway_station_data, path_to_pickle, verbose=verbose)

        return railway_station_data
