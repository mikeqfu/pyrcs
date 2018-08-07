"""

Data source: http://www.railwaycodes.org.uk

Railway viaducts (Reference: http://www.railwaycodes.org.uk/tunnels/tunnels0.shtm)

"""

import os
import re

import bs4
import fuzzywuzzy.process
import pandas as pd
import requests

from utils import cdd, get_last_updated_date, load_pickle, parse_tr, save_pickle

# ====================================================================================================================
""" Change directory """


# Change directory to "dat\\Other assets\\Railway viaducts\\"
def cdd_viaducts(*directories):
    path = cdd("Other assets", "Railway viaducts")
    for directory in directories:
        path = os.path.join(path, directory)
    return path


# ====================================================================================================================
""" Railway viaducts """


# Get the titles for each page
def get_page_titles():
    intro_url = 'http://www.railwaycodes.org.uk/viaducts/viaducts0.shtm'
    intro_page = requests.get(intro_url)
    pages = [x.text for x in bs4.BeautifulSoup(intro_page.text, 'lxml').find_all('a', text=re.compile('^Page.*'))]
    pages = pages[0:int(len(pages) / 2)]
    return pages


# Scrape viaducts data by page
def scrape_railway_viaducts(page_no, update=False):
    """
    :param page_no: [int] page number; valid values include 1, 2, 3, 4, 5, and 6
    :param update:
    :return:
    """
    page_headers = get_page_titles()
    pickle_filename = fuzzywuzzy.process.extractOne(str(page_no), page_headers)[0] + ".pickle"

    path_to_file = cdd_viaducts("Page 1-6", pickle_filename)

    if os.path.isfile(path_to_file) and not update:
        viaducts_data = load_pickle(path_to_file)
    else:
        url = 'http://www.railwaycodes.org.uk/viaducts/viaducts{}.shtm'.format(page_no)
        last_updated_date = get_last_updated_date(url)
        source = requests.get(url)

        try:
            parsed_text = bs4.BeautifulSoup(source.text, 'lxml')  # Optional parsers:, 'html5lib', 'html.parser'

            # Column names
            header = [x.text for x in parsed_text.find_all('th')]

            # Table data
            temp_tables = parsed_text.find_all('table', attrs={'width': '1100px'})
            tbl_lst = parse_tr(header, trs=temp_tables[1].find_all('tr'))
            tbl_lst = [[item.replace('\r', ' ').replace('\xa0', '') for item in record] for record in tbl_lst]

            # Create a DataFrame
            viaducts = pd.DataFrame(data=tbl_lst, columns=header)

        except Exception as e:
            print("Scraping viaducts data for Page {} ... failed due to '{}'".format(page_no, e))
            viaducts = None

        viaducts_keys = [s + str(page_no) for s in ('Viaducts_', 'Last_updated_date_')]
        viaducts_data = dict(zip(viaducts_keys, [viaducts, last_updated_date]))

        save_pickle(viaducts_data, path_to_file)

    return viaducts_data


#
def get_railway_viaducts(update=False):
    path_to_file = cdd_viaducts("Railway-viaducts.pickle")
    if os.path.isfile(path_to_file) and not update:
        viaducts_data = load_pickle(path_to_file)
    else:
        try:
            data = [scrape_railway_viaducts(page_no, update) for page_no in range(1, 7)]

            viaducts_data = [dat[k] for dat in data for k, v in dat.items() if re.match('^Viaducts.*', k)]
            last_updated_dates = [dat[k] for dat in data for k, v in dat.items() if re.match('^Last_updated_date.*', k)]

            viaducts = pd.concat(viaducts_data, ignore_index=True, sort=False)
            viaducts = viaducts[list(viaducts_data[0].columns)]
            viaducts_data = {'Viaducts': viaducts, 'Last_updated_date': max(last_updated_dates)}

            save_pickle(viaducts_data, path_to_file)

        except Exception as e:
            print("Failed to get \"viaducts\" data due to \"{}\".".format(e))
            viaducts_data = {'Viaducts': pd.DataFrame(), 'Last_updated_date': None}

    return viaducts_data
