"""
Collects `railway station data <http://www.railwaycodes.org.uk/stations/station0.shtm>`_.
"""

import functools
import re
import string
import urllib.parse

import bs4
import pandas as pd

from .._base import _Base
from ..parser import _get_last_updated_date, get_catalogue, parse_tr
from ..utils import cd_data, get_collect_verbosity_for_fetch, handle_connection_error, \
    homepage_url, is_homepage_connectable, print_void_collection_message, validate_initial


def _split_elr_mileage_column(dat):
    """
    Split the ``'ELRMileage'`` column into ``'ELR'`` and ``'Mileage'`` columns.

    This function processes the engineering line reference (ELR) and mileage string
    representations by dividing them into distinct columns and applying necessary
    string standardisation.

    :param dat: Preprocessed data of the station locations.
    :type dat: pandas.DataFrame
    :return: Data with independent ``'ELR'`` and ``'Mileage'`` columns.
    :rtype: pandas.DataFrame
    """

    em_col_name = next((col for col in dat.columns if re.match(r'ELR ?Mileage', col)), None)
    if em_col_name is None:
        return dat

    temp = dat[em_col_name].str.split(r'\t\t / | / \[', n=1, regex=True, expand=True)
    if temp.shape[1] == 1:
        temp[1] = ''

    temp.columns = ['ELR', 'Mileage']

    def _replace_elr(x, repl=' &&& '):
        if pd.isna(x):
            return x

        y = str(x).strip()

        if '  /  ' in y:
            return y.replace('  /  ', repl)
        if ' / ' in y:
            return y.replace(' / ', repl)
        if ' ' in y:
            return y.replace(' ', repl)
        return y

    elr_dat = temp['ELR'].map(_replace_elr)

    def _clean_mileage(x):
        if pd.isna(x) or str(x).strip() == '':
            return ''
        parts = str(x).split('\t\t / ')
        cleaned_parts = [' / '.join(p.strip(' []').split('  ')) for p in parts]

        mil = cleaned_parts[0] if len(cleaned_parts) == 1 else ' &&& '.join(cleaned_parts)
        pat = re.compile(r'(?<=\S)\s*/\s*(?=\S)')
        if pat.search(mil):
            return re.sub(pat, ' &&& ', mil)

        return mil

    mil_dat = temp['Mileage'].map(_clean_mileage)

    dat = dat.drop(columns=[em_col_name])
    dat.insert(1, 'ELR', elr_dat)
    dat.insert(2, 'Mileage', mil_dat)

    return dat


def _align_list_lengths(df, target_cols):
    """
    Equalise list lengths across target columns for each row in a DataFrame.

    This function ensures all specified columns contain lists of identical length for
    every row, repeating single-element lists or padding shorter lists with empty
    strings to prevent errors during multi-column explosion.

    :param df: Target DataFrame containing list elements.
    :type df: pandas.DataFrame
    :param target_cols: Column names whose list lengths should be equalised.
    :type target_cols: list[str]
    :return: DataFrame with aligned list lengths across target columns.
    :rtype: pandas.DataFrame
    """

    cols = [c for c in target_cols if c in df.columns]
    if not cols or df.empty:
        return df

    for col in cols:
        df[col] = df[col].map(lambda x: x if isinstance(x, list) else [x])

    def _pad_row(row):
        lengths = [len(row[c]) for c in cols]
        max_len = max(lengths) if lengths else 1
        if max_len <= 1 or all(length == max_len for length in lengths):
            return row
        for c in cols:
            curr_len = len(row[c])
            if curr_len < max_len:
                if curr_len == 1:
                    row[c] = row[c] * max_len
                else:
                    row[c] = row[c] + [''] * (max_len - curr_len)
        return row

    return df.apply(_pad_row, axis=1)


def _check_row_spans(dat):
    """
    Check and expand data rows containing row spans in coordinate or mileage columns.

    This function identifies rows where multiple values are merged using delimiters
    and explodes them across multiple rows to ensure each row represents a single entity.

    :param dat: Preprocessed data of the station locations.
    :type dat: pandas.DataFrame
    :return: Data with row spans expanded into individual rows.
    :rtype: pandas.DataFrame
    """

    em_col_names = ['ELR', 'Mileage']
    coords_col_names = ['Degrees Longitude', 'Degrees Latitude']
    ref_col_name = ['Grid Reference']

    cols = em_col_names + coords_col_names + ref_col_name

    if not all(col in dat.columns for col in cols):
        return dat

    has_spans: pd.Series = dat['Degrees Longitude'].astype(str).str.contains(r' / |\r', regex=True)
    temp1: pd.DataFrame = dat.loc[has_spans].copy()

    existing_cols = [c for c in cols if c in temp1.columns]

    if not temp1.empty:
        for col in existing_cols:
            temp1[col] = temp1[col].astype(str).str.split(r' &&& |\r| / ', regex=True)

        try:
            # Modern pandas supports multi-column explode if list lengths match
            temp1 = temp1.explode(existing_cols, ignore_index=True)
        except ValueError:
            # Fallback for mismatched list lengths
            exploded_cols = {col: temp1[col].explode(ignore_index=True) for col in existing_cols}
            other_cols = [c for c in temp1.columns if c not in existing_cols]
            base_expanded = (
                temp1[other_cols].loc[temp1.index.repeat(temp1[existing_cols[0]].str.len())]
                .reset_index(drop=True)
            )
            temp1 = pd.concat([base_expanded] + list(exploded_cols.values()), axis=1)

        dat0 = pd.concat([dat.loc[~has_spans], temp1], ignore_index=True)

    else:
        dat0 = dat.copy()

    active_em_cols = [c for c in em_col_names if c in dat0.columns]
    if active_em_cols:
        for col in active_em_cols:
            dat0[col] = dat0[col].map(
                lambda x: x.split(' &&& ') if isinstance(x, str) and ' &&& ' in x else [x]
            )

        dat0 = _align_list_lengths(dat0, active_em_cols)
        dat0 = dat0.explode(active_em_cols, ignore_index=True)

    return dat0


def _parse_coordinates_columns(dat):
    """
    Parse ``'Degrees Longitude'`` and ``'Degrees Latitude'`` of the station locations data.

    :param dat: Preprocessed data of the station locations.
    :type dat: pandas.DataFrame
    :return: Data with parsed and sanitised coordinates.
    :rtype: pandas.DataFrame
    """

    ll_col_names = ['Degrees Longitude', 'Degrees Latitude']
    existing_cols = [c for c in ll_col_names if c in dat.columns]

    if existing_cols:
        dat[existing_cols] = dat[existing_cols].replace(r'(c\.)|≈', '', regex=True)

        def _to_float(x):
            if pd.isna(x):
                return x
            x_str = str(x).strip()
            return float(x_str) if x_str else None

        for col in existing_cols:
            dat[col] = dat[col].map(_to_float)

    return dat


def _extract_picture_links_and_clean_trs(trs, base_url='http://www.railwaycodes.org.uk/stations/'):
    """
    Extract picture links from table row tags and decompose sign containers.

    This function iterates through BeautifulSoup table row tags, collects image URLs
    from sign container elements and removes those elements from the DOM tree to prevent
    duplicate station text during table parsing.

    :param trs: List of table row tags.
    :type trs: list[bs4.element.Tag]
    :param base_url: Base URL used to resolve relative picture links.
        Defaults to ``'http://www.railwaycodes.org.uk/stations/'``.
    :type base_url: str
    :return: List of extracted picture link strings for each table row.
    :rtype: list[str]
    """

    pic_links = []

    for tr in trs:
        links = []

        for div_signs in tr.find_all('div', class_='signs'):
            for a_tag in div_signs.find_all('a', href=True):
                href = a_tag.get('href')

                if isinstance(href, str):
                    full_url = urllib.parse.urljoin(base_url, href.strip())
                    if full_url not in links:
                        links.append(full_url)

            div_signs.decompose()

        pic_links.append(' / '.join(links))

    return pic_links


def _deduplicate_name(name_str):
    if not isinstance(name_str, str) or not name_str.strip():
        return ''
    parts = [p.strip() for p in name_str.split(' / ') if p.strip()]
    if not parts:
        return ''

    part0 = parts[0]
    words = part0.split()
    num_words = len(words)
    if num_words > 1 and num_words % 2 == 0:
        half = num_words // 2
        w1 = ' '.join(words[:half])
        w2 = ' '.join(words[half:])
        if w1.lower().replace('&', 'and') == w2.lower().replace('&', 'and'):
            return w1

    for p in parts[1:]:
        if part0.lower().startswith(p.lower()):
            return part0[:len(p)].strip()

    return part0


def _clean_crs(z):
    if not isinstance(z, str):
        return z

    z = re.sub(r'[()]', '', z)

    if ' &&& ' in z:
        z_parts = []
        for z_ in z.split(' &&& '):
            split_z = z_.split('✖')
            if len(split_z) >= 2:
                z_parts.append(f"{split_z[0]} [{split_z[1]}]")
            else:
                z_parts.append(z_)
        return ' and '.join(z_parts)

    return z


def _parse_station_column(dat, pic_links=None):
    """
    Parse the station column of the station locations data.

    This function identifies the station column (e.g. ``'( CRS ) Station'`` or
    ``'Station'``), separates station names from Computer Reservation System (CRS)
    codes, extracts supplementary notes, inserts picture links and eliminates
    duplicate station names.

    :param dat: Preprocessed data of the station locations.
    :type dat: pandas.DataFrame
    :param pic_links: Extracted picture links for each row. Defaults to ``None``.
    :type pic_links: list[str] | None
    :return: Data with parsed station names, station notes, picture links, CRS codes and CRS notes.
    :rtype: pandas.DataFrame

    **Examples**::

        # Handles formats such as:
        # "Hythe Road\\t\\t / [CRS awaited]"
        # "Heathrow Junction [sometimes referred to as Heathrow Interchange]\\t\\t / [no CRS?]"
    """

    stn_cols = [col for col in dat.columns if 'Station' in col]
    if not stn_cols:
        return dat

    stn_col_name = stn_cols[0]

    if stn_col_name != 'Station':
        dat = dat.rename(columns={stn_col_name: 'Station'})
        stn_col_name = 'Station'

    temp1 = dat[stn_col_name].astype(str).str.split('\t\t', n=1, expand=True)

    if temp1.shape[1] == 1:
        temp1[1] = ''
    temp1.columns = [stn_col_name, 'CRS']

    stn_names = []
    stn_notes = []

    for x in temp1[stn_col_name].fillna('').str.rstrip(' / ').str.strip():
        if isinstance(x, str) and '[' in x and ']' in x:
            match = re.search(r' \[(.*)](✖.*)?', x)
            if match:
                y = match.group(0)
                raw_name = x.replace(y, '').strip()
                stn_names.append(_deduplicate_name(raw_name))
                if '✖' in y:
                    stn_notes.append('; '.join([y_.strip(' []') for y_ in y.split('✖')]))
                else:
                    stn_notes.append(re.sub(r"'\s*([^']+?)\s*'", r"'\1'", y.strip(' []')))
                continue
        stn_names.append(_deduplicate_name(x))
        stn_notes.append('')

    dat[stn_col_name] = stn_names

    stn_loc = dat.columns.get_loc(stn_col_name)
    dat.insert(loc=stn_loc + 1, column='Station Note', value=stn_notes)

    if pic_links is not None and len(pic_links) == len(dat):
        dat.insert(loc=stn_loc + 2, column='Picture Link', value=pic_links)
    elif 'Picture Link' not in dat.columns:
        dat.insert(loc=stn_loc + 2, column='Picture Link', value='')

    temp2 = temp1['CRS'].fillna('').str.replace(' / /', ' &&& ').str.split(
        r'  | / ', regex=True, expand=True).fillna('')

    if temp2.shape[1] == 1:
        temp2.columns = ['CRS']
        temp2['CRS Note'] = ''
    else:
        temp2.columns = ['CRS', 'CRS Note']
        temp2['CRS Note'] = temp2['CRS Note'].str.strip('[]')

    temp2['CRS'] = temp2['CRS'].map(_clean_crs).str.strip()

    cols_to_drop = [c for c in ['CRS', 'CRS Note'] if c in dat.columns]
    if cols_to_drop:
        dat = dat.drop(columns=cols_to_drop)

    dat = pd.concat([dat, temp2[['CRS', 'CRS Note']]], axis=1).sort_values(stn_col_name)

    return dat


def _parse_owner_and_operator(x):
    """
    Parse a single string describing owners and operators into current and former lists.

    :param x: The string containing the owner or operator information.
    :type x: str | Any
    :return: A tuple comprising current and former owners or operators.
    :rtype: tuple[str, str]

    x = dat['Owner'][0]
    x = dat['Owner'][2]
    """

    if not isinstance(x, str):
        return '', ''

    pat1 = re.compile(r'  ?/  ?and  ?/  ?')
    pat2 = re.compile(r' / |\r')

    if pat1.search(x):
        y, y_ = re.sub(pat1, ' &&& ', x), ''
    elif pat2.search(x):
        x_ = re.split(pat2, x)
        if len(x_) > 1:
            y = x_[0]
            y_ = x_[1] if len(x_[1:]) == 1 else ' / '.join(x_[1:])
        else:
            y, y_ = x_[0], ''
    else:
        y, y_ = x, ''

    if '✖' in y or ' &&& ' in y:
        y_parts = []
        for z in y.split(' &&& '):
            split_z = z.split('✖')
            if len(split_z) >= 2:
                y_parts.append(f"{split_z[0]} [{split_z[1]}]")
            else:
                y_parts.append(z)
        y = ' and '.join(y_parts)

    # if ' [from ' in y or ' (form ' in y:
    #     y = remove_punctuation(y)

    return y, y_


def _parse_owner_and_operator_columns(dat):
    """
    Parse ``'Owner'`` and ``'Operator'`` columns of the station locations data.

    :param dat: Preprocessed data of the station locations.
    :type dat: pandas.DataFrame
    :return: Data with parsed information of current and former owners and operators.
    :rtype: pandas.DataFrame
    """

    df = dat.copy()

    for col in ['Owner', 'Operator']:
        if col in df.columns:
            parsed = df[col].map(_parse_owner_and_operator)

            df[col] = parsed.map(lambda x: x[0])

            former_col = f"Former {col}"
            df.insert(
                loc=df.columns.get_loc(col) + 1,
                column=former_col,
                value=parsed.map(lambda x: x[1])
            )

    return df


class Stations(_Base):
    """
    A class for collecting
    `railway station data <http://www.railwaycodes.org.uk/stations/station0.shtm>`_.
    """

    #: The name of the data.
    NAME: str = 'Railway station data'

    #: The key for accessing the data.
    KEY: str = 'Stations'

    #: The key for accessing the data of *Mileages, operators and grid coordinates*.
    KEY_TO_STN: str = 'Mileages, operators and grid coordinates'

    #: The URL of the main web page for the data.
    URL: str = urllib.parse.urljoin(homepage_url(), '/stations/station0.shtm')

    #: The key used to reference the last updated date in the data.
    KEY_TO_LAST_UPDATED_DATE: str = 'Last updated date'

    def __init__(self, data_dir=None, update=False, verbose=True):
        """
        :param data_dir: The name of the directory for storing the data. Defaults to ``None``.
        :type data_dir: str | None
        :param update: Whether to check for updates to the catalogue. Defaults to ``False``.
        :type update: bool
        :param verbose: Whether to print relevant information to the console. Defaults to ``True``.
        :type verbose: bool | int

        :ivar dict catalogue: The catalogue of the data.
        :ivar str last_updated_date: The date when the data was last updated.
        :ivar str data_dir: The path to the directory containing the data.
        :ivar str current_data_dir: The path to the current data directory.

        **Examples**::

            >>> from pyrcs.other_assets import Stations  # from pyrcs import Stations
            >>> stn = Stations()
            >>> stn.NAME
            'Railway station data'
            >>> stn.URL
            'http://www.railwaycodes.org.uk/stations/station0.shtm'
        """

        super().__init__(
            data_dir=data_dir,
            data_category="other-assets",
            update=update,
            verbose=verbose
        )

        self.catalogue = self.fetch_catalogue(update=update, verbose=False)

        self.station_names_errata = {
                "-By-": "-by-",
                "-In-": "-in-",
                "-En-Le-": "-en-le-",
                "-La-": "-la-",
                "-Le-": "-le-",
                "-On-": "-on-",
                "-The-": "-the-",
                " Of ": " of ",
                "-Super-": "-super-",
                "-Upon-": "-upon-",
                "-Under-": "-under-",
                "-Y-": "-y-",
            }

    def _collect_catalogue(self, source, verbose=False):
        # noinspection shadowing-names
        """
        Parse and collect the station catalogue from the provided HTML source.

        This method extracts links from the secondary navigation bar to build a
        hierarchical catalogue of station data. It retrieves sub-catalogues
        dynamically and saves the final structured output to a JSON file.

        :param source: The HTTP response object containing the webpage content.
        :type source: requests.Response | Any
        :param verbose: Whether to print progress to the console. Defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary representing the hierarchical station catalogue.
        :rtype: dict
        :raises ValueError: If the required navigation elements are missing from the source.

        **Examples**::

            >>> from pyrcs.other_assets import Stations
            >>> from pyhelpers.ops import fake_requests_headers
            >>> import requests

            >>> stn = Stations()

            >>> url = 'http://www.railwaycodes.org.uk/stations/station0.shtm'
            >>> source = requests.get(url, headers=fake_requests_headers())
            >>> data = stn._collect_catalogue(source, verbose=True)
        """

        soup = bs4.BeautifulSoup(markup=source.text, features='html.parser')

        navs = soup.find_all('nav')
        if len(navs) < 2:
            raise ValueError("Expected at least two '<nav>' elements in the source HTML.")

        nav_tag = navs[1]

        nav_links = {
            a.get_text(strip=True): urllib.parse.urljoin(self.URL, a.get('href'))
            for a in nav_tag.find_all('a')
            if a.get('href')
        }

        catalogue = {}
        for key, url in nav_links.items():
            sub_cat: dict = get_catalogue(url=url, update=True, json_it=False)

            if sub_cat != nav_links:
                if key in sub_cat:
                    sub_cat.pop(key)
                elif 'Introduction' in sub_cat:
                    sub_cat.pop('Introduction')

                if url in sub_cat.values():
                    catalogue[key] = sub_cat
                else:
                    catalogue[key] = {'Introduction': url, **sub_cat}

            else:
                catalogue[key] = url

        if verbose in {True, 1}:
            print("Done.")

        parsed_url = urllib.parse.urlparse(self.URL)
        data_name = parsed_url.path.strip('/').removesuffix('.shtm').replace('/', '-')

        self._save_data_to_file(
            data=catalogue,
            data_name=data_name,
            ext=".json",
            dump_dir=cd_data("catalogue"),
            verbose=verbose,
            indent=4
        )

        return catalogue

    def collect_catalogue(self, confirmation_required=True, verbose=False, raise_error=False):
        """
        Collects the catalogue of `railway station data`_ from the source web page.

        .. _`railway station data`: http://www.railwaycodes.org.uk/stations/station0.shtm

        :param confirmation_required: Whether user confirmation is required;
            if ``confirmation_required=True`` (default), prompts the user for confirmation
            before proceeding with data collection.
        :type confirmation_required: bool
        :param verbose: Whether to print relevant information to the console. Defaults to ``False``.
        :type verbose: bool | int
        :param raise_error: Whether to raise the provided exception;
            if ``raise_error=False`` (default), the error will be suppressed.
        :type raise_error: bool
        :return: A dictionary containing the catalogue of railway station data,
            or ``None`` if no data catalogue is collected.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.other_assets import Stations

            >>> stn = Stations()

            >>> stn.collect_catalogue(verbose=True)
        """

        catalogue = self._collect_data_from_source(
            data_name=f'{self.NAME.lower()} catalogue',
            method=self._collect_catalogue,
            url=self.URL,
            confirmation_required=confirmation_required,
            verbose=verbose,
            raise_error=raise_error
        )

        return catalogue

    def fetch_catalogue(self, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetches the catalogue of `railway station data`_.

        .. _`railway station data`: http://www.railwaycodes.org.uk/stations/station0.shtm

        :param update: Whether to check for updates to the package data. Defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console. Defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the catalogue of railway station data,
            or ``None`` if no data catalogue is collected.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.other_assets import Stations  # from pyrcs import Stations

            >>> stn = Stations()

            >>> stn_data_cat = stn.fetch_catalogue()

            >>> type(stn_data_cat)
            dict
            >>> list(stn_data_cat)
            ['Mileages, operators and grid coordinates',
             'Bilingual names',
             'Sponsored signs',
             'Not served by SFO',
             'International',
             'Trivia',
             'Access rights',
             'Barrier error codes',
             'London Underground',
             'Railnet']
        """

        data_name = urllib.parse.urlparse(
            self.URL).path.lstrip('/').rstrip('.shtm').replace('/', '-')

        args = {
            'data_name': data_name,
            'method': self.collect_catalogue,
            'ext': ".json",
            'data_dir': cd_data("catalogue"),
        }
        kwargs.update(args)

        catalogue = self._fetch_data_from_file(
            update=update, dump_dir=dump_dir, verbose=verbose, **kwargs)

        return catalogue

    def _collect_locations(self, initial, source, verbose=False):
        # noinspection shadowing-names
        """
        Parse and collect station location data for a specific initial letter.

        This method processes the HTML content of a station locations page, extracts the
        primary table, applies a sequence of data cleaning transformations and saves the
        resulting dataset to disk.

        :param initial: The initial letter representing the alphabetical category.
        :type initial: str
        :param source: The HTTP response object containing the webpage content.
        :type source: requests.Response | Any
        :param verbose: Whether to print progress to the console. Defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the parsed station data and the last updated date.
        :rtype: dict
        :raises ValueError: If the required table header or body structure is missing.

        **Examples**::

            >>> from pyrcs.other_assets import Stations
            >>> from pyhelpers.ops import fake_requests_headers
            >>> import requests

            >>> stn = Stations()

            >>> initial = 'a'
            >>> url = 'http://www.railwaycodes.org.uk/stations/stationa.shtm'
            >>> source = requests.get(url, headers=fake_requests_headers())
            >>> data = stn._collect_locations(initial, source, verbose=True)
        """

        initial_ = validate_initial(initial)

        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')
        thead = soup.find('thead')
        tbody = soup.find('tbody')

        if not thead or not tbody:
            raise ValueError(
                f"Table structure missing in source content for initial '{initial_}'."
            )

        # Create a DataFrame of the requested table
        trs = tbody.find_all('tr')
        ths = [
            re.sub(r'\s+', ' ', th.get_text(separator=' ', strip=True))
            for th in thead.find_all('th')
        ]

        dat: pd.DataFrame = parse_tr(trs=trs, ths=ths, as_dataframe=True)

        # Extract picture links and clean sign tags prior to DataFrame parsing
        pic_links = _extract_picture_links_and_clean_trs(trs=trs)

        parser_funcs = [
            _split_elr_mileage_column,
            _check_row_spans,
            _parse_coordinates_columns,
            functools.partial(_parse_station_column, pic_links=pic_links),
            _parse_owner_and_operator_columns,
        ]
        for f in parser_funcs:
            # # Debugging
            # for f in parser_funcs:
            #     try:
            #         dat = f(dat)
            #     except Exception e:
            #         print(f)
            #         break
            dat = f(dat)

        # Explode only if target columns exist
        explode_cols = [c for c in ['ELR', 'Mileage'] if c in dat.columns]
        if explode_cols:
            dat = dat.explode(column=explode_cols, ignore_index=True)

        # Apply errata replacements and sort
        stn_col_name = 'Station'
        if stn_col_name in dat.columns and hasattr(self, 'station_names_errata'):
            dat[stn_col_name] = dat[stn_col_name].replace(self.station_names_errata, regex=True)
            dat = dat.sort_values(stn_col_name, ignore_index=True)

        data = {
            initial_: dat,
            self.KEY_TO_LAST_UPDATED_DATE: _get_last_updated_date(soup)
        }

        if verbose in {True, 1}:
            print("Done.")

        self._save_data_to_file(data=data, data_name=initial_, sub_dir="a-z", verbose=verbose)

        return data

    def collect_locations(self, initial, confirmation_required=True, verbose=False,
                          raise_error=False):
        """
        Collects data of `railway station locations
        <http://www.railwaycodes.org.uk/stations/station0.shtm>`_
        (mileages, operators and grid coordinates) for a given initial letter.

        :param initial: The initial letter (e.g. ``'a'``, ``'z'``) of railway station names.
        :type initial: str
        :param confirmation_required: Whether user confirmation is required;
            if ``confirmation_required=True`` (default), prompts the user for confirmation
            before proceeding with data collection.
        :type confirmation_required: bool
        :param verbose: Whether to print relevant information to the console. Defaults to ``True``.
        :type verbose: bool | int
        :param raise_error: Whether to raise the provided exception;
            if ``raise_error=False`` (default), the error will be suppressed.
        :type raise_error: bool
        :return: A dictionary containing the data of railway station locations whose initial letters
            are the given ``initial`` and date of when the data was last updated.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Stations  # from pyrcs import Stations

            >>> stn = Stations()

            >>> stn_loc_a_codes = stn.collect_locations(initial='a', verbose=True)
            Proceed with collecting data of "mileages, operators and grid coordinates" beginning..
             [No]|Yes: yes
            Collecting the data ... Done.

            >>> type(stn_loc_a_codes)
            dict
            >>> list(stn_loc_a_codes)
            ['A', 'Last updated date']

            >>> stn_loc_a_codes_df = stn_loc_a_codes['A']
            >>> stn_loc_a_codes_df.shape
            (143, 15)
            >>> stn_loc_a_codes_df.head()
                  Station                               Station Note  ...  CRS CRS Note
            0  Abbey Wood                                             ...  ABW
            1  Abbey Wood                                             ...  ABW
            2        Aber                                             ...  ABE
            3   Abercynon  formerly 'Abercynon South' to 24 May 2008  ...  ACY
            4   Abercynon  formerly 'Abercynon South' to 24 May 2008  ...  ACY
            [5 rows x 15 columns]

            >>> stn_loc_a_codes_df[['Station', 'ELR', 'Mileage']].head()
                  Station  ELR   Mileage
            0  Abbey Wood  NKL  11m 43ch
            1  Abbey Wood  XRS  24.458km
            2        Aber  CAR   8m 69ch
            3   Abercynon  CAM  16m 28ch
            4   Abercynon  ABD  16m 28ch
        """

        initial_ = validate_initial(initial=initial)

        url = self._get_url(key=self.KEY_TO_STN, initial=initial_, raise_error=raise_error)

        data = self._collect_data_from_source(
            data_name=self.KEY_TO_STN.lower(),
            method=self._collect_locations,
            initial=initial_,
            url=url,
            confirmation_required=confirmation_required,
            verbose=verbose,
            raise_error=raise_error
        )

        return data

    def fetch_locations(self, initial=None, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetches data of `railway station locations`_ (mileages, operators and grid coordinates).

        .. _`railway station locations`:
            http://www.railwaycodes.org.uk/stations/station0.shtm

        :param initial: The initial letter (e.g. ``'a'``, ``'z'``) of railway station names.
        :type initial: str
        :param update: Whether to check for updates to the package data. Defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console. Defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the data of railway station locations and
            the date of when the data was last updated.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Stations  # from pyrcs import Stations

            >>> stn = Stations()

            >>> stn_loc_codes = stn.fetch_locations()

            >>> list(stn_loc_codes)
            ['Mileages, operators and grid coordinates', 'Last updated date']

            >>> stn_loc_codes_df = stn_loc_codes['Mileages, operators and grid coordinates']
            >>> stn_loc_codes_df.shape
            (2932, 15)
            >>> stn_loc_codes_df.head()
                  Station                               Station Note  ...  CRS CRS Note
            0  Abbey Wood                                             ...  ABW
            1  Abbey Wood                                             ...  ABW
            2        Aber                                             ...  ABE
            3   Abercynon  formerly 'Abercynon South' to 24 May 2008  ...  ACY
            4   Abercynon  formerly 'Abercynon South' to 24 May 2008  ...  ACY
            [5 rows x 15 columns]

            >>> stn_loc_codes_df[['Station', 'ELR', 'Mileage']].head()
                  Station  ELR   Mileage
            0  Abbey Wood  NKL  11m 43ch
            1  Abbey Wood  XRS  24.458km
            2        Aber  CAR   8m 69ch
            3   Abercynon  CAM  16m 28ch
            4   Abercynon  ABD  16m 28ch
        """

        if initial:
            args = {
                'data_name': validate_initial(initial),
                'method': self.collect_locations,
                'sub_dir': "a-z",
                'initial': initial,
            }
            kwargs.update(args)

            railway_station_data = self._fetch_data_from_file(
                update=update, dump_dir=dump_dir, verbose=verbose, **kwargs)

        else:
            verbose_1 = get_collect_verbosity_for_fetch(data_dir=dump_dir, verbose=verbose)
            verbose_2 = verbose_1 if is_homepage_connectable() else False

            data_sets = [
                self.fetch_locations(initial=x, update=update, verbose=verbose_2)
                for x in string.ascii_lowercase
            ]

            if all(d[x] is None for d, x in zip(data_sets, string.ascii_uppercase)):
                if update:
                    handle_connection_error(verbose=verbose)
                    print_void_collection_message(data_name=self.KEY_TO_STN, verbose=verbose)

                data_sets = [
                    self.fetch_locations(x, update=False, verbose=verbose_1)
                    for x in string.ascii_lowercase
                ]

            stn_dat_tbl_ = (
                item[x] for item, x in zip(data_sets, string.ascii_uppercase)
            )
            stn_dat_tbl = sorted(
                [x for x in stn_dat_tbl_ if x is not None],
                key=lambda x: x.shape[1],
                reverse=True
            )
            stn_data: pd.DataFrame = pd.concat(stn_dat_tbl, axis=0, ignore_index=True, sort=False)

            stn_data = stn_data.where(pd.notna(stn_data), None)
            stn_data.sort_values(['Station'], inplace=True)

            stn_data.index = range(len(stn_data))

            last_updated_dates = (d[self.KEY_TO_LAST_UPDATED_DATE] for d in data_sets)
            latest_update_date = max(d for d in last_updated_dates if d is not None)

            railway_station_data = {
                self.KEY_TO_STN: stn_data,
                self.KEY_TO_LAST_UPDATED_DATE: latest_update_date,
            }

        if dump_dir is not None:
            self._save_data_to_file(
                data=railway_station_data,
                data_name=self.KEY_TO_STN,
                dump_dir=dump_dir,
                verbose=verbose
            )

        return railway_station_data
