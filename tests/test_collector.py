"""Test the module :py:mod:`pyrcs.collector`."""

import pandas as pd
import pytest


class TestInit:

    def test_LineData(self):
        from pyrcs import LineData

        ld = LineData()

        location_codes = ld.LocationIdentifiers.fetch_codes()
        assert isinstance(location_codes, dict)
        assert list(location_codes.keys()) == [
            'LocationID', 'Other systems', 'Additional notes', 'Last updated date']

        location_codes_dat = location_codes[ld.LocationIdentifiers.KEY]
        assert isinstance(location_codes_dat, pd.DataFrame)

        line_names_codes = ld.LineNames.fetch_codes()
        assert isinstance(line_names_codes, dict)
        assert list(line_names_codes.keys()) == ['Line names', 'Last updated date']

        line_names_codes_dat = line_names_codes[ld.LineNames.KEY]
        assert isinstance(line_names_codes_dat, pd.DataFrame)

    def test_OtherAssets(self):
        from pyrcs import OtherAssets

        oa = OtherAssets()

        rail_stn_locations = oa.Stations.fetch_locations()

        assert isinstance(rail_stn_locations, dict)
        assert list(rail_stn_locations.keys()) == [
            'Mileages, operators and grid coordinates', 'Last updated date']

        rail_stn_locations_dat = rail_stn_locations[oa.Stations.KEY_TO_STN]
        assert isinstance(rail_stn_locations_dat, pd.DataFrame)

        signal_boxes_codes = oa.SignalBoxes.fetch_prefix_codes()
        assert isinstance(signal_boxes_codes, dict)
        assert list(signal_boxes_codes.keys()) == ['Signal boxes', 'Last updated date']

        signal_boxes_codes_dat = signal_boxes_codes[oa.SignalBoxes.KEY]
        assert isinstance(signal_boxes_codes_dat, pd.DataFrame)


if __name__ == '__main__':
    pytest.main()
