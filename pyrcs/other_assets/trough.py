"""
Collects codes of `water troughs <http://www.railwaycodes.org.uk/misc/troughs.shtm>`_.
"""

import re
import urllib.parse

import bs4
import numpy as np
import unicodedata

from .._base import _Base
from ..parser import _get_last_updated_date, parse_tr
from ..utils import cd_data, home_page_url


def _decode_vulgar_fraction(x):
    for s in x:
        try:
            name = unicodedata.name(s)
            if name.startswith('VULGAR FRACTION'):
                # normalized = unicodedata.normalize('NFKC', s)
                # numerator, _, denominator = normalized.partition('⁄')
                # frac_val = int(numerator) / int(denominator)
                frac_val = unicodedata.numeric(s)
                return frac_val
        except (TypeError, ValueError):
            pass


def _parse_vulgar_fraction_in_length(x):
    """
    Parses 'VULGAR FRACTION' for 'Length' of water trough locations.
    """

    if x == '':
        yd = np.nan

    elif re.match(r'\d+yd', x):  # e.g. '620yd'
        yd = int(re.search(r'\d+(?=yd)', x).group(0))

    elif re.match(r'\d+&frac\d+;yd', x):  # e.g. '506&frac23;yd'
        yd, frac = re.search(r'(\d+)&frac(\d+)(?=;yd)', x).groups()
        yd = int(yd) + int(frac[0]) / int(frac[1])

    else:  # e.g. '557½yd'
        yd = _decode_vulgar_fraction(x)

    return yd


class WaterTroughs(_Base):
    """
    A class for `water troughs locations <http://www.railwaycodes.org.uk/features/troughs.shtm>`_.
    """

    #: The name of the data.
    NAME: str = 'Water trough locations'
    #: The key for accessing the data.
    KEY: str = 'Water troughs'
    #: The URL of the main web page for the data.
    URL: str = urllib.parse.urljoin(home_page_url(), '/features/troughs.shtm')
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
            data_dir=data_dir, data_category="other-assets", update=update, verbose=verbose)

    def _collect_codes(self, source, verbose=False):
        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

        ths = [th.text.strip() for th in soup.find('thead').find_all('th')]
        trs = soup.find('tbody').find_all('tr')

        dat = parse_tr(trs=trs, ths=ths, as_dataframe=True)

        if 'Length' in dat.columns:
            dat['Length (Yard)'] = dat.Length.map(_parse_vulgar_fraction_in_length)

        water_troughs_codes = {
            self.KEY: dat,
            self.KEY_TO_LAST_UPDATED_DATE: _get_last_updated_date(soup=soup),
        }

        if verbose in {True, 1}:
            print("Done.")

        self._save_data_to_file(
            data=water_troughs_codes, data_name=self.KEY, dump_dir=cd_data("features"),
            verbose=verbose)

        return water_troughs_codes

    def collect_codes(self, confirmation_required=True, verbose=False, raise_error=False):
        """
        Collects codes of `water troughs locations`_ from the source web page.

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
            >>> wt_codes = wt.collect_codes()
            To collect data of water troughs
            ? [No]|Yes: yes
            >>> type(wt_codes)
            dict
            >>> list(wt_codes.keys())
            ['Water troughs', 'Last updated date']
            >>> wt.KEY
            'Water troughs'
            >>> wt_codes_dat = wt_codes[wt.KEY]
            >>> type(wt_codes_dat)
            pandas.core.frame.DataFrame
            >>> wt_codes_dat.head()
                ELR  ... Length (Yard)
            0   BEI  ...           NaN
            1   BHL  ...    620.000000
            2  CGJ2  ...      0.666667
            3  CGJ6  ...    561.000000
            4  CGJ6  ...    560.000000
            [5 rows x 6 columns]
        """

        water_troughs_codes = self._collect_data_from_source(
            data_name=self.KEY.lower(), method=self._collect_codes, url=self.URL,
            confirmation_required=confirmation_required,
            confirmation_prompt=f"To collect data of {self.KEY.lower()}\n?",
            verbose=verbose, raise_error=raise_error)

        return water_troughs_codes

    def fetch_codes(self, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetches the codes of `water troughs locations`_.

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
            >>> list(wt_codes.keys())
            ['Water troughs', 'Last updated date']
            >>> wt.KEY
            'Water troughs'
            >>> wt_codes_dat = wt_codes[wt.KEY]
            >>> type(wt_codes_dat)
            pandas.core.frame.DataFrame
            >>> wt_codes_dat.head()
                ELR  ... Length (Yard)
            0   BEI  ...           NaN
            1   BHL  ...    620.000000
            2  CGJ2  ...      0.666667
            3  CGJ6  ...    561.000000
            4  CGJ6  ...    560.000000
            [5 rows x 6 columns]
        """

        args = {
            'data_name': self.KEY,
            'method': self.collect_codes,
            'data_dir': cd_data("features"),
        }
        kwargs.update(args)

        troughs_locations_codes = self._fetch_data_from_file(
            update=update, dump_dir=dump_dir, verbose=verbose, **kwargs)

        return troughs_locations_codes
