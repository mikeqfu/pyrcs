"""
A sub-package of modules for collecting codes of `other assets
<http://www.railwaycodes.org.uk/otherassetsmenu.shtm>`_.

(See also :py:class:`~pyrcs.collector.OtherAssets`.)
"""

from .depot import Depots
from .feature import Features
from .sig_box import SignalBoxes
from .station import Stations
from .tunnel import Tunnels
from .viaduct import Viaducts

__all__ = [
    'sig_box', 'SignalBoxes',
    'tunnel', 'Tunnels',
    'viaduct', 'Viaducts',
    'station', 'Stations',
    'depot', 'Depots',
    'feature', 'Features',
]
