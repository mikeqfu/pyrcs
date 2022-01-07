import json

import setuptools

with open(file="pyrcs/dat/metadata.json", mode='r') as metadata_file:
    metadata = json.load(metadata_file)

_author = metadata['Author']
_author_email = metadata['Email']
_description = metadata['Description']
_license = metadata['License']
_package = metadata['Package']
_version = metadata['Version']

with open("README.rst", 'r', encoding='utf-8') as readme:
    long_description = readme.read()

setuptools.setup(

    name=_package,

    version=_version,

    description=_description,
    long_description=long_description,
    long_description_content_type="text/x-rst",

    url=f'https://github.com/mikeqfu/{__package__}',

    author=_author,
    author_email=_author_email,

    license='GPLv3',

    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',

        'Topic :: Education',
        'Topic :: Scientific/Engineering',
        'Topic :: Utilities',

        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        'Programming Language :: Python :: 3',

        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux'
    ],

    keywords=['Python', 'Railway Codes', 'Railway', 'Bridges', 'CRS', 'NLC', 'TIPLOC',
              'STANOX', 'Electrification', 'ELR', 'Mileage', 'LOR', 'Stations',
              'Signal boxes', 'Tunnels', 'Viaducts', 'Depots', 'Tracks'],

    project_urls={
        'Documentation': f'https://{_package}.readthedocs.io/en/{_version}/',
        'Source': f'https://github.com/mikeqfu/{_package}',
        'Tracker': f'https://github.com/mikeqfu/{_package}/issues',
    },

    packages=setuptools.find_packages(exclude=["*.tests", "tests.*", "tests"]),

    install_requires=[
        'beautifulsoup4',
        'numpy',
        'pandas',
        'requests',
        'pyhelpers>=1.3.0',
    ],

    package_data={"": ["dat/*", "requirements.txt", "LICENSE"]},
    include_package_data=True,

)
