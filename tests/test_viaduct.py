"""
Test the module :py:mod:`pyrcs.other_assets.viaduct`.
"""

import pandas as pd
import pytest

from pyrcs.other_assets import Viaducts


class TestViaducts:

    @pytest.fixture(scope='class')
    def vdct(self):
        return Viaducts()

    def test_collect_codes_by_page(self, vdct):
        vdct_1_codes = vdct.collect_codes(page_no=1, confirmation_required=False, verbose=True)
        assert isinstance(vdct_1_codes, dict)
        assert list(vdct_1_codes.keys()) == ['Page 1 (A-C)', 'Last updated date']

        vdct_1_codes_dat = vdct_1_codes['Page 1 (A-C)']
        assert isinstance(vdct_1_codes_dat, pd.DataFrame)

    @pytest.mark.parametrize('update', [True, False])
    def test_fetch_codes(self, vdct, update):
        vdct_codes = vdct.fetch_codes(update=update, verbose=True)
        assert isinstance(vdct_codes, dict)
        assert list(vdct_codes.keys()) == ['Viaducts', 'Last updated date']

        vdct_codes_dat = vdct_codes[vdct.KEY]
        assert isinstance(vdct_codes_dat, dict)


if __name__ == '__main__':
    pytest.main()
