"""
Collect `railway station data <http://www.railwaycodes.org.uk/stations/station0.shtm>`_.
"""

import itertools
import string
import urllib.parse

from pyhelpers.dir import cd
from pyhelpers.store import load_pickle

from pyrcs.utils import *
from pyrcs.utils import _cd_dat


class Stations:
    """
    A class for collecting railway station data.
    """

    #: Name of the data
    NAME = 'Railway station data'
    #: Key of the `dict <https://docs.python.org/3/library/stdtypes.html#dict>`_-type data
    KEY = 'Stations'

    #: URL of the main web page of the data
    URL = urllib.parse.urljoin(home_page_url(), '/stations/station0.shtm')

    #: Key of the data of the last updated date
    KEY_TO_LAST_UPDATED_DATE = 'Last updated date'

    def __init__(self, data_dir=None, verbose=True):
        """
        :param data_dir: name of data directory, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``True``
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

        :ivar str StnKey: key of the dict-type data of railway station locations
        :ivar str StnPickle: name of the pickle file of railway station locations
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

            >>> print(stn.NAME)
            Railway station data

            >>> print(stn.URL)
            http://www.railwaycodes.org.uk/stations/station0.shtm
        """

        print_connection_error(verbose=verbose)

        self.last_updated_date = get_last_updated_date(url=self.URL, parsed=True, as_date_type=False)

        self.StnKey = 'Mileages, operators and grid coordinates'

        self.BilingualKey = 'Bilingual names'
        self.SpStnNameSignKey = 'Sponsored signs'
        self.NSFOKey = 'Not served by SFO'
        self.IntlKey = 'International'
        self.TriviaKey = 'Trivia'
        self.ARKey = 'Access rights'
        self.BarrierErrKey = 'Barrier error codes'

        self.data_dir, self.current_data_dir = init_data_dir(self, data_dir, category="other-assets")

    def _cdd_stn(self, *sub_dir, **kwargs):
        """
        Change directory to package data directory and subdirectories (and/or a file).

        The directory for this module: ``"dat\\other-assets\\stations"``.

        :param sub_dir: subdirectory or subdirectories (and/or a file)
        :type sub_dir: str
        :param kwargs: optional parameters of `os.makedirs`_, e.g. ``mode=0o777``
        :return: path to the backup data directory for ``Stations``
        :rtype: str

        .. _`os.makedirs`: https://docs.python.org/3/library/os.html#os.makedirs

        :meta private:
        """

        path = cd(self.data_dir, *sub_dir, mkdir=True, **kwargs)

        return path

    def get_station_data_catalogue(self, update=False, verbose=False):
        """
        Get catalogue of railway station data.

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: catalogue of railway station data
        :rtype: dict

        **Example**::

            >>> from pyrcs.other_assets import Stations

            >>> stn = Stations()

            >>> # stn_data_cat = stn.get_station_data_catalogue(update=True, verbose=True)
            >>> stn_data_cat = stn.get_station_data_catalogue()

            >>> type(stn_data_cat)
            collections.OrderedDict
            >>> list(stn_data_cat.keys())
            ['Mileages, operators and grid coordinates',
             'Bilingual names',
             'Sponsored signs',
             'Not served by SFO',
             'International',
             'Trivia',
             'Access rights',
             'Barrier error codes',
             'London Underground']
        """

        cat_json = '-'.join(x for x in urllib.parse.urlparse(self.URL).path.replace(
            '.shtm', '.pickle').split('/') if x)
        path_to_cat = _cd_dat("catalogue", cat_json)

        if os.path.isfile(path_to_cat) and not update:
            catalogue = load_pickle(path_to_cat)

        else:
            if verbose == 2:
                print("Collecting a catalogue of {}".format(self.StnKey.lower()), end=" ... ")

            try:
                source = requests.get(self.URL, headers=fake_requests_headers())
            except requests.exceptions.ConnectionError:
                print("Failed.") if verbose == 2 else ""
                print_conn_err(update=update, verbose=verbose)
                catalogue = load_json(path_to_cat)

            else:
                try:
                    soup = bs4.BeautifulSoup(source.text, 'html.parser')

                    cold_soup = soup.find_all('nav')[1]

                    hot_soup = {a.text: urllib.parse.urljoin(self.URL, a.get('href'))
                                for a in cold_soup.find_all('a')}

                    catalogue = collections.OrderedDict()
                    for k, v in hot_soup.items():
                        sub_cat = get_catalogue(v, update=True, confirmation_required=False,
                                                json_it=False)
                        if sub_cat != hot_soup:
                            if k in sub_cat.keys():
                                sub_cat.pop(k)
                            elif 'Introduction' in sub_cat.keys():
                                sub_cat.pop('Introduction')
                            if v in sub_cat.values():
                                catalogue[k] = sub_cat
                            else:
                                catalogue[k] = {'Introduction': v, **sub_cat}
                        else:
                            catalogue.update({k: v})

                    print("Done.") if verbose == 2 else ""

                    save_pickle(catalogue, path_to_cat, verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(e))
                    catalogue = None

        return catalogue

    @staticmethod
    def _parse_degrees(x):
        if x == '':
            y = np.nan
        else:
            y = float(re.sub(r'(c\.)|≈', '', x))
        return y

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
            op_lst = [y.rstrip(', ').strip(',').strip() for y in re.split(r'\(\[|\r|\\r', x_)]
            op_lst = [p for p in op_lst if p]
            if len(op_lst) >= 2:
                current_op, past_op = op_lst[0], op_lst[1:]
            else:
                current_op, past_op = op_lst[0], ''
        except ValueError:
            try:
                current_op, past_op = x_.split('\\r, ')[0], x_.split('\\r, ')[1:]
            except ValueError:
                current_op, past_op = x_, ''

        def get_current_name_date(nd):
            n = re.search(cname_pat, nd)
            if n and nd != '':
                n = n.group(0)
            else:
                n = nd
            d_from = re.search(cdate_pat, nd)
            if d_from:
                d_from = d_from.group(0)
            return [(n, d_from)]

        def get_past_name_date(nd):
            dft = re.findall(pdate_pat, nd)
            ns = [
                y.strip().lstrip('([') for y in re.split(pdate_pat, nd) if y.strip()]
            if not dft:
                dft = [''] * len(ns)
            return [(n, d) for n, d in zip(ns, dft)]

        # Current operator
        current_operator = get_current_name_date(current_op)

        if past_op:
            # Past operators
            if isinstance(past_op, str):
                past_op = [past_op]

            past_operators = [get_past_name_date(x) for x in past_op]

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

    def _extended_info(self, info_dat, name):
        """
        Get extended information of the owners/operators.

        :param info_dat: raw data of owners/operators
        :type info_dat: pandas.Series
        :param name: original column name of the owners/operators data
        :type name: str
        :return: extended information of the owners/operators
        :rtype: pandas.DataFrame
        """

        temp = list(
            info_dat.map(lambda x: self._parse_owner_and_operator(x) if x else [('', '')]))

        temp_lst = []
        for item in temp:
            sub_lst = []
            for sub_item in item:
                if isinstance(sub_item, list):
                    sub_item = sub_item[0]
                sub_lst.append(sub_item)
            temp_lst.append(sub_lst)

        length = len(max(temp_lst, key=len))
        col_names_current = [name, name + '_since']
        prev_no = list(
            itertools.chain.from_iterable(itertools.repeat(x, 2) for x in range(1, length)))
        col_names_ = zip(col_names_current * (length - 1), prev_no)
        col_names = col_names_current + [
            '_'.join(['Prev', x, str(d)]).replace('_since', '_Period') for x, d in col_names_]

        for i in range(len(temp_lst)):
            if len(temp_lst[i]) < length:
                temp_lst[i] += [('', '')] * (length - len(temp_lst[i]))

        temp_lst_ = [list(itertools.chain.from_iterable(x)) for x in temp_lst]
        extended_info = pd.DataFrame(temp_lst_)
        # _extended_info = [temp2[c].apply(pd.Series) for c in temp2.columns]
        # _extended_info = pd.concat(_extended_info, axis=1, sort=False)
        extended_info.columns = col_names

        extended_info.fillna('', inplace=True)

        return extended_info

    def collect_station_data_by_initial(self, initial, update=False, verbose=False):
        """
        Collect `data of railway station locations
        <http://www.railwaycodes.org.uk/stations/station0.shtm>`_ for the given ``initial`` letter.

        :param initial: initial letter of locations of the railway station data
        :type initial: str
        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of railway station locations beginning with ``initial`` and
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

            >>> sa['A'].head()
                  Station   ELR  ... Prev_Operator_6 Prev_Operator_Period_6
            0  Abbey Wood   NKL  ...
            1  Abbey Wood  XRS3  ...
            2        Aber   CAR  ...
            3   Abercynon   CAM  ...
            4   Abercynon   ABD  ...
            [5 rows x 28 columns]
        """

        path_to_pickle = self._cdd_stn("a-z", initial.lower() + ".pickle")

        beginning_with = initial.upper()

        if os.path.isfile(path_to_pickle) and not update:
            railway_station_data = load_pickle(path_to_pickle)

        else:
            railway_station_data = {beginning_with: None, self.KEY_TO_LAST_UPDATED_DATE: None}

            if verbose == 2:
                print("Collecting {} of stations (beginning with \"{}\")".format(
                    self.StnKey.lower(), beginning_with), end=" ... ")

            stn_data_catalogue = self.get_station_data_catalogue()
            stn_data_initials = list(stn_data_catalogue[self.StnKey].keys())

            if beginning_with not in stn_data_initials:
                if verbose:
                    print(f"No data is available for the stations beginning with \"{beginning_with}\".")

            else:
                url = self.URL.replace('station0', 'station{}'.format(initial.lower()))

                try:
                    source = requests.get(url=url, headers=fake_requests_headers())
                except requests.exceptions.ConnectionError:
                    print("Failed.") if verbose == 2 else ""
                    print_conn_err(verbose=verbose)

                else:
                    try:
                        records, header = parse_table(source=source, parser='html.parser')

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
                            temp_col = [
                                'ELR',
                                'Degrees Longitude',
                                'Degrees Latitude',
                                'Grid Reference',
                            ]

                            idx = [
                                j for j in stn_dat.index
                                if max(len(temp_degree[j]), len(temp_elr[j])) > 1
                            ]

                            temp_vals = []

                            for i in idx:
                                t = max(len(temp_degree[i]), len(temp_elr[i]))
                                temp_val = []
                                for c in col:
                                    x_ = stn_dat.loc[i, c]
                                    if c == 'Status':
                                        if 'Operator confusion\r' in x_:
                                            y_ = re.search(r'\[(.*?)]', x_).group(1)
                                            y_ = ['Operator confusion: ' + re.sub(' +', ' ', y_)]
                                        else:
                                            y_ = [x_]
                                        y_ *= t
                                    elif c == 'Mileage':
                                        y_ = re.findall(r'\d+m \d+ch|\d+\.\d+km|\w+', x_)
                                        if len(y_) > t:
                                            y_ = re.findall(r'\d+m \d+ch|unknown', x_)
                                    elif c in temp_col:
                                        x_ = re.sub(r' \(\[\'|\', \'|\']\)', ' ', x_)
                                        if '\r' in x_ or '\\r' in x_:
                                            x_ = re.sub(r'\r|\\r', ',', x_).strip().split(',')
                                            y_ = [z.strip() for z in x_]
                                        else:
                                            y_ = x_.strip().split(' ')
                                        if len(y_) == 1:
                                            y_ *= t
                                    else:
                                        y_ = [x_] * t
                                    temp_val.append(y_)

                                temp_vals.append(
                                    pd.DataFrame(np.array(temp_val, dtype=object).T, columns=col))

                            stn_dat.drop(idx, axis='index', inplace=True)
                            stn_dat = pd.concat([stn_dat] + temp_vals, axis=0, ignore_index=True)

                            stn_dat.sort_values(['Station'], inplace=True)

                            stn_dat.index = range(len(stn_dat))

                        degrees_col = ['Degrees Longitude', 'Degrees Latitude']
                        stn_dat[degrees_col] = stn_dat[degrees_col].applymap(self._parse_degrees)
                        stn_dat['Grid Reference'] = stn_dat['Grid Reference'].map(
                            lambda x: x.replace('c.', '') if x.startswith('c.') else x)

                        stn_dat[['Station', 'Station_Note']] = stn_dat.Station.map(
                            parse_location_name).apply(pd.Series)

                        # Owners
                        owners = self._extended_info(stn_dat.Owner, name='Owner')

                        stn_dat.drop('Owner', axis=1, inplace=True)
                        stn_dat = stn_dat.join(owners)

                        # Operators
                        operators = self._extended_info(stn_dat.Operator, name='Operator')

                        stn_dat.drop('Operator', axis=1, inplace=True)
                        stn_dat = stn_dat.join(operators)

                        last_updated_date = get_last_updated_date(url=url, parsed=True)

                        railway_stn_dat = {
                            beginning_with: stn_dat,
                            self.KEY_TO_LAST_UPDATED_DATE: last_updated_date,
                        }

                        railway_station_data.update(railway_stn_dat)

                        if verbose == 2:
                            print("Done.")

                        save_pickle(railway_station_data, path_to_pickle=path_to_pickle, verbose=verbose)

                    except Exception as e:
                        print("Failed. {}".format(e))

        return railway_station_data

    def fetch_station_data(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch `data of railway station locations
        <http://www.railwaycodes.org.uk/stations/station0.shtm>`_
        (incl. mileages, operators and grid coordinates) from local backup.

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param pickle_it: whether to save the data as a pickle file, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of a folder where the pickle file is to be saved, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of railway station locations and date of when the data was last updated
        :rtype: dict

        **Example**::

            >>> from pyrcs.other_assets import Stations

            >>> stn = Stations()

            >>> # rail_stn_data = stn.fetch_station_data(update=True, verbose=True)
            >>> rail_stn_data = stn.fetch_station_data()

            >>> type(rail_stn_data)
            dict
            >>> list(rail_stn_data.keys())
            ['Mileages, operators and grid coordinates', 'Last updated date']

            >>> rail_stn_dat = rail_stn_data[stn.StnKey]

            >>> type(rail_stn_dat)
            pandas.core.frame.DataFrame
            >>> rail_stn_dat.head()
                  Station   ELR  ... Prev_Operator_6 Prev_Operator_Period_6
            0  Abbey Wood  XRS3  ...
            1  Abbey Wood   NKL  ...
            2        Aber   CAR  ...
            3   Abercynon   ABD  ...
            4   Abercynon   CAM  ...
            [5 rows x 30 columns]
        """

        verbose_1 = collect_in_fetch_verbose(data_dir=data_dir, verbose=verbose)
        verbose_2 = verbose_1 if is_internet_connected() else False

        data_sets = [
            self.collect_station_data_by_initial(
                initial=x, update=update, verbose=verbose_2)
            for x in string.ascii_lowercase]

        if all(d[x] is None for d, x in zip(data_sets, string.ascii_uppercase)):
            if update:
                print_conn_err(verbose=verbose)
                print_void_msg(data_name=self.StnKey, verbose=verbose)

            data_sets = [
                self.collect_station_data_by_initial(x, update=False, verbose=verbose_1)
                for x in string.ascii_lowercase
            ]

        stn_dat_tbl_ = (item[x] for item, x in zip(data_sets, string.ascii_uppercase))
        stn_dat_tbl = sorted(
            [x for x in stn_dat_tbl_ if x is not None], key=lambda x: x.shape[1], reverse=True)
        stn_data = pd.concat(stn_dat_tbl, axis=0, ignore_index=True, sort=False)

        stn_data = stn_data.where(pd.notna(stn_data), None)
        stn_data.sort_values(['Station'], inplace=True)

        stn_data.index = range(len(stn_data))

        last_updated_dates = (d[self.KEY_TO_LAST_UPDATED_DATE] for d in data_sets)
        latest_update_date = max(d for d in last_updated_dates if d is not None)

        railway_station_data = {
            self.StnKey: stn_data,
            self.KEY_TO_LAST_UPDATED_DATE: latest_update_date,
        }

        data_to_pickle(
            self, data=railway_station_data, data_name=self.StnKey,
            pickle_it=pickle_it, data_dir=data_dir, verbose=verbose)

        return railway_station_data
