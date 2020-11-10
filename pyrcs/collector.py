"""
Collect data of railway codes.

The current release includes only:

    - `line data <http://www.railwaycodes.org.uk/linedatamenu.shtm>`_
    - `other assets <http://www.railwaycodes.org.uk/otherassetsmenu.shtm>`_
"""

import time
import urllib.parse

from pyhelpers.ops import confirmed

from .line_data import *
from .other_assets import *
from .utils import get_category_menu, homepage_url


class LineData:
    """
    A class representation of all modules of the subpackage
    :ref:`pyrcs.line_data<line_data>` for collecting line data.

    :param update: whether to check on update and proceed to update the package data,
        defaults to ``False``
    :type update: bool

    **Examples**::

        >>> from pyrcs import LineData

        >>> ld = LineData()

        >>> # To get data of location codes
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

        >>> # To get data of line names
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
        self.ELRMileages = elr_mileage.ELRMileages(update=update)
        self.Electrification = elec.Electrification(update=update)
        self.LocationIdentifiers = loc_id.LocationIdentifiers(update=update)
        self.LOR = lor_code.LOR(update=update)
        self.LineNames = line_name.LineNames(update=update)
        self.TrackDiagrams = trk_diagr.TrackDiagrams()

    def update(self, verbose=False, time_gap=2, init_update=False):
        """
        Update local backup of the line data.

        :param verbose: whether to print relevant information in console
            as the function runs, defaults to ``False``
        :type verbose: bool
        :param time_gap: time gap (in seconds) between the updating of different classes
        :type time_gap: int
        :param init_update: whether to update the data for instantiation of each subclass,
            defaults to ``False``
        :type init_update: bool

        **Example**::

            >>> from pyrcs import LineData

            >>> ld = LineData()
            >>> ld.update(verbose=True)
        """

        if confirmed("To update line data?"):

            if init_update:
                self.__init__(update=init_update)

            # ELR and mileages
            print(f"{self.ELRMileages.Name}:")
            _ = self.ELRMileages.fetch_elr(update=True, verbose=verbose)

            time.sleep(time_gap)

            # Electrification
            print(f"\n{self.Electrification.Name}:")
            _ = self.Electrification.fetch_elec_codes(update=True, verbose=verbose)

            time.sleep(time_gap)

            # Location
            print(f"\n{self.LocationIdentifiers.Name}:")
            _ = self.LocationIdentifiers.fetch_location_codes(update=True,
                                                              verbose=verbose)

            time.sleep(time_gap)

            # Line of routes
            print(f"\n{self.LOR.Name}:")
            _ = self.LOR.update_catalogue(confirmation_required=False, verbose=verbose)
            _ = self.LOR.fetch_lor_codes(update=True, verbose=verbose)
            _ = self.LOR.fetch_elr_lor_converter(update=True, verbose=verbose)

            time.sleep(time_gap)

            # Line names
            print(f"\n{self.LineNames.Name}:")
            _ = self.LineNames.fetch_line_names(update=True, verbose=verbose)

            time.sleep(time_gap)

            # Track diagrams
            print(f"\n{self.TrackDiagrams.Name}:")
            _ = self.TrackDiagrams.get_track_diagrams_items(update=True, verbose=verbose)
            _ = self.TrackDiagrams.fetch_sample_catalogue(update=True, verbose=verbose)


class OtherAssets:
    """
    A class representation of all modules of the subpackage
    :ref:`pyrcs.other_assets<other_assets>` for collecting other assets.

    :param update: whether to check on update and proceed to update the package data,
        defaults to ``False``
    :type update: bool

    **Examples**::

        >>> from pyrcs import OtherAssets

        >>> oa = OtherAssets()

        >>> # To get data of railway stations
        >>> railway_station_data = oa.Stations.fetch_station_data()

        >>> type(railway_station_data)
        <class 'dict'>
        >>> print(list(railway_station_data.keys()))
        ['Railway station data', 'Last updated date']
        >>> railway_station_dat = railway_station_data['Railway station data']
        >>> print(railway_station_dat.head())
              Station   ELR   Mileage  ... Prev_Date_6 Prev_Operator_7  Prev_Date_7
        0  Abbey Wood   NKL  11m 43ch  ...         NaN             NaN          NaN
        1  Abbey Wood  XRS3  24.458km  ...         NaN             NaN          NaN
        2        Aber   CAR   8m 69ch  ...         NaN             NaN          NaN
        3   Abercynon   CAM  16m 28ch  ...         NaN             NaN          NaN
        4   Abercynon   ABD  16m 28ch  ...         NaN             NaN          NaN

        [5 rows x 25 columns]

        >>> # To get data of signal boxes
        >>> signal_boxes_data = oa.SignalBoxes.fetch_prefix_codes()
        >>> type(signal_boxes_data)
        <class 'dict'>
        >>> print(list(signal_boxes_data.keys()))
        ['Signal boxes', 'Last updated date']
        >>> signal_boxes_dat = signal_boxes_data['Signal boxes']
        >>> print(signal_boxes_dat.head())
          Code               Signal Box  ...            Closed        Control to
        0   AF  Abbey Foregate Junction  ...
        1   AJ           Abbey Junction  ...  16 February 1992     Nuneaton (NN)
        2    R           Abbey Junction  ...  16 February 1992     Nuneaton (NN)
        3   AW               Abbey Wood  ...      13 July 1975      Dartford (D)
        4   AE         Abbey Works East  ...   1 November 1987  Port Talbot (PT)

        [5 rows x 8 columns]
    """

    def __init__(self, update=False):
        """
        Constructor method.
        """
        # Basic info
        self.Name = 'Other assets'
        self.HomeURL = homepage_url()
        self.SourceURL = urllib.parse.urljoin(
            self.HomeURL, '{}menu.shtm'.format(self.Name.lower().replace(' ', '')))
        self.Catalogue = \
            get_category_menu(self.SourceURL, update=update, confirmation_required=False)
        # Classes
        self.SignalBoxes = sig_box.SignalBoxes(update=update)
        self.Tunnels = tunnel.Tunnels(update=update)
        self.Viaducts = viaduct.Viaducts(update=update)
        self.Stations = station.Stations()
        self.Depots = depot.Depots(update=update)
        self.Features = feature.Features(update=update)

    def update(self, verbose=False, time_gap=2, init_update=False):
        """
        Update local backup of the other assets data.

        :param verbose: whether to print relevant information in console
            as the function runs, defaults to ``False``
        :type verbose: bool
        :param time_gap: time gap (in seconds) between the updating of different classes
        :type time_gap: int
        :param init_update: whether to update the data for instantiation of each subclass,
            defaults to ``False``
        :type init_update: bool

        **Example**::

            >>> from pyrcs.collector import OtherAssets

            >>> oa = OtherAssets()
            >>> oa.update(verbose=True)
        """

        if init_update:
            self.__init__(update=init_update)

        # Signal boxes
        print(f"\n{self.SignalBoxes.Name}:")
        _ = self.SignalBoxes.fetch_prefix_codes(update=True, verbose=verbose)
        _ = self.SignalBoxes.fetch_non_national_rail_codes(update=True, verbose=verbose)

        time.sleep(time_gap)

        # Tunnels
        print(f"\n{self.Tunnels.Name}:")
        _ = self.Tunnels.fetch_tunnel_lengths(update=True, verbose=verbose)

        time.sleep(time_gap)

        # Viaducts
        print(f"\n{self.Viaducts.Name}:")
        _ = self.Viaducts.fetch_viaduct_codes(update=True, verbose=verbose)

        time.sleep(time_gap)

        # Stations
        print(f"\n{self.Stations.Name}:")
        _ = self.Stations.get_station_data_catalogue(update=True, verbose=verbose)
        _ = self.Stations.fetch_station_data(update=True, verbose=verbose)

        time.sleep(time_gap)

        # Depots
        print(f"\n{self.Depots.Name}:")
        _ = self.Depots.fetch_depot_codes(update=True, verbose=verbose)

        time.sleep(time_gap)

        # Features
        print(f"\n{self.Features.Name}:")
        _ = self.Features.fetch_features_codes(update=True, verbose=verbose)
