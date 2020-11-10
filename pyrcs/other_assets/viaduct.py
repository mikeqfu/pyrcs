"""
Collect codes of
`railway viaducts <http://www.railwaycodes.org.uk/tunnels/tunnels0.shtm>`_.
"""

import copy
import itertools
import os
import re
import socket
import urllib.error
import urllib.parse

import pandas as pd
from pyhelpers.dir import cd, validate_input_data_dir
from pyhelpers.store import load_pickle, save_pickle
from pyhelpers.text import find_similar_str

from pyrcs.utils import cd_dat, get_catalogue, get_last_updated_date, homepage_url, \
    print_conn_err, is_internet_connected, print_connection_error


class Viaducts:
    """
    A class for collecting railway viaducts.

    :param data_dir: name of data directory, defaults to ``None``
    :type data_dir: str, None
    :param update: whether to check on update and proceed to update the package data, 
        defaults to ``False``
    :type update: bool
    :param verbose: whether to print relevant information in console as the function runs,
        defaults to ``True``
    :type verbose: bool or int

    **Example**::

        >>> from pyrcs.other_assets import Viaducts

        >>> viaducts = Viaducts()

        >>> print(viaducts.Name)
        Railway viaducts

        >>> print(viaducts.SourceURL)
        http://www.railwaycodes.org.uk/viaducts/viaducts0.shtm
    """

    def __init__(self, data_dir=None, update=False, verbose=True):
        """
        Constructor method.
        """
        if not is_internet_connected():
            print_connection_error(verbose=verbose)

        self.Name = 'Railway viaducts'
        self.Key = 'Viaducts'

        self.HomeURL = homepage_url()
        self.SourceURL = urllib.parse.urljoin(self.HomeURL, '/viaducts/viaducts0.shtm')

        self.LUDKey = 'Last updated date'
        self.Date = get_last_updated_date(url=self.SourceURL, parsed=True,
                                          as_date_type=False)

        self.Catalogue = get_catalogue(page_url=self.SourceURL, update=update,
                                       confirmation_required=False)

        self.P1Key, self.P2Key, self.P3Key, self.P4Key, self.P5Key, self.P6Key = \
            list(self.Catalogue.keys())[1:]

        if data_dir:
            self.DataDir = validate_input_data_dir(data_dir)
        else:
            self.DataDir = cd_dat("other-assets", self.Key.lower())
        self.CurrentDataDir = copy.copy(self.DataDir)

    def _cdd_vdct(self, *sub_dir, **kwargs):
        """
        Change directory to package data directory and sub-directories (and/or a file).

        The directory for this module: ``"\\dat\\other-assets\\viaducts"``.

        :param sub_dir: sub-directory or sub-directories (and/or a file)
        :type sub_dir: str
        :param kwargs: optional parameters of
            `os.makedirs <https://docs.python.org/3/library/os.html#os.makedirs>`_,
            e.g. ``mode=0o777``
        :return: path to the backup data directory for ``Viaducts``
        :rtype: str

        :meta private:
        """

        path = cd(self.DataDir, *sub_dir, mkdir=True, **kwargs)

        return path

    def collect_viaduct_codes_by_page(self, page_no, update=False, verbose=False):
        """
        Collect data of railway viaducts for a given page number from source web page.

        :param page_no: page number;
            valid values include ``1``, ``2``, ``3``, ``4``, ``5``, and ``6``
        :type page_no: int, str
        :param update: whether to check on update and proceed to update the package data,
            defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console
            as the function runs, defaults to ``False``
        :type verbose: bool
        :return: railway viaducts data of the given ``page_no`` and
            date of when the data was last updated
        :rtype: dict

        **Example**::

            >>> from pyrcs.other_assets import Viaducts

            >>> viaducts = Viaducts()

            >>> viaducts_1 = viaducts.collect_viaduct_codes_by_page(page_no=1)

            >>> type(viaducts_1)
            <class 'dict'>
            >>> print(list(viaducts_1.keys()))
            ['Page 1 (A-C)', 'Last updated date']
        """

        assert page_no in range(1, 7), \
            "Valid \"page_no\" must be one of 1, 2, 3, 4, 5, and 6."

        page_name = find_similar_str(str(page_no), list(self.Catalogue.keys()))

        pickle_filename = re.sub(
            r"[()]", "", re.sub(r"[ -]", "-", page_name)).lower() + ".pickle"
        path_to_pickle = self._cdd_vdct(pickle_filename)

        if os.path.isfile(path_to_pickle) and not update:
            page_railway_viaducts = load_pickle(path_to_pickle)

        else:
            url = self.Catalogue[page_name]

            page_railway_viaducts = None

            if verbose == 2:
                print("Collecting data of {} on {}".format(self.Key.lower(), page_name),
                      end=" ... ")

            try:
                header, viaducts_table = pd.read_html(
                    url, na_values=[''], keep_default_na=False)
            except (urllib.error.URLError, socket.gaierror):
                print("Failed. ") if verbose == 2 else ""
                print_conn_err(verbose=verbose)

            else:
                try:
                    viaducts_table.columns = header.columns.to_list()
                    viaducts_table.fillna('', inplace=True)

                    last_updated_date = get_last_updated_date(url)

                    print("Done. ") if verbose == 2 else ""

                    page_railway_viaducts = {page_name: viaducts_table,
                                             self.LUDKey: last_updated_date}

                    save_pickle(page_railway_viaducts, path_to_pickle, verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(page_name, e))

        return page_railway_viaducts

    def fetch_viaduct_codes(self, update=False, pickle_it=False, data_dir=None,
                            verbose=False):
        """
        Fetch data of railway viaducts from local backup.

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
        :type verbose: bool
        :return: railway viaducts data and date of when the data was last updated
        :rtype: dict

        **Example**::

            >>> from pyrcs.other_assets import Viaducts

            >>> viaducts = Viaducts()

            >>> viaducts_data = viaducts.fetch_viaduct_codes()

            >>> type(viaducts_data)
            <class 'dict'>
            >>> print(list(viaducts_data.keys()))
            ['Viaducts', 'Last updated date']

            >>> viaducts_dat = viaducts_data['Viaducts']
            >>> type(viaducts_dat)
            <class 'dict'>
            >>> print(list(viaducts_dat.keys()))
            ['Page 1 (A-C)',
             'Page 2 (D-G)',
             'Page 3 (H-K)',
             'Page 4 (L-P)',
             'Page 5 (Q-S)',
             'Page 6 (T-Z)']
        """

        verbose_ = False if (data_dir or not verbose) else (2 if verbose == 2 else True)

        page_data = [
            self.collect_viaduct_codes_by_page(
                page_no, update, verbose=verbose_ if is_internet_connected() else False)
            for page_no in range(1, 7)]

        if all(x is None for x in page_data):
            if update:
                print_conn_err(verbose=verbose)
                print("No data of the {} has been freshly collected.".format(
                    self.Key.lower()))
            page_data = [
                self.collect_viaduct_codes_by_page(x, update=False, verbose=verbose_)
                for x in range(1, 7)]

        railways_viaducts_data = {
            self.Key: {next(iter(x)): next(iter(x.values())) for x in page_data},
            self.LUDKey:
                max(next(itertools.islice(iter(x.values()), 1, 2)) for x in page_data)}

        if pickle_it and data_dir:
            self.CurrentDataDir = validate_input_data_dir(data_dir)
            path_to_pickle = os.path.join(
                self.CurrentDataDir, self.Key.lower().replace(" ", "-") + ".pickle")
            save_pickle(railways_viaducts_data, path_to_pickle, verbose=verbose)

        return railways_viaducts_data
