"""
Collect `CRS, NLC, TIPLOC and STANOX codes <http://www.railwaycodes.org.uk/crs/CRS0.shtm>`_.
"""

import string
import urllib.parse

from pyhelpers.dir import cd
from pyhelpers.ops import split_list_by_size
from pyhelpers.store import save

from pyrcs.utils import *


def _collect_list(h3, p, list_head_tag):
    notes = p.text.strip('thus:', '.')

    elements = [get_hypertext(x) for x in list_head_tag.findChildren('li')]

    list_data = {
        'Notes': notes,
        'BulletPoints': elements,
    }

    return list_data


class LocationIdentifiers:
    """
    A class for collecting location identifiers
    (including `other systems <http://www.railwaycodes.org.uk/crs/CRS1.shtm>`_ station).
    """

    #: Name of the data
    NAME = 'CRS, NLC, TIPLOC and STANOX codes'
    #: Key of the `dict <https://docs.python.org/3/library/stdtypes.html#dict>`_-type data
    KEY = 'LocationID'

    #: Key of the dict-type data of the '*other systems*'
    KEY_TO_OTHER_SYSTEMS = 'Other systems'
    #: Key of the dict-type data of the '*multiple station codes explanatory note*'
    KEY_TO_MSCEN = 'Multiple station codes explanatory note'
    #: Key of the dict-type data of *additional notes*
    KEY_TO_ADDITIONAL_NOTES = 'Additional notes'

    #: URL of the main web page of the data
    URL = urllib.parse.urljoin(home_page_url(), '/crs/crs0.shtm')

    #: Key of the data of the last updated date
    KEY_TO_LAST_UPDATED_DATE = 'Last updated date'

    def __init__(self, data_dir=None, update=False, verbose=True):
        """
        :param data_dir: name of data directory, defaults to ``None``
        :type data_dir: str or None
        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console, defaults to ``True``
        :type verbose: bool or int

        :ivar str last_updated_date: last updated date
        :ivar dict catalogue: catalogue of the data
        :ivar str data_dir: path to the data directory
        :ivar str current_data_dir: path to the current data directory

        **Example**::

            >>> # from pyrcs import LocationIdentifiers
            >>> from pyrcs.line_data import LocationIdentifiers

            >>> lid = LocationIdentifiers()

            >>> print(lid.NAME)
            CRS, NLC, TIPLOC and STANOX codes

            >>> print(lid.URL)
            http://www.railwaycodes.org.uk/crs/crs0.shtm
        """

        print_connection_error(verbose=verbose)

        self.last_updated_date = get_last_updated_date(url=self.URL, parsed=True)

        self.catalogue = get_catalogue(url=self.URL, update=update, confirmation_required=False)
        mscen_url = urllib.parse.urljoin(home_page_url(), '/crs/crs2.shtm')
        self.catalogue.update({self.KEY_TO_MSCEN: mscen_url})

        self.data_dir, self.current_data_dir = init_data_dir(
            self, data_dir=data_dir, category="line-data",
            cluster=re.sub(r",| codes| and", "", self.NAME.lower()).replace(" ", "-"))

    def _cdd_locid(self, *sub_dir, **kwargs):
        """
        Change directory to package data directory and subdirectories (and/or a file).

        The directory for this module: ``"dat\\line-data\\crs-nlc-tiploc-stanox"``.

        :param sub_dir: subdirectory or subdirectories (and/or a file)
        :type sub_dir: str
        :param kwargs: optional parameters of `pyhelpers.dir.cd`_
        :return: path to the backup data directory for ``LocationIdentifiers``
        :rtype: str

        .. _pyhelpers.dir.cd:
            https://pyhelpers.readthedocs.io/en/latest/_generated/pyhelpers.dir.cd.html
        """

        path = cd(self.data_dir, *sub_dir, mkdir=True, **kwargs)

        return path

    def _get_introduction(self, subtitle_tag='h3', verbose=False):
        try:
            source = requests.get(url=self.URL, headers=fake_requests_headers(randomized=True))
        except requests.ConnectionError:
            print("Failed. ") if verbose == 2 else ""
            print_conn_err(verbose=verbose)

        else:
            web_page_text = bs4.BeautifulSoup(markup=source.text, features='html.parser')

            div = web_page_text.find(name='div', attrs={'class': 'background'})

            intro_texts = {}

            h3 = div.find_next(name=subtitle_tag)

            p = h3.find_next('p')
            while h3:
                sub_heading = get_heading(heading_tag=h3, elem_name='em')

                if p.find_previous(name='h3') == h3:
                    txt = p.text.replace(' thus:', '.')

                    p = h3.find_next('p')

                ol = h3.find_next('ol')

    # def get_introduction(self, subtitle_tag='h3', update=False, verbose=False):
    #     path_to_pickle = self._cdd_locid("intro.pickle")
    #
    #     if os.path.isfile(path_to_pickle) and not update:
    #         intro_texts = load_pickle(path_to_pickle)
    #
    #     else:
    #
    #
    #         else:
    #             try:
    #
    #
    #                 save_pickle(intro_texts, path_to_pickle, verbose=verbose)
    #
    #             except Exception as e:
    #                 print("Failed. {}.".format(e))
    #                 intro_texts = None
    #
    #     return intro_texts

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

    @staticmethod
    def parse_note_page(note_url, parser='html.parser', verbose=False):
        """
        Parse addition note page.

        :param note_url: URL link of the target web page
        :type note_url: str
        :param parser: the `parser`_ to use for `bs4.BeautifulSoup`_, defaults to ``'html.parser'``
        :type parser: str
        :param verbose: whether to print relevant information in console, defaults to ``False``
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

            >>> url = lid.catalogue[lid.KEY_TO_MSCEN]
            >>> parsed_note_dat = lid.parse_note_page(url, parser='html.parser')

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

        web_page_text = bs4.BeautifulSoup(markup=source.text, features=parser).find_all(['p', 'pre'])
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

        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of multiple station codes explanatory note
        :rtype: dict or None

        **Example**::

            >>> from pyrcs.line_data import LocationIdentifiers

            >>> lid = LocationIdentifiers()

            >>> exp_note = lid.collect_explanatory_note()
            To collect data of multiple station codes explanatory note? [No]|Yes: yes

            >>> type(exp_note)
            dict
            >>> list(exp_note.keys())
            ['Multiple station codes explanatory note', 'Notes', 'Last updated date']

            >>> print(lid.KEY_TO_MSCEN)
            Multiple station codes explanatory note

            >>> exp_note_dat = exp_note[lid.KEY_TO_MSCEN]

            >>> type(exp_note_dat)
            pandas.core.frame.DataFrame
            >>> exp_note_dat.head()
                             Location  CRS CRS_alt1 CRS_alt2
            0    Glasgow Queen Street  GLQ      GQL
            1         Glasgow Central  GLC      GCL
            2                 Heworth  HEW      HEZ
            3    Highbury & Islington  HHY      HII      XHZ
            4  Lichfield Trent Valley  LTV      LIF
        """

        cfm_msg = confirm_msg(data_name=self.KEY_TO_MSCEN)
        if confirmed(prompt=cfm_msg, confirmation_required=confirmation_required):

            print_collect_msg(
                self.KEY_TO_MSCEN, verbose=verbose, confirmation_required=confirmation_required)

            note_url = self.catalogue[self.KEY_TO_MSCEN]
            explanatory_note_ = self.parse_note_page(note_url=note_url, verbose=False)

            if explanatory_note_ is None:
                if verbose == 2:
                    print("Failed. ")

                if not is_internet_connected():
                    print_conn_err(verbose=verbose)

                explanatory_note = None

            else:
                try:
                    explanatory_note, notes = {}, []

                    for x in explanatory_note_:
                        if isinstance(x, str):
                            if 'Last update' in x:
                                lud = {self.KEY_TO_LAST_UPDATED_DATE: parse_date(x, as_date_type=False)}
                                explanatory_note.update(lud)
                            else:
                                notes.append(x)
                        else:
                            explanatory_note.update({self.KEY_TO_MSCEN: x})

                    explanatory_note.update({'Notes': notes})

                    # Rearrange the dict
                    explanatory_note = {
                        k: explanatory_note[k]
                        for k in [self.KEY_TO_MSCEN, 'Notes', self.KEY_TO_LAST_UPDATED_DATE]
                    }

                    if verbose == 2:
                        print("Done.")

                    path_to_pickle = make_pickle_pathname(self, data_name=self.KEY_TO_MSCEN)
                    save_pickle(explanatory_note, path_to_pickle, verbose=verbose)

                except Exception as e:
                    print("Failed. {}.".format(e))
                    explanatory_note = None

            return explanatory_note

    def fetch_explanatory_note(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch multiple station codes explanatory note from local backup.

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param pickle_it: whether to save the data as a pickle file, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of a folder where the pickle file is to be saved, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
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

            >>> print(lid.KEY_TO_MSCEN)
            Multiple station codes explanatory note

            >>> exp_note_dat = exp_note[lid.KEY_TO_MSCEN]

            >>> type(exp_note_dat)
            pandas.core.frame.DataFrame
            >>> exp_note_dat.head()
                             Location  CRS CRS_alt1 CRS_alt2
            0    Glasgow Queen Street  GLQ      GQL
            1         Glasgow Central  GLC      GCL
            2                 Heworth  HEW      HEZ
            3    Highbury & Islington  HHY      HII      XHZ
            4  Lichfield Trent Valley  LTV      LIF
        """

        path_to_pickle = make_pickle_pathname(self, data_name=self.KEY_TO_MSCEN)

        if os.path.isfile(path_to_pickle) and not update:
            explanatory_note = load_pickle(path_to_pickle)

        else:
            verbose_ = collect_in_fetch_verbose(data_dir=data_dir, verbose=verbose)
            explanatory_note = self.collect_explanatory_note(
                confirmation_required=False, verbose=verbose_)

            if explanatory_note is not None:
                data_to_pickle(
                    self, data=explanatory_note, data_name=self.KEY_TO_MSCEN,
                    pickle_it=pickle_it, data_dir=data_dir, verbose=verbose)

            else:
                print_void_msg(data_name=self.KEY_TO_MSCEN, verbose=verbose)
                explanatory_note = load_pickle(path_to_pickle)

        return explanatory_note

    def collect_other_systems_codes(self, confirmation_required=True, verbose=False):
        """
        Collect data of `other systems' codes <http://www.railwaycodes.org.uk/crs/CRS1.shtm>`_
        from source web page.

        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: codes of other systems
        :rtype: dict or None

        **Example**::

            >>> from pyrcs.line_data import LocationIdentifiers

            >>> lid = LocationIdentifiers()

            >>> os_dat = lid.collect_other_systems_codes()
            To collect data of other systems? [No]|Yes: yes

            >>> type(os_dat)
            dict
            >>> list(os_dat.keys())
            ['Other systems', 'Last updated date']

            >>> print(lid.KEY_TO_OTHER_SYSTEMS)
            Other systems

            >>> os_codes = os_dat[lid.KEY_TO_OTHER_SYSTEMS]

            >>> type(os_codes)
            dict
            >>> list(os_codes.keys())
            ['Córas Iompair Éireann (Republic of Ireland)',
             'Crossrail',
             'Croydon Tramlink',
             'Docklands Light Railway',
             'Manchester Metrolink',
             'Translink (Northern Ireland)',
             'Tyne & Wear Metro']
        """

        cfm_msg = confirm_msg(data_name=self.KEY_TO_OTHER_SYSTEMS)
        if confirmed(prompt=cfm_msg, confirmation_required=confirmation_required):

            print_collect_msg(
                self.KEY_TO_OTHER_SYSTEMS, verbose=verbose, confirmation_required=confirmation_required)

            other_systems_codes = None

            url = self.catalogue[self.KEY_TO_OTHER_SYSTEMS]

            try:
                source = requests.get(url=url, headers=fake_requests_headers(randomized=True))
            except requests.ConnectionError:
                print("Failed. ") if verbose == 2 else ""
                print_conn_err(verbose=verbose)

            else:
                try:
                    web_page_text = bs4.BeautifulSoup(source.text, 'html.parser')

                    # Get system name
                    system_names = [k.text for k in web_page_text.find_all('h3')]

                    # Parse table data for each system
                    table_data = list(split_list_by_size(web_page_text.find_all('table'), sub_len=2))

                    tables = []
                    for table in table_data:
                        headers = [x.text for x in table[0].find_all('th')]
                        tbl_dat = table[1].find_all('tr')
                        tbl_data = pd.DataFrame(parse_tr(headers, tbl_dat), columns=headers)
                        tables.append(tbl_data)

                    # Make a dict
                    other_systems_codes = {
                        self.KEY_TO_OTHER_SYSTEMS: dict(zip(system_names, tables)),
                        self.KEY_TO_LAST_UPDATED_DATE: get_last_updated_date(url),
                    }

                    if verbose == 2:
                        print("Done.")

                    path_to_pickle = make_pickle_pathname(self, data_name=self.KEY_TO_OTHER_SYSTEMS)
                    save_pickle(other_systems_codes, path_to_pickle, verbose=verbose)

                except Exception as e:
                    print("Failed. {}.".format(e))

            return other_systems_codes

    def fetch_other_systems_codes(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch data of `other systems' codes <http://www.railwaycodes.org.uk/crs/CRS1.shtm>`_
        from local backup.

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param pickle_it: whether to save the data as a pickle file, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of a folder where the pickle file is to be saved, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: codes of other systems
        :rtype: dict

        **Example**::

            >>> from pyrcs.line_data import LocationIdentifiers

            >>> lid = LocationIdentifiers()

            >>> # os_dat = lid.fetch_other_systems_codes(update=True, verbose=True)
            >>> os_dat = lid.fetch_other_systems_codes()

            >>> type(os_dat)
            dict
            >>> list(os_dat.keys())
            ['Other systems', 'Last updated date']

            >>> print(lid.KEY_TO_OTHER_SYSTEMS)
            Other systems

            >>> os_codes = os_dat[lid.KEY_TO_OTHER_SYSTEMS]

            >>> type(os_codes)
            dict
            >>> list(os_codes.keys())
            ['Córas Iompair Éireann (Republic of Ireland)',
             'Crossrail',
             'Croydon Tramlink',
             'Docklands Light Railway',
             'Manchester Metrolink',
             'Translink (Northern Ireland)',
             'Tyne & Wear Metro']
        """

        path_to_pickle = make_pickle_pathname(self, data_name=self.KEY_TO_OTHER_SYSTEMS)

        if os.path.isfile(path_to_pickle) and not update:
            other_systems_codes = load_pickle(path_to_pickle)

        else:
            verbose_ = collect_in_fetch_verbose(data_dir=data_dir, verbose=verbose)

            other_systems_codes = self.collect_other_systems_codes(
                confirmation_required=False, verbose=verbose_)

            if other_systems_codes is not None:
                data_to_pickle(
                    self, data=other_systems_codes, data_name=self.KEY_TO_OTHER_SYSTEMS,
                    pickle_it=pickle_it, data_dir=data_dir, verbose=verbose)

            else:
                print_void_msg(data_name=self.KEY_TO_OTHER_SYSTEMS, verbose=verbose)
                other_systems_codes = load_pickle(path_to_pickle)

        return other_systems_codes

    def collect_loc_codes_by_initial(self, initial, update=False, verbose=False):
        """
        Collect `CRS, NLC, TIPLOC, STANME and STANOX codes
        <http://www.railwaycodes.org.uk/crs/CRS0.shtm>`_ for a given ``initial`` letter.

        :param initial: initial letter of station/junction name or certain word for specifying URL
        :type initial: str
        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of locations beginning with ``initial`` and
            date of when the data was last updated
        :rtype: dict

        **Example**::

            >>> from pyrcs.line_data import LocationIdentifiers

            >>> lid = LocationIdentifiers()

            >>> # loc_a = lid.collect_loc_codes_by_initial('a', update=True, verbose=True)
            >>> loc_a = lid.collect_loc_codes_by_initial(initial='a')

            >>> type(loc_a)
            dict
            >>> list(loc_a.keys())
            ['A', 'Additional notes', 'Last updated date']

            >>> loc_a_codes = loc_a['A']

            >>> type(loc_a_codes)
            pandas.core.frame.DataFrame
            >>> loc_a_codes.head()
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
            url = self.catalogue[beginning_with]

            if verbose == 2:
                collect_msg = "Collecting data of locations starting with \"{}\"".format(beginning_with)
                print(collect_msg, end=" ... ")

            location_codes_initial = {
                beginning_with: None,
                self.KEY_TO_ADDITIONAL_NOTES: None,
                self.KEY_TO_LAST_UPDATED_DATE: None,
            }

            try:
                source = requests.get(url, headers=fake_requests_headers())
            except requests.ConnectionError:
                print("Failed. ") if verbose == 2 else ""
                print_conn_err(verbose=verbose)

            else:
                try:
                    tbl_lst, header = parse_table(source=source, parser='html.parser')

                    # Get a raw DataFrame
                    reps = {'\b-\b': '', '\xa0\xa0': ' ', '&half;': ' and 1/2'}
                    pattern = re.compile("|".join(reps.keys()))
                    tbl_lst = [
                        [pattern.sub(lambda x: reps[x.group(0)], item) for item in record]
                        for record in tbl_lst
                    ]
                    loc_codes = pd.DataFrame(tbl_lst, columns=header)
                    loc_codes.replace({'\xa0': ''}, regex=True, inplace=True)

                    # Collect additional information as note
                    loc_codes[['Location', 'Location_Note']] = \
                        loc_codes.Location.map(parse_location_name).apply(pd.Series)

                    # CRS, NLC, TIPLOC, STANME
                    drop_pattern = re.compile(r'[Ff]ormerly|[Ss]ee[ also]|Also .[\w ,]+')
                    idx = [
                        loc_codes[loc_codes.CRS == x].index[0] for x in loc_codes.CRS
                        if re.match(drop_pattern, x)
                    ]
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
                    loc_codes[other_notes_col] = loc_codes[other_codes_col].applymap(collect_others_note)
                    loc_codes[other_codes_col] = loc_codes[other_codes_col].applymap(strip_others_note)

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
                        loc_idx = [
                            i for i, crs_note in enumerate(loc_codes.CRS_Note) if 'see note' in crs_note
                        ]

                        web_page_text = bs4.BeautifulSoup(source.text, 'html.parser')

                        note_urls = [
                            urllib.parse.urljoin(self.catalogue[beginning_with], x['href'])
                            for x in web_page_text.find_all('a', href=True, text='note')
                        ]
                        add_notes = [self.parse_note_page(note_url) for note_url in note_urls]

                        additional_notes = dict(zip(loc_codes.CRS.iloc[loc_idx], add_notes))

                    else:
                        additional_notes = None

                    loc_codes = loc_codes.replace(self.amendment_to_loc_names(), regex=True)

                    loc_codes.STANOX = loc_codes.STANOX.replace({'-': ''})

                    loc_codes.index = range(len(loc_codes))  # Rearrange index

                    last_updated_date = get_last_updated_date(url=url)

                    if verbose == 2:
                        print("Done.")

                    data = {
                        beginning_with: loc_codes,
                        self.KEY_TO_ADDITIONAL_NOTES: additional_notes,
                        self.KEY_TO_LAST_UPDATED_DATE: last_updated_date,
                    }
                    location_codes_initial.update(data)

                    save_pickle(location_codes_initial, path_to_pickle, verbose=verbose)

                except Exception as e:
                    print("Failed. {}.".format(e))

        return location_codes_initial

    def fetch_location_codes(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch `CRS, NLC, TIPLOC, STANME and STANOX codes
        <http://www.railwaycodes.org.uk/crs/CRS0.shtm>`_ from local backup.

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param pickle_it: whether to save the data as a pickle file, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of a folder where the pickle file is to be saved, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of location codes and date of when the data was last updated
        :rtype: dict

        **Example**::

            >>> from pyrcs.line_data import LocationIdentifiers

            >>> lid = LocationIdentifiers()

            >>> # loc_dat = lid.fetch_location_codes(update=True, verbose=True)
            >>> loc_dat = lid.fetch_location_codes()

            >>> type(loc_dat)
            dict
            >>> list(loc_dat.keys())
            ['Location codes', 'Other systems', 'Additional notes', 'Last updated date']

            >>> print(lid.KEY)
            Location codes

            >>> loc_codes = loc_dat['Location codes']

            >>> type(loc_codes)
            pandas.core.frame.DataFrame
            >>> loc_codes.head()
                                           Location CRS  ... STANME_Note STANOX_Note
            0                                Aachen      ...
            1                    Abbeyhill Junction      ...
            2                 Abbeyhill Signal E811      ...
            3            Abbeyhill Turnback Sidings      ...
            4  Abbey Level Crossing (Staffordshire)      ...
            [5 rows x 12 columns]
        """

        verbose_1 = collect_in_fetch_verbose(data_dir=data_dir, verbose=verbose)

        # Get every data table
        verbose_2 = verbose_1 if is_internet_connected() else False
        data = [
            self.collect_loc_codes_by_initial(initial=x, update=update, verbose=verbose_2)
            for x in string.ascii_lowercase
        ]

        if all(d[x] is None for d, x in zip(data, string.ascii_uppercase)):
            if update:
                print_conn_err(verbose=verbose)
                print_void_msg(data_name=self.KEY, verbose=verbose)

            data = [
                self.collect_loc_codes_by_initial(initial=x, update=False, verbose=verbose_1)
                for x in string.ascii_lowercase
            ]

        # Select DataFrames only
        location_codes_data = (item[x] for item, x in zip(data, string.ascii_uppercase))
        location_codes_data_table = pd.concat(location_codes_data, ignore_index=True, sort=False)

        # Likely errors (spotted occasionally)
        idx = location_codes_data_table[
            location_codes_data_table.Location == 'Selby Melmerby Estates'].index
        values = location_codes_data_table.loc[idx, 'STANME':'STANOX'].values
        location_codes_data_table.loc[idx, 'STANME':'STANOX'] = ['', '']
        idx = location_codes_data_table[
            location_codes_data_table.Location == 'Selby Potter Group'].index
        location_codes_data_table.loc[idx, 'STANME':'STANOX'] = values

        # Get the latest updated date
        last_updated_dates = (
            item[self.KEY_TO_LAST_UPDATED_DATE] for item, _ in zip(data, string.ascii_uppercase))
        latest_update_date = max(d for d in last_updated_dates if d is not None)

        # Get other systems codes
        other_systems_codes = self.fetch_other_systems_codes(
            update=update, verbose=verbose_1)[self.KEY_TO_OTHER_SYSTEMS]

        # Get additional note
        additional_notes = self.fetch_explanatory_note(update=update, verbose=verbose_1)

        # Create a dict to include all information
        location_codes = {
            self.KEY: location_codes_data_table,
            self.KEY_TO_OTHER_SYSTEMS: other_systems_codes,
            self.KEY_TO_ADDITIONAL_NOTES: additional_notes,
            self.KEY_TO_LAST_UPDATED_DATE: latest_update_date,
        }

        data_to_pickle(
            self, data=location_codes, data_name=self.KEY,
            pickle_it=pickle_it, data_dir=data_dir, verbose=verbose)

        return location_codes

    def make_loc_id_dict(self, keys, initials=None, drop_duplicates=False, as_dict=False, main_key=None,
                         save_it=False, data_dir=None, update=False, verbose=False):
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
        :param main_key: key of the returned dictionary (if ``as_dict`` is ``True``),
            defaults to ``None``
        :type main_key: str or None
        :param save_it: whether to save the location codes dictionary, defaults to ``False``
        :type save_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str or None
        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: dictionary or a data frame for location code data for the given ``keys``
        :rtype: dict or pandas.DataFrame or None

        **Examples**::

            >>> from pyrcs.line_data import LocationIdentifiers

            >>> lid = LocationIdentifiers()

            >>> stanox_dictionary = lid.make_loc_id_dict(keys='STANOX')

            >>> type(stanox_dictionary)
            pandas.core.frame.DataFrame
            >>> stanox_dictionary.head()
                                      Location
            STANOX
            00005                       Aachen
            04309           Abbeyhill Junction
            04311        Abbeyhill Signal E811
            04308   Abbeyhill Turnback Sidings
            88601                   Abbey Wood

            >>> s_t_dictionary = lid.make_loc_id_dict(['STANOX', 'TIPLOC'], initials='a')

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

            >>> s_t_dictionary = lid.make_loc_id_dict(['STANOX', 'TIPLOC'], initials='b',
            ...                                       as_dict=True, main_key='Data')

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

        dat_dir = validate_dir(data_dir) if data_dir else self.data_dir
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
                location_codes = self.fetch_location_codes(verbose=verbose)[self.KEY]
            else:
                temp = [
                    self.collect_loc_codes_by_initial(initial, verbose=verbose)[initial.upper()]
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
                    location_codes_subset = key_location_codes.drop_duplicates(subset=keys, keep='first')
                    location_codes_duplicated = None

                else:  # drop_duplicates is False or None
                    location_codes_subset = key_location_codes.drop_duplicates(subset=keys, keep=False)
                    #
                    dupl_temp_1 = key_location_codes[
                        key_location_codes.duplicated(['Location'] + keys, keep=False)]
                    dupl_temp_2 = key_location_codes[key_location_codes.duplicated(keys, keep=False)]
                    duplicated_1 = dupl_temp_2[dupl_temp_1.eq(dupl_temp_2)].dropna().drop_duplicates()
                    duplicated_2 = dupl_temp_2[~dupl_temp_1.eq(dupl_temp_2)].dropna()
                    duplicated = pd.concat([duplicated_1, duplicated_2], axis=0, sort=False)
                    location_codes_duplicated = duplicated.groupby(keys).agg(tuple)
                    location_codes_duplicated.Location = location_codes_duplicated.Location.map(
                        lambda x: x[0] if len(set(x)) == 1 else x)

                location_codes_subset.set_index(keys, inplace=True)
                location_codes_ref = pd.concat(
                    [location_codes_subset, location_codes_duplicated], axis=0, sort=False)

                if as_dict:
                    location_codes_ref_dict = location_codes_ref.to_dict()
                    if main_key is None:
                        location_codes_dictionary = location_codes_ref_dict['Location']
                    else:
                        location_codes_ref_dict[main_key] = location_codes_ref_dict.pop('Location')
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
