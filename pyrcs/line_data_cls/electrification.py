"""

Data source: http://www.railwaycodes.org.uk

Section codes for overhead line electrification (OLE) installations
(Reference: http://www.railwaycodes.org.uk/electrification/mast_prefix0.shtm)

"""

import os

from pyhelpers.dir import regulate_input_data_dir

from pyrcs.utils import cd_dat, get_cls_catalogue, get_last_updated_date


class Electrification:
    def __init__(self, data_dir=None):
        self.HomeURL = 'http://www.railwaycodes.org.uk'
        self.Name = 'Electrification'
        self.URL = self.HomeURL + '/electrification/mast_prefix0.shtm'
        self.Catalogue = get_cls_catalogue(self.URL)
        self.Date = get_last_updated_date(self.URL, parsed=True, date_type=False)
        self.DataDir = regulate_input_data_dir(data_dir) if data_dir else cd_dat("Line data", self.Name)

    # Change directory to "dat\\Line data\\Electrification" and sub-directories
    def cd_elec(self, *sub_dir):
        path = self.DataDir
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

    # Change directory to "dat\\Line data\\Electrification\\dat" and sub-directories
    def cdd_elec(self, *sub_dir):
        path = self.cd_elec("dat")
        for x in sub_dir:
            path = os.path.join(path, x)
        return path

# To be updated.
