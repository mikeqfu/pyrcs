"""Test the module :py:mod:`pyrcs.other_assets.depot`."""

import pandas as pd
import pytest

from pyrcs.other_assets import Depots


class TestDepots:
    depots = Depots()

    def _assert_test_fetch_codes(self, depots_codes):
        assert isinstance(depots_codes, dict)
        assert list(depots_codes.keys()) == ['Depots', 'Last updated date']

        depots_codes_dat = depots_codes[self.depots.KEY]
        assert isinstance(depots_codes_dat, dict)
        assert isinstance(depots_codes_dat[self.depots.KEY_TO_PRE_TOPS], pd.DataFrame)

    @pytest.mark.parametrize('update', [True, False])
    @pytest.mark.parametrize('verbose', [True, False])
    def test_fetch_codes(self, update, verbose):
        depots_codes = self.depots.fetch_codes(update=update, verbose=verbose)
        self._assert_test_fetch_codes(depots_codes)

        depots_codes = self.depots.fetch_codes()
        self._assert_test_fetch_codes(depots_codes)


if __name__ == '__main__':
    pytest.main()
