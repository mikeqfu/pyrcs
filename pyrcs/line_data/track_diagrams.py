""" Collecting British railway track diagrams.

Data source: http://www.railwaycodes.org.uk/track/diagrams0.shtm

.. todo::

   All.
"""

import copy
import os
import urllib.parse

import bs4
import pandas as pd
import requests
from pyhelpers.dir import regulate_input_data_dir

from pyrcs.utils import cd_dat, fake_requests_headers, get_last_updated_date, homepage_url


class TrackDiagrams:
    """
    A class for collecting British railway track diagrams.

    :param data_dir: name of data directory, defaults to ``None``
    :type data_dir: str, None

    **Example**::

        from pyrcs.line_data import TrackDiagrams

        td = TrackDiagrams()

        print(td.Name)
        # Railway track diagrams

        print(td.SourceURL)
        # http://www.railwaycodes.org.uk/track/diagrams0.shtm
    """

    def __init__(self, data_dir=None):
        self.Name = 'Railway track diagrams'
        self.HomeURL = homepage_url()
        self.SourceURL = self.HomeURL + '/track/diagrams0.shtm'

        # Get contents
        source = requests.get(self.SourceURL, headers=fake_requests_headers())
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
                urls = [urllib.parse.urljoin(os.path.dirname(self.SourceURL), a.get('href'))
                        for a in cold_soup.find_all('a')]
            else:
                cold_soup = h3.find_next('a', attrs={'target': '_blank'})
                info, urls = [], []
                while cold_soup:
                    info.append(cold_soup.text)
                    urls.append(urllib.parse.urljoin(os.path.dirname(self.SourceURL), cold_soup['href']))
                    cold_soup = cold_soup.find_next('a') if h3.text == 'Miscellaneous' \
                        else cold_soup.find_next_sibling('a')
            meta = pd.DataFrame(zip(info, urls), columns=['Description', 'FileURL'])
            items.update({h3.text: (desc, meta)})  # Update
            h3 = h3.find_next_sibling('h3')  # Move on

        self.Catalogue = items
        self.Date = get_last_updated_date(self.SourceURL, parsed=True, as_date_type=False)
        self.Key = 'Track diagrams'
        self.LUDKey = 'Last updated date'
        if data_dir:
            self.DataDir = regulate_input_data_dir(data_dir)
        else:
            self.DataDir = cd_dat("line-data", self.Key.lower().replace(" ", "-"))
        self.CurrentDataDir = copy.copy(self.DataDir)

    def cdd_td(self, *sub_dir):
        """
        Change directory to "dat\\line-data\\track-diagrams" and sub-directories (and/or a file)

        :param sub_dir: sub-directory or sub-directories (and/or a file)
        :type sub_dir: str
        :return: path to the backup data directory for ``LOR``
        :rtype: str

        :meta private:
        """

        path = self.DataDir
        for x in sub_dir:
            path = os.path.join(path, x)
        return path
