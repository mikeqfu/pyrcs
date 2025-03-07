# PyRCS

[![PyPI Release Version](https://img.shields.io/pypi/v/pyrcs)](https://pypi.org/project/pyrcs/)
[![Python Version](https://img.shields.io/pypi/pyversions/pyrcs)](https://docs.python.org/3/)
[![License](https://img.shields.io/github/license/mikeqfu/pyrcs)](https://github.com/mikeqfu/pyrcs/blob/master/LICENSE)
[![ReadTheDocs Documentation](https://img.shields.io/readthedocs/pyrcs?logo=readthedocs)](https://pyrcs.readthedocs.io/en/latest/?badge=latest)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/mikeqfu/pyrcs/github-pages.yml?logo=github&branch=master)](https://github.com/mikeqfu/pyrcs/actions)
[![Codacy - Code Quality](https://app.codacy.com/project/badge/Grade/7369679225b14eaeb92ba40c12c339d5)](https://app.codacy.com/gh/mikeqfu/pyrcs/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![Codecov - Test Coverage](https://codecov.io/gh/mikeqfu/pyrcs/graph/badge.svg?token=6CKN8T1RVL)](https://codecov.io/gh/mikeqfu/pyrcs)
[![DOI](https://img.shields.io/badge/10.5281%2Fzenodo.4026744-blue?label=doi)](https://doi.org/10.5281/zenodo.4026744)

PyRCS is an open-source Python package that simplifies the collection and management of railway codes used across different systems in the UK rail industry. It provides a practical toolkit for researchers, practitioners and frequent users of the [Railway Codes](http://www.railwaycodes.org.uk/index.shtml) website who work extensively with railway codes in the UK. By leveraging Python's capabilities, PyRCS enables efficient access, retrieval and manipulation of railway code data, enhancing productivity and effectiveness in working with these codes.

During [installation](https://pyrcs.readthedocs.io/en/latest/installation.html), PyRCS includes a set of pre-packaged data. When users request data from a specific category on the [Railway Codes](http://www.railwaycodes.org.uk/index.shtml) website, PyRCS loads the corresponding pre-packaged data for that category by default. Additionally, it provides functionality for direct access to the latest data from the source website, ensuring users stay up to date. Users can also update the pre-packaged data as needed, keeping their resources synchronized with the latest developments.

With PyRCS, users can leverage Python's power to streamline workflows and enhance productivity when working with railway codes in the UK rail industry.

## Installation

To install the latest version of pyrcs from [PyPI](https://pypi.org/project/pyrcs/) via [pip](https://pip.pypa.io/en/stable/cli/pip/):

```bash
$ pip install --upgrade pyrcs
```

For more information, see the [Installation](https://pyrcs.readthedocs.io/en/latest/installation.html). 

## Quick start

For a concise guide on how to use PyRCS, check out the [Quick Start](https://pyrcs.readthedocs.io/en/latest/quick-start.html) tutorial, which includes illustrative examples for three frequently-used code categories in the UK railway system: 

* [Location identifiers](http://www.railwaycodes.org.uk/crs/CRS0.shtm) (CRS, NLC, TIPLOC and STANOX codes)
* [Engineer’s Line References](http://www.railwaycodes.org.uk/elrs/elr0.shtm) (ELRs) and their associated mileage files
* [Railway station data](http://www.railwaycodes.org.uk/stations/station1.shtm) (mileages, operators and grid coordinates)

## Documentation

The complete PyRCS Documentation is available in [HTML](https://pyrcs.readthedocs.io/en/latest/) and [PDF](https://pyrcs.readthedocs.io/_/downloads/en/latest/pdf/) formats.

It is hosted on [Read the Docs](https://app.readthedocs.org/projects/pyrcs/), and the HTML version is also accessible via [GitHub Pages](https://mikeqfu.github.io/pyrcs/). The documentation includes detailed examples, tutorials and comprehensive references to help users get the most out of PyRCS. 

## Cite as

Fu, Q. (2020). PyRCS: an open-source tool for collecting railway codes used in different UK rail industry systems. Zenodo. [doi:10.5281/zenodo.4026744](https://doi.org/10.5281/zenodo.4026744)

```bibtex
@software{Fu_PyRCS_2020,
    author = {Fu, Qian},
    title = {{PyRCS: An open-source tool for collecting railway codes used in different UK rail industry systems}},
    year = 2020,
    publisher = {Zenodo},
    doi = {10.5281/zenodo.4026744},
    license = {MIT},
    url = {https://github.com/mikeqfu/pyrcs}
}
```

For specific version references, please refer to [Zenodo](https://zenodo.org/search?q=conceptrecid%3A%224026744%22&f=allversions%3Atrue&l=list&p=1&s=10&sort=version).

## License

PyRCS is licensed under the [MIT License](https://github.com/mikeqfu/pyrcs/blob/master/LICENSE).

Please note that this project was initially licensed under the [GPLv3+](https://github.com/mikeqfu/pyrcs/blob/0.3.7/LICENSE) up to version *0.3.7*. Starting with version *1.0.0*, it has been re-licensed under the MIT License.

## Acknowledgement

PyRCS uses data available from the [Railway Codes](http://www.railwaycodes.org.uk/index.shtml) website. The time and effort that the website's editor and [all contributors](http://www.railwaycodes.org.uk/misc/acknowledgements.shtm) put in making the site and data available are fully credited.
