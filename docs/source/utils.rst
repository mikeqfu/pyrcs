.. py:module:: pyrcs.utils

utils
-----

.. automodule:: pyrcs.utils
    :noindex:
    :no-members:
    :no-undoc-members:
    :no-inherited-members:

Specification of resource homepage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autosummary::
    :toctree: _generated/
    :template: function.rst

    homepage_url

Data converters
~~~~~~~~~~~~~~~

.. autosummary::
    :toctree: _generated/
    :template: function.rst

    mile_chain_to_nr_mileage
    nr_mileage_to_mile_chain
    nr_mileage_str_to_num
    nr_mileage_num_to_str
    nr_mileage_to_yards
    yards_to_nr_mileage
    shift_num_nr_mileage
    year_to_financial_year

Data parsers
~~~~~~~~~~~~

.. autosummary::
    :toctree: _generated/
    :template: function.rst

    parse_tr
    parse_table
    parse_location_name
    parse_date

Retrieval of useful information
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autosummary::
    :toctree: _generated/
    :template: function.rst

    get_site_map
    get_last_updated_date
    get_catalogue
    get_category_menu

Rectification of location names
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autosummary::
    :toctree: _generated/
    :template: function.rst

    fetch_loc_names_repl_dict
    update_loc_names_repl_dict

Data fixers
~~~~~~~~~~~

.. autosummary::
    :toctree: _generated/
    :template: function.rst

    fix_num_stanox
    fix_nr_mileage_str

Miscellaneous utilities
~~~~~~~~~~~~~~~~~~~~~~~

.. autosummary::
    :toctree: _generated/
    :template: function.rst

    print_connection_error
    print_conn_err
    is_str_float
    is_internet_connected
