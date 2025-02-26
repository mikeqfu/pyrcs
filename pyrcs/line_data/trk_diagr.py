"""
Collects British `railway track diagrams <http://www.railwaycodes.org.uk/track/diagrams0.shtm>`_.
"""

import urllib.parse

import bs4
import pandas as pd
from pyhelpers._cache import _print_failure_message

from .._base import _Base
from ..parser import _get_last_updated_date
from ..utils import cd_data, home_page_url


class TrackDiagrams(_Base):
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

        super().__init__(
            data_dir=data_dir, data_category="line-data", update=update, verbose=verbose)

        self.catalogue = self.fetch_catalogue(update=update, verbose=(verbose == 2 or False))

    def _collect_catalogue(self, source, verbose=False):
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
                self.KEY_TO_LAST_UPDATED_DATE: _get_last_updated_date(soup=soup),
            }

            if verbose in {True, 1}:
                print("Done.")

            self._save_data_to_file(
                data_name=self.KEY.lower(), data=track_diagrams_catalogue,
                dump_dir=cd_data("catalogue"), verbose=verbose)

            return track_diagrams_catalogue

        except Exception as e:
            _print_failure_message(e)

    def collect_catalogue(self, confirmation_required=True, verbose=False, raise_error=False):
        """
        Collects the catalogue of sample `railway track diagrams`_ from the source web page.

        .. _`railway track diagrams`: http://www.railwaycodes.org.uk/track/diagrams0.shtm

        :param confirmation_required: Whether user confirmation is required;
            if ``confirmation_required=True`` (default), prompts the user for confirmation
            before proceeding with data collection.
        :type confirmation_required: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :param raise_error: Whether to raise the provided exception;
            if ``raise_error=False`` (default), the error will be suppressed.
        :type raise_error: bool
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

        track_diagrams_catalogue = self._collect_data_from_source(
            data_name=self.KEY.lower(), method=self._collect_catalogue, url=self.URL,
            confirmation_required=confirmation_required, verbose=verbose, raise_error=raise_error)

        return track_diagrams_catalogue

    def fetch_catalogue(self, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetches the catalogue of `railway track diagrams`_.

        .. _`railway track diagrams`: http://www.railwaycodes.org.uk/track/diagrams0.shtm

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

        args = {
            'data_name': self.KEY,
            'method': self.collect_catalogue,
            'data_dir': cd_data("catalogue"),
        }
        kwargs.update(args)

        track_diagrams_catalogue = self._fetch_data_from_file(
            update=update, dump_dir=dump_dir, verbose=verbose, **kwargs)

        return track_diagrams_catalogue
