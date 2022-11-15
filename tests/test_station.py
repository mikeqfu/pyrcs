"""Test the module :py:mod:`pyrcs.other_assets.station`."""

import pandas as pd
import pytest

from pyrcs.other_assets import Stations

stn = Stations()


class TestStations:

    @staticmethod
    def test__get_station_data_catalogue():
        stn_data_cat = stn.get_catalogue(update=True, verbose=True)
        assert isinstance(stn_data_cat, dict)

        stn_data_cat = stn.get_catalogue()
        assert isinstance(stn_data_cat, dict)

    @staticmethod
    def test_collect_locations_by_initial():
        stn_locations_a = stn.collect_locations_by_initial(initial='a', update=True, verbose=True)

        assert isinstance(stn_locations_a, dict)
        assert list(stn_locations_a.keys()) == ['A', 'Last updated date']
        stn_locations_a_codes = stn_locations_a['A']
        assert isinstance(stn_locations_a_codes, pd.DataFrame)

        stn_locations_a = stn.collect_locations_by_initial(initial='a')

        assert isinstance(stn_locations_a, dict)
        assert list(stn_locations_a.keys()) == ['A', 'Last updated date']
        stn_locations_a_codes = stn_locations_a['A']
        assert isinstance(stn_locations_a_codes, pd.DataFrame)

    @staticmethod
    def test_fetch_locations():
        stn_location_codes = stn.fetch_locations()
        assert isinstance(stn_location_codes, dict)
        assert list(stn_location_codes.keys()) == [
            'Mileages, operators and grid coordinates', 'Last updated date']

        stn_location_codes_dat = stn_location_codes[stn.KEY_TO_STN]
        assert isinstance(stn_location_codes_dat, pd.DataFrame)


if __name__ == '__main__':
    pytest.main()
