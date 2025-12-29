"""
Test the module :py:mod:`pyrcs.other_assets.tunnel`.
"""

import unittest.mock

import numpy as np
import pandas as pd
import pytest

from pyrcs.other_assets.tunnel import Tunnels


class TestTunnels:

    @pytest.fixture(scope='class')
    def tunl(self):
        return Tunnels()

    def test__parse_length(self, tunl):
        assert tunl._parse_length('') == (np.nan, 'Unavailable')
        assert tunl._parse_length('1m 182y') == (1775.7648, '')
        assert tunl._parse_length('formerly 0m236y') == (215.7984, 'Formerly')
        assert tunl._parse_length('0.325km (0m 356y)') == (325.5264, '0.325km')
        assert tunl._parse_length("0m 48yd- (['0m 58yd'])") == (48.4632, '43.89-53.04 metres')
        assert tunl._parse_length('c0m 100yd') == (91.44, 'Approximate')
        assert tunl._parse_length('≈1m 0yd') == (1609.344, 'Approximate')
        assert tunl._parse_length('0m 10ch') == (201.168, '')
        assert tunl._parse_length('0m 50y extra info') == (45.72, 'extra info')

    def test__collect_codes_edge_case(self, tunl, monkeypatch, tmp_path):
        from pyhelpers.store import save_pickle

        # Create mock HTML with specific headers
        html_content = b"""
        <html>
            <body>
                <h3>Page 1 Test</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Tunnel Name</th>
                            <th>Between Alpha</th>
                            <th>Between Beta</th>
                            <th>Length</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Woodland</td>
                            <td>Station A</td>
                            <td>Station B</td>
                            <td>1m 10y</td>
                        </tr>
                    </tbody>
                </table>
            </body>
        </html>
        """

        # Mock the 'source' argument
        mock_source = unittest.mock.MagicMock()
        mock_source.content = html_content

        def side_effect_save(data, data_name, **_kwargs):
            """
            This replaces the real _save_data_to_file during the test.
            It ignores the 'dump_dir' passed by the code and forces it to 'tmp_path'.
            """
            save_pickle(data, tmp_path / f"{data_name}.pkl")

        with unittest.mock.patch(
                'pyrcs.other_assets.tunnel.validate_page_name', return_value='Page 1'), \
                unittest.mock.patch.object(
                    tunl, '_save_data_to_file', side_effect=side_effect_save) as mock_save_data:

            # Run the method
            result = tunl._collect_codes(page_no=1, source=mock_source)

            df = result['Page 1']

            # Verify the rename happened
            assert 'Station A' in df.columns
            assert 'Station B' in df.columns
            assert 'Between Alpha' not in df.columns
            assert 'Between Beta' not in df.columns

            expected_file = tmp_path / "page-1.pkl"
            assert expected_file.exists()

            # Verify the mock was called with the arguments we expected
            mock_save_data.assert_called_once()

    def test_collect_codes(self, tunl):
        tunl_len_1 = tunl.collect_codes(page_no=1, confirmation_required=False, verbose=True)

        assert isinstance(tunl_len_1, dict)
        assert list(tunl_len_1.keys()) == ['Page 1 (A-F)', 'Last updated date']

        tunl_len_1_codes = tunl_len_1['Page 1 (A-F)']
        assert isinstance(tunl_len_1_codes, pd.DataFrame)

    def test_fetch_codes(self, tunl, capfd):
        tunl_len_codes = tunl.fetch_codes(update=False, verbose=2)

        out, _ = capfd.readouterr()
        assert "Loading" in out and "Done." in out

        assert isinstance(tunl_len_codes, dict)
        assert list(tunl_len_codes.keys()) == ['Tunnels', 'Last updated date']

        tunl_len_codes_dat = tunl_len_codes[tunl.KEY]

        assert isinstance(tunl_len_codes_dat, dict)

    def test_fetch_codes_update_failure(self, tunl, monkeypatch, tmp_path, capsys):
        def mock_fetch_data(update=True, **_kwargs):
            if update:
                return None
            return {tunl.KEY: {}, tunl.KEY_TO_LAST_UPDATED_DATE: ''}

        monkeypatch.setattr(tunl, '_fetch_data_from_file', mock_fetch_data)
        tunl.fetch_codes(page_no=None, update=True, verbose=True, dump_dir=tmp_path)

        # Check the captured output
        captured = capsys.readouterr()

        # Assert the specific messages were printed
        assert "The Internet connection is not available." in captured.out
        assert f'No data of "{tunl.KEY}" has been freshly collected.' in captured.out


if __name__ == '__main__':
    pytest.main()
