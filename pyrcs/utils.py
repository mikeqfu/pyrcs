"""Provide a number of helper functions."""

import copy
import importlib.resources
import os
import re
import string

import pandas as pd
from pyhelpers.dirs import validate_dir
from pyhelpers.ops import confirmed, is_url_connectable
from pyhelpers.store import load_data, save_data


# == Specify address of web pages ==================================================================


def home_page_url():
    """
    Specify the homepage URL of the data source.

    :return: URL of the data source homepage
    :rtype: str

    **Example**::

        >>> from pyrcs.utils import home_page_url

        >>> home_page_url()
        'http://www.railwaycodes.org.uk/'
    """

    return 'http://www.railwaycodes.org.uk/'


# == Validate inputs ===============================================================================


def is_home_connectable():
    """
    Check whether the Railway Codes website is connectable.

    :return: whether the Railway Codes website is connectable
    :rtype: bool

    **Example**::

        >>> from pyrcs.utils import is_home_connectable

        >>> is_home_connectable()
        True
    """

    url = home_page_url()

    rslt = is_url_connectable(url=url)

    return rslt


def is_str_float(x):
    """
    Check if a string-type variable can express a float-type value.

    :param x: a string-type variable
    :type x: str
    :return: whether ``str_val`` can express a float value
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
    Get a valid initial letter as an input.

    :param x: any string variable (which is supposed to be an initial letter)
    :type x: str
    :param as_is: whether to return the validated letter as is the input
    :type as_is: bool
    :return: validated initial letter
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


def validate_page_name(cls, page_no, valid_page_no):
    """
    Get a valid page name.

    :param cls: instance of a class
    :type cls: any
    :param page_no: page number
    :type page_no: int | str
    :param valid_page_no: all valid page numbers
    :type valid_page_no: set | list | tuple
    :return: validated page name of the given ``cls``
    :rtype: str

    .. seealso::

        - Examples for the methods
          :meth:`Tunnels.collect_codes_by_page()
          <pyrcs.other_assets.tunnel.Tunnels.collect_codes_by_page>`
          and
          :meth:`Tunnels.collect_codes_by_page()
          <pyrcs.other_assets.viaduct.Viaducts.collect_codes_by_page>`.
    """

    assert page_no in valid_page_no, f"Valid `page_no` must be one of {valid_page_no}."

    page_name = [k for k in cls.catalogue.keys() if str(page_no) in k][0]

    return page_name


def collect_in_fetch_verbose(data_dir, verbose):
    """
    Create a new parameter that indicates whether to print relevant information in console
    (used only if it is necessary to re-collect data when trying to fetch the data).

    :param data_dir: name of a folder where the pickle file is to be saved
    :type data_dir: str | None
    :param verbose: whether to print relevant information in console
    :type verbose: bool | int
    :return: whether to print relevant information in console when collecting data
    :rtype: bool | int

    **Example**::

        >>> from pyrcs.utils import collect_in_fetch_verbose

        >>> collect_in_fetch_verbose(data_dir="data", verbose=True)
        False
    """

    verbose_ = False if (data_dir or not verbose) else (2 if verbose == 2 else True)

    return verbose_


def fetch_all_verbose(data_dir, verbose):
    """
    Create a new parameter that indicates whether to print relevant information in console
    (used only when trying to fetch all data of a cluster).

    :param data_dir: name of a folder where the pickle file is to be saved
    :type data_dir: str | None
    :param verbose: whether to print relevant information in console
    :type verbose: bool | int
    :return: whether to print relevant information in console when collecting data
    :rtype: bool | int

    **Example**::

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


def confirm_msg(data_name):
    """
    Create a confirmation message (for data collection).

    :param data_name: name of data, e.g. "Railway Codes"
    :type data_name: str
    :return: a confirmation message
    :rtype: str

    **Example**::

        >>> from pyrcs.utils import confirm_msg

        >>> msg = confirm_msg(data_name="Railway Codes")
        >>> print(msg)
        To collect data of Railway Codes
        ?
    """

    cfm_msg = f"To collect data of {data_name}\n?"

    return cfm_msg


def print_collect_msg(data_name, verbose, confirmation_required, end=" ... "):
    """
    Print a message about the status of collecting data.

    :param data_name: name of the data being collected
    :type data_name: str
    :param verbose: whether to print relevant information in console
    :type verbose: bool | int
    :param confirmation_required: whether to confirm before proceeding
    :type confirmation_required: bool
    :param end: string appended after the last value, defaults to ``" ... "``.
    :type end: str

    **Example**::

        >>> from pyrcs.utils import print_collect_msg

        >>> print_collect_msg("Railway Codes", verbose=2, confirmation_required=False)
        Collecting the data of "Railway Codes" ...
    """

    if verbose == 2:
        if confirmation_required:
            print("Collecting the data", end=end)
        else:
            print(f"Collecting the data of \"{data_name}\"", end=end)


def print_conn_err(verbose=False):
    """
    Print a message about unsuccessful attempts to establish a connection to the Internet.

    :param verbose: whether to print relevant information in console, defaults to ``False``
    :type verbose: bool | int

    **Example**::

        >>> from pyrcs.utils import print_conn_err

        >>> # If Internet connection is ready, nothing would be printed
        >>> print_conn_err(verbose=True)

    """

    if not is_home_connectable():
        if verbose:
            print("Failed to establish an Internet connection. "
                  "The current instance relies on local backup.")


def format_err_msg(e):
    """
    Format an error message.

    :param e: Subclass of Exception.
    :type e: Exception | None
    :return: An error message.
    :rtype: str
    """

    if e:
        e_ = f"{e}"
        err_msg = e_ + "." if not e_.endswith((".", "!", "?")) else e_
    else:
        err_msg = ""

    return err_msg


def print_inst_conn_err(update=False, verbose=False, e=None):
    """
    Print a message about unsuccessful attempts to establish a connection to the Internet
    (for an instance of a class).

    :param update: mostly complies with ``update`` in a parent function that uses this function,
        defaults to ``False``
    :type update: bool
    :param verbose: whether to print relevant information in console, defaults to ``False``
    :type verbose: bool | int
    :param e: error message
    :type e: Exception | None

    **Example**::

        >>> from pyrcs.utils import print_inst_conn_err

        >>> print_inst_conn_err(verbose=True)
        The Internet connection is not available.
    """

    if e is None:
        err_msg = "The Internet connection is not available."
    else:
        err_msg = format_err_msg(e)

    if update and verbose:
        print((err_msg + " " if err_msg else err_msg) + "Failed to update the data.")
    elif verbose:
        print(err_msg)


def print_void_msg(data_name, verbose):
    """
    Print a message about the status of collecting data
    (only when the data collection process fails).

    :param data_name: name of the data being collected
    :type data_name: str
    :param verbose: whether to print relevant information in console
    :type verbose: bool | int

    **Example**::

        >>> from pyrcs.utils import print_void_msg

        >>> print_void_msg(data_name="Railway Codes", verbose=True)
        No data of "Railway Codes" has been freshly collected.
    """

    if verbose:
        print(f"No data of \"{data_name.title()}\" has been freshly collected.")


# == Save and retrieve pre-packed data =============================================================


def cd_data(*sub_dir, data_dir="data", mkdir=False, **kwargs):
    """
    Specify (or change to) a directory (or any subdirectories) for backup data of the package.

    :param sub_dir: [optional] name of a directory; names of directories (and/or a filename)
    :type sub_dir: str
    :param data_dir: name of a directory to store data, defaults to ``"data"``
    :type data_dir: str
    :param mkdir: whether to create a directory, defaults to ``False``
    :type mkdir: bool
    :param kwargs: [optional] parameters (e.g. ``mode=0o777``) of `os.makedirs`_
    :return: a full pathname of a directory or a file under the specified data directory ``data_dir``
    :rtype: str

    .. _`os.makedirs`: https://docs.python.org/3/library/os.html#os.makedirs

    **Example**::

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


def init_data_dir(cls_instance, data_dir, category, cluster=None, **kwargs):
    """
    Specify an initial data directory for (an instance of) a class for a data cluster.

    :param cls_instance: An instance of a class for a certain data cluster.
    :type cls_instance: object
    :param data_dir: The name of a folder where the pickle file is to be saved.
    :type data_dir: str | None
    :param category: The name of a data category, e.g. ``"line-data"``.
    :type category: str
    :param cluster: A replacement for ``cls.KEY``.
    :type cluster: str | None
    :param kwargs: [optional] parameters of the function :func:`~pyrcs.utils.cd_data`.
    :return: Pathnames of a default data directory and a current data directory.
    :rtype: tuple[str, os.PathLike[str]]

    **Example**::

        >>> from pyrcs.utils import init_data_dir
        >>> from pyrcs.line_data import Bridges
        >>> import os

        >>> bridges = Bridges()

        >>> dat_dir, current_dat_dir = init_data_dir(bridges, data_dir="data", category="line-data")
        >>> os.path.relpath(dat_dir)
        'data'
        >>> os.path.relpath(current_dat_dir)
        'data'
    """

    if data_dir:
        cls_instance.data_dir = validate_dir(data_dir)

    else:
        cluster_ = cls_instance.__getattribute__('KEY') if cluster is None else copy.copy(cluster)
        cls_instance.data_dir = cd_data(category, cluster_.lower().replace(" ", "-"), **kwargs)

    cls_instance.current_data_dir = copy.copy(cls_instance.data_dir)

    return cls_instance.data_dir, cls_instance.current_data_dir


def make_file_pathname(cls, data_name, ext=".pkl", data_dir=None):
    """
    Make a pathname for saving data as a file of a certain format.

    :param cls: (An instance of) a class for a certain data cluster.
    :type cls: object
    :param data_name: The key to the dict-type data of a certain code cluster.
    :type data_name: str
    :param ext: A file extension, defaults to ``".pkl"``.
    :type ext: str
    :param data_dir: The name of a folder where the data is saved, defaults to ``None``.
    :type data_dir: str | None
    :return: A pathname for saving the data.
    :rtype: str

    **Example**::

        >>> from pyrcs.utils import make_file_pathname
        >>> from pyrcs.line_data import Bridges
        >>> import os

        >>> bridges = Bridges()

        >>> example_pathname = make_file_pathname(bridges, data_name="example-data", ext=".pkl")
        >>> os.path.relpath(example_pathname)
        'pyrcs\\data\\line-data\\bridges\\example-data.pkl'
    """

    filename = data_name.lower().replace(" ", "-") + ext

    if data_dir is not None:
        cls.current_data_dir = validate_dir(path_to_dir=data_dir)
        file_pathname = os.path.join(cls.current_data_dir, filename)

    else:  # data_dir is None or data_dir == ""
        # func = [x for x in dir(cls) if x.startswith('_cdd')][0]
        file_pathname = getattr(cls, '_cdd')(filename)

    return file_pathname


def fetch_location_names_errata(k=None, regex=False, as_dataframe=False, column_name=None):
    """
    Create a dictionary for rectifying location names.

    :param k: key of the created dictionary, defaults to ``None``
    :type k: str | int | float | bool | None
    :param regex: whether to create a dictionary for replacement based on regular expressions,
        defaults to ``False``
    :type regex: bool
    :param as_dataframe: whether to return the created dictionary as a pandas.DataFrame,
        defaults to ``False``
    :type as_dataframe: bool
    :param column_name: (if ``as_dataframe=True``) column name of the errata data as a dataframe
    :type column_name: str | list | None
    :return: dictionary for rectifying location names
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
    Update the location-names replacement dictionary in the package data.

    :param new_items: new items to replace
    :type new_items: dict
    :param regex: whether this update is for regular-expression dictionary
    :type regex: bool
    :param verbose: whether to print relevant information in console, defaults to ``False``
    :type verbose: bool | int
    """

    json_filename = "location-names-repl{}.json".format("" if not regex else "-regex")

    new_items_keys = list(new_items.keys())

    if confirmed(f"To update \"{json_filename}\" with {{\"{new_items_keys[0]}\"... }}?"):
        path_to_json = cd_data(json_filename)
        location_name_repl_dict = load_data(path_to_json)

        if any(isinstance(k, re.Pattern) for k in new_items_keys):
            new_items = {k.pattern: v for k, v in new_items.items() if isinstance(k, re.Pattern)}

        location_name_repl_dict.update(new_items)

        save_data(location_name_repl_dict, path_to_json, verbose=verbose)


def save_data_to_file(cls, data, data_name, ext, dump_dir=None, verbose=False, **kwargs):
    """
    Save the collected data as a file, depending on the given parameters.

    :param cls: (an instance of) a class for a certain data cluster
    :type cls: object
    :param data: data collected for a certain cluster
    :type data: pandas.DataFrame | list | dict
    :param data_name: key to the dict-type data of a certain cluster
    :type data_name: str
    :param ext: whether to save the data as a file, or file extension
    :type ext: bool | str
    :param dump_dir: pathname of a directory where the data file is to be dumped, defaults to ``None``
    :type dump_dir: str | None
    :param verbose: whether to print relevant information in console, defaults to ``False``
    :type verbose: bool | int
    :param kwargs: [optional] parameters of the function `pyhelpers.store.save_data()`_

    .. _`pyhelpers.store.save_data()`:
        https://pyhelpers.readthedocs.io/en/latest/_generated/pyhelpers.store.save_data.html
    """

    data_has_contents = bool(data) if not isinstance(data, pd.DataFrame) else True

    if data_has_contents:
        if isinstance(ext, str):
            file_ext = "." + ext if not ext.startswith(".") else copy.copy(ext)
        else:
            file_ext = ".pkl"

        path_to_file = make_file_pathname(cls=cls, data_name=data_name, ext=file_ext, data_dir=dump_dir)

        kwargs.update({'data': data, 'path_to_file': path_to_file, 'verbose': verbose})
        save_data(**kwargs)

    else:
        print_void_msg(data_name=data_name, verbose=verbose)


def fetch_data_from_file(cls, method, data_name, ext, update, dump_dir, verbose, data_dir=None,
                         save_data_kwargs=None, **kwargs):
    """
    Fetch/load desired data from a backup file, depending on the given parameters.

    :param cls: (an instance of) a class for a certain data cluster
    :type cls: object
    :param method: name of a method of the ``cls``, which is used for collecting the data
    :type method: str
    :param data_name: key to the dict-type data of a certain cluster
    :type data_name: str
    :param ext: whether to save the data as a file, or file extension
    :type ext: bool | str
    :param update: whether to do an update check (for the package data), defaults to ``False``
    :type update: bool
    :param dump_dir: pathname of a directory where the data file is to be dumped, defaults to ``None``
    :type dump_dir: str | os.PathLike[str] | None
    :param verbose: whether to print relevant information in console
    :type verbose: bool | int
    :param data_dir: pathname of a directory where the data is fetched, defaults to ``None``
    :type data_dir: str | os.PathLike[str] | None
    :param save_data_kwargs: equivalent of ``kwargs`` used by the function
        :func:`pyrcs.utils.save_data_to_file`, defaults to ``None``
    :type save_data_kwargs: dict | None
    :param kwargs: [optional] parameters of the ``cls``.``method`` being called
    :type kwargs: typing.Any
    :return: data fetched for the desired cluster
    :rtype: dict | None
    """

    try:
        path_to_file = make_file_pathname(cls=cls, data_name=data_name, ext=ext, data_dir=data_dir)
        if os.path.isfile(path_to_file) and not update:
            data = load_data(path_to_file)

        else:
            verbose_ = collect_in_fetch_verbose(data_dir=dump_dir, verbose=verbose)

            kwargs.update({'confirmation_required': False, 'verbose': verbose_})
            data = getattr(cls, method)(**kwargs)

        if dump_dir is not None:
            if save_data_kwargs is None:
                save_data_kwargs = {}

            save_data_to_file(
                cls=cls, data=data, data_name=data_name, ext=ext, dump_dir=dump_dir, verbose=verbose,
                **save_data_kwargs)

    except Exception as e:
        if verbose:
            print(f"Some errors occurred when fetching the data. {format_err_msg(e)}")

        data = None

    return data
