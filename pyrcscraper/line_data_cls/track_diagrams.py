"""

Data source: http://www.railwaycodes.org.uk

Railway track diagrams
(Reference: http://www.railwaycodes.org.uk/track/diagrams0.shtm)

"""

import os
import urllib.parse

import bs4
import pandas as pd
import requests

from pyrcscraper.utils import cd_dat, get_last_updated_date


class TrackDiagrams:
    def __init__(self):
        self.HomeURL = 'http://www.railwaycodes.org.uk'
        self.Name = 'Railway track diagrams'
        self.URL = 'http://www.railwaycodes.org.uk/track/diagrams0.shtm'

        # Get contents
        source = requests.get(self.URL)
        soup, items = bs4.BeautifulSoup(source.text, 'lxml'), {}
        h3 = soup.find('h3', text=True, attrs={'class': None})
        while h3:
            # Description
            if h3.text == 'Miscellaneous':
                desc = [x.text for x in h3.find_next_siblings('p')]
            else:
                desc = h3.find_next_sibling('p').text.replace('\xa0', '')
            # Extract details
            cold_soup = h3.find_next('div', attrs={'class': 'columns'})
            if cold_soup:
                info = [x.text for x in cold_soup.find_all('p') if x.string != '\xa0']
                urls = [urllib.parse.urljoin(os.path.dirname(self.URL), x['href']) for x in cold_soup.find_all('a')]
            else:
                cold_soup = h3.find_next('a', attrs={'target': '_blank'})
                info, urls = [], []
                while cold_soup:
                    info.append(cold_soup.text)
                    urls.append(urllib.parse.urljoin(os.path.dirname(self.URL), cold_soup['href']))
                    if h3.text == 'Miscellaneous':
                        cold_soup = cold_soup.find_next('a')
                    else:
                        cold_soup = cold_soup.find_next_sibling('a')

            meta = pd.DataFrame(zip(info, urls), columns=['Description', 'FileURL'])
            # Update
            items.update({h3.text: (desc, meta)})
            # Move on
            h3 = h3.find_next_sibling('h3')

        self.Catalogue = items

        self.Date = get_last_updated_date(self.URL, parsed=True, date_type=False)

    # Change directory to "...dat\\Line data\\Electrification" and sub-directories
    @staticmethod
    def cdd_td(*sub_dir):
        path = cd_dat("Line data", "Track diagrams")
        for x in sub_dir:
            path = os.path.join(path, x)
        return path
