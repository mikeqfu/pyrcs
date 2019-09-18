"""

Data source: http://www.railwaycodes.org.uk

ELRs, mileages, operators, grid references
Bilingual station names
Sponsored stations
Stations not served by their Station Facility Operator (SFO)
International stations
Station trivia

Railway station data (http://www.railwaycodes.org.uk/stations/station0.shtm)

"""

import copy
import itertools
import os
import re
import string
import urllib.parse

import bs4
import pandas as pd
import requests
from pyhelpers.dir import regulate_input_data_dir
from pyhelpers.store import load_pickle

from pyrcs.utils import cd_dat, get_catalogue, get_last_updated_date, parse_location_note, parse_table
from pyrcs.utils import save_pickle


class Stations:
    def __init__(self, data_dir=None):
        self.HomeURL = 'http://www.railwaycodes.org.uk'
        self.Name = 'Railway station data'
        self.URL = self.HomeURL + '/stations/station0.shtm'
        self.Catalogue = get_catalogue(self.URL)

        source = requests.get(self.URL)
        soup = bs4.BeautifulSoup(source.text, 'lxml').find_all('a', href=True)
        self.SubCatalogue = dict((x.text, urllib.parse.urljoin(os.path.dirname(self.URL) + '/', x['href']))
                                 for x in [x for x in soup if x.text in string.ascii_uppercase][2:])

        self.Date = get_last_updated_date(self.URL, parsed=True, date_type=False)
        self.DataDir = regulate_input_data_dir(data_dir) if data_dir else cd_dat("other-assets", "stations")
        self.CurrentDataDir = copy.copy(self.DataDir)

    # Change directory to "dat\\other-assets\\stations" and sub-directories
    def cd_stn(self, *sub_dir):
        path = self.DataDir
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    # Change directory to "dat\\other-assets\\stations\\dat"
    def cdd_stn(self, *sub_dir):
        path = self.cd_stn("dat")
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    # Parse 'Operator' column
    @staticmethod
    def parse_current_operator(x):
        contents = re.split(r'\\r| \[\'|\\\\r| {2}\'\]|\', \'|\\n',
                            x.lstrip(' [\'').rstrip('  \']').lstrip('\n').strip())
        contents = [x for x in contents if x != '']
        operators = []
        for y in contents:
            # Operators names
            operator_name = re.search(r'.*(?= \(from \d+ \w+ \d+(.*)?\))', y)
            operator_name = operator_name.group() if operator_name is not None else ''
            # Start dates
            start_date = re.search(r'(?<= \(from )\d+ \w+ \d+( to \d+ \w+ \d+(.*))?(?=\))', y)
            start_date = start_date.group() if start_date is not None else ''
            # Form a tuple
            operators.append((operator_name, start_date))
        return operators

    # Collect railway station data for a given 'keyword'
    def collect_station_locations(self, initial, update=False, verbose=False):
        """
        :param initial: [str] station data (including the station name, ELR, mileage, status, owner, operator,
                            degrees of longitude and latitude, and grid reference) for stations whose name start with
        :param update: [bool]
        :param verbose: [bool]
        :return [dict] {keyword: [DataFrame] railway station data,
                        'Last_updated_date': [str] date of when the data was last updated}
        """
        path_to_pickle = self.cd_stn("a-z", initial.lower() + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            station_location_codes = load_pickle(path_to_pickle)

        else:
            url = self.URL.replace('station0', 'station{}'.format(initial.lower()))

            if initial.upper() not in list(self.SubCatalogue.keys()):
                print("No data is available for signal box codes beginning with \"{}\".".format(initial.upper()))
                station_location_codes = {initial.upper(): pd.DataFrame(), 'Last_updated_date': ''}

            else:
                try:
                    source = requests.get(url)  # Request to get connected to the url
                    records, header = parse_table(source, parser='lxml')
                    # Create a DataFrame of the requested table
                    dat = [[x.replace('=', 'See').strip('\xa0') for x in i] for i in records]
                    col = [h.replace('\r\n', ' ').replace('\r', ' ') for h in header]
                    station_locations_table = pd.DataFrame(dat, columns=col)

                    station_locations_table[['Degrees Longitude', 'Degrees Latitude']] = \
                        station_locations_table[['Degrees Longitude', 'Degrees Latitude']].applymap(
                            lambda x: pd.np.nan if x == '' else float(x))

                    station_locations_table[['Station', 'Station_Note']] = \
                        station_locations_table.Station.map(parse_location_note).apply(pd.Series)

                    # Operator
                    temp = list(station_locations_table.Operator.map(self.parse_current_operator))
                    length = len(max(temp, key=len))
                    col_names_current = ['Operator', 'Date']
                    prev_no = list(
                        itertools.chain.from_iterable(itertools.repeat(x, 2) for x in list(range(1, length))))
                    col_names = zip(col_names_current * (length - 1), prev_no)
                    col_names = col_names_current + ['_'.join(['Prev', x, str(d)]) for x, d in col_names]

                    for i in range(len(temp)):
                        if len(temp[i]) < length:
                            temp[i] += [(None, None)] * (length - len(temp[i]))

                    temp = pd.DataFrame(temp)
                    operators = [pd.DataFrame(temp)[col].apply(pd.Series) for col in temp.columns]
                    operators = pd.concat(operators, axis=1, sort=False)
                    operators.columns = col_names

                    station_locations_table.drop('Operator', axis=1, inplace=True)
                    station_locations_table = station_locations_table.join(operators)

                except Exception as e:
                    print("Failed to collect station location codes beginning with \"{}\". {}".format(
                        initial.upper(), e))
                    station_locations_table = pd.DataFrame()

                try:
                    last_updated_date = get_last_updated_date(url)
                except Exception as e:
                    print("Failed to find the last updated date of the station location codes beginning with "
                          "\"{}\" {}".format(initial.upper(), e))
                    last_updated_date = ''

                station_location_codes = {initial.upper(): station_locations_table,
                                          'Last_updated_date': last_updated_date}

            save_pickle(station_location_codes, path_to_pickle, verbose)

        return station_location_codes

    # Fetch all of the collected railway station data
    def fetch_station_locations(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        :param update: [bool]
        :param pickle_it: [bool]
        :param data_dir: [str; None]
        :param verbose: [bool]
        :return [dict] {initial: [DataFrame] station data, including the station name, ELR, mileage, status, owner,
                                    operator, degrees of longitude and latitude, and grid reference,
                        'Latest_update_date': [str] date of when the data was last updated}
        """
        data_sets = [self.collect_station_locations(x, update, verbose=False if data_dir or not verbose else True)
                     for x in string.ascii_lowercase]

        station_location_codes_tables = (item[x] for item, x in zip(data_sets, string.ascii_uppercase))
        station_location_codes = pd.concat(station_location_codes_tables, axis=0, ignore_index=True, sort=False)

        last_updated_dates = (d['Last_updated_date'] for d in data_sets)
        latest_update_date = max(d for d in last_updated_dates if d != '')

        station_locations_data = {'Stations': station_location_codes, 'Latest_update_date': latest_update_date}

        if pickle_it and data_dir:
            self.CurrentDataDir = regulate_input_data_dir(data_dir)
            path_to_pickle = os.path.join(self.CurrentDataDir, "station_locations.pickle")
            save_pickle(station_locations_data, path_to_pickle, verbose=True)

        return station_locations_data
