"""Test the module :py:mod:`pyrcs.line_data.trk_diagr`."""

import pytest

from pyrcs.line_data import TrackDiagrams

td = TrackDiagrams()


def test__get_items():
    trk_diagr_items = td._get_items(update=True, verbose=True)
    assert isinstance(trk_diagr_items, dict)

    trk_diagr_items = td._get_items()
    assert isinstance(trk_diagr_items, dict)


def test__collect_catalogue():
    track_diagrams_catalog = td._collect_catalogue(confirmation_required=False, verbose=True)

    assert isinstance(track_diagrams_catalog, dict)
    assert list(track_diagrams_catalog.keys()) == ['Track diagrams', 'Last updated date']


def test__fetch_catalogue():
    trk_diagr_cat = td._fetch_catalogue()

    assert isinstance(trk_diagr_cat, dict)
    assert list(trk_diagr_cat.keys()) == ['Track diagrams', 'Last updated date']


if __name__ == '__main__':
    pytest.main()
