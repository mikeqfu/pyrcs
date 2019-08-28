""" Utilities - Helper functions """

import collections
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
import rapidjson
import requests

# ====================================================================================================================
""" Change directory """


# Change directory to "dat" and sub-directories
def cd_dat(*sub_dir, dat_dir="dat", mkdir=False):
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
    :param verbose: [bool]
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
    :param verbose: [bool]
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
def mile_chain_to_nr_mileage(miles_chains):
    """
    :param miles_chains: [str] 'miles.chains'
    :return: [str] 'miles.yards'

    Note on the 'ELRs and mileages' web page that 'mileages' are given in the form 'miles.chains'.
    """

    if pd.notna(miles_chains) and miles_chains != '':
        miles, chains = str(miles_chains).split('.')
        yards = measurement.measures.Distance(chain=chains).yd
        network_rail_mileage = '%.4f' % (int(miles) + round(yards / (10 ** 4), 4))
    else:
        network_rail_mileage = miles_chains
    return network_rail_mileage


# Convert Network Rail mileages to "miles.chains"
def nr_mileage_to_mile_chain(str_mileage):
    """
    :param str_mileage: [str] 'miles.yards'
    :return: [str] 'miles.chains'

    Note on the 'ELRs and mileages' web page that 'mileages' are given in the form 'miles.chains'.
    """

    if pd.notna(str_mileage) and str_mileage != '':
        miles, yards = str(str_mileage).split('.')
        chains = measurement.measures.Distance(yard=yards).chain
        miles_chains = '%.2f' % (int(miles) + round(chains / (10 ** 2), 2))
    else:
        miles_chains = str_mileage
    return miles_chains


# Convert str type mileage to numerical type
def str_to_num_mileage(str_mileage):
    return '' if str_mileage == '' else round(float(str_mileage), 4)


# Convert mileage to str type
def nr_mileage_num_to_str(x):
    return '%.4f' % round(float(x), 4)


# Convert yards to Network Rail mileages
def yards_to_nr_mileage(yards):
    if not pd.isnull(yards) and yards is not None:
        mileage_mi = np.floor(measurement.measures.Distance(yd=yards).mi)
        mileage_yd = int(yards - measurement.measures.Distance(mi=mileage_mi).yd)
        # Example: "%.2f" % round(2606.89579999999, 2)
        mileage = str('%.4f' % round((mileage_mi + mileage_yd / (10 ** 4)), 4))
        return mileage


# Convert Network Rail mileages to yards
def nr_mileage_to_yards(nr_mileage):
    if isinstance(nr_mileage, float):
        nr_mileage = str('%.4f' % nr_mileage)
    elif isinstance(nr_mileage, str):
        pass
    miles = int(nr_mileage.split('.')[0])
    yards = int(nr_mileage.split('.')[1])
    yards += measurement.measures.Distance(mi=miles).yd
    return yards


# Convert calendar year to Network Rail financial year
def year_to_financial_year(date):
    financial_date = date + pd.DateOffset(months=-3)
    return financial_date.year


# ====================================================================================================================
""" Parser """


# Get a list of parsed HTML tr's
def parse_tr(header, trs):
    """
    :param header: [list] list of column names of a requested table
    :param trs: [list] contents under tr tags of the web page
    :return: [list] list of lists each comprising a row of the requested table

    Get a list of parsed contents of tr-tag's, each of which corresponds to a piece of record
    *This is a key function to drive its following functions
    Reference: stackoverflow.com/questions/28763891/what-should-i-do-when-tr-has-rowspan

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
def parse_table(source, parser='lxml'):
    """
    :param source: response object to connecting a URL to request a table
    :param parser: [str] Optional parsers: 'lxml', 'html5lib', 'html.parser'
    :return [tuple] ([list] of lists each comprising a row of the requested table - (see also parse_trs())
                     [list] of column names of the requested table)
    """
    # (If source.status_code == 200, the requested URL is available.)
    # Get plain text from the source URL
    web_page_text = source.text
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
def parse_location_note(x_note):
    # Data
    # d = re.search('[\w ,]+(?=[ \n]\[)', x)
    # if d is not None:
    #     dat = d.group()
    # else:

    # Location name
    d = re.search(r'.*(?= \[[\"\']\()', x_note)
    if d is not None:
        dat = d.group()
    elif ' [unknown feature, labelled "do not use"]' in x_note:
        dat = re.search(r'\w+(?= \[unknown feature, )', x_note).group()
    elif ') [formerly' in x_note:
        dat = re.search(r'.*(?= \[formerly)', x_note).group()
    else:
        m_pattern = re.compile(
            r'[Oo]riginally |[Ff]ormerly |[Ll]ater |[Pp]resumed | \(was | \(in | \(at | \(also |'
            r' \(second code |\?|\n| \(\[\'| \(definition unknown\)')
        # dat = re.search('["\w ,]+(?= [[(?\'])|["\w ,]+', x).group(0) if re.search(m_pattern, x) else x
        x_tmp = re.search(r'(?=[\[(]).*(?<=[\])])|(?=\().*(?<=\) \[)', x_note)
        x_tmp = x_tmp.group() if x_tmp is not None else x_note
        dat = ' '.join(x_note.replace(x_tmp, '').split()) if re.search(m_pattern, x_note) else x_note

    # Note
    y = x_note.replace(dat, '').strip()
    if y == '':
        note = ''
    else:
        n = re.search(r'(?<=[\[(])[\w ,?]+(?=[])])', y)
        # n = re.search('(?<=[\n ]((\[\'\()|(\(\[\')))[\w ,\'\"/?]+', y)
        if n is None:
            n = re.search(r'(?<=(\[[\'\"]\()|(\([\'\"]\[)|(\) \[)).*(?=(\)[\'\"]\])|(\][\'\"]\))|\])', y)
        elif '"now deleted"' in y and y.startswith('(') and y.endswith(')'):
            n = re.search(r'(?<=\().*(?=\))', y)
        note = n.group() if n is not None else ''
        if note.endswith('\'') or note.endswith('"'):
            note = note[:-1]

    if 'STANOX ' in dat and 'STANOX ' in x_note and note == '':
        dat = x_note[0:x_note.find('STANOX')].strip()
        note = x_note[x_note.find('STANOX'):]

    return dat, note


# Parse date string
def parse_date(str_date, as_date_type=False):
    """
    :param str_date: [str]
    :param as_date_type: [bool]
    :return: the date formatted as requested
    """
    parsed_date = dateutil.parser.parse(str_date, fuzzy=True)
    # Or, parsed_date = datetime.strptime(last_update_date[12:], '%d %B %Y')
    parsed_date = parsed_date.date() if as_date_type else str(parsed_date.date())
    return parsed_date


# ====================================================================================================================
""" Get useful information """


# Get last update date
def get_last_updated_date(url, parsed=True, date_type=False):
    """
    :param url: [str] URL link of a requested web page
    :param parsed: [bool] indicator of whether to reformat the date
    :param date_type: [bool]
    :return:[str] date of when the specified web page was last updated
    """
    # Request to get connected to the given url
    source = requests.get(url)
    web_page_text = source.text
    # Parse the text scraped from the requested web page
    # (Optional parsers: 'lxml', 'html5lib' and 'html.parser')
    parsed_text = bs4.BeautifulSoup(web_page_text, 'lxml')
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


#
def get_navigation_elements(lst):
    """
    :param lst: [list]
    :return:
    """
    assert isinstance(lst, list)
    lst_reversed = list(reversed(lst))
    for x in lst_reversed:
        if x.text == 'Introduction':
            starting_idx = len(lst) - lst_reversed.index(x) - 1
            return lst[starting_idx:]


#
def get_catalogue(url, navigation_bar_exists=True, menu_exists=True):
    """
    :param url: [str]
    :param navigation_bar_exists: [bool]
    :param menu_exists: [bool]
    :return:
    """

    source = requests.get(url)

    if navigation_bar_exists:
        cold_soup = bs4.BeautifulSoup(source.text, 'lxml').find_all('a', text=True, attrs={'class': None})
        hot_soup = get_navigation_elements(cold_soup)
    else:
        if menu_exists:
            hot_soup = bs4.BeautifulSoup(source.text, 'lxml').find_all('a', text=True, attrs={'class': None})[-6:]
        else:
            hot_soup = []

    source.close()

    raw_contents = [{x.text: urllib.parse.urljoin(os.path.dirname(url) + '/', x['href'])} for x in hot_soup]

    contents = dict(e for d in raw_contents for e in d.items())

    return contents


#
def get_cls_menu(cls_url):
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
""" Misc """


#
def is_float(text):
    try:
        float(text)  # float(re.sub('[()~]', '', text))
        test_res = True
    except ValueError:
        test_res = False
    return test_res
