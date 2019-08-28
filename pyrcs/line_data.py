""" Line data """

from pyrcs.line_data_cls import crs_nlc_tiploc_stanox, electrification, elrs_mileages, lor_codes
from pyrcs.line_data_cls import line_names, track_diagrams
from pyrcs.utils import get_cls_menu


class LineData:
    def __init__(self):
        # Basic info
        self.HomeURL = 'http://www.railwaycodes.org.uk'
        self.Name = 'Line data'
        self.URL = self.HomeURL + '/linedatamenu.shtm'
        self.Catalogue = get_cls_menu(self.URL)
        # Classes
        self.ELRMileages = elrs_mileages.ELRMileages()
        self.Electrification = electrification.Electrification()
        self.LocationIdentifiers = crs_nlc_tiploc_stanox.LocationIdentifiers()
        self.LOR = lor_codes.LOR()
        self.LineNames = line_names.LineNames()
        self.TrackDiagrams = track_diagrams.TrackDiagrams()
