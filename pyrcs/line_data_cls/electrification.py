""" A class for collecting section codes for OLE installations.

Data source: http://www.railwaycodes.org.uk/electrification/mast_prefix0.shtm
"""

import copy
import os
import re

import bs4
import pandas as pd
import requests
from pyhelpers.dir import regulate_input_data_dir
from pyhelpers.ops import confirmed
from pyhelpers.store import load_pickle, save_pickle

from pyrcs.utils import cd_dat, fake_requests_headers, get_catalogue, get_last_updated_date, homepage_url, parse_tr


class Electrification:
    """
    A class for collecting codes associated with British railway overhead electrification installations.

    :param data_dir: name of data directory, defaults to ``None``
    :type data_dir: str, None

    **Example**::

        from pyrcs.line_data import Electrification

        elec = Electrification()

        print(elec.Name)
        # Electrification

        print(elec.SourceURL)
        # http://www.railwaycodes.org.uk/electrification/mast_prefix0.shtm
    """

    def __init__(self, data_dir=None):
        """
        Constructor method.
        """
        self.Name = 'Electrification'
        self.HomeURL = homepage_url()
        self.SourceURL = self.HomeURL + '/electrification/mast_prefix0.shtm'
        self.Catalogue = get_catalogue(self.SourceURL)
        self.Date = get_last_updated_date(self.SourceURL, parsed=True, as_date_type=False)
        self.DataDir = regulate_input_data_dir(data_dir) if data_dir else cd_dat("line-data", 'electrification')
        self.CurrentDataDir = copy.copy(self.DataDir)
        self.Key = 'Electrification'
        self.LUDKey = 'Last_updated_date'  # key to last updated date

    def cdd_elec(self, *sub_dir):
        """
        Change directory to "dat\\line-data\\electrification\\" and sub-directories (and/or a file)

        :param sub_dir: sub-directory or sub-directories (and/or a file)
        :type sub_dir: str
        :return: path to the backup data directory for ``Electrification``
        :rtype: str

        :meta private:
        """

        path = self.DataDir
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    def collect_codes_for_national_network(self, confirmation_required=True, verbose=False):
        """
        Collect OLE section codes for National network from source web page.

        :param confirmation_required: whether to require users to confirm and proceed, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool
        :return: OLE section codes for National network, in the form {<name>: <code>, ..., 'Last_updated_date': <date>}
        :rtype: dict, None

        **Example**::

            from pyrcs.line_data import Electrification

            elec = Electrification()

            confirmation_required = True
            verbose = True

            national_network_ole = elec.collect_codes_for_national_network(confirmation_required, verbose)

            print(national_network_ole)
            # {<name>: <code>,
            #  ...,
            #  'Last_updated_date': <date>}
        """

        if confirmed("To collect section codes for OLE installations: national network? ",
                     confirmation_required=confirmation_required):

            title_name = 'National network'
            url = self.Catalogue[title_name]

            if verbose:
                print("Collecting the section codes for OLE installations: national network", end=" ... ")
            try:
                source = requests.get(url, headers=fake_requests_headers())
                soup = bs4.BeautifulSoup(source.text, 'lxml')

                national_network_ole, h3 = {}, soup.find('h3')
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
                        notes_ = dict((x.a.get('id').title(), x.get_text(strip=True).replace('\xa0', ''))
                                      for x in soup.find('ol') if x != '\n')
                        if notes['Notes'] is None:
                            notes['Notes'] = notes_
                        else:
                            notes['Notes'] = [notes['Notes'], notes_]

                    data_key = re.search(r'(\w ?)+(?=( \((\w ?)+\))?)', h3.text).group(0)
                    national_network_ole.update({data_key.strip(): {'Codes': table, **notes}})

                    h3 = h3.find_next_sibling('h3')

                source.close()

                last_updated_date = get_last_updated_date(url)
                national_network_ole.update({self.LUDKey: last_updated_date})

                print("Done. ") if verbose else ""

                path_to_pickle = self.cdd_elec(title_name.lower().replace(" ", "-") + ".pickle")
                save_pickle(national_network_ole, path_to_pickle, verbose=verbose)

            except Exception as e:
                print("Failed. {}".format(e))
                national_network_ole = None

            return national_network_ole

    def fetch_codes_for_national_network(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch OLE section codes for National network from local backup.

        :param update: whether to check on update and proceed to update the package data, defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data with newly collected data, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str, None
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool
        :return: OLE section codes for National network, in the form {<name>: <code>, ..., 'Last_updated_date': <date>}
        :rtype: dict, None

        **Example**::

            from pyrcs.line_data import Electrification

            elec = Electrification()

            update = False
            pickle_it = False
            data_dir = None
            verbose = True

            national_network_ole = elec.fetch_codes_for_national_network(update, pickle_it, data_dir,
                                                                         verbose)

            print(national_network_ole)
            # {<name>: <code>,
            #  ...,
            #  'Last_updated_date': <date>}
        """

        pickle_filename = "national-network.pickle"
        path_to_pickle = self.cdd_elec(pickle_filename)

        if os.path.isfile(path_to_pickle) and not update:
            national_network_ole = load_pickle(path_to_pickle, verbose=verbose)

        else:
            national_network_ole = self.collect_codes_for_national_network(
                confirmation_required=False, verbose=False if data_dir or not verbose else True)

            if national_network_ole:  # codes_for_ole is not None
                if pickle_it and data_dir:
                    self.CurrentDataDir = regulate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, pickle_filename)
                    save_pickle(national_network_ole, path_to_pickle, verbose=verbose)
            else:
                print("No data of section codes has been collected for national network OLE installations.")

        return national_network_ole

    def get_names_of_independent_lines(self):
        """
        Get names of independent lines.

        :return: a list of independent line names
        :rtype: list

        **Example**::

            from pyrcs.line_data import Electrification

            elec = Electrification()

            line_names = elec.get_names_of_independent_lines()

            print(line_names)
            # a list of independent line names
        """

        url = self.Catalogue['Independent lines']
        source = requests.get(url, headers=fake_requests_headers())
        soup = bs4.BeautifulSoup(source.text, 'lxml')
        for x in soup.find_all('p'):
            if re.match(r'^Jump to: ', x.text):
                line_names = x.text.replace('Jump to: ', '').split(' | ')
                return line_names

    def collect_codes_for_independent_lines(self, confirmation_required=True, verbose=False):
        """
        Collect OLE section codes for independent lines from source web page.

        :param confirmation_required: whether to require users to confirm and proceed, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool
        :return: OLE section codes for independent lines, in the form {<name>: <code>, ..., 'Last_updated_date': <date>}
        :rtype: dict, None

        **Example**::

            from pyrcs.line_data import Electrification

            elec = Electrification()

            confirmation_required = True
            verbose = True

            independent_lines_ole = elec.collect_codes_for_independent_lines(confirmation_required, verbose)
        """

        if confirmed("To collect section codes for OLE installations: independent lines?",
                     confirmation_required=confirmation_required):

            title_name = 'Independent lines'
            url = self.Catalogue[title_name]

            if verbose:
                print("Collecting the section codes for OLE installations: independent lines", end=" ... ")
            try:
                source = requests.get(url, headers=fake_requests_headers())
                soup = bs4.BeautifulSoup(source.text, 'lxml')

                independent_lines_ole = {}
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
                            notes_ = dict((x.a.get('id').title(), x.get_text(strip=True).replace('\xa0', ''))
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
                            li = pd.DataFrame(list(re.sub(r'[()]', '', x.text).split(' ', 1)
                                                   for x in ex_note_tag.find_all('li')), columns=['Initial', 'Code'])
                            notes.update({'Section codes known at present': li})

                    independent_lines_ole.update({h3.text: {'Codes': table, **notes}})

                    h3 = h3.find_next_sibling('h3')

                source.close()

                last_updated_date = get_last_updated_date(url)
                independent_lines_ole.update({self.LUDKey: last_updated_date})

                print("Done. ") if verbose else ""

                path_to_pickle = self.cdd_elec(title_name.lower().replace(" ", "-") + ".pickle")
                save_pickle(independent_lines_ole, path_to_pickle, verbose=verbose)

            except Exception as e:
                print("Failed. {}".format(e))
                independent_lines_ole = None

            return independent_lines_ole

    def fetch_codes_for_independent_lines(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch OLE section codes for independent lines from local backup.

        :param update: whether to check on update and proceed to update the package data, defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data with newly collected data, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str, None
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool
        :return: OLE section codes for independent lines, in the form {<name>: <code>, ..., 'Last_updated_date': <date>}
        :rtype: dict

        **Example**::

            from pyrcs.line_data import Electrification

            elec = Electrification()

            update = False
            pickle_it = False
            data_dir = None
            verbose = True

            independent_lines_ole = elec.fetch_codes_for_independent_lines(update, pickle_it, data_dir,
                                                                           verbose)
        """

        pickle_filename = "independent-lines.pickle"
        path_to_pickle = self.cdd_elec(pickle_filename)

        if os.path.isfile(path_to_pickle) and not update:
            independent_lines_ole = load_pickle(path_to_pickle, verbose=verbose)

        else:
            independent_lines_ole = self.collect_codes_for_independent_lines(
                confirmation_required=False, verbose=False if data_dir or not verbose else True)

            if independent_lines_ole:  # codes_for_independent_lines is not None
                if pickle_it and data_dir:
                    self.CurrentDataDir = regulate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, pickle_filename)
                    save_pickle(independent_lines_ole, path_to_pickle, verbose=verbose)
            else:
                print("No data of section codes has been collected for independent lines OLE installations.")

        return independent_lines_ole

    def collect_codes_for_ohns(self, confirmation_required=True, verbose=False):
        """
        Collect codes for overhead line electrification neutral sections (OHNS) from source web page.

        :param confirmation_required: whether to require users to confirm and proceed, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool
        :return: OHNS codes in the form {<name>: <code>, ..., 'Last_updated_date': <date>}
        :rtype: dict, None

        **Example**::

            from pyrcs.line_data import Electrification

            elec = Electrification()

            confirmation_required = True
            verbose = True

            ohns_codes = elec.collect_codes_for_ohns(confirmation_required, verbose)
        """

        if confirmed("To collect codes for OLE neutral sections (OHNS)?", confirmation_required=confirmation_required):

            title_name = 'National network neutral sections'
            url = self.Catalogue[title_name]

            if verbose:
                print("Collecting OHNS codes", end=" ... ")
            try:
                header, neutral_sections_data = pd.read_html(url)
                neutral_sections_data.columns = header.columns.to_list()
                neutral_sections_data.fillna('', inplace=True)

                last_updated_date = get_last_updated_date(url)
                ohns_codes = {'Codes': neutral_sections_data, self.LUDKey: last_updated_date}

                print("Done. ") if verbose else ""

                path_to_pickle = self.cdd_elec(title_name.lower().replace(" ", "-") + ".pickle")
                save_pickle(ohns_codes, path_to_pickle, verbose=verbose)

            except Exception as e:
                print("Failed. {}".format(e))
                ohns_codes = None

            return ohns_codes

    def fetch_codes_for_ohns(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch codes for overhead line electrification neutral sections (OHNS) from local backup.

        :param update: whether to check on update and proceed to update the package data, defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data with newly collected data, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str, None
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool
        :return: OHNS codes in the form {<name>: <code>, ..., 'Last_updated_date': <date>}
        :rtype: dict

        **Example**::

            from pyrcs.line_data import Electrification

            elec = Electrification()

            update = False
            pickle_it = False
            data_dir = None
            verbose = True

            ohns_codes = elec.fetch_codes_for_ohns(update, pickle_it, data_dir, verbose)
        """

        pickle_filename = "national-network-neutral-sections.pickle"
        path_to_pickle = self.cdd_elec(pickle_filename)

        if os.path.isfile(path_to_pickle) and not update:
            ohns_codes = load_pickle(path_to_pickle, verbose=verbose)

        else:
            ohns_codes = self.collect_codes_for_ohns(confirmation_required=False,
                                                     verbose=False if data_dir or not verbose else True)

            if ohns_codes:  # ohns is not None
                if pickle_it and data_dir:
                    self.CurrentDataDir = regulate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, pickle_filename)
                    save_pickle(ohns_codes, path_to_pickle, verbose=verbose)
            else:
                print("No data of section codes for OHNS has been collected.")

        return ohns_codes

    def collect_codes_for_energy_tariff_zones(self, confirmation_required=True, verbose=False):
        """
        Collect OLE section codes for national network energy tariff zones from source web page.

        :param confirmation_required: whether to require users to confirm and proceed, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool
        :return: OLE section codes for national network energy tariff zones,
            in the form {<name>: <code>, ..., 'Last_updated_date': <date>}
        :rtype: dict, None

        **Example**::

            from pyrcs.line_data import Electrification

            elec = Electrification()

            confirmation_required = True
            verbose = True

            etz_ole = elec.collect_codes_for_energy_tariff_zones(confirmation_required, verbose)
        """

        if confirmed("To collect codes for the UK railway electrification tariff zones?",
                     confirmation_required=confirmation_required):

            title_name = 'National network energy tariff zones'
            url = self.Catalogue[title_name]

            if verbose:
                print("Collecting OLE sections codes for the UK railway electrification tariff zones", end=" ... ")
            try:
                source = requests.get(url)
                soup = bs4.BeautifulSoup(source.text, 'lxml')

                etz_ole = {}
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

                    etz_ole.update({h3.text: {'Codes': table, 'Notes': notes}})

                    h3 = h3.find_next_sibling('h3')

                source.close()

                last_updated_date = get_last_updated_date(url)
                etz_ole.update({self.LUDKey: last_updated_date})

                print("Done. ") if verbose else ""

                path_to_pickle = self.cdd_elec(title_name.lower().replace(" ", "-") + ".pickle")
                save_pickle(etz_ole, path_to_pickle, verbose=verbose)

            except Exception as e:
                print("Failed. {}".format(e))
                etz_ole = None

            return etz_ole

    def fetch_codes_for_energy_tariff_zones(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch OLE section codes for national network energy tariff zones from source web page.

        :param update: whether to check on update and proceed to update the package data, defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data with newly collected data, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str, None
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool
        :return: OLE section codes for national network energy tariff zones,
            in the form {<name>: <code>, ..., 'Last_updated_date': <date>}
        :rtype: dict

        **Example**::

            from pyrcs.line_data import Electrification

            elec = Electrification()

            update = False
            pickle_it = False
            data_dir = None
            verbose = True

            etz_ole = elec.fetch_codes_for_energy_tariff_zones(update, pickle_it, data_dir, verbose)
        """

        pickle_filename = "national-network-energy-tariff-zones.pickle"
        path_to_pickle = self.cdd_elec(pickle_filename)

        if os.path.isfile(path_to_pickle) and not update:
            etz_ole = load_pickle(path_to_pickle, verbose=verbose)

        else:
            etz_ole = self.collect_codes_for_energy_tariff_zones(
                confirmation_required=False, verbose=False if data_dir or not verbose else True)

            if etz_ole:  # codes_for_energy_tariff_zones is not None
                if pickle_it and data_dir:
                    self.CurrentDataDir = regulate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, pickle_filename)
                    save_pickle(etz_ole, path_to_pickle, verbose=verbose)
            else:
                print("No data of section codes has been collected for the UK railway electrification tariff zones.")

        return etz_ole

    def fetch_electrification_codes(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch OLE section codes in the electrification catalogue.

        :param update: whether to check on update and proceed to update the package data, defaults to ``False``
        :type update: bool
        :param pickle_it: whether to replace the current package data with newly collected data, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of package data folder, defaults to ``None``
        :type data_dir: str, None
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool
        :return: section codes for overhead line electrification (OLE) installations
        :rtype: dict

        **Example**::

            from pyrcs.line_data import Electrification

            elec = Electrification()

            update = False
            pickle_it = False
            data_dir = None
            verbose = True

            ole_section_codes = elec.fetch_electrification_codes(update, pickle_it, data_dir, verbose)
        """

        national_network = self.fetch_codes_for_national_network(update, verbose=verbose)
        independent_lines = self.fetch_codes_for_independent_lines(update, verbose=verbose)
        ohns = self.fetch_codes_for_ohns(update, verbose=verbose)
        energy_tariff_zones = self.fetch_codes_for_energy_tariff_zones(update, verbose=verbose)

        keys = list(self.Catalogue.keys())
        keys.remove('Introduction')

        ole_section_codes = {
            self.Key: dict(zip(keys, [national_network, independent_lines, ohns, energy_tariff_zones]))}

        if pickle_it and data_dir:
            pickle_filename = "electrification-codes.pickle"
            self.CurrentDataDir = regulate_input_data_dir(data_dir)
            path_to_pickle = os.path.join(self.CurrentDataDir, pickle_filename)
            save_pickle(ole_section_codes, path_to_pickle, verbose=verbose)

        return ole_section_codes
