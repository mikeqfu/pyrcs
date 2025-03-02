"""
Collects `Line of Route (LOR/PRIDE) <http://www.railwaycodes.org.uk/pride/pride0.shtm>`_ codes.
"""

import itertools
import os
import re
import urllib.parse

import bs4
import pandas as pd
from pyhelpers.ops import remove_dict_keys, update_dict_keys
from pyhelpers.text import find_similar_str

from .._base import _Base
from ..parser import _get_last_updated_date, parse_tr
from ..utils import fetch_all_verbose, home_page_url, print_inst_conn_err, print_void_msg


class LOR(_Base):
    """
    A class for collecting data of
    `Line of Route (LOR/PRIDE) <http://www.railwaycodes.org.uk/pride/pride0.shtm>`_.

    .. note::

        'LOR' and 'PRIDE' stands for 'Line Of Route' and 'Possession Resource Information Database',
        respectively.
    """

    #: The name of the data.
    NAME: str = 'Possession Resource Information Database (PRIDE)/Line Of Route (LOR) codes'
    #: A short name of the data
    SHORT_NAME: str = 'Line of Route (LOR/PRIDE) codes'
    #: The key for accessing the data.
    KEY: str = 'LOR'
    #: The key for accessing the data of *prefixes*.
    KEY_P: str = 'Key to prefixes'
    #: The key for accessing the data of *ELR/LOR converter*.
    KEY_ELC: str = 'ELR/LOR converter'

    #: The URL of the main web page for the data.
    URL = urllib.parse.urljoin(home_page_url(), '/pride/pride0.shtm')

    #: The key used to reference the last updated date in the data.
    KEY_TO_LAST_UPDATED_DATE = 'Last updated date'

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
        :ivar list valid_prefixes: A list of valid prefixes.

        **Examples**::

            >>> from pyrcs.line_data import LOR  # from pyrcs import LOR
            >>> lor = LOR()
            >>> lor.NAME
            'Possession Resource Information Database (PRIDE)/Line Of Route (LOR) codes'
            >>> lor.URL
            'http://www.railwaycodes.org.uk/pride/pride0.shtm'
        """

        super().__init__(
            data_dir=data_dir, content_type='catalogue', data_category="line-data",
            update=update, verbose=verbose)

        self.valid_prefixes = self.get_keys_to_prefixes(prefixes_only=True)

    def validate_prefix(self, prefix):
        """
        Validates and standardises a PRIDE/LOR code prefix.

        If the provided `prefix` is not found in the list of valid prefixes, an attempt is made
        to find the closest matching valid prefix. If no match is found, an error is raised.

        :param prefix: The PRIDE/LOR code prefix to validate.
        :type prefix: str
        :raises AssertionError: If the `prefix` is not a valid PRIDE/LOR prefix.
        :return: A validated and standardised uppercase prefix.
        :rtype: str

        **Examples**::

            >>> from pyrcs.line_data import LOR  # from pyrcs import LOR
            >>> lor = LOR()
            >>> lor.validate_prefix(prefix='cy')
            'CY'
            >>> lor.validate_prefix(prefix='ca')
            Traceback (most recent call last):
                ...
            AssertionError: `prefix` must be one of ['CY', 'EA', 'GW', 'LN', 'MD', 'NW', 'NZ', ...
        """

        prefix_ = prefix.upper()

        if prefix_ not in self.valid_prefixes:
            prefix_ = find_similar_str(prefix_, self.valid_prefixes)

            if not prefix_:
                raise AssertionError(f"`prefix` must be one of {self.valid_prefixes}")

        return prefix_

    def get_url(self, prefix):
        """
        Generates the URL for the given PRIDE/LOR code prefix.

        This method constructs the appropriate webpage URL based on the provided `prefix`,
        ensuring that it is valid before appending the correct suffix.

        :param prefix: The PRIDE/LOR code prefix.
        :type prefix: str
        :return: A fully constructed URL corresponding to the given prefix.
        :rtype: str

        **Examples**::

            >>> from pyrcs.line_data import LOR  # from pyrcs import LOR
            >>> lor = LOR()
            >>> lor.get_url(prefix='CY')
            'http://www.railwaycodes.org.uk/pride/pridecy.shtm'
            >>> lor.get_url(prefix='CA')
            Traceback (most recent call last):
                ...
            AssertionError: `prefix` must be one of ['CY', 'EA', 'GW', 'LN', 'MD', 'NW', 'NZ', ...
        """

        url = urllib.parse.urljoin(home_page_url(), '/pride/pride')

        prefix_ = self.validate_prefix(prefix)

        if prefix_ in ("NW", "NZ"):
            url += 'nw.shtm'
        else:
            url += f'{prefix_.lower()}.shtm'

        return url

    def _parse_keys_to_prefixes(self, source, verbose=False):
        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')
        span_tags = soup.find_all(name='span', attrs={'class': 'tab2'})

        data = [
            (x.get_text(strip=True), str(x.next_sibling).strip().replace('=  ', ''))
            for x in span_tags]

        lor_pref = pd.DataFrame(data=data, columns=['Prefixes', 'Name'])

        keys_to_prefixes = {
            self.KEY_P: lor_pref, self.KEY_TO_LAST_UPDATED_DATE: self.last_updated_date}

        self._save_data_to_file(
            data=keys_to_prefixes, data_name="keys-to-prefixes", verbose=verbose)

        return keys_to_prefixes

    def collect_keys_to_prefixes(self, confirmation_required=True, verbose=False,
                                 raise_error=False):
        # noinspection PyShadowingNames
        """
        Collects the keys to PRIDE/LOR code prefixes from the source web page.

        :param confirmation_required: Whether user confirmation is required;
            if ``confirmation_required=True`` (default), prompts the user for confirmation
            before proceeding with data collection.
        :type confirmation_required: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :param raise_error: Whether to raise the provided exception;
            if ``raise_error=False`` (default), the error will be suppressed.
        :type raise_error: bool
        :return: A dictionary containing code prefixes and the last updated date,
            or ``None`` if no data is available.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.line_data import LOR  # from pyrcs import LOR
            >>> lor = LOR()
            >>> lor_page_urls = lor.collect_keys_to_prefixes()
            To collect data of URLs to LOR codes web pages
            ? [No]|Yes: yes
            Collecting the data ... Done.
            >>> lor_page_urls[0]
            'http://www.railwaycodes.org.uk/pride/pridecy.shtm'
        """

        keys_to_prefixes = self._collect_data_from_source(
            data_name='keys to LOR prefixes', method=self._parse_keys_to_prefixes, url=self.URL,
            confirmation_required=confirmation_required, verbose=verbose, raise_error=raise_error)

        return keys_to_prefixes

    def get_keys_to_prefixes(self, prefixes_only=True, update=False, dump_dir=None, verbose=False,
                             **kwargs):
        """
        Gets the keys to PRIDE/LOR code prefixes.

        :param prefixes_only: If ``True`` (default), returns only the prefixes;
            otherwise, additional information, including the last updated date.
        :type prefixes_only: bool
        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A list of the keys to LOR code prefixes if ``prefixes_only=True``,
            otherwise a dictionary containing code prefixes and the last updated date,
            or ``None`` if no data is available.
        :rtype: list | dict | None

        **Examples**::

            >>> from pyrcs.line_data import LOR  # from pyrcs import LOR
            >>> lor = LOR()
            >>> keys_to_pfx = lor.get_keys_to_prefixes()
            >>> keys_to_pfx
            ['CY', 'EA', 'GW', 'LN', 'MD', 'NW', 'NZ', 'SC', 'SO', 'SW', 'XR']
            >>> keys_to_pfx = lor.get_keys_to_prefixes(prefixes_only=False)
            >>> type(keys_to_pfx)
            dict
            >>> list(keys_to_pfx.keys())
            ['Key to prefixes', 'Last updated date']
            >>> keys_to_pfx_codes = keys_to_pfx['Key to prefixes']
            >>> type(keys_to_pfx_codes)
            pandas.core.frame.DataFrame
            >>> keys_to_pfx_codes.head()
              Prefixes                                    Name
            0       CY                                   Wales
            1       EA         South Eastern: East Anglia area
            2       GW  Great Western (later known as Western)
            3       LN                  London & North Eastern
            4       MD       North West: former Midlands lines
        """

        kwargs.update({'data_name': "keys-to-prefixes", 'method': self.collect_keys_to_prefixes})

        keys_to_prefixes = self._fetch_data_from_file(
            update=update, dump_dir=dump_dir, verbose=verbose, **kwargs)

        if prefixes_only:
            keys_to_prefixes = keys_to_prefixes[self.KEY_P]['Prefixes'].to_list()

            if update and len(keys_to_prefixes) > 0:
                self.valid_prefixes = keys_to_prefixes

        return keys_to_prefixes

    def _parse_page_urls(self, source, verbose=False):
        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

        links = soup.find_all(
            name='a', href=re.compile('^pride|elrmapping'),
            string=re.compile('.*(codes|converter|Historical)'))

        lor_page_urls = list(
            dict.fromkeys([self.URL.replace(os.path.basename(self.URL), x['href']) for x in links]))

        if verbose in {True, 1}:
            print("Done.")

        self._save_data_to_file(data=lor_page_urls, data_name="prefix-page-urls", verbose=verbose)

        return lor_page_urls

    def collect_page_urls(self, confirmation_required=True, verbose=False, raise_error=False):
        # noinspection PyShadowingNames
        """
        Collects a list of URLs to
        `PRIDE/LOR codes <http://www.railwaycodes.org.uk/pride/pride0.shtm>`_ web pages.

        :param confirmation_required: Whether user confirmation is required;
            if ``confirmation_required=True`` (default), prompts the user for confirmation
            before proceeding with data collection.
        :type confirmation_required: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :param raise_error: Whether to raise the provided exception;
            if ``raise_error=False`` (default), the error will be suppressed.
        :type raise_error: bool
        :return: A list of URLs of web pages the LOR codes.
        :rtype: list

        **Examples**::

            >>> from pyrcs.line_data import LOR  # from pyrcs import LOR
            >>> lor = LOR()
            >>> lor_page_urls = lor.collect_page_urls()
            To collect data of URLs to LOR codes web pages
            ? [No]|Yes: yes
            Collecting the data ... Done.
            >>> lor_page_urls[0]
            'http://www.railwaycodes.org.uk/pride/pridecy.shtm'
        """

        lor_page_urls = self._collect_data_from_source(
            data_name='URLs to LOR codes web pages', method=self._parse_page_urls, url=self.URL,
            confirmation_required=confirmation_required, verbose=verbose, raise_error=raise_error)

        return lor_page_urls

    def get_page_urls(self, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Gets a list of URLs to
        `PRIDE/LOR codes <http://www.railwaycodes.org.uk/pride/pride0.shtm>`_ web pages.

        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A list of URLs of the web pages hosting LOR codes for each prefix.
        :rtype: list | None

        **Examples**::

            >>> from pyrcs.line_data import LOR  # from pyrcs import LOR
            >>> lor = LOR()
            >>> lor_urls = lor.get_page_urls()
            >>> type(lor_urls)
            list
            >>> lor_urls[0]
            'http://www.railwaycodes.org.uk/pride/pridecy.shtm'
        """

        kwargs.update({'data_name': "prefix-page-urls", 'method': self.collect_page_urls})

        lor_page_urls = self._fetch_data_from_file(
            update=update, dump_dir=dump_dir, verbose=verbose, **kwargs)

        return lor_page_urls

    @staticmethod
    def _parse_line_name(x):
        """
        Parses the column of 'Line Name'.

        :return: The line name and its corresponding note.
        :rtype: tuple
        """
        # re.search('\w+.*(?= \(\[\')', x).group()
        # re.search('(?<=\(\[\')\w+.*(?=\')', x).group()
        try:
            line_name, line_name_note = x.split(' ([\'')
            line_name_note = line_name_note.strip('\'])')

        except ValueError:
            line_name, line_name_note = x, ''

        return line_name, line_name_note

    @staticmethod
    def _parse_ra(x):
        # x = '3✖Originally reported as RA4'
        if '✖' in x:
            ra_dat, ra_note = x.split('✖')
        elif x == '[unknown]':
            ra_dat, ra_note = '', 'unknown'
        else:
            ra_dat, ra_note = x, ''

        return ra_dat, ra_note

    def _parse_h3_table(self, tbl):
        # thead, tbody = tbl[0].find('thead'), tbl[0].find('tbody')
        thead, tbody = tbl.find('thead'), tbl.find('tbody')
        ths = [x.text.replace('\n', ' ') for x in thead.find_all('th')]
        trs = tbody.find_all('tr')
        tbl_ = parse_tr(trs=trs, ths=ths, as_dataframe=True)

        ln_col_name, ra_col_name = 'Line Name', 'Route Availability (RA)'

        tbl_[[ln_col_name, ln_col_name + ' Note']] = pd.DataFrame(
            tbl_[ln_col_name].map(self._parse_line_name).to_list(), index=tbl_.index)

        tbl_[[ra_col_name, 'RA Note']] = pd.DataFrame(
            tbl_[ra_col_name].map(self._parse_ra).to_list(), index=tbl_.index)

        try:
            # note_dat_ = [
            #     (x['id'].title(), x.text.strip().replace('\xa0', ''))
            #     for x in soup.find('ol').findChildren('a')]
            # note_dat = dict(note_dat_)
            note = tbl.find_previous('p').text

        except AttributeError:
            # note = dict([('Note', None)])
            note = ''

        return tbl_, note

    def _parse_codes(self, prefix, source, verbose=False):
        # prefix = prefix.upper()
        # assert prefix in self.valid_prefixes, f"`prefix` must be one of {self.valid_prefixes}"

        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

        h3, table = soup.find_all(name='h3'), soup.find_all(name='table')
        if len(h3) == 0:
            code_data, code_notes = self._parse_h3_table(table[0])

            lor_codes_by_initials = {prefix: code_data, 'Notes': code_notes}

        else:
            # code_data_and_notes = [
            #     dict(zip([prefix, 'Notes'], self._parse_h3_table(x, soup=soup)))
            #     for x in zip(*[iter(table)] * 2)]
            data_and_note = [self._parse_h3_table(tbl) for tbl in table]
            keys = [(h3_.text, h3_.text + ' note') for h3_ in h3]

            code_data_and_notes = dict(
                zip(*map(itertools.chain.from_iterable, [keys, data_and_note])))

            lor_codes_by_initials = {prefix: code_data_and_notes}

        last_updated_date = _get_last_updated_date(soup=soup)

        lor_codes_by_initials.update({self.KEY_TO_LAST_UPDATED_DATE: last_updated_date})

        if verbose in {True, 1}:
            print("Done.")

        self._save_data_to_file(
            data=lor_codes_by_initials, data_name=prefix.lower(), sub_dir="prefixes",
            verbose=verbose)

        return lor_codes_by_initials

    def collect_codes(self, prefix, confirmation_required=True, verbose=False, raise_error=False):
        """
        Collects data of `PRIDE/LOR codes <http://www.railwaycodes.org.uk/pride/pride0.shtm>`_
        for the given prefix.

        :param prefix: The prefix of LOR codes to collect.
        :type prefix: str
        :param confirmation_required: Whether user confirmation is required;
            if ``confirmation_required=True`` (default), prompts the user for confirmation
            before proceeding with data collection.
        :type confirmation_required: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :param raise_error: Whether to raise the provided exception;
            if ``raise_error=False`` (default), the error will be suppressed.
        :type raise_error: bool
        :return: A dictionary containing the LOR codes for the given ``prefix``,
            or ``None`` if no data is available.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.line_data import LOR  # from pyrcs import LOR
            >>> lor = LOR()
            >>> lor_codes_cy = lor.collect_codes(prefix='CY')
            >>> type(lor_codes_cy)
            dict
            >>> list(lor_codes_cy.keys())
            ['CY', 'Notes', 'Last updated date']
            >>> cy_codes = lor_codes_cy['CY']
            >>> type(cy_codes)
            pandas.core.frame.DataFrame
            >>> cy_codes.head()
                 Code  ...                       RA Note
            0   CY240  ...           Caerwent branch RA4
            1  CY1540  ...  Pembroke - Pembroke Dock RA6
            [2 rows x 5 columns]
            >>> lor_codes_nw = lor.collect_codes(prefix='NW')
            >>> type(lor_codes_nw)
            dict
            >>> list(lor_codes_nw.keys())
            ['NW/NZ', 'Notes', 'Last updated date']
            >>> nw_codes = lor_codes_nw['NW/NZ']
            >>> nw_codes.head()
                 Code  ... RA Note
            0  NW1001  ...
            1  NW1002  ...
            2  NW1003  ...
            3  NW1004  ...
            4  NW1005  ...
            [5 rows x 5 columns]
            >>> lor_codes_xr = lor.collect_codes(prefix='XR')
            >>> type(lor_codes_xr)
            dict
            >>> list(lor_codes_xr.keys())
            ['XR', 'Last updated date']
            >>> xr_codes = lor_codes_xr['XR']
            >>> type(xr_codes)
            dict
            >>> list(xr_codes.keys())
            ['Current codes', 'Current codes note', 'Past codes', 'Past codes note']
            >>> xr_codes['Past codes'].head()
                Code  ... RA Note
            0  XR001  ...
            1  XR002  ...
            [2 rows x 5 columns]
            >>> xr_codes['Current codes'].head()
                Code  ...                     RA Note
            0  XR001  ...  Originally reported as RA4
            1  XR002  ...  Originally reported as RA4
            [2 rows x 5 columns]
        """

        prefix_ = self.validate_prefix(prefix=prefix)

        url = self.get_url(prefix=prefix_)

        lor_codes = self._collect_data_from_source(
            data_name=self.KEY, method=self._parse_codes, url=url, initial=prefix_, prefix=prefix_,
            confirmation_required=confirmation_required, verbose=verbose, raise_error=raise_error)

        return lor_codes

    def fetch_codes(self, prefix=None, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetches data of `PRIDE/LOR codes`_.

        .. _`PRIDE/LOR codes`: http://www.railwaycodes.org.uk/pride/pride0.shtm

        :param prefix: The prefix of LOR codes; defaults to ``None``.
        :type prefix: str | None
        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the LOR codes.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.line_data import LOR  # from pyrcs import LOR
            >>> lor = LOR()
            >>> lor_codes_dat_cy = lor.fetch_codes(prefix='CY')
            >>> type(lor_codes_dat_cy)
            dict
            >>> list(lor_codes_dat_cy)
            ['CY', 'Notes', 'Last updated date']
            >>> lor_codes_dat_cy['CY']
                 Code  ...                       RA Note
            0   CY240  ...           Caerwent branch RA4
            1  CY1540  ...  Pembroke - Pembroke Dock RA6
            [2 rows x 5 columns]
            >>> lor_codes_dat = lor.fetch_codes()
            >>> type(lor_codes_dat)
            dict
            >>> list(lor_codes_dat.keys())
            ['LOR', 'Last updated date']
            >>> l_codes = lor_codes_dat['LOR']
            >>> type(l_codes)
            dict
            >>> list(l_codes.keys())[:5]
            ['CY', 'CY Notes', 'EA', 'EA Notes', 'GW']
            >>> cy_codes = l_codes['CY']
            >>> type(cy_codes)
            pandas.core.frame.DataFrame
            >>> cy_codes
                 Code  ...                       RA Note
            0   CY240  ...           Caerwent branch RA4
            1  CY1540  ...  Pembroke - Pembroke Dock RA6
            [2 rows x 5 columns]
            >>> xr_codes = l_codes['XR']
            >>> type(xr_codes)
            dict
            >>> list(xr_codes.keys())
            ['Current codes', 'Current codes note', 'Past codes', 'Past codes note']
            >>> xr_codes['Past codes']
                Code  ... RA Note
            0  XR001  ...
            1  XR002  ...
            [2 rows x 5 columns]
            >>> xr_codes['Current codes']
                Code  ...                     RA Note
            0  XR001  ...  Originally reported as RA4
            1  XR002  ...  Originally reported as RA4
            [2 rows x 5 columns]
        """

        if prefix:
            prefix_ = self.validate_prefix(prefix)
            args = {
                'data_name': prefix_.lower(),
                'method': self.collect_codes,
                'sub_dir': "prefixes",
                'prefix': prefix_,
            }
            kwargs.update(args)

            lor_data = self._fetch_data_from_file(
                update=update, dump_dir=dump_dir, verbose=verbose, **kwargs)

        else:
            prefixes = self.get_keys_to_prefixes(prefixes_only=True, verbose=verbose)

            # # Adjust prefixes list: replace 'NW' with 'NW/NZ' and remove 'NZ'
            # prefixes_ = ['NW/NZ' if p == 'NW' else p for p in prefixes if p != 'NZ']

            # Set verbosity based on conditions
            verbose_ = fetch_all_verbose(data_dir=dump_dir, verbose=verbose)

            # Fetch LOR codes
            lor_codes = [
                self.fetch_codes(prefix=p, update=update, verbose=verbose_, **kwargs)
                for p in prefixes]

            # Retry if all fetches failed
            if all(x is None for x in lor_codes):
                if update:
                    print_inst_conn_err(verbose=verbose)
                    print_void_msg(data_name=self.KEY.lower(), verbose=verbose)

                lor_codes = [
                    self.fetch_codes(prefix=p, update=False, verbose=verbose_)
                    for p in prefixes]

            # Process fetched data
            lor_data, last_updated_dates = {self.KEY: {}}, []

            for p, dat in zip(prefixes, lor_codes):
                last_updated_dates.append(dat.get(self.KEY_TO_LAST_UPDATED_DATE))
                remove_dict_keys(dat, self.KEY_TO_LAST_UPDATED_DATE)

                # Merge fetched data with optional renaming of "Notes" keys
                lor_data[self.KEY].update(
                    update_dict_keys(dat, replacements={'Notes': f'{p} Notes'}) if 'Notes' in dat
                    else dat)

            # Get the latest updated date
            latest_update_date = max(filter(None, last_updated_dates), default=None)
            lor_data.update({self.KEY_TO_LAST_UPDATED_DATE: latest_update_date})

        if dump_dir:
            self._save_data_to_file(
                data=lor_data, data_name=self.KEY, dump_dir=dump_dir, verbose=verbose)

        return lor_data

    # == ELR/LOR converter =========================================================================

    def _collect_elr_lor_converter(self, source, verbose=False):
        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

        thead, tbody = soup.find_all('thead')[0], soup.find_all('tbody')[0]
        ths = thead.find_all('th')
        trs = tbody.find_all(name='tr')

        elr_lor_dat = parse_tr(trs=trs, ths=ths, as_dataframe=True)

        elr_links = soup.find_all(name='td', string=re.compile(r'([A-Z]{3})(\d)?'))
        lor_links = soup.find_all(name='a', href=re.compile(r'pride([a-z]{2})\.shtm#'))

        # if len(elr_links) != len(elr_lor_dat):
        #     duplicates = elr_lor_dat[elr_lor_dat.duplicated(['ELR', 'LOR code'], keep=False)]
        #     for i in duplicates.index:
        #         if not duplicates['ELR'].loc[i].lower() in elr_links[i]:
        #             elr_links.insert(i, elr_links[i - 1])
        #         if not lor_links[i].endswith(duplicates['LOR code'].loc[i].lower()):
        #             lor_links.insert(i, lor_links[i - 1])

        elr_lor_dat['ELR_URL'] = [
            urllib.parse.urljoin(home_page_url(), x.a.get('href')) if x.a else None
            for x in elr_links]

        elr_lor_dat['LOR_URL'] = [
            urllib.parse.urljoin(home_page_url(), 'pride/' + x.get('href'))
            for x in lor_links]

        elr_lor_converter = {
            self.KEY_ELC: elr_lor_dat,
            self.KEY_TO_LAST_UPDATED_DATE: _get_last_updated_date(soup=soup)}

        if verbose in {True, 1}:
            print("Done.")

        self._save_data_to_file(
            data=elr_lor_converter, data_name=re.sub(r"[/ ]", "-", self.KEY_ELC), verbose=verbose)

        return elr_lor_converter

    def collect_elr_lor_converter(self, confirmation_required=True, verbose=False,
                                  raise_error=False):
        """
        Collects data of
        `ELR/LOR converter <http://www.railwaycodes.org.uk/pride/elrmapping.shtm>`_
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
        :return: A dictionary containing the data of ELR/LOR converter,
            or ``None`` if no data is collected.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.line_data import LOR  # from pyrcs import LOR
            >>> lor = LOR()
            >>> elr_lor_conv = lor.collect_elr_lor_converter()
            To collect data of ELR/LOR converter
            ? [No]|Yes: yes
            >>> type(elr_lor_conv)
            dict
            >>> list(elr_lor_conv.keys())
            ['ELR/LOR converter', 'Last updated date']
            >>> elr_loc_conv_data = elr_lor_conv['ELR/LOR converter']
            >>> type(elr_loc_conv_data)
            pandas.core.frame.DataFrame
            >>> elr_loc_conv_data.head()
                ELR  ...                                            LOR_URL
            0   AAV  ...  http://www.railwaycodes.org.uk/pride/pridesw.s...
            1   ABD  ...  http://www.railwaycodes.org.uk/pride/pridegw.s...
            2   ABE  ...  http://www.railwaycodes.org.uk/pride/prideln.s...
            3  ABE1  ...  http://www.railwaycodes.org.uk/pride/prideln.s...
            4  ABE2  ...  http://www.railwaycodes.org.uk/pride/prideln.s...
            [5 rows x 6 columns]
        """

        elr_lor_converter = self._collect_data_from_source(
            data_name=self.KEY_ELC, method=self._collect_elr_lor_converter,
            confirmation_required=confirmation_required, verbose=verbose, raise_error=raise_error)

        return elr_lor_converter

    def fetch_elr_lor_converter(self, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetches data of `ELR/LOR converter`_.

        .. _`ELR/LOR converter`: http://www.railwaycodes.org.uk/pride/elrmapping.shtm

        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the data of ELR/LOR converter.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.line_data import LOR  # from pyrcs import LOR
            >>> lor = LOR()
            >>> elr_lor_conv = lor.fetch_elr_lor_converter()
            >>> type(elr_lor_conv)
            dict
            >>> list(elr_lor_conv.keys())
            ['ELR/LOR converter', 'Last updated date']
            >>> elr_loc_conv_data = elr_lor_conv['ELR/LOR converter']
            >>> type(elr_loc_conv_data)
            pandas.core.frame.DataFrame
            >>> elr_loc_conv_data.head()
                ELR  ...                                            LOR_URL
            0   AAV  ...  http://www.railwaycodes.org.uk/pride/pridesw.s...
            1   ABD  ...  http://www.railwaycodes.org.uk/pride/pridegw.s...
            2   ABE  ...  http://www.railwaycodes.org.uk/pride/prideln.s...
            3  ABE1  ...  http://www.railwaycodes.org.uk/pride/prideln.s...
            4  ABE2  ...  http://www.railwaycodes.org.uk/pride/prideln.s...
            [5 rows x 6 columns]
        """

        args = {
            'data_name': re.sub(r"[/ ]", "-", self.KEY_ELC),
            'method': self.collect_elr_lor_converter,
        }
        kwargs.update(args)

        elr_lor_converter = self._fetch_data_from_file(
            update=update, dump_dir=dump_dir, verbose=verbose, **kwargs)

        return elr_lor_converter
