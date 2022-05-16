#####
PyRCS
#####

.. only:: html

    |PyPI| |Python| |Documentation| |License| |Codacy grade| |DOI|

    .. |PyPI| image:: https://img.shields.io/pypi/v/pyrcs
        :alt: PyPI - Release
        :target: https://pypi.org/project/pyrcs/
    .. |Python| image:: https://img.shields.io/pypi/pyversions/pyrcs
        :alt: Python version
        :target: https://www.python.org/downloads/
    .. |Documentation| image:: https://img.shields.io/readthedocs/pyrcs
        :alt: PyRCS Documentation
        :target: https://pyrcs.readthedocs.io/en/latest/
    .. |License| image:: https://img.shields.io/pypi/l/pyrcs
        :alt: License for PyRCS
        :target: https://github.com/mikeqfu/pyrcs/blob/master/LICENSE
    .. |Codacy grade| image:: https://app.codacy.com/project/badge/Grade/7369679225b14eaeb92ba40c12c339d5
        :alt: Codacy grade for PyRCS
        :target: https://www.codacy.com/gh/mikeqfu/pyrcs/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=mikeqfu/pyrcs&amp;utm_campaign=Badge_Grade
    .. |DOI| image:: https://zenodo.org/badge/92501006.svg
        :alt: Zenodo - DOI
        :target: https://zenodo.org/badge/latestdoi/92501006

| **Author**: Qian Fu
| **Email**: q.fu@bham.ac.uk

PyRCS is an open-source Python package for collecting and handling various codes (used in different UK rail industry systems), which are made available from `Railway Codes`_ website. This tool is intended for those, such as researchers and practitioners, who are the website users or work with the UK's railway codes by using Python programming language. It can facilitate access to, and manipulation of, the relevant data.

The :ref:`installation<pyrcs-installation>` of PyRCS includes a set of pre-packed data. When users request data of a category that is specified on the `Railway Codes`_ website, the pre-packed data of the category is loaded by default. Beyond that, it also offers capabilities to directly access the most up-to-date data on the data source website, and update the relevant pre-packed data as well.

.. _`Railway Codes`: http://www.railwaycodes.org.uk/index.shtml


.. toctree::
    :maxdepth: 1
    :includehidden:
    :caption: Documentation

    introduction
    installation
    sub-pkg-and-mod
    license
    use-of-data
    acknowledgement

.. toctree::
    :maxdepth: 2
    :includehidden:
    :caption: Quick start

    quick-start


Indices
#######

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
