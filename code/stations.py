""" Railway station data """

import os
import re
import string

import pandas as pd
import requests

from utils import cdd, load_pickle, save_pickle
from utils import get_last_updated_date, parse_table, parse_location_name


# ====================================================================================================================
""" Change directory """


# Change directory to "...dat\\Other assets\\Stations\\ELRs, mileages, operators, grid references" and sub-directories
def cdd_stnloc(*directories):
    path = cdd("Other assets", "Stations", "ELRs, mileages, operators, grid references")
    for directory in directories:
        path = os.path.join(path, directory)
    return path


# ====================================================================================================================
""" ELRs, mileages, operators, grid references """


# Railway station data by keywords
def scrape_station_locations(keyword, update=False):
    """
    :param keyword: [str] station data (including the station name, ELR, mileage, status, owner, operator, degrees of
                        longitude and latitude, and grid reference) for stations whose name start with
    :param update: [bool]
    :return [dict] {keyword: [DataFrame] railway station data,
                    'Last_updated_date': [str] date of when the data was last updated}
    """
    path_to_file = cdd_stnloc("A-Z", keyword.title() + ".pickle")
    if os.path.isfile(path_to_file) and not update:
        station_locations = load_pickle(path_to_file)
    else:
        url = 'http://www.railwaycodes.org.uk/stations/station{}.shtm'.format(keyword.lower())
        last_updated_date = get_last_updated_date(url)
        try:
            source = requests.get(url)  # Request to get connected to the url
            records, header = parse_table(source, parser='lxml')
            # Create a DataFrame of the requested table
            station_locations_data = pd.DataFrame([[x.replace('=', 'See').strip('\xa0') for x in i] for i in records],
                                                  columns=[h.replace('\r\n', ' ') for h in header])

            station_locations_data[['Station', 'Station_Note']] = \
                station_locations_data.Station.map(parse_location_name).apply(pd.Series)

            # Operator
            def get_current_operator(x):
                contents = re.split(' \[\'\', \'| \[\'\r\', \'|\', \'|\r\', \'|\n+', x.rstrip('\']'))
                current_operator, previous_operators = contents[0], contents[1:]
                current_operator_name = re.search('.*(?= \(from \d+ \w+ \d+.*?\))', current_operator)
                operator_name = current_operator_name.group() if current_operator_name is not None else ''
                current_operator_start_date = re.search('(?<= \(from )\d+ \w+ \d+.?(?=\))', current_operator)
                start_date = current_operator_start_date.group() if current_operator_start_date is not None else ''
                return operator_name, start_date, previous_operators

            station_locations_data[['Operator', 'Operator_StartDate', 'Previous_Operators']] = \
                station_locations_data.Operator.map(get_current_operator).apply(pd.Series)

        except Exception as e:
            source = requests.get(url)
            if not source.ok:
                print("Data for the keyword '{}' is not available".format(keyword))
            else:
                print("Scraping station locations for the keyword '{}' ... failed due to '{}'".format(keyword, e))
            station_locations_data = None

        if station_locations_data is not None and last_updated_date is not None:
            station_locations = {'Station_{}'.format(keyword): station_locations_data,
                                 'Last_updated_date': last_updated_date}
            save_pickle(station_locations, path_to_file)
        else:
            station_locations = None

    return station_locations


# Get all railway station data
def get_station_locations(update=False):
    """
    :param update: [bool]
    :return [dict] {keyword: [DataFrame] station data, including the station name, ELR, mileage, status, owner,
                                operator, degrees of longitude and latitude, and grid reference,
                    'Last_updated_date': [str] date of when the data was last updated}
    """
    path_to_file = cdd_stnloc("ELRs-mileages-operators-grid.pickle")
    if os.path.isfile(path_to_file) and not update:
        station_locations = load_pickle(path_to_file)
    else:
        try:
            stn_locs, last_updated_dates = [], []
            for k in string.ascii_lowercase:
                data = scrape_station_locations(k, update)
                if data is not None:
                    stn_loc, updated_date = scrape_station_locations(k, update).values()
                    if stn_loc is not None:
                        stn_locs.append(stn_loc)
                    if updated_date is not None:
                        last_updated_dates.append(updated_date)

            station_locations = {'Station': pd.concat(stn_locs, ignore_index=True),
                                 'Last_updated_date': max(last_updated_dates)}

            save_pickle(station_locations, path_to_file)

        except Exception as e:
            print("Getting station locations ... failed due to '{}'".format(e))
            station_locations = None

    return station_locations


# ====================================================================================================================
""" Bilingual station names """
