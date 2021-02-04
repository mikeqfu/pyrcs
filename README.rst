=====
PyRCS
=====

|PyPI| |Python| |License| |Downloads| |DOI|

.. |PyPI| image:: https://img.shields.io/pypi/v/pyrcs?color=important&label=PyPI
   :target: https://pypi.org/project/pyrcs/
.. |Python| image:: https://img.shields.io/pypi/pyversions/pyrcs?color=informational&label=Python
   :target: https://www.python.org/downloads/
.. |License| image:: https://img.shields.io/pypi/l/pyrcs?color=green&label=License
   :target: https://github.com/mikeqfu/pyrcs/blob/master/LICENSE
.. |Downloads| image:: https://img.shields.io/pypi/dm/pyrcs?color=yellow&label=Downloads
   :target: https://pypistats.org/packages/pyrcs
.. |DOI| image:: https://zenodo.org/badge/92501006.svg
   :target: https://zenodo.org/badge/latestdoi/92501006

**Author**: Qian Fu

PyRCS is an open-source tool for collecting |Railway Codes|_ used in different UK rail industry systems.


Cite as
=======

Qian Fu, 2020. PyRCS: an open-source tool for collecting railway codes used in different UK rail industry systems. `doi:10.5281/zenodo.4026744 <https://doi.org/10.5281/zenodo.4026744>`_


Resources
=========

- `Documentation <https://pyrcs.readthedocs.io/en/latest/>`_
- `Issue Tracker <https://github.com/mikeqfu/pyrcs/issues>`_


License
=======

PyRCS is licensed under `GNU General Public License v3 (GPLv3) <https://github.com/mikeqfu/pyrcs/blob/master/LICENSE>`_.


Acknowledgement
===============

The development of the `PyRCS <https://github.com/mikeqfu/pyrcs/>`_ is mainly built on data from the |Railway Codes|_ website. The author of the package would like to thank the website editor and `all contributors <http://www.railwaycodes.org.uk/misc/acknowledgements.shtm>`_ to the data resources.

.. _Railway Codes: http://www.railwaycodes.org.uk/index.shtml

.. |Railway Codes| replace:: *Railway Codes*


Release history
===============

.. |space| unicode:: U+0020
.. |nbsp| unicode:: U+00A0

.. |ss| raw:: html

    <strike>

.. |se| raw:: html

    </strike>


`v0.2.12 <https://github.com/mikeqfu/pyrcs/releases/tag/0.2.12>`_
-----------------------------------------------------------------

**Main changes (since v0.2.11):**

    - enabled offline mode (by loading local backup when network connection is lost)
    - enabled direct access to all classes from importing the package, without having to specifying the submodules they reside in
    - combined the modules |ss| `_line_data <https://github.com/mikeqfu/pyrcs/commit/ac477c9dc6d76a7400ffcf9d031ffd545d662fac#diff-51811be1398d2439ca84a8504b8531b0411773c357881c423df0922f44e6923b>`__ |se| and |ss| `_other_assets <https://github.com/mikeqfu/pyrcs/commit/ac477c9dc6d76a7400ffcf9d031ffd545d662fac#diff-b7304475ca50edd2572798e94bb2d0d5e2f627c6f5470d1ad24722efdb803609>`__ |se| into a new module `collector <https://pyrcs.readthedocs.io/en/latest/collector.html>`__
    - combined the functions |ss| `collect_site_map() <https://github.com/mikeqfu/pyrcs/commit/5a9b983ea55c22edf04fe4be1711b6ded7a3eccc#diff-4fe83da7eb97d70cc844349191441cf8ecb65e67ee655989e774a44c2cd4eb6dL20>`__ |se| and |ss| `fetch_site_map() <https://github.com/mikeqfu/pyrcs/commit/5a9b983ea55c22edf04fe4be1711b6ded7a3eccc#diff-4fe83da7eb97d70cc844349191441cf8ecb65e67ee655989e774a44c2cd4eb6dL110>`__ |se| into a new function `get_site_map() <https://pyrcs.readthedocs.io/en/latest/_generated/pyrcs.utils.get_site_map.html#pyrcs.utils.get_site_map>`__, which are moved from the module `updater <https://pyrcs.readthedocs.io/en/latest/updater.html#module-pyrcs.updater>`__ to `utils <https://pyrcs.readthedocs.io/en/latest/utils.html>`__
    - converted the function |ss| `get_track_diagrams_items() <https://github.com/mikeqfu/pyrcs/commit/0216bf07d00769f08a6a7e09c6a0a08a42c5fb56#diff-3bd1279c5db5b09065ddf6468e4acfb650e3402d8b0c410ce7beaacb667a8135R78>`__ |se| (from the module `utils <https://pyrcs.readthedocs.io/en/latest/utils.html>`__) to a method `.get_track_diagrams_items() <https://pyrcs.readthedocs.io/en/latest/_generated/trk_diagr.TrackDiagrams.get_track_diagrams_items.html>`__ of the class `TrackDiagrams <https://pyrcs.readthedocs.io/en/latest/_generated/trk_diagr.TrackDiagrams.html>`__

`v0.2.11 <https://github.com/mikeqfu/pyrcs/releases/tag/0.2.11>`_
-----------------------------------------------------------------

**Main changes (since v0.2.10):**

    - renamed the following methods of the class `Stations <https://github.com/mikeqfu/pyrcs/commit/6dd583dfbb0fc5d88c4f39d337dd4a438034a46c>`__:

      - |ss| .collect_railway_station_data_by_initial() |se| to `.collect_station_data_by_initial() <https://github.com/mikeqfu/pyrcs/blob/6dd583dfbb0fc5d88c4f39d337dd4a438034a46c/pyrcs/other_assets/station.py#L127>`__
      - |ss| .fetch_railway_station_data() |se| to `.fetch_station_data() <https://github.com/mikeqfu/pyrcs/blob/6dd583dfbb0fc5d88c4f39d337dd4a438034a46c/pyrcs/other_assets/station.py#L245>`__

    - updated `PyRCS Documentation <https://pyrcs.readthedocs.io/en/latest/>`__

`v0.2.10 <https://github.com/mikeqfu/pyrcs/releases/tag/0.2.10>`_
-----------------------------------------------------------------

**Main changes (since v0.2.9):**

    - renamed the following modules and a few of their functions

    .. list-table::
        :header-rows: 1

        * - Old
          - New
        * - |ss| `crs_nlc_tiploc_stanox <https://github.com/mikeqfu/pyrcs/commit/095b9d946e3c1f4a72b33ee1926f41654914f27c>`__ |se|
          - `loc_id <https://github.com/mikeqfu/pyrcs/blob/095b9d946e3c1f4a72b33ee1926f41654914f27c/pyrcs/line_data/loc_id.py>`__
        * - |ss| `electrification <https://github.com/mikeqfu/pyrcs/commit/e3b8bf752403b2d962528723b40977d0172e7182>`__ |se|
          - `elec <https://github.com/mikeqfu/pyrcs/blob/e3b8bf752403b2d962528723b40977d0172e7182/pyrcs/line_data/elec.py>`__
        * - |ss| `track_diagrams <https://github.com/mikeqfu/pyrcs/commit/5712990892792d404cb9c883f313abcb0848479b>`__ |se|
          - `trk_diagr <https://github.com/mikeqfu/pyrcs/blob/5712990892792d404cb9c883f313abcb0848479b/pyrcs/line_data/trk_diagr.py>`__
        * - |ss| `tunnels <https://github.com/mikeqfu/pyrcs/commit/31854d6d2e98690c5d92ee074cdb8a03e293e987>`__ |se|
          - `tunnel <https://github.com/mikeqfu/pyrcs/blob/31854d6d2e98690c5d92ee074cdb8a03e293e987/pyrcs/other_assets/tunnel.py>`__

    - renamed the following modules without (or with minor) changes:

    .. list-table::
        :header-rows: 1

        * - Old
          - New
        * - |ss| `elrs_mileages <https://github.com/mikeqfu/pyrcs/commit/22b05dab9a51ffa69849be04ff26a5d8d444f9ca>`__ |se|
          - `elr_mileage <https://github.com/mikeqfu/pyrcs/blob/22b05dab9a51ffa69849be04ff26a5d8d444f9ca/pyrcs/line_data/elr_mileage.py>`__
        * - |ss| `line_names <https://github.com/mikeqfu/pyrcs/commit/0c7130c122cb9f55ce721711cf02935cb0f86e60>`__ |se|
          - `line_name <https://github.com/mikeqfu/pyrcs/blob/0c7130c122cb9f55ce721711cf02935cb0f86e60/pyrcs/line_data/line_name.py>`__
        * - |ss| `lor_codes <https://github.com/mikeqfu/pyrcs/commit/12e4cd04e598f9d74a0b4eb7f616b9f9e24e4b5e>`__ |se|
          - `lor_code <https://github.com/mikeqfu/pyrcs/blob/12e4cd04e598f9d74a0b4eb7f616b9f9e24e4b5e/pyrcs/line_data/lor_code.py>`__
        * - |ss| `depots <https://github.com/mikeqfu/pyrcs/commit/750e50c52124b2a28c121b88957bdae84eafecf6>`__
          - `depot <https://github.com/mikeqfu/pyrcs/blob/750e50c52124b2a28c121b88957bdae84eafecf6/pyrcs/other_assets/depot.py>`__
        * - |ss| `features <https://github.com/mikeqfu/pyrcs/commit/1d9645f9c9b754cf507f0c6b60ea96a26a3d105c>`__ |se|
          - `feature <https://github.com/mikeqfu/pyrcs/blob/1d9645f9c9b754cf507f0c6b60ea96a26a3d105c/pyrcs/other_assets/feature.py>`__
        * - |ss| `signal_boxes <https://github.com/mikeqfu/pyrcs/commit/8cd5a1eba435d8a961b2065a1e61a12c04d91248>`__ |se|
          - `sig_box <https://github.com/mikeqfu/pyrcs/blob/8cd5a1eba435d8a961b2065a1e61a12c04d91248/pyrcs/other_assets/sig_box.py>`__
        * - |ss| `stations <https://github.com/mikeqfu/pyrcs/commit/e0814219e719b82325dd5ff6c308f4a45cc43818>`__ |se|
          - `station <https://github.com/mikeqfu/pyrcs/blob/e0814219e719b82325dd5ff6c308f4a45cc43818/pyrcs/other_assets/station.py>`__
        * - |ss| `viaducts <https://github.com/mikeqfu/pyrcs/commit/b3d89ed5948319fc547737e752debb460b85991c>`__ |se|
          - `viaduct <https://github.com/mikeqfu/pyrcs/blob/b3d89ed5948319fc547737e752debb460b85991c/pyrcs/other_assets/viaduct.py>`__

    - updated `PyRCS Documentation <https://pyrcs.readthedocs.io/en/latest/>`__ with substantial revisions

`v0.2.9 <https://github.com/mikeqfu/pyrcs/releases/tag/0.2.9>`_
---------------------------------------------------------------

**Main changes (since v0.2.8):**

    - updated `PyRCS Documentation <https://pyrcs.readthedocs.io/en/latest/>`__

`v0.2.8 <https://github.com/mikeqfu/pyrcs/releases/tag/0.2.8>`_
---------------------------------------------------------------

**Main changes (since v0.2.7):**

    - modified all modules (including docstrings) with bug fixes
    - updated `PyRCS Documentation <https://pyrcs.readthedocs.io/en/latest/>`__

`v0.2.7 <https://github.com/mikeqfu/pyrcs/releases/tag/0.2.7>`_
---------------------------------------------------------------

**Main changes (since v0.2.6):**

    - modified all modules (including docstrings) with bug fixes
    - created `PyRCS Documentation <https://pyrcs.readthedocs.io/en/latest/>`__, which is hosted at `Read the Docs <https://readthedocs.org/>`__.

`v0.2.6 <https://github.com/mikeqfu/pyrcs/releases/tag/0.2.6>`_
---------------------------------------------------------------

**Main changes (since v0.2.5):**

    - added a new function |ss| `fix_num_stanox() <https://github.com/mikeqfu/pyrcs/commit/fd5df3a101aa565bab2b5c1d9ca840dd1b812291>`__ |se| to the module `utils <https://github.com/mikeqfu/pyrcs/blob/fd5df3a101aa565bab2b5c1d9ca840dd1b812291/pyrcs/utils.py>`__

`v0.2.5 <https://github.com/mikeqfu/pyrcs/releases/tag/0.2.5>`_
---------------------------------------------------------------

**Main changes (since v0.2.4):**

    - modified the `keys of the dict-type data <https://github.com/mikeqfu/pyrcs/commit/48e2b908984f940c3abe3aba5899de5fe8c285cc>`__ for the following classes:

      - `ELRMileages <https://github.com/mikeqfu/pyrcs/blob/48e2b908984f940c3abe3aba5899de5fe8c285cc/pyrcs/line_data_cls/elrs_mileages.py#L244>`__
      - `SignalBoxes <https://github.com/mikeqfu/pyrcs/blob/48e2b908984f940c3abe3aba5899de5fe8c285cc/pyrcs/other_assets_cls/signal_boxes.py#L18>`__

    - renamed the function `update_package_data() <https://github.com/mikeqfu/pyrcs/commit/e46e17002cd048db63dc5c7c0e074b4162377705>`__ to `update_pkg_metadata() <https://github.com/mikeqfu/pyrcs/blob/e46e17002cd048db63dc5c7c0e074b4162377705/pyrcs/update.py#L11>`__ in the module `update <https://github.com/mikeqfu/pyrcs/blob/e46e17002cd048db63dc5c7c0e074b4162377705/pyrcs/update.py>`__
    - tested the package in Python 3.8

`v0.2.4 <https://github.com/mikeqfu/pyrcs/releases/tag/0.2.4>`_
---------------------------------------------------------------

**Main changes (since v0.2.3):**

    - removed the module `settings <https://github.com/mikeqfu/pyrcs/commit/8e6340bfe078f0cd558f059f89ef1d5029ef62b4>`__
    - updated imports throughout the package due to changes in the dependency modules from `PyHelpers <https://github.com/mikeqfu/pyhelpers>`__
    - modified a few classes due to changes on the web pages of the data source

`v0.2.3 <https://github.com/mikeqfu/pyrcs/releases/tag/0.2.3>`_
---------------------------------------------------------------

**Main changes (since v0.2.2):**

    - updated a few helper functions with `bug fixes <https://github.com/mikeqfu/pyrcs/commit/7872dc917065623f3cb5f7939a065900c6070af4>`__ in the module `utils <https://github.com/mikeqfu/pyrcs/blob/7872dc917065623f3cb5f7939a065900c6070af4/pyrcs/utils.py>`__

`v0.2.2 <https://github.com/mikeqfu/pyrcs/releases/tag/0.2.2>`_
---------------------------------------------------------------

**Main changes (since v0.2.1):**

    - modified the following methods of the class `ELRMileages <https://github.com/mikeqfu/pyrcs/blob/bc45055b6d07f83bddadd29c590226d7ddb9a7d3/pyrcs/line_data_cls/elrs_mileages.py#L244>`__, which are used for collecting ELRs and mileages:

      - `.collect_mileage_file_by_elr() <https://github.com/mikeqfu/pyrcs/commit/3a4b210c8373de14de7740c9ca874db100687200>`__
      - `.get_conn_mileages() <https://github.com/mikeqfu/pyrcs/commit/bc45055b6d07f83bddadd29c590226d7ddb9a7d3>`__

    - fixed a minor `issue <https://github.com/mikeqfu/pyrcs/commit/fe6373d2f7ff73cad893a865879e74b2c54d9e86>`__ in the filenames of the package's backup data

`v0.2.1 <https://github.com/mikeqfu/pyrcs/releases/tag/0.2.1>`_
---------------------------------------------------------------

**Main changes (since v0.2.0):**

    - modified the following modules with bug fixes:

      - `utils <https://github.com/mikeqfu/pyrcs/blob/80fed8c2fb3096457a20e543af5f15cb55f40407/pyrcs/utils.py>`__
      - `elrs_mileages <https://github.com/mikeqfu/pyrcs/blob/0dd70c69bea3a8190455cbf36eab659b02d86315/pyrcs/line_data_cls/elrs_mileages.py>`__

    - renamed the backup data of the package

`v0.2.0 <https://github.com/mikeqfu/pyrcs/releases/tag/0.2.0>`_
---------------------------------------------------------------

**A brand new release.**

*Note that the initial release and the later versions up to v0.1.28 have been deprecated and permanently removed.*
