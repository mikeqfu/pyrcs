"""
Collect codes of
`railway tunnel lengths <http://www.railwaycodes.org.uk/tunnels/tunnels0.shtm>`_.
"""

import copy
import itertools
import operator
import os
import re
import urllib.parse

import bs4
import measurement.measures
import numpy as np
import pandas as pd
import requests
from pyhelpers.dir import cd, validate_input_data_dir
from pyhelpers.ops import fake_requests_headers
from pyhelpers.store import load_pickle, save_pickle
from pyhelpers.text import find_similar_str

from pyrcs.utils import cd_dat, get_catalogue, get_last_updated_date, homepage_url, \
    parse_tr, print_conn_err, is_internet_connected, print_connection_error


class Tunnels:
    """
    A class for collecting railway tunnel lengths.

    :param data_dir: name of data directory, defaults to ``None``
    :type data_dir: str, None
    :param update: whether to check on update and proceed to update the package data,
        defaults to ``False``
    :type update: bool
    :param verbose: whether to print relevant information in console as the function runs,
        defaults to ``True``
    :type verbose: bool or int

    **Example**::

        >>> from pyrcs.other_assets import Tunnels

        >>> tunnels = Tunnels()

        >>> print(tunnels.Name)
        Railway tunnel lengths

        >>> print(tunnels.SourceURL)
        http://www.railwaycodes.org.uk/tunnels/tunnels0.shtm
    """

    def __init__(self, data_dir=None, update=False, verbose=True):
        """
        Constructor method.
        """
        if not is_internet_connected():
            print_connection_error(verbose=verbose)

        self.Name = 'Railway tunnel lengths'
        self.Key = 'Tunnels'

        self.HomeURL = homepage_url()
        self.SourceURL = urllib.parse.urljoin(self.HomeURL, '/tunnels/tunnels0.shtm')

        self.LUDKey = 'Last updated date'
        self.Date = get_last_updated_date(url=self.SourceURL, parsed=True,
                                          as_date_type=False)

        self.Catalogue = get_catalogue(page_url=self.SourceURL, update=update,
                                       confirmation_required=False)

        self.P1Key, self.P2Key, self.P3Key, self.P4Key = list(self.Catalogue.keys())[1:]

        if data_dir:
            self.DataDir = validate_input_data_dir(data_dir)
        else:
            self.DataDir = cd_dat("other-assets", self.Key.lower())
        self.CurrentDataDir = copy.copy(self.DataDir)

    def _cdd_tnl(self, *sub_dir, **kwargs):
        """
        Change directory to package data directory and sub-directories (and/or a file).

        The directory for this module: ``"\\dat\\other-assets\\tunnels"``.

        :param sub_dir: sub-directory or sub-directories (and/or a file)
        :type sub_dir: str
        :param kwargs: optional parameters of
            `os.makedirs <https://docs.python.org/3/library/os.html#os.makedirs>`_,
            e.g. ``mode=0o777``
        :return: path to the backup data directory for ``Tunnels``
        :rtype: str

        :meta private:
        """

        path = cd(self.DataDir, *sub_dir, mkdir=True, **kwargs)

        return path

    @staticmethod
    def parse_length(x):
        """
        Parse data in ``'Length'`` column, i.e. convert miles/yards to metres.

        :param x: raw length data
        :type x: str, None
        :return: parsed length data and, if any, additional information associated with it
        :rtype: tuple

        **Examples**::

            >>> from pyrcs.other_assets import Tunnels

            >>> tunnels = Tunnels()

            >>> tunnels.parse_length('')
            (nan, 'Unavailable')

            >>> tunnels.parse_length('1m 182y')
            (1775.7648, None)

            >>> tunnels.parse_length('formerly 0m236y')
            (215.7984, 'Formerly')

            >>> tunnels.parse_length('0.325km (0m 356y)')
            (325.5264, '0.325km')

            >>> tunnels.parse_length("0m 48yd- (['0m 58yd'])")
            (48.4632, '43.89-53.04 metres')
        """

        if re.match(r'[Uu]nknown', x):
            length = np.nan
            add_info = 'Unknown'
        elif x == '':
            length = np.nan
            add_info = 'Unavailable'
        elif re.match(r'\d+m \d+yd-.*\d+m \d+yd.*', x):
            miles_a, yards_a, miles_b, yards_b = re.findall(r'\d+', x)
            length_a = \
                measurement.measures.Distance(mi=miles_a).m + \
                measurement.measures.Distance(yd=yards_a).m
            length_b = \
                measurement.measures.Distance(mi=miles_b).m + \
                measurement.measures.Distance(yd=yards_b).m
            length = (length_a + length_b) / 2
            add_info = \
                '-'.join([str(round(length_a, 2)), str(round(length_b, 2))]) + ' metres'
        else:
            if re.match(r'(formerly )?c?\d+m ?\d+y?(ch)?.*', x):
                miles, yards = re.findall(r'\d+', x)
                if re.match(r'.*\d+ch$', x):
                    yards = measurement.measures.Distance(chain=yards).yd
                if re.match(r'^c.*', x):
                    add_info = 'Approximate'
                elif re.match(r'\d+y$', x):
                    add_info = re.search(r'(?<=\dy).*$', x).group(0)
                elif re.match(r'^(formerly).*', x):
                    add_info = 'Formerly'
                else:
                    add_info = None
            elif re.match(r'\d+\.\d+km(\r)? .*(\[\')?\(\d+m \d+y\).*', x):
                miles, yards = re.findall(
                    r'\d+', re.search(r'(?<=\()\d+.*(?=\))', x).group(0))
                add_info = re.search(r'.+(?= (\[\')?\()', x.replace('\r', '')).group(0)
            else:
                print(x)
                miles, yards = 0, 0
                add_info = ''
            length = \
                measurement.measures.Distance(mi=miles).m + \
                measurement.measures.Distance(yd=yards).m
        return length, add_info

    def collect_lengths_by_page(self, page_no, update=False, verbose=False):
        """
        Collect data of railway tunnel lengths for a page number from source web page.

        :param page_no: page number; valid values include ``1``, ``2``, ``3`` and ``4``
        :type page_no: int, str
        :param update: whether to check on update and proceed to update the package data,
            defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console
            as the function runs, defaults to ``False``
        :type verbose: bool, int
        :return: tunnel lengths data of the given ``page_no`` and
            date of when the data was last updated
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Tunnels

            >>> tunnels = Tunnels()

            >>> tunnel_len_1 = tunnels.collect_lengths_by_page(page_no=1)
            >>> type(tunnel_len_1)
            <class 'dict'>
            >>> print(list(tunnel_len_1.keys()))
            ['Page 1 (A-F)', 'Last updated date']

            >>> tunnel_len_4 = tunnels.collect_lengths_by_page(page_no=4)
            >>> type(tunnel_len_4)
            <class 'dict'>
            >>> print(list(tunnel_len_4.keys()))
            ['Page 4 (others)', 'Last updated date']
        """

        assert page_no in range(1, 5)
        page_name = find_similar_str(str(page_no), list(self.Catalogue.keys()))

        pickle_filename_ = re.sub(r"[()]", "", re.sub(r"[ -]", "-", page_name)).lower()
        path_to_pickle = self._cdd_tnl(pickle_filename_ + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            page_railway_tunnel_lengths = load_pickle(path_to_pickle)

        else:
            url = self.Catalogue[page_name]

            page_railway_tunnel_lengths = None

            if verbose == 2:
                print("Collecting data of {} on {}".format(self.Key.lower(), page_name),
                      end=" ... ")

            try:
                source = requests.get(url, headers=fake_requests_headers())
            except requests.ConnectionError:
                print("Failed. ") if verbose == 2 else ""
                print_conn_err(verbose=verbose)

            else:
                try:
                    parsed_text = bs4.BeautifulSoup(source.text, 'lxml')

                    headers = []
                    temp_header = parsed_text.find('table')
                    while temp_header.find_next('th'):
                        header = [x.text for x in temp_header.find_all('th')]
                        if len(header) > 0:
                            crossed = [re.match('^Between.*', x) for x in header]
                            if any(crossed):
                                idx = list(itertools.compress(range(len(crossed)), crossed))
                                assert len(idx) == 1
                                header.remove(header[idx[0]])
                                header[idx[0]:idx[0]] = ['Station_O', 'Station_D']
                            headers.append(header)
                        temp_header = temp_header.find_next('table')

                    tbl_lst = operator.itemgetter(
                        1, len(parsed_text.find_all('h3')) + 1)(
                        parsed_text.find_all('table'))
                    tbl_lst = [
                        parse_tr(header, x.find_all('tr'))
                        for header, x in zip(headers, tbl_lst)]
                    tbl_lst = [
                        [[item.replace('\xa0', '') for item in record] for record in tbl]
                        for tbl in tbl_lst]

                    tunnel_lengths = [pd.DataFrame(tbl, columns=header)
                                      for tbl, header in zip(tbl_lst, headers)]

                    for i in range(len(tunnel_lengths)):
                        tunnel_lengths[i][['Length_metres', 'Length_notes']] = \
                            tunnel_lengths[i].Length.map(
                                self.parse_length).apply(pd.Series)

                    if len(tunnel_lengths) == 1:
                        tunnel_lengths_data = tunnel_lengths[0]
                    else:
                        tunnel_lengths_data = dict(
                            zip([x.text for x in parsed_text.find_all('h3')],
                                tunnel_lengths))

                    last_updated_date = get_last_updated_date(url)

                    print("Done. ") if verbose == 2 else ""

                    page_railway_tunnel_lengths = {page_name: tunnel_lengths_data,
                                                   self.LUDKey: last_updated_date}

                    save_pickle(page_railway_tunnel_lengths, path_to_pickle,
                                verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(e))

        return page_railway_tunnel_lengths

    def fetch_tunnel_lengths(self, update=False, pickle_it=False, data_dir=None,
                             verbose=False):
        """
        Fetch data of railway tunnel lengths from local backup.

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
        :return: railway tunnel lengths data
            (including the name, length, owner and relative location) and
            date of when the data was last updated
        :rtype: dict

        **Example**::

            >>> from pyrcs.other_assets import Tunnels

            >>> tunnels = Tunnels()

            >>> tunnel_lengths_data = tunnels.fetch_tunnel_lengths()

            >>> type(tunnel_lengths_data)
            <class 'dict'>
            >>> print(list(tunnel_lengths_data.keys()))
            ['Tunnels', 'Last updated date']

            >>> tunnel_lengths_dat = tunnel_lengths_data['Tunnels']
            >>> type(tunnel_lengths_dat)
            <class 'dict'>
            >>> print(list(tunnel_lengths_dat.keys()))
            ['Page 1 (A-F)', 'Page 2 (G-P)', 'Page 3 (Q-Z)', 'Page 4 (others)']
        """

        verbose_ = False if (data_dir or not verbose) else (2 if verbose == 2 else True)

        page_data = [
            self.collect_lengths_by_page(
                x, update=update, verbose=verbose_ if is_internet_connected() else False)
            for x in range(1, 5)]

        if all(x is None for x in page_data):
            if update:
                print_conn_err(verbose=verbose)
                print("No data of the {} has been freshly collected.".format(
                    self.Key.lower()))
            page_data = [self.collect_lengths_by_page(x, update=False, verbose=verbose_)
                         for x in range(1, 5)]

        railway_tunnel_lengths = {
            self.Key: {next(iter(x)): next(iter(x.values())) for x in page_data},
            self.LUDKey:
                max(next(itertools.islice(iter(x.values()), 1, 2)) for x in page_data)}

        if pickle_it and data_dir:
            self.CurrentDataDir = validate_input_data_dir(data_dir)
            path_to_pickle = os.path.join(
                self.CurrentDataDir, self.Key.lower().replace(" ", "-") + ".pickle")
            save_pickle(railway_tunnel_lengths, path_to_pickle, verbose=verbose)

        return railway_tunnel_lengths
