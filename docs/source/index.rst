#####
PyRCS
#####

|PyPI| |Python| |License| |Docs| |Build| |Codacy| |Codecov| |DOI|

.. |PyPI| image:: https://img.shields.io/pypi/v/pyrcs
    :alt: PyPI Release Version
    :target: https://pypi.org/project/pyrcs/
.. |Python| image:: https://img.shields.io/pypi/pyversions/pyrcs
    :alt: Python Version
    :target: https://docs.python.org/3/
.. |License| image:: https://img.shields.io/github/license/mikeqfu/pyrcs
    :alt: License
    :target: https://github.com/mikeqfu/pyrcs/blob/master/LICENSE
.. |Docs| image:: https://img.shields.io/readthedocs/pyrcs?logo=readthedocs
    :alt: ReadTheDocs Documentation
    :target: https://pyrcs.readthedocs.io/en/latest/?badge=latest
.. |Build| image:: https://img.shields.io/github/actions/workflow/status/mikeqfu/pyrcs/github-pages.yml?logo=github&branch=master
    :alt: GitHub Actions Workflow Status
    :target: https://github.com/mikeqfu/pyrcs/actions
.. |Codacy| image:: https://app.codacy.com/project/badge/Grade/7369679225b14eaeb92ba40c12c339d5
    :alt: Codacy Code Quality
    :target: https://www.codacy.com/gh/mikeqfu/pyrcs/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=mikeqfu/pyrcs&amp;utm_campaign=Badge_Grade
.. |Codecov| image:: https://codecov.io/gh/mikeqfu/pyrcs/graph/badge.svg?token=6CKN8T1RVL
    :alt: Codecov Test Coverage
    :target: https://codecov.io/gh/mikeqfu/pyrcs
.. |DOI| image:: https://img.shields.io/badge/10.5281%2Fzenodo.4026744-blue?label=doi
    :alt: DOI
    :target: https://doi.org/10.5281/zenodo.4026744

| **Author**: Qian Fu |ORCID|
| **Email**: q.fu@bham.ac.uk

.. |ORCID| image:: https://info.orcid.org/wp-content/uploads/2019/11/orcid_16x16.png
    :alt: ORCID
    :target: https://orcid.org/0000-0002-6502-9934

PyRCS is an open-source Python package that simplifies the collection and management of railway codes used across different systems in the UK rail industry. It provides a practical toolkit for researchers, practitioners and frequent users of the `Railway Codes <http://www.railwaycodes.org.uk/index.shtml>`_ website who work extensively with railway codes in the UK. By leveraging Python's capabilities, PyRCS enables efficient access, retrieval and manipulation of railway code data, enhancing productivity and effectiveness in working with these codes.

During :doc:`installation`, PyRCS includes a set of pre-packaged data. When users request data from a specific category on the `Railway Codes <http://www.railwaycodes.org.uk/index.shtml>`_ website, PyRCS loads the corresponding pre-packaged data for that category by default. Additionally, it provides functionality for direct access to the latest data from the source website, ensuring users stay up to date. Users can also update the pre-packaged data as needed, keeping their resources synchronized with the latest developments.

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
