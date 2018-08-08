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

from utils import cdd, load_json, load_pickle, save_json, save_pickle
from utils import get_last_updated_date, parse_loc_note, parse_table, parse_tr

# ====================================================================================================================
""" Change directory """


# Change directory to "dat\\Line data\\CRS, NLC, TIPLOC and STANOX codes\\"
def cdd_loc_codes(*directories):
    path = cdd("Line data", "CRS, NLC, TIPLOC and STANOX codes")
    for directory in directories:
        path = os.path.join(path, directory)
    return path


# ====================================================================================================================
""" Scrape/get data """


# Location name modifications
def create_location_name_mod_dict():
    location_name_mod_dict = {
        'Location': {re.compile(' And | \+ '): ' & ',
                     re.compile('-By-'): '-by-',
                     re.compile('-In-'): '-in-',
                     re.compile('-En-Le-'): '-en-le-',
                     re.compile('-La-'): '-la-',
                     re.compile('-Le-'): '-le-',
                     re.compile('-On-'): '-on-',
                     re.compile('-The-'): '-the-',
                     re.compile(' Of '): ' of ',
                     re.compile('-Super-'): '-super-',
                     re.compile('-Upon-'): '-upon-',
                     re.compile('-Under-'): '-under-',
                     re.compile('-Y-'): '-y-'}}
    return location_name_mod_dict


# Parse addition note page
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


# Scrape data of locations including CRS, NLC, TIPLOC, STANME and STANOX codes
def scrape_location_codes(keyword, update=False):
    """
    :param keyword: [str] initial letter of station/junction name or certain word for specifying URL
    :param update: [bool]
    :return [tuple] ([DataFrame] CRS, NLC, TIPLOC and STANOX data of (almost) all stations/junctions,
                     [str]} date of when the data was last updated)
    """
    path_to_file = cdd_loc_codes("A-Z", keyword.title() + ".pickle")
    if os.path.isfile(path_to_file) and not update:
        location_codes = load_pickle(path_to_file)
    else:
        # Specify the requested URL
        url = 'http://www.railwaycodes.org.uk/CRS/CRS{}.shtm'.format(keyword)
        last_updated_date = get_last_updated_date(url)
        # Request to get connected to the URL
        try:
            source = requests.get(url)
            tbl_lst, header = parse_table(source, parser='lxml')

            # Get a raw DataFrame
            reps = {'\b-\b': '', '\xa0': '', '&half;': ' and 1/2'}
            pattern = re.compile("|".join(reps.keys()))
            tbl_lst = [[pattern.sub(lambda x: reps[x.group(0)], item) for item in record] for record in tbl_lst]
            data = pd.DataFrame(tbl_lst, columns=header)

            """ Extract additional information as note """

            # Location
            data[['Location', 'Location_Note']] = data.Location.map(parse_loc_note).apply(pd.Series)

            # CRS, NLC, TIPLOC, STANME
            drop_pattern = re.compile('[Ff]ormerly|[Ss]ee[ also]|Also .[\w ,]+')
            idx = [data[data.CRS == x].index[0] for x in data.CRS if re.match(drop_pattern, x)]
            data.drop(labels=idx, axis=0, inplace=True)

            def extract_others_note(x):
                n = re.search('(?<=[\[(\'])[\w,? ]+(?=[)\]\'])', x)
                note = n.group() if n is not None else ''
                return note

            def strip_others_note(x):
                d = re.search('[\w ,]+(?= [\[(\'])', x)
                dat = d.group() if d is not None else x
                return dat

            other_codes_col = ['CRS', 'NLC', 'TIPLOC', 'STANME']
            other_notes_col = [x + '_Note' for x in other_codes_col]

            data[other_notes_col] = data[other_codes_col].applymap(extract_others_note)
            data[other_codes_col] = data[other_codes_col].applymap(strip_others_note)

            # STANOX
            def parse_stanox_note(x):
                if x == '-':
                    dat, note = '', ''
                else:
                    d = re.search('[\w *,]+(?= [\[(\'])', x)
                    dat = d.group() if d is not None else x
                    note = 'Pseudo STANOX' if '*' in dat else ''
                    n = re.search('(?<=[\[(\'])[\w, ]+.(?=[)\]\'])', x)
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
                note_urls = [urllib.parse.urljoin(url, l['href'])
                             for l in web_page_text.find_all('a', href=True, text='note')]
                additional_notes = [parse_additional_note_page(note_url) for note_url in note_urls]
                additional_note = dict(zip(data.CRS.iloc[loc_idx], additional_notes))
            else:
                additional_note = None

            location_name_mod_dict = create_location_name_mod_dict()
            data = data.replace(location_name_mod_dict, regex=True)

            data.STANOX = data.STANOX.replace({'-': ''})

            data.index = range(len(data))  # Rearrange index

        except Exception as e:
            print("Scraping location data ... failed due to {}.".format(e))
            data = None
            additional_note = None

        location_codes_keys = [s + keyword.title() for s in ('Locations_', 'Last_updated_date_', 'Additional_note_')]
        location_codes = dict(zip(location_codes_keys, [data, last_updated_date, additional_note]))
        save_pickle(location_codes, path_to_file)

    return location_codes


# Scrape data for other systems
def scrape_other_systems_codes(update=False):
    path_to_file = cdd_loc_codes("Other-systems-location-codes.pickle")
    if os.path.isfile(path_to_file) and not update:
        other_systems_codes = load_pickle(path_to_file)
    else:
        try:
            url = 'http://www.railwaycodes.org.uk/crs/CRS1.shtm'
            source = requests.get(url)
            web_page_text = bs4.BeautifulSoup(source.text, 'lxml')
            # Get system name
            system_names = [k.text for k in web_page_text.find_all('h3')]
            system_names = [n.replace('Tramlnk', 'Tramlink') if 'Tramlnk' in n else n for n in system_names]
            # Get column names for the other systems table
            headers = list(more_itertools.unique_everseen([h.text for h in web_page_text.find_all('th')]))
            # Parse table data for each system
            table_data = web_page_text.find_all('table', {'width': '1100px'})
            tables = [pd.DataFrame(parse_tr(headers, table.find_all('tr')), columns=headers) for table in table_data]
            codes = [tables[i] for i in range(len(tables)) if i % 2 != 0]
            # Create a dict
            other_systems_codes = dict(zip(system_names, codes))
        except Exception as e:
            print("Scraping location data for other systems ... failed due to '{}'.".format(e))
            other_systems_codes = None

    return other_systems_codes


# --------------------------------------------------------------------------------------------------------------------
""" """


# Get note about CRS
def get_additional_crs_note(update=False):
    path_to_file = cdd_loc_codes("additional-CRS-note.pickle")
    if os.path.isfile(path_to_file) and not update:
        additional_note = load_pickle(path_to_file)
    else:
        try:
            note_url = 'http://www.railwaycodes.org.uk/crs/CRS2.shtm'
            additional_note = parse_additional_note_page(note_url)
            save_pickle(additional_note, path_to_file)
        except Exception as e:
            print("Getting additional note for CRS ... failed due to '{}'.".format(e))
            additional_note = None
    return additional_note


# Get all Location data including CRS, NLC, TIPLOC, STANME and STANOX codes either locally or from online
def get_location_codes(update=False):
    path_to_file = cdd_loc_codes("CRS-NLC-TIPLOC-STANOX-codes.pickle")

    if os.path.isfile(path_to_file) and not update:
        location_codes = load_pickle(path_to_file)
    else:
        # Get every data table
        data = [scrape_location_codes(i, update) for i in string.ascii_lowercase]

        # Select DataFrames only
        location_codes_data = (item['Locations_{}'.format(x)] for item, x in zip(data, string.ascii_uppercase))
        location_codes_data_table = pd.concat(location_codes_data, axis=0, ignore_index=True)

        # Get the latest updated date
        last_updated_dates = (item['Last_updated_date_{}'.format(x)] for item, x in zip(data, string.ascii_uppercase))
        last_updated_date = max(d for d in last_updated_dates if d is not None)

        # Get additional note
        additional_note = get_additional_crs_note(update)

        # Get other systems codes
        other_systems_codes = scrape_other_systems_codes(update)

        # Create a dict to include all information
        location_codes = {'Locations': location_codes_data_table,
                          'Latest_updated_date': last_updated_date,
                          'Additional_note': additional_note,
                          'Other_systems': other_systems_codes}

        save_pickle(location_codes, path_to_file)

    return location_codes


# Get a dict for location code data for the given keyword
def get_location_codes_dictionary(keyword, initial=None, drop_duplicates=True, main_key=None, update=False):
    """
    :param keyword: [str] 'CRS', 'NLC', 'TIPLOC', 'STANOX'
    :param initial: [str] or None: one of string.ascii_letters, or (default) None
    :param drop_duplicates: [bool] If drop_duplicates is False, loc_dict will take the last item to be the value
    :param main_key: [str] or None
    :param update: [bool]
    :return:
    """
    assert keyword in ['CRS', 'NLC', 'TIPLOC', 'STANOX', 'STANME']

    json_filename = keyword + ".json"
    path_to_json = cdd_loc_codes(json_filename)

    if os.path.isfile(path_to_json) and not update:
        location_codes_dictionary = load_json(path_to_json)
    else:
        if initial is not None and initial in string.ascii_letters:
            location_code = scrape_location_codes(initial)['Locations_' + initial.capitalize()]
        else:
            location_code = get_location_codes()['Locations']

        assert isinstance(location_code, pd.DataFrame)

        try:
            loc_code_original = location_code[['Location', keyword]]
            loc_code_original = loc_code_original[loc_code_original[keyword] != '']
            if drop_duplicates:
                if drop_duplicates is True:
                    loc_code = loc_code_original.drop_duplicates(subset=keyword, keep='first')
                else:
                    loc_code = loc_code_original
                loc_dict = loc_code.set_index(keyword).to_dict()
            else:  # drop_duplicates is False
                loc_code = loc_code_original.groupby(keyword).aggregate(list)
                loc_code.Location = loc_code.Location.map(lambda x: x[0] if len(x) == 1 else x)
                loc_dict = loc_code.to_dict()

            if main_key is not None:
                loc_dict[main_key] = loc_dict.pop('Location')
                location_codes_dictionary = loc_dict
            else:
                location_codes_dictionary = loc_dict['Location']

            save_json(location_codes_dictionary, path_to_json)

        except Exception as e:
            print("Failed to get location code reference dictionary. This is due to {}.".format(e))
            location_codes_dictionary = None

    return location_codes_dictionary


# Get a dict/dataframe for location code data for the given keyword
def get_location_codes_dictionary_v2(keywords, initial=None, as_dict=False, main_key=None, update=False):
    """
    :param keywords: [list] e.g. ['CRS', 'NLC', 'TIPLOC', 'STANOX', 'STANME']
    :param initial: [str] one of string.ascii_letters
    :param as_dict:
    :param main_key: [str] or None
    :param update: [bool]
    :return:
    """
    assert isinstance(keywords, list) and all(x in ['CRS', 'NLC', 'TIPLOC', 'STANOX', 'STANME'] for x in keywords)

    filename = "-".join(keywords) + "-v2" + (".json" if as_dict else ".pickle")
    path_to_file = cdd_loc_codes(filename)

    if os.path.isfile(path_to_file) and not update:
        location_code_ref_dict = load_json(path_to_file) if as_dict else load_pickle(path_to_file)
    else:

        if initial is not None and initial in string.ascii_letters:
            location_code = scrape_location_codes(initial)['Locations_' + initial.capitalize()]
        else:
            location_code = get_location_codes()['Locations']

        # Deep cleansing location_code
        try:
            loc_code = location_code[['Location'] + keywords]
            loc_code = loc_code.query(' | '.join(["{} != ''".format(k) for k in keywords]))

            loc_code_unique = loc_code.drop_duplicates(subset=keywords, keep=False)
            loc_code_unique.set_index(keywords, inplace=True)

            duplicated_temp_1 = loc_code[loc_code.duplicated(subset=['Location'] + keywords, keep=False)]
            duplicated_temp_2 = loc_code[loc_code.duplicated(subset=keywords, keep=False)]
            duplicated_1 = duplicated_temp_2[duplicated_temp_1.eq(duplicated_temp_2)].dropna().drop_duplicates()
            duplicated_2 = duplicated_temp_2[~duplicated_temp_1.eq(duplicated_temp_2)].dropna()
            duplicated = pd.concat([duplicated_1, duplicated_2], axis=0)
            loc_code_duplicated = duplicated.groupby(keywords).agg(list)
            loc_code_duplicated.Location = loc_code_duplicated.Location.map(lambda x: x[0] if len(set(x)) == 1 else x)

            loc_code_ref = pd.concat([loc_code_unique, loc_code_duplicated], axis=0)

            if as_dict:
                loc_code_ref_dict = loc_code_ref.to_dict()
                if main_key is not None:
                    loc_code_ref_dict[main_key] = loc_code_ref_dict.pop('Location')
                    location_code_ref_dict = loc_code_ref_dict
                else:
                    location_code_ref_dict = loc_code_ref_dict['Location']
                save_json(location_code_ref_dict, path_to_file)
            else:
                location_code_ref_dict = loc_code_ref
                save_pickle(location_code_ref_dict, path_to_file)

        except Exception as e:
            print("Failed to get multiple location code indexed reference. This is due to {}.".format(e))
            location_code_ref_dict = None

    return location_code_ref_dict
