"""
This module provides the foundational class for managing data persistence, including
saving, loading and fetching data from files. It standardises file naming conventions,
handles directory management and supports verbose logging for debugging.
"""

import copy
import inspect
import os

import pandas as pd
import requests
from pyhelpers._cache import _print_failure_message
from pyhelpers.dirs import cd, validate_dir
from pyhelpers.ops import confirmed, fake_requests_headers
from pyhelpers.store import load_data, save_data

from .parser import get_catalogue, get_introduction, get_last_updated_date
from .utils import cd_data, collect_in_fetch_verbose, format_confirmation_prompt, home_page_url, \
    print_collect_msg, print_conn_err, print_inst_conn_err, print_void_msg


class _Base:

    #: The name of the data.
    NAME: str = 'Railway Codes and other data'
    #: The key for accessing the data.
    KEY: str = ''
    #: The URL of the main web page for the data.
    URL: str = home_page_url()
    #: The key used to reference the last updated date in the data.
    KEY_TO_LAST_UPDATED_DATE: str = 'Last updated date'

    def __init__(self, data_dir=None, content_type=None, data_category="", data_cluster=None,
                 update=False, verbose=True):
        """
        Initialises the base class for handling railway codes and related data.

        :param data_dir: Path to the directory where the data is stored; defaults to ``None``.
        :type data_dir: str | None
        :param content_type: Type of content to process, defaults to ``None``.
            Valid options (case-insensitive):

            - ``'catalogue'``, ``'catalog'``, or ``'cat'`` for catalogue-related content.
            - ``'introduction'`` or ``'intro'`` for introductory content.

        :type content_type: str | None
        :param data_category: Category to which the data belongs; defaults to ``''``.
        :type data_category: str
        :param data_cluster: Optional override for ``KEY`` to specify a different subdirectory name.
        :type data_cluster: str | None
        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``True``.
        :type verbose: bool | int

        :ivar dict | None catalogue: Dictionary containing catalogue data
            (if ``content_type='catalogue'``).
        :ivar str | None introduction: Introduction text (if ``content_type='introduction'``).
        :ivar str last_updated_date: The date when the data was last updated.
        :ivar str data_dir: The path to the directory containing the data.
        :ivar str current_data_dir: The specific directory being used for the current operation.

        **Examples**::

            >>> from pyrcs._base import _Base
            >>> _b = _Base()
            >>> _b.NAME
            'Railway Codes and other data'
            >>> _b.URL
            'http://www.railwaycodes.org.uk/'
        """

        print_conn_err(verbose=verbose)

        self.catalogue, self.introduction = None, None

        verbose_ = True if verbose == 2 else False

        if isinstance(content_type, str):
            content_type_ = content_type.lower()

            if content_type_.startswith('cat'):  # Get the catalogue of the data
                self.catalogue = get_catalogue(url=self.URL, update=update, verbose=verbose_)

            elif content_type_.startswith('intro'):  # Get the introductory text of the data
                self.introduction = get_introduction(url=self.URL, verbose=verbose_)

        elif content_type is True:  # Get both the catalogue and introductory text of the data
            self.catalogue = get_catalogue(url=self.URL, update=update, verbose=verbose_)

            self.introduction = get_introduction(url=self.URL, verbose=verbose_)

        self.last_updated_date = get_last_updated_date(url=self.URL)

        # Initialise the data directory for storing or retrieving data
        self.data_dir, self.current_data_dir = self._setup_data_dir(
            data_dir=data_dir, category=data_category, cluster=data_cluster)

    def _setup_data_dir(self, data_dir, category, cluster=None, **kwargs):
        # noinspection PyShadowingNames
        """
        Specifies the initial data directory for a class instance to manage a specific data cluster.

        :param data_dir: The base directory where data files (e.g. pickle files) will be stored.
        :type data_dir: str | None
        :param category: The data category (e.g. ``"line-data"``).
        :type category: str
        :param cluster: Optional override for ``KEY`` to specify a different subdirectory name.
        :type cluster: str | None
        :param kwargs: [Optional] Additional parameters passed to :func:`~pyrcs.utils.cd_data`.
        :return: A tuple containing the default data directory path and
            the current data directory path.
        :rtype: tuple[str, str]

        **Examples**::

            >>> from pyrcs._base import _Base
            >>> import os
            >>> _b = _Base()
            >>> data_dir, current_data_dir = _b._setup_data_dir("data", category="line-data")
            >>> assert data_dir == _b.data_dir
            >>> os.path.relpath(data_dir)
            'data'
            >>> assert current_data_dir == _b.current_data_dir
            >>> os.path.relpath(current_data_dir)
            'data'
        """

        if data_dir:
            self.data_dir = validate_dir(data_dir)

        else:
            cluster_ = self.KEY if cluster is None else copy.copy(cluster)
            self.data_dir = cd_data(category, cluster_.lower().replace(" ", "-"), **kwargs)

        self.current_data_dir = copy.copy(self.data_dir)

        return self.data_dir, self.current_data_dir

    def _cdd(self, *sub_dir, mkdir=True, **kwargs):
        """
        Changes the current directory to the package's data directory,
        or its specified subdirectories (or file).

        The default data directory is: ``"data\\<data_category>\\<data_name>"``.

        :param sub_dir: One or more subdirectories and/or a file to navigate to
            within the data directory.
        :type sub_dir: str
        :param mkdir: Whether to create the specified directory if it doesn't exist;
            defaults to ``True``.
        :type mkdir: bool
        :param kwargs: [Optional] Additional parameters for the `pyhelpers.dir.cd()`_ function.
        :return: The path to the backup data directory or its specified subdirectories (or file).
        :rtype: str

        .. _`pyhelpers.dir.cd()`:
            https://pyhelpers.readthedocs.io/en/latest/_generated/pyhelpers.dir.cd.html

        **Examples**::

            >>> from pyrcs._base import _Base
            >>> import os
            >>> _b = _Base()
            >>> os.path.relpath(_b._cdd())
            'pyrcs\\data'
        """

        path = cd(self.data_dir, *sub_dir, mkdir=mkdir, **kwargs)

        return path

    @staticmethod
    def _format_confirmation_message(data_name, confirmation_prompt=None, initial=None, **kwargs):
        """
        Generates a confirmation prompt message.

        :param confirmation_prompt: A custom confirmation message
            or a callable function that generates one.
        :type confirmation_prompt: str | typing.Callable | None
        :param data_name: The name of the data being confirmed
            (passed to the prompt function if callable).
        :type data_name: str
        :return: The generated confirmation prompt as a string.
        :rtype: str
        """

        if confirmation_prompt:
            if isinstance(confirmation_prompt, str):
                prompt = confirmation_prompt
            else:
                assert callable(confirmation_prompt)
                if 'initial' in inspect.signature(confirmation_prompt).parameters:
                    kwargs.update({'initial': initial})
                prompt = confirmation_prompt(data_name, **kwargs)

        else:
            prompt = format_confirmation_prompt(data_name=data_name, initial=initial)

        return prompt

    def _fallback_data(self, key=None, additional_fields=None):
        """
        Creates a fallback data dictionary in case of failure.
        """

        if not key:
            return None

        data = {key: None, self.KEY_TO_LAST_UPDATED_DATE: None}

        if additional_fields:
            if isinstance(additional_fields, dict):
                data.update(additional_fields)
            else:
                data.update({additional_fields: None})

        return data

    def _collect_data_from_source(self, data_name, method, url=None, initial=None,
                                  additional_fields=None, confirmation_required=True,
                                  confirmation_prompt=None, verbose=False, raise_error=False,
                                  **kwargs):
        """
        Collects data from the specified source webpage(s).

        :param data_name: Name of the data to be collected.
        :type data_name: str
        :param url: URL of the webpage from which the data will be collected.
        :type url: str
        :param method: A callable function or method used to parse and extract data from the
            webpage. This function should accept the following parameters:

            - ``source``: The response object from the HTTP request.
            - ``verbose``: Whether to print additional information during extraction.

        :type method: typing.Callable
        :param initial: The initial letter of the desired code or data; defaults to ``None``.
        :type initial: str | None
        :param additional_fields: Extra key-value pairs to be included in the returned dictionary
            if data collection fails or is canceled; defaults to ``None``.
        :type additional_fields: dict | str | None
        :param confirmation_required: Whether user confirmation is required;
            if ``confirmation_required=True`` (default), prompts the user for confirmation
            before proceeding with data collection.
        :type confirmation_required: bool
        :param confirmation_prompt:
        :type confirmation_prompt:
        :param verbose: Whether to print relevant information in the console; defaults to ``False``.
        :type verbose: bool | int
        :param raise_error: Whether to raise the provided exception;
            if ``raise_error=False`` (default), the error will be suppressed.
        :type raise_error: bool
        :return: The collected data.
        :rtype: pandas.DataFrame | dict | None
        """

        prompt = self._format_confirmation_message(
            data_name=data_name, confirmation_prompt=confirmation_prompt, initial=initial)

        if not confirmed(prompt=prompt, confirmation_required=confirmation_required):
            return None

        print_collect_msg(
            data_name=data_name, initial=initial, verbose=verbose,
            confirmation_required=confirmation_required)

        fallback_data = self._fallback_data(key=initial, additional_fields=additional_fields)

        url_ = copy.copy(url or self.catalogue.get(initial or data_name))
        if not url_:
            if initial and verbose:
                print(f'No data is available for codes beginning with "{initial}".')
            return fallback_data

        try:
            source = requests.get(url=url_, headers=fake_requests_headers())
            source.raise_for_status()  # Raises HTTPError for bad responses (4xx, 5xx)
        except Exception as e:
            print_inst_conn_err(verbose=verbose, e=e)
            return fallback_data

        # Build kwargs dynamically based on method signature
        kwargs.update({'source': source, 'verbose': verbose})

        for param in ('data_name', 'initial'):
            if param in inspect.signature(method).parameters:
                kwargs.update({param: locals()[param]})

        # Attempt method execution
        try:
            return method(**kwargs)
        except Exception as e:
            _print_failure_message(
                e, prefix="Failed. Error:", verbose=verbose, raise_error=raise_error)
            return fallback_data

    def _make_file_pathname(self, data_name, ext=".pkl", data_dir=None, sub_dir=None, **kwargs):
        """
        Generates a standardised file pathname for saving data.

        The method constructs a filename by converting the given ``data_name`` to lowercase
        and replacing spaces with hyphens. The filename is then appended with the specified
        file extension (``ext``). If a ``data_dir`` is provided, the file will be placed in that
        directory; otherwise, the default directory within the class will be used.

        :param data_name: The key identifying the data within a specific code cluster.
        :type data_name: str
        :param ext: The file extension (including the leading dot), defaults to ``".pkl"``.
        :type ext: str
        :param data_dir: The directory where the file will be saved; defaults to ``None``.
        :type data_dir: str | None
        :param sub_dir: A subdirectory name or a list of subdirectory names; defaults to ``None``.
        :type sub_dir: str | list | None
        :return: The pathname for saving the data file.
        :rtype: str

        **Examples**::

            >>> from pyrcs._base import _Base
            >>> import os
            >>> _b = _Base()
            >>> pathname = _b._make_file_pathname("example-data", ext=".pkl")
            >>> os.path.relpath(pathname)
            'pyrcs\\data\\example-data.pkl'
            >>> pathname = _b._make_file_pathname("example-data", ext=".json", sub_dir="a-z")
            >>> os.path.relpath(pathname)
            'pyrcs\\data\\a-z\\example-data.json'
        """

        filename = data_name.lower().replace(",", "").replace(" ", "-") + ext

        if sub_dir:
            sub_dir_ = [sub_dir] if isinstance(sub_dir, str) else sub_dir
        else:
            sub_dir_ = []

        if data_dir:
            self.current_data_dir = validate_dir(path_to_dir=data_dir)
            file_pathname = os.path.join(self.current_data_dir, *sub_dir_, filename)

        else:  # data_dir is None or data_dir == ""
            file_pathname = self._cdd(*sub_dir_, filename, **kwargs)

        return file_pathname

    def _save_data_to_file(self, data, data_name, ext=".pkl", dump_dir=None, sub_dir=None,
                           verbose=False, **kwargs):
        # noinspection PyShadowingNames
        """
        Saves the provided ``data`` to a file using the specified format and location.

        This method determines the appropriate file format and saves the ``data`` accordingly.
        If ``dump_dir`` is specified, the file will be saved there; otherwise, a default directory
        managed by the class is used. If ``verbose`` is set to ``True`` or ``2``, status messages
        will be printed to the console.

        :param data: The data to be saved.
        :type data: pandas.DataFrame | list | dict
        :param data_name: A unique identifier for the data.
        :type data_name: str
        :param ext: The file extension or a boolean indicating whether to save the data;
            defaults to ``".pkl"``.
        :type ext: str | bool
        :param dump_dir: The directory where the file should be saved;
            if ``None`` (default) a default directory within the class is used.
        :type dump_dir: str | None
        :param sub_dir: A subdirectory name or a list of subdirectory names; defaults to ``None``.
        :type sub_dir: str | list | None
        :param verbose: Whether to print detailed information to the console; defaults to ``False``.
        :type verbose: bool | int
        :param kwargs: [Optional] Additional parameters passed to `pyhelpers.store.save_data()`_.

        .. _`pyhelpers.store.save_data()`:
            https://pyhelpers.readthedocs.io/en/latest/_generated/pyhelpers.store.save_data.html

        **Examples**::

            >>> from pyrcs._base import _Base
            >>> from pyhelpers._cache import example_dataframe
            >>> import os
            >>> _b = _Base()
            >>> data = example_dataframe()
            >>> _b._save_data_to_file(data, data_name="Example data", ext=".csv", verbose=2)
            Saving "example-data.csv" to ".\\pyrcs\\data\\" ... Done.
            >>> example_filepath = "pyrcs\\data\\example-data.csv"
            >>> os.path.isfile(example_filepath)
            True
            >>> os.remove(example_filepath)
        """

        # Check if data has content
        data_has_contents = bool(data) if not isinstance(data, pd.DataFrame) else True

        if data_has_contents:
            # Ensure extension starts with '.'
            if isinstance(ext, str):
                file_ext = "." + ext if not ext.startswith(".") else copy.copy(ext)
            else:
                file_ext = ".pkl"

            path_to_file = self._make_file_pathname(
                data_name=data_name, ext=file_ext, data_dir=dump_dir, sub_dir=sub_dir)

            save_data(data=data, path_to_file=path_to_file, verbose=(verbose == 2), **kwargs)

        else:
            print_void_msg(data_name=data_name, verbose=verbose)

    def _fetch_data_from_file(self, data_name, method, ext=".pkl", update=False, dump_dir=None,
                              verbose=False, raise_error=False, data_dir=None, sub_dir=None,
                              save_data_kwargs=None, **kwargs):
        # noinspection PyShadowingNames
        """
        Fetches data from a stored file or generates it using the specified ``method``.

        This method attempts to load data from a backup file based on the provided parameters.
        If the file exists and ``update=False``, the data is loaded from the file. Otherwise, the
        ``method`` is called to generate the data, which can then be optionally saved to a specified
        directory (``dump_dir``).

        :param data_name: A unique identifier for the data, used to determine the filename.
        :type data_name: str
        :param method: A callable method that generates the data if the file does not exist
            or an update is required.
        :type method: typing.Callable
        :param ext: The file extension or a boolean indicating whether to save the data;
            defaults to ``".pkl"``.
        :type ext: bool | str
        :param update: Whether to perform an update check on the package data;
            defaults to ``False``.
        :type update: bool
        :param dump_dir: The directory where the file is stored or should be saved;
            defaults to ``None``.
        :type dump_dir: str | pathlib.Path | None
        :param verbose: Whether to print detailed information to the console; defaults to ``False``.
        :type verbose: bool | int
        :param data_dir: The directory where the data should be fetched from;
            if ``None``, the default data directory is used.
        :type data_dir: str | os.PathLike | None
        :param sub_dir: A subdirectory name or a list of subdirectory names; defaults to ``None``.
        :type sub_dir: str | list | None
        :param raise_error: Whether to raise the provided exception;
            if ``raise_error=False`` (default), the error will be suppressed.
        :type raise_error: bool
        :param save_data_kwargs: [Optional] Additional parameters for the
            :func:`pyrcs.utils.save_data_to_file` function; defaults to ``None``.
        :type save_data_kwargs: dict | None
        :param kwargs: [Optional] Additional parameters passed to ``method`` when generating data.
        :return: The fetched or generated data;
            returns ``None`` if an error occurs and  ``raise_error=False``.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs._base import _Base
            >>> from pyhelpers._cache import example_dataframe
            >>> import os
            >>> _b = _Base()
            >>> def create_example_dataframe(confirmation_required=False, verbose=False):
            ...     assert isinstance(confirmation_required, bool)
            ...     assert isinstance(verbose, (bool, int))
            ...     return example_dataframe()
            >>> data = _b._fetch_data_from_file("example-data", create_example_dataframe)
            >>> data
                        Longitude   Latitude
            City
            London      -0.127647  51.507322
            Birmingham  -1.902691  52.479699
            Manchester  -2.245115  53.479489
            Leeds       -1.543794  53.797418
        """

        try:
            # Generate the file path
            path_to_file = self._make_file_pathname(
                data_name=data_name, ext=ext, data_dir=data_dir, sub_dir=sub_dir)

            if os.path.isfile(path_to_file) and not update:  # Attempt to load existing data
                data = load_data(path_to_file, verbose=(verbose == 2))

            else:
                verbose_ = collect_in_fetch_verbose(data_dir=dump_dir, verbose=verbose)

                kwargs.update({'confirmation_required': False, 'verbose': verbose_})

                if isinstance(method, str):
                    data = getattr(self, method)(**kwargs)
                else:
                    data = method(**kwargs)

            if dump_dir:
                self._save_data_to_file(
                    data=data, data_name=data_name, ext=ext, dump_dir=dump_dir, sub_dir=sub_dir,
                    verbose=verbose, **(save_data_kwargs or {}))

            return data

        except Exception as e:
            _print_failure_message(e=e, prefix="Error:", verbose=verbose, raise_error=raise_error)
