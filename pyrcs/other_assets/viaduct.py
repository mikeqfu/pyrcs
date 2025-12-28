"""
Collects codes of `railway viaducts <http://www.railwaycodes.org.uk/tunnels/tunnels0.shtm>`_.
"""

import itertools
import re
import urllib.parse

from .._base import _Base
from ..parser import _get_last_updated_date, parse_table
from ..utils import homepage_url, is_homepage_connectable, print_instance_connection_error, \
    print_void_collection_message, validate_page_name


class Viaducts(_Base):
    """
    A class for collecting codes of
    `railway viaducts <http://www.railwaycodes.org.uk/tunnels/tunnels0.shtm>`_.
    """

    #: The name of the data.
    NAME: str = 'Railway viaducts'
    #: The key for accessing the data.
    KEY: str = 'Viaducts'

    #: The URL of the main web page for the data.
    URL: str = urllib.parse.urljoin(homepage_url(), '/viaducts/viaducts0.shtm')

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

            >>> from pyrcs.other_assets import Viaducts  # from pyrcs import Viaducts
            >>> vdct = Viaducts()
            >>> vdct.NAME
            'Railway viaducts'
            >>> vdct.URL
            'http://www.railwaycodes.org.uk/viaducts/viaducts0.shtm'
        """

        super().__init__(
            data_dir=data_dir, content_type='catalogue', data_category="other-assets",
            update=update, verbose=verbose)

        self.page_range = range(1, 7)

    def _collect_codes(self, page_no, source, verbose=False):
        page_name = validate_page_name(self, page_no, valid_page_no=self.page_range)

        codes_dat, soup = parse_table(source=source, parser='html.parser', as_dataframe=True)

        codes_on_page = {
            page_name: codes_dat,
            self.KEY_TO_LAST_UPDATED_DATE: _get_last_updated_date(soup=soup),
        }

        if verbose in {True, 1}:
            print("Done.")

        data_name = re.sub(r"[()]", "", re.sub(r"[ -]", "-", page_name)).lower()
        self._save_data_to_file(data=codes_on_page, data_name=data_name, verbose=verbose)

        return codes_on_page

    def collect_codes(self, page_no, confirmation_required=True, verbose=False, raise_error=False):
        """
        Collects data of `railway viaducts`_ for a specific page number
        from the source web page.

        .. _`railway viaducts`: http://www.railwaycodes.org.uk/tunnels/tunnels0.shtm

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
        :return: A dictionary containing the data of railway viaducts for the specified ``page_no``
            and the date of when the data was last updated.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Viaducts  # from pyrcs import Viaducts
            >>> vdct = Viaducts()
            >>> page_1_codes = vdct.collect_codes(page_no=1)
            >>> type(page_1_codes)
            dict
            >>> list(page_1_codes.keys())
            ['Page 1 (A-C)', 'Last updated date']
            >>> page_1_dat = page_1_codes['Page 1 (A-C)']
            >>> type(page_1_dat)
            pandas.core.frame.DataFrame
            >>> page_1_dat.head()
                        Name  ... Spans
            0       7 Arches  ...     7
            1        36 Arch  ...    36
            2        42 Arch  ...
            3           A698  ...     5
            4  Abattoir Road  ...     8
            [5 rows x 7 columns]
        """

        data_name = self.NAME.lower()

        page_name = validate_page_name(self, page_no, valid_page_no=self.page_range)

        viaducts_codes = self._collect_data_from_source(
            data_name=data_name,
            method=self._collect_codes, initial=page_name, page_no=page_no,
            url=self.catalogue.get(page_name), confirmation_required=confirmation_required,
            confirmation_prompt=f"To collect data of {data_name} ({page_name})\n?",
            verbose=verbose, raise_error=raise_error)

        return viaducts_codes

    def fetch_codes(self, page_no=None, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetches data of `railway viaducts`_.

        .. _`railway viaducts`: http://www.railwaycodes.org.uk/tunnels/tunnels0.shtm

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
        :return: A dictionary containing the data of railway viaducts and
            the date of when the data was last updated.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Viaducts  # from pyrcs import Viaducts
            >>> vdct = Viaducts()
            >>> vdct_codes = vdct.fetch_codes()
            >>> type(vdct_codes)
            dict
            >>> list(vdct_codes.keys())
            ['Viaducts', 'Last updated date']
            >>> vdct.KEY
            'Viaducts'
            >>> vdct_codes_dat = vdct_codes[vdct.KEY]
            >>> type(vdct_codes_dat)
            dict
            >>> list(vdct_codes_dat.keys())
            ['Page 1 (A-C)',
             'Page 2 (D-G)',
             'Page 3 (H-K)',
             'Page 4 (L-P)',
             'Page 5 (Q-S)',
             'Page 6 (T-Z)']
            >>> page_6_codes = vdct_codes_dat['Page 6 (T-Z)']
            >>> type(page_6_codes)
            pandas.core.frame.DataFrame
            >>> page_6_codes.head()
                     Name                                  Notes  ... End mileage Spans
            0   Tadcaster  crosses River Wharfe; grade II listed  ...                11
            1        Taff                         see Red Bridge  ...
            2        Taff                                         ...
            3  Taff River                  also called Afon Taff  ...   170m 42ch
            4  Taffs Well                         see River Taff  ...
            [5 rows x 7 columns]
        """

        if page_no:
            page_name = validate_page_name(self, page_no, valid_page_no=self.page_range)

            args = {
                'data_name': re.sub(r"[()]", "", re.sub(r"[ -]", "-", page_name)).lower(),
                'method': self.collect_codes,
                'page_no': page_no,
            }
            kwargs.update(args)

            viaducts_codes = self._fetch_data_from_file(
                update=update, dump_dir=dump_dir, verbose=verbose, **kwargs)

        else:
            verbose_1 = False if (dump_dir or not verbose) else (2 if verbose == 2 else True)
            verbose_2 = verbose_1 if is_homepage_connectable() else False

            codes_on_pages = [
                self.fetch_codes(page_no=page_no, update=update, verbose=verbose_2)
                for page_no in self.page_range]

            if all(x is None for x in codes_on_pages):
                if update:
                    print_instance_connection_error(verbose=verbose)
                    print_void_collection_message(data_name=self.KEY, verbose=verbose)

                codes_on_pages = [
                    self.fetch_codes(page_no=page_no, update=False, verbose=verbose_1)
                    for page_no in self.page_range]

            viaducts_codes = {
                self.KEY: {next(iter(x)): next(iter(x.values())) for x in codes_on_pages},
                self.KEY_TO_LAST_UPDATED_DATE:
                    max(next(itertools.islice(iter(x.values()), 1, 2)) for x in codes_on_pages),
            }

        if dump_dir is not None:
            self._save_data_to_file(
                data=viaducts_codes, data_name=self.KEY, dump_dir=dump_dir, verbose=verbose)

        return viaducts_codes
