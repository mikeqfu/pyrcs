"""
A collection of modules for collecting `line data <http://www.railwaycodes.org.uk/linedatamenu.shtm>`_.
See also :py:class:`pyrcs.collector.LineData`.
"""

from .elec import Electrification
from .elr_mileage import ELRMileages
from .line_name import LineNames
from .loc_id import LocationIdentifiers
from .lor_code import LOR
from .trk_diagr import TrackDiagrams

__all__ = ['elec', 'Electrification',
           'elr_mileage', 'ELRMileages',
           'line_name', 'LineNames',
           'loc_id', 'LocationIdentifiers',
           'lor_code', 'LOR',
           'trk_diagr', 'TrackDiagrams']
