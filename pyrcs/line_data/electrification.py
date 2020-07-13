""" Collecting section codes for OLE installations.

Data source: http://www.railwaycodes.org.uk/electrification/mast_prefix0.shtm
"""

import copy
import itertools
import os
import re
import urllib.parse

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
        self.Name = 'Electrification masts and related features'
        self.HomeURL = homepage_url()
        self.SourceURL = urllib.parse.urljoin(self.HomeURL, '/electrification/mast_prefix0.shtm')
        self.Catalogue = get_catalogue(self.SourceURL, confirmation_required=False)
        self.Date = get_last_updated_date(self.SourceURL, parsed=True, as_date_type=False)
        self.Key = 'Electrification'
        self.LUDKey = 'Last updated date'  # key to last updated date
        self.DataDir = regulate_input_data_dir(data_dir) if data_dir else cd_dat("line-data", self.Key.lower())
        self.CurrentDataDir = copy.copy(self.DataDir)
        self.NationalNetworkKey = 'National network'
        self.NationalNetworkPickle = self.NationalNetworkKey.lower().replace(" ", "-")
        self.IndependentLinesKey = 'Independent lines'
        self.IndependentLinesPickle = self.IndependentLinesKey.lower().replace(" ", "-")
        self.OhnsKey = 'National network neutral sections'
        self.OhnsPickle = self.OhnsKey.lower().replace(" ", "-")
        self.TariffZonesKey = 'National network energy tariff zones'
        self.TariffZonesPickle = self.TariffZonesKey.lower().replace(" ", "-")

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
        :type verbose: bool, int
        :return: OLE section codes for National network
        :rtype: dict, None

        **Example**::

            from pyrcs.line_data import Electrification

            elec = Electrification()

            confirmation_required = True
            verbose = True

            national_network_ole = elec.collect_codes_for_national_network(confirmation_required, verbose)
            # To collect section codes for OLE installations: national network? [No]|Yes: >? yes

            print(national_network_ole)
            # {'National network': <code>,
            #  'Last_updated_date': <date>}
        """

        if confirmed("To collect section codes for OLE installations: {}?".format(self.NationalNetworkKey.lower()),
                     confirmation_required=confirmation_required):

            if verbose == 2:
                print("Collecting the codes for {}".format(self.NationalNetworkKey.lower()), end=" ... ")

            try:
                source = requests.get(self.Catalogue[self.NationalNetworkKey], headers=fake_requests_headers())
                soup = bs4.BeautifulSoup(source.text, 'lxml')

                national_network_ole_, h3 = {}, soup.find('h3')
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
                    national_network_ole_.update({data_key.strip(): table, **notes})

                    h3 = h3.find_next_sibling('h3')

                source.close()

                last_updated_date = get_last_updated_date(self.Catalogue[self.NationalNetworkKey])
                national_network_ole = {self.NationalNetworkKey: national_network_ole_, self.LUDKey: last_updated_date}

                print("Done. ") if verbose == 2 else ""

                path_to_pickle = self.cdd_elec(self.NationalNetworkPickle + ".pickle")
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
        :type verbose: bool, int
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

        path_to_pickle = self.cdd_elec(self.NationalNetworkPickle + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            national_network_ole = load_pickle(path_to_pickle, verbose=verbose)

        else:
            national_network_ole = self.collect_codes_for_national_network(
                confirmation_required=False, verbose=False if data_dir or not verbose else True)

            if national_network_ole:  # codes_for_ole is not None
                if pickle_it and data_dir:
                    self.CurrentDataDir = regulate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, self.NationalNetworkPickle + ".pickle")
                    save_pickle(national_network_ole, path_to_pickle, verbose=verbose)
            else:
                print("No data of {} has been collected.".format(self.NationalNetworkKey.lower()))

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

        source = requests.get(self.Catalogue[self.IndependentLinesKey], headers=fake_requests_headers())
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
        :type verbose: bool, int
        :return: OLE section codes for independent lines
        :rtype: dict, None

        **Example**::

            from pyrcs.line_data import Electrification

            elec = Electrification()

            confirmation_required = True
            verbose = True

            independent_lines_ole = elec.collect_codes_for_independent_lines(confirmation_required, verbose)
            # To collect section codes for OLE installations: independent lines? [No]|Yes: >? yes

            print(independent_lines_ole)
            # {'Independent lines': <codes>,
            #  'Last updated date': <date>}
        """

        if confirmed("To collect section codes for OLE installations: {}?".format(self.IndependentLinesKey.lower()),
                     confirmation_required=confirmation_required):

            if verbose == 2:
                print("Collecting the codes for {}".format(self.IndependentLinesKey.lower()), end=" ... ")

            try:
                source = requests.get(self.Catalogue[self.IndependentLinesKey], headers=fake_requests_headers())
                soup = bs4.BeautifulSoup(source.text, 'lxml')

                independent_lines_ole_ = {}
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

                    independent_lines_ole_.update({h3.text: table, **notes})

                    h3 = h3.find_next_sibling('h3')

                source.close()

                last_updated_date = get_last_updated_date(self.Catalogue[self.IndependentLinesKey])
                independent_lines_ole = {self.IndependentLinesKey: independent_lines_ole_,
                                         self.LUDKey: last_updated_date}

                print("Done. ") if verbose == 2 else ""

                pickle_filename = self.IndependentLinesKey.lower().replace(" ", "-") + ".pickle"
                path_to_pickle = self.cdd_elec(pickle_filename)
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
        :type verbose: bool, int
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

        pickle_filename = self.IndependentLinesKey.lower().replace(" ", "-") + ".pickle"
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
                print("No data of {} has been collected.".format(self.IndependentLinesKey.lower()))

        return independent_lines_ole

    def collect_codes_for_ohns(self, confirmation_required=True, verbose=False):
        """
        Collect codes for overhead line electrification neutral sections (OHNS) from source web page.

        :param confirmation_required: whether to require users to confirm and proceed, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool, int
        :return: OHNS codes in the form {<name>: <code>, ..., 'Last_updated_date': <date>}
        :rtype: dict, None

        **Example**::

            from pyrcs.line_data import Electrification

            elec = Electrification()

            confirmation_required = True
            verbose = True

            ohns_codes = elec.collect_codes_for_ohns(confirmation_required, verbose)
            # To collect section codes for OLE installations: national network neutral sections? [No]|Yes:
            # >? yes

            print(ohns_codes)
            # {'National network neutral sections': <codes>,
            #  'Last updated date': <date>}
        """

        if confirmed("To collect section codes for OLE installations: {}?".format(self.OhnsKey.lower()),
                     confirmation_required=confirmation_required):

            if verbose == 2:
                print("Collecting data of {}".format(self.OhnsKey.lower()), end=" ... ")

            try:
                header, neutral_sections_data = pd.read_html(self.Catalogue[self.OhnsKey])
                neutral_sections_data.columns = header.columns.to_list()
                neutral_sections_data.fillna('', inplace=True)

                ohns_codes = {self.OhnsKey: neutral_sections_data,
                              self.LUDKey: get_last_updated_date(self.Catalogue[self.OhnsKey])}

                print("Done. ") if verbose == 2 else ""

                path_to_pickle = self.cdd_elec(self.OhnsPickle + ".pickle")
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
        :type verbose: bool, int
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

        path_to_pickle = self.cdd_elec(self.OhnsPickle + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            ohns_codes = load_pickle(path_to_pickle, verbose=verbose)

        else:
            ohns_codes = self.collect_codes_for_ohns(confirmation_required=False,
                                                     verbose=False if data_dir or not verbose else True)

            if ohns_codes:  # ohns is not None
                if pickle_it and data_dir:
                    self.CurrentDataDir = regulate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, self.OhnsPickle + ".pickle")
                    save_pickle(ohns_codes, path_to_pickle, verbose=verbose)
            else:
                print("No data of section codes for {} has been collected.".format(self.OhnsKey.lower()))

        return ohns_codes

    def collect_codes_for_energy_tariff_zones(self, confirmation_required=True, verbose=False):
        """
        Collect OLE section codes for national network energy tariff zones from source web page.

        :param confirmation_required: whether to require users to confirm and proceed, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
        :type verbose: bool, int
        :return: OLE section codes for national network energy tariff zones,
            in the form {<name>: <code>, ..., 'Last_updated_date': <date>}
        :rtype: dict, None

        **Example**::

            from pyrcs.line_data import Electrification

            elec = Electrification()

            confirmation_required = True
            verbose = True

            etz_ole = elec.collect_codes_for_energy_tariff_zones(confirmation_required, verbose)
            # To collect section codes for OLE installations: national network energy tariff zones? [No]|Yes:
            # >? yes

            print(etz_ole)
            # {'National network energy tariff zones': <codes>,
            #  'Last updated date': <date>}
        """

        if confirmed("To collect section codes for OLE installations: {}?".format(self.TariffZonesKey.lower()),
                     confirmation_required=confirmation_required):

            if verbose == 2:
                print("Collecting the codes for {}".format(self.TariffZonesKey.lower()), end=" ... ")

            try:
                source = requests.get(self.Catalogue[self.TariffZonesKey], headers=fake_requests_headers())
                soup = bs4.BeautifulSoup(source.text, 'lxml')

                etz_ole_ = {}
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

                    etz_ole_.update({h3.text: table, 'Notes': notes})

                    h3 = h3.find_next_sibling('h3')

                source.close()

                etz_ole = {self.TariffZonesKey: etz_ole_,
                           self.LUDKey: get_last_updated_date(self.Catalogue[self.TariffZonesKey])}

                print("Done. ") if verbose == 2 else ""

                path_to_pickle = self.cdd_elec(self.TariffZonesPickle + ".pickle")
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
        :type verbose: bool, int
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

        path_to_pickle = self.cdd_elec(self.TariffZonesPickle + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            etz_ole = load_pickle(path_to_pickle, verbose=verbose)

        else:
            etz_ole = self.collect_codes_for_energy_tariff_zones(
                confirmation_required=False, verbose=False if data_dir or not verbose else True)

            if etz_ole:  # codes_for_energy_tariff_zones is not None
                if pickle_it and data_dir:
                    self.CurrentDataDir = regulate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, self.TariffZonesPickle + ".pickle")
                    save_pickle(etz_ole, path_to_pickle, verbose=verbose)
            else:
                print("No data of {} has been collected.".format(self.TariffZonesKey.lower()))

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
        :type verbose: bool, int
        :return: section codes for overhead line electrification (OLE) installations
        :rtype: dict

        **Example**::

            from pyrcs.line_data import Electrification

            elec = Electrification()

            update = False
            pickle_it = False
            data_dir = None
            verbose = False

            ole_section_codes = elec.fetch_electrification_codes(update, pickle_it, data_dir, verbose)

            print(ole_section_codes)
            # {'Electrification': <codes>,
            #  'Latest update date': <date>}
        """

        codes = []
        for func in dir(self):
            if func.startswith('fetch_codes_for_'):
                codes.append(getattr(self, func)(update=update, verbose=verbose))

        ole_section_codes = {self.Key: {next(iter(x)): next(iter(x.values())) for x in codes},
                             self.LUDKey: max(next(itertools.islice(iter(x.values()), 1, 2)) for x in codes)}

        if pickle_it and data_dir:
            pickle_filename = self.Name.lower().replace(" ", "-") + ".pickle"
            self.CurrentDataDir = regulate_input_data_dir(data_dir)
            path_to_pickle = os.path.join(self.CurrentDataDir, pickle_filename)
            save_pickle(ole_section_codes, path_to_pickle, verbose=verbose)

        return ole_section_codes
