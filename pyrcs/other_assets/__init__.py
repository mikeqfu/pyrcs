"""
A collection of modules for collecting
`other assets <http://www.railwaycodes.org.uk/otherassetsmenu.shtm>`_.
See also :py:class:`pyrcs.collector.OtherAssets`.
"""

from .depot import Depots
from .feature import Features
from .sig_box import SignalBoxes
from .station import Stations
from .tunnel import Tunnels
from .viaduct import Viaducts

__all__ = ['depot', 'Depots',
           'feature', 'Features',
           'sig_box', 'SignalBoxes',
           'station', 'Stations',
           'tunnel', 'Tunnels',
           'viaduct', 'Viaducts']
