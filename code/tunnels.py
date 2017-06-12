""" Railway tunnel lengths """

import os
import re

import bs4
import fuzzywuzzy.process
import measurement.measures
import pandas as pd
import requests

from utils import cdd_rc_dat, get_last_updated_date, save_pickle, load_pickle, parse_tr


#
def cdd_tunnels(*directories):
    path = cdd_rc_dat("Other assets", "Railway tunnel lengths")
    for directory in directories:
        path = os.path.join(path, directory)
    return path


def get_page_headers():
    intro_url = 'http://www.railwaycodes.org.uk/tunnels/tunnels0.shtm'
    intro = requests.get(intro_url)
    pages = [x.text for x in bs4.BeautifulSoup(intro.text, 'lxml').find_all('a', text=re.compile('^Page.*'))]
    return pages


# Railway tunnel lengths (by page) ===========================================
def scrape_railway_tunnel_lengths(page_no, update=False):
    """
    :param page_no: [int] page number; valid values include 1, 2, and 3
    :param update: [bool] indicate whether to re-scrape the tunnel lengths data for the given page_no
    :return [dict] containing:
                [DataFrame] tunnel lengths data of the given 'page'
                [str] date of when the data was last updated
    """
    page_headers = get_page_headers()
    filename = fuzzywuzzy.process.extractOne(str(page_no), page_headers, score_cutoff=10)[0]

    path_to_file = cdd_tunnels("Page 1-4", filename + ".pickle")

    if os.path.isfile(path_to_file) and not update:
        tunnels = load_pickle(path_to_file)
    else:
        url = 'http://www.railwaycodes.org.uk/tunnels/tunnels{}.shtm'.format(page_no)
        last_updated_date = get_last_updated_date(url)
        source = requests.get(url)
        try:
            parsed_text = bs4.BeautifulSoup(source.text, 'lxml')  # Optional parsers:, 'html5lib', 'html.parser'

            # Column names
            header = [x.text for x in parsed_text.find_all('th')]
            if 'Between...' in header:
                header.remove('Between...')
            header += ['Station_A', 'Station_B']

            # Table data
            temp_tables = parsed_text.find_all('table', attrs={'border': 1})
            tbl_lst = parse_tr(header, trs=temp_tables[0].find_all('tr'))
            tbl_lst = [[item.replace('\r', ' ').replace('\xa0', '') for item in record] for record in tbl_lst]

            # Create a DataFrame
            tunnels = pd.DataFrame(data=tbl_lst, columns=header)

        except Exception as e:
            print("Scraping tunnel lengths data for Page {} ... failed due to '{}'".format(page_no, e))
            tunnels = None

        tunnel_keys = [s + str(page_no) for s in ('Tunnels_', 'Last_updated_date_')]
        tunnels = dict(zip(tunnel_keys, [tunnels, last_updated_date]))

        # Save the DataFrame(s)
        save_pickle(tunnels, path_to_file)

    return tunnels


# Minor lines and other odds and ends
def scrape_page4_others(update=False):
    """
    Page 4 (others) contains more than one table on the web page
    """
    page_headers = get_page_headers()
    filename = fuzzywuzzy.process.extractOne('others', page_headers, score_cutoff=10)[0]
    path_to_file = cdd_tunnels("Page 1-4", filename + ".pickle")

    if os.path.isfile(path_to_file) and not update:
        tunnels = load_pickle(path_to_file)
    else:
        url = 'http://www.railwaycodes.org.uk/tunnels/tunnels4.shtm'
        last_updated_date = get_last_updated_date(url)
        source = requests.get(url)
        try:
            parsed_text = bs4.BeautifulSoup(source.text, 'lxml')  # Optional parsers:, 'html5lib', 'html.parser'
            other_types = [x.text for x in parsed_text.find_all('h2')][2:]
            headers = []
            temp_header = parsed_text.find('table', cellpadding=1)
            while temp_header.find_next('th'):
                header = [x.text for x in temp_header.find_all('th')]
                if len(header) > 0:
                    if 'Between...' in header:
                        header.remove('Between...')
                        header += ['Station_A', 'Station_B']
                    headers.append(header)
                temp_header = temp_header.find_next('table', cellpadding=1)

            tbl_lst = parsed_text.find_all('table', attrs={'border': 1})
            tbls_lst = [parse_tr(header, x.find_all('tr')) for header, x in zip(headers, tbl_lst)]
            tbls_lst = [[[item.replace('\xa0', '') for item in record] for record in tbl] for tbl in tbls_lst]

            tunnels = [pd.DataFrame(tbl, columns=header) for tbl, header in zip(tbls_lst, headers)]

            tunnel_keys = other_types + ['Last_updated_date_4']
            tunnels = dict(zip(tunnel_keys, tunnels + [last_updated_date]))

            save_pickle(tunnels, path_to_file)

        except Exception as e:
            print("Scraping tunnel lengths data for Page 4 (others) ... failed due to '{}'".format(e))
            tunnels = None

    return tunnels


# All available data of railway tunnel lengths =======================================================================
def get_railway_tunnel_lengths(update=False):
    """
    :param update: [str] ext of file which the acquired DataFrame is saved as
    :return [tuple] containing:
                [DataFrame] railway tunnel lengths data, including the name,
                            length, owner and relative location
                [str] date of when the data was last updated
    """
    #
    path_to_file = cdd_tunnels("Railway-tunnel-lengths.pickle")
    if os.path.isfile(path_to_file) and not update:
        tunnel_lengths = load_pickle(path_to_file)
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

            tunnel_lengths = pd.DataFrame(pd.concat(tunnel_data, ignore_index=True))[list(tunnel_data[0].columns)]

            save_pickle(tunnel_lengths, path_to_file)
        except Exception as e:
            print("Getting railway tunnel lengths ... failed due to '{}'.".format(e))
            tunnel_lengths = None

    return tunnel_lengths


# Parse the Length column - convert miles/yards to metres
def parse_tunnel_length(x):
    if re.match('[Uu]nknown', x):
        length = pd.np.nan
        add_info = 'The length is unknown.'
    elif x != '':
        if re.match('^\d+m \d+yd- .*\d+m \d+yd.*]', x):
            miles0, yards0, miles, yards = re.findall('\d+', x)
            length0 = measurement.measures.Distance(mi=miles0).m + measurement.measures.Distance(yd=yards0).m
            length = measurement.measures.Distance(mi=miles).m + measurement.measures.Distance(yd=yards).m
            add_info = '-'.join([str(round(length0, 2)), str(round(length, 2))]) + ' metres'
        else:
            if re.match('\d+\.\d+km \(.*\)', x):
                miles, yards = re.findall('\d+', re.search('(?<=\()\d+.*(?=\))', x).group())
                add_info = re.search('\d+.*(?= \()', x).group()
            else:
                miles, yards = re.findall('\d+', x)
                add_info = None if not re.match('^c.*', x) else 'Approximate'
            length = measurement.measures.Distance(mi=miles).m + measurement.measures.Distance(yd=yards).m
    else:
        length = x
        add_info = None
    return length, add_info
