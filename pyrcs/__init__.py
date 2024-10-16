"""
Package initialisation.
"""

import datetime
import json
import pkgutil

from .collector import *

metadata = json.loads(pkgutil.get_data(__name__, "data/metadata").decode())

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
    'LineData',
    'OtherAssets',
    'Electrification',
    'ELRMileages',
    'LineNames',
    'LocationIdentifiers',
    'LOR',
    'TrackDiagrams',
    'Bridges',
    'Depots',
    'Features',
    'SignalBoxes',
    'Stations',
    'Tunnels',
    'Viaducts',
]
