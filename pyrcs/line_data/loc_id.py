"""
Collect `CRS, NLC, TIPLOC and STANOX codes <http://www.railwaycodes.org.uk/crs/CRS0.shtm>`_.
"""

import copy
import os
import re
import string
import urllib.parse

import bs4
import pandas as pd
import requests
from pyhelpers.dir import cd, validate_input_data_dir
from pyhelpers.ops import confirmed, fake_requests_headers, split_list_by_size
from pyhelpers.store import load_json, load_pickle, save, save_pickle

from pyrcs.utils import cd_dat, homepage_url, get_catalogue, get_last_updated_date, \
    parse_date, parse_location_name, parse_table, parse_tr, print_conn_err, \
    is_internet_connected, print_connection_error


class LocationIdentifiers:
    """
    A class for collecting location identifiers
    (including `other systems <http://www.railwaycodes.org.uk/crs/CRS1.shtm>`_ station).

    :param data_dir: name of data directory, defaults to ``None``
    :type data_dir: str or None
    :param update: whether to check on update and proceed to update the package data,
        defaults to ``False``
    :type update: bool
    :param verbose: whether to print relevant information in console as the function runs,
        defaults to ``True``
    :type verbose: bool or int

    :ivar str Name: name of the data
    :ivar str Key: key of the dict-type data
    :ivar str HomeURL: URL of the main homepage
    :ivar str SourceURL: URL of the data web page
    :ivar str LUDKey: key of the last updated date
    :ivar str LUD: last updated date
    :ivar dict Catalogue: catalogue of the data
    :ivar str DataDir: path to the data directory
    :ivar str CurrentDataDir: path to the current data directory

    :ivar str OtherSystemsKey: key of the dict-type data of other systems
    :ivar str OtherSystemsPickle: name of the pickle file of other systems data
    :ivar str AddNotesKey: key of the dict-type data of additional notes
    :ivar str MscENKey: key of the dict-type data of multiple station codes explanatory note
    :ivar str MscENPickle: name of the pickle file of multiple station codes explanatory note

    **Example**::

        >>> from pyrcs.line_data import LocationIdentifiers

        >>> lid = LocationIdentifiers()

        >>> print(lid.Name)
        CRS, NLC, TIPLOC and STANOX codes

        >>> print(lid.SourceURL)
        http://www.railwaycodes.org.uk/crs/crs0.shtm
    """

    def __init__(self, data_dir=None, update=False, verbose=True):
        """
        Constructor method.
        """
        if not is_internet_connected():
            print_connection_error(verbose=verbose)

        self.Name = 'CRS, NLC, TIPLOC and STANOX codes'
        self.Key = 'Location codes'  # key to location codes

        self.HomeURL = homepage_url()
        self.SourceURL = urllib.parse.urljoin(self.HomeURL, '/crs/crs0.shtm')

        self.LUDKey = 'Last updated date'  # key to last updated date
        self.LUD = get_last_updated_date(url=self.SourceURL, parsed=True, as_date_type=False)

        if data_dir:
            self.DataDir = validate_input_data_dir(data_dir)
        else:
            self.DataDir = cd_dat(
                "line-data", re.sub(r',| codes| and', '', self.Name.lower()).replace(" ", "-"))
        self.CurrentDataDir = copy.copy(self.DataDir)

        self.OtherSystemsKey = 'Other systems'  # key to other systems codes
        self.OtherSystemsPickle = self.OtherSystemsKey.lower().replace(" ", "-")
        self.AddNotesKey = 'Additional notes'  # key to additional notes
        self.MscENKey = 'Multiple station codes explanatory note'
        self.MscENPickle = self.MscENKey.lower().replace(" ", "-")

        self.Catalogue = get_catalogue(page_url=self.SourceURL, update=update,
                                       confirmation_required=False)
        self.Catalogue.update(
            {self.MscENKey: urllib.parse.urljoin(self.HomeURL, '/crs/crs2.shtm')})

    def _cdd_locid(self, *sub_dir, **kwargs):
        """
        Change directory to package data directory and sub-directories (and/or a file).

        The directory for this module: ``"\\dat\\line-data\\crs-nlc-tiploc-stanox"``.

        :param sub_dir: sub-directory or sub-directories (and/or a file)
        :type sub_dir: str
        :param kwargs: optional parameters of
            `os.makedirs <https://docs.python.org/3/library/os.html#os.makedirs>`_,
            e.g. ``mode=0o777``
        :return: path to the backup data directory for ``LocationIdentifiers``
        :rtype: str

        :meta private:
        """

        path = cd(self.DataDir, *sub_dir, mkdir=True, **kwargs)

        return path

    @staticmethod
    def amendment_to_loc_names():
        """
        Create a replacement dictionary for location name amendments.

        :return: dictionary of regular-expression amendments to location names
        :rtype: dict

        **Example**::

            >>> from pyrcs.line_data import LocationIdentifiers

            >>> lid = LocationIdentifiers()

            >>> loc_name_amendment_dict = lid.amendment_to_loc_names()

            >>> print(loc_name_amendment_dict.keys())
            dict_keys(['Location'])
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

    @staticmethod
    def parse_note_page(note_url, parser='lxml', verbose=False):
        """
        Parse addition note page.

        :param note_url: URL link of the target web page
        :type note_url: str
        :param parser: the `parser`_ to use for `bs4.BeautifulSoup`_, defaults to ``'lxml'``
        :type parser: str
        :param verbose: whether to print relevant information in console as the function runs,
            defaults to ``False``
        :type verbose: bool or int
        :return: parsed texts
        :rtype: list

        .. _`parser`:
            https://www.crummy.com/software/BeautifulSoup/bs4/doc/
            index.html#specifying-the-parser-to-use
        .. _`bs4.BeautifulSoup`:
            https://www.crummy.com/software/BeautifulSoup/bs4/doc/index.html

        **Example**::

            >>> from pyrcs.line_data import LocationIdentifiers

            >>> lid = LocationIdentifiers()

            >>> url = lid.Catalogue[lid.MscENKey]
            >>> parsed_note_dat = lid.parse_note_page(url, parser='lxml')

            >>> print(parsed_note_dat[3].head())
                             Location  CRS CRS_alt1 CRS_alt2
            0    Glasgow Queen Street  GLQ      GQL
            1         Glasgow Central  GLC      GCL
            2                 Heworth  HEW      HEZ
            3    Highbury & Islington  HHY      HII      XHZ
            4  Lichfield Trent Valley  LTV      LIF
        """

        try:
            source = requests.get(note_url, headers=fake_requests_headers())
        except requests.ConnectionError:
            print_conn_err(verbose=verbose)
            return None

        web_page_text = bs4.BeautifulSoup(source.text, parser).find_all(['p', 'pre'])
        parsed_text = [x.text for x in web_page_text if isinstance(x.next_element, str)]

        parsed_note = []
        for x in parsed_text:
            if '\n' in x:
                text = re.sub('\t+', ',', x).replace('\t', ' '). \
                    replace('\xa0', '').split('\n')
            else:
                text = x.replace('\t', ' ').replace('\xa0', '')

            if isinstance(text, list):
                text = [[x.strip() for x in t.split(',')] for t in text if t != '']
                temp = pd.DataFrame(
                    text, columns=['Location', 'CRS', 'CRS_alt1', 'CRS_alt2']).fillna('')
                parsed_note.append(temp)
            else:
                to_remove = ['click the link',
                             'click your browser',
                             'Thank you',
                             'shown below']
                if text != '' and not any(t in text for t in to_remove):
                    parsed_note.append(text)

        return parsed_note

    def collect_explanatory_note(self, confirmation_required=True, verbose=False):
        """
        Collect note about CRS code from source web page.

        :param confirmation_required: whether to prompt a message for confirmation to proceed,
            defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console as the function runs,
            defaults to ``False``
        :type verbose: bool or int
        :return: data of multiple station codes explanatory note
        :rtype: dict or None

        **Example**::

            >>> from pyrcs.line_data import LocationIdentifiers

            >>> lid = LocationIdentifiers()

            >>> exp_note = lid.collect_explanatory_note(confirmation_required=False)

            >>> type(exp_note)
            dict
            >>> list(exp_note.keys())
            ['Multiple station codes explanatory note', 'Notes', 'Last updated date']

            >>> print(exp_note['Multiple station codes explanatory note'].head())
                             Location  CRS CRS_alt1 CRS_alt2
            0    Glasgow Queen Street  GLQ      GQL
            1         Glasgow Central  GLC      GCL
            2                 Heworth  HEW      HEZ
            3    Highbury & Islington  HHY      HII      XHZ
            4  Lichfield Trent Valley  LTV      LIF
        """

        if confirmed("To collect data of {}?".format(self.MscENKey.lower()),
                     confirmation_required=confirmation_required):

            if verbose == 2:
                print("Collecting data of {}".format(self.MscENKey.lower()), end=" ... ")

            explanatory_note_ = self.parse_note_page(self.Catalogue[self.MscENKey], verbose=False)

            if explanatory_note_ is None:
                print("Failed. ") if verbose == 2 else ""
                if not is_internet_connected():
                    print_conn_err(verbose=verbose)
                explanatory_note = None

            else:
                try:
                    explanatory_note, notes = {}, []

                    for x in explanatory_note_:
                        if isinstance(x, str):
                            if 'Last update' in x:
                                explanatory_note.update(
                                    {self.LUDKey: parse_date(x, as_date_type=False)})
                            else:
                                notes.append(x)
                        else:
                            explanatory_note.update({self.MscENKey: x})

                    explanatory_note.update({'Notes': notes})

                    # Rearrange the dict
                    explanatory_note = {
                        k: explanatory_note[k] for k in [self.MscENKey, 'Notes', self.LUDKey]}

                    print("Done.") if verbose == 2 else ""

                    save_pickle(explanatory_note, self._cdd_locid(self.MscENPickle + ".pickle"),
                                verbose=verbose)

                except Exception as e:
                    print("Failed. {}.".format(e))
                    explanatory_note = None

            return explanatory_note

    def fetch_explanatory_note(self, update=False, pickle_it=False, data_dir=None,
                               verbose=False):
        """
        Fetch multiple station codes explanatory note from local backup.

        :param update: whether to check on update and proceed to update the package data,
            defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data with newly collected data,
            defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console as the function runs,
            defaults to ``False``
        :type verbose: bool or int
        :return: data of multiple station codes explanatory note
        :rtype: dict

        **Example**::

            >>> from pyrcs.line_data import LocationIdentifiers

            >>> lid = LocationIdentifiers()

            >>> # exp_note = lid.fetch_explanatory_note(update=True, verbose=True)
            >>> exp_note = lid.fetch_explanatory_note()

            >>> type(exp_note)
            dict
            >>> list(exp_note.keys())
            ['Multiple station codes explanatory note', 'Notes', 'Last updated date']

            >>> print(exp_note['Multiple station codes explanatory note'].head())
                             Location  CRS CRS_alt1 CRS_alt2
            0    Glasgow Queen Street  GLQ      GQL
            1         Glasgow Central  GLC      GCL
            2                 Heworth  HEW      HEZ
            3    Highbury & Islington  HHY      HII      XHZ
            4  Lichfield Trent Valley  LTV      LIF
        """

        path_to_pickle = self._cdd_locid(self.MscENPickle + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            explanatory_note = load_pickle(path_to_pickle)

        else:
            verbose_ = False if data_dir or not verbose else (2 if verbose == 2 else True)
            explanatory_note = self.collect_explanatory_note(
                confirmation_required=False, verbose=verbose_)

            if explanatory_note:  # additional_note is not None
                if pickle_it and data_dir:
                    self.CurrentDataDir = validate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, self.MscENPickle + ".pickle")
                    save_pickle(explanatory_note, path_to_pickle, verbose=verbose)
            else:
                print("No data of {} has been freshly collected.".format(self.MscENKey.lower()))
                explanatory_note = load_pickle(path_to_pickle)

        return explanatory_note

    def collect_other_systems_codes(self, confirmation_required=True, verbose=False):
        """
        Collect data of `other systems' codes <http://www.railwaycodes.org.uk/crs/CRS1.shtm>`_
        from source web page.

        :param confirmation_required: whether to require users to confirm and proceed,
            defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console as the function runs,
            defaults to ``False``
        :type verbose: bool or int
        :return: codes of other systems
        :rtype: dict or None

        **Example**::

            >>> from pyrcs.line_data import LocationIdentifiers

            >>> lid = LocationIdentifiers()

            >>> os_codes = lid.collect_other_systems_codes(confirmation_required=False)

            >>> type(os_codes)
            dict
            >>> list(os_codes.keys())
            ['Other systems', 'Last updated date']

            >>> type(os_codes['Other systems'])
            dict
            >>> list(os_codes['Other systems'].keys())
            ['Córas Iompair Éireann (Republic of Ireland)',
             'Crossrail',
             'Croydon Tramlink',
             'Docklands Light Railway',
             'Manchester Metrolink',
             'Translink (Northern Ireland)',
             'Tyne & Wear Metro']
        """

        if confirmed("To collect data of {}?".format(self.OtherSystemsKey.lower()),
                     confirmation_required=confirmation_required):

            url = self.Catalogue['Other systems']

            if verbose == 2:
                print("Collecting data of {}".format(self.OtherSystemsKey.lower()), end=" ... ")

            other_systems_codes = None

            try:
                source = requests.get(url, headers=fake_requests_headers())
            except requests.ConnectionError:
                print("Failed. ") if verbose == 2 else ""
                print_conn_err(verbose=verbose)

            else:
                try:
                    web_page_text = bs4.BeautifulSoup(source.text, 'lxml')

                    # Get system name
                    system_names = [k.text for k in web_page_text.find_all('h3')]

                    # Parse table data for each system
                    table_data = list(
                        split_list_by_size(web_page_text.find_all('table'), sub_len=2))

                    tables = []
                    for table in table_data:
                        headers = [x.text for x in table[0].find_all('th')]
                        tbl_dat = table[1].find_all('tr')
                        tbl_data = pd.DataFrame(parse_tr(headers, tbl_dat), columns=headers)
                        tables.append(tbl_data)

                    # Make a dict
                    other_systems_codes = {self.OtherSystemsKey: dict(zip(system_names, tables)),
                                           self.LUDKey: get_last_updated_date(url)}

                    print("Done.") if verbose == 2 else ""

                    save_pickle(
                        other_systems_codes, self._cdd_locid(self.OtherSystemsPickle + ".pickle"),
                        verbose=verbose)

                except Exception as e:
                    print("Failed. {}.".format(e))

            return other_systems_codes

    def fetch_other_systems_codes(self, update=False, pickle_it=False, data_dir=None,
                                  verbose=False):
        """
        Fetch data of `other systems' codes
        <http://www.railwaycodes.org.uk/crs/CRS1.shtm>`_ from local backup.

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
        :type verbose: bool or int
        :return: codes of other systems
        :rtype: dict

        **Example**::

            >>> from pyrcs.line_data import LocationIdentifiers

            >>> lid = LocationIdentifiers()

            >>> # os_codes = lid.fetch_other_systems_codes(update=True, verbose=True)
            >>> os_codes = lid.fetch_other_systems_codes()

            >>> type(os_codes)
            dict
            >>> list(os_codes.keys())
            ['Other systems', 'Last updated date']

            >>> type(os_codes['Other systems'])
            dict
            >>> list(os_codes['Other systems'].keys())
            ['Córas Iompair Éireann (Republic of Ireland)',
             'Crossrail',
             'Croydon Tramlink',
             'Docklands Light Railway',
             'Manchester Metrolink',
             'Translink (Northern Ireland)',
             'Tyne & Wear Metro']
        """

        path_to_pickle = self._cdd_locid(self.OtherSystemsPickle + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            other_systems_codes = load_pickle(path_to_pickle)

        else:
            verbose_ = False if data_dir or not verbose else (2 if verbose == 2 else True)

            other_systems_codes = self.collect_other_systems_codes(
                confirmation_required=False, verbose=verbose_)

            if other_systems_codes:  # other_systems_codes is not None
                if pickle_it and data_dir:
                    self.CurrentDataDir = validate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(
                        self.CurrentDataDir, self.OtherSystemsPickle + ".pickle")
                    save_pickle(other_systems_codes, path_to_pickle, verbose=verbose)

            else:
                print("No data of {} has been freshly collected.".format(
                    self.OtherSystemsKey.lower()))
                other_systems_codes = load_pickle(path_to_pickle)

        return other_systems_codes

    def collect_loc_codes_by_initial(self, initial, update=False, verbose=False):
        """
        Collect `CRS, NLC, TIPLOC, STANME and STANOX codes
        <http://www.railwaycodes.org.uk/crs/CRS0.shtm>`_ for a given ``initial`` letter.

        :param initial: initial letter of station/junction name or certain word
            for specifying URL
        :type initial: str
        :param update: whether to check on update and proceed to update the package data, 
            defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console as the function runs,
            defaults to ``False``
        :type verbose: bool or int
        :return: data of location codes for the given ``initial`` letter;
            and date of when the data was last updated
        :rtype: dict

        **Example**::

            >>> from pyrcs.line_data import LocationIdentifiers

            >>> lid = LocationIdentifiers()

            >>> location_codes_a = lid.collect_loc_codes_by_initial(initial='a')

            >>> type(location_codes_a)
            dict
            >>> list(location_codes_a.keys())
            ['A', 'Additional notes', 'Last updated date']

            >>> print(location_codes_a['A'].head())
                                           Location CRS  ... STANME_Note STANOX_Note
            0                                Aachen      ...
            1                    Abbeyhill Junction      ...
            2                 Abbeyhill Signal E811      ...
            3            Abbeyhill Turnback Sidings      ...
            4  Abbey Level Crossing (Staffordshire)      ...
            [5 rows x 12 columns]
        """

        assert initial in string.ascii_letters
        beginning_with = initial.upper()

        path_to_pickle = self._cdd_locid("a-z", initial.lower() + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            location_codes_initial = load_pickle(path_to_pickle)

        else:
            url = self.Catalogue[beginning_with]

            if verbose == 2:
                print("Collecting data of locations starting with \"{}\"".format(
                    beginning_with), end=" ... ")

            location_codes_initial = {beginning_with: None,
                                      self.AddNotesKey: None,
                                      self.LUDKey: None}

            try:
                source = requests.get(url, headers=fake_requests_headers())
            except requests.ConnectionError:
                print("Failed. ") if verbose == 2 else ""
                print_conn_err(verbose=verbose)

            else:
                try:
                    tbl_lst, header = parse_table(source, parser='lxml')

                    # Get a raw DataFrame
                    reps = {'\b-\b': '', '\xa0\xa0': ' ', '&half;': ' and 1/2'}
                    pattern = re.compile("|".join(reps.keys()))
                    tbl_lst = [
                        [pattern.sub(lambda x: reps[x.group(0)], item) for item in record]
                        for record in tbl_lst]
                    loc_codes = pd.DataFrame(tbl_lst, columns=header)
                    loc_codes.replace({'\xa0': ''}, regex=True, inplace=True)

                    # Collect additional information as note
                    loc_codes[['Location', 'Location_Note']] = \
                        loc_codes.Location.map(parse_location_name).apply(pd.Series)

                    # CRS, NLC, TIPLOC, STANME
                    drop_pattern = re.compile(r'[Ff]ormerly|[Ss]ee[ also]|Also .[\w ,]+')
                    idx = [loc_codes[loc_codes.CRS == x].index[0]
                           for x in loc_codes.CRS if re.match(drop_pattern, x)]
                    loc_codes.drop(labels=idx, axis=0, inplace=True)

                    # Collect others note
                    def collect_others_note(other_note_x):
                        n = re.search(r'(?<=[\[(\'])[\w,? ]+(?=[)\]\'])', other_note_x)
                        note = n.group() if n is not None else ''
                        return note

                    # Strip others note
                    def strip_others_note(other_note_x):
                        d = re.search(r'[\w ,]+(?= [\[(\'])', other_note_x)
                        dat = d.group() if d is not None else other_note_x
                        return dat

                    other_codes_col = loc_codes.columns[1:-1]
                    other_notes_col = [x + '_Note' for x in other_codes_col]
                    loc_codes[other_notes_col] = \
                        loc_codes[other_codes_col].applymap(collect_others_note)
                    loc_codes[other_codes_col] = \
                        loc_codes[other_codes_col].applymap(strip_others_note)

                    # Parse STANOX note
                    def parse_stanox_note(x):
                        if x in ('-', ''):
                            dat, note = '', ''
                        else:
                            if re.match(r'\d{5}$', x):
                                dat = x
                                note = ''
                            elif re.match(r'\d{5}\*$', x):
                                dat = x.rstrip('*')
                                note = 'Pseudo STANOX'
                            elif re.match(r'\d{5} \w.*', x):
                                dat = re.search(r'\d{5}', x).group()
                                note = re.search(r'(?<= )\w.*', x).group()
                            else:
                                d = re.search(r'[\w *,]+(?= [\[(\'])', x)
                                dat = d.group() if d is not None else x
                                note = 'Pseudo STANOX' if '*' in dat else ''
                                n = re.search(r'(?<=[\[(\'])[\w, ]+.(?=[)\]\'])', x)
                                if n is not None:
                                    note = '; '.join(x for x in [note, n.group()] if x != '')
                                if '(' not in note and note.endswith(')'):
                                    note = note.rstrip(')')
                        return dat, note

                    if not loc_codes.empty:
                        loc_codes[['STANOX', 'STANOX_Note']] = loc_codes.STANOX.map(
                            parse_stanox_note).apply(pd.Series)
                    else:
                        # No data is available on the web page for the given 'key_word'
                        loc_codes['STANOX_Note'] = loc_codes.STANOX

                    if any('see note' in crs_note for crs_note in loc_codes.CRS_Note):
                        loc_idx = [i for i, crs_note in enumerate(loc_codes.CRS_Note)
                                   if 'see note' in crs_note]

                        web_page_text = bs4.BeautifulSoup(source.text, 'lxml')

                        note_urls = [urllib.parse.urljoin(
                            self.Catalogue[beginning_with], x['href'])
                            for x in web_page_text.find_all('a', href=True, text='note')]
                        add_notes = [self.parse_note_page(note_url) for note_url in note_urls]

                        additional_notes = dict(zip(loc_codes.CRS.iloc[loc_idx], add_notes))

                    else:
                        additional_notes = None

                    loc_codes = loc_codes.replace(self.amendment_to_loc_names(), regex=True)

                    loc_codes.STANOX = loc_codes.STANOX.replace({'-': ''})

                    loc_codes.index = range(len(loc_codes))  # Rearrange index

                    last_updated_date = get_last_updated_date(url)

                    print("Done.") if verbose == 2 else ""

                    location_codes_initial.update({beginning_with: loc_codes,
                                                   self.AddNotesKey: additional_notes,
                                                   self.LUDKey: last_updated_date})

                    save_pickle(location_codes_initial, path_to_pickle, verbose=verbose)

                except Exception as e:
                    print("Failed. {}.".format(e))

        return location_codes_initial

    def fetch_location_codes(self, update=False, pickle_it=False, data_dir=None,
                             verbose=False):
        """
        Fetch `CRS, NLC, TIPLOC, STANME and STANOX codes
        <http://www.railwaycodes.org.uk/crs/CRS0.shtm>`_ from local backup.

        :param update: whether to check on update and proceed to update the package data, 
            defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data with newly collected data,
            defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console as the function runs,
            defaults to ``False``
        :type verbose: bool or int
        :return: data of location codes and date of when the data was last updated
        :rtype: dict

        **Example**::

            >>> from pyrcs.line_data import LocationIdentifiers

            >>> lid = LocationIdentifiers()

            >>> # loc_codes = lid.fetch_location_codes(update=True, verbose=True)
            >>> loc_codes = lid.fetch_location_codes()

            >>> type(loc_codes)
            dict
            >>> list(loc_codes.keys())
            ['Location codes', 'Other systems', 'Additional notes', 'Last updated date']

            >>> print(loc_codes['Location codes'].head())
                                           Location CRS  ... STANME_Note STANOX_Note
            0                                Aachen      ...
            1                    Abbeyhill Junction      ...
            2                 Abbeyhill Signal E811      ...
            3            Abbeyhill Turnback Sidings      ...
            4  Abbey Level Crossing (Staffordshire)      ...
            [5 rows x 12 columns]
        """

        verbose_ = False if (data_dir or not verbose) else (2 if verbose == 2 else True)

        # Get every data table
        data = [
            self.collect_loc_codes_by_initial(
                x, update, verbose=verbose_ if is_internet_connected() else False)
            for x in string.ascii_lowercase]

        if all(d[x] is None for d, x in zip(data, string.ascii_uppercase)):
            if update:
                print_conn_err(verbose=verbose)
                print("No data of the {} has been freshly collected.".format(self.Key.lower()))
            data = [self.collect_loc_codes_by_initial(x, update=False, verbose=verbose_)
                    for x in string.ascii_lowercase]

        # Select DataFrames only
        location_codes_data = (item[x] for item, x in zip(data, string.ascii_uppercase))
        location_codes_data_table = pd.concat(
            location_codes_data, axis=0, ignore_index=True, sort=False)

        # Likely errors (spotted occasionally)
        idx = location_codes_data_table[
            location_codes_data_table.Location == 'Selby Melmerby Estates'].index
        values = location_codes_data_table.loc[idx, 'STANME':'STANOX'].values
        location_codes_data_table.loc[idx, 'STANME':'STANOX'] = ['', '']
        idx = location_codes_data_table[
            location_codes_data_table.Location == 'Selby Potter Group'].index
        location_codes_data_table.loc[idx, 'STANME':'STANOX'] = values

        # Get the latest updated date
        last_updated_dates = (item[self.LUDKey] for item, _ in zip(data, string.ascii_uppercase))
        latest_update_date = max(d for d in last_updated_dates if d is not None)

        # Get other systems codes
        other_systems_codes = self.fetch_other_systems_codes(
            update=update, verbose=verbose_)[self.OtherSystemsKey]

        # Get additional note
        additional_notes = self.fetch_explanatory_note(
            update=update, verbose=verbose_)

        # Create a dict to include all information
        location_codes = {self.Key: location_codes_data_table,
                          self.OtherSystemsKey: other_systems_codes,
                          self.AddNotesKey: additional_notes,
                          self.LUDKey: latest_update_date}

        if pickle_it and data_dir:
            self.CurrentDataDir = validate_input_data_dir(data_dir)
            path_to_pickle = os.path.join(
                self.CurrentDataDir, self.Key.lower().replace(" ", "-") + ".pickle")
            save_pickle(location_codes, path_to_pickle, verbose=verbose)

        return location_codes

    def make_loc_id_dict(self, keys, initials=None, drop_duplicates=False, as_dict=False,
                         main_key=None, save_it=False, data_dir=None, update=False,
                         verbose=False):
        """
        Make a dict/dataframe for location code data for the given ``keys``.

        :param keys: one or a sublist of ['CRS', 'NLC', 'TIPLOC', 'STANOX', 'STANME']
        :type keys: str or list
        :param initials: one or a sequence of initials for which the location codes are used,
            defaults to ``None``
        :type initials: str or list or None
        :param drop_duplicates: whether to drop duplicates, defaults to ``False``
        :type drop_duplicates: bool
        :param as_dict: whether to return a dictionary, defaults to ``False``
        :type as_dict: bool
        :param main_key: key of the returned dictionary if ``as_dict`` is ``True``,
            defaults to ``None``
        :type main_key: str or None
        :param save_it: whether to save the location codes dictionary, defaults to ``False``
        :type save_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str or None
        :param update: whether to check on update and proceed to update the package data, 
            defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console as the function runs,
            defaults to ``False``
        :type verbose: bool or int
        :return: dictionary or a data frame for location code data for the given ``keys``
        :rtype: dict or pandas.DataFrame or None

        **Examples**::

            >>> from pyrcs.line_data import LocationIdentifiers

            >>> lid = LocationIdentifiers()

            >>> key = 'STANOX'
            >>> stanox_dictionary = lid.make_loc_id_dict(key)

            >>> print(stanox_dictionary.head())
                                      Location
            STANOX
            00005                       Aachen
            04309           Abbeyhill Junction
            04311        Abbeyhill Signal E811
            04308   Abbeyhill Turnback Sidings
            88601                   Abbey Wood

            >>> ks = ['STANOX', 'TIPLOC']
            >>> ini = 'a'

            >>> stanox_dictionary = lid.make_loc_id_dict(ks, ini)

            >>> print(stanox_dictionary.head())
                                              Location
            STANOX TIPLOC
            00005  AACHEN                       Aachen
            04309  ABHLJN           Abbeyhill Junction
            04311  ABHL811       Abbeyhill Signal E811
            04308  ABHLTB   Abbeyhill Turnback Sidings
            88601  ABWD                     Abbey Wood

            >>> ks = ['STANOX', 'TIPLOC']
            >>> ini = 'b'

            >>> stanox_dictionary = lid.make_loc_id_dict(ks, ini, as_dict=True, main_key='Data')

            >>> type(stanox_dictionary)
            dict
            >>> list(stanox_dictionary['Data'].keys())[:5]
            [('55115', ''),
             ('23490', 'BABWTHL'),
             ('38306', 'BACHE'),
             ('66021', 'BADESCL'),
             ('81003', 'BADMTN')]
        """

        valid_keys = {'CRS', 'NLC', 'TIPLOC', 'STANOX', 'STANME'}

        if isinstance(keys, str):
            assert keys in valid_keys
            keys = [keys]
        elif isinstance(keys, list):
            assert all(x in valid_keys for x in keys)

        if initials:
            if isinstance(initials, str):
                assert initials in string.ascii_letters
                initials = [initials]
            else:  # e.g. isinstance(initials, list)
                assert all(x in string.ascii_letters for x in initials)

        if main_key:
            assert isinstance(main_key, str)

        dat_dir = validate_input_data_dir(data_dir) if data_dir else self.DataDir
        path_to_file = os.path.join(
            dat_dir,
            "-".join(keys) + ("" if initials is None else "-" + "".join(initials)) +
            (".json" if as_dict and len(keys) == 1 else ".pickle"))

        if os.path.isfile(path_to_file) and not update:
            if as_dict:
                location_codes_dictionary = load_json(path_to_file)
            else:
                location_codes_dictionary = load_pickle(path_to_file)

        else:
            if initials is None:
                location_codes = self.fetch_location_codes(verbose=verbose)[self.Key]
            else:
                temp = [
                    self.collect_loc_codes_by_initial(initial, verbose=verbose)[
                        initial.upper()]
                    for initial in initials]
                location_codes = pd.concat(temp, axis=0, ignore_index=True, sort=False)

            if verbose == 2:
                print("To make/update a location code dictionary", end=" ... ")

            # Deep cleansing location_code
            try:
                key_location_codes = location_codes[['Location'] + keys]
                key_location_codes = key_location_codes.query(
                    ' | '.join(['{} != \'\''.format(k) for k in keys]))

                if drop_duplicates:
                    location_codes_subset = key_location_codes.drop_duplicates(
                        subset=keys, keep='first')
                    location_codes_duplicated = None

                else:  # drop_duplicates is False or None
                    location_codes_subset = key_location_codes.drop_duplicates(
                        subset=keys, keep=False)
                    #
                    dupl_temp_1 = key_location_codes[
                        key_location_codes.duplicated(['Location'] + keys, keep=False)]
                    dupl_temp_2 = key_location_codes[
                        key_location_codes.duplicated(keys, keep=False)]
                    duplicated_1 = dupl_temp_2[
                        dupl_temp_1.eq(dupl_temp_2)].dropna().drop_duplicates()
                    duplicated_2 = dupl_temp_2[~dupl_temp_1.eq(dupl_temp_2)].dropna()
                    duplicated = pd.concat(
                        [duplicated_1, duplicated_2], axis=0, sort=False)
                    location_codes_duplicated = duplicated.groupby(keys).agg(tuple)
                    location_codes_duplicated.Location = \
                        location_codes_duplicated.Location.map(
                            lambda x: x[0] if len(set(x)) == 1 else x)

                location_codes_subset.set_index(keys, inplace=True)
                location_codes_ref = pd.concat(
                    [location_codes_subset, location_codes_duplicated], axis=0,
                    sort=False)

                if as_dict:
                    location_codes_ref_dict = location_codes_ref.to_dict()
                    if main_key is None:
                        location_codes_dictionary = location_codes_ref_dict['Location']
                    else:
                        location_codes_ref_dict[main_key] = \
                            location_codes_ref_dict.pop('Location')
                        location_codes_dictionary = location_codes_ref_dict
                else:
                    location_codes_dictionary = location_codes_ref

                print("Successfully.") if verbose == 2 else ""

                if save_it:
                    save(location_codes_dictionary, path_to_file, verbose=verbose)

            except Exception as e:
                print("Failed. {}.".format(e))
                location_codes_dictionary = None

        return location_codes_dictionary
