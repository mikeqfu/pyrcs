"""Collect British `railway track diagrams <http://www.railwaycodes.org.uk/track/diagrams0.shtm>`_."""

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
    A class for collecting data of British `railway track diagrams`_.

    .. _`railway track diagrams`: http://www.railwaycodes.org.uk/track/diagrams0.shtm
    """

    #: Name of the data
    NAME = 'Railway track diagrams'
    #: Key of the `dict <https://docs.python.org/3/library/stdtypes.html#dict>`_-type data
    KEY = 'Track diagrams'
    #: URL of the main web page of the data
    URL = urllib.parse.urljoin(home_page_url(), '/line/diagrams0.shtm')
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

            >>> from pyrcs.line_data import TrackDiagrams  # from pyrcs import TrackDiagrams

            >>> td = TrackDiagrams()

            >>> print(td.NAME)
            Railway track diagrams

            >>> print(td.URL)
            http://www.railwaycodes.org.uk/line/diagrams0.shtm
        """

        print_conn_err(verbose=verbose)

        self.last_updated_date = get_last_updated_date(url=self.URL, parsed=True, as_date_type=False)

        self.data_dir, self.current_data_dir = init_data_dir(self, data_dir, category="line-data")

        self.catalogue = self._fetch_catalogue(update=update, verbose=True if verbose == 2 else False)

    def _cdd(self, *sub_dir, **kwargs):
        """
        Change directory to package data directory and subdirectories (and/or a file).

        The directory for this module: ``"data\\line-data\\track-diagrams"``.

        :param sub_dir: subdirectory or subdirectories (and/or a file)
        :type sub_dir: str
        :param kwargs: [optional] parameters of the function `pyhelpers.dir.cd`_
        :return: path to the backup data directory for the class
            :py:class:`~pyrcs.line_data.trk_diagr.TrackDiagrams`
        :rtype: str

        .. _pyhelpers.dir.cd:
            https://pyhelpers.readthedocs.io/en/latest/_generated/pyhelpers.dir.cd.html
        """

        path = cd(self.data_dir, *sub_dir, mkdir=True, **kwargs)

        return path

    def _get_items(self, update=False, verbose=False):
        """
        Get catalogue of track diagrams.

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console, defaults to ``True``
        :type verbose: bool or int
        :return: catalogue of railway station data
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
        ext = ".pickle"
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

    def _collect_catalogue(self, confirmation_required=True, verbose=False):
        """
        Collect catalogue of sample railway track diagrams from source web page.

        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: catalogue of railway track diagrams and date of when the catalogue was last updated
        :rtype: dict or None

        **Examples**::

            >>> from pyrcs.line_data import TrackDiagrams  # from pyrcs import TrackDiagrams

            >>> td = TrackDiagrams()

            >>> track_diagrams_catalog = td._collect_catalogue()
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

        if confirmed("To collect the catalogue of {}\n?".format(data_name), confirmation_required):

            print_collect_msg(data_name, verbose=verbose, confirmation_required=confirmation_required)

            track_diagrams_catalogue = None

            try:
                source = requests.get(url=self.URL, headers=fake_requests_headers())

            except Exception as e:
                if verbose == 2:
                    print("Failed. ", end="")
                print_inst_conn_err(verbose=verbose, e=e)

            else:
                try:
                    track_diagrams_catalogue_ = {}

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
                                for a in cold_soup.find_all('a')
                            ]
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
                        self, data=track_diagrams_catalogue, data_name=data_name, ext=".pickle",
                        dump_dir=cd_data("catalogue"), verbose=verbose)

                except Exception as e:
                    print(f"Failed. {format_err_msg(e)}")

            return track_diagrams_catalogue

    def _fetch_catalogue(self, update=False, dump_dir=None, verbose=False):
        """
        Fetch the catalogue of railway track diagrams.

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param dump_dir: pathname of a directory where the data file is dumped, defaults to ``None``
        :type dump_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: catalogue of sample railway track diagrams and
            date of when the catalogue was last updated
        :rtype: dict

        **Examples**::

            >>> from pyrcs.line_data import TrackDiagrams  # from pyrcs import TrackDiagrams

            >>> td = TrackDiagrams()

            >>> trk_diagr_cat = td._fetch_catalogue()
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
            cls=self, method='_collect_catalogue', data_name=self.KEY, ext=".pickle",
            update=update, dump_dir=dump_dir, verbose=verbose, data_dir=cd_data("catalogue"))

        return track_diagrams_catalogue
