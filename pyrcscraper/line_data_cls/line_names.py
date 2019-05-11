"""

Data source: http://www.railwaycodes.org.uk

Railway line names (Reference: http://www.railwaycodes.org.uk/misc/line_names.shtm)

"""

import os
import re

import pandas as pd
import requests

from pyrcscraper import line_data
from pyrcscraper.utils import get_last_updated_date, load_pickle, parse_table, save_pickle


class LineNames:
    def __init__(self):
        self.Name = 'Railway line names'
        self.URL = 'http://www.railwaycodes.org.uk/misc/line_names.shtm'
        self.Catalogue = 'A single table.'  # get_cls_contents(self.URL, navigation_bar_exists=False, menu_exists=False)
        self.Date = get_last_updated_date(self.URL, parsed=True, date_type=False)

    # Change directory to "dat\\Line data\\Line names" and sub-directories
    @staticmethod
    def cdd_line_names(*sub_dir):
        path = line_data.cd_dat("Line data", "Line names")
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    # Scrape the data of railway line names
    def scrape_line_names(self):
        """
        :return [tuple] {'Line_names': [DataFrame] railway line names and routes data,
                         'Last_updated_date': [str] date of when the data was last updated}
        """

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

        last_updated_date = get_last_updated_date(self.URL)

        source = requests.get(self.URL)
        row_lst, header = parse_table(source, parser='lxml')
        line_names_data = pd.DataFrame([[r.replace('\xa0', '').strip() for r in row] for row in row_lst],
                                       columns=header)

        line_names_data[['Route', 'Route_note']] = \
            line_names_data.Route.map(parse_route_column).apply(pd.Series)

        line_names = {'Line_names': line_names_data, 'Last_updated_date': last_updated_date}

        return line_names

    # Get the data of line names either locally or from online
    def get_line_names(self, update=False):
        path_to_pickle = self.cdd_line_names("Line-names.pickle")
        if os.path.isfile(path_to_pickle) and not update:
            line_names = load_pickle(path_to_pickle)
        else:
            try:
                line_names = self.scrape_line_names()
                save_pickle(line_names, path_to_pickle)
            except Exception as e:
                print("Failed to get line names due to \"{}\"".format(e))
                line_names = None
        return line_names
