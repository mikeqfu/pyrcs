"""
Collect data of `other assets <http://www.railwaycodes.org.uk/otherassetsmenu.shtm>`_.
"""

import urllib.parse

from pyrcs.other_assets import *
from pyrcs.utils import get_category_menu, homepage_url


class OtherAssets:
    """
    A class representation of all modules of the subpackage
    :ref:`pyrcs.other_assets<other_assets>` for collecting other assets.

    :param update: whether to check on update and proceed to update the package data,
        defaults to ``False``
    :type update: bool

    **Example**::

        >>> from pyrcs import OtherAssets

        >>> oa = OtherAssets()

        >>> # To get data of railway stations
        >>> railway_station_data = oa.Stations.fetch_railway_station_data()

        >>> type(railway_station_data)
        <class 'dict'>
        >>> print(list(railway_station_data.keys()))
        ['Railway station data', 'Last updated date']
        >>> railway_station_dat = railway_station_data['Railway station data']
        >>> print(railway_station_dat.head())
              Station   ELR   Mileage  ... Prev_Date_6 Prev_Operator_7  Prev_Date_7
        0  Abbey Wood   NKL  11m 43ch  ...         NaN             NaN          NaN
        1  Abbey Wood  XRS3  24.458km  ...         NaN             NaN          NaN
        2        Aber   CAR   8m 69ch  ...         NaN             NaN          NaN
        3   Abercynon   CAM  16m 28ch  ...         NaN             NaN          NaN
        4   Abercynon   ABD  16m 28ch  ...         NaN             NaN          NaN

        [5 rows x 25 columns]

        >>> # To get data of signal boxes
        >>> signal_boxes_data = oa.SignalBoxes.fetch_signal_box_prefix_codes()
        >>> type(signal_boxes_data)
        <class 'dict'>
        >>> print(list(signal_boxes_data.keys()))
        ['Signal boxes', 'Last updated date']
        >>> signal_boxes_dat = signal_boxes_data['Signal boxes']
        >>> print(signal_boxes_dat.head())
          Code               Signal Box  ...            Closed        Control to
        0   AF  Abbey Foregate Junction  ...
        1   AJ           Abbey Junction  ...  16 February 1992     Nuneaton (NN)
        2    R           Abbey Junction  ...  16 February 1992     Nuneaton (NN)
        3   AW               Abbey Wood  ...      13 July 1975      Dartford (D)
        4   AE         Abbey Works East  ...   1 November 1987  Port Talbot (PT)

        [5 rows x 8 columns]
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
        self.Catalogue = \
            get_category_menu(self.SourceURL, update=update, confirmation_required=False)
        # Classes
        self.SignalBoxes = sig_box.SignalBoxes(update=update)
        self.Tunnels = tunnel.Tunnels(update=update)
        self.Viaducts = viaduct.Viaducts(update=update)
        self.Stations = station.Stations(update=update)
        self.Depots = depot.Depots(update=update)
        self.Features = feature.Features(update=update)
