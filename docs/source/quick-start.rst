===========
Quick start
===========

To showcase the functionality of PyRCS, this concise tutorial offers a quick guide with examples on how to work with three frequently-used code categories in the UK railway system:

- `Location identifiers <http://www.railwaycodes.org.uk/crs/CRS0.shtm>`_ (CRS, NLC, TIPLOC and STANOX codes);
- `Engineer's Line References (ELRs) <http://www.railwaycodes.org.uk/elrs/elr0.shtm>`_ and their associated mileage files;
- `Railway station data <http://www.railwaycodes.org.uk/stations/station1.shtm>`_ (mileages, operators and grid coordinates).

The tutorial aims to demonstrate how PyRCS operates by providing practical illustrations and guidance.

.. _quickstart-location-identifiers:

Location identifiers
====================

The location identifiers, including CRS, NLC, TIPLOC and STANOX codes, are categorised as `line data`_ on the `Railway Codes`_ website. To get these codes via PyRCS, we can use the class :class:`~loc_id.LocationIdentifiers`, which is contained in the sub-package :mod:`~pyrcs.line_data`. Let's firstly import the class and create an instance:

.. _`line data`: http://www.railwaycodes.org.uk/linedatamenu.shtm
.. _`Railway Codes`: http://www.railwaycodes.org.uk/index.shtml

.. code-block:: python

    >>> from pyrcs.line_data import LocationIdentifiers  # from pyrcs import LocationIdentifiers

    >>> lid = LocationIdentifiers()

    >>> lid.NAME
    'CRS, NLC, TIPLOC and STANOX codes'
    >>> lid.URL
    'http://www.railwaycodes.org.uk/crs/crs0.shtm'

.. note::

    An alternative way of creating the instance is through the class :class:`~pyrcs.collector.LineData` (see below).

.. code-block:: python

    >>> from pyrcs.collector import LineData  # from pyrcs import LineData

    >>> ld = LineData()
    >>> lid_ = ld.LocationIdentifiers

    >>> lid.NAME == lid_.NAME
    True

.. note::

    - The instance ``ld`` refers to all classes under the category of `line data`_.
    - Here ``lid_`` is equivalent to ``lid``.

.. _quickstart-location-identifiers-given-initial:

Location identifiers given a specific initial letter
----------------------------------------------------

Now we can get the codes (in a `pandas.DataFrame`_ type) for all locations beginning with a given letter, by using the method :meth:`LocationIdentifiers.collect_codes_by_initial()<loc_id.LocationIdentifiers.collect_codes_by_initial>`. For example, to get the codes for locations whose names begin with ``'A'`` (or ``'a'``):

.. _`pandas.DataFrame`: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html

.. code-block:: python

    >>> loc_a_codes = lid.collect_codes_by_initial(initial='a')  # The input is case-insensitive
    >>> type(loc_a_codes)
    dict
    >>> list(loc_a_codes.keys())
    ['A', 'Additional notes', 'Last updated date']

As demonstrated above, ``loc_a_codes`` is a `dictionary`_ (in `dict`_ type), which has the following *keys*:

-  ``'A'``
-  ``'Additional notes'``
-  ``'Last updated date'``

The corresponding *values* are:

-  ``loc_a_codes['A']`` - CRS, NLC, TIPLOC and STANOX codes for the locations whose names begin with ``'A'`` (referring to the table presented on the web page `Locations beginning A`_);
-  ``loc_a_codes['Additional notes']`` - Additional information on the web page (if available);
-  ``loc_a_codes['Last updated date']`` - The date when the web page `Locations beginning A`_ was last updated.

.. _`dictionary`: https://docs.python.org/3/tutorial/datastructures.html#dictionaries
.. _`dict`: https://docs.python.org/3/library/stdtypes.html#dict
.. _`Locations beginning A`: http://www.railwaycodes.org.uk/crs/CRSa.shtm

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

    >>> print("Last updated date: {}".format(loc_a_codes['Last updated date']))


.. _quickstart-all-location-identifiers:

All available location identifiers
----------------------------------

In addition to the ``'A'`` group of locations, we can use the method :meth:`LocationIdentifiers.fetch_codes()<loc_id.LocationIdentifiers.fetch_codes>` to get the codes of all locations (with the initial letters ranging from ``'A'`` to ``'Z'``) available in this category:

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

    >>> lid.KEY
    'LocationID'

    >>> loc_codes_dat = loc_codes[lid.KEY]  # loc_codes['LocationID']
    >>> type(loc_codes_dat)
    pandas.core.frame.DataFrame
    >>> loc_codes_dat.head()
                                  Location CRS  ... STANME_Note STANOX_Note
    0                 1999 Reorganisations      ...
    1                                   A1      ...
    2                       A463 Traded In      ...
    3  A483 Road Scheme Supervisors Closed      ...
    4                               Aachen      ...
    [5 rows x 12 columns]

    >>> # Relevant codes of the 'Other systems'
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

    >>> # Take 'Crossrail' as an example
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


.. _quickstart-elrs-and-mileages:

ELRs and mileages
=================

`Engineer's Line References (ELRs)`_ are also frequently seen among various data in Britain's railway system. To get the codes of ELRs (and their associated mileage files), we can use the class :class:`~elr_mileage.ELRMileages`:

.. code-block:: python

    >>> from pyrcs.line_data import ELRMileages  # from pyrcs import ELRMileages

    >>> em = ELRMileages()

    >>> em.NAME
    "Engineer's Line References (ELRs)"
    >>> em.URL
    'http://www.railwaycodes.org.uk/elrs/elr0.shtm'

.. _quickstart-elrs:

Engineer's Line References (ELRs)
---------------------------------

Similar to the location identifiers, the codes of ELRs on the `Railway Codes`_ website are also alphabetically arranged given their initial letters. We can use the method :meth:`ELRMileages.collect_elr_by_initial()<elr_mileage.ELRMileages.collect_elr_by_initial>` to get the data of ELRs which begin with a specific initial letter. Let's take ``'A'`` as an example:

.. code-block:: python

    >>> elrs_a_codes = em.collect_elr_by_initial(initial='a')  # Data of ELRs beginning with 'A'
    >>> type(elrs_a_codes)
    dict
    >>> list(elrs_a_codes.keys())
    ['A', 'Last updated date']

``elrs_a_codes`` is a `dictionary`_ and has the following *keys*:

-  ``'A'``
-  ``'Last updated date'``

The corresponding *values* are:

-  ``elrs_a_codes['A']`` - Data of ELRs that begin with ``'A'`` (referring to the table presented on the web page `ELRs beginning with A`_);
-  ``elrs_a_codes['Last updated date']`` - The date when the web page `ELRs beginning with A`_ was last updated.

.. _`ELRs beginning with A`: http://www.railwaycodes.org.uk/elrs/elra.shtm

A snapshot of the data contained in ``elrs_a_codes`` is demonstrated below:

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


To get the data of all ELRs (with the initial letters ranging from ``'A'`` to ``'Z'``) available in this category, we can use the method :meth:`ELRMileages.fetch_elr()<elr_mileage.ELRMileages.fetch_elr>`:

.. code-block:: python

    >>> elrs_codes = em.fetch_elr()
    >>> type(elrs_codes)
    dict
    >>> list(elrs_codes.keys())
    ['ELRs and mileages', 'Last updated date']

In like manner, ``elrs_codes`` is also a `dictionary`_, of which the *keys* are:

-  ``'ELRs and mileages'``
-  ``'Latest update date'``

The corresponding *values* are:

-  ``elrs_codes['ELRs and mileages']`` - Codes of all available ELRs (with the initial letters ranging from ``'A'`` to ``'Z'``);
-  ``elrs_codes['Latest update date']`` - The latest ``'Last updated date'`` among all the initial-specific codes.

A snapshot of the data contained in ``elrs_codes`` is demonstrated below:

.. code-block:: python

    >>> elrs_codes_dat = elrs_codes[em.KEY]
    >>> type(elrs_codes_dat)
    pandas.core.frame.DataFrame
    >>> elrs_codes_dat.head()
       ELR  ...         Notes
    0  AAL  ...      Now NAJ3
    1  AAM  ...  Formerly AML
    2  AAV  ...
    3  ABB  ...       Now AHB
    4  ABB  ...
    [5 rows x 5 columns]

.. _quickstart-mileage-files-given-elr:

Mileage file of a given ELR
---------------------------

Further to the codes of ELRs, each ELR is associated with a mileage file, which specifies the major mileages for the ELR. To get the mileage data, we can use the method :meth:`ELRMileages.fetch_mileage_file()<elr_mileage.ELRMileages.fetch_mileage_file>`.

For example, let's try to get the `mileage file for 'AAM'`_:

.. _`mileage file for 'AAM'`: http://www.railwaycodes.org.uk/elrs/_mileages/a/aam.shtm

.. code-block:: python

    >>> amm_mileage_file = em.fetch_mileage_file(elr='AAM')
    >>> type(amm_mileage_file)
    dict
    >>> list(amm_mileage_file.keys())
    ['ELR', 'Line', 'Sub-Line', 'Mileage', 'Notes']

As demonstrated above, ``amm_mileage_file`` is a `dictionary`_ and has the following *keys*:

-  ``'ELR'``
-  ``'Line'``
-  ``'Sub-Line'``
-  ``'Mileage'``
-  ``'Notes'``

The corresponding *values* are:

-  ``amm_mileage_file['ELR']`` - The given ELR, which, in this example, is ``'AAM'``;
-  ``amm_mileage_file['Line']`` - Name of the line associated with the given ELR;
-  ``amm_mileage_file['Sub-Line']`` - Name of the sub line (if any) associated with the given ELR;
-  ``amm_mileage_file['Mileage']`` - Major mileages for the given ELR;
-  ``amm_mileage_file['Notes']`` - Additional information/notes (if any).

A snapshot of the data contained in ``amm_mileage_file`` is demonstrated below:

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


.. _quickstart-railway-station-data:

Railway station data
====================

The `railway station data`_ (including the station name, ELR, mileage, status, owner, operator, degrees of longitude and latitude, and grid reference) is categorised as one of the `other assets`_ on the `Railway Codes`_ website. To deal with data in this category, PyRCS offers a sub-package :mod:`~pyrcs.other_assets`, from which we can use the contained class :class:`~station.Stations` to get the `railway station data`_:

.. _`other assets`: http://www.railwaycodes.org.uk/otherassetsmenu.shtm

Now let's import the class and create an instance of it:

.. code-block:: python

    >>> from pyrcs.other_assets import Stations  # from pyrcs import Stations

    >>> stn = Stations()

    >>> stn.NAME
    'Railway station data'
    >>> stn.URL
    'http://www.railwaycodes.org.uk/stations/station0.shtm'

.. note::

    - Alternatively, the instance ``stn`` can also be defined through the class :class:`~pyrcs.collector.OtherAssets`, which contains all classes under the category of `other assets`_ (see below).

.. code-block:: python

    >>> from pyrcs.collector import OtherAssets  # from pyrcs import OtherAssets

    >>> oa = OtherAssets()
    >>> stn_ = oa.Stations

    >>> stn.NAME == stn_.NAME
    True

.. note::

    - The instances ``stn_`` and ``stn`` are of the same class :class:`~station.Stations`.

.. _quickstart-railway-station-locations-given-initial:

Railway station locations given a specific initial letter
---------------------------------------------------------

To get the location data of railway stations whose names start with a given letter, say ``'A'``, we can use the method :meth:`Stations.collect_locations_by_initial()<station.Stations.collect_locations_by_initial>`:

.. code-block:: python

    >>> stn_loc_a_codes = stn.collect_locations_by_initial(initial='a')
    >>> type(stn_loc_a_codes)
    dict
    >>> list(stn_loc_a_codes.keys())
    ['A', 'Last updated date']

As demonstrated above, the dictionary ``stn_loc_a_codes`` include the following *keys*:

-  ``'A'``
-  ``'Last updated date'``

The corresponding *values* are:

-  ``stn_loc_a_codes['A']`` - Mileages, operators and grid coordinates of railway stations whose names begin with ``'A'`` (referring to the table presented on the web page of `Stations beginning with A`_);
-  ``stn_loc_a_codes['Last updated date']`` - The date when the web page `Stations beginning with A`_ was last updated.

.. _`Stations beginning with A`: http://www.railwaycodes.org.uk/stations/stationa.shtm

A snapshot of the data contained in ``stn_loc_a`` is demonstrated below:

.. code-block:: python

    >>> stn_loc_a_codes_dat = stn_loc_a_codes['A']
    >>> type(stn_loc_a_codes_dat)
    pandas.core.frame.DataFrame
    >>> stn_loc_a_codes_dat.head()
          Station  ...                                    Former Operator
    0  Abbey Wood  ...  London & South Eastern Railway from 1 April 20...
    1  Abbey Wood  ...  London & South Eastern Railway from 1 April 20...
    2        Aber  ...  Keolis Amey Operations/Gweithrediadau Keolis A...
    3   Abercynon  ...  Keolis Amey Operations/Gweithrediadau Keolis A...
    4   Abercynon  ...  Keolis Amey Operations/Gweithrediadau Keolis A...
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
    0  Abbey Wood  NKL  11m 43ch
    1  Abbey Wood  XRS  24.458km
    2        Aber  CAR   8m 69ch
    3   Abercynon  CAM  16m 28ch
    4   Abercynon  ABD  16m 28ch

    >>> print("Last updated date: {}".format(stn_loc_a_codes['Last updated date']))


.. _quickstart-all-railway-station-locations:

All available railway station locations
---------------------------------------

To get the location data of all railway stations (with the initial letters ranging from ``'A'`` to ``'Z'``) available in this category, we can use the method :meth:`Stations.fetch_locations()<station.Stations.fetch_locations>`:

.. code-block:: python

    >>> stn_loc_codes = stn.fetch_locations()
    >>> type(stn_loc_codes)
    dict
    >>> list(stn_loc_codes.keys())
    ['Mileages, operators and grid coordinates', 'Last updated date']

The dictionary ``stn_loc_codes`` include the following *keys*:

-  ``'Mileages, operators and grid coordinates'``
-  ``'Latest update date'``

The corresponding *values* are:

-  ``stn_loc_codes['Mileages, operators and grid coordinates']`` - Location data of all railway stations available on the relevant web pages ranging from ``'A'`` to ``'Z'``;
-  ``stn_loc_codes['Latest update date']`` - The latest ``'Last updated date'`` among all initial-specific codes.

A snapshot of the data contained in ``stn_loc_codes`` is demonstrated below:

.. code-block:: python

    >>> stn.KEY_TO_STN
    'Mileages, operators and grid coordinates'

    >>> stn_loc_codes_dat = stn_loc_codes[stn.KEY_TO_STN]
    >>> type(stn_loc_codes_dat)
    pandas.core.frame.DataFrame
    >>> stn_loc_codes_dat.head()
          Station  ...                                    Former Operator
    0  Abbey Wood  ...  London & South Eastern Railway from 1 April 20...
    1  Abbey Wood  ...  London & South Eastern Railway from 1 April 20...
    2        Aber  ...  Keolis Amey Operations/Gweithrediadau Keolis A...
    3   Abercynon  ...  Keolis Amey Operations/Gweithrediadau Keolis A...
    4   Abercynon  ...  Keolis Amey Operations/Gweithrediadau Keolis A...
    [5 rows x 14 columns]

    >>> stn_loc_codes_dat.columns.to_list()
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
    >>> stn_loc_codes_dat[['Station', 'ELR', 'Mileage']].head()
          Station  ELR   Mileage
    0  Abbey Wood  NKL  11m 43ch
    1  Abbey Wood  XRS  24.458km
    2        Aber  CAR   8m 69ch
    3   Abercynon  CAM  16m 28ch
    4   Abercynon  ABD  16m 28ch

    >>> print("Last updated date: {}".format(stn_loc_codes['Last updated date']))


.. _quickstart-the-end:

**This is the end of the** :doc:`quick-start`.

-----------------------------------------------------------

Any issues regarding the use of the package are all welcome and should be logged/reported onto the `Bug Tracker`_.

.. _`Bug Tracker`: https://github.com/mikeqfu/pyrcs/issues

For more details and examples, check :doc:`sub-pkg-and-mod`.
