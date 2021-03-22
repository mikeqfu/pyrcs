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
from .utils import get_category_menu, homepage_url, is_internet_connected, \
    print_connection_error, print_conn_err


class LineData:
    """
    A class representation of all modules of the subpackage
    :ref:`pyrcs.line_data<line_data>` for collecting line data.

    :param update: whether to do an update check (for the package data), defaults to ``False``
    :type update: bool
    :param verbose: whether to print relevant information in console, defaults to ``True``
    :type verbose: bool or int

    **Examples**::

        >>> from pyrcs import LineData

        >>> ld = LineData()

        >>> # To get data of location codes
        >>> location_codes_data = ld.LocationIdentifiers.fetch_location_codes()

        >>> type(location_codes_data)
        dict
        >>> list(location_codes_data.keys())
        ['Location codes', 'Other systems', 'Additional notes', 'Last updated date']

        >>> location_codes_dat = location_codes_data[ld.LocationIdentifiers.Key]

        >>> type(location_codes_dat)
        pandas.core.frame.DataFrame
        >>> location_codes_dat.head()
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
        dict
        >>> list(line_names_data.keys())
        ['Line names', 'Last updated date']

        >>> line_names_dat = line_names_data[ld.LineNames.Key]

        >>> type(line_names_dat)
        pandas.core.frame.DataFrame
        >>> line_names_dat.head()
                     Line name  ... Route_note
        0           Abbey Line  ...       None
        1        Airedale Line  ...       None
        2          Argyle Line  ...       None
        3     Arun Valley Line  ...       None
        4  Atlantic Coast Line  ...       None
        [5 rows x 3 columns]
    """

    def __init__(self, update=False, verbose=True):
        """
        Constructor method.
        """
        if not is_internet_connected():
            self.Connected = False
            print_connection_error(verbose=verbose)
        else:
            self.Connected = True

        # Basic info
        self.Name = 'Line data'
        self.HomeURL = homepage_url()
        self.SourceURL = urllib.parse.urljoin(
            self.HomeURL, '{}menu.shtm'.format(self.Name.lower().replace(' ', '')))

        self.Catalogue = get_category_menu(url=self.SourceURL, update=update,
                                           confirmation_required=False)

        # Classes
        self.ELRMileages = elr_mileage.ELRMileages(update=update, verbose=False)
        self.Electrification = elec.Electrification(update=update, verbose=False)
        self.LocationIdentifiers = loc_id.LocationIdentifiers(update=update, verbose=False)
        self.LOR = lor_code.LOR(update=update, verbose=False)
        self.LineNames = line_name.LineNames(update=update, verbose=False)
        self.TrackDiagrams = trk_diagr.TrackDiagrams(verbose=False)

    def update(self, confirmation_required=True, verbose=False, time_gap=2, init_update=False):
        """
        Update local backup of the line data.

        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :param time_gap: time gap (in seconds) between updating different classes, defaults to ``2``
        :type time_gap: int
        :param init_update: whether to update the data for instantiation of each subclass,
            defaults to ``False``
        :type init_update: bool

        **Example**::

            >>> from pyrcs import LineData

            >>> ld = LineData()

            >>> ld.update(verbose=True)
        """

        if not self.Connected:
            print_conn_err(verbose=verbose)

        else:
            if confirmed("To update line data?", confirmation_required=confirmation_required):

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
                _ = self.LocationIdentifiers.fetch_location_codes(update=True, verbose=verbose)

                time.sleep(time_gap)

                # Line of routes
                print(f"\n{self.LOR.Name}:")
                _ = self.LOR.get_keys_to_prefixes(prefixes_only=True, update=True, verbose=verbose)
                _ = self.LOR.get_keys_to_prefixes(prefixes_only=False, update=True, verbose=verbose)
                _ = self.LOR.get_lor_page_urls(update=True, verbose=verbose)
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

    :param update: whether to do an update check (for the package data), defaults to ``False``
    :type update: bool
    :param verbose: whether to print relevant information in console, defaults to ``True``
    :type verbose: bool or int
    :type verbose: bool or int

    **Examples**::

        >>> from pyrcs import OtherAssets

        >>> oa = OtherAssets()

        >>> # To get data of railway stations
        >>> railway_station_data = oa.Stations.fetch_station_data()

        >>> type(railway_station_data)
        dict
        >>> list(railway_station_data.keys())
        ['Railway station data', 'Last updated date']

        >>> railway_station_dat = railway_station_data[oa.Stations.StnKey]

        >>> type(railway_station_dat)
        pandas.core.frame.DataFrame
        >>> railway_station_dat.head()
              Station   ELR  ... Prev_Operator_6 Prev_Operator_Period_6
        0  Abbey Wood  XRS3  ...
        1  Abbey Wood   NKL  ...
        2        Aber   CAR  ...
        3   Abercynon   ABD  ...
        4   Abercynon   CAM  ...
        [5 rows x 30 columns]

        >>> # To get data of signal boxes
        >>> signal_boxes_data = oa.SignalBoxes.fetch_prefix_codes()

        >>> type(signal_boxes_data)
        dict
        >>> list(signal_boxes_data.keys())
        ['Signal boxes', 'Last updated date']

        >>> signal_boxes_dat = signal_boxes_data[oa.SignalBoxes.Key]

        >>> signal_boxes_dat.head()
          Code               Signal Box  ...            Closed        Control to
        0   AF  Abbey Foregate Junction  ...
        1   AJ           Abbey Junction  ...  16 February 1992     Nuneaton (NN)
        2    R           Abbey Junction  ...  16 February 1992     Nuneaton (NN)
        3   AW               Abbey Wood  ...      13 July 1975      Dartford (D)
        4   AE         Abbey Works East  ...   1 November 1987  Port Talbot (PT)
        [5 rows x 8 columns]
    """

    def __init__(self, update=False, verbose=True):
        """
        Constructor method.
        """
        if not is_internet_connected():
            self.Connected = False
            print_connection_error(verbose=verbose)
        else:
            self.Connected = True

        # Basic info
        self.Name = 'Other assets'
        self.HomeURL = homepage_url()
        self.SourceURL = urllib.parse.urljoin(
            self.HomeURL, '{}menu.shtm'.format(self.Name.lower().replace(' ', '')))

        self.Catalogue = get_category_menu(url=self.SourceURL, update=update,
                                           confirmation_required=False)

        # Classes
        self.SignalBoxes = sig_box.SignalBoxes(update=update, verbose=False)
        self.Tunnels = tunnel.Tunnels(update=update, verbose=False)
        self.Viaducts = viaduct.Viaducts(update=update, verbose=False)
        self.Stations = station.Stations(verbose=False)
        self.Depots = depot.Depots(update=update, verbose=False)
        self.Features = feature.Features(update=update, verbose=False)

    def update(self, confirmation_required=True, verbose=False, time_gap=2, init_update=False):
        """
        Update local backup of the other assets data.

        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
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

        if not self.Connected:
            print_conn_err(verbose=verbose)

        else:
            if confirmed("To update data of other assets?",
                         confirmation_required=confirmation_required):

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
