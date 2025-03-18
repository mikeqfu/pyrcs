"""
Package initialisation.
"""

import datetime
import json
import pkgutil

from . import collector, converter, line_data, other_assets, parser, utils
from .collector import LineData, OtherAssets
from .line_data import Bridges, ELRMileages, Electrification, LOR, LineNames, LocationIdentifiers, \
    TrackDiagrams
from .other_assets import Buzzer, Depots, Features, HabdWild, SignalBoxes, Stations, Telegraph, \
    Tunnels, Viaducts, WaterTroughs

metadata = json.loads(pkgutil.get_data(__name__, "data/.metadata").decode())

__project__ = metadata['Project']
__pkgname__ = metadata['Package']
__desc__ = metadata['Description']

__author__ = metadata['Author']
__affil__ = metadata['Affiliation']
__email__ = metadata['Email']

__version__ = metadata['Version']
__license__ = metadata['License']
__copyright__ = f'2019-{datetime.datetime.now().year}, {__author__}'

__first_release__ = metadata['First release']

__all__ = [
    'collector',
    'converter',
    'parser',
    'utils',
    'line_data',
    'other_assets',
    'LineData',
    'OtherAssets',
    'Electrification',
    'ELRMileages',
    'LineNames',
    'LocationIdentifiers',
    'LOR',
    'TrackDiagrams',
    'Bridges',
    'SignalBoxes',
    'Tunnels',
    'Viaducts',
    'Stations',
    'Depots',
    'Features',
    'HabdWild',
    'WaterTroughs',
    'Telegraph',
    'Buzzer',
]
