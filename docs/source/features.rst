.. _oa-features:

.. py:module:: features

.. py:module:: pyrcs.other_assets
   :noindex:

Features
~~~~~~~~

A class for collecting infrastructure features, including `OLE neutral sections <http://www.railwaycodes.org.uk/electrification/neutral.shtm>`_, `HABD and WILD <http://www.railwaycodes.org.uk/misc/habdwild.shtm>`_, `water troughs <http://www.railwaycodes.org.uk/misc/troughs.shtm>`_, `telegraph codes <http://www.railwaycodes.org.uk/misc/telegraph.shtm>`_ and `driver/guard buzzer codes <http://www.railwaycodes.org.uk/misc/buzzer.shtm>`_.

.. autosummary::

   Features.decode_vulgar_fraction
   Features.parse_vulgar_fraction_in_length
   Features.collect_habds_and_wilds
   Features.fetch_habds_and_wilds
   Features.collect_water_troughs
   Features.fetch_water_troughs
   Features.collect_telegraph_codes
   Features.fetch_telegraph_codes
   Features.collect_buzzer_codes
   Features.fetch_buzzer_codes
   Features.fetch_features_codes

.. autoclass:: pyrcs.other_assets.Features

   .. automethod:: decode_vulgar_fraction

   .. automethod:: parse_vulgar_fraction_in_length

   .. automethod:: collect_habds_and_wilds

   .. automethod:: fetch_habds_and_wilds

   .. automethod:: collect_water_troughs

   .. automethod:: fetch_water_troughs

   .. automethod:: collect_telegraph_codes

   .. automethod:: fetch_telegraph_codes

   .. automethod:: collect_buzzer_codes

   .. automethod:: fetch_buzzer_codes

   .. automethod:: fetch_features_codes
