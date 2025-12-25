"""
Collects data of
`CRS, NLC, TIPLOC and STANOX codes <http://www.railwaycodes.org.uk/crs/crs0.shtm>`_.
"""

import collections
import re
import string
import urllib.parse

import bs4
import pandas as pd
import requests
from pyhelpers._cache import _print_failure_message
from pyhelpers.dirs import validate_dir
from pyhelpers.ops import fake_requests_headers

from .._base import _Base
from ..parser import _get_last_updated_date, get_page_catalogue, parse_tr
from ..utils import collect_in_fetch_verbose, format_confirmation_prompt, home_page_url, \
    is_home_connectable, print_inst_conn_err, print_void_msg, validate_initial


def _parse_raw_location_name(x):
    """
    Parses the location name and extracts any associated note from the raw data.

    This function separates the main location name from metadata/notes usually
    found in parentheses, brackets or separated by specific markers.

    :param x: Location name (in raw data).
    :type x: str | None
    :return: A tuple of (Location Name, Note). Returns ``('', '')`` if input is None/Empty.
    :rtype: tuple

    **Examples**::

        >>> from pyrcs.line_data.loc_id import _parse_raw_location_name
        >>> _parse_raw_location_name(None)
        ('', '')
        >>> _parse_raw_location_name('Abbey Wood')
        ('Abbey Wood', '')
        >>> _parse_raw_location_name('Abercynon (formerly Abercynon South)')
        ('Abercynon', 'formerly Abercynon South')
        >>> _parse_raw_location_name('Allerton (reopened as Liverpool South Parkway)')
        ('Allerton', 'reopened as Liverpool South Parkway')
        >>> _parse_raw_location_name('Ashford International [domestic portion]')
        ('Ashford International', 'domestic portion')
        >>> _parse_raw_location_name('Ayr [unknown feature]')
        ('Ayr', 'unknown feature')
        >>> _parse_raw_location_name('Birkenhead Hamilton Square [see Hamilton Square]')
        ('Birkenhead Hamilton Square', 'see Hamilton Square')
    """

    if not x:
        return '', ''

    x_ = x.strip()  # Clean leading/trailing whitespace

    # Handle explicit special delimiters
    if '✖' in x_:  # Check for the '✖' symbol
        name, _, note = x_.partition('✖')
        return name.strip(), note.strip()

    if 'STANOX ' in x_:  # Check for 'STANOX'
        # Split at the first occurrence of STANOX
        name, sep, note = x_.partition('STANOX')
        return name.strip(), (sep + note).strip()

    # Regex to capture: Name (Note Content) OR Name [Note Content]
    match = re.search(r'^(.*?)\s*[(\[](.+)[)\]]$', x_, re.DOTALL)

    if match:
        name_part, note_part = match.groups()

        # Keywords that identify a bracket/parenthesis as a 'Note'
        note_keywords = [
            'originally', 'formerly', 'later', 'presumed', 'was', 'reopened',
            'portion', 'see', 'unknown feature', 'definition unknown', 'now deleted', 'now'
        ]
        keyword_pattern = re.compile('|'.join(note_keywords), re.IGNORECASE)

        # Split if it contains a keyword OR if it's the standard format from your docs
        if keyword_pattern.search(note_part):
            # Use regex to strip any leading/trailing non-alphanumeric noise like ["( or )"]
            note_part = re.sub(r'^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$', '', note_part)
            return name_part.strip(), note_part.strip()

    return x_, ''


def _amendment_to_location_names():
    """
    Creates a dictionary of amendments to adjust location names using regular expressions.

    This method generates a dictionary where the keys are regular expression patterns, and the
    values are the corresponding amendments to be applied to location names.

    :return: A dictionary where each key is a regular expression pattern and each value is the
        corresponding replacement string to amend the location names.
    :rtype: dict

    **Examples**::

        >>> from pyrcs.line_data.loc_id import _amendment_to_location_names
        >>> loc_name_amendment_dict = _amendment_to_location_names()
        >>> list(loc_name_amendment_dict.keys())
        ['Location']
    """

    location_name_amendment_dict = {
        'Location': {re.compile(r' And | \+ '): ' & ',
                     re.compile(r'-By-'): '-by-',
                     re.compile(r'-In-'): '-in-',
                     re.compile(r'-En-Le-'): '-en-le-',
                     re.compile(r'-La-'): '-la-',
                     re.compile(r'-Le-'): '-le-',
                     re.compile(r'-On-'): '-on-',
                     re.compile(r'-The-'): '-the-',
                     re.compile(r' Of '): ' of ',
                     re.compile(r'-Super-'): '-super-',
                     re.compile(r'-Upon-'): '-upon-',
                     re.compile(r'-Under-'): '-under-',
                     re.compile(r'-Y-'): '-y-'}}

    return location_name_amendment_dict


def _extra_annotations():
    extra_annotations = [
        ('✖Earlier code ', '✖Later code'),
        ('✖Later code ', '✖Earlier code'),
        ('✖Earlier code, soon replaced ', '✖Later code introduced before station opened'),
        ('✖Later code introduced before station opened ', '✖Earlier code, soon replaced'),
        ('✖Original code ', '✖Later code'),
        ('✖Later code ', '✖Original code'),
        ('✖Original code ', '✖Later code from station opening'),
        ('✖Later code from station opening ', '✖Original code'),
        ('✖Newer designation? ', '✖Older designation?'),
        ('✖Older designation? ', '✖Newer designation?'),
        ('✖Both codes quoted with equal reliability ',
         '✖Both codes quoted with equal reliability'),
        ('✖Code used by operational research software ',
         '✖Code as used by National Rail Enquiries and other public systems'),
        ('✖Code as used by National Rail Enquiries and other public systems ',
         '✖Code used by operational research software'),
        ('✖Code assigned in error ', '✖Corrected code'),
        ('✖Original code ', '✖Later code after becoming part of national network'),
        ('✖Later code after becoming part of national network ', '✖Original code'),
        ('✖Code used after station reopened ', '✖Code used until station reopened'),
        ('✖Code used until station reopened ', '✖Code used after station reopened'),
        ('✖Code used after nearby station reopened ', '✖Code used until nearby station reopened'),
        ('✖Code used until nearby station reopened ', '✖Code used after nearby station reopened'),
        ('✖Original code; see also CRS explanation ', '✖Later code; see also CRS explanation'),
        ('✖Later code; see also CRS explanation ', '✖Original code; see also CRS explanation'),
        ('✖Most sources state LOUNOC, some have LOUNGOC ',
         '✖Most sources state LOUNOC, some have LOUNGOC'),
        ("✖Code may start with 'R' ", "✖Code may start with 'B'"),
        ("✖Code may start with 'B' ", "✖Code may start with 'R'"),
        ('✖Older designation when station open ', '✖Newer designation once station closed'),
        ('✖Newer designation once station closed ', '✖Older designation when station open'),
        ('✖Original code when named Butlins Penychain ', '✖Later code after renaming Penychain'),
        ('✖Later code after renaming Penychain ', '✖Original code when named Butlins Penychain'),
        ('✖Earlier code ',
         '✖Later code after East London Line operated as part of national network'),
        ('✖Code should be ROODENDGD but some listings show this as RO0DENDGD (with zero digit) ',
         '✖Code should be ROODENDGD but some listings show this as RO0DENDGD (with zero digit)'),
        ('✖Earlier code? ', '✖Later code'),
        ('✖See CRS explanation ', '✖Code believed listed in error'),
        ('✖Code is 56582 but some sources have 56782 ',
         '✖Code is 56582 but some sources have 56782'),
        ('✖Code should be 79251 but one source has 79521 ',
         '✖Code should be 79251 but one source has 79521'),
        ('✖Code is 56540 but some sources have 56450 ',
         '✖Code is 56540 but some sources have 56450'),
        ('✖Earlier code ', '✖Later code; also see CRS explanation'),
        ('✖Later code ', '✖Possibly earlier code'),
        ('✖Code is 142505 but is also reported as 145505 ',
         '✖Code is 142505 but is also reported as 145505'),
        ('✖Earlier code ', '✖Later code after station closed'),
    ]

    return extra_annotations


def _count_sep(x):
    if '\r\n' in x:
        r_n_counts = x.count('\r\n')
    elif '\r' in x:
        r_n_counts = x.count('\r')
    else:  # Ad hoc
        if '~LO\n' in x:
            x = x.replace('~LO\n', '')
        r_n_counts = x.count('\n')
    return r_n_counts


def _split_dat_and_note(x):
    if '\r\n' in x:
        x_ = x.split('\r\n')

    elif '\r' in x:
        x_ = x.split('\r')

    elif '\n' in x:
        if '~LO\n' in x:  # Ad hoc
            x = x.replace('~LO\n', '')
        x_ = x.split('\n')

    else:
        x_ = x

    return x_


def _fix_exceptional_cases(data):
    x1 = 'Ely Papworth Sidings English Welsh & Scottish Railway International\n' \
         'Ely Papworth Sidings DB Schenker International'

    if x1 in data['Location'].values:
        x1_ = 'Ely Papworth Sidings English Welsh & Scottish Railway International\n' \
              'Ely Papworth Sidings DB Schenker International\n' \
              'Ely Papworth Sidings DB Schenker International'

        data.loc[data['Location'] == x1, 'Location'] = x1_

    return data


def _parse_mult_alt_codes(data):
    """
    Cleanses multiple alternatives for every code column.

    :param data: The preprocessed data of the location codes.
    :type data: pandas.DataFrame
    :return: The cleansed data of the location codes where multiple alternatives are replicated.
    :rtype: pandas.DataFrame
    """

    df = data.copy()
    df = _fix_exceptional_cases(df)

    code_cols = ['Location', 'CRS', 'NLC', 'TIPLOC', 'STANME', 'STANOX']

    r_n_counts = df[code_cols].map(_count_sep)
    # # Debugging:
    # for col in code_col_names:
    #     for i, x in enumerate(data_[col]):
    #         try:
    #             lid._count_sep(x)
    #         except Exception:
    #             print(col, i, x)
    #             break
    r_n_counts_ = r_n_counts.mul(-1).add(r_n_counts.max(axis=1), axis='index')

    for col in code_cols:
        for i in df.index:
            d = r_n_counts_.loc[i, col]
            val = df.loc[i, col]
            if d > 0:
                if '\r\n' in val:
                    if col == 'Location':
                        df.loc[i, col] = val + ''.join(['\r\n' + val.split('\r\n')[-1]] * d)
                    else:
                        df.loc[i, col] = val + ''.join(['\r\n'] * d)
                elif '\r' in val:
                    if col == 'Location':
                        df.loc[i, col] = val + ''.join(['\r' + val.split('\r')[-1]] * d)
                    else:
                        df.loc[i, col] = val + ''.join(['\r'] * d)
                else:  # e.g. '\n' in dat:
                    if col == 'Location':
                        df.loc[i, col] = '\n'.join([val] * (d + 1))
                    else:
                        df.loc[i, col] = val + ''.join(['\n'] * d)

    df[code_cols] = df[code_cols].map(_split_dat_and_note)

    df = df.explode(code_cols, ignore_index=True)

    temp = df.select_dtypes(['object'])
    df[temp.columns] = temp.apply(lambda x_: x_.str.strip())

    return df


def _parse_code_note(x):
    """
    Gets note for every code column.

    :param x: The raw data of a given code.
    :type x: str | None
    :return: The extra information (if any) about the given code.
    :rtype: str

    **Examples**::

        >>> from pyrcs.line_data.loc_id import _parse_code_note
        >>> _parse_code_note('860260✖Earlier code')
        ('860260', 'Earlier code')
    """

    if not x:
        y, note = x, ''

    else:
        if '✖' in x:
            y, note = map(str.strip, x.split('✖', 1))

        else:  # Search for notes
            n1 = re.search(r'(?<=[\[(])[\w,? ]+(?=[)\]])', x)

            if n1:
                note = n1.group(0)
                y = x.replace(note, '').strip('[(\')] ')

                n2 = re.search(r'[\w ,]+(?= [\[(\'])', note)  # Remove redundant characters
                if n2:
                    note = n2.group(0)

            else:
                y, note = x.strip(), ''  # Default case: No note found

    return y, note


def _parse_code_notes(data):
    """
    Gets notes for every code column.

    :param data: The preprocessed data of the location codes.
    :type data: pandas.DataFrame
    """

    codes_col_names = ['CRS', 'NLC', 'TIPLOC', 'STANME', 'STANOX']

    for col in codes_col_names:
        data[[col, col + '_Note']] = pd.DataFrame(
            data[col].map(_parse_code_note).to_list(), index=data.index)
    # # Debugging:
    # for col in codes_col_names:
    #     for i, x in enumerate(data[col]):
    #         try:
    #             _parse_code_note(x)
    #         except Exception:
    #             print(col, i, x)
    #             break
    return data


def _stanox_note(x):
    """
    Parses STANOX note.

    :param x: STANOX note.
    :type x: str | None
    :return: STANOX and its corresponding note.
    :rtype: tuple
    """

    if x in ('-', '') or x is None:
        stanox, note = '', ''

    else:
        if re.match(r'\d{5}$', x):
            stanox, note = x, ''

        elif re.match(r'\d{5}\*$', x):
            stanox, note = x.rstrip('*'), 'Pseudo STANOX'

        elif re.match(r'\d{5} \w.*', x):
            stanox = re.search(r'\d{5}', x).group()
            note = re.search(r'(?<= )\w.*', x).group()

        else:
            d = re.search(r'[\w *,]+(?= [\[(\'])', x)
            stanox = d.group().strip() if d is not None else x

            # Check for Pseudo STANOX marker before stripping it
            note = 'Pseudo STANOX' if '*' in stanox else ''
            stanox = stanox.rstrip('*')

            # Extract notes within brackets/quotes
            n = re.search(r'(?<=[\[(\'])[\w, ]+.(?=[)\]\'])', x)

            if n is not None:
                note = '; '.join(item for item in [note, n.group()] if item != '')

            if '(' not in note and note.endswith(')'):
                note = note.rstrip(')')

    return stanox, note


def _parse_stanox_note(data):
    """
    Parses the note for STANOX.

    :param data: The preprocessed data of the location codes.
    :type data: pandas.DataFrame
    """

    col_name = 'STANOX'
    note_col_name = col_name + '_Note'

    # noinspection SpellCheckingInspection
    data[col_name] = data[col_name].str.replace('NANAN', '')

    if not data.empty:
        parsed_dat = data[col_name].map(_stanox_note).to_list()
        data[[col_name, note_col_name]] = pd.DataFrame(parsed_dat, index=data.index)
    else:
        # No data is available on the web page for the given 'key_word'
        data[note_col_name] = data[col_name]

    data[col_name] = data[col_name].str.replace('-', '')

    return data


def _fill_location_names(data):
    """
    Fills missing or empty code values based on other rows sharing the same 'Location' name.

    :param data: Input DataFrame with station data.
    :return: DataFrame with populated code columns.
    """

    df = data.copy()
    code_cols = ['CRS', 'NLC', 'TIPLOC', 'STANME', 'STANOX']  # The code columns to be filled

    # Standardise empty strings/None to NA so pandas recognises them as 'missing'
    for col in code_cols:
        df[col] = df[col].replace(r'^\s*$', pd.NA, regex=True)

    # Group and fill
    with pd.option_context('future.no_silent_downcasting', True):
        # Group by 'Location' and apply forward then backward fill
        df[code_cols] = df.groupby('Location', sort=False)[code_cols].transform(
            lambda x: x.ffill().bfill())

    # Replace any remaining NaNs back with empty strings (optional)
    df[code_cols] = df[code_cols].astype(object).fillna('')

    return df


def _parse_note_page_pre_span(pre_span):
    lines = [line.strip() for line in pre_span.decode_contents().splitlines() if line.strip()]

    data = []
    for line in lines:
        temp = bs4.BeautifulSoup(line, "html.parser")
        spans = temp.find_all('span')
        texts = [span.get_text(strip=True) for span in spans]

        # Remaining text after last span (e.g. "BLU", "EBF")
        remaining = temp.get_text(strip=True)
        for t in texts:
            remaining = remaining.replace(t, '', 1)
        remaining = remaining.strip()

        row = texts + ([remaining] if remaining else [])  # Build row: [Location, CRS1, CRS2, ..., ]
        data.append(row)

    if not data:
        return pd.DataFrame()

    # Determine dynamic column width
    max_len = max(len(row) for row in data)

    # Header: 'location_name' followed by incrementing CRS numbers
    columns = ['location_name'] + [f'CRS{i}' for i in range(1, max_len)]
    # Pad rows with empty strings to match max_len
    padded_data = [row + [''] * (max_len - len(row)) for row in data]

    return pd.DataFrame(padded_data, columns=columns)


def _format_structured_note(text):
    # noinspection PyShadowingNames
    """
    Formats a raw string of tab-separated notes into a structured DataFrame.

    This helper processes text blocks where data is organised by lines and delimited by tabs
    or multiple commas. It dynamically scales the number of 'CRS' columns based on the row
    with the most data points.

    :param text: Raw note text containing newline and tab characters.
    :type text: str
    :return: A structured DataFrame with columns ``['Location', 'CRS', 'CRS1', ...]``.
        Returns an empty DataFrame if required delimiters are not present.
    :rtype: pandas.DataFrame

    **Examples**::

        >>> from pyrcs.line_data.loc_id import _format_structured_note
        >>> text = "Abbey Wood\\tABW\\nAllerton\\tALN\\tLVP\\tLSP"
        >>> df = _format_structured_note(text)
        >>> df.columns.tolist()
        ['Location', 'CRS', 'CRS1']
    """

    if not text:
        return pd.DataFrame()

    # Normalise potential literal string escapes from web data
    # This ensures consistency across Windows/Unix and different scrape sources
    normalised_text = text.replace('\\t', '\t').replace('\\n', '\n').replace('\\r', '')

    if '\t' not in normalised_text:
        return pd.DataFrame()

    # Split into lines and remove empty strings
    lines = [line.strip() for line in normalised_text.splitlines() if line.strip()]

    processed_data = []
    max_cols = 0
    for line in lines:
        # Split by tabs or sequences of commas
        parts = [p.strip() for p in re.split(r'\t+|,+', line)]
        processed_data.append(parts)
        max_cols = max(max_cols, len(parts))

    if max_cols == 0:
        return pd.DataFrame()

    # Standardise columns: ['Location', 'CRS', 'CRS1', 'CRS2'...]
    columns = ['Location', 'CRS1']
    effective_max = max(2, max_cols)
    if effective_max > 2:
        columns += [f'CRS{i}' for i in range(2, effective_max)]

    # Match data to column length
    final_data = [row + [''] * (len(columns) - len(row)) for row in processed_data]

    return pd.DataFrame(final_data, columns=columns[:max_cols])


class LocationIdentifiers(_Base):
    """
    A class for collecting data of location identifiers
    (including `CRS, NLC, TIPLOC and STANOX codes <http://www.railwaycodes.org.uk/crs/crs0.shtm>`_
    and `other systems' station codes <http://www.railwaycodes.org.uk/crs/crs1.shtm>`_).

    The class retrieves and organises location identifiers for various railway stations and
    other related systems.
    """

    #: The name of the data.
    NAME: str = 'CRS, NLC, TIPLOC and STANOX codes'
    #: The key for accessing the data.
    KEY: str = 'Location ID'

    #: The URL of the main web page for the data.
    URL: str = urllib.parse.urljoin(home_page_url(), '/crs/crs0.shtm')

    #: The key for accessing the data of *other systems*.
    KEY_TO_OTHER_SYSTEMS: str = 'Other systems'
    #: The key for accessing the data of *multiple station codes explanatory note*.
    KEY_TO_MSCEN: str = 'Multiple station codes explanatory note'
    #: The key for accessing the data of *additional notes*.
    KEY_TO_NOTES: str = 'Notes'

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

        **Examples**::

            >>> from pyrcs.line_data import LocationIdentifiers
            >>> # from pyrcs import LocationIdentifiers
            >>> lid = LocationIdentifiers()
            >>> lid.NAME
            'CRS, NLC, TIPLOC and STANOX codes'
            >>> lid.URL
            'http://www.railwaycodes.org.uk/crs/crs0.shtm'
        """

        # data_cluster = re.sub(r",| codes| and", "", self.NAME.lower()).replace(" ", "-")
        super().__init__(
            data_dir=data_dir, content_type='catalogue', data_category="line-data",
            data_cluster="crs-nlc-tiploc-stanox", update=update, verbose=verbose)

        # Adds the multiple station codes explanatory note (MSCEN) to the catalogue
        mscen_url = urllib.parse.urljoin(home_page_url(), '/crs/crs2.shtm')
        self.catalogue.update({self.KEY_TO_MSCEN: mscen_url})

        # Retrieve the catalogue for other systems' station codes
        other_systems_url = self.catalogue[self.KEY_TO_OTHER_SYSTEMS]
        self.other_systems_catalogue = get_page_catalogue(url=other_systems_url)

    @staticmethod
    def _parse_notes_page(source, parser='html.parser'):
        """
        Parses the additional note page at the specified URL and extracts its contents.

        :param parser: The `parser`_ to use with `bs4.BeautifulSoup`_
            (e.g. ``'html.parser'``, ``'lxml'``); defaults to ``'html.parser'``.
        :type parser: str
        :return: A list of parsed text elements from the web page.
        :rtype: list

        .. _`parser`:
            https://www.crummy.com/software/BeautifulSoup/bs4/doc/
            index.html#specifying-the-parser-to-use
        .. _`bs4.BeautifulSoup`:
            https://www.crummy.com/software/BeautifulSoup/bs4/doc/index.html

        **Examples**::

            >>> from pyrcs.line_data import LocationIdentifiers
            >>> from pyhelpers.ops import fake_requests_headers
            >>> import requests
            >>> # from pyrcs import LocationIdentifiers
            >>> lid = LocationIdentifiers()
            >>> url = 'http://www.railwaycodes.org.uk/crs/crs2.shtm'
            >>> response = requests.get(url, headers=fake_requests_headers())
            >>> parsed_note_dat, _ = lid._parse_notes_page(response)
            >>> parsed_note_dat[3]
                          location_name CRS1 CRS2 CRS3
            0                 Bletchley  BLY  BLU
            1   Ebbsfleet International  EBD  EBF
            2           Glasgow Central  GLC  GCL
            3      Glasgow Queen Street  GLQ  GQL
            4                   Heworth  HEW  HEZ
            5      Highbury & Islington  HHY  HII  XHZ
            6    Lichfield Trent Valley  LTV  LIF
            7     Liverpool Lime Street  LIV  LVL
            8   Liverpool South Parkway  LPY  ALE
            9         London St Pancras  STP  SPL  SPX
            10                  Retford  RET  XRO
            11                 Tamworth  TAM  TAH
            12       Willesden Junction  WIJ  WJH  WJL
            13   Worcestershire Parkway  WOP  WPH
        """

        if not source or not source.ok:
            return [], None

        soup = bs4.BeautifulSoup(markup=source.content, features=parser)
        raw_elements = []

        # Extract elements from the page
        for x in soup.find_all(['p', 'pre']):
            if x.name == 'pre':
                raw_elements.append(_parse_note_page_pre_span(x))
            else:  # Check if the paragraph has direct string content
                text = x.get_text().strip().replace('  ', ' ')
                if text:
                    raw_elements.append(text)

        # Process elements into notes
        notes = []
        to_remove = {'click the link', 'click your browser', 'thank you', 'shown below'}

        for x in raw_elements:
            if isinstance(x, pd.DataFrame):
                notes.append(x)
            elif isinstance(x, str):
                if '\t' in x or '\\t' in x:  # If it looks like structured tab data
                    notes.append(_format_structured_note(x))
                else:  # Filter out boilerplate strings
                    if not any(phrase in x.lower() for phrase in to_remove):
                        notes.append(x)

        return notes, soup

    # -- CRS, NLC, TIPLOC and STANOX ---------------------------------------------------------------

    def _parse_crs_notes(self, data, initial, soup):
        # Identify rows that actually need a note lookup
        mask = data['CRS_Note'].str.contains('see note', case=False, na=False)
        if not mask.any():
            return None

        indices = data.index[mask].tolist()

        # Extract the specific 'note' links from the soup
        note_links = soup.find_all('a', href=True, string=re.compile(r'note', re.I))

        loc_id_notes = {}
        with requests.Session() as session:  # Using a Session is faster for multiple requests
            session.headers.update(fake_requests_headers())

            for idx, link_tag in zip(indices, note_links):
                crs_code = data.at[idx, 'CRS']
                # noinspection PyBroadException
                try:
                    url = urllib.parse.urljoin(self.catalogue[initial], link_tag['href'])
                    response = session.get(url, timeout=10)

                    parsed_content, _ = self._parse_notes_page(response)
                    # Get the first element if it's a list
                    loc_id_notes[crs_code] = parsed_content[0] if parsed_content else None

                except Exception:
                    loc_id_notes[crs_code] = None

        return loc_id_notes

    def _collect_loc_id(self, initial, source, verbose=False):
        initial_ = validate_initial(x=initial)

        # url = lid.catalogue[initial_]
        # source = requests.get(url)
        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

        thead, tbody = soup.find('thead'), soup.find('tbody')
        ths, trs = [th.get_text(strip=True) for th in thead.find_all('th')], tbody.find_all('tr')

        dat = parse_tr(trs=trs, ths=ths, sep=None, as_dataframe=True)
        dat = dat.replace({'\b-\b': '', '\xa0\xa0': ' ', '&half;': ' and 1/2'}, regex=True)

        data = dat.replace({'\xa0': ''}, regex=True)

        # Parse location names and their corresponding notes
        data[['Location', 'Location_Note']] = pd.DataFrame(  # Collect additional info as note
            data['Location'].map(_parse_raw_location_name).to_list())
        # # Debugging
        # for i, x in enumerate(data['Location']):
        #     try:
        #         _parse_raw_location_name(x)
        #     except Exception:
        #         print(i)
        #         break
        data.replace(_amendment_to_location_names(), regex=True, inplace=True)

        # Cleanse multiple alternatives for every code column
        data = _parse_mult_alt_codes(data=data)

        # Parse note for every code column
        data = _parse_code_notes(data=data)

        # Parse STANOX note
        data = _parse_stanox_note(data=data)

        # Fills missing or empty code values based on other rows sharing the same 'Location' name.
        data = _fill_location_names(data)

        loc_codes = {
            initial_: data,
            self.KEY_TO_NOTES: self._parse_crs_notes(data=data, initial=initial_, soup=soup),
            self.KEY_TO_LAST_UPDATED_DATE: _get_last_updated_date(soup=soup),
        }

        if verbose in {True, 1}:
            print("Done.")

        self._save_data_to_file(data=loc_codes, data_name=initial_, sub_dir="a-z", verbose=verbose)

        return loc_codes

    def collect_loc_id(self, initial, confirmation_required=True, verbose=False, raise_error=False):
        """
        Collects `CRS, NLC, TIPLOC, STANME and STANOX codes
        <http://www.railwaycodes.org.uk/crs/crs0.shtm>`_ for a given initial letter.

        :param initial: The initial letter (e.g. ``'a'``, ``'z'``) of a location name.
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
        :return: A dictionary containing data of locations whose names start with the given
            initial letter, along with the date of the last update.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.line_data import LocationIdentifiers
            >>> # from pyrcs import LocationIdentifiers
            >>> lid = LocationIdentifiers()
            >>> loc_a_codes = lid.collect_loc_id(initial='a')
            To collect data of CRS, NLC, TIPLOC and STANOX codes beginning with "A"
            ? [No]|Yes: yes
            >>> type(loc_a_codes)
            dict
            >>> list(loc_a_codes.keys())
            ['A', 'Additional notes', 'Last updated date']
            >>> loc_a_codes_dat = loc_a_codes['A']
            >>> type(loc_a_codes_dat)
            pandas.core.frame.DataFrame
            >>> loc_a_codes_dat.head()
                                          Location CRS  ... STANME_Note STANOX_Note
            0                 1999 Reorganisations      ...
            1                                   A1      ...
            2                       A463 Traded In      ...
            3  A483 Road Scheme Supervisors Closed      ...
            4                               Aachen      ...
            [5 rows x 12 columns]
        """

        initial_ = validate_initial(x=initial)

        loc_id_data = self._collect_data_from_source(
            data_name=self.NAME, method=self._collect_loc_id, initial=initial_,
            additional_fields=self.KEY_TO_NOTES, confirmation_required=confirmation_required,
            verbose=verbose, raise_error=raise_error)

        return loc_id_data

    def fetch_loc_id(self, initial=None, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetches data of `CRS, NLC, TIPLOC, STANME and STANOX codes`_.

        .. _`CRS, NLC, TIPLOC, STANME and STANOX codes`:
            http://www.railwaycodes.org.uk/crs/crs0.shtm

        :param initial: The initial letter (e.g. ``'a'``, ``'z'``) of a location name.
        :type initial: str
        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: Path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``True``.
        :type verbose: bool | int
        :return: A dictionary containing data of locations whose names start with the given
            initial letter, along with the date of the last update.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.line_data import LocationIdentifiers
            >>> # from pyrcs import LocationIdentifiers
            >>> lid = LocationIdentifiers()
            >>> loc_a_codes = lid.fetch_loc_id(initial='a')
            >>> type(loc_a_codes)
            dict
            >>> list(loc_a_codes.keys())
            ['A', 'Additional notes', 'Last updated date']
            >>> loc_a_codes_dat = loc_a_codes['A']
            >>> type(loc_a_codes_dat)
            pandas.core.frame.DataFrame
            >>> loc_a_codes_dat.head()
                                          Location CRS  ... STANME_Note STANOX_Note
            0                 1999 Reorganisations      ...
            1                                   A1      ...
            2                       A463 Traded In      ...
            3  A483 Road Scheme Supervisors Closed      ...
            4                               Aachen      ...
            [5 rows x 12 columns]
            >>> loc_codes = lid.fetch_loc_id()
            >>> list(loc_codes.keys())
            ['Location ID', 'Last updated date']
            >>> loc_codes[lid.KEY].shape
            (59873, 12)
        """

        if initial:
            args = {
                'data_name': validate_initial(initial),
                'method': self.collect_loc_id,
                'sub_dir': "a-z",
                'initial': initial,
            }
            kwargs.update(args)

            loc_id_data = self._fetch_data_from_file(
                update=update, dump_dir=dump_dir, verbose=verbose, **kwargs)

        else:
            verbose_1 = collect_in_fetch_verbose(data_dir=dump_dir, verbose=verbose)

            # Get every data table
            verbose_2 = verbose_1 if is_home_connectable() else False
            dat_list = [
                self.fetch_loc_id(initial=x, update=update, verbose=verbose_2)
                for x in string.ascii_lowercase]

            if all(d[x] is None for d, x in zip(dat_list, string.ascii_uppercase)):
                if update:
                    print_inst_conn_err(verbose=verbose)
                    print_void_msg(data_name=self.KEY, verbose=verbose)

                dat_list = [
                    self.fetch_loc_id(initial=x, update=False, verbose=verbose_1)
                    for x in string.ascii_lowercase]

            # Select DataFrames only
            data = pd.concat(
                (item[x] for item, x in zip(dat_list, string.ascii_uppercase)), ignore_index=True)

            # Get the latest updated date
            last_updated_dates = (
                item[self.KEY_TO_LAST_UPDATED_DATE]
                for item, _ in zip(dat_list, string.ascii_uppercase))
            latest_update_date = max(d for d in last_updated_dates if d is not None)

            loc_id_data = {self.KEY: data, self.KEY_TO_LAST_UPDATED_DATE: latest_update_date}

        return loc_id_data

    # -- Other systems -----------------------------------------------------------------------------

    @staticmethod
    def _parse_code(x):
        protocol = 'https://'

        if '; ' in x and protocol in x:
            temp = x.split('; ')
            x0, x1 = temp[0], [y.split(protocol) for y in temp if protocol in y][0]
            x1 = ' ('.join([x1[0], protocol + x1[1]]) + ')'
            x_ = [x0, x1]
        else:
            x_ = [x, '']

        return x_

    def _parse_tbl_dat(self, h3_or_h4):
        tbl_dat = h3_or_h4.find_next('thead'), h3_or_h4.find_next('tbody')
        thead, tbody = tbl_dat
        ths = [x.text for x in thead.find_all('th')]
        trs = tbody.find_all('tr')
        tbl = parse_tr(trs=trs, ths=ths, as_dataframe=True)

        if 'Code' in tbl.columns:
            if tbl.Code.str.contains('https://').sum() > 0:
                temp = tbl['Code'].map(self._parse_code)
                tbl_ext = pd.DataFrame(zip(*temp)).T
                tbl_ext.columns = ['Code', 'Code_extra']
                del tbl['Code']
                tbl = pd.concat([tbl, tbl_ext], axis=1, sort=False)

        return tbl

    def _collect_other_systems_codes(self, source, verbose=False):
        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

        other_systems_codes = collections.defaultdict(dict)

        for h3 in soup.find_all('h3'):
            h4 = h3.find_next('h4')

            if h4 is not None:
                while h4:
                    prev_h3 = h4.find_previous('h3')
                    if prev_h3.text == h3.text:
                        other_systems_codes[h3.text].update(
                            {h4.text: self._parse_tbl_dat(h4)})
                        h4 = h4.find_next('h4')
                    elif h3.text not in other_systems_codes.keys():
                        other_systems_codes.update({h3.text: self._parse_tbl_dat(h3)})
                        break
                    else:
                        break
            else:
                other_systems_codes.update({h3.text: self._parse_tbl_dat(h3)})

        other_systems_codes = {
            self.KEY_TO_OTHER_SYSTEMS: dict(other_systems_codes),
            self.KEY_TO_LAST_UPDATED_DATE: _get_last_updated_date(soup=soup),
        }

        if verbose in {True, 1}:
            print("Done.")

        self._save_data_to_file(
            data=other_systems_codes, data_name=self.KEY_TO_OTHER_SYSTEMS, verbose=verbose)

        return other_systems_codes

    def collect_other_systems_codes(self, confirmation_required=True, verbose=False,
                                    raise_error=False):
        """
        Collects data of `other systems' station codes`_ from the source web page.

        .. _`other systems' station codes`: http://www.railwaycodes.org.uk/crs/crs1.shtm

        :param confirmation_required: Whether user confirmation is required before proceeding;
            defaults to ``True``.
        :type confirmation_required: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :param raise_error: Whether to raise the provided exception; defaults to ``True``.
            if ``raise_error=False``, the error will be suppressed.
        :type raise_error: bool
        :return: A dictionary containing station codes for other systems,
            or ``None`` if no data is collected.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.line_data import LocationIdentifiers
            >>> # from pyrcs import LocationIdentifiers
            >>> lid = LocationIdentifiers()
            >>> os_codes = lid.collect_other_systems_codes()
            To collect data of Other systems
            ? [No]|Yes: yes
            >>> type(os_codes)
            dict
            >>> list(os_codes.keys())
            ['Other systems', 'Last updated date']
            >>> lid.KEY_TO_OTHER_SYSTEMS
            'Other systems'
            >>> os_codes_dat = os_codes[lid.KEY_TO_OTHER_SYSTEMS]
            >>> type(os_codes_dat)
            dict
            >>> list(os_codes_dat.keys())
            ['Córas Iompair Éireann (Republic of Ireland)',
             'Crossrail',
             'Croydon Tramlink',
             'Docklands Light Railway',
             'Manchester Metrolink',
             'Translink (Northern Ireland)',
             'Tyne & Wear Metro']
        """

        other_systems_codes = self._collect_data_from_source(
            data_name=self.KEY_TO_OTHER_SYSTEMS.lower(), method=self._collect_other_systems_codes,
            url=self.catalogue[self.KEY_TO_OTHER_SYSTEMS],
            confirmation_required=confirmation_required, verbose=verbose, raise_error=raise_error)

        return other_systems_codes

    def fetch_other_systems_codes(self, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetches data of `other systems' station codes`_.

        .. _`other systems' station codes`: http://www.railwaycodes.org.uk/crs/crs1.shtm

        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing station codes for other systems.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.line_data import LocationIdentifiers
            >>> # from pyrcs import LocationIdentifiers
            >>> lid = LocationIdentifiers()
            >>> os_codes = lid.fetch_other_systems_codes()
            >>> type(os_codes)
            dict
            >>> list(os_codes.keys())
            ['Other systems', 'Last updated date']
            >>> lid.KEY_TO_OTHER_SYSTEMS
            'Other systems'
            >>> os_codes_dat = os_codes[lid.KEY_TO_OTHER_SYSTEMS]
            >>> type(os_codes_dat)
            collections.defaultdict
            >>> list(os_codes_dat.keys())
            ['Córas Iompair Éireann (Republic of Ireland)',
             'Crossrail',
             'Croydon Tramlink',
             'Docklands Light Railway',
             'Manchester Metrolink',
             'Translink (Northern Ireland)',
             'Tyne & Wear Metro']
        """

        kwargs.update(
            {'data_name': self.KEY_TO_OTHER_SYSTEMS, 'method': self.collect_other_systems_codes})

        other_systems_codes = self._fetch_data_from_file(
            update=update, dump_dir=dump_dir, verbose=verbose, **kwargs)

        return other_systems_codes

    # -- Additional notes --------------------------------------------------------------------------

    def _collect_notes(self, source, verbose=False, parser='html.parser'):
        notes_dat, soup = self._parse_notes_page(source=source, parser=parser)

        notes = {
            self.KEY_TO_NOTES: {self.KEY_TO_MSCEN: [x for x in notes_dat if 'Last update' not in x]},
            self.KEY_TO_LAST_UPDATED_DATE: _get_last_updated_date(soup=soup),
        }

        if verbose in {True, 1}:
            print("Done.")

        self._save_data_to_file(data=notes, data_name=self.KEY_TO_NOTES, verbose=verbose)

        return notes

    def collect_notes(self, confirmation_required=True, verbose=False, raise_error=False):
        # noinspection PyShadowingNames
        """
        Collects the explanatory note related to multiple station codes (CRS codes)
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
        :return: A dictionary containing the data of the multiple station codes explanatory note,
            or ``None`` if the note is not found or the collection is not performed.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.line_data import LocationIdentifiers
            >>> # from pyrcs import LocationIdentifiers
            >>> lid = LocationIdentifiers()
            >>> notes = lid.collect_notes()
            To collect data of multiple station codes explanatory note
            ? [No]|Yes: yes
            >>> type(notes)
            dict
            >>> list(notes.keys())
            ['Notes', 'Last updated date']
            >>> lid.KEY_TO_NOTES
            'Notes'
            >>> notes_ = notes[lid.KEY_TO_NOTES]
            >>> type(notes_)
            dict
            >>> notes_[lid.KEY_TO_MSCEN][2].head()
                         location_name CRS1 CRS2 CRS3
            0                Bletchley  BLY  BLU
            1  Ebbsfleet International  EBD  EBF
            2          Glasgow Central  GLC  GCL
            3     Glasgow Queen Street  GLQ  GQL
            4                  Heworth  HEW  HEZ
        """

        explanatory_notes = self._collect_data_from_source(
            data_name="additional notes", method=self._collect_notes,
            url=self.catalogue[self.KEY_TO_MSCEN],
            confirmation_required=confirmation_required,
            confirmation_prompt=format_confirmation_prompt(data_name="additional notes"),
            verbose=verbose, raise_error=raise_error)

        return explanatory_notes

    def fetch_notes(self, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetches the explanatory note for multiple station codes (CRS codes).

        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the data of the multiple station codes explanatory note.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.line_data import LocationIdentifiers
            >>> # from pyrcs import LocationIdentifiers
            >>> lid = LocationIdentifiers()
            >>> exp_note = lid.fetch_notes()
            >>> type(exp_note)
            dict
            >>> list(exp_note.keys())
            ['Multiple station codes explanatory note', 'Notes', 'Last updated date']
            >>> lid.KEY_TO_MSCEN
            'Multiple station codes explanatory note'
            >>> exp_note_dat = exp_note[lid.KEY_TO_MSCEN]
            >>> type(exp_note_dat)
            pandas.core.frame.DataFrame
            >>> exp_note_dat.head()
                             Location  CRS CRS_alt1 CRS_alt2
            0         Glasgow Central  GLC      GCL
            1    Glasgow Queen Street  GLQ      GQL
            2                 Heworth  HEW      HEZ
            3    Highbury & Islington  HHY      HII      XHZ
            4  Lichfield Trent Valley  LTV      LIF
        """

        kwargs.update({'data_name': self.KEY_TO_NOTES, 'method': self.collect_notes})

        explanatory_note = self._fetch_data_from_file(
            update=update, dump_dir=dump_dir, verbose=verbose, **kwargs)

        return explanatory_note

    # -- All codes ---------------------------------------------------------------------------------

    def fetch_codes(self, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetches location codes listed in the `CRS, NLC, TIPLOC and STANOX codes`_ catalogue
        (including `other systems' station codes`_).

        .. _`CRS, NLC, TIPLOC and STANOX codes`:
            http://www.railwaycodes.org.uk/crs/crs0.shtm
        .. _`other systems' station codes`:
            http://www.railwaycodes.org.uk/crs/crs1.shtm

        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing location codes and date of when the data was last updated.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.line_data import LocationIdentifiers
            >>> # from pyrcs import LocationIdentifiers
            >>> lid = LocationIdentifiers()
            >>> loc_codes = lid.fetch_codes()
            >>> type(loc_codes)
            dict
            >>> list(loc_codes.keys())
            ['Location ID', 'Other systems', 'Additional notes', 'Last updated date']
            >>> lid.KEY
            'LocationID'
            >>> loc_codes_dat = loc_codes[lid.KEY]
            >>> type(loc_codes_dat)
            pandas.core.frame.DataFrame
            >>> loc_codes_dat.head()
                                          Location CRS  ... STANME_Note STANOX_Note
            0                 1999 Reorganisations      ...
            1                                   A1      ...
            2                       A463 Traded In      ...
            3  A483 Road Scheme Supervisors Closed      ...
            4                               Aachen      ...
            [5 rows x 12 columns]
        """

        verbose_ = collect_in_fetch_verbose(data_dir=dump_dir, verbose=verbose)

        loc_id_data = self.fetch_loc_id(update=update, verbose=verbose_)

        # Get other systems codes
        other_systems_codes = self.fetch_other_systems_codes(update=update, verbose=verbose_)

        # Get explanatory notes
        explanatory_notes = self.fetch_notes(update=update, verbose=verbose_)

        keys = [self.KEY, self.KEY_TO_OTHER_SYSTEMS, self.KEY_TO_NOTES]
        data_list = [loc_id_data, other_systems_codes, explanatory_notes]

        location_codes = {}
        for dat, key in zip(data_list, keys):
            if dat is None:
                location_codes.update({key: None})
            else:
                for k, v in dat.items():
                    if k != self.KEY_TO_LAST_UPDATED_DATE:
                        location_codes.update({k: v})

        # Get the latest updated date
        latest_update_date = max(d[self.KEY_TO_LAST_UPDATED_DATE] for d in filter(None, data_list))

        # Create a dict to include all information
        location_codes.update({self.KEY_TO_LAST_UPDATED_DATE: latest_update_date})

        if dump_dir:
            kwargs.update({'data': location_codes, 'data_name': self.KEY})
            self._save_data_to_file(dump_dir=dump_dir, verbose=verbose, **kwargs)

        return location_codes

    @staticmethod
    def _make_xref_dict(location_codes, keys, drop_duplicates=False, as_dict=False, main_key=None):
        # Extract relevant columns and remove empty rows
        key_locid = location_codes[['Location'] + keys].query(
            ' | '.join([f"{k} != ''" for k in keys]))

        # Further clean location_code
        if drop_duplicates:
            location_codes_ref = key_locid.drop_duplicates(keys, keep='first').set_index(keys)

        else:  # drop_duplicates is False or None
            locid_unique = key_locid.drop_duplicates(subset=keys, keep=False)

            dupl_temp_1 = key_locid[key_locid.duplicated(['Location'] + keys, keep=False)]
            dupl_temp_2 = key_locid[key_locid.duplicated(keys, keep=False)]
            duplicated_1 = dupl_temp_2[dupl_temp_1.eq(dupl_temp_2)].dropna().drop_duplicates()
            duplicated_2 = dupl_temp_2[~dupl_temp_1.eq(dupl_temp_2)].dropna()
            duplicated_entries = pd.concat([duplicated_1, duplicated_2], axis=0)

            grouped_duplicates = duplicated_entries.groupby(keys).agg(tuple)
            grouped_duplicates['Location'] = grouped_duplicates['Location'].map(
                lambda x: x[0] if len(set(x)) == 1 else x)

            locid_unique.set_index(keys, inplace=True)
            location_codes_ref = pd.concat([locid_unique, grouped_duplicates])

        if as_dict:
            location_codes_dict = location_codes_ref.to_dict()
            if main_key:
                location_codes_dict = {main_key: location_codes_dict.pop('Location')}
            else:
                location_codes_dict = location_codes_dict['Location']

        else:
            location_codes_dict = location_codes_ref

        return location_codes_dict

    def make_xref_dict(self, keys, initials=None, drop_duplicates=False, as_dict=False,
                       main_key=None, update=False, dump_it=False, dump_dir=None, verbose=False):
        """
        Creates a dictionary or dataframe containing location code data for the specified ``keys``.

        :param keys: A string or list of keys from ``['CRS', 'NLC', 'TIPLOC', 'STANOX', 'STANME']``
            representing the location codes.
        :type keys: str | list
        :param initials: A string or list of initials for which the codes are filtered;
            defaults to ``None``.
        :type initials: str | list | None
        :param drop_duplicates: If ``True``, removes duplicate entries from the result;
            defaults to ``False``.
        :type drop_duplicates: bool
        :param as_dict: If ``True``, returns the result as a dictionary;
            otherwise, returns a dataframe; defaults to ``False``.
        :type as_dict: bool
        :param main_key: The key used for the returned dictionary when ``as_dict=True``;
            defaults to ``None``.
        :type main_key: str | None
        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_it: If ``True``, saves the result to a file; defaults to ``False``.
        :type dump_it: bool
        :param dump_dir: The directory path where the file can be saved, if ``dump_it=True``;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary or dataframe containing cross-reference location data
            for the specified ``keys``, or ``None`` if no data is available.
        :rtype: dict | pandas.DataFrame | None

        **Examples**::

            >>> from pyrcs.line_data import LocationIdentifiers
            >>> # from pyrcs import LocationIdentifiers
            >>> lid = LocationIdentifiers()
            >>> stanox_dict = lid.make_xref_dict(keys='STANOX')
            >>> type(stanox_dict)
            pandas.core.frame.DataFrame
            >>> stanox_dict.head()
                                      Location
            STANOX
            00005                       Aachen
            04309           Abbeyhill Junction
            04311        Abbeyhill Signal E811
            04308   Abbeyhill Turnback Sidings
            88601                   Abbey Wood
            >>> s_t_dictionary = lid.make_xref_dict(keys=['STANOX', 'TIPLOC'], initials='a')
            >>> type(s_t_dictionary)
            pandas.core.frame.DataFrame
            >>> s_t_dictionary.head()
                                              Location
            STANOX TIPLOC
            00005  AACHEN                       Aachen
            04309  ABHLJN           Abbeyhill Junction
            04311  ABHL811       Abbeyhill Signal E811
            04308  ABHLTB   Abbeyhill Turnback Sidings
            88601  ABWD                     Abbey Wood
            >>> ks = ['STANOX', 'TIPLOC']
            >>> ini = 'b'
            >>> main_k = 'Data'
            >>> s_t_dictionary = lid.make_xref_dict(ks, ini, main_k, as_dict=True)
            >>> type(s_t_dictionary)
            dict
            >>> list(s_t_dictionary.keys())
            ['Data']
            >>> list(s_t_dictionary['Data'].keys())[:5]
            [('55115', ''),
             ('23490', 'BABWTHL'),
             ('38306', 'BACHE'),
             ('66021', 'BADESCL'),
             ('81003', 'BADMTN')]
        """

        valid_keys = {'CRS', 'NLC', 'TIPLOC', 'STANOX', 'STANME'}
        if isinstance(keys, str):
            keys = [keys]
        if not all(k in valid_keys for k in keys):
            raise ValueError(f"`keys` must be one of {valid_keys}, but got {keys}.")

        if main_key and not isinstance(main_key, str):
            raise TypeError("`main_key` must be a string.")

        # Validate `initials`
        if initials:
            if isinstance(initials, str):
                initials = [validate_initial(initials, as_is=True)]
            elif not all(isinstance(x, str) and x in string.ascii_letters for x in initials):
                raise ValueError("`initials` must be a string or a list of letters.")

            dat_list = [
                self.fetch_loc_id(x, update=update, verbose=verbose).get(x.upper())
                for x in initials]
            location_codes = pd.concat(dat_list, ignore_index=True)

        else:
            location_codes = self.fetch_codes(update=update, verbose=verbose).get(self.KEY)

        if verbose == 2:
            print("Generating location code dictionary", end=" ... ")

        try:
            location_codes_dict = self._make_xref_dict(
                location_codes, keys=keys, drop_duplicates=drop_duplicates, as_dict=as_dict,
                main_key=main_key)

            if verbose == 2:
                print("Done.")

            if dump_it:
                self._save_data_to_file(
                    data=location_codes_dict,
                    data_name="-".join(keys) + (f"-{''.join(initials)}" if initials else ""),
                    ext=".json" if as_dict and len(keys) == 1 else ".pkl",
                    dump_dir=validate_dir(dump_dir) if dump_dir else self._cdd("xref-dicts"),
                    verbose=verbose)

            return location_codes_dict

        except Exception as e:
            _print_failure_message(e)
