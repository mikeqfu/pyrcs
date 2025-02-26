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

    def test_fetch_catalogue(self, stn, update):
        stn_data_cat = stn.fetch_catalogue(update=update, verbose=True)
        assert isinstance(stn_data_cat, dict)

    def test_fetch_locations(self, stn, update):
        stn_locations_a = stn.collect_locations(
            initial='a', confirmation_required=False, verbose=True)

        assert isinstance(stn_locations_a, dict)
        assert list(stn_locations_a.keys()) == ['A', 'Last updated date']
        stn_locations_a_codes = stn_locations_a['A']
        assert isinstance(stn_locations_a_codes, pd.DataFrame)

        stn_location_codes = stn.fetch_locations(update=update, verbose=True)
        assert isinstance(stn_location_codes, dict)
        assert list(stn_location_codes.keys()) == [
            'Mileages, operators and grid coordinates', 'Last updated date']

        stn_location_codes_dat = stn_location_codes[stn.KEY_TO_STN]
        assert isinstance(stn_location_codes_dat, pd.DataFrame)


if __name__ == '__main__':
    pytest.main()
