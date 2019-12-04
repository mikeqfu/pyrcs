"""

Data source: http://www.railwaycodes.org.uk

Possession Resource Information Database (PRIDE)/Line Of Route (LOR) codes
(http://www.railwaycodes.org.uk/pride/pride0.shtm)

PRIDE numbers are now known as line of route (LOR) numbers.  The name has changed, but the codes are unchanged.

"""


import copy
import os
import re
import urllib.parse

import bs4
import pandas as pd
import requests
from pyhelpers.dir import regulate_input_data_dir
from pyhelpers.ops import confirmed
from pyhelpers.store import load_pickle

from pyrcs.utils import cd_dat, get_catalogue, get_last_updated_date, parse_tr
from pyrcs.utils import save_pickle


class LOR:
    def __init__(self, data_dir=None):
        self.HomeURL = 'http://www.railwaycodes.org.uk'
        self.Name = 'Line of Route (LOR/PRIDE) codes'
        self.URL = self.HomeURL + '/pride/pride0.shtm'
        self.Catalogue = get_catalogue(self.URL)
        self.Date = get_last_updated_date(self.URL, parsed=True, date_type=False)
        self.DataDir = regulate_input_data_dir(data_dir) if data_dir else cd_dat("line-data", "lor-codes")
        self.CurrentDataDir = copy.copy(self.DataDir)

    # Change directory to "dat\\line-data\\lor-codes" and sub-directories
    def cd_lor(self, *sub_dir):
        path = self.DataDir
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    # Change directory to "dat\\line-data\\lor-codes\\dat" and sub-directories
    def cdd_lor(self, *sub_dir):
        path = self.cd_lor("dat")
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    # Get key to LOR code prefixes
    def get_key_to_prefixes(self, prefixes_only=True, update=False):
        path_to_pickle = self.cdd_lor("{}prefixes.pickle".format("" if prefixes_only else "key_to_"))
        if os.path.isfile(path_to_pickle) and not update:
            key_to_prefixes = load_pickle(path_to_pickle)
        else:
            try:
                lor_pref = pd.read_html(self.URL)[0].loc[:, [0, 2]]
                lor_pref.columns = ['Prefixes', 'Name']
                if prefixes_only:
                    key_to_prefixes = lor_pref.Prefixes.tolist()
                else:
                    key_to_prefixes = {'Key_to_prefixes': lor_pref, 'Last_update_date': self.Date}
                save_pickle(key_to_prefixes, path_to_pickle)
            except Exception as e:
                print("Failed to get the \"key to prefixes\". {}.".format(e))
                key_to_prefixes = [] if prefixes_only else {'Key_to_prefixes': None, 'Last_update_date': None}
        return key_to_prefixes

    # Get the urls to LOR codes with different prefixes
    def get_lor_page_urls(self, update=False):
        path_to_pickle = self.cdd_lor("urls.pickle")
        if os.path.isfile(path_to_pickle) and not update:
            urls = load_pickle(path_to_pickle)
        else:
            try:
                source = requests.get(self.URL)
                soup = bs4.BeautifulSoup(source.text, 'lxml')
                links = soup.find_all('a', href=re.compile('^pride|elrmapping'),
                                      text=re.compile('.*(codes|converter|Historical)'))
                urls = list(dict.fromkeys([self.URL.replace(os.path.basename(self.URL), x['href']) for x in links]))
                save_pickle(urls, path_to_pickle)
            except Exception as e:
                print("Failed to get the \"urls\" to LOR codes web pages. {}.".format(e))
                urls = []
        return urls

    # Update catalogue data
    def update_catalogue(self):
        if confirmed("To update catalogue?"):
            self.get_key_to_prefixes(prefixes_only=True, update=True)
            self.get_key_to_prefixes(prefixes_only=False, update=True)
            self.get_lor_page_urls(update=True)

    # Collect LOR codes by prefix
    def collect_lor_codes_by_prefix(self, prefixes, update=False, verbose=False):

        assert prefixes in self.get_key_to_prefixes(prefixes_only=True), \
            "\"prefixes\" must be one of {}".format(self.get_key_to_prefixes(prefixes_only=True))

        pickle_filename = "{}.pickle".format(prefixes if prefixes not in ("NW", "NZ") else "NW-NZ").lower()
        path_to_pickle = self.cd_lor("prefixes", pickle_filename)

        if os.path.isfile(path_to_pickle) and not update:
            lor_codes_by_initials = load_pickle(path_to_pickle)

        else:
            try:
                prefixes = "NW" if prefixes in ("NW", "NZ") else prefixes
                url = self.HomeURL + '/pride/pride{}.shtm'.format(prefixes.lower())
                source = requests.get(url)
                source_text = source.text
                source.close()

                soup = bs4.BeautifulSoup(source_text, 'lxml')

                # Parse the column of Line Name
                def parse_line_name(x):
                    # re.search('\w+.*(?= \(\[\')', x).group(), re.search('(?<=\(\[\')\w+.*(?=\')', x).group()
                    try:
                        line_name, line_name_note = x.split(' ([\'')
                        line_name_note = line_name_note.strip('\'])')
                    except ValueError:
                        line_name, line_name_note = x, None
                    return line_name, line_name_note

                def parse_h3_table(tbl_soup):
                    header, code = tbl_soup
                    header_text = [h.text.replace('\n', ' ') for h in header.find_all('th')]
                    code_dat = pd.DataFrame(parse_tr(header_text, code.find_all('tr')), columns=header_text)
                    line_name_info = code_dat['Line Name'].map(parse_line_name).apply(pd.Series)
                    line_name_info.columns = ['Line Name', 'Line Name Note']
                    code_dat = pd.concat([code_dat, line_name_info], axis=1, sort=False)
                    try:
                        note_dat = dict([(x['id'].title(), x.text) for x in soup.find('ol').findChildren('a')])
                    except AttributeError:
                        note_dat = dict([('Note', None)])
                    return code_dat, note_dat

                h3, table_soup = soup.find_all('h3'), soup.find_all('table')
                if len(h3) == 0:
                    code_data, code_data_notes = parse_h3_table(table_soup)
                    lor_codes_by_initials = {'Code': code_data, 'Note': code_data_notes}
                else:
                    code_data_and_notes = [dict(zip(['Code', 'Note'], parse_h3_table(x)))
                                           for x in zip(*[iter(table_soup)] * 2)]
                    lor_codes_by_initials = dict(zip([x.text for x in h3], code_data_and_notes))

                last_updated_date = get_last_updated_date(url)
                lor_codes_by_initials.update({'Last_updated_date': last_updated_date})

                save_pickle(lor_codes_by_initials, path_to_pickle, verbose)

            except Exception as e:
                print("Failed to collect LOR codes with prefix \"{}\". {}".format(prefixes.upper(), e))
                lor_codes_by_initials = None

        return lor_codes_by_initials

    # Fetch all LOR codes either locally or from online
    def fetch_lor_codes(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        prefixes = self.get_key_to_prefixes(prefixes_only=True, update=update)
        lor_codes = [self.collect_lor_codes_by_prefix(p, update, verbose) for p in prefixes if p != 'NZ']

        prefixes[prefixes.index('NW')] = 'NW-NZ'
        prefixes.remove('NZ')

        lor_codes_data = dict(zip(prefixes, lor_codes))

        # Get the latest updated date
        last_updated_dates = (item['Last_updated_date'] for item, _ in zip(lor_codes, prefixes))
        latest_update_date = max(d for d in last_updated_dates if d is not None)

        lor_codes_data.update({'Latest_update_date': latest_update_date})

        if pickle_it and data_dir:
            pickle_filename = "lor-codes.pickle"
            self.CurrentDataDir = regulate_input_data_dir(data_dir)
            path_to_pickle = os.path.join(self.CurrentDataDir, pickle_filename)
            save_pickle(lor_codes_data, path_to_pickle, verbose)

        return lor_codes_data

    # Collect ELR/LOR converter
    def collect_elr_lor_converter(self, confirmation_required=True, verbose=False):
        if confirmed("To collect ELR/LOR converter?", confirmation_required=confirmation_required):
            url = self.Catalogue['ELR/LOR converter']
            try:
                headers, elr_lor_dat = pd.read_html(url)
                elr_lor_dat.columns = list(headers)
                #
                source = requests.get(url)
                soup = bs4.BeautifulSoup(source.text, 'lxml')
                tds = soup.find_all('td')
                links = [x.get('href') for x in [x.find('a', href=True) for x in tds] if x is not None]
                elr_links, lor_links = [x for x in links[::2]], [x for x in links[1::2]]
                #
                if len(elr_links) != len(elr_lor_dat):
                    duplicates = elr_lor_dat[elr_lor_dat.duplicated(['ELR', 'LOR code'], keep=False)]
                    for i in duplicates.index:
                        if not duplicates['ELR'].loc[i].lower() in elr_links[i]:
                            elr_links.insert(i, elr_links[i - 1])
                        if not lor_links[i].endswith(duplicates['LOR code'].loc[i].lower()):
                            lor_links.insert(i, lor_links[i - 1])
                #
                elr_lor_dat['ELR_URL'] = [urllib.parse.urljoin(self.HomeURL, x) for x in elr_links]
                elr_lor_dat['LOR_URL'] = [self.HomeURL + 'pride/' + x for x in lor_links]
                #
                elr_lor_converter = {'ELR_LOR_converter': elr_lor_dat, 'Last_updated_date': get_last_updated_date(url)}

                save_pickle(elr_lor_converter, self.cd_lor("elr-lor-converter.pickle"), verbose)

            except Exception as e:
                print("Failed to collect \"ELR/LOR converter\". {}".format(e))
                elr_lor_converter = None

            return elr_lor_converter

    # Fetch ELR/LOR converter
    def fetch_elr_lor_converter(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        pickle_filename = "elr-lor-converter.pickle"
        path_to_pickle = self.cd_lor(pickle_filename)

        if os.path.isfile(path_to_pickle) and not update:
            elr_lor_converter = load_pickle(path_to_pickle)

        else:
            elr_lor_converter = self.collect_elr_lor_converter(confirmation_required=False,
                                                               verbose=False if data_dir or not verbose else True)
            if elr_lor_converter:  # codes_for_ole is not None
                if pickle_it and data_dir:
                    self.CurrentDataDir = regulate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, pickle_filename)
                    save_pickle(elr_lor_converter, path_to_pickle, verbose=True)
            else:
                print("No data of \"ELR/LOR converter\" has been collected for national network OLE installations.")

        return elr_lor_converter
