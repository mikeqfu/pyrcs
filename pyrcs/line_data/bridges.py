"""
Collect data of `railway bridges <http://www.railwaycodes.org.uk/bridges/bridges0.shtm>`_.
"""

import copy

from pyhelpers.dir import cd, validate_input_data_dir

from pyrcs.utils import *
from pyrcs.utils import _cd_dat


class Bridges:
    """
    A class for collecting data of railway bridges.

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

        >>> print(bridges.Name)
        Railway bridges

        >>> print(bridges.SourceURL)
        http://www.railwaycodes.org.uk/bridges/bridges0.shtm
    """

    def __init__(self, data_dir=None, verbose=True):
        """
        Constructor method.
        """
        if not is_internet_connected():
            print_connection_error(verbose=verbose)

        self.Name = 'Railway bridges'
        self.Key = 'Bridges'

        self.HomeURL = homepage_url()
        self.SourceURL = urllib.parse.urljoin(self.HomeURL, '/bridges/bridges0.shtm')

        self.LUDKey = 'Last updated date'
        self.LUD = get_last_updated_date(url=self.SourceURL, parsed=True, as_date_type=False)

        if data_dir:
            self.DataDir = validate_input_data_dir(data_dir)
        else:
            self.DataDir = _cd_dat("line-data", self.Key.lower())
        self.CurrentDataDir = copy.copy(self.DataDir)

    def _cdd_bdg(self, *sub_dir, **kwargs):
        """
        Change directory to package data directory and sub-directories (and/or a file).

        The directory for this module: ``"dat\\line-data\\bridges"``.

        :param sub_dir: sub-directory or sub-directories (and/or a file)
        :type sub_dir: str
        :param kwargs: optional parameters of `pyhelpers.dir.cd`_
        :return: path to the backup data directory for the class ``Bridges``
        :rtype: str

        .. _pyhelpers.dir.cd:
            https://pyhelpers.readthedocs.io/en/latest/_generated/pyhelpers.dir.cd.html
        """

        path = cd(self.DataDir, *sub_dir, mkdir=True, **kwargs)

        return path
