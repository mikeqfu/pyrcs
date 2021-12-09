===========
Quick start
===========

To demonstrate how PyRCS works, this part of the documentation provides a quick guide with examples of getting `location codes <http://www.railwaycodes.org.uk/crs/CRS0.shtm>`_, Engineer's Line References `(ELRs) <http://www.railwaycodes.org.uk/elrs/elr0.shtm>`_ and `railway stations data <http://www.railwaycodes.org.uk/stations/station0.shtm>`_.


.. _qs-crs-nlc-tiploc-and-stanox:

Get location codes
==================

The location codes (including CRS, NLC, TIPLOC and STANOX) are categorised as `line data <http://www.railwaycodes.org.uk/linedatamenu.shtm>`_. Import the class :py:class:`LocationIdentifiers()<loc_id.LocationIdentifiers>` as follows:

.. code-block:: python

    >>> from pyrcs.line_data import LocationIdentifiers

    >>> # Or,
    >>> # from pyrcs import LocationIdentifiers

Now we can create an instance for getting the location codes:

.. code-block:: python

    >>> lid = LocationIdentifiers()

.. note::

    An alternative way of creating the instance is through the class :py:class:`LineData()<pyrcs.collector.LineData>` (see below).

.. code-block:: python

    >>> from pyrcs import LineData

    >>> ld = LineData()
    >>> lid_ = ld.LocationIdentifiers

.. note::

    The instance ``ld`` contains all classes under the category of `line data <http://www.railwaycodes.org.uk/linedatamenu.shtm>`_. Here ``lid_`` is equivalent to ``lid``.

.. _qs-locations-beginning-with-a-given-letter:

Get location codes for a given initial letter
---------------------------------------------

By using the method :py:meth:`LocationIdentifiers.collect_codes_by_initial()<loc_id.LocationIdentifiers.collect_codes_by_initial>`, we can get the location codes that start with a specific letter, say ``'A'`` or ``'a'``:

.. code-block:: python

    >>> # The input is case-insensitive
    >>> loc_codes_a = lid.collect_codes_by_initial('A')

    >>> type(loc_codes_a)
    dict
    >>> list(loc_codes_a.keys())
    ['A', 'Additional notes', 'Last updated date']

``loc_codes_a`` is a dictionary (i.e. `dict`_ type), with the following keys:

-  ``'A'``
-  ``'Additional notes'``
-  ``'Last updated date'``

Their corresponding values are

-  ``loc_codes_a['A']``: a data frame (in `pandas.DataFrame`_ type) of the location names that begin with 'A'. We may compare it with the table on the web page of `Locations beginning with 'A' <http://www.railwaycodes.org.uk/crs/CRSa.shtm>`_;
-  ``loc_codes_a['Additional notes']``: some additional information on the web page (if available);
-  ``loc_codes_a['Last updated date']``: the date when the web page was last updated.

Below is a snapshot of the codes of the location names beginning with 'A':

.. code-block:: python

    >>> loc_codes_a['A'].head()
                                   Location CRS  ... STANME_Note STANOX_Note
    0                                Aachen      ...
    1                    Abbeyhill Junction      ...
    2                 Abbeyhill Signal E811      ...
    3            Abbeyhill Turnback Sidings      ...
    4  Abbey Level Crossing (Staffordshire)      ...
    [5 rows x 12 columns]

    >>> print("Last updated date: {}".format(loc_codes_a['Last updated date']))
    Last updated date: 2021-03-21

.. _qs-all-available-location-codes:

Get all available location codes
--------------------------------

To get all available location codes in this category, use the method :py:class:`LocationIdentifiers.fetch_codes()<loc_id.LocationIdentifiers.fetch_codes>`:

.. code-block:: python

    >>> loc_codes = lid.fetch_codes()

    >>> type(loc_codes)
    dict
    >>> list(loc_codes.keys())
    ['Location codes', 'Other systems', 'Additional notes', 'Last updated date']

``loc_codes`` is also a dictionary, of which the keys are as follows:

-  ``'Location codes'``
-  ``'Other systems'``
-  ``'Additional notes'``
-  ``'Latest update date'``

Their corresponding values are

-  ``loc_codes['Location codes']``: a `pandas.DataFrame`_ of all location codes (from 'A' to 'Z');
-  ``loc_codes['Other systems']``: a dictionary for `other systems <http://www.railwaycodes.org.uk/crs/CRS1.shtm>`_;
-  ``loc_codes['Additional notes']``: some additional information on the web page (if available);
-  ``loc_codes['Latest update date']``: the latest ``'Last updated date'`` among all initial letter-specific codes.

Below is a snapshot of a random sample of the location codes data:

.. code-block:: python

    >>> loc_codes[lid.Key].head(10)
                                   Location  CRS  ... STANME_Note STANOX_Note
    0                                Aachen       ...
    1                    Abbeyhill Junction       ...
    2                 Abbeyhill Signal E811       ...
    3            Abbeyhill Turnback Sidings       ...
    4  Abbey Level Crossing (Staffordshire)       ...
    5                        Abbey Road DLR  ZAL  ...
    6                            Abbey Wood  ABW  ...
    7       Abbey Wood Alsike Road Junction       ...
    8                  Abbey Wood Crossrail  ABX  ...
    9           Abbey Wood Crossrail Siding       ...
    [10 rows x 12 columns]


.. _qs-elrs:

Get ELRs and mileages
=====================

To get `ELRs and mileages <http://www.railwaycodes.org.uk/elrs/elr0.shtm>`_, use the class :py:class:`ELRMileages()<elr_mileage.ELRMileages>`:

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
    dict
    >>> list(elrs_a.keys())
    ['A', 'Last updated date']

The keys of the dictionary ``elrs_a`` include:

-  ``'A'``
-  ``'Last updated date'``

Their corresponding values are

-  ``elrs_a['A']``: a data frame of ELRs that begin with 'A'. We may compare it with the table on the web page of `ELRs beginning with 'A' <http://www.railwaycodes.org.uk/elrs/elra.shtm>`_;
-  ``elrs_a['Last updated date']``: the date when the web page was last updated.

Below is a snapshot of the data of the ELR codes beginning with 'A':

.. code-block:: python

    >>> elrs_a['A'].head()
       ELR  ...         Notes
    0  AAL  ...      Now NAJ3
    1  AAM  ...  Formerly AML
    2  AAV  ...
    3  ABB  ...       Now AHB
    4  ABB  ...
    [5 rows x 5 columns]

    >>> print("Last updated date: {}".format(elrs_a['Last updated date']))
    Last updated date: 2020-10-27

To get all available ELR codes, use the method :py:meth:`ELRMileages.fetch_elr()<elr_mileage.ELRMileages.fetch_elr>`, which also returns a dictionary:

.. code-block:: python

    >>> elrs_dat = em.fetch_elr()

    >>> type(elrs_dat)
    dict
    >>> list(elrs_dat.keys())
    ['ELRs', 'Last updated date']

The keys of ``elrs_dat`` include:

-  ``'ELRs'``
-  ``'Latest update date'``

Their corresponding values are

-  ``elrs_dat['ELRs']``: a `pandas.DataFrame`_ of all available ELRs (from 'A' to 'Z');
-  ``elrs_dat['Latest update date']``: the latest ``'Last updated date'`` among all initial letter-specific codes.

Below is a snapshot of a random sample of the ELR codes data:

.. code-block:: python

    >>> elrs_dat[em.Key].head()
        ELR  ...                   Notes
    0   AAL  ...                Now NAJ3
    1   AAM  ...            Formerly AML
    2   AAV  ...
    3   ABB  ...                 Now AHB
    4   ABB  ...
    5   ABD  ...
    6   ABE  ...  Formerly ABE1 and ABE2
    7   ABE  ...
    8  ABE1  ...         Now part of ABE
    9  ABE2  ...         Now part of ABE
    [10 rows x 5 columns]

.. _qs-mileage-files:

Get mileage data for a given ELR
--------------------------------

To get detailed mileage data for a given ELR, for example, `AAM <http://www.railwaycodes.org.uk/elrs/_mileages/a/aam.shtm>`_, use the method :py:meth:`ELRMileages.fetch_mileage_file()<elr_mileage.ELRMileages.fetch_mileage_file>`, which returns a dictionary as well:

.. code-block:: python

    >>> em_amm = em.fetch_mileage_file('AAM')

    >>> type(em_amm)
    dict
    >>> list(em_amm.keys())
    ['ELR', 'Line', 'Sub-Line', 'Mileage', 'Notes']

The keys of ``em_amm`` include:

-  ``'ELR'``
-  ``'Line'``
-  ``'Sub-Line'``
-  ``'Mileage'``
-  ``'Notes'``

Their corresponding values are

-  ``em_amm['ELR']``: the name of the given ELR (which in this example is 'AAM');
-  ``em_amm['Line']``: the associated line name;
-  ``em_amm['Sub-Line']``: the associated sub line name (if available);
-  ``em_amm['Mileage']``: a `pandas.DataFrame`_ of the mileage file data;
-  ``em_amm['Notes']``: additional information/notes (if any).

Below is a snapshot of the mileage data of `AAM <http://www.railwaycodes.org.uk/elrs/_mileages/a/aam.shtm>`_:

.. code-block:: python

    >>> em_amm['Mileage'].head(10)
       Mileage Mileage_Note  ... Link_2_ELR Link_2_Mile_Chain
    0   0.0000               ...
    1   0.0154               ...
    2   0.0396               ...
    3   1.1012               ...
    4   1.1408               ...
    5   5.0330               ...
    6   7.0374               ...
    7  11.1298               ...
    8  13.0638               ...
    [9 rows x 11 columns]


.. _qs-railway-stations-data:

Get railway stations data
=========================

The `railway station data <http://www.railwaycodes.org.uk/stations/station0.shtm>`_ (incl. the station name, ELR, mileage, status, owner, operator, degrees of longitude and latitude, and grid reference) is categorised into `other assets <http://www.railwaycodes.org.uk/otherassetsmenu.shtm>`_ in the source data.

.. code-block:: python

    >>> from pyrcs.other_assets import Stations
    >>> # Or simply
    >>> # from pyrcs import Stations

    >>> stn = Stations()

.. note::

    Alternatively, the instance ``stn`` can also be defined through :py:class:`OtherAssets()<pyrcs.collector.OtherAssets>` that contains all classes under the category of `other assets <http://www.railwaycodes.org.uk/otherassetsmenu.shtm>`_ (see below).

.. code-block:: python

    >>> from pyrcs import OtherAssets

    >>> oa = OtherAssets()
    >>> stn_ = oa.Stations

.. note::

    ``stn_`` is equivalent to ``stn``.

To get the data of railway stations whose names start with a specific letter, e.g. ``'A'``, use the method :py:meth:`Stations.collect_station_data_by_initial()<station.Stations.collect_station_data_by_initial>`:

.. code-block:: python

    >>> stn_data_a = stn.collect_station_data_by_initial('A')

    >>> type(stn_data_a)
    dict
    >>> list(stn_data_a.keys())
    ['A', 'Last updated date']

The keys of ``stn_data_a`` include:

-  ``'A'``
-  ``'Last updated date'``

The corresponding values are

-  ``stn_data_a['A']``: a `pandas.DataFrame`_ of the data of railway stations whose names begin with 'A'. We may compare it with the table on the web page of `Stations beginning with 'A' <http://www.railwaycodes.org.uk/stations/stationa.shtm>`_;
-  ``stn_data_a['Last updated date']``: the date when the web page was last updated.

Below is a snapshot of the data of the railway stations beginning with 'A':

.. code-block:: python

    >>> stn_data_a['A'].head()
          Station   ELR  ... Prev_Operator_6 Prev_Operator_Period_6
    0  Abbey Wood   NKL  ...
    1  Abbey Wood  XRS3  ...
    2        Aber   CAR  ...
    3   Abercynon   CAM  ...
    4   Abercynon   ABD  ...
    [5 rows x 28 columns]

    >>> print("Last updated date: {}".format(stn_data_a['Last updated date']))
    Last updated date: 2021-02-22


To get available railway station data (from 'A' to 'Z') in this category, use the method :py:meth:`Stations.fetch_station_data()<station.Stations.fetch_station_data>`

.. code-block:: python

    >>> stn_data = stn.fetch_station_data()

    >>> type(stn_data)
    dict
    >>> list(stn_data.keys())
    ['Mileages, operators and grid coordinates', 'Last updated date']

The keys of ``stn_data`` include:

-  ``'Mileages, operators and grid coordinates'``
-  ``'Latest update date'``

Their corresponding values are

-  ``stn_data['Mileages, operators and grid coordinates']``: a `pandas.DataFrame`_ of available railway station data (from 'A' to 'Z');
-  ``stn_data['Latest update date']``: the latest ``'Last updated date'`` among all initial letter-specific codes.

Below is a snapshot of a random sample of the railway station data:

.. code-block:: python

    >>> stn_data[stn.StnKey].head(10)
               Station   ELR  ... Prev_Operator_6 Prev_Operator_Period_6
    0       Abbey Wood  XRS3  ...
    1       Abbey Wood   NKL  ...
    2             Aber   CAR  ...
    3        Abercynon   ABD  ...
    4        Abercynon   CAM  ...
    5  Abercynon North   ABD  ...
    6         Aberdare   VON  ...
    7         Aberdeen  ANI1  ...
    8         Aberdeen  ECN5  ...
    9         Aberdour  ECN2  ...
    [10 rows x 30 columns]

    >>> print("Last updated date: {}".format(stn_data['Last updated date']))
    Last updated date: 2021-03-21


.. _`dict`: https://docs.python.org/3/library/stdtypes.html#dict
.. _`pandas.DataFrame`: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html

|

**(The end of the quick start)**

For more details and examples, check :ref:`Sub-packages and modules<sub-pkg-and-mod>`.
