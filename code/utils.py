import copy
import json
import os
import pickle

import bs4
import dateutil.parser
import measurement.measures
import pandas as pd
import pdfkit
import requests


# Change directory ===================================================================================================
def cdd_rc(*directories):
    # Current working directory
    path = os.getcwd()
    for directory in directories:
        path = os.path.join(path, directory)
    return path


# Change to data directory ===========================================================================================
def cdd_rc_dat(*directories):
    path = os.path.join(os.getcwd(), "dat")
    for directory in directories:
        path = os.path.join(path, directory)
    return path


# Print a web page as PDF ============================================================================================
def save_to_pdf(url_to_webpage, path_to_pdf):
    """
    :param url_to_webpage: [str] URL of a web page
    :param path_to_pdf: [str] local file path
    :return: Whether the webpa successfully
    """
    config = pdfkit.configuration(wkhtmltopdf="C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
    pdf_options = {'page-size': 'A4',
                   # 'margin-top': '0',
                   # 'margin-right': '0',
                   # 'margin-left': '0',
                   # 'margin-bottom': '0',
                   'zoom': '1.0',
                   'encoding': "UTF-8"}
    status = pdfkit.from_url(url_to_webpage, path_to_pdf, configuration=config, options=pdf_options)
    return "Web page '{}' saved as '{}'".format(url_to_webpage, os.path.basename(path_to_pdf)) \
        if status else "Check URL status."


# Save pickles =======================================================================================================
def save_pickle(pickle_data, path_to_pickle):
    """
    :param pickle_data: any object that could be dumped by the 'pickle' package
    :param path_to_pickle: [str] local file path
    :return: Whether the data has been successfully saved.
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
        print("failed due to {}.".format(e))


# Load pickles =======================================================================================================
def load_pickle(path_to_pickle):
    """
    :param path_to_pickle: [str] local file path
    :return: the object retrieved from the pickle
    """
    pickle_in = open(path_to_pickle, 'rb')
    data = pickle.load(pickle_in)
    pickle_in.close()
    return data


# Save and load json files ===========================================================================================
def save_json(json_data, path_to_json):
    """
    :param json_data: [Any object that could be dumped by the 'json' package]
    :param path_to_json: [str] local file path
    :return:
    """
    json_filename = os.path.basename(path_to_json)
    print("{} \"{}\" ... ".format("Updating" if os.path.isfile(path_to_json) else "Saving", json_filename), end="")
    try:
        os.makedirs(os.path.dirname(path_to_json), exist_ok=True)
        json_out = open(path_to_json, 'w')
        json.dump(json_data, json_out)
        json_out.close()
        print("Done.")
    except Exception as e:
        print("failed due to {}.".format(e))


def load_json(path_to_json):
    """
    :param path_to_json: [str]
    :return: the json data retrieved
    """
    json_in = open(path_to_json, 'r')
    data = json.load(json_in)
    json_in.close()
    return data


def save_workbook(excel_data, path_to_excel, sep, sheet_name, engine='xlsxwriter'):
    excel_filename = os.path.basename(path_to_excel)
    filename, save_as = os.path.splitext(excel_filename)
    print("{} \"{}\" ... ".format("Updating" if os.path.isfile(path_to_excel) else "Saving", excel_filename), end="")
    try:
        os.makedirs(os.path.dirname(path_to_excel), exist_ok=True)
        if save_as == ".csv":  # Save the data to a .csv file
            excel_data.to_csv(path_to_excel, index=False, sep=sep)
        else:  # Save the data to a .xlsx or .xls file
            xlsx_writer = pd.ExcelWriter(path_to_excel, engine)
            excel_data.to_excel(xlsx_writer, sheet_name, index=False)
            xlsx_writer.save()
            xlsx_writer.close()
        print("Done.")
    except Exception as e:
        print("failed due to {}.".format(e))


# Save data locally (.pickle, .csv or .xlsx) =========================================================================
def save(data, path_to_file, sep=',', sheet_name='Details', deep_copy=True):

    dat = copy.deepcopy(data) if deep_copy else copy.copy(data)

    # The specified path exists?
    os.makedirs(os.path.dirname(os.path.abspath(path_to_file)), exist_ok=True)

    # Get the file extension
    _, save_as = os.path.splitext(path_to_file)

    if isinstance(dat, pd.DataFrame) and dat.index.nlevels > 1:
        dat.reset_index(inplace=True)

    # Save the data according to the file extension
    if save_as == ".csv" or save_as == ".xlsx" or save_as == ".xls":
        save_workbook(dat, path_to_file, sep, sheet_name, engine='xlsxwriter')
    elif save_as == ".json":
        save_json(dat, path_to_file)
    else:
        save_pickle(dat, path_to_file)


# Convert "miles.chains" to Network Rail mileages ====================================================================
def miles_chains_to_mileage(miles_chains):
    """ 
    Note on the 'ELRs and mileages' web page that 'mileages' are given in the form 'miles.chains'.
    """
    miles, chains = str(miles_chains).split('.')
    yards = measurement.measures.Distance(chain=chains).yd
    networkrail_mileage = '%.4f' % (int(miles) + round(yards / (10 ** 4), 4))
    return networkrail_mileage


# Parse date string ==================================================================================================
def get_parsed_date(str_date, date_type=False):
    parsed_date = dateutil.parser.parse(str_date, fuzzy=True)
    # Or, parsed_date = datetime.strptime(last_update_date[12:], '%d %B %Y')
    parsed_date = parsed_date.date() if date_type else str(parsed_date.date())
    return parsed_date


# Show last update date ==============================================================================================
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
            last_update_date = get_parsed_date(last_update_date, date_type)
    else:
        last_update_date = None  # print('Information not available.')
    return last_update_date


# Get a list of parsed HTML tr's =====================================================================================
def parse_tr(header, trs):
    """
    :param header: [list] list of column names of a requested table
    :param trs: [list] contents under tr tags of the web page
    :return: [list] list of lists each comprising a row of the requested table

    Get a list of parsed HTML tr's, each of which corresponds to a piece of
    record (A key function to drive the following functions)

    Reference:
    stackoverflow.com/questions/28763891/what-should-i-do-when-tr-has-rowspan

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
    for no, trs in enumerate(trs):
        for td_no, rho in enumerate(trs.find_all('td')):
            # print(data.has_attr("rowspan"))
            if rho.has_attr('rowspan'):
                row_spanned.append((no, td_no, int(rho['rowspan']), rho.text))

    if row_spanned:
        for i in row_spanned:
            # assert isinstance(i[0], int)
            for j in range(1, i[2]):
                # Add value in next tr
                idx = i[0] + j
                # assert isinstance(idx, int)
                if i[1] >= len(tbl_lst[idx]):
                    tbl_lst[idx].insert(i[1], i[3])
                elif tbl_lst[idx][i[1]] != tbl_lst[i[0]][i[1]]:
                    tbl_lst[idx].insert(i[1], i[3])
                else:
                    tbl_lst[idx].insert(i[1] + 1, i[3])

    for k in range(len(tbl_lst)):
        l = len(header) - len(tbl_lst[k])
        if l > 0:
            tbl_lst[k].extend(['\xa0'] * l)

    return tbl_lst


# Parse the acquired list to make it be ready for creating the DataFrame =============================================
def parse_table(source, parser='lxml'):
    """
    :param source: response object to connecting a URL to request a table
    :param parser:
    :return [tuple] containing: (see parse_trs())
                [list] of lists each comprising a row of the requested table;
                [list] of column names of the requested table
    """
    # (If source.status_code == 200, the requested URL is available.)
    # Get plain text from the source URL
    web_page_text = source.text
    # Parse the text
    # (Optional parsers: 'lxml', 'html5lib', 'html.parser')
    parsed_text = bs4.BeautifulSoup(web_page_text, parser)
    # Get all data under the HTML label 'tr'
    table_temp = parsed_text.find_all('tr')
    # Get a list of column names for output DataFrame
    headers = table_temp[0]
    header = [header.text for header in headers.find_all('th')]
    # Get a list of lists, each of which corresponds to a piece of record
    trs = table_temp[3:]
    # Return a list of parsed tr's, each of which corresponds to one df row
    return parse_tr(header, trs), header


#
def isfloat(string, extras='()~'):
    try:
        float(string)
        return True
    except ValueError:
        if any(extr in string for extr in extras):
            return True
        else:
            return False
