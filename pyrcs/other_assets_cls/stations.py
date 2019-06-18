"""

Data source: http://www.railwaycodes.org.uk

ELRs, mileages, operators, grid references
Bilingual station names
Sponsored stations
Stations not served by their Station Facility Operator (SFO)
International stations
Station trivia

Railway station data (Reference: http://www.railwaycodes.org.uk/stations/station0.shtm)

"""

import itertools
import os
import re
import string

import pandas as pd
import requests
from pyhelpers.store import load_pickle, save_pickle

from pyrcs.utils import cd_dat
from pyrcs.utils import get_last_updated_date, regulate_input_data_dir
from pyrcs.utils import parse_location_note, parse_table


class Stations:
    def __init__(self, data_dir=None):
        self.HomeURL = 'http://www.railwaycodes.org.uk'
        self.Name = 'Railway station data'
        self.URL = 'http://www.railwaycodes.org.uk/stations/station0.shtm'
        self.Date = get_last_updated_date(self.URL, parsed=True, date_type=False)
        self.DataDir = regulate_input_data_dir(data_dir) if data_dir else cd_dat("Other assets", "Stations")

    # Change directory to "dat\\Other assets\\Stations" and sub-directories
    def cd_stn(self, *sub_dir):
        path = self.DataDir
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    # Change directory to "dat\\Other assets\\Stations\\dat"
    def cdd_stn(self, *sub_dir):
        path = self.cd_stn("dat")
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    #
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

    # Railway station data by keywords
    def collect_station_locations(self, keyword, update=False):
        """
        :param keyword: [str] station data (including the station name, ELR, mileage, status, owner, operator,
                            degrees of longitude and latitude, and grid reference) for stations whose name start with
        :param update: [bool]
        :return [dict] {keyword: [DataFrame] railway station data,
                        'Last_updated_date': [str] date of when the data was last updated}
        """
        path_to_file = self.cd_stn("A-Z", keyword.title() + ".pickle")
        if os.path.isfile(path_to_file) and not update:
            station_locations = load_pickle(path_to_file)
        else:
            url = 'http://www.railwaycodes.org.uk/stations/station{}.shtm'.format(keyword.lower())
            last_updated_date = get_last_updated_date(url)
            try:
                source = requests.get(url)  # Request to get connected to the url
                records, header = parse_table(source, parser='lxml')
                # Create a DataFrame of the requested table
                dat = [[x.replace('=', 'See').strip('\xa0') for x in i] for i in records]
                col = [h.replace('\r\n', ' ').replace('\r', ' ') for h in header]
                station_locations_data = pd.DataFrame(dat, columns=col)

                station_locations_data[['Degrees Longitude', 'Degrees Latitude']] = \
                    station_locations_data[['Degrees Longitude', 'Degrees Latitude']].applymap(
                        lambda x: pd.np.nan if x == '' else float(x))

                station_locations_data[['Station', 'Station_Note']] = \
                    station_locations_data.Station.map(parse_location_note).apply(pd.Series)

                # Operator
                temp = list(station_locations_data.Operator.map(self.parse_current_operator))
                length = len(max(temp, key=len))
                col_names_current = ['Operator', 'Date']
                prev_no = list(itertools.chain.from_iterable(itertools.repeat(x, 2) for x in list(range(1, length))))
                col_names = zip(col_names_current * (length - 1), prev_no)
                col_names = col_names_current + ['_'.join(['Prev', x, str(d)]) for x, d in col_names]

                for i in range(len(temp)):
                    if len(temp[i]) < length:
                        temp[i] += [(None, None)] * (length - len(temp[i]))

                temp = pd.DataFrame(temp)
                operators = [pd.DataFrame(temp)[col].apply(pd.Series) for col in temp.columns]
                operators = pd.concat(operators, axis=1)
                operators.columns = col_names

                station_locations_data.drop('Operator', axis=1, inplace=True)
                station_locations_data = station_locations_data.join(operators)

                station_locations = {'Station_{}'.format(keyword.upper()): station_locations_data,
                                     'Last_updated_date': last_updated_date}

                save_pickle(station_locations, path_to_file)

            except Exception as e:
                if keyword not in ['x', 'X', 'z', 'Z']:
                    print("Failed to scrape station locations for the keyword \"{}\" due to '{}'".format(keyword, e))
                station_locations = {'Station_{}'.format(keyword.upper()): pd.DataFrame(),
                                     'Last_updated_date': last_updated_date}

        return station_locations

    # Get all railway station data
    def fetch_station_locations(self, update=False, pickle_it=False, data_dir=None):
        """
        :param update: [bool]
        :param pickle_it: [bool]
        :param data_dir: [str; None]
        :return [dict] {keyword: [DataFrame] station data, including the station name, ELR, mileage, status, owner,
                                    operator, degrees of longitude and latitude, and grid reference,
                        'Last_updated_date': [str] date of when the data was last updated}
        """

        stn_locs, last_updated_dates = [], []
        for k in string.ascii_lowercase:
            stn_loc, updated_date = self.collect_station_locations(k, update).values()
            if stn_loc is not None:
                stn_locs.append(stn_loc)
            if updated_date is not None:
                last_updated_dates.append(updated_date)

        stn_dat = pd.concat(stn_locs, ignore_index=True, sort=False)
        station_locations = {'Station': stn_dat, 'Last_updated_date': max(last_updated_dates)}

        if pickle_it:
            dat_dir = regulate_input_data_dir(data_dir) if data_dir else self.DataDir
            path_to_pickle = os.path.join(dat_dir, "ELRs-mileages-operators-grid.pickle")
            save_pickle(station_locations, path_to_pickle)

        return station_locations
