# PyRCS

[![PyPI - Release](https://img.shields.io/pypi/v/pyrcs)](https://pypi.org/project/pyrcs/)
[![Python version](https://img.shields.io/pypi/pyversions/pyrcs)](https://www.python.org/downloads/)
[![Documentation status](https://readthedocs.org/projects/pyrcs/badge/?version=latest)](https://pyrcs.readthedocs.io/en/latest/?badge=latest)
[![License](https://img.shields.io/pypi/l/pyrcs)](https://github.com/mikeqfu/pyrcs/blob/master/LICENSE)
[![Codacy grade (Code quality)](https://app.codacy.com/project/badge/Grade/7369679225b14eaeb92ba40c12c339d5)](https://www.codacy.com/gh/mikeqfu/pyrcs/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=mikeqfu/pyrcs&amp;utm_campaign=Badge_Grade)
[![Zenodo - DOI](https://zenodo.org/badge/92501006.svg)](https://zenodo.org/badge/latestdoi/92501006)

PyRCS is an open-source Python package designed to simplifies the collection and management of diverse codes used in different systems within the UK rail industry. It serves as a practical toolkit for researchers, practitioners, and individuals who frequently interact with the [Railway Codes](http://www.railwaycodes.org.uk/index.shtml) website and work extensively with railway codes in the UK. Leveraging the capabilities of the Python programming language, PyRCS enables efficient access to and manipulation of railway code data, enhancing productivity and effectiveness in working with these codes.

During [installation](https://pyrcs.readthedocs.io/en/latest/installation.html), PyRCS includes a set of pre-packaged data. When users request data from a specific category listed on the [Railway Codes](http://www.railwaycodes.org.uk/index.shtml) website, PyRCS automatically loads the corresponding pre-packaged data for that category by default. Additionally, it provides functionality that enables direct access to the latest data from the data source website, ensuring users can stay updated with the most current information. Furthermore, PyRCS users can conveniently update the relevant pre-packaged data, keeping their data resources synchronized with the latest developments.

With PyRCS, users can leverage Python's power to streamline workflows and enhance productivity when working with railway codes in the UK rail industry.

## Installation

To install the latest release of pyrcs from [PyPI](https://pypi.org/project/pyrcs/) via [pip](https://pip.pypa.io/en/stable/cli/pip/):

```bash
pip install --upgrade pyrcs
```

For more information, please also refer to [Installation](https://pyrcs.readthedocs.io/en/latest/installation.html).

## Documentation

The full PyRCS documentation (including detailed examples and a quick-start tutorial) is hosted on [ReadTheDocs](https://readthedocs.org/projects/pyrcs/): [[PDF](https://pyrcs.readthedocs.io/_/downloads/en/latest/pdf/)\] \[[HTML](https://pyrcs.readthedocs.io/en/latest/)].

## Cite as

Fu, Q. (2020). PyRCS: an open-source tool for collecting railway codes used in different UK rail industry systems. Zenodo. [doi:10.5281/zenodo.4026744](https://doi.org/10.5281/zenodo.4026744)

```bibtex
@software{qian_fu_pyrcs_4026744,
  author       = {Qian Fu},
  title        = {{PyRCS: an open-source tool for collecting railway
                   codes used in different UK rail industry systems}},
  year         = 2020,
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.4026744},
  url          = {https://doi.org/10.5281/zenodo.4026744}
}
```

(Please also refer to the export options from [Zenodo](https://zenodo.org/search?page=1&size=20&q=conceptrecid:%224026744%22&sort=-version&all_versions=True) to reference the specific version of PyRCS as appropriate.)

## License

PyRCS is licensed under [GNU General Public License v3](https://github.com/mikeqfu/pyrcs/blob/master/LICENSE) or later (GPLv3+).

## Acknowledgement

PyRCS uses data available from the [Railway Codes](http://www.railwaycodes.org.uk/index.shtml) website. The time and effort that the website's editor and [all contributors](http://www.railwaycodes.org.uk/misc/acknowledgements.shtm) put in making the site and data available are fully credited.
