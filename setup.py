import json

import setuptools

with open(file="pyrcs/data/metadata", mode='r') as metadata_file:
    metadata = json.load(metadata_file)

__pkgname__ = metadata['Package']
__version__ = metadata['Version']
__home_page__ = 'https://github.com/mikeqfu/' + f'{__pkgname__}'

setuptools.setup(
    name=__pkgname__,
    version=__version__,
    description=metadata['Description'],
    url=__home_page__,
    author=metadata['Author'],
    author_email=metadata['Email'],
    license=metadata['License'],
    project_urls={
        'Documentation': f'https://{__pkgname__}.readthedocs.io/en/{__version__}/',
        'Source': __home_page__,
        'Bug Tracker': __home_page__ + '/issues',
    },
)
