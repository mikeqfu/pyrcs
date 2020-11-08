import setuptools

import pyrcs

with open("README.rst", 'r', encoding='utf-8') as readme:
    long_description = readme.read()

setuptools.setup(

    name=pyrcs.__package_name__,
    version=pyrcs.__version__,
    author=pyrcs.__author__,
    author_email=pyrcs.__email__,

    description=pyrcs.__description__,
    long_description=long_description,
    long_description_content_type="text/x-rst",

    url='https://github.com/mikeqfu/pyrcs',

    install_requires=[
        'beautifulsoup4~=4.9.3',
        'fake_useragent',
        'fuzzywuzzy~=0.18.0',
        'html5lib',
        'lxml',
        'measurement~=3.2.0',
        'more-itertools~=8.6.0',
        'numpy~=1.19.4',
        'pandas~=1.1.4',
        'pyhelpers>=1.2.6',
        'requests~=2.24.0',
    ],

    packages=setuptools.find_packages(exclude=["*.tests", "tests.*", "tests"]),

    include_package_data=True,

    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux'
    ],
)
