""" Collecting British railway track diagrams.

Data source: http://www.railwaycodes.org.uk/track/diagrams0.shtm
"""

import copy
import os
import urllib.parse

import bs4
import pandas as pd
import requests
from pyhelpers.dir import cd, validate_input_data_dir
from pyhelpers.ops import fake_requests_headers
from pyhelpers.store import load_pickle, save_pickle

from pyrcs.utils import cd_dat, confirmed, get_last_updated_date, get_track_diagrams_items, homepage_url


class TrackDiagrams:
    """
    A class for collecting British railway track diagrams.

    :param data_dir: name of data directory, defaults to ``None``
    :type data_dir: str, None
    :param update: whether to check on update and proceed to update the package data, defaults to ``False``
    :type update: bool

    **Example**::

        from pyrcs.line_data import TrackDiagrams

        td = TrackDiagrams()

        print(td.Name)
        # Railway track diagrams (some samples)

        print(td.SourceURL)
        # http://www.railwaycodes.org.uk/track/diagrams0.shtm
    """

    def __init__(self, data_dir=None, update=False):
        self.Name = 'Railway track diagrams (some samples)'
        self.HomeURL = homepage_url()
        self.SourceURL = urllib.parse.urljoin(self.HomeURL, '/track/diagrams0.shtm')

        self.Key = 'Track diagrams'
        self.LUDKey = 'Last updated date'
        self.Items = get_track_diagrams_items(self.SourceURL, self.Key, update=update)
        self.Date = get_last_updated_date(self.SourceURL, parsed=True, as_date_type=False)
        if data_dir:
            self.DataDir = validate_input_data_dir(data_dir)
        else:
            self.DataDir = cd_dat("line-data", self.Key.lower().replace(" ", "-"))
        self.CurrentDataDir = copy.copy(self.DataDir)

    def cdd_td(self, *sub_dir, **kwargs):
        """
        Change directory to "dat\\line-data\\track-diagrams" and sub-directories (and/or a file)

        :param sub_dir: sub-directory or sub-directories (and/or a file)
        :type sub_dir: str
        :param kwargs: optional parameters of `os.makedirs`_, e.g. ``mode=0o777``
        :return: path to the backup data directory for ``LOR``
        :rtype: str

        :meta private:
        """

        path = cd(self.DataDir, *sub_dir, mkdir=True, **kwargs)

        return path

    def collect_sample_track_diagrams_catalogue(self, confirmation_required=True, verbose=False):
        """
        Collect catalogue of sample railway track diagrams from source web page.

        :param confirmation_required: whether to require users to confirm and proceed, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool
        :return: catalogue of sample railway track diagrams and date of when the data was last updated
        :rtype: dict, None

        **Example**::

            from pyrcs.line_data import TrackDiagrams

            td = TrackDiagrams()

            confirmation_required = True

            track_diagrams_catalogue = td.collect_sample_track_diagrams_catalogue(confirmation_required)
            # To collect the catalogue of sample track diagrams? [No]|Yes:
            # >? yes

            print(track_diagrams_catalogue)
            # {'Track diagrams': <code>,
            #  'Last updated date': <date>}
        """

        if confirmed("To collect the catalogue of sample {}?".format(self.Key.lower()),
                     confirmation_required=confirmation_required):

            if verbose == 2:
                print("Collecting the catalogue of sample {}".format(self.Key.lower()), end=" ... ")

            try:
                source = requests.get(self.SourceURL, headers=fake_requests_headers())

                track_diagrams_catalogue_ = {}

                soup = bs4.BeautifulSoup(source.text, 'lxml')
                h3 = soup.find('h3', text=True, attrs={'class': None})
                while h3:
                    # Description
                    if h3.text == 'Miscellaneous':
                        desc = [x.text for x in h3.find_next_siblings('p')]
                    else:
                        desc = h3.find_next_sibling('p').text.replace('\xa0', '')
                    # Extract details
                    cold_soup = h3.find_next('div', attrs={'class': 'columns'})
                    if cold_soup:
                        info = [x.text for x in cold_soup.find_all('p') if x.string != '\xa0']
                        urls = [urllib.parse.urljoin(self.SourceURL, a.get('href'))
                                for a in cold_soup.find_all('a')]
                    else:
                        cold_soup = h3.find_next('a', attrs={'target': '_blank'})
                        info, urls = [], []
                        while cold_soup:
                            info.append(cold_soup.text)
                            urls.append(urllib.parse.urljoin(self.SourceURL, cold_soup['href']))
                            cold_soup = cold_soup.find_next('a') if h3.text == 'Miscellaneous' \
                                else cold_soup.find_next_sibling('a')
                    meta = pd.DataFrame(zip(info, urls), columns=['Description', 'FileURL'])

                    track_diagrams_catalogue_.update({h3.text: (desc, meta)})  # Update

                    h3 = h3.find_next_sibling('h3')

                track_diagrams_catalogue = {self.Key: track_diagrams_catalogue_, self.LUDKey: self.Date}

                print("Done. ") if verbose == 2 else ""

                pickle_filename = self.Key.lower().replace(" ", "-") + ".pickle"
                path_to_pickle = self.cdd_td(pickle_filename)
                save_pickle(track_diagrams_catalogue, path_to_pickle, verbose=verbose)

            except Exception as e:
                print("Failed. {}".format(e))
                track_diagrams_catalogue = None

            return track_diagrams_catalogue

    def fetch_sample_track_diagrams_catalogue(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch catalogue of sample railway track diagrams from local backup.

        :param update: whether to check on update and proceed to update the package data, defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data with newly collected data, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str, None
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool
        :return: catalogue of sample railway track diagrams and date of when the data was last updated
        :rtype: dict

        **Example**::

            from pyrcs.line_data import TrackDiagrams

            td = TrackDiagrams()

            update = False
            pickle_it = False
            data_dir = None

            track_diagrams_cat = td.fetch_sample_track_diagrams_catalogue(update, pickle_it, data_dir)

            print(track_diagrams_cat)
            # {'Track diagrams': <code>,
            #  'Last updated date': <date>}
        """

        pickle_filename = self.Key.lower().replace(" ", "-") + ".pickle"
        path_to_pickle = self.cdd_td(pickle_filename)

        if os.path.isfile(path_to_pickle) and not update:
            track_diagrams_catalogue = load_pickle(path_to_pickle)

        else:
            verbose_ = False if data_dir or not verbose else True
            track_diagrams_catalogue = self.collect_sample_track_diagrams_catalogue(confirmation_required=False,
                                                                                    verbose=verbose_)
            if track_diagrams_catalogue:
                if pickle_it and data_dir:
                    self.CurrentDataDir = validate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, pickle_filename)
                    save_pickle(track_diagrams_catalogue, path_to_pickle, verbose=verbose)
            else:
                print("No data of the sample {} catalogue has been collected.".format(self.Key.lower()))

        return track_diagrams_catalogue
