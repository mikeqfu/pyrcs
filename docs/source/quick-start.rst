===========
Quick start
===========

**This part of the documentation provides a quick guide and a few examples to demonstrate how PyRCS works.**

- :ref:`Get location codes: CRS, NLC, TIPLOC and STANOX<qs-crs-nlc-tiploc-and-stanox>`
    - :ref:`Location codes for a given initial letter<qs-locations-beginning-with-a-given-letter>`
    - :ref:`All available location codes<qs-all-available-location-codes>`
- :ref:`Get ELRs and mileages<qs-elrs>`
    - :ref:`ELR codes<qs-elr-codes>`
    - :ref:`Mileage files<qs-mileage-files>`
- :ref:`Get railway stations data<qs-railway-stations-data>`

|

.. _qs-crs-nlc-tiploc-and-stanox:

Get location codes
------------------

.. code-block:: python

   >>> from pyrcs.line_data import LocationIdentifiers

After importing the module, you can create an instance for getting the location codes:

.. code-block:: python

   >>> lid = LocationIdentifiers()

.. note::

   An alternative way of creating the instance is through :ref:`pyrcs._line_data.LineData()<pyrcs-_line-data>`:

    .. code-block:: python

        >>> from pyrcs._line_data import LineData

        >>> ld = LineData()
        >>> lid = ld.LocationIdentifiers

    The instance ``ld`` contains all classes under the category of `line data`_. In that way, ``ld.LocationIdentifiers`` is equivalent to ``lid``.

.. _qs-locations-beginning-with-a-given-letter:

For a given initial letter
~~~~~~~~~~~~~~~~~~~~~~~~~~

By using the method :ref:`collect_location_codes_by_initial()<cnts-collect-location-codes-by-initial>`, you can get the location codes that start with a specific letter, say ``'A'`` or ``'a'``:

.. code-block:: python

   # The input is case-insensitive
   >>> location_codes_a = lid.collect_location_codes_by_initial('A')

``location_codes_a`` is a dictionary (in `dict`_ type), with the following keys:

-  ``'A'``
-  ``'Additional notes'``
-  ``'Last updated date'``

Their corresponding values are

-  ``location_codes_a['A']``: a `pandas.DataFrame`_ of the location codes that begin with 'A'. You may compare it with the table on the web page of `Locations beginning with 'A' <http://www.railwaycodes.org.uk/crs/CRSa.shtm>`_;
-  ``location_codes_a['Additional notes']``: some additional information on the web page (if available);
-  ``location_codes_a['Last updated date']``: the date when the web page was last updated.

.. _qs-all-available-location-codes:

For all location codes
~~~~~~~~~~~~~~~~~~~~~~

To get all available location codes in this category, use the method :ref:``.fetch_location_codes()<cnts-fetch-location-codes>``:

.. code-block:: python

   >>> location_codes = lid.fetch_location_codes()

This method also returns a dictionary, ``location_codes_a``, of which the keys are as follows:

-  ``'Location codes'``
-  ``'Other systems'``
-  ``'Additional notes'``
-  ``'Latest update date'``

Their corresponding values are

-  ``location_codes['Location codes']``: a `pandas.DataFrame`_ of all location codes (from 'A' to 'Z');
-  ``location_codes['Other systems']``: a dictionary for `other systems`_;
-  ``location_codes['Additional notes']``: some additional information on the web page (if available);
-  ``location_codes['Latest update date']``: the latest ``'Last updated date'`` among all initial letter-specific codes.

|

.. _qs-elrs:

Get ELRs and mileages
---------------------

To get `ELRs (Engineer's Line References) and mileages`_, use the class :ref:`pyrcs.line_data.ELRMileages()<ld-elrs-mileages>`:

.. code-block:: python

   >>> from pyrcs.line_data import ELRMileages

   >>> em = ELRMileages()

.. _qs-elr-codes:

Get ELR codes
~~~~~~~~~~~~~

To get ELR codes which start with ``'A'``, use the method :ref:`.collect_elr_by_initial()<em-collect-elr-by-initial>`:

.. code-block:: python

   >>> elrs_a = em.collect_elr_by_initial('A')

The keys of ``elrs_a`` include:

-  ``'A'``
-  ``'Last updated date'``

Their corresponding values are

-  ``elrs_a['A']``: a `pandas.DataFrame`_ of ELRs that begin with 'A'. You may compare it with the table on the web page of `ELRs beginning with 'A' <http://www.railwaycodes.org.uk/elrs/elra.shtm>`_;
-  ``elrs_a['Last updated date']``: the date when the web page was last updated.

To get all available ELR codes, use the method :ref:``.fetch_elr()<em-fetch-elr>``, which also returns a dictionary:

.. code-block:: python

   >>> elrs_data = em.fetch_elr()

The keys of ``elrs_data`` include:

-  ``'ELRs'``
-  ``'Latest update date'``

Their corresponding values are

-  ``elrs_data['ELRs']``: a ``pandas.DataFrame`` of all available ELRs (from 'A' to 'Z');
-  ``elrs_data['Latest update date']``: the latest `Last updated date` among all initial letter-specific codes.

.. _qs-mileage-files:

Get mileage files
~~~~~~~~~~~~~~~~~

To get detailed mileage data for a given ELR, for example, `AAM`_, use the method :ref:``.fetch_mileage_file()<em-fetch-mileage-file>``, which returns a dictionary as well:

.. code-block:: python

   >>> em_amm = em.fetch_mileage_file('AAM')

The keys of ``em_amm`` include:

-  ``'ELR'``
-  ``'Line'``
-  ``'Sub-Line'``
-  ``'AAM'``
-  ``'Notes'``

Their corresponding values are

-  ``em_amm['ELR']``: the name of the given ELR (which in this example is 'AAM');
-  ``em_amm['Line']``: the associated line name;
-  ``em_amm['Sub-Line']``: the associated sub line name (if available);
-  ``em_amm['AAM']``: a `pandas.DataFrame`_ of the mileage file data;
-  ``em_amm['Notes']``: additional information/notes (if any).

|

.. _qs-railway-stations-data:

Get railway stations data
-------------------------

The `railway station data`_ (incl. the station name, ELR, mileage, status, owner, operator, degrees of longitude and latitude, and grid reference) is categorised into `other assets`_ in the source data. To get the data of railway stations whose names start with a specific letter, e.g. ``'A'``, use the method :ref:`.collect_railway_station_data_by_initial()<stations-collect-railway-station-data-by-initial>`:

.. code-block:: python

   >>> from pyrcs.other_assets import Stations

   >>> stations = Stations()
   >>> railway_station_data_a = stations.collect_railway_station_data_by_initial('A')

.. note::

   Alternatively, the class ``stations`` can also be defined in the following way:

    .. code-block:: python

        >>> from pyrcs._other_assets import OtherAssets

        >>> other_assets = OtherAssets()
        >>> stations = other_assets.Stations

Like ``elrs_data`` above, yhe keys of ``railway_station_data_a`` include:

-  ``'A'``
-  ``'Last updated date'``

The corresponding values are

-  ``railway_station_data_a['A']``: a `pandas.DataFrame`_ of the data of railway stations whose names begin with 'A'. You may compare it with the table on the web page of `Stations beginning with 'A' <http://www.railwaycodes.org.uk/stations/station0.shtm>`_;
-  ``railway_station_data_a['Last updated date']``: the date when the web page was last updated.

To get available railway station data (from 'A' to 'Z') in this category, use the method :ref:`.fetch_railway_station_data()<stations-fetch-railway-station-data>`

.. code-block:: python

   >>> railway_station_data = stations.fetch_railway_station_data()

The keys of ``railway_station_data`` include:

-  ``'Railway station data'``
-  ``'Latest update date'``

Their corresponding values are

-  ``railway_station_data['Railway station data']``: a ``pandas.DataFrame`` of available railway station data (from 'A' to 'Z');
-  ``railway_station_data['Latest update date']``: the latest `Last updated date` among all initial letter-specific codes.

.. _`line data`: http://www.railwaycodes.org.uk/linedatamenu.shtm
.. _`CRS, NLC, TIPLOC and STANOX codes`: http://www.railwaycodes.org.uk/crs/CRS0.shtm
.. _`other systems`: http://www.railwaycodes.org.uk/crs/CRS1.shtm
.. _`ELRs (Engineer's Line References) and mileages`: http://www.railwaycodes.org.uk/elrs/elr0.shtm
.. _`AAM`: http://www.railwaycodes.org.uk/elrs/_mileages/a/aam.shtm
.. _`other assets`: http://www.railwaycodes.org.uk/otherassetsmenu.shtm
.. _`railway station data`: http://www.railwaycodes.org.uk/stations/station0.shtm
.. _`dict`: https://docs.python.org/3/library/stdtypes.html#dict
.. _`pandas.DataFrame`: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html
