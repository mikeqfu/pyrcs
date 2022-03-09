"""
Collect data of railway codes.

The current release includes only:

    - `line data <http://www.railwaycodes.org.uk/linedatamenu.shtm>`_
    - `other assets <http://www.railwaycodes.org.uk/otherassetsmenu.shtm>`_
"""

import time

from .line_data import *
from .other_assets import *
from .utils import *


class LineData:
    """
    A class representation of all modules of the subpackage :py:mod:`~pyrcs.line_data`
    for collecting line data.
    """

    #: Name of data
    NAME = 'Line data'
    #: URL of the main web page of the data
    URL = urllib.parse.urljoin(home_page_url(), '{}menu.shtm'.format(NAME.lower().replace(' ', '')))

    def __init__(self, update=False, verbose=True):
        """
        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console, defaults to ``True``
        :type verbose: bool or int

        :ivar bool connected: whether the Internet / the website can be connected
        :ivar dict catalogue: catalogue of the data
        :ivar object ELRMileages: instance of the class :py:class:`~elr_mileage.ELRMileages`
        :ivar object Electrification: instance of the class :py:class:`~elec.Electrification`
        :ivar object LocationIdentifiers: instance of the class :py:class:`~loc_id.LocationIdentifiers`
        :ivar object LOR: instance of the class :py:class:`~lor_code.LOR`
        :ivar object LineNames: instance of the class :py:class:`~line_name.LineNames`
        :ivar object TrackDiagrams: instance of the class :py:class:`~trk_diagr.TrackDiagrams`
        :ivar object Bridges: instance of the class :py:class:`~bridge.Bridges`

        **Examples**::

            >>> from pyrcs import LineData

            >>> ld = LineData()

            >>> # To get data of location codes
            >>> location_codes = ld.LocationIdentifiers.fetch_codes()
            >>> type(location_codes)
            dict
            >>> list(location_codes.keys())
            ['LocationID', 'Other systems', 'Additional notes', 'Last updated date']

            >>> location_codes_dat = location_codes[ld.LocationIdentifiers.KEY]
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
            >>> line_names_codes = ld.LineNames.fetch_codes()
            >>> type(line_names_codes)
            dict
            >>> list(line_names_codes.keys())
            ['Line names', 'Last updated date']

            >>> line_names_codes_dat = line_names_codes[ld.LineNames.KEY]
            >>> type(line_names_codes_dat)
            pandas.core.frame.DataFrame
            >>> line_names_codes_dat.head()
                         Line name  ... Route_note
            0           Abbey Line  ...       None
            1        Airedale Line  ...       None
            2          Argyle Line  ...       None
            3     Arun Valley Line  ...       None
            4  Atlantic Coast Line  ...       None

            [5 rows x 3 columns]
        """

        if not is_home_connectable():
            self.connected = False
            print_connection_error(verbose=verbose)
        else:
            self.connected = True

        self.catalogue = get_category_menu(url=self.URL, update=update, confirmation_required=False)

        # Relevant classes
        self.ELRMileages = elr_mileage.ELRMileages(update=update, verbose=False)
        self.Electrification = elec.Electrification(update=update, verbose=False)
        self.LocationIdentifiers = loc_id.LocationIdentifiers(update=update, verbose=False)
        self.LOR = lor_code.LOR(update=update, verbose=False)
        self.LineNames = line_name.LineNames(update=update, verbose=False)
        self.TrackDiagrams = trk_diagr.TrackDiagrams(update=update, verbose=False)
        self.Bridges = bridge.Bridges(verbose=False)

    def update(self, confirmation_required=True, verbose=False, time_gap=5, init_update=False):
        """
        Update local backup of the `line data <http://www.railwaycodes.org.uk/linedatamenu.shtm>`_.

        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :param time_gap: time gap (in seconds) between the updating of different classes,
            defaults to ``5``
        :type time_gap: int
        :param init_update: whether to update the data for instantiation of each subclass,
            defaults to ``False``
        :type init_update: bool

        **Example**::

            >>> from pyrcs.collector import LineData

            >>> ld = LineData()

            >>> ld.update(verbose=True)
        """

        if not self.connected:
            print_conn_err(verbose=verbose)

        else:
            if confirmed("To update line data\n?", confirmation_required=confirmation_required):

                if init_update:
                    self.__init__(update=init_update)

                # ELR and mileages
                print(f"\n{self.ELRMileages.NAME}:")
                _ = self.ELRMileages.fetch_elr(update=True, verbose=verbose)

                time.sleep(time_gap)

                # Electrification
                print(f"\n{self.Electrification.NAME}:")
                _ = self.Electrification.fetch_codes(update=True, verbose=verbose)

                time.sleep(time_gap)

                # Location
                print(f"\n{self.LocationIdentifiers.NAME}:")
                _ = self.LocationIdentifiers.fetch_codes(update=True, verbose=verbose)

                time.sleep(time_gap)

                # Line of routes
                print(f"\n{self.LOR.NAME}:")
                _ = self.LOR.get_keys_to_prefixes(prefixes_only=True, update=True, verbose=verbose)
                _ = self.LOR.get_keys_to_prefixes(prefixes_only=False, update=True, verbose=verbose)
                _ = self.LOR.get_page_urls(update=True, verbose=verbose)
                _ = self.LOR.fetch_codes(update=True, verbose=verbose)
                _ = self.LOR.fetch_elr_lor_converter(update=True, verbose=verbose)

                time.sleep(time_gap)

                # Line names
                print(f"\n{self.LineNames.NAME}:")
                _ = self.LineNames.fetch_codes(update=True, verbose=verbose)

                # time.sleep(time_gap)

                # # Track diagrams
                # print(f"\n{self.TrackDiagrams.NAME}:")
                # # noinspection PyProtectedMember
                # _ = self.TrackDiagrams._get_items(update=True, verbose=verbose)
                # # noinspection PyProtectedMember
                # _ = self.TrackDiagrams._fetch_catalogue(update=True, verbose=verbose)

                time.sleep(time_gap)

                # Bridges
                print(f"\n{self.Bridges.NAME}:")
                _ = self.Bridges.fetch_codes(update=True, verbose=verbose)


class OtherAssets:
    """
    A class representation of all modules of the subpackage
    :ref:`pyrcs.other_assets<other_assets>` for collecting other assets.
    """

    #: Name of data
    NAME = 'Other assets'
    #: URL of the main web page of the data
    URL = urllib.parse.urljoin(home_page_url(), '{}menu.shtm'.format(NAME.lower().replace(' ', '')))

    def __init__(self, update=False, verbose=True):
        """
        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console, defaults to ``True``
        :type verbose: bool or int

        :ivar bool connected: whether the Internet / the website can be connected
        :ivar dict catalogue: catalogue of the data
        :ivar object SignalBoxes: instance of the class :py:class:`~sig_box.SignalBoxes`
        :ivar object Tunnels: instance of the class :py:class:`~tunnel.Tunnels`
        :ivar object Viaducts: instance of the class :py:class:`~viaduct.Viaducts`
        :ivar object Stations: instance of the class :py:class:`~station.Stations`
        :ivar object Depots: instance of the class :py:class:`~depot.Depots`
        :ivar object Features: instance of the class :py:class:`~feature.Features`

        **Examples**::

            >>> from pyrcs import OtherAssets

            >>> oa = OtherAssets()

            >>> # To get data of railway stations
            >>> rail_stn_locations = oa.Stations.fetch_locations()

            >>> type(rail_stn_locations)
            dict
            >>> list(rail_stn_locations.keys())
            ['Mileages, operators and grid coordinates', 'Last updated date']

            >>> rail_stn_locations_dat = rail_stn_locations[oa.Stations.KEY_TO_STN]
            >>> type(rail_stn_locations_dat)
            pandas.core.frame.DataFrame
            >>> rail_stn_locations_dat.head()
                       Station  ...                                    Former Operator
            0       Abbey Wood  ...  London & South Eastern Railway from 1 April 20...
            1       Abbey Wood  ...
            2             Aber  ...  Keolis Amey Operations/Gweithrediadau Keolis A...
            3        Abercynon  ...  Keolis Amey Operations/Gweithrediadau Keolis A...
            4  Abercynon North  ...  [Cardiff Railway Company from 13 October 1996 ...

            [5 rows x 13 columns]

            >>> # To get data of signal boxes
            >>> signal_boxes_codes = oa.SignalBoxes.fetch_prefix_codes()

            >>> type(signal_boxes_codes)
            dict
            >>> list(signal_boxes_codes.keys())
            ['Signal boxes', 'Last updated date']

            >>> signal_boxes_codes_dat = signal_boxes_codes[oa.SignalBoxes.KEY]
            >>> type(signal_boxes_codes_dat)
            pandas.core.frame.DataFrame
            >>> signal_boxes_codes_dat.head()
              Code               Signal Box  ...            Closed        Control to
            0   AF  Abbey Foregate Junction  ...
            1   AJ           Abbey Junction  ...  16 February 1992     Nuneaton (NN)
            2    R           Abbey Junction  ...  16 February 1992     Nuneaton (NN)
            3   AW               Abbey Wood  ...      13 July 1975      Dartford (D)
            4   AE         Abbey Works East  ...   1 November 1987  Port Talbot (PT)

            [5 rows x 8 columns]
        """

        if not is_home_connectable():
            self.connected = False
            print_connection_error(verbose=verbose)
        else:
            self.connected = True

        self.catalogue = get_category_menu(url=self.URL, update=update, confirmation_required=False)

        # Relevant classes
        self.SignalBoxes = sig_box.SignalBoxes(update=update, verbose=False)
        self.Tunnels = tunnel.Tunnels(update=update, verbose=False)
        self.Viaducts = viaduct.Viaducts(update=update, verbose=False)
        self.Stations = station.Stations(verbose=False)
        self.Depots = depot.Depots(update=update, verbose=False)
        self.Features = feature.Features(update=update, verbose=False)

    def update(self, confirmation_required=True, verbose=False, time_gap=5, init_update=False):
        """
        Update local backup data of the
        `other assets <http://www.railwaycodes.org.uk/otherassetsmenu.shtm>`_.

        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :param time_gap: time gap (in seconds) between the updating of different classes,
            defaults to ``5``
        :type time_gap: int
        :param init_update: whether to update the data for instantiation of each subclass,
            defaults to ``False``
        :type init_update: bool

        **Example**::

            >>> from pyrcs.collector import OtherAssets

            >>> oa = OtherAssets()

            >>> oa.update(verbose=True)
        """

        if not self.connected:
            print_conn_err(verbose=verbose)

        else:
            if confirmed("To update data of other assets\n?", confirmation_required):

                if init_update:
                    self.__init__(update=init_update)

                # Signal boxes
                print(f"\n{self.SignalBoxes.NAME}:")
                _ = self.SignalBoxes.fetch_prefix_codes(update=True, verbose=verbose)
                _ = self.SignalBoxes.fetch_non_national_rail_codes(update=True, verbose=verbose)
                _ = self.SignalBoxes.fetch_ireland_codes(update=True, verbose=verbose)
                _ = self.SignalBoxes.fetch_wr_mas_dates(update=True, verbose=verbose)
                _ = self.SignalBoxes.fetch_bell_codes(update=True, verbose=verbose)

                time.sleep(time_gap)

                # Tunnels
                print(f"\n{self.Tunnels.NAME}:")
                _ = self.Tunnels.fetch_codes(update=True, verbose=verbose)

                time.sleep(time_gap)

                # Viaducts
                print(f"\n{self.Viaducts.NAME}:")
                _ = self.Viaducts.fetch_codes(update=True, verbose=verbose)

                time.sleep(time_gap)

                # Stations
                print(f"\n{self.Stations.NAME}:")
                _ = self.Stations.fetch_locations(update=True, verbose=verbose)

                time.sleep(time_gap)

                # Depots
                print(f"\n{self.Depots.NAME}:")
                _ = self.Depots.fetch_codes(update=True, verbose=verbose)

                time.sleep(time_gap)

                # Features
                print(f"\n{self.Features.NAME}:")
                _ = self.Features.fetch_codes(update=True, verbose=verbose)
