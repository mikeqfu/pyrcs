"""
A sub-package of modules for collecting codes of
`line data <http://www.railwaycodes.org.uk/linedatamenu.shtm>`_.

See also :py:class:`~pyrcs.collector.LineData`.
"""

from .bridge import Bridges
from .elec import Electrification
from .elr_mileage import ELRMileages
from .line_name import LineNames
from .loc_id import LocationIdentifiers
from .lor_code import LOR
from .trk_diagr import TrackDiagrams

__all__ = [
    'elr_mileage', 'ELRMileages',
    'elec', 'Electrification',
    'loc_id', 'LocationIdentifiers',
    'lor_code', 'LOR',
    'line_name', 'LineNames',
    'trk_diagr', 'TrackDiagrams',
    'bridge', 'Bridges',
]
