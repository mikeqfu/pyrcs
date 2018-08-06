""" Railway tunnel lengths """

import itertools
import operator
import os
import re

import bs4
import fuzzywuzzy.process
import measurement.measures
import pandas as pd
import requests

from utils import cdd, get_last_updated_date, load_pickle, parse_tr, save_pickle


# Change directory to "dat\\Other assets\\Railway tunnel lengths"
def cdd_tunnels(*directories):
    path = cdd("Other assets", "Railway tunnel lengths")
    for directory in directories:
        path = os.path.join(path, directory)
    return path


# Scrape page headers
def scrape_page_headers():
    intro_url = 'http://www.railwaycodes.org.uk/tunnels/tunnels0.shtm'
    intro_page = requests.get(intro_url)
    pages = [x.text for x in bs4.BeautifulSoup(intro_page.text, 'lxml').find_all('a', text=re.compile('^Page.*'))]
    return pages[:int(len(pages)/2)]


# Parse the Length column - convert miles/yards to metres
def parse_tunnel_length(x):
    """
    :param x:
    :return:

    Examples:
        '' or Unknown
        1m 182y; 0m111y; c0m 150y; 0m 253y without avalanche shelters
        0m 56ch
        formerly 0m236y
        0.325km (0m 356y); 0.060km ['(0m 66y)']
        0m 48yd- (['0m 58yd'])
    """

    if re.match('[Uu]nknown', x):
        length = pd.np.nan
        add_info = 'Unknown'
    elif x == '':
        length = pd.np.nan
        add_info = 'Unavailable'
    elif re.match('\d+m \d+yd-.*\d+m \d+yd.*', x):
        miles_a, yards_a, miles_b, yards_b = re.findall('\d+', x)
        length_a = measurement.measures.Distance(mi=miles_a).m + measurement.measures.Distance(yd=yards_a).m
        length_b = measurement.measures.Distance(mi=miles_b).m + measurement.measures.Distance(yd=yards_b).m
        length = (length_a + length_b) / 2
        add_info = '-'.join([str(round(length_a, 2)), str(round(length_b, 2))]) + ' metres'
    else:
        if re.match('(formerly )?c?\d+m ?\d+y?(ch)?.*', x):
            miles, yards = re.findall('\d+', x)
            if re.match('.*\d+ch$', x):
                yards = measurement.measures.Distance(chain=yards).yd
            if re.match('^c.*', x):
                add_info = 'Approximate'
            elif re.match('\d+y$', x):
                add_info = re.search('(?<=\dy).*$', x).group()
            elif re.match('^(formerly).*', x):
                add_info = 'Formerly'
            else:
                add_info = None
        elif re.match('\d+\.\d+km .*\(\d+m \d+y\).*', x):
            miles, yards = re.findall('\d+', re.search('(?<=\()\d+.*(?=\))', x).group())
            add_info = re.search('.+(?= (\[\')?\()', x).group()
        else:
            print(x)
            miles, yards = 0, 0
            add_info = ''
        length = measurement.measures.Distance(mi=miles).m + measurement.measures.Distance(yd=yards).m
    return length, add_info


# Railway tunnel lengths (by page)
def scrape_railway_tunnel_lengths(page_no, update=False):
    """
    :param page_no: [int] page number; valid values include 1, 2, and 3
    :param update: [bool] indicate whether to re-scrape the tunnel lengths data for the given page_no
    :return [dict] containing:
                [DataFrame] tunnel lengths data of the given 'page'
                [str] date of when the data was last updated
    """
    page_headers = scrape_page_headers()
    filename = fuzzywuzzy.process.extractOne(str(page_no), page_headers)[0]

    path_to_file = cdd_tunnels("Page 1-4", filename + ".pickle")

    if os.path.isfile(path_to_file) and not update:
        tunnels_data = load_pickle(path_to_file)
    else:
        url = 'http://www.railwaycodes.org.uk/tunnels/tunnels{}.shtm'.format(page_no)
        last_updated_date = get_last_updated_date(url)
        source = requests.get(url)
        try:
            parsed_text = bs4.BeautifulSoup(source.text, 'lxml')  # Optional parsers:, 'html5lib', 'html.parser'

            # Column names
            header = [x.text for x in parsed_text.find_all('th')]

            crossed = [re.match('^Between.*', x) for x in header]
            if any(crossed):
                idx = list(itertools.compress(range(len(crossed)), crossed))
                assert len(idx) == 1
                header.remove(header[idx[0]])
                header[idx[0]:idx[0]] = ['Station_O', 'Station_D']

            # Table data
            temp_tables = parsed_text.find_all('table', attrs={'width': '1100px'})
            tbl_lst = parse_tr(header, trs=temp_tables[1].find_all('tr'))
            tbl_lst = [[item.replace('\r', ' ').replace('\xa0', '') for item in record] for record in tbl_lst]

            # Create a DataFrame
            tunnels = pd.DataFrame(data=tbl_lst, columns=header)
            tunnels[['Length_m', 'Length_note']] = tunnels.Length.map(parse_tunnel_length).apply(pd.Series)

            tunnels_keys = [s + str(page_no) for s in ('Tunnels_', 'Last_updated_date_')]
            tunnels_data = dict(zip(tunnels_keys, [tunnels, last_updated_date]))

            # Save the DataFrame(s)
            save_pickle(tunnels_data, path_to_file)

        except Exception as e:
            print("Scraping tunnel lengths data for Page {} ... failed due to '{}'".format(page_no, e))
            tunnels_data = None

    return tunnels_data


# Minor lines and other odds and ends
def scrape_page4_others(update=False):
    """
    Page 4 (others) contains more than one table on the web page
    """
    page_headers = scrape_page_headers()
    filename = fuzzywuzzy.process.extractOne('others', page_headers)[0]
    path_to_file = cdd_tunnels("Page 1-4", filename + ".pickle")

    if os.path.isfile(path_to_file) and not update:
        tunnels = load_pickle(path_to_file)
    else:
        url = 'http://www.railwaycodes.org.uk/tunnels/tunnels4.shtm'
        last_updated_date = get_last_updated_date(url)
        source = requests.get(url)
        try:
            parsed_text = bs4.BeautifulSoup(source.text, 'lxml')  # Optional parsers:, 'html5lib', 'html.parser'
            other_types = [x.text for x in parsed_text.find_all('h2')]
            headers = []
            temp_header = parsed_text.find('table')
            while temp_header.find_next('th'):
                header = [x.text for x in temp_header.find_all('th')]
                if len(header) > 0:
                    crossed = [re.match('^Between.*', x) for x in header]
                    if any(crossed):
                        idx = list(itertools.compress(range(len(crossed)), crossed))
                        assert len(idx) == 1
                        header.remove(header[idx[0]])
                        header[idx[0]:idx[0]] = ['Station_O', 'Station_D']
                    headers.append(header)
                temp_header = temp_header.find_next('table')

            tbl_lst = parsed_text.find_all('table', attrs={'width': '1100px'})
            tbl_lst = operator.itemgetter(1, 3)(tbl_lst)
            tbl_lst = [parse_tr(header, x.find_all('tr')) for header, x in zip(headers, tbl_lst)]
            tbl_lst = [[[item.replace('\xa0', '') for item in record] for record in tbl] for tbl in tbl_lst]

            tunnels = [pd.DataFrame(tbl, columns=header) for tbl, header in zip(tbl_lst, headers)]
            for i in range(len(tunnels)):
                tunnels[i][['Length_m', 'Length_note']] = tunnels[i].Length.map(parse_tunnel_length).apply(pd.Series)

            tunnel_keys = other_types + ['Last_updated_date_4']
            tunnels = dict(zip(tunnel_keys, tunnels + [last_updated_date]))

            save_pickle(tunnels, path_to_file)

        except Exception as e:
            print("Scraping tunnel lengths data for Page 4 (others) ... failed due to '{}'".format(e))
            tunnels = None

    return tunnels


# All available data of railway tunnel lengths
def get_railway_tunnel_lengths(update=False):
    """
    :param update: [str] ext of file which the acquired DataFrame is saved as
    :return [tuple] containing:
                [DataFrame] railway tunnel lengths data, including the name,
                            length, owner and relative location
                [str] date of when the data was last updated
    """
    #
    pickle_filename = "Railway-tunnel-lengths.pickle"
    path_to_pickle = cdd_tunnels(pickle_filename)

    if os.path.isfile(path_to_pickle) and not update:
        tunnel_lengths = load_pickle(path_to_pickle)
    else:
        try:
            data = [scrape_railway_tunnel_lengths(page_no, update) for page_no in range(1, 4)]
            others = scrape_page4_others(update)

            tunnel_data = [dat[k] for dat in data for k, v in dat.items() if re.match('^Tunnels.*', k)]
            other_data = [v for k, v in others.items() if not k.startswith('Last_updated_date')]
            tunnel_data += other_data

            last_updated_dates = [dat[k] for dat in data for k, v in dat.items() if re.match('^Last_updated_date.*', k)]
            other_last_updated_date = others['Last_updated_date_4']
            last_updated_dates.append(other_last_updated_date)

            tunnel_lengths = pd.concat(tunnel_data, ignore_index=True, sort=False)[list(tunnel_data[0].columns)]

            save_pickle({'Tunnels': tunnel_lengths, 'Last_updated_date': max(last_updated_dates)}, path_to_pickle)

        except Exception as e:
            print("Getting railway tunnel lengths ... failed due to '{}'.".format(e))
            tunnel_lengths = None

    return tunnel_lengths
