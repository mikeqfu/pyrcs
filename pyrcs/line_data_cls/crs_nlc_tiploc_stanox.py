""" 
Data source: http://www.railwaycodes.org.uk

CRS, NLC, TIPLOC and STANOX Codes (http://www.railwaycodes.org.uk/crs/CRS0.shtm)

This links to a four-way listing of railway codes:

    - Computer reservation system (CRS) codes
        * [replaced by national reservation system (NRS) codes from late 2004, but the codes are the same]
    - National location codes (NLC)
    - Timing point locations (TIPLOC)
    - Station number names (STANME)
    - Station numbers (STANOX)
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
from pyhelpers.misc import confirmed
from pyhelpers.store import load_json, load_pickle

from pyrcs.utils import cd_dat, save_json, save_pickle
from pyrcs.utils import get_catalogue, get_last_updated_date
from pyrcs.utils import parse_date, parse_location_note, parse_table, parse_tr


class LocationIdentifiers:
    def __init__(self, data_dir=None):
        self.HomeURL = 'http://www.railwaycodes.org.uk'
        self.Name = 'CRS, NLC, TIPLOC and STANOX codes'
        self.URL = self.HomeURL + '/crs/CRS0.shtm'
        self.Catalogue = get_catalogue(self.URL)
        self.Date = get_last_updated_date(self.URL, parsed=True, date_type=False)
        self.DataDir = regulate_input_data_dir(data_dir) if data_dir else cd_dat("line-data", "crs-nlc-tiploc-stanox")
        self.CurrentDataDir = copy.copy(self.DataDir)

    # Change directory to "dat\\line-data\\crs-nlc-tiploc-stanox\\" and sub-directories
    def cd_lc(self, *sub_dir):
        path = self.DataDir
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    # Change directory to "dat\\line-data\\crs-nlc-tiploc-stanox\\dat" and sub-directories
    def cdd_lc(self, *sub_dir):
        path = self.cd_lc("dat")
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    # Location name modifications
    @staticmethod
    def amendment_to_location_names():
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

    # Parse addition note page
    @staticmethod
    def parse_additional_note_page(url, parser='lxml'):
        source = requests.get(url)
        web_page_text = bs4.BeautifulSoup(source.text, parser).find_all(['p', 'pre'])
        parsed_text = [x.text for x in web_page_text if isinstance(x.next_element, str)]
        parsed_texts = []
        for x in parsed_text:
            if '\n' in x:
                text = re.sub('\t+', ',', x).replace('\t', ' ').replace('\xa0', '').split('\n')
            else:
                text = x.replace('\t', ' ').replace('\xa0', '')
            if isinstance(text, list):
                text = [t.split(',') for t in text if t != '']
                parsed_texts.append(pd.DataFrame(text, columns=['Location', 'CRS', 'CRS_alt1', 'CRS_alt2']).fillna(''))
            else:
                to_remove = ['click the link', 'click your browser', 'Thank you', 'shown below']
                if text != '' and not any(t in text for t in to_remove):
                    parsed_texts.append(text)
        return parsed_texts

    # Collect note about CRS
    def collect_additional_crs_note(self, confirmation_required=True, verbose=False):
        if confirmed("To collect additional CRS note?", confirmation_required=confirmation_required):

            try:
                note_url = self.HomeURL + '/crs/CRS2.shtm'
                additional_note = self.parse_additional_note_page(note_url)
                additional_crs_note, notes = {}, []
                for x in additional_note:
                    if isinstance(x, str):
                        if 'Last update' in x:
                            additional_crs_note.update({'Last_updated_date': parse_date(x, as_date_type=False)})
                        else:
                            notes.append(x)
                    else:
                        additional_crs_note.update({'Alternative_CRS': x})
                additional_crs_note.update({'Note': notes})
                save_pickle(additional_crs_note, self.cd_lc("additional-crs-note.pickle"), verbose)

            except Exception as e:
                print("Failed to collect/update additional note for CRS. {}.".format(e))
                additional_crs_note = None

            return additional_crs_note

    # Fetch note about CRS
    def fetch_additional_crs_note(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        pickle_filename = "additional-crs-note.pickle"
        path_to_pickle = self.cd_lc(pickle_filename)

        if os.path.isfile(path_to_pickle) and not update:
            additional_note = load_pickle(path_to_pickle)
        else:
            additional_note = self.collect_additional_crs_note(confirmation_required=False,
                                                               verbose=False if data_dir or not verbose else True)
            if additional_note:  # additional_note is not None
                if pickle_it and data_dir:
                    self.CurrentDataDir = regulate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, pickle_filename)
                    save_pickle(additional_note, path_to_pickle, verbose=True)
            else:
                print("No data of additional note for CRS has been collected.")
        return additional_note

    # Collect data for other systems
    def collect_other_systems_codes(self, confirmation_required=True, verbose=False):
        if confirmed("To collect other systems codes?", confirmation_required=confirmation_required):

            try:
                source = requests.get(self.Catalogue['Other systems'])
                web_page_text = bs4.BeautifulSoup(source.text, 'lxml')
                # Get system name
                system_names = [k.text for k in web_page_text.find_all('h3')]
                system_names = [n.replace('Tramlnk', 'Tramlink') if 'Tramlnk' in n else n for n in system_names]
                # Get column names for the other systems table
                headers = list(more_itertools.unique_everseen([h.text for h in web_page_text.find_all('th')]))
                # Parse table data for each system
                tbl_data = web_page_text.find_all('table', {'width': '1100px'})
                tables = [pd.DataFrame(parse_tr(headers, table.find_all('tr')), columns=headers) for table in tbl_data]
                codes = [tables[i] for i in range(len(tables)) if i % 2 != 0]
                # Make a dict
                other_systems_codes = dict(zip(system_names, codes))
                save_pickle(other_systems_codes, self.cd_lc("other-systems-codes.pickle"), verbose)

            except Exception as e:
                print("Failed to collect location codes for other systems. {}.".format(e))
                other_systems_codes = None

            return other_systems_codes

    # Fetch the data for other systems
    def fetch_other_systems_codes(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        pickle_filename = "other-systems-codes.pickle"
        path_to_pickle = self.cd_lc(pickle_filename)

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

    # Collect data of locations including CRS, NLC, TIPLOC, STANME and STANOX codes
    def collect_location_codes_by_initial(self, initial, update=False, verbose=False):
        """
        :param initial: [str] initial letter of station/junction name or certain word for specifying URL
        :param update: [bool]
        :param verbose: [bool]
        :return [tuple] ([DataFrame] CRS, NLC, TIPLOC and STANOX data of (almost) all stations/junctions,
                         [str]} date of when the data was last updated)
        """
        assert initial in string.ascii_letters
        path_to_pickle = self.cd_lc("a-z", initial.lower() + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            location_codes_data = load_pickle(path_to_pickle)

        else:
            url = self.Catalogue[initial.upper()]

            try:
                last_updated_date = get_last_updated_date(url)
            except Exception as e:
                print("Failed to find the last update date for codes starting with \"{}.\" {}".format(
                    initial.upper(), e))
                last_updated_date = ''

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
                    parse_location_note).apply(pd.Series)

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
                    note_urls = [urllib.parse.urljoin(self.Catalogue[initial.upper()], l['href'])
                                 for l in web_page_text.find_all('a', href=True, text='note')]
                    additional_notes = [self.parse_additional_note_page(note_url) for note_url in note_urls]
                    additional_note = dict(zip(location_codes.CRS.iloc[loc_idx], additional_notes))
                else:
                    additional_note = None

                location_codes = location_codes.replace(self.amendment_to_location_names(), regex=True)

                location_codes.STANOX = location_codes.STANOX.replace({'-': ''})

                location_codes.index = range(len(location_codes))  # Rearrange index

            except Exception as e:
                print("Failed to collect the codes of locations starting with \"{}\". {}.".format(initial.upper(), e))
                location_codes, additional_note = pd.DataFrame(), None

            location_codes_data = dict(zip([initial.upper(), 'Additional_note', 'Last_updated_date'],
                                           [location_codes, additional_note, last_updated_date]))

            save_pickle(location_codes_data, path_to_pickle, verbose)

        return location_codes_data

    # Fetch all Location data including CRS, NLC, TIPLOC, STANME and STANOX codes either locally or from online
    def fetch_location_codes(self, update=False, pickle_it=False, data_dir=None, verbose=False):
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
        last_updated_dates = (item['Last_updated_date'] for item, _ in zip(data, string.ascii_uppercase))
        latest_update_date = max(d for d in last_updated_dates if d is not None)

        # Get additional note
        additional_note = self.fetch_additional_crs_note()

        # Get other systems codes
        other_systems_codes = self.fetch_other_systems_codes()

        # Create a dict to include all information
        location_codes = {'Location_codes': location_codes_data_table,
                          'Latest_update_date': latest_update_date,
                          'Additional_note': additional_note,
                          'Other_systems': other_systems_codes}

        if pickle_it and data_dir:
            self.CurrentDataDir = regulate_input_data_dir(data_dir)
            path_to_pickle = os.path.join(self.CurrentDataDir, "crs-nlc-tiploc-stanox-codes.pickle")
            save_pickle(location_codes, path_to_pickle, verbose=True)

        return location_codes

    # Make a dict/dataframe for location code data for the given keyword
    def make_location_codes_dictionary(self, keys, initials=None, main_key=None, drop_duplicates=False, as_dict=False,
                                       pickle_it=False, data_dir=None, update=False):
        """
        :param keys: [list] e.g. ['CRS', 'NLC', 'TIPLOC', 'STANOX', 'STANME']
        :param initials: [str] one of string.ascii_letters
        :param main_key: [str; None]
        :param drop_duplicates: [bool] If drop_duplicates is False, loc_dict will take the last item to be the value
        :param as_dict: [bool]
        :param pickle_it: [bool]
        :param data_dir: [str; None]
        :param update: [bool]
        :return:
        """
        if isinstance(keys, str):
            assert keys in ('CRS', 'NLC', 'TIPLOC', 'STANOX', 'STANME')
            keys = [keys]
        elif isinstance(keys, list):
            assert all(x in ('CRS', 'NLC', 'TIPLOC', 'STANOX', 'STANME') for x in keys)
        if isinstance(initials, str):
            assert initials in string.ascii_letters
            initials = [initials]
        elif isinstance(initials, list):
            assert all(x in string.ascii_letters for x in initials)
        else:
            assert initials is None
        assert isinstance(main_key, str) or main_key is None

        dat_dir = regulate_input_data_dir(data_dir) if data_dir else self.DataDir
        path_to_file = os.path.join(dat_dir, "-".join(keys) +
                                    ("" if initials is None else "-" + "".join(initials)) +
                                    (".json" if as_dict and len(keys) == 1 else ".pickle"))

        if os.path.isfile(path_to_file) and not update:
            if as_dict:
                location_codes_dictionary = load_json(path_to_file)
            else:
                location_codes_dictionary = load_pickle(path_to_file)

        else:
            if initials is None:
                location_codes = self.fetch_location_codes()['Location_codes']
            else:
                temp = [self.collect_location_codes_by_initial(initial)[initial.upper()] for initial in initials]
                location_codes = pd.concat(temp, axis=0, ignore_index=True, sort=False)
            assert isinstance(location_codes, pd.DataFrame)

            # Deep cleansing location_code
            try:
                key_location_codes = location_codes[['Location'] + keys]
                key_location_codes = key_location_codes.query(' | '.join(['{} != \'\''.format(k) for k in keys]))

                #
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
                    if main_key is not None:
                        location_codes_ref_dict[main_key] = location_codes_ref_dict.pop('Location')
                        location_codes_dictionary = location_codes_ref_dict
                    else:
                        location_codes_dictionary = location_codes_ref_dict['Location']
                else:

                    location_codes_dictionary = location_codes_ref

                if pickle_it:
                    if path_to_file.endswith(".json"):
                        save_json(location_codes_dictionary, path_to_file)
                    else:
                        save_pickle(location_codes_dictionary, path_to_file)

            except Exception as e:
                print("Failed to get multiple location code indexed reference. {}.".format(e))
                location_codes_dictionary = None

        return location_codes_dictionary
