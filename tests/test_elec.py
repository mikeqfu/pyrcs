"""
Test the module :py:mod:`pyrcs.line_data.elec`.
"""

import pandas as pd
import pytest

from pyrcs.line_data import Electrification


class TestElectrification:

    @pytest.fixture(scope='class')
    def elec(self):
        return Electrification()

    def test_collect_national_network_codes(self, elec):
        nn_codes = elec.collect_national_network_codes(confirmation_required=False, verbose=True)

        assert isinstance(nn_codes, dict)
        assert list(nn_codes.keys()) == ['National network', 'Last updated date']

    def test_get_independent_lines_catalogue(self, elec):
        indep_line_cat = elec.get_independent_lines_catalogue(update=True, verbose=True)

        assert isinstance(indep_line_cat, pd.DataFrame)

    def test_collect_independent_lines_codes(self, elec):
        indep_lines_codes = elec.collect_independent_lines_codes(
            confirmation_required=False, verbose=True)

        assert isinstance(indep_lines_codes, dict)
        assert list(indep_lines_codes.keys()) == ['Independent lines', 'Last updated date']

    def test_collect_ohns_codes(self, elec):
        ohl_ns_codes = elec.collect_ohns_codes(confirmation_required=False, verbose=True)

        assert isinstance(ohl_ns_codes, dict)
        assert list(ohl_ns_codes.keys()) == ['National network neutral sections', 'Last updated date']

    def test_collect_etz_codes(self, elec):
        rail_etz_codes = elec.collect_etz_codes(confirmation_required=False, verbose=True)

        assert isinstance(rail_etz_codes, dict)
        assert list(rail_etz_codes.keys()) == [
            'National network energy tariff zones', 'Last updated date']

    def test_fetch_codes(self, elec, tmp_path, capfd):
        elec_codes = elec.fetch_codes(verbose=2, dump_dir=tmp_path)
        out, _ = capfd.readouterr()
        assert "Saving" in out and "Done." in out
        assert isinstance(elec_codes, dict)
        assert list(elec_codes.keys()) == ['Electrification', 'Last updated date']


if __name__ == '__main__':
    pytest.main()
