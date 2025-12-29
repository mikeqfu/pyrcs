"""
Test the module :py:mod:`pyrcs.line_data.elr_mileage`.
"""

import functools

import pandas as pd
import pytest

from pyrcs.line_data.elr_mileage import ELRMileages


def test__parse_non_float_str_mileage():
    from pyrcs.line_data.elr_mileage import _parse_non_float_str_mileage

    test_mileages = pd.Series([''])

    miles_chains, mileage_note = _parse_non_float_str_mileage(test_mileages)
    assert miles_chains == ['']
    assert mileage_note == ['']

    test_mileages = pd.Series(['(8.1518)'])
    miles_chains, mileage_note = _parse_non_float_str_mileage(test_mileages)
    assert miles_chains == ['8.1518']
    assert mileage_note == ['Not on this route but given for reference']

    test_mileages = pd.Series(['≈8.1518'])
    miles_chains, mileage_note = _parse_non_float_str_mileage(test_mileages)
    assert miles_chains == ['8.1518']
    assert mileage_note == ['Approximate']

    test_mileages = pd.Series(['8.1518 private portion'])
    miles_chains, mileage_note = _parse_non_float_str_mileage(test_mileages)
    assert miles_chains == ['8.1518']
    assert mileage_note == ['private portion']

    test_mileages = pd.Series(['8.1518†'])
    miles_chains, mileage_note = _parse_non_float_str_mileage(test_mileages)
    assert miles_chains == ['8.1518']
    assert mileage_note == ["(See 'Notes')"]

    test_mileages = pd.Series(['8.1518 private portion'])
    miles_chains, mileage_note = _parse_non_float_str_mileage(test_mileages)
    assert miles_chains == ['8.1518']
    assert mileage_note == ['private portion']


def test__uncouple_elr_mileage():
    from pyrcs.line_data.elr_mileage import _uncouple_elr_mileage

    assert _uncouple_elr_mileage(None) == ['', '']
    assert _uncouple_elr_mileage('ECM5') == ['ECM5', '']
    assert _uncouple_elr_mileage('ECM5 (44.64)') == ['ECM5', '44.64']
    assert _uncouple_elr_mileage('ECM5 (44.64) [Downtown]') == ['ECM5', '44.64']
    assert _uncouple_elr_mileage('ECM5 [Downtown]') == ['ECM5', '']
    assert _uncouple_elr_mileage('DNT (12.3km)') == ['DNT', '7.51']


def test__parse_mileages():
    from pyrcs.line_data.elr_mileage import _parse_mileages

    test_data = [['8.69 km', '10.12 km'], ['8.69', '10.12'], ['8.69 km', '10.12']]

    for i, dat in enumerate(test_data):
        test_mileages = pd.Series(data=dat, index=[0, 1], name='Mileage')
        parsed_mileage = _parse_mileages(mileages=test_mileages)
        assert parsed_mileage.columns.tolist() == ['Mileage', 'Mileage_Note', 'Miles_Chains']
        if i == 0:
            assert parsed_mileage['Mileage_Note'].str.contains('km').all()
        elif i == 1:
            assert parsed_mileage['Mileage_Note'].tolist() == ['', '']
        else:
            assert parsed_mileage['Mileage_Note'].tolist() == ['8.69 km', '']


@pytest.fixture(scope='class')
def em():
    return ELRMileages()


class TestELRMileages:

    def test_collect_elr(self, em, capfd, monkeypatch):
        test_initials = ['a', 'q']
        for initial in test_initials:
            elr_codes = em.collect_elr(initial=initial, confirmation_required=False, verbose=True)

            test_initial = initial.upper()

            out, _ = capfd.readouterr()
            assert f'beginning with "{test_initial}"' in out and "Done." in out

            assert isinstance(elr_codes, dict)
            assert list(elr_codes.keys()) == [test_initial, em.KEY_TO_LAST_UPDATED_DATE]

            elrs_codes_dat = elr_codes[test_initial]
            assert isinstance(elrs_codes_dat, pd.DataFrame)

        test_initial = 'B'

        monkeypatch.setattr('builtins.input', lambda _: "No")
        elr_codes = em.collect_elr(initial='b', verbose=True)
        assert elr_codes is None

        monkeypatch.setattr('builtins.input', lambda _: "Yes")
        elr_codes = em.collect_elr(initial=test_initial, verbose=True)
        out, _ = capfd.readouterr()
        assert "Collecting the data" in out and "Done." in out

        assert isinstance(elr_codes, dict)
        assert list(elr_codes.keys()) == [test_initial, em.KEY_TO_LAST_UPDATED_DATE]
        elrs_codes_dat = elr_codes[test_initial]
        assert isinstance(elrs_codes_dat, pd.DataFrame)

    def test_fetch_elr(self, em, tmp_path, capfd):
        elrs_codes_a = em.fetch_elr(initial='a', dump_dir=tmp_path, verbose=2)
        out, _ = capfd.readouterr()
        assert 'Saving "a.pkl"' in out and "Done." in out

        assert isinstance(elrs_codes_a, dict)
        assert list(elrs_codes_a.keys()) == ['A', em.KEY_TO_LAST_UPDATED_DATE]

        elrs_codes = em.fetch_elr(verbose=True)

        assert isinstance(elrs_codes, dict)
        assert list(elrs_codes.keys()) == ['ELRs and mileages', em.KEY_TO_LAST_UPDATED_DATE]

        elrs_codes_dat = elrs_codes[em.KEY]
        assert isinstance(elrs_codes_dat, pd.DataFrame)

        elrs_codes = em.fetch_elr(dump_dir=tmp_path, verbose=2)
        out, _ = capfd.readouterr()
        assert "Saving" in out and "Done." in out

        assert isinstance(elrs_codes, dict)
        assert list(elrs_codes.keys()) == [em.KEY, em.KEY_TO_LAST_UPDATED_DATE]

        elrs_codes_dat = elrs_codes[em.KEY]
        assert isinstance(elrs_codes_dat, pd.DataFrame)

    def test__get_parsed_contents(self, em):
        elr_dat = pd.DataFrame({
            'Line name': ['Main Line'],
            'Mileages': ['0.00 - 1.00'],
            'Datum': ['']
        })
        notes = 'loc_a and loc_b'
        line_name, parsed_content = em._get_parsed_contents(elr_dat, notes)
        assert line_name == 'Main Line'
        assert parsed_content == [['0.00', 'loc_a'], ['1.00', 'loc_b']]

        elr_dat = pd.DataFrame({
            'Line name': ['Main Line'],
            'Mileages': ['0.00 - 2.00'],
            'Datum': ['Datum A']
        })
        notes = ''
        line_name, parsed_content = em._get_parsed_contents(elr_dat, notes)
        assert line_name == 'Main Line'
        assert parsed_content == [['0.00', 'Datum A'], ['2.00', 'Main Line']]

        elr_dat = pd.DataFrame({
            'Line name': ['Main Line'],
            'Mileages': ['0.00 - 2.00'],
            'Datum': ['']
        })
        notes = ''
        line_name, parsed_content = em._get_parsed_contents(elr_dat, notes)
        assert line_name == 'Main Line'
        assert parsed_content == [['0.00', 'Main Line'], ['2.00', 'Main Line']]

    def test_mileage_parsing_and_splitting(self, em, monkeypatch):
        # 1. Setup a mock class instance to provide self.measure_headers
        class MockParser:
            measure_headers = [
                'Current measure', 'Original measure', 'Later measure',
                'One measure', 'Alternative measure', 'Previous measure'
            ]
            # Attach the methods to the mock instance
            _split_measures = em._split_measures
            _parse_mileage_and_notes = em._parse_mileage_and_notes

        parser = MockParser()

        # --- Scenario 1: Test "Later measure" splitting logic ---
        # This covers the branch where measure_headers_indices == 1 and requires
        # the creation of a "Later" vs "Earlier" dictionary mapping.
        content_later = [
            ['0.00', 'Station A'],
            ['0.50', 'Station B'],
            ['', 'Later measure'],  # This is the split point
            ['0.00', 'Station A New'],
            ['0.60', 'Station B New'],
        ]

        # We need to mock 'loop_in_pairs' if it's not imported
        # Typically: loop_in_pairs([0, 3, 6]) -> [(0, 3), (3, 6)]
        def mock_loop(iterable):
            it = iter(iterable)
            prev = next(it)
            for item in it:
                yield prev, item
                prev = item

        monkeypatch.setattr('pyrcs.line_data.elr_mileage.loop_in_pairs', mock_loop)

        mil_dat, notes = parser._parse_mileage_and_notes(content_later)

        # Verify that the data was split into two measures
        assert isinstance(mil_dat, dict)
        assert 'Earlier measure' in mil_dat
        assert 'Later measure' in mil_dat
        assert len(mil_dat['Earlier measure']) == 2
        assert len(mil_dat['Later measure']) == 2

        # --- Scenario 2: Test "Alternative measure" logic via else branch ---
        # This covers the branch: if 'One measure' in test_temp_node
        content_alt = [
            ['', 'One measure'],
            ['1.00', 'Point A'],
            ['', 'Alternative measure'],
            ['1.05', 'Point A Alt'],
            ['(A note about distances)']  # Single element list becomes a note
        ]

        mil_dat_alt, notes_alt = parser._parse_mileage_and_notes(content_alt)

        assert 'One measure' in mil_dat_alt
        assert 'Alternative measure' in mil_dat_alt
        assert 'A note about distances' in notes_alt['Notes']

        # --- Scenario 3: Test km suffixing ---
        content_km = [
            ['10.00', 'Kilometer Point'],
            ['Distances in km']
        ]
        mil_dat_km, _ = parser._parse_mileage_and_notes(content_km)

        # Check that 'km' was appended to the mileage string
        assert mil_dat_km.iloc[0]['Mileage'] == '10.00km'

    def test_collect_mileage_file(self, em, monkeypatch, capfd):
        test_elrs = ['GAM', 'SLD', 'ELR', 'BTJ']
        for test_elr in test_elrs:
            test_mileage_file = em.collect_mileage_file(
                elr=test_elr, confirmation_required=False, verbose=True)
            out, _ = capfd.readouterr()
            assert f'Collecting the mileage file of "{test_elr}" ... Done.' in out
            assert isinstance(test_mileage_file, dict)
            assert list(test_mileage_file.keys()) == ['ELR', 'Line', 'Sub-Line', 'Mileage', 'Notes']
            assert isinstance(test_mileage_file['Mileage'], (pd.DataFrame, dict))

        test_elr = 'CJD'

        monkeypatch.setattr('builtins.input', lambda _: "No")
        test_mileage_file = em.collect_mileage_file(elr=test_elr, verbose=True)
        assert test_mileage_file is None

        monkeypatch.setattr('builtins.input', lambda _: "Yes")
        test_mileage_file = em.collect_mileage_file(elr=test_elr, verbose=True)
        out, _ = capfd.readouterr()
        assert 'Collecting the mileage file ... Done.' in out and "Done." in out
        assert isinstance(test_mileage_file, dict)
        assert list(test_mileage_file.keys()) == ['ELR', 'Line', 'Sub-Line', 'Mileage', 'Notes']
        assert isinstance(test_mileage_file['Mileage'], pd.DataFrame)

    def test_fetch_mileage_file(self, em, tmp_path, capfd):
        for test_elr in ['AAL', 'MLA', 'FED']:
            test_mileage_file = em.fetch_mileage_file(elr=test_elr, dump_dir=None, verbose=True)
            assert isinstance(test_mileage_file, dict)
            assert isinstance(test_mileage_file['Mileage'], (pd.DataFrame, dict))

        aal_mileage_file = em.fetch_mileage_file(elr='AAL', update=True, verbose=2)
        out, _ = capfd.readouterr()
        assert "Updating" in out and "Done." in out
        assert isinstance(aal_mileage_file, dict)
        assert isinstance(aal_mileage_file['Mileage'], (pd.DataFrame, dict))

        lcg_mileage_file = em.fetch_mileage_file(elr='LCG', dump_dir=tmp_path)
        assert isinstance(lcg_mileage_file, dict)
        assert isinstance(lcg_mileage_file['Mileage'], (pd.DataFrame, dict))

        abk_mileage_file = em.fetch_mileage_file(elr='ABK', dump_dir=tmp_path)
        assert isinstance(abk_mileage_file, dict)
        assert isinstance(abk_mileage_file['Mileage'], (pd.DataFrame, dict))

    def test_search_conn(self, em):
        elr_1, elr_2 = 'AAM', 'ANZ'

        mileage_file_1, mileage_file_2 = map(
            functools.partial(em.collect_mileage_file, confirmation_required=False),
            [elr_1, elr_2])
        mf_1_mileages, mf_2_mileages = mileage_file_1['Mileage'], mileage_file_2['Mileage']

        elr_1_dest, elr_2_orig = em.search_conn(elr_1, mf_1_mileages, elr_2, mf_2_mileages)
        assert (elr_1_dest, elr_2_orig) == ('0.0396', '84.1364')

    def test_get_conn_mileages(self, em):
        conn = em.get_conn_mileages(start_elr='NAY', end_elr='LTN2')
        assert conn == ('5.1606', 'NOL', '5.1606', '0.0638', '123.1320')

        conn = em.get_conn_mileages(start_elr='MAC3', end_elr='DBP1')
        assert conn == ('', '', '', '', '')

        conn = em.get_conn_mileages(start_elr='MAC4', end_elr='DBP4')
        assert conn == ('', '', '', '', '')


if __name__ == '__main__':
    pytest.main()
