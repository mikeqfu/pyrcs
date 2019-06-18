""" Line data """

from pyrcs.line_data_cls import crs_nlc_tiploc_stanox, elrs_mileages, line_names, lor_codes
from pyrcs.line_data_cls import electrification, track_diagrams
from pyrcs.utils import get_cls_catalogue, get_last_updated_date


class LineData:
    def __init__(self):
        # Basic info
        self.HomeURL = 'http://www.railwaycodes.org.uk'
        self.Name = 'Line data'
        self.URL = 'http://www.railwaycodes.org.uk/linedatamenu.shtm'
        self.Catalogue = get_cls_catalogue(self.URL, navigation_bar_exists=False)
        self.Date = get_last_updated_date(self.URL, parsed=True, date_type=False)
        # Classes
        self.ELRMileages = elrs_mileages.ELRMileages()
        self.LocationIdentifiers = crs_nlc_tiploc_stanox.LocationIdentifiers()
        self.LOR = lor_codes.LOR()
        self.LineNames = line_names.LineNames()
        self.Electrification = electrification.Electrification()
        self.TrackDiagrams = track_diagrams.TrackDiagrams()
