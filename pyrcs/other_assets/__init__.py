"""
A collection of modules for collecting
`other assets <http://www.railwaycodes.org.uk/otherassetsmenu.shtm>`_. See also
:py:mod:`pyrcs._other_assets<pyrcs._other_assets>`.
"""

from .depot import Depots
from .feature import Features
from .sig_box import SignalBoxes
from .station import Stations
from .tunnel import Tunnels
from .viaduct import Viaducts


__all__ = ['depot', 'feature', 'sig_box', 'station', 'tunnel', 'viaduct',
           'Depots', 'Features', 'SignalBoxes', 'Stations', 'Tunnels', 'Viaducts']
