""" Update package data """

import time

from pyhelpers.ops import confirmed

from pyrcs.line_data import LineData
from pyrcs.other_assets import OtherAssets


def update_package_data(verbose=False):
    """
    Update package data.

    :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
    :type verbose: bool

    **Example**::

        verbose = True

        update_package_data(verbose)
    """

    if confirmed("To update resources?"):

        line_dat = LineData()

        # ELR and mileages
        _ = line_dat.ELRMileages.fetch_elr(update=True, verbose=verbose)

        time.sleep(10)

        # Electrification
        _ = line_dat.Electrification.fetch_electrification_codes(update=True, verbose=verbose)

        time.sleep(10)

        # Location
        _ = line_dat.LocationIdentifiers.fetch_location_codes(update=True, verbose=verbose)
        _ = line_dat.LocationIdentifiers.fetch_additional_crs_note(update=True, verbose=verbose)
        _ = line_dat.LocationIdentifiers.fetch_other_systems_codes(update=True, verbose=verbose)

        time.sleep(10)

        # Line of routes
        _ = line_dat.LOR.fetch_lor_codes(update=True, verbose=verbose)
        _ = line_dat.LOR.fetch_elr_lor_converter(update=True, verbose=verbose)

        time.sleep(10)

        # Line names
        _ = line_dat.LineNames.fetch_line_names(update=True, verbose=verbose)

        """
        # Track diagrams
        """

        time.sleep(10)

        other_assets = OtherAssets()

        # Signal boxes
        _ = other_assets.SignalBoxes.fetch_signal_box_prefix_codes(update=True, verbose=verbose)
        _ = other_assets.SignalBoxes.fetch_non_national_rail_codes(update=True, verbose=verbose)

        time.sleep(10)

        # Tunnels
        _ = other_assets.Tunnels.fetch_railway_tunnel_lengths(update=True, verbose=verbose)

        time.sleep(10)

        # Viaducts
        _ = other_assets.Viaducts.fetch_railway_viaducts(update=True, verbose=verbose)

        time.sleep(10)

        # Stations
        _ = other_assets.Stations.fetch_station_locations(update=True, verbose=verbose)

        time.sleep(10)

        # Depots
        _ = other_assets.Depots.fetch_depot_codes(update=True, verbose=verbose)

        if verbose:
            print("\nUpdate finished.")
