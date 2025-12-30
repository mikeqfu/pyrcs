"""
Test the module :py:mod:`pyrcs._updater`.
"""

import unittest.mock

import pytest


def test__update_prepacked_data(capfd):
    from pyrcs._updater import _update_prepacked_data

    mod = 'pyrcs._updater'

    with unittest.mock.patch(f'{mod}.is_homepage_connectable') as mock_connectable, \
            unittest.mock.patch(f'{mod}.confirmed') as mock_confirmed, \
            unittest.mock.patch(f'{mod}.get_site_map') as mock_gsm, \
            unittest.mock.patch(f'{mod}.LineData') as mock_ld, \
            unittest.mock.patch(f'{mod}.OtherAssets') as mock_oa:

        # 1. Cover 'if not is_home_connectable' and 'print_conn_err'
        mock_connectable.return_value = False
        _update_prepacked_data(verbose=True)
        out, _ = capfd.readouterr()
        assert "Unable to update the data." in out

        # 2. Cover 'if not is_home_connectable' and 'verbose=False'
        mock_connectable.return_value = False
        _update_prepacked_data(verbose=False)
        out, _ = capfd.readouterr()
        assert "Unable to update the data." in out

        # 3. Cover 'if confirmed' as False
        mock_connectable.return_value = True
        mock_confirmed.return_value = False
        _update_prepacked_data()
        # The 'main update' chunk is skipped here
        mock_gsm.assert_not_called()

        # 3. Cover 'if confirmed' as False
        mock_connectable.return_value = True
        mock_confirmed.return_value = True
        _update_prepacked_data()
        mock_gsm.assert_called_once()
        mock_ld.assert_called_once_with(update=True)
        mock_oa.assert_called_once_with(update=True)

    # 4. Run the main update chunk once
    _update_prepacked_data(confirmation_required=False, verbose=True)
    out, _ = capfd.readouterr()
    assert "Failed" not in out
    assert "Update finished." in out


if __name__ == '__main__':
    pytest.main()
