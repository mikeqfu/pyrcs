""" Collecting line data """

import urllib.parse

from .line_data import *
from .utils import get_category_menu, homepage_url


class LineData:
    """
    :param update: whether to check on update and proceed to update the package data, defaults to ``False``
    :type update: bool

    **Example**::

        from pyrcs import LineData

        ld = LineData()

        # To get location codes
        lid = ld.LocationIdentifiers

        # location codes that start with 'A'
        location_codes_a = lid.collect_location_codes_by_initial('A')
    """

    def __init__(self, update=False):
        """
        Constructor method.
        """
        # Basic info
        self.Name = 'Line data'
        self.HomeURL = homepage_url()
        self.SourceURL = urllib.parse.urljoin(
            self.HomeURL, '{}menu.shtm'.format(self.Name.lower().replace(' ', '')))
        self.Catalogue = get_category_menu(self.SourceURL, update=update, confirmation_required=False)
        # Classes
        self.ELRMileages = elrs_mileages.ELRMileages(update=update)
        self.Electrification = electrification.Electrification(update=update)
        self.LocationIdentifiers = crs_nlc_tiploc_stanox.LocationIdentifiers(update=update)
        self.LOR = lor_codes.LOR(update=update)
        self.LineNames = line_names.LineNames(update=update)
        self.TrackDiagrams = track_diagrams.TrackDiagrams(update=update)
