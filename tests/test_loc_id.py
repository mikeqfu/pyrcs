"""Test the module :py:mod:`pyrcs.line_data.loc_id`."""

import collections

import pandas as pd
import pytest

from pyrcs.line_data import LocationIdentifiers


class TestLocationIdentifiers:
    lid = LocationIdentifiers()

    @pytest.mark.parametrize('update', [True, False])
    @pytest.mark.parametrize('verbose', [True, False])
    def test_fetch_explanatory_note(self, update, verbose):
        exp_note = self.lid.fetch_explanatory_note(update=update, verbose=verbose)

        assert isinstance(exp_note, dict)
        assert list(exp_note.keys()) == [
            'Multiple station codes explanatory note', 'Notes', 'Last updated date']
        exp_note_dat = exp_note[self.lid.KEY_TO_MSCEN]
        assert isinstance(exp_note_dat, pd.DataFrame)

    def test__parse_location_name(self):
        dat = self.lid._location_name('Abbey Wood')
        assert dat == ('Abbey Wood', '')

        dat = self.lid._location_name(None)
        assert dat == ('', '')

        dat = self.lid._location_name('Abercynon (formerly Abercynon South)')
        assert dat == ('Abercynon', 'formerly Abercynon South')

        dat = self.lid._location_name('Allerton (reopened as Liverpool South Parkway)')
        assert dat == ('Allerton', 'reopened as Liverpool South Parkway')

        dat = self.lid._location_name('Ashford International [domestic portion]')
        assert dat == ('Ashford International', 'domestic portion')

        dat = self.lid._location_name('Ayr [unknown feature]')
        assert dat == ('Ayr', 'unknown feature')

    @pytest.mark.parametrize('update', [True, False])
    @pytest.mark.parametrize('verbose', [True, False])
    def test_collect_codes_by_initial(self, update, verbose):
        loc_a = self.lid.collect_codes_by_initial(initial='a', update=update, verbose=verbose)

        assert isinstance(loc_a, dict)
        assert list(loc_a.keys()) == ['A', 'Additional notes', 'Last updated date']

        loc_a_codes = loc_a['A']
        assert isinstance(loc_a_codes, pd.DataFrame)

    @pytest.mark.parametrize('update', [True, False])
    @pytest.mark.parametrize('verbose', [True, False])
    def test_fetch_other_systems_codes(self, update, verbose):
        os_codes = self.lid.fetch_other_systems_codes(update=update, verbose=verbose)

        assert isinstance(os_codes, dict)
        assert list(os_codes.keys()) == ['Other systems', 'Last updated date']
        os_codes_dat = os_codes[self.lid.KEY_TO_OTHER_SYSTEMS]
        assert isinstance(os_codes_dat, collections.defaultdict)

    def test_fetch_codes(self):
        loc_codes = self.lid.fetch_codes()

        assert isinstance(loc_codes, dict)
        assert list(loc_codes.keys()) == [
            'LocationID', 'Other systems', 'Additional notes', 'Last updated date']

        loc_codes_dat = loc_codes['LocationID']
        assert isinstance(loc_codes_dat, pd.DataFrame)

    def test_make_xref_dict(self):
        stanox_dictionary = self.lid.make_xref_dict(keys='STANOX')
        assert isinstance(stanox_dictionary, pd.DataFrame)

        s_t_dictionary = self.lid.make_xref_dict(keys=['STANOX', 'TIPLOC'], initials='a')
        assert isinstance(s_t_dictionary, pd.DataFrame)

        s_t_dictionary = self.lid.make_xref_dict(
            keys=['STANOX', 'TIPLOC'], initials='b', main_key='Data', as_dict=True)
        assert isinstance(s_t_dictionary, dict)
        assert list(s_t_dictionary.keys()) == ['Data']


if __name__ == '__main__':
    pytest.main()
