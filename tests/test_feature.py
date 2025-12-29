"""
Test the module :py:mod:`pyrcs.other_assets.feature`.
"""

import pytest

from pyrcs.other_assets.feature import Features


@pytest.fixture(scope='class')
def feats():
    return Features()


class TestFeatures:

    @staticmethod
    def _assert_test_fetch_codes(feats, feats_codes):
        assert isinstance(feats_codes, dict)
        assert list(feats_codes.keys()) == ['Features', 'Last updated date']

        feats_codes_dat = feats_codes[feats.KEY]
        assert isinstance(feats_codes_dat, dict)

        water_troughs_locations = feats_codes_dat[feats.KEY_TO_TROUGH]
        assert hasattr(water_troughs_locations, 'T')

    def test_fetch_codes(self, feats, tmp_path, monkeypatch, capfd):
        feats_codes = feats.fetch_codes(dump_dir=tmp_path, verbose=2)
        out, _ = capfd.readouterr()
        assert "Saving" in out and "Done." in out
        self._assert_test_fetch_codes(feats, feats_codes)

        feats_codes = feats.fetch_codes(verbose=2)
        out, _ = capfd.readouterr()
        assert "Loading" in out and "Done." in out
        self._assert_test_fetch_codes(feats, feats_codes)


if __name__ == '__main__':
    pytest.main()
