"""
Test the module :py:mod:`pyrcs.line_data.elr_mileage`.
"""

import functools

import pandas as pd
import pytest

from pyrcs.line_data import ELRMileages


def test__parse_mileages():
    from pyrcs.line_data.elr_mileage import _parse_mileages

    test_data = [['8.69 km', '10.12 km'], ['8.69', '10.12']]

    for i, dat in enumerate(test_data):
        test_mileages = pd.Series(data=dat, index=[0, 1], name='Mileage')
        parsed_mileage = _parse_mileages(test_mileages)
        assert parsed_mileage.columns.tolist() == ['Mileage', 'Mileage_Note', 'Miles_Chains']
        if i == 0:
            assert parsed_mileage['Mileage_Note'].str.contains('km').all()
        else:
            assert parsed_mileage['Mileage_Note'].tolist() == ['', '']


class TestELRMileages:

    @pytest.fixture(scope='class')
    def em(self):
        return ELRMileages()

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

    @pytest.mark.parametrize('update', [False, True])
    def test_fetch_elr(self, em, update):
        elrs_codes = em.fetch_elr(update=update, verbose=True)

        assert isinstance(elrs_codes, dict)
        assert list(elrs_codes.keys()) == ['ELRs and mileages', 'Last updated date']

        elrs_codes_dat = elrs_codes[em.KEY]
        assert isinstance(elrs_codes_dat, pd.DataFrame)

    def test_collect_mileage_file(self, em, monkeypatch, capfd):
        test_elrs = ['GAM', 'SLD', 'ELR']
        for test_elr in test_elrs:
            test_mileage_file = em.collect_mileage_file(
                elr=test_elr, confirmation_required=False, verbose=True)
            out, _ = capfd.readouterr()
            assert f'Collecting the mileage file of "{test_elr}" ... Done.' in out
            assert isinstance(test_mileage_file, dict)
            assert list(test_mileage_file.keys()) == ['ELR', 'Line', 'Sub-Line', 'Mileage', 'Notes']
            assert isinstance(test_mileage_file['Mileage'], pd.DataFrame)

        test_elr = 'CJD'

        monkeypatch.setattr('builtins.input', lambda _: "No")
        test_mileage_file = em.collect_mileage_file(elr=test_elr, verbose=True)
        assert test_mileage_file is None

        monkeypatch.setattr('builtins.input', lambda _: "Yes")
        test_mileage_file = em.collect_mileage_file(elr='CJD', verbose=True)
        out, _ = capfd.readouterr()
        assert 'Collecting the mileage file ... Done.' in out and "Done." in out
        assert isinstance(test_mileage_file, dict)
        assert list(test_mileage_file.keys()) == ['ELR', 'Line', 'Sub-Line', 'Mileage', 'Notes']
        assert isinstance(test_mileage_file['Mileage'], pd.DataFrame)

    @pytest.mark.parametrize('update', [False, True])
    def test_fetch_mileage_file(self, em, update, tmp_path, capfd):
        test_elrs = ['AAL', 'MLA']
        for test_elr in test_elrs:
            test_mileage_file = em.fetch_mileage_file(elr=test_elr, update=update, verbose=True)
            assert isinstance(test_mileage_file, dict)
            assert isinstance(test_mileage_file['Mileage'], (pd.DataFrame, dict))

        test_mileage_file = em.fetch_mileage_file(elr='AAL', verbose=2, dump_dir=tmp_path)
        out, _ = capfd.readouterr()
        assert "Saving" in out and "Done." in out
        assert isinstance(test_mileage_file, dict)
        assert isinstance(test_mileage_file['Mileage'], (pd.DataFrame, dict))

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
