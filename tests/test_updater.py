"""Test the module :py:mod:`pyrcs._updater`."""

import pytest


def test__updater(capfd):
    from pyrcs._updater import _update_prepacked_data

    _update_prepacked_data(confirmation_required=False, verbose=True)
    out, _ = capfd.readouterr()
    assert "Failed" not in out


if __name__ == '__main__':
    pytest.main()
