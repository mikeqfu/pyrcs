"""
Collect `depots codes <http://www.railwaycodes.org.uk/depots/depots0.shtm>`_.
"""

import urllib.error
import urllib.parse

from pyhelpers.dir import cd

from pyrcs.utils import *


class Depots:
    """
    A class for collecting depot codes.
    """

    NAME = 'Depot codes'
    KEY = 'Depots'

    URL = urllib.parse.urljoin(home_page_url(), '/depots/depots0.shtm')

    KEY_TO_LAST_UPDATED_DATE = 'Last updated date'  # key to last updated date

    def __init__(self, data_dir=None, update=False, verbose=True):
        """
        :param data_dir: name of data directory, defaults to ``None``
        :type data_dir: str or None
        :param update: whether to do an update check (for the catagloue data), defaults to ``False``
        :type update: bool
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

        :ivar str TCTKey: key of the dict-type data of two character TOPS codes
        :ivar str TCTPickle: name of the pickle file of two character TOPS codes
        :ivar str FDPTKey: key of the dict-type data of four digit pre-TOPS codes
        :ivar str FDPTPickle: name of the pickle file of four digit pre-TOPS codes
        :ivar str S1950Key: key of the dict-type data of 1950 system (pre-TOPS) codes
        :ivar str S1950Pickle: name of the pickle file of 1950 system (pre-TOPS) codes
        :ivar str GWRKey: key of the dict-type data of GWR codes
        :ivar str GWRPickle: name of the pickle file of GWR codes

        **Example**::

            >>> from pyrcs.other_assets import Depots

            >>> depots = Depots()

            >>> print(depots.NAME)
            Depot codes

            >>> print(depots.URL)
            http://www.railwaycodes.org.uk/depots/depots0.shtm
        """

        print_connection_error(verbose=verbose)

        self.last_updated_date = get_last_updated_date(url=self.URL, parsed=True, as_date_type=False)

        self.catalogue = get_catalogue(url=self.URL, update=update, confirmation_required=False)

        self.data_dir, self.current_data_dir = init_data_dir(self, data_dir, category="other-assets")

        self.TCTKey, self.FDPTKey, self.S1950Key, self.GWRKey = list(self.catalogue.keys())[1:]
        self.TCTPickle = self.TCTKey.replace(" ", "-").lower()
        self.FDPTPickle = re.sub(r'[ -]', '-', self.FDPTKey).lower()
        self.S1950Pickle = re.sub(r' \(|\) | ', '-', self.S1950Key).lower()
        self.GWRPickle = self.GWRKey.replace(" ", "-").lower()

    def _cdd_depots(self, *sub_dir, **kwargs):
        """
        Change directory to package data directory and subdirectories (and/or a file).
        
        The directory for this module: ``"dat\\other-assets\\depots"``.

        :param sub_dir: subdirectory or subdirectories (and/or a file)
        :type sub_dir: str
        :param kwargs: optional parameters of `os.makedirs`_, e.g. ``mode=0o777``
        :return: path to the backup data directory for ``Depots``
        :rtype: str

        .. _`os.makedirs`: https://docs.python.org/3/library/os.html#os.makedirs

        :meta private:
        """

        path = cd(self.data_dir, *sub_dir, mkdir=True, **kwargs)

        return path

    def collect_two_char_tops_codes(self, confirmation_required=True, verbose=False):
        """
        Collect `two-character TOPS codes <http://www.railwaycodes.org.uk/depots/depots1.shtm>`_ 
        from source web page.

        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of two-character TOPS codes and date of when the data was last updated
        :rtype: dict or None

        **Example**::

            >>> from pyrcs.other_assets import Depots

            >>> depots = Depots()

            >>> tct_dat = depots.collect_two_char_tops_codes()
            To collect data of two character TOPS codes? [No]|Yes: yes

            >>> type(tct_dat)
            dict
            >>> list(tct_dat.keys())
            ['Two character TOPS codes', 'Last updated date']

            >>> print(depots.TCTKey)
            Two character TOPS codes

            >>> tct_codes = tct_dat[depots.TCTKey]

            >>> type(tct_codes)
            pandas.core.frame.DataFrame
            >>> tct_codes.head()
              Code click to sort  ...                Notes
            0                 AB  ...          Closed 1987
            1                 AB  ...
            2                 AC  ...  Became WH from 1994
            3                 AC  ...
            4                 AD  ...
            [5 rows x 5 columns]
        """

        if confirmed("To collect data of {}?".format(self.TCTKey[:1].lower() + self.TCTKey[1:]),
                     confirmation_required=confirmation_required):

            url = self.catalogue[self.TCTKey]

            if verbose == 2:
                print("Collecting data of {}".format(
                    self.TCTKey[:1].lower() + self.TCTKey[1:]), end=" ... ")

            two_char_tops_codes_data = None

            try:
                header, two_char_tops_codes = \
                    pd.read_html(url, na_values=[''], keep_default_na=False)
            except (urllib.error.URLError, socket.gaierror):
                print("Failed.") if verbose == 2 else ""
                print_conn_err(verbose=verbose)

            else:
                try:
                    two_char_tops_codes.columns = header.columns.to_list()
                    two_char_tops_codes.fillna('', inplace=True)

                    last_updated_date = get_last_updated_date(url)

                    print("Done.") if verbose == 2 else ""

                    two_char_tops_codes_data = {self.TCTKey: two_char_tops_codes,
                                                self.KEY_TO_LAST_UPDATED_DATE: last_updated_date}

                    path_to_pickle = self._cdd_depots(self.TCTPickle + ".pickle")
                    save_pickle(two_char_tops_codes_data, path_to_pickle, verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(e))

            return two_char_tops_codes_data

    def fetch_two_char_tops_codes(self, update=False, pickle_it=False, data_dir=None,
                                  verbose=False):
        """
        Fetch `two-character TOPS codes <http://www.railwaycodes.org.uk/depots/depots1.shtm>`_
        from local backup.

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param pickle_it: whether to save the data as a pickle file, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of a folder where the pickle file is to be saved, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of two-character TOPS codes and date of when the data was last updated
        :rtype: dict

        **Example**::

            >>> from pyrcs.other_assets import Depots

            >>> depots = Depots()

            >>> # tct_dat = depots.fetch_two_char_tops_codes(update=True, verbose=True)
            >>> tct_dat = depots.fetch_two_char_tops_codes()

            >>> type(tct_dat)
            dict
            >>> list(tct_dat.keys())
            ['Two character TOPS codes', 'Last updated date']

            >>> print(depots.TCTKey)
            Two character TOPS codes

            >>> tct_codes = tct_dat[depots.TCTKey]

            >>> type(tct_codes)
            pandas.core.frame.DataFrame
            >>> tct_codes.head()
              Code click to sort  ...                Notes
            0                 AB  ...          Closed 1987
            1                 AB  ...
            2                 AC  ...  Became WH from 1994
            3                 AC  ...
            4                 AD  ...
            [5 rows x 5 columns]
        """

        path_to_pickle = self._cdd_depots(self.TCTPickle + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            two_char_tops_codes_data = load_pickle(path_to_pickle)

        else:
            verbose_ = False if data_dir or not verbose else (2 if verbose == 2 else True)

            two_char_tops_codes_data = self.collect_two_char_tops_codes(
                confirmation_required=False, verbose=verbose_)

            if two_char_tops_codes_data:
                if pickle_it and data_dir:
                    self.current_data_dir = validate_dir(data_dir)
                    path_to_pickle = os.path.join(self.current_data_dir, self.TCTPickle + ".pickle")
                    save_pickle(two_char_tops_codes_data, path_to_pickle, verbose=verbose)
            else:
                print("No data of {} has been freshly collected.".format(
                    self.TCTKey[:1].lower() + self.TCTKey[1:]))
                two_char_tops_codes_data = load_pickle(path_to_pickle)

        return two_char_tops_codes_data

    def collect_four_digit_pre_tops_codes(self, confirmation_required=True, verbose=False):
        """
        Collect `four-digit pre-TOPS codes <http://www.railwaycodes.org.uk/depots/depots2.shtm>`_
        from source web page.

        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of two-character TOPS codes and date of when the data was last updated
        :rtype: dict or None

        **Example**::

            >>> from pyrcs.other_assets import Depots

            >>> depots = Depots()

            >>> fdpt = depots.collect_four_digit_pre_tops_codes()
            To collect data of four digit pre-TOPS codes? [No]|Yes: yes

            >>> type(fdpt)
            dict
            >>> list(fdpt.keys())
            ['Four digit pre-TOPS codes', 'Last updated date']

            >>> print(depots.FDPTKey)
            Four digit pre-TOPS codes

            >>> fdpt_codes = fdpt[depots.FDPTKey]

            >>> type(fdpt_codes)
            pandas.core.frame.DataFrame
            >>> fdpt_codes.head()
               Code             Depot name          Region
            0  2000             Accrington  London Midland
            1  2001   Derby Litchurch Lane      Main Works
            2  2003              Blackburn  London Midland
            3  2004  Bolton Trinity Street  London Midland
            4  2006                Burnley  London Midland
        """

        if confirmed("To collect data of {}?".format(self.FDPTKey[:1].lower() + self.FDPTKey[1:]),
                     confirmation_required=confirmation_required):

            path_to_pickle = self._cdd_depots(self.FDPTPickle + ".pickle")

            url = self.catalogue[self.FDPTKey]

            if verbose == 2:
                print("Collecting data of {}".format(self.FDPTKey[:1].lower() + self.FDPTKey[1:]),
                      end=" ... ")

            four_digit_pre_tops_codes_data = None

            try:
                headers_, four_digit_pre_tops_codes = pd.read_html(url)
            except requests.ConnectionError:
                print("Failed.") if verbose == 2 else ""
                print_conn_err(verbose=verbose)

            else:
                try:
                    four_digit_pre_tops_codes.columns = [
                        x.replace(' click to sort', '') for x in list(headers_)]

                    col_region = 'Region'
                    four_digit_pre_tops_codes[col_region] = ''

                    dagger, col_depot = ' †', 'Depot name'
                    for i in four_digit_pre_tops_codes.index:
                        v = four_digit_pre_tops_codes.loc[i, col_depot]
                        c = four_digit_pre_tops_codes.loc[i, 'Code']
                        if v.endswith(dagger):
                            four_digit_pre_tops_codes.loc[i, col_region] = 'Main Works'
                        elif 2000 <= c < 3000:
                            four_digit_pre_tops_codes.loc[i, col_region] = 'London Midland'
                        elif 3000 <= c < 4000:
                            four_digit_pre_tops_codes.loc[i, col_region] = 'Western'
                        elif 4000 <= c < 5000:
                            four_digit_pre_tops_codes.loc[i, col_region] = 'Southern'
                        elif 5000 <= c < 7000:
                            four_digit_pre_tops_codes.loc[i, col_region] = 'Eastern'
                        elif c >= 7000:
                            four_digit_pre_tops_codes.loc[i, col_region] = 'Scottish'

                    four_digit_pre_tops_codes[col_depot] = \
                        four_digit_pre_tops_codes[col_depot].str.rstrip(dagger)

                    last_updated_date = get_last_updated_date(url)

                    print("Done.") if verbose == 2 else ""

                    # four_digit_pre_tops_codes_data = {
                    #     self.FDPTKey: dict(zip(region_names, four_digit_pre_tops_codes_list)),
                    #     self.LUDKey: last_updated_date}

                    four_digit_pre_tops_codes_data = {self.FDPTKey: four_digit_pre_tops_codes,
                                                      self.KEY_TO_LAST_UPDATED_DATE: last_updated_date}

                    save_pickle(four_digit_pre_tops_codes_data, path_to_pickle, verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(e))

            return four_digit_pre_tops_codes_data

    def fetch_four_digit_pre_tops_codes(self, update=False, pickle_it=False, data_dir=None,
                                        verbose=False):
        """
        Fetch `four-digit pre-TOPS codes <http://www.railwaycodes.org.uk/depots/depots2.shtm>`_
        from local backup.

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param pickle_it: whether to save the data as a pickle file, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of a folder where the pickle file is to be saved, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of two-character TOPS codes and date of when the data was last updated
        :rtype: dict

        **Example**::

            >>> from pyrcs.other_assets import Depots

            >>> depots = Depots()

            >>> # fdpt = depots.fetch_four_digit_pre_tops_codes(update=True, verbose=True)
            >>> fdpt = depots.fetch_four_digit_pre_tops_codes()

            >>> type(fdpt)
            dict
            >>> list(fdpt.keys())
            ['Four digit pre-TOPS codes', 'Last updated date']

            >>> print(depots.FDPTKey)
            Four digit pre-TOPS codes

            >>> fdpt_codes = fdpt[depots.FDPTKey]

            >>> type(fdpt_codes)
            pandas.core.frame.DataFrame
            >>> fdpt_codes.head()
               Code             Depot name          Region
            0  2000             Accrington  London Midland
            1  2001   Derby Litchurch Lane      Main Works
            2  2003              Blackburn  London Midland
            3  2004  Bolton Trinity Street  London Midland
            4  2006                Burnley  London Midland
        """

        path_to_pickle = self._cdd_depots(self.FDPTPickle + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            four_digit_pre_tops_codes_data = load_pickle(path_to_pickle)

        else:
            verbose_ = False if data_dir or not verbose else (2 if verbose == 2 else True)

            four_digit_pre_tops_codes_data = self.collect_four_digit_pre_tops_codes(
                confirmation_required=False, verbose=verbose_)

            if four_digit_pre_tops_codes_data:
                if pickle_it and data_dir:
                    self.current_data_dir = validate_dir(data_dir)
                    path_to_pickle = os.path.join(
                        self.current_data_dir, os.path.basename(path_to_pickle))

                    save_pickle(four_digit_pre_tops_codes_data, path_to_pickle, verbose=verbose)

            else:
                print("No data of {} has been freshly collected.".format(
                    self.FDPTKey[:1].lower() + self.FDPTKey[1:]))
                four_digit_pre_tops_codes_data = load_pickle(path_to_pickle)

        return four_digit_pre_tops_codes_data

    def collect_1950_system_codes(self, confirmation_required=True, verbose=False):
        # noinspection GrazieInspection
        """
        Collect `1950 system (pre-TOPS) codes <http://www.railwaycodes.org.uk/depots/depots3.shtm>`_
        from source web page.

        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of 1950 system (pre-TOPS) codes and date of when the data was last updated
        :rtype: dict or None

        **Example**::

            >>> from pyrcs.other_assets import Depots

            >>> depots = Depots()

            >>> s1950_dat = depots.collect_1950_system_codes()
            To collect data of 1950 system (pre-TOPS) codes? [No]|Yes: yes

            >>> type(s1950_dat)
            dict
            >>> list(s1950_dat.keys())
            ['1950 system (pre-TOPS) codes', 'Last updated date']

            >>> print(depots.S1950Key)
            1950 system (pre-TOPS) codes

            >>> s1950_codes = s1950_dat[depots.S1950Key]

            >>> type(s1950_codes)
            pandas.core.frame.DataFrame
            >>> s1950_codes.head()
              Code click to sort  ...                                              Notes
            0                 1A  ...               From 1950. Became WN from 6 May 1973
            1                 1B  ...                       From 1950. To 3 January 1966
            2                 1C  ...               From 1950. Became WJ from 6 May 1973
            3                 1D  ...  Previously 13B to 9 June 1950. Became 1J from ...
            4                 1D  ...  Previously 14F to 31 August 1963. Became ME fr...
            [5 rows x 3 columns]
        """

        if confirmed("To collect data of {}?".format(self.S1950Key),
                     confirmation_required=confirmation_required):

            url = self.catalogue[self.S1950Key]

            if verbose == 2:
                print("Collecting data of {}".format(self.S1950Key), end=" ... ")

            system_1950_codes_data = None

            try:
                header, system_1950_codes = pd.read_html(url, na_values=[''], keep_default_na=False)
            except (urllib.error.URLError, socket.gaierror):
                print("Failed.") if verbose == 2 else ""
                print_conn_err(verbose=verbose)

            else:
                try:
                    system_1950_codes.columns = header.columns.to_list()

                    last_updated_date = get_last_updated_date(url)

                    print("Done.") if verbose == 2 else ""

                    system_1950_codes_data = {self.S1950Key: system_1950_codes,
                                              self.KEY_TO_LAST_UPDATED_DATE: last_updated_date}

                    path_to_pickle = self._cdd_depots(self.S1950Pickle + ".pickle")
                    save_pickle(system_1950_codes_data, path_to_pickle, verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(e))

            return system_1950_codes_data

    def fetch_1950_system_codes(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        # noinspection GrazieInspection
        """
        Fetch `1950 system (pre-TOPS) codes <http://www.railwaycodes.org.uk/depots/depots3.shtm>`_
        from local backup.

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param pickle_it: whether to save the data as a pickle file, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of a folder where the pickle file is to be saved, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of 1950 system (pre-TOPS) codes and date of when the data was last updated
        :rtype: dict

        **Example**::

            >>> from pyrcs.other_assets import Depots

            >>> depots = Depots()

            >>> # s1950_dat = depots.fetch_1950_system_codes(update=True, verbose=True)
            >>> s1950_dat = depots.fetch_1950_system_codes()

            >>> print(depots.S1950Key)
            1950 system (pre-TOPS) codes

            >>> s1950_codes = s1950_dat[depots.S1950Key]

            >>> type(s1950_codes)
            pandas.core.frame.DataFrame
            >>> s1950_codes.head()
              Code click to sort  ...                                              Notes
            0                 1A  ...               From 1950. Became WN from 6 May 1973
            1                 1B  ...                       From 1950. To 3 January 1966
            2                 1C  ...               From 1950. Became WJ from 6 May 1973
            3                 1D  ...  Previously 13B to 9 June 1950. Became 1J from ...
            4                 1D  ...  Previously 14F to 31 August 1963. Became ME fr...
            [5 rows x 3 columns]
        """

        path_to_pickle = self._cdd_depots(self.S1950Pickle + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            system_1950_codes_data = load_pickle(path_to_pickle)

        else:
            verbose_ = False if data_dir or not verbose else (2 if verbose == 2 else True)

            system_1950_codes_data = self.collect_1950_system_codes(
                confirmation_required=False, verbose=verbose_)

            if system_1950_codes_data:
                if pickle_it and data_dir:
                    self.current_data_dir = validate_dir(data_dir)
                    path_to_pickle = os.path.join(
                        self.current_data_dir, os.path.basename(path_to_pickle))
                    save_pickle(system_1950_codes_data, path_to_pickle, verbose=verbose)

            else:
                print("No data of {} has been freshly collected.".format(self.S1950Key))
                system_1950_codes_data = load_pickle(path_to_pickle)

        return system_1950_codes_data

    def collect_gwr_codes(self, confirmation_required=True, verbose=False):
        """
        Collect `Great Western Railway (GWR) depot codes
        <http://www.railwaycodes.org.uk/depots/depots4.shtm>`_ from source web page.

        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of GWR depot codes and date of when the data was last updated
        :rtype: dict or None

        **Example**::

            >>> from pyrcs.other_assets import Depots

            >>> depots = Depots()

            >>> gwr_codes_dat = depots.collect_gwr_codes()
            To collect data of GWR codes? [No]|Yes: yes

            >>> type(gwr_codes_dat)
            dict
            >>> list(gwr_codes_dat.keys())
            ['GWR codes', 'Last updated date']

            >>> print(depots.GWRKey)
            GWR codes

            >>> type(gwr_codes_dat[depots.GWRKey])
            dict
            >>> list(gwr_codes_dat[depots.GWRKey].keys())
            ['Alphabetical codes', 'Numerical codes']

            >>> alpha_codes = gwr_codes_dat[depots.GWRKey]['Alphabetical codes']

            >>> type(alpha_codes)
            pandas.core.frame.DataFrame
            >>> alpha_codes.head()
                Code   Depot name
            0  ABEEG     Aberbeeg
            1    ABG     Aberbeeg
            2    AYN    Abercynon
            3   ABDR     Aberdare
            4    ABH  Aberystwyth
        """

        if confirmed("To collect data of {}?".format(self.GWRKey),
                     confirmation_required=confirmation_required):

            url = self.catalogue[self.GWRKey]

            if verbose == 2:
                print("Collecting data of {}".format(self.GWRKey), end=" ... ")

            gwr_codes_data = None

            try:
                header_, alphabetical_codes, _, numerical_codes_2 = pd.read_html(url)
                headers = [x.replace(' click to sort', '') for x in header_.columns]

                # Alphabetical codes
                alphabetical_codes.columns = headers

                # Numerical codes
                source = requests.get(url, headers=fake_requests_headers())
                soup = bs4.BeautifulSoup(source.text, 'lxml')

                span_tags = soup.find_all('span', {'class': 'tab2'})
                num_codes_1 = [
                    (span_tag.text, span_tag.next_sibling.replace(' = ', '').strip())
                    for span_tag in span_tags]

                numerical_codes_1 = pd.DataFrame(num_codes_1, columns=headers)

                numerical_codes_2.drop(2, axis=1, inplace=True)
                numerical_codes_2.columns = headers

                numerical_codes = pd.concat([numerical_codes_1, numerical_codes_2],
                                            ignore_index=True)

            except (urllib.error.URLError, socket.gaierror):
                print("Failed.") if verbose == 2 else ""
                print_conn_err(verbose=verbose)

            else:
                try:
                    gwr_codes = dict(zip([x.text for x in soup.find_all('h3')],
                                         [alphabetical_codes, numerical_codes]))

                    last_updated_date = get_last_updated_date(url)

                    print("Done.") if verbose == 2 else ""

                    gwr_codes_data = {
                        self.GWRKey: gwr_codes,
                        self.KEY_TO_LAST_UPDATED_DATE: last_updated_date,
                    }

                    path_to_pickle = self._cdd_depots(self.GWRPickle + ".pickle")
                    save_pickle(gwr_codes_data, path_to_pickle, verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(e))

            return gwr_codes_data

    def fetch_gwr_codes(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch `Great Western Railway (GWR) depot codes
        <http://www.railwaycodes.org.uk/depots/depots4.shtm>`_ from local backup.

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param pickle_it: whether to save the data as a pickle file, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of a folder where the pickle file is to be saved, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of GWR depot codes and date of when the data was last updated
        :rtype: dict

        **Example**::

            >>> from pyrcs.other_assets import Depots

            >>> depots = Depots()

            >>> # gwr_codes_dat = depots.fetch_gwr_codes(update=True, verbose=True)
            >>> gwr_codes_dat = depots.fetch_gwr_codes()

            >>> print(depots.GWRKey)
            GWR codes

            >>> gwr_codes = gwr_codes_dat[depots.GWRKey]

            >>> type(gwr_codes)
            dict
            >>> list(gwr_codes.keys())
            ['Alphabetical codes', 'Numerical codes']

            >>> gwr_codes_alpha = gwr_codes['Alphabetical codes']

            >>> type(gwr_codes_alpha)
            pandas.core.frame.DataFrame
            >>> gwr_codes_alpha.head()
                Code   Depot name
            0  ABEEG     Aberbeeg
            1    ABG     Aberbeeg
            2    AYN    Abercynon
            3   ABDR     Aberdare
            4    ABH  Aberystwyth
        """

        path_to_pickle = self._cdd_depots(self.GWRPickle + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            gwr_codes_data = load_pickle(path_to_pickle)

        else:
            verbose_ = False if data_dir or not verbose else (2 if verbose == 2 else True)

            gwr_codes_data = self.collect_gwr_codes(confirmation_required=False, verbose=verbose_)

            if gwr_codes_data:
                if pickle_it and data_dir:
                    self.current_data_dir = validate_dir(data_dir)
                    path_to_pickle = os.path.join(
                        self.current_data_dir, os.path.basename(path_to_pickle))

                    save_pickle(gwr_codes_data, path_to_pickle, verbose=verbose)

            else:
                print("No data of \"{}\" has been freshly collected.".format(self.GWRKey))
                gwr_codes_data = load_pickle(path_to_pickle)

        return gwr_codes_data

    def fetch_depot_codes(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch `depots codes
        <http://www.railwaycodes.org.uk/depots/depots0.shtm>`_ from local backup.

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param pickle_it: whether to save the data as a pickle file, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of a folder where the pickle file is to be saved, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of depot codes and date of when the data was last updated
        :rtype: dict

        **Example**::

            >>> from pyrcs.other_assets import Depots

            >>> depots = Depots()

            >>> # depot_codes_dat = depots.fetch_depot_codes(update=True, verbose=True)
            >>> depot_codes_dat = depots.fetch_depot_codes()

            >>> type(depot_codes_dat)
            dict
            >>> list(depot_codes_dat.keys())
            ['Depots', 'Last updated date']

            >>> print(depots.KEY)
            Depots

            >>> type(depot_codes_dat[depots.KEY])
            dict
            >>> list(depot_codes_dat[depots.KEY].keys())
            ['1950 system (pre-TOPS) codes',
             'Four digit pre-TOPS codes',
             'GWR codes',
             'Two character TOPS codes']

            >>> print(depots.FDPTKey)

            >>> depot_codes_dat[depots.KEY][depots.FDPTKey].head()
               Code             Depot name          Region
            0  2000             Accrington  London Midland
            1  2001   Derby Litchurch Lane      Main Works
            2  2003              Blackburn  London Midland
            3  2004  Bolton Trinity Street  London Midland
            4  2006                Burnley  London Midland
        """

        verbose_ = False if (data_dir or not verbose) else (2 if verbose == 2 else True)

        depot_codes = []
        for func in dir(self):
            if func.startswith('fetch_') and func != 'fetch_depot_codes':
                depot_codes.append(getattr(self, func)(
                    update=update, verbose=verbose_ if is_internet_connected() else False))

        depot_codes_data = {
            self.KEY: {next(iter(x)): next(iter(x.values())) for x in depot_codes},
            self.KEY_TO_LAST_UPDATED_DATE: self.last_updated_date}

        if pickle_it and data_dir:
            self.current_data_dir = validate_dir(data_dir)
            path_to_pickle = os.path.join(self.current_data_dir, self.KEY.lower() + ".pickle")

            save_pickle(depot_codes_data, path_to_pickle, verbose=verbose)

        return depot_codes_data
