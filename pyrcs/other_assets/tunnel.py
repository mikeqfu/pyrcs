"""
Collects data of `railway tunnel lengths <http://www.railwaycodes.org.uk/tunnels/tunnels0.shtm>`_.
"""

import itertools
import re
import urllib.parse

import bs4
import numpy as np
import pandas as pd

from .._base import _Base
from ..parser import _get_last_updated_date, parse_tr
from ..utils import home_page_url, is_home_connectable, print_inst_conn_err, print_void_msg, \
    validate_page_name


class Tunnels(_Base):
    """
    A class for collecting data of
    `railway tunnel lengths <http://www.railwaycodes.org.uk/tunnels/tunnels0.shtm>`_.
    """

    #: The name of the data.
    NAME: str = 'Railway tunnel lengths'
    #: The key for accessing the data.
    KEY: str = 'Tunnels'

    #: The URL of the main web page for the data.
    URL: str = urllib.parse.urljoin(home_page_url(), '/tunnels/tunnels0.shtm')

    #: The key used to reference the last updated date in the data.
    KEY_TO_LAST_UPDATED_DATE: str = 'Last updated date'

    def __init__(self, data_dir=None, update=False, verbose=True):
        """
        :param data_dir: The name of the directory for storing the data; defaults to ``None``.
        :type data_dir: str | None
        :param update: Whether to check for updates to the catalogue; defaults to ``False``.
        :type update: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``True``.
        :type verbose: bool | int

        :ivar dict catalogue: The catalogue of the data.
        :ivar str last_updated_date: The date when the data was last updated.
        :ivar str data_dir: The path to the directory containing the data.
        :ivar str current_data_dir: The path to the current data directory.

        **Examples**::

            >>> from pyrcs.other_assets import Tunnels  # from pyrcs import Tunnels
            >>> tunl = Tunnels()
            >>> tunl.NAME
            'Railway tunnel lengths'
            >>> tunl.URL
            'http://www.railwaycodes.org.uk/tunnels/tunnels0.shtm'
        """

        super().__init__(
            data_dir=data_dir, content_type='catalogue', data_category="other-assets",
            update=update, verbose=verbose)

        self.page_range = range(1, 5)

    @staticmethod
    def _parse_length(x):
        """
        Parses data in ``'Length'`` column, i.e. convert miles/yards to metres.

        :param x: Raw length data.
        :type x: str | None
        :return: The parsed length data and, if any, additional information associated with it.
        :rtype: tuple

        **Examples**::

            >>> from pyrcs.other_assets import Tunnels  # from pyrcs import Tunnels
            >>> tunl = Tunnels()
            >>> tunl._parse_length('')
            (nan, 'Unavailable')
            >>> tunl._parse_length('1m 182y')
            (1775.7648, None)
            >>> tunl._parse_length('formerly 0m236y')
            (215.7984, 'Formerly')
            >>> tunl._parse_length('0.325km (0m 356y)')
            (325.5264, '0.325km')
            >>> tunl._parse_length("0m 48yd- (['0m 58yd'])")
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

    def _collect_codes(self, page_no, source, verbose=False):
        page_name = validate_page_name(self, page_no, valid_page_no=self.page_range)

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
            temp = dat['Length'].map(self._parse_length)
            codes_dat[i][len_cols] = pd.DataFrame(zip(*temp)).T

        if len(codes_dat) == 1:
            codes_ = codes_dat[0]
        else:
            codes_ = dict(zip([x.text.strip() for x in soup.find_all('h3')], codes_dat))

        codes_on_page = {
            page_name: codes_,
            self.KEY_TO_LAST_UPDATED_DATE: _get_last_updated_date(soup=soup),
        }

        if verbose in {True, 1}:
            print("Done.")

        data_name = re.sub(r"[()]", "", re.sub(r"[ -]", "-", page_name)).lower()
        self._save_data_to_file(data=codes_on_page, data_name=data_name, verbose=verbose)

        return codes_on_page

    def collect_codes(self, page_no, confirmation_required=True, verbose=False, raise_error=False):
        """
        Collects data of `railway tunnel lengths`_ for a specified page number
        from the source web page.

        .. _`railway tunnel lengths`: http://www.railwaycodes.org.uk/tunnels/tunnels0.shtm

        :param page_no: The page number to collect data from;
            valid values are ``1``, ``2``, ``3`` and ``4``.
        :type page_no: int | str
        :param confirmation_required: Whether user confirmation is required;
            if ``confirmation_required=True`` (default), prompts the user for confirmation
            before proceeding with data collection.
        :type confirmation_required: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :param raise_error: Whether to raise the provided exception;
            if ``raise_error=False`` (default), the error will be suppressed.
        :type raise_error: bool
        :return: A dictionary containing the data of tunnel lengths for the specified ``page_no``
            and the date of when the data was last updated.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Tunnels  # from pyrcs import Tunnels
            >>> tunl = Tunnels()
            >>> page_1 = tunl.collect_codes(page_no=1)
            >>> type(page_1)
            dict
            >>> list(page_1.keys())
            ['Page 1 (A-F)', 'Last updated date']
            >>> page_1_codes = page_1['Page 1 (A-F)']
            >>> type(page_1_codes)
            pandas.core.frame.DataFrame
            >>> page_1_codes.head()
                         Name  Other names, remarks  ... Length (metres) Length (note)
            0    Abbotscliffe                        ...       1775.7648
            1      Abercanaid           see Merthyr  ...             NaN   Unavailable
            2     Aberchalder         see Loch Oich  ...             NaN   Unavailable
            3  Aberdovey No 1  also called Frongoch  ...        182.8800
            4  Aberdovey No 2    also called Morfor  ...        200.2536
            [5 rows x 10 columns]
            >>> page_4 = tunl.collect_codes(page_no=4)
            >>> type(page_4)
            dict
            >>> list(page_4.keys())
            ['Page 4 (others)', 'Last updated date']
            >>> page_4_codes = page_4['Page 4 (others)']
            >>> type(page_4_codes)
            dict
            >>> list(page_4_codes.keys())
            ['Tunnels on industrial and other minor lines',
             'Large bridges that are not officially tunnels but could appear to be so']
            >>> key1 = 'Tunnels on industrial and other minor lines'
            >>> page_4_dat = page_4_codes[key1]
            >>> type(page_4_dat)
            pandas.core.frame.DataFrame
            >>> page_4_dat.head()
                                  Name Other names, remarks  ... Length (metres) Length (note)
            0             Ashes Quarry                       ...         56.6928
            1        Ashey Down Quarry                       ...         33.8328
            2  Baileycroft Quarry No 1                       ...         28.3464
            3  Baileycroft Quarry No 2                       ...         21.0312
            4            Basfords Hill                       ...         46.6344
            [5 rows x 6 columns]
            >>> key2 = 'Large bridges that are not officially tunnels but could appear to be so'
            >>> page_4_dat_ = page_4_codes[key2]
            >>> type(page_4_dat_)
            pandas.core.frame.DataFrame
            >>> page_4_dat_.head()
                            Name Other names, remarks  ... Length (metres) Length (note)
            0  A470/A472 (north)                       ...         35.6616
            1  A470/A472 (south)                       ...         28.3464
            2               A720                       ...        145.3896
            3                 A9        Aberdeen line  ...        141.7320
            4                 A9           Perth line  ...        146.3040
            [5 rows x 8 columns]
        """

        data_name = self.NAME.lower()

        page_name = validate_page_name(self, page_no, valid_page_no=self.page_range)

        data = self._collect_data_from_source(
            data_name=data_name,
            method=self._collect_codes, initial=page_name, page_no=page_no,
            url=self.catalogue.get(page_name), confirmation_required=confirmation_required,
            confirmation_prompt=f"To collect data of {data_name} ({page_name})\n?",
            verbose=verbose, raise_error=raise_error)

        return data

    def fetch_codes(self, page_no=None, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetches the data of `railway tunnel lengths`_.

        .. _`railway tunnel lengths`: http://www.railwaycodes.org.uk/tunnels/tunnels0.shtm

        :param page_no: The page number to collect data from;
            valid values are ``1``, ``2``, ``3`` and ``4``; defaults to ``None``.
        :type page_no: int | str
        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the data of tunnel lengths
            (including the name, length, owner and relative location) and
            the date of when the data was last updated.
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
            >>> page_1_codes = tunl_len_codes_dat['Page 1 (A-F)']
            >>> type(page_1_codes)
            pandas.core.frame.DataFrame
            >>> page_1_codes.head()
                         Name  Other names, remarks  ... Length (metres) Length (note)
            0    Abbotscliffe                        ...       1775.7648
            1      Abercanaid           see Merthyr  ...             NaN   Unavailable
            2     Aberchalder         see Loch Oich  ...             NaN   Unavailable
            3  Aberdovey No 1  also called Frongoch  ...        182.8800
            4  Aberdovey No 2    also called Morfor  ...        200.2536
            [5 rows x 10 columns]
            >>> page_4_codes = tunl_len_codes_dat['Page 4 (others)']
            >>> type(page_4_codes)
            dict
            >>> list(page_4_codes.keys())
            ['Tunnels on industrial and other minor lines',
             'Large bridges that are not officially tunnels but could appear to be so']
            >>> key1 = 'Tunnels on industrial and other minor lines'
            >>> page_4_dat = page_4_codes[key1]
            >>> type(page_4_dat)
            pandas.core.frame.DataFrame
            >>> page_4_dat.head()
                                  Name Other names, remarks  ... Length (metres) Length (note)
            0             Ashes Quarry                       ...         56.6928
            1        Ashey Down Quarry                       ...         33.8328
            2  Baileycroft Quarry No 1                       ...         28.3464
            3  Baileycroft Quarry No 2                       ...         21.0312
            4            Basfords Hill                       ...         46.6344
            [5 rows x 6 columns]
            >>> key2 = 'Large bridges that are not officially tunnels but could appear to be so'
            >>> page_4_dat_ = page_4_codes[key2]
            >>> type(page_4_dat_)
            pandas.core.frame.DataFrame
            >>> page_4_dat_.head()
                            Name Other names, remarks  ... Length (metres) Length (note)
            0  A470/A472 (north)                       ...         35.6616
            1  A470/A472 (south)                       ...         28.3464
            2               A720                       ...        145.3896
            3                 A9        Aberdeen line  ...        141.7320
            4                 A9           Perth line  ...        146.3040
            [5 rows x 8 columns]
        """

        if page_no:
            page_name = validate_page_name(self, page_no, valid_page_no=self.page_range)

            args = {
                'data_name': re.sub(r"[()]", "", re.sub(r"[ -]", "-", page_name)).lower(),
                'method': self.collect_codes,
                'page_no': page_no,
            }
            kwargs.update(args)

            tunnel_lengths = self._fetch_data_from_file(
                update=update, dump_dir=dump_dir, verbose=verbose, **kwargs)

        else:
            verbose_1 = False if (dump_dir or not verbose) else (2 if verbose == 2 else True)
            verbose_2 = verbose_1 if is_home_connectable() else False

            codes_on_pages = [
                self.fetch_codes(x, update=update, verbose=verbose_2) for x in self.page_range]

            if all(x is None for x in codes_on_pages):
                if update:
                    print_inst_conn_err(verbose=verbose)
                    print_void_msg(data_name=self.KEY, verbose=verbose)

                codes_on_pages = [
                    self.fetch_codes(x, update=False, verbose=verbose_1) for x in self.page_range]

            tunnel_lengths = {
                self.KEY: {next(iter(x)): next(iter(x.values())) for x in codes_on_pages},
                self.KEY_TO_LAST_UPDATED_DATE:
                    max(next(itertools.islice(iter(x.values()), 1, 2)) for x in codes_on_pages),
            }

        if dump_dir is not None:
            self._save_data_to_file(
                data=tunnel_lengths, data_name=self.KEY, dump_dir=dump_dir, verbose=verbose)

        return tunnel_lengths
