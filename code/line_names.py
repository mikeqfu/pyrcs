""" Railway line names """

import os
import re

import pandas as pd
import requests

from utils import cdd, get_last_updated_date, load_pickle, parse_table, save_pickle

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
    line_names_data = pd.DataFrame([[r.replace('\xa0', '').strip() for r in row] for row in row_lst], columns=header)

    line_names_data[['Route', 'Route_note']] = line_names_data.Route.map(parse_route).apply(pd.Series)

    line_names = {'Line_names': line_names_data, 'Last_updated_date': last_updated_date}

    return line_names


# Get data of line names
def get_line_names(update=False):
    pickle_filename = "Line-names.pickle"
    path_to_pickle = cdd_line_names(pickle_filename)
    if os.path.isfile(path_to_pickle) and not update:
        line_names = load_pickle(path_to_pickle)
    else:
        try:
            line_names = scrape_line_names()
            save_pickle(line_names, path_to_pickle)
        except Exception as e:
            print("Failed to get line names due to \"{}\"".format(e))
            line_names = None
    return line_names
