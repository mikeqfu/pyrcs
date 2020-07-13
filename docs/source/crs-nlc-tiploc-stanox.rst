.. _ld-cnts:

.. py:module:: crs_nlc_tiploc_stanox

.. py:module:: pyrcs.line_data
   :noindex:

LocationIdentifiers
~~~~~~~~~~~~~~~~~~~

A class for collecting `CRS, NLC, TIPLOC and STANOX codes <http://www.railwaycodes.org.uk/crs/CRS0.shtm>`_.

.. autosummary::

   LocationIdentifiers.amendment_to_location_names_dict
   LocationIdentifiers.parse_additional_note_page
   LocationIdentifiers.collect_multiple_station_codes_explanatory_note
   LocationIdentifiers.fetch_multiple_station_codes_explanatory_note
   LocationIdentifiers.collect_other_systems_codes
   LocationIdentifiers.fetch_other_systems_codes
   LocationIdentifiers.collect_location_codes_by_initial
   LocationIdentifiers.fetch_location_codes
   LocationIdentifiers.make_location_codes_dictionary

.. autoclass:: pyrcs.line_data.LocationIdentifiers

   .. automethod:: amendment_to_location_names_dict

   .. automethod:: parse_additional_note_page

   .. automethod:: collect_multiple_station_codes_explanatory_note

   .. automethod:: fetch_multiple_station_codes_explanatory_note

   .. automethod:: collect_other_systems_codes

   .. automethod:: fetch_other_systems_codes

   .. _cnts-collect-location-codes-by-initial:

   .. automethod:: collect_location_codes_by_initial

   .. _cnts-fetch-location-codes:

   .. automethod:: fetch_location_codes

   .. automethod:: make_location_codes_dictionary
