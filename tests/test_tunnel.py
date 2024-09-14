"""
Test the module :py:mod:`pyrcs.other_assets.tunnel`.
"""

import pandas as pd
import pytest

from pyrcs.other_assets import Tunnels


@pytest.mark.parametrize('update', [True, False])
class TestTunnels:

    @pytest.fixture(scope='class')
    def tunl(self):
        return Tunnels()

    def test_collect_codes_by_page(self, tunl, update):
        tunl_len_1 = tunl.collect_codes_by_page(page_no=1, update=update, verbose=True)

        assert isinstance(tunl_len_1, dict)
        assert list(tunl_len_1.keys()) == ['Page 1 (A-F)', 'Last updated date']

        tunl_len_1_codes = tunl_len_1['Page 1 (A-F)']
        assert isinstance(tunl_len_1_codes, pd.DataFrame)

    def test_fetch_codes(self, tunl, update):
        tunl_len_codes = tunl.fetch_codes(update=update, verbose=True)

        assert isinstance(tunl_len_codes, dict)
        assert list(tunl_len_codes.keys()) == ['Tunnels', 'Last updated date']

        tunl_len_codes_dat = tunl_len_codes[tunl.KEY]

        assert isinstance(tunl_len_codes_dat, dict)


if __name__ == '__main__':
    pytest.main()
