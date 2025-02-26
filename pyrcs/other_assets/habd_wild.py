"""
Collects codes of `HABD and WILD <http://www.railwaycodes.org.uk/misc/habdwild.shtm>`_.
"""

import urllib.parse

import bs4

from .._base import _Base
from ..parser import _get_last_updated_date, parse_tr
from ..utils import cd_data, home_page_url


class HABDWILD(_Base):
    """
    A class for `HABDs and WILDs <http://www.railwaycodes.org.uk/features/habdwild.shtm>`_.

    .. note::

        - HABD: Hot axle box detector
        - WILD: Wheel impact load detector
    """

    #: The name of the data.
    NAME: str = 'Hot axle box detectors (HABDs) and wheel impact load detectors (WILDs)'
    #: The key for accessing the data.
    KEY: str = 'HABD and WILD'
    #: The URL of the main web page for the data.
    URL: str = urllib.parse.urljoin(home_page_url(), '/features/habdwild.shtm')
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

            >>> from pyrcs.other_assets import HABDWILD  # from pyrcs import HABDWILD
            >>> hw = HABDWILD()
            >>> hw.NAME
            'Hot axle box detectors (HABDs) and wheel impact load detectors (WILDs)'
        """

        super().__init__(
            data_dir=data_dir, data_category="other-assets", update=update, verbose=verbose)

    def _collect_codes(self, source, verbose=False):
        try:
            sub_keys = self.KEY.split(' and ')
        except ValueError:
            sub_keys = [self.KEY + ' 1', self.KEY + ' 2']

        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

        codes_list = []
        for h3 in soup.find_all('h3'):
            ths = [th.text.strip() for th in h3.find_next('thead').find_all('th')]
            trs = h3.find_next('tbody').find_all('tr')

            dat = parse_tr(trs=trs, ths=ths, as_dataframe=True)

            codes_list.append(dat)

        habds_and_wilds_codes_dat = dict(zip(sub_keys, codes_list))

        habds_and_wilds_codes = {
            self.KEY: habds_and_wilds_codes_dat,
            self.KEY_TO_LAST_UPDATED_DATE: _get_last_updated_date(soup=soup),
        }

        if verbose in {True, 1}:
            print("Done.")

        self._save_data_to_file(
            data=habds_and_wilds_codes, data_name=self.KEY, dump_dir=cd_data("features"),
            verbose=verbose)

        return habds_and_wilds_codes

    def collect_codes(self, confirmation_required=True, verbose=False, raise_error=False):
        """
        Collects codes of `HABDs and WILDs <http://www.railwaycodes.org.uk/misc/habdwild.shtm>`_
        from the source web page.

        .. note::

            - HABDs: Hot axle box detectors
            - WILDs: Wheel impact load detectors

        :param confirmation_required: Whether user confirmation is required;
            if ``confirmation_required=True`` (default), prompts the user for confirmation
            before proceeding with data collection.
        :type confirmation_required: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :param raise_error: Whether to raise the provided exception;
            if ``raise_error=False`` (default), the error will be suppressed.
        :type raise_error: bool
        :return: A dictionary containing the codes of HABDs and WILDs and
            the date they were last updated, or ``None`` if no data is collected.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.other_assets import HABDWILD  # from pyrcs import HABDWILD
            >>> hw = HABDWILD()
            >>> hw_codes = hw.collect_codes()
            To collect data of HABD and WILD
            ? [No]|Yes: yes
            >>> type(hw_codes)
            dict
            >>> list(hw_codes.keys())
            ['HABD and WILD', 'Last updated date']
            >>> hw.KEY
            'HABD and WILD'
            >>> hw_codes_dat = hw_codes[hw.KEY]
            >>> type(hw_codes_dat)
            dict
            >>> list(hw_codes_dat.keys())
            ['HABD', 'WILD']
            >>> habd_dat = hw_codes_dat['HABD']
            >>> type(habd_dat)
            pandas.core.frame.DataFrame
            >>> habd_dat.head()
                ELR  ...                                              Notes
            0  BAG2  ...
            1  BAG2  ...  installed 29 September 1997, later moved to 74...
            2  BAG2  ...                             previously at 74m 51ch
            3  BAG2  ...                          removed 29 September 1997
            4  BAG2  ...           present in 1969, later moved to 89m 00ch
            [5 rows x 5 columns]
            >>> wild_dat = hw_codes_dat['WILD']
            >>> type(wild_dat)
            pandas.core.frame.DataFrame
            >>> wild_dat.head()
                ELR  ...                                              Notes
            0  AYR3  ...
            1  BAG2  ...
            2  BML1  ...
            3  BML1  ...
            4  CGJ3  ...  moved to 183m 68ch from 8 September 2018 / mov...
            [5 rows x 5 columns]
        """

        habds_and_wilds_codes = self._collect_data_from_source(
            data_name=self.KEY, method=self._collect_codes, url=self.URL,
            confirmation_required=confirmation_required, verbose=verbose, raise_error=raise_error)

        return habds_and_wilds_codes

    def fetch_codes(self, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetches the codes of `HABDs and WILDs`_.

        .. _`HABDs and WILDs`: http://www.railwaycodes.org.uk/misc/habdwild.shtm

        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the codes of HABDs and WILDs and
            the date they were last updated.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import HABDWILD  # from pyrcs import HABDWILD
            >>> hw = HABDWILD()
            >>> hw_codes = hw.fetch_codes()
            >>> type(hw_codes)
            dict
            >>> list(hw_codes.keys())
            ['HABD and WILD', 'Last updated date']
            >>> hw.KEY
            'HABD and WILD'
            >>> hw_codes_dat = hw_codes[hw.KEY]
            >>> type(hw_codes_dat)
            dict
            >>> list(hw_codes_dat.keys())
            ['HABD', 'WILD']
            >>> habd_dat = hw_codes_dat['HABD']
            >>> type(habd_dat)
            pandas.core.frame.DataFrame
            >>> habd_dat.head()
                ELR  ...                                              Notes
            0  BAG2  ...
            1  BAG2  ...  installed 29 September 1997, later moved to 74...
            2  BAG2  ...                             previously at 74m 51ch
            3  BAG2  ...                          removed 29 September 1997
            4  BAG2  ...           present in 1969, later moved to 89m 00ch
            [5 rows x 5 columns]
            >>> wild_dat = hw_codes_dat['WILD']
            >>> type(wild_dat)
            pandas.core.frame.DataFrame
            >>> wild_dat.head()
                ELR  ...                                              Notes
            0  AYR3  ...
            1  BAG2  ...
            2  BML1  ...
            3  BML1  ...
            4  CGJ3  ...  moved to 183m 68ch from 8 September 2018 / mov...
            [5 rows x 5 columns]
        """

        args = {
            'data_name': self.KEY,
            'method': self.collect_codes,
            'data_dir': cd_data("features"),
        }
        kwargs.update(args)

        habds_and_wilds_codes = self._fetch_data_from_file(
            update=update, dump_dir=dump_dir, verbose=verbose, **kwargs)

        return habds_and_wilds_codes
