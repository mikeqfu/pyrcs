""" Other assets """

from pyrcs.other_assets_cls import depots, features, signal_boxes, stations, tunnels, viaducts
from pyrcs.utils import get_cls_menu


class OtherAssets:
    def __init__(self):
        # Basic info
        self.HomeURL = 'http://www.railwaycodes.org.uk'
        self.Name = 'Other assets'
        self.URL = self.HomeURL + '/otherassetsmenu.shtm'
        self.Catalogue = get_cls_menu(self.URL)
        # Classes
        self.SignalBoxes = signal_boxes.SignalBoxes()
        self.Tunnels = tunnels.Tunnels()
        self.Viaducts = viaducts.Viaducts()
        self.Stations = stations.Stations()
        self.Depots = depots.Depots()
        self.Features = features.Features()
