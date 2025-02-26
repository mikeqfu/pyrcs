"""
A subpackage for collecting codes of
`other assets <http://www.railwaycodes.org.uk/otherassetsmenu.shtm>`_.

(See also the :py:class:`~pyrcs.collector.OtherAssets` class.)
"""

from .buzzer import Buzzer
from .depot import Depots
from .feature import Features
from .habd_wild import HABDWILD
from .sig_box import SignalBoxes
from .station import Stations
from .telegraph import Telegraph
from .trough import WaterTroughs
from .tunnel import Tunnels
from .viaduct import Viaducts

__all__ = [
    'buzzer', 'Buzzer',
    'depot', 'Depots',
    'feature', 'Features',
    'habd_wild', 'HABDWILD',
    'sig_box', 'SignalBoxes',
    'station', 'Stations',
    'telegraph', 'Telegraph',
    'trough', 'WaterTroughs',
    'tunnel', 'Tunnels',
    'viaduct', 'Viaducts',
]
