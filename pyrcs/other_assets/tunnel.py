"""
Collect data of `railway tunnel lengths <http://www.railwaycodes.org.uk/tunnels/tunnels0.shtm>`_.
"""

import itertools
import os
import re
import urllib.parse

import bs4
import numpy as np
import pandas as pd
import requests
from pyhelpers.dir import cd
from pyhelpers.ops import fake_requests_headers
from pyhelpers.store import load_data

from ..parser import get_catalogue, get_last_updated_date, parse_tr
from ..utils import home_page_url, init_data_dir, is_home_connectable, print_conn_err, \
    print_inst_conn_err, print_void_msg, save_data_to_file, validate_page_name


class Tunnels:
    """
    A class for collecting data of `railway tunnel lengths`_.

    .. _`railway tunnel lengths`: http://www.railwaycodes.org.uk/tunnels/tunnels0.shtm
    """

    #: Name of the data
    NAME = 'Railway tunnel lengths'
    #: Key of the `dict <https://docs.python.org/3/library/stdtypes.html#dict>`_-type data
    KEY = 'Tunnels'
    #: URL of the main web page of the data
    URL = urllib.parse.urljoin(home_page_url(), '/tunnels/tunnels0.shtm')
    #: Key of the data of the last updated date
    KEY_TO_LAST_UPDATED_DATE = 'Last updated date'

    def __init__(self, data_dir=None, update=False, verbose=True):
        """
        :param data_dir: name of data directory, defaults to ``None``
        :type data_dir: str or None
        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console, defaults to ``True``
        :type verbose: bool or int

        :ivar dict catalogue: catalogue of the data
        :ivar str last_updated_date: last updated date
        :ivar str data_dir: path to the data directory
        :ivar str current_data_dir: path to the current data directory

        **Examples**::

            >>> from pyrcs.other_assets import Tunnels  # from pyrcs import Tunnels

            >>> tunl = Tunnels()

            >>> print(tunl.NAME)
            Railway tunnel lengths

            >>> print(tunl.URL)
            http://www.railwaycodes.org.uk/tunnels/tunnels0.shtm
        """

        print_conn_err(verbose=verbose)

        self.catalogue = get_catalogue(url=self.URL, update=update, confirmation_required=False)

        self.last_updated_date = get_last_updated_date(url=self.URL, parsed=True, as_date_type=False)

        self.data_dir, self.current_data_dir = init_data_dir(self, data_dir, category="other-assets")

    def _cdd(self, *sub_dir, **kwargs):
        """
        Change directory to package data directory and subdirectories (and/or a file).

        The directory for this module: ``"data\\other-assets\\tunnels"``.

        :param sub_dir: subdirectory or subdirectories (and/or a file)
        :type sub_dir: str
        :param kwargs: [optional] parameters of the function `pyhelpers.dir.cd`_
        :return: path to the backup data directory for the class
            :py:class:`~pyrcs.other_assets.tunnel.Tunnels`
        :rtype: str

        .. _`pyhelpers.dir.cd`:
            https://pyhelpers.readthedocs.io/en/latest/_generated/pyhelpers.dir.cd.html
        """

        path = cd(self.data_dir, *sub_dir, mkdir=True, **kwargs)

        return path

    @staticmethod
    def parse_length(x):
        """
        Parse data in ``'Length'`` column, i.e. convert miles/yards to metres.

        :param x: raw length data
        :type x: str or None
        :return: parsed length data and, if any, additional information associated with it
        :rtype: tuple

        **Examples**::

            >>> from pyrcs.other_assets import Tunnels  # from pyrcs import Tunnels

            >>> tunl = Tunnels()

            >>> tunl.parse_length('')
            (nan, 'Unavailable')

            >>> tunl.parse_length('1m 182y')
            (1775.7648, None)

            >>> tunl.parse_length('formerly 0m236y')
            (215.7984, 'Formerly')

            >>> tunl.parse_length('0.325km (0m 356y)')
            (325.5264, '0.325km')

            >>> tunl.parse_length("0m 48yd- (['0m 58yd'])")
            (48.4632, '43.89-53.04 metres')
        """

        if '✖' in x:
            x, note_ = x.split('✖')
            note_ = ' (' + note_ + ')'
        else:
            note_ = ''

        if re.match(r'[Uu]nknown', x):
            length = np.nan
            note = 'Unknown'

        elif x == '':
            length = np.nan
            note = 'Unavailable'

        elif re.match(r'\d+m \d+yd?(- | to )?.*\d+m \d+yd?.*', x):
            miles_a, yards_a, miles_b, yards_b = re.findall(r'\d+', x)
            length_a = float(miles_a) * 1609.344 + float(yards_a) * 0.9144
            # measurement.measures.Distance(mi=miles_a).m + measurement.measures.Distance(yd=yards_a).m
            length_b = float(miles_b) * 1609.344 + float(yards_b) * 0.9144
            # measurement.measures.Distance(mi=miles_b).m + measurement.measures.Distance(yd=yards_b).m
            length = (length_a + length_b) / 2
            note = '-'.join([str(round(length_a, 2)), str(round(length_b, 2))]) + ' metres'

        else:
            if re.match(r'(formerly )?c?≈?\d+m ?\d+yd?|ch', x):
                miles, yards = re.findall(r'\d+', x)
                if re.match(r'.*\d+ch$', x):  # "yards" is "chains"
                    yards = yards * 22  # measurement.measures.Distance(chain=yards).yd

                if re.match(r'^c.*|^≈', x):
                    note = 'Approximate'
                elif re.match(r'\d+y$', x):
                    note = re.search(r'(?<=\dy).*$', x).group(0)
                elif re.match(r'^(formerly).*', x):
                    note = 'Formerly'
                else:
                    note = ''

            elif re.match(r'\d+\.\d+km(\r)? .*(\[\')?\(\d+m \d+yd?\).*', x):
                miles, yards = re.findall(r'\d+', re.search(r'(?<=\()\d+.*(?=\))', x).group(0))
                note = re.search(r'.+(?= (\[\')?\()', x.replace('\r', '')).group(0)

            else:
                miles, yards = 0, 0
                note = ''

            length = float(miles) * 1609.344 + float(yards) * 0.9144
            # measurement.measures.Distance(mi=miles).m + measurement.measures.Distance(yd=yards).m

            if note != '':
                note = note + note_

        return length, note

    def collect_codes_by_page(self, page_no, update=False, verbose=False):
        """
        Collect data of `railway tunnel lengths`_ for a page number from source web page.

        .. _`railway tunnel lengths`: http://www.railwaycodes.org.uk/tunnels/tunnels0.shtm

        :param page_no: page number; valid values include ``1``, ``2``, ``3`` and ``4``
        :type page_no: int or str
        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of tunnel lengths on page ``page_no`` and
            date of when the data was last updated
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Tunnels  # from pyrcs import Tunnels

            >>> tunl = Tunnels()

            >>> tunl_len_1 = tunl.collect_codes_by_page(page_no=1)
            >>> type(tunl_len_1)
            dict
            >>> list(tunl_len_1.keys())
            ['Page 1 (A-F)', 'Last updated date']

            >>> tunl_len_1_codes = tunl_len_1['Page 1 (A-F)']
            >>> type(tunl_len_1_codes)
            pandas.core.frame.DataFrame
            >>> tunl_len_1_codes.head()
                         Name  Other names, remarks  ... Length (metres) Length (note)
            0    Abbotscliffe                        ...       1775.7648
            1      Abercanaid           see Merthyr  ...             NaN   Unavailable
            2     Aberchalder         see Loch Oich  ...             NaN   Unavailable
            3  Aberdovey No 1  also called Frongoch  ...        182.8800
            4  Aberdovey No 2    also called Morfor  ...        200.2536

            [5 rows x 11 columns]

            >>> tunl_len_4 = tunl.collect_codes_by_page(page_no=4)
            >>> type(tunl_len_4)
            dict
            >>> list(tunl_len_4.keys())
            ['Page 4 (others)', 'Last updated date']

            >>> tunl_len_4_codes = tunl_len_4['Page 4 (others)']
            >>> type(tunl_len_4_codes)
            dict
            >>> list(tunl_len_4_codes.keys())
            ['Tunnels on industrial and other minor lines',
             'Large bridges that are not officially tunnels but could appear to be so']

            >>> tunl_len_4_dat = tunl_len_4_codes['Tunnels on industrial and other minor lines']
            >>> type(tunl_len_4_dat)
            pandas.core.frame.DataFrame
            >>> tunl_len_4_dat.head()
                                  Name Other names, remarks  ... Length (metres) Length (note)
            0             Ashes Quarry                       ...         56.6928
            1        Ashey Down Quarry                       ...         33.8328
            2  Baileycroft Quarry No 1                       ...         28.3464
            3  Baileycroft Quarry No 2                       ...         21.0312
            4            Basfords Hill                       ...         46.6344

            [5 rows x 6 columns]
        """

        page_name = validate_page_name(self, page_no, valid_page_no=set(range(1, 5)))

        data_name = re.sub(r"[()]", "", re.sub(r"[ -]", "-", page_name)).lower()
        ext = ".pickle"
        path_to_pickle = self._cdd(data_name + ext)

        if os.path.exists(path_to_pickle) and not update:
            codes_on_page = load_data(path_to_pickle)

        else:
            if verbose == 2:
                print("Collecting {} data ({})".format(self.KEY.lower(), page_name), end=" ... ")

            codes_on_page = None

            try:
                url = self.catalogue[page_name]
                # url = tunl.catalogue[page_name]
                source = requests.get(url=url, headers=fake_requests_headers())

            except Exception as e:
                if verbose == 2:
                    print("Failed. ", end="")
                print_inst_conn_err(verbose=verbose, e=e)

            else:
                try:
                    soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

                    theads, tbodies = soup.find_all('thead'), soup.find_all('tbody')

                    codes_dat = []
                    for thead, tbody in zip(theads, tbodies):
                        ths = [th.text.strip() for th in thead.find_all('th')]
                        trs = tbody.find_all('tr')
                        dat = parse_tr(trs=trs, ths=ths, as_dataframe=True)

                        temp = [re.match('^Between.*', x) or x == '' for x in dat.columns]
                        if bool(temp):
                            indices = list(itertools.compress(range(len(temp)), temp))
                            if len(indices) == 2:
                                new_cols = ['Station A', 'Station B']
                                repl_col_names = dict(zip(dat.columns[indices].to_list(), new_cols))
                                dat.rename(columns=repl_col_names, inplace=True)

                        codes_dat.append(dat)

                    len_cols = ['Length (metres)', 'Length (note)']
                    for i, dat in enumerate(codes_dat):
                        codes_dat[i][len_cols] = dat['Length'].map(self.parse_length).apply(pd.Series)

                    if len(codes_dat) == 1:
                        codes_ = codes_dat[0]
                    else:
                        codes_ = dict(zip([x.text.strip() for x in soup.find_all('h3')], codes_dat))

                    last_updated_date = get_last_updated_date(url=url)

                    codes_on_page = {page_name: codes_, self.KEY_TO_LAST_UPDATED_DATE: last_updated_date}

                    if verbose == 2:
                        print("Done.")

                    save_data_to_file(
                        self, data=codes_on_page, data_name=data_name, ext=ext, verbose=verbose)

                except Exception as e:
                    print("Failed. \"{}\": {}".format(page_name, e))

        return codes_on_page

    def fetch_codes(self, update=False, dump_dir=None, verbose=False):
        """
        Fetch data of `railway tunnel lengths`_.

        .. _`railway tunnel lengths`: http://www.railwaycodes.org.uk/tunnels/tunnels0.shtm

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param dump_dir: name of a folder where the pickle file is to be saved, defaults to ``None``
        :type dump_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of railway tunnel lengths
            (including the name, length, owner and relative location) and
            date of when the data was last updated
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Tunnels  # from pyrcs import Tunnels

            >>> tunl = Tunnels()

            >>> tunl_len_codes = tunl.fetch_codes()

            >>> type(tunl_len_codes)
            dict
            >>> list(tunl_len_codes.keys())
            ['Tunnels', 'Last updated date']

            >>> tunl.KEY
            'Tunnels'

            >>> tunl_len_codes_dat = tunl_len_codes[tunl.KEY]
            >>> type(tunl_len_codes_dat)
            dict
            >>> list(tunl_len_codes_dat.keys())
            ['Page 1 (A-F)', 'Page 2 (G-P)', 'Page 3 (Q-Z)', 'Page 4 (others)']

            >>> page_1 = tunl_len_codes_dat['Page 1 (A-F)']
            >>> type(page_1)
            pandas.core.frame.DataFrame
            >>> page_1.head()
                         Name  Other names, remarks  ... Length (metres) Length (note)
            0    Abbotscliffe                        ...       1775.7648
            1      Abercanaid           see Merthyr  ...             NaN   Unavailable
            2     Aberchalder         see Loch Oich  ...             NaN   Unavailable
            3  Aberdovey No 1  also called Frongoch  ...        182.8800
            4  Aberdovey No 2    also called Morfor  ...        200.2536

            [5 rows x 11 columns]
        """

        verbose_1 = False if (dump_dir or not verbose) else (2 if verbose == 2 else True)
        verbose_2 = verbose_1 if is_home_connectable() else False

        codes_on_pages = [
            self.collect_codes_by_page(x, update=update, verbose=verbose_2) for x in range(1, 5)]

        if all(x is None for x in codes_on_pages):
            if update:
                print_inst_conn_err(verbose=verbose)
                print_void_msg(data_name=self.KEY, verbose=verbose)

            codes_on_pages = [
                self.collect_codes_by_page(x, update=False, verbose=verbose_1) for x in range(1, 5)]

        tunnel_lengths = {
            self.KEY: {next(iter(x)): next(iter(x.values())) for x in codes_on_pages},
            self.KEY_TO_LAST_UPDATED_DATE:
                max(next(itertools.islice(iter(x.values()), 1, 2)) for x in codes_on_pages),
        }

        if dump_dir is not None:
            save_data_to_file(
                self, data=tunnel_lengths, data_name=self.KEY, ext=".pickle",
                dump_dir=dump_dir, verbose=verbose)

        return tunnel_lengths
