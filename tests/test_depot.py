"""
Test the module :py:mod:`pyrcs.other_assets.depot`.
"""

import pandas as pd
import pytest

from pyrcs.other_assets.depot import Depots


@pytest.fixture(scope='class')
def depots():
    return Depots()


class TestDepots:

    @staticmethod
    def _assert_test_fetch_codes(depots, depots_codes):
        assert isinstance(depots_codes, dict)
        assert list(depots_codes.keys()) == ['Depots', 'Last updated date']

        depots_codes_dat = depots_codes[depots.KEY]
        assert isinstance(depots_codes_dat, dict)
        assert isinstance(depots_codes_dat[depots.KEY_TO_PRE_TOPS], pd.DataFrame)

    def test_fetch_codes(self, depots):
        depots_codes = depots.fetch_codes(verbose=True)
        self._assert_test_fetch_codes(depots, depots_codes)


if __name__ == '__main__':
    pytest.main()
