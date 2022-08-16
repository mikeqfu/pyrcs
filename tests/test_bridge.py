"""Test the module :py:mod:`pyrcs.line_data.bridge`."""

import pytest

from pyrcs.line_data import Bridges

bdg = Bridges()


def test_collect_codes():
    bdg_codes = bdg.collect_codes(confirmation_required=False, verbose=True)

    assert isinstance(bdg_codes, dict)


def test_fetch_codes():
    bdg_codes = bdg.fetch_codes()

    assert isinstance(bdg_codes, dict)


if __name__ == '__main__':
    pytest.main()
