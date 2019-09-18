"""

Data source: http://www.railwaycodes.org.uk

Railway line names (http://www.railwaycodes.org.uk/misc/line_names.shtm)

"""

import copy
import os
import re

import pandas as pd
import requests
from pyhelpers.dir import regulate_input_data_dir
from pyhelpers.misc import confirmed
from pyhelpers.store import load_pickle

from pyrcs.utils import cd_dat, get_last_updated_date, parse_table, save_pickle


class LineNames:
    def __init__(self, data_dir=None):
        self.HomeURL = 'http://www.railwaycodes.org.uk'
        self.Name = 'Railway line names'
        self.URL = self.HomeURL + '/misc/line_names.shtm'
        self.Date = get_last_updated_date(self.URL, parsed=True, date_type=False)
        self.DataDir = regulate_input_data_dir(data_dir) if data_dir else cd_dat("line-data", "line-names")
        self.CurrentDataDir = copy.copy(self.DataDir)

    # Change directory to "dat\\line-data\\line-names" and sub-directories
    def cd_ln(self, *sub_dir):
        path = self.DataDir
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    # Change directory to "dat\\line-data\\line-names\\dat" and sub-directories
    def cdd_ln(self, *sub_dir):
        path = self.cd_ln("dat")
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    # Scrape the data of railway line names
    def collect_line_names(self, confirmation_required=True, verbose=False):
        """
        :return [tuple] {'Line_names': [DataFrame] railway line names and routes data,
                         'Last_updated_date': [str] date of when the data was last updated}
        """
        if confirmed("To collect line names?", confirmation_required=confirmation_required):

            try:
                last_updated_date = get_last_updated_date(self.URL)
            except Exception as e:
                print("Failed to find the last update date for line names. {}".format(e))
                last_updated_date = ''

            try:
                source = requests.get(self.URL)
                row_lst, header = parse_table(source, parser='lxml')
                line_names = pd.DataFrame([[r.replace('\xa0', '').strip() for r in row] for row in row_lst],
                                          columns=header)

                # Parse route column
                def parse_route_column(x):
                    if 'Watford - Euston suburban route' in x:
                        route, route_note = 'Watford - Euston suburban route', x
                    elif ', including Moorgate - Farringdon' in x:
                        route_note = 'including Moorgate - Farringdon'
                        route = x.replace(', including Moorgate - Farringdon', '')
                    elif re.match(r'.+(?= \[\')', x):
                        route, route_note = re.split(r' \[\'\(?', x)
                        route_note = route_note.strip(")']")
                    elif re.match(r'.+\)$', x):
                        if re.match(r'.+(?= - \()', x):
                            route, route_note = x, None
                        else:
                            route, route_note = re.split(r' \(\[?\'?', x)
                            route_note = route_note.rstrip('\'])')
                    else:
                        route, route_note = x, None
                    return route, route_note

                line_names[['Route', 'Route_note']] = line_names.Route.map(parse_route_column).apply(pd.Series)

                line_names_data = {'Line_names': line_names, 'Last_updated_date': last_updated_date}

                save_pickle(line_names_data, self.cd_ln("line-names.pickle"), verbose)

            except Exception as e:
                print("Failed to collect line names. {}".format(e))
                line_names_data = None

            return line_names_data

    # Get the data of line names either locally or from online
    def fetch_line_names(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        pickle_filename = "line-names.pickle"
        path_to_pickle = self.cd_ln(pickle_filename)

        if os.path.isfile(path_to_pickle) and not update:
            line_names_data = load_pickle(path_to_pickle)

        else:
            line_names_data = self.collect_line_names(confirmation_required=False,
                                                      verbose=False if data_dir or not verbose else True)
            if line_names_data:  # line-names is not None
                if pickle_it and data_dir:
                    self.CurrentDataDir = regulate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, pickle_filename)
                    save_pickle(line_names_data, path_to_pickle, verbose=True)
            else:
                print("No data of the railway line names has been collected.")

        return line_names_data
