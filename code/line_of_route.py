"""

Data source: http://www.railwaycodes.org.uk

Possession Resource Information Database (PRIDE)/Line Of Route (LOR) codes
(Reference: http://www.railwaycodes.org.uk/pride/pride0.shtm)

PRIDE numbers are now known as line of route (LOR) numbers.  The name has changed, but the codes are unchanged.

"""


import os
import re
import urllib.parse

import bs4
import pandas as pd
import requests

from utils import cdd, get_last_updated_date, load_pickle, parse_tr, save_pickle

# ====================================================================================================================
""" Change directory """


# Change directory to "...dat\\Line data\\Line of route" and sub-directories
def cdd_line_of_route(*directories):
    path = cdd("Line data", "Line of route codes")
    for directory in directories:
        path = os.path.join(path, directory)
    return path


# ====================================================================================================================
""" Scrape/get data """


# Get key to LOR code prefixes
def get_lor_prefixes(update=False):
    pickle_filename = "LOR-prefixes.pickle"
    path_to_pickle = cdd_line_of_route(pickle_filename)
    if os.path.isfile(path_to_pickle) and not update:
        lor_prefixes = load_pickle(path_to_pickle)
    else:
        try:
            intro_url = 'http://www.railwaycodes.org.uk/pride/pride0.shtm'
            last_updated_date = get_last_updated_date(intro_url)
            lor_pref = pd.read_html(intro_url)[0].loc[:, [0, 2]]
            lor_pref.columns = ['Prefix', 'Name']
            lor_prefixes = {'LOR_prefixes': lor_pref, 'Last_updated': last_updated_date}
            save_pickle(lor_prefixes, path_to_pickle)
        except Exception as e:
            print("Failed to get \"LOR initials\" due to \"{}\".".format(e))
            lor_prefixes = {'LOR_initials': None, 'Last_updated': None}
    return lor_prefixes


# Get the urls to LOR codes with different prefixes
def get_lor_urls(update=False):
    pickle_filename = "LOR-URLs.pickle"
    path_to_pickle = cdd_line_of_route(pickle_filename)
    if os.path.isfile(path_to_pickle) and not update:
        urls = load_pickle(path_to_pickle)
    else:
        try:
            intro_url = 'http://www.railwaycodes.org.uk/pride/pride0.shtm'
            source = requests.get(intro_url)
            soup = bs4.BeautifulSoup(source.text, 'lxml')
            links = soup.find_all('a', href=re.compile('^pride'), text=re.compile('.*codes'))
            urls = [intro_url.replace(os.path.basename(intro_url), l['href']) for l in links]
            save_pickle(urls, path_to_pickle)
        except Exception as e:
            print("Failed to get \"LOR URLs\" due to \"{}\".".format(e))
            urls = []
    return urls


# Parse the column of Line Name
def parse_line_name(x):
    # re.search('\w+.*(?= \(\[\')', x).group(), re.search('(?<=\(\[\')\w+.*(?=\')', x).group()
    try:
        line_name, line_name_note = x.split(' ([\'')
        line_name_note = line_name_note.strip('\'])')
    except ValueError:
        line_name, line_name_note = x, None
    return line_name, line_name_note


# Scrape LOR codes by prefix
def scrape_lor_codes_by_prefix(prefix, update=False):

    pickle_filename = "LOR-codes-{}.pickle".format(prefix)
    if prefix == 'NW' or prefix == 'NZ':
        pickle_filename = "LOR-codes-NW-NZ.pickle"
    path_to_pickle = cdd_line_of_route(pickle_filename)

    if os.path.isfile(path_to_pickle) and not update:
        lor_codes_by_prefix = load_pickle(path_to_pickle)
    else:
        try:
            if prefix == 'NW' or prefix == 'NZ':
                prefix = 'NW'
            url = 'http://www.railwaycodes.org.uk/pride/pride{}.shtm'.format(prefix.lower())
            source = requests.get(url)
            source_text = source.text

            soup = bs4.BeautifulSoup(source_text, 'lxml')
            try:
                note_dat = [(x['name'].title(), x.text) for x in soup.find('ol').findChildren('a')]
            except AttributeError:
                note_dat = [('Note', None)]
            note = dict(note_dat)

            header, code = soup.find_all('table', {'width': '1100px'})
            header_text = [h.text.replace('\n', ' ') for h in header.find_all('th')]
            code_data = pd.DataFrame(parse_tr(header_text, code.find_all('tr')), columns=header_text)

            line_name_info = code_data['Line Name'].map(parse_line_name).apply(pd.Series)
            line_name_info.columns = ['Line Name', 'Line Name Note']

            code_data.drop('Line Name', axis=1, inplace=True)
            codes_beginning = soup.find_all('h2')[1].text[-2:]

            lor_codes_by_prefix = {codes_beginning: {'Code': code_data.join(line_name_info), 'Note': note}}

            save_pickle(lor_codes_by_prefix, path_to_pickle)

        except Exception as e:
            print("Failed to get LOR codes by prefix \"{}\" due to \"{}\".".format(prefix, e))
            lor_codes_by_prefix = {prefix: {'Code': None, 'Note': None}}

    return lor_codes_by_prefix


# Get all LOR codes either locally or from online
def get_lor_codes(update=False):
    path_to_file = cdd_line_of_route("LOR-codes.pickle")
    if os.path.isfile(path_to_file) and not update:
        lor_codes = load_pickle(path_to_file)
    else:
        try:
            prefixes = get_lor_prefixes(update)['LOR_prefixes'].Prefix
            lor_codes = [scrape_lor_codes_by_prefix(prefix, update) for prefix in prefixes if prefix != 'NZ']
            save_pickle(lor_codes, path_to_file)
        except Exception as e:
            print("Failed to get \"line of route codes\" due to \"{}\"".format(e))
            lor_codes = None
    return lor_codes


# Scrape ELR/LOR converter
def scrape_elr_lor_converter():

    url = 'http://www.railwaycodes.org.uk/pride/elrmapping.shtm'

    last_updated_date = get_last_updated_date(url)

    page_data = pd.read_html(url)
    headers, elr_lor_converter = page_data
    elr_lor_converter.columns = list(headers.loc[0, :])

    source = requests.get(url)
    soup = bs4.BeautifulSoup(source.text, 'lxml')
    tds = soup.find_all('td')
    links = [x.find('a', href=True) for x in tds]
    links = [x.get('href') for x in links if x is not None]
    main_url = 'http://www.railwaycodes.org.uk/'
    elr_links, lor_links = [x for x in links[::2]], [x for x in links[1::2]]

    elr_lor_converter['ELR_URL'] = [urllib.parse.urljoin(main_url, x) for x in elr_links]
    elr_lor_converter['LOR_URL'] = [main_url + 'pride/' + x for x in lor_links]

    elr_lor_converter_data = {'ELR_LOR_converter': elr_lor_converter, 'Last_updated_date': last_updated_date}

    return elr_lor_converter_data


# Get ELR/LOR converter
def get_elr_lor_converter(update=False):

    pickle_filename = "ELR-LOR-converter.pickle"
    path_to_pickle = cdd_line_of_route(pickle_filename)

    if os.path.isfile(path_to_pickle) and not update:
        elr_lor_converter_data = load_pickle(path_to_pickle)
    else:
        try:
            elr_lor_converter_data = scrape_elr_lor_converter()
            save_pickle(elr_lor_converter_data, path_to_pickle)
        except Exception as e:
            print("Failed to get \"ELR/LOR converter\" due to \"{}\".".format(e))
            elr_lor_converter_data = {'ELR_LOR_converter': None, 'Last_updated_date': None}

    return elr_lor_converter_data
