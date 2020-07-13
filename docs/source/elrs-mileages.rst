.. _ld-elrs-mileages:

.. py:module:: elrs_mileages

.. py:module:: pyrcs.line_data
   :noindex:

ELRMileages
~~~~~~~~~~~

A class for collecting `Engineer's Line References (ELRs) <http://www.railwaycodes.org.uk/elrs/elr0.shtm>`_ codes.

.. autosummary::

   ELRMileages.identify_multiple_measures
   ELRMileages.parse_mileage_data
   ELRMileages.collect_elr_by_initial
   ELRMileages.fetch_elr
   ELRMileages.collect_mileage_file_by_elr
   ELRMileages.fetch_mileage_file
   ELRMileages.search_conn
   ELRMileages.get_conn_mileages

.. autoclass:: pyrcs.line_data.ELRMileages

   .. automethod:: identify_multiple_measures

   .. automethod:: parse_mileage_data

   .. _em-collect-elr-by-initial:

   .. automethod:: collect_elr_by_initial

   .. _em-fetch-elr:

   .. automethod:: fetch_elr

   .. automethod:: collect_mileage_file_by_elr

   .. _em-fetch-mileage-file:

   .. automethod:: fetch_mileage_file

   .. automethod:: search_conn

   .. automethod:: get_conn_mileages
