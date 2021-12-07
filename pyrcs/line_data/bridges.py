"""
Collect data of `railway bridges <http://www.railwaycodes.org.uk/bridges/bridges0.shtm>`_.
"""

from pyhelpers.dir import cd

from pyrcs.utils import *


class Bridges:
    """
    A class for collecting data of railway bridges.

    """

    NAME = 'Railway bridges'
    KEY = 'Bridges'

    URL = urllib.parse.urljoin(home_page_url(), '/bridges/bridges0.shtm')

    KEY_TO_LAST_UPDATED_DATE = 'Last updated date'

    def __init__(self, data_dir=None, verbose=True):
        """
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

            >>> from pyrcs.line_data import Bridges

            >>> bridges = Bridges()

            >>> print(bridges.NAME)
            Railway bridges

            >>> print(bridges.URL)
            http://www.railwaycodes.org.uk/bridges/bridges0.shtm
        """

        print_connection_error(verbose=verbose)

        self.last_updated_date = get_last_updated_date(url=self.URL, parsed=True, as_date_type=False)

        self.data_dir, self.current_data_dir = init_data_dir(self, data_dir, category="line-data")

    def _cdd_bdg(self, *sub_dir, **kwargs):
        """
        Change directory to package data directory and subdirectories (and/or a file).

        The directory for this module: ``"dat\\line-data\\bridges"``.

        :param sub_dir: subdirectory or subdirectories (and/or a file)
        :type sub_dir: str
        :param kwargs: optional parameters of `pyhelpers.dir.cd`_
        :return: path to the backup data directory for the class ``Bridges``
        :rtype: str

        .. _pyhelpers.dir.cd:
            https://pyhelpers.readthedocs.io/en/latest/_generated/pyhelpers.dir.cd.html
        """

        path = cd(self.data_dir, *sub_dir, mkdir=True, **kwargs)

        return path

    def collect_bridges(self, confirmation_required=True, verbose=False):
        """
        Collect data of railway bridges from source web page.

        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: information about railway bridges and date of when the data was last updated
        :rtype: dict or None

        **Example**::

        """

        data_name = "data of {}" + self.NAME.lower()

        if confirmed(f"To collect {data_name}?", confirmation_required=confirmation_required):

            print_collect_msg(
                data_name=data_name, verbose=verbose, confirmation_required=confirmation_required)

            bridges_data = None

            try:
                """
                url = 'http://www.railwaycodes.org.uk/bridges/bridges0.shtm'
                source = requests.get(url, headers=fake_requests_headers(randomized=True))
                """
                source = requests.get(self.URL, headers=fake_requests_headers(randomized=True))
            except requests.ConnectionError:
                print("Failed. ") if verbose == 2 else ""
                print_conn_err(verbose=verbose)

            else:
                try:
                    row_lst, header = parse_table(source, parser='lxml')




                except Exception as e:
                    print("Failed. {}".format(e))

            return bridges_data
