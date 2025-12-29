"""
Test the module :py:mod:`pyrcs.collector`.
"""

import unittest.mock

import pytest

from pyrcs.collector import LineData, OtherAssets, _Base


class TestCollectorBase:

    def test_init(self, monkeypatch):
        mock_warning = unittest.mock.MagicMock()

        monkeypatch.setattr('pyrcs.collector.is_homepage_connectable', lambda: False)
        monkeypatch.setattr('pyrcs.collector.print_connection_warning', mock_warning)
        monkeypatch.setattr('pyrcs.collector.get_category_menu', lambda *a, **k: {})
        _Base(verbose=True, raise_error=True)
        mock_warning.assert_called_once_with(verbose=True)


def test_line_data_update_no_connection(monkeypatch, capfd):
    # 1. Mock the connection check to return False
    # Note: Patch this in the module where _Base is defined
    monkeypatch.setattr('pyrcs.collector.is_homepage_connectable', lambda: False)

    # 2. Mock get_category_menu (called in _Base.__init__)
    monkeypatch.setattr('pyrcs.collector.get_category_menu', lambda *a, **k: {})

    # 3. Mock the sub-classes to prevent them from initializing fully
    # This keeps the test focused only on LineData.update()
    def mock_class(**_kwargs):
        return None

    monkeypatch.setattr('pyrcs.collector.ELRMileages', mock_class)
    monkeypatch.setattr('pyrcs.collector.Electrification', mock_class)
    monkeypatch.setattr('pyrcs.collector.LocationIdentifiers', mock_class)
    monkeypatch.setattr('pyrcs.collector.LOR', mock_class)
    monkeypatch.setattr('pyrcs.collector.LineNames', mock_class)
    monkeypatch.setattr('pyrcs.collector.TrackDiagrams', mock_class)
    monkeypatch.setattr('pyrcs.collector.Bridges', mock_class)

    # 4. Initialize LineData
    # Because is_homepage_connectable is False, self.connected will be False
    ld = LineData()
    assert ld.connected is False

    # 5. Call update()
    # This should trigger the 'if not self.connected' block
    ld.update(verbose=True)

    # 6. Verify the error message was printed
    out, _ = capfd.readouterr()
    assert "The Internet connection is not available" in out


def test_other_assets_update_no_connection(monkeypatch, capfd):
    # 1. Mock the connection check to return False
    # Note: Patch this in the module where _Base is defined
    monkeypatch.setattr('pyrcs.collector.is_homepage_connectable', lambda: False)

    # 2. Mock get_category_menu (called in _Base.__init__)
    monkeypatch.setattr('pyrcs.collector.get_category_menu', lambda *a, **k: {})

    # 3. Mock the sub-classes to prevent them from initialising fully
    # This keeps the test focused only on OtherAssets.update()
    def mock_class(**_kwargs):
        return None

    monkeypatch.setattr('pyrcs.collector.SignalBoxes', mock_class)
    monkeypatch.setattr('pyrcs.collector.Tunnels', mock_class)
    monkeypatch.setattr('pyrcs.collector.Viaducts', mock_class)
    monkeypatch.setattr('pyrcs.collector.Stations', mock_class)
    monkeypatch.setattr('pyrcs.collector.Depots', mock_class)
    monkeypatch.setattr('pyrcs.collector.HabdWild', mock_class)
    monkeypatch.setattr('pyrcs.collector.WaterTroughs', mock_class)
    monkeypatch.setattr('pyrcs.collector.Telegraph', mock_class)
    monkeypatch.setattr('pyrcs.collector.Buzzer', mock_class)
    monkeypatch.setattr('pyrcs.collector.Features', mock_class)

    # 4. Initialize LineData
    # Because is_homepage_connectable is False, self.connected will be False
    oa = OtherAssets()
    assert oa.connected is False

    # 5. Call update()
    # This should trigger the 'if not self.connected' block
    oa.update(verbose=True)

    # 6. Verify the error message was printed
    out, _ = capfd.readouterr()
    assert "The Internet connection is not available" in out


if __name__ == '__main__':
    pytest.main()
