"""
Collecting `line data <http://www.railwaycodes.org.uk/linedatamenu.shtm>`_.
"""

import urllib.parse

from .line_data import *
from .utils import get_category_menu, homepage_url


class LineData:
    """
    :param update: whether to check on update and proceed to update the package data,
        defaults to ``False``
    :type update: bool

    **Example**::

        >>> from pyrcs import LineData

        >>> ld = LineData()

        >>> # To get location codes
        >>> location_codes_data = ld.LocationIdentifiers.fetch_location_codes()

        >>> type(location_codes_data)
        <class 'dict'>
        >>> print(list(location_codes_data.keys()))
        ['Location codes', 'Other systems', 'Additional notes', 'Last updated date']
        >>> location_codes_dat = location_codes_data['Location codes']
        >>> print(location_codes_dat.head())
                                       Location CRS  ... STANME_Note STANOX_Note
        0                                Aachen      ...
        1                    Abbeyhill Junction      ...
        2                 Abbeyhill Signal E811      ...
        3            Abbeyhill Turnback Sidings      ...
        4  Abbey Level Crossing (Staffordshire)      ...

        [5 rows x 12 columns]

        >>> # To get location codes
        >>> line_names_data = ld.LineNames.fetch_line_names()

        >>> type(line_names_data)
        <class 'dict'>
        >>> print(list(line_names_data.keys()))
        ['Line names', 'Last updated date']
        >>> line_names_dat = line_names_data['Line names']
        >>> print(line_names_dat.head())
                     Line name  ... Route_note
        0           Abbey Line  ...       None
        1        Airedale Line  ...       None
        2          Argyle Line  ...       None
        3     Arun Valley Line  ...       None
        4  Atlantic Coast Line  ...       None

        [5 rows x 3 columns]
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
        self.Catalogue = \
            get_category_menu(self.SourceURL, update=update, confirmation_required=False)
        # Classes
        self.ELRMileages = elrs_mileages.ELRMileages(update=update)
        self.Electrification = electrification.Electrification(update=update)
        self.LocationIdentifiers = \
            crs_nlc_tiploc_stanox.LocationIdentifiers(update=update)
        self.LOR = lor_codes.LOR(update=update)
        self.LineNames = line_names.LineNames(update=update)
        self.TrackDiagrams = track_diagrams.TrackDiagrams(update=update)
