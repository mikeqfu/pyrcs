import setuptools

with open("README.md", 'r') as readme:
    long_description = readme.read()

setuptools.setup(

    name='pyrcscraper',
    version='0.0.1',

    author='Qian Fu',
    author_email='qian.fu@outlook.com',

    description=" A little web scraping tool for collecting railway codes used in GB.",
    long_description=long_description,
    long_description_content_type="text/markdown",

    url='https://github.com/mikeqfu/pyrcscraper',

    install_requires=[
        'beautifulsoup4',
        'fuzzywuzzy',
        'measurement',
        'more-itertools',
        'numpy',
        'pandas',
        'pdfkit',
        'python-rapidjson',
        'requests',
        'sqlalchemy',
        'sqlalchemy-utils'
    ],

    packages=setuptools.find_packages(exclude=["*.tests", "tests.*", "tests"]),

    package_data={"pyrcscraper": ["dat/*"]},
    include_package_data=True,

    classifiers=[
        'License :: OSI Approved :: MIT',
        'Programming Language :: Python :: 3.x',
        'Operating System :: Microsoft :: Windows :: Windows 10',
    ],
)
