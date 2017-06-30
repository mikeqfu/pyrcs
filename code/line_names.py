""" Railway line names """

import os
import re

import pandas as pd
import requests

from utils import cdd, load_pickle, save_pickle, get_last_updated_date, parse_table


# ====================================================================================================================
""" Change directory """


# Change directory to "...dat\\Line data\\Line names" and sub-directories
def cdd_line_names(*directories):
    path = cdd("Line data", "Line names")
    for directory in directories:
        path = os.path.join(path, directory)
    return path


# ====================================================================================================================
""" Scrape/get data """


# Railway line names
def scrape_line_names():
    """
    :return [tuple] {'Line_names': [DataFrame] railway line names and routes data,
                     'Last_updated_date': [str] date of when the data was last updated}
    """
    url = 'http://www.railwaycodes.org.uk/misc/line_names.shtm'

    last_updated_date = get_last_updated_date(url)

    source = requests.get(url)
    row_lst, header = parse_table(source, parser='lxml')
    line_names_data = pd.DataFrame([[r.replace('\xa0', '').strip() for r in row] for row in row_lst],
                                   columns=header)

    def parse_route(x):
        if 'Watford - Euston suburban route' in x:
            route, route_note = 'Watford - Euston suburban route', x
        elif ', including Moorgate - Farringdon' in x:
            route_note = 'including Moorgate - Farringdon'
            route = x.replace(', including Moorgate - Farringdon', '')
        elif re.match('.+(?= \[\')', x):
            route, route_note = re.split(' \[\'\(?', x)
            route_note = route_note.strip(')\'\]')
        elif re.match('.+\)$', x):
            if re.match('.+(?= - \()', x):
                route, route_note = x, None
            else:
                route, route_note = re.split(' \(\[?\'?', x)
                route_note = route_note.rstrip('\'])')
        else:
            route, route_note = x, None
        return route, route_note

    line_names_data[['Route', 'Route_note']] = line_names_data.Route.map(parse_route).apply(pd.Series)

    line_names = {'Line_names': line_names_data, 'Last_updated_date': last_updated_date}

    return line_names


# Get data of line names
def get_line_names(update=False):
    path_to_file = cdd_line_names("Line-names.pickle")
    if os.path.isfile(path_to_file) and not update:
        line_names = load_pickle(path_to_file)
    else:
        try:
            line_names = scrape_line_names()
            save_pickle(line_names, path_to_file)
        except Exception as e:
            print("Getting line names ... failed due to '{}'".format(e))
            line_names = None
    return line_names
