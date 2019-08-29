import os

import setuptools

ver = '0.2.0'


def find_all_pkg_dat_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


dat_files = find_all_pkg_dat_files('pyrcs\\dat')


with open("README.md", 'r', encoding='utf-8') as readme:
    long_description = readme.read()

setuptools.setup(

    name='pyrcs',
    version=ver,

    author='Qian Fu',
    author_email='qian.fu@outlook.com',

    description="A small web scraper for collecting the railway codes used in the UK rail industry",
    long_description=long_description,
    long_description_content_type="text/markdown",

    url='https://github.com/mikeqfu/pyrcs',

    install_requires=[
        'beautifulsoup4',
        'fuzzywuzzy',
        'html5lib',
        'lxml',
        'measurement',
        'more-itertools',
        'pandas',
        'pyhelpers',
        'python-Levenshtein',
        'requests',
        'sqlalchemy',
        'sqlalchemy-utils'
    ],

    packages=setuptools.find_packages(exclude=["*.tests", "tests.*", "tests"]),

    package_data={"pyrcs": dat_files + ["line_data_cls/*", "other_assets_cls/*"]},
    include_package_data=True,

    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: Microsoft :: Windows',
    ],
)
