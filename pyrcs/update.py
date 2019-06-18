""" Update package data """

import time

from pyrcs.line_data import LineData
from pyrcs.other_assets import OtherAssets


def update_package_data():

    line_dat = LineData()

    # ELR and mileages
    _ = line_dat.ELRMileages.fetch_elr(update=True)

    time.sleep(10)

    # Location
    _ = line_dat.LocationIdentifiers.fetch_location_codes(update=True)
    _ = line_dat.LocationIdentifiers.fetch_additional_crs_note(update=True)
    _ = line_dat.LocationIdentifiers.fetch_other_systems_codes(update=True)

    time.sleep(10)

    # Line of routes
    _ = line_dat.LOR.fetch_lor_codes(update=True)
    _ = line_dat.LOR.fetch_elr_lor_converter(update=True)

    time.sleep(10)

    """
    # Line names
    # Electrification
    # Track diagrams
    """

    other_assets = OtherAssets()

    # Signal boxes
    _ = other_assets.SignalBoxes.fetch_signal_box_prefix_codes(update=True)
    _ = other_assets.SignalBoxes.fetch_non_national_rail_codes(update=True)

    time.sleep(10)

    # Stations
    _ = other_assets.Stations.fetch_station_locations(update=True)

    time.sleep(10)

    # Tunnels
    _ = other_assets.Tunnels.fetch_railway_tunnel_lengths(update=True)

    time.sleep(10)

    # Viaducts
    _ = other_assets.Viaducts.fetch_railway_viaducts(update=True)


update_package_data()
