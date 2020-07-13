.. _pyrcs-utils:

.. py:module:: pyrcs.utils

utils
-----

A module of helper functions.

Source homepage
~~~~~~~~~~~~~~~

.. autosummary::

   homepage_url

.. autofunction:: homepage_url


Directory
~~~~~~~~~

.. autosummary::

   cd_dat

.. autofunction:: cd_dat

Converters
~~~~~~~~~~

.. autosummary::

   mile_chain_to_nr_mileage
   nr_mileage_to_mile_chain
   nr_mileage_str_to_num
   nr_mileage_num_to_str
   nr_mileage_to_yards
   yards_to_nr_mileage
   shift_num_nr_mileage
   year_to_financial_year

.. autofunction:: mile_chain_to_nr_mileage

.. autofunction:: nr_mileage_to_mile_chain

.. autofunction:: nr_mileage_str_to_num

.. autofunction:: nr_mileage_num_to_str

.. autofunction:: nr_mileage_to_yards

.. autofunction:: yards_to_nr_mileage

.. autofunction:: shift_num_nr_mileage

.. autofunction:: year_to_financial_year

Parsers
~~~~~~~

.. autosummary::

   parse_tr
   parse_table
   parse_location_name
   parse_date

.. autofunction:: parse_tr

.. autofunction:: parse_table

.. autofunction:: parse_location_name

.. autofunction:: parse_date

Get useful information
~~~~~~~~~~~~~~~~~~~~~~

.. autosummary::

   fake_requests_headers
   get_last_updated_date
   get_catalogue
   get_category_menu

.. autofunction:: fake_requests_headers

.. autofunction:: get_last_updated_date

.. autofunction:: get_catalogue

.. autofunction:: get_category_menu

Rectification of location names
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autosummary::

   fetch_location_names_repl_dict
   update_location_name_repl_dict

.. autofunction:: fetch_location_names_repl_dict

.. autofunction:: update_location_name_repl_dict

Fixers
~~~~~~

.. autosummary::

   fix_num_stanox

.. autofunction:: fix_num_stanox

Misc
~~~~

.. autosummary::

   is_str_float

.. autofunction:: is_str_float
