"""
Collects British `railway track diagrams <http://www.railwaycodes.org.uk/track/diagrams0.shtm>`_.
"""

import urllib.parse

import bs4
import pandas as pd
from pyhelpers._cache import _print_failure_message

from .._base import _Base
from ..parser import _get_last_updated_date
from ..utils import cd_data, homepage_url


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
    URL: str = urllib.parse.urljoin(homepage_url(), '/line/diagrams0.shtm')

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
        """
        Parse and extract track diagram structural collections from the page source.

        This internal routine scans through HTML DOM nodes to group diagram metadata, hyperlinks,
        and description fields under explicit category keys before persisting them locally.

        :param source: The network response payload containing target document source content.
        :type source: requests.Response
        :param verbose: Whether to print functional status to the console window.
            Defaults to ``False``.
        :type verbose: bool | int
        :return: A structured map containing categorised items alongside dates, or ``None``.
        :rtype: dict | None
        """

        track_diagrams_catalogue_ = {}

        try:
            soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

            h3 = soup.find('h3', string=True, attrs={'class': None})
            while h3:
                category_name = h3.get_text(strip=True)

                # Description parsing with structure tag protection
                if category_name == 'Miscellaneous':
                    desc = [x.get_text(strip=True) for x in h3.find_next_siblings('p')]
                else:
                    sibling_p = h3.find_next_sibling('p')
                    desc = sibling_p.get_text(strip=True).replace('\xa0', '') if sibling_p else ''

                # Extract file references and metadata information block sections
                cold_soup = h3.find_next('div', attrs={'class': 'columns'})
                if cold_soup:
                    info = [
                        x.get_text(strip=True) for x in cold_soup.find_all('p')
                        if x.string != '\xa0'
                    ]
                    urls = [
                        urllib.parse.urljoin(self.URL, a.get('href'))
                        for a in cold_soup.find_all('a')
                        if a.get('href')
                    ]

                else:
                    # Bounded navigation loop avoids crossing section limits
                    next_h3 = h3.find_next_sibling('h3')
                    cold_soup = h3.find_next('a', attrs={'target': '_blank'})
                    info, urls = [], []

                    while cold_soup:
                        # Ensure navigation stays confined within the current section container
                        if (next_h3 and
                                cold_soup.replace_with(cold_soup) in next_h3.find_all_previous()):
                            pass  # element is within current block context bounds

                        # Simple global position validation boundary logic check
                        current_h3_context = cold_soup.find_previous('h3')
                        if (current_h3_context and
                                current_h3_context.get_text(strip=True) != category_name):
                            break

                        info.append(cold_soup.get_text(strip=True))
                        url_path = cold_soup.get('href')
                        urls.append(urllib.parse.urljoin(self.URL, url_path) if url_path else '')

                        if category_name == 'Miscellaneous':
                            cold_soup = cold_soup.find_next('a')
                        else:
                            cold_soup = cold_soup.find_next_sibling('a')

                meta = pd.DataFrame(data=zip(info, urls), columns=['description', 'file_url'])

                track_diagrams_catalogue_.update({category_name: (desc, meta)})

                h3 = h3.find_next_sibling('h3')

            track_diagrams_catalogue = {
                self.KEY: track_diagrams_catalogue_,
                self.KEY_TO_LAST_UPDATED_DATE: _get_last_updated_date(soup=soup),
            }

            if verbose in {True, 1}:
                print("Done.")

            self._save_data_to_file(
                data_name=self.KEY.lower(),
                data=track_diagrams_catalogue,
                dump_dir=cd_data("catalogue"),
                verbose=verbose
            )

            return track_diagrams_catalogue

        except Exception as e:
            _print_failure_message(e)

        return None

    def collect_catalogue(self, confirmation_required=True, verbose=False, raise_error=False):
        # noinspection PyShadowingNames,PyUnresolvedReferences
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

            >>> track_diagrams_catalogue = td.collect_catalogue()
            To collect the catalogue of track diagrams
            ? [No]|Yes: yes

            >>> type(track_diagrams_catalogue)
            dict
            >>> list(track_diagrams_catalogue.keys())
            ['Track diagrams', 'Last updated date']

            >>> td_dat = track_diagrams_catalogue['Track diagrams']
            >>> list(td_dat.keys())
            ['Main line diagrams', 'Tram systems', 'London Underground', 'Miscellaneous']

            >>> main_line_diagrams = td_dat['Main line diagrams']
            >>> type(main_line_diagrams)
            tuple
            >>> type(main_line_diagrams[1])
            pandas.core.frame.DataFrame
            >>> main_line_diagrams[1]
                                       description                                       file_url
            0  South Central area(1985)10.4Mb file  http://www.railwaycodes.org.uk/line/track/...
            1   South Eastern area(1976)5.4Mb file  http://www.railwaycodes.org.uk/line/track/...
        """

        track_diagrams_catalogue = self._collect_data_from_source(
            data_name=self.KEY.lower(),
            method=self._collect_catalogue,
            url=self.URL,
            confirmation_required=confirmation_required,
            verbose=verbose,
            raise_error=raise_error
        )

        return track_diagrams_catalogue

    def fetch_catalogue(self, update=False, dump_dir=None, verbose=False, **kwargs):
        # noinspection PyShadowingNames,PyUnresolvedReferences
        """
        Fetch the catalogue of `railway track diagrams`_.

        .. _`railway track diagrams`: http://www.railwaycodes.org.uk/track/diagrams0.shtm

        This method retrieves the structured track diagram catalogue either from a local file
        cache or by parsing the live online platform source.

        :param update: Whether to check for updates to the package data. Defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved.
            Defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console. Defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the catalogue of railway track diagrams and
            the date it was last updated.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.line_data import TrackDiagrams  # from pyrcs import TrackDiagrams

            >>> td = TrackDiagrams()

            >>> track_diagrams_catalogue = td.fetch_catalogue()

            >>> type(track_diagrams_catalogue)
            dict
            >>> list(track_diagrams_catalogue.keys())
            ['Track diagrams', 'Last updated date']

            >>> td_dat = track_diagrams_catalogue['Track diagrams']
            >>> list(td_dat.keys())
            ['Main line diagrams', 'Tram systems', 'London Underground', 'Miscellaneous']

            >>> main_line_diagrams = td_dat['Main line diagrams']
            >>> type(main_line_diagrams)
            tuple
            >>> type(main_line_diagrams[1])
            pandas.core.frame.DataFrame
            >>> main_line_diagrams[1]
                                       description                                       file_url
            0  South Central area(1985)10.4Mb file  http://www.railwaycodes.org.uk/line/track/...
            1   South Eastern area(1976)5.4Mb file  http://www.railwaycodes.org.uk/line/track/...
        """

        # Define internal resolution configurations safely
        default_args = {
            'data_name': self.KEY,
            'method': self.collect_catalogue,
            'data_dir': cd_data("catalogue"),
        }
        # Merge dictionaries safely using unpacking to prevent mutating external kwargs references
        merged_kwargs = default_args | kwargs

        track_diagrams_catalogue = self._fetch_data_from_file(
            update=update,
            dump_dir=dump_dir,
            verbose=verbose,
            **merged_kwargs
        )

        return track_diagrams_catalogue
