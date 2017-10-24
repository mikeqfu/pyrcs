""" Possession Resource Information Database (PRIDE)/Line Of Route (LOR) codes """
# PRIDE numbers are now known as line of route (LOR) numbers.  The name has changed, but the codes are unchanged.

import os
import re

import bs4
import pandas as pd
import requests

from utils import cdd, get_last_updated_date, parse_tr, load_pickle, save_pickle

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
def get_key_to_lor_prefixes():
    intro_url = 'http://www.railwaycodes.org.uk/pride/pride0.shtm'
    last_updated_date = get_last_updated_date(intro_url)
    key_to_prefixes = pd.read_html(intro_url)[0].ix[:, [0, 2]]
    key_to_prefixes.columns = ['Prefix', 'Name']
    return {'Keys': key_to_prefixes, 'Last_updated': last_updated_date}


# Get the urls to LOR codes with different prefixes
def get_lor_urls():
    intro_url = 'http://www.railwaycodes.org.uk/pride/pride0.shtm'
    source = requests.get(intro_url)
    soup = bs4.BeautifulSoup(source.text, 'lxml')
    links = soup.find_all('a', href=re.compile('^pride'), text=re.compile('.*codes'))
    urls = [intro_url.replace(os.path.basename(intro_url), l['href']) for l in links]
    return urls


# Scrape LOR codes
def scrape_lor_codes_by_prefix(url):

    source = requests.get(url)
    source_text = source.text

    soup = bs4.BeautifulSoup(source_text, 'lxml')
    note = pd.DataFrame([(x['name'], x.text) for x in soup.find('ol').findChildren('a')], columns=['id', 'info'])
    note.id = note.id.str.title()

    header, code = soup.find_all('table', {'width': '1100px'})
    header_text = [h.text.replace('\n', ' ') for h in header.find_all('th')]
    code_data = pd.DataFrame(parse_tr(header_text, code.find_all('tr')))
    code_data.columns = header_text

    def parse_line_name(x):
        # re.search('\w+.*(?= \(\[\')', x).group(), re.search('(?<=\(\[\')\w+.*(?=\')', x).group()
        try:
            line_name, line_name_note = x.split(' ([\'')
            line_name_note = line_name_note.strip('\'])')
        except ValueError:
            line_name, line_name_note = x, None
        return line_name, line_name_note

    line_name_info = code_data['Line Name'].map(parse_line_name).apply(pd.Series)
    line_name_info.columns = ['Line Name', 'Line Name Note']

    code_data.drop('Line Name', axis=1, inplace=True)
    codes_beginning = soup.find_all('h2')[1].text[-2:]

    return {codes_beginning: {'Code': code_data.join(line_name_info), 'Note': note}}


def scrape_lor_codes():
    urls = get_lor_urls()
    lor_codes = [scrape_lor_codes_by_prefix(url) for url in urls]
    return lor_codes


def get_lor_codes(update=False):
    path_to_file = cdd_line_of_route("Line-of-route-codes.pickle")
    if os.path.isfile(path_to_file) and not update:
        lor_codes = load_pickle(path_to_file)
    else:
        try:
            lor_codes = scrape_lor_codes()
            save_pickle(lor_codes, path_to_file)
        except Exception as e:
            print("Getting line of route codes ... failed due to '{}'".format(e))
            lor_codes = None
    return lor_codes
