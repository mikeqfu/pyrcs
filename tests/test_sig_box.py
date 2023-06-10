"""Test the module :py:mod:`pyrcs.other_assets.sig_box`."""

import collections

import pandas as pd
import pytest

from pyrcs.other_assets import SignalBoxes


# def test_collect_prefix_codes(self):
#     sb_a_codes = self.sb.collect_prefix_codes(initial='a', update=True, verbose=True)
#
#     assert isinstance(sb_a_codes, dict)
#     assert list(sb_a_codes.keys()) == ['A', 'Last updated date']
#
#     sb_a_codes_dat = sb_a_codes['A']
#     assert isinstance(sb_a_codes_dat, pd.DataFrame)


@pytest.mark.parametrize('update', [True, False])
@pytest.mark.parametrize('verbose', [True, False])
class TestSignalBoxes:
    sb = SignalBoxes()

    def test_collect_prefix_codes(self, update, verbose):
        sb_a_codes = self.sb.collect_prefix_codes(initial='a', update=update, verbose=verbose)

        assert isinstance(sb_a_codes, dict)
        assert list(sb_a_codes.keys()) == ['A', 'Last updated date']

        sb_a_codes_dat = sb_a_codes['A']
        assert isinstance(sb_a_codes_dat, pd.DataFrame)

    def test_fetch_prefix_codes(self, update, verbose):
        sb_prefix_codes = self.sb.fetch_prefix_codes(update=update, verbose=verbose)

        assert isinstance(sb_prefix_codes, dict)
        assert list(sb_prefix_codes.keys()) == ['Signal boxes', 'Last updated date']

        sb_prefix_codes_dat = sb_prefix_codes[self.sb.KEY]
        assert isinstance(sb_prefix_codes_dat, pd.DataFrame)

    def test_fetch_non_national_rail_codes(self, update, verbose):
        nnr_codes = self.sb.fetch_non_national_rail_codes(update=update, verbose=verbose)

        assert isinstance(nnr_codes, dict)
        assert list(nnr_codes.keys()) == ['Non-National Rail', 'Last updated date']

        nnr_codes_dat = nnr_codes[self.sb.KEY_TO_NON_NATIONAL_RAIL]
        assert isinstance(nnr_codes_dat, dict)

        sb_prefix_codes = self.sb.fetch_prefix_codes()
        assert isinstance(sb_prefix_codes, dict)

        lu_signals_codes = nnr_codes_dat['London Underground signals']
        assert isinstance(lu_signals_codes, dict)

    def test_fetch_ireland_codes(self, update, verbose):
        ireland_sb_codes = self.sb.fetch_ireland_codes(update=update, verbose=verbose)

        assert isinstance(ireland_sb_codes, dict)
        assert list(ireland_sb_codes.keys()) == ['Ireland', 'Notes', 'Last updated date']
        ireland_sb_codes_dat = ireland_sb_codes[self.sb.KEY_TO_IRELAND]
        assert isinstance(ireland_sb_codes_dat, pd.DataFrame)

    def test_fetch_wr_mas_dates(self, update, verbose):
        sb_wr_mas_dates = self.sb.fetch_wr_mas_dates(update=update, verbose=verbose)

        assert isinstance(sb_wr_mas_dates, dict)
        assert list(sb_wr_mas_dates.keys()) == ['WR MAS dates', 'Last updated date']
        sb_wr_mas_dates_dat = sb_wr_mas_dates[self.sb.KEY_TO_WRMASD]
        assert isinstance(sb_wr_mas_dates_dat, collections.defaultdict)

    def test_fetch_bell_codes(self, update, verbose):
        sb_bell_codes = self.sb.fetch_bell_codes(update=update, verbose=verbose)

        assert isinstance(sb_bell_codes, dict)
        assert list(sb_bell_codes.keys()) == ['Bell codes', 'Last updated date']
        sb_bell_codes_dat = sb_bell_codes[self.sb.KEY_TO_BELL_CODES]
        assert isinstance(sb_bell_codes_dat, collections.OrderedDict)
        sb_nr_bell_codes = sb_bell_codes_dat['Network Rail codes']
        assert isinstance(sb_nr_bell_codes, dict)


if __name__ == '__main__':
    pytest.main()
