""" Utilities - Helper functions """

import collections
import copy
import os
import pickle
import re
import urllib.parse

import bs4
import dateutil.parser
import measurement.measures
import pandas as pd
import pdfkit
import pkg_resources
import rapidjson
import requests


# Type to confirm whether to proceed or not
def confirmed(prompt=None, resp=False, confirmation_required=True):
    """
    Reference: http://code.activestate.com/recipes/541096-prompt-the-user-for-confirmation/

    :param prompt: [str] or None
    :param resp: [bool]
    :param confirmation_required: [bool]
    :return:

    Example: confirm(prompt="Create Directory?", resp=True)
             Create Directory? Yes|No:

    """
    if confirmation_required:
        if prompt is None:
            prompt = "Confirmed? "

        if resp is True:  # meaning that default response is True
            prompt = "{} [{}]|{}: ".format(prompt, "Yes", "No")
        else:
            prompt = "{} [{}]|{}: ".format(prompt, "No", "Yes")

        ans = input(prompt)
        if not ans:
            return resp

        if re.match('[Yy](es)?', ans):
            return True
        if re.match('[Nn](o)?', ans):
            return False

    else:
        return True


# ====================================================================================================================
""" Change directory """


# Change directory and sub-directories
def cd(*sub_dir):
    # Current working directory
    path = os.getcwd()
    for x in sub_dir:
        path = os.path.join(path, x)
    return path


# Change to data directory and sub-directories
def cdd(*sub_dir):
    path = os.path.join(os.getcwd(), "dat")
    for x in sub_dir:
        path = os.path.join(path, x)
    return path


# Change directory to "dat" and sub-directories
def cd_dat(*sub_dir):
    path = pkg_resources.resource_filename(__name__, 'dat/')
    for x in sub_dir:
        path = os.path.join(path, x)
    return path


# Regulate the input data directory
def regulate_input_data_dir(data_dir):
    """
    :param data_dir: [str] data directory as input
    :return: [str] regulated data directory
    """
    assert isinstance(data_dir, str) or data_dir is None

    if not data_dir:  # Use default file directory
        data_dir = cd()
    else:
        data_dir = os.path.realpath(data_dir.lstrip('.\\'))
        assert os.path.isabs(data_dir), "The input 'dat_dir' is invalid."

    return data_dir


# ====================================================================================================================
""" Save and load data """


# Save data as a pickle file
def save_pickle(pickle_data, path_to_pickle):
    """
    :param pickle_data: any object that could be dumped by the 'pickle' package
    :param path_to_pickle: [str] local file path
    :return: whether the data has been successfully saved
    """
    pickle_filename = os.path.basename(path_to_pickle)
    print("{} \"{}\" ... ".format("Updating" if os.path.isfile(path_to_pickle) else "Saving", pickle_filename), end="")
    try:
        os.makedirs(os.path.dirname(path_to_pickle), exist_ok=True)
        pickle_out = open(path_to_pickle, 'wb')
        pickle.dump(pickle_data, pickle_out)
        pickle_out.close()
        print("Done.")
    except Exception as e:
        print("Failed. {}.".format(e))


# Load a pickle file
def load_pickle(path_to_pickle):
    """
    :param path_to_pickle: [str] local file path
    :return: the object retrieved from the pickle
    """
    pickle_in = open(path_to_pickle, 'rb')
    data = pickle.load(pickle_in)
    pickle_in.close()
    return data


# Save data as a JSON file
def save_json(json_data, path_to_json):
    """
    :param json_data: any object that could be dumped by the 'json' package
    :param path_to_json: [str] local file path
    :return: whether the data has been successfully saved
    """
    json_filename = os.path.basename(path_to_json)
    print("{} \"{}\" ... ".format("Updating" if os.path.isfile(path_to_json) else "Saving", json_filename), end="")
    try:
        os.makedirs(os.path.dirname(path_to_json), exist_ok=True)
        json_out = open(path_to_json, 'w')
        rapidjson.dump(json_data, json_out)
        json_out.close()
        print("Done.")
    except Exception as e:
        print("Failed. {}.".format(e))


# Load a JSON file
def load_json(path_to_json):
    """
    :param path_to_json: [str] local file path
    :return: the json data retrieved
    """
    json_in = open(path_to_json, 'r')
    data = rapidjson.load(json_in)
    json_in.close()
    if isinstance(data, str):
        data = rapidjson.loads(data)
    return data


# Save data to an MSExcel workbook
def save_excel(excel_data, path_to_excel, sep, index, sheet_name, engine='xlsxwriter'):
    """
    :param excel_data: any [DataFrame] that could be dumped saved as a Excel workbook, e.g. '.csv', '.xlsx'
    :param path_to_excel: [str] local file path
    :param sep: [str] separator for saving excel_data to a '.csv' file
    :param index: [bool]
    :param sheet_name: [str] name of worksheet for saving the excel_data to a e.g. '.xlsx' file
    :param engine: [str] ExcelWriter engine; pandas writes Excel files using the 'xlwt' module for '.xls' files and the
                        'openpyxl' or 'xlsxWriter' modules for '.xlsx' files.
    :return: whether the data has been successfully saved or updated
    """
    excel_filename = os.path.basename(path_to_excel)
    _, save_as = os.path.splitext(excel_filename)
    print("{} \"{}\" ... ".format("Updating" if os.path.isfile(path_to_excel) else "Saving", excel_filename), end="")
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path_to_excel)), exist_ok=True)
        if excel_filename.endswith(".csv"):  # Save the data to a .csv file
            excel_data.to_csv(path_to_excel, index=index, sep=sep, na_rep='', float_format=None, columns=None,
                              header=True, index_label=None, mode='w', encoding=None, compression='infer',
                              quoting=None, quotechar='"', line_terminator=None, chunksize=None,
                              tupleize_cols=None, date_format=None, doublequote=True, escapechar=None,
                              decimal='.')
        else:  # Save the data to a .xlsx or .xls file, e.g. excel_filename.endswith(".xlsx")
            xlsx_writer = pd.ExcelWriter(path_to_excel, engine)
            excel_data.to_excel(xlsx_writer, sheet_name, index=index, na_rep='', float_format=None,
                                columns=None, header=True, index_label=None, startrow=0, startcol=0,
                                engine=None, merge_cells=True, encoding=None, inf_rep='inf', verbose=True,
                                freeze_panes=None)
            xlsx_writer.save()
            xlsx_writer.close()
        print("Successfully.")
    except Exception as e:
        print("Failed. {}.".format(e))


# Save data locally (".pickle", ".csv", ".xlsx" or ".xls")
def save(data, path_to_file, sep=',', index=False, sheet_name='Sheet1', engine='xlsxwriter', deep_copy=True):
    """
    :param data: any object that could be dumped
    :param path_to_file: [str] local file path
    :param sep: [str] separator for '.csv'
    :param index:
    :param engine: [str] 'xlwt' for .xls; 'xlsxwriter' or 'openpyxl' for .xlsx
    :param sheet_name: [str] name of worksheet
    :param deep_copy: [bool] whether make a deep copy of the data before saving it
    :return: whether the data has been successfully saved or updated
    """
    # Make a copy the original data
    dat = copy.deepcopy(data) if deep_copy else copy.copy(data)

    # The specified path exists?
    os.makedirs(os.path.dirname(os.path.abspath(path_to_file)), exist_ok=True)

    if isinstance(dat, pd.DataFrame) and dat.index.nlevels > 1:
        dat.reset_index(inplace=True)

    # Save the data according to the file extension
    if path_to_file.endswith((".csv", ".xlsx", ".xls")):
        save_excel(dat, path_to_file, sep, index, sheet_name, engine)
    elif path_to_file.endswith(".json"):
        save_json(dat, path_to_file)
    else:
        save_pickle(dat, path_to_file)
        if not path_to_file.endswith(".pickle"):
            print("Note that the file extension is not among the recognisable formats of this 'save()' function.")


# Print a web page as PDF
def save_web_page_as_pdf(web_page_url, path_to_pdf):
    """
    :param web_page_url: [str] URL of a web page
    :param path_to_pdf: [str] local file path
    :return: whether the web page is saved successfully
    """
    config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
    pdf_options = {'page-size': 'A4',
                   # 'margin-top': '0',
                   # 'margin-right': '0',
                   # 'margin-left': '0',
                   # 'margin-bottom': '0',
                   'zoom': '1.0',
                   'encoding': "UTF-8"}
    status = pdfkit.from_url(web_page_url, path_to_pdf, configuration=config, options=pdf_options)
    return "Web page '{}' saved as '{}'".format(web_page_url, os.path.basename(path_to_pdf)) \
        if status else "Check URL status."


# ====================================================================================================================
""" Converter/parser """


# Convert "miles.chains" to Network Rail mileages
def miles_chains_to_mileage(miles_chains):
    """
    :param miles_chains: [str] 'miles.chains'
    :return: [str] 'miles.yards'

    Note on the 'ELRs and mileages' web page that 'mileages' are given in the form 'miles.chains'.

    """
    if not pd.isnull(miles_chains):
        miles, chains = str(miles_chains).split('.')
        yards = measurement.measures.Distance(chain=chains).yd
        network_rail_mileage = '%.4f' % (int(miles) + round(yards / (10 ** 4), 4))
    else:
        network_rail_mileage = miles_chains
    return network_rail_mileage


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
def get_cls_catalogue(url, navigation_bar_exists=True, menu_exists=True):
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


# Divide a list into sub-lists of equal length
def divide_equally(lst, chunk_size):
    """
    Ref: https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
    Yield successive n-sized chunks from l.
    """
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]
