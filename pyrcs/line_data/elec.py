"""
Collects data of `section codes for overhead line electrification (OLE) installations
<http://www.railwaycodes.org.uk/electrification/mast_prefix0.shtm>`_.
"""

import itertools
import os
import re
import urllib.parse

import bs4
import pandas as pd
from pyhelpers.store import load_data

from .._base import _Base
from ..parser import _get_last_updated_date, get_heading_text, get_hypertext, get_page_catalogue, \
    parse_tr
from ..utils import cd_data, fetch_all_verbose, home_page_url


# def _parse_notes(h3):
#     notes_ = []
#
#     next_p = h3.find_next('p')
#     if next_p is not None:
#         h3_ = next_p.find_previous('h3')
#         while h3_ == h3:
#             notes_2 = get_hypertext(hypertext_tag=next_p, hyperlink_tag_name='a')
#             if notes_2:
#                 notes_2 = notes_2.replace(
#                     ' Section codes known at present are:', '').replace('Known prefixes are:', ' ')
#                 notes_.append(notes_2)
#
#             next_p = next_p.find_next('p')
#             if next_p is None:
#                 break
#             else:
#                 h3_ = next_p.find_previous('h3')
#
#     notes = ' '.join(notes_).replace('  ', ' ')
#
#     if not notes:
#         notes = None
#
#     return notes


def _parse_notes(h3):
    notes_ = []

    next_p = h3.find_next('p')
    while next_p and next_p.find_previous('h3') == h3:
        notes_2 = get_hypertext(hypertext_tag=next_p, hyperlink_tag_name='a')
        if notes_2:
            notes_2 = notes_2.replace(' Section codes known at present are:', '') \
                             .replace('Known prefixes are:', ' ')
            notes_.append(notes_2)

        next_p = next_p.find_next('p')

    return ' '.join(notes_).replace('  ', ' ') or None


def _parse_data_with_lists(h3, ul):
    sub_heading = get_heading_text(heading_tag=h3, elem_tag_name='em')

    data_1_key, data_2_key = 'Section codes', 'Known prefixes'

    # data_1
    table_1 = {data_1_key: None}
    if ul:
        table_1[data_1_key] = pd.DataFrame(
            [re.sub(r'[()]', '', li.text).split(' ', 1) for li in ul.findChildren('li')
             if li.text.strip()],
            columns=['Code', 'Area'])

    # data_2
    table_2 = {data_2_key: None}
    thead, tbody = h3.find_next('thead'), h3.find_next('tbody')
    if thead and tbody:
        ths = [th.text for th in thead.find_all('th')]
        trs = tbody.find_all('tr')
        table_2[data_2_key] = parse_tr(trs=trs, ths=ths, as_dataframe=True)

    # Notes
    notes = _parse_notes(h3)

    codes_with_lists = {sub_heading: {**table_1, **table_2, 'Notes': notes}}

    return codes_with_lists


def _parse_lists_only(h3, ul):
    sub_heading = get_heading_text(heading_tag=h3, elem_tag_name='em')

    list_data = [get_hypertext(x) for x in ul.findChildren('li')] if ul else []
    notes = (_parse_notes(h3) or "").strip().replace(' were:', '.')

    codes_with_lists = {sub_heading: {'Codes': list_data, 'Notes': notes}}

    return codes_with_lists


def _parse_data_without_lists(h3):
    sub_heading = get_heading_text(heading_tag=h3, elem_tag_name='em')

    notes = _parse_notes(h3=h3)

    data = {sub_heading: {'Codes': None, 'Notes': notes}}

    return data


def _parse_codes_and_notes(h3):
    """
    from pyrcs import Electrification
    import bs4
    import requests
    from pyhelpers.ops import fake_requests_headers

    elec = Electrification()

    url = elec.catalogue[elec.KEY_TO_INDEPENDENT_LINES]
    source = requests.get(url=url, headers=fake_requests_headers())
    soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

    h3 = soup.find('h3')

    h3 = h3.find_next('h3')
    """

    codes_and_notes = None

    # p = h3.find_next(name='p')
    ul, table = h3.find_next(name='ul'), h3.find_next(name='table')

    # Case 1: If there's a <ul> list
    if ul is not None:
        if ul.find_previous('h3') == h3:
            if table is not None:
                codes_and_notes = _parse_data_with_lists(h3=h3, ul=ul)
            else:
                codes_and_notes = _parse_lists_only(h3=h3, ul=ul)

    # Case 2: If there's a <table> but no <ul>
    if table is not None and codes_and_notes is None:
        if table.find_previous(name='h3') == h3:
            codes = None
            h3_ = table.find_previous(name='h3')
            thead, tbody = table.find_next(name='thead'), table.find_next(name='tbody')

            while h3_ == h3:
                ths, trs = [x.text for x in thead.find_all('th')], tbody.find_all('tr')

                # Parse table data
                dat = parse_tr(trs=trs, ths=ths, as_dataframe=True)
                codes_ = dat.map(
                    lambda x: re.sub(
                        pattern=r'\']\)?', repl=']',
                        string=re.sub(r'\(?\[\'', '[', x)).replace(
                        '\\xa0', '').replace('\r ', ' ').strip())

                codes = codes_ if codes is None else [codes, codes_]

                # Move to the next (if any)
                thead, tbody = thead.find_next(name='thead'), tbody.find_next(name='tbody')

                if tbody is None:
                    break
                else:
                    h3_ = tbody.find_previous(name='h3')

            notes = _parse_notes(h3=h3)

            sub_heading = get_heading_text(heading_tag=h3, elem_tag_name='em')
            codes_and_notes = {sub_heading: {'Codes': codes, 'Notes': notes}}

    if codes_and_notes is None:
        codes_and_notes = _parse_data_without_lists(h3=h3)

    return codes_and_notes


def _parse_source(soup):
    data = {}

    for h3 in soup.find_all('h3'):
        if data_ := _parse_codes_and_notes(h3):
            # If data_ is not None: data_ = _parse_codes_and_notes(h3)
            data.update(data_)

    return data


def _parse_ohns_codes(soup):
    thead, tbody = soup.find('thead'), soup.find('tbody')
    # if not thead or not tbody:
    #     return {'Codes': None, 'Notes': None}

    ths = [th.get_text(strip=True) for th in thead.find_all(name='th')]
    trs = tbody.find_all(name='tr')
    tbl = parse_tr(trs=trs, ths=ths)

    # Define cleanup rules
    sep = ',\t'
    records = [[x.replace('\r (', sep).replace(" (['", sep).replace(
        "'])", '').replace('\r', sep).replace("', '", sep).replace(
        ' &ap;', '≈').strip(')') for x in dat]
               for dat in tbl]

    # Handle rows where tracks and dates are multiple values
    expanded_records = []
    for row in records:
        tracks, dates = row[3].split(sep), row[4].split(sep)
        if len(tracks) > 1 and len(dates) > 1:
            expanded_records.extend([row[:3] + [trk, date] for trk, date in zip(tracks, dates)])
        else:
            expanded_records.append(row)
    # Convert to DataFrame
    neutral_sections_codes = pd.DataFrame(data=records, columns=ths)

    # Extract notes
    notes_ = soup.find(name='div', attrs={'class': 'background'})
    if notes_:
        notes_ = notes_.find_all(name='p')
        notes = '\n'.join(p.get_text(strip=True) for p in notes_).replace('  ', ' ')
    else:
        notes = None

    ohns_data = {'Codes': neutral_sections_codes, 'Notes': notes}

    return ohns_data, soup


class Electrification(_Base):
    """
    A class for collecting `section codes for overhead line electrification (OLE) installations
    <http://www.railwaycodes.org.uk/electrification/mast_prefix0.shtm>`_.
    """

    #: The name of the data.
    NAME: str = 'Section codes for overhead line electrification (OLE) installations'
    #: The key for accessing the data.
    KEY: str = 'Electrification'

    #: The key used to reference the data of the '*national network*'.
    KEY_TO_NATIONAL_NETWORK: str = 'National network'
    #: The key used to reference the data of the '*independent lines*'.
    KEY_TO_INDEPENDENT_LINES: str = 'Independent lines'
    #: The key used to reference the data of the
    #: '*overhead line electrification neutral sections (OHNS)*'.
    KEY_TO_OHNS: str = 'National network neutral sections'
    #: The key used to reference the data of the '*UK railway electrification tariff zones*'.
    KEY_TO_ETZ: str = 'National network energy tariff zones'

    #: The URL of the main web page for the data.
    URL: str = urllib.parse.urljoin(home_page_url(), f'/{KEY.lower()}/mast_prefix0.shtm')

    #: The key used to reference the last updated date in the data.
    KEY_TO_LAST_UPDATED_DATE: str = 'Last updated date'

    def __init__(self, data_dir=None, update=False, verbose=True):
        """
        :param data_dir: Name of the data directory; defaults to ``None``.
        :type data_dir: str | None
        :param update: Whether to check for updates to the data catalogue; defaults to ``False``.
        :type update: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``True``.
        :type verbose: bool | int

        :ivar dict catalogue: The catalogue of the data.
        :ivar str last_updated_date: The date when the data was last updated.
        :ivar str data_dir: The path to the directory containing the data.
        :ivar str current_data_dir: The path to the current data directory.

        **Examples**::

            >>> from pyrcs.line_data import Electrification  # from pyrcs import Electrification
            >>> elec = Electrification()
            >>> elec.NAME
            'Section codes for overhead line electrification (OLE) installations'
            >>> elec.URL
            'http://www.railwaycodes.org.uk/electrification/mast_prefix0.shtm'
        """

        super().__init__(
            data_dir=data_dir, content_type='catalogue', data_category="line-data", update=update,
            verbose=verbose)

    @staticmethod
    def _confirm_to_collect(data_name):
        return f"To collect section codes for OLE installations: {data_name}\n?"

    def _collect_elec_codes(self, source, data_name, parser_func=None, verbose=False):
        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

        # Get data of the specific category
        if parser_func is None:
            dat = _parse_source(soup)
        else:
            dat = parser_func(soup)

        # Get last updated date
        last_updated_date = _get_last_updated_date(soup=soup)

        # Put everything in a dictionary
        data = {data_name: dat, self.KEY_TO_LAST_UPDATED_DATE: last_updated_date}

        if verbose in {True, 1}:
            print("Done.")

        # Save a local backup for quick retrieval
        self._save_data_to_file(data=data, data_name=data_name, ext=".pkl", verbose=verbose)

        return data

    def collect_national_network_codes(self, confirmation_required=True, verbose=False,
                                       raise_error=True):
        """
        Collects the section codes for Overhead Line Electrification (OLE) installations for the
        `national network <http://www.railwaycodes.org.uk/electrification/mast_prefix1.shtm>`_
        from the source web page.

        :param confirmation_required: Whether user confirmation is required before proceeding;
            defaults to ``True``.
        :type confirmation_required: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :param raise_error: Whether to raise the provided exception; defaults to ``True``.
            if ``raise_error=False``, the error will be suppressed.
        :type raise_error: bool
        :return: A dictionary of OLE section codes for the national network,
            or ``None`` if not applicable.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.line_data import Electrification  # from pyrcs import Electrification
            >>> elec = Electrification()
            >>> nn_codes = elec.collect_national_network_codes(verbose=True)
            To collect section codes for OLE installations: National network
            ? [No]|Yes: yes
            Collecting the data ... Done.
            >>> type(nn_codes)
            dict
            >>> list(nn_codes.keys())
            ['National network', 'Last updated date']
            >>> elec.KEY_TO_NATIONAL_NETWORK
            'National network'
            >>> nn_codes_dat = nn_codes[elec.KEY_TO_NATIONAL_NETWORK]
            >>> type(nn_codes_dat)
            dict
            >>> list(nn_codes_dat.keys())
            ['Traditional numbering system [distance and sequence]',
             'New numbering system [km and decimal]',
             'Codes not certain [confirmation is welcome]',
             'Suspicious data',
             'An odd one to complete the record',
             'LBSC/Southern Railway overhead system',
             'Codes not known']
            >>> tns_codes = nn_codes_dat['Traditional numbering system [distance and sequence]']
            >>> type(tns_codes)
            dict
            >>> list(tns_codes.keys())
            ['Codes', 'Notes']
            >>> tns_codes_dat = tns_codes['Codes']
            >>> tns_codes_dat.head()
              Code  ...                          Datum
            0    A  ...               Fenchurch Street
            1    A  ...             Newbridge Junction
            2    A  ...               Fenchurch Street
            3    A  ...  Guide Bridge Station Junction
            4   AB  ...
            [5 rows x 4 columns]
        """

        national_network_ole = self._collect_data_from_source(
            data_name=self.KEY_TO_NATIONAL_NETWORK, method=self._collect_elec_codes,
            confirmation_required=confirmation_required,
            confirmation_prompt=self._confirm_to_collect,
            verbose=verbose, raise_error=raise_error)

        return national_network_ole

    def fetch_national_network_codes(self, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetches section codes for Overhead Line Electrification (OLE) installations on the
        `national network`_.

        .. _`national network`: http://www.railwaycodes.org.uk/electrification/mast_prefix1.shtm

        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: Path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary of OLE section codes for the national network,
            or ``None`` if not applicable.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.line_data import Electrification  # from pyrcs import Electrification
            >>> elec = Electrification()
            >>> nn_codes = elec.fetch_national_network_codes()
            >>> type(nn_codes)
            dict
            >>> list(nn_codes.keys())
            ['National network', 'Last updated date']
            >>> elec.KEY_TO_NATIONAL_NETWORK
            'National network'
            >>> nn_codes_dat = nn_codes[elec.KEY_TO_NATIONAL_NETWORK]
            >>> type(nn_codes_dat)
            dict
            >>> list(nn_codes_dat.keys())
            ['Traditional numbering system [distance and sequence]',
             'New numbering system [km and decimal]',
             'Codes not certain [confirmation is welcome]',
             'Suspicious data',
             'An odd one to complete the record',
             'LBSC/Southern Railway overhead system',
             'Codes not known']
            >>> tns_codes = nn_codes_dat['Traditional numbering system [distance and sequence]']
            >>> type(tns_codes)
            dict
            >>> list(tns_codes.keys())
            ['Codes', 'Notes']
            >>> tns_codes_dat = tns_codes['Codes']
            >>> tns_codes_dat.head()
              Code  ...                          Datum
            0    A  ...               Fenchurch Street
            1    A  ...             Newbridge Junction
            2    A  ...               Fenchurch Street
            3    A  ...  Guide Bridge Station Junction
            4   AB  ...
            [5 rows x 4 columns]
        """

        args = {
            'data_name': self.KEY_TO_NATIONAL_NETWORK,
            'method': self.collect_national_network_codes,
        }
        kwargs.update(args)

        national_network_ole = self._fetch_data_from_file(
            update=update, dump_dir=dump_dir, verbose=verbose, **kwargs)

        return national_network_ole

    def get_independent_lines_catalogue(self, update=False, verbose=False):
        """
        Gets a catalogue for the
        `independent lines <http://www.railwaycodes.org.uk/electrification/mast_prefix2.shtm>`_.

        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A pandas DataFrame containing the names of independent lines.
        :rtype: pandas.DataFrame

        **Examples**::

            >>> from pyrcs.line_data import Electrification  # from pyrcs import Electrification
            >>> from pyhelpers.settings import pd_preferences
            >>> pd_preferences(max_columns=1)
            >>> elec = Electrification()
            >>> indep_line_cat = elec.get_independent_lines_catalogue()
            >>> indep_line_cat.head()
                                                         Feature  ...
            0                                    Beamish Tramway  ...
            1                                 Birkenhead Tramway  ...
            2                        Black Country Living Museum  ...
            3                                  Blackpool Tramway  ...
            4  Brighton and Rottingdean Seashore Electric Rai...  ...
            [5 rows x 3 columns]
        """

        data_name, ext = "electrification-independent-lines", ".pkl"
        path_to_file = cd_data("catalogue", data_name + ext)

        if os.path.isfile(path_to_file) and not update:
            indep_line_names = load_data(path_to_file)

        else:
            url = self.catalogue[self.KEY_TO_INDEPENDENT_LINES]

            indep_line_names = get_page_catalogue(
                url=url, head_tag_name='nav', head_tag_txt='Jump to: ', feature_tag_name='h3',
                verbose=verbose)

            self._save_data_to_file(
                data=indep_line_names, data_name=data_name, ext=ext,
                dump_dir=cd_data("catalogue"), verbose=verbose)

        return indep_line_names

    def collect_independent_lines_codes(self, confirmation_required=True, verbose=False,
                                        raise_error=True):
        """
        Collects OLE section codes for `independent lines`_ from the source web page.

        .. _`independent lines`: http://www.railwaycodes.org.uk/electrification/mast_prefix2.shtm

        :param confirmation_required: Whether user confirmation is required before proceeding;
            defaults to ``True``.
        :type confirmation_required: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :param raise_error: Whether to raise the provided exception; defaults to ``True``.
            if ``raise_error=False``, the error will be suppressed.
        :type raise_error: bool
        :return: A dictionary of OLE section codes for independent lines,
            or ``None`` if not applicable.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.line_data import Electrification  # from pyrcs import Electrification
            >>> elec = Electrification()
            >>> indep_lines_codes = elec.collect_independent_lines_codes(verbose=True)
            To collect section codes for OLE installations: Independent lines
            ? [No]|Yes: yes
            Collecting the data ... Done.
            >>> type(indep_lines_codes)
            dict
            >>> list(indep_lines_codes.keys())
            ['Independent lines', 'Last updated date']
            >>> elec.KEY_TO_INDEPENDENT_LINES
            'Independent lines'
            >>> indep_lines_codes_dat = indep_lines_codes[elec.KEY_TO_INDEPENDENT_LINES]
            >>> type(indep_lines_codes_dat)
            dict
            >>> len(indep_lines_codes_dat)
            23
            >>> list(indep_lines_codes_dat.keys())[-5:]
            ['Sheffield Supertram',
             'Snaefell Mountain Railway',
             'Summerlee, Museum of Scottish Industrial Life Tramway',
             'Tyne & Wear Metro',
             'West Midlands Metro [West Midlands]']
            >>> indep_lines_codes_dat['Summerlee, Museum of Scottish Industrial Life Tramway']
            {'Codes': None, 'Notes': 'Masts do not carry any labels.'}
        """

        independent_lines_ole = self._collect_data_from_source(
            data_name=self.KEY_TO_INDEPENDENT_LINES, method=self._collect_elec_codes,
            confirmation_required=confirmation_required,
            confirmation_prompt=self._confirm_to_collect,
            verbose=verbose, raise_error=raise_error)

        return independent_lines_ole

    def fetch_independent_lines_codes(self, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetches OLE section codes for `independent lines`_.

        .. _`independent lines`: http://www.railwaycodes.org.uk/electrification/mast_prefix2.shtm

        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: Path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary of OLE section codes for independent lines.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.line_data import Electrification  # from pyrcs import Electrification
            >>> elec = Electrification()
            >>> indep_lines_codes = elec.fetch_independent_lines_codes()
            >>> type(indep_lines_codes)
            dict
            >>> list(indep_lines_codes.keys())
            ['Independent lines', 'Last updated date']
            >>> elec.KEY_TO_INDEPENDENT_LINES
            'Independent lines'
            >>> indep_lines_codes_dat = indep_lines_codes[elec.KEY_TO_INDEPENDENT_LINES]
            >>> type(indep_lines_codes_dat)
            dict
            >>> len(indep_lines_codes_dat)
            22
            >>> list(indep_lines_codes_dat.keys())
            ['Beamish Tramway',
             'Birkenhead Tramway',
             'Black Country Living Museum [Tipton]',
             'Blackpool Tramway',
             "Brighton and Rottingdean Seashore Electric Railway [Magnus Volk's 'Daddy Long Legs'...
             'Channel Tunnel',
             'Croydon Tramlink',
             'East Anglia Transport Museum [Lowestoft]',
             'Edinburgh Tramway',
             'Heath Park Tramway [Cardiff]',
             'Heaton Park Tramway [Manchester]',
             'Iarnród Éireann',
             'Luas [Dublin]',
             'Manchester Metrolink',
             'Manx Electric Railway',
             'Nottingham Express Transit',
             'Seaton Tramway',
             'Sheffield Supertram',
             'Snaefell Mountain Railway',
             'Summerlee, Museum of Scottish Industrial Life Tramway',
             'Tyne & Wear Metro',
             'West Midlands Metro [West Midlands]']
            >>> indep_lines_codes_dat['Beamish Tramway']
            {'Codes': None, 'Notes': 'Masts do not appear labelled.'}
        """

        args = {
            'data_name': self.KEY_TO_INDEPENDENT_LINES,
            'method': self.collect_independent_lines_codes,
        }
        kwargs.update(args)

        independent_lines_ole = self._fetch_data_from_file(
            update=update, dump_dir=dump_dir, verbose=verbose, **kwargs)

        return independent_lines_ole

    def collect_ohns_codes(self, confirmation_required=True, verbose=False, raise_error=True):
        """
        Collects codes for
        `overhead line electrification neutral sections
        <http://www.railwaycodes.org.uk/electrification/neutral.shtm>`_ (OHNS)
        from the source web page.

        :param confirmation_required: Whether user confirmation is required before proceeding;
            defaults to ``True``.
        :type confirmation_required: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :param raise_error: Whether to raise the provided exception; defaults to ``True``.
            if ``raise_error=False``, the error will be suppressed.
        :return: A dictionary of OHNS codes, or ``None`` if not applicable.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.line_data import Electrification  # from pyrcs import Electrification
            >>> elec = Electrification()
            >>> ohl_ns_codes = elec.collect_ohns_codes(verbose=True)
            To collect section codes for OLE installations: National network neutral sections
            ? [No]|Yes: yes
            Collecting the data ... Done.
            >>> type(ohl_ns_codes)
            dict
            >>> list(ohl_ns_codes.keys())
            ['National network neutral sections', 'Last updated date']
            >>> elec.KEY_TO_OHNS
            'National network neutral sections'
            >>> ohl_ns_codes_dat = ohl_ns_codes[elec.KEY_TO_OHNS]
            >>> type(ohl_ns_codes_dat)
            dict
            >>> list(ohl_ns_codes_dat.keys())
            ['Codes', 'Notes']
            >>> ohl_ns_codes_dat['Codes'].head()
                ELR         OHNS Name  Mileage    Tracks Dates
            0  ARG1        Rutherglen  0m 03ch
            1  ARG2   Finnieston East  4m 23ch      Down
            2  ARG2   Finnieston West  4m 57ch        Up
            3  AYR1  Shields Junction  0m 68ch    Up Ayr
            4  AYR1  Shields Junction  0m 69ch  Down Ayr
        """

        ohns_data = self._collect_data_from_source(
            data_name=self.KEY_TO_OHNS, method=self._collect_elec_codes,
            parser_func=_parse_ohns_codes, confirmation_required=confirmation_required,
            confirmation_prompt=self._confirm_to_collect, verbose=verbose, raise_error=raise_error)

        return ohns_data

    def fetch_ohns_codes(self, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetches the `overhead line electrification neutral sections`_ (OHNS) codes.

        .. _`overhead line electrification neutral sections`:
            http://www.railwaycodes.org.uk/electrification/neutral.shtm

        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: Path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary of OHNS codes.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.line_data import Electrification  # from pyrcs import Electrification
            >>> elec = Electrification()
            >>> ohl_ns_codes = elec.fetch_ohns_codes()
            >>> type(ohl_ns_codes)
            dict
            >>> list(ohl_ns_codes.keys())
            ['National network neutral sections', 'Last updated date']
            >>> elec.KEY_TO_OHNS
            'National network neutral sections'
            >>> ohl_ns_codes_dat = ohl_ns_codes[elec.KEY_TO_OHNS]
            >>> type(ohl_ns_codes_dat)
            dict
            >>> list(ohl_ns_codes_dat.keys())
            ['Codes', 'Notes']
            >>> ohl_ns_codes_dat['Codes'].head()
                ELR         OHNS Name  Mileage    Tracks Dates
            0  ARG1        Rutherglen  0m 03ch
            1  ARG2   Finnieston East  4m 23ch      Down
            2  ARG2   Finnieston West  4m 57ch        Up
            3  AYR1  Shields Junction  0m 68ch    Up Ayr
            4  AYR1  Shields Junction  0m 69ch  Down Ayr
        """

        args = {'data_name': self.KEY_TO_OHNS, 'method': self.collect_ohns_codes}
        kwargs.update(args)

        ohns_codes = self._fetch_data_from_file(
            update=update, dump_dir=dump_dir, verbose=verbose, **kwargs)

        return ohns_codes

    def collect_etz_codes(self, confirmation_required=True, verbose=False, raise_error=True):
        """
        Collects OLE section codes for `national network energy tariff zones
        <http://www.railwaycodes.org.uk/electrification/tariff.shtm>`_
        from the source web page.

        :param confirmation_required: Whether user confirmation is required before proceeding;
            defaults to ``True``.
        :type confirmation_required: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :param raise_error: Whether to raise the provided exception; defaults to ``True``.
            if ``raise_error=False``, the error will be suppressed.
        :return: A dictionary of OLE section codes for national network energy tariff zones.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.line_data import Electrification  # from pyrcs import Electrification
            >>> elec = Electrification()
            >>> rail_etz_codes = elec.collect_etz_codes(verbose=True)
            To collect section codes for OLE installations: National network energy tariff zones
            ? [No]|Yes: yes
            Collecting the data ... Done.
            >>> type(rail_etz_codes)
            dict
            >>> list(rail_etz_codes.keys())
            ['National network energy tariff zones', 'Last updated date']
            >>> elec.KEY_TO_ETZ
            'National network energy tariff zones'
            >>> rail_etz_codes_dat = rail_etz_codes[elec.KEY_TO_ETZ]
            >>> type(rail_etz_codes_dat)
            dict
            >>> list(rail_etz_codes_dat.keys())
            ['Railtrack', 'Network Rail']
            >>> rail_etz_codes_dat['Railtrack']['Codes']
               Code                   Energy tariff zone
            0    EA                          East Anglia
            1    EC                 East Coast Main Line
            2    GE                      Great Eastern †
            3    LT                                LTS †
            4    MD                    Midland Main Line
            5    ME                         Merseyside †
            6    MS  Merseyside (North West DC traction)
            7    NE                           North East
            8    NL           North London (DC traction)
            9    SC                             Scotland
            10   SO                                South
            11   SW                           South West
            12   WA                        West Anglia †
            13   WC                West Coast/North West
        """

        etz_ole = self._collect_data_from_source(
            data_name=self.KEY_TO_ETZ, method=self._collect_elec_codes,
            confirmation_required=confirmation_required,
            confirmation_prompt=self._confirm_to_collect,
            verbose=verbose, raise_error=raise_error)

        return etz_ole

    def fetch_etz_codes(self, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetches OLE section codes for `national network energy tariff zones`_.

        .. _`national network energy tariff zones`:
            http://www.railwaycodes.org.uk/electrification/tariff.shtm

        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: Path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary of OLE section codes for national network energy tariff zones.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.line_data import Electrification  # from pyrcs import Electrification
            >>> elec = Electrification()
            >>> rail_etz_codes = elec.fetch_etz_codes()
            >>> type(rail_etz_codes)
            dict
            >>> list(rail_etz_codes.keys())
            ['National network energy tariff zones', 'Last updated date']
            >>> elec.KEY_TO_ETZ
            'National network energy tariff zones'
            >>> rail_etz_codes_dat = rail_etz_codes[elec.KEY_TO_ETZ]
            >>> type(rail_etz_codes_dat)
            dict
            >>> list(rail_etz_codes_dat.keys())
            ['Railtrack', 'Network Rail']
            >>> rail_etz_codes_dat['Railtrack']['Codes']
               Code                   Energy tariff zone
            0    EA                          East Anglia
            1    EC                 East Coast Main Line
            2    GE                      Great Eastern †
            3    LT                                LTS †
            4    MD                    Midland Main Line
            5    ME                         Merseyside †
            6    MS  Merseyside (North West DC traction)
            7    NE                           North East
            8    NL           North London (DC traction)
            9    SC                             Scotland
            10   SO                                South
            11   SW                           South West
            12   WA                        West Anglia †
            13   WC                West Coast/North West
        """

        args = {'data_name': self.KEY_TO_ETZ, 'method': self.collect_etz_codes}
        kwargs.update(args)

        etz_ole = self._fetch_data_from_file(
            update=update, dump_dir=dump_dir, verbose=verbose, **kwargs)

        return etz_ole

    def fetch_codes(self, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetches OLE section codes listed in the `Electrification`_ catalogue.

        .. _`Electrification`: http://www.railwaycodes.org.uk/electrification/mast_prefix0.shtm

        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: Path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary of the section codes for OLE installations.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.line_data import Electrification  # from pyrcs import Electrification
            >>> elec = Electrification()
            >>> elec_codes = elec.fetch_codes()
            >>> type(elec_codes)
            dict
            >>> list(elec_codes.keys())
            ['Electrification', 'Last updated date']
            >>> elec.KEY
            'Electrification'
            >>> elec_codes_dat = elec_codes[elec.KEY]
            >>> type(elec_codes_dat)
            dict
            >>> list(elec_codes_dat.keys())
            ['National network energy tariff zones',
             'Independent lines',
             'National network',
             'National network neutral sections']
        """

        verbose_ = fetch_all_verbose(data_dir=dump_dir, verbose=verbose)

        codes = []
        for func in dir(self):
            if re.match(r'fetch_(.*)_codes', func):
                codes.append(getattr(self, func)(update=update, verbose=verbose_))

        data = {
            self.KEY: {next(iter(x)): next(iter(x.values())) for x in codes},
            self.KEY_TO_LAST_UPDATED_DATE:
                max(next(itertools.islice(iter(x.values()), 1, 2)) for x in codes),
        }

        if dump_dir is not None:
            args = {
                'cls_instance': self,
                'data': data,
                'data_name': self.KEY,
            }
            kwargs.update(args)

            self._save_data_to_file(dump_dir=dump_dir, verbose=verbose, **kwargs)

        return data
