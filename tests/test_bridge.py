"""Test the module :py:mod:`pyrcs.line_data.bridge`."""

import pytest

from pyrcs.line_data import Bridges


class TestBridges:
    bdg = Bridges()

    def test_collect_codes(self):
        bdg_codes = self.bdg.collect_codes(confirmation_required=False, verbose=True)
        assert isinstance(bdg_codes, dict)

    def test_fetch_codes(self):
        bdg_codes = self.bdg.fetch_codes()
        assert isinstance(bdg_codes, dict)


if __name__ == '__main__':
    pytest.main()
