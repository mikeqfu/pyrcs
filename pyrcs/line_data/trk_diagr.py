"""
Collect British `railway track diagrams <http://www.railwaycodes.org.uk/track/diagrams0.shtm>`_.
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

from pyrcs.utils import cd_dat, confirmed, get_last_updated_date, homepage_url, print_conn_err, \
    is_internet_connected, print_connection_error


class TrackDiagrams:
    """
    A class for collecting British railway track diagrams.

    :param data_dir: name of data directory, defaults to ``None``
    :type data_dir: str or None
    :param verbose: whether to print relevant information in console, defaults to ``True``
    :type verbose: bool or int

    :ivar str Name: name of the data
    :ivar str Key: key of the dict-type data
    :ivar str HomeURL: URL of the main homepage
    :ivar str SourceURL: URL of the data web page
    :ivar str LUDKey: key of the last updated date
    :ivar str LUD: last updated date
    :ivar str DataDir: path to the data directory
    :ivar str CurrentDataDir: path to the current data directory

    **Example**::

        >>> from pyrcs.line_data import TrackDiagrams

        >>> td = TrackDiagrams()

        >>> print(td.Name)
        Railway track diagrams (some samples)

        >>> print(td.SourceURL)
        http://www.railwaycodes.org.uk/track/diagrams0.shtm
    """

    def __init__(self, data_dir=None, verbose=True):
        if not is_internet_connected():
            print_connection_error(verbose=verbose)

        self.Name = 'Railway track diagrams (some samples)'
        self.Key = 'Track diagrams'

        self.HomeURL = homepage_url()
        self.SourceURL = urllib.parse.urljoin(self.HomeURL, '/line/diagrams0.shtm')

        self.LUDKey = 'Last updated date'
        self.LUD = get_last_updated_date(url=self.SourceURL, parsed=True, as_date_type=False)

        if data_dir:
            self.DataDir = validate_input_data_dir(data_dir)
        else:
            self.DataDir = cd_dat("line-data", self.Key.lower().replace(" ", "-"))
        self.CurrentDataDir = copy.copy(self.DataDir)

    def _cdd_td(self, *sub_dir, **kwargs):
        """
        Change directory to package data directory and sub-directories (and/or a file).

        The directory for this module: ``"dat\\line-data\\track-diagrams"``.

        :param sub_dir: sub-directory or sub-directories (and/or a file)
        :type sub_dir: str
        :param kwargs: optional parameters of `os.makedirs`_, e.g. ``mode=0o777``
        :return: path to the backup data directory for ``LOR``
        :rtype: str

        .. _`os.makedirs`: https://docs.python.org/3/library/os.html#os.makedirs

        :meta private:
        """

        path = cd(self.DataDir, *sub_dir, mkdir=True, **kwargs)

        return path

    def get_track_diagrams_items(self, update=False, verbose=False):
        """
        Get catalogue of track diagrams.

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console, defaults to ``True``
        :type verbose: bool or int
        :return: catalogue of railway station data
        :rtype: dict

        **Example**::

            >>> from pyrcs.line_data import TrackDiagrams

            >>> td = TrackDiagrams()

            >>> # trk_diagr_items = td.get_track_diagrams_items(update=True, verbose=True)
            >>> trk_diagr_items = td.get_track_diagrams_items()

            >>> type(trk_diagr_items)
            dict
            >>> list(trk_diagr_items.keys())
            ['Track diagrams']
        """

        cat_json = '-'.join(x for x in urllib.parse.urlparse(self.SourceURL).path.replace(
            '.shtm', '.json').split('/') if x)
        path_to_cat = cd_dat("catalogue", cat_json)

        if os.path.isfile(path_to_cat) and not update:
            items = load_pickle(path_to_cat)

        else:
            if verbose == 2:
                print("Collecting a list of {} items".format(self.Key.lower()), end=" ... ")

            try:
                source = requests.get(self.SourceURL, headers=fake_requests_headers())
            except requests.exceptions.ConnectionError:
                print("Failed. ") if verbose == 2 else ""
                print_conn_err(update=update, verbose=verbose)
                items = load_pickle(path_to_cat)

            else:
                try:
                    soup = bs4.BeautifulSoup(source.text, 'lxml')
                    h3 = {x.get_text(strip=True) for x in soup.find_all('h3', text=True)}
                    items = {self.Key: h3}

                    print("Done. ") if verbose == 2 else ""

                    save_pickle(items, path_to_cat, verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(e))
                    items = None

        return items

    def collect_sample_catalogue(self, confirmation_required=True, verbose=False):
        """
        Collect catalogue of sample railway track diagrams from source web page.

        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: catalogue of sample railway track diagrams and
            date of when the catalogue was last updated
        :rtype: dict or None

        **Example**::

            >>> from pyrcs.line_data import TrackDiagrams

            >>> td = TrackDiagrams()

            >>> track_diagrams_catalog = td.collect_sample_catalogue()
            To collect the catalogue of sample track diagrams? [No]|Yes: yes

            >>> type(track_diagrams_catalog)
            dict
            >>> list(track_diagrams_catalog.keys())
            ['Track diagrams', 'Last updated date']

            >>> td_dat = track_diagrams_catalog['Track diagrams']

            >>> type(td_dat)
            dict
            >>> list(td_dat.keys())
            ['Main line diagrams', 'Tram systems', 'London Underground', 'Miscellaneous']

            >>> main_line_diagrams = td_dat['Main line diagrams']

            >>> type(main_line_diagrams)
            tuple

            >>> type(main_line_diagrams[1])
            pandas.core.frame.DataFrame
            >>> main_line_diagrams[1].head()
                                         Description                               FileURL
            0  South Central area (1985) 10.4Mb file  http://www.railwaycodes.org.uk/li...
            1   South Eastern area (1976) 5.4Mb file  http://www.railwaycodes.org.uk/li...
        """

        if confirmed("To collect the catalogue of sample {}?".format(self.Key.lower()),
                     confirmation_required=confirmation_required):

            if verbose == 2:
                print("Collecting the catalogue of sample {}".format(self.Key.lower()),
                      end=" ... ")

            track_diagrams_catalogue = None

            try:
                source = requests.get(self.SourceURL, headers=fake_requests_headers())
            except requests.exceptions.ConnectionError:
                print("Failed. ") if verbose == 2 else ""
                print_conn_err(verbose=verbose)

            else:
                try:
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
                                cold_soup = cold_soup.find_next('a') \
                                    if h3.text == 'Miscellaneous' \
                                    else cold_soup.find_next_sibling('a')

                        meta = pd.DataFrame(zip(info, urls), columns=['Description', 'FileURL'])

                        track_diagrams_catalogue_.update({h3.text: (desc, meta)})

                        h3 = h3.find_next_sibling('h3')

                    track_diagrams_catalogue = {self.Key: track_diagrams_catalogue_,
                                                self.LUDKey: self.LUD}

                    print("Done. ") if verbose == 2 else ""

                    pickle_filename = self.Key.lower().replace(" ", "-") + ".pickle"
                    path_to_pickle = self._cdd_td(pickle_filename)
                    save_pickle(track_diagrams_catalogue, path_to_pickle, verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(e))

            return track_diagrams_catalogue

    def fetch_sample_catalogue(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch catalogue of sample railway track diagrams from local backup.

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param pickle_it: whether to save the data as a pickle file, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of a folder where the pickle file is to be saved, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: catalogue of sample railway track diagrams and
            date of when the catalogue was last updated
        :rtype: dict

        **Example**::

            >>> from pyrcs.line_data import TrackDiagrams

            >>> td = TrackDiagrams()

            >>> # trk_diagr_cat = td.fetch_sample_catalogue(update=True, verbose=True)
            >>> trk_diagr_cat = td.fetch_sample_catalogue()

            >>> type(trk_diagr_cat)
            dict
            >>> list(trk_diagr_cat.keys())
            ['Track diagrams', 'Last updated date']

            >>> td_dat = trk_diagr_cat['Track diagrams']

            >>> type(td_dat)
            dict
            >>> list(td_dat.keys())
            ['Main line diagrams', 'Tram systems', 'London Underground', 'Miscellaneous']

            >>> main_line_diagrams = td_dat['Main line diagrams']

            >>> type(main_line_diagrams)
            tuple

            >>> type(main_line_diagrams[1])
            pandas.core.frame.DataFrame
            >>> main_line_diagrams[1].head()
                                         Description                               FileURL
            0  South Central area (1985) 10.4Mb file  http://www.railwaycodes.org.uk/li...
            1   South Eastern area (1976) 5.4Mb file  http://www.railwaycodes.org.uk/li...
        """

        pickle_filename = self.Key.lower().replace(" ", "-") + ".pickle"
        path_to_pickle = self._cdd_td(pickle_filename)

        if os.path.isfile(path_to_pickle) and not update:
            track_diagrams_catalogue = load_pickle(path_to_pickle)

        else:
            verbose_ = False if data_dir or not verbose else (2 if verbose == 2 else True)

            track_diagrams_catalogue = self.collect_sample_catalogue(
                confirmation_required=False, verbose=verbose_)

            if track_diagrams_catalogue:
                if pickle_it and data_dir:
                    self.CurrentDataDir = validate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, pickle_filename)
                    save_pickle(track_diagrams_catalogue, path_to_pickle, verbose=verbose)

            else:
                print("No data of the sample {} catalogue has been freshly collected.".format(
                    self.Key.lower()))
                track_diagrams_catalogue = load_pickle(path_to_pickle)

        return track_diagrams_catalogue
