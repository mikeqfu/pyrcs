"""Test the module :py:mod:`pyrcs.line_data.line_name`."""

import pandas as pd
import pytest

from pyrcs.line_data import LineNames

ln = LineNames()


class TestLineNames:

    @staticmethod
    def test_collect_codes():
        line_names_codes = ln.collect_codes(confirmation_required=False, verbose=True)

        assert isinstance(line_names_codes, dict)
        assert list(line_names_codes.keys()) == ['Line names', 'Last updated date']

        line_names_codes_dat = line_names_codes[ln.KEY]
        assert isinstance(line_names_codes_dat, pd.DataFrame)

    @staticmethod
    def test_fetch_codes():
        line_names_codes = ln.fetch_codes(verbose=True)

        assert isinstance(line_names_codes, dict)
        assert list(line_names_codes.keys()) == ['Line names', 'Last updated date']

        line_names_codes_dat = line_names_codes[ln.KEY]
        assert isinstance(line_names_codes_dat, pd.DataFrame)


if __name__ == '__main__':
    pytest.main()
