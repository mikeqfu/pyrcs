""" 
Reference: http://www.railwaycodes.org.uk/crs/CRS0.shtm

CRS, NLC, TIPLOC and STANOX Codes 

This links to a four-way listing of railway codes:

    - Computer reservation system (CRS) codes 
        * [replaced by national reservation system (NRS) codes from late 2004, but the codes are the same]
    - National location codes (NLCs)
    - Timing point locations (TIPLOCs)
    - Station number names (STANME)
    - Station numbers (STANOX)

"""

import os
import re
import string
from urllib.parse import urljoin

import bs4
import pandas as pd
import requests
from more_itertools import unique_everseen

from utils import cdd_rc_dat, load_pickle, save_pickle, get_last_updated_date, parse_tr, parse_table


#
def cdd_loc_codes(*directories):
    path = cdd_rc_dat("Line data", "CRS, NLC, TIPLOC and STANOX codes")
    for directory in directories:
        path = os.path.join(path, directory)
    return path


#
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


#
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


# Locations and CRS, NLC, TIPLOC, STANME and STANOX codes ============================================================
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
            reps = {'-': '', '\xa0': '', '&half;': ' and 1/2'}
            pattern = re.compile("|".join(reps.keys()))
            tbl_lst = [[pattern.sub(lambda x: reps[x.group(0)], item) for item in record] for record in tbl_lst]
            data = pd.DataFrame(tbl_lst, columns=header)

            """ Extract additional information as note """

            # Location
            def clean_loc_note(x):
                # Data
                d = re.search('[\w ,]+(?=[ \n]\[)', x)
                if d is not None:
                    dat = d.group()
                else:
                    m_pat = re.compile('[Oo]riginally |[Ff]ormerly |[Ll]ater |[Pp]resumed |\?|\"|\n')
                    # dat = re.search('["\w ,]+(?= [[(?\'])|["\w ,]+', x).group() if re.search(m_pat, x) else x
                    dat = ' '.join(x.replace(x[x.find('('):x.find(')')+1], '').split()) if re.search(m_pat, x) else x
                # Note
                n = re.search('(?<=[\n ][[(\'])[\w ,\'\"/?]+', x)
                if n is not None and (n.group() == "'" or n.group() == '"'):
                    n = re.search('(?<=[[(])[\w ,?]+(?=[])])', x)
                note = n.group() if n is not None else ''
                if 'STANOX ' in dat and 'STANOX ' in x and note == '':
                    dat = x[0:x.find('STANOX')].strip()
                    note = x[x.find('STANOX'):]
                return dat, note

            data[['Location', 'Location_Note']] = data.Location.map(clean_loc_note).apply(pd.Series)

            # CRS, NLC, TIPLOC, STANME
            drop_pattern = re.compile('[Ff]ormerly|[Ss]ee[ also]|Also .[\w ,]+')
            idx = [data[data.CRS == x].index[0] for x in data.CRS if re.match(drop_pattern, x)]
            data.drop(labels=idx, axis=0, inplace=True)

            def extract_others_note(x):
                n = re.search('(?<=[[(\'])[\w,? ]+(?=[])\'])', x)
                note = n.group() if n is not None else ''
                return note

            def strip_others_note(x):
                d = re.search('[\w ,]+(?= [[(\'])', x)
                dat = d.group() if d is not None else x
                return dat

            other_codes_col = ['CRS', 'NLC', 'TIPLOC', 'STANME']
            other_notes_col = [x + '_Note' for x in other_codes_col]

            data[other_notes_col] = data[other_codes_col].applymap(extract_others_note)
            data[other_codes_col] = data[other_codes_col].applymap(strip_others_note)

            # STANOX
            def clean_stanox_note(x):
                d = re.search('[\w *,]+(?= [[(\'])', x)
                dat = d.group() if d is not None else x
                note = 'Pseudo STANOX' if '*' in dat else ''
                n = re.search('(?<=[[(\'])[\w, ]+.(?=[])\'])', x)
                if n is not None:
                    note = '; '.join(x for x in [note, n.group()] if x != '')
                dat = dat.rstrip('*') if '*' in dat else dat
                return dat, note

            if not data.empty:
                data[['STANOX', 'STANOX_Note']] = data.STANOX.map(clean_stanox_note).apply(pd.Series)
            else:  # It is likely that no data is available on the web page for the given 'key_word'
                data['STANOX_Note'] = data.STANOX

            if any('see note' in crs_note for crs_note in data.CRS_Note):
                loc_idx = [i for i, crs_note in enumerate(data.CRS_Note) if 'see note' in crs_note]
                web_page_text = bs4.BeautifulSoup(source.text, 'lxml')
                note_urls = [urljoin(url, l['href']) for l in web_page_text.find_all('a', href=True, text='note')]
                additional_notes = [parse_additional_note_page(note_url) for note_url in note_urls]
                additional_note = dict(zip(data.CRS.iloc[loc_idx], additional_notes))
            else:
                additional_note = None

            data.index = range(len(data))  # Rearrange index

        except Exception as e:
            print("Scraping location data ... failed due to {}.".format(e))
            data = None
            additional_note = None

        location_codes_keys = [s + keyword.title() for s in ('Locations_', 'Last_updated_date_', 'Additional_note_')]
        location_codes = dict(zip(location_codes_keys, [data, last_updated_date, additional_note]))
        save_pickle(location_codes, path_to_file)

    return location_codes


#
def scrape_other_systems(update=False):
    path_to_file = cdd_loc_codes("Other-systems-location-codes.pickle")
    if os.path.isfile(path_to_file) and not update:
        other_systems_codes = load_pickle(path_to_file)
    else:
        try:
            url = 'http://www.railwaycodes.org.uk/crs/CRS1.shtm'
            source = requests.get(url)
            web_page_text = bs4.BeautifulSoup(source.text, 'lxml')
            # Get system name
            systems = [k.text for k in web_page_text.find_all('h3')]
            # Get column names for the other systems table
            headers = list(unique_everseen([h.text for h in web_page_text.find_all('th')]))
            # Parse table data for each system
            table_data = web_page_text.find_all('table', {'border': 1})
            tables = [pd.DataFrame(parse_tr(headers, table.find_all('tr')), columns=headers) for table in table_data]
            # Create a dict
            other_systems_codes = dict(zip(systems, tables))
        except Exception as e:
            print("Scraping location data for other systems ... failed due to '{}'.".format(e))
            other_systems_codes = None

    return other_systems_codes


#
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
        other_systems_codes = scrape_other_systems(update)

        # Create a dict to include all information
        location_codes = {'Locations': location_codes_data_table,
                          'Latest_updated_date': last_updated_date,
                          'Additional_note': additional_note,
                          'Other_systems': other_systems_codes}

        save_pickle(location_codes, path_to_file)

    return location_codes
