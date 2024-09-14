"""
Test the module :py:mod:`pyrcs.line_data.trk_diagr`.
"""

import pytest

from pyrcs.line_data import TrackDiagrams


class TestTrackDiagrams:

    @pytest.fixture(scope='class')
    def td(self):
        return TrackDiagrams()

    @pytest.mark.parametrize('update', [False, True])
    def test__get_items(self, td, update):
        trk_diagr_items = td._get_items(update=update, verbose=True)
        assert isinstance(trk_diagr_items, dict)

    def test_collect_catalogue(self, td):
        track_diagrams_catalog = td.collect_catalogue(confirmation_required=False, verbose=True)

        assert isinstance(track_diagrams_catalog, dict)
        assert list(track_diagrams_catalog.keys()) == ['Track diagrams', 'Last updated date']

    @pytest.mark.parametrize('update', [False, True])
    def test_fetch_catalogue(self, td, update):
        trk_diagr_cat = td.fetch_catalogue(update=update, verbose=True)

        assert isinstance(trk_diagr_cat, dict)
        assert list(trk_diagr_cat.keys()) == ['Track diagrams', 'Last updated date']


if __name__ == '__main__':
    pytest.main()
