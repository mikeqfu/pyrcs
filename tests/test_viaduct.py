"""Test the module :py:mod:`pyrcs.other_assets.viaduct`."""

import pandas as pd
import pytest

from pyrcs.other_assets import Viaducts

vdct = Viaducts()


class TestViaducts:

    @staticmethod
    def test_collect_codes_by_page():
        vdct_1_codes = vdct.collect_codes_by_page(page_no=1, update=True, verbose=True)
        assert isinstance(vdct_1_codes, dict)
        assert list(vdct_1_codes.keys()) == ['Page 1 (A-C)', 'Last updated date']

        vdct_1_codes_dat = vdct_1_codes['Page 1 (A-C)']
        assert isinstance(vdct_1_codes_dat, pd.DataFrame)

        vdct_1_codes = vdct.collect_codes_by_page(page_no=1)
        assert isinstance(vdct_1_codes, dict)
        assert list(vdct_1_codes.keys()) == ['Page 1 (A-C)', 'Last updated date']

        vdct_1_codes_dat = vdct_1_codes['Page 1 (A-C)']
        assert isinstance(vdct_1_codes_dat, pd.DataFrame)

    @staticmethod
    def test_fetch_codes():
        vdct_codes = vdct.fetch_codes()
        assert isinstance(vdct_codes, dict)
        assert list(vdct_codes.keys()) == ['Viaducts', 'Last updated date']

        vdct_codes_dat = vdct_codes[vdct.KEY]
        assert isinstance(vdct_codes_dat, dict)


if __name__ == '__main__':
    pytest.main()
