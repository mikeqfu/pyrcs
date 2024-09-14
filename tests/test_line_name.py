"""
Test the module :py:mod:`pyrcs.line_data.line_name`.
"""

import pandas as pd
import pytest

from pyrcs.line_data import LineNames


class TestLineNames:

    @pytest.fixture(scope='class')
    def ln(self):
        return LineNames()

    @staticmethod
    def _assert_line_names_codes(ln, line_names_codes):
        assert isinstance(line_names_codes, dict)
        assert list(line_names_codes.keys()) == ['Line names', 'Last updated date']

        line_names_codes_dat = line_names_codes[ln.KEY]
        assert isinstance(line_names_codes_dat, pd.DataFrame)

    def test_collect_and_fetch_codes(self, ln):
        line_names_codes = ln.collect_codes(confirmation_required=False, verbose=True)
        self._assert_line_names_codes(ln, line_names_codes)

        line_names_codes = ln.fetch_codes(verbose=True)
        self._assert_line_names_codes(ln, line_names_codes)


if __name__ == '__main__':
    pytest.main()
