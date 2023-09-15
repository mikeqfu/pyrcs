# PyRCS

[![PyPI](https://img.shields.io/pypi/v/pyrcs)](https://pypi.org/project/pyrcs/)
[![Python Version](https://img.shields.io/pypi/pyversions/pyrcs)](https://www.python.org/downloads/)
[![Documentation Status](https://readthedocs.org/projects/pyrcs/badge/?version=latest)](https://pyrcs.readthedocs.io/en/latest/?badge=latest)
[![License](https://img.shields.io/pypi/l/pyrcs)](https://github.com/mikeqfu/pyrcs/blob/master/LICENSE)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/7369679225b14eaeb92ba40c12c339d5)](https://app.codacy.com/gh/mikeqfu/pyrcs/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![Zenodo](https://zenodo.org/badge/92501006.svg)](https://zenodo.org/badge/latestdoi/92501006)

PyRCS is an open-source Python package designed to simplify the collection and management of diverse codes used in different systems within the UK rail industry. It serves as a practical toolkit for researchers, practitioners, and individuals who frequently interact with the [Railway Codes](http://www.railwaycodes.org.uk/index.shtml) website and work extensively with railway codes in the UK. Leveraging the capabilities of the Python programming language, PyRCS enables efficient access to and manipulation of railway code data, enhancing productivity and effectiveness in working with these codes.

During [installation](https://pyrcs.readthedocs.io/en/latest/installation.html), PyRCS includes a set of pre-packaged data. When users request data from a specific category listed on the [Railway Codes](http://www.railwaycodes.org.uk/index.shtml) website, PyRCS automatically loads the corresponding pre-packaged data for that category by default. Additionally, it provides functionality that enables direct access to the latest data from the data source website, ensuring users can stay updated with the most current information. Furthermore, PyRCS users can conveniently update the relevant pre-packaged data, keeping their data resources synchronized with the latest developments.

With PyRCS, users can leverage Python's power to streamline workflows and enhance productivity when working with railway codes in the UK rail industry.

## Installation

To install the latest release of pyrcs from [PyPI](https://pypi.org/project/pyrcs/) via [pip](https://pip.pypa.io/en/stable/cli/pip/):

```bash
pip install --upgrade pyrcs
```

Please also refer to [Installation](https://pyrcs.readthedocs.io/en/latest/installation.html) for more information. 

## Quick start

For a concise guide on how to utilise PyRCS, we recommend checking out the [quick-start tutorial](https://pyrcs.readthedocs.io/en/latest/quick-start.html), which features multiple illustrative examples for three frequently used code categories in the UK railway system: 

* [Location identifiers](http://www.railwaycodes.org.uk/crs/CRS0.shtm) (CRS, NLC, TIPLOC and STANOX codes)
* [Engineer’s Line References](http://www.railwaycodes.org.uk/elrs/elr0.shtm) (ELRs) and their associated mileage files
* [Railway station data](http://www.railwaycodes.org.uk/stations/station1.shtm) (mileages, operators and grid coordinates) 

## Documentation

The complete PyRCS documentation: [[HTML](https://pyrcs.readthedocs.io/en/latest/)\] \[[PDF](https://pyrcs.readthedocs.io/_/downloads/en/latest/pdf/)].

It is hosted on [ReadTheDocs](https://readthedocs.org/projects/pyrcs/) and provides a wealth of detailed examples.

## License

PyRCS is licensed under [GNU General Public License v3](https://github.com/mikeqfu/pyrcs/blob/master/LICENSE) or later (GPLv3+).

## Acknowledgement

PyRCS uses data available from the [Railway Codes](http://www.railwaycodes.org.uk/index.shtml) website. The time and effort that the website's editor and [all contributors](http://www.railwaycodes.org.uk/misc/acknowledgements.shtm) put in making the site and data available are fully credited.

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

## Contributors

<!--suppress HtmlDeprecatedAttribute -->
<table>
  <tbody>
    <tr>
      <td align="center">
        <a href="https://github.com/mikeqfu" target="_blank"><img src="https://avatars.githubusercontent.com/u/1729711?v=4?s=100" width="100px;" alt="Qian Fu"/><br><sub><b>Qian Fu</b></sub></a><br>
        <a href="https://github.com/mikeqfu/pyrcs" target="_blank" title="Seeding">🌱</a>
        <a href="https://github.com/mikeqfu/pyrcs/commits?author=mikeqfu" target="_blank" title="Code">💻</a>
        <a href="https://github.com/mikeqfu/pyrcs/tree/master/tests" target="_blank" title="Tests">🧪</a>
        <a href="https://pyrcs.readthedocs.io/en/latest/" target="_blank" title="Documentation">📖</a>
      </td>
      <td align="center">
        <a href="https://github.com/Firtun" target="_blank"><img src="https://avatars.githubusercontent.com/u/75030535?v=4?s=100" width="100px;" alt="Firtun"/><br><sub><b>Firtun</b></sub></a><br>
        <a href="https://github.com/mikeqfu/pyrcs/commits?author=Firtun" target="_blank" title="Documentation">📖</a>
      </td>
  </tbody>
</table>
