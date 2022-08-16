"""Test the module :py:mod:`pyrcs.other_assets.depot`."""

import pandas as pd
import pytest

from pyrcs.other_assets import Depots

depots = Depots()


def test_fetch_codes():
    depots_codes = depots.fetch_codes(update=True, verbose=True)

    assert isinstance(depots_codes, dict)
    assert list(depots_codes.keys()) == ['Depots', 'Last updated date']

    depots_codes_dat = depots_codes[depots.KEY]
    assert isinstance(depots_codes_dat, dict)
    assert isinstance(depots_codes_dat[depots.KEY_TO_PRE_TOPS], pd.DataFrame)

    depots_codes = depots.fetch_codes()

    assert isinstance(depots_codes, dict)
    assert list(depots_codes.keys()) == ['Depots', 'Last updated date']

    depots_codes_dat = depots_codes[depots.KEY]
    assert isinstance(depots_codes_dat, dict)
    assert isinstance(depots_codes_dat[depots.KEY_TO_PRE_TOPS], pd.DataFrame)


if __name__ == '__main__':
    pytest.main()
