""" 
Data source: http://www.railwaycodes.org.uk

CRS, NLC, TIPLOC and STANOX Codes (Reference: http://www.railwaycodes.org.uk/crs/CRS0.shtm)

This links to a four-way listing of railway codes:

    - Computer reservation system (CRS) codes
        * [replaced by national reservation system (NRS) codes from late 2004, but the codes are the same]
    - National location codes (NLC)
    - Timing point locations (TIPLOC)
    - Station number names (STANME)
    - Station numbers (STANOX)
"""

import os
import re
import string
import urllib.parse

import bs4
import more_itertools
import pandas as pd
import requests
from pyhelpers.store import load_json, load_pickle, save_json, save_pickle

from pyrcs.utils import cd_dat
from pyrcs.utils import get_cls_catalogue, get_last_updated_date, regulate_input_data_dir
from pyrcs.utils import parse_location_note, parse_table, parse_tr


class LocationIdentifiers:
    def __init__(self, data_dir=None):
        self.HomeURL = 'http://www.railwaycodes.org.uk'
        self.Name = 'CRS, NLC, TIPLOC and STANOX codes'
        self.URL = 'http://www.railwaycodes.org.uk/crs/CRS0.shtm'
        self.Catalogue = get_cls_catalogue(self.URL)
        self.Date = get_last_updated_date(self.URL, parsed=True, date_type=False)
        self.DataDir = regulate_input_data_dir(data_dir) if data_dir \
            else cd_dat("Line data", "CRS, NLC, TIPLOC and STANOX codes")

    # Change directory to "dat\\Line data\\CRS, NLC, TIPLOC and STANOX codes\\" and sub-directories
    def cd_lc(self, *sub_dir):
        path = self.DataDir
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    # Change directory to "dat\\Line data\\CRS, NLC, TIPLOC and STANOX codes\\dat" and sub-directories
    def cdd_lc(self, *sub_dir):
        path = self.cd_lc("dat")
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    # Location name modifications
    @staticmethod
    def location_name_errata():
        location_name_mod_dict = {
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
        return location_name_mod_dict

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
    def collect_additional_crs_note(self, update=False):
        if update:
            try:
                note_url = 'http://www.railwaycodes.org.uk/crs/CRS2.shtm'
                additional_note = self.parse_additional_note_page(note_url)
                save_pickle(additional_note, os.path.join(self.cd_lc(), "Additional-CRS-note.pickle"))
            except Exception as e:
                print("Failed to collect additional note for CRS. {}.".format(e))
                additional_note = None
            return additional_note

    # Fetch note about CRS
    def fetch_additional_crs_note(self, update=False):
        path_to_pickle = os.path.join(self.cd_lc(), "Additional-CRS-note.pickle")
        if not os.path.isfile(path_to_pickle) or update:
            self.collect_additional_crs_note(update=True)
        try:
            additional_note = load_pickle(path_to_pickle)
        except Exception as e:
            print("Failed to fetch additional note for CRS. {}.".format(e))
            additional_note = None
        return additional_note

    # Collect data for other systems
    def collect_other_systems_codes(self, update=False):
        if update:
            try:
                source = requests.get(self.Catalogue['Other systems'])
                web_page_text = bs4.BeautifulSoup(source.text, 'lxml')
                # Get system name
                system_names = [k.text for k in web_page_text.find_all('h3')]
                system_names = [n.replace('Tramlnk', 'Tramlink') if 'Tramlnk' in n else n for n in system_names]
                # Get column names for the other systems table
                headers = list(more_itertools.unique_everseen([h.text for h in web_page_text.find_all('th')]))
                # Parse table data for each system
                table_data = web_page_text.find_all('table', {'width': '1100px'})
                tables = [pd.DataFrame(parse_tr(headers, table.find_all('tr')), columns=headers)
                          for table in table_data]
                codes = [tables[i] for i in range(len(tables)) if i % 2 != 0]
                # Make a dict
                other_systems_codes = dict(zip(system_names, codes))
                save_pickle(other_systems_codes, os.path.join(self.cd_lc(), "Other-systems-location-codes.pickle"))
            except Exception as e:
                print("Failed to collect location codes for other systems. {}.".format(e))
                other_systems_codes = None
            return other_systems_codes

    # Fetch the data for other systems
    def fetch_other_systems_codes(self, update=False):
        path_to_pickle = os.path.join(self.cd_lc(), "Other-systems-location-codes.pickle")
        if not os.path.isfile(path_to_pickle) or update:
            self.collect_other_systems_codes(update=True)
        try:
            other_systems_codes = load_pickle(path_to_pickle)
        except Exception as e:
            print("Failed to fetch the data for other systems. {}".format(e))
            other_systems_codes = None
        return other_systems_codes

    # Scrape data of locations including CRS, NLC, TIPLOC, STANME and STANOX codes
    def collect_location_codes_by_initial(self, initial, update=False):
        """
        :param initial: [str] initial letter of station/junction name or certain word for specifying URL
        :param update: [bool]
        :return [tuple] ([DataFrame] CRS, NLC, TIPLOC and STANOX data of (almost) all stations/junctions,
                         [str]} date of when the data was last updated)
        """
        assert initial in string.ascii_letters

        path_to_pickle = os.path.join(self.cd_lc(), "A-Z", initial.upper() + ".pickle")
        if os.path.isfile(path_to_pickle) and not update:
            location_codes = load_pickle(path_to_pickle)
        else:
            url = self.Catalogue[initial.upper()]
            # Request to get connected to the URL
            try:
                source = requests.get(url)
                tbl_lst, header = parse_table(source, parser='lxml')

                # Get a raw DataFrame
                reps = {'\b-\b': '', '\xa0\xa0': ' ', '&half;': ' and 1/2'}
                pattern = re.compile("|".join(reps.keys()))
                tbl_lst = [[pattern.sub(lambda x: reps[x.group(0)], item) for item in record] for record in tbl_lst]
                data = pd.DataFrame(tbl_lst, columns=header)
                data.replace({'\xa0': ''}, regex=True, inplace=True)

                # Collect additional information as note
                data[['Location', 'Location_Note']] = data.Location.map(parse_location_note).apply(pd.Series)

                # CRS, NLC, TIPLOC, STANME
                drop_pattern = re.compile(r'[Ff]ormerly|[Ss]ee[ also]|Also .[\w ,]+')
                idx = [data[data.CRS == x].index[0] for x in data.CRS if re.match(drop_pattern, x)]
                data.drop(labels=idx, axis=0, inplace=True)

                #
                def collect_others_note(other_note_x):
                    n = re.search(r'(?<=[\[(\'])[\w,? ]+(?=[)\]\'])', other_note_x)
                    note = n.group() if n is not None else ''
                    return note

                #
                def strip_others_note(other_note_x):
                    d = re.search(r'[\w ,]+(?= [\[(\'])', other_note_x)
                    dat = d.group() if d is not None else other_note_x
                    return dat

                other_codes_col = data.columns[1:-1]
                other_notes_col = [x + '_Note' for x in other_codes_col]
                data[other_notes_col] = data[other_codes_col].applymap(collect_others_note)
                data[other_codes_col] = data[other_codes_col].applymap(strip_others_note)

                # STANOX
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

                if not data.empty:
                    data[['STANOX', 'STANOX_Note']] = data.STANOX.map(parse_stanox_note).apply(pd.Series)
                else:  # It is likely that no data is available on the web page for the given 'key_word'
                    data['STANOX_Note'] = data.STANOX

                if any('see note' in crs_note for crs_note in data.CRS_Note):
                    loc_idx = [i for i, crs_note in enumerate(data.CRS_Note) if 'see note' in crs_note]
                    web_page_text = bs4.BeautifulSoup(source.text, 'lxml')
                    note_urls = [urllib.parse.urljoin(self.Catalogue[initial.upper()], l['href'])
                                 for l in web_page_text.find_all('a', href=True, text='note')]
                    additional_notes = [self.parse_additional_note_page(note_url) for note_url in note_urls]
                    additional_note = dict(zip(data.CRS.iloc[loc_idx], additional_notes))
                else:
                    additional_note = None

                data = data.replace(self.location_name_errata(), regex=True)

                data.STANOX = data.STANOX.replace({'-': ''})

                data.index = range(len(data))  # Rearrange index

                # Specify the requested URL
                last_updated_date = get_last_updated_date(url)

                location_codes_keys = (initial.upper(), 'Last_updated_date', 'Additional_note')
                location_codes_vals = (data, last_updated_date, additional_note)
                location_codes = dict(zip(location_codes_keys, location_codes_vals))

                save_pickle(location_codes, path_to_pickle)

            except Exception as e:
                print("Failed to collect location data. {}.".format(e))
                location_codes = None

        return location_codes

    # Get all Location data including CRS, NLC, TIPLOC, STANME and STANOX codes either locally or from online
    def fetch_location_codes(self, update=False, pickle_it=False, data_dir=None):
        # Get every data table
        data = [self.collect_location_codes_by_initial(x, update=update) for x in string.ascii_lowercase]

        # Select DataFrames only
        location_codes_data = (item[x] for item, x in zip(data, string.ascii_uppercase))
        location_codes_data_table = pd.concat(location_codes_data, axis=0, ignore_index=True)

        # Likely errors (spotted occasionally)
        idx = location_codes_data_table[location_codes_data_table.Location == 'Selby Melmerby Estates'].index
        values = location_codes_data_table.loc[idx, 'STANME':'STANOX'].values
        location_codes_data_table.loc[idx, 'STANME':'STANOX'] = ['', '']
        idx = location_codes_data_table[location_codes_data_table.Location == 'Selby Potter Group'].index
        location_codes_data_table.loc[idx, 'STANME':'STANOX'] = values

        # Get the latest updated date
        last_updated_dates = (item['Last_updated_date'] for item, _ in zip(data, string.ascii_uppercase))
        last_updated_date = max(d for d in last_updated_dates if d is not None)

        # Get additional note
        additional_note = self.fetch_additional_crs_note()

        # Get other systems codes
        other_systems_codes = self.fetch_other_systems_codes()

        # Create a dict to include all information
        location_codes = {'Location_codes': location_codes_data_table,
                          'Latest_updated_date': last_updated_date,
                          'Additional_note': additional_note,
                          'Other_systems': other_systems_codes}

        if pickle_it:
            dat_dir = regulate_input_data_dir(data_dir) if data_dir else self.DataDir
            path_to_pickle = os.path.join(dat_dir, "CRS-NLC-TIPLOC-STANOX-codes.pickle")
            save_pickle(location_codes, path_to_pickle)

        return location_codes

    # Get a dict/dataframe for location code data for the given keyword
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
                location_codes = pd.concat(temp, axis=0, ignore_index=True)
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
                    duplicated = pd.concat([duplicated_1, duplicated_2], axis=0)
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
