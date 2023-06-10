"""Test the module :py:mod:`pyrcs.other_assets.station`."""

import pandas as pd
import pytest

from pyrcs.other_assets import Stations


class TestStations:
    stn = Stations()

    @pytest.mark.parametrize('update', [True, False])
    @pytest.mark.parametrize('verbose', [True, False])
    def test__get_station_data_catalogue(self, update, verbose):
        stn_data_cat = self.stn.get_catalogue(update=update, verbose=verbose)
        assert isinstance(stn_data_cat, dict)

    @pytest.mark.parametrize('update', [True, False])
    @pytest.mark.parametrize('verbose', [True, False])
    def test_collect_locations_by_initial(self, update, verbose):
        stn_locations_a = self.stn.collect_locations_by_initial(
            initial='a', update=update, verbose=verbose)

        assert isinstance(stn_locations_a, dict)
        assert list(stn_locations_a.keys()) == ['A', 'Last updated date']
        stn_locations_a_codes = stn_locations_a['A']
        assert isinstance(stn_locations_a_codes, pd.DataFrame)

    def test_fetch_locations(self):
        stn_location_codes = self.stn.fetch_locations()
        assert isinstance(stn_location_codes, dict)
        assert list(stn_location_codes.keys()) == [
            'Mileages, operators and grid coordinates', 'Last updated date']

        stn_location_codes_dat = stn_location_codes[self.stn.KEY_TO_STN]
        assert isinstance(stn_location_codes_dat, pd.DataFrame)


if __name__ == '__main__':
    pytest.main()
