"""
Collects codes of `railway viaducts <http://www.railwaycodes.org.uk/tunnels/tunnels0.shtm>`_.
"""

import itertools
import re
import urllib.parse

from .._base import _Base
from ..parser import _get_last_updated_date, parse_table
from ..utils import handle_connection_error, homepage_url, is_homepage_connectable, \
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

    def _parse_and_save_page(self, source, page_no, verbose=False):
        """
        Parse raw HTML source to extract viaduct codes and save the data to a file.

        This internal method acts as a callback for the data collection pipeline, parsing
        the HTML table data into a DataFrame and extracting metadata before local saving.

        :param source: The raw HTML source content response.
        :type source: requests.Response | Any
        :param page_no: The page number associated with the source.
        :type page_no: int | str
        :param verbose: Whether to print progress messages to the console. Defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the parsed DataFrame and the last updated date.
        :rtype: dict
        """

        page_name = validate_page_name(self, page_no, valid_page_no=self.page_range)

        viaduct_codes, soup = parse_table(source, parser='html.parser', as_dataframe=True)
        last_updated_date = _get_last_updated_date(soup=soup)

        viaducts_data = {
            page_name: viaduct_codes,
            self.KEY_TO_LAST_UPDATED_DATE: last_updated_date
        }

        if verbose in {True, 1}:
            print("Done.")

        # Clean filename characters and replace multiple spaces/dashes with a single dash
        clean_name = re.sub(r'[()]', '', page_name)
        data_name = re.sub(r'[- ]+', '-', clean_name).lower()

        self._save_data_to_file(viaducts_data, data_name=data_name, verbose=verbose)

        return viaducts_data

    def collect_codes(self, page_no, confirmation_required=True, verbose=False, raise_error=False):
        """
        Collect data of `railway viaducts`_ for a specific page number from the source web page.

        .. _`railway viaducts`: http://www.railwaycodes.org.uk/tunnels/tunnels0.shtm

        This method coordinates the retrieval process by identifying the target URL from
        the catalogue and calling the base data collection method with user confirmation.

        :param page_no: The page number where data is collected from;
            valid values are ``1`` to ``6``.
        :type page_no: int | str
        :param confirmation_required: Whether user confirmation is required;
            if ``True`` (default), prompts the user before proceeding.
        :type confirmation_required: bool
        :param verbose: Whether to print status information to the console. Defaults to ``False``.
        :type verbose: bool | int
        :param raise_error: Whether to raise exceptions encountered during retrieval;
            if ``False`` (default), errors are suppressed.
        :type raise_error: bool
        :return: A dictionary containing the viaduct data and the last updated date.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.other_assets import Viaducts  # from pyrcs import Viaducts

            >>> vdct = Viaducts()

            >>> viaducts_page_1: dict = vdct.collect_codes(page_no=1, verbose=True)
            Proceed with collecting data of railway viaducts (Page 1 (A-C))?
             [No]|Yes: yes
            Collecting the data ... Done.

            >>> list(viaducts_page_1)
            ['Page 1 (A-C)', 'Last updated date']

            >>> viaducts_page_1_data = viaducts_page_1['Page 1 (A-C)']

            >>> type(viaducts_page_1_data)
            pandas.DataFrame
            >>> viaducts_page_1_data.shape
            (630, 7)
            >>> viaducts_page_1_data.head()
                   Name  ... Spans/arches
            0  7 Arches  ...              7
            1   36 Arch  ...             36
            2   42 Arch  ...
            3       A46  ...
            4      A413  ...
            [5 rows x 7 columns]
        """

        viaducts_data = self._collect_data_from_source_by_page(
            page_no=page_no,
            method=self._parse_and_save_page,
            confirmation_required=confirmation_required,
            verbose=verbose,
            raise_error=raise_error
        )

        return viaducts_data

    def fetch_codes(self, page_no=None, update=False, dump_dir=None, verbose=False, **kwargs):
        # noinspection PyShadowingNames,PyUnresolvedReferences
        """
        Fetch data of `railway viaducts`_.

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
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.other_assets import Viaducts  # from pyrcs import Viaducts

            >>> vdct = Viaducts()

            >>> viaducts_codes: dict = vdct.fetch_codes()
            >>> list(viaducts_codes)
            ['Viaducts', 'Last updated date']
            >>> vdct.KEY
            'Viaducts'

            >>> viaducts_data = viaducts_codes[vdct.KEY]
            >>> type(viaducts_data)
            dict
            >>> list(viaducts_data)
            ['Page 1 (A-C)',
             'Page 2 (D-G)',
             'Page 3 (H-K)',
             'Page 4 (L-P)',
             'Page 5 (Q-S)',
             'Page 6 (T-Z)']

            >>> page_6_codes = viaducts_data['Page 6 (T-Z)']
            >>> type(page_6_codes)
            pandas.DataFrame
            >>> page_6_codes.shape
            (319, 7)
            >>> page_6_codes.head()
                     Name                                 Notes  ... End mileage Spans/arches
            0   Tadcaster  crosses River Wharfe; grade Ⅱ listed  ...                       11
            1        Taff                        see Red Bridge  ...
            2        Taff                                        ...
            3  Taff River                 also called Afon Taff  ...   170m 42ch
            4  Taffs Well                        see River Taff  ...
            [5 rows x 7 columns]
        """

        if page_no:
            page_name = validate_page_name(self, page_no, valid_page_no=self.page_range)
            data_name = re.sub(r"[()]", "", re.sub(r"[ -]", "-", page_name)).lower()

            fetch_args = {
                'data_name': data_name,
                'method': self.collect_codes,
                'page_no': page_no
            }

            viaducts_data = self._fetch_data_from_file(
                update=update,
                dump_dir=dump_dir,
                verbose=verbose,
                **(fetch_args | kwargs)
            )

        else:
            verbose_1 = False if (dump_dir or not verbose) else (2 if verbose == 2 else True)
            verbose_2 = verbose_1 if is_homepage_connectable() else False

            codes_on_pages: list[dict] = [
                self.fetch_codes(page_no=page_no, update=update, verbose=verbose_2)
                for page_no in self.page_range
            ]

            if all(x is None for x in codes_on_pages):
                if update:
                    handle_connection_error(verbose=verbose)
                    print_void_collection_message(data_name=self.KEY, verbose=verbose)

                codes_on_pages = [
                    self.fetch_codes(page_no=page_no, update=False, verbose=verbose_1)
                    for page_no in self.page_range]

            viaducts_data = {
                self.KEY:
                    {next(iter(x)): next(iter(x.values())) for x in codes_on_pages},
                self.KEY_TO_LAST_UPDATED_DATE:
                    max(next(itertools.islice(iter(x.values()), 1, 2)) for x in codes_on_pages),
            }

        if dump_dir is not None:
            self._save_data_to_file(
                data=viaducts_data,
                data_name=self.KEY,
                dump_dir=dump_dir,
                verbose=verbose
            )

        return viaducts_data
