""" Collecting data of other assets """

import urllib.parse

from .other_assets import *
from .utils import get_category_menu, homepage_url


class OtherAssets:
    """

    :param update: whether to check on update and proceed to update the package data, defaults to ``False``
    :type update: bool

    **Example**::

        from pyrcs import OtherAssets

        oa = OtherAssets()

        # To get railway station data
        stations = oa.Stations

        # data of railway stations whose names start with 'A'
        railway_station_data_a = stations.collect_railway_station_data_by_initial('A')
    """

    def __init__(self, update=False):
        """
        Constructor method.
        """
        # Basic info
        self.Name = 'Other assets'
        self.HomeURL = homepage_url()
        self.SourceURL = urllib.parse.urljoin(
            self.HomeURL, '{}menu.shtm'.format(self.Name.lower().replace(' ', '')))
        self.Catalogue = get_category_menu(self.SourceURL, update=update, confirmation_required=False)
        # Classes
        self.SignalBoxes = signal_boxes.SignalBoxes(update=update)
        self.Tunnels = tunnels.Tunnels(update=update)
        self.Viaducts = viaducts.Viaducts(update=update)
        self.Stations = stations.Stations(update=update)
        self.Depots = depots.Depots(update=update)
        self.Features = features.Features(update=update)
