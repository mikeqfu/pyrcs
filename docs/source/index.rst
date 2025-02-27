#####
PyRCS
#####

|PyPI - Version| |PyPI - Python Version| |Read the Docs - Documentation| |GitHub Pages - Documentation| |License| |Codacy - Code Quality| |DOI|

.. |PyPI - Version| image:: https://img.shields.io/pypi/v/pyrcs
    :alt: PyPI - Version
    :target: https://pypi.org/project/pyrcs/
.. |PyPI - Python Version| image:: https://img.shields.io/pypi/pyversions/pyrcs
    :alt: PyPI - Python Version
    :target: https://docs.python.org/3/
.. |Read the Docs - Documentation| image:: https://img.shields.io/readthedocs/pyrcs?logo=readthedocs
    :alt: Read the Docs - Documentation
    :target: https://pyrcs.readthedocs.io/en/latest/?badge=latest
.. |GitHub Pages - Documentation| image:: https://img.shields.io/github/actions/workflow/status/mikeqfu/pyrcs/github-pages.yml?logo=github&label=docs
    :alt: GitHub Pages - Documentation
    :target: https://mikeqfu.github.io/pyrcs/
.. |License| image:: https://img.shields.io/github/license/mikeqfu/pyrcs
    :alt: License
    :target: https://github.com/mikeqfu/pyrcs/blob/master/LICENSE
.. |Codacy - Code Quality| image:: https://app.codacy.com/project/badge/Grade/7369679225b14eaeb92ba40c12c339d5
    :alt: Codacy - Code Quality
    :target: https://www.codacy.com/gh/mikeqfu/pyrcs/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=mikeqfu/pyrcs&amp;utm_campaign=Badge_Grade
.. |DOI| image:: https://img.shields.io/badge/10.5281%2Fzenodo.4026744-blue?label=doi
    :alt: DOI
    :target: https://doi.org/10.5281/zenodo.4026744

| **Author**: Qian Fu |ORCID|
| **Email**: q.fu@bham.ac.uk

.. |ORCID| image:: https://info.orcid.org/wp-content/uploads/2019/11/orcid_16x16.png
    :alt: ORCID
    :target: https://orcid.org/0000-0002-6502-9934

PyRCS is an open-source Python package designed to simplify the collection and management of diverse codes used in different systems within the UK rail industry. It serves as a practical toolkit for researchers, practitioners, and individuals who frequently interact with the `Railway Codes <http://www.railwaycodes.org.uk/index.shtml>`_ website and work extensively with railway codes in the UK. Leveraging the capabilities of the Python programming language, PyRCS enables efficient access to and manipulation of railway code data, enhancing productivity and effectiveness in working with these codes.

During :doc:`installation`, PyRCS includes a set of pre-packaged data. When users request data from a specific category listed on the `Railway Codes <http://www.railwaycodes.org.uk/index.shtml>`_ website, PyRCS automatically loads the corresponding pre-packaged data for that category by default. Additionally, it provides functionality that enables direct access to the latest data from the data source website, ensuring users can stay updated with the most current information. Furthermore, PyRCS users can conveniently update the relevant pre-packaged data, keeping their data resources synchronized with the latest developments.

With PyRCS, users can leverage Python's power to streamline workflows and enhance productivity when working with railway codes in the UK rail industry.


.. toctree::
    :maxdepth: 1
    :includehidden:
    :caption: Getting Started

    installation
    quick-start

.. toctree::
    :maxdepth: 1
    :includehidden:
    :caption: Usage & Reference

    subpackages
    modules

.. toctree::
    :maxdepth: 1
    :includehidden:
    :caption: Additional Info

    license
    use-of-data
    acknowledgement
    contributors


Indices
#######

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
