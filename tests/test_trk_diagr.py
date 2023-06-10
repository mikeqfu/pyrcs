"""Test the module :py:mod:`pyrcs.line_data.trk_diagr`."""

import pytest

from pyrcs.line_data import TrackDiagrams


class TestTrackDiagrams:
    td = TrackDiagrams()

    def test__get_items(self):
        trk_diagr_items = self.td._get_items(update=True, verbose=True)
        assert isinstance(trk_diagr_items, dict)

        trk_diagr_items = self.td._get_items()
        assert isinstance(trk_diagr_items, dict)

    def test_collect_catalogue(self):
        track_diagrams_catalog = self.td.collect_catalogue(confirmation_required=False, verbose=True)

        assert isinstance(track_diagrams_catalog, dict)
        assert list(track_diagrams_catalog.keys()) == ['Track diagrams', 'Last updated date']

    def test_fetch_catalogue(self):
        trk_diagr_cat = self.td.fetch_catalogue()

        assert isinstance(trk_diagr_cat, dict)
        assert list(trk_diagr_cat.keys()) == ['Track diagrams', 'Last updated date']


if __name__ == '__main__':
    pytest.main()
