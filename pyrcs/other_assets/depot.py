"""
Collects data of `depot codes <http://www.railwaycodes.org.uk/depots/depots0.shtm>`_.
"""

import itertools
import re
import urllib.parse

import bs4
import pandas as pd

from .._base import _Base
from ..parser import _get_last_updated_date, parse_tr
from ..utils import fetch_all_verbose, home_page_url


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
    KEY_TO_TOPS: str = 'Two character TOPS codes'
    #: The key for accessing the data of four digit pre-TOPS codes
    KEY_TO_PRE_TOPS: str = 'Four digit pre-TOPS codes'
    #: The key for accessing the data of 1950 system (pre-TOPS) codes
    KEY_TO_1950_SYSTEM: str = '1950 system (pre-TOPS) codes'
    #: The key for accessing the data of GWR codes
    KEY_TO_GWR: str = 'GWR codes'

    #: The URL of the main web page for the data.
    URL: str = urllib.parse.urljoin(home_page_url(), '/depots/depots0.shtm')

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
            data_dir=data_dir, content_type='catalogue', data_category="other-assets",
            update=update, verbose=verbose)

    def _collect_tops_codes(self, source, verbose=False):
        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

        thead, tbody = soup.find('thead'), soup.find('tbody')
        ths = [th.text for th in thead.find_all(name='th')]
        trs = tbody.find_all(name='tr')
        two_char_tops_codes = parse_tr(trs=trs, ths=ths, as_dataframe=True)

        two_char_tops_codes_data = {
            self.KEY_TO_TOPS: two_char_tops_codes,
            self.KEY_TO_LAST_UPDATED_DATE: _get_last_updated_date(soup=soup)
        }

        if verbose in {True, 1}:
            print("Done.")

        self._save_data_to_file(
            data=two_char_tops_codes_data, data_name=self.KEY_TO_TOPS, verbose=verbose)

        return two_char_tops_codes_data

    def collect_tops_codes(self, confirmation_required=True, verbose=False, raise_error=False):
        """
        Collects `two-character TOPS codes <http://www.railwaycodes.org.uk/depots/depots1.shtm>`_
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
            >>> tct_codes = depots.collect_tops_codes()
            To collect data of two character TOPS codes
            ? [No]|Yes: yes
            >>> type(tct_codes)
            dict
            >>> list(tct_codes.keys())
            ['Two character TOPS codes', 'Last updated date']
            >>> depots.KEY_TO_TOPS
            'Two character TOPS codes'
            >>> tct_codes_dat = tct_codes[depots.KEY_TO_TOPS]
            >>> type(tct_codes_dat)
            pandas.core.frame.DataFrame
            >>> tct_codes_dat.head()
              Code  ...                Notes
            0   AB  ...          Closed 1987
            1   AB  ...
            2   AC  ...  Became WH from 1994
            3   AC  ...
            4   AD  ...
            [5 rows x 5 columns]
        """

        two_char_tops_codes_data = self._collect_data_from_source(
            data_name=self.KEY_TO_TOPS, method=self._collect_tops_codes,
            confirmation_required=confirmation_required, verbose=verbose, raise_error=raise_error)

        return two_char_tops_codes_data

    def fetch_tops_codes(self, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetches the data of `two-character TOPS codes`_.

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
            ['Two character TOPS codes', 'Last updated date']
            >>> depots.KEY_TO_TOPS
            'Two character TOPS codes'
            >>> tct_codes_dat = tct_codes[depots.KEY_TO_TOPS]
            >>> type(tct_codes_dat)
            pandas.core.frame.DataFrame
            >>> tct_codes_dat.head()
              Code  ...                Notes
            0   AB  ...          Closed 1987
            1   AB  ...
            2   AC  ...  Became WH from 1994
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
        if 2000 <= x < 3000:
            _region_name = 'London Midland'
        elif 3000 <= x < 4000:
            _region_name = 'Western'
        elif 4000 <= x < 5000:
            _region_name = 'Southern'
        elif 5000 <= x < 7000:
            _region_name = 'Eastern'
        else:  # x >= 7000:
            _region_name = 'Scottish'
        return _region_name

    def _collect_pre_tops_codes(self, source, verbose=False):
        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

        thead, tbody = soup.find('thead'), soup.find('tbody')

        ths = [th.get_text(strip=True) for th in thead.find_all(name='th')]
        trs = tbody.find_all(name='tr')
        codes = parse_tr(trs=trs, ths=ths, as_dataframe=True)
        codes.Code = codes['Code'].map(int)

        codes['Region'] = codes.Code.map(self._identify_region)

        dagger_mark, depot_name_column = ' †', 'Depot name'
        codes['Main Works site'] = codes[depot_name_column].map(
            lambda x: True if x.endswith(dagger_mark) else False)

        codes[depot_name_column] = codes[depot_name_column].str.rstrip(dagger_mark)

        four_digit_pre_tops_codes_data = {
            self.KEY_TO_PRE_TOPS: codes,
            self.KEY_TO_LAST_UPDATED_DATE: _get_last_updated_date(soup=soup),
        }

        if verbose in {True, 1}:
            print("Done.")

        self._save_data_to_file(
            data=four_digit_pre_tops_codes_data,
            data_name=self.KEY_TO_PRE_TOPS[:1].lower() + self.KEY_TO_PRE_TOPS[1:], verbose=verbose)

        return four_digit_pre_tops_codes_data

    def collect_pre_tops_codes(self, confirmation_required=True, verbose=False, raise_error=False):
        """
        Collects `four-digit pre-TOPS codes <http://www.railwaycodes.org.uk/depots/depots2.shtm>`_
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
            >>> fdpt_codes = depots.collect_pre_tops_codes()
            To collect data of four digit pre-TOPS codes
            ? [No]|Yes: yes
            >>> type(fdpt_codes)
            dict
            >>> list(fdpt_codes.keys())
            ['Four digit pre-TOPS codes', 'Last updated date']
            >>> depots.KEY_TO_PRE_TOPS
            'Four digit pre-TOPS codes'
            >>> fdpt_codes_dat = fdpt_codes[depots.KEY_TO_PRE_TOPS]
            >>> type(fdpt_codes_dat)
            pandas.core.frame.DataFrame
            >>> fdpt_codes_dat.head()
               Code             Depot name          Region  Main Works site
            0  2000             Accrington  London Midland            False
            1  2001   Derby Litchurch Lane  London Midland             True
            2  2003              Blackburn  London Midland            False
            3  2004  Bolton Trinity Street  London Midland            False
            4  2006                Burnley  London Midland            False
        """

        four_digit_pre_tops_codes_data = self._collect_data_from_source(
            data_name=self.KEY_TO_PRE_TOPS[:1].lower() + self.KEY_TO_PRE_TOPS[1:],
            method=self._collect_pre_tops_codes, url=self.catalogue[self.KEY_TO_PRE_TOPS],
            confirmation_required=confirmation_required, verbose=verbose, raise_error=raise_error)

        return four_digit_pre_tops_codes_data

    def fetch_pre_tops_codes(self, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetches the data of `four-digit pre-TOPS codes`_.

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
            ['Four digit pre-TOPS codes', 'Last updated date']
            >>> depots.KEY_TO_PRE_TOPS
            'Four digit pre-TOPS codes'
            >>> fdpt_codes_dat = fdpt_codes[depots.KEY_TO_PRE_TOPS]
            >>> type(fdpt_codes_dat)
            pandas.core.frame.DataFrame
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
        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

        thead, tbody = soup.find('thead'), soup.find('tbody')

        ths = [th.text for th in thead.find_all(name='th')]
        trs = tbody.find_all(name='tr')
        system_1950_codes = parse_tr(trs=trs, ths=ths, as_dataframe=True)

        system_1950_codes_data = {
            self.KEY_TO_1950_SYSTEM: system_1950_codes,
            self.KEY_TO_LAST_UPDATED_DATE: _get_last_updated_date(soup=soup),
        }

        if verbose in {True, 1}:
            print("Done.")

        self._save_data_to_file(
            data=system_1950_codes_data,
            data_name=re.sub(r' \(|\) | ', '-', self.KEY_TO_1950_SYSTEM), verbose=verbose)

        return system_1950_codes_data

    def collect_1950_system_codes(self, confirmation_required=True, verbose=False,
                                  raise_error=False):
        """
        Collects
        `1950 system (pre-TOPS) codes <http://www.railwaycodes.org.uk/depots/depots3.shtm>`_
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
            >>> s1950_codes = depots.collect_1950_system_codes()
            To collect data of 1950 system (pre-TOPS) codes
            ? [No]|Yes: yes
            >>> type(s1950_codes)
            dict
            >>> list(s1950_codes.keys())
            ['1950 system (pre-TOPS) codes', 'Last updated date']
            >>> depots.KEY_TO_1950_SYSTEM
            '1950 system (pre-TOPS) codes'
            >>> s1950_codes_dat = s1950_codes[depots.KEY_TO_1950_SYSTEM]
            >>> type(s1950_codes_dat)
            pandas.core.frame.DataFrame
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
        Fetches the data of `1950 system (pre-TOPS) codes`_.

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
            >>> list(s1950_codes.keys())
            ['1950 system (pre-TOPS) codes', 'Last updated date']
            >>> depots.KEY_TO_1950_SYSTEM
            '1950 system (pre-TOPS) codes'
            >>> s1950_codes_dat = s1950_codes[depots.KEY_TO_1950_SYSTEM]
            >>> type(s1950_codes_dat)
            pandas.core.frame.DataFrame
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
        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

        theads, tbodies = soup.find_all(name='thead'), soup.find_all(name='tbody')

        tables = []
        for thead, tbody in zip(theads, tbodies):
            ths = [th.text for th in thead.find_all(name='th')]
            trs = tbody.find_all(name='tr')

            if len(ths) == 2:
                table = parse_tr(trs=trs, ths=ths, as_dataframe=True)
            else:
                list_dat = [[td.text for td in tr.find_all('td')] for tr in trs]
                table = pd.DataFrame(data=list_dat, columns=ths)

            tables.append(table)

        alphabetical_codes, numerical_codes = tables

        span_tags = soup.find_all(name='span', attrs={'class': 'tab2'})
        num_codes_dict = dict([
            (int(span_tag.text), str(span_tag.next_sibling).replace(' = ', '').strip())
            for span_tag in span_tags])

        numerical_codes.rename(columns={'sort by division': 'Division'}, inplace=True)
        numerical_codes.Division = numerical_codes.Code.map(
            lambda x: num_codes_dict[int(str(x)[-1])])

        h3_titles = [h3.text for h3 in soup.find_all('h3')]
        gwr_depot_codes_data = dict(zip(h3_titles, [alphabetical_codes, numerical_codes]))

        gwr_depot_codes = {
            self.KEY_TO_GWR: gwr_depot_codes_data,
            self.KEY_TO_LAST_UPDATED_DATE: _get_last_updated_date(soup=soup),
        }

        if verbose in {True, 1}:
            print("Done.")

        self._save_data_to_file(
            data=gwr_depot_codes, data_name=self.KEY_TO_GWR, verbose=verbose)

        return gwr_depot_codes

    def collect_gwr_codes(self, confirmation_required=True, verbose=False, raise_error=False):
        """
        Collects `Great Western Railway (GWR) depot codes
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
            >>> gwr_codes = depots.collect_gwr_codes()
            To collect data of GWR codes
            ? [No]|Yes: yes
            >>> type(gwr_codes)
            dict
            >>> list(gwr_codes.keys())
            ['GWR codes', 'Last updated date']
            >>> depots.KEY_TO_GWR
            'GWR codes'
            >>> gwr_codes_dat = gwr_codes[depots.KEY_TO_GWR]
            >>> type(gwr_codes_dat)
            dict
            >>> list(gwr_codes_dat.keys())
            ['Alphabetical codes', 'Numerical codes']
            >>> gwr_alpha_codes = gwr_codes_dat['Alphabetical codes']
            >>> type(gwr_alpha_codes)
            pandas.core.frame.DataFrame
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
        Fetches the data of `Great Western Railway (GWR) depot codes`_.

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
            ['GWR codes', 'Last updated date']
            >>> depots.KEY_TO_GWR
            'GWR codes'
            >>> gwr_codes_dat = gwr_codes[depots.KEY_TO_GWR]
            >>> type(gwr_codes_dat)
            dict
            >>> list(gwr_codes_dat.keys())
            ['Alphabetical codes', 'Numerical codes']
            >>> gwr_alpha_codes = gwr_codes_dat['Alphabetical codes']
            >>> type(gwr_alpha_codes)
            pandas.core.frame.DataFrame
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

    def fetch_codes(self, update=False, dump_dir=None, verbose=False):
        """
        Fetches the data of `depot codes`_.

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
            >>> list(depots_codes.keys())
            ['Depots', 'Last updated date']
            >>> depots.KEY
            'Depots'
            >>> depots_codes_dat = depots_codes[depots.KEY]
            >>> type(depots_codes_dat)
            dict
            >>> list(depots_codes_dat.keys())
            ['1950 system (pre-TOPS) codes',
             'Four digit pre-TOPS codes',
             'GWR codes',
             'Two character TOPS codes']
            >>> depots.KEY_TO_PRE_TOPS
            'Four digit pre-TOPS codes'
            >>> depots_codes_dat[depots.KEY_TO_PRE_TOPS].head()
               Code             Depot name          Region  Main Works site
            0  2000             Accrington  London Midland            False
            1  2001   Derby Litchurch Lane  London Midland             True
            2  2003              Blackburn  London Midland            False
            3  2004  Bolton Trinity Street  London Midland            False
            4  2006                Burnley  London Midland            False
            >>> depots.KEY_TO_TOPS
            'Two character TOPS codes'
            >>> depots_codes_dat[depots.KEY_TO_TOPS].head()
              Code  ...                Notes
            0   AB  ...          Closed 1987
            1   AB  ...
            2   AC  ...  Became WH from 1994
            3   AC  ...
            4   AD  ...
            [5 rows x 5 columns]
        """

        verbose_ = fetch_all_verbose(data_dir=dump_dir, verbose=verbose)

        depot_data = []
        for func in dir(self):
            if re.match(r'fetch_(.*)_codes', func):
                depot_data.append(getattr(self, func)(update=update, verbose=verbose_))

        depot_codes = {
            self.KEY: {next(iter(x)): next(iter(x.values())) for x in depot_data},
            self.KEY_TO_LAST_UPDATED_DATE:
                max(next(itertools.islice(iter(x.values()), 1, 2)) for x in depot_data)
        }

        if dump_dir is not None:
            self._save_data_to_file(
                data=depot_codes, data_name=self.KEY, dump_dir=dump_dir, verbose=verbose)

        return depot_codes
