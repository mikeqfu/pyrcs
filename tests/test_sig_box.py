"""
Test the module :py:mod:`pyrcs.other_assets.sig_box`.
"""

import pandas as pd
import pytest

from pyrcs.other_assets.sig_box import SignalBoxes


@pytest.fixture(scope='class')
def sb():
    return SignalBoxes()


class TestSignalBoxes:

    def test_fetch_prefix_codes(self, sb):
        sb_a_codes = sb.collect_prefix_codes(initial='a', confirmation_required=False, verbose=True)

        assert isinstance(sb_a_codes, dict)
        assert list(sb_a_codes.keys()) == ['A', 'Last updated date']

        sb_a_codes_dat = sb_a_codes['A']
        assert isinstance(sb_a_codes_dat, pd.DataFrame)

        sb_prefix_codes = sb.fetch_prefix_codes(verbose=True)

        assert isinstance(sb_prefix_codes, dict)
        assert list(sb_prefix_codes.keys()) == ['Signal boxes', 'Last updated date']

        sb_prefix_codes_dat = sb_prefix_codes[sb.KEY]
        assert isinstance(sb_prefix_codes_dat, pd.DataFrame)

    def test_fetch_prefix_codes_update_failure(self, sb, monkeypatch, tmp_path, capsys):

        def mock_fetch_from_file(update=True, initial=None, **_kwargs):
            # The logic uses uppercase letters for keys in the dict
            letter_key = initial.upper() if initial else None

            if update:  # PHASE 1: Trigger the failure branch
                # all(d[x] is None ...) will be True
                return {letter_key: None, sb.KEY_TO_LAST_UPDATED_DATE: None}
            else:  # PHASE 2: Provide valid fallback data for processing
                dummy_df = pd.DataFrame({'Station': ['Test'], 'ELR': ['ABC'], 'Mileage': ['0']})
                return {letter_key: dummy_df, sb.KEY_TO_LAST_UPDATED_DATE: ''}

        monkeypatch.setattr(sb, '_fetch_data_from_file', mock_fetch_from_file)

        result = sb.fetch_prefix_codes(update=True, verbose=True, dump_dir=tmp_path)
        captured = capsys.readouterr()

        # Check for the printed failure messages
        assert "The Internet connection is not available" in captured.out
        assert "No data" in captured.out

        # Check the data structure of the result
        assert isinstance(result[sb.KEY], pd.DataFrame)
        assert result[sb.KEY_TO_LAST_UPDATED_DATE] == ''

    def test_fetch_non_national_rail_codes(self, sb):
        nnr_codes = sb.fetch_non_national_rail_codes(verbose=True)

        assert isinstance(nnr_codes, dict)
        assert list(nnr_codes.keys()) == ['Non-National Rail', 'Last updated date']

        nnr_codes_dat = nnr_codes[sb.KEY_TO_NON_NATIONAL_RAIL]
        assert isinstance(nnr_codes_dat, dict)

        sb_prefix_codes = sb.fetch_prefix_codes()
        assert isinstance(sb_prefix_codes, dict)

        lu_signals_codes = nnr_codes_dat['London Underground signals']
        assert isinstance(lu_signals_codes, dict)

    def test_fetch_ireland_codes(self, sb):
        ireland_sb_codes = sb.fetch_ireland_codes(verbose=True)

        assert isinstance(ireland_sb_codes, dict)
        assert list(ireland_sb_codes.keys()) == ['Ireland', 'Notes', 'Last updated date']
        ireland_sb_codes_dat = ireland_sb_codes[sb.KEY_TO_IRELAND]
        assert isinstance(ireland_sb_codes_dat, pd.DataFrame)

    def test_fetch_wr_mas_dates(self, sb):
        sb_wr_mas_dates = sb.fetch_wr_mas_dates(verbose=True)

        assert isinstance(sb_wr_mas_dates, dict)
        assert list(sb_wr_mas_dates.keys()) == ['WR MAS dates', 'Last updated date']
        sb_wr_mas_dates_dat = sb_wr_mas_dates[sb.KEY_TO_WRMASD]
        assert isinstance(sb_wr_mas_dates_dat, dict)

    def test_fetch_bell_codes(self, sb):
        sb_bell_codes = sb.fetch_bell_codes(verbose=True)

        assert isinstance(sb_bell_codes, dict)
        assert list(sb_bell_codes.keys()) == ['Bell codes', 'Last updated date']
        sb_bell_codes_dat = sb_bell_codes[sb.KEY_TO_BELL_CODES]
        assert isinstance(sb_bell_codes_dat, dict)
        sb_nr_bell_codes = sb_bell_codes_dat['Network Rail codes']
        assert isinstance(sb_nr_bell_codes, dict)


if __name__ == '__main__':
    pytest.main()
