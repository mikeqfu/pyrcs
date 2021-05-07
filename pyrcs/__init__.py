from .collector import *

__all__ = [
    'collector', 'LineData', 'OtherAssets',
    'Electrification', 'ELRMileages', 'LineNames', 'LocationIdentifiers', 'LOR', 'TrackDiagrams',
    'Depots', 'Features', 'SignalBoxes', 'Stations', 'Tunnels', 'Viaducts']

__package_name__ = 'pyrcs'
__package_name_alt__ = 'PyRCS'
__version__ = '0.2.15'
__author__ = 'Qian Fu'
__email__ = 'q.fu@bham.ac.uk'
__description__ = 'PyRCS: an open-source tool for collecting railway codes ' \
                  'used in different UK rail industry systems.'
