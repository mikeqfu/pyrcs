"""
Collects `driver/guard buzzer codes <http://www.railwaycodes.org.uk/misc/buzzer.shtm>`_.
"""

import urllib.parse

from .._base import _Base
from ..parser import parse_table
from ..utils import homepage_url


class Buzzer(_Base):
    """
    A class for collecting data of
    `buzzer codes <http://www.railwaycodes.org.uk/features/buzzer.shtm>`_.
    """

    #: The name of the data.
    NAME = 'Buzzer codes'
    #: The key for accessing the data.
    KEY = 'Buzzer codes'
    #: The URL of the main web page for the data.
    URL = urllib.parse.urljoin(homepage_url(), '/features/buzzer.shtm')
    #: The key used to reference the last updated date in the data.
    KEY_TO_LAST_UPDATED_DATE = 'Last updated date'

    def __init__(self, data_dir=None, update=False, verbose=True):
        """
        :param data_dir: The name of the directory for storing the data; defaults to ``None``.
        :type data_dir: str | None
        :param update: Whether to check for updates to the catalogue; defaults to ``False``.
        :type update: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``True``.
        :type verbose: bool | int

        :ivar dict catalogue: The catalogue of the data.
        :ivar str last_updated_date: The date when the data was last updated.
        :ivar str data_dir: The path to the directory containing the data.
        :ivar str current_data_dir: The path to the current data directory.

        **Examples**::

            >>> from pyrcs.other_assets import Buzzer  # from pyrcs import Buzzer
            >>> buz = Buzzer()
            >>> buz.NAME
            'Buzzer codes'
        """

        super().__init__(
            data_dir=data_dir, data_category="other-assets", update=update, verbose=verbose)

    def _collect_codes(self, source, verbose=False):
        """
        Collect and parse buzzer codes from the provided HTML source.

        This method extracts tabular buzzer code data from the HTML content, cleans
        and standardises multi-line column headers, and persists the resulting
        dataset.

        :param source: The HTTP response object or raw HTML content string.
        :type source: requests.Response | bs4.BeautifulSoup | str
        :param verbose: Whether to print progress logs. Defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the parsed buzzer codes and metadata.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Buzzer
            >>> buzzer = Buzzer()
            >>> # # Internal collection call
            >>> # data = buzzer._collect_codes(source=source, verbose=True)
        """

        codes_dat, soup = parse_table(source=source, parser='html.parser', as_dataframe=True)

        column_names = []
        for col in codes_dat.columns:
            lines = [line.strip() for line in str(col).splitlines() if line.strip()]
            if len(lines) > 1:
                header = f"{lines[0]} [{' '.join(lines[1:])}]"
            elif lines:
                header = lines[0]
            else:
                header = str(col)
            column_names.append(header)

        codes_dat.columns = column_names

        buzzer_codes = self._pack_and_save_data(
            data=codes_dat,
            soup=soup,
            dump_dir=self._cdd("..", "features"),
            verbose=verbose
        )

        return buzzer_codes

    def collect_codes(self, confirmation_required=True, verbose=False, raise_error=False):
        # noinspection unresolved-references
        """
        Collect data of `buzzer codes`_ from the source web page.

        .. _`buzzer codes`: http://www.railwaycodes.org.uk/misc/buzzer.shtm

        :param confirmation_required: Whether user confirmation is required;
            if ``confirmation_required=True`` (default), prompts the user for confirmation
            before proceeding with data collection.
        :type confirmation_required: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :param raise_error: Whether to raise the provided exception;
            if ``raise_error=False`` (default), the error will be suppressed.
        :type raise_error: bool
        :return: A dictionary containing the data of buzzer codes and
            the date they were last updated, or ``None`` if no data is collected.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.other_assets import Buzzer  # from pyrcs import Buzzer

            >>> buz = Buzzer()

            >>> buz_codes = buz.collect_codes(verbose=True)
            To collect data of buzzer codes?
             [No]|Yes: yes
            Collecting the data ... Done.

            >>> type(buz_codes)
            dict
            >>> list(buz_codes)
            ['Buzzer codes', 'Last updated date']

            >>> buz_codes_dat = buz_codes['Buzzer codes']
            >>> type(buz_codes_dat)
            pandas.DataFrame
            >>> buz_codes_dat.head()
              Code (number of buzzes or groups separate...                                 Meaning
            0                                            1                                    Stop
            1                                          1-2                             Close doors
            2                                            2                          Ready to start
            3                                          2-2     Create vacuum [used in early 1960s]
            4                                          2-2                       Do not open doors
        """

        buzzer_codes = self._collect_data_from_source(
            data_name=self.KEY.lower(),
            method=self._collect_codes,
            url=self.URL,
            confirmation_required=confirmation_required,
            confirmation_prompt=f"To collect data of {self.KEY.lower()}?\n",
            verbose=verbose,
            raise_error=raise_error
        )

        return buzzer_codes

    def fetch_codes(self, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetch data of `buzzer codes`_.

        .. _`buzzer codes`: http://www.railwaycodes.org.uk/misc/buzzer.shtm

        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the data of buzzer codes and
            the date they were last updated
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Buzzer  # from pyrcs import Buzzer

            >>> buz = Buzzer()

            >>> buz_codes = buz.fetch_codes()

            >>> type(buz_codes)
            dict
            >>> list(buz_codes.keys())
            ['Buzzer codes', 'Last updated date']

            >>> buz.KEY
            'Buzzer codes'

            >>> buz_codes_dat = buz_codes[buz.KEY]

            >>> type(buz_codes_dat)
            pandas.DataFrame
            >>> buz_codes_dat.head()
              Code (number of buzzes or groups separate...                                 Meaning
            0                                            1                                    Stop
            1                                          1-2                             Close doors
            2                                            2                          Ready to start
            3                                          2-2     Create vacuum [used in early 1960s]
            4                                          2-2                       Do not open doors
        """

        args = {
            'data_name': self.KEY,
            'method': self.collect_codes,
            'data_dir': self._cdd("..", "features"),
        }

        buzzer_codes = self._fetch_data_from_file(
            update=update, dump_dir=dump_dir, verbose=verbose, **(args | kwargs)
        )

        return buzzer_codes
