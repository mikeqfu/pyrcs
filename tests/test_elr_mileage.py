"""Test the module :py:mod:`pyrcs.line_data.elr_mileage`."""

import pandas as pd
import pytest

from pyrcs.line_data import ELRMileages

em = ELRMileages()


class TestELRMileages:

    @staticmethod
    def test_collect_elr_by_initial():
        elrs_a_codes = em.collect_elr_by_initial(initial='a', update=True, verbose=True)

        assert isinstance(elrs_a_codes, dict)
        assert list(elrs_a_codes.keys()) == ['A', 'Last updated date']

        elrs_a_codes_dat = elrs_a_codes['A']
        assert isinstance(elrs_a_codes_dat, pd.DataFrame)

        elrs_q_codes = em.collect_elr_by_initial(initial='Q')
        elrs_q_codes_dat = elrs_q_codes['Q']
        assert isinstance(elrs_q_codes_dat, pd.DataFrame)

    @staticmethod
    def test_fetch_elr():
        elrs_codes = em.fetch_elr()

        assert isinstance(elrs_codes, dict)
        assert list(elrs_codes.keys()) == ['ELRs and mileages', 'Last updated date']

        elrs_codes_dat = elrs_codes[em.KEY]
        assert isinstance(elrs_codes_dat, pd.DataFrame)

    @staticmethod
    def test_collect_mileage_file():
        cjd_mileage_file = em.collect_mileage_file(elr='CJD', confirmation_required=False, verbose=True)

        assert isinstance(cjd_mileage_file, dict)
        assert list(cjd_mileage_file.keys()) == ['ELR', 'Line', 'Sub-Line', 'Mileage', 'Notes']
        assert isinstance(cjd_mileage_file['Mileage'], pd.DataFrame)

        gam_mileage_file = em.collect_mileage_file(elr='GAM', confirmation_required=False, verbose=True)
        assert isinstance(gam_mileage_file['Mileage'], pd.DataFrame)

        sld_mileage_file = em.collect_mileage_file(elr='SLD', confirmation_required=False, verbose=True)
        assert isinstance(sld_mileage_file['Mileage'], pd.DataFrame)

        elr_mileage_file = em.collect_mileage_file(elr='ELR', confirmation_required=False, verbose=True)
        assert isinstance(elr_mileage_file['Mileage'], pd.DataFrame)

    @staticmethod
    def test_fetch_mileage_file():
        aal_mileage_file = em.fetch_mileage_file(elr='AAL')
        assert isinstance(aal_mileage_file, dict)

        # assert aal_mileage_file['ELR'] == 'NAJ3'
        # assert aal_mileage_file['Formerly'] == 'AAL'
        assert isinstance(aal_mileage_file['Mileage'], pd.DataFrame)

        mla_mileage_file = em.fetch_mileage_file(elr='MLA')
        assert isinstance(mla_mileage_file, dict)

    @staticmethod
    def test_search_conn():
        elr_1 = 'AAM'
        mileage_file_1 = em.collect_mileage_file(elr_1, confirmation_required=False)
        mf_1_mileages = mileage_file_1['Mileage']
        assert isinstance(mf_1_mileages, pd.DataFrame)

        elr_2 = 'ANZ'
        mileage_file_2 = em.collect_mileage_file(elr_2, confirmation_required=False)
        mf_2_mileages = mileage_file_2['Mileage']
        assert isinstance(mf_2_mileages, pd.DataFrame)

        elr_1_dest, elr_2_orig = em.search_conn(elr_1, mf_1_mileages, elr_2, mf_2_mileages)
        assert elr_1_dest == '0.0396'
        assert elr_2_orig == '84.1364'

    @staticmethod
    def test_get_conn_mileages():
        conn = em.get_conn_mileages(start_elr='NAY', end_elr='LTN2')
        (s_dest_mlg, c_elr, c_orig_mlg, c_dest_mlg, e_orig_mlg) = conn

        assert s_dest_mlg == '5.1606'
        assert c_elr == 'NOL'
        assert c_orig_mlg == '5.1606'
        assert c_dest_mlg == '0.0638'
        assert e_orig_mlg == '123.1320'

        conn = em.get_conn_mileages(start_elr='MAC3', end_elr='DBP1')
        assert conn == ('', '', '', '', '')


if __name__ == '__main__':
    pytest.main()
