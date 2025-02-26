"""
Provides a number of helper functions.
"""

import importlib.resources
import os
import re
import string

import pandas as pd
from pyhelpers._cache import _format_error_message
from pyhelpers.ops import confirmed, is_url_connectable
from pyhelpers.store import load_data, save_data


# == Specify address of web pages ==================================================================


def home_page_url():
    """
    Returns the homepage URL of the data source.

    :return: The homepage URL of the data source.
    :rtype: str

    **Examples**::

        >>> from pyrcs.utils import home_page_url
        >>> home_page_url()
        'http://www.railwaycodes.org.uk/'
    """

    return 'http://www.railwaycodes.org.uk/'


# == Validate inputs ===============================================================================


def is_home_connectable():
    """
    Checks and returns whether the Railway Codes website is reacheable.

    :return: Whether the Railway Codes website is reacheable.
    :rtype: bool

    **Examples**::

        >>> from pyrcs.utils import is_home_connectable
        >>> is_home_connectable()
        True
    """

    url = home_page_url()

    rslt = is_url_connectable(url=url)

    return rslt


def is_str_float(x):
    """
    Checks and returns whether a string represents a float value.

    :param x: String-type data.
    :type x: str
    :return: Whether the string-type data represents a float value.
    :rtype: bool

    **Examples**::

        >>> from pyrcs.utils import is_str_float
        >>> is_str_float('')
        False
        >>> is_str_float('a')
        False
        >>> is_str_float('1')
        True
        >>> is_str_float('1.1')
        True
    """

    try:
        float(x)  # float(re.sub('[()~]', '', text))
        is_float = True

    except ValueError:
        is_float = False

    return is_float


def validate_initial(x, as_is=False):
    """
    Validates if a string is a single letter, returning it in upper case or as is.

    :param x: The input value to validate,
        which is expected to be a string representing a single letter.
    :type x: str
    :param as_is: If set to ``True``, the function returns the letter in its original case;
        if set to ``False`` (default), the letter is returned in uppercase.
    :type as_is: bool
    :return: The validated initial letter, either in uppercase or as-is.
    :rtype: str

    **Examples**::

        >>> from pyrcs.utils import validate_initial
        >>> validate_initial('x')
        'X'
        >>> validate_initial('x', as_is=True)
        'x'
        >>> validate_initial('xyz')
        AssertionError: `x` must be a single letter.
    """

    assert x in set(string.ascii_letters), "`x` must be a single letter."

    valid_initial = x if as_is else x.upper()

    return valid_initial


def validate_page_name(cls_instance, page_no, valid_page_no):
    """
    Retrieves the valid page name corresponding to a given page number.

    This method checks if the provided ``page_no`` is within the set of
    valid page numbers. If valid, it returns the name of the page
    associated with the specified ``page_no`` from the catalogue of the given ``cls_instance``.

    :param cls_instance: An instance of the class that contains the page catalogue.
    :type cls_instance: object
    :param page_no: The page number to validate,
        which can be an integer or a string representation of a number.
    :type page_no: int | str
    :param valid_page_no: A collection of valid page numbers,
        which can be a set, list, or tuple containing the allowable page numbers.
    :type valid_page_no: set | list | tuple | range
    :return: The validated page name associated with the given ``page_no`` in the class's catalogue.
    :rtype: str

    .. seealso::

        Examples for the methods:

        - :meth:`Tunnels.collect_codes_by_page()
          <pyrcs.other_assets.tunnel.Tunnels.collect_codes_by_page>`
        - :meth:`Tunnels.collect_codes_by_page()
          <pyrcs.other_assets.viaduct.Viaducts.collect_codes_by_page>`
    """

    assert page_no in valid_page_no, f"Valid `page_no` must be one of {valid_page_no}."

    assert hasattr(cls_instance, 'catalogue'), \
        "The input `cls_instance` must have an attribute named `catalogue`."
    # noinspection PyUnresolvedReferences
    page_name = [k for k in cls_instance.catalogue.keys() if str(page_no) in k][0]

    return page_name


def collect_in_fetch_verbose(data_dir, verbose):
    """
    Creates a new parameter that indicates whether to print relevant information to the console.

    This function is used only if it is necessary to re-collect data when trying to fetch the data.

    :param data_dir: The name of the folder where the pickle file is to be saved.
    :type data_dir: str | None
    :param verbose: Whether to print relevant information to the console.
    :type verbose: bool | int
    :return: A boolean indicating whether to print relevant information to the console when
        collecting data.
    :rtype: bool | int

    **Examples**::

        >>> from pyrcs.utils import collect_in_fetch_verbose
        >>> collect_in_fetch_verbose(data_dir="data", verbose=True)
        False
    """

    verbose_ = False if (data_dir or not verbose) else (2 if verbose == 2 else True)

    return verbose_


def fetch_all_verbose(data_dir, verbose):
    """
    Creates a new parameter that indicates whether to print relevant information to the console.

    This function is used only when fetching all data of a cluster.

    :param data_dir: Name of the folder where the pickle file is to be saved.
    :type data_dir: str | None
    :param verbose: Whether to print relevant information to the console.
    :type verbose: bool | int
    :return: A boolean indicating whether to print relevant information to the console when
        fetching all data of a cluster.
    :rtype: bool | int

    **Examples**::

        >>> from pyrcs.utils import fetch_all_verbose
        >>> fetch_all_verbose(data_dir="data", verbose=True)
        False
    """

    if is_home_connectable():
        verbose_ = collect_in_fetch_verbose(data_dir=data_dir, verbose=verbose)
    else:
        verbose_ = False

    return verbose_


# == Print messages ================================================================================


def format_confirmation_prompt(data_name, initial=None, ending="\n?"):
    # noinspection PyShadowingNames
    """
    Returns a message for comfirming whether to proceed to collect a certain cluster of data.

    :param data_name: The name of the dataset to be collected, e.g. ``"Railway Codes"``.
    :type data_name: str
    :param initial: The initial letter for the code; defaults to ``None``.
    :type initial: str | None
    :param ending: The ending of the confirmation message; defaults to ``"\\n?"``.
    :type ending: str
    :return: A confirmation message asking whether to proceed with the dataset collection.
    :rtype: str

    **Examples**::

        >>> from pyrcs.utils import format_confirmation_prompt
        >>> prompt = format_confirmation_prompt(data_name="Railway Codes")
        >>> print(prompt)
        To collect data of Railway Codes
        ?
        >>> prompt = format_confirmation_prompt(data_name="location codes", initial="A")
        >>> print(prompt)
        To collect data of location codes beginning with "A"
        ?
    """

    prompt = f"To collect data of {data_name}"
    if initial:
        if initial.lower() in string.ascii_letters:
            prompt += f' beginning with "{initial}"{ending}'
        else:
            prompt += f' ({initial})'
    else:
        prompt += ending

    return prompt


def print_collect_msg(data_name, initial=None, verbose=False, confirmation_required=True,
                      end=" ... "):
    """
    Prints a message indicating the status of data collection.

    :param data_name: The name of the data being collected.
    :type data_name: str
    :param initial: The initial letter of the desired code or data; defaults to ``None``.
    :type initial: str | None
    :param verbose: Whether to print relevant information to the console.
    :type verbose: bool | int
    :param confirmation_required: Whether user confirmation is required before proceeding.
    :type confirmation_required: bool
    :param end: String appended at the end of the message; defaults to ``" ... "``.
    :type end: str

    **Examples**::

        >>> from pyrcs.utils import print_collect_msg
        >>> print_collect_msg("Railway Codes", verbose=True, confirmation_required=False)
        Collecting the data of "Railway Codes" ...
    """

    message_ = "Collecting the data"

    if verbose in {True, 1}:
        if confirmation_required:
            print(message_, end=end)

        else:
            message_ += f" of {data_name}"
            if initial:
                if initial.lower() in string.ascii_letters:
                    print(f'{message_} beginning with "{initial}"', end=end)
                else:
                    print(f'{message_} ({initial})', end=end)
            else:
                print(message_, end=end)


def print_conn_err(verbose=False):
    """
    Prints a message if an Internet connection attempt is unsuccessful.

    :param verbose: Whether to print relevant information to the console; defaults to ``False``
    :type verbose: bool | int

    **Examples**::

        >>> from pyrcs.utils import print_conn_err
        >>> # If Internet connection is ready, nothing would be printed
        >>> print_conn_err(verbose=True)

    """

    if not is_home_connectable():
        if verbose:
            print("Failed to establish an Internet connection. "
                  "The current instance relies on local backup.")


def print_inst_conn_err(update=False, verbose=False, e=None):
    """
    Prints an error message when an instance fails to establish an Internet connection.

    :param update: Indicates whether the error occurred during a data update; defaults to ``False``.
    :type update: bool
    :param verbose: Whether to print relevant information to the console; defaults to ``False``.
    :type verbose: bool | int
    :param e: An optional exception message to display.
    :type e: Exception | None

    **Examples**::

        >>> from pyrcs.utils import print_inst_conn_err
        >>> print_inst_conn_err(verbose=True)
        The Internet connection is not available.
        >>> print_inst_conn_err(update=True, verbose=True)
        The Internet connection is not available. Failed to update the data.
    """

    if not verbose:
        return None  # No need to print anything if verbosity is off

    if verbose == 2:
        print("Failed.", end=" ")

    err_msg = _format_error_message(e) if e else "The Internet connection is not available."

    if update:
        err_msg += " Failed to update the data."

    print(err_msg)


def print_void_msg(data_name, verbose):
    """
    Print a message when the data collection process fails.

    :param data_name: The name of the data being collected.
    :type data_name: str
    :param verbose: Whether to print relevant information to the console.
    :type verbose: bool | int

    **Examples**::

        >>> from pyrcs.utils import print_void_msg
        >>> print_void_msg(data_name="Railway Codes", verbose=True)
        No data of "Railway Codes" has been freshly collected.
    """

    if verbose:
        print(f"No data of \"{data_name.title()}\" has been freshly collected.")


# == Save and retrieve pre-packed data =============================================================


def cd_data(*sub_dir, data_dir="data", mkdir=False, **kwargs):
    """
    Specifies or changes to a directory (or subdirectories) for storing backup data for the package.

    :param sub_dir: Name(s) of directories and/or a filename to navigate to or create.
    :type sub_dir: str
    :param data_dir: The base directory for storing data; defaults to ``"data"``.
    :type data_dir: str
    :param mkdir: Whether to create the specified directory if it does not exist;
        defaults to ``False``.
    :type mkdir: bool
    :param kwargs: [Optional] Additional parameters for `os.makedirs()`_, such as ``mode=0o777``.
    :return: The full path of the specified directory or file within ``data_dir``.
    :rtype: str

    .. _`os.makedirs()`: https://docs.python.org/3/library/os.html#os.makedirs

    **Examples**::

        >>> from pyrcs.utils import cd_data
        >>> import os
        >>> path_to_dat_dir = cd_data(data_dir="data")
        >>> os.path.relpath(path_to_dat_dir)
        'pyrcs\\data'
    """

    path = importlib.resources.files(__package__).joinpath(data_dir)
    for x in sub_dir:
        path = os.path.join(path, x)

    if mkdir:
        path_to_file, ext = os.path.splitext(path)
        if ext == '':
            os.makedirs(path_to_file, exist_ok=True, **kwargs)
        else:
            os.makedirs(os.path.dirname(path_to_file), exist_ok=True, **kwargs)

    return path


def fetch_location_names_errata(k=None, regex=False, as_dataframe=False, column_name=None):
    """
    Fetches a dictionary or dataframe to rectify location names.

    :param k: The key for the errata dictionary; defaults to ``None``.
    :type k: str | int | float | bool | None
    :param regex: Whether to create the dictionary for replacements based on regular expressions;
        defaults to ``False``.
    :type regex: bool
    :param as_dataframe: Whether to return the dictionary as a dataframe; defaults to ``False``.
    :type as_dataframe: bool
    :param column_name: If ``as_dataframe=True``, the column name for the dataframe;
        defaults to ``None``.
    :type column_name: str | list | None
    :return: A dictionary for rectifying location names, or a dataframe if requested.
    :rtype: dict | pandas.DataFrame

    **Examples**::

        >>> from pyrcs.utils import fetch_location_names_errata
        >>> repl_dict = fetch_location_names_errata()
        >>> type(repl_dict)
        dict
        >>> list(repl_dict.keys())[:5]
        ['"Tyndrum Upper" (Upper Tyndrum)',
         'AISH EMERGENCY CROSSOVER',
         'ATLBRJN',
         'Aberdeen Craiginches',
         'Aberdeen Craiginches T.C.']
        >>> repl_dict = fetch_location_names_errata(regex=True, as_dataframe=True)
        >>> type(repl_dict)
        pandas.core.frame.DataFrame
        >>> repl_dict.head()
                                         new_value
        re.compile(' \\(DC lines\\)')   [DC lines]
        re.compile(' And | \\+ ')               &
        re.compile('-By-')                    -by-
        re.compile('-In-')                    -in-
        re.compile('-En-Le-')              -en-le-
    """

    json_filename = "location-names-errata{}.json".format("" if not regex else "-regex")
    location_name_repl_dict = load_data(cd_data(json_filename))

    if regex:
        location_name_repl_dict = {re.compile(k): v for k, v in location_name_repl_dict.items()}

    replacement_dict = {k: location_name_repl_dict} if k else location_name_repl_dict

    if as_dataframe:
        if column_name is None:
            col_name = ['Name']
        else:
            col_name = [column_name] if isinstance(column_name, str) else column_name.copy()
        replacement_dict = pd.DataFrame.from_dict(replacement_dict, orient='index', columns=col_name)

    return replacement_dict


def _update_location_names_errata(new_items, regex, verbose=False):
    """
    Updates the location name replacement dictionary in the package data.

    :param new_items: The new items to add or replace in the dictionary.
    :type new_items: dict
    :param regex: Whether this update applies to the regular expression dictionary.
    :type regex: bool
    :param verbose: Whether to print detailed information to the console; defaults to ``False``.
    :type verbose: bool | int
    """

    json_filename = "location-names-repl{}.json".format("" if not regex else "-regex")

    new_items_keys = list(new_items.keys())

    if confirmed(f'To update "{json_filename}" with {{"{new_items_keys[0]}"... }}?'):
        path_to_json = cd_data(json_filename)
        location_name_repl_dict = load_data(path_to_json)

        if any(isinstance(k, re.Pattern) for k in new_items_keys):
            new_items = {k.pattern: v for k, v in new_items.items() if isinstance(k, re.Pattern)}

        location_name_repl_dict.update(new_items)

        save_data(location_name_repl_dict, path_to_json, verbose=verbose)
