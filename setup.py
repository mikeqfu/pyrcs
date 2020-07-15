import setuptools

import pyrcs

with open("README.rst", 'r', encoding='utf-8') as readme:
    long_description = readme.read()

with open("requirements.txt") as f:
    requirements = f.readlines()
install_requirements = [r.strip() for r in requirements]

setuptools.setup(

    name=pyrcs.__package_name__,
    version=pyrcs.__version__,

    author=pyrcs.__author__,
    author_email=pyrcs.__email__,

    description=pyrcs.__description__,
    long_description=long_description,
    long_description_content_type="text/x-rst",

    url='https://github.com/mikeqfu/pyrcs',

    install_requires=install_requirements,

    packages=setuptools.find_packages(exclude=["*.tests", "tests.*", "tests"]),

    include_package_data=True,

    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux'
    ],
)
