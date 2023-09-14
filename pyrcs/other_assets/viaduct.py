"""Collect codes of `railway viaducts <http://www.railwaycodes.org.uk/tunnels/tunnels0.shtm>`_."""

import itertools
import os
import re
import urllib.parse

import requests
from pyhelpers.dirs import cd
from pyhelpers.ops import fake_requests_headers
from pyhelpers.store import load_data

from ..parser import get_catalogue, get_last_updated_date, parse_table
from ..utils import home_page_url, init_data_dir, is_home_connectable, print_conn_err, \
    print_inst_conn_err, save_data_to_file, validate_page_name


class Viaducts:
    """
    A class for collecting codes of
    `railway viaducts <http://www.railwaycodes.org.uk/tunnels/tunnels0.shtm>`_.
    """

    #: Name of the data
    NAME = 'Railway viaducts'
    #: Key of the `dict <https://docs.python.org/3/library/stdtypes.html#dict>`_-type data
    KEY = 'Viaducts'
    #: URL of the main web page of the data
    URL = urllib.parse.urljoin(home_page_url(), '/viaducts/viaducts0.shtm')
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

            >>> from pyrcs.other_assets import Viaducts  # from pyrcs import Viaducts

            >>> vdct = Viaducts()

            >>> vdct.NAME
            'Railway viaducts'

            >>> vdct.URL
            'http://www.railwaycodes.org.uk/viaducts/viaducts0.shtm'
        """

        print_conn_err(verbose=verbose)

        self.catalogue = get_catalogue(url=self.URL, update=update, confirmation_required=False)

        self.last_updated_date = get_last_updated_date(url=self.URL, parsed=True, as_date_type=False)

        self.data_dir, self.current_data_dir = init_data_dir(self, data_dir, category="other-assets")

    def _cdd(self, *sub_dir, **kwargs):
        """
        Change directory to package data directory and subdirectories (and/or a file).

        The directory for this module: ``"data\\other-assets\\viaducts"``.

        :param sub_dir: subdirectory or subdirectories (and/or a file)
        :type sub_dir: str
        :param kwargs: [optional] parameters of the function `pyhelpers.dir.cd`_
        :return: path to the backup data directory for the class
            :py:class:`~pyrcs.other_assets.viaduct.Viaducts`
        :rtype: str

        .. _`pyhelpers.dir.cd`:
            https://pyhelpers.readthedocs.io/en/latest/_generated/pyhelpers.dir.cd.html
        """

        path = cd(self.data_dir, *sub_dir, mkdir=True, **kwargs)

        return path

    def collect_codes_by_page(self, page_no, update=False, verbose=False):
        """
        Collect data of `railway viaducts`_ for a given page number from source web page.

        .. _`railway viaducts`: http://www.railwaycodes.org.uk/tunnels/tunnels0.shtm

        :param page_no: page number;
            valid values include ``1``, ``2``, ``3``, ``4``, ``5``, and ``6``
        :type page_no: int or str
        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of railway viaducts on page ``page_no`` and
            date of when the data was last updated
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Viaducts  # from pyrcs import Viaducts

            >>> vdct = Viaducts()

            >>> page_1_codes = vdct.collect_codes_by_page(page_no=1)
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

        page_name = validate_page_name(self, page_no, valid_page_no=set(range(1, 7)))
        # page_name = get_page_name(vdct, page_no, valid_page_no=set(range(1, 7)))

        data_name = re.sub(r"[()]", "", re.sub(r"[ -]", "-", page_name)).lower()
        ext = ".pkl"
        path_to_pickle = self._cdd(data_name + ext)

        if os.path.exists(path_to_pickle) and not update:
            codes_on_page = load_data(path_to_pickle)

        else:
            if verbose == 2:
                print("Collecting data of {} on {}".format(self.KEY.lower(), page_name), end=" ... ")

            codes_on_page = None

            try:
                url = self.catalogue[page_name]
                # url = vdct.catalogue[page_name]
                source = requests.get(url=url, headers=fake_requests_headers())

            except Exception as e:
                if verbose == 2:
                    print("Failed. ", end="")
                print_inst_conn_err(verbose=verbose, e=e)

            else:
                try:
                    codes_dat = parse_table(source=source, parser='html.parser', as_dataframe=True)

                    last_updated_date = get_last_updated_date(url)

                    codes_on_page = {
                        page_name: codes_dat,
                        self.KEY_TO_LAST_UPDATED_DATE: last_updated_date,
                    }

                    if verbose == 2:
                        print("Done.")

                    save_data_to_file(
                        self, data=codes_on_page, data_name=data_name, ext=ext, verbose=verbose)

                except Exception as e:
                    print("Failed. \"{}\": {}".format(page_name, e))

        return codes_on_page

    def fetch_codes(self, update=False, dump_dir=None, verbose=False):
        """
        Fetch data of `railway viaducts`_.

        .. _`railway viaducts`: http://www.railwaycodes.org.uk/tunnels/tunnels0.shtm

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param dump_dir: name of a folder where the pickle file is to be saved, defaults to ``None``
        :type dump_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of railway viaducts and date of when the data was last updated
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

        verbose_1 = False if (dump_dir or not verbose) else (2 if verbose == 2 else True)
        verbose_2 = verbose_1 if is_home_connectable() else False

        codes_on_pages = [
            self.collect_codes_by_page(page_no, update=update, verbose=verbose_2)
            for page_no in range(1, 7)]

        if all(x is None for x in codes_on_pages):
            if update:
                print_inst_conn_err(verbose=verbose)
                print("No data of the {} has been freshly collected.".format(self.KEY.lower()))
            codes_on_pages = [
                self.collect_codes_by_page(page_no, update=False, verbose=verbose_1)
                for page_no in range(1, 7)]

        viaducts_codes = {
            self.KEY: {next(iter(x)): next(iter(x.values())) for x in codes_on_pages},
            self.KEY_TO_LAST_UPDATED_DATE:
                max(next(itertools.islice(iter(x.values()), 1, 2)) for x in codes_on_pages),
        }

        if dump_dir is not None:
            save_data_to_file(
                self, data=viaducts_codes, data_name=self.KEY, ext=".pkl", dump_dir=dump_dir,
                verbose=verbose)

        return viaducts_codes
