"""
Test the module :py:mod:`pyrcs.line_data.loc_id`.
"""

import collections

import pandas as pd
import pytest

from pyrcs.line_data import LocationIdentifiers


class TestLocationIdentifiers:

    @pytest.fixture(scope='class')
    def lid(self):
        return LocationIdentifiers()

    @pytest.mark.parametrize('update', [True, False])
    def test_fetch_explanatory_note(self, lid, update):
        exp_note = lid.fetch_explanatory_note(update=update, verbose=True)

        assert isinstance(exp_note, dict)
        assert list(exp_note.keys()) == [
            'Multiple station codes explanatory note', 'Notes', 'Last updated date']
        exp_note_dat = exp_note[lid.KEY_TO_MSCEN]
        assert isinstance(exp_note_dat, pd.DataFrame)

    def test__parse_location_name(self, lid):
        dat = lid._parse_raw_location_name('Abbey Wood')
        assert dat == ('Abbey Wood', '')

        dat = lid._parse_raw_location_name(None)
        assert dat == ('', '')

        dat = lid._parse_raw_location_name('Abercynon (formerly Abercynon South)')
        assert dat == ('Abercynon', 'formerly Abercynon South')

        dat = lid._parse_raw_location_name('Allerton (reopened as Liverpool South Parkway)')
        assert dat == ('Allerton', 'reopened as Liverpool South Parkway')

        dat = lid._parse_raw_location_name('Ashford International [domestic portion]')
        assert dat == ('Ashford International', 'domestic portion')

        dat = lid._parse_raw_location_name('Ayr [unknown feature]')
        assert dat == ('Ayr', 'unknown feature')

    @pytest.mark.parametrize('update', [True, False])
    def test_collect_codes_by_initial(self, lid, update):
        loc_a = lid.collect_codes_by_initial(initial='a', update=update, verbose=True)

        assert isinstance(loc_a, dict)
        assert list(loc_a.keys()) == ['A', 'Additional notes', 'Last updated date']

        loc_a_codes = loc_a['A']
        assert isinstance(loc_a_codes, pd.DataFrame)

    @pytest.mark.parametrize('update', [True, False])
    def test_fetch_other_systems_codes(self, lid, update):
        os_codes = lid.fetch_other_systems_codes(update=update, verbose=True)

        assert isinstance(os_codes, dict)
        assert list(os_codes.keys()) == ['Other systems', 'Last updated date']
        os_codes_dat = os_codes[lid.KEY_TO_OTHER_SYSTEMS]
        assert isinstance(os_codes_dat, collections.defaultdict)

    def test_fetch_codes(self, lid):
        loc_codes = lid.fetch_codes()

        assert isinstance(loc_codes, dict)
        assert list(loc_codes.keys()) == [
            'LocationID', 'Other systems', 'Additional notes', 'Last updated date']

        loc_codes_dat = loc_codes['LocationID']
        assert isinstance(loc_codes_dat, pd.DataFrame)

    def test_make_xref_dict(self, lid):
        stanox_dictionary = lid.make_xref_dict(keys='STANOX')
        assert isinstance(stanox_dictionary, pd.DataFrame)

        s_t_dictionary = lid.make_xref_dict(keys=['STANOX', 'TIPLOC'], initials='a')
        assert isinstance(s_t_dictionary, pd.DataFrame)

        s_t_dictionary = lid.make_xref_dict(
            keys=['STANOX', 'TIPLOC'], initials='b', main_key='Data', as_dict=True)
        assert isinstance(s_t_dictionary, dict)
        assert list(s_t_dictionary.keys()) == ['Data']


if __name__ == '__main__':
    pytest.main()
