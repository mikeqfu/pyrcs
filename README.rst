#####
PyRCS
#####

|PyPI| |Python| |Documentation| |License| |Codacy grade| |DOI|

.. |PyPI| image:: https://img.shields.io/pypi/v/pyrcs
    :alt: PyPI - Release
    :target: https://pypi.org/project/pyrcs/
.. |Python| image:: https://img.shields.io/pypi/pyversions/pyrcs
    :alt: Python version
    :target: https://www.python.org/downloads/
.. |Documentation| image:: https://readthedocs.org/projects/pyrcs/badge/?version=latest
    :alt: Documentation status
    :target: https://pyrcs.readthedocs.io/en/latest/?badge=latest
.. |License| image:: https://img.shields.io/pypi/l/pyrcs
    :alt: License
    :target: https://github.com/mikeqfu/pyrcs/blob/master/LICENSE
.. |Codacy grade| image:: https://app.codacy.com/project/badge/Grade/7369679225b14eaeb92ba40c12c339d5
    :alt: Codacy grade (Code quality)
    :target: https://www.codacy.com/gh/mikeqfu/pyrcs/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=mikeqfu/pyrcs&amp;utm_campaign=Badge_Grade
.. |DOI| image:: https://zenodo.org/badge/92501006.svg
    :alt: Zenodo - DOI
    :target: https://zenodo.org/badge/latestdoi/92501006

PyRCS is an open-source Python package for collecting and handling various codes (used in different UK rail industry systems), which are made available from the `Railway Codes`_ website. This tool is intended for those people, such as researchers and practitioners, that currently either use that website or work with the UK's railway codes and who are interested in using the Python programming language to facilitate access to, and manipulation of, data relating to railway codes.

The `installation <https://pyrcs.readthedocs.io/en/latest/installation.html>`_ of PyRCS includes a set of pre-packed data. When users request data of a category that is specified on the `Railway Codes`_ website, the pre-packed data of the category is loaded by default. Beyond that, it also offers capabilities to directly access the most up-to-date data on the data source website, and update the relevant pre-packed data as well.

.. _`Railway Codes`: http://www.railwaycodes.org.uk/index.shtml

Installation
############

To install the latest release of pyrcs from `PyPI <https://pypi.org/project/pyrcs/>`_ via `pip <https://pip.pypa.io/en/stable/cli/pip/>`_:

.. code-block:: bash

   pip install --upgrade pyrcs

**Note:** For more information, please also refer to `Installation <https://pyrcs.readthedocs.io/en/latest/installation.html>`_.

Documentation
#############

The full PyRCS documentation (including detailed examples and a quick-start tutorial) is hosted on `ReadTheDocs <https://readthedocs.org/projects/pyrcs/>`_: [`PDF <https://pyrcs.readthedocs.io/_/downloads/en/latest/pdf/>`_] [`HTML <https://pyrcs.readthedocs.io/en/latest/>`_].

License
#######

PyRCS is licensed under `GNU General Public License v3 <https://github.com/mikeqfu/pyrcs/blob/master/LICENSE>`_ or later (GPLv3+).

Cite as
#######

Fu, Q. (2020). PyRCS: an open-source tool for collecting railway codes used in different UK rail industry systems. Zenodo. `doi:10.5281/zenodo.4026744 <https://doi.org/10.5281/zenodo.4026744>`_

.. code-block:: bibtex

    @software{qian_fu_pyrcs_4026744,
      author       = {Qian Fu},
      title        = {{PyRCS: an open-source tool for collecting railway
                       codes used in different UK rail industry systems}},
      year         = 2020,
      publisher    = {Zenodo},
      doi          = {10.5281/zenodo.4026744},
      url          = {https://doi.org/10.5281/zenodo.4026744}
    }

**Note:** Please also refer to the export options from `Zenodo <https://zenodo.org/search?page=1&size=20&q=conceptrecid:%224026744%22&sort=-version&all_versions=True>`_ to reference the specific version of PyRCS as appropriate.

Acknowledgement
###############

PyRCS uses data available from the `Railway Codes`_ website. The time and effort that the website's editor and `all contributors <http://www.railwaycodes.org.uk/misc/acknowledgements.shtm>`_ put in making the site and data available are fully credited.
