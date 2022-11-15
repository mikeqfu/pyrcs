"""Test the module :py:mod:`pyrcs.line_data.lor_code`."""

import pandas as pd
import pytest

from pyrcs.line_data import LOR

lor = LOR()


class TestLORCode:

    @staticmethod
    def test_get_keys_to_prefixes():
        keys_to_pfx = lor.get_keys_to_prefixes(update=True, verbose=True)
        assert set(keys_to_pfx) == {'CY', 'EA', 'GW', 'LN', 'MD', 'NW', 'NZ', 'SC', 'SO', 'SW', 'XR'}

        keys_to_pfx = lor.get_keys_to_prefixes()
        assert set(keys_to_pfx) == {'CY', 'EA', 'GW', 'LN', 'MD', 'NW', 'NZ', 'SC', 'SO', 'SW', 'XR'}

        keys_to_pfx = lor.get_keys_to_prefixes(prefixes_only=False)
        assert isinstance(keys_to_pfx, dict)
        assert list(keys_to_pfx.keys()) == ['Key to prefixes', 'Last updated date']

        keys_to_pfx_codes = keys_to_pfx['Key to prefixes']
        assert isinstance(keys_to_pfx_codes, pd.DataFrame)

    @staticmethod
    def test_get_page_urls():
        lor_urls = lor.get_page_urls(update=True, verbose=True)
        assert isinstance(lor_urls, list)

        lor_urls = lor.get_page_urls()
        assert isinstance(lor_urls, list)

    @staticmethod
    def test_collect_codes_by_prefix():
        lor_codes_cy = lor.collect_codes_by_prefix(prefix='CY', update=True, verbose=True)

        assert isinstance(lor_codes_cy, dict)
        assert list(lor_codes_cy.keys()) == ['CY', 'Notes', 'Last updated date']

        cy_codes = lor_codes_cy['CY']
        assert isinstance(cy_codes, pd.DataFrame)

        lor_codes_nw = lor.collect_codes_by_prefix(prefix='NW', update=True, verbose=True)
        assert isinstance(lor_codes_nw, dict)
        nw_codes = lor_codes_nw['NW/NZ']
        assert isinstance(nw_codes, pd.DataFrame)

        lor_codes_nw = lor.collect_codes_by_prefix(prefix='NW')
        assert isinstance(lor_codes_nw, dict)
        nw_codes = lor_codes_nw['NW/NZ']
        assert isinstance(nw_codes, pd.DataFrame)

        lor_codes_xr = lor.collect_codes_by_prefix(prefix='XR')
        assert isinstance(lor_codes_xr, dict)
        xr_codes = lor_codes_xr['XR']
        assert isinstance(xr_codes, dict)
        assert list(xr_codes.keys()) == [
            'Current codes', 'Current codes note', 'Past codes', 'Past codes note']

    @staticmethod
    def test_fetch_codes():
        lor_codes_dat = lor.fetch_codes()
        assert isinstance(lor_codes_dat, dict)

        l_codes = lor_codes_dat['LOR']
        assert isinstance(l_codes, dict)

    @staticmethod
    def test_fetch_elr_lor_converter():
        elr_lor_conv = lor.fetch_elr_lor_converter(update=True, verbose=True)

        assert isinstance(elr_lor_conv, dict)
        assert list(elr_lor_conv.keys()) == ['ELR/LOR converter', 'Last updated date']
        elr_loc_conv_data = elr_lor_conv['ELR/LOR converter']
        assert isinstance(elr_loc_conv_data, pd.DataFrame)

        elr_lor_conv = lor.fetch_elr_lor_converter()

        assert isinstance(elr_lor_conv, dict)
        assert list(elr_lor_conv.keys()) == ['ELR/LOR converter', 'Last updated date']
        elr_loc_conv_data = elr_lor_conv['ELR/LOR converter']
        assert isinstance(elr_loc_conv_data, pd.DataFrame)


if __name__ == '__main__':
    pytest.main()
