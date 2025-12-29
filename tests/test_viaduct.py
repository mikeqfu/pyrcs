"""
Test the module :py:mod:`pyrcs.other_assets.viaduct`.
"""

import pytest

from pyrcs.other_assets.viaduct import Viaducts


class TestViaducts:

    @pytest.fixture(scope='class')
    def vdct(self):
        return Viaducts()

    def test_collect_codes_by_page(self, vdct):
        vdct_1_codes = vdct.collect_codes(page_no=1, confirmation_required=False, verbose=True)
        assert isinstance(vdct_1_codes, dict)
        assert list(vdct_1_codes.keys()) == ['Page 1 (A-C)', 'Last updated date']

        vdct_1_codes_dat = vdct_1_codes['Page 1 (A-C)']
        assert not vdct_1_codes_dat.empty

    def test_fetch_codes(self, vdct):
        vdct_codes = vdct.fetch_codes(verbose=True)
        assert isinstance(vdct_codes, dict)
        assert list(vdct_codes.keys()) == ['Viaducts', 'Last updated date']

        vdct_codes_dat = vdct_codes[vdct.KEY]
        assert isinstance(vdct_codes_dat, dict)

    def test_fetch_codes_update_failure(self, vdct, monkeypatch, tmp_path, capsys):
        def mock_fetch_data(update=True, **_kwargs):
            if update:
                return None
            return {vdct.KEY: None, vdct.KEY_TO_LAST_UPDATED_DATE: ''}

        monkeypatch.setattr(vdct, '_fetch_data_from_file', mock_fetch_data)
        vdct_codes = vdct.fetch_codes(page_no=None, update=True, verbose=True, dump_dir=tmp_path)

        assert vdct_codes[vdct.KEY] == {vdct.KEY: None}
        assert vdct_codes[vdct.KEY_TO_LAST_UPDATED_DATE] == ''

        # Check the captured output
        captured = capsys.readouterr()

        # Assert the specific messages were printed
        assert "The Internet connection is not available." in captured.out
        assert f'No data of "{vdct.KEY}" has been freshly collected.' in captured.out


if __name__ == '__main__':
    pytest.main()
