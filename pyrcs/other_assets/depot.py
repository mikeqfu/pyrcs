"""
Collect data of `depot codes <http://www.railwaycodes.org.uk/depots/depots0.shtm>`_.
"""

import itertools
import re
import urllib.parse

import bs4
import pandas as pd

from .._base import _Base
from ..parser import _get_last_updated_date, _parse_th_tag, parse_tr
from ..utils import get_batch_fetch_verbosity, homepage_url


class Depots(_Base):
    """
    A class for collecting data of
    `depot codes <http://www.railwaycodes.org.uk/depots/depots0.shtm>`_.
    """

    #: The name of the data.
    NAME: str = 'Depot codes'
    #: The key for accessing the data.
    KEY: str = 'Depots'

    #: The key for accessing the data of two character TOPS codes
    KEY_TO_TOPS: str = 'Two character TOPS'
    #: The key for accessing the data of four digit pre-TOPS codes
    KEY_TO_PRE_TOPS: str = 'Four digit pre-TOPS'
    #: The key for accessing the data of 1950 system (pre-TOPS) codes
    KEY_TO_1950_SYSTEM: str = '1950 system (pre-TOPS)'
    #: The key for accessing the data of GWR codes
    KEY_TO_GWR: str = 'GWR'

    #: The URL of the main web page for the data.
    URL: str = urllib.parse.urljoin(homepage_url(), '/depots/depots0.shtm')

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

            >>> from pyrcs.other_assets import Depots  # from pyrcs import Depots
            >>> depots = Depots()
            >>> depots.NAME
            'Depot codes'
            >>> depots.URL
            'http://www.railwaycodes.org.uk/depots/depots0.shtm'
        """

        super().__init__(
            data_dir=data_dir,
            content_type='catalogue',
            data_category="other-assets",
            update=update,
            verbose=verbose
        )

    def _collect_tops_codes(self, source, verbose=False):
        """
        Parse and save two-character TOPS depot codes from an HTML source.

        Extracts the HTML table containing Total Operations Processing System (TOPS) depot codes,
        packages the DataFrame alongside the last updated date and saves the result to file.

        :param source: HTML response object containing the TOPS depot code table.
        :type source: requests.Response | bs4.BeautifulSoup
        :param verbose: Level of logging detail where ``True`` or ``1`` enables progress messages.
            Defaults to ``False``.
        :type verbose: bool | int
        :return: Dictionary containing the parsed DataFrame and the last updated date.
        :rtype: dict[str, pandas.DataFrame | str]
        :raises ValueError: If the required table elements are missing from ``source``.
        """

        two_char_tops_codes, soup = self._parse_table_source(
            source=source, dataset_label=self.KEY_TO_TOPS
        )

        two_char_tops_codes_data = {
            self.KEY_TO_TOPS: two_char_tops_codes,
            self.KEY_TO_LAST_UPDATED_DATE: _get_last_updated_date(soup=soup)
        }

        if verbose in {True, 1}:
            print("Done.")

        self._save_data_to_file(
            data=two_char_tops_codes_data,
            data_name=self.KEY_TO_TOPS,
            verbose=verbose
        )

        return two_char_tops_codes_data

    def collect_tops_codes(self, confirmation_required=True, verbose=False, raise_error=False):
        # noinspection unresolved-references
        """
        Collect `two-character TOPS codes <http://www.railwaycodes.org.uk/depots/depots1.shtm>`_
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
        :return: A dictionary containing the two-character TOPS codes and
            the date they were last updated, or ``None`` if no data is collected.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.other_assets import Depots  # from pyrcs import Depots

            >>> depots = Depots()

            >>> tct_codes = depots.collect_tops_codes(verbose=True)
            Proceed with collecting data of "two character tops"?
             [No]|Yes: yes
            Collecting the data ... Done.

            >>> type(tct_codes)
            dict
            >>> list(tct_codes)
            ['Two character TOPS', 'Last updated date']

            >>> tct_codes_dat = tct_codes['Two character TOPS']
            >>> type(tct_codes_dat)
            pandas.DataFrame
            >>> tct_codes_dat.shape
            (591, 5)
            >>> tct_codes_dat.head()
              Code  ...                Notes
            0   AB  ...          closed 1987
            1   AB  ...
            2   AC  ...  became WH from 1994
            3   AC  ...
            4   AD  ...
            [5 rows x 5 columns]
        """

        two_char_tops_codes_data = self._collect_data_from_source(
            data_name=self.KEY_TO_TOPS.lower(),
            method=self._collect_tops_codes,
            url=self.catalogue[self.KEY_TO_TOPS],  # noqa
            confirmation_required=confirmation_required,
            verbose=verbose,
            raise_error=raise_error
        )

        return two_char_tops_codes_data

    def fetch_tops_codes(self, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetch data of `two-character TOPS codes`_.

        .. _`two-character TOPS codes`: http://www.railwaycodes.org.uk/depots/depots1.shtm

        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the data of two-character TOPS codes and
            the date they were last updated.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Depots  # from pyrcs import Depots

            >>> depots = Depots()

            >>> tct_codes = depots.fetch_tops_codes()
            >>> type(tct_codes)
            dict
            >>> list(tct_codes.keys())
            ['Two character TOPS', 'Last updated date']

            >>> depots.KEY_TO_TOPS
            'Two character TOPS codes'

            >>> tct_codes_dat = tct_codes['Two character TOPS']
            >>> type(tct_codes_dat)
            pandas.DataFrame
            >>> tct_codes_dat.shape
            (591, 5)
            >>> tct_codes_dat.head()
              Code  ...                Notes
            0   AB  ...          closed 1987
            1   AB  ...
            2   AC  ...  became WH from 1994
            3   AC  ...
            4   AD  ...
            [5 rows x 5 columns]
        """

        kwargs.update({'data_name': self.KEY_TO_TOPS, 'method': self.collect_tops_codes})

        two_char_tops_codes_data = self._fetch_data_from_file(
            update=update, dump_dir=dump_dir, verbose=verbose, **kwargs)

        return two_char_tops_codes_data

    @staticmethod
    def _identify_region(x):
        """
        Map a numeric pre-TOPS depot code to its corresponding railway region.

        Evaluates the numerical range of the code to determine the historical British Rail region
        (e.g. London Midland, Western or Southern).

        :param x: Four-digit numeric pre-TOPS depot code.
        :type x: int
        :return: Name of the identified railway region or ``'Unknown'`` if unrecognised.
        :rtype: str
        """

        if 2000 <= x < 3000:
            return 'London Midland'
        if 3000 <= x < 4000:
            return 'Western'
        if 4000 <= x < 5000:
            return 'Southern'
        if 5000 <= x < 7000:
            return 'Eastern'
        if x >= 7000:
            return 'Scottish'
        return 'Unknown'

    def _collect_pre_tops_codes(self, source, verbose=False):
        """
        Parse, classify and save four-digit pre-TOPS depot codes from an HTML source.

        Extracts pre-TOPS depot codes, assigns regional classifications, flags Main Works sites,
        cleans depot names and saves the structured dataset.

        :param source: HTML response object containing the pre-TOPS depot code table.
        :type source: requests.Response | bs4.BeautifulSoup
        :param verbose: Level of logging detail where ``True`` or ``1`` enables progress messages.
            Defaults to ``False``.
        :type verbose: bool | int
        :return: Dictionary containing the processed DataFrame and the last updated date.
        :rtype: dict[str, pandas.DataFrame | str]
        :raises ValueError: If the required table elements are missing from ``source``.
        """

        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

        thead, tbody = soup.find('thead'), soup.find('tbody')
        if not thead or not tbody:
            raise ValueError(
                f"HTML source is missing mandatory 'thead' or 'tbody' elements "
                f"for {self.KEY_TO_PRE_TOPS}.")

        ths = [_parse_th_tag(th) for th in thead.find_all(name='th')]
        trs = tbody.find_all(name='tr')
        codes = parse_tr(trs=trs, ths=ths, as_dataframe=True)

        codes['Code'] = codes['Code'].map(int)
        codes['Region'] = codes['Code'].map(self._identify_region)

        dagger_mark = ' †'
        depot_name_column = 'Depot name'

        codes['Main Works site'] = codes[depot_name_column].str.endswith(dagger_mark)
        codes[depot_name_column] = codes[depot_name_column].str.removesuffix(dagger_mark)

        four_digit_pre_tops_codes_data = {
            self.KEY_TO_PRE_TOPS: codes,
            self.KEY_TO_LAST_UPDATED_DATE: _get_last_updated_date(soup=soup),
        }

        if verbose in {True, 1}:
            print("Done.")

        self._save_data_to_file(
            data=four_digit_pre_tops_codes_data,
            data_name=self.KEY_TO_PRE_TOPS[:1].lower() + self.KEY_TO_PRE_TOPS[1:],
            verbose=verbose
        )

        return four_digit_pre_tops_codes_data

    def collect_pre_tops_codes(self, confirmation_required=True, verbose=False, raise_error=False):
        # noinspection unresolved-references
        """
        Collect `four-digit pre-TOPS codes <http://www.railwaycodes.org.uk/depots/depots2.shtm>`_
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
        :return: A dictionary containing the four-digit pre-TOPS codes and
            the date they were last updated, or ``None`` if no data is collected.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.other_assets import Depots  # from pyrcs import Depots

            >>> depots = Depots()

            >>> fdpt_codes = depots.collect_pre_tops_codes(verbose=True)
            Proceed with collecting data of "four digit pre-TOPS"?
             [No]|Yes: yes
            Collecting the data ... Done.

            >>> type(fdpt_codes)
            dict
            >>> list(fdpt_codes)
            ['Four digit pre-TOPS', 'Last updated date']

            >>> fdpt_codes_dat = fdpt_codes['Four digit pre-TOPS']
            >>> type(fdpt_codes_dat)
            pandas.DataFrame
            >>> fdpt_codes_dat.shape
            (950, 4)
            >>> fdpt_codes_dat.head()
               Code             Depot name          Region  Main Works site
            0  2000             Accrington  London Midland            False
            1  2001   Derby Litchurch Lane  London Midland             True
            2  2003              Blackburn  London Midland            False
            3  2004  Bolton Trinity Street  London Midland            False
            4  2006                Burnley  London Midland            False
        """

        target_url = None
        if isinstance(self.catalogue, dict):
            target_url = self.catalogue.get(self.KEY_TO_PRE_TOPS)

        if not target_url:
            if verbose:
                print(f"Failed to resolve the target URL for {self.KEY_TO_PRE_TOPS.lower()}.")
            return None

        four_digit_pre_tops_codes_data = self._collect_data_from_source(
            data_name=self.KEY_TO_PRE_TOPS[:1].lower() + self.KEY_TO_PRE_TOPS[1:],
            method=self._collect_pre_tops_codes,
            url=target_url,
            confirmation_required=confirmation_required,
            verbose=verbose,
            raise_error=raise_error
        )

        return four_digit_pre_tops_codes_data

    def fetch_pre_tops_codes(self, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetch data of `four-digit pre-TOPS codes`_.

        .. _`four-digit pre-TOPS codes`: http://www.railwaycodes.org.uk/depots/depots2.shtm

        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the four-digit pre-TOPS codes and
            the date they were last updated.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Depots  # from pyrcs import Depots

            >>> depots = Depots()

            >>> fdpt_codes = depots.fetch_pre_tops_codes()
            >>> type(fdpt_codes)
            dict
            >>> list(fdpt_codes.keys())
            ['Four digit pre-TOPS', 'Last updated date']

            >>> depots.KEY_TO_PRE_TOPS
            'Four digit pre-TOPS codes'

            >>> fdpt_codes_dat = fdpt_codes['Four digit pre-TOPS']
            >>> type(fdpt_codes_dat)
            pandas.DataFrame
            >>> fdpt_codes_dat.shape
            (950, 4)
            >>> fdpt_codes_dat.head()
               Code             Depot name          Region  Main Works site
            0  2000             Accrington  London Midland            False
            1  2001   Derby Litchurch Lane  London Midland             True
            2  2003              Blackburn  London Midland            False
            3  2004  Bolton Trinity Street  London Midland            False
            4  2006                Burnley  London Midland            False
        """

        args = {
            'data_name': re.sub(r'[ -]', '-', self.KEY_TO_PRE_TOPS),
            'method': self.collect_pre_tops_codes,
        }
        kwargs.update(args)

        four_digit_pre_tops_codes_data = self._fetch_data_from_file(
            update=update, dump_dir=dump_dir, verbose=verbose, **kwargs)

        return four_digit_pre_tops_codes_data

    def _collect_1950_system_codes(self, source, verbose=False):
        """
        Parse and save 1950 system depot codes from an HTML source.

        Extracts the HTML table containing 1950 regional depot codes, packages the DataFrame with
        the last updated timestamp and saves the output to file.

        :param source: HTML response object containing the 1950 system depot code table.
        :type source: requests.Response | bs4.BeautifulSoup
        :param verbose: Level of logging detail where ``True`` or ``1`` enables progress messages.
            Defaults to ``False``.
        :type verbose: bool | int
        :return: Dictionary containing the parsed DataFrame and the last updated date.
        :rtype: dict[str, pandas.DataFrame | str]
        :raises ValueError: If the required table elements are missing from ``source``.
        """

        system_1950_codes, soup = self._parse_table_source(
            source=source, dataset_label=self.KEY_TO_1950_SYSTEM
        )

        system_1950_codes_data = {
            self.KEY_TO_1950_SYSTEM: system_1950_codes,
            self.KEY_TO_LAST_UPDATED_DATE: _get_last_updated_date(soup=soup),
        }

        if verbose in {True, 1}:
            print("Done.")

        self._save_data_to_file(
            data=system_1950_codes_data,
            data_name=re.sub(r' \(|\) | ', '-', self.KEY_TO_1950_SYSTEM),
            verbose=verbose
        )

        return system_1950_codes_data

    def collect_1950_system_codes(self, confirmation_required=True, verbose=False,
                                  raise_error=False):
        # noinspection unresolved-references
        """
        Collect `1950 system (pre-TOPS) codes <http://www.railwaycodes.org.uk/depots/depots3.shtm>`_
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
        :return: A dictionary containing the 1950 system (pre-TOPS) codes and
            the date they were last updated, or ``None`` if no data is collected.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.other_assets import Depots  # from pyrcs import Depots

            >>> depots = Depots()

            >>> s1950_codes = depots.collect_1950_system_codes(verbose=True)
            Proceed with collecting data of "1950 system (pre-TOPS)"?
             [No]|Yes: yes
            Collecting the data ... Done.

            >>> type(s1950_codes)
            dict
            >>> list(s1950_codes)
            ['1950 system (pre-TOPS)', 'Last updated date']

            >>> s1950_codes_dat = s1950_codes['1950 system (pre-TOPS)']
            >>> type(s1950_codes_dat)
            pandas.DataFrame
            >>> s1950_codes_dat.shape
            (622, 3)
            >>> s1950_codes_dat.head()
              Code        Depot name                                              Notes
            0   1A         Willesden              From 1950.  Became WN from 6 May 1973
            1   1B            Camden                      From 1950.  To 3 January 1966
            2   1C           Watford              From 1950.  Became WJ from 6 May 1973
            3   1D  Devons Road, Bow  Previously 13B to 9 June 1950.  Became 1J from...
            4   1D        Marylebone  Previously 14F to 31 August 1963.  Became ME f...
        """

        system_1950_codes_data = self._collect_data_from_source(
            data_name=self.KEY_TO_1950_SYSTEM, method=self._collect_1950_system_codes,
            confirmation_required=confirmation_required, verbose=verbose, raise_error=raise_error)

        return system_1950_codes_data

    def fetch_1950_system_codes(self, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetch data of `1950 system (pre-TOPS) codes`_.

        .. _`1950 system (pre-TOPS) codes`: http://www.railwaycodes.org.uk/depots/depots3.shtm

        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the 1950 system (pre-TOPS) codes and
            the date they were last updated.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Depots  # from pyrcs import Depots

            >>> depots = Depots()

            >>> s1950_codes = depots.fetch_1950_system_codes()
            >>> type(s1950_codes)
            dict
            >>> list(s1950_codes)
            ['1950 system (pre-TOPS) codes', 'Last updated date']

            >>> depots.KEY_TO_1950_SYSTEM
            '1950 system (pre-TOPS) codes'

            >>> s1950_codes_dat = s1950_codes['1950 system (pre-TOPS)']
            >>> type(s1950_codes_dat)
            pandas.DataFrame
            >>> s1950_codes_dat.shape
            (622, 3)
            >>> s1950_codes_dat.head()
              Code        Depot name                                              Notes
            0   1A         Willesden              From 1950.  Became WN from 6 May 1973
            1   1B            Camden                      From 1950.  To 3 January 1966
            2   1C           Watford              From 1950.  Became WJ from 6 May 1973
            3   1D  Devons Road, Bow  Previously 13B to 9 June 1950.  Became 1J from...
            4   1D        Marylebone  Previously 14F to 31 August 1963.  Became ME f...
        """

        args = {
            'data_name': re.sub(r' \(|\) | ', '-', self.KEY_TO_1950_SYSTEM).lower(),
            'method': self.collect_1950_system_codes,
        }
        kwargs.update(args)

        system_1950_data = self._fetch_data_from_file(
            update=update, dump_dir=dump_dir, verbose=verbose, **kwargs)

        return system_1950_data

    def _collect_gwr_codes(self, source, verbose=False):
        """
        Parse and save Great Western Railway (GWR) depot codes from an HTML source.

        Extracts both alphabetical and numerical GWR depot code tables from the HTML markup,
        resolves divisional keys, packages the resulting DataFrames and saves the dataset.

        :param source: HTML response object or parsed BeautifulSoup instance containing GWR data.
        :type source: requests.Response | bs4.BeautifulSoup
        :param verbose: Level of logging detail where ``True`` or ``1`` enables progress messages.
            Defaults to ``False``.
        :type verbose: bool | int
        :return: Dictionary containing the parsed GWR depot codes, key mappings and metadata.
        :rtype: dict[str, dict[str, pandas.DataFrame | dict] | str]
        :raises ValueError: If mandatory table elements are missing from ``source``.
        """

        if isinstance(source, bs4.BeautifulSoup):
            soup = source
        else:
            soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

        theads, tbodies = soup.find_all('thead'), soup.find_all('tbody')
        if len(theads) < 2 or len(tbodies) < 2:
            raise ValueError("HTML source is missing expected table elements for GWR codes.")

        tables = []
        for thead, tbody in zip(theads, tbodies):
            ths = [_parse_th_tag(th) for th in thead.find_all('th')]
            trs = tbody.find_all('tr')

            if len(ths) == 2:
                table = parse_tr(trs=trs, ths=ths, as_dataframe=True)
            else:
                list_dat = [[td.get_text(strip=True) for td in tr.find_all('td')] for tr in trs]
                table = pd.DataFrame(data=list_dat, columns=ths)

            tables.append(table)

        alphabetical_codes, numerical_codes = tables[:2]

        span_tags = soup.find_all('span', attrs={'class': 'tab2'})
        # noinspection string-conversion-without-dunder-method
        num_codes_dict = {
            int(span.get_text(strip=True)): str(span.next_sibling or '').replace('=', '').strip()
            for span in span_tags
            if span.get_text(strip=True).isdigit()
        }

        first_col_name = numerical_codes.columns[0]
        temp = numerical_codes[first_col_name].astype(str).str.split(' ', expand=True)
        temp.columns = ['Code', 'Division']

        def _map_division(val):
            if val and str(val)[-1].isdigit():
                key = int(str(val)[-1])
                return num_codes_dict.get(key, val)
            return val

        temp['Division'] = temp['Division'].map(_map_division)
        numerical_codes = pd.concat([temp, numerical_codes.drop(columns=[first_col_name])], axis=1)

        h3_titles = [h3.get_text(strip=True) for h3 in soup.find_all('h3')]
        if len(h3_titles) < 2:
            h3_titles = ['Alphabetical codes', 'Numerical codes']

        gwr_depot_codes_data = dict(
            zip(h3_titles, [alphabetical_codes, numerical_codes])
        )
        gwr_depot_codes_data['Keys to numerical codes'] = num_codes_dict

        gwr_depot_codes = {
            self.KEY_TO_GWR: gwr_depot_codes_data,
            self.KEY_TO_LAST_UPDATED_DATE: _get_last_updated_date(soup=soup),
        }

        if verbose in {True, 1}:
            print("Done.")

        self._save_data_to_file(data=gwr_depot_codes, data_name=self.KEY_TO_GWR, verbose=verbose)

        return gwr_depot_codes

    def collect_gwr_codes(self, confirmation_required=True, verbose=False, raise_error=False):
        # noinspection unresolved-references
        """
        Collect `Great Western Railway (GWR) depot codes
        <http://www.railwaycodes.org.uk/depots/depots4.shtm>`_
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
        :return: A dictionary containing the GWR depot codes and
            the date they were last updated, or ``None`` if no data is collected.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.other_assets import Depots  # from pyrcs import Depots

            >>> depots = Depots()

            >>> gwr_codes = depots.collect_gwr_codes(verbose=True)
            Proceed with collecting data of "GWR"?
             [No]|Yes: yes
            Collecting the data ... Done.

            >>> type(gwr_codes)
            dict
            >>> list(gwr_codes)
            ['GWR', 'Last updated date']

            >>> gwr_codes_dat = gwr_codes['GWR']
            >>> type(gwr_codes_dat)
            dict
            >>> list(gwr_codes_dat.keys())
            ['Alphabetical codes', 'Numerical codes', 'Keys to numerical codes']

            >>> gwr_alpha_codes = gwr_codes_dat['Alphabetical codes']
            >>> type(gwr_alpha_codes)
            pandas.DataFrame
            >>> gwr_alpha_codes.shape
            (75, 2)
            >>> gwr_alpha_codes.head()
                Code   Depot name
            0  ABEEG     Aberbeeg
            1    ABG     Aberbeeg
            2    AYN    Abercynon
            3   ABDR     Aberdare
            4    ABH  Aberystwyth
        """

        gwr_depot_codes = self._collect_data_from_source(
            data_name=self.KEY_TO_GWR, method=self._collect_gwr_codes,
            confirmation_required=confirmation_required, verbose=verbose, raise_error=raise_error)

        return gwr_depot_codes

    def fetch_gwr_codes(self, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetch data of `Great Western Railway (GWR) depot codes`_.

        .. _`Great Western Railway (GWR) depot codes`:
            http://www.railwaycodes.org.uk/depots/depots4.shtm

        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the GWR depot codes and
            the date they were last updated.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Depots  # from pyrcs import Depots

            >>> depots = Depots()

            >>> gwr_codes = depots.fetch_gwr_codes()
            >>> type(gwr_codes)
            dict
            >>> list(gwr_codes.keys())
            ['GWR', 'Last updated date']

            >>> depots.KEY_TO_GWR
            'GWR'

            >>> gwr_codes_dat = gwr_codes[depots.KEY_TO_GWR]
            >>> type(gwr_codes_dat)
            dict
            >>> list(gwr_codes_dat)
            ['Alphabetical codes', 'Numerical codes', 'Keys to numerical codes']

            >>> gwr_alpha_codes = gwr_codes_dat['Alphabetical codes']
            >>> type(gwr_alpha_codes)
            pandas.DataFrame
            >>> gwr_alpha_codes.shape
            (75, 2)
            >>> gwr_alpha_codes.head()
                Code   Depot name
            0  ABEEG     Aberbeeg
            1    ABG     Aberbeeg
            2    AYN    Abercynon
            3   ABDR     Aberdare
            4    ABH  Aberystwyth
        """

        kwargs.update({'data_name': self.KEY_TO_GWR, 'method': self.collect_gwr_codes})

        gwr_depot_codes = self._fetch_data_from_file(
            update=update, dump_dir=dump_dir, verbose=verbose, **kwargs)

        return gwr_depot_codes

    def fetch_codes(self, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetch data of `depot codes`_.

        .. _`depot codes`: http://www.railwaycodes.org.uk/depots/depots0.shtm

        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the depot codes and the date they were last updated.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Depots  # from pyrcs import Depots

            >>> depots = Depots()

            >>> depots_codes = depots.fetch_codes()
            >>> type(depots_codes)
            dict
            >>> list(depots_codes)
            ['Depots', 'Last updated date']

            >>> depots.KEY
            'Depots'

            >>> depots_codes_dat = depots_codes[depots.KEY]
            >>> type(depots_codes_dat)
            dict
            >>> list(depots_codes_dat)
            ['1950 system (pre-TOPS)', 'GWR', 'Four digit pre-TOPS', 'Two character TOPS']

            >>> depots.KEY_TO_PRE_TOPS
            'Four digit pre-TOPS'
            >>> depots_codes_dat[depots.KEY_TO_PRE_TOPS].shape
            (950, 4)
            >>> depots_codes_dat[depots.KEY_TO_PRE_TOPS].head()
               Code             Depot name          Region  Main Works site
            0  2000             Accrington  London Midland            False
            1  2001   Derby Litchurch Lane  London Midland             True
            2  2003              Blackburn  London Midland            False
            3  2004  Bolton Trinity Street  London Midland            False
            4  2006                Burnley  London Midland            False

            >>> depots.KEY_TO_TOPS
            'Two character TOPS'
            >>> depots_codes_dat[depots.KEY_TO_TOPS].shape
            (591, 5)
            >>> depots_codes_dat[depots.KEY_TO_TOPS].head()
              Code  ...                Notes
            0   AB  ...          Closed 1987
            1   AB  ...
            2   AC  ...  Became WH from 1994
            3   AC  ...
            4   AD  ...
            [5 rows x 5 columns]
        """

        verbose_ = get_batch_fetch_verbosity(data_dir=dump_dir, verbose=verbose)

        depot_data = []
        for func in dir(self):
            if re.match(r'fetch_(.*)_codes', func):
                depot_data.append(getattr(self, func)(update=update, verbose=verbose_, **kwargs))

        depot_codes = {
            self.KEY: {next(iter(x)): next(iter(x.values())) for x in depot_data},
            self.KEY_TO_LAST_UPDATED_DATE:
                max(next(itertools.islice(iter(x.values()), 1, 2)) for x in depot_data)
        }

        if dump_dir is not None:
            self._save_data_to_file(
                data=depot_codes, data_name=self.KEY, dump_dir=dump_dir, verbose=verbose
            )

        return depot_codes
