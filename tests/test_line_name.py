"""Test the module :py:mod:`pyrcs.line_data.line_name`."""

import pandas as pd
import pytest

from pyrcs.line_data import LineNames


class TestLineNames:
    ln = LineNames()

    def _assert_line_names_codes(self, line_names_codes):
        assert isinstance(line_names_codes, dict)
        assert list(line_names_codes.keys()) == ['Line names', 'Last updated date']

        line_names_codes_dat = line_names_codes[self.ln.KEY]
        assert isinstance(line_names_codes_dat, pd.DataFrame)

    def test_collect_and_fetch_codes(self):
        line_names_codes = self.ln.collect_codes(confirmation_required=False, verbose=True)
        self._assert_line_names_codes(line_names_codes)

        line_names_codes = self.ln.fetch_codes(verbose=True)
        self._assert_line_names_codes(line_names_codes)


if __name__ == '__main__':
    pytest.main()
