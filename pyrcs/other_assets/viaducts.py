""" Collecting codes of railway viaducts.

Data source: http://www.railwaycodes.org.uk/tunnels/tunnels0.shtm
"""

import copy
import itertools
import os
import re
import urllib.parse

import pandas as pd
from pyhelpers.dir import validate_input_data_dir
from pyhelpers.store import load_pickle, save_pickle
from pyhelpers.text import find_similar_str

from pyrcs.utils import cd_dat, get_catalogue, get_last_updated_date, homepage_url


class Viaducts:
    """
    A class for collecting railway viaducts.

    :param data_dir: name of data directory, defaults to ``None``
    :type data_dir: str, None
    :param update: whether to check on update and proceed to update the package data, defaults to ``False``
    :type update: bool

    **Example**::

        from pyrcs.other_assets import Viaducts

        viaducts = Viaducts()

        print(viaducts.Name)
        # Railway viaducts

        print(viaducts.SourceURL)
        # http://www.railwaycodes.org.uk/viaducts/viaducts0.shtm
    """

    def __init__(self, data_dir=None, update=False):
        """
        Constructor method.
        """
        self.Name = 'Railway viaducts'
        self.Key = 'Viaducts'
        self.LUDKey = 'Last updated date'
        self.HomeURL = homepage_url()
        self.SourceURL = urllib.parse.urljoin(self.HomeURL, '/viaducts/viaducts0.shtm')
        self.Catalogue = get_catalogue(self.SourceURL, update=update, confirmation_required=False)
        self.P1Key, self.P2Key, self.P3Key, self.P4Key, self.P5Key, self.P6Key = list(self.Catalogue.keys())[1:]
        self.Date = get_last_updated_date(self.SourceURL, parsed=True, as_date_type=False)
        self.DataDir = validate_input_data_dir(data_dir) if data_dir else cd_dat("other-assets", self.Key.lower())
        self.CurrentDataDir = copy.copy(self.DataDir)

    def cdd_viaducts(self, *sub_dir):
        """
        Change directory to "dat\\other-assets\\viaducts\\" and sub-directories (and/or a file)

        :param sub_dir: sub-directory or sub-directories (and/or a file)
        :type sub_dir: str
        :return: path to the backup data directory for ``Viaducts``
        :rtype: str

        :meta private:
        """

        path = self.DataDir
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    def collect_railway_viaducts_by_page(self, page_no, update=False, verbose=False):
        """
        Collect data of railway viaducts for a given page number from source web page.

        :param page_no: page number; valid values include 1, 2, 3, 4, 5, and 6
        :type page_no: int, str
        :param update: whether to check on update and proceed to update the package data, defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool
        :return: railway viaducts data of the given ``page_no`` and date of when the data was last updated
        :rtype: dict

        **Example**::

            from pyrcs.other_assets import Viaducts

            viaducts = Viaducts()

            update = True

            page_no = 1
            railway_viaducts_1 = viaducts.collect_railway_viaducts_by_page(page_no, update)

            print(railway_viaducts_1)
            # {'Page 1 (A-C)': <codes>,
            #  'Last updated date': <date>}
        """

        assert page_no in range(1, 7), "Valid \"page_no\" must be one of 1, 2, 3, 4, 5, and 6."

        page_name = find_similar_str(str(page_no), list(self.Catalogue.keys()))

        pickle_filename = re.sub(r"[()]", "", re.sub(r"[ -]", "-", page_name)).lower() + ".pickle"
        path_to_pickle = self.cdd_viaducts(pickle_filename)

        if os.path.isfile(path_to_pickle) and not update:
            page_railway_viaducts = load_pickle(path_to_pickle)

        else:
            url = self.Catalogue[page_name]

            try:
                last_updated_date = get_last_updated_date(url)
            except Exception as e:
                print("Failed to find the last updated date for viaducts data of {}. {}".format(page_name, e))
                last_updated_date = None

            try:
                header, viaducts_table = pd.read_html(url, na_values=[''], keep_default_na=False)
                viaducts_table.columns = header.columns.to_list()
                viaducts_table.fillna('', inplace=True)
            except Exception as e:
                print("Failed to collect viaducts data of {}. {}".format(page_name, e))
                viaducts_table = None

            page_railway_viaducts = {page_name: viaducts_table, self.LUDKey: last_updated_date}

            save_pickle(page_railway_viaducts, path_to_pickle, verbose=verbose)

        return page_railway_viaducts

    def fetch_railway_viaducts(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch data of railway viaducts from local backup.

        :param update: whether to check on update and proceed to update the package data, defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data with newly collected data, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str, None
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool
        :return: railway viaducts data and date of when the data was last updated
        :rtype: dict

        **Example**::

            from pyrcs.other_assets import Viaducts

            viaducts = Viaducts()

            update = False
            pickle_it = False
            data_dir = None

            railway_viaducts = viaducts.fetch_railway_viaducts(update, pickle_it, data_dir)

            print(railway_tunnel_lengths)
            # {'Viaducts': <codes>,
            #  'Latest update date': <date>}
        """

        verbose_ = False if data_dir or not verbose else True
        codes = [self.collect_railway_viaducts_by_page(page_no, update, verbose=verbose_) for page_no in range(1, 7)]

        railways_viaducts_data = {
            self.Key: {next(iter(x)): next(iter(x.values())) for x in codes},
            self.LUDKey: max(next(itertools.islice(iter(x.values()), 1, 2)) for x in codes)}

        if pickle_it and data_dir:
            self.CurrentDataDir = validate_input_data_dir(data_dir)
            path_to_pickle = os.path.join(self.CurrentDataDir, self.Key.lower().replace(" ", "-") + ".pickle")
            save_pickle(railways_viaducts_data, path_to_pickle, verbose=verbose)

        return railways_viaducts_data
