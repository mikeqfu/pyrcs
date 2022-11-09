"""Test the module :py:mod:`pyrcs.line_data.elec`."""

import pandas as pd
import pytest

from pyrcs.line_data import Electrification

elec = Electrification()


class TestElectrification:

    @staticmethod
    def test_collect_national_network_codes():
        nn_codes = elec.collect_national_network_codes(confirmation_required=False, verbose=True)

        assert isinstance(nn_codes, dict)
        assert list(nn_codes.keys()) == ['National network', 'Last updated date']

    @staticmethod
    def test_get_indep_line_catalogue():
        indep_line_cat = elec.get_indep_line_catalogue(update=True, verbose=True)

        assert isinstance(indep_line_cat, pd.DataFrame)

    @staticmethod
    def test_collect_indep_lines_codes():
        indep_lines_codes = elec.collect_indep_lines_codes(confirmation_required=False, verbose=True)

        assert isinstance(indep_lines_codes, dict)
        assert list(indep_lines_codes.keys()) == ['Independent lines', 'Last updated date']

    @staticmethod
    def test_collect_ohns_codes():
        ohl_ns_codes = elec.collect_ohns_codes(confirmation_required=False, verbose=True)

        assert isinstance(ohl_ns_codes, dict)
        assert list(ohl_ns_codes.keys()) == ['National network neutral sections', 'Last updated date']

    @staticmethod
    def test_collect_etz_codes():
        rail_etz_codes = elec.collect_etz_codes(confirmation_required=False, verbose=True)

        assert isinstance(rail_etz_codes, dict)
        assert list(rail_etz_codes.keys()) == [
            'National network energy tariff zones', 'Last updated date']

    @staticmethod
    def test_fetch_codes():
        elec_codes = elec.fetch_codes(verbose=True)

        assert isinstance(elec_codes, dict)
        assert list(elec_codes.keys()) == ['Electrification', 'Last updated date']


if __name__ == '__main__':
    pytest.main()
