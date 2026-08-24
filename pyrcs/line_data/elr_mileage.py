"""
Collect data of
`Engineer's Line References (ELRs) <http://www.railwaycodes.org.uk/elrs/elr0.shtm>`_.
"""

import functools
import itertools
import os
import re
import string
import urllib.parse

import bs4
import numpy as np
import pandas as pd
import requests
from pyhelpers._cache import _print_failure_message
from pyhelpers.ops import confirmed, fake_requests_headers, loop_in_pairs
from pyhelpers.store import load_data
from pyhelpers.text import remove_punctuation

from .._base import _Base
from ..converter import kilometer_to_yard, mile_chain_to_mileage, mileage_to_mile_chain, \
    yard_to_mileage
from ..parser import _get_last_updated_date, parse_table
from ..utils import get_collect_verbosity_for_fetch, handle_connection_error, homepage_url, \
    is_homepage_connectable, is_str_float, print_void_collection_message, validate_initial


def _parse_non_float_str_mileage(mileage):
    """
    Parse non-float mileage strings into structured numeric values and associated notes.

    This function processes abnormal or heavily annotated railway mileage strings (typically
    representing miles and chains) into a standardised format alongside descriptive footnotes.

    :param mileage: A collection of raw, unformatted mileage strings.
    :type mileage: pandas.Series | list | tuple
    :return: A tuple containing two lists: the cleaned ``miles_chains`` values and
        the parsed ``mileage_note`` annotations.
    :rtype: tuple[list, list]
    """

    miles_chains, mileage_note = [], []

    for m_ in mileage:
        m = m_.strip()

        if not m:  # e.g. m == '':
            miles_chains.append('')
            mileage_note.append('')

        elif m.startswith('(') and m.endswith(')'):
            match = re.search(r'\d+\.\d+', m)
            miles_chains.append(match.group(0) if match else m)
            mileage_note.append('Not on this route but given for reference')

        elif m.startswith('≈') or m.endswith('?'):
            miles_chains.append(m.strip('≈?'))
            mileage_note.append('Approximate')

        elif re.match(r'\d+\.\d+/\s?\d+\.\d+', m):
            m1, m2 = map(str.strip, m.split('/'))
            miles_chains.append(m1)
            mileage_note.append(f'{m2} (Alternative)')

        elif ' + ' in m or 'private portion' in m:
            match = re.search(r'\d+\.\d+', m)
            if match:
                m1 = match.group(0)
                miles_chains.append(m1)
                mileage_note.append(m.replace(m1, '').strip())
            else:
                miles_chains.append(m)
                mileage_note.append('')

        elif '†' in m:
            miles_chains.append(m.replace('†', '').strip())
            mileage_note.append("(See 'Notes')")

        else:  # Convert "1,234" → "1.234", and "1 234" → "1.234"
            miles_chains.append(re.sub(r'[ ,]', '.', m))
            mileage_note.append('')

    return miles_chains, mileage_note


def _parse_mileages(mileages):
    """
    Parses a column of mileage data.

    The function handles different formats, such as km, mile chains and special notations.

    :param mileages: Column of mileage data.
    :type mileages: pandas.Series
    :return: Parsed mileage data.
    :rtype: pandas.DataFrame
    """

    mileage = mileages.reset_index(drop=True)

    if mileage.str.contains('km', regex=True).any():  # any(mileage.str.match('.*km')):
        if mileage.str.endswith('km').all():  # all(mileage.str.match('.*km')):
            mileage_ = mileage.str.replace(r'km|\(|\)', '', regex=True).map(
                lambda x: yard_to_mileage(kilometer_to_yard(km=x.replace('≈', ''))))
            miles_chains = mileage_.map(mileage_to_mile_chain)  # Warning: Might contain issues!

        else:
            # miles_chains = mileage.str.replace(r'/?\d+\.\d+km/?', '', regex=True)
            miles_chains = mileage.where(~mileage.str.contains('km', na=False), '')
            mileage_ = miles_chains.map(mile_chain_to_mileage)
            mileage = mileage.where(mileage.str.contains('km', na=False), '')

        # mileage_note = [x + ' (Approximate)' if x.startswith('≈') else x for x in list(mileage)]
        mileage_note = mileage.map(lambda x: f"{x} (Approximate)" if x.startswith('≈') else x)

    else:
        if mileage.map(is_str_float).all():  # all(mileage.map(is_str_float)):
            miles_chains = mileage
            mileage_note = [''] * len(miles_chains)

        else:
            miles_chains, mileage_note = _parse_non_float_str_mileage(mileage)

        mileage_ = [mile_chain_to_mileage(m) for m in miles_chains]

    parsed_mileage_ = {
        'Mileage': mileage_,
        'Mileage_Note': mileage_note,
        'Miles_Chains': miles_chains,
    }
    parsed_mileage = pd.DataFrame(parsed_mileage_)

    return parsed_mileage


def _parse_node(node):
    pat = re.compile(r'\w+.*( \(\d+\.\d+\))?(/| and \w+)? with ([A-Z]).*(\d)?( \(\d+\.\d+\))?')

    if re.match(pat, node):
        node_name = [x.group() for x in re.finditer(r'\w+.*(?= with)', node)]
        conn_node = [x.group() for x in re.finditer(r'(?<= with )[^*]+', node)]

    else:
        node_name, conn_node = [node], [None]

    return node_name + conn_node


def _parse_node_connection(prep_nodes, col_name='Connection'):
    conn_node_lst = []

    for n in prep_nodes[col_name].values:
        if not n or pd.isna(n):
            conn_node_lst.append([None])
            continue

        if re.match(r'[A-Z]{3}\d?( \(\d+\.\d+\))? ?/ ?[A-Z]{3}\d?( \(\d+\.\d+\))?', n):
            m = [x.strip() for x in n.split('/')]
        else:
            m = n.split(' and ')

        if len(m) > 2:
            m = [' and '.join(m[:2]), ' and '.join(m[2:])]

        # Flattening nested structures
        m = [x.replace('later ', '').rstrip(',') for x in m]
        m = sum([x.split(' and ') for x in m], [])
        m = sum([x.split(', ') for x in m], [])

        conn_node_lst.append(m)

    # Determine the maximum number of connections
    max_conn = max(map(len, conn_node_lst))

    # Create DataFrame with dynamic column names
    nodes_ = pd.DataFrame(conn_node_lst, columns=[f'Link_{i + 1}' for i in range(max_conn)])

    return nodes_


def _uncouple_elr_mileage(node_x):
    """
    Split a raw node string into its ELR and numeric mileage components.

    This function parses composite identifiers such as ``"ECM5 (44.64)"`` or ``"DNT"`` into a
    two-element list containing the isolated Engineer's Line Reference (ELR) and the mileage.
    If the mileage is in kilometres, it is automatically converted to miles and chains.

    :param node_x: The raw node string containing ELR and/or mileage info.
    :type node_x: str | float | None
    :return: A list of two elements where the first is the ELR (up to 4 characters)
        and the second is the mileage.
    :rtype: list[str]
    """

    # e.g. x = 'ECM5 (44.64)' or x = 'DNT'
    if not node_x or pd.isna(node_x):
        return ['', '']

    node_str = str(node_x).strip()

    # Compile regex patterns
    pat1 = re.compile(r'([A-Z]{3}(\d)?$)|((\w\s?)*\w$)')
    pat2 = re.compile(r'([A-Z]{3}(\d)?$)|(([\w\s&]?)*(\s\(\d+\.\d+\))?$)')
    pat3 = re.compile(r'[A-Z]{3}(\d)?(\s\(\d+.\d+\))?\s\[.*?]$')
    pat4 = re.compile(r'[A-Z]{3}(\d)?\s\(\d+\.\d+km\)')

    if pat1.match(node_str):
        result = [node_x, '']

    elif pat2.match(node_str):
        parts = node_str.split('(')
        y = [part[:-1] if part.endswith(')') else part.strip() for part in parts]
        if len(y) < 2:
            y.append('')
        y[0] = '' if len(y[0]) > 4 else y[0]
        result = y[:2]

    elif pat3.match(node_str):
        elr_match = re.search(r'[A-Z]{3}(\d)?', node_str)
        mileage_match = re.search(r'\d+\.\d+', node_str)

        elr = elr_match.group(0) if elr_match else ''
        mileage = mileage_match.group(0) if mileage_match else ''
        result = [elr, mileage]

    elif pat4.match(node_str):
        elr_match = re.search(r'[A-Z]{3}(\d)?', node_str)
        km_match = re.search(r'\d+\.\d+', node_str)

        elr = elr_match.group(0) if elr_match else ''
        if km_match:
            miles_chains = mileage_to_mile_chain(
                yard_to_mileage(kilometer_to_yard(km=km_match.group(0)))
            )
        else:
            miles_chains = ''
        result = [elr, miles_chains]
    else:
        result = [node_str, ''] if len(node_str) <= 4 else ['', '']

    # Safeguard: ensure the ELR code does not exceed 4 characters
    result[0] = result[0] if len(result[0]) <= 4 else ''

    return result


def _parse_nodes(nodes):
    """
    Parse column of node data.

    :param nodes: column of nodes data
    :type nodes: pandas.Series
    :return: parsed nodes
    :rtype: pandas.DataFrame
    """

    prep_nodes = pd.DataFrame((_parse_node(node) for node in nodes), columns=['Node', 'Connection'])

    conn_nodes = _parse_node_connection(prep_nodes=prep_nodes, col_name='Connection')

    link_cols = [x for x in conn_nodes.columns if re.match(r'^(Link_\d)', x)]
    link_nodes = conn_nodes[link_cols].map(_uncouple_elr_mileage)

    dat = [
        pd.DataFrame(
            link_nodes[col].values.tolist(), columns=[col + '_ELR', col + '_Mile_Chain'])
        for col in link_cols]
    link_elr_mileage = pd.concat(dat, axis=1, sort=False)

    parsed_node_and_conn = pd.concat([prep_nodes, conn_nodes, link_elr_mileage], axis=1).fillna('')

    return parsed_node_and_conn


def _parse_mileage_data(mileage_data):
    """
    Parse scraped data of mileage file.

    :param mileage_data: preprocessed data of mileage file scraped from source web page
    :type mileage_data: pandas.DataFrame
    :return: parsed data of mileage file
    :rtype: pandas.DataFrame
    """

    mileages, nodes = mileage_data.iloc[:, 0], mileage_data.iloc[:, 1]

    parsed_mileages = _parse_mileages(mileages=mileages)
    parsed_nodes_and_connections = _parse_nodes(nodes=nodes)

    parsed_dat = pd.concat([parsed_mileages, parsed_nodes_and_connections], axis=1)

    return parsed_dat


class ELRMileages(_Base):
    """
    A class for collecting data of
    `Engineer's Line References (ELRs) <http://www.railwaycodes.org.uk/elrs/elr0.shtm>`_.

    This class provides methods to access and manage ELR data, including their mileages
    and last updated information.
    """

    #: The name of the data.
    NAME: str = "Engineer's Line References (ELRs)"
    #: The key for accessing the data.
    KEY: str = 'ELRs and mileages'

    #: The URL of the main web page for the data.
    URL: str = urllib.parse.urljoin(homepage_url(), '/elrs/elr0.shtm')

    #: The key used to reference the last updated date in the data.
    KEY_TO_LAST_UPDATED_DATE: str = 'Last updated date'

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
        :ivar list measure_headers: A list of potential headers for various measures in the data.

        **Examples**::

            >>> from pyrcs.line_data import ELRMileages  # from pyrcs import ELRMileages
            >>> em = ELRMileages()
            >>> em.NAME
            "Engineer's Line References (ELRs)"
            >>> em.URL
            'http://www.railwaycodes.org.uk/elrs/elr0.shtm'
        """

        super().__init__(
            data_dir=data_dir, content_type='catalogue', data_category="line-data", update=update,
            verbose=verbose)

        self.measure_headers = [' '.join(x) for x in itertools.product(
            *(('Current', 'Later', 'Earlier', 'One', 'Original', 'Former', 'Alternative', 'Usual',
               'New', 'Old'),
              ('measure', 'route', 'diversion')))]

    def _collect_elr(self, initial, source, verbose=False):
        initial_ = validate_initial(initial=initial)

        # Create a DataFrame of the requested table
        (columns, records), soup = parse_table(source=source)
        data_ = [[x.replace('=', 'See').strip('\xa0') for x in i] for i in records]
        elrs_codes = pd.DataFrame(data=data_, columns=columns)

        elrs_codes[columns[0]] = elrs_codes[columns[0]].map(lambda x: x.split(' ')[0])

        # Get last update date
        last_updated_date = _get_last_updated_date(soup=soup, parsed=True)

        # Update the dict with both the DataFrame and its last updated date
        data = {initial_: elrs_codes, self.KEY_TO_LAST_UPDATED_DATE: last_updated_date}

        if verbose in {True, 1}:
            print("Done.")

        self._save_data_to_file(data=data, data_name=initial_, sub_dir="a-z", verbose=verbose)

        return data

    def collect_elr(self, initial, confirmation_required=True, verbose=False, raise_error=False):
        """
        Collects Engineer's Line References (ELRs) that begin with a specified initial letter
        from the source web page.

        :param initial: The initial letter (e.g. ``'a'``, ``'z'``) of an ELR.
        :type initial: str
        :param confirmation_required: Whether user confirmation is required;
            if ``confirmation_required=True`` (default), prompts the user for confirmation
            before proceeding with data collection.
        :type confirmation_required: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``True``.
        :type verbose: bool | int
        :param raise_error: Whether to raise the provided exception;
            if ``raise_error=False`` (default), the error will be suppressed.
        :type raise_error: bool
        :return: A dictionary containing ELR data whose names start with the given initial letter,
            along with the date of the last update.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.line_data import ELRMileages  # from pyrcs import ELRMileages
            >>> em = ELRMileages()
            >>> elrs_a_codes = em.collect_elr(initial='a')
            >>> type(elrs_a_codes)
            dict
            >>> list(elrs_a_codes.keys())
            ['A', 'Last updated date']
            >>> elrs_a_codes_dat = elrs_a_codes['A']
            >>> type(elrs_a_codes_dat)
            pandas.core.frame.DataFrame
            >>> elrs_a_codes_dat.head()
               ELR  ...         Notes
            0  AAL  ...      Now NAJ3
            1  AAM  ...  Formerly AML
            2  AAV  ...
            3  ABB  ...       Now AHB
            4  ABB  ...
            [5 rows x 5 columns]
            >>> elrs_q_codes = em.collect_elr(initial='Q')
            >>> elrs_q_codes_dat = elrs_q_codes['Q']
            >>> elrs_q_codes_dat.head()
                ELR  ...            Notes
            0   QAB  ...  Duplicates ALB?
            1   QBL  ...
            2   QDS  ...
            3   QLT  ...
            4  QLT1  ...
            [5 rows x 5 columns]
        """

        initial_ = validate_initial(initial=initial)

        data = self._collect_data_from_source(
            data_name=self.NAME, method=self._collect_elr, initial=initial_,
            confirmation_required=confirmation_required, verbose=verbose, raise_error=raise_error)

        return data

    def fetch_elr(self, initial=None, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetches data of ELRs and their associated mileages.

        :param initial: The initial letter (e.g. ``'a'``, ``'z'``) of an ELR; defaults to ``None``.
        :type initial: str | None
        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: Path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing data for all available ELRs,
            along with the date of the last update.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.line_data import ELRMileages  # from pyrcs import ELRMileages
            >>> em = ELRMileages()
            >>> elrs_codes = em.fetch_elr()
            >>> type(elrs_codes)
            dict
            >>> list(elrs_codes.keys())
            ['ELRs and mileages', 'Last updated date']
            >>> em.KEY
            'ELRs and mileages'
            >>> elrs_codes_dat = elrs_codes[em.KEY]
            >>> type(elrs_codes_dat)
            pandas.core.frame.DataFrame
            >>> elrs_codes_dat.head()
               ELR  ...         Notes
            0  AAL  ...      Now NAJ3
            1  AAM  ...  Formerly AML
            2  AAV  ...
            3  ABB  ...       Now AHB
            4  ABB  ...
            [5 rows x 5 columns]
        """

        if initial:
            args = {
                'data_name': validate_initial(initial),
                'method': self.collect_elr,
                'sub_dir': "a-z",
                'initial': initial,
            }
            kwargs.update(args)

            data = self._fetch_data_from_file(
                update=update, dump_dir=dump_dir, verbose=verbose, **kwargs)

        else:
            verbose_1 = False if (dump_dir or not verbose) else (2 if verbose == 2 else True)
            verbose_2 = verbose_1 if is_homepage_connectable() else False

            dat_list = [
                self.fetch_elr(initial=x, update=update, verbose=verbose_2)
                for x in string.ascii_lowercase]

            if all(d[x] is None for d, x in zip(dat_list, string.ascii_uppercase)):
                if update:
                    handle_connection_error(verbose=verbose)
                    print_void_collection_message(data_name=self.KEY, verbose=verbose)
                dat_list = [
                    self.fetch_elr(initial=x, update=False, verbose=verbose_1)
                    for x in string.ascii_lowercase]

            # Select DataFrames only
            data_ = pd.concat(
                (item[x] for item, x in zip(dat_list, string.ascii_uppercase)), axis=0,
                ignore_index=True, sort=False)

            # Get the latest updated date
            last_updated_dates = (
                item[self.KEY_TO_LAST_UPDATED_DATE]
                for item, _ in zip(dat_list, string.ascii_uppercase))
            latest_update_date = max(d for d in last_updated_dates if d is not None)

            data = {self.KEY: data_, self.KEY_TO_LAST_UPDATED_DATE: latest_update_date}

            if dump_dir:
                self._save_data_to_file(
                    data=data, data_name=self.NAME, dump_dir=dump_dir, verbose=verbose)

        return data

    def _save_mileage_file(self, mileage_file, dump_dir=None, verbose=False):
        """
        Save the collected mileage file data to a persistent file.

        This method serialises and writes railway mileage data into a picklable format.

        :param mileage_file: Data of the mileage file containing an ``"ELR"`` key.
        :type mileage_file: dict
        :param dump_dir: The directory path where the mileage file is saved.
            If ``False``, the saving process is bypassed. Defaults to ``None``.
        :type dump_dir: str | os.PathLike | bool | None
        :param verbose: Whether to print progress details to the console. Defaults to ``False``.
        :type verbose: bool | int
        :return: ``None`` if saving is bypassed or completed successfully.
        :rtype: None
        """

        if dump_dir is False:
            return None

        data_name = mileage_file['ELR'].lower()
        data_name += ("_" if data_name == "prn" else "")

        if dump_dir is None:
            sub_dir = data_name[0]
            target_dir = self._cdd("mileage-files", sub_dir)
        else:
            target_dir = dump_dir

        self._save_data_to_file(
            data=mileage_file,
            data_name=data_name,
            ext=".pkl",
            dump_dir=target_dir,
            verbose=verbose
        )

        return None

    def _handle_err404(self, elr, notes_dat, parsed, dump_dir=False, verbose=False):
        """
        Handle 404 resource errors by attempting to resolve alternative ELR codes.

        When a mileage page cannot be located directly, this method parses the error or
        index notes to identify alternative (formerly or currently active) ELR codes,
        fetches their datasets, and serialises the cross-referenced mappings.

        :param elr: The original Engineer's Line Reference (ELR) code that triggered the 404.
        :type elr: str
        :param notes_dat: The raw text string containing redirected or historical notes.
        :type notes_dat: str
        :param parsed: The pre-compiled dictionary or cache of parsed HTML documents.
        :type parsed: dict
        :param dump_dir: The directory path where resolved mileage files are saved.
            Defaults to ``False``.
        :type dump_dir: str | os.PathLike | bool
        :param verbose: Whether to print status information to the console. Defaults to ``False``.
        :type verbose: bool | int
        :return: The resolved alternative mileage file data dictionary, or ``None`` if
            the alternative ELR could not be extracted.
        :rtype: dict | None
        """

        match = re.search(r'(?<= )[A-Z]{3}(\d)?', notes_dat)
        if not match:
            if verbose in {True, 1}:
                print(f"Warning: Could not extract an alternative ELR from note: '{notes_dat}'")
            return None

        elr_alt = match.group(0)

        mileage_file_alt = self.collect_mileage_file(
            elr=elr_alt,
            parsed=parsed,
            confirmation_required=False,
            dump_dir=False,
            verbose=verbose
        )

        if notes_dat.startswith('Now') and isinstance(mileage_file_alt, dict):
            mileage_file_former = mileage_file_alt.copy()

            mileage_file_alt.update({'Formerly': elr})
            self._save_mileage_file(
                mileage_file=mileage_file_alt,
                dump_dir=dump_dir,
                verbose=verbose
            )

            mileage_file_former.update({'ELR': elr, 'Now': elr_alt})
            self._save_mileage_file(
                mileage_file=mileage_file_former,
                dump_dir=dump_dir,
                verbose=verbose
            )

        return mileage_file_alt

    @staticmethod
    def _parse_line_details(elr_dat, notes):
        """
        Parse ELR record details to extract the line name and mileage locations.

        This method processes string descriptions using regular expressions to extract
        geographic termini and map them to their corresponding mileage bounds.

        :param elr_dat: A single-row DataFrame containing ``'Line name'``, ``'Mileages'``,
            and ``'Datum'`` columns.
        :type elr_dat: pandas.DataFrame
        :param notes: Explanatory notes that may detail route variations or boundaries.
        :type notes: str
        :return: A tuple of the cleaned line name and a list mapping mileages to locations.
        :rtype: tuple[str, list[list[str]]]
        """

        val_cols = ['Line name', 'Mileages', 'Datum']
        row_values = elr_dat[val_cols].values[0]

        line_name = str(row_values[0]).strip()
        mileages = str(row_values[1]).strip()
        datum = str(row_values[2]).strip()
        notes_str = str(notes).strip() if notes else ''

        # Non-capturing group prevents the separator itself from appearing in the split list
        pat = re.compile(r' (?:and|&|to|-) ')

        def _split_locs(text):
            """Safely split text into exactly two locations."""
            txt_parts = pat.split(text)
            if len(txt_parts) == 2:
                return txt_parts[0].strip(), txt_parts[1].strip()
            raise ValueError("String does not contain exactly one separator.")

        loc_a, loc_b = '', ''

        if re.match(r'(\w ?)+ \((\w ?)+\)', line_name):
            # Extract text inside and outside parentheses
            inner_match = re.search(r'\(([^)]+)\)', line_name)
            outer_match = re.search(r'^(.*?)\s*\(', line_name)

            line_name_inner = inner_match.group(1).strip() if inner_match else ''
            line_name_outer = outer_match.group(1).strip() if outer_match else line_name

            try:
                loc_a, loc_b = _split_locs(line_name_inner)
                line_name = line_name_outer
            except ValueError:
                try:
                    loc_a, loc_b = _split_locs(notes_str)
                    line_name = line_name_inner
                except ValueError:
                    loc_a, loc_b = '', ''

        elif mileages.startswith('0.00') and datum != '':
            loc_a = datum
            if loc_a in line_name:
                parts = pat.split(line_name)
                loc_b = parts[1].strip() if len(parts) >= 2 else line_name
            else:
                loc_b = line_name

        elif re.match(r'(\w ?)+ (and|&|to) (\w ?)+', notes_str):
            try:
                loc_a, loc_b = _split_locs(notes_str)
            except ValueError:
                loc_a, loc_b = '', ''

        else:
            try:
                loc_a, loc_b = _split_locs(notes_str)
            except ValueError:
                try:
                    loc_a, loc_b = _split_locs(line_name)
                except ValueError:
                    pass

            # Fix: Only fallback to line_name if no valid locations were parsed previously
            if not loc_a and line_name:
                loc_a, loc_b = line_name, line_name

        miles_chains = mileages.split(' - ')
        locations = [loc_a, loc_b]

        # Safely bind extracted mileages to their corresponding parsed locations
        parsed_content = [[m, l] for m, l in zip(miles_chains, locations)]

        return line_name, parsed_content

    def _split_measures(self, mileage_data, measure_headers_indices):
        """
        Processes data of mileage file with multiple measures.

        :param mileage_data: scraped raw mileage file from source web page
        :type: pandas.DataFrame
        """

        dat = mileage_data.copy()

        if len(measure_headers_indices) >= 1:

            if len(measure_headers_indices) == 1 and measure_headers_indices[0] != 0:
                j = measure_headers_indices[0]
                m_key, _ = dat.loc[j, 'Node'].split(maxsplit=1)
                d = {
                    'Earlier': 'Later',
                    'Later': 'Earlier',
                    'Alternative': 'One',
                    'Alternate': 'One',
                    'One': 'Alternative',
                    'Original': 'Current',
                    'Current': 'Original',
                    'Former': 'Current',
                    'Old': 'Current',
                    'New': 'Old',
                }
                if m_key in d:
                    measure_headers_indices = [0] + [j + 1]
                    new_m_key = d[m_key] + ' measure'
                    dat.loc[-1] = ['', new_m_key]  # adding a row
                    dat.index = dat.index + 1
                    dat.sort_index(inplace=True)

            # if measure_headers_indices[-1] != dat.index[-1] - 1:
            #     sep_rows_idx = loop_in_pairs(measure_headers_indices + [dat.index[-1]])
            # else:
            sep_rows_idx = loop_in_pairs(measure_headers_indices + [dat.index[-1] + 1])
            dat_ = {dat.loc[i, 'Node']: dat.loc[i + 1:j - 1] for i, j in sep_rows_idx}

        else:
            test_temp = dat[~dat['Mileage'].astype(bool)]
            if not test_temp.empty:
                test_temp_node, sep_rows_idx = test_temp['Node'].tolist(), test_temp.index[-1]

                if '1949 measure' in test_temp_node:
                    dat['Node'] = dat['Node'].str.replace('1949 measure', 'Current measure')
                    test_temp_node = [re.sub(r'1949 ', 'Current ', x) for x in test_temp_node]

                if 'One measure' in test_temp_node:
                    sep_rows_idx = dat[dat['Node'].str.contains('Alternative measure')].index[0]
                    m_dat_1, m_dat_2 = dat.loc[:(sep_rows_idx - 1)], dat.loc[sep_rows_idx:]
                    assert isinstance(m_dat_1, pd.DataFrame) and isinstance(m_dat_2, pd.DataFrame)
                    dat_ = {
                        'One measure':
                            m_dat_1[~m_dat_1['Node'].str.contains('One measure')],
                        'Alternative measure':
                            m_dat_2[~m_dat_2['Node'].str.contains('Alternative measure')],
                    }

                elif 'Later measure' in test_temp_node:
                    sep_rows_idx = dat[dat['Node'].str.contains('Later measure')].index[0]
                    m_dat_1, m_dat_2 = dat.loc[:(sep_rows_idx - 1)], dat.loc[sep_rows_idx:]
                    assert isinstance(m_dat_1, pd.DataFrame) and isinstance(m_dat_2, pd.DataFrame)
                    dat_ = {
                        'Original measure':
                            m_dat_1[~m_dat_1['Node'].str.contains('Original measure')],
                        'Later measure':
                            m_dat_2[~m_dat_2['Node'].str.contains('Later measure')],
                    }

                elif "This line has two 'legs':" in test_temp_node:
                    dat_ = dat.iloc[1:].drop_duplicates(ignore_index=True)

                elif 'Measure sometimes used' in test_temp_node:
                    sep_rows_idx = test_temp.index.tolist() + [dat.index[-1]]
                    dat_ = {
                        dat.loc[j, 'Node']: dat.loc[j + 1:k]
                        for j, k in loop_in_pairs(sep_rows_idx)}

                else:
                    alt_sep_rows_idx = [x in test_temp_node for x in self.measure_headers]
                    num_of_measures = sum(alt_sep_rows_idx)

                    if num_of_measures == 1:  #
                        m_name = self.measure_headers[alt_sep_rows_idx.index(True)]  # measure name
                        sep_rows_idx = dat[dat['Node'].str.contains(m_name)].index[0]
                        m_dat_1, m_dat_2 = dat.loc[:(sep_rows_idx - 1)], dat.loc[sep_rows_idx:]
                        assert isinstance(m_dat_1, pd.DataFrame)
                        assert isinstance(m_dat_2, pd.DataFrame)

                        x = [x_ for x_ in test_temp_node if 'measure' in x_ or 'route' in x_][0]
                        if re.match(r'(Original)|(Former)|(Alternative)|(Usual)', x):
                            measure_ = re.sub(
                                r'(Original)|(Former)|(Alternative)|(Usual)', 'Current', x)
                        else:
                            measure_ = re.sub(r'(Current)|(Later)|(One)', 'Previous', x)

                        dat_ = {
                            measure_: m_dat_1.loc[0:sep_rows_idx, :],
                            test_temp_node[0]: m_dat_2.loc[sep_rows_idx + 1:, :],
                        }

                    elif num_of_measures == 2:  # e.g. elr='BTJ'
                        sep_rows_idx_items = [
                            self.measure_headers[x] for x in np.where(alt_sep_rows_idx)[0]]
                        sep_rows_idx = dat[dat['Node'].isin(sep_rows_idx_items)].index[-1]
                        m_dat_list = dat.loc[:(sep_rows_idx - 1)], dat.loc[sep_rows_idx:]

                        sep_rows_idx_items_checked = map(
                            lambda x: x[x['Node'].isin(sep_rows_idx_items)]['Node'].iloc[0],
                            m_dat_list)
                        m_dat_list_ = map(
                            lambda x: x[~x['Node'].isin(sep_rows_idx_items)],
                            m_dat_list)

                        dat_ = dict(zip(sep_rows_idx_items_checked, m_dat_list_))

                    else:
                        if dat.loc[sep_rows_idx, 'Mileage'] == '':
                            dat.loc[sep_rows_idx, 'Mileage'] = dat.loc[sep_rows_idx - 1, 'Mileage']
                        dat_ = dat

            else:
                dat_ = dat

        return dat_

    def _parse_mileage_and_notes(self, content):
        # Search for notes
        notes_dat = []
        parsed_content = content.copy()
        # measure_headers = []
        measure_headers_indices = []

        for _, x in enumerate(content):
            if len(x) == 1:
                x_ = f'{x[0]}.' if x[0].endswith(tuple(string.ascii_letters)) else x[0]
                notes_dat.append(x_)
                parsed_content.remove(x)
            else:
                mil_dat, txt_dat = x
                if mil_dat == '':
                    if txt_dat in self.measure_headers or any(
                            mh in txt_dat for mh in self.measure_headers):
                        # measure_headers.append(txt_dat)
                        measure_headers_indices.append(parsed_content.index(x))
                    elif 'Revised distances are thus:' in txt_dat:
                        txt_dat = 'Current measure'
                        j = parsed_content.index(x)
                        parsed_content[j] = [mil_dat, txt_dat]
                        # measure_headers.append(txt_dat)
                        measure_headers_indices.append(j)
                    elif 'Later (post-preservation measure)' in txt_dat:
                        txt_dat = 'Later measure (post-preservation measure)'
                        j = parsed_content.index(x)
                        parsed_content[j] = [mil_dat, txt_dat]
                        measure_headers_indices.append(j)
                    elif 'Distances in km' in txt_dat or \
                            'measured from accurate mapping systems' in txt_dat \
                            or len(txt_dat) >= 50:
                        notes_dat.append(txt_dat)
                        parsed_content.remove(x)
                    elif re.search(r'\b[Mm]easure\b', txt_dat):
                        # measure_headers.append(txt_dat)
                        measure_headers_indices.append(parsed_content.index(x))

        if any('Distances in km' in x for x in notes_dat):
            parsed_content = [
                [x[0] + 'km', x[1]] if not x[0].endswith('km') else x for x in parsed_content]

        # Create a table of the mileage data
        mileage_data = pd.DataFrame(parsed_content, columns=['Mileage', 'Node'])

        # If there are multiple measures in 'mileage_data', e.g. current/former measures
        mileage_data = self._split_measures(
            mileage_data=mileage_data, measure_headers_indices=measure_headers_indices)

        # Make a dict of note
        notes_data = {'Notes': ' '.join(notes_dat).strip()}

        return mileage_data, notes_data

    def _collect_mileage_file(self, source, elr, parsed=True, dump_dir=False, verbose=False):
        """
        Parse the HTML response of an ELR mileage page and construct a structured dataset.

        This method extracts the line name, sub-line, and mileage data from the raw HTML.
        If a 404 error is detected, it falls back to querying the local ELR database to
        resolve redirects or parse alternative line details.

        :param source: The HTTP response object containing the raw HTML content.
        :type source: requests.Response | Any
        :param elr: The target Engineer's Line Reference (ELR) code.
        :type elr: str
        :param parsed: Whether to deeply parse the raw mileage data into structured formats.
            Defaults to ``True``.
        :type parsed: bool
        :param dump_dir: The directory path where the mileage file should be saved.
            Defaults to ``False``.
        :type dump_dir: str | os.PathLike | bool | None
        :param verbose: Whether to print progress details to the console. Defaults to ``False``.
        :type verbose: bool | int
        :return: A compiled dictionary containing line info, mileage data, and notes.
        :rtype: dict
        """

        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

        # Safely extract headers
        h3_tag = soup.find('h3')
        if h3_tag:
            if h3_tag.em:  # Check if an <em> tag exists inside it, and destroy it if it does
                h3_tag.em.decompose()
            line_name = h3_tag.get_text(strip=True)
        else:
            line_name = ''

        h4_tag = soup.find('h4')
        sub_line_name = h4_tag.get_text().strip() if h4_tag else ''

        err_msgs = {'"404" error: page not found', '404 error: page not found'}
        is_404 = (line_name.lower() in err_msgs) or (sub_line_name.lower() in err_msgs)

        if is_404:
            elr_data_all = self.fetch_elr(initial=elr[0])[elr[0]]
            elr_data = elr_data_all[elr_data_all['ELR'] == elr]

            if not elr_data.empty:
                notes_dat = str(elr_data['Notes'].iloc[0])

                if re.match(r'(Now( part of)? |= |See )[A-Z]{3}(\d)?$', notes_dat):
                    return self._handle_err404(
                        elr=elr,
                        notes_dat=notes_dat,
                        parsed=parsed,
                        dump_dir=dump_dir,
                        verbose=verbose
                    )
                else:
                    line_name, content = self._parse_line_details(elr_data, notes_dat)
            else:
                line_name, content = '', []

        else:
            ln_temp = line_name.split('\t')
            line_name = ln_temp[0] if len(ln_temp) == 1 else ln_temp[1]

            pre_tag = soup.find('pre')
            if pre_tag:
                temp = [
                    x.strip().split('\t', 1)
                    for x in pre_tag.text.splitlines() if x.strip() != ''
                ]
                temp = [[y.replace('  ', ' ').replace('\t', ' ') for y in x] for x in temp]
                content = [
                    [''] + x if (len(x) == 1) and ('Note that' not in x[0]) else x
                    for x in temp
                ]
            else:
                content = []

        if sub_line_name and (sub_line_name.lower() not in err_msgs):
            sub_ln_temp = sub_line_name.split('\t')
            sub_headers = sub_ln_temp[0] if len(sub_ln_temp) == 1 else sub_ln_temp[1]
        else:
            sub_headers = ''

        # Consolidate line information
        line_info = {'ELR': elr, 'Line': line_name, 'Sub-Line': sub_headers}

        mileage_data, notes_data = self._parse_mileage_and_notes(content=content)

        if parsed:
            if isinstance(mileage_data, dict) and len(mileage_data) > 1:
                mileage_data = {
                    h: _parse_mileage_data(mileage_data=dat) for h, dat in mileage_data.items()
                }
            else:  # isinstance(dat, pd.DataFrame)
                mileage_data = _parse_mileage_data(mileage_data=mileage_data)

        # Efficiently combine all dictionaries via unpacking
        mileage_file = {**line_info, 'Mileage': mileage_data, **notes_data}

        if verbose in {True, 1}:
            print("Done.")

        self._save_mileage_file(mileage_file=mileage_file, dump_dir=dump_dir, verbose=verbose)

        return mileage_file

    def collect_mileage_file(self, elr, parsed=True, confirmation_required=True, dump_dir=False,
                             verbose=False, raise_error=False):
        """
        Collects the mileage file for a specific ELR from the source web page.

        :param elr: The ELR for which the mileage file is requested
            (e.g. ``'CJD'``, ``'MLA'``, ``'FED'``).
        :type elr: str
        :param parsed: Whether to parse the scraped mileage data; defaults to ``True``.
        :type parsed: bool
        :param confirmation_required: Whether user confirmation is required;
            if ``confirmation_required=True`` (default), prompts the user for confirmation
            before proceeding with data collection.
        :type confirmation_required: bool
        :param dump_dir: The path to a directory where the mileage file data is saved;
            if ``False`` (default), the data will not be dumped.
        :type dump_dir: str | os.PathLike | bool | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :param raise_error: Whether to raise the provided exception;
            if ``raise_error=False`` (default), the error will be suppressed.
        :type raise_error: bool
        :return: A dictionary containing the mileage file for the specified ELR.
        :rtype: dict

        .. note::

            - In some cases, mileages may be unknown and thus left blank
              (e.g. ``'ANI2, Orton Junction with ROB (~3.05)'``).
            - Mileages in parentheses are not on that ELR but are included for reference
              (e.g. ``'ANL, (8.67) NORTHOLT [London Underground]'``).
            - As with the main ELR list, mileages preceded by a tilde (~) are approximate.

        **Examples**::

            >>> from pyrcs.line_data import ELRMileages  # from pyrcs import ELRMileages

            >>> em = ELRMileages()

            >>> gam_mileage_file = em.collect_mileage_file(elr='GAM', verbose=True)
            Proceed with collecting the mileage file of "GAM"?
             [No]|Yes: yes
            Collecting the mileage file ... Done.

            >>> list(gam_mileage_file)
            ['ELR', 'Line', 'Sub-Line', 'Mileage', 'Notes']
            >>> gam_mileage_file['Mileage']
               Mileage Mileage_Note Miles_Chains  ... Link_1 Link_1_ELR Link_1_Mile_Chain
            0   8.1518                      8.69  ...
            1  10.0264                     10.12  ...
            [2 rows x 8 columns]

            >>> xrc2_mileage_file = em.collect_mileage_file(elr='XRC2', verbose=True)
            Proceed with collecting the mileage file of "XRC2"?
             [No]|Yes: yes
            Collecting the mileage file ... Done.

            >>> xrc2_mileage_file['Mileage']
              Mileage Mileage_Note  ... Link_1_ELR Link_1_Mile_Chain
            0  9.0158     14.629km  ...
            1  9.0447     14.893km  ...
            2  9.0557     14.994km  ...
            [3 rows x 8 columns]

            >>> xre_mileage_file = em.collect_mileage_file(elr='XRE', verbose=True)
            Proceed with collecting the mileage file of "XRE"?
             [No]|Yes: yes
            Collecting the mileage file ... Done.

            >>> xre_mileage_file['Mileage']
              Mileage Mileage_Note  ... Link_2_ELR Link_2_Mile_Chain
            0  7.0073     11.333km  ...
            1  7.0174     11.425km  ...
            2  9.0158     14.629km  ...
            3  9.0198     14.666km  ...
            4  9.0389     14.840km  ...
            5  9.0439   (14.886)km  ...
            6  9.0540   (14.978)km  ...
            [7 rows x 11 columns]

            >>> mor_mileage_file = em.collect_mileage_file(elr='MOR', verbose=True)
            Proceed with collecting the mileage file of "MOR"?
             [No]|Yes: yes
            Collecting the mileage file ... Done.

            >>> mor_mileage_file_data = mor_mileage_file['Mileage']

            >>> list(mor_mileage_file_data)
            ['Original measure', 'Later measure']
            >>> mor_mileage_file_data['Original measure']
               Mileage Mileage_Note Miles_Chains  ...        Link_1 Link_1_ELR Link_1_Mile_Chain
            0   0.0000                      0.00  ...  SWA (215.18)        SWA            215.18
            1   0.0242                      0.11  ...
            2   0.0572                      0.26  ...
            3   0.0792                      0.36  ...
            4   0.1078                      0.49  ...
            5   0.1716                      0.78  ...
            6   1.1166                      1.53  ...
            7   2.0066                      2.03  ...
            8   2.0836                      2.38  ...
            9                                     ...
            10  3.0462                      3.21  ...   SDI2 (2.79)       SDI2              2.79
            [11 rows x 8 columns]

            >>> mor_mileage_file_data['Later measure']
               Mileage Mileage_Note Miles_Chains  ...        Link_1 Link_1_ELR Link_1_Mile_Chain
            0   0.0000                      0.00  ...  SWA (215.26)        SWA            215.26
            1   0.0176                      0.08  ...  SWA (215.18)        SWA            215.18
            2   0.0418                      0.19  ...
            3   0.0748                      0.34  ...
            4   0.0968                      0.44  ...
            5   0.1254                      0.57  ...
            6   1.0132                      1.06  ...
            7   1.1342                      1.61  ...
            8   2.0242                      2.11  ...
            9   2.1012                      2.46  ...
            10                                    ...
            11  3.0638                      3.29  ...   SDI2 (2.79)       SDI2              2.79
            [12 rows x 8 columns]

            >>> fed_mileage_file = em.collect_mileage_file(elr='FED', verbose=True)
            Proceed with collecting the mileage file of "FED"?
             [No]|Yes: yes
            Collecting the mileage file ... Done.

            >>> fed_mileage_file_data = fed_mileage_file['Mileage']
            >>> list(fed_mileage_file_data)
            ['Current measure', 'Original route']

            >>> fed_mileage_file_data['Current measure']
               Mileage Mileage_Note  ... Link_1_ELR Link_1_Mile_Chain
            0  83.1254               ...        FEL
            1  84.0198               ...
            2  84.1430               ...
            3  84.1540               ...
            4  85.0484               ...
            5  85.1122               ...
            6  85.1188               ...        TFN              2.13
            [7 rows x 8 columns]

            >>> fed_mileage_file_data['Original route']
              Mileage Mileage_Note Miles_Chains  ...       Link_1 Link_1_ELR Link_1_Mile_Chain
            0  0.0000                      0.00  ...  FEL (84.22)        FEL             84.22
            1  1.0176                      1.08  ...
            2  1.1540                      1.70  ...
            3  1.1694                      1.77  ...
            [4 rows x 8 columns]
        """

        target_elr = remove_punctuation(elr).upper()

        if not target_elr:
            return None

        target_elr = target_elr.upper()
        confirm_prompt = f'Proceed with collecting the mileage file of "{target_elr}"?\n'

        if confirmed(confirm_prompt, confirmation_required=confirmation_required):
            if verbose in {True, 1}:
                message_ = "Collecting the mileage file"
                if not confirmation_required:
                    message_ += f' of "{target_elr}"'
                print(message_, end=" ... ")

            try:
                url = urllib.parse.urljoin(
                    homepage_url(),
                    f'/elrs/_mileages/{target_elr[0]}/{target_elr}.shtm'.lower())
                source = requests.get(url=url, headers=fake_requests_headers())
                source.raise_for_status()
            except Exception as e:
                handle_connection_error(verbose=verbose, e=e)
                return None

            try:
                return self._collect_mileage_file(
                    source=source, elr=target_elr, parsed=parsed, dump_dir=dump_dir,
                    verbose=verbose)
            except Exception as e:
                _print_failure_message(e, "Errors:", verbose=verbose, raise_error=raise_error)

        return None

    def fetch_mileage_file(self, elr, update=False, dump_dir=None, verbose=False,
                           raise_error=False):
        """
        Fetches the mileage file for a specific ELR.

        :param elr: The ELR for which the mileage file is requested
            (e.g. ``'CJD'``, ``'MLA'``, ``'FED'``).
        :type elr: str
        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: Path to the directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | os.PathLike | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :param raise_error: Whether to raise the provided exception;
            if ``raise_error=False`` (default), the error will be suppressed.
        :type raise_error: bool
        :return: A dictionary containing the mileage file (codes), line name and
            any additional information or notes.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.line_data import ELRMileages  # from pyrcs import ELRMileages
            >>> import tempfile
            >>> import pathlib
            >>> tmp_path = pathlib.Path(tempfile.TemporaryDirectory().name)
            >>> em = ELRMileages()
            >>> # Get the mileage file of 'AAL' (Now 'NAJ3')
            >>> aal_mileage_file = em.fetch_mileage_file(elr='AAL', dump_dir=tmp_path)
            >>> type(aal_mileage_file)
            dict
            >>> list(aal_mileage_file.keys())
            ['ELR', 'Line', 'Sub-Line', 'Mileage', 'Notes', 'Formerly']
            >>> aal_mileage_file['ELR']
            'NAJ3'
            >>> aal_mileage_file['Notes']
            'Note that Ashendon Junction up line junction is on NAJ2'
            >>> aal_mileage_file['Mileage']
                Mileage Mileage_Note  ... Link_1_ELR Link_1_Mile_Chain
            0    0.0000               ...       NAJ2             33.69
            1    0.0594               ...        GUA            164.75
            2    1.0396               ...
            3    3.0682               ...
            4    6.0704               ...
            5    8.0572               ...        BSG              0.00
            6    8.0990               ...        WEJ
            7    9.0594               ...
            8   13.0264               ...
            9   17.0858               ...
            10  17.0968               ...
            11  18.0572               ...        DCL             81.10
            12  18.0638               ...        DCL             81.12
            [13 rows x 8 columns]
            >>> # Get the mileage file of 'MLA'
            >>> mla_mileage_file = em.fetch_mileage_file(elr='MLA', dump_dir=tmp_path)
            >>> type(mla_mileage_file)
            dict
            >>> list(mla_mileage_file.keys())
            ['ELR', 'Line', 'Sub-Line', 'Mileage', 'Notes']
            >>> mla_mileage_file_mileages = mla_mileage_file['Mileage']
            >>> type(mla_mileage_file_mileages)
            dict
            >>> list(mla_mileage_file_mileages.keys())
            ['Current measure', 'Original measure']
            >>> mla_mileage_file_mileages['Original measure']
              Mileage Mileage_Note  ... Link_3_ELR Link_3_Mile_Chain
            0  4.1386               ...       NEM4              0.00
            1  5.0616               ...
            2  5.1122               ...
            [3 rows x 14 columns]
            >>> mla_mileage_file_mileages['Current measure']
              Mileage Mileage_Note Miles_Chains  ...       Link_1 Link_1_ELR Link_1_Mile_Chain
            0  0.0000                      0.00  ...  MRL2 (4.44)       MRL2              4.44
            1  0.0572                      0.26  ...         None
            2  0.1540                      0.70  ...         None
            3  0.1606                      0.73  ...         None
            [4 rows x 8 columns]
            >>> # Get the mileage file of 'LCG'
            >>> mla_mileage_file = em.fetch_mileage_file(elr='LCG', dump_dir=tmp_path)
        """

        try:
            target_elr = remove_punctuation(elr)

            data_name = target_elr.lower()
            data_name += ("_" if data_name == "prn" else "")
            sub_dir, ext = data_name[0], ".pkl"

            path_to_file = self._cdd("mileage-files", sub_dir, f"{data_name}{ext}", mkdir=False)

            if os.path.isfile(path_to_file) and not update:
                mileage_file = load_data(path_to_file)

            else:
                verbose_ = get_collect_verbosity_for_fetch(data_dir=dump_dir, verbose=verbose)
                mileage_file = self.collect_mileage_file(
                    elr=target_elr, parsed=True, confirmation_required=False, dump_dir=None,
                    verbose=verbose_)

            if dump_dir not in {False, None}:
                self._save_data_to_file(
                    data=mileage_file, data_name=data_name, ext=ext, dump_dir=dump_dir,
                    verbose=verbose)

            return mileage_file

        except Exception as e:
            _print_failure_message(e, prefix="Errors:", verbose=verbose, raise_error=raise_error)

    @staticmethod
    def search_conn(start_elr, start_em, end_elr, end_em):
        """
        Searches for connections between two pairs of ELRs and their associated mileages.

        :param start_elr: The starting ELR.
        :type start_elr: str
        :param start_em: The mileage file associated with the starting ELR.
        :type start_em: pandas.DataFrame
        :param end_elr: The ending ELR.
        :type end_elr: str
        :param end_em: The mileage file associated with the ending ELR.
        :type end_em: pandas.DataFrame
        :return: A tuple containing the end mileage of the starting ELR and
            the start mileage of the ending ELR.
        :rtype: tuple

        **Examples**::

            >>> from pyrcs.line_data import ELRMileages  # from pyrcs import ELRMileages
            >>> em = ELRMileages()
            >>> elr_1 = 'AAM'
            >>> mileage_file_1 = em.collect_mileage_file(elr_1, confirmation_required=False)
            >>> mf_1_mileages = mileage_file_1['Mileage']
            >>> mf_1_mileages.head()
              Mileage Mileage_Note  ... Link_2_ELR Link_2_Mile_Chain
            0  0.0000               ...
            1  0.0154               ...
            2  0.0396               ...
            3  1.1012               ...
            4  1.1408               ...
            [5 rows x 11 columns]
            >>> elr_2 = 'ANZ'
            >>> mileage_file_2 = em.collect_mileage_file(elr_2, confirmation_required=False)
            >>> mf_2_mileages = mileage_file_2['Mileage']
            >>> mf_2_mileages.head()
               Mileage Mileage_Note Miles_Chains  ...      Link_1 Link_1_ELR Link_1_Mile_Chain
            0  84.0924                     84.42  ...         BEA        BEA
            1  84.1364                     84.62  ...  AAM (0.18)        AAM              0.18
            [2 rows x 8 columns]
            >>> elr_1_dest, elr_2_orig = em.search_conn(elr_1, mf_1_mileages, elr_2, mf_2_mileages)
            >>> elr_1_dest
            '0.0396'
            >>> elr_2_orig
            '84.1364'
        """

        start_mask = start_em.apply(lambda x: x.str.contains(end_elr, case=False).any(), axis=1)
        start_temp = start_em[start_mask]
        assert isinstance(start_temp, pd.DataFrame)

        if not start_temp.empty:
            # Get exact location
            key_idx = start_temp.index[0]
            mile_chain_col = [x for x in start_temp.columns if re.match(r'.*_Mile_Chain', x)][0]

            # Mileage of the Start ELR
            start_dest_mileage = start_em.loc[key_idx, 'Mileage']
            # Mileage of the End ELR
            end_orig_mile_chain: str | None = start_temp.loc[key_idx, mile_chain_col]

            if end_orig_mile_chain and end_orig_mile_chain != 'Unknown':
                end_orig_mileage = mile_chain_to_mileage(end_orig_mile_chain)

            else:  # end_conn_mile_chain == '':
                end_mask = end_em.apply(
                    lambda x: x.str.contains(start_elr, case=False).any(), axis=1)
                end_temp = end_em[end_mask]

                if not end_temp.empty:
                    end_orig_mileage = end_temp['Mileage'].iloc[0]
                else:
                    end_orig_mileage = start_dest_mileage

        else:
            start_dest_mileage, end_orig_mileage = '', ''

        return start_dest_mileage, end_orig_mileage

    @staticmethod
    def _select_measure(em_dat, key_pat):
        if isinstance(em_dat, dict):
            em_ks = [k for k in em_dat.keys() if re.match(key_pat, k)]
            if not em_ks:
                em_dat_ = em_dat[list(em_dat.keys())[0]]
            else:
                em_dat_ = em_dat[em_ks[0]]

        else:
            em_dat_ = em_dat

        return em_dat_

    def get_conn_mileages(self, start_elr, end_elr, update=False, **kwargs):
        """
        Retrieves the connection point between two pairs of ELRs and their associated mileages.

        Specifically, it finds the end mileage for the starting ELR and
        the start mileage for the ending ELR.

        .. note::

            This function may not be able to find a connection for every pair of ELRs.
            Please refer to :ref:`Example 2<get_conn_mileages-example-2>` for more information.

        :param start_elr: The starting ELR.
        :type start_elr: str
        :param end_elr: The ending ELR.
        :type end_elr: str
        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param kwargs: [Optional] Additional parameters for the method
            :py:meth:`~pyrcs.line_data.elr_mileage.ELRMileages.fetch_mileage_file`.
        :return: A tuple containing the connection ELR(s) and mileage(s) between the specified 
            ``start_elr`` and ``end_elr``.
        :rtype: tuple

        **Example 1**::

            >>> from pyrcs.line_data import ELRMileages  # from pyrcs import ELRMileages
            >>> em = ELRMileages()
            >>> conn = em.get_conn_mileages(start_elr='NAY', end_elr='LTN2')
            >>> (s_dest_mlg, c_elr, c_orig_mlg, c_dest_mlg, e_orig_mlg) = conn
            >>> s_dest_mlg
            '5.1606'
            >>> c_elr
            'NOL'
            >>> c_orig_mlg
            '5.1606'
            >>> c_dest_mlg
            '0.0638'
            >>> e_orig_mlg
            '123.1320'

        .. _get_conn_mileages-example-2:

        **Example 2**::

            >>> from pyrcs.line_data import ELRMileages  # from pyrcs import ELRMileages
            >>> em = ELRMileages()
            >>> conn = em.get_conn_mileages(start_elr='MAC3', end_elr='DBP1', dump_dir="tests")
            >>> conn
            ('', '', '', '', '')
        """

        start_file, end_file = map(
            functools.partial(self.fetch_mileage_file, update=update, **kwargs),
            [start_elr, end_elr])

        if start_file is not None and end_file is not None:
            start_elr, end_elr = start_file['ELR'], end_file['ELR']
            start_em, end_em = start_file['Mileage'], end_file['Mileage']
            key_pat = re.compile(r'(Current\s)|(One\s)|(Later\s)|(Usual\s)|(Measure used by\s)')

            start_em = self._select_measure(start_em, key_pat)
            end_em = self._select_measure(end_em, key_pat)

            start_dest_mileage, end_orig_mileage = self.search_conn(
                start_elr=start_elr, start_em=start_em, end_elr=end_elr, end_em=end_em)

            conn_elr, conn_orig_mileage, conn_dest_mileage = '', '', ''

            if not start_dest_mileage and not end_orig_mileage:
                link_cols = [x for x in start_em.columns if re.match(r'Link_\d_ELR.?', x)]
                conn_elrs = start_em[link_cols]

                i = 0
                while i < len(link_cols):
                    link_col = link_cols[i]
                    conn_temp = conn_elrs[
                        conn_elrs.astype(bool)].dropna(how='all')[link_col].dropna()

                    j = 0
                    while j < len(conn_temp):
                        # print(i, j)
                        conn_elr = conn_temp.iloc[j]
                        conn_em = self.fetch_mileage_file(elr=conn_elr, update=update)
                        if conn_em is not None:
                            conn_elr, conn_em = conn_em['ELR'], conn_em['Mileage']
                            if isinstance(conn_em, dict):
                                conn_em = self._select_measure(conn_em, key_pat)

                            start_dest_mileage, conn_orig_mileage = self.search_conn(
                                start_elr, start_em, conn_elr, conn_em)

                            conn_dest_mileage, end_orig_mileage = self.search_conn(
                                conn_elr, conn_em, end_elr, end_em)

                            if conn_dest_mileage and end_orig_mileage:
                                if not start_dest_mileage:
                                    start_dest_mileage = start_em[
                                        start_em[link_col] == conn_elr]['Mileage'].values[0]
                                if not conn_orig_mileage:
                                    link_col_conn = conn_em.where(conn_em == start_elr).dropna(
                                        axis=1, how='all').columns[0]
                                    temp = conn_em[conn_em[link_col_conn] == start_elr].Mileage
                                    conn_orig_mileage = temp.values[0]
                                break

                            else:
                                conn_elr = ''
                        j += 1

                    if conn_elr != '':
                        break
                    # else:
                    i += 1

            if conn_orig_mileage and not conn_elr:
                start_dest_mileage, conn_orig_mileage = '', ''

        else:
            return tuple([''] * 5)

        return start_dest_mileage, conn_elr, conn_orig_mileage, conn_dest_mileage, end_orig_mileage
