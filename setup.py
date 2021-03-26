import setuptools

import pyrcs

with open("README.rst", 'r', encoding='utf-8') as readme:
    long_description = readme.read()

setuptools.setup(

    name=pyrcs.__package_name__,

    version=pyrcs.__version__,

    description=pyrcs.__description__,
    long_description=long_description,
    long_description_content_type="text/x-rst",

    url='https://github.com/mikeqfu/pyrcs',

    author=pyrcs.__author__,
    author_email=pyrcs.__email__,

    license='GPLv3',

    classifiers=[
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

    keywords=['Python', 'Railway Codes', 'Railway', 'CRS', 'NLC', 'TIPLOC', 'STANOX',
              'Electrification', 'ELR', 'Mileage', 'LOR', 'Stations', 'Signal boxes',
              'Tunnels', 'Viaducts', 'Depots', 'Tracks'],

    project_urls={
        'Documentation': 'https://pyrcs.readthedocs.io/en/latest/',
        'Source': 'https://github.com/mikeqfu/pyrcs',
        'Tracker': 'https://github.com/mikeqfu/pyrcs/issues',
    },

    packages=setuptools.find_packages(exclude=["*.tests", "tests.*", "tests"]),

    install_requires=[
        'beautifulsoup4',
        'html5lib',
        'lxml',
        'measurement',
        'numpy',
        'pandas',
        'pyhelpers>=1.2.13',
        'requests',
    ],

    package_data={"": ["requirements.txt", "LICENSE"]},
    include_package_data=True,

)
