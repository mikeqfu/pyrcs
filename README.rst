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

The development of the `PyRCS <https://pyrcs.readthedocs.io/en/latest/>`_ is mainly built on data from the |Railway Codes|_ website. The author of the package would like to thank the website editor and `all contributors <http://www.railwaycodes.org.uk/misc/acknowledgements.shtm>`_ to the data resources.

.. _Railway Codes: http://www.railwaycodes.org.uk/index.shtml

.. |Railway Codes| replace:: *Railway Codes*


Release history
===============

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
