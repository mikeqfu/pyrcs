"""
Collecting `PRIDE/LOR <http://www.railwaycodes.org.uk/pride/pride0.shtm>`_ codes.
"""

import copy
import os
import re
import urllib.parse

import bs4
import pandas as pd
import requests
from pyhelpers.dir import cd, validate_input_data_dir
from pyhelpers.ops import confirmed, fake_requests_headers
from pyhelpers.store import load_pickle, save_pickle

from pyrcs.utils import cd_dat, get_catalogue, get_last_updated_date, homepage_url, \
    parse_tr


class LOR:
    """
    A class for collecting PRIDE/LOR codes.

    - PRIDE: Possession Resource Information Database
    - LOR: Line Of Route

    :param data_dir: name of data directory, defaults to ``None``
    :type data_dir: str or None
    :param update: whether to check on update and proceed to update the package data, 
        defaults to ``False``
    :type update: bool

    **Example**::

        >>> from pyrcs.line_data import LOR

        >>> lor = LOR()

        >>> print(lor.Name)
        Possession Resource Information Database (PRIDE)/Line Of Route (LOR) codes

        >>> print(lor.SourceURL)
        http://www.railwaycodes.org.uk/pride/pride0.shtm
    """

    def __init__(self, data_dir=None, update=False):
        """
        Constructor method.
        """
        self.Name = 'Possession Resource Information Database (PRIDE)/' \
                    'Line Of Route (LOR) codes'

        self.HomeURL = homepage_url()
        self.SourceURL = urllib.parse.urljoin(self.HomeURL, '/pride/pride0.shtm')

        self.Catalogue = get_catalogue(
            self.SourceURL, update=update, confirmation_required=False)

        self.Date = get_last_updated_date(self.SourceURL, parsed=True, as_date_type=False)

        self.Key = 'LOR'
        self.LUDKey = 'Last updated date'

        self.DataDir = validate_input_data_dir(data_dir) if data_dir \
            else cd_dat("line-data", self.Key.lower())

        self.CurrentDataDir = copy.copy(self.DataDir)

        self.PKey = 'Key to prefixes'
        self.ELCKey = 'ELR/LOR converter'

    def cdd_lor(self, *sub_dir, **kwargs):
        """
        Change directory to package data directory and sub-directories (and/or a file).

        The directory for this module: ``"\\dat\\line-data\\lor-codes"``.

        :param sub_dir: sub-directory or sub-directories (and/or a file)
        :type sub_dir: str
        :param kwargs: optional parameters of
            `os.makedirs <https://docs.python.org/3/library/os.html#os.makedirs>`_,
            e.g. ``mode=0o777``
        :return: path to the backup data directory for ``LOR``
        :rtype: str

        :meta private:
        """

        path = cd(self.DataDir, *sub_dir, mkdir=True, **kwargs)

        return path

    def get_keys_to_prefixes(self, prefixes_only=True, update=False, verbose=False):
        """
        Get key to LOR code prefixes.

        :param prefixes_only: whether to get only prefixes, defaults to ``True``
        :type prefixes_only: bool
        :param update: whether to check on update and proceed to update the package data, 
            defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console 
            as the function runs, defaults to ``False``
        :type verbose: bool
        :return: keys to LOR code prefixes
        :rtype: list, dict

        **Examples**::

            >>> from pyrcs.line_data import LOR

            >>> lor = LOR()

            >>> keys_to_prefixes_ = lor.get_keys_to_prefixes()

            >>> print(keys_to_prefixes_)
            ['CY', 'EA', 'GW', 'LN', 'MD', 'NW', 'NZ', 'SC', 'SO', 'SW', 'XR']

            >>> keys_to_prefixes_ = lor.get_keys_to_prefixes(prefixes_only=False)

            >>> type(keys_to_prefixes_)
            <class 'dict'>
            >>> print(keys_to_prefixes_['Key to prefixes'].head())
              Prefixes                                    Name
            0       CY                                   Wales
            1       EA         South Eastern: East Anglia area
            2       GW  Great Western (later known as Western)
            3       LN                  London & North Eastern
            4       MD       North West: former Midlands lines
        """

        path_to_pickle = self.cdd_lor("{}prefixes.pickle".format(
            "" if prefixes_only else "keys-to-"))

        if os.path.isfile(path_to_pickle) and not update:
            keys_to_prefixes = load_pickle(path_to_pickle)

        else:
            try:
                lor_pref = pd.read_html(self.SourceURL)[0].loc[:, [0, 2]]
                lor_pref.columns = ['Prefixes', 'Name']

                if prefixes_only:
                    keys_to_prefixes = lor_pref.Prefixes.tolist()
                else:
                    keys_to_prefixes = {self.PKey: lor_pref, self.LUDKey: self.Date}

                save_pickle(keys_to_prefixes, path_to_pickle, verbose=verbose)

            except Exception as e:
                print("Failed to get the keys to LOR prefixes. {}.".format(e))
                keys_to_prefixes = [] if prefixes_only \
                    else {self.PKey: None, self.LUDKey: None}

        return keys_to_prefixes

    def get_lor_page_urls(self, update=False, verbose=False):
        """
        Get URLs to LOR codes with different prefixes.

        :param update: whether to check on update and proceed to update the package data, 
            defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console 
            as the function runs, defaults to ``False``
        :type verbose: bool
        :return: a list of URLs of web pages hosting LOR codes for each prefix
        :rtype: list

        **Example**::

            >>> from pyrcs.line_data import LOR

            >>> lor = LOR()

            >>> lor_page_urls_ = lor.get_lor_page_urls()
            >>> print(lor_page_urls_[:2])
            ['http://www.railwaycodes.org.uk/pride/pridecy.shtm',
             'http://www.railwaycodes.org.uk/pride/prideea.shtm']
        """

        path_to_pickle = self.cdd_lor("prefix-page-urls.pickle")
        if os.path.isfile(path_to_pickle) and not update:
            lor_page_urls = load_pickle(path_to_pickle)

        else:
            try:
                source = requests.get(self.SourceURL, headers=fake_requests_headers())
                soup = bs4.BeautifulSoup(source.text, 'lxml')

                links = soup.find_all('a', href=re.compile('^pride|elrmapping'),
                                      text=re.compile('.*(codes|converter|Historical)'))

                lor_page_urls = list(dict.fromkeys(
                    [self.SourceURL.replace(os.path.basename(self.SourceURL), x['href'])
                     for x in links]))

                save_pickle(lor_page_urls, path_to_pickle, verbose=verbose)

            except Exception as e:
                print("Failed to get the URLs to LOR codes web pages. {}.".format(e))
                lor_page_urls = []

        return lor_page_urls

    def update_catalogue(self, confirmation_required=True, verbose=False):
        """
        Update catalogue data including keys to prefixes and LOR page URLs.

        :param confirmation_required: whether to require users to confirm and proceed, 
            defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console 
            as the function runs, defaults to ``False``
        :type verbose: bool

        :meta private:
        """

        if confirmed("To update catalogue? ", confirmation_required=confirmation_required):
            self.get_keys_to_prefixes(prefixes_only=True, update=True, verbose=verbose)
            self.get_keys_to_prefixes(prefixes_only=False, update=True, verbose=verbose)
            self.get_lor_page_urls(update=True, verbose=verbose)

    def collect_lor_codes_by_prefix(self, prefix, update=False, verbose=False):
        """
        Collect LOR codes by a given prefix. 

        :param prefix: prefix of LOR codes
        :type prefix: str
        :param update: whether to check on update and proceed to update the package data, 
            defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console 
            as the function runs, defaults to ``False``
        :type verbose: bool
        :return: LOR codes for the given ``prefix``
        :rtype: dict or None

        **Examples**::

            >>> from pyrcs.line_data import LOR

            >>> lor = LOR()

            >>> lor_codes_cy = lor.collect_lor_codes_by_prefix(prefix='CY')

            >>> type(lor_codes_cy)
            <class 'dict'>
            >>> print(list(lor_codes_cy.keys()))
            ['CY', 'Notes', 'Last updated date']
            >>> type(lor_codes_cy['CY'])
            <class 'pandas.core.frame.DataFrame'>

            >>> lor_codes_nw = lor.collect_lor_codes_by_prefix(prefix='NW')
            >>> print(list(lor_codes_nw.keys()))
            ['NW/NZ', 'Notes', 'Last updated date']

            >>> lor_codes_ea = lor.collect_lor_codes_by_prefix(prefix='EA')
            >>> ea_dat = lor_codes_ea['EA']
            >>> type(ea_dat)
            <class 'dict'>
            >>> print(ea_dat['Current system']['EA'].head())
                 Code  ...                             Line Name Note
            0  EA1000  ...                                       None
            1  EA1010  ...                                       None
            2  EA1011  ...                                       None
            3  EA1012  ...                                       None
            4  EA1013  ...  Replaced by new EA1013 from 19 April 2014

            [5 rows x 5 columns]
        """

        available_prefixes = self.get_keys_to_prefixes(prefixes_only=True)
        assert prefix in available_prefixes, "`prefix` must be one of {}".format(
            ", ".join(available_prefixes))

        pickle_filename = "{}.pickle".format(
            "nw-nz" if prefix.upper() in ("NW", "NZ") else prefix.lower())
        path_to_pickle = self.cdd_lor("prefixes", pickle_filename)

        if os.path.isfile(path_to_pickle) and not update:
            lor_codes_by_initials = load_pickle(path_to_pickle)

        else:
            if verbose == 2:
                print("To collect LOR codes for the prefix \"{}\". ".format(
                    prefix.upper()), end=" ... ")

            try:
                if prefix in ("NW", "NZ"):
                    url = self.HomeURL + '/pride/pridenw.shtm'
                    prefix = "NW/NZ"
                else:
                    url = self.HomeURL + '/pride/pride{}.shtm'.format(prefix.lower())
                source = requests.get(url, headers=fake_requests_headers())
                source_text = source.text
                source.close()

                soup = bs4.BeautifulSoup(source_text, 'lxml')

                # Parse the column of Line Name
                def parse_line_name(x):
                    # re.search('\w+.*(?= \(\[\')', x).group()
                    # re.search('(?<=\(\[\')\w+.*(?=\')', x).group()
                    try:
                        line_name, line_name_note = x.split(' ([\'')
                        line_name_note = line_name_note.strip('\'])')
                    except ValueError:
                        line_name, line_name_note = x, None
                    return line_name, line_name_note

                def parse_h3_table(tbl_soup):
                    header, code = tbl_soup
                    header_text = [
                        h.text.replace('\n', ' ') for h in header.find_all('th')]
                    code_dat = pd.DataFrame(
                        parse_tr(header_text, code.find_all('tr')), columns=header_text)
                    line_name_info = \
                        code_dat['Line Name'].map(parse_line_name).apply(pd.Series)
                    line_name_info.columns = ['Line Name', 'Line Name Note']
                    code_dat = pd.concat([code_dat, line_name_info], axis=1, sort=False)
                    try:
                        note_dat = dict(
                            [(x['id'].title(), x.text.replace('\xa0', ''))
                             for x in soup.find('ol').findChildren('a')])
                    except AttributeError:
                        note_dat = dict([('Note', None)])
                    return code_dat, note_dat

                h3, table_soup = soup.find_all('h3'), soup.find_all('table')
                if len(h3) == 0:
                    code_data, code_data_notes = parse_h3_table(table_soup)
                    lor_codes_by_initials = {prefix: code_data, 'Notes': code_data_notes}
                else:
                    code_data_and_notes = [dict(zip([prefix, 'Notes'], parse_h3_table(x)))
                                           for x in zip(*[iter(table_soup)] * 2)]
                    lor_codes_by_initials = {
                        prefix: dict(zip([x.text for x in h3], code_data_and_notes))}

                last_updated_date = get_last_updated_date(url)
                lor_codes_by_initials.update({self.LUDKey: last_updated_date})

                print("Done. ") if verbose == 2 else ""

                save_pickle(lor_codes_by_initials, path_to_pickle, verbose=verbose)

            except Exception as e:
                print("Failed. {}".format(prefix.upper(), e))
                lor_codes_by_initials = None

        return lor_codes_by_initials

    def fetch_lor_codes(self, update=False, pickle_it=False, data_dir=None,
                        verbose=False):
        """
        Fetch LOR codes from local backup.

        :param update: whether to check on update and proceed to update the package data, 
            defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data
            with newly collected data, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console 
            as the function runs, defaults to ``False``
        :type verbose: bool
        :return: LOR codes
        :rtype: dict

        **Example**::

            >>> from pyrcs.line_data import LOR

            >>> lor = LOR()

            >>> lor_codes_dat = lor.fetch_lor_codes()

            >>> type(lor_codes_dat)
            <class 'dict'>
            >>> type(lor_codes_dat['LOR'])
            <class 'dict'>
            >>> print(list(lor_codes_dat['LOR'].keys()))
            ['CY', 'EA', 'GW', 'LN', 'MD', 'NW/NZ', 'SC', 'SO', 'SW', 'XR']

            >>> type(lor_codes_dat['LOR']['CY'])
            <class 'dict'>
        """

        prefixes = self.get_keys_to_prefixes(prefixes_only=True, update=update, verbose=verbose)
        lor_codes = [self.collect_lor_codes_by_prefix(p, update, verbose) for p in prefixes if p != 'NZ']

        prefixes[prefixes.index('NW')] = 'NW/NZ'
        prefixes.remove('NZ')

        lor_codes_data = {self.Key: dict(zip(prefixes, lor_codes))}

        # Get the latest updated date
        last_updated_dates = (item[self.LUDKey] for item, _ in zip(lor_codes, prefixes))
        latest_update_date = max(d for d in last_updated_dates if d is not None)

        lor_codes_data.update({self.LUDKey: latest_update_date})

        if pickle_it and data_dir:
            pickle_filename = "lor-codes.pickle"
            self.CurrentDataDir = validate_input_data_dir(data_dir)
            path_to_pickle = os.path.join(self.CurrentDataDir, pickle_filename)
            save_pickle(lor_codes_data, path_to_pickle, verbose=verbose)

        return lor_codes_data

    def collect_elr_lor_converter(self, confirmation_required=True, verbose=False):
        """
        Collect ELR/LOR converter from source web page.

        :param confirmation_required: whether to require users to confirm and proceed, 
            defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console 
            as the function runs, defaults to ``False``
        :type verbose: bool
        :return: data of ELR/LOR converter
        :rtype: dict or None

        **Example**::

            >>> from pyrcs.line_data import LOR

            >>> lor = LOR()

            >>> elr_lor_converter_ = lor.collect_elr_lor_converter()
            To collect data of ELR/LOR converter? [No]|Yes: yes

            >>> type(elr_lor_converter_)
            <class 'dict'>
            >>> print(elr_lor_converter_['ELR/LOR converter'].head())
                ELR  ...                                            LOR_URL
            0   AAV  ...  http://www.railwaycodes.org.uk/pride/pridesw.s...
            1   ABD  ...  http://www.railwaycodes.org.uk/pride/pridegw.s...
            2   ABE  ...  http://www.railwaycodes.org.uk/pride/prideln.s...
            3  ABE1  ...  http://www.railwaycodes.org.uk/pride/prideln.s...
            4  ABE2  ...  http://www.railwaycodes.org.uk/pride/prideln.s...

            [5 rows x 6 columns]
        """

        if confirmed("To collect data of {}?".format(self.ELCKey),
                     confirmation_required=confirmation_required):

            url = self.Catalogue[self.ELCKey]

            if verbose == 2:
                print("Collecting data of {}".format(self.ELCKey), end=" ... ")

            try:
                headers, elr_lor_dat = pd.read_html(url)
                elr_lor_dat.columns = list(headers)
                #
                source = requests.get(url, headers=fake_requests_headers())
                soup = bs4.BeautifulSoup(source.text, 'lxml')
                tds = soup.find_all('td')
                links = [x.get('href') for x in [x.find('a', href=True) for x in tds]
                         if x is not None]
                elr_links, lor_links = [x for x in links[::2]], [x for x in links[1::2]]
                #
                if len(elr_links) != len(elr_lor_dat):
                    duplicates = elr_lor_dat[elr_lor_dat.duplicated(['ELR', 'LOR code'],
                                                                    keep=False)]
                    for i in duplicates.index:
                        if not duplicates['ELR'].loc[i].lower() in elr_links[i]:
                            elr_links.insert(i, elr_links[i - 1])
                        if not lor_links[i].endswith(
                                duplicates['LOR code'].loc[i].lower()):
                            lor_links.insert(i, lor_links[i - 1])
                #
                elr_lor_dat['ELR_URL'] = [
                    urllib.parse.urljoin(self.HomeURL, x) for x in elr_links]
                elr_lor_dat['LOR_URL'] = [
                    self.HomeURL + 'pride/' + x for x in lor_links]
                #
                elr_lor_converter = {self.ELCKey: elr_lor_dat,
                                     self.LUDKey: get_last_updated_date(url)}

                print("Done. ") if verbose == 2 else ""

                pickle_filename = re.sub(r"[/ ]", "-", self.ELCKey.lower()) + ".pickle"
                save_pickle(elr_lor_converter, self.cdd_lor(pickle_filename),
                            verbose=verbose)

            except Exception as e:
                print("Failed. {}".format(e))
                elr_lor_converter = None

            return elr_lor_converter

    def fetch_elr_lor_converter(self, update=False, pickle_it=False, data_dir=None,
                                verbose=False):
        """
        Fetch ELR/LOR converter from local backup.

        :param update: whether to check on update and proceed to update the package data, 
            defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data
            with newly collected data, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console 
            as the function runs, defaults to ``False``
        :type verbose: bool
        :return: data of ELR/LOR converter
        :rtype: dict

        **Example**::

            >>> from pyrcs.line_data import LOR

            >>> lor = LOR()

            >>> elr_lor_converter_ = lor.fetch_elr_lor_converter()

            >>> type(elr_lor_converter_)
            <class 'dict'>
            >>> for col in elr_lor_converter_['ELR/LOR converter'].columns:
            ...     print(col)
            ELR
            Miles from
            Miles to
            LOR code
            ELR_URL
            LOR_URL
        """

        pickle_filename = re.sub(r"[/ ]", "-", self.ELCKey.lower()) + ".pickle"
        path_to_pickle = self.cdd_lor(pickle_filename)

        if os.path.isfile(path_to_pickle) and not update:
            elr_lor_converter = load_pickle(path_to_pickle)

        else:
            elr_lor_converter = self.collect_elr_lor_converter(
                confirmation_required=False,
                verbose=False if data_dir or not verbose else True)

            if elr_lor_converter:  # codes_for_ole is not None
                if pickle_it and data_dir:
                    self.CurrentDataDir = validate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, pickle_filename)
                    save_pickle(elr_lor_converter, path_to_pickle, verbose=verbose)
            else:
                print("No data of {} has been collected.".format(self.ELCKey))

        return elr_lor_converter
