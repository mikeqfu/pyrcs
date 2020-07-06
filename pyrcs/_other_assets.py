""" Other assets """

from pyrcs.other_assets import *
from utils import get_category_menu, homepage_url


class OtherAssets:
    def __init__(self):
        # Basic info
        self.Name = 'Other assets'
        self.HomeURL = homepage_url()
        self.URL = self.HomeURL + '/otherassetsmenu.shtm'
        self.Catalogue = get_category_menu(self.URL)
        # Classes
        self.SignalBoxes = signal_boxes.SignalBoxes()
        self.Tunnels = tunnels.Tunnels()
        self.Viaducts = viaducts.Viaducts()
        self.Stations = stations.Stations()
        self.Depots = depots.Depots()
        self.Features = features.Features()
