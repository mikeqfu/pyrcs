"""

Data source: http://www.railwaycodes.org.uk

Section codes for overhead line electrification (OLE) installations
(Reference: http://www.railwaycodes.org.uk/electrification/mast_prefix0.shtm)

"""

import os

from pyrcscraper import line_data
from pyrcscraper.utils import get_cls_catalogue, get_last_updated_date


class Electrification:
    def __init__(self):
        self.Name = 'Electrification masts and related features'
        self.URL = 'http://www.railwaycodes.org.uk/electrification/mast_prefix0.shtm'
        self.Catalogue = get_cls_catalogue(self.URL)
        self.Date = get_last_updated_date(self.URL, parsed=True, date_type=False)

    # Change directory to "...dat\\Line data\\Electrification" and sub-directories
    @staticmethod
    def cdd_elec(*sub_dir):
        path = line_data.cd_dat("Line data", "Electrification")
        for x in sub_dir:
            path = os.path.join(path, x)
        return path
