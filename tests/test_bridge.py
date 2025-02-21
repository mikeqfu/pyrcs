"""
Test the module :py:mod:`pyrcs.line_data.bridge`.
"""

import pytest

from pyrcs.line_data import Bridges


class TestBridges:

    @pytest.fixture(scope='class')
    def bdg(self):
        return Bridges()

    def test_collect_codes(self, bdg):
        bdg_codes = bdg.collect_codes(confirmation_required=False, verbose=True)
        assert isinstance(bdg_codes, dict)

    def test_fetch_codes(self, bdg):
        bdg_codes = bdg.fetch_codes()
        assert isinstance(bdg_codes, dict)

        keys = [
            'East Coast Main Line',
            'Midland Main Line',
            'West Coast Main Line',
            'Scotland',
            'Elizabeth Line',
            'London Overground',
            'Anglia',
            'London Underground',
            'Key to text presentation conventions',
        ]
        assert all(k in bdg_codes[bdg.KEY] for k in keys)


if __name__ == '__main__':
    pytest.main()
