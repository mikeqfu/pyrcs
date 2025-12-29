"""
Test the module :py:mod:`pyrcs.other_assets.station`.
"""

import pandas as pd
import pytest

from pyrcs.other_assets.station import Stations


@pytest.fixture(scope='class')
def stn():
    return Stations()


class TestStations:

    @pytest.mark.parametrize('update', [True, False])
    def test_fetch_catalogue(self, stn, update):
        stn_data_cat = stn.fetch_catalogue(update=update, verbose=True)
        assert isinstance(stn_data_cat, dict)

    def test_fetch_locations(self, stn):
        stn_locations_a = stn.collect_locations(
            initial='a', confirmation_required=False, verbose=True)

        assert isinstance(stn_locations_a, dict)
        assert list(stn_locations_a.keys()) == ['A', 'Last updated date']
        stn_locations_a_codes = stn_locations_a['A']
        assert isinstance(stn_locations_a_codes, pd.DataFrame)

        stn_location_codes = stn.fetch_locations(verbose=True)
        assert isinstance(stn_location_codes, dict)
        assert list(stn_location_codes.keys()) == [
            'Mileages, operators and grid coordinates', 'Last updated date']

        stn_location_codes_dat = stn_location_codes[stn.KEY_TO_STN]
        assert isinstance(stn_location_codes_dat, pd.DataFrame)

    def test_fetch_locations_update_failure(self, stn, monkeypatch, tmp_path, capsys):

        def mock_fetch_from_file(update=True, initial=None, **_kwargs):
            # The logic uses uppercase letters for keys in the dict
            letter_key = initial.upper() if initial else None

            if update:  # PHASE 1: Trigger the failure branch
                # all(d[x] is None ...) will be True
                return {letter_key: None, stn.KEY_TO_LAST_UPDATED_DATE: None}
            else:  # PHASE 2: Provide valid fallback data for processing
                dummy_df = pd.DataFrame({'Station': ['Test'], 'ELR': ['ABC'], 'Mileage': ['0']})
                return {letter_key: dummy_df, stn.KEY_TO_LAST_UPDATED_DATE: ''}

        monkeypatch.setattr(stn, '_fetch_data_from_file', mock_fetch_from_file)

        result = stn.fetch_locations(update=True, verbose=True, dump_dir=tmp_path)
        captured = capsys.readouterr()

        # Check for the printed failure messages
        assert "The Internet connection is not available" in captured.out
        assert "No data" in captured.out

        # Check the data structure of the result
        assert isinstance(result[stn.KEY_TO_STN], pd.DataFrame)
        assert result[stn.KEY_TO_LAST_UPDATED_DATE] == ''


if __name__ == '__main__':
    pytest.main()
