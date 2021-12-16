"""
Collect codes of `railway viaducts <http://www.railwaycodes.org.uk/tunnels/tunnels0.shtm>`_.
"""

import itertools
import socket
import urllib.error
import urllib.parse

from pyhelpers.dir import cd
from pyhelpers.store import load_pickle

from pyrcs.utils import *


class Viaducts:
    """
    A class for collecting railway viaducts.
    """

    def __init__(self, data_dir=None, update=False, verbose=True):
        """
        :param data_dir: name of data directory, defaults to ``None``
        :type data_dir: str or None
        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console, defaults to ``True``
        :type verbose: bool or int

        :ivar str Name: name of the data
        :ivar str Key: key of the dict-type data
        :ivar str HomeURL: URL of the main homepage
        :ivar str SourceURL: URL of the data web page
        :ivar str LUDKey: key of the last updated date
        :ivar str LUD: last updated date
        :ivar dict Catalogue: catalogue of the data
        :ivar str DataDir: path to the data directory
        :ivar str CurrentDataDir: path to the current data directory

        :ivar str P1Key: key of the dict-type data of Page 1
        :ivar str P2Key: key of the dict-type data of Page 2
        :ivar str P3Key: key of the dict-type data of Page 3
        :ivar str P4Key: key of the dict-type data of Page 4
        :ivar str P5Key: key of the dict-type data of Page 5
        :ivar str P6Key: key of the dict-type data of Page 6

        **Example**::

            >>> from pyrcs.other_assets import Viaducts

            >>> vdct = Viaducts()

            >>> print(vdct.NAME)
            Railway viaducts

            >>> print(vdct.URL)
            http://www.railwaycodes.org.uk/viaducts/viaducts0.shtm
        """

        print_connection_error(verbose=verbose)

        self.NAME = 'Railway viaducts'
        self.KEY = 'Viaducts'

        self.URL = urllib.parse.urljoin(home_page_url(), '/viaducts/viaducts0.shtm')

        self.LUDKey = 'Last updated date'
        self.LUD = get_last_updated_date(url=self.URL, parsed=True, as_date_type=False)

        self.catalogue = get_catalogue(url=self.URL, update=update, confirmation_required=False)

        self.P1Key, self.P2Key, self.P3Key, self.P4Key, self.P5Key, self.P6Key = \
            list(self.catalogue.keys())[1:]

        self.data_dir, self.current_data_dir = init_data_dir(self, data_dir, category="other-assets")

    def _cdd_vdct(self, *sub_dir, **kwargs):
        """
        Change directory to package data directory and subdirectories (and/or a file).

        The directory for this module: ``"dat\\other-assets\\viaducts"``.

        :param sub_dir: subdirectory or subdirectories (and/or a file)
        :type sub_dir: str
        :param kwargs: optional parameters of `os.makedirs`_, e.g. ``mode=0o777``
        :return: path to the backup data directory for ``Viaducts``
        :rtype: str

        .. _`os.makedirs`: https://docs.python.org/3/library/os.html#os.makedirs

        :meta private:
        """

        path = cd(self.data_dir, *sub_dir, mkdir=True, **kwargs)

        return path

    def collect_viaduct_codes_by_page(self, page_no, update=False, verbose=False):
        """
        Collect data of railway viaducts for a given page number from source web page.

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

        **Example**::

            >>> from pyrcs.other_assets import Viaducts

            >>> vdct = Viaducts()

            >>> # vd1 = vdct.collect_viaduct_codes_by_page(1, update=True, verbose=True)
            >>> vd1 = vdct.collect_viaduct_codes_by_page(page_no=1)

            >>> type(vd1)
            dict
            >>> list(vd1.keys())
            ['Page 1 (A-C)', 'Last updated date']

            >>> viaducts_1 = vd1['Page 1 (A-C)']

            >>> type(viaducts_1)
            pandas.core.frame.DataFrame
            >>> viaducts_1.head()
                        Name  ... Spans
            0       7 Arches  ...     7
            1        36 Arch  ...    36
            2        42 Arch  ...
            3           A698  ...     5
            4  Abattoir Road  ...     8
            [5 rows x 7 columns]
        """

        assert page_no in range(1, 7), "Valid \"page_no\" must be one of 1, 2, 3, 4, 5, and 6."

        page_name = find_similar_str(str(page_no), list(self.catalogue.keys()))

        pickle_filename = re.sub(r"[()]", "", re.sub(r"[ -]", "-", page_name)).lower() + ".pickle"
        path_to_pickle = self._cdd_vdct(pickle_filename)

        if os.path.isfile(path_to_pickle) and not update:
            page_railway_viaducts = load_pickle(path_to_pickle)

        else:
            url = self.catalogue[page_name]

            page_railway_viaducts = None

            if verbose == 2:
                print("Collecting data of {} on {}".format(self.KEY.lower(), page_name),
                      end=" ... ")

            try:
                header, viaducts_table = pd.read_html(url, na_values=[''], keep_default_na=False)
            except (urllib.error.URLError, socket.gaierror):
                print("Failed. ") if verbose == 2 else ""
                print_conn_err(verbose=verbose)

            else:
                try:
                    viaducts_table.columns = header.columns.to_list()
                    viaducts_table.fillna('', inplace=True)

                    last_updated_date = get_last_updated_date(url)

                    print("Done.") if verbose == 2 else ""

                    page_railway_viaducts = {
                        page_name: viaducts_table, self.LUDKey: last_updated_date}

                    save_pickle(page_railway_viaducts, path_to_pickle, verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(page_name, e))

        return page_railway_viaducts

    def fetch_viaduct_codes(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch data of railway viaducts from local backup.

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param pickle_it: whether to save the data as a pickle file, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of a folder where the pickle file is to be saved, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of railway viaducts and date of when the data was last updated
        :rtype: dict

        **Example**::

            >>> from pyrcs.other_assets import Viaducts

            >>> vdct = Viaducts()

            >>> # viaducts_data = vdct.fetch_viaduct_codes(update=True, verbose=True)
            >>> viaducts_data = vdct.fetch_viaduct_codes()

            >>> type(viaducts_data)
            dict
            >>> list(viaducts_data.keys())
            ['Viaducts', 'Last updated date']

            >>> print(vdct.KEY)
            Viaducts

            >>> viaducts_codes = viaducts_data[vdct.KEY]

            >>> type(viaducts_codes)
            dict
            >>> list(viaducts_codes.keys())
            ['Page 1 (A-C)',
             'Page 2 (D-G)',
             'Page 3 (H-K)',
             'Page 4 (L-P)',
             'Page 5 (Q-S)',
             'Page 6 (T-Z)']

            >>> viaducts6 = viaducts_codes['Page 6 (T-Z)']

            >>> type(viaducts6)
            pandas.core.frame.DataFrame
            >>> viaducts6.head()
                     Name  ... Spans
            0        Taff  ...
            1        Taff  ...
            2  Taff River  ...
            3  Taffs Well  ...
            4        Tame  ...     4
            [5 rows x 7 columns]
        """

        verbose_ = False if (data_dir or not verbose) else (2 if verbose == 2 else True)

        page_data = [
            self.collect_viaduct_codes_by_page(
                page_no, update, verbose=verbose_ if is_home_connectable() else False)
            for page_no in range(1, 7)]

        if all(x is None for x in page_data):
            if update:
                print_conn_err(verbose=verbose)
                print("No data of the {} has been freshly collected.".format(self.KEY.lower()))
            page_data = [self.collect_viaduct_codes_by_page(x, update=False, verbose=verbose_)
                         for x in range(1, 7)]

        railways_viaducts_data = {
            self.KEY: {next(iter(x)): next(iter(x.values())) for x in page_data},
            self.LUDKey: max(next(itertools.islice(iter(x.values()), 1, 2)) for x in page_data)}

        if pickle_it and data_dir:
            self.current_data_dir = validate_dir(data_dir)
            path_to_pickle = os.path.join(
                self.current_data_dir, self.KEY.lower().replace(" ", "-") + ".pickle")
            save_pickle(railways_viaducts_data, path_to_pickle, verbose=verbose)

        return railways_viaducts_data
