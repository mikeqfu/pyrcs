"""
A collection of modules for collecting
`line data <http://www.railwaycodes.org.uk/linedatamenu.shtm>`_. See also
:py:mod:`pyrcs._line_data<pyrcs._line_data>`.
"""

from .elec import Electrification
from .elr_mileage import ELRMileages
from .line_name import LineNames
from .loc_id import LocationIdentifiers
from .lor_code import LOR
from .trk_diagr import TrackDiagrams

__all__ = ['loc_id', 'elec', 'elr_mileage', 'line_name', 'lor_code', 'trk_diagr',
           'LocationIdentifiers', 'Electrification', 'ELRMileages', 'LineNames',
           'LOR', 'TrackDiagrams']
