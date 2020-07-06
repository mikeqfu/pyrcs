""" A class for collecting CRS, NLC, TIPLOC and STANOX codes.

Data source: http://www.railwaycodes.org.uk/crs/CRS0.shtm
"""

import copy
import os
import re
import string
import urllib.parse

import bs4
import more_itertools
import pandas as pd
import requests
from pyhelpers.dir import regulate_input_data_dir
from pyhelpers.ops import confirmed
from pyhelpers.store import load_json, load_pickle, save, save_pickle

from pyrcs.utils import cd_dat, get_catalogue, get_last_updated_date, homepage_url
from pyrcs.utils import parse_date, parse_location_name, parse_table, parse_tr


class LocationIdentifiers:
    """
    A class for collecting `CRS, NLC, TIPLOC and STANOX codes`_.

    .. _`CRS, NLC, TIPLOC and STANOX codes`: http://www.railwaycodes.org.uk/crs/CRS0.shtm

    :param data_dir: name of data directory, defaults to ``None``
    :type data_dir: str, None

    **Example**::

        from pyrcs.line_data import LocationIdentifiers

        lid = LocationIdentifiers()

        print(lid.Name)
        # CRS, NLC, TIPLOC and STANOX codes

        print(lid.SourceURL)
        # http://www.railwaycodes.org.uk/crs/CRS0.shtm
    """

    def __init__(self, data_dir=None):
        """
        Constructor method.
        """
        self.Name = 'CRS, NLC, TIPLOC and STANOX codes'
        self.HomeURL = homepage_url()
        self.SourceURL = urllib.parse.urljoin(self.HomeURL, '/crs/CRS0.shtm')
        self.Catalogue = get_catalogue(self.SourceURL)
        self.Date = get_last_updated_date(self.SourceURL, parsed=True, as_date_type=False)
        self.DataDir = regulate_input_data_dir(data_dir) if data_dir else cd_dat("line-data", "crs-nlc-tiploc-stanox")
        self.CurrentDataDir = copy.copy(self.DataDir)
        self.Key = 'Location_codes'  # key to location codes
        self.LUDKey = 'Last_updated_date'  # key to last updated date
        self.OSKey = 'Other_systems'  # key to other systems codes
        self.ANKey = 'Additional_note'  # key to additional note

    def cdd_lc(self, *sub_dir):
        """
        Change directory to "dat\\line-data\\crs-nlc-tiploc-stanox\\" and sub-directories (and/or a file)

        :param sub_dir: sub-directory or sub-directories (and/or a file)
        :type sub_dir: str
        :return: path to the backup data directory for ``LocationIdentifiers``
        :rtype: str

        :meta private:
        """

        path = self.DataDir
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    @staticmethod
    def amendment_to_location_names_dict():
        """
        Create a replacement dictionary for location name amendments.

        :return: dictionary of regular-expression amendments to location names
        :rtype: str

        **Example**::

            from pyrcs.line_data import LocationIdentifiers

            lid = LocationIdentifiers()

            location_name_amendment_dict = lid.amendment_to_location_names_dict()
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
    def parse_additional_note_page(note_url, parser='lxml'):
        """
        Parse addition note page.

        :param note_url: URL link of the target web page
        :type note_url: str
        :param parser: the `parser`_ to use for `bs4.BeautifulSoup`_, defaults to ``'lxml'``
        :type parser: str
        :return: parsed texts
        :rtype: list

        .. _`parser`: https://www.crummy.com/software/BeautifulSoup/bs4/doc/index.html#specifying-the-parser-to-use
        .. _`bs4.BeautifulSoup`: https://www.crummy.com/software/BeautifulSoup/bs4/doc/index.html

        **Example**::

            from pyrcs.line_data import LocationIdentifiers

            lid = LocationIdentifiers()

            note_url = locid.HomeURL + '/crs/CRS2.shtm'
            parser = 'lxml'

            parsed_note = lid.parse_additional_note_page(note_url, parser)
        """

        source = requests.get(note_url)
        web_page_text = bs4.BeautifulSoup(source.text, parser).find_all(['p', 'pre'])
        parsed_text = [x.text for x in web_page_text if isinstance(x.next_element, str)]
        parsed_note = []
        for x in parsed_text:
            if '\n' in x:
                text = re.sub('\t+', ',', x).replace('\t', ' ').replace('\xa0', '').split('\n')
            else:
                text = x.replace('\t', ' ').replace('\xa0', '')
            if isinstance(text, list):
                text = [t.split(',') for t in text if t != '']
                parsed_note.append(pd.DataFrame(text, columns=['Location', 'CRS', 'CRS_alt1', 'CRS_alt2']).fillna(''))
            else:
                to_remove = ['click the link', 'click your browser', 'Thank you', 'shown below']
                if text != '' and not any(t in text for t in to_remove):
                    parsed_note.append(text)
        return parsed_note

    def collect_additional_crs_note(self, confirmation_required=True, verbose=False):
        """
        Collect note about CRS code from source web page.

        :param confirmation_required: whether to prompt a message for confirmation to proceed, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool
        :return: additional note about CRS code
        :rtype: dict, None

        **Example**::

            from pyrcs.line_data import LocationIdentifiers

            lid = LocationIdentifiers()

            confirmation_required = True
            verbose = True

            additional_crs_note = lid.collect_additional_crs_note(confirmation_required, verbose)
            # To collect additional CRS note? [No]|Yes: >? yes

            print(additional_crs_note)
            # {'Last_updated_date': <str>,
            #  'Alternative_CRS': <pandas.DataFrame>,
            #  'Note': <list of str>}
        """

        if confirmed("To collect additional CRS note? ", confirmation_required=confirmation_required):

            if verbose:
                print("Collecting additional note for CRS", end=" ... ")
            try:
                note_url = self.HomeURL + '/crs/CRS2.shtm'
                additional_note = self.parse_additional_note_page(note_url)
                additional_crs_note, notes = {}, []

                for x in additional_note:
                    if isinstance(x, str):
                        if 'Last update' in x:
                            additional_crs_note.update({self.LUDKey: parse_date(x, as_date_type=False)})
                        else:
                            notes.append(x)
                    else:
                        additional_crs_note.update({'Alternative_CRS': x})

                additional_crs_note.update({'Note': notes})

                print("Done.") if verbose else ""

                save_pickle(additional_crs_note, self.cdd_lc("additional-crs-note.pickle"), verbose=verbose)

            except Exception as e:
                print("Failed in collecting/updating additional note for CRS. {}.".format(e))
                additional_crs_note = None

            return additional_crs_note

    def fetch_additional_crs_note(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch note about CRS code from local backup.

        :param update: whether to check on update and proceed to update the package data, defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data with newly collected data, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str, None
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool
        :return: additional note about CRS code
        :rtype: dict

        **Example**::

            from pyrcs.line_data import LocationIdentifiers

            lid = LocationIdentifiers()

            update = False
            pickle_it = False
            data_dir = None
            verbose = True

            additional_crs_note = lid.fetch_additional_crs_note(update, pickle_it, data_dir, verbose)

            print(additional_crs_note)
            # {'Last_updated_date': <str>,
            #  'Alternative_CRS': <pandas.DataFrame>,
            #  'Note': <list of str>}
        """

        pickle_filename = "additional-crs-note.pickle"
        path_to_pickle = self.cdd_lc(pickle_filename)

        if os.path.isfile(path_to_pickle) and not update:
            additional_crs_note = load_pickle(path_to_pickle, verbose=verbose)

        else:
            additional_crs_note = self.collect_additional_crs_note(
                confirmation_required=False, verbose=False if data_dir or not verbose else True)

            if additional_crs_note:  # additional_note is not None
                if pickle_it and data_dir:
                    self.CurrentDataDir = regulate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, pickle_filename)
                    save_pickle(additional_crs_note, path_to_pickle, verbose=True)
            else:
                print("No data of additional note for CRS has been collected.")

        return additional_crs_note

    def collect_other_systems_codes(self, confirmation_required=True, verbose=False):
        """
        Collect data of the other systems codes from source web page.

        :param confirmation_required: whether to require users to confirm and proceed, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool
        :return: codes of other systems, in the form {<system name>: <code>, ...}
        :rtype: dict, None

        **Example**::

            from pyrcs.line_data import LocationIdentifiers

            lid = LocationIdentifiers()

            confirmation_required = True
            verbose = True

            other_systems_codes = lid.collect_other_systems_codes(confirmation_required, verbose)
            # To collect additional CRS note? [No]|Yes: >? yes

            # print(other_systems_codes)
        """

        if confirmed("To collect other systems codes? ", confirmation_required=confirmation_required):

            if verbose:
                print("To collect location codes for other systems", end=" ... ")
            try:
                source = requests.get(self.Catalogue['Other systems'])
                web_page_text = bs4.BeautifulSoup(source.text, 'lxml')
                # Get system name
                system_names = [k.text for k in web_page_text.find_all('h3')]
                system_names = [n.replace('Tramlnk', 'Tramlink') if 'Tramlnk' in n else n for n in system_names]
                # Get column names for the other systems table
                headers = list(more_itertools.unique_everseen([h.text for h in web_page_text.find_all('th')]))
                # Parse table data for each system
                tbl_data = web_page_text.find_all('table')
                tables = [pd.DataFrame(parse_tr(headers, table.find_all('tr')), columns=headers) for table in tbl_data]
                codes = [tables[i] for i in range(len(tables)) if i % 2 != 0]
                # Make a dict
                other_systems_codes = dict(zip(system_names, codes))

                print("Done.") if verbose else ""

                save_pickle(other_systems_codes, self.cdd_lc("other-systems-codes.pickle"), verbose=verbose)

            except Exception as e:
                print("Failed in collecting the other systems codes. {}.".format(e))
                other_systems_codes = None

            return other_systems_codes

    def fetch_other_systems_codes(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch data of the other systems codes from local backup.

        :param update: whether to check on update and proceed to update the package data, defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data with newly collected data, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str, None
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool
        :return: codes of other systems, in the form {<system name>: <code>, ...}
        :rtype: dict

        **Example**::

            from pyrcs.line_data import LocationIdentifiers

            lid = LocationIdentifiers()

            update = False
            pickle_it = False
            data_dir = None
            verbose = True

            other_systems_codes = lid.fetch_other_systems_codes(update, pickle_it, data_dir, verbose)
        """

        pickle_filename = "other-systems-codes.pickle"
        path_to_pickle = self.cdd_lc(pickle_filename)

        if os.path.isfile(path_to_pickle) and not update:
            other_systems_codes = load_pickle(path_to_pickle)

        else:
            other_systems_codes = self.collect_other_systems_codes(confirmation_required=False,
                                                                   verbose=False if data_dir or not verbose else True)
            if other_systems_codes:  # other_systems_codes is not None
                if pickle_it and data_dir:
                    self.CurrentDataDir = regulate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, pickle_filename)
                    save_pickle(other_systems_codes, path_to_pickle, verbose=True)
            else:
                print("No data of other systems codes has been collected.")

        return other_systems_codes

    def collect_location_codes_by_initial(self, initial, update=False, verbose=False):
        """
        Collect CRS, NLC, TIPLOC, STANME and STANOX codes for the given ``initial`` letter.

        :param initial: initial letter of station/junction name or certain word for specifying URL
        :type initial: str
        :param update: whether to check on update and proceed to update the package data, defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool
        :return: data of location codes for the given ``initial`` letter; and date of when the data was last updated
        :rtype: dict

        **Example**::

            from pyrcs.line_data import LocationIdentifiers

            lid = LocationIdentifiers()

            update = False
            verbose = True

            initial = 'a'
            location_codes_a = lid.collect_location_codes_by_initial(initial, update, verbose)

            print(location_codes_a)
            # {<initial letter>: <pandas.DataFrame>,
            #  'Additional_note': <dict>,
            #  'Last_updated_date': <str>}
        """

        assert initial in string.ascii_letters
        path_to_pickle = self.cdd_lc("a-z", initial.lower() + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            location_codes_initial = load_pickle(path_to_pickle)

        else:
            url = self.Catalogue[initial.upper()]

            if verbose:
                print("To get the last update date for codes starting with \"{}\" ... ".format(initial.upper()), end="")
            try:
                last_updated_date = get_last_updated_date(url)
                print("Done.") if verbose else ""
            except Exception as e:
                print("Failed on getting the last update date. {}".format(e))
                last_updated_date = ''

            if verbose:
                print("To collect the codes of locations starting with \"{}\" ... ".format(initial.upper()), end="")
            try:
                source = requests.get(url)  # Request to get connected to the URL
                tbl_lst, header = parse_table(source, parser='lxml')

                # Get a raw DataFrame
                reps = {'\b-\b': '', '\xa0\xa0': ' ', '&half;': ' and 1/2'}
                pattern = re.compile("|".join(reps.keys()))
                tbl_lst = [[pattern.sub(lambda x: reps[x.group(0)], item) for item in record] for record in tbl_lst]
                location_codes = pd.DataFrame(tbl_lst, columns=header)
                location_codes.replace({'\xa0': ''}, regex=True, inplace=True)

                # Collect additional information as note
                location_codes[['Location', 'Location_Note']] = location_codes.Location.map(
                    parse_location_name).apply(pd.Series)

                # CRS, NLC, TIPLOC, STANME
                drop_pattern = re.compile(r'[Ff]ormerly|[Ss]ee[ also]|Also .[\w ,]+')
                idx = [location_codes[location_codes.CRS == x].index[0]
                       for x in location_codes.CRS if re.match(drop_pattern, x)]
                location_codes.drop(labels=idx, axis=0, inplace=True)

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

                other_codes_col = location_codes.columns[1:-1]
                other_notes_col = [x + '_Note' for x in other_codes_col]
                location_codes[other_notes_col] = location_codes[other_codes_col].applymap(collect_others_note)
                location_codes[other_codes_col] = location_codes[other_codes_col].applymap(strip_others_note)

                # Parse STANOX note
                def parse_stanox_note(x):
                    if x == '-':
                        dat, note = '', ''
                    else:
                        d = re.search(r'[\w *,]+(?= [\[(\'])', x)
                        dat = d.group() if d is not None else x
                        note = 'Pseudo STANOX' if '*' in dat else ''
                        n = re.search(r'(?<=[\[(\'])[\w, ]+.(?=[)\]\'])', x)
                        if n is not None:
                            note = '; '.join(x for x in [note, n.group()] if x != '')
                        if '(' not in note and note.endswith(')'):
                            note = note.rstrip(')')
                        dat = dat.rstrip('*') if '*' in dat else dat
                    return dat, note

                if not location_codes.empty:
                    location_codes[['STANOX', 'STANOX_Note']] = location_codes.STANOX.map(
                        parse_stanox_note).apply(pd.Series)
                else:  # It is likely that no data is available on the web page for the given 'key_word'
                    location_codes['STANOX_Note'] = location_codes.STANOX

                if any('see note' in crs_note for crs_note in location_codes.CRS_Note):
                    loc_idx = [i for i, crs_note in enumerate(location_codes.CRS_Note) if 'see note' in crs_note]
                    web_page_text = bs4.BeautifulSoup(source.text, 'lxml')
                    note_urls = [urllib.parse.urljoin(self.Catalogue[initial.upper()], x['href'])
                                 for x in web_page_text.find_all('a', href=True, text='note')]
                    additional_notes = [self.parse_additional_note_page(note_url) for note_url in note_urls]
                    additional_note = dict(zip(location_codes.CRS.iloc[loc_idx], additional_notes))
                else:
                    additional_note = None

                location_codes = location_codes.replace(self.amendment_to_location_names_dict(), regex=True)

                location_codes.STANOX = location_codes.STANOX.replace({'-': ''})

                location_codes.index = range(len(location_codes))  # Rearrange index

                print("Done.") if verbose else ""

            except Exception as e:
                print("Failed in collecting the codes. {}.".format(e))
                location_codes, additional_note = pd.DataFrame(), None

            location_codes_initial = dict(zip([initial.upper(), self.ANKey, self.LUDKey],
                                              [location_codes, additional_note, last_updated_date]))

            save_pickle(location_codes_initial, path_to_pickle, verbose=verbose)

        return location_codes_initial

    def fetch_location_codes(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch CRS, NLC, TIPLOC, STANME and STANOX codes from local backup.

        :param update: whether to check on update and proceed to update the package data, defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data with newly collected data, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str, None
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool
        :return: data of location codes and date of when the data was last updated
        :rtype: dict

        **Example**::

            from pyrcs.line_data import LocationIdentifiers

            lid = LocationIdentifiers()

            update = False
            pickle_it = False
            data_dir = None
            verbose = True

            location_codes = lid.fetch_location_codes(update, pickle_it, data_dir, verbose)

            print(location_codes)
            # {'Location_codes': <pandas.DataFrame>,
            #  'Other_systems': <dict>,
            #  'Additional_note': <dict>,
            #  'Latest_update_date': <str>}
        """

        # Get every data table
        data = [self.collect_location_codes_by_initial(x, update, verbose=False if data_dir or not verbose else True)
                for x in string.ascii_lowercase]

        # Select DataFrames only
        location_codes_data = (item[x] for item, x in zip(data, string.ascii_uppercase))
        location_codes_data_table = pd.concat(location_codes_data, axis=0, ignore_index=True, sort=False)

        # Likely errors (spotted occasionally)
        idx = location_codes_data_table[location_codes_data_table.Location == 'Selby Melmerby Estates'].index
        values = location_codes_data_table.loc[idx, 'STANME':'STANOX'].values
        location_codes_data_table.loc[idx, 'STANME':'STANOX'] = ['', '']
        idx = location_codes_data_table[location_codes_data_table.Location == 'Selby Potter Group'].index
        location_codes_data_table.loc[idx, 'STANME':'STANOX'] = values

        # Get the latest updated date
        last_updated_dates = (item[self.LUDKey] for item, _ in zip(data, string.ascii_uppercase))
        latest_update_date = max(d for d in last_updated_dates if d is not None)

        # Get additional note
        additional_note = self.fetch_additional_crs_note(verbose=verbose)

        # Get other systems codes
        other_systems_codes = self.fetch_other_systems_codes(verbose=verbose)

        # Create a dict to include all information
        location_codes = {self.Key: location_codes_data_table,
                          self.LUDKey: latest_update_date,
                          self.ANKey: additional_note,
                          self.OSKey: other_systems_codes}

        if pickle_it and data_dir:
            self.CurrentDataDir = regulate_input_data_dir(data_dir)
            path_to_pickle = os.path.join(self.CurrentDataDir, "crs-nlc-tiploc-stanox-codes.pickle")
            save_pickle(location_codes, path_to_pickle, verbose=verbose)

        return location_codes

    def make_location_codes_dictionary(self, keys, initials=None, drop_duplicates=False, as_dict=False, main_key=None,
                                       save_it=False, data_dir=None, update=False, verbose=False):
        """
        Make a dict/dataframe for location code data for the given ``keys``

        :param keys: one or a sublist of ['CRS', 'NLC', 'TIPLOC', 'STANOX', 'STANME']
        :type keys: str, list
        :param initials: one or a sequence of initials for which the location codes are used, defaults to ``None``
        :type initials: str, list, None
        :param drop_duplicates: whether to drop duplicates, defaults to ``False``
        :type drop_duplicates: bool
        :param as_dict: whether to return a dictionary, defaults to ``False``
        :type as_dict: bool
        :param main_key: key of the returned dictionary if ``as_dict`` is ``True``, defaults to ``None``
        :type main_key: str, None
        :param save_it: whether to save the location codes dictionary, defaults to ``False``
        :type save_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str, None
        :param update: whether to check on update and proceed to update the package data, defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool
        :return: dictionary or a data frame for location code data for the given ``keys``
        :rtype: dict, pandas.DataFrame, None

        **Examples**::

            from pyrcs.line_data import LocationIdentifiers

            lid = LocationIdentifiers()

            drop_duplicates = False
            save_it = False
            data_dir = None
            update = False
            verbose = True

            keys = 'STANOX'
            initials = None
            as_dict = False
            main_key = None
            stanox_dictionary = lid.make_location_codes_dictionary(keys, initials, main_key,
                                                                   drop_duplicates, as_dict, save_it,
                                                                   data_dir, update, verbose)

            keys = ['STANOX', 'TIPLOC']
            initials = 'a'
            as_dict = False
            main_key = None
            stanox_dictionary = lid.make_location_codes_dictionary(keys, initials, main_key,
                                                                   drop_duplicates, as_dict, save_it,
                                                                   data_dir, update, verbose)

            keys = ['STANOX', 'TIPLOC']
            initials = 'b'
            as_dict = True
            main_key = 'Data'
            stanox_dictionary = lid.make_location_codes_dictionary(keys, initials, main_key,
                                                                   drop_duplicates, as_dict, save_it,
                                                                   data_dir, update, verbose)
        """

        valid_keys = {'CRS', 'NLC', 'TIPLOC', 'STANOX', 'STANME'}

        if isinstance(keys, str):
            assert keys in valid_keys
            keys = [keys]
        elif isinstance(keys, list):
            assert all(x in valid_keys for x in keys)

        if not initials:
            if isinstance(initials, str):
                assert initials in string.ascii_letters
                initials = [initials]
            else:  # e.g. isinstance(initials, list)
                assert all(x in string.ascii_letters for x in initials)

        if not main_key:
            assert isinstance(main_key, str)

        dat_dir = regulate_input_data_dir(data_dir) if data_dir else self.DataDir
        path_to_file = os.path.join(dat_dir, "-".join(keys) +
                                    ("" if initials is None else "-" + "".join(initials)) +
                                    (".json" if as_dict and len(keys) == 1 else ".pickle"))

        if os.path.isfile(path_to_file) and not update:
            if as_dict:
                location_codes_dictionary = load_json(path_to_file, verbose=verbose)
            else:
                location_codes_dictionary = load_pickle(path_to_file, verbose=verbose)

        else:
            if initials is None:
                location_codes = self.fetch_location_codes(verbose=verbose)[self.Key]
            else:
                temp = [self.collect_location_codes_by_initial(initial, verbose=verbose)[initial.upper()]
                        for initial in initials]
                location_codes = pd.concat(temp, axis=0, ignore_index=True, sort=False)

            print("To make/update a location code dictionary", end=" ... ") if verbose else ""

            # Deep cleansing location_code
            try:
                key_location_codes = location_codes[['Location'] + keys]
                key_location_codes = key_location_codes.query(' | '.join(['{} != \'\''.format(k) for k in keys]))

                if drop_duplicates:
                    location_codes_subset = key_location_codes.drop_duplicates(subset=keys, keep='first')
                    location_codes_duplicated = None

                else:  # drop_duplicates is False or None
                    location_codes_subset = key_location_codes.drop_duplicates(subset=keys, keep=False)
                    #
                    dupl_temp_1 = key_location_codes[key_location_codes.duplicated(['Location'] + keys, keep=False)]
                    dupl_temp_2 = key_location_codes[key_location_codes.duplicated(keys, keep=False)]
                    duplicated_1 = dupl_temp_2[dupl_temp_1.eq(dupl_temp_2)].dropna().drop_duplicates()
                    duplicated_2 = dupl_temp_2[~dupl_temp_1.eq(dupl_temp_2)].dropna()
                    duplicated = pd.concat([duplicated_1, duplicated_2], axis=0, sort=False)
                    location_codes_duplicated = duplicated.groupby(keys).agg(tuple)
                    location_codes_duplicated.Location = location_codes_duplicated.Location.map(
                        lambda x: x[0] if len(set(x)) == 1 else x)

                location_codes_subset.set_index(keys, inplace=True)
                location_codes_ref = pd.concat([location_codes_subset, location_codes_duplicated], axis=0, sort=False)

                if as_dict:
                    location_codes_ref_dict = location_codes_ref.to_dict()
                    if not main_key:
                        location_codes_dictionary = location_codes_ref_dict['Location']
                    else:
                        location_codes_ref_dict[main_key] = location_codes_ref_dict.pop('Location')
                        location_codes_dictionary = location_codes_ref_dict
                else:
                    location_codes_dictionary = location_codes_ref

                print("Successfully.") if verbose else ""

                if save_it:
                    save(location_codes_dictionary, path_to_file, verbose=verbose)

            except Exception as e:
                print("Failed. {}.".format(e))
                location_codes_dictionary = None

        return location_codes_dictionary
