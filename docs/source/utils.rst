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
    make_file_pathname

Converters
~~~~~~~~~~

.. autosummary::
    :toctree: _generated/
    :template: function.rst

    fix_stanox
    fix_mileage
    kilometer_to_yard
    yard_to_mileage
    mileage_to_yard
    mile_chain_to_mileage
    mileage_to_mile_chain
    mile_yard_to_mileage
    mileage_str_to_num
    mileage_num_to_str
    shift_mileage_by_yard
    get_financial_year

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
    get_heading_text
    get_page_catalogue
    get_hypertext
    get_introduction

Data checkers and rectification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. rubric:: Data rectification
.. autosummary::
    :toctree: _generated/
    :template: function.rst

    fetch_loc_names_repl_dict
    is_str_float
    validate_initial

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
