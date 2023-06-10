"""Test the module :py:mod:`pyrcs.other_assets.feature`."""

import pandas as pd
import pytest

from pyrcs.other_assets import Features


class TestFeatures:
    feats = Features()

    def _assert_test_fetch_codes(self, feats_codes):
        assert isinstance(feats_codes, dict)
        assert list(feats_codes.keys()) == ['Features', 'Last updated date']

        feats_codes_dat = feats_codes[self.feats.KEY]
        assert isinstance(feats_codes_dat, dict)

        water_troughs_locations = feats_codes_dat[self.feats.KEY_TO_TROUGH]
        assert isinstance(water_troughs_locations, pd.DataFrame)

    @pytest.mark.parametrize('update', [True, False])
    @pytest.mark.parametrize('verbose', [True, False])
    def test_fetch_codes(self, update, verbose):
        feats_codes = self.feats.fetch_codes(update=update, verbose=verbose)
        self._assert_test_fetch_codes(feats_codes)

        feats_codes = self.feats.fetch_codes()
        self._assert_test_fetch_codes(feats_codes)


if __name__ == '__main__':
    pytest.main()
