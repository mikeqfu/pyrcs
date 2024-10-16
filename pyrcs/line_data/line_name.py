"""
Collects data of `railway line names <http://www.railwaycodes.org.uk/misc/line_names.shtm>`_.
"""

import re
import urllib.parse

import pandas as pd
import requests
from pyhelpers.dirs import cd
from pyhelpers.ops import confirmed, fake_requests_headers

from ..parser import get_catalogue, get_last_updated_date, parse_table
from ..utils import fetch_data_from_file, format_err_msg, home_page_url, init_data_dir, \
    print_collect_msg, print_conn_err, print_inst_conn_err, save_data_to_file


class LineNames:
    """
    A class for collecting data of
    `railway line names <http://www.railwaycodes.org.uk/misc/line_names.shtm>`_.
    """

    #: The name of the data.
    NAME: str = 'Railway line names'
    #: The key for accessing the data.
    KEY: str = 'Line names'

    #: The URL of the main web page for the data.
    URL: str = urllib.parse.urljoin(home_page_url(), '/line/line_names.shtm')

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

        print_conn_err(verbose=verbose)

        self.catalogue = get_catalogue(url=self.URL, update=update, confirmation_required=False)

        self.last_updated_date = get_last_updated_date(url=self.URL)

        self.data_dir, self.current_data_dir = init_data_dir(self, data_dir, category="line-data")

    def _cdd(self, *sub_dir, mkdir=True, **kwargs):
        """
        Changes the current directory to the package's data directory,
        or its specified subdirectories (or file).

        The default data directory for this class is: ``"data\\line-data\\line-names"``.

        :param sub_dir: One or more subdirectories and/or a file to navigate to
            within the data directory.
        :type sub_dir: str
        :param mkdir: Whether to create the specified directory if it doesn't exist;
            defaults to ``True``.
        :type mkdir: bool
        :param kwargs: [Optional] Additional parameters for the `pyhelpers.dir.cd()`_ function.
        :return: The path to the backup data directory or its specified subdirectories (or file).
        :rtype: str

        .. _`pyhelpers.dir.cd()`:
            https://pyhelpers.readthedocs.io/en/latest/_generated/pyhelpers.dir.cd.html
        """

        kwargs.update({'mkdir': mkdir})
        path = cd(self.data_dir, *sub_dir, **kwargs)

        return path

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

    def collect_codes(self, confirmation_required=True, verbose=False):
        """
        Collects data of `railway line names`_ and associated route data from the source web page.

        .. _`railway line names`: http://www.railwaycodes.org.uk/misc/line_names.shtm

        :param confirmation_required: Whether user confirmation is required before proceeding;
            defaults to ``True``.
        :type confirmation_required: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
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
            0           Abbey Line  ...       None
            1        Airedale Line  ...       None
            2          Argyle Line  ...       None
            3     Arun Valley Line  ...       None
            4  Atlantic Coast Line  ...       None
            [5 rows x 3 columns]
        """

        data_name = self.NAME.lower()

        if confirmed(
                f"To collect British {data_name}\n?", confirmation_required=confirmation_required):

            print_collect_msg(
                data_name=data_name, verbose=verbose, confirmation_required=confirmation_required)

            line_names_data = None

            try:
                source = requests.get(url=self.URL, headers=fake_requests_headers())

            except Exception as e:
                if verbose == 2:
                    print("Failed. ", end="")
                print_inst_conn_err(verbose=verbose, e=e)

            else:
                try:
                    columns, records = parse_table(source=source, parser='html.parser')
                    line_names = pd.DataFrame(
                        [[rec.replace('\xa0', '').strip() for rec in record] for record in records],
                        columns=columns)

                    rte_col = ['Route', 'Route_note']
                    temp = line_names['Route'].map(self._parse_route)
                    line_names[rte_col] = pd.DataFrame(zip(*temp)).T

                    line_names_data = {
                        self.KEY: line_names,
                        self.KEY_TO_LAST_UPDATED_DATE: get_last_updated_date(self.URL)
                    }

                    if verbose == 2:
                        print("Done.")

                    save_data_to_file(
                        self, data=line_names_data, data_name=self.KEY, ext=".pkl", verbose=verbose)

                except Exception as e:
                    print(f"Failed. {format_err_msg(e)}")

            return line_names_data

    def fetch_codes(self, update=False, dump_dir=None, verbose=False):
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

        line_names_data = fetch_data_from_file(
            self, method='collect_codes', data_name=self.KEY, ext=".pkl",
            update=update, dump_dir=dump_dir, verbose=verbose)

        return line_names_data
