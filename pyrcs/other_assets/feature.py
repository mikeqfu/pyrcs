"""
Collect codes of infrastructure features.

This category includes:

    - `HABD and WILD <http://www.railwaycodes.org.uk/misc/habdwild.shtm>`_
    - `Water troughs <http://www.railwaycodes.org.uk/misc/troughs.shtm>`_
    - `Telegraph codes <http://www.railwaycodes.org.uk/misc/telegraph.shtm>`_
    - `Driver/guard buzzer codes <http://www.railwaycodes.org.uk/misc/buzzer.shtm>`_
"""

import itertools
import unicodedata

from pyhelpers.dir import cd

from pyrcs.utils import *


class _HABDWILD:
    """
    A class for `HABDs and WILDs <http://www.railwaycodes.org.uk/features/habdwild.shtm>`_.

    - HABD: Hot axle box detector
    - WILD: Wheel impact load detector
    """
    #: Name of the data
    NAME = 'Hot axle box detectors (HABDs) and wheel impact load detectors (WILDs)'
    #: Key of the `dict <https://docs.python.org/3/library/stdtypes.html#dict>`_-type data
    KEY = 'HABD and WILD'
    #: URL of the main web page of the data
    URL = urllib.parse.urljoin(home_page_url(), '/features/habdwild.shtm')
    #: Key of the data of the last updated date
    KEY_TO_LAST_UPDATED_DATE = 'Last updated date'
    pass


class _WaterTroughs:
    """
    A class for `water troughs locations <http://www.railwaycodes.org.uk/features/troughs.shtm>`_.
    """
    #: Name of the data
    NAME = 'Water trough locations'
    #: Key of the `dict <https://docs.python.org/3/library/stdtypes.html#dict>`_-type data
    KEY = 'Water troughs'
    #: URL of the main web page of the data
    URL = urllib.parse.urljoin(home_page_url(), '/features/troughs.shtm')
    #: Key of the data of the last updated date
    KEY_TO_LAST_UPDATED_DATE = 'Last updated date'
    pass


class _Telegraph:
    """
    A class for `telegraph code words <http://www.railwaycodes.org.uk/features/telegraph.shtm>`_.
    """
    #: Name of the data
    NAME = 'Telegraph code words'
    #: Key of the `dict <https://docs.python.org/3/library/stdtypes.html#dict>`_-type data
    KEY = 'Telegraphic codes'
    #: URL of the main web page of the data
    URL = urllib.parse.urljoin(home_page_url(), '/features/telegraph.shtm')
    #: Key of the data of the last updated date
    KEY_TO_LAST_UPDATED_DATE = 'Last updated date'
    pass


class _Buzzer:
    """
    A class for `buzzer codes <http://www.railwaycodes.org.uk/features/buzzer.shtm>`_.
    """
    #: Name of the data
    NAME = 'Buzzer codes'
    #: Key of the `dict <https://docs.python.org/3/library/stdtypes.html#dict>`_-type data
    KEY = 'Buzzer codes'
    #: URL of the main web page of the data
    URL = urllib.parse.urljoin(home_page_url(), '/features/buzzer.shtm')
    #: Key of the data of the last updated date
    KEY_TO_LAST_UPDATED_DATE = 'Last updated date'
    pass


def _decode_vulgar_fraction(x):
    for s in x:
        try:
            name = unicodedata.name(s)
            if name.startswith('VULGAR FRACTION'):
                # normalized = unicodedata.normalize('NFKC', s)
                # numerator, _, denominator = normalized.partition('⁄')
                # frac_val = int(numerator) / int(denominator)
                frac_val = unicodedata.numeric(s)
                return frac_val
        except (TypeError, ValueError):
            pass


def _parse_vulgar_fraction_in_length(x):
    """
    Parse 'VULGAR FRACTION' for 'Length' of water trough locations.
    """

    if x == '':
        yd = np.nan

    elif re.match(r'\d+yd', x):  # e.g. '620yd'
        yd = int(re.search(r'\d+(?=yd)', x).group(0))

    elif re.match(r'\d+&frac\d+;yd', x):  # e.g. '506&frac23;yd'
        yd, frac = re.search(r'([0-9]+)&frac([0-9]+)(?=;yd)', x).groups()
        yd = int(yd) + int(frac[0]) / int(frac[1])

    else:  # e.g. '557½yd'
        yd = _decode_vulgar_fraction(x)

    return yd


def _parse_telegraph_in_use_term(x):
    if x == '♠':
        y = 'cross industry term used in 1939'
    elif x == '†':
        y = 'cross industry term used in 1939 and still used by BR in the 1980s'
    else:
        y = x

    return y


class Features:
    """
    A class for collecting codes of several infrastructure features.
    """

    #: Name of the data
    NAME = 'Infrastructure features'
    #: Key of the `dict <https://docs.python.org/3/library/stdtypes.html#dict>`_-type data
    KEY = 'Features'

    #: Key of the dict-type data of '*HABD*' and '*WILD*'
    KEY_TO_HABD_WILD = _HABDWILD.KEY
    #: Key of the dict-type data of '*water troughs*'
    KEY_TO_TROUGH = _WaterTroughs.KEY
    #: Key of the dict-type data of '*telegraph codes*'
    KEY_TO_TELEGRAPH = _Telegraph.KEY
    #: Key of the dict-type data of '*buzzer codes*'
    KEY_TO_BUZZER = _Buzzer.KEY

    #: Key of the data of the last updated date
    KEY_TO_LAST_UPDATED_DATE = 'Last updated date'

    def __init__(self, data_dir=None, update=False, verbose=True):
        """
        :param data_dir: name of data directory, defaults to ``None``
        :type data_dir: str or None
        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console, defaults to ``True``
        :type verbose: bool or int

        :ivar dict catalogue: catalogue of the data
        :ivar str last_updated_date: last updated date
        :ivar str data_dir: path to the data directory
        :ivar str current_data_dir: path to the current data directory

        **Examples**::

            >>> from pyrcs.other_assets import Features  # from pyrcs import Features

            >>> feats = Features()

            >>> print(feats.NAME)
            Infrastructure features
        """

        print_connection_error(verbose=verbose)

        self.catalogue = get_catalogue(url=_HABDWILD.URL, update=update, confirmation_required=False)

        self.data_dir, self.current_data_dir = init_data_dir(self, data_dir, category="other-assets")

    def _cdd(self, *sub_dir, **kwargs):
        """
        Change directory to package data directory and subdirectories (and/or a file).

        The directory for this module: ``"data\\other-assets\\features"``.

        :param sub_dir: subdirectory or subdirectories (and/or a file)
        :type sub_dir: str
        :param kwargs: [optional] parameters of the function `pyhelpers.dir.cd`_
        :return: path to the backup data directory for the class
            :py:class:`~pyrcs.other_assets.feature.Features`
        :rtype: str

        .. _`pyhelpers.dir.cd`:
            https://pyhelpers.readthedocs.io/en/latest/_generated/pyhelpers.dir.cd.html
        """

        path = cd(self.data_dir, *sub_dir, mkdir=True, **kwargs)

        return path

    def collect_habds_and_wilds(self, confirmation_required=True, verbose=False):
        """
        Collect codes of `HABDs and WILDs <http://www.railwaycodes.org.uk/misc/habdwild.shtm>`_
        from source web page.

            - HABDs - Hot axle box detectors
            - WILDs - Wheel impact load detectors

        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of HABDs and WILDs, and date of when the data was last updated
        :rtype: dict or None

        **Examples**::

            >>> from pyrcs.other_assets import Features  # from pyrcs import Features

            >>> feats = Features()

            >>> hw_codes = feats.collect_habds_and_wilds()
            To collect data of HABD and WILD
            ? [No]|Yes: yes
            >>> type(hw_codes)
            dict
            >>> list(hw_codes.keys())
            ['HABD and WILD', 'Last updated date']

            >>> feats.KEY_TO_HABD_WILD
            'HABD and WILD'

            >>> hw_codes_dat = hw_codes[feats.KEY_TO_HABD_WILD]
            >>> type(hw_codes_dat)
            dict
            >>> list(hw_codes_dat.keys())
            ['HABD', 'WILD']

            >>> habd_dat = hw_codes_dat['HABD']
            >>> type(habd_dat)
            pandas.core.frame.DataFrame
            >>> habd_dat.head()
                ELR  ...                                              Notes
            0  BAG2  ...
            1  BAG2  ...  installed 29 September 1997, later moved to 74...
            2  BAG2  ...                             previously at 74m 51ch
            3  BAG2  ...                          removed 29 September 1997
            4  BAG2  ...           present in 1969, later moved to 89m 00ch

            [5 rows x 5 columns]

            >>> wild_dat = hw_codes_dat['WILD']
            >>> type(wild_dat)
            pandas.core.frame.DataFrame
            >>> wild_dat.head()
                ELR  ...                                              Notes
            0  AYR3  ...
            1  BAG2  ...
            2  BML1  ...
            3  BML1  ...
            4  CGJ3  ...  moved to 183m 68ch from 8 September 2018 / mov...

            [5 rows x 5 columns]
        """

        if confirmed(confirm_msg(self.KEY_TO_HABD_WILD), confirmation_required=confirmation_required):

            print_collect_msg(
                self.KEY_TO_HABD_WILD, verbose=verbose, confirmation_required=confirmation_required)

            habds_and_wilds_codes = {self.KEY_TO_HABD_WILD: None, self.KEY_TO_LAST_UPDATED_DATE: None}

            try:
                url = self.catalogue[self.KEY_TO_HABD_WILD]
                # url = feats.catalogue[feats.KEY_TO_HABD_WILD]
                source = requests.get(url=url, headers=fake_requests_headers())

            except Exception as e:
                if verbose == 2:
                    print("Failed. ", end="")
                print_conn_err(verbose=verbose, e=e)

            else:
                try:
                    sub_keys = self.KEY_TO_HABD_WILD.split(' and ')
                except ValueError:
                    sub_keys = [self.KEY_TO_HABD_WILD + ' 1', self.KEY_TO_HABD_WILD + ' 2']

                try:
                    soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

                    codes_list = []
                    for h3 in soup.find_all('h3'):
                        ths = [th.text.strip() for th in h3.find_next('thead').find_all('th')]
                        trs = h3.find_next('tbody').find_all('tr')

                        dat = parse_tr(trs=trs, ths=ths, as_dataframe=True)

                        codes_list.append(dat)

                    habds_and_wilds_codes_dat = dict(zip(sub_keys, codes_list))

                    last_updated_date = get_last_updated_date(url)

                    habds_and_wilds_codes = {
                        self.KEY_TO_HABD_WILD: habds_and_wilds_codes_dat,
                        self.KEY_TO_LAST_UPDATED_DATE: last_updated_date,
                    }

                    if verbose == 2:
                        print("Done.")

                    save_data_to_file(
                        self, data=habds_and_wilds_codes, data_name=self.KEY_TO_HABD_WILD, ext=".pickle",
                        verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(e))

            return habds_and_wilds_codes

    def fetch_habds_and_wilds(self, update=False, dump_dir=None, verbose=False):
        """
        Fetch codes of `HABDs and WILDs`_.

        .. _`HABDs and WILDs`: http://www.railwaycodes.org.uk/misc/habdwild.shtm

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param dump_dir: name of a folder where the pickle file is to be saved, defaults to ``None``
        :type dump_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of hot axle box detectors (HABDs) and wheel impact load detectors (WILDs),
            and date of when the data was last updated
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Features  # from pyrcs import Features

            >>> feats = Features()

            >>> hw_codes = feats.fetch_habds_and_wilds()

            >>> type(hw_codes)
            dict
            >>> list(hw_codes.keys())
            ['HABD and WILD', 'Last updated date']

            >>> feats.KEY_TO_HABD_WILD
            'HABD and WILD'

            >>> hw_codes_dat = hw_codes[feats.KEY_TO_HABD_WILD]
            >>> type(hw_codes_dat)
            dict
            >>> list(hw_codes_dat.keys())
            ['HABD', 'WILD']

            >>> habd_dat = hw_codes_dat['HABD']
            >>> type(habd_dat)
            pandas.core.frame.DataFrame
            >>> habd_dat.head()
                ELR  ...                                              Notes
            0  BAG2  ...
            1  BAG2  ...  installed 29 September 1997, later moved to 74...
            2  BAG2  ...                             previously at 74m 51ch
            3  BAG2  ...                          removed 29 September 1997
            4  BAG2  ...           present in 1969, later moved to 89m 00ch

            [5 rows x 5 columns]

            >>> wild_dat = hw_codes_dat['WILD']
            >>> type(wild_dat)
            pandas.core.frame.DataFrame
            >>> wild_dat.head()
                ELR  ...                                              Notes
            0  AYR3  ...
            1  BAG2  ...
            2  BML1  ...
            3  BML1  ...
            4  CGJ3  ...  moved to 183m 68ch from 8 September 2018 / mov...

            [5 rows x 5 columns]
        """

        habds_and_wilds_codes = fetch_data_from_file(
            cls=self, method='collect_habds_and_wilds', data_name=self.KEY_TO_HABD_WILD, ext=".pickle",
            update=update, dump_dir=dump_dir, verbose=verbose)

        return habds_and_wilds_codes

    def collect_water_troughs(self, confirmation_required=True, verbose=False):
        """
        Collect codes of `water troughs locations <http://www.railwaycodes.org.uk/misc/troughs.shtm>`_
        from source web page.

        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of water trough locations, and date of when the data was last updated
        :rtype: dict or None

        **Examples**::

            >>> from pyrcs.other_assets import Features  # from pyrcs import Features

            >>> feats = Features()

            >>> wt_codes = feats.collect_water_troughs()
            To collect data of Water troughs
            ? [No]|Yes: yes
            >>> type(wt_codes)
            dict
            >>> list(wt_codes.keys())
            ['Water troughs', 'Last updated date']

            >>> feats.KEY_TO_TROUGH
            'Water troughs'

            >>> wt_codes_dat = wt_codes[feats.KEY_TO_TROUGH]
            >>> type(wt_codes_dat)
            pandas.core.frame.DataFrame
            >>> wt_codes_dat.head()
                ELR  ... Length (Yard)
            0   BEI  ...           NaN
            1   BHL  ...    620.000000
            2  CGJ2  ...      0.666667
            3  CGJ6  ...    561.000000
            4  CGJ6  ...    560.000000

            [5 rows x 6 columns]
        """

        if confirmed(confirm_msg(self.KEY_TO_TROUGH), confirmation_required=confirmation_required):

            print_collect_msg(
                self.KEY_TO_TROUGH, verbose=verbose, confirmation_required=confirmation_required)

            water_troughs_codes = {self.KEY_TO_TROUGH: None, self.KEY_TO_LAST_UPDATED_DATE: None}

            try:
                url = self.catalogue[self.KEY_TO_TROUGH]
                # url = feats.catalogue[feats.KEY_TO_TROUGH]
                source = requests.get(url=url, headers=fake_requests_headers())

            except Exception as e:
                if verbose == 2:
                    print("Failed. ", end="")
                print_conn_err(verbose=verbose, e=e)

            else:
                try:
                    soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

                    ths = [th.text.strip() for th in soup.find('thead').find_all('th')]
                    trs = soup.find('tbody').find_all('tr')

                    dat = parse_tr(trs=trs, ths=ths, as_dataframe=True)

                    if 'Length' in dat.columns:
                        dat['Length (Yard)'] = dat.Length.map(_parse_vulgar_fraction_in_length)

                    last_updated_date = get_last_updated_date(url)

                    water_troughs_codes = {
                        self.KEY_TO_TROUGH: dat,
                        self.KEY_TO_LAST_UPDATED_DATE: last_updated_date,
                    }

                    if verbose == 2:
                        print("Done.")

                    save_data_to_file(
                        self, data=water_troughs_codes, data_name=self.KEY_TO_TROUGH, ext=".pickle",
                        verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(e))

            return water_troughs_codes

    def fetch_water_troughs(self, update=False, dump_dir=None, verbose=False):
        """
        Fetch codes of `water troughs locations`_.

        .. _`water troughs locations`: http://www.railwaycodes.org.uk/misc/troughs.shtm

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param dump_dir: name of a folder where the pickle file is to be saved, defaults to ``None``
        :type dump_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of water trough locations, and date of when the data was last updated
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Features  # from pyrcs import Features

            >>> feats = Features()

            >>> # wt_codes = feats.fetch_water_troughs(update=True, verbose=True)
            >>> wt_codes = feats.fetch_water_troughs()

            >>> type(wt_codes)
            dict
            >>> list(wt_codes.keys())
            ['Water troughs', 'Last updated date']

            >>> feats.KEY_TO_TROUGH
            'Water troughs'

            >>> wt_codes_dat = wt_codes[feats.KEY_TO_TROUGH]
            >>> type(wt_codes_dat)
            pandas.core.frame.DataFrame
            >>> wt_codes_dat.head()
                ELR  ... Length (Yard)
            0   BEI  ...           NaN
            1   BHL  ...    620.000000
            2  CGJ2  ...      0.666667
            3  CGJ6  ...    561.000000
            4  CGJ6  ...    560.000000

            [5 rows x 6 columns]
        """

        troughs_locations_codes = fetch_data_from_file(
            cls=self, method='collect_water_troughs', data_name=self.KEY_TO_TROUGH, ext=".pickle",
            update=update, dump_dir=dump_dir, verbose=verbose)

        return troughs_locations_codes

    def collect_telegraph_codes(self, confirmation_required=True, verbose=False):
        """
        Collect data of `telegraph code words <http://www.railwaycodes.org.uk/misc/telegraph.shtm>`_
        from source web page.

        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of telegraph code words, and date of when the data was last updated
        :rtype: dict or None

        **Examples**::

            >>> from pyrcs.other_assets import Features  # from pyrcs import Features

            >>> feats = Features()

            >>> tel_codes = feats.collect_telegraph_codes()
            To collect data of Telegraphic codes
            ? [No]|Yes: yes
            >>> type(tel_codes)
            dict
            >>> list(tel_codes.keys())
            ['Telegraphic codes', 'Last updated date']

            >>> feats.KEY_TO_TELEGRAPH
            'Telegraphic codes'

            >>> tel_codes_dat = tel_codes[feats.KEY_TO_TELEGRAPH]
            >>> type(tel_codes_dat)
            dict
            >>> list(tel_codes_dat.keys())
            ['Official codes', 'Unofficial codes']

            >>> tel_official_codes = tel_codes_dat['Official codes']
            >>> type(tel_official_codes)
            pandas.core.frame.DataFrame
            >>> tel_official_codes.head()
                  Code  ...                               In use
            0    ABACK  ...     cross industry term used in 1939
            1    ABASE  ...                            GWR, 1939
            2  ABREAST  ...  GWR, 1939 / Railway Executive, 1950
            3  ABREAST  ...   British Transport Commission, 1958
            4   ABSENT  ...                            GWR, 1939

            [5 rows x 3 columns]

            >>> tel_unofficial_codes = tel_codes_dat['Unofficial codes']
            >>> type(tel_unofficial_codes)
            pandas.core.frame.DataFrame
            >>> tel_unofficial_codes.head()
                  Code                             Unofficial description
            0  CRANKEX                                      [See KRANKEX]
            1  DRUNKEX  Saturday night special train (usually a DMU) t...
            2     GYFO    Strongly urge all speed ('Get your finger out')
            3  KRANKEX  Special train with interesting routing or trac...
            4   MYSTEX  Special excursion going somewhere no one reall...
        """

        if confirmed(confirm_msg(self.KEY_TO_TELEGRAPH), confirmation_required=confirmation_required):

            print_collect_msg(
                self.KEY_TO_TELEGRAPH, verbose=verbose, confirmation_required=confirmation_required)

            telegraph_code_words = {self.KEY_TO_TELEGRAPH: None, self.KEY_TO_LAST_UPDATED_DATE: None}

            try:
                url = self.catalogue[self.KEY_TO_TELEGRAPH]
                # url = feats.catalogue[feats.KEY_TO_TELEGRAPH]
                source = requests.get(url=url, headers=fake_requests_headers())

            except Exception as e:
                if verbose == 2:
                    print("Failed. ", end="")
                print_conn_err(verbose=verbose, e=e)

            else:
                try:
                    soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

                    h3s = soup.find_all('h3')

                    sub_keys, codes_list = [], []
                    for h3 in h3s:
                        sub_keys.append(h3.text.strip())

                        ths = [th.text.strip() for th in h3.find_next('thead').find_all('th')]
                        trs = h3.find_next('tbody').find_all('tr')

                        dat = parse_tr(trs=trs, ths=ths, as_dataframe=True)

                        if 'In use' in dat.columns:
                            dat['In use'] = dat['In use'].map(_parse_telegraph_in_use_term)

                        codes_list.append(dat)

                    telegraph_code_words_dat = dict(zip(sub_keys, codes_list))

                    last_updated_date = get_last_updated_date(url)

                    telegraph_code_words = {
                        self.KEY_TO_TELEGRAPH: telegraph_code_words_dat,
                        self.KEY_TO_LAST_UPDATED_DATE: last_updated_date,
                    }

                    if verbose == 2:
                        print("Done.")

                    save_data_to_file(
                        self, data=telegraph_code_words, data_name=self.KEY_TO_TELEGRAPH, ext=".pickle",
                        verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(e))

            return telegraph_code_words

    def fetch_telegraph_codes(self, update=False, dump_dir=None, verbose=False):
        """
        Fetch data of `telegraph code words`_.

        .. _`telegraph code words`: http://www.railwaycodes.org.uk/misc/telegraph.shtm

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param dump_dir: name of a folder where the pickle file is to be saved, defaults to ``None``
        :type dump_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of telegraph code words, and date of when the data was last updated
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Features  # from pyrcs import Features

            >>> feats = Features()

            >>> tel_codes = feats.fetch_telegraph_codes()
            >>> type(tel_codes)
            dict
            >>> list(tel_codes.keys())
            ['Telegraphic codes', 'Last updated date']

            >>> feats.KEY_TO_TELEGRAPH
            'Telegraphic codes'

            >>> tel_codes_dat = tel_codes[feats.KEY_TO_TELEGRAPH]
            >>> type(tel_codes_dat)
            dict
            >>> list(tel_codes_dat.keys())
            ['Official codes', 'Unofficial codes']

            >>> tel_official_codes = tel_codes_dat['Official codes']
            >>> type(tel_official_codes)
            pandas.core.frame.DataFrame
            >>> tel_official_codes.head()
                  Code  ...                               In use
            0    ABACK  ...     cross industry term used in 1939
            1    ABASE  ...                            GWR, 1939
            2  ABREAST  ...  GWR, 1939 / Railway Executive, 1950
            3  ABREAST  ...   British Transport Commission, 1958
            4   ABSENT  ...                            GWR, 1939

            [5 rows x 3 columns]

            >>> tel_unofficial_codes = tel_codes_dat['Unofficial codes']
            >>> type(tel_unofficial_codes)
            pandas.core.frame.DataFrame
            >>> tel_unofficial_codes.head()
                  Code                             Unofficial description
            0  CRANKEX                                      [See KRANKEX]
            1  DRUNKEX  Saturday night special train (usually a DMU) t...
            2     GYFO    Strongly urge all speed ('Get your finger out')
            3  KRANKEX  Special train with interesting routing or trac...
            4   MYSTEX  Special excursion going somewhere no one reall...
        """

        telegraph_code_words = fetch_data_from_file(
            cls=self, method='collect_telegraph_codes', data_name=self.KEY_TO_TELEGRAPH, ext=".pickle",
            update=update, dump_dir=dump_dir, verbose=verbose)

        return telegraph_code_words

    def collect_buzzer_codes(self, confirmation_required=True, verbose=False):
        """
        Collect data of `buzzer codes <http://www.railwaycodes.org.uk/misc/buzzer.shtm>`_
        from source web page.

        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of buzzer codes, and date of when the data was last updated
        :rtype: dict or None

        **Examples**::

            >>> from pyrcs.other_assets import Features  # from pyrcs import Features

            >>> feats = Features()

            >>> buz_codes = feats.collect_buzzer_codes()
            To collect data of Buzzer codes
            ? [No]|Yes: yes
            >>> type(buz_codes)
            dict
            >>> list(buz_codes.keys())
            ['Buzzer codes', 'Last updated date']

            >>> feats.KEY_TO_BUZZER
            'Buzzer codes'

            >>> buz_codes_dat = buz_codes[feats.KEY_TO_BUZZER]
            >>> type(buz_codes_dat)
            pandas.core.frame.DataFrame
            >>> buz_codes_dat.head()
              Code [number of buzzes or groups separated by pauses]            Meaning
            0                                                  1                  Stop
            1                                                1-2           Close doors
            2                                                  2        Ready to start
            3                                                2-2     Do not open doors
            4                                                  3              Set back
        """

        if confirmed(confirm_msg(self.KEY_TO_BUZZER), confirmation_required=confirmation_required):

            print_collect_msg(
                self.KEY_TO_BUZZER, verbose=verbose, confirmation_required=confirmation_required)

            buzzer_codes = {self.KEY_TO_BUZZER: None, self.KEY_TO_LAST_UPDATED_DATE: None}

            try:
                url = self.catalogue[self.KEY_TO_BUZZER]
                # url = feats.catalogue[feats.KEY_TO_BUZZER]
                source = requests.get(url=url, headers=fake_requests_headers())

            except Exception as e:
                if verbose == 2:
                    print("Failed. ", end="")
                print_conn_err(verbose=verbose, e=e)

            else:
                try:
                    codes_dat = parse_table(source=source, parser='html.parser', as_dataframe=True)

                    column_names = []
                    for col in codes_dat.columns:
                        col_name = col.split('\r\n')
                        if len(col_name) > 1:
                            column_names.append(col_name[0] + ' [' + ''.join(col_name[1:]) + ']')
                        else:
                            column_names.append(col_name[0])

                    codes_dat.columns = column_names

                    last_updated_date = get_last_updated_date(url)

                    buzzer_codes = {
                        self.KEY_TO_BUZZER: codes_dat,
                        self.KEY_TO_LAST_UPDATED_DATE: last_updated_date,
                    }

                    if verbose == 2:
                        print("Done.")

                    save_data_to_file(
                        self, data=buzzer_codes, data_name=self.KEY_TO_BUZZER, ext=".pickle",
                        verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(e))

            return buzzer_codes

    def fetch_buzzer_codes(self, update=False, dump_dir=None, verbose=False):
        """
        Fetch data of `buzzer codes`_.

        .. _`buzzer codes`: http://www.railwaycodes.org.uk/misc/buzzer.shtm

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param dump_dir: name of a folder where the pickle file is to be saved, defaults to ``None``
        :type dump_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of buzzer codes, and date of when the data was last updated
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Features  # from pyrcs import Features

            >>> feats = Features()

            >>> buz_codes = feats.fetch_buzzer_codes()
            >>> type(buz_codes)
            dict
            >>> list(buz_codes.keys())
            ['Buzzer codes', 'Last updated date']

            >>> feats.KEY_TO_BUZZER
            'Buzzer codes'

            >>> buz_codes_dat = buz_codes[feats.KEY_TO_BUZZER]
            >>> type(buz_codes_dat)
            pandas.core.frame.DataFrame
            >>> buz_codes_dat.head()
              Code [number of buzzes or groups separated by pauses]            Meaning
            0                                                  1                  Stop
            1                                                1-2           Close doors
            2                                                  2        Ready to start
            3                                                2-2     Do not open doors
            4                                                  3              Set back
        """

        buzzer_codes = fetch_data_from_file(
            cls=self, method='collect_buzzer_codes', data_name=self.KEY_TO_BUZZER, ext=".pickle",
            update=update, dump_dir=dump_dir, verbose=verbose)

        return buzzer_codes

    def fetch_codes(self, update=False, dump_dir=None, verbose=False):
        """
        Fetch codes of infrastructure features.

        Including:

            - `HABD and WILD <http://www.railwaycodes.org.uk/misc/habdwild.shtm>`_
            - `Water troughs <http://www.railwaycodes.org.uk/misc/troughs.shtm>`_
            - `Telegraph codes <http://www.railwaycodes.org.uk/misc/telegraph.shtm>`_
            - `Driver/guard buzzer codes <http://www.railwaycodes.org.uk/misc/buzzer.shtm>`_

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param dump_dir: name of a folder where the pickle file is to be saved, defaults to ``None``
        :type dump_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of features codes and date of when the data was last updated
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Features  # from pyrcs import Features

            >>> feats = Features()

            >>> feats_codes = feats.fetch_codes()
            >>> type(feats_codes)
            dict
            >>> list(feats_codes.keys())
            ['Features', 'Last updated date']

            >>> feats.KEY
            'Features'

            >>> feats_codes_dat = feats_codes[feats.KEY]
            >>> type(feats_codes_dat)
            dict
            >>> list(feats_codes_dat.keys())
            ['Buzzer codes', 'HABD and WILD', 'Telegraphic codes', 'Water troughs']

            >>> water_troughs_locations = feats_codes_dat[feats.KEY_TO_TROUGH]
            >>> type(water_troughs_locations)
            pandas.core.frame.DataFrame
            >>> water_troughs_locations.head()
                ELR  ... Length (Yard)
            0   BEI  ...           NaN
            1   BHL  ...    620.000000
            2  CGJ2  ...      0.666667
            3  CGJ6  ...    561.000000
            4  CGJ6  ...    560.000000

            [5 rows x 6 columns]
        """

        verbose_ = False if (dump_dir or not verbose) else (2 if verbose == 2 else True)

        features_codes_dat = []

        for func in dir(self):
            if func.startswith('fetch_') and func != 'fetch_codes':
                dat = getattr(self, func)(
                    update=update, verbose=verbose_ if is_home_connectable() else False)
                features_codes_dat.append(dat)

        features_codes = {
            self.KEY:
                {next(iter(x)): next(iter(x.values())) for x in features_codes_dat},
            self.KEY_TO_LAST_UPDATED_DATE:
                max(next(itertools.islice(iter(x.values()), 1, 2)) for x in features_codes_dat),
        }

        if dump_dir is not None:
            save_data_to_file(
                self, data=features_codes, data_name=self.KEY, ext=".pickle", dump_dir=dump_dir,
                verbose=verbose)

        return features_codes
