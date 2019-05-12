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

from pyrcscraper.utils import cd_dat, cdd, load_pickle, parse_tr, regulate_input_data_dir, save_pickle
from pyrcscraper.utils import confirmed, get_cls_catalogue, get_last_updated_date


class LOR:
    def __init__(self, data_dir=None):
        self.Name = 'Line of Route (LOR/PRIDE) codes'
        self.URL = 'http://www.railwaycodes.org.uk/pride/pride0.shtm'
        self.Catalogue = get_cls_catalogue(self.URL)
        self.Date = get_last_updated_date(self.URL, parsed=True, date_type=False)
        self.DataDir = regulate_input_data_dir(data_dir) if data_dir else cdd("Line data", "Line of route codes")

    # Change directory to "dat\\Line data\\Line of route" and sub-directories
    @staticmethod
    def cd_lor(*sub_dir):
        path = cd_dat("Line data", "Line of route codes")
        os.makedirs(path, exist_ok=True)
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    # Change directory to "dat\\Line data\\Line of route\\dat" and sub-directories
    def cdd_lor(self, *sub_dir):
        path = self.cd_lor("dat")
        os.makedirs(path, exist_ok=True)
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    # Get key to LOR code prefixes
    def get_key_to_prefixes(self, prefixes_only=True, update=False):
        path_to_pickle = self.cdd_lor("{}prefixes.pickle".format("" if prefixes_only else "key-to-"))
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
                urls = list(dict.fromkeys([self.URL.replace(os.path.basename(self.URL), l['href']) for l in links]))
                save_pickle(urls, path_to_pickle)
            except Exception as e:
                print("Failed to get the \"urls\" to LOR codes web pages. {}.".format(e))
                urls = []
        return urls

    # Update catalogue data
    def __update__(self):
        if confirmed("To update catalogue?"):
            self.get_key_to_prefixes(prefixes_only=True, update=True)
            self.get_key_to_prefixes(prefixes_only=False, update=True)
            self.get_lor_page_urls(update=True)

    # Collect LOR codes by prefix
    def collect_lor_codes_by_prefix(self, prefixes):

        assert prefixes in self.get_key_to_prefixes(prefixes_only=True), \
            "\"prefixes\" must be one of {}".format(self.get_key_to_prefixes(prefixes_only=True))

        pickle_filename = "{}.pickle".format(prefixes if prefixes not in ("NW", "NZ") else "NW-NZ")
        path_to_pickle = os.path.join(self.cd_lor(), pickle_filename)

        try:
            prefixes = "NW" if prefixes in ("NW", "NZ") else prefixes
            url = 'http://www.railwaycodes.org.uk/pride/pride{}.shtm'.format(prefixes.lower())
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
                code_dat = pd.concat([code_dat, line_name_info], axis=1)
                try:
                    note_dat = dict([(x['name'].title(), x.text) for x in soup.find('ol').findChildren('a')])
                except AttributeError:
                    note_dat = dict([('Note', None)])
                return code_dat, note_dat

            h3, table_soup = soup.find_all('h3'), soup.find_all('table', {'width': '1100px'})
            if len(h3) == 0:
                code_data, code_data_notes = parse_h3_table(table_soup)
                lor_codes_by_initials = {'Code': code_data, 'Note': code_data_notes}
            else:
                code_data_and_notes = [dict(zip(['Code', 'Note'], parse_h3_table(x)))
                                       for x in zip(*[iter(table_soup)] * 2)]
                lor_codes_by_initials = dict(zip([x.text for x in h3], code_data_and_notes))

            save_pickle(lor_codes_by_initials, path_to_pickle)

        except Exception as e:
            print("Failed to get LOR codes by prefix \"{}\". {}.".format(prefixes, e))
            lor_codes_by_initials = {}

        return lor_codes_by_initials

    # Fetch LOR codes by prefix
    def fetch_lor_codes_by_prefix(self, prefixes, update=False):
        pickle_filename = "{}.pickle".format(prefixes if prefixes not in ("NW", "NZ") else "NW-NZ")
        path_to_pickle = os.path.join(self.cd_lor(), pickle_filename)
        if not os.path.isfile(path_to_pickle) or update:
            self.collect_lor_codes_by_prefix(prefixes)
        try:
            lor_codes_by_initials = load_pickle(path_to_pickle)
            return lor_codes_by_initials
        except Exception as e:
            print(e)

    # Fetch all LOR codes either locally or from online
    def fetch_lor_codes(self, update=False):
        path_to_pickle = os.path.join(self.DataDir, "LOR-codes.pickle")
        if not os.path.isfile(path_to_pickle) or update:
            prefixes = self.get_key_to_prefixes(prefixes_only=True, update=update)
            lor_codes = [self.fetch_lor_codes_by_prefix(p, update) for p in prefixes if p != 'NZ']
            save_pickle(lor_codes, path_to_pickle)
        try:
            lor_codes = load_pickle(path_to_pickle)
            return lor_codes
        except Exception as e:
            print(e)

    # Collect ELR/LOR converter
    def collect_elr_lor_converter(self):
        path_to_pickle = os.path.join(self.cd_lor(), "ELR-LOR-converter.pickle")
        url = self.Catalogue['ELR/LOR converter']
        try:
            page_data = pd.read_html(url)
            headers, elr_lor_dat = page_data
            elr_lor_dat.columns = list(headers)
            #
            source = requests.get(url)
            soup = bs4.BeautifulSoup(source.text, 'lxml')
            tds = soup.find_all('td')
            links = [x.get('href') for x in [x.find('a', href=True) for x in tds] if x is not None]
            main_url = 'http://www.railwaycodes.org.uk/'
            elr_links, lor_links = [x for x in links[::2]], [x for x in links[1::2]]
            #
            elr_lor_dat['ELR_URL'] = [urllib.parse.urljoin(main_url, x) for x in elr_links]
            elr_lor_dat['LOR_URL'] = [main_url + 'pride/' + x for x in lor_links]
            #
            elr_lor_converter = {'ELR_LOR_converter': elr_lor_dat, 'Last_updated_date': get_last_updated_date(url)}
            save_pickle(elr_lor_converter, path_to_pickle)
        except Exception as e:
            print("Failed to collect \"ELR/LOR converter\". {}.".format(e))

    # Get ELR/LOR converter
    def fetch_elr_lor_converter(self, update=False):
        path_to_pickle = os.path.join(self.cd_lor(), "ELR-LOR-converter.pickle")
        if not os.path.isfile(path_to_pickle) or update:
            self.collect_elr_lor_converter()
        try:
            elr_lor_converter = load_pickle(path_to_pickle)
        except Exception as e:
            elr_lor_converter = {}
            print("Failed to get \"ELR/LOR converter\". {}.".format(e))
        return elr_lor_converter
