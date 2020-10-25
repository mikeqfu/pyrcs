===========
Quick start
===========

To demonstrate how PyRCS works, this part of the documentation provides a quick guide with examples of getting `location codes <http://www.railwaycodes.org.uk/crs/CRS0.shtm>`_, `ELRs <http://www.railwaycodes.org.uk/elrs/elr0.shtm>`_ and `railway stations data <http://www.railwaycodes.org.uk/stations/station0.shtm>`_.


.. _qs-crs-nlc-tiploc-and-stanox:

Get location codes
==================

The location codes (including CRS, NLC, TIPLOC and STANOX) are categorised as `line data`_. Import the class :py:class:`LocationIdentifiers()<loc_id.LocationIdentifiers>` as follows:

.. code-block:: python

    >>> from pyrcs.line_data import LocationIdentifiers

    >>> # Or simply
    >>> # from pyrcs import LocationIdentifiers

Now we can create an instance for getting the location codes:

.. code-block:: python

    >>> lid = LocationIdentifiers()

.. note::

    An alternative way of creating the instance is through the class :ref:`LineData()<_line_data>` (see below).

.. code-block:: python

    >>> from pyrcs import LineData

    >>> ld = LineData()
    >>> lid_ = ld.LocationIdentifiers

.. note::

    The instance ``ld`` contains all classes under the category of `line data`_. Here ``lid_`` is equivalent to ``lid``.

.. _qs-locations-beginning-with-a-given-letter:

Get location codes for a given initial letter
---------------------------------------------

By using the method :py:meth:`LocationIdentifiers.collect_loc_codes_by_initial()<loc_id.LocationIdentifiers.collect_loc_codes_by_initial>`, we can get the location codes that start with a specific letter, say ``'A'`` or ``'a'``:

.. code-block:: python

    >>> # The input is case-insensitive
    >>> loc_codes_a = lid.collect_loc_codes_by_initial('A')

    >>> type(loc_codes_a)
    <class 'dict'>
    >>> print(list(loc_codes_a.keys()))
    ['A', 'Additional notes', 'Last updated date']

``loc_codes_a`` is a dictionary (i.e. in `dict`_ type), with the following keys:

-  ``'A'``
-  ``'Additional notes'``
-  ``'Last updated date'``

Their corresponding values are

-  ``loc_codes_a['A']``: a `pandas.DataFrame`_ of the location codes that begin with 'A'. We may compare it with the table on the web page of `Locations beginning with 'A'`_;
-  ``loc_codes_a['Additional notes']``: some additional information on the web page (if available);
-  ``loc_codes_a['Last updated date']``: the date when the web page was last updated.

.. _qs-all-available-location-codes:

Get all available location codes
--------------------------------

To get all available location codes in this category, use the method :py:class:`LocationIdentifiers.fetch_location_codes()<loc_id.LocationIdentifiers.fetch_location_codes>`:

.. code-block:: python

    >>> loc_codes = lid.fetch_location_codes()

    >>> type(loc_codes)
    <class 'dict'>
    >>> print(list(loc_codes.keys()))
    ['Location codes', 'Other systems', 'Additional notes', 'Last updated date']

``loc_codes`` is also a dictionary, of which the keys are as follows:

-  ``'Location codes'``
-  ``'Other systems'``
-  ``'Additional notes'``
-  ``'Latest update date'``

Their corresponding values are

-  ``loc_codes['Location codes']``: a `pandas.DataFrame`_ of all location codes (from 'A' to 'Z');
-  ``loc_codes['Other systems']``: a dictionary for `other systems`_;
-  ``loc_codes['Additional notes']``: some additional information on the web page (if available);
-  ``loc_codes['Latest update date']``: the latest ``'Last updated date'`` among all initial letter-specific codes.


.. _qs-elrs:

Get ELRs and mileages
=====================

To get `ELRs (Engineer's Line References) and mileages`_, use the class :py:class:`ELRMileages()<elr_mileage.ELRMileages>`:

.. code-block:: python

    >>> from pyrcs.line_data import ELRMileages
    >>> # Or simply
    >>> # from pyrcs import ELRMileages

    >>> em = ELRMileages()

.. _qs-elr-codes:

Get ELR codes
-------------

To get ELR codes which start with ``'A'``, use the method :py:meth:`ELRMileages.collect_elr_by_initial()<elr_mileage.ELRMileages.collect_elr_by_initial>`, which returns a dictionary:

.. code-block:: python

    >>> elrs_a = em.collect_elr_by_initial('A')

    >>> type(elrs_a)
    <class 'dict'>
    >>> print(list(elrs_a.keys()))
    ['A', 'Last updated date']

The keys of ``elrs_a`` include:

-  ``'A'``
-  ``'Last updated date'``

Their corresponding values are

-  ``elrs_a['A']``: a `pandas.DataFrame`_ of ELRs that begin with 'A'. We may compare it with the table on the web page of `ELRs beginning with 'A'`_;
-  ``elrs_a['Last updated date']``: the date when the web page was last updated.

To get all available ELR codes, use the method :py:meth:`ELRMileages.fetch_elr()<elr_mileage.ELRMileages.fetch_elr>`, which also returns a dictionary:

.. code-block:: python

    >>> elrs_dat = em.fetch_elr()

    >>> type(elrs_dat)
    <class 'dict'>
    >>> print(list(elrs_dat.keys()))
    ['ELRs', 'Last updated date']

The keys of ``elrs_dat`` include:

-  ``'ELRs'``
-  ``'Latest update date'``

Their corresponding values are

-  ``elrs_dat['ELRs']``: a `pandas.DataFrame`_ of all available ELRs (from 'A' to 'Z');
-  ``elrs_dat['Latest update date']``: the latest ``'Last updated date'`` among all initial letter-specific codes.

.. _qs-mileage-files:

Get mileage data for a given ELR
--------------------------------

To get detailed mileage data for a given ELR, for example, `AAM`_, use the method :py:meth:`ELRMileages.fetch_mileage_file()<elr_mileage.ELRMileages.fetch_mileage_file>`, which returns a dictionary as well:

.. code-block:: python

    >>> em_amm = em.fetch_mileage_file('AAM')

    >>> type(em_amm)
    <class 'dict'>
    >>> print(list(em_amm.keys()))
    ['ELR', 'Line', 'Sub-Line', 'Mileage', 'Notes']

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


.. _qs-railway-stations-data:

Get railway stations data
=========================

The `railway station data`_ (incl. the station name, ELR, mileage, status, owner, operator, degrees of longitude and latitude, and grid reference) is categorised into `other assets`_ in the source data.

.. code-block:: python

    >>> from pyrcs.other_assets import Stations
    >>> # Or simply
    >>> # from pyrcs import Stations

    >>> stn = Stations()

.. note::

    Alternatively, the instance ``stn`` can also be defined through :ref:`OtherAssets()<_other_assets>` that contains all classes under the category of `other assets`_ (see below).

.. code-block:: python

    >>> from pyrcs import OtherAssets

    >>> oa = OtherAssets()
    >>> stn_ = oa.Stations

.. note::

    ``stn_`` is equivalent to ``stn``.

To get the data of railway stations whose names start with a specific letter, e.g. ``'A'``, use the method :py:meth:`Stations.collect_railway_station_data_by_initial()<station.Stations.collect_railway_station_data_by_initial>`:

.. code-block:: python

    >>> stn_data_a = stn.collect_railway_station_data_by_initial('A')

    >>> type(stn_data_a)
    <class 'dict'>
    >>> print(list(stn_data_a.keys()))
    ['A', 'Last updated date']

The keys of ``stn_data_a`` include:

-  ``'A'``
-  ``'Last updated date'``

The corresponding values are

-  ``stn_data_a['A']``: a `pandas.DataFrame`_ of the data of railway stations whose names begin with 'A'. We may compare it with the table on the web page of `Stations beginning with 'A'`_;
-  ``stn_data_a['Last updated date']``: the date when the web page was last updated.

To get available railway station data (from 'A' to 'Z') in this category, use the method :py:meth:`Stations.fetch_railway_station_data()<station.Stations.fetch_railway_station_data>`

.. code-block:: python

    >>> stn_data = stn.fetch_railway_station_data()

    >>> type(stn_data)
    <class 'dict'>
    >>> print(list(stn_data.keys()))
    ['Railway station data', 'Last updated date']

The keys of ``stn_data`` include:

-  ``'Railway station data'``
-  ``'Latest update date'``

Their corresponding values are

-  ``stn_data['Railway station data']``: a `pandas.DataFrame`_ of available railway station data (from 'A' to 'Z');
-  ``stn_data['Latest update date']``: the latest ``'Last updated date'`` among all initial letter-specific codes.

.. _`line data`: http://www.railwaycodes.org.uk/linedatamenu.shtm
.. _`CRS, NLC, TIPLOC and STANOX codes`: http://www.railwaycodes.org.uk/crs/CRS0.shtm
.. _`Locations beginning with 'A'`: http://www.railwaycodes.org.uk/crs/CRSa.shtm
.. _`other systems`: http://www.railwaycodes.org.uk/crs/CRS1.shtm
.. _`ELRs (Engineer's Line References) and mileages`: http://www.railwaycodes.org.uk/elrs/elr0.shtm
.. _`ELRs beginning with 'A'`: http://www.railwaycodes.org.uk/elrs/elra.shtm
.. _`AAM`: http://www.railwaycodes.org.uk/elrs/_mileages/a/aam.shtm
.. _`other assets`: http://www.railwaycodes.org.uk/otherassetsmenu.shtm
.. _`railway station data`: http://www.railwaycodes.org.uk/stations/station0.shtm
.. _`Stations beginning with 'A'`: http://www.railwaycodes.org.uk/stations/stationa.shtm
.. _`dict`: https://docs.python.org/3/library/stdtypes.html#dict
.. _`pandas.DataFrame`: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html

**(The end of the quick start)**


For more details and examples, check :ref:`Sub-packages and modules<modules>`.
