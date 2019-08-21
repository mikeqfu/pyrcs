#
import os
import urllib.parse

import bs4
import requests

from pyrcs.other_assets_cls import depots, signal_boxes, stations, tunnels, viaducts


class OtherAssets:
    def __init__(self):
        self.Name = 'Other assets'
        self.URL = 'http://www.railwaycodes.org.uk/otherassetsmenu.shtm'
        self.HomeURL = os.path.split(self.URL)[0]

        source = requests.get(self.URL)
        soup = bs4.BeautifulSoup(source.text, 'lxml').find_all('a', text=True)[-6:]
        contents = [{x.text: urllib.parse.urljoin(self.HomeURL, x['href'])} for x in soup]
        self.contents = dict(e for d in contents for e in d.items())

        self.SignalBoxes = signal_boxes.SignalBoxes()
        self.Tunnels = tunnels.Tunnels()
        self.Viaducts = viaducts.Viaducts()
        self.Stations = stations.Stations()
        self.Depots = depots.Depots()
