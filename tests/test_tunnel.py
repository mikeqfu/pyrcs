"""
Test the module :py:mod:`pyrcs.other_assets.tunnel`.
"""

import numpy as np
import pandas as pd
import pytest

from pyrcs.other_assets import Tunnels


class TestTunnels:

    @pytest.fixture(scope='class')
    def tunl(self):
        return Tunnels()

    def test_parse_length(self, tunl):
        assert tunl._parse_length('') == (np.nan, 'Unavailable')
        assert tunl._parse_length('1m 182y') == (1775.7648, '')
        assert tunl._parse_length('formerly 0m236y') == (215.7984, 'Formerly')
        assert tunl._parse_length('0.325km (0m 356y)') == (325.5264, '0.325km')
        assert tunl._parse_length("0m 48yd- (['0m 58yd'])") == (48.4632, '43.89-53.04 metres')

    def test_collect_codes_by_page(self, tunl):
        tunl_len_1 = tunl.collect_codes(page_no=1, confirmation_required=False, verbose=True)

        assert isinstance(tunl_len_1, dict)
        assert list(tunl_len_1.keys()) == ['Page 1 (A-F)', 'Last updated date']

        tunl_len_1_codes = tunl_len_1['Page 1 (A-F)']
        assert isinstance(tunl_len_1_codes, pd.DataFrame)

    @pytest.mark.parametrize('update', [True, False])
    def test_fetch_codes(self, tunl, update, capfd, tmp_path):
        tunl_len_codes = tunl.fetch_codes(update=update, verbose=2)

        out, _ = capfd.readouterr()
        assert ("Loading" if not update else "Updating") in out and "Done." in out

        assert isinstance(tunl_len_codes, dict)
        assert list(tunl_len_codes.keys()) == ['Tunnels', 'Last updated date']

        tunl_len_codes_dat = tunl_len_codes[tunl.KEY]

        assert isinstance(tunl_len_codes_dat, dict)

        _ = tunl.fetch_codes(update=False, verbose=2, dump_dir=tmp_path)
        out, _ = capfd.readouterr()
        assert "Saving" in out and "Done." in out


if __name__ == '__main__':
    pytest.main()
