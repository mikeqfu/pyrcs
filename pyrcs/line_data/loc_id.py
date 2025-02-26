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
    Parses the location name and extract any associated note from the raw data.

    :param x: Location name (in raw data).
    :type x: str | None
    :return: Location name and note (if any).
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
        x_, note = '', ''

    else:
        # Location name
        d = re.search(r'.*(?= \[[\"\']\()', x)
        if d is not None:
            x_ = d.group(0)
        elif ' [unknown feature' in x:  # ' [unknown feature, labelled "do not use"]' in x
            x_ = re.search(r'\w.*(?= \[unknown feature(, )?)', x).group(0)
        elif ') [formerly' in x:
            x_ = re.search(r'.*(?= \[formerly)', x).group(0)
        elif '✖' in x:
            x_ = re.search(r'.*(?=✖)', x).group(0)
        else:
            x_tmp = re.search(r'(?=[\[(]).*(?<=[])])|(?=\().*(?<=\) \[)', x)
            if x_tmp is not None:
                x_tmp = x_tmp.group(0)
                x_pat = re.compile(r'[Oo]riginally |'
                                   r'[Ff]ormerly |'
                                   r'[Ll]ater |'
                                   r'[Pp]resumed |'
                                   r' \(was |'
                                   r' \(in |'
                                   r' \(at |'
                                   r' \(also |'
                                   r' \(second code |'
                                   r'\?|'
                                   r'\n|'
                                   r' \(\[\'|'
                                   r' \(definition unknown\)|'
                                   r' \(reopened |'
                                   r'( portion])$|'
                                   r'[Ss]ee ')
                x_ = ' '.join(x.replace(x_tmp, '').split()) if re.search(x_pat, x) else x
            else:
                x_ = x

        # Note
        y_ = x.replace(x_, '', 1).strip()
        if y_ == '':
            note = ''
        elif '✖' in y_:
            note = re.search(r'(?<=✖).*', y_).group(0)
        else:
            note_ = re.search(r'(?<=[\[(])[\w ,?]+(?=[])])', y_)
            if note_ is None:
                note_ = re.search(
                    r'(?<=(\[[\'\"]\()|(\([\'\"]\[)|(\) \[)).*(?=(\)[\'\"]])|(][\'\"]\))|])',
                    y_)
            elif '"now deleted"' in y_ and y_.startswith('(') and y_.endswith(')'):
                note_ = re.search(r'(?<=\().*(?=\))', y_)

            note = note_.group(0) if note_ is not None else ''
            if note.endswith('\'') or note.endswith('"'):
                note = note[:-1]

        if 'STANOX ' in x_ and 'STANOX ' in x and note == '':
            x_ = x[0:x.find('STANOX')].strip()
            note = x[x.find('STANOX'):]

    return x_, note


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
        # elif any(all(a_ in x for a_ in a) for a in self._extra_annotations()):
        #     temp = [
        #         x.replace(a[0], f'{a[0][:-1]}\n') for a in self._extra_annotations()
        #         if a[0] in x and x.endswith(a[1])]
        #     x = temp[0]
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

    data_ = data.copy()
    data_ = _fix_exceptional_cases(data_)

    code_col_names = ['Location', 'CRS', 'NLC', 'TIPLOC', 'STANME', 'STANOX']

    r_n_counts = data_[code_col_names].map(_count_sep)
    # # Debugging:
    # for col in code_col_names:
    #     for i, x in enumerate(data_[col]):
    #         try:
    #             lid._count_sep(x)
    #         except Exception:
    #             print(col, i, x)
    #             break
    r_n_counts_ = r_n_counts.mul(-1).add(r_n_counts.max(axis=1), axis='index')

    for col in code_col_names:
        for i in data_.index:
            d = r_n_counts_.loc[i, col]
            x = data_.loc[i, col]
            if d > 0:
                if '\r\n' in x:
                    if col == 'Location':
                        data_.loc[i, col] = x + ''.join(['\r\n' + x.split('\r\n')[-1]] * d)
                    else:
                        data_.loc[i, col] = x + ''.join(['\r\n'] * d)
                elif '\r' in x:
                    if col == 'Location':
                        data_.loc[i, col] = x + ''.join(['\r' + x.split('\r')[-1]] * d)
                    else:
                        data_.loc[i, col] = x + ''.join(['\r'] * d)
                else:  # e.g. '\n' in dat:
                    if col == 'Location':
                        data_.loc[i, col] = '\n'.join([x] * (d + 1))
                    else:
                        data_.loc[i, col] = x + ''.join(['\n'] * d)
            # elif any(all(a_ in x for a_ in a) for a in self._extra_annotations()):
            #     temp = [
            #         x.replace(a[0], f'{a[0][:-1]}\n') for a in self._extra_annotations()
            #         if a[0] in x and x.endswith(a[1])]
            #     data_.loc[i, col] = temp[0]

    data_[code_col_names] = data_[code_col_names].map(_split_dat_and_note)

    data_ = data_.explode(code_col_names, ignore_index=True)

    temp = data_.select_dtypes(['object'])
    data_[temp.columns] = temp.apply(lambda x_: x_.str.strip())

    return data_


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
    #             lid._get_code_note(x)
    #         except Exception:
    #             print(col, i, x)
    #             break

    return data


def _stanox_note(x):  # Parse STANOX note
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
            stanox = x
            note = ''

        elif re.match(r'\d{5}\*$', x):
            stanox = x.rstrip('*')
            note = 'Pseudo STANOX'

        elif re.match(r'\d{5} \w.*', x):
            stanox = re.search(r'\d{5}', x).group()
            note = re.search(r'(?<= )\w.*', x).group()

        else:
            d = re.search(r'[\w *,]+(?= [\[(\'])', x)
            stanox = d.group() if d is not None else x
            note = 'Pseudo STANOX' if '*' in stanox else ''
            n = re.search(r'(?<=[\[(\'])[\w, ]+.(?=[)\]\'])', x)

            if n is not None:
                note = '; '.join(x for x in [note, n.group()] if x != '')

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
        Parses the additional note page at the specified URL and extract its contents.

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
            >>> # from pyrcs import LocationIdentifiers
            >>> lid = LocationIdentifiers()
            >>> url = 'http://www.railwaycodes.org.uk/crs/crs2.shtm'
            >>> parsed_note_dat = lid._parse_notes_page(note_url=url)
            >>> parsed_note_dat[3]
                               Location  CRS CRS_alt1 CRS_alt2
            0           Glasgow Central  GLC      GCL
            1      Glasgow Queen Street  GLQ      GQL
            2                   Heworth  HEW      HEZ
            3      Highbury & Islington  HHY      HII      XHZ
            4    Lichfield Trent Valley  LTV      LIF
            5     Liverpool Lime Street  LIV      LVL
            6   Liverpool South Parkway  LPY      ALE
            7         London St Pancras  STP      SPL      SPX
            8                   Retford  RET      XRO
            9   Smethwick Galton Bridge  SGB      GTI
            10                 Tamworth  TAM      TAH
            11       Willesden Junction  WIJ      WJH      WJL
            12   Worcestershire Parkway  WOP      WPH
        """

        soup = bs4.BeautifulSoup(markup=source.content, features=parser)
        contents = soup.find_all(['p', 'pre'])

        raw_text = filter(
            None, [x.get_text(strip=True) for x in contents if isinstance(x.next_element, str)])

        notes = []
        for x in raw_text:
            if '\n' in x and '\t' in x:
                text = re.sub('\t+', ',', x).replace('\t', ' ').replace('\xa0', '').split('\n')
            else:
                text = x.replace('\t', ' ').replace('\xa0', '')

            if isinstance(text, list):
                text = [[x.strip() for x in t.split(',')] for t in text if t != '']
                text = [x + [''] if len(x) < 4 else x for x in text]
                temp = pd.DataFrame(text, columns=['Location', 'CRS', 'CRS_alt1', 'CRS_alt2'])
                notes.append(temp.fillna(''))
            else:
                to_remove = ['click the link', 'click your browser', 'Thank you', 'shown below']
                if text.strip() != '' and not any(t in text for t in to_remove):
                    notes.append(text)

        return notes, soup

    # -- CRS, NLC, TIPLOC and STANOX ---------------------------------------------------------------

    def _parse_crs_notes(self, data, initial, soup):
        if any('see note' in crs_note for crs_note in data['CRS_Note']):
            indices = [i for i, crs_n in enumerate(data['CRS_Note']) if 'see note' in crs_n]

            notes = []
            for x in soup.find_all('a', href=True, string='note'):
                source = requests.get(
                    url=urllib.parse.urljoin(self.catalogue[initial], x['href']),
                    headers=fake_requests_headers())

                notes.append(self._parse_notes_page(source)[0])

            loc_id_notes = dict(zip(data['CRS'].iloc[indices], notes))

        else:
            loc_id_notes = None

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
        #         _parse_location_name(x)
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
        Fetches data of `CRS, NLC, TIPLOC, STANME and STANOX codes`_ for a given initial letter.

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
            self.KEY_TO_OTHER_SYSTEMS: other_systems_codes,
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

        notes = {}
        explanatory_notes, additional_notes = {}, []

        for x in notes_dat:
            if isinstance(x, str):
                if 'Last update' not in x:
                    additional_notes.append(x)
            else:
                explanatory_notes.update({self.KEY_TO_MSCEN: x})

        notes.update(
            {self.KEY_TO_NOTES: explanatory_notes | {'Additional notes': additional_notes},
             self.KEY_TO_LAST_UPDATED_DATE: _get_last_updated_date(soup=soup)}
        )

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
            >>> explanatory_notes = lid.collect_notes()
            To collect data of multiple station codes explanatory note
            ? [No]|Yes: yes
            >>> type(explanatory_notes)
            dict
            >>> list(explanatory_notes.keys())
            ['Multiple station codes explanatory note', 'Notes', 'Last updated date']
            >>> lid.KEY_TO_MSCEN
            'Multiple station codes explanatory note'
            >>> explanatory_notes_ = explanatory_notes[lid.KEY_TO_MSCEN]
            >>> type(explanatory_notes_)
            pandas.core.frame.DataFrame
            >>> explanatory_notes_.head()
                              Location  CRS CRS_alt1 CRS_alt2
            0  Ebbsfleet International  EBD      EBF
            1          Glasgow Central  GLC      GCL
            2     Glasgow Queen Street  GLQ      GQL
            3                  Heworth  HEW      HEZ
            4     Highbury & Islington  HHY      HII      XHZ
        """

        explanatory_notes = self._collect_data_from_source(
            data_name=self.KEY_TO_MSCEN.lower(), method=self._collect_notes,
            url=self.catalogue[self.KEY_TO_MSCEN],
            confirmation_required=confirmation_required,
            confirmation_prompt=format_confirmation_prompt(data_name=self.KEY_TO_MSCEN.lower()),
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
                print("Successfully.")

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
