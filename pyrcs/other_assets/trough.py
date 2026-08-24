"""
Collects codes of `water troughs <http://www.railwaycodes.org.uk/misc/troughs.shtm>`_.
"""

import re
import urllib.parse

import bs4
import numpy as np
import pandas as pd
import unicodedata

from .._base import _Base
from ..parser import _align_column_list_lengths, _parse_th_tag, parse_tr
from ..utils import homepage_url


def _expand_slash_delimited_rows(dat, target_cols):
    # noinspection shadowing-names
    """
    Expand multi-value slash-delimited rows into individual DataFrame records.

    This function identifies rows where target columns contain values separated by
    slashes, splits them into lists, aligns list lengths across target columns and
    explodes the row so each corresponding sub-entry forms an independent row.

    :param dat: The DataFrame containing tabular asset data.
    :type dat: pandas.DataFrame
    :param target_cols: List of column names to evaluate and expand.
    :type target_cols: list[str]
    :return: DataFrame with slash-delimited rows exploded into individual records.
    :rtype: pandas.DataFrame

    **Examples**::

        >>> import pandas as pd
        >>> df = pd.DataFrame({
        ...     'Mileage': ['7m 73ch to 8m 18ch / 7m 73ch to 8m 18ch'],
        ...     'Length': ['560yd / 560yd']
        ... })
        >>> expanded = _expand_slash_delimited_rows(df, ['Mileage', 'Length'])
        >>> len(expanded)
        2
    """

    if dat.empty:
        return dat

    cols = [c for c in target_cols if c in dat.columns]
    if not cols:
        return dat

    has_slash = dat[cols].map(
        lambda x: isinstance(x, str) and ' / ' in x
    ).any(axis=1)

    if not has_slash.any():
        return dat

    temp = dat.loc[has_slash].copy()

    for col in cols:
        temp[col] = temp[col].map(
            lambda x: [s.strip() for s in x.split('/')] if isinstance(x, str) else [x]
        )

    temp = _align_column_list_lengths(temp, cols)
    temp = temp.explode(cols, ignore_index=True)

    return pd.concat([dat.loc[~has_slash], temp], ignore_index=True)


def _decode_vulgar_fraction(s):
    """
    Decode a Unicode vulgar fraction character into its numeric float value.

    :param s: A string or character containing a Unicode vulgar fraction.
    :type s: str
    :return: The numeric value of the fraction, or ``None`` if no fraction exists.
    :rtype: float | None
    """

    if not isinstance(s, str):
        return None

    for char in s:
        try:
            if unicodedata.name(char, '').startswith('VULGAR FRACTION'):
                return unicodedata.numeric(char)
        except (TypeError, ValueError):
            pass

    return None


def _parse_length(x):
    """
    Parse a single yardage string into a numeric floating-point value.

    This function converts individual yardage entries containing plain integers,
    HTML fraction entities or Unicode vulgar fractions into floating-point numbers.

    :param x: The raw length string to parse.
    :type x: str | float | None
    :return: Parsed yardage in yards as a rounded float, or ``np.nan`` if invalid.
    :rtype: float

    **Examples**::

        >>> _parse_length('620yd')
        620.0
        >>> _parse_length('506⅔yd')
        506.67
        >>> _parse_length('557½yd')
        557.5
    """

    if not isinstance(x, str) or not x.strip():
        return np.nan

    cleaned = x.strip()
    if cleaned.lower().endswith('yd'):
        cleaned = cleaned[:-2].strip()

    # 1. HTML fraction entity format, e.g. '506&frac23;'
    match_html = re.fullmatch(r'(?:(\d+))?&frac(\d)(\d);?', cleaned)  # noqa
    if match_html:
        int_str, num_str, den_str = match_html.groups()
        int_val = float(int_str) if int_str else 0.0
        return round(int_val + int(num_str) / int(den_str), 2)

    # 2. Unicode vulgar fraction or plain number, e.g. '557½', '506⅔', '620'
    match_unicode = re.fullmatch(r'(?:(\d+))?([^\d\s])?', cleaned)  # noqa
    if match_unicode:
        int_str, frac_char = match_unicode.groups()
        if not int_str and not frac_char:
            return np.nan

        int_val = float(int_str) if int_str else 0.0
        if frac_char:
            frac_val = _decode_vulgar_fraction(frac_char)
            if frac_val is not None:
                return round(int_val + frac_val, 2)
        else:
            return round(int_val, 2)

    try:
        return round(float(cleaned), 2)
    except ValueError:
        return np.nan


class WaterTroughs(_Base):
    """
    A class for collecting data of
    `water troughs locations <http://www.railwaycodes.org.uk/features/troughs.shtm>`_.
    """

    #: The name of the data.
    NAME: str = 'Water trough locations'
    #: The key for accessing the data.
    KEY: str = 'Water troughs'
    #: The URL of the main web page for the data.
    URL: str = urllib.parse.urljoin(homepage_url(), '/features/troughs.shtm')
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

            >>> from pyrcs.other_assets import WaterTroughs  # from pyrcs import WaterTroughs
            >>> wt = WaterTroughs()
            >>> wt.NAME
            'Water trough locations'
        """

        super().__init__(
            data_dir=data_dir,
            data_category="other-assets",
            update=update,
            verbose=verbose
        )

    def _collect_codes(self, source, verbose=False):
        """
        Collect and parse water trough codes from the provided HTML source.

        This method extracts water trough location data, parses table structures,
        computes numeric yardage values and persists the resulting dataset.

        :param source: The HTTP response object, raw HTML content or parsed soup.
        :type source: requests.Response | bs4.BeautifulSoup | str
        :param verbose: Whether to print progress logs; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing parsed water trough codes and metadata.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import WaterTroughs
            >>> water_troughs = WaterTroughs()
            >>> # # Internal collection call
            >>> # data = water_troughs._collect_codes(source=source, verbose=True)
        """

        content = source.content if hasattr(source, 'content') else source
        soup = bs4.BeautifulSoup(markup=content, features='html.parser')

        thead = soup.find('thead')
        tbody = soup.find('tbody')

        if thead and tbody:
            ths = [_parse_th_tag(th) for th in thead.find_all('th')]
            trs = tbody.find_all('tr')
            dat: pd.DataFrame = parse_tr(trs=trs, ths=ths, as_dataframe=True)
        else:
            dat = pd.DataFrame()

        if not dat.empty:
            target_cols = ['Mileage', 'Length', 'Notes']
            dat = _expand_slash_delimited_rows(dat, target_cols)

            if 'Length' in dat.columns:
                dat['Length (Yard)'] = dat['Length'].map(_parse_length)

            if 'ELR' in dat.columns:
                dat = dat.sort_values('ELR')

        water_troughs_codes = self._pack_and_save_data(
            data=dat,
            soup=soup,
            dump_dir=self._cdd("..", "features"),
            verbose=verbose
        )

        return water_troughs_codes

    def collect_codes(self, confirmation_required=True, verbose=False, raise_error=False):
        # noinspection unresolved-references
        """
        Collect codes of `water troughs locations`_ from the source web page.

        .. _`water troughs locations`: http://www.railwaycodes.org.uk/misc/troughs.shtm

        :param confirmation_required: Whether user confirmation is required;
            if ``confirmation_required=True`` (default), prompts the user for confirmation
            before proceeding with data collection.
        :type confirmation_required: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :param raise_error: Whether to raise the provided exception;
            if ``raise_error=False`` (default), the error will be suppressed.
        :type raise_error: bool
        :return: A dictionary containing the codes of water trough locations and
            the date they were last updated.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.other_assets import WaterTroughs  # from pyrcs import WaterTroughs

            >>> wt = WaterTroughs()

            >>> wt_codes = wt.collect_codes(verbose=True)
            To collect data of water troughs?
             [No]|Yes: yes
            Collecting the data ... Done.

            >>> type(wt_codes)
            dict
            >>> list(wt_codes)
            ['Water troughs', 'Last updated date']

            >>> wt_codes_dat = wt_codes['Water troughs']
            >>> type(wt_codes_dat)
            pandas.DataFrame
            >>> wt_codes_dat.shape
            (99, 6)
            >>> wt_codes_dat.head()
                 ELR  ... Length (Yard)
            0    BEI  ...           NaN
            1    BHL  ...        620.00
            42  CGJ2  ...        506.67
            41  CGJ2  ...        506.67
            2   CGJ6  ...        561.00
            [5 rows x 6 columns]
        """

        water_troughs_codes = self._collect_data_from_source(
            data_name=self.KEY.lower(),
            method=self._collect_codes,
            url=self.URL,
            confirmation_required=confirmation_required,
            confirmation_prompt=f"To collect data of {self.KEY.lower()}?\n",
            verbose=verbose,
            raise_error=raise_error
        )

        return water_troughs_codes

    def fetch_codes(self, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetches codes of `water troughs locations`_.

        .. _`water troughs locations`: http://www.railwaycodes.org.uk/misc/troughs.shtm

        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the codes of water trough locations and
            the date they were last updated.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import WaterTroughs  # from pyrcs import WaterTroughs

            >>> wt = WaterTroughs()

            >>> wt_codes = wt.fetch_codes()
            >>> type(wt_codes)
            dict
            >>> list(wt_codes)
            ['Water troughs', 'Last updated date']

            >>> wt.KEY
            'Water troughs'

            >>> wt_codes_dat = wt_codes['Water troughs']
            >>> type(wt_codes_dat)
            pandas.DataFrame
            >>> wt_codes_dat.shape
            (99, 6)
            >>> wt_codes_dat.head()
                 ELR  ... Length (Yard)
            0    BEI  ...           NaN
            1    BHL  ...        620.00
            42  CGJ2  ...        506.67
            41  CGJ2  ...        506.67
            2   CGJ6  ...        561.00
            [5 rows x 6 columns]
        """

        args = {
            'data_name': self.KEY,
            'method': self.collect_codes,
            'data_dir': self._cdd("..", "features"),
        }
        kwargs.update(args)

        troughs_locations_codes = self._fetch_data_from_file(
            update=update, dump_dir=dump_dir, verbose=verbose, **kwargs
        )

        return troughs_locations_codes
