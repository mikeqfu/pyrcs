""" Utilities - Helper functions """

import collections
import datetime
import os
import pickle
import re
import urllib.parse

import bs4
import dateutil.parser
import measurement.measures
import numpy as np
import pandas as pd
import pkg_resources
import pyhelpers.ops
import pyhelpers.store
import rapidjson
import requests

# ====================================================================================================================
""" Change directory """


# Change directory to "dat" and sub-directories
def cd_dat(*sub_dir, dat_dir="dat", mkdir=False) -> str:
    """
    :param sub_dir: [str]
    :param dat_dir: [str] (default: "dat")
    :param mkdir: [bool] (default: False)
    :return: [str]
    """
    path = pkg_resources.resource_filename(__name__, dat_dir)
    for x in sub_dir:
        path = os.path.join(path, x)
    if mkdir:
        os.makedirs(path, exist_ok=True)
    return path


# ====================================================================================================================
""" Save data """


# Save Pickle file
def save_pickle(pickle_data, path_to_pickle, verbose=True):
    """
    :param pickle_data: any object that could be dumped by the 'pickle' package
    :param path_to_pickle: [str] local file path
    :param verbose: [bool] (default: True)
    :return: whether the data has been successfully saved
    """
    pickle_filename = os.path.basename(path_to_pickle)
    pickle_dir = os.path.basename(os.path.dirname(path_to_pickle))
    pickle_dir_parent = os.path.basename(os.path.dirname(os.path.dirname(path_to_pickle)))

    if verbose:
        print("{} \"{}\" ... ".format("Updating" if os.path.isfile(path_to_pickle) else "Saving",
                                      " - ".join([pickle_dir_parent, pickle_dir, pickle_filename])), end="")

    try:
        os.makedirs(os.path.dirname(os.path.abspath(path_to_pickle)), exist_ok=True)
        pickle_out = open(path_to_pickle, 'wb')
        pickle.dump(pickle_data, pickle_out)
        pickle_out.close()
        print("Successfully.") if verbose else None
    except Exception as e:
        print("Failed. {}.".format(e))


# Save JSON file
def save_json(json_data, path_to_json, verbose=True):
    """
    :param json_data: any object that could be dumped by the 'json' package
    :param path_to_json: [str] local file path
    :param verbose: [bool] (default: True)
    :return: whether the data has been successfully saved
    """
    json_filename = os.path.basename(path_to_json)
    json_dir = os.path.basename(os.path.dirname(path_to_json))
    json_dir_parent = os.path.basename(os.path.dirname(os.path.dirname(path_to_json)))

    print("{} \"{}\" ... ".format("Updating" if os.path.isfile(path_to_json) else "Saving",
                                  " - ".join([json_dir_parent, json_dir, json_filename])), end="") if verbose else None
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path_to_json)), exist_ok=True)
        json_out = open(path_to_json, 'w')
        rapidjson.dump(json_data, json_out)
        json_out.close()
        print("Successfully.") if verbose else None
    except Exception as e:
        print("Failed. {}.".format(e))


# ====================================================================================================================
""" Converter """


# Convert "miles.chains" to Network Rail mileages
def mile_chain_to_nr_mileage(miles_chains) -> str:
    """
    :param miles_chains: [str; np.nan; None] 'miles.chains'
    :return: [str] 'miles.yards'

    Note on the 'ELRs and mileages' web page that 'mileages' are given in the form 'miles.chains'.

    Testing e.g.
        miles_chains = '0.18'  # AAM 0.18 Tewkesbury Junction with ANZ (84.62)
        mile_chain_to_nr_mileage(miles_chains)  # '0.0396'
        miles_chains = ''  # np.nan  # None
        mile_chain_to_nr_mileage(miles_chains)  # ''
    """
    if pd.notna(miles_chains) and miles_chains != '':
        miles, chains = str(miles_chains).split('.')
        yards = measurement.measures.Distance(chain=chains).yd
        network_rail_mileage = '%.4f' % (int(miles) + round(yards / (10 ** 4), 4))
    else:
        network_rail_mileage = ''
    return network_rail_mileage


# Convert Network Rail mileages to "miles.chains"
def nr_mileage_to_mile_chain(str_mileage) -> str:
    """
    :param str_mileage: [str; np.nan; None] 'miles.yards'
    :return: [str] 'miles.chains'

    Note on the 'ELRs and mileages' web page that 'mileages' are given in the form 'miles.chains'.

    Testing e.g.
        str_mileage = '0.0396'
        nr_mileage_to_mile_chain(str_mileage)  # '0.18'
        str_mileage = ''  # np.nan  # None
        nr_mileage_to_mile_chain(str_mileage)  # ''
    """
    if pd.notna(str_mileage) and str_mileage != '':
        miles, yards = str(str_mileage).split('.')
        chains = measurement.measures.Distance(yard=yards).chain
        miles_chains = '%.2f' % (int(miles) + round(chains / (10 ** 2), 2))
    else:
        miles_chains = ''
    return miles_chains


# Convert str type Network Rail mileage to numerical type
def nr_mileage_str_to_num(str_mileage: str) -> float:
    """
    Testing e.g.
        str_mileage = '0.0396'
        nr_mileage_str_to_num(str_mileage)  # 0.0396
        str_mileage = ''
        nr_mileage_str_to_num(str_mileage)  # np.nan
    """
    num_mileage = np.nan if str_mileage == '' else round(float(str_mileage), 4)
    return num_mileage


# Convert Network Rail mileage to str type
def nr_mileage_num_to_str(num_mileage: float) -> str:
    """
    Testing e.g.
        num_mileage = 0.0396
        nr_mileage_num_to_str(num_mileage)  # '0.0396'
        num_mileage = np.nan
        nr_mileage_num_to_str(num_mileage)  # ''
    """
    nr_mileage = '%.4f' % round(float(num_mileage), 4) if num_mileage and pd.notna(num_mileage) else ''
    return nr_mileage


# Convert Network Rail mileages to yards
def nr_mileage_to_yards(nr_mileage: (float, str)) -> int:
    """
    Testing e.g.
        nr_mileage = '0.0396'
        nr_mileage_to_yards(nr_mileage)  # 396
        nr_mileage = 0.0396
        nr_mileage_to_yards(nr_mileage)  # 396
    """
    if isinstance(nr_mileage, (float, np.float, int, np.integer)):
        nr_mileage = nr_mileage_num_to_str(nr_mileage)
    else:
        pass
    miles = int(nr_mileage.split('.')[0])
    yards = int(nr_mileage.split('.')[1])
    yards += int(measurement.measures.Distance(mi=miles).yd)
    return yards


# Convert yards to Network Rail mileages
def yards_to_nr_mileage(yards: (int, float, np.nan)) -> str:
    """
    Testing e.g.
        yards = 396
        yards_to_nr_mileage(yards)  # '0.0396'
        yards = 396.0
        yards_to_nr_mileage(yards)  # '0.0396'
        yards = None  # np.nan
        yards_to_nr_mileage(yards)  # ''
    """
    if pd.notnull(yards) and yards != '':
        mileage_mi = np.floor(measurement.measures.Distance(yd=yards).mi)
        mileage_yd = yards - int(measurement.measures.Distance(mi=mileage_mi).yd)
        # Example: "%.2f" % round(2606.89579999999, 2)
        mileage = str('%.4f' % round((mileage_mi + mileage_yd / (10 ** 4)), 4))
    else:
        mileage = ''
    return mileage


# For a location x where (start_mileage_num == end_mileage_num), consider a section [x - shift_yards, x + shift_yards]
def shift_num_nr_mileage(nr_mileage: (float, int, str), shift_yards: (int, float)) -> float:
    """
    :param nr_mileage: [float]
    :param shift_yards: [int]
    :return: [float]

    Testing e.g.
        nr_mileage  = '0.0396'  # 0.0396  # 10
        shift_yards = 220  # 220.99
        shift_num_mileage(nr_mileage, shift_yards)  # 0.0616  # 0.0617
    """
    yards = nr_mileage_to_yards(nr_mileage) + shift_yards
    shifted_nr_mileage = yards_to_nr_mileage(yards)
    shifted_num_mileage = nr_mileage_str_to_num(shifted_nr_mileage)
    return shifted_num_mileage


# Convert calendar year to Network Rail financial year
def year_to_financial_year(date: datetime.datetime) -> int:
    """
    Testing e.g.
        date = datetime.datetime.now()
        year_to_financial_year(date)
    """
    financial_date = date + pd.DateOffset(months=-3)
    return financial_date.year


# ====================================================================================================================
""" Parser """


# Get a list of parsed HTML tr's
def parse_tr(header, trs) -> list:
    """
    :param header: [list] list of column names of a requested table
    :param trs: [bs4.ResultSet - list of bs4.Tag] contents under 'tr' tags of the web page
    :return: [list] list of lists each comprising a row of the requested table

    Get a list of parsed contents of tr-tag's, each of which corresponds to a piece of record
    Reference: https://stackoverflow.com/questions/28763891/

    Testing e.g.
        source = requests.get('http://www.railwaycodes.org.uk/tunnels/tunnels1.shtm')
        parsed_text = bs4.BeautifulSoup(source.text, 'lxml')
        header = [x.text for x in parsed_text.find_all('th')]  # Column names
        trs = parsed_text.find_all('table', attrs={'width': '1100px'})[1].find_all('tr')
        parse_tr(header, trs)
    """
    tbl_lst = []
    for row in trs:
        data = []
        for dat in row.find_all('td'):
            txt = dat.get_text()
            if '\n' in txt:
                t = txt.split('\n')
                txt = '%s (%s)' % (t[0], t[1:]) if '(' not in txt and ')' not in txt else '%s %s' % (t[0], t[1:])
                data.append(txt)
            else:
                data.append(txt)
        tbl_lst.append(data)

    row_spanned = []
    for no, tr in enumerate(trs):
        for td_no, rho in enumerate(tr.find_all('td')):
            # print(data.has_attr("rowspan"))
            if rho.has_attr('rowspan'):
                row_spanned.append((no, int(rho['rowspan']), td_no, rho.text))

    if row_spanned:
        d = collections.defaultdict(list)
        for k, *v in row_spanned:
            d[k].append(v)
        row_spanned = list(d.items())

        for x in row_spanned:
            i, to_repeat = x[0], x[1]
            for y in to_repeat:
                for j in range(1, y[0]):
                    if y[2] in tbl_lst[i] and y[2] != '\xa0':
                        y[1] += pd.np.abs(tbl_lst[i].index(y[2]) - y[1])
                    tbl_lst[i + j].insert(y[1], y[2])

    # if row_spanned:
    #     for x in row_spanned:
    #         for j in range(1, x[2]):
    #             # Add value in next tr
    #             idx = x[0] + j
    #             # assert isinstance(idx, int)
    #             if x[1] >= len(tbl_lst[idx]):
    #                 tbl_lst[idx].insert(x[1], x[3])
    #             elif x[3] in tbl_lst[x[0]]:
    #                 tbl_lst[idx].insert(tbl_lst[x[0]].index(x[3]), x[3])
    #             else:
    #                 tbl_lst[idx].insert(x[1] + 1, x[3])

    for k in range(len(tbl_lst)):
        n = len(header) - len(tbl_lst[k])
        if n > 0:
            tbl_lst[k].extend(['\xa0'] * n)
        elif n < 0 and tbl_lst[k][2] == '\xa0':
            del tbl_lst[k][2]

    return tbl_lst


# Parse the acquired list to make it be ready for creating the DataFrame
def parse_table(source, parser='lxml') -> tuple:
    """
    :param source: [requests.Response] response object to connecting a URL to request a table
    :param parser: [str] (default: 'lxml'; alternatives: 'html5lib', 'html.parser')
    :return [tuple] ([list] of lists each comprising a row of the requested table - (see also parse_trs())
                     [list] of column names of the requested table)

    Testing e.g.
        source = requests.get('http://www.railwaycodes.org.uk/tunnels/tunnels1.shtm')
        parser = 'lxml'
        parse_table(source, parser='lxml')
    """
    # Get plain text from the source URL
    web_page_text = source.text  # (If source.status_code == 200, the requested URL is available.)
    # Parse the text
    parsed_text = bs4.BeautifulSoup(web_page_text, parser)
    # Get all data under the HTML label 'tr'
    table_temp = parsed_text.find_all('tr')
    # Get a list of column names for output DataFrame
    headers = table_temp[0]
    header = [header.text for header in headers.find_all('th')]
    # Get a list of lists, each of which corresponds to a piece of record
    trs = table_temp[1:]
    # Return a list of parsed tr's, each of which corresponds to one df row
    return parse_tr(header, trs), header


# Parse location note
def parse_location_note(location_dat) -> tuple:
    """
    :param location_dat: [str; None]
    :return: [tuple] ([str] - Location name, [str] - Note)

    Testing e.g.
        location_dat = 'Abbey Wood'
        parse_location_note(location_dat)
        location_dat = 'Abercynon (formerly Abercynon South)'
        parse_location_note(location_dat)
        location_dat = 'Allerton (reopened as Liverpool South Parkway)'
        parse_location_note(location_dat)
        location_dat = 'Ashford International [domestic portion]'
        parse_location_note(location_dat)
    """
    # Location name
    d = re.search(r'.*(?= \[[\"\']\()', location_dat)
    if d is not None:
        dat = d.group()
    elif ' [unknown feature, labelled "do not use"]' in location_dat:
        dat = re.search(r'\w+(?= \[unknown feature, )', location_dat).group()
    elif ') [formerly' in location_dat:
        dat = re.search(r'.*(?= \[formerly)', location_dat).group()
    else:
        m_pattern = re.compile(
            r'[Oo]riginally |[Ff]ormerly |[Ll]ater |[Pp]resumed | \(was | \(in | \(at | \(also |'
            r' \(second code |\?|\n| \(\[\'| \(definition unknown\)| \(reopened |( portion])$')
        x_tmp = re.search(r'(?=[\[(]).*(?<=[\])])|(?=\().*(?<=\) \[)', location_dat)
        x_tmp = x_tmp.group() if x_tmp is not None else location_dat
        dat = ' '.join(location_dat.replace(x_tmp, '').split()) if re.search(m_pattern, location_dat) else location_dat

    # Note
    y = location_dat.replace(dat, '', 1).strip()
    if y == '':
        note = ''
    else:
        n = re.search(r'(?<=[\[(])[\w ,?]+(?=[])])', y)
        if n is None:
            n = re.search(r'(?<=(\[[\'\"]\()|(\([\'\"]\[)|(\) \[)).*(?=(\)[\'\"]\])|(\][\'\"]\))|\])', y)
        elif '"now deleted"' in y and y.startswith('(') and y.endswith(')'):
            n = re.search(r'(?<=\().*(?=\))', y)
        note = n.group() if n is not None else ''
        if note.endswith('\'') or note.endswith('"'):
            note = note[:-1]

    if 'STANOX ' in dat and 'STANOX ' in location_dat and note == '':
        dat = location_dat[0:location_dat.find('STANOX')].strip()
        note = location_dat[location_dat.find('STANOX'):]

    return dat, note


# Parse date string
def parse_date(str_date, as_date_type=False) -> (str, datetime.date):
    """
    :param str_date: [str]
    :param as_date_type: [bool] (default: False)
    :return: [str; datetime.date] the date formatted as needed

    Testing e.g.
        str_date     = '2019-01-01'
        as_date_type = True
        parse_date(str_date, as_date_type)
    """
    temp_date = dateutil.parser.parse(str_date, fuzzy=True)  # datetime.strptime(last_update_date[12:], '%d %B %Y')
    parsed_date = temp_date.date() if as_date_type else str(temp_date.date())
    return parsed_date


# ====================================================================================================================
""" Get useful information """


# Get last update date
def get_last_updated_date(url, parsed=True, date_type=False) -> (str, None):
    """
    :param url: [str] URL link of a requested web page
    :param parsed: [bool] (default: True) indicator of whether to reformat the date
    :param date_type: [bool] (default: False)
    :return:[str; None] date of when the specified web page was last updated

    Testing e.g.
        url       = 'http://www.railwaycodes.org.uk/crs/CRSa.shtm'
        url_      = 'http://www.railwaycodes.org.uk/linedatamenu.shtm'
        parsed    = True
        date_type = False
        get_last_updated_date(url, parsed, date_type)
        get_last_updated_date(url_, parsed, date_type)  # None
    """
    # Request to get connected to the given url
    source = requests.get(url)
    web_page_text = source.text
    # Parse the text scraped from the requested web page
    parsed_text = bs4.BeautifulSoup(web_page_text, 'lxml')  # (Alternative parsers: 'html5lib', 'html.parser')
    # Find 'Last update date'
    update_tag = parsed_text.find('p', {'class': 'update'})
    if update_tag is not None:
        last_update_date = update_tag.text
        # Decide whether to convert the date's format
        if parsed:
            # Convert the date to "yyyy-mm-dd" format
            last_update_date = parse_date(last_update_date, date_type)
    else:
        last_update_date = None  # print('Information not available.')
    return last_update_date


# Get the catalogue for a class
def get_catalogue(cls_url, navigation_bar_exists=True, menu_exists=True) -> dict:
    """
    :param cls_url: [str]
    :param navigation_bar_exists: [bool] (default: True)
    :param menu_exists: [bool] (default: True)
    :return: [dict] {[str] - title: [str] - URL}

    Testing e.g.
        url                   = 'http://www.railwaycodes.org.uk/crs/CRS0.shtm'
        navigation_bar_exists = True
        menu_exists           = True
        get_catalogue(url, navigation_bar_exists, menu_exists)
    """
    source = requests.get(cls_url)

    if navigation_bar_exists:
        cold_soup = bs4.BeautifulSoup(source.text, 'lxml').find_all('a', text=True, attrs={'class': None})
        lst_reversed = list(reversed(cold_soup))
        hot_soup = []
        for x in lst_reversed:
            if x.text == 'Introduction':
                starting_idx = len(cold_soup) - lst_reversed.index(x) - 1
                hot_soup = cold_soup[starting_idx:]
                break
    else:
        hot_soup = bs4.BeautifulSoup(source.text, 'lxml').find_all('a', text=True, attrs={'class': None})[-6:] \
            if menu_exists else []

    source.close()

    raw_contents = [{x.text: urllib.parse.urljoin(os.path.dirname(cls_url) + '/', x['href'])} for x in hot_soup]

    contents = dict(e for d in raw_contents for e in d.items())

    return contents


# Get a menu of the available classes
def get_cls_menu(cls_url: str) -> dict:
    """
    Testing e.g.
        cls_url = 'http://www.railwaycodes.org.uk/linedatamenu.shtm'
        get_cls_menu(cls_url)
    """
    source = requests.get(cls_url)

    soup = bs4.BeautifulSoup(source.text, 'lxml')
    h1, h2s = soup.find('h1'), soup.find_all('h2')

    cls_name = h1.text.replace(' menu', '')

    if len(h2s) == 0:
        cls_elem = dict((x.text, urllib.parse.urljoin(cls_url, x.get('href'))) for x in h1.find_all_next('a'))

    else:
        all_next = [x.replace(':', '') for x in h1.find_all_next(string=True) if x != '\n' and x != '\xa0'][2:]
        h2s_list = [x.text.replace(':', '') for x in h2s]
        all_next_a = [(x.text, urllib.parse.urljoin(cls_url, x.get('href'))) for x in h1.find_all_next('a', href=True)]

        idx = [all_next.index(x) for x in h2s_list]
        for i in idx:
            all_next_a.insert(i, all_next[i])

        cls_elem, i = {}, 0
        while i <= len(idx):
            if i == 0:
                d = dict(all_next_a[i:idx[i]])
            elif i < len(idx):
                d = {h2s_list[i-1]: dict(all_next_a[idx[i-1]+1:idx[i]])}
            else:
                d = {h2s_list[i-1]: dict(all_next_a[idx[i-1]+1:])}
            i += 1
            cls_elem.update(d)

    cls_menu = {cls_name: cls_elem}
    return cls_menu


# ====================================================================================================================
""" Rectification of location names """


# Create a dict for replace location names
def fetch_location_names_repl_dict(k=None, regex=False, as_dataframe=False) -> dict:
    """
    :param k: [str; None (default)]
    :param regex: [bool] (default: False)
    :param as_dataframe: [bool] (default: False)
    :return: [dict]

    Testing e.g.
        k            = None
        regex        = False
        as_dataframe = True
        fetch_location_names_repl_dict(k, regex, as_dataframe)
    """
    json_filename = "location-names-repl{}.json".format("" if not regex else "-regex")
    location_name_repl_dict = pyhelpers.store.load_json(cd_dat(json_filename))

    if regex:
        location_name_repl_dict = {re.compile(k): v for k, v in location_name_repl_dict.items()}

    replacement_dict = {k: location_name_repl_dict} if k else location_name_repl_dict

    if as_dataframe:
        replacement_dict = pd.DataFrame.from_dict(replacement_dict)

    return replacement_dict


# Rectify location names
def update_location_name_repl_dict(new_items, regex, verbose=False):
    """
    :param new_items: [dict]
    :param regex: [bool]
    :param verbose: [bool] (default: False)

    Testing e.g.
        new_items = {}
        regex     = False
        verbose   = True
        update_location_name_repl_dict(new_items, regex, verbose)
    """
    json_filename = "location-names-repl{}.json".format("" if not regex else "-regex")

    new_items_keys = list(new_items.keys())

    if pyhelpers.ops.confirmed("To update \"{}\" with {{\"{}\"... }}?".format(json_filename, new_items_keys[0])):
        path_to_json = cd_dat(json_filename)
        location_name_repl_dict = pyhelpers.store.load_json(path_to_json)

        if any(isinstance(k, re.Pattern) for k in new_items_keys):
            new_items = {k.pattern: v for k, v in new_items.items() if isinstance(k, re.Pattern)}

        location_name_repl_dict.update(new_items)

        save_json(location_name_repl_dict, path_to_json, verbose=verbose)
