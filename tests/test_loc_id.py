"""
Test the module :py:mod:`pyrcs.line_data.loc_id`.
"""

import collections

import pandas as pd
import pytest

from pyrcs.line_data.loc_id import LocationIdentifiers, _parse_raw_location_name


def test__extra_annotations():
    from pyrcs.line_data.loc_id import _extra_annotations

    assert isinstance(_extra_annotations(), list)


class TestLocationIdentifiers:

    @pytest.fixture(scope='class')
    def lid(self):
        return LocationIdentifiers()

    @pytest.mark.parametrize('update', [True, False])
    def test_fetch_notes(self, lid, update):
        notes = lid.fetch_notes(update=update, verbose=True)

        assert isinstance(notes, dict)
        assert list(notes.keys()) == [lid.KEY_TO_NOTES, lid.KEY_TO_LAST_UPDATED_DATE]

        notes_dat = notes[lid.KEY_TO_NOTES][lid.KEY_TO_MSCEN]
        assert isinstance(notes_dat, list)

    def test__parse_location_name(self):
        dat = _parse_raw_location_name('Abbey Wood')
        assert dat == ('Abbey Wood', '')

        dat = _parse_raw_location_name(None)
        assert dat == ('', '')

        dat = _parse_raw_location_name('Abercynon (formerly Abercynon South)')
        assert dat == ('Abercynon', 'formerly Abercynon South')

        dat = _parse_raw_location_name('Allerton (reopened as Liverpool South Parkway)')
        assert dat == ('Allerton', 'reopened as Liverpool South Parkway')

        dat = _parse_raw_location_name('Ashford International [domestic portion]')
        assert dat == ('Ashford International', 'domestic portion')

        dat = _parse_raw_location_name('Ayr [unknown feature]')
        assert dat == ('Ayr', 'unknown feature')

    @pytest.mark.parametrize('update', [True, False])
    def test_collect_codes_by_initial(self, lid, update):
        loc_a = lid.fetch_loc_id(initial='a', update=update, verbose=True)

        assert isinstance(loc_a, dict)
        assert list(loc_a.keys()) == ['A', 'Notes', 'Last updated date']

        loc_a_codes = loc_a['A']
        assert isinstance(loc_a_codes, pd.DataFrame)

    @pytest.mark.parametrize('update', [True, False])
    def test_fetch_other_systems_codes(self, lid, update):
        os_codes = lid.fetch_other_systems_codes(update=update, verbose=True)

        assert isinstance(os_codes, dict)
        assert list(os_codes.keys()) == ['Other systems', 'Last updated date']
        os_codes_dat = os_codes[lid.KEY_TO_OTHER_SYSTEMS]
        assert isinstance(os_codes_dat, collections.defaultdict)

    def test_fetch_codes(self, lid, tmp_path, capfd):
        loc_codes = lid.fetch_codes(dump_dir=tmp_path, verbose=2)

        out, _ = capfd.readouterr()
        assert "Saving" in out and "Done." in out

        assert isinstance(loc_codes, dict)
        assert list(loc_codes.keys()) == [
            'Location ID', 'Other systems', 'Notes', 'Last updated date']

        loc_codes_dat = loc_codes[lid.KEY]
        assert isinstance(loc_codes_dat, pd.DataFrame)

    def test_make_xref_dict(self, lid, capfd, tmp_path):
        stanox_dictionary = lid.make_xref_dict(keys='STANOX')
        assert isinstance(stanox_dictionary, pd.DataFrame)

        s_t_dictionary = lid.make_xref_dict(keys=['STANOX', 'TIPLOC'], initials='a', verbose=2)
        out, _ = capfd.readouterr()
        assert "Generating location code dictionary" in out and "Done." in out
        assert isinstance(s_t_dictionary, pd.DataFrame)

        s_t_dictionary = lid.make_xref_dict(
            keys=['STANOX', 'TIPLOC'], initials='b', main_key='Data', as_dict=True, verbose=2,
            dump_it=True, dump_dir=tmp_path)
        out, _ = capfd.readouterr()
        assert "Saving" in out and "Done." in out
        assert isinstance(s_t_dictionary, dict)
        assert list(s_t_dictionary.keys()) == ['Data']


if __name__ == '__main__':
    pytest.main()
