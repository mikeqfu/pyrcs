"""
Test the module :py:mod:`pyrcs.other_assets.station`.
"""

import pandas as pd
import pytest

from pyrcs.other_assets import Stations


@pytest.mark.parametrize('update', [True, False])
class TestStations:

    @pytest.fixture(scope='class')
    def stn(self):
        return Stations()

    def test__get_station_data_catalogue(self, stn, update):
        stn_data_cat = stn.get_catalogue(update=update, verbose=True)
        assert isinstance(stn_data_cat, dict)

    def test_collect_locations_by_initial(self, stn, update, verbose=True):
        stn_locations_a = stn.collect_locations_by_initial(
            initial='a', update=update, verbose=verbose)

        assert isinstance(stn_locations_a, dict)
        assert list(stn_locations_a.keys()) == ['A', 'Last updated date']
        stn_locations_a_codes = stn_locations_a['A']
        assert isinstance(stn_locations_a_codes, pd.DataFrame)

    def test_fetch_locations(self, stn, update):
        stn_location_codes = stn.fetch_locations(update=update, verbose=True)
        assert isinstance(stn_location_codes, dict)
        assert list(stn_location_codes.keys()) == [
            'Mileages, operators and grid coordinates', 'Last updated date']

        stn_location_codes_dat = stn_location_codes[stn.KEY_TO_STN]
        assert isinstance(stn_location_codes_dat, pd.DataFrame)


if __name__ == '__main__':
    pytest.main()
