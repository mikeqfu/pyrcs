"""
Collect
`signal box prefix codes <http://www.railwaycodes.org.uk/signal/signal_boxes0.shtm>`_.

.. todo::

   Ireland
   Western region MAS dates
   Mechanical signalling bell codes
"""

import copy
import os
import string
import urllib.parse

import bs4
import pandas as pd
import requests
from pyhelpers.dir import cd, validate_input_data_dir
from pyhelpers.ops import confirmed, fake_requests_headers
from pyhelpers.store import load_pickle, save_pickle

from pyrcs.utils import cd_dat, get_catalogue, get_last_updated_date, homepage_url, \
    is_internet_connected, parse_table, parse_tr, print_conn_err


class SignalBoxes:
    """
    A class for collecting signal box prefix codes.

    :param data_dir: name of data directory, defaults to ``None``
    :type data_dir: str, None
    :param update: whether to check on update and proceed to update the package data, 
        defaults to ``False``
    :type update: bool
    :param verbose: whether to print relevant information in console as the function runs,
        defaults to ``True``
    :type verbose: bool or int

    **Example**::

        >>> from pyrcs.other_assets import SignalBoxes

        >>> sb = SignalBoxes()

        >>> print(sb.Name)
        Signal box prefix codes

        >>> print(sb.SourceURL)
        http://www.railwaycodes.org.uk/signal/signal_boxes0.shtm
    """

    def __init__(self, data_dir=None, update=False, verbose=True):
        """
        Constructor method.
        """
        self.Name = 'Signal box prefix codes'
        self.HomeURL = homepage_url()
        self.SourceURL = urllib.parse.urljoin(self.HomeURL, '/signal/signal_boxes0.shtm')

        self.Date = get_last_updated_date(self.SourceURL, parsed=True, as_date_type=False,
                                          verbose=verbose)

        self.Catalogue = get_catalogue(self.SourceURL, update=update,
                                       confirmation_required=False)

        self.Key = 'Signal boxes'
        self.LUDKey = 'Last updated date'  # key to last updated date

        if data_dir:
            self.DataDir = validate_input_data_dir(data_dir)
        else:
            self.DataDir = cd_dat("other-assets", self.Key.lower().replace(" ", "-"))
        self.CurrentDataDir = copy.copy(self.DataDir)

        self.NonNationalRailKey = 'Non-National Rail'
        self.NonNationalRailPickle = self.NonNationalRailKey.lower().replace(" ", "-")
        self.IrelandKey = 'Ireland'
        self.WMASDKey = 'Western region MAS dates'
        self.MSBKey = 'Mechanical signalling bell codes'

    def _cdd_sigbox(self, *sub_dir, **kwargs):
        """
        Change directory to package data directory and sub-directories (and/or a file).

        The directory for this module: ``"\\dat\\other-assets\\signal-boxes"``.

        :param sub_dir: sub-directory or sub-directories (and/or a file)
        :type sub_dir: str
        :param kwargs: optional parameters of
            `os.makedirs <https://docs.python.org/3/library/os.html#os.makedirs>`_,
            e.g. ``mode=0o777``
        :return: path to the backup data directory for ``SignalBoxes``
        :rtype: str

        :meta private:
        """

        path = cd(self.DataDir, *sub_dir, mkdir=True, **kwargs)

        return path

    def collect_prefix_codes(self, initial, update=False, verbose=False):
        """
        Collect signal box prefix codes for the given ``initial`` from source web page.

        :param initial: initial letter of signal box name (for specifying a target URL)
        :type initial: str
        :param update: whether to check on update and proceed to update the package data, 
            defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console 
            as the function runs, defaults to ``False``
        :type verbose: bool, int
        :return: data of signal box prefix codes for the given ``initial`` and
            date of when the data was last updated
        :rtype: dict

        **Example**::

            >>> from pyrcs.other_assets import SignalBoxes

            >>> sb = SignalBoxes()

            >>> signal_boxes_a = sb.collect_prefix_codes(initial='a')

            >>> type(signal_boxes_a)
            <class 'dict'>
            >>> print(list(signal_boxes_a.keys()))
            ['A', 'Last updated date']

            >>> signal_boxes_a_codes = signal_boxes_a['A']
            >>> type(signal_boxes_a_codes)
            <class 'pandas.core.frame.DataFrame'>
            >>> print(signal_boxes_a_codes.head())
              Code               Signal Box  ...            Closed        Control to
            0   AF  Abbey Foregate Junction  ...
            1   AJ           Abbey Junction  ...  16 February 1992     Nuneaton (NN)
            2    R           Abbey Junction  ...  16 February 1992     Nuneaton (NN)
            3   AW               Abbey Wood  ...      13 July 1975      Dartford (D)
            4   AE         Abbey Works East  ...   1 November 1987  Port Talbot (PT)

            [5 rows x 8 columns]
        """

        path_to_pickle = self._cdd_sigbox("a-z", initial.lower() + ".pickle")

        beginning_with = initial.upper()

        if os.path.isfile(path_to_pickle) and not update:
            signal_box_prefix_codes = load_pickle(path_to_pickle)

        else:
            signal_box_prefix_codes = {beginning_with: None, self.LUDKey: None}

            if beginning_with not in list(self.Catalogue.keys()):
                if verbose:
                    print("No data is available for {} codes beginning "
                          "with \"{}\".".format(self.Key.lower(), beginning_with))

            else:
                url = self.SourceURL.replace('0', initial.lower())

                if verbose == 2:
                    print("Collecting data of {} beginning with \"{}\"".format(
                        self.Key.lower(), beginning_with), end=" ... ")

                try:
                    source = requests.get(url, headers=fake_requests_headers())
                except requests.ConnectionError:
                    print("Failed. ") if verbose == 2 else ""
                    print_conn_err(verbose=verbose)

                else:
                    try:
                        # Get table data and its column names
                        records, header = parse_table(source, 'lxml')
                        # Create a DataFrame of the requested table
                        dat = [[x.strip('\xa0') for x in i] for i in records]
                        col = [h.replace('Signal box', 'Signal Box') for h in header]
                        signal_boxes_data_table = pd.DataFrame(dat, columns=col)

                        last_updated_date = get_last_updated_date(url)

                        print("Done.") if verbose == 2 else ""

                        signal_box_prefix_codes.update(
                            {beginning_with: signal_boxes_data_table,
                             self.LUDKey: last_updated_date})

                        save_pickle(signal_box_prefix_codes, path_to_pickle,
                                    verbose=verbose)

                    except Exception as e:
                        print("Failed. {}".format(e))

        return signal_box_prefix_codes

    def fetch_prefix_codes(self, update=False, pickle_it=False, data_dir=None,
                           verbose=False):
        """
        Fetch signal box prefix codes from local backup.

        :param update: whether to check on update and proceed to update the package data, 
            defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data 
            with newly collected data, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str, None
        :param verbose: whether to print relevant information in console 
            as the function runs, defaults to ``False``
        :type verbose: bool, int
        :return: data of location codes and date of when the data was last updated
        :rtype: dict

        **Example**::

            >>> from pyrcs.other_assets import SignalBoxes

            >>> sb = SignalBoxes()

            >>> signal_box_prefix_codes_dat = sb.fetch_prefix_codes()

            >>> type(signal_box_prefix_codes_dat)
            <class 'dict'>
            >>> print(list(signal_box_prefix_codes_dat.keys()))
            ['Signal boxes', 'Last updated date']

            >>> signal_box_prefix_codes_ = signal_box_prefix_codes_dat['Signal boxes']
            >>> type(signal_box_prefix_codes_)
            <class 'pandas.core.frame.DataFrame'>
            >>> print(signal_box_prefix_codes_.head())
              Code               Signal Box  ...            Closed        Control to
            0   AF  Abbey Foregate Junction  ...
            1   AJ           Abbey Junction  ...  16 February 1992     Nuneaton (NN)
            2    R           Abbey Junction  ...  16 February 1992     Nuneaton (NN)
            3   AW               Abbey Wood  ...      13 July 1975      Dartford (D)
            4   AE         Abbey Works East  ...   1 November 1987  Port Talbot (PT)

            [5 rows x 8 columns]
        """

        verbose_ = False if (data_dir or not verbose) else (2 if verbose == 2 else True)

        # Get every data table
        data = [
            self.collect_prefix_codes(
                x, update=update, verbose=verbose_ if is_internet_connected() else False)
            for x in string.ascii_lowercase]

        if all(d[x] is None for d, x in zip(data, string.ascii_uppercase)):
            if update:
                print_conn_err(verbose=verbose)
                print("No data of the {} has been freshly collected.".format(
                    self.Key.lower()))
            data = [self.collect_prefix_codes(x, update=False, verbose=verbose_)
                    for x in string.ascii_lowercase]

        # Select DataFrames only
        signal_boxes_data = (item[x] for item, x in zip(data, string.ascii_uppercase))
        signal_boxes_data_table = pd.concat(signal_boxes_data, axis=0, ignore_index=True,
                                            sort=False)

        # Get the latest updated date
        last_updated_dates = (item[self.LUDKey] for item in data)
        latest_update_date = max(d for d in last_updated_dates if d is not None)

        # Create a dict to include all information
        signal_box_prefix_codes = {self.Key: signal_boxes_data_table,
                                   self.LUDKey: latest_update_date}

        if pickle_it and data_dir:
            self.CurrentDataDir = validate_input_data_dir(data_dir)
            path_to_pickle = os.path.join(
                self.CurrentDataDir, self.Key.lower().replace(" ", "-") + ".pickle")
            save_pickle(signal_box_prefix_codes, path_to_pickle, verbose=verbose)

        return signal_box_prefix_codes

    def collect_non_national_rail_codes(self, confirmation_required=True, verbose=False):
        """
        Collect signal box prefix codes of `non-national rail
        <http://www.railwaycodes.org.uk/signal/signal_boxesX.shtm>`_ from source web page.

        :param confirmation_required: whether to require users to confirm and proceed,
            defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console 
            as the function runs, defaults to ``False``
        :type verbose: bool, int
        :return: signal box prefix codes of non-national rail
        :rtype: dict, None

        **Example**::

            >>> from pyrcs.other_assets import SignalBoxes

            >>> sb = SignalBoxes()

            >>> non_national_rail_codes_dat = sb.collect_non_national_rail_codes()
            To collect signal box data of non-national rail? [No]|Yes: yes

            >>> type(non_national_rail_codes_dat)
            <class 'dict'>
            >>> print(list(non_national_rail_codes_dat.keys()))
            ['Non-National Rail', 'Last updated date']
        """

        if confirmed("To collect signal box data of {}?".format(
                self.NonNationalRailKey.lower()),
                confirmation_required=confirmation_required):

            url = self.Catalogue[self.NonNationalRailKey]

            if verbose == 2:
                print("Collecting signal box data of {}".format(
                    self.NonNationalRailKey.lower()), end=" ... ")

            non_national_rail_codes_data = None

            try:
                source = requests.get(url, headers=fake_requests_headers())
            except requests.ConnectionError:
                print("Failed. ") if verbose == 2 else ""
                print_conn_err(verbose=verbose)

            else:
                try:
                    web_page_text = bs4.BeautifulSoup(source.text, 'lxml')
                    non_national_rail, non_national_rail_codes = [], {}

                    for h in web_page_text.find_all('h3'):
                        # Get the name of the non-national rail
                        non_national_rail_name = h.text

                        # Find text descriptions
                        desc = h.find_next('p')
                        desc_text = desc.text.replace('\xa0', '')
                        more_desc = desc.find_next('p')
                        while more_desc.find_previous('h3') == h:
                            desc_text = '\n'.join(
                                [desc_text, more_desc.text.replace('\xa0', '')])
                            more_desc = more_desc.find_next('p')
                            if more_desc is None:
                                break

                        # Get table data
                        tbl_dat = desc.find_next('table')
                        if tbl_dat.find_previous('h3').text == non_national_rail_name:
                            header = [th.text for th in tbl_dat.find_all('th')]  # header
                            data = pd.DataFrame(
                                parse_tr(header, tbl_dat.find_next('table').find_all('tr')),
                                columns=header)
                        else:
                            data = None

                        # Update data dict
                        non_national_rail_codes.update({
                            non_national_rail_name:
                                [data, desc_text.replace('\xa0', '').strip()]})

                    last_updated_date = get_last_updated_date(url)

                    print("Done. ") if verbose == 2 else ""

                    non_national_rail_codes_data = {
                        self.NonNationalRailKey: non_national_rail_codes,
                        self.LUDKey: last_updated_date}

                    pickle_filename = self.NonNationalRailPickle + ".pickle"
                    save_pickle(non_national_rail_codes_data,
                                self._cdd_sigbox(pickle_filename), verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(e))

            return non_national_rail_codes_data

    def fetch_non_national_rail_codes(self, update=False, pickle_it=False, data_dir=None,
                                      verbose=False):
        """
        Fetch signal box prefix codes of `non-national rail
        <http://www.railwaycodes.org.uk/signal/signal_boxesX.shtm>`_ from local backup.

        :param update: whether to check on update and proceed to update the package data, 
            defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data 
            with newly collected data, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str, None
        :param verbose: whether to print relevant information in console 
            as the function runs, defaults to ``False``
        :type verbose: bool, int
        :return: signal box prefix codes of non-national rail
        :rtype: dict

        **Example**::

            >>> from pyrcs.other_assets import SignalBoxes

            >>> sb = SignalBoxes()

            >>> non_national_rail_codes_dat = sb.fetch_non_national_rail_codes()

            >>> non_national_rail_codes = non_national_rail_codes_dat['Non-National Rail']
            >>> type(non_national_rail_codes)
            <class 'dict'>
            >>> print(list(non_national_rail_codes.keys())[:5])
            ['Croydon Tramlink signals',
             'Docklands Light Railway signals',
             'Edinburgh Tramway signals',
             'Glasgow Subway signals',
             'London Underground signals']

            >>> croydon_tl_signals = non_national_rail_codes['Croydon Tramlink signals']
            >>> type(croydon_tl_signals)
            <class 'list'>
            >>> print(croydon_tl_signals[0])
            None
            >>> print(croydon_tl_signals[1])
            Croydon Tramlink signal codes can be found on the ...
        """

        pickle_filename = self.NonNationalRailPickle + ".pickle"
        path_to_pickle = self._cdd_sigbox(pickle_filename)

        if os.path.isfile(path_to_pickle) and not update:
            non_national_rail_codes_data = load_pickle(path_to_pickle)

        else:
            verbose_ = False if data_dir or not verbose else (2 if verbose == 2 else True)

            non_national_rail_codes_data = self.collect_non_national_rail_codes(
                confirmation_required=False, verbose=verbose_)

            if non_national_rail_codes_data:
                if pickle_it and data_dir:
                    self.CurrentDataDir = validate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, pickle_filename)
                    save_pickle(non_national_rail_codes_data, path_to_pickle,
                                verbose=verbose)

            else:
                print("No data of {} has been collected.".format(
                    self.NonNationalRailKey.lower()))
                non_national_rail_codes_data = load_pickle(path_to_pickle)

        return non_national_rail_codes_data
