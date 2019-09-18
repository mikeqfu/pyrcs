"""

Data source: http://www.railwaycodes.org.uk

Section codes for overhead line electrification (OLE) installations
(http://www.railwaycodes.org.uk/electrification/mast_prefix0.shtm)

"""

import copy
import os
import re

import bs4
import pandas as pd
import requests
from pyhelpers.dir import regulate_input_data_dir
from pyhelpers.misc import confirmed
from pyhelpers.store import load_pickle

from pyrcs.utils import cd_dat, get_catalogue, get_last_updated_date, parse_tr, save_pickle


class Electrification:
    def __init__(self, data_dir=None):
        self.HomeURL = 'http://www.railwaycodes.org.uk'
        self.Name = 'Electrification'
        self.URL = self.HomeURL + '/electrification/mast_prefix0.shtm'
        self.Catalogue = get_catalogue(self.URL)
        self.Date = get_last_updated_date(self.URL, parsed=True, date_type=False)
        self.DataDir = regulate_input_data_dir(data_dir) if data_dir else cd_dat("line-data", 'electrification')
        self.CurrentDataDir = copy.copy(self.DataDir)

    # Change directory to "dat\\line-data\\electrification" and sub-directories
    def cd_elec(self, *sub_dir):
        path = self.DataDir
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    # Change directory to "dat\\line-data\\electrification\\dat" and sub-directories
    def cdd_elec(self, *sub_dir):
        path = self.cd_elec("dat")
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    # National network
    def collect_codes_for_national_network(self, confirmation_required=True, verbose=False):
        if confirmed("To collect section codes for OLE installations: national network?",
                     confirmation_required=confirmation_required):
            title_name = 'National network'
            url = self.Catalogue[title_name]

            try:
                source = requests.get(url)
                soup = bs4.BeautifulSoup(source.text, 'lxml')

                codes_for_ole, h3 = {}, soup.find('h3')
                while h3:
                    header_tag = h3.find_next('table')
                    if header_tag:
                        header = [x.text for x in header_tag.find_all('th')]

                        table = pd.DataFrame(parse_tr(header, header_tag.find_next('table').find_all('tr')),
                                             columns=header)
                        table = table.applymap(
                            lambda x: re.sub(r'\']\)?', ']', re.sub(r'\(?\[\'', '[', x)).replace('\\xa0', ''))
                    else:
                        table = pd.DataFrame((x.text for x in h3.find_all_next('li')), columns=['Unknown_codes'])

                    # Notes
                    notes = {'Notes': None}
                    if h3.find_next_sibling().name == 'p':
                        next_p = h3.find_next('p')
                        if next_p.find_previous('h3') == h3:
                            notes['Notes'] = next_p.text.replace('\xa0', '')

                    note_tag = h3.find_next('h4')
                    if note_tag and note_tag.text == 'Notes':
                        notes_ = dict((x.find('a').get('name').title(), x.text.replace('\xa0', ''))
                                      for x in soup.find('ol') if x != '\n')
                        if notes['Notes'] is None:
                            notes['Notes'] = notes_
                        else:
                            notes['Notes'] = [notes['Notes'], notes_]

                    data_key = re.search(r'(\w ?)+(?=( \((\w ?)+\))?)', h3.text).group(0)
                    codes_for_ole.update({data_key.strip(): {'Codes': table, **notes}})

                    h3 = h3.find_next_sibling('h3')

                source.close()

                last_updated_date = get_last_updated_date(url)
                codes_for_ole.update({'Last_updated_date': last_updated_date})

                path_to_pickle = self.cd_elec(title_name.lower().replace(" ", "-") + ".pickle")
                save_pickle(codes_for_ole, path_to_pickle, verbose)

            except Exception as e:
                print("Failed to collect section codes for OLE installations: national network. {}".format(e))
                codes_for_ole = None

            return codes_for_ole

    # Fetch codes for national network
    def fetch_codes_for_national_network(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        pickle_filename = "national-network.pickle"
        path_to_pickle = self.cd_elec(pickle_filename)

        if os.path.isfile(path_to_pickle) and not update:
            codes_for_ole = load_pickle(path_to_pickle)

        else:
            codes_for_ole = self.collect_codes_for_national_network(
                confirmation_required=False, verbose=False if data_dir or not verbose else True)

            if codes_for_ole:  # codes_for_ole is not None
                if pickle_it and data_dir:
                    self.CurrentDataDir = regulate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, pickle_filename)
                    save_pickle(codes_for_ole, path_to_pickle, verbose=True)
            else:
                print("No data of section codes has been collected for national network OLE installations.")

        return codes_for_ole

    # Get names of independent lines
    def get_names_of_independent_lines(self):
        url = self.Catalogue['Independent lines']
        source = requests.get(url)
        soup = bs4.BeautifulSoup(source.text, 'lxml')
        for x in soup.find_all('p'):
            if re.match(r'^Jump to: ', x.text):
                line_names = x.text.replace('Jump to: ', '').split(' | ')
                return line_names

    # Independent lines
    def collect_codes_for_independent_lines(self, confirmation_required=True, verbose=False):
        if confirmed("To collect section codes for OLE installations: independent lines?",
                     confirmation_required=confirmation_required):
            title_name = 'Independent lines'
            url = self.Catalogue[title_name]
            try:
                source = requests.get(url)
                soup = bs4.BeautifulSoup(source.text, 'lxml')

                codes_for_independent_lines = {}
                h3 = soup.find('h3')
                while h3:
                    header_tag, table = h3.find_next('table'), None
                    if header_tag:
                        if header_tag.find_previous('h3') == h3:
                            header = [x.text for x in header_tag.find_all('th')]
                            table = pd.DataFrame(parse_tr(header, header_tag.find_next('table').find_all('tr')),
                                                 columns=header)
                            table = table.applymap(
                                lambda x: re.sub(
                                    r'\']\)?', ']', re.sub(r'\(?\[\'', '[', x)).replace('\\xa0', '').strip())

                    notes = {'Notes': None}
                    h4 = h3.find_next('h4')
                    if h4:
                        previous_h3 = h4.find_previous('h3')
                        if previous_h3 == h3 and h4.text == 'Notes':
                            notes_ = dict((x.find('a').get('name').title(), x.text.replace('\xa0', ''))
                                          for x in h4.find_next('ol') if x != '\n')
                            if notes['Notes'] is None:
                                notes['Notes'] = notes_

                    note_tag, note_txt = h3.find_next('p'), ''
                    if note_tag:
                        previous_h3 = note_tag.find_previous('h3')
                        if previous_h3 == h3:
                            note_txt = note_tag.text.replace('\xa0', '')
                            if notes['Notes'] is None:
                                notes['Notes'] = note_txt
                            else:
                                notes['Notes'] = [notes['Notes'], note_txt]

                    ex_note_tag = note_tag.find_next('ol')
                    if ex_note_tag:
                        previous_h3 = ex_note_tag.find_previous('h3')
                        if previous_h3 == h3:
                            li = dict(re.sub(r'[()]', '', x.text).split(' ', 1) for x in ex_note_tag.find_all('li'))
                            notes.update(li)

                    codes_for_independent_lines.update({h3.text: {'Codes': table, **notes}})

                    h3 = h3.find_next_sibling('h3')

                source.close()

                last_updated_date = get_last_updated_date(url)
                codes_for_independent_lines.update({'Last_updated_date': last_updated_date})

                path_to_pickle = self.cd_elec(title_name.lower().replace(" ", "-") + ".pickle")
                save_pickle(codes_for_independent_lines, path_to_pickle, verbose)

            except Exception as e:
                print("Failed to collect section codes for OLE installations: independent lines. {}".format(e))
                codes_for_independent_lines = None

            return codes_for_independent_lines

    # Fetch codes for independent lines
    def fetch_codes_for_independent_lines(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        pickle_filename = "independent-lines.pickle"
        path_to_pickle = self.cd_elec(pickle_filename)

        if os.path.isfile(path_to_pickle) and not update:
            codes_for_independent_lines = load_pickle(path_to_pickle)

        else:
            codes_for_independent_lines = self.collect_codes_for_independent_lines(
                confirmation_required=False, verbose=False if data_dir or not verbose else True)

            if codes_for_independent_lines:  # codes_for_independent_lines is not None
                if pickle_it and data_dir:
                    self.CurrentDataDir = regulate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, pickle_filename)
                    save_pickle(codes_for_independent_lines, path_to_pickle, verbose=True)
            else:
                print("No data of section codes has been collected for independent lines OLE installations.")

        return codes_for_independent_lines

    # National network neutral sections
    def collect_codes_for_ohns(self, confirmation_required=True, verbose=False):
        if confirmed("To collect codes for OLE neutral sections (OHNS)?", confirmation_required=confirmation_required):
            title_name = 'National network neutral sections'
            url = self.Catalogue[title_name]

            try:
                header, neutral_sections_data = pd.read_html(url)
                neutral_sections_data.columns = header.columns.to_list()
                neutral_sections_data.fillna('', inplace=True)

                last_updated_date = get_last_updated_date(url)
                ohns = {'Codes': neutral_sections_data, 'Last_updated_date': last_updated_date}

                path_to_pickle = self.cd_elec(title_name.lower().replace(" ", "-") + ".pickle")
                save_pickle(ohns, path_to_pickle, verbose)

            except Exception as e:
                print("Failed to collect codes for OLE neutral sections (OHNS). {}".format(e))
                ohns = None

            return ohns

    # Fetch codes for Overhead line electrification neutral sections (OHNS)
    def fetch_codes_for_ohns(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        pickle_filename = "national-network-neutral-sections.pickle"
        path_to_pickle = self.cd_elec(pickle_filename)

        if os.path.isfile(path_to_pickle) and not update:
            ohns = load_pickle(path_to_pickle)

        else:
            ohns = self.collect_codes_for_ohns(confirmation_required=False,
                                               verbose=False if data_dir or not verbose else True)

            if ohns:  # ohns is not None
                if pickle_it and data_dir:
                    self.CurrentDataDir = regulate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, pickle_filename)
                    save_pickle(ohns, path_to_pickle, verbose=True)
            else:
                print("No data of section codes for OHNS has been collected.")

        return ohns

    # National network energy tariff zones
    def collect_codes_for_energy_tariff_zones(self, confirmation_required=True, verbose=False):
        if confirmed("To collect codes for the UK railway electrification tariff zones?",
                     confirmation_required=confirmation_required):
            title_name = 'National network energy tariff zones'
            url = self.Catalogue[title_name]
            try:
                source = requests.get(url)
                soup = bs4.BeautifulSoup(source.text, 'lxml')

                codes_for_energy_tariff_zones = {}
                h3 = soup.find('h3')
                while h3:
                    header_tag, table = h3.find_next('table'), None
                    if header_tag:
                        if header_tag.find_previous('h3') == h3:
                            header = [x.text for x in header_tag.find_all('th')]
                            table = pd.DataFrame(parse_tr(header, header_tag.find_next('table').find_all('tr')),
                                                 columns=header)
                            table = table.applymap(
                                lambda x: re.sub(r'\']\)?', ']', re.sub(r'\(?\[\'', '[', x)).replace(
                                    '\\xa0', '').strip())

                    notes, next_p = [], h3.find_next('p')
                    previous_h3 = next_p.find_previous('h3')
                    while previous_h3 == h3:
                        notes.append(next_p.text.replace('\xa0', ''))
                        next_p = next_p.find_next('p')
                        try:
                            previous_h3 = next_p.find_previous('h3')
                        except AttributeError:
                            break
                    notes = ' '.join(notes).strip()

                    codes_for_energy_tariff_zones.update({h3.text: {'Codes': table, 'Notes': notes}})

                    h3 = h3.find_next_sibling('h3')

                source.close()

                last_updated_date = get_last_updated_date(url)
                codes_for_energy_tariff_zones.update({'Last_updated_date': last_updated_date})

                path_to_pickle = self.cd_elec(title_name.lower().replace(" ", "-") + ".pickle")
                save_pickle(codes_for_energy_tariff_zones, path_to_pickle, verbose)

            except Exception as e:
                print("Failed to collect the codes for UK railway electrification tariff zones. {}".format(e))
                codes_for_energy_tariff_zones = None

            return codes_for_energy_tariff_zones

    # Fetch codes for Overhead line electrification neutral sections (OHNS)
    def fetch_codes_for_energy_tariff_zones(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        pickle_filename = "national-network-energy-tariff-zones.pickle"
        path_to_pickle = self.cd_elec(pickle_filename)

        if os.path.isfile(path_to_pickle) and not update:
            codes_for_energy_tariff_zones = load_pickle(path_to_pickle)

        else:
            codes_for_energy_tariff_zones = self.collect_codes_for_energy_tariff_zones(
                confirmation_required=False, verbose=False if data_dir or not verbose else True)

            if codes_for_energy_tariff_zones:  # codes_for_energy_tariff_zones is not None
                if pickle_it and data_dir:
                    self.CurrentDataDir = regulate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, pickle_filename)
                    save_pickle(codes_for_energy_tariff_zones, path_to_pickle, verbose=True)
            else:
                print("No data of section codes has been collected for the UK railway electrification tariff zones.")

        return codes_for_energy_tariff_zones

    # Fetch codes in the electrification catalogue
    def fetch_electrification_codes(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        national_network = self.fetch_codes_for_national_network(update, verbose=verbose)
        independent_lines = self.fetch_codes_for_independent_lines(update, verbose=verbose)
        ohns = self.fetch_codes_for_ohns(update, verbose=verbose)
        energy_tariff_zones = self.fetch_codes_for_energy_tariff_zones(update, verbose=verbose)

        items = list(self.Catalogue.keys())
        items.remove('Introduction')

        electrification_codes = dict(zip(items, [national_network, independent_lines, ohns, energy_tariff_zones]))

        if pickle_it and data_dir:
            pickle_filename = "electrification-codes.pickle"
            self.CurrentDataDir = regulate_input_data_dir(data_dir)
            path_to_pickle = os.path.join(self.CurrentDataDir, pickle_filename)
            save_pickle(electrification_codes, path_to_pickle, verbose=True)

        return electrification_codes
