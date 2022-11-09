"""Test the module :py:mod:`pyrcs.line_data.loc_id`."""

import collections

import pandas as pd
import pytest

from pyrcs.line_data import LocationIdentifiers

lid = LocationIdentifiers()


class TestLocationIdentifiers:

    @staticmethod
    def test_fetch_explanatory_note():
        exp_note = lid.fetch_explanatory_note(update=True, verbose=True)

        assert isinstance(exp_note, dict)
        assert list(exp_note.keys()) == [
            'Multiple station codes explanatory note', 'Notes', 'Last updated date']
        exp_note_dat = exp_note[lid.KEY_TO_MSCEN]
        assert isinstance(exp_note_dat, pd.DataFrame)

        exp_note = lid.fetch_explanatory_note()

        assert isinstance(exp_note, dict)
        assert list(exp_note.keys()) == [
            'Multiple station codes explanatory note', 'Notes', 'Last updated date']
        exp_note_dat = exp_note[lid.KEY_TO_MSCEN]
        assert isinstance(exp_note_dat, pd.DataFrame)

    @staticmethod
    def test_collect_codes_by_initial():
        loc_a = lid.collect_codes_by_initial(initial='a', update=True, verbose=True)
        assert isinstance(loc_a, dict)
        assert list(loc_a.keys()) == ['A', 'Additional notes', 'Last updated date']

        loc_a_codes = loc_a['A']
        assert isinstance(loc_a_codes, pd.DataFrame)

        loc_a = lid.collect_codes_by_initial(initial='a')
        assert isinstance(loc_a, dict)
        assert list(loc_a.keys()) == ['A', 'Additional notes', 'Last updated date']

        loc_a_codes = loc_a['A']
        assert isinstance(loc_a_codes, pd.DataFrame)

    @staticmethod
    def test_fetch_other_systems_codes():
        os_codes = lid.fetch_other_systems_codes(update=True, verbose=True)

        assert isinstance(os_codes, dict)
        assert list(os_codes.keys()) == ['Other systems', 'Last updated date']
        os_codes_dat = os_codes[lid.KEY_TO_OTHER_SYSTEMS]
        assert isinstance(os_codes_dat, collections.defaultdict)

        os_codes = lid.fetch_other_systems_codes()

        assert isinstance(os_codes, dict)
        assert list(os_codes.keys()) == ['Other systems', 'Last updated date']
        os_codes_dat = os_codes[lid.KEY_TO_OTHER_SYSTEMS]
        assert isinstance(os_codes_dat, collections.defaultdict)

    @staticmethod
    def test_fetch_codes():
        loc_codes = lid.fetch_codes()

        assert isinstance(loc_codes, dict)
        assert list(loc_codes.keys()) == [
            'LocationID', 'Other systems', 'Additional notes', 'Last updated date']

        loc_codes_dat = loc_codes['LocationID']
        assert isinstance(loc_codes_dat, pd.DataFrame)

    @staticmethod
    def test_make_xref_dict():
        stanox_dictionary = lid.make_xref_dict(keys='STANOX')
        assert isinstance(stanox_dictionary, pd.DataFrame)

        s_t_dictionary = lid.make_xref_dict(keys=['STANOX', 'TIPLOC'], initials='a')
        assert isinstance(s_t_dictionary, pd.DataFrame)

        ks = ['STANOX', 'TIPLOC']
        ini = 'b'
        main_k = 'Data'
        s_t_dictionary = lid.make_xref_dict(ks, ini, main_k, as_dict=True)
        assert isinstance(s_t_dictionary, dict)
        assert list(s_t_dictionary.keys()) == ['Data']


if __name__ == '__main__':
    pytest.main()
