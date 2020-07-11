""" A class for collecting line data """

import urllib.parse

from pyrcs.line_data import *
from utils import get_category_menu, homepage_url


class LineData:
    def __init__(self):
        # Basic info
        self.Name = 'Line data'
        self.HomeURL = homepage_url()
        self.SourceURL = urllib.parse.urljoin(
            self.HomeURL, '{}menu.shtm'.format(self.Name.lower().replace(' ', '')))
        self.Catalogue = get_category_menu(self.SourceURL)
        # Classes
        self.ELRMileages = elrs_mileages.ELRMileages()
        self.Electrification = electrification.Electrification()
        self.LocationIdentifiers = crs_nlc_tiploc_stanox.LocationIdentifiers()
        self.LOR = lor_codes.LOR()
        self.LineNames = line_names.LineNames()
        self.TrackDiagrams = track_diagrams.TrackDiagrams()
