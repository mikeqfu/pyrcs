.. _pyrcs-tutorial:

========
Tutorial
========

To demonstrate how PyRCS works, this brief tutorial provides a quick guide with examples of getting the following three categories of codes, which are frequently used in the railway system in the UK:

- `Location identifiers`_ (CRS, NLC, TIPLOC and STANOX codes);
- `Engineer's Line References (ELRs)`_ and their associated mileage files;
- `Railway station data`_ (mileages, operators and grid coordinates).

.. _`Location identifiers`: http://www.railwaycodes.org.uk/crs/CRS0.shtm
.. _`Engineer's Line References (ELRs)`: http://www.railwaycodes.org.uk/elrs/elr0.shtm
.. _`Railway station data`: http://www.railwaycodes.org.uk/stations/station1.shtm


.. _tutorial-location-identifiers:

Location identifiers
====================

The location identifiers, including CRS, NLC, TIPLOC and STANOX codes, are categorised as `line data`_ on the `Railway Codes`_ website. To get these codes via PyRCS, we can  the class :py:class:`~loc_id.LocationIdentifiers`, which is contained in the sub-package :py:mod:`~pyrcs.line_data`. Let's firstly import the class and create an instance:

.. _`line data`: http://www.railwaycodes.org.uk/linedatamenu.shtm
.. _`Railway Codes`: http://www.railwaycodes.org.uk/index.shtml

.. code-block:: python

    >>> from pyrcs.line_data import LocationIdentifiers  # from pyrcs import LocationIdentifiers

    >>> lid = LocationIdentifiers()

    >>> lid.NAME
    'CRS, NLC, TIPLOC and STANOX codes'

.. note::

    An alternative way of creating the instance is through the class :py:class:`~pyrcs.collector.LineData` (see below).

.. code-block:: python

    >>> from pyrcs.collector import LineData  # from pyrcs import LineData

    >>> ld = LineData()
    >>> lid_ = ld.LocationIdentifiers

    >>> lid.NAME == lid_.NAME
    True

.. note::

    - The instance ``ld`` refers to all classes under the category of `line data`_.
    - Here ``lid_`` is equivalent to ``lid``.

.. _tutorial-location-identifiers-given-initial:

Location identifiers given a specific initial letter
----------------------------------------------------

Now we can get the codes (in a `pandas.DataFrame`_ type) for all locations beginning with a given letter, by using the method :py:meth:`LocationIdentifiers.collect_codes_by_initial()<loc_id.LocationIdentifiers.collect_codes_by_initial>`. For example, to get the codes for locations whose names begin with ``'A'`` (or ``'a'``):

.. _`pandas.DataFrame`: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html

.. code-block:: python

    >>> loc_id_a = lid.collect_codes_by_initial(initial='A')  # The input is case-insensitive

    >>> type(loc_id_a)
    dict
    >>> list(loc_id_a.keys())
    ['A', 'Additional notes', 'Last updated date']

As demonstrated above, ``loc_id_a`` is a `dictionary`_ (in `dict`_ type), which has the following *keys*:

-  ``'A'``
-  ``'Additional notes'``
-  ``'Last updated date'``

The corresponding *values* are:

-  ``loc_id_a['A']`` - CRS, NLC, TIPLOC and STANOX codes for the locations whose names begin with ``'A'`` (referring to the table presented on the web page `Locations beginning A`_);
-  ``loc_id_a['Additional notes']`` - Additional information on the web page (if available);
-  ``loc_id_a['Last updated date']`` - The date when the web page `Locations beginning A`_ was last updated.

.. _`dictionary`: https://docs.python.org/3/tutorial/datastructures.html#dictionaries
.. _`dict`: https://docs.python.org/3/library/stdtypes.html#dict
.. _`Locations beginning A`: http://www.railwaycodes.org.uk/crs/CRSa.shtm

A snapshot of the data contained in ``loc_id_a`` is demonstrated below:

.. code-block:: python

    >>> loc_id_a['A'].head()
                         Location CRS     NLC  ... TIPLOC_Note STANME_Note STANOX_Note
    0                      Aachen      081601  ...
    1        Abbey & West Dereham      705300  ...
    2          Abbeyhill Junction      937800  ...
    3       Abbeyhill Signal E811      937802  ...
    4  Abbeyhill Turnback Sidings      937801  ...

    [5 rows x 12 columns]

    >>> print("Last updated date: {}".format(loc_id_a['Last updated date']))
    Last updated date: 2022-02-27

.. _tutorial-all-location-identifiers:

All available location identifiers
----------------------------------

In addition to the ``'A'`` group of locations, we can use the method :py:meth:`LocationIdentifiers.fetch_codes()<loc_id.LocationIdentifiers.fetch_codes>` to get the codes of all locations (with the initial letters ranging from ``'A'`` to ``'Z'``) available in this category:

.. code-block:: python

    >>> loc_codes = lid.fetch_codes()

    >>> type(loc_codes)
    dict
    >>> list(loc_codes.keys())
    ['LocationID', 'Other systems', 'Additional notes', 'Last updated date']

``loc_codes`` is also in a `dictionary`_, of which the *keys* are as follows:

-  ``'LocationID'``
-  ``'Other systems'``
-  ``'Additional notes'``
-  ``'Latest update date'``

The corresponding *values* are:

-  ``loc_codes['LocationID']`` - CRS, NLC, TIPLOC and STANOX codes for all locations available on the relevant web pages ranging from ``'A'`` to ``'Z'``;
-  ``loc_codes['Other systems']`` - Relevant codes of the `Other systems`_;
-  ``loc_codes['Additional notes']`` - Additional notes and information (if available);
-  ``loc_codes['Latest update date']`` - The latest ``'Last updated date'`` among all initial-specific codes.

.. _`Other systems`: http://www.railwaycodes.org.uk/crs/CRS1.shtm

A snapshot of the data contained in ``loc_codes`` is demonstrated below:

.. code-block:: python

    >>> loc_codes['LocationID'].head(10)
                                   Location  CRS  ... STANME_Note STANOX_Note
    0                                Aachen       ...
    1                  Abbey & West Dereham       ...
    2                    Abbeyhill Junction       ...
    3                 Abbeyhill Signal E811       ...
    4            Abbeyhill Turnback Sidings       ...
    5  Abbey Level Crossing (Staffordshire)       ...
    6                           Abbey Mills       ...
    7                        Abbey Road DLR  ZAL  ...
    8                            Abbey Wood  ABW  ...
    9       Abbey Wood Alsike Road Junction       ...

    [10 rows x 12 columns]

    >>> other_sys_codes = loc_codes['Other systems']  # Relevant codes of the 'Other systems'
    >>> type(other_sys_codes)
    collections.defaultdict
    >>> list(other_sys_codes.keys())
    ['Córas Iompair Éireann (Republic of Ireland)',
     'Crossrail',
     'Croydon Tramlink',
     'Docklands Light Railway',
     'Manchester Metrolink',
     'Translink (Northern Ireland)',
     'Tyne & Wear Metro']

    >>> crossrail_codes = other_sys_codes['Crossrail']  # Take 'Crossrail' as an example
    >>> type(crossrail_codes)
    dict
    >>> list(crossrail_codes.keys())
    ['Codes shown on development signalling plans']
    >>> crossrail_codes_dat = crossrail_codes['Codes shown on development signalling plans']
    >>> type(crossrail_codes_dat)
    pandas.core.frame.DataFrame
    >>> crossrail_codes_dat.head()
                                          Location  ... Timetable planning rule code
    0                                   Abbey Wood  ...                          ABX
    1  Abbey Wood Bolthole Berth/Crossrail Sidings  ...                          ABB
    2                           Abbey Wood Sidings  ...                          XWN
    3                                  Bond Street  ...                          BDS
    4                                 Canary Wharf  ...                          CWX

    [5 rows x 4 columns]


.. _tutorial-elrs-and-mileages:

ELRs and mileages
=================

`Engineer's Line References (ELRs)`_ are also frequently seen among various data in Britain's railway system. To get the codes of ELRs (and their associated mileage files), we can use the class :py:class:`~elr_mileage.ELRMileages`:

.. code-block:: python

    >>> from pyrcs.line_data import ELRMileages  # from pyrcs import ELRMileages

    >>> em = ELRMileages()

    >>> em.NAME
    "Engineer's Line References (ELRs)"

.. _tutorial-elrs:

Engineer's Line References (ELRs)
---------------------------------

Similar to the location identifiers, the codes of ELRs on the `Railway Codes`_ website are also alphabetically arranged given their initial letters. We can use the method :py:meth:`ELRMileages.collect_elr_by_initial()<elr_mileage.ELRMileages.collect_elr_by_initial>` to get the data of ELRs which begin with a specific initial letter. Let's take ``'A'`` as an example:

.. code-block:: python

    >>> elrs_a = em.collect_elr_by_initial(initial='A')  # Data of ELRs beginning with 'A'

    >>> type(elrs_a)
    dict
    >>> list(elrs_a.keys())
    ['A', 'Last updated date']

``elrs_a`` is a `dictionary`_ and has the following *keys*:

-  ``'A'``
-  ``'Last updated date'``

The corresponding *values* are:

-  ``elrs_a['A']`` - Data of ELRs that begin with ``'A'`` (referring to the table presented on the web page `ELRs beginning with A`_);
-  ``elrs_a['Last updated date']`` - The date when the web page `ELRs beginning with A`_ was last updated.

.. _`ELRs beginning with A`: http://www.railwaycodes.org.uk/elrs/elra.shtm

A snapshot of the data contained in ``elrs_a`` is demonstrated below:

.. code-block:: python

    >>> elrs_a['A'].tail()
          ELR                                Line name       Mileages                  Datum Notes
    186  AYR4      Dalry Junction to Barassie Junction  22.53 - 33.08  Bridge Street Station
    187  AYR5  Barassie Junction to Lochgreen Junction    0.00 - 2.15      Barrasie Junction
    188  AYR6                Lochgreen Junction to Ayr  35.05 - 40.49  Bridge Street Station
    189   AYS                    Ashburys Yard Sidings    1.32 - 2.50  Manchester Piccadilly
    190   AYT                       Aberystwyth Branch   0.00 - 41.15      Pencader Junction

    [5 rows x 5 columns]

    >>> print("Last updated date: {}".format(elrs_a['Last updated date']))
    Last updated date: 2022-02-19

To get the data of all ELRs (with the initial letters ranging from ``'A'`` to ``'Z'``) available in this category, we can use the method :py:meth:`ELRMileages.fetch_elr()<elr_mileage.ELRMileages.fetch_elr>`:

.. code-block:: python

    >>> elrs_data = em.fetch_elr()

    >>> type(elrs_data)
    dict
    >>> list(elrs_data.keys())
    ['ELRs and mileages', 'Last updated date']

In like manner, ``elrs_data`` is also a `dictionary`_, of which the *keys* are:

-  ``'ELRs and mileages'``
-  ``'Latest update date'``

The corresponding *values* are:

-  ``elrs_dat['ELRs and mileages']`` - Codes of all available ELRs (with the initial letters ranging from ``'A'`` to ``'Z'``);
-  ``elrs_dat['Latest update date']`` - The latest ``'Last updated date'`` among all the initial-specific codes.

A snapshot of the data contained in ``elrs_data`` is demonstrated below:

.. code-block:: python

    >>> elrs_data['ELRs and mileages'].tail(10)
           ELR  ...                                              Notes
    4539  ZZF4  ...  Remainder now 0.00 - 0.58 from Sighthill East ...
    4540  ZZF5  ...
    4541        ...
    4542  ZDEL  ...
    4543  ZDEL  ...
    4544  ZGW1  ...
    4545  ZGW2  ...
    4546   ZZY  ...
    4547   ZZZ  ...
    4548  ZZZ9  ...

    [10 rows x 5 columns]

.. _tutorial-mileage-files-given-elr:

Mileage file of a given ELR
---------------------------

Further to the codes of ELRs, each ELR is associated with a mileage file, which specifies the major mileages for the ELR. To get the mileage data, we can use the method :py:meth:`ELRMileages.fetch_mileage_file()<elr_mileage.ELRMileages.fetch_mileage_file>`.

For example, let's try to get the `mileage file for 'AAM'`_:

.. _`mileage file for 'AAM'`: http://www.railwaycodes.org.uk/elrs/_mileages/a/aam.shtm

.. code-block:: python

    >>> em_amm = em.fetch_mileage_file(elr='AAM')

    >>> type(em_amm)
    dict
    >>> list(em_amm.keys())
    ['ELR', 'Line', 'Sub-Line', 'Mileage', 'Notes']

As demonstrated above, ``em_amm`` is a `dictionary`_ and has the following *keys*:

-  ``'ELR'``
-  ``'Line'``
-  ``'Sub-Line'``
-  ``'Mileage'``
-  ``'Notes'``

The corresponding *values* are:

-  ``em_amm['ELR']`` - The given ELR, which, in this example, is ``'AAM'``;
-  ``em_amm['Line']`` - Name of the line associated with the given ELR;
-  ``em_amm['Sub-Line']`` - Name of the sub line (if any) associated with the given ELR;
-  ``em_amm['Mileage']`` - Major mileages for the given ELR;
-  ``em_amm['Notes']`` - Additional information/notes (if any).

A snapshot of the data contained in ``em_amm`` is demonstrated below:

.. code-block:: python

    >>> em_amm['Line']
    'Ashchurch and Malvern Line'

    >>> em_amm['Mileage'].head(10)
       Mileage Mileage_Note Miles_Chains  ... Link_1_Mile_Chain Link_2_ELR Link_2_Mile_Chain
    0   0.0000                      0.00  ...             79.45
    1   0.0154                      0.07  ...
    2   0.0396                      0.18  ...             84.62
    3   1.1012                      1.46  ...
    4   1.1408                      1.64  ...
    5   5.0330                      5.15  ...
    6   7.0374                      7.17  ...
    7  11.1298                     11.59  ...
    8  13.0638                     13.29  ...            129.50

    [9 rows x 11 columns]


.. _tutorial-railway-station-data:

Railway station data
====================

The `railway station data`_ (including the station name, ELR, mileage, status, owner, operator, degrees of longitude and latitude, and grid reference) is categorised as one of the `other assets`_ on the `Railway Codes`_ website. To deal with data in this category, PyRCS offers a sub-package :py:mod:`~pyrcs.other_assets`, from which we can use the contained class :py:class:`~station.Stations` to get the `railway station data`_:

.. _`other assets`: http://www.railwaycodes.org.uk/otherassetsmenu.shtm

Now let's import the class and create an instance of it:

.. code-block:: python

    >>> from pyrcs.other_assets import Stations  # from pyrcs import Stations

    >>> stn = Stations()

    >>> stn.NAME
    'Railway station data'

.. note::

    - Alternatively, the instance ``stn`` can also be defined through the class :py:class:`~pyrcs.collector.OtherAssets`, which contains all classes under the category of `other assets`_ (see below).

.. code-block:: python

    >>> from pyrcs.collector import OtherAssets  # from pyrcs import OtherAssets

    >>> oa = OtherAssets()
    >>> stn_ = oa.Stations

    >>> stn.NAME == stn_.NAME
    True

.. note::

    - The instances ``stn_`` and ``stn`` are of the same class :py:class:`~station.Stations`.

.. _tutorial-railway-station-locations-given-initial:

Railway station locations given a specific initial letter
---------------------------------------------------------

To get the location data of railway stations whose names start with a given letter, say ``'A'``, we can use the method :py:meth:`Stations.collect_locations_by_initial()<station.Stations.collect_locations_by_initial>`:

.. code-block:: python

    >>> stn_loc_a = stn.collect_locations_by_initial('A')

    >>> type(stn_loc_a)
    dict
    >>> list(stn_loc_a.keys())
    ['A', 'Last updated date']

As demonstrated above, the dictionary ``stn_loc_a`` include the following *keys*:

-  ``'A'``
-  ``'Last updated date'``

The corresponding *values* are:

-  ``stn_loc_a['A']`` - Mileages, operators and grid coordinates of railway stations whose names begin with ``'A'`` (referring to the table presented on the web page of `Stations beginning with A`_);
-  ``stn_loc_a['Last updated date']`` - The date when the web page `Stations beginning with A`_ was last updated.

.. _`Stations beginning with A`: http://www.railwaycodes.org.uk/stations/stationa.shtm

A snapshot of the data contained in ``stn_loc_a`` is demonstrated below:

.. code-block:: python

    >>> stn_loc_a['A'].head()
               Station  ...                                    Former Operator
    0       Abbey Wood  ...  London & South Eastern Railway from 1 April 20...
    1       Abbey Wood  ...
    2             Aber  ...  Keolis Amey Operations/Gweithrediadau Keolis A...
    3        Abercynon  ...  Keolis Amey Operations/Gweithrediadau Keolis A...
    4  Abercynon North  ...  [Cardiff Railway Company from 13 October 1996 ...

    [5 rows x 13 columns]

    >>> print("Last updated date: {}".format(stn_loc_a['Last updated date']))
    Last updated date: 2022-03-08

.. _tutorial-all-railway-station-locations:

All available railway station locations
---------------------------------------

To get the location data of all railway stations (with the initial letters ranging from ``'A'`` to ``'Z'``) available in this category, we can use the method :py:meth:`Stations.fetch_locations()<station.Stations.fetch_locations>`:

.. code-block:: python

    >>> stn_loc_data = stn.fetch_locations()

    >>> type(stn_loc_data)
    dict
    >>> list(stn_loc_data.keys())
    ['Mileages, operators and grid coordinates', 'Last updated date']

The dictionary ``stn_loc_data`` include the following *keys*:

-  ``'Mileages, operators and grid coordinates'``
-  ``'Latest update date'``

The corresponding *values* are:

-  ``stn_loc_data['Mileages, operators and grid coordinates']`` - Location data of all railway stations available on the relevant web pages ranging from ``'A'`` to ``'Z'``;
-  ``stn_loc_data['Latest update date']`` - The latest ``'Last updated date'`` among all initial-specific codes.

A snapshot of the data contained in ``stn_loc_data`` is demonstrated below:

.. code-block:: python

    >>> stn_loc_data['Mileages, operators and grid coordinates'].head(10)
               Station  ...                                    Former Operator
    0       Abbey Wood  ...  London & South Eastern Railway from 1 April 20...
    1       Abbey Wood  ...
    2             Aber  ...  Keolis Amey Operations/Gweithrediadau Keolis A...
    3        Abercynon  ...  Keolis Amey Operations/Gweithrediadau Keolis A...
    4  Abercynon North  ...  [Cardiff Railway Company from 13 October 1996 ...
    5         Aberdare  ...  Keolis Amey Operations/Gweithrediadau Keolis A...
    6         Aberdeen  ...  Abellio ScotRail from 1 April 2015 to 31 March...
    7         Aberdour  ...  Abellio ScotRail from 1 April 2015 to 31 March...
    8        Aberdovey  ...  Keolis Amey Operations/Gweithrediadau Keolis A...
    9         Abererch  ...  Keolis Amey Operations/Gweithrediadau Keolis A...

    [10 rows x 13 columns]

    >>> print("Last updated date: {}".format(stn_loc_data['Last updated date']))
    Last updated date: 2022-03-09


.. _tutorial-the-end:

**This is the end of the** :ref:`tutorial<pyrcs-tutorial>`.

-----------------------------------------------------------

Any issues regarding the use of the package are all welcome and should be logged/reported onto the `Bug Tracker`_.

.. _`Bug Tracker`: https://github.com/mikeqfu/pyrcs/issues

For more details and examples, check :ref:`sub-packages and modules<pyrcs-sub-pkg-and-mod>`.
