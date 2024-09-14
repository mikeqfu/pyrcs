"""
Test the module :py:mod:`pyrcs.line_data.lor_code`.
"""

import pandas as pd
import pytest

from pyrcs.line_data import LOR


@pytest.mark.parametrize('update', [True, False])
class TestLORCode:

    @pytest.fixture(scope='class')
    def lor(self):
        return LOR()

    def test_get_keys_to_prefixes(self, lor, update):
        keys_to_pfx = lor.get_keys_to_prefixes(update=update, verbose=True)
        assert set(keys_to_pfx) == {'CY', 'EA', 'GW', 'LN', 'MD', 'NW', 'NZ', 'SC', 'SO', 'SW', 'XR'}

        keys_to_pfx = lor.get_keys_to_prefixes(prefixes_only=False)
        assert isinstance(keys_to_pfx, dict)
        assert list(keys_to_pfx.keys()) == ['Key to prefixes', 'Last updated date']

        keys_to_pfx_codes = keys_to_pfx['Key to prefixes']
        assert isinstance(keys_to_pfx_codes, pd.DataFrame)

    def test_get_page_urls(self, lor, update):
        lor_urls = lor.get_page_urls(update=update, verbose=True)
        assert isinstance(lor_urls, list)

    def test_collect_codes_by_prefix(self, lor, update):
        lor_codes_cy = lor.collect_codes_by_prefix(prefix='CY', update=True, verbose=True)

        assert isinstance(lor_codes_cy, dict)
        assert list(lor_codes_cy.keys()) == ['CY', 'Notes', 'Last updated date']

        cy_codes = lor_codes_cy['CY']
        assert isinstance(cy_codes, pd.DataFrame)

        lor_codes_nw = lor.collect_codes_by_prefix(prefix='NW', update=update, verbose=True)
        assert isinstance(lor_codes_nw, dict)
        nw_codes = lor_codes_nw['NW/NZ']
        assert isinstance(nw_codes, pd.DataFrame)

        lor_codes_nw = lor.collect_codes_by_prefix(prefix='NW', verbose=True)
        assert isinstance(lor_codes_nw, dict)
        nw_codes = lor_codes_nw['NW/NZ']
        assert isinstance(nw_codes, pd.DataFrame)

        lor_codes_xr = lor.collect_codes_by_prefix(prefix='XR', verbose=True)
        assert isinstance(lor_codes_xr, dict)
        xr_codes = lor_codes_xr['XR']
        assert isinstance(xr_codes, dict)
        assert list(xr_codes.keys()) == [
            'Current codes', 'Current codes note', 'Past codes', 'Past codes note']

    def test_fetch_codes(self, lor, update):
        lor_codes_dat = lor.fetch_codes(update=update, verbose=True)
        assert isinstance(lor_codes_dat, dict)

        l_codes = lor_codes_dat['LOR']
        assert isinstance(l_codes, dict)

    def test_fetch_elr_lor_converter(self, lor, update):
        elr_lor_conv = lor.fetch_elr_lor_converter(update=update, verbose=True)

        assert isinstance(elr_lor_conv, dict)
        assert list(elr_lor_conv.keys()) == ['ELR/LOR converter', 'Last updated date']
        elr_loc_conv_data = elr_lor_conv['ELR/LOR converter']
        assert isinstance(elr_loc_conv_data, pd.DataFrame)


if __name__ == '__main__':
    pytest.main()
