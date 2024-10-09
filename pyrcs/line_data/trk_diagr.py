"""
Collects British `railway track diagrams <http://www.railwaycodes.org.uk/track/diagrams0.shtm>`_.
"""

import os
import urllib.parse

import bs4
import pandas as pd
import requests
from pyhelpers.dirs import cd
from pyhelpers.ops import confirmed, fake_requests_headers
from pyhelpers.store import load_data

from ..parser import get_last_updated_date
from ..utils import cd_data, fetch_data_from_file, format_err_msg, home_page_url, init_data_dir, \
    print_collect_msg, print_conn_err, print_inst_conn_err, save_data_to_file


class TrackDiagrams:
    """
    A class for collecting data of British
    `railway track diagrams <http://www.railwaycodes.org.uk/track/diagrams0.shtm>`_.
    """

    #: The name of the data.
    NAME: str = 'Railway track diagrams'
    #: The key for accessing the data.
    KEY: str = 'Track diagrams'

    #: The URL of the main web page for the data.
    URL: str = urllib.parse.urljoin(home_page_url(), '/line/diagrams0.shtm')

    #: The key used to reference the last updated date in the data.
    KEY_TO_LAST_UPDATED_DATE: str = 'Last updated date'

    def __init__(self, data_dir=None, update=False, verbose=True):
        """
        :param data_dir: The name of the directory for storing the data; defaults to ``None``.
        :type data_dir: str | None
        :param update: Whether to check for updates to the data catalogue; defaults to ``False``.
        :type update: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``True``.
        :type verbose: bool | int

        :ivar dict catalogue: The catalogue of the data.
        :ivar str last_updated_date: The date when the data was last updated.
        :ivar str data_dir: The path to the directory containing the data.
        :ivar str current_data_dir: The path to the current data directory.

        **Examples**::

            >>> from pyrcs.line_data import TrackDiagrams  # from pyrcs import TrackDiagrams
            >>> td = TrackDiagrams()
            >>> td.NAME
            'Railway track diagrams'
            >>> td.URL
            'http://www.railwaycodes.org.uk/line/diagrams0.shtm'
        """

        print_conn_err(verbose=verbose)

        self.last_updated_date = get_last_updated_date(url=self.URL)

        self.catalogue = self.fetch_catalogue(
            update=update, verbose=True if verbose == 2 else False)

        self.data_dir, self.current_data_dir = init_data_dir(self, data_dir, category="line-data")

    def _cdd(self, *sub_dir, mkdir=True, **kwargs):
        """
        Changes the current directory to the package's data directory,
        or its specified subdirectories (or file).

        The default data directory for this class is: ``"data\\line-data\\track-diagrams"``.

        :param sub_dir: One or more subdirectories and/or a file to navigate to
            within the data directory.
        :type sub_dir: str
        :param mkdir: Whether to create the specified directory if it doesn't exist;
            defaults to ``True``.
        :type mkdir: bool
        :param kwargs: [Optional] Additional parameters for the `pyhelpers.dir.cd()`_ function.
        :return: The path to the backup data directory or its specified subdirectories (or file).
        :rtype: str

        .. _pyhelpers.dir.cd():
            https://pyhelpers.readthedocs.io/en/latest/_generated/pyhelpers.dir.cd.html
        """

        kwargs.update({'mkdir': mkdir})
        path = cd(self.data_dir, *sub_dir, **kwargs)

        return path

    def _get_items(self, update=False, verbose=False):
        """
        Gets the catalogue of track diagrams.

        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: The catalogue of railway station data.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.line_data import TrackDiagrams  # from pyrcs import TrackDiagrams
            >>> td = TrackDiagrams()
            >>> trk_diagr_items = td._get_items()
            >>> trk_diagr_items
            {'Track diagrams': {'London Underground',
              'Main line diagrams',
              'Miscellaneous',
              'Tram systems'}}
        """

        dat_name = self.KEY.lower()
        ext = ".pkl"
        path_to_cat = cd_data("catalogue", dat_name.replace(" ", "-") + ext)

        if os.path.isfile(path_to_cat) and not update:
            items = load_data(path_to_cat)

        else:
            if verbose == 2:
                print("Collecting a list of {} items".format(dat_name), end=" ... ")

            items = None

            try:
                source = requests.get(url=self.URL, headers=fake_requests_headers())

            except Exception as e:
                if verbose == 2:
                    print("Failed. ", end="")
                print_inst_conn_err(update=update, verbose=verbose, e=e)

            else:
                try:
                    soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')
                    h3 = {x.get_text(strip=True) for x in soup.find_all('h3', string=True)}
                    items = {self.KEY: h3}

                    if verbose == 2:
                        print("Done.")

                    save_data_to_file(
                        self, data=items, data_name=dat_name, ext=ext, dump_dir=cd_data("catalogue"),
                        verbose=verbose)

                except Exception as e:
                    print(f"Failed. {format_err_msg(e)}")

        return items

    def _collect_catalogue(self, source, data_name, verbose):
        track_diagrams_catalogue_ = {}

        try:
            soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

            h3 = soup.find('h3', string=True, attrs={'class': None})
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
                    urls = [
                        urllib.parse.urljoin(self.URL, a.get('href'))
                        for a in cold_soup.find_all('a')]
                else:
                    cold_soup = h3.find_next('a', attrs={'target': '_blank'})
                    info, urls = [], []

                    while cold_soup:
                        info.append(cold_soup.text)
                        urls.append(urllib.parse.urljoin(self.URL, cold_soup['href']))
                        if h3.text == 'Miscellaneous':
                            cold_soup = cold_soup.find_next('a')
                        else:
                            cold_soup = cold_soup.find_next_sibling('a')

                meta = pd.DataFrame(data=zip(info, urls), columns=['Description', 'FileURL'])

                track_diagrams_catalogue_.update({h3.text: (desc, meta)})

                h3 = h3.find_next_sibling('h3')

            track_diagrams_catalogue = {
                self.KEY: track_diagrams_catalogue_,
                self.KEY_TO_LAST_UPDATED_DATE: self.last_updated_date,
            }

            if verbose == 2:
                print("Done.")

            save_data_to_file(
                self, data=track_diagrams_catalogue, data_name=data_name, ext=".pkl",
                dump_dir=cd_data("catalogue"), verbose=verbose)

        except Exception as e:
            print(f"Failed. {format_err_msg(e)}")
            track_diagrams_catalogue = None

        return track_diagrams_catalogue

    def collect_catalogue(self, confirmation_required=True, verbose=False):
        """
        Collects the catalogue of sample railway track diagrams from the source web page.

        :param confirmation_required: Whether user confirmation is required before proceeding;
            defaults to ``True``.
        :type confirmation_required: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the railway track diagram catalogue and
            the date it was last updated, or ``None`` if no data is collected.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.line_data import TrackDiagrams  # from pyrcs import TrackDiagrams
            >>> td = TrackDiagrams()
            >>> track_diagrams_catalog = td.collect_catalogue()
            To collect the catalogue of track diagrams
            ? [No]|Yes: yes
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
                                         Description                                         FileURL
            0  South Central area (1985) 10.4Mb file  http://www.railwaycodes.org.uk/line/track/d...
            1   South Eastern area (1976) 5.4Mb file  http://www.railwaycodes.org.uk/line/track/d...
        """

        data_name = self.KEY.lower()

        if confirmed(f"To collect the catalogue of {data_name}\n?", confirmation_required):
            print_collect_msg(data_name, verbose, confirmation_required)

            try:
                source = requests.get(url=self.URL, headers=fake_requests_headers())

            except Exception as e:
                if verbose == 2:
                    print("Failed. ", end="")
                print_inst_conn_err(verbose=verbose, e=e)

            else:
                track_diagrams_catalogue = self._collect_catalogue(source, data_name, verbose)

                return track_diagrams_catalogue

    def fetch_catalogue(self, update=False, dump_dir=None, verbose=False):
        """
        Fetches the catalogue of railway track diagrams.

        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the catalogue of railway track diagrams and
            the date it was last updated.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.line_data import TrackDiagrams  # from pyrcs import TrackDiagrams
            >>> td = TrackDiagrams()
            >>> trk_diagr_cat = td.fetch_catalogue()
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
                                         Description                                         FileURL
            0  South Central area (1985) 10.4Mb file  http://www.railwaycodes.org.uk/line/track/d...
            1   South Eastern area (1976) 5.4Mb file  http://www.railwaycodes.org.uk/line/track/d...
        """

        track_diagrams_catalogue = fetch_data_from_file(
            self, method='collect_catalogue', data_name=self.KEY, ext=".pkl", update=update,
            dump_dir=dump_dir, verbose=verbose, data_dir=cd_data("catalogue"))

        return track_diagrams_catalogue
