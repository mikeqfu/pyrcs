"""
Collect British `railway line names <http://www.railwaycodes.org.uk/misc/line_names.shtm>`_.
"""

from pyhelpers.dir import cd
from pyhelpers.store import load_pickle

from pyrcs.utils import *


class LineNames:
    """
    A class for collecting data of British railway line names.


    """

    NAME = 'Railway line names'
    KEY = 'Line names'

    URL = urllib.parse.urljoin(home_page_url(), '/line/line_names.shtm')

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
        :ivar str data_dir: path to the data directory
        :ivar str current_data_dir: path to the current data directory

        **Example**::

            >>> from pyrcs.line_data import LineNames

            >>> ln = LineNames()

            >>> print(ln.NAME)
            Railway line names

            >>> print(ln.URL)
            http://www.railwaycodes.org.uk/misc/line_names.shtm
        """
        if not is_internet_connected():
            print_connection_error(verbose=verbose)

        self.last_updated_date = get_last_updated_date(url=self.URL, parsed=True, as_date_type=False)

        self.catalogue = get_catalogue(url=self.URL, update=update, confirmation_required=False)

        self.data_dir, self.current_data_dir = init_data_dir(self, data_dir, category="line-data")

    def _cdd_ln(self, *sub_dir, **kwargs):
        """
        Change directory to package data directory and subdirectories (and/or a file).

        The directory for this module: ``"dat\\line-data\\line-names"``.

        :param sub_dir: subdirectory or subdirectories (and/or a file)
        :type sub_dir: str
        :param kwargs: optional parameters of `pyhelpers.dir.cd`_
        :return: path to the backup data directory for ``LineNames``
        :rtype: str

        .. _pyhelpers.dir.cd:
            https://pyhelpers.readthedocs.io/en/latest/_generated/pyhelpers.dir.cd.html
        """

        path = cd(self.data_dir, *sub_dir, mkdir=True, **kwargs)

        return path

    @staticmethod
    def _parse_route_column(x):
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

    def collect_line_names(self, confirmation_required=True, verbose=False):
        """
        Collect data of railway line names from source web page.

        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: railway line names and routes data and date of when the data was last updated
        :rtype: dict or None

        **Example**::

            >>> from pyrcs.line_data import LineNames

            >>> ln = LineNames()

            >>> line_names_dat = ln.collect_line_names()
            To collect British railway line names? [No]|Yes: yes

            >>> type(line_names_dat)
            dict
            >>> list(line_names_dat.keys())
            ['Line names', 'Last updated date']

            >>> print(ln.KEY)
            Line names

            >>> line_names_codes = line_names_dat['Line names']

            >>> type(line_names_codes)
            pandas.core.frame.DataFrame
            >>> line_names_codes.head()
                         Line name  ... Route_note
            0           Abbey Line  ...       None
            1        Airedale Line  ...       None
            2          Argyle Line  ...       None
            3     Arun Valley Line  ...       None
            4  Atlantic Coast Line  ...       None
            [5 rows x 3 columns]
        """

        data_name = "British" + self.NAME.lower()

        if confirmed(f"To collect {data_name}?", confirmation_required=confirmation_required):

            print_collect_msg(
                data_name=data_name, verbose=verbose, confirmation_required=confirmation_required)

            line_names_data = None

            try:
                source = requests.get(self.URL, headers=fake_requests_headers())
            except requests.ConnectionError:
                print("Failed. ") if verbose == 2 else ""
                print_conn_err(verbose=verbose)

            else:
                try:
                    row_lst, header = parse_table(source, parser='lxml')
                    line_names = pd.DataFrame(
                        [[r.replace('\xa0', '').strip() for r in row] for row in row_lst],
                        columns=header)

                    line_names[['Route', 'Route_note']] = \
                        line_names.Route.map(self._parse_route_column).apply(pd.Series)

                    last_updated_date = get_last_updated_date(self.URL)

                    line_names_data = {self.KEY: line_names,
                                       self.KEY_TO_LAST_UPDATED_DATE: last_updated_date}

                    print("Done. ") if verbose == 2 else ""

                    pickle_filename = self.KEY.lower().replace(" ", "-") + ".pickle"
                    path_to_pickle = self._cdd_ln(pickle_filename)
                    save_pickle(line_names_data, path_to_pickle, verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(e))

            return line_names_data

    def fetch_line_names(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch data of railway line names from local backup.

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param pickle_it: whether to save the data as a pickle file, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of a folder where the pickle file is to be saved, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: railway line names and routes data and date of when the data was last updated
        :rtype: dict

        **Example**::

            >>> from pyrcs.line_data import LineNames

            >>> ln = LineNames()

            >>> # line_names_dat = ln.fetch_line_names(update=True, verbose=True)
            >>> line_names_dat = ln.fetch_line_names()

            >>> type(line_names_dat)
            dict
            >>> list(line_names_dat.keys())
            ['Line names', 'Last updated date']

            >>> print(ln.KEY)
            Line names

            >>> line_names_codes = line_names_dat['Line names']

            >>> type(line_names_codes)
            pandas.core.frame.DataFrame
            >>> line_names_codes.head()
                         Line name  ... Route_note
            0           Abbey Line  ...       None
            1        Airedale Line  ...       None
            2          Argyle Line  ...       None
            3     Arun Valley Line  ...       None
            4  Atlantic Coast Line  ...       None
            [5 rows x 3 columns]
        """

        pickle_filename = self.KEY.lower().replace(" ", "-") + ".pickle"
        path_to_pickle = self._cdd_ln(pickle_filename)

        if os.path.isfile(path_to_pickle) and not update:
            line_names_data = load_pickle(path_to_pickle)

        else:
            verbose_ = False if data_dir or not verbose else (2 if verbose == 2 else True)

            line_names_data = self.collect_line_names(confirmation_required=False,
                                                      verbose=verbose_)

            if line_names_data:  # line-names is not None
                if pickle_it and data_dir:
                    self.current_data_dir = validate_dir(data_dir)
                    path_to_pickle = os.path.join(self.current_data_dir, pickle_filename)
                    save_pickle(line_names_data, path_to_pickle, verbose=verbose)
            else:
                print("No data of the railway {} has been freshly collected.".format(
                    self.KEY.lower()))
                line_names_data = load_pickle(path_to_pickle)

        return line_names_data
