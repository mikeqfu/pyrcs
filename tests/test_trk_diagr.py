"""Test the module :py:mod:`pyrcs.line_data.trk_diagr`."""

import pytest

from pyrcs.line_data import TrackDiagrams

td = TrackDiagrams()


class TestTrackDiagrams:

    @staticmethod
    def test__get_items():
        trk_diagr_items = td._get_items(update=True, verbose=True)
        assert isinstance(trk_diagr_items, dict)

        trk_diagr_items = td._get_items()
        assert isinstance(trk_diagr_items, dict)

    @staticmethod
    def test_collect_catalogue():
        track_diagrams_catalog = td.collect_catalogue(confirmation_required=False, verbose=True)

        assert isinstance(track_diagrams_catalog, dict)
        assert list(track_diagrams_catalog.keys()) == ['Track diagrams', 'Last updated date']

    @staticmethod
    def test_fetch_catalogue():
        trk_diagr_cat = td.fetch_catalogue()

        assert isinstance(trk_diagr_cat, dict)
        assert list(trk_diagr_cat.keys()) == ['Track diagrams', 'Last updated date']


if __name__ == '__main__':
    pytest.main()
