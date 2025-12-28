"""
Collects data of `railway line names <http://www.railwaycodes.org.uk/misc/line_names.shtm>`_.
"""

import re
import urllib.parse

import pandas as pd

from .._base import _Base
from ..parser import _get_last_updated_date, parse_table
from ..utils import homepage_url


class LineNames(_Base):
    """
    A class for collecting data of
    `railway line names <http://www.railwaycodes.org.uk/misc/line_names.shtm>`_.
    """

    #: The name of the data.
    NAME: str = 'Railway line names'
    #: The key for accessing the data.
    KEY: str = 'Line names'

    #: The URL of the main web page for the data.
    URL: str = urllib.parse.urljoin(homepage_url(), '/line/line_names.shtm')

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

            >>> from pyrcs.line_data import LineNames  # from pyrcs import LineNames
            >>> ln = LineNames()
            >>> ln.NAME
            'Railway line names'
            >>> ln.URL
            'http://www.railwaycodes.org.uk/misc/line_names.shtm'
        """

        super().__init__(
            data_dir=data_dir, content_type='catalogue', data_category="line-data", update=update,
            verbose=verbose)

    @staticmethod
    def _parse_route(x):
        """Parse route column."""
        if 'Watford - Euston suburban route' in x:
            route, route_note = 'Watford - Euston suburban route', x

        elif ', including Moorgate - Farringdon' in x:
            route_note = 'including Moorgate - Farringdon'
            route = x.replace(', including Moorgate - Farringdon', '')

        elif re.match(r'.+(?= \[\')', x):
            route, route_note = re.split(r' \[\'\(?', x)
            route_note = route_note.strip(")']")

        elif re.match(r'.+\)$', x):
            if re.match(r'.+(?= - \()', x):
                route, route_note = x, None
            else:
                route, route_note = re.split(r' \(\[?\'?', x)
                route_note = route_note.rstrip('\'])')

        else:
            route, route_note = x, None

        return route, route_note

    def _collect_codes(self, source, verbose=False):
        (columns, records), soup = parse_table(source=source)
        line_names = pd.DataFrame(
            [[rec.replace('\xa0', '').strip() for rec in record] for record in records],
            columns=columns)

        rte_col = ['Route', 'Route_note']
        temp = line_names['Route'].map(self._parse_route)
        line_names[rte_col] = pd.DataFrame(zip(*temp)).T

        last_updated_date = _get_last_updated_date(soup=soup)
        line_names_data = {self.KEY: line_names, self.KEY_TO_LAST_UPDATED_DATE: last_updated_date}

        if verbose in {True, 1}:
            print("Done.")

        self._save_data_to_file(data=line_names_data, data_name=self.KEY, verbose=verbose)

        return line_names_data

    def collect_codes(self, confirmation_required=True, verbose=False, raise_error=False):
        """
        Collects data of `railway line names`_ and associated route data from the source web page.

        .. _`railway line names`: http://www.railwaycodes.org.uk/misc/line_names.shtm

        :param confirmation_required: Whether user confirmation is required;
            if ``confirmation_required=True`` (default), prompts the user for confirmation
            before proceeding with data collection.
        :type confirmation_required: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :param raise_error: Whether to raise the provided exception;
            if ``raise_error=False`` (default), the error will be suppressed.
        :type raise_error: bool
        :return: A dictionary containing railway line names, route data and the last update date,
            or ``None`` if no data is collected.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.line_data import LineNames  # from pyrcs import LineNames
            >>> ln = LineNames()
            >>> line_names_codes = ln.collect_codes()
            To collect British railway line names
            ? [No]|Yes: yes
            >>> type(line_names_codes)
            dict
            >>> list(line_names_codes.keys())
            ['Line names', 'Last updated date']
            >>> ln.KEY
            'Line names'
            >>> line_names_codes_dat = line_names_codes[ln.KEY]
            >>> type(line_names_codes_dat)
            pandas.core.frame.DataFrame
            >>> line_names_codes_dat.head()
                      Line name  ... Route_note
            0        Abbey Line  ...       None
            1     Aberdare Line  ...       None
            2     Airedale Line  ...       None
            3       Argyle Line  ...       None
            4  Arun Valley Line  ...       None
            [5 rows x 3 columns]
        """

        data = self._collect_data_from_source(
            data_name=self.NAME.lower(), method=self._collect_codes, url=self.URL,
            confirmation_required=confirmation_required, verbose=verbose,
            raise_error=raise_error)

        return data

    def fetch_codes(self, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetches data of `railway line names`_ and associated route data.

        .. _`railway line names`: http://www.railwaycodes.org.uk/misc/line_names.shtm

        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing railway line names, route data and the last update date.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.line_data import LineNames  # from pyrcs import LineNames
            >>> ln = LineNames()
            >>> line_names_codes = ln.fetch_codes()
            >>> type(line_names_codes)
            dict
            >>> list(line_names_codes.keys())
            ['Line names', 'Last updated date']
            >>> ln.KEY
            'Line names'
            >>> line_names_codes_dat = line_names_codes[ln.KEY]
            >>> type(line_names_codes_dat)
            pandas.core.frame.DataFrame
            >>> line_names_codes_dat.head()
                         Line name  ... Route_note
            0           Abbey Line  ...       None
            1        Airedale Line  ...       None
            2          Argyle Line  ...       None
            3     Arun Valley Line  ...       None
            4  Atlantic Coast Line  ...       None
            [5 rows x 3 columns]
        """

        kwargs.update({'data_name': self.KEY, 'method': self.collect_codes})

        line_names_data = self._fetch_data_from_file(
            update=update, dump_dir=dump_dir, verbose=verbose, **kwargs)

        return line_names_data
