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
from ..utils import handle_connection_error, homepage_url, is_homepage_connectable, \
    print_void_collection_message, validate_page_name


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
    URL: str = urllib.parse.urljoin(homepage_url(), '/tunnels/tunnels0.shtm')

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
        Parse raw length data to convert imperial measurements to metres.

        This method extracts miles and yards (or chains) from the raw string, converts
        them to metres and identifies additional textual notes or approximations.

        :param x: The raw length data string to parse.
        :type x: str | None
        :return: A tuple containing the parsed length in metres and any associated notes.
        :rtype: tuple[float, str]

        **Examples**::

            >>> from pyrcs.other_assets import Tunnels  # from pyrcs import Tunnels

            >>> tunl = Tunnels()

            >>> tunl._parse_length('')
            (nan, 'Unavailable')

            >>> tunl._parse_length('1m 182y')
            (1775.7648, '')

            >>> tunl._parse_length('formerly 0m236y')
            (215.7984, 'Formerly')

            >>> tunl._parse_length('0.325km (0m 356y)')
            (325.5264, '0.325km')

            >>> tunl._parse_length("0m 48yd- (['0m 58yd'])")
            (48.4632, '43.89-53.04 metres')
        """

        if not isinstance(x, str) or not x.strip():
            return np.nan, 'Unavailable'

        # Normalise all whitespace (including \r, \n) into a single space
        x = re.sub(r'\s+', ' ', x.strip())

        note_suffix = ''
        if '✖' in x:
            parts = x.split('✖', 1)
            x = parts[0].strip()
            note_suffix = f" ({parts[1].strip()})"

        if re.match(r'(?i)unknown', x):
            return np.nan, ('Unknown' + note_suffix).strip()

        # 1. Range format (e.g. "0m 48yd- (['0m 58yd'])")
        range_match = re.search(r'(\d+)m\s*(\d+)yd?.*?(\d+)m\s*(\d+)yd?', x, flags=re.IGNORECASE)
        if range_match:
            m1, y1, m2, y2 = map(float, range_match.groups())
            len1 = m1 * 1609.344 + y1 * 0.9144
            len2 = m2 * 1609.344 + y2 * 0.9144
            length = (len1 + len2) / 2.0
            note = f"{len1:.2f}-{len2:.2f} metres"
            return length, (note + note_suffix).strip()

        # 2. Metric prefix format (e.g. "0.325km (0m 356y)")
        metric_match = re.search(r'([\d.]+km).*?(\d+)m\s*(\d+)yd?', x, flags=re.IGNORECASE)
        if metric_match:
            note_prefix, m, y = metric_match.groups()
            length = float(m) * 1609.344 + float(y) * 0.9144
            return length, (note_prefix + note_suffix).strip()

        # 3. Standard imperial format (e.g. "formerly 0m 236y", "c1m 22ch")
        std_match = re.search(r'(\d+)m\s*(\d+)(yd?|ch)', x, flags=re.IGNORECASE)
        if std_match:
            m = float(std_match.group(1))
            val = float(std_match.group(2))
            unit = std_match.group(3).lower()

            yards = val * 22.0 if unit == 'ch' else val
            length = m * 1609.344 + yards * 0.9144

            x_lower = x.lower()
            if x_lower.startswith('c') or x_lower.startswith('≈'):
                note = 'Approximate'
            elif 'formerly' in x_lower:
                note = 'Formerly'
            else:
                # Isolate leftover string as a note, stripping noise characters
                residual = x[:std_match.start()] + x[std_match.end():]
                note = re.sub(r'^[-(\[\']+|[-)\]\']+$', '', residual.strip()).strip()

            return length, (note + note_suffix).strip()

        # 4. Unmatched format fallback
        return np.nan, note_suffix.strip()

    def _parse_and_save_page(self, page_no, source, verbose=False):
        """
        Parse raw HTML source to extract tunnel lengths and save the data to a file.

        This internal method acts as a callback for the data collection pipeline, extracting
        table data, formatting lengths and matching tables with their corresponding headings.

        :param page_no: The page number associated with the source.
        :type page_no: int | str
        :param source: The raw HTML source content response.
        :type source: requests.Response | Any
        :param verbose: Whether to print progress messages to the console;
            defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the parsed DataFrame(s) and the last updated date.
        :rtype: dict
        """

        page_name = validate_page_name(self, page_no, valid_page_no=self.page_range)

        soup = bs4.BeautifulSoup(source.content, features='html.parser')
        last_updated_date = _get_last_updated_date(soup=soup)

        theads, tbodies = soup.find_all('thead'), soup.find_all('tbody')

        tunnels_codes = []
        for thead, tbody in zip(theads, tbodies):
            ths = [th.text.strip() for th in thead.find_all('th')]
            trs = tbody.find_all('tr')
            dat: pd.DataFrame = parse_tr(trs=trs, ths=ths, as_dataframe=True)

            # Identify columns that are empty or start with 'Between'
            col_mask = [bool(re.match(r'^Between.*', str(x))) or x == '' for x in dat.columns]

            # Use 'any' to correctly evaluate if a column matched, avoiding 'bool(list)' bug
            if any(col_mask):
                indices = [i for i, val in enumerate(col_mask) if val]
                if len(indices) == 2:
                    dat = dat.rename(columns={
                        dat.columns[indices[0]]: 'Station A',
                        dat.columns[indices[1]]: 'Station B'
                    })

            # Expand the parsed lengths idiomatically into two distinct columns
            if 'Length' in dat.columns:
                parsed_lengths = dat['Length'].map(self._parse_length)
                dat[['Length (metres)', 'Length (note)']] = pd.DataFrame(
                    parsed_lengths.tolist(), index=dat.index
                )

            tunnels_codes.append(dat)

        # Map to specific structures based on the count of parsed tables
        if len(tunnels_codes) == 1:
            tunnels_codes = tunnels_codes[0]
        elif len(tunnels_codes) > 1:
            h3_tags = [h3.get_text(strip=True) for h3 in soup.find_all('h3')]
            tunnels_codes = dict(zip(h3_tags, tunnels_codes))
        else:
            tunnels_codes = None

        tunnels_data = {page_name: tunnels_codes, self.KEY_TO_LAST_UPDATED_DATE: last_updated_date}

        if verbose in {True, 1}:
            print("Done.")

        # Clean filename characters and replace multiple spaces/dashes with a single dash
        data_name = re.sub(r"[()]", "", re.sub(r"[ -]", "-", page_name)).lower()
        self._save_data_to_file(tunnels_data, data_name=data_name, verbose=verbose)

        return tunnels_data

    def collect_codes(self, page_no, confirmation_required=True, verbose=False, raise_error=False):
        """
        Collect data of `railway tunnel lengths`_ for a specific page from the source web page.

        .. _`railway tunnel lengths`: http://www.railwaycodes.org.uk/tunnels/tunnels0.shtm

        This method coordinates the retrieval process by requesting the target page from
        the source and parsing the structural table information.

        :param page_no: The page number to collect data from;
            valid values are ``1``, ``2``, ``3`` and ``4``.
        :type page_no: int | str
        :param confirmation_required: Whether user confirmation is required;
            if ``True`` (default), prompts the user before proceeding.
        :type confirmation_required: bool
        :param verbose: Whether to print status information to the console. Defaults to ``False``.
        :type verbose: bool | int
        :param raise_error: Whether to raise exceptions encountered during retrieval;
            if ``False`` (default), errors are suppressed.
        :type raise_error: bool
        :return: A dictionary containing the tunnel length data and the last updated date.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.other_assets import Tunnels  # from pyrcs import Tunnels

            >>> tunl = Tunnels()

            >>> tunnels_page_1_data: dict = tunl.collect_codes(page_no=1, verbose=True)
            Proceed with collecting data of railway tunnel lengths (Page 1 (A-F))?
             [No]|Yes: yes
            Collecting the data ... Done.

            >>> list(tunnels_page_1_data)
            ['Page 1 (A-F)', 'Last updated date']

            >>> tunnels_page_1_codes = tunnels_page_1_data['Page 1 (A-F)']

            >>> type(tunnels_page_1_codes)
            pandas.DataFrame
            >>> tunnels_page_1_codes.shape
            (777, 11)
            >>> tunnels_page_1_codes.head()
                         Name  Other names, remarks  ... Length (metres) Length (note)
            0    Abbotscliffe                        ...       1775.7648
            1      Abercanaid           see Merthyr  ...             NaN   Unavailable
            2     Aberchalder         see Loch Oich  ...             NaN   Unavailable
            3  Aberdovey No 1  also called Frongoch  ...          182.88
            4  Aberdovey No 2    also called Morfor  ...        200.2536
            [5 rows x 11 columns]

            >>> tunnels_page_4_data: dict = tunl.collect_codes(page_no=4, verbose=True)
            Proceed with collecting data of railway tunnel lengths (Page 4 (others))?
             [No]|Yes: yes
            Collecting the data ... Done.

            >>> list(tunnels_page_4_data)
            ['Page 4 (others)', 'Last updated date']
            >>> tunnels_page_4_codes = tunnels_page_4_data['Page 4 (others)']

            >>> type(tunnels_page_4_codes)
            dict
            >>> list(tunnels_page_4_codes)
            ['Tunnels on industrial and other minor lines',
             'Large bridges that are not officially tunnels but could appear to be so']

            >>> page_4_1 = tunnels_page_4_codes['Tunnels on industrial and other minor lines']
            >>> type(page_4_1)
            pandas.DataFrame
            >>> page_4_1.shape
            (107, 6)
            >>> page_4_1.head()
                                  Name Other names, remarks  ... Length (metres) Length (note)
            0             Ashes Quarry                       ...         56.6928
            1        Ashey Down Quarry                       ...         33.8328
            2  Baileycroft Quarry No 1                       ...         28.3464
            3  Baileycroft Quarry No 2                       ...         21.0312
            4            Basfords Hill                       ...         46.6344
            [5 rows x 6 columns]

            >>> page_4_2 = tunnels_page_4_codes[
            ...     'Large bridges that are not officially tunnels but could appear to be so']
            >>> type(page_4_2)
            pandas.DataFrame
            >>> page_4_2.shape
            (16, 8)
            >>> page_4_2.head()
                            Name Other names, remarks  ... Length (metres) Length (note)
            0  A470/A472 (north)                       ...         35.6616
            1  A470/A472 (south)                       ...         28.3464
            2               A720                       ...        145.3896
            3                 A9        Aberdeen line  ...         141.732
            4                 A9           Perth line  ...         146.304
            [5 rows x 8 columns]
        """

        tunnels_data = self._collect_data_from_source_by_page(
            page_no=page_no,
            method=self._parse_and_save_page,
            confirmation_required=confirmation_required,
            verbose=verbose,
            raise_error=raise_error
        )

        return tunnels_data

    def fetch_codes(self, page_no=None, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetch data of `railway tunnel lengths`_.

        .. _`railway tunnel lengths`: http://www.railwaycodes.org.uk/tunnels/tunnels0.shtm

        :param page_no: The page number to collect data from;
            valid values are ``1``, ``2``, ``3`` and ``4``. Defaults to ``None``.
        :type page_no: int | str | None
        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved.
            Defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console. Defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the data of tunnel lengths (including the name, length,
            owner and relative location) and the date of when the data was last updated.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.other_assets import Tunnels  # from pyrcs import Tunnels

            >>> tunl = Tunnels()

            >>> tunnels_lengths_data: dict = tunl.fetch_codes()

            >>> list(tunnels_lengths_data)
            ['Tunnels', 'Last updated date']
            >>> tunl.KEY
            'Tunnels'

            >>> tunnels_lengths_dat = tunnels_lengths_data[tunl.KEY]
            >>> type(tunnels_lengths_dat)
            dict
            >>> list(tunnels_lengths_dat.keys())
            ['Page 1 (A-F)', 'Page 2 (G-P)', 'Page 3 (Q-Z)', 'Page 4 (others)']

            >>> tunnels_page_1_codes = tunnels_lengths_dat['Page 1 (A-F)']

            >>> type(tunnels_page_1_codes)
            pandas.DataFrame
            >>> tunnels_page_1_codes.shape
            (777, 11)
            >>> tunnels_page_1_codes.head()
                         Name  Other names, remarks  ... Length (metres) Length (note)
            0    Abbotscliffe                        ...       1775.7648
            1      Abercanaid           see Merthyr  ...             NaN   Unavailable
            2     Aberchalder         see Loch Oich  ...             NaN   Unavailable
            3  Aberdovey No 1  also called Frongoch  ...          182.88
            4  Aberdovey No 2    also called Morfor  ...        200.2536
            [5 rows x 11 columns]

            >>> tunnels_page_4_data: dict = tunl.collect_codes(page_no=4, verbose=True)
            Proceed with collecting data of railway tunnel lengths (Page 4 (others))?
             [No]|Yes: yes
            Collecting the data ... Done.

            >>> list(tunnels_page_4_data)
            ['Page 4 (others)', 'Last updated date']
            >>> tunnels_page_4_codes = tunnels_page_4_data['Page 4 (others)']

            >>> type(tunnels_page_4_codes)
            dict
            >>> list(tunnels_page_4_codes)
            ['Tunnels on industrial and other minor lines',
             'Large bridges that are not officially tunnels but could appear to be so']

            >>> page_4_1 = tunnels_page_4_codes['Tunnels on industrial and other minor lines']
            >>> type(page_4_1)
            pandas.DataFrame
            >>> page_4_1.shape
            (107, 6)
            >>> page_4_1.head()
                                  Name Other names, remarks  ... Length (metres) Length (note)
            0             Ashes Quarry                       ...         56.6928
            1        Ashey Down Quarry                       ...         33.8328
            2  Baileycroft Quarry No 1                       ...         28.3464
            3  Baileycroft Quarry No 2                       ...         21.0312
            4            Basfords Hill                       ...         46.6344
            [5 rows x 6 columns]

            >>> page_4_2 = tunnels_page_4_codes[
            ...     'Large bridges that are not officially tunnels but could appear to be so']
            >>> type(page_4_2)
            pandas.DataFrame
            >>> page_4_2.shape
            (16, 8)
            >>> page_4_2.head()
                            Name Other names, remarks  ... Length (metres) Length (note)
            0  A470/A472 (north)                       ...         35.6616
            1  A470/A472 (south)                       ...         28.3464
            2               A720                       ...        145.3896
            3                 A9        Aberdeen line  ...         141.732
            4                 A9           Perth line  ...         146.304
            [5 rows x 8 columns]
        """

        if page_no:
            page_name = validate_page_name(self, page_no, valid_page_no=self.page_range)

            args = {
                'data_name': re.sub(r"[()]", "", re.sub(r"[ -]", "-", page_name)).lower(),
                'method': self.collect_codes,
                'page_no': page_no,
            } | kwargs

            tunnel_lengths = self._fetch_data_from_file(
                update=update,
                dump_dir=dump_dir,
                verbose=verbose,
                **args
            )

        else:
            verbose_1 = False if (dump_dir or not verbose) else (2 if verbose == 2 else True)
            verbose_2 = verbose_1 if is_homepage_connectable() else False

            codes_on_pages: list[dict] = [
                self.fetch_codes(x, update=update, verbose=verbose_2) for x in self.page_range
            ]

            if all(x is None for x in codes_on_pages):
                if update:
                    handle_connection_error(verbose=verbose)
                    print_void_collection_message(data_name=self.KEY, verbose=verbose)

                codes_on_pages = [
                    self.fetch_codes(x, update=False, verbose=verbose_1) for x in self.page_range
                ]

            tunnel_lengths = {
                self.KEY:
                    {next(iter(x)): next(iter(x.values())) for x in codes_on_pages},
                self.KEY_TO_LAST_UPDATED_DATE:
                    max(next(itertools.islice(iter(x.values()), 1, 2)) for x in codes_on_pages),
            }

        if dump_dir is not None:
            self._save_data_to_file(
                data=tunnel_lengths,
                data_name=self.KEY,
                dump_dir=dump_dir,
                verbose=verbose
            )

        return tunnel_lengths
