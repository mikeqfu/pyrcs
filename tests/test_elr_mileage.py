"""
Test the module :py:mod:`pyrcs.line_data.elr_mileage`.
"""

import functools

import pandas as pd
import pytest

from pyrcs.line_data import ELRMileages


class TestELRMileages:

    @pytest.fixture(scope='class')
    def em(self):
        return ELRMileages()

    def test_collect_elr(self, em, capfd):
        test_initials = ['a', 'q']
        for initial in test_initials:
            elr_codes = em.collect_elr(initial=initial, confirmation_required=False, verbose=True)

            test_initial = initial.upper()

            out, _ = capfd.readouterr()
            assert f'beginning with "{test_initial}"' in out and "Done." in out

            assert isinstance(elr_codes, dict)
            assert list(elr_codes.keys()) == [test_initial, 'Last updated date']

            elrs_codes_dat = elr_codes[test_initial]
            assert isinstance(elrs_codes_dat, pd.DataFrame)

    @pytest.mark.parametrize('update', [False, True])
    def test_fetch_elr(self, em, update):
        elrs_codes = em.fetch_elr(update=update, verbose=True)

        assert isinstance(elrs_codes, dict)
        assert list(elrs_codes.keys()) == ['ELRs and mileages', 'Last updated date']

        elrs_codes_dat = elrs_codes[em.KEY]
        assert isinstance(elrs_codes_dat, pd.DataFrame)

    def test_collect_mileage_file(self, em):
        test_elrs = ['CJD', 'GAM', 'SLD', 'ELR']
        for test_elr in test_elrs:
            test_mileage_file = em.collect_mileage_file(
                elr=test_elr, confirmation_required=False, verbose=True)

            assert isinstance(test_mileage_file, dict)
            assert list(test_mileage_file.keys()) == ['ELR', 'Line', 'Sub-Line', 'Mileage', 'Notes']
            assert isinstance(test_mileage_file['Mileage'], pd.DataFrame)

    @pytest.mark.parametrize('update', [False, True])
    def test_fetch_mileage_file(self, em, update):
        test_elrs = ['AAL', 'MLA']
        for test_elr in test_elrs:
            test_mileage_file = em.fetch_mileage_file(elr=test_elr, update=update, verbose=True)
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


if __name__ == '__main__':
    pytest.main()
