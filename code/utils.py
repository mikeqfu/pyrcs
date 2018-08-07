""" Utilities - Helper functions """

import collections
import copy
import json
import os
import pickle
import re
import subprocess

import bs4
import dateutil.parser
import matplotlib.pyplot
import measurement.measures
import pandas as pd
import pdfkit
import requests

# ===================================================================================================
""" Change directory """


# Change directory and sub-directories
def cd(*directories):
    # Current working directory
    path = os.getcwd()
    for directory in directories:
        path = os.path.join(path, directory)
    return path


# Change to data directory and sub-directories
def cdd(*directories):
    path = os.path.join(os.getcwd(), "dat")
    for directory in directories:
        path = os.path.join(path, directory)
    return path


# ====================================================================================================================
""" Save and load data """


# Print a web page as PDF
def print_to_pdf(url_to_web_page, path_to_pdf):
    """
    :param url_to_web_page: [str] URL of a web page
    :param path_to_pdf: [str] local file path
    :return: whether the webpa successfully
    """
    config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
    pdf_options = {'page-size': 'A4',
                   # 'margin-top': '0',
                   # 'margin-right': '0',
                   # 'margin-left': '0',
                   # 'margin-bottom': '0',
                   'zoom': '1.0',
                   'encoding': "UTF-8"}
    status = pdfkit.from_url(url_to_web_page, path_to_pdf, configuration=config, options=pdf_options)
    return "Web page '{}' saved as '{}'".format(url_to_web_page, os.path.basename(path_to_pdf)) \
        if status else "Check URL status."


# Save pickles
def save_pickle(pickle_data, path_to_pickle):
    """
    :param pickle_data: any object that could be dumped by the 'pickle' package
    :param path_to_pickle: [str] local file path
    :return: whether the data has been successfully saved
    """
    pickle_filename = os.path.basename(path_to_pickle)
    print("{} \"{}\" ... ".format("Updating" if os.path.isfile(path_to_pickle) else "Saving", pickle_filename), end="")
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path_to_pickle)), exist_ok=True)
        pickle_out = open(path_to_pickle, 'wb')
        pickle.dump(pickle_data, pickle_out)
        pickle_out.close()
        print("Successfully.")
    except Exception as e:
        print("failed due to {}.".format(e))


# Load pickles
def load_pickle(path_to_pickle):
    """
    :param path_to_pickle: [str] local file path
    :return: the object retrieved from the pickle
    """
    print("Loading \"{}\" ... ".format(os.path.basename(path_to_pickle)), end="")
    try:
        pickle_in = open(path_to_pickle, 'rb')
        pickle_data = pickle.load(pickle_in)
        pickle_in.close()
        print("Successfully.")
    except Exception as e:
        print("failed due to {}.".format(e))
        pickle_data = None
    return pickle_data


# Save json file
def save_json(json_data, path_to_json):
    """
    :param json_data: any object that could be dumped by the 'json' package
    :param path_to_json: [str] local file path
    :return: whether the data has been successfully saved
    """
    json_filename = os.path.basename(path_to_json)
    print("{} \"{}\" ... ".format("Updating" if os.path.isfile(path_to_json) else "Saving", json_filename), end="")
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path_to_json)), exist_ok=True)
        json_out = open(path_to_json, 'w')
        json.dump(json_data, json_out)
        json_out.close()
        print("Successfully.")
    except Exception as e:
        print("failed due to {}.".format(e))


# Load json file
def load_json(path_to_json):
    """
    :param path_to_json: [str] local file path
    :return: the json data retrieved
    """
    print("Loading \"{}\" ... ".format(os.path.basename(path_to_json)), end="")
    try:
        json_in = open(path_to_json, 'r')
        json_data = json.load(json_in)
        json_in.close()
        print("Successfully.")
    except Exception as e:
        print("failed due to {}.".format(e))
        json_data = None
    return json_data


# Save Excel workbook
def save_spreadsheet(excel_data, path_to_sheet, sep, index, sheet_name, engine='xlsxwriter'):
    """
    :param excel_data: any [DataFrame] that could be dumped saved as a Excel workbook, e.g. '.csv', '.xlsx'
    :param path_to_sheet: [str] local file path
    :param sep: [str] separator for saving excel_data to a '.csv' file
    :param index:
    :param sheet_name: [str] name of worksheet for saving the excel_data to a e.g. '.xlsx' file
    :param engine: [str] ExcelWriter engine; pandas writes Excel files using the 'xlwt' module for '.xls' files and the
                        'openpyxl' or 'xlsxWriter' modules for '.xlsx' files.
    :return: whether the data has been successfully saved or updated
    """
    excel_filename = os.path.basename(path_to_sheet)
    filename, save_as = os.path.splitext(excel_filename)
    print("{} \"{}\" ... ".format("Updating" if os.path.isfile(path_to_sheet) else "Saving", excel_filename), end="")
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path_to_sheet)), exist_ok=True)
        if save_as == ".csv":  # Save the data to a .csv file
            excel_data.to_csv(path_to_sheet, index=index, sep=sep)
        else:  # Save the data to a .xlsx or .xls file
            xlsx_writer = pd.ExcelWriter(path_to_sheet, engine)
            excel_data.to_excel(xlsx_writer, sheet_name, index=index)
            xlsx_writer.save()
            xlsx_writer.close()
        print("Successfully.")
    except Exception as e:
        print("failed due to {}.".format(e))


# Save data locally (.pickle, .csv or .xlsx)
def save(data, path_to_file, sep=',', index=True, sheet_name='Details', engine='xlsxwriter', deep_copy=True):
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

    dat = copy.deepcopy(data) if deep_copy else copy.copy(data)

    # The specified path exists?
    os.makedirs(os.path.dirname(os.path.abspath(path_to_file)), exist_ok=True)

    # Get the file extension
    _, save_as = os.path.splitext(path_to_file)

    if isinstance(dat, pd.DataFrame) and dat.index.nlevels > 1:
        dat.reset_index(inplace=True)

    # Save the data according to the file extension
    if save_as == ".csv" or save_as == ".xlsx" or save_as == ".xls":
        save_spreadsheet(dat, path_to_file, sep, index, sheet_name, engine)
    elif save_as == ".json":
        save_json(dat, path_to_file)
    else:
        save_pickle(dat, path_to_file)


# Save a figure using plt.savefig()
def save_fig(path_to_fig_file, dpi):
    matplotlib.pyplot.savefig(path_to_fig_file, dpi=dpi)

    save_as = os.path.splitext(path_to_fig_file)[1]
    if save_as == ".svg":
        path_to_emf = path_to_fig_file.replace(save_as, ".emf")
        subprocess.call(["C:\Program Files\Inkscape\inkscape.exe", '-z', path_to_fig_file, '-M', path_to_emf])


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
        networkrail_mileage = '%.4f' % (int(miles) + round(yards / (10 ** 4), 4))
    else:
        networkrail_mileage = miles_chains
    return networkrail_mileage


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


# Show last update date
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
            i = x[0]
            to_repeat = x[1]
            for y in to_repeat:
                for j in range(1, y[0]):
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
def parse_loc_note(x):
    # Data
    d = re.search('[\w ,]+(?=[ \n]\[)', x)
    if d is not None:
        dat = d.group()
    else:
        m_pat = re.compile('[Oo]riginally |[Ff]ormerly |[Ll]ater |[Pp]resumed |\?|\"|\n')
        # dat = re.search('["\w ,]+(?= [[(?\'])|["\w ,]+', x).group(0) if re.search(m_pat, x) else x
        dat = ' '.join(x.replace(x[x.find('('):x.find(')') + 1], '').split()) if re.search(m_pat, x) else x
    # Note
    n = re.search('(?<=[\n ][\[(\'])[\w ,\'\"/?]+', x)
    if n is not None and (n.group() == "'" or n.group() == '"'):
        n = re.search(r'(?<=[\[(])[\w ,?]+(?=[])])', x)
    note = n.group() if n is not None else ''
    if 'STANOX ' in dat and 'STANOX ' in x and note == '':
        dat = x[0:x.find('STANOX')].strip()
        note = x[x.find('STANOX'):]
    return dat, note


# ====================================================================================================================
""" Misc """


#
def is_float(text):
    try:
        float(text)
        return True
    except ValueError:
        try:
            float(re.sub('[()~]', '', text))
            return True
        except ValueError:
            return False
