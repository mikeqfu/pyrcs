""" A class for collecting line data """

from pyrcs.line_data import *
from utils import get_category_menu, homepage_url


class LineData:
    def __init__(self):
        # Basic info
        self.Name = 'Line data'
        self.SourceURL = homepage_url()
        self.URL = self.SourceURL + '/linedatamenu.shtm'
        self.Catalogue = get_category_menu(self.URL)
        # Classes
        self.ELRMileages = elrs_mileages.ELRMileages()
        self.Electrification = electrification.Electrification()
        self.LocationIdentifiers = crs_nlc_tiploc_stanox.LocationIdentifiers()
        self.LOR = lor_codes.LOR()
        self.LineNames = line_names.LineNames()
        self.TrackDiagrams = track_diagrams.TrackDiagrams()
