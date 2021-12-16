utils
-----

.. py:module:: pyrcs.utils

.. automodule:: pyrcs.utils
    :noindex:
    :no-members:
    :no-undoc-members:
    :no-inherited-members:

Specifications
~~~~~~~~~~~~~~

.. autosummary::
    :toctree: _generated/
    :template: function.rst

    home_page_url
    init_data_dir
    make_pickle_pathname

Converters
~~~~~~~~~~

.. autosummary::
    :toctree: _generated/
    :template: function.rst

    mileage_str_to_num
    mileage_num_to_str
    mileage_to_yard
    yard_to_mileage
    mile_yard_to_mileage
    shift_mileage_by_yard
    mile_chain_to_mileage
    mileage_to_mile_chain
    get_financial_year
    fix_stanox
    fix_mileage

Parsers
~~~~~~~

.. autosummary::
    :toctree: _generated/
    :template: function.rst

    parse_tr
    parse_table
    parse_location_name
    parse_date

Assistant scrapers
~~~~~~~~~~~~~~~~~~

.. autosummary::
    :toctree: _generated/
    :template: function.rst

    get_site_map
    get_last_updated_date
    get_catalogue
    get_category_menu
    get_page_catalogue
    get_heading
    get_hypertext

Data checkers and rectification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. rubric:: Data rectification
.. autosummary::
    :toctree: _generated/
    :template: function.rst

    fetch_loc_names_repl_dict
    update_loc_names_repl_dict

.. rubric:: Network connections
.. autosummary::
    :toctree: _generated/
    :template: function.rst

    is_home_connectable
    print_connection_error
    print_conn_err

Miscellaneous helpers
~~~~~~~~~~~~~~~~~~~~~

.. autosummary::
    :toctree: _generated/
    :template: function.rst

    confirm_msg
    print_collect_msg
    print_void_msg
    collect_in_fetch_verbose
    fetch_all_verbose
    data_to_pickle
