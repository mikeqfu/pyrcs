"""
Collects data of railway codes.

.. note::

    The current release only includes
    `line data <http://www.railwaycodes.org.uk/linedatamenu.shtm>`_ and
    `other assets <http://www.railwaycodes.org.uk/otherassetsmenu.shtm>`_.
"""

import time
import urllib.parse

from pyhelpers.ops import confirmed

from .line_data import (Bridges, ELRMileages, Electrification, LOR, LineNames, LocationIdentifiers,
                        TrackDiagrams)
from .other_assets import Depots, Features, SignalBoxes, Stations, Tunnels, Viaducts
from .parser import get_category_menu
from .utils import home_page_url, is_home_connectable, print_conn_err, print_inst_conn_err


class LineData:
    """
    A class representation of all modules of the subpackage :py:mod:`~pyrcs.line_data`
    for collecting the codes of `line data`_.

    .. _`line data`: http://www.railwaycodes.org.uk/linedatamenu.shtm
    """

    #: The name of the data.
    NAME: str = 'Line data'

    #: The URL of the main web page for the data.
    URL: str = urllib.parse.urljoin(
        home_page_url(), '{}menu.shtm'.format(NAME.lower().replace(' ', '')))

    def __init__(self, update=False, verbose=True):
        """
        :param update: Whether to check for updates to the catalogue; defaults to ``False``.
        :type update: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``True``.
        :type verbose: bool | int

        :ivar bool connected: Whether the Internet / the Railway Codes website is connected.
        :ivar dict catalogue: The catalogue of the line data.
        :ivar ELRMileages ELRMileages: An instance of the :class:`~elr_mileage.ELRMileages` class.
        :ivar Electrification Electrification:
            An instance of the :class:`~elec.Electrification` class.
        :ivar LocationIdentifiers LocationIdentifiers:
            An instance of the :class:`~loc_id.LocationIdentifiers` class.
        :ivar LOR LOR: An instance of the :class:`~lor_code.LOR` class.
        :ivar LineNames LineNames: An instance of the :class:`~line_name.LineNames` class.
        :ivar TrackDiagrams TrackDiagrams:
            An instance of the :class:`~trk_diagr.TrackDiagrams` class.
        :ivar Bridges Bridges: An instance of the :py:class:`~bridge.Bridges` class.

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
            print_conn_err(verbose=verbose)
        else:
            self.connected = True

        self.catalogue = get_category_menu(url=self.URL, update=update, confirmation_required=False)

        # Relevant classes
        self.ELRMileages = ELRMileages(update=update, verbose=False)
        self.Electrification = Electrification(update=update, verbose=False)
        self.LocationIdentifiers = LocationIdentifiers(update=update, verbose=False)
        self.LOR = LOR(update=update, verbose=False)
        self.LineNames = LineNames(update=update, verbose=False)
        self.TrackDiagrams = TrackDiagrams(update=update, verbose=False)
        self.Bridges = Bridges(verbose=False)

    def update(self, confirmation_required=True, verbose=False, interval=5, init_update=False):
        """
        Updates the pre-packed `line data`_.

        .. _`line data`: http://www.railwaycodes.org.uk/linedatamenu.shtm

        :param confirmation_required: Whether user confirmation is required before proceeding;
            defaults to ``True``.
        :type confirmation_required: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :param interval: A time gap (in seconds) between the updating of different classes,
            defaults to ``5``
        :type interval: int or float
        :param init_update: Whether to update the data for each subclass when being instantiated,
            defaults to ``False``
        :type init_update: bool

        **Examples**::

            >>> from pyrcs.collector import LineData
            >>> ld = LineData()
            >>> ld.update(verbose=True)
        """

        if not self.connected:
            print_inst_conn_err(verbose=verbose)

        else:
            if confirmed("To update line data\n?", confirmation_required=confirmation_required):

                if init_update:
                    self.__init__(update=init_update)

                update_args = {'update': True, 'verbose': verbose}

                # ELR and mileages
                print(f"\n{self.ELRMileages.NAME}:")
                _ = self.ELRMileages.fetch_elr(**update_args)

                time.sleep(interval)

                # Electrification
                print(f"\n{self.Electrification.NAME}:")
                _ = self.Electrification.get_indep_line_catalogue(**update_args)
                _ = self.Electrification.fetch_codes(**update_args)

                time.sleep(interval)

                # Location
                print(f"\n{self.LocationIdentifiers.NAME}:")
                _ = self.LocationIdentifiers.fetch_codes(**update_args)

                time.sleep(interval)

                # Line of routes
                print(f"\n{self.LOR.NAME}:")
                _ = self.LOR.get_keys_to_prefixes(prefixes_only=True, **update_args)
                _ = self.LOR.get_keys_to_prefixes(prefixes_only=False, **update_args)
                _ = self.LOR.get_page_urls(**update_args)
                _ = self.LOR.fetch_codes(**update_args)
                _ = self.LOR.fetch_elr_lor_converter(**update_args)

                time.sleep(interval)

                # Line names
                print(f"\n{self.LineNames.NAME}:")
                _ = self.LineNames.fetch_codes(**update_args)

                time.sleep(interval)

                # Track diagrams
                print(f"\n{self.TrackDiagrams.NAME}:")
                _ = self.TrackDiagrams.fetch_catalogue(**update_args)

                time.sleep(interval)

                # Bridges
                print(f"\n{self.Bridges.NAME}:")
                _ = self.Bridges.fetch_codes(**update_args)


class OtherAssets:
    """
    A class representation of all modules of the subpackage :py:mod:`~pyrcs.other_assets`
    for collecting the codes of `other assets`_.

    .. _`other assets`: http://www.railwaycodes.org.uk/otherassetsmenu.shtm
    """

    #: The name of the data.
    NAME: str = 'Other assets'

    #: The URL of the main web page for the data.
    URL: str = urllib.parse.urljoin(
        home_page_url(), '{}menu.shtm'.format(NAME.lower().replace(' ', '')))

    def __init__(self, update=False, verbose=True):
        """
        :param update: Whether to check for updates to the catalogue; defaults to ``False``.
        :type update: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``True``.
        :type verbose: bool | int

        :ivar bool connected: Whether the Internet / the Railway Codes website is connected.
        :ivar dict catalogue: The catalogue of the data.
        :ivar SignalBoxes SignalBoxes: An instance of the :class:`~sig_box.SignalBoxes` class.
        :ivar Tunnels Tunnels: An instance of the :class:`~tunnel.Tunnels` class.
        :ivar Viaducts Viaducts: An instance of the :class:`~viaduct.Viaducts` class.
        :ivar Stations Stations: An instance of the :class:`~station.Stations` class.
        :ivar Depots Depots: An instance of the :class:`~depot.Depots` class.
        :ivar Features Features: An instance of the :class:`~feature.Features` class.

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
            print_conn_err(verbose=verbose)
        else:
            self.connected = True

        self.catalogue = get_category_menu(url=self.URL, update=update, confirmation_required=False)

        # Relevant classes
        self.SignalBoxes = SignalBoxes(update=update, verbose=False)
        self.Tunnels = Tunnels(update=update, verbose=False)
        self.Viaducts = Viaducts(update=update, verbose=False)
        self.Stations = Stations(verbose=False)
        self.Depots = Depots(update=update, verbose=False)
        self.Features = Features(update=update, verbose=False)

    def update(self, confirmation_required=True, verbose=False, interval=5, init_update=False):
        """
        Updates the pre-packed data of the `other assets`_.

        .. _`other assets`: http://www.railwaycodes.org.uk/otherassetsmenu.shtm

        :param confirmation_required: Whether user confirmation is required before proceeding;
            defaults to ``True``.
        :type confirmation_required: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :param interval: A time gap (in seconds) between the updating of different classes,
            defaults to ``5``
        :type interval: int or float
        :param init_update: Whether to update the data for each subclass when being instantiated,
            defaults to ``False``
        :type init_update: bool

        **Examples**::

            >>> from pyrcs.collector import OtherAssets
            >>> oa = OtherAssets()
            >>> oa.update(verbose=True)
        """

        if not self.connected:
            print_inst_conn_err(verbose=verbose)

        else:
            if confirmed("To update data of other assets\n?", confirmation_required):

                if init_update:
                    self.__init__(update=init_update)

                update_args = {'update': True, 'verbose': verbose}

                # Signal boxes
                print(f"\n{self.SignalBoxes.NAME}:")
                _ = self.SignalBoxes.fetch_prefix_codes(**update_args)
                _ = self.SignalBoxes.fetch_non_national_rail_codes(**update_args)
                _ = self.SignalBoxes.fetch_ireland_codes(**update_args)
                _ = self.SignalBoxes.fetch_wr_mas_dates(**update_args)
                _ = self.SignalBoxes.fetch_bell_codes(**update_args)

                time.sleep(interval)

                # Tunnels
                print(f"\n{self.Tunnels.NAME}:")
                _ = self.Tunnels.fetch_codes(**update_args)

                time.sleep(interval)

                # Viaducts
                print(f"\n{self.Viaducts.NAME}:")
                _ = self.Viaducts.fetch_codes(**update_args)

                time.sleep(interval)

                # Stations
                print(f"\n{self.Stations.NAME}:")
                _ = self.Stations.fetch_locations(**update_args)

                time.sleep(interval)

                # Depots
                print(f"\n{self.Depots.NAME}:")
                _ = self.Depots.fetch_codes(**update_args)

                time.sleep(interval)

                # Features
                print(f"\n{self.Features.NAME}:")
                _ = self.Features.fetch_codes(**update_args)
