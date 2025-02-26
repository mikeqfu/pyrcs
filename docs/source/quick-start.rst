===========
Quick Start
===========

This brief tutorial provides a step-by-step guide to using PyRCS, highlighting its key functionalities. It demonstrates how to retrieve three key categories of codes used in the UK railway system, which are commonly applied in both practical and research contexts:

- `Location identifiers`_ (CRS, NLC, TIPLOC and STANOX codes);
- `Engineer's Line References (ELRs)`_ and their associated mileage files;
- `Railway station data`_ (mileages, operators and grid coordinates).

Through practical examples, this tutorial will guide you in understanding how PyRCS works and how to use it effectively.

.. _quickstart-location-identifiers:

Location Identifiers
====================

:doc:`< Back to Top <quick-start>` | :ref:`Next > <quickstart-elrs-and-mileages>`

The location identifiers, including CRS, NLC, TIPLOC and STANOX codes, are classified as `line data`_ on the `Railway Codes`_ website. To retrieve these codes using PyRCS, we can use the :class:`~pyrcs.line_data.LocationIdentifiers` class, contained in the :mod:`~pyrcs.line_data` subpackage.

First, let's import the class and create an instance:

.. code-block:: python

    >>> from pyrcs.line_data import LocationIdentifiers
    >>> # Alternatively, from pyrcs import LocationIdentifiers
    >>> lid = LocationIdentifiers()
    >>> lid.NAME
    'CRS, NLC, TIPLOC and STANOX codes'
    >>> lid.URL
    'http://www.railwaycodes.org.uk/crs/crs0.shtm'

Alternatively, we can create the instance using the :class:`~pyrcs.collector.LineData` class:

.. code-block:: python

    >>> from pyrcs.collector import LineData
    >>> # Alternatively, from pyrcs import LineData
    >>> ld = LineData()
    >>> lid_ = ld.LocationIdentifiers
    >>> lid.NAME == lid_.NAME
    True

.. note::

    - The instance ``ld`` encompasses all classes within the `line data`_ category.
    - ``lid_`` is equivalent to ``lid``.

.. _quickstart-location-identifiers-by-initial-letter:

Location identifiers by initial letter
--------------------------------------

We can retrieve codes (in `pandas.DataFrame`_ format) for all locations starting with a specific letter using the :meth:`LocationIdentifiers.collect_loc_id()<pyrcs.line_data.LocationIdentifiers.collect_loc_id>` method. This input value for the parameter is case-insensitive. For example, to get the codes for locations whose names begin with the letter ``'A'`` (or ``'a'``):

.. code-block:: python

    >>> loc_a_codes = lid.collect_loc_id(initial='a', verbose=True)
    To collect data of CRS, NLC, TIPLOC and STANOX codes beginning with "A"
    ? [No]|Yes:  yes
    Collecting the data ... Done.
    >>> type(loc_a_codes)
    dict
    >>> list(loc_a_codes.keys())
    ['A', 'Notes', 'Last updated date']

As shown above, ``loc_a_codes`` is a `dictionary`_ (i.e. in `dict`_ format) with the following *keys*:

-  ``'A'``
-  ``'Notes'``
-  ``'Last updated date'``

The corresponding *values* are:

-  ``loc_a_codes['A']`` - CRS, NLC, TIPLOC and STANOX codes for the locations whose names begin with ``'A'``, referring to the table on the `Locations beginning A`_ web page.
-  ``loc_a_codes['Notes']`` - Any additional information provided on the web page (if available).
-  ``loc_a_codes['Last updated date']`` - The date when the `Locations beginning A`_ web page was last updated.

A snapshot of the data contained in ``loc_a_codes`` is demonstrated below:

.. code-block:: python

    >>> loc_a_codes_dat = loc_a_codes['A']
    >>> type(loc_a_codes_dat)
    pandas.core.frame.DataFrame
    >>> loc_a_codes_dat.head()
                                  Location CRS  ... STANME_Note STANOX_Note
    0                 1999 Reorganisations      ...
    1                                   A1      ...
    2                       A463 Traded In      ...
    3  A483 Road Scheme Supervisors Closed      ...
    4                               Aachen      ...
    [5 rows x 12 columns]
    >>> print("Notes: {}".format(loc_a_codes['Notes']))
    >>> print("Last updated date: {}".format(loc_a_codes['Last updated date']))
    Notes: None
    Last updated date: 2025-02-19

    >>> ## Try more examples! Uncomment the lines below and run:
    >>> # loc_a_codes = lid.fetch_loc_id('a')  # Fetch location codes starting with 'A'
    >>> # loc_codes = lid.fetch_loc_id()  # Fetch all location codes

.. _quickstart-all-available-location-identifiers:

All available location identifiers
----------------------------------

Beyond retrieving location codes for a specific letter, we can use the :meth:`LocationIdentifiers.fetch_codes()<pyrcs.line_data.LocationIdentifiers.fetch_codes>` method to obtain codes for all locations with names starting from ``'A'`` to ``'Z'``:

.. code-block:: python

    >>> loc_codes = lid.fetch_codes()
    >>> type(loc_codes)
    dict
    >>> list(loc_codes.keys())
    ['Location ID', 'Other systems', 'Additional notes', 'Last updated date']

The ``loc_codes`` object is a dictionary with the following *keys*:

-  ``'Location ID'``
-  ``'Other systems'``
-  ``'Additional notes'``
-  ``'Latest update date'``

The corresponding *values* are:

-  ``loc_codes['Location ID']`` - CRS, NLC, TIPLOC, and STANOX codes for all locations listed across the relevant web pages.
-  ``loc_codes['Other systems']`` - Codes related to the `other systems`_.
-  ``loc_codes['Additional notes']`` - Any additional notes and information (if available).
-  ``loc_codes['Latest update date']`` - The latest ``'Last updated date'`` across all initial-specific data.

Here is a snapshot of the data contained in ``loc_codes``:

.. code-block:: python

    >>> lid.KEY
    'Location ID'
    >>> loc_codes_dat = loc_codes[lid.KEY]  # loc_codes['Location ID']
    >>> type(loc_codes_dat)
    pandas.core.frame.DataFrame
    >>> loc_codes_dat.tail()
                    Location CRS     NLC  ... TIPLOC_Note STANME_Note STANOX_Note
    59783  Zone U3456 London      083900  ...
    59784     Zone U4 London      084100  ...
    59785    Zone U56 London      084700  ...
    59786            ZNGHTYK              ...
    59787            ZZWMNST              ...
    [5 rows x 12 columns]
    >>> loc_codes_dat[['Location', 'Location_Note']].tail()
                    Location    Location_Note
    59783  Zone U3456 London
    59784     Zone U4 London
    59785    Zone U56 London
    59786            ZNGHTYK  see Naughty Kid
    59787            ZZWMNST  see Westminster

To access codes from other systems, such as Crossrail or the Tyne & Wear Metro:

.. code-block:: python

    >>> lid.KEY_TO_OTHER_SYSTEMS
    'Other systems'
    >>> os_codes_dat = loc_codes[lid.KEY_TO_OTHER_SYSTEMS]
    >>> type(os_codes_dat)
    collections.defaultdict
    >>> list(os_codes_dat.keys())
    ['Córas Iompair Éireann (Republic of Ireland)',
     'Crossrail',
     'Croydon Tramlink',
     'Docklands Light Railway',
     'Manchester Metrolink',
     'Translink (Northern Ireland)',
     'Tyne & Wear Metro']

For example, to view the data for Crossrail:

.. code-block:: python

    >>> crossrail_codes_dat = os_codes_dat['Crossrail']
    >>> type(crossrail_codes_dat)
    pandas.core.frame.DataFrame
    >>> crossrail_codes_dat.head()
                                          Location  ... New operating code
    0                                   Abbey Wood  ...                ABW
    1  Abbey Wood Bolthole Berth/Crossrail Sidings  ...
    2                           Abbey Wood Sidings  ...
    3                                  Bond Street  ...                BDS
    4                                 Canary Wharf  ...                CWX
    [5 rows x 5 columns]

    >>> ## Try more examples! Uncomment the lines below and run:
    >>> ## Get a dictionary for STANOX codes and location names
    >>> # stanox_dict = lid.make_xref_dict('STANOX')
    >>> ## ... and for STANOX, TIPLOC and location names starting with 'A'
    >>> # stanox_tiploc_dict_a = lid.make_xref_dict(['STANOX', 'TIPLOC'], initials='a')

.. _quickstart-elrs-and-mileages:

ELRs and mileages
=================

:ref:`< Previous <quickstart-location-identifiers>` | :doc:`Back to Top <quick-start>` | :ref:`Next > <quickstart-railway-station-data>`

`Engineer's Line References (ELRs)`_ are also commonly encountered in various data sets within the UK's railway system. To retrieve the codes for ELRs along with their associated mileage files, we can use the :class:`~pyrcs.line_data.ELRMileages` class:

.. code-block:: python

    >>> from pyrcs.line_data import ELRMileages
    >>> # Alternatively, from pyrcs import ELRMileages
    >>> em = ELRMileages()
    >>> em.NAME
    "Engineer's Line References (ELRs)"
    >>> em.URL
    'http://www.railwaycodes.org.uk/elrs/elr0.shtm'

.. _quickstart-elrs:

Engineer's Line References (ELRs)
---------------------------------

Similar to location identifiers, the ELR codes on the `Railway Codes`_ website are arranged alphabetically based on their initial letters. We can use the :meth:`ELRMileages.collect_elr()<pyrcs.line_data.ELRMileages.collect_elr>` method to obtain ELRs starting with a specific letter. For example, to get the data for ELRs beginning with the letter ``'A'``:

.. code-block:: python

    >>> elrs_a_codes = em.collect_elr(initial='a')
    To collect data of Engineer's Line References (ELRs) beginning with "A"
    ? [No]|Yes:  yes
    Collecting the data ... Done.
    >>> type(elrs_a_codes)
    dict
    >>> list(elrs_a_codes.keys())
    ['A', 'Last updated date']

The ``elrs_a_codes`` object is a dictionary with the following *keys*:

-  ``'A'``
-  ``'Last updated date'``

The corresponding *values* are:

-  ``elrs_a_codes['A']`` - Data for ELRs that begin with ``'A'``, referring to the table presented on the `ELRs beginning with A`_ web page.
-  ``elrs_a_codes['Last updated date']`` - The date when the `ELRs beginning with A`_ web page was last updated.

Here is a snapshot of the data contained in ``elrs_a_codes``:

.. code-block:: python

    >>> elrs_a_codes_dat = elrs_a_codes['A']
    >>> type(elrs_a_codes_dat)
    pandas.core.frame.DataFrame
    >>> elrs_a_codes_dat.head()
       ELR  ...         Notes
    0  AAL  ...      Now NAJ3
    1  AAM  ...  Formerly AML
    2  AAV  ...
    3  ABB  ...       Now AHB
    4  ABB  ...
    [5 rows x 5 columns]
    >>> print("Last updated date: {}".format(elrs_a_codes['Last updated date']))
    Last updated date: 2024-10-20

To retrieve data for all ELRs (from ``'A'`` to ``'Z'``), we can use the :meth:`ELRMileages.fetch_elr()<pyrcs.line_data.ELRMileages.fetch_elr>` method:

.. code-block:: python

    >>> elrs_codes = em.fetch_elr()
    >>> type(elrs_codes)
    dict
    >>> list(elrs_codes.keys())
    ['ELRs and mileages', 'Last updated date']

Similarly, ``elrs_codes`` is a dictionary with the following *keys*:

-  ``'ELRs and mileages'``
-  ``'Latest update date'``

The corresponding *values* are:

-  ``elrs_codes['ELRs and mileages']`` - Codes for all available ELRs (with the initial letters ranging from ``'A'`` to ``'Z'``).
-  ``elrs_codes['Latest update date']`` - The most recent update date among all the ELR data.

Here is a snapshot of the data contained in ``elrs_codes``:

.. code-block:: python

    >>> elrs_codes_dat = elrs_codes[em.KEY]
    >>> type(elrs_codes_dat)
    pandas.core.frame.DataFrame
    >>> elrs_codes_dat.tail()
           ELR                                 Line name  ... Datum Notes
    4575  ZGW1                     Records to be deleted  ...   n/a
    4576  ZGW2        Records for comparison if required  ...   n/a
    4577   ZZY                            Deleted record  ...   n/a
    4578   ZZZ                      Record to be deleted  ...   n/a
    4579  ZZZ9  Dummy ELR for demonstrations and testing  ...   n/a
    [5 rows x 5 columns]

    >>> ## Try more examples! Uncomment the lines below and run:
    >>> # elrs_a_codes = em.fetch_elr(initial='a')  # Fetch ELRs starting with 'A'
    >>> # elrs_b_codes = em.fetch_elr(initial='B')  # Fetch ELRs starting with 'B'

.. _quickstart-mileage-file-of-a-given-elr:

Mileage file of a given ELR
---------------------------

In addition to the codes of ELRs, each ELR is associated with a mileage file that specifies the major mileages along the line. To retrieve this data, we can use the :meth:`ELRMileages.fetch_mileage_file()<pyrcs.line_data.ELRMileages.fetch_mileage_file>` method.

For example, to get the `mileage file for 'AAM'`_:

.. code-block:: python

    >>> amm_mileage_file = em.fetch_mileage_file(elr='AAM')
    >>> type(amm_mileage_file)
    dict
    >>> list(amm_mileage_file.keys())
    ['ELR', 'Line', 'Sub-Line', 'Mileage', 'Notes']

The ``amm_mileage_file`` object is also a dictionary and has the following *keys*:

-  ``'ELR'``
-  ``'Line'``
-  ``'Sub-Line'``
-  ``'Mileage'``
-  ``'Notes'``

The corresponding *values* are:

-  ``amm_mileage_file['ELR']`` - The given ELR (in this example, ``'AAM'``).
-  ``amm_mileage_file['Line']`` - The name of the line associated with the ELR.
-  ``amm_mileage_file['Sub-Line']`` - The sub-line name (if applicable).
-  ``amm_mileage_file['Mileage']`` - The major mileages along the line.
-  ``amm_mileage_file['Notes']`` - Additional notes or information (if available).

Here is a snapshot of the data contained in ``amm_mileage_file``:

.. code-block:: python

    >>> amm_mileage_file['Line']
    'Ashchurch and Malvern Line'
    >>> amm_mileage_file['Mileage'].head()
      Mileage Mileage_Note  ... Link_2_ELR Link_2_Mile_Chain
    0  0.0000               ...
    1  0.0154               ...
    2  0.0396               ...
    3  1.1012               ...
    4  1.1408               ...
    [5 rows x 11 columns]

    >>> ## Try more examples! Uncomment the lines below and run:
    >>> # xre_mileage_file = em.fetch_mileage_file('XRE')  # Fetch mileage file for 'XRE'
    >>> # your_mileage_file = em.fetch_mileage_file(elr='?')  # ... and for a given ELR '?'

.. _quickstart-railway-station-data:

Railway station data
====================

:ref:`< Previous <quickstart-elrs-and-mileages>` | :doc:`Back to Top <quick-start>` | :ref:`Next > <quickstart-the-end>`

The `railway station data`_ includes information such as the station name, ELR, mileage, status, owner, operator, coordinates and grid reference. This data is available in the `other assets`_ section of the `Railway Codes`_ website and can be retrieved using the :class:`~pyrcs.other_assets.Stations` class contained in the :mod:`~pyrcs.other_assets` subpackage.

To get the data, let's import the :class:`~pyrcs.other_assets.Stations` class and create an instance:

.. code-block:: python

    >>> from pyrcs.other_assets import Stations
    >>> # Alternatively, from pyrcs import Stations
    >>> stn = Stations()
    >>> stn.NAME
    'Railway station data'
    >>> stn.URL
    'http://www.railwaycodes.org.uk/stations/station0.shtm'

Alternatively, we can also create the instance by using the :class:`~pyrcs.collector.OtherAssets` class:.

.. code-block:: python

    >>> from pyrcs.collector import OtherAssets  # from pyrcs import OtherAssets
    >>> oa = OtherAssets()
    >>> stn_ = oa.Stations
    >>> stn.NAME == stn_.NAME
    True

.. note::

    - The instance ``stn`` encompasses all classes within the `other assets`_ category.
    - ``stn_`` is equivalent to ``stn``.

.. _quickstart-railway-stations-by-initial-letter:

Railway stations by initial letter
----------------------------------

We can obtain railway station data based on the first letter (e.g. ``'A'`` or ``'Z'``) of the station's name using the :meth:`Stations.collect_locations()<pyrcs.other_assets.Stations.collect_locations>` method. For example, to get data for stations starting with ``'A'``:

.. code-block:: python

    >>> stn_loc_a_codes = stn.collect_locations(initial='a')
    To collect data of mileages, operators and grid coordinates beginning with "A"
    ? [No]|Yes:  yes
    Collecting the data ... Done.
    >>> type(stn_loc_a_codes)
    dict
    >>> list(stn_loc_a_codes.keys())
    ['A', 'Last updated date']

The dictionary ``stn_loc_a_codes`` includes the following *keys*:

-  ``'A'``
-  ``'Last updated date'``

The corresponding *values* are:

-  ``stn_loc_a_codes['A']`` - Data for railway stations whose names begin with ``'A'``, including mileages, operators and grid coordinates, referring to the table on the `Stations beginning with A`_ web page.
-  ``stn_loc_a_codes['Last updated date']`` - The date when the `Stations beginning with A`_ web page was last updated.

Here is a snapshot of the data contained in ``stn_loc_a``:

.. code-block:: python

    >>> stn_loc_a_codes_dat = stn_loc_a_codes['A']
    >>> type(stn_loc_a_codes_dat)
    pandas.core.frame.DataFrame
    >>> stn_loc_a_codes_dat.head()
                                  Station  ...                              Former Operator
    0  Abbey Wood Abbey Wood / ABBEY WOOD  ...  London & South Eastern Railway from 1 Ap...
    1  Abbey Wood Abbey Wood / ABBEY WOOD  ...  London & South Eastern Railway from 1 Ap...
    2                                Aber  ...  Keolis Amey Operations/Gweithrediadau Ke...
    3                           Abercynon  ...  Keolis Amey Operations/Gweithrediadau Ke...
    4                           Abercynon  ...  Keolis Amey Operations/Gweithrediadau Ke...
    [5 rows x 14 columns]
    >>> stn_loc_a_codes_dat.columns.to_list()
    ['Station',
     'Station Note',
     'ELR',
     'Mileage',
     'Status',
     'Degrees Longitude',
     'Degrees Latitude',
     'Grid Reference',
     'CRS',
     'CRS Note',
     'Owner',
     'Former Owner',
     'Operator',
     'Former Operator']
    >>> stn_loc_a_codes_dat[['Station', 'ELR', 'Mileage']].head()
                                  Station  ELR   Mileage
    0  Abbey Wood Abbey Wood / ABBEY WOOD  NKL  11m 43ch
    1  Abbey Wood Abbey Wood / ABBEY WOOD  XRS  24.458km
    2                                Aber  CAR   8m 69ch
    3                           Abercynon  CAM  16m 28ch
    4                           Abercynon  ABD  16m 28ch
    >>> print("Last updated date: {}".format(stn_loc_a_codes['Last updated date']))
    Last updated date: 2025-02-12

.. _quickstart-all-available-railway-stations:

All available railway stations
------------------------------

To retrieve data for all railway stations available in the `other assets`_ category, we can use the :meth:`Stations.fetch_locations()<pyrcs.other_assets.Stations.fetch_locations>` method:

.. code-block:: python

    >>> stn_loc_codes = stn.fetch_locations()
    >>> type(stn_loc_codes)
    dict
    >>> list(stn_loc_codes.keys())
    ['Mileages, operators and grid coordinates', 'Last updated date']

The dictionary ``stn_loc_codes`` includes the following *keys*:

-  ``'Mileages, operators and grid coordinates'``
-  ``'Latest update date'``

The corresponding *values* are:

-  ``stn_loc_codes['Mileages, operators and grid coordinates']`` - Data for all railway stations, with the initial letters ranging from ``'A'`` to ``'Z'``.
-  ``stn_loc_codes['Latest update date']`` - The most recent update date among all the station data.

Here is a snapshot of the data contained in ``stn_loc_codes``:

.. code-block:: python

    >>> stn.KEY_TO_STN
    'Mileages, operators and grid coordinates'
    >>> stn_loc_codes_dat = stn_loc_codes[stn.KEY_TO_STN]
    >>> type(stn_loc_codes_dat)
    pandas.core.frame.DataFrame
    >>> stn_loc_codes_dat.tail()
                 Station  ...                                    Former Operator
    2898            York  ...  East Coast Main Line Company 14 November 2009 ...
    2899            York  ...  East Coast Main Line Company 14 November 2009 ...
    2900          Yorton  ...  Keolis Amey Operations/Gweithrediadau Keolis A...
    2901   Ystrad Mynach  ...  Keolis Amey Operations/Gweithrediadau Keolis A...
    2902  Ystrad Rhondda  ...  Keolis Amey Operations/Gweithrediadau Keolis A...
    [5 rows x 14 columns]
    >>> stn_loc_codes_dat.columns.to_list()
    >>> sel_cols = ['Station', 'ELR', 'Mileage', 'Degrees Longitude', 'Degrees Latitude']
    >>> stn_loc_codes_dat[sel_cols].tail()
                 Station   ELR    Mileage  Degrees Longitude  Degrees Latitude
    2898            York  ECM5    0m 00ch            -1.0920           53.9584
    2899            York  ECM4  188m 40ch            -1.0920           53.9584
    2900          Yorton   SYC   25m 14ch            -2.7360           52.8083
    2901   Ystrad Mynach   CAR   13m 60ch            -3.2414           51.6414
    2902  Ystrad Rhondda   THT   20m 05ch            -3.4666           51.6436
    >>> print("Last updated date: {}".format(stn_loc_codes['Last updated date']))
    Last updated date: 2025-02-26

    >>> ## Try more examples! Uncomment the lines below and run:
    >>> # stn_loc_a_codes = em.fetch_locations('a')  # railway stations starting with 'A'
    >>> # your_stn_loc_codes = em.fetch_locations('?')  # ... and a given letter '?'

.. _quickstart-the-end:

:ref:`< Previous <quickstart-railway-station-data>` | :doc:`Back to Top <quick-start>`

-----------------------------------------------------------

Any issues regarding the use of pyrcs are welcome and can be logged/reported onto the `Issue Tracker`_.

For more details and examples, check :doc:`subpackages` and :doc:`modules`.


.. _`Location identifiers`: http://www.railwaycodes.org.uk/crs/CRS0.shtm
.. _`Engineer's Line References (ELRs)`: http://www.railwaycodes.org.uk/elrs/elr0.shtm
.. _`Railway station data`: http://www.railwaycodes.org.uk/stations/station1.shtm
.. _`line data`: http://www.railwaycodes.org.uk/linedatamenu.shtm
.. _`Railway Codes`: http://www.railwaycodes.org.uk/index.shtml
.. _`pandas.DataFrame`: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html
.. _`dictionary`: https://docs.python.org/3/tutorial/datastructures.html#dictionaries
.. _`dict`: https://docs.python.org/3/library/stdtypes.html#dict
.. _`Locations beginning A`: http://www.railwaycodes.org.uk/crs/CRSa.shtm
.. _`other systems`: http://www.railwaycodes.org.uk/crs/CRS1.shtm
.. _`ELRs beginning with A`: http://www.railwaycodes.org.uk/elrs/elra.shtm
.. _`mileage file for 'AAM'`: http://www.railwaycodes.org.uk/elrs/_mileages/a/aam.shtm
.. _`other assets`: http://www.railwaycodes.org.uk/otherassetsmenu.shtm
.. _`Stations beginning with A`: http://www.railwaycodes.org.uk/stations/stationa.shtm
.. _`Issue Tracker`: https://github.com/mikeqfu/pyrcs/issues
