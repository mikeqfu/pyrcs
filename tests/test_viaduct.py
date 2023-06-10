"""Test the module :py:mod:`pyrcs.other_assets.viaduct`."""

import pandas as pd
import pytest

from pyrcs.other_assets import Viaducts


class TestViaducts:
    vdct = Viaducts()

    @pytest.mark.parametrize('update', [True, False])
    @pytest.mark.parametrize('verbose', [True, False])
    def test_collect_codes_by_page(self, update, verbose):
        vdct_1_codes = self.vdct.collect_codes_by_page(page_no=1, update=update, verbose=verbose)
        assert isinstance(vdct_1_codes, dict)
        assert list(vdct_1_codes.keys()) == ['Page 1 (A-C)', 'Last updated date']

        vdct_1_codes_dat = vdct_1_codes['Page 1 (A-C)']
        assert isinstance(vdct_1_codes_dat, pd.DataFrame)

    def test_fetch_codes(self):
        vdct_codes = self.vdct.fetch_codes()
        assert isinstance(vdct_codes, dict)
        assert list(vdct_codes.keys()) == ['Viaducts', 'Last updated date']

        vdct_codes_dat = vdct_codes[self.vdct.KEY]
        assert isinstance(vdct_codes_dat, dict)


if __name__ == '__main__':
    pytest.main()
