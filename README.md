# pyrcs

**Author**: Qian Fu [![Twitter URL](https://img.shields.io/twitter/url/https/twitter.com/Qian_Fu?label=Follow&style=social)](https://twitter.com/Qian_Fu) 

[![PyPI](https://img.shields.io/pypi/v/pyrcs?color=important&label=PyPI)](https://pypi.org/project/pyrcs/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pyrcs?color=informational&label=Python)](https://www.python.org/downloads/)
[![GitHub](https://img.shields.io/pypi/l/pyrcs?color=green&label=License)](https://github.com/mikeqfu/pyrcs/blob/master/LICENSE)
[![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/mikeqfu/pyrcs?color=yellowgreen&label=Code%20size)](https://github.com/mikeqfu/pyrcs/tree/master/pyrcs)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/pyrcs?color=yellow&label=Downloads)](https://pypistats.org/packages/pyrcs)

A small web scraper for collecting railway codes and other data used in the UK rail industry. 



---

**<span style="font-size:larger;">Contents</span>**

- [Installation](#installation)
- [Quick start (Examples)](#quick-start-examples)
  - [1. CRS, NLC, TIPLOC and STANOX Codes](#crs-nlc-tiploc-and-stanox-codes)
    - [1.1  Location codes for a given initial letter](#locations-beginning-with-a-given-letter)
    - [1.2  All available location codes](#all-available-location-codes)
  - [2. Engineer's Line References (ELRs)](#elr)
    - [2.1  ELR codes](#elr-codes)
    - [2.2  Mileage files](#mileage-files)
  - [3. Railway stations data](#railway-stations-data)
- [Data source](http://www.railwaycodes.org.uk/misc/acknowledgements.shtm) & [Note](http://www.railwaycodes.org.uk/misc/contributing.shtm)

---



## Installation

```
pip3 install pyrcs
```

**Note**: 

* Make sure you have the most up-to-date version of `pip` installed.

  ```
  python -m pip3 install --upgrade pip
  ```

* The installation of one of the dependencies, `Python-Levenshtein`, requires VC2015 (or above). A workaround is to download and install its [.whl](https://www.lfd.uci.edu/~gohlke/pythonlibs/#python-levenshtein) file. For example, if you're using Python 3.8 on 64-bit OS, you can download and install "python_Levenshtein-0.12.0-cp38-cp38-win_amd64.whl" manually: 

  ```
  pip3 install \path\to\python_Levenshtein-0.12.0-cp38-cp38-win_amd64.whl
  ```



## Quick start (Examples) <a name="quick-start-examples"></a>

The following examples provide a quick guide to the use of the package.



### 1.  Get "CRS, NLC, TIPLOC and STANOX Codes" <a name="crs-nlc-tiploc-and-stanox-codes"></a>

###### There are several ways of importing the module/class. 

***Alternative 1***: 

If your preferred import style is `from <module> import <name>`:

```python
from pyrcs.line_data_cls import crs_nlc_tiploc_stanox as ldlc
```

Or

```python
from pyrcs.line_data import crs_nlc_tiploc_stanox as ldlc
```

If your prefer `import <module>.<name>`:

```python
import pyrcs.line_data_cls.crs_nlc_tiploc_stanox as ldlc
```

After importing the module, you can create a 'class' for the location codes (including all CRS, NLC, TIPLOC, STANME and STANOX) :

```python
location_codes = ldlc.LocationIdentifiers()
```

***Alternative 2*** (*Used for the following examples*):

```python
from pyrcs.line_data import LineData
line_data = LineData()
```

`line_data` contains all classes under the category of "[Line data](http://www.railwaycodes.org.uk/linedatamenu.shtm)". That way, `location_codes` is equivalent to `line_data.LocationIdentifiers`.

```python
location_codes = line_data.LocationIdentifiers
```



#### 1.1  Locations beginning with a given letter <a name="locations-beginning-with-a-given-letter"></a>

By using the method `collect_location_codes_by_initial`, you can get the location codes, which start with a specific letter, say `'A'` or `'a'`: 

```python
# The input is case-insensitive
location_codes_a = line_data.LocationIdentifiers.collect_location_codes_by_initial('A')
```

`location_codes_a` is a `dict`, with the keys being: 

* `'A'`
* `'Additional_note'`
* `'Last_updated_date'`

Their corresponding values are:

* `location_codes_a['A']`  is a `pandas.DataFrame` that contains the table data. You may compare it with the table on the [web page](http://www.railwaycodes.org.uk/crs/CRSa.shtm).
* `location_codes_a['Additional_note']` is some additional information on the web page (if available).
* `location_codes_a['Last_updated_date']` is the date (`str`) when the web page was last updated.



#### 1.2  All available location codes in this category <a name="all-available-location-codes"></a>

You can also get all available location codes in this category as a whole , using the method `fetch_location_codes`, which also returns a `dict`:

```python
location_codes_data = line_data.LocationIdentifiers.fetch_location_codes()
```

The keys of `location_codes_a` include: 

- `'Location_codes'`
- `'Latest_updated_date'` 
- `'Additional_note'`
- `'Other_systems'`

Their corresponding values are:

- `location_codes_data['Location_codes']`  is a `pandas.DataFrame` that contains all table data (from 'A' to 'Z').
- `location_codes_data['Latest_updated_date']` is the latest 'Last_updated_date' (in `str`) among all initial-specific table data.
- `location_codes_data['Additional_note']` is some important additional information on the web page (if available).
- `location_codes_data['Other_systems']` is a `dict` for "[Other systems](http://www.railwaycodes.org.uk/crs/CRS1.shtm)".



### 2.  Get "Engineer's Line References (ELRs)" <a name="elr"></a>

Now you need to use the class`line_data.ELRMileages`, which could just be assigned to any simpler variable, e.g.`em`

```python
em = line_data.ELRMileages
```



#### 2.1  ELR codes <a name="elr-codes"></a>

To get ELR codes starting with a specific letter, say `'A'`, you can use the method `collect_elr_by_initial`, which returns a `dict`. 

```python
elr_a = em.collect_elr_by_initial('A')  
# Or elr_a = line_data.ELRMileages.collect_elr_by_initial('a')
```

The keys of `elr_a` include: 

- `'A'`
- `'Last_updated_date'`

Their corresponding values are:

- `elr_a['A']`  is a `pandas.DataFrame` that contains the table data. You may compare it with the table on the [web page](http://www.railwaycodes.org.uk/elrs/elra.shtm).
- `elr_a['Last_updated_date']` is the date (in `str`) when the web page was last updated.

To get all available ELR codes, by using the method `fetch_elr`, which also returns a `dict`:

```python
elr_codes = em.fetch_elr()
```

The keys of `elr_codes` include: 

- `'ELRs_mileages'`
- `'Latest_update_date'`

Their corresponding values are:

- `elr_codes['ELRs_mileages']`  is a `pandas.DataFrame` that contains all table data (from 'A' to 'Z').
- `elr_codes['Latest_updated_date']` is the latest 'Last_updated_date' (in `str`) among all initial-specific table data.



#### 2.2  Mileage files <a name="mileage-files"></a>

To collect more detailed mileage data for a given ELR, for example, `'AAM'`, you can use the method `fetch_mileage_file`, which returns a `dict`:

```python
em_amm = em.fetch_mileage_file('AAM')
```

The keys of `em_amm` include: 

- `'ELR'`
- `'Line'`
- `'Sub-Line'`
- `'AAM'`
- `'Note'`

Their corresponding values are:

- `em_amm['ELR']`  is the name (in `str`) of the given ELR
- `em_amm['Line']` is associated line name (in `str`) 
- `em_amm['Sub-Line']` is associated sub line name (in `str`), if available
- `em_amm['AAM']` is a `pandas.DataFrame` of the mileage file data



### 3.  Get "Railway stations data" <a name="railway-stations-data"></a>

The data of railway stations belongs to another category - "[Other assets](http://www.railwaycodes.org.uk/otherassetsmenu.shtm)"

```python
from pyrcs.other_assets import OtherAssets
other_assets = OtherAssets()
```

Similarly to **Sections** [**1.1**](#locations-beginning-with-a-given-letter) and [**2.1**](#elr-codes), to get stations data by a given initial letter (say `'A'`):

```python
stations_a = other_assets.Stations.collect_station_locations('A')
```

To get all available stations data:

```python
stations_data = other_assets.Stations.fetch_station_locations()
```

Both the data types of `stations_a` and `stations_data` are `dict`. 

