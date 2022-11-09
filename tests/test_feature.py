"""Test the module :py:mod:`pyrcs.other_assets.feature`."""

import pandas as pd
import pytest

from pyrcs.other_assets import Features

feats = Features()


class TestFeatures:

    @staticmethod
    def test_fetch_codes():
        feats_codes = feats.fetch_codes(update=True, verbose=True)

        assert isinstance(feats_codes, dict)
        assert list(feats_codes.keys()) == ['Features', 'Last updated date']

        feats_codes_dat = feats_codes[feats.KEY]
        assert isinstance(feats_codes_dat, dict)

        water_troughs_locations = feats_codes_dat[feats.KEY_TO_TROUGH]
        assert isinstance(water_troughs_locations, pd.DataFrame)

        feats_codes = feats.fetch_codes()

        assert isinstance(feats_codes, dict)
        assert list(feats_codes.keys()) == ['Features', 'Last updated date']

        feats_codes_dat = feats_codes[feats.KEY]
        assert isinstance(feats_codes_dat, dict)

        water_troughs_locations = feats_codes_dat[feats.KEY_TO_TROUGH]
        assert isinstance(water_troughs_locations, pd.DataFrame)


if __name__ == '__main__':
    pytest.main()
