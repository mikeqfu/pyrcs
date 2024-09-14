"""
Test the module :py:mod:`pyrcs.other_assets.feature`.
"""

import pandas as pd
import pytest

from pyrcs.other_assets import Features


class TestFeatures:

    @pytest.fixture(scope='class')
    def feats(self):
        return Features()

    @staticmethod
    def _assert_test_fetch_codes(feats, feats_codes):
        assert isinstance(feats_codes, dict)
        assert list(feats_codes.keys()) == ['Features', 'Last updated date']

        feats_codes_dat = feats_codes[feats.KEY]
        assert isinstance(feats_codes_dat, dict)

        water_troughs_locations = feats_codes_dat[feats.KEY_TO_TROUGH]
        assert isinstance(water_troughs_locations, pd.DataFrame)

    @pytest.mark.parametrize('update', [True, False])
    def test_fetch_codes(self, feats, update):
        feats_codes = feats.fetch_codes(update=update, verbose=True)
        self._assert_test_fetch_codes(feats, feats_codes)

        feats_codes = feats.fetch_codes(verbose=True)
        self._assert_test_fetch_codes(feats, feats_codes)


if __name__ == '__main__':
    pytest.main()
