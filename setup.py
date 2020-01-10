import os

import setuptools

ver_no = '0.2.5'


def find_all_pkg_dat_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


dat_files = find_all_pkg_dat_files('pyrcs\\dat')


with open("README.md", 'r', encoding='utf-8') as readme:
    long_description = readme.read()

with open('requirements.txt') as f:
    requirements = f.readlines()
requirements_ = [r.strip() for r in requirements]

setuptools.setup(

    name='pyrcs',
    version=ver_no,

    author='Qian Fu',
    author_email='qian.fu@outlook.com',

    description="A data scraping tool for collection and storage of the railway codes used in the UK rail industry",
    long_description=long_description,
    long_description_content_type="text/markdown",

    url='https://github.com/mikeqfu/pyrcs',

    install_requires=requirements_,

    packages=setuptools.find_packages(exclude=["*.tests", "tests.*", "tests"]),

    package_data={"pyrcs": dat_files + ["line_data_cls/*", "other_assets_cls/*"]},
    include_package_data=True,

    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux'
    ],
)
