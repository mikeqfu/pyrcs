"""
Collect data of `signal box prefix codes <http://www.railwaycodes.org.uk/signal/signal_boxes0.shtm>`_.
"""

import collections
import re
import string
import urllib.parse

import bs4
import pandas as pd

from .._base import _Base
from ..parser import _get_last_updated_date, parse_tr
from ..utils import get_collect_verbosity_for_fetch, handle_connection_error, homepage_url, \
    is_homepage_connectable, print_void_collection_message, validate_initial


def _get_h3_table_data(h3):
    """
    Extract and parse HTML table data immediately following an ``h3`` tag.

    This method checks whether the next table element belongs directly to the
    provided ``h3`` tag and parses its header and row content into a DataFrame.

    :param h3: The HTML header tag preceding the target table.
    :type h3: bs4.element.Tag
    :return: Parsed table data as a DataFrame, or ``None`` if no associated table exists.
    :rtype: pandas.DataFrame | None
    """

    if not h3:
        return None

    tbl_dat = h3.find_next('table')

    if tbl_dat and tbl_dat.find_previous('h3') == h3:
        ths = [th.get_text(separator=' ', strip=True) for th in tbl_dat.find_all('th')]
        trs = tbl_dat.find_all('tr')

        return parse_tr(trs=trs, ths=ths, as_dataframe=True)

    return None


def _parse_tbl_dat(h3_or_h4, ths):
    """
    Parse HTML table rows following a header element into a DataFrame.

    This method traverses subsequent table rows starting from a given header element
    until a row containing a ``colspan`` attribute is encountered or no further rows exist.

    :param h3_or_h4: Header tag preceding target table rows.
    :type h3_or_h4: bs4.element.Tag
    :param ths: List of table header column names.
    :type ths: list[str]
    :return: Parsed table data as a DataFrame.
    :rtype: pandas.DataFrame
    """

    trs = []
    tr = h3_or_h4.find_next('tr')
    while tr:
        td = tr.find('td')
        if td and td.has_attr('colspan'):
            break
        trs.append(tr)
        tr = tr.find_next('tr')

    tbl = parse_tr(trs=trs, ths=ths, as_dataframe=True)

    return tbl


class SignalBoxes(_Base):
    """
    A class for collecting data of
    `signal box prefix codes <http://www.railwaycodes.org.uk/signal/signal_boxes0.shtm>`_.
    """

    #: The name of the data.
    NAME: str = 'Signal box prefix codes'

    #: The key for accessing the data.
    KEY: str = 'Signal boxes'

    #: The key for accessing *non-national rail* data.
    KEY_TO_NON_NATIONAL_RAIL: str = 'Non-National Rail'

    #: The key for accessing *Ireland* data.
    KEY_TO_IRELAND: str = 'Ireland'

    #: The key for accessing *WR (Western region) MAS (multiple aspect signalling) dates*.
    KEY_TO_WRMASD: str = 'WR MAS dates'

    #: The key for accessing *bell codes*.
    KEY_TO_BELL_CODES: str = 'Bell codes'

    #: The URL of the main web page for the data.
    URL: str = urllib.parse.urljoin(homepage_url(), '/signal/signal_boxes0.shtm')

    #: The key used to reference the last updated date in the data.
    KEY_TO_LAST_UPDATED_DATE: str = 'Last updated date'

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

            >>> from pyrcs.other_assets import SignalBoxes  # from pyrcs import SignalBoxes

            >>> sb = SignalBoxes()

            >>> sb.NAME
            'Signal box prefix codes'

            >>> sb.URL
            'http://www.railwaycodes.org.uk/signal/signal_boxes0.shtm'
        """

        super().__init__(
            data_dir=data_dir,
            content_type='catalogue',
            data_category="other-assets",
            update=update,
            verbose=verbose
        )

    def _collect_prefix_codes(self, initial, source, verbose=False):
        # noinspection shadowing-names
        """
        Parse and collect signal box prefix codes from the provided web source.

        This method processes the HTML content for a specific initial letter, extracts the
        data table of signal boxes, parses any combined ``ELR Mileage`` column into separate
        ``ELR`` and ``Mileage`` columns and retrieves the last updated date. It also saves
        the parsed data to a local file.

        :param initial: The initial letter of signal box names.
        :type initial: str
        :param source: The HTTP response object containing webpage content.
        :type source: requests.Response | Any
        :param verbose: Whether to print progress to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the signal box data table and last updated date.
        :rtype: dict
        :raises ValueError: If required table elements are missing from the source content.

        **Examples**::

            >>> from pyrcs.other_assets import SignalBoxes  # from pyrcs import SignalBoxes
            >>> from pyhelpers.ops import fake_requests_headers
            >>> import requests

            >>> sb = SignalBoxes()

            >>> initial = 'a'
            >>> url = 'http://www.railwaycodes.org.uk/signal/signal_boxesa.shtm'
            >>> source = requests.get(url, headers=fake_requests_headers())
            >>> verbose = True
            >>> sb._collect_prefix_codes(initial, source, verbose)
        """

        valid_initial = validate_initial(initial=initial)

        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')
        thead = soup.find('thead')
        tbody = soup.find('tbody')

        if not thead or not tbody:
            raise ValueError(
                f"Table structure missing in the source for initial '{valid_initial}'."
            )

        ths = [th.get_text(separator=' ', strip=True) for th in thead.find_all('th')]
        trs = tbody.find_all('tr')

        table_data: pd.DataFrame = parse_tr(trs=trs, ths=ths, as_dataframe=True)

        col_name = next(
            (col for col in table_data.columns if re.search(r'ELR ?Mileage', col)), None
        )
        if col_name:
            pattern = r'^\s*(.*?)\s*(?:/\s*\[(.*?)\])?$'
            extracted = table_data[col_name].str.extract(pattern)

            col_idx = table_data.columns.get_loc(col_name)
            table_data = table_data.drop(columns=[col_name])

            table_data.insert(col_idx, 'Mileage', extracted[1])
            table_data.insert(col_idx, 'ELR', extracted[0])

        last_updated_date = _get_last_updated_date(soup)

        prefix_codes = {
            valid_initial: table_data,
            self.KEY_TO_LAST_UPDATED_DATE: last_updated_date
        }

        if verbose in {True, 1}:
            print("Done.")

        self._save_data_to_file(
            data=prefix_codes,
            data_name=valid_initial,
            sub_dir="a-z",
            verbose=verbose
        )

        return prefix_codes

    def collect_prefix_codes(self, initial, confirmation_required=True, verbose=False,
                             raise_error=False):
        """
        Collects `signal box prefix codes`_ for a given initial letter from the source web page.

        .. _`signal box prefix codes`: http://www.railwaycodes.org.uk/signal/signal_boxes0.shtm

        :param initial: The initial letter (e.g. ``'a'``, ``'z'``) of signal box prefix code.
        :type initial: str
        :param confirmation_required: Whether user confirmation is required;
            if ``confirmation_required=True`` (default), prompts the user for confirmation
            before proceeding with data collection.
        :type confirmation_required: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :param raise_error: Whether to raise the provided exception;
            if ``raise_error=False`` (default), the error will be suppressed.
        :type raise_error: bool
        :return: A dictionary containing data of signal box prefix codes whose initial letters are
            the specified ``initial`` and the date of when the data was last updated.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import SignalBoxes  # from pyrcs import SignalBoxes

            >>> sb = SignalBoxes()

            >>> sb_a_codes = sb.collect_prefix_codes(initial='a', verbose=True)
            Proceed with collecting data of "signal box prefix codes" beginning with "A"?
             [No]|Yes: yes
            Collecting the data ... Done.

            >>> type(sb_a_codes)
            dict
            >>> list(sb_a_codes)
            ['A', 'Last updated date']

            >>> sb_a_codes_dat = sb_a_codes['A']
            >>> type(sb_a_codes_dat)
            pandas.DataFrame

            >>> sb_a_codes_dat.shape
            (225, 8)
            >>> sb_a_codes_dat.head()
              Code               Signal Box  ...            Closed        Control to
            0   AF  Abbey Foregate Junction  ...
            1   AJ           Abbey Junction  ...  16 February 1992     Nuneaton (NN)
            2    R           Abbey Junction  ...  16 February 1992     Nuneaton (NN)
            3   AW               Abbey Wood  ...      13 July 1975      Dartford (D)
            4   AE         Abbey Works East  ...   1 November 1987  Port Talbot (PT)
            [5 rows x 8 columns]
        """

        initial_ = validate_initial(initial=initial)

        signal_box_prefix_codes = self._collect_data_from_source(
            data_name=self.NAME.lower(),
            method=self._collect_prefix_codes,
            initial=initial_,
            confirmation_required=confirmation_required,
            verbose=verbose,
            raise_error=raise_error
        )

        return signal_box_prefix_codes

    def fetch_prefix_codes(self, initial=None, update=False, dump_dir=None, verbose=False,
                           **kwargs):
        # noinspection shadowing-names,unresolved-references
        """
        Fetches data of `signal box prefix codes`_.

        .. _`signal box prefix codes`: http://www.railwaycodes.org.uk/signal/signal_boxes0.shtm

        :param initial: The initial letter (e.g. ``'a'``, ``'z'``) of signal box prefix code;
            defaults to ``None``.
        :type initial: str
        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the data of signal box prefix codes and
            the date whey they were last updated.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import SignalBoxes  # from pyrcs import SignalBoxes

            >>> sb = SignalBoxes()

            >>> signal_box_prefix_codes = sb.fetch_prefix_codes()

            >>> type(signal_box_prefix_codes, dict)
            >>> list(signal_box_prefix_codes)
            ['Signal boxes', 'Last updated date']

            >>> prefix_codes_df = signal_box_prefix_codes.get('Signal boxes')
            >>> prefix_codes_df.shape
            (5542, 8)
            >>> prefix_codes.head()
              Code               Signal Box  ...            Closed        Control to
            0   AF  Abbey Foregate Junction  ...
            1   AJ           Abbey Junction  ...  16 February 1992     Nuneaton (NN)
            2    R           Abbey Junction  ...  16 February 1992     Nuneaton (NN)
            3   AW               Abbey Wood  ...      13 July 1975      Dartford (D)
            4   AE         Abbey Works East  ...   1 November 1987  Port Talbot (PT)
            [5 rows x 8 columns]
        """

        if initial:
            args = {
                'data_name': validate_initial(initial),
                'method': self.collect_prefix_codes,
                'sub_dir': "a-z",
                'initial': initial,
            }
            kwargs.update(args)

            signal_box_prefix_codes = self._fetch_data_from_file(
                update=update, dump_dir=dump_dir, verbose=verbose, **kwargs)

        else:

            verbose_1 = get_collect_verbosity_for_fetch(data_dir=dump_dir, verbose=verbose)
            verbose_2 = verbose_1 if is_homepage_connectable() else False

            # Get every data table
            data = [
                self.fetch_prefix_codes(initial=x, update=update, verbose=verbose_2)
                for x in string.ascii_lowercase
            ]

            if all(d[x] is None for d, x in zip(data, string.ascii_uppercase)):
                if update:
                    handle_connection_error(verbose=verbose)
                    print_void_collection_message(data_name=self.KEY.lower(), verbose=verbose)

                data = [
                    self.fetch_prefix_codes(initial=x, update=False, verbose=verbose_1)
                    for x in string.ascii_lowercase
                ]

            # Select DataFrames only
            signal_boxes_codes_ = [
                item[x] for item, x in zip(data, string.ascii_uppercase)
            ]
            signal_boxes_codes = pd.concat(signal_boxes_codes_, ignore_index=True)

            # Get the latest updated date
            last_updated_dates = (item[self.KEY_TO_LAST_UPDATED_DATE] for item in data)
            latest_update_date = max(d for d in last_updated_dates if d is not None)

            # Create a dict to include all information
            signal_box_prefix_codes = {
                self.KEY: signal_boxes_codes,
                self.KEY_TO_LAST_UPDATED_DATE: latest_update_date
            }

        if dump_dir:
            self._save_data_to_file(
                data=signal_box_prefix_codes,
                data_name=self.KEY,
                dump_dir=dump_dir,
                verbose=verbose
            )

        return signal_box_prefix_codes

    def _collect_non_national_rail_codes(self, source, verbose=False):
        # noinspection shadowing-names
        """
        Parse and collect non-national rail signal box codes from source content.

        This method processes the HTML source, extracts section headings for non-national rail
        systems, retrieves associated descriptive notes and parses corresponding data tables into
        DataFrames before saving the result locally.

        :param source: The HTTP response object containing webpage content.
        :type source: requests.Response | Any
        :param verbose: Whether to print progress to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing non-national rail codes and last updated date.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import SignalBoxes
            >>> from pyhelpers.ops import fake_requests_headers
            >>> import requests
            >>> sb = SignalBoxes()
            >>> url = 'http://www.railwaycodes.org.uk/signal/signal_boxesX.shtm'
            >>> source = requests.get(url, headers=fake_requests_headers())
            >>> verbose = True
            >>> nnr_codes = sb._collect_non_national_rail_codes(source, verbose)
        """

        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

        non_national_rail_codes = {}

        for h3 in soup.find_all('h3'):
            # Get the name of the non-national rail
            non_national_rail_name = h3.get_text(strip=True)

            # Find text descriptions
            desc_text_list = []
            curr_p = h3.find_next('p')
            while curr_p and curr_p.find_previous('h3') == h3:
                p_text = curr_p.get_text().replace('\xa0', ' ').strip()
                if p_text:
                    desc_text_list.append(p_text)
                curr_p = curr_p.find_next('p')

            desc_text = '\n'.join(desc_text_list)

            # Get table data
            data = _get_h3_table_data(h3)

            # Update data dict
            non_national_rail_codes[non_national_rail_name] = {
                'Codes': data,
                'Notes': desc_text,
            }

        non_national_rail_codes_data = {
            self.KEY_TO_NON_NATIONAL_RAIL: non_national_rail_codes,
            self.KEY_TO_LAST_UPDATED_DATE: _get_last_updated_date(soup),
        }

        if verbose in {True, 1}:
            print("Done.")

        self._save_data_to_file(
            data=non_national_rail_codes_data,
            data_name=self.KEY_TO_NON_NATIONAL_RAIL,
            verbose=verbose
        )

        return non_national_rail_codes_data

    def collect_non_national_rail_codes(self, confirmation_required=True, verbose=False,
                                        raise_error=False):
        """
        Collects signal box prefix codes for `non-national rail
        <http://www.railwaycodes.org.uk/signal/signal_boxesX.shtm>`_ from the source web page.

        This method retrieves the target URL from the catalogue, prompts for user confirmation
        if required and delegates data parsing to ``_collect_non_national_rail_codes``.

        :param confirmation_required: Whether user confirmation is required before proceeding;
            defaults to ``True``.
        :type confirmation_required: bool
        :param verbose: Whether to print progress to the console; defaults to ``False``.
        :type verbose: bool | int
        :param raise_error: Whether to raise an exception if data collection fails;
            defaults to ``False``.
        :type raise_error: bool
        :return: A dictionary containing non-national rail signal box prefix codes and last updated
            date, or ``None`` if collection fails.
        :rtype: dict | None
        :raises ValueError: If the catalogue is unavailable or missing the target URL when
            ``raise_error`` is ``True``.

        **Examples**::

            >>> from pyrcs.other_assets import SignalBoxes  # from pyrcs import SignalBoxes

            >>> sb = SignalBoxes()

            >>> nnr_codes: dict = sb.collect_non_national_rail_codes(verbose=True)
            Proceed with collecting data of "non-national rail signal box prefix codes"?
             [No]|Yes: yes
            Collecting the data ... Done.

            >>> list(nnr_codes)
            ['Non-National Rail', 'Last updated date']

            >>> nnr_codes_dat = nnr_codes['Non-National Rail']
            >>> type(nnr_codes_dat)
            dict
            >>> list(nnr_codes_dat)
            ['Croydon Tramlink signals',
             'Docklands Light Railway signals',
             'Edinburgh Tramway signals',
             'Glasgow Subway signals',
             'London Underground signals',
             'Luas signals',
             'Manchester Metrolink signals',
             'Midland Metro signals',
             'Nottingham Tram signals',
             'Sheffield Supertram signals',
             'Tyne & Wear Metro signals',
             "Heritage, minor and miniature railways and other 'special' signals"]

            >>> lu_signals_codes = nnr_codes_dat['London Underground signals']
            >>> type(lu_signals_codes)
            dict
            >>> list(lu_signals_codes)
            ['Codes', 'Notes']

            >>> lu_signals_codes_df = lu_signals_codes['Codes']
            >>> lu_signals_codes_df.shape
            (485, 5)
            >>> lu_signals_codes_df.head()
              Code  ... Became or taken over by (where known)
            0  BMX  ...                                     -
            1    A  ...                                     -
            2    S  ...                                     -
            3    X  ...                                     -
            4    R  ...                                     -
            [5 rows x 5 columns]
        """

        url = self._get_url(key=self.KEY_TO_NON_NATIONAL_RAIL, raise_error=raise_error)

        data_name = f"{self.KEY_TO_NON_NATIONAL_RAIL.lower()} signal box prefix codes"

        non_national_rail_codes_data = self._collect_data_from_source(
            data_name=data_name,
            method=self._collect_non_national_rail_codes,
            url=url,
            confirmation_required=confirmation_required,
            verbose=verbose,
            raise_error=raise_error
        )

        return non_national_rail_codes_data

    def fetch_non_national_rail_codes(self, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetches signal box prefix codes for `non-national rail`_.

        .. _`non-national rail`: http://www.railwaycodes.org.uk/signal/signal_boxesX.shtm

        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the signal box prefix codes for non-national rail and
            the date when they were last updated.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import SignalBoxes  # from pyrcs import SignalBoxes

            >>> sb = SignalBoxes()

            >>> nnr_codes = sb.fetch_non_national_rail_codes()
            >>> type(nnr_codes)
            dict
            >>> list(nnr_codes)
            ['Non-National Rail', 'Last updated date']

            >>> nnr_codes_dat = nnr_codes['Non-National Rail']
            >>> type(nnr_codes_dat)
            dict
            >>> list(nnr_codes_dat)
            ['Croydon Tramlink signals',
             'Docklands Light Railway signals',
             'Edinburgh Tramway signals',
             'Glasgow Subway signals',
             'London Underground signals',
             'Luas signals',
             'Manchester Metrolink signals',
             'Midland Metro signals',
             'Nottingham Tram signals',
             'Sheffield Supertram signals',
             'Tyne & Wear Metro signals',
             "Heritage, minor and miniature railways and other 'special' signals"]

            >>> lu_signals_codes = nnr_codes_dat['London Underground signals']
            >>> type(lu_signals_codes)
            dict
            >>> list(lu_signals_codes)
            ['Codes', 'Notes']

            >>> lu_signals_codes_df = lu_signals_codes['Codes']
            >>> lu_signals_codes_df.shape
            (485, 5)
            >>> lu_signals_codes_df.head()
              Code  ... Became or taken over by (where known)
            0  BMX  ...                                     -
            1    A  ...                                     -
            2    S  ...                                     -
            3    X  ...                                     -
            4    R  ...                                     -
            [5 rows x 5 columns]
        """

        args = {
            'data_name': self.KEY_TO_NON_NATIONAL_RAIL,
            'method': self.collect_non_national_rail_codes,
        }
        kwargs.update(args)

        non_national_rail_codes_data = self._fetch_data_from_file(
            update=update, dump_dir=dump_dir, verbose=verbose, **kwargs)

        return non_national_rail_codes_data

    def _collect_ireland_codes(self, source, verbose=False):
        # noinspection shadowing-names
        """
        Parse and collect signal box codes for Ireland from source content.

        This method processes the HTML content, extracts the data table for Irish signal
        boxes, parses associated explanatory notes and retrieves the last updated date
        before saving the data locally.

        :param source: The HTTP response object containing webpage content.
        :type source: requests.Response | typing.Any
        :param verbose: Whether to print progress to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing Irish signal box codes, notes and last updated date.
        :rtype: dict
        :raises ValueError: If required table elements are missing from the source content.

        **Examples**::

            >>> from pyrcs.other_assets import SignalBoxes
            >>> from pyhelpers.ops import fake_requests_headers
            >>> import requests

            >>> sb = SignalBoxes()

            >>> url = 'http://www.railwaycodes.org.uk/signal/signal_boxes1.shtm'
            >>> source = requests.get(url, headers=fake_requests_headers())
            >>> verbose = True
            >>> ireland_codes = sb._collect_ireland_codes(source, verbose)
        """

        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

        thead = soup.find('thead')
        tbody = soup.find('tbody')

        if not thead or not tbody:
            raise ValueError("Table structure missing in source content for Ireland codes.")

        ths = [th.get_text(separator=' ', strip=True) for th in thead.find_all('th')]
        trs = tbody.find_all('tr')
        ireland_codes = parse_tr(trs=trs, ths=ths, as_dataframe=True)

        h4_tag = soup.find('h4')
        ol_tag = h4_tag.find_next('ol') if h4_tag else None
        notes = [li.get_text(strip=True) for li in ol_tag.find_all('li')] if ol_tag else []

        last_updated_date = _get_last_updated_date(soup)

        ireland_codes_data = {
            self.KEY_TO_IRELAND: ireland_codes,
            'Notes': notes,
            self.KEY_TO_LAST_UPDATED_DATE: last_updated_date,
        }

        if verbose in {True, 1}:
            print("Done.")

        self._save_data_to_file(
            data=ireland_codes_data,
            data_name=self.KEY_TO_IRELAND,
            verbose=verbose
        )

        return ireland_codes_data

    def collect_ireland_codes(self, confirmation_required=True, verbose=False, raise_error=False):
        # noinspection unresolved-references
        """
        Collects data of `Irish signal cabin prefix codes
        <http://www.railwaycodes.org.uk/signal/signal_boxes1.shtm>`_ from the source web page.

        :param confirmation_required: Whether user confirmation is required;
            if ``confirmation_required=True`` (default), prompts the user for confirmation
            before proceeding with data collection.
        :type confirmation_required: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :param raise_error: Whether to raise the provided exception;
            if ``raise_error=False`` (default), the error will be suppressed.
        :type raise_error: bool
        :return: A dictionary containing the data of Irish signal cabin prefix codes and
            the date when they were last updated, or ``None`` if no data is collectd.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.other_assets import SignalBoxes  # from pyrcs import SignalBoxes

            >>> sb = SignalBoxes()

            >>> ireland_sb_codes = sb.collect_ireland_codes(verbose=True)
            Proceed with collecting data of "signal box prefix codes of Ireland"?
             [No]|Yes: yes
            Collecting the data ... Done.

            >>> type(ireland_sb_codes)
            dict
            >>> list(ireland_sb_codes)
            ['Ireland', 'Notes', 'Last updated date']

            >>> ireland_sb_codes_df = ireland_sb_codes['Ireland']
            >>> ireland_sb_codes_df.shape
            (154, 3)
            >>> ireland_sb_codes_df.head()
               Code Signal Cabin                    Note
            0    AD     Adelaide
            1    AN       Antrim
            2    AE      Athlone
            3  AE R                      Distant signals
            4    XG               Level crossing signals
        """

        url = self._get_url(key=self.KEY_TO_IRELAND, raise_error=raise_error)

        data_name = f"signal box prefix codes of {self.KEY_TO_IRELAND}"

        ireland_codes_data = self._collect_data_from_source(
            data_name=data_name,
            method=self._collect_ireland_codes,
            url=url,
            additional_fields='Notes',
            confirmation_required=confirmation_required,
            verbose=verbose,
            raise_error=raise_error
        )

        return ireland_codes_data

    def fetch_ireland_codes(self, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetches data of `Irish signal cabin prefix codes`_.

        .. _`Irish signal cabin prefix codes`:
            http://www.railwaycodes.org.uk/signal/signal_boxes1.shtm

        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the data of Irish signal cabin prefix codes and
            the date when they were last updated.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import SignalBoxes  # from pyrcs import SignalBoxes

            >>> sb = SignalBoxes()

            >>> ireland_sb_codes = sb.fetch_ireland_codes()

            >>> type(ireland_sb_codes)
            dict
            >>> list(ireland_sb_codes)
            ['Ireland', 'Notes', 'Last updated date']

            >>> ireland_sb_codes_df = ireland_sb_codes['Ireland']
            >>> ireland_sb_codes_df.shape

            >>> ireland_sb_codes_df.head()
               Code Signal Cabin                    Note
            0    AD     Adelaide
            1    AN       Antrim
            2    AE      Athlone
            3  AE R                      Distant signals
            4    XG               Level crossing signals
        """

        kwargs.setdefault('data_name', self.KEY_TO_IRELAND)
        kwargs.setdefault('method', self.collect_ireland_codes)

        ireland_codes_data = self._fetch_data_from_file(
            update=update,
            dump_dir=dump_dir,
            verbose=verbose,
            **kwargs
        )

        return ireland_codes_data

    def _collect_wr_mas_dates(self, source, verbose=False):
        # noinspection shadowing-names
        """
        Parse and collect Western Region MAS dates from source content.

        This method processes HTML content, extracts tables under section headers and
        subheadings for Western Region Multiple Aspect Signalling dates, retrieves last
        updated date and saves data locally.

        :param source: HTTP response object containing webpage content.
        :type source: requests.Response | Any
        :param verbose: Whether to print progress to console; defaults to ``False``.
        :type verbose: bool | int
        :return: Dictionary containing Western Region MAS dates and last updated date.
        :rtype: dict
        :raises ValueError: If required table header structure is missing from source content.

        **Examples**::

            >>> from pyrcs.other_assets import SignalBoxes
            >>> from pyhelpers.ops import fake_requests_headers
            >>> import requests

            >>> sb = SignalBoxes()

            >>> url = 'http://www.railwaycodes.org.uk/signal/dates.shtm'
            >>> source = requests.get(url, headers=fake_requests_headers())
            >>> verbose = True
            >>> wr_mas_data = sb._collect_wr_mas_dates(source, verbose)
        """

        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

        thead = soup.find('thead')
        if not thead:
            raise ValueError(
                "Table header structure missing in source content for Western Region MAS dates."
            )

        ths = [th.get_text(separator=' ', strip=True) for th in thead.find_all('th')]

        wr_mas_dates = collections.defaultdict(dict)

        for h3 in soup.find_all('h3'):
            h3_text = h3.get_text(strip=True)

            h4 = h3.find_next('h4')
            h4_found = False

            while h4 and h4.find_previous('h3') == h3:
                h4_text = h4.get_text(strip=True)
                wr_mas_dates[h3_text][h4_text] = _parse_tbl_dat(h4, ths)
                h4_found = True
                h4 = h4.find_next('h4')

            if not h4_found:
                wr_mas_dates[h3_text] = _parse_tbl_dat(h3, ths)

        last_updated_date = _get_last_updated_date(soup)

        wr_mas_dates_data = {
            self.KEY_TO_WRMASD: dict(wr_mas_dates),
            self.KEY_TO_LAST_UPDATED_DATE: last_updated_date,
        }

        if verbose in {True, 1}:
            print("Done.")

        self._save_data_to_file(
            data=wr_mas_dates_data,
            data_name=self.KEY_TO_WRMASD,
            verbose=verbose
        )

        return wr_mas_dates_data

    def collect_wr_mas_dates(self, confirmation_required=True, verbose=False, raise_error=False):
        """
        Collects data of `WR (western region) MAS (multiple aspect signalling) dates
        <http://www.railwaycodes.org.uk/signal/dates.shtm>`_
        from the source web page.

        :param confirmation_required: Whether user confirmation is required;
            if ``confirmation_required=True`` (default), prompts the user for confirmation
            before proceeding with data collection.
        :type confirmation_required: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :param raise_error: Whether to raise the provided exception;
            if ``raise_error=False`` (default), the error will be suppressed.
        :type raise_error: bool
        :return: A dictionary containing the data of WR MAS dates and
            the date when they were last updated, or ``None`` if no data is collected.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.other_assets import SignalBoxes  # from pyrcs import SignalBoxes

            >>> sb = SignalBoxes()

            >>> sb_wr_mas_dates: dict = sb.collect_wr_mas_dates(verbose=True)
            Proceed with collecting data of "WR MAS dates"?
             [No]|Yes: yes
            Collecting the data ... Done.

            >>> list(sb_wr_mas_dates)
            ['WR MAS dates', 'Last updated date']

            >>> sb_wr_mas_dates_dict = sb_wr_mas_dates['WR MAS dates']

            >>> list(sb_wr_mas_dates_dict)[:5]
            ['Paddington-Hayes',
             'Birmingham',
             'Plymouth',
             'Reading-Hayes',
             'Newport Multiple Aspect Signalling']

            >>> sb_wr_mas_dates_dict.get('Paddington-Hayes')
              Stage             Date                        Area
            0    1A    12 April 1953               Hayes-Hanwell
            1    1B    20 March 1955        Hanwell-Acton Middle
            2    1C  1 February 1959  Acton West-Friars Junction
        """

        return self._collect_data_from_source(
            data_name=self.KEY_TO_WRMASD,
            method=self._collect_wr_mas_dates,
            confirmation_required=confirmation_required,
            verbose=verbose,
            raise_error=raise_error
        )

    def fetch_wr_mas_dates(self, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetches data of `WR (western region) MAS (multiple aspect signalling) dates`_.

        .. _`WR (western region) MAS (multiple aspect signalling) dates`:
            http://www.railwaycodes.org.uk/signal/dates.shtm

        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the data of WR MAS dates and
            the date when they were last updated.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.other_assets import SignalBoxes  # from pyrcs import SignalBoxes

            >>> sb = SignalBoxes()

            >>> sb_wr_mas_dates: dict = sb.fetch_wr_mas_dates()

            >>> type(sb_wr_mas_dates)
            dict
            >>> list(sb_wr_mas_dates)
            ['WR MAS dates', 'Last updated date']

            >>> sb_wr_mas_dates_dict = sb_wr_mas_dates['WR MAS dates']

            >>> list(sb_wr_mas_dates_dict)[:5]
            ['Paddington-Hayes',
             'Birmingham',
             'Plymouth',
             'Reading-Hayes',
             'Newport Multiple Aspect Signalling']

            >>> sb_wr_mas_dates_dict.get('Paddington-Hayes')
              Stage             Date                        Area
            0    1A    12 April 1953               Hayes-Hanwell
            1    1B    20 March 1955        Hanwell-Acton Middle
            2    1C  1 February 1959  Acton West-Friars Junction
        """

        kwargs.setdefault('data_name', self.KEY_TO_WRMASD)
        kwargs.setdefault('method', self.collect_wr_mas_dates)

        wr_mas_dates_data = self._fetch_data_from_file(
            update=update,
            dump_dir=dump_dir,
            verbose=verbose,
            **kwargs
        )

        return wr_mas_dates_data

    def _collect_bell_codes(self, source, verbose=False):
        # noinspection shadowing-names
        """
        Parse and collect bell codes from the provided web source.

        This method processes the HTML content, iterates through section headings, extracts
        the corresponding table of bell codes and associated descriptive notes, and retrieves
        the last updated date before saving the output locally.

        :param source: The HTTP response object containing webpage content.
        :type source: requests.Response | Any
        :param verbose: Whether to print progress to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the bell codes and last updated date.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import SignalBoxes
            >>> from pyhelpers.ops import fake_requests_headers
            >>> import requests

            >>> sb = SignalBoxes()

            >>> url = 'http://www.railwaycodes.org.uk/signal/bellcodes.shtm'
            >>> source = requests.get(url, headers=fake_requests_headers())
            >>> verbose = True
            >>> bell_codes = sb._collect_bell_codes(source, verbose)
        """

        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

        bell_codes_data = {}

        for h3 in soup.find_all('h3'):
            section_name = h3.get_text(strip=True)

            codes_table = _get_h3_table_data(h3)

            p_tag = h3.find_next('p')
            notes = p_tag.get_text(strip=True) if p_tag and p_tag.find_previous('h3') == h3 else ''

            bell_codes_data[section_name] = {
                'Codes': codes_table,
                'Notes': notes,
            }

        last_updated_date = _get_last_updated_date(soup)

        bell_codes = {
            self.KEY_TO_BELL_CODES: bell_codes_data,
            self.KEY_TO_LAST_UPDATED_DATE: last_updated_date,
        }

        if verbose in {True, 1}:
            print("Done.")

        self._save_data_to_file(data=bell_codes, data_name=self.KEY_TO_BELL_CODES, verbose=verbose)

        return bell_codes

    def collect_bell_codes(self, confirmation_required=True, verbose=False, raise_error=False):
        # noinspection unresolved-references
        """
        Collects data of `bell codes <http://www.railwaycodes.org.uk/signal/bellcodes.shtm>`_
        from the source web page.

        :param confirmation_required: Whether user confirmation is required;
            if ``confirmation_required=True`` (default), prompts the user for confirmation
            before proceeding with data collection.
        :type confirmation_required: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :param raise_error: Whether to raise the provided exception;
            if ``raise_error=False`` (default), the error will be suppressed.
        :type raise_error: bool
        :return: A dictionary containing the data of bell codes and
            the date when they were last updated, or ``None`` if no data is collected.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.other_assets import SignalBoxes  # from pyrcs import SignalBoxes

            >>> sb = SignalBoxes()

            >>> sb_bell_codes: dict = sb.collect_bell_codes(verbose=True)
            Proceed with collecting data of "Bell codes"?
             [No]|Yes: yes
            Collecting the data ... Done.

            >>> list(sb_bell_codes)
            ['Bell codes', 'Last updated date']

            >>> sb_bell_codes_dict: dict = sb_bell_codes.get('Bell codes')

            >>> list(sb_bell_codes_dict)
            ['Network Rail codes',
             'Southern Railway codes',
             'Lancashire & Yorkshire Railway codes']

            >>> sb_nr_bell_codes: dict = sb_bell_codes_dict.get('Network Rail codes')

            >>> list(sb_nr_bell_codes)
            ['Codes', 'Notes']

            >>> sb_nr_bell_codes_df = sb_nr_bell_codes.get('Codes')

            >>> sb_nr_bell_codes_df.shape
            (69, 2)
            >>> sb_nr_bell_codes_df.head()
                Code                                       Meaning
            0      1                                Call attention
            1    1-1             Answer telephone [withdrawn 2007]
            2  1-1-6           Police assistance urgently required
            3    1-2  Signaller required on telephone [added 2007]
            4  1-2-1                             Train approaching
        """

        return self._collect_data_from_source(
            data_name=self.KEY_TO_BELL_CODES,
            method=self._collect_bell_codes,
            confirmation_required=confirmation_required,
            verbose=verbose,
            raise_error=raise_error
        )

    def fetch_bell_codes(self, update=False, dump_dir=None, verbose=False, **kwargs):
        # noinspection unresolved-references
        """
        Fetches data of `bell codes`_.

        .. _`bell codes`: http://www.railwaycodes.org.uk/signal/bellcodes.shtm

        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the data of bell codes and
            the date when they were last updated.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import SignalBoxes  # from pyrcs import SignalBoxes

            >>> sb = SignalBoxes()

            >>> sb_bell_codes = sb.fetch_bell_codes()

            >>> list(sb_bell_codes)
            ['Bell codes', 'Last updated date']

            >>> sb_bell_codes_dict: dict = sb_bell_codes.get('Bell codes')

            >>> list(sb_bell_codes_dict)
            ['Network Rail codes',
             'Southern Railway codes',
             'Lancashire & Yorkshire Railway codes']

            >>> sb_nr_bell_codes: dict = sb_bell_codes_dict.get('Network Rail codes')

            >>> list(sb_nr_bell_codes)
            ['Codes', 'Notes']

            >>> sb_nr_bell_codes_df = sb_nr_bell_codes.get('Codes')

            >>> sb_nr_bell_codes_df.shape
            (69, 2)
            >>> sb_nr_bell_codes_df.head()
                Code                                       Meaning
            0      1                                Call attention
            1    1-1             Answer telephone [withdrawn 2007]
            2  1-1-6           Police assistance urgently required
            3    1-2  Signaller required on telephone [added 2007]
            4  1-2-1                             Train approaching
        """

        kwargs.setdefault('data_name', self.KEY_TO_BELL_CODES)
        kwargs.setdefault('method', self.collect_bell_codes)

        return self._fetch_data_from_file(
            update=update,
            dump_dir=dump_dir,
            verbose=verbose,
            **kwargs
        )
