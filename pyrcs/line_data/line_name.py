"""
Collect `railway line names <http://www.railwaycodes.org.uk/misc/line_names.shtm>`_.
"""

from pyhelpers.dir import cd

from ..parser import *
from ..utils import *


class LineNames:
    """
    A class for collecting data of `railway line names`_.

    .. _`railway line names`: http://www.railwaycodes.org.uk/misc/line_names.shtm
    """

    #: Name of the data
    NAME = 'Railway line names'
    #: Key of the `dict <https://docs.python.org/3/library/stdtypes.html#dict>`_-type data
    KEY = 'Line names'
    #: URL of the main web page of the data
    URL = urllib.parse.urljoin(home_page_url(), '/line/line_names.shtm')
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
        :ivar str last_updated_date: last update date
        :ivar str data_dir: path to the data directory
        :ivar str current_data_dir: path to the current data directory

        **Examples**::

            >>> from pyrcs.line_data import LineNames  # from pyrcs import LineNames

            >>> ln = LineNames()

            >>> print(ln.NAME)
            Railway line names

            >>> print(ln.URL)
            http://www.railwaycodes.org.uk/misc/line_names.shtm
        """

        print_conn_err(verbose=verbose)

        self.catalogue = get_catalogue(url=self.URL, update=update, confirmation_required=False)

        self.last_updated_date = get_last_updated_date(url=self.URL, parsed=True, as_date_type=False)

        self.data_dir, self.current_data_dir = init_data_dir(self, data_dir, category="line-data")

    def _cdd(self, *sub_dir, **kwargs):
        """
        Change directory to package data directory and subdirectories (and/or a file).

        The directory for this module: ``"data\\line-data\\line-names"``.

        :param sub_dir: subdirectory or subdirectories (and/or a file)
        :type sub_dir: str
        :param kwargs: [optional] parameters of the function `pyhelpers.dir.cd`_
        :return: path to the backup data directory for the class
            :py:class:`~pyrcs.line_data.line_name.LineNames`
        :rtype: str

        .. _pyhelpers.dir.cd:
            https://pyhelpers.readthedocs.io/en/latest/_generated/pyhelpers.dir.cd.html
        """

        path = cd(self.data_dir, *sub_dir, mkdir=True, **kwargs)

        return path

    @staticmethod
    def _parse_route(x):
        """
        Parse route column.
        """
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
        Collect data of `railway line names`_ from source web page.

        .. _`railway line names`: http://www.railwaycodes.org.uk/misc/line_names.shtm

        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: railway line names and routes data and date of when the data was last updated
        :rtype: dict or None

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

        if confirmed(f"To collect British {data_name}\n?", confirmation_required=confirmation_required):

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
                    line_names[rte_col] = line_names.Route.map(self._parse_route).apply(pd.Series)

                    last_updated_date = get_last_updated_date(self.URL)

                    line_names_data = {
                        self.KEY: line_names,
                        self.KEY_TO_LAST_UPDATED_DATE: last_updated_date
                    }

                    if verbose == 2:
                        print("Done.")

                    save_data_to_file(
                        self, data=line_names_data, data_name=self.KEY, ext=".pickle", verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(e))

            return line_names_data

    def fetch_codes(self, update=False, dump_dir=None, verbose=False):
        """
        Fetch data of `railway line names`_.

        .. _`railway line names`: http://www.railwaycodes.org.uk/misc/line_names.shtm

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param dump_dir: pathname of a directory where the data file is dumped, defaults to ``None``
        :type dump_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: railway line names and routes data and date of when the data was last updated
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
            cls=self, method='collect_codes', data_name=self.KEY, ext=".pickle",
            update=update, dump_dir=dump_dir, verbose=verbose)

        return line_names_data
