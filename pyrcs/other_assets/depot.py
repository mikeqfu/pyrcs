"""Collect data of `depot codes <http://www.railwaycodes.org.uk/depots/depots0.shtm>`_."""

import re
import urllib.parse

import bs4
import pandas as pd
import requests
from pyhelpers.dirs import cd
from pyhelpers.ops import confirmed, fake_requests_headers

from ..parser import get_catalogue, get_last_updated_date, parse_tr
from ..utils import confirm_msg, fetch_data_from_file, format_err_msg, home_page_url, init_data_dir, \
    is_home_connectable, print_collect_msg, print_conn_err, print_inst_conn_err, save_data_to_file


class Depots:
    """
    A class for collecting data of `depot codes`_.

    .. _`depot codes`: http://www.railwaycodes.org.uk/depots/depots0.shtm
    """

    #: Name of the data
    NAME = 'Depot codes'
    #: Key of the `dict <https://docs.python.org/3/library/stdtypes.html#dict>`_-type data
    KEY = 'Depots'

    #: Key of the dict-type data of two character TOPS codes
    KEY_TO_TOPS = 'Two character TOPS codes'
    #: Key of the dict-type data of four digit pre-TOPS codes
    KEY_TO_PRE_TOPS = 'Four digit pre-TOPS codes'
    #: Key of the dict-type data of 1950 system (pre-TOPS) codes
    KEY_TO_1950_SYSTEM = '1950 system (pre-TOPS) codes'
    #: Key of the dict-type data of GWR codes
    KEY_TO_GWR = 'GWR codes'

    #: URL of the main web page of the data
    URL = urllib.parse.urljoin(home_page_url(), '/depots/depots0.shtm')

    #: Key of the data of the last updated date
    KEY_TO_LAST_UPDATED_DATE = 'Last updated date'

    def __init__(self, data_dir=None, update=False, verbose=True):
        """
        :param data_dir: name of data directory, defaults to ``None``
        :type data_dir: str or None
        :param update: whether to do an update check (for the catagloue data), defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console, defaults to ``True``
        :type verbose: bool or int

        :ivar dict catalogue: catalogue of the data
        :ivar str last_updated_date: last updated date
        :ivar str data_dir: path to the data directory
        :ivar str current_data_dir: path to the current data directory

        **Examples**::

            >>> from pyrcs.other_assets import Depots  # from pyrcs import Depots

            >>> depots = Depots()

            >>> depots.NAME
            'Depot codes'

            >>> depots.URL
            'http://www.railwaycodes.org.uk/depots/depots0.shtm'
        """

        print_conn_err(verbose=verbose)

        self.catalogue = get_catalogue(url=self.URL, update=update, confirmation_required=False)

        self.last_updated_date = get_last_updated_date(url=self.URL, parsed=True, as_date_type=False)

        self.data_dir, self.current_data_dir = init_data_dir(self, data_dir, category="other-assets")

    def _cdd(self, *sub_dir, **kwargs):
        """
        Change directory to package data directory and subdirectories (and/or a file).

        The directory for this module: ``"data\\other-assets\\depots"``.

        :param sub_dir: subdirectory or subdirectories (and/or a file)
        :type sub_dir: str
        :param kwargs: [optional] parameters of the function `pyhelpers.dir.cd`_
        :return: path to the backup data directory for the class
            :py:class:`~pyrcs.other_assets.depot.Depots`
        :rtype: str

        .. _`pyhelpers.dir.cd`:
            https://pyhelpers.readthedocs.io/en/latest/_generated/pyhelpers.dir.cd.html
        """

        path = cd(self.data_dir, *sub_dir, mkdir=True, **kwargs)

        return path

    def collect_tops_codes(self, confirmation_required=True, verbose=False):
        """
        Collect `two-character TOPS codes <http://www.railwaycodes.org.uk/depots/depots1.shtm>`_
        from source web page.

        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of two-character TOPS codes and date of when the data was last updated
        :rtype: dict or None

        **Examples**::

            >>> from pyrcs.other_assets import Depots  # from pyrcs import Depots

            >>> depots = Depots()

            >>> tct_codes = depots.collect_tops_codes()
            To collect data of two character TOPS codes
            ? [No]|Yes: yes
            >>> type(tct_codes)
            dict
            >>> list(tct_codes.keys())
            ['Two character TOPS codes', 'Last updated date']

            >>> depots.KEY_TO_TOPS
            'Two character TOPS codes'

            >>> tct_codes_dat = tct_codes[depots.KEY_TO_TOPS]
            >>> type(tct_codes_dat)
            pandas.core.frame.DataFrame
            >>> tct_codes_dat.head()
              Code  ...                Notes
            0   AB  ...          Closed 1987
            1   AB  ...
            2   AC  ...  Became WH from 1994
            3   AC  ...
            4   AD  ...
            [5 rows x 5 columns]
        """

        cfm_msg = confirm_msg(self.KEY_TO_TOPS)

        if confirmed(cfm_msg, confirmation_required=confirmation_required):

            print_collect_msg(
                self.KEY_TO_TOPS, verbose=verbose, confirmation_required=confirmation_required)

            two_char_tops_codes_data = None

            try:
                url = self.catalogue[self.KEY_TO_TOPS]
                source = requests.get(url=url, headers=fake_requests_headers())

            except Exception as e:
                if verbose == 2:
                    print("Failed. ", end="")
                print_inst_conn_err(verbose=verbose, e=e)

            else:
                try:
                    soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

                    thead, tbody = soup.find('thead'), soup.find('tbody')
                    ths = [th.text for th in thead.find_all(name='th')]
                    trs = tbody.find_all(name='tr')
                    two_char_tops_codes = parse_tr(trs=trs, ths=ths, as_dataframe=True)

                    if verbose == 2:
                        print("Done.")

                    two_char_tops_codes_data = {
                        self.KEY_TO_TOPS: two_char_tops_codes,
                        self.KEY_TO_LAST_UPDATED_DATE: get_last_updated_date(url)
                    }

                    save_data_to_file(
                        self, data=two_char_tops_codes_data, data_name=self.KEY_TO_TOPS, ext=".pickle",
                        verbose=verbose)

                except Exception as e:
                    print(f"Failed. {format_err_msg(e)}")

            return two_char_tops_codes_data

    def fetch_tops_codes(self, update=False, dump_dir=None, verbose=False):
        """
        Fetch data of `two-character TOPS codes`_.

        .. _`two-character TOPS codes`: http://www.railwaycodes.org.uk/depots/depots1.shtm

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param dump_dir: pathname of a directory where the data file is dumped, defaults to ``None``
        :type dump_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of two-character TOPS codes and date of when the data was last updated
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Depots  # from pyrcs import Depots

            >>> depots = Depots()

            >>> tct_codes = depots.fetch_tops_codes()
            >>> type(tct_codes)
            dict
            >>> list(tct_codes.keys())
            ['Two character TOPS codes', 'Last updated date']

            >>> depots.KEY_TO_TOPS
            'Two character TOPS codes'

            >>> tct_codes_dat = tct_codes[depots.KEY_TO_TOPS]
            >>> type(tct_codes_dat)
            pandas.core.frame.DataFrame
            >>> tct_codes_dat.head()
              Code  ...                Notes
            0   AB  ...          Closed 1987
            1   AB  ...
            2   AC  ...  Became WH from 1994
            3   AC  ...
            4   AD  ...
            [5 rows x 5 columns]
        """

        two_char_tops_codes_data = fetch_data_from_file(
            cls=self, method='collect_tops_codes', data_name=self.KEY_TO_TOPS, ext=".pickle",
            update=update, dump_dir=dump_dir, verbose=verbose)

        return two_char_tops_codes_data

    def collect_pre_tops_codes(self, confirmation_required=True, verbose=False):
        """
        Collect `four-digit pre-TOPS codes <http://www.railwaycodes.org.uk/depots/depots2.shtm>`_
        from source web page.

        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of four-digit pre-TOPS codes and date of when the data was last updated
        :rtype: dict or None

        **Examples**::

            >>> from pyrcs.other_assets import Depots  # from pyrcs import Depots

            >>> depots = Depots()

            >>> fdpt_codes = depots.collect_pre_tops_codes()
            To collect data of four digit pre-TOPS codes
            ? [No]|Yes: yes
            >>> type(fdpt_codes)
            dict
            >>> list(fdpt_codes.keys())
            ['Four digit pre-TOPS codes', 'Last updated date']

            >>> depots.KEY_TO_PRE_TOPS
            'Four digit pre-TOPS codes'

            >>> fdpt_codes_dat = fdpt_codes[depots.KEY_TO_PRE_TOPS]
            >>> type(fdpt_codes_dat)
            pandas.core.frame.DataFrame
            >>> fdpt_codes_dat.head()
               Code             Depot name          Region  Main Works site
            0  2000             Accrington  London Midland            False
            1  2001   Derby Litchurch Lane  London Midland             True
            2  2003              Blackburn  London Midland            False
            3  2004  Bolton Trinity Street  London Midland            False
            4  2006                Burnley  London Midland            False
        """

        data_name = self.KEY_TO_PRE_TOPS[:1].lower() + self.KEY_TO_PRE_TOPS[1:]
        cfm_msg = confirm_msg(data_name)
        if confirmed(cfm_msg, confirmation_required=confirmation_required):

            print_collect_msg(data_name, verbose=verbose, confirmation_required=confirmation_required)

            four_digit_pre_tops_codes_data = None

            try:
                url = self.catalogue[self.KEY_TO_PRE_TOPS]
                # headers_, four_digit_pre_tops_codes = pd.read_html(url)
                source = requests.get(url=url, headers=fake_requests_headers())

            except Exception as e:
                if verbose == 2:
                    print("Failed. ", end="")
                print_inst_conn_err(verbose=verbose, e=e)

            else:
                try:
                    soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

                    thead, tbody = soup.find('thead'), soup.find('tbody')

                    ths = [th.text for th in thead.find_all(name='th')]
                    trs = tbody.find_all(name='tr')
                    codes = parse_tr(trs=trs, ths=ths, as_dataframe=True)
                    codes.Code = codes['Code'].map(int)

                    dagger_mark, depot_name_column, region_column = ' †', 'Depot name', 'Region'

                    def _identify_region(x):
                        if 2000 <= x < 3000:
                            _region_name = 'London Midland'
                        elif 3000 <= x < 4000:
                            _region_name = 'Western'
                        elif 4000 <= x < 5000:
                            _region_name = 'Southern'
                        elif 5000 <= x < 7000:
                            _region_name = 'Eastern'
                        else:  # x >= 7000:
                            _region_name = 'Scottish'
                        return _region_name

                    codes[region_column] = codes.Code.map(_identify_region)

                    codes['Main Works site'] = codes[depot_name_column].map(
                        lambda x: True if x.endswith(dagger_mark) else False)

                    codes[depot_name_column] = codes[depot_name_column].str.rstrip(dagger_mark)

                    last_updated_date = get_last_updated_date(url)

                    four_digit_pre_tops_codes_data = {
                        self.KEY_TO_PRE_TOPS: codes,
                        self.KEY_TO_LAST_UPDATED_DATE: last_updated_date
                    }

                    if verbose == 2:
                        print("Done.")

                    save_data_to_file(
                        self, data=four_digit_pre_tops_codes_data, data_name=data_name, ext=".pickle",
                        verbose=verbose)

                except Exception as e:
                    print(f"Failed. {format_err_msg(e)}")

            return four_digit_pre_tops_codes_data

    def fetch_pre_tops_codes(self, update=False, dump_dir=None, verbose=False):
        """
        Fetch data of `four-digit pre-TOPS codes`_.

        .. _`four-digit pre-TOPS codes`: http://www.railwaycodes.org.uk/depots/depots2.shtm

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param dump_dir: pathname of a directory where the data file is dumped, defaults to ``None``
        :type dump_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of four-digit pre-TOPS codes and date of when the data was last updated
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Depots  # from pyrcs import Depots

            >>> depots = Depots()

            >>> fdpt_codes = depots.fetch_pre_tops_codes()
            >>> type(fdpt_codes)
            dict
            >>> list(fdpt_codes.keys())
            ['Four digit pre-TOPS codes', 'Last updated date']

            >>> depots.KEY_TO_PRE_TOPS
            'Four digit pre-TOPS codes'

            >>> fdpt_codes_dat = fdpt_codes[depots.KEY_TO_PRE_TOPS]
            >>> type(fdpt_codes_dat)
            pandas.core.frame.DataFrame
            >>> fdpt_codes_dat.head()
               Code             Depot name          Region  Main Works site
            0  2000             Accrington  London Midland            False
            1  2001   Derby Litchurch Lane  London Midland             True
            2  2003              Blackburn  London Midland            False
            3  2004  Bolton Trinity Street  London Midland            False
            4  2006                Burnley  London Midland            False
        """

        data_name = re.sub(r'[ -]', '-', self.KEY_TO_PRE_TOPS)

        four_digit_pre_tops_codes_data = fetch_data_from_file(
            cls=self, method='collect_pre_tops_codes', data_name=data_name, ext=".pickle",
            update=update, dump_dir=dump_dir, verbose=verbose)

        return four_digit_pre_tops_codes_data

    def collect_1950_system_codes(self, confirmation_required=True, verbose=False):
        """
        Collect `1950 system (pre-TOPS) codes <http://www.railwaycodes.org.uk/depots/depots3.shtm>`_
        from source web page.

        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of 1950 system (pre-TOPS) codes and date of when the data was last updated
        :rtype: dict or None

        **Examples**::

            >>> from pyrcs.other_assets import Depots  # from pyrcs import Depots

            >>> depots = Depots()

            >>> s1950_codes = depots.collect_1950_system_codes()
            To collect data of 1950 system (pre-TOPS) codes
            ? [No]|Yes: yes
            >>> type(s1950_codes)
            dict
            >>> list(s1950_codes.keys())
            ['1950 system (pre-TOPS) codes', 'Last updated date']

            >>> depots.KEY_TO_1950_SYSTEM
            '1950 system (pre-TOPS) codes'

            >>> s1950_codes_dat = s1950_codes[depots.KEY_TO_1950_SYSTEM]

            >>> type(s1950_codes_dat)
            pandas.core.frame.DataFrame
            >>> s1950_codes_dat.head()
              Code        Depot name                                              Notes
            0   1A         Willesden              From 1950.  Became WN from 6 May 1973
            1   1B            Camden                      From 1950.  To 3 January 1966
            2   1C           Watford              From 1950.  Became WJ from 6 May 1973
            3   1D  Devons Road, Bow  Previously 13B to 9 June 1950.  Became 1J from...
            4   1D        Marylebone  Previously 14F to 31 August 1963.  Became ME f...
        """

        if confirmed(confirm_msg(self.KEY_TO_1950_SYSTEM), confirmation_required=confirmation_required):

            print_collect_msg(
                self.KEY_TO_1950_SYSTEM, verbose=verbose, confirmation_required=confirmation_required)

            system_1950_codes_data = None

            try:
                url = self.catalogue[self.KEY_TO_1950_SYSTEM]
                source = requests.get(url=url, headers=fake_requests_headers())

            except Exception as e:
                if verbose == 2:
                    print("Failed. ", end="")
                print_inst_conn_err(verbose=verbose, e=e)

            else:
                try:
                    soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')
                    source.close()

                    thead, tbody = soup.find('thead'), soup.find('tbody')

                    ths = [th.text for th in thead.find_all(name='th')]
                    trs = tbody.find_all(name='tr')
                    system_1950_codes = parse_tr(trs=trs, ths=ths, as_dataframe=True)

                    last_updated_date = get_last_updated_date(url)

                    system_1950_codes_data = {
                        self.KEY_TO_1950_SYSTEM: system_1950_codes,
                        self.KEY_TO_LAST_UPDATED_DATE: last_updated_date
                    }

                    if verbose == 2:
                        print("Done.")

                    save_data_to_file(
                        self, data=system_1950_codes_data,
                        data_name=re.sub(r' \(|\) | ', '-', self.KEY_TO_1950_SYSTEM), ext=".pickle",
                        verbose=verbose)

                except Exception as e:
                    print(f"Failed. {format_err_msg(e)}")

            return system_1950_codes_data

    def fetch_1950_system_codes(self, update=False, dump_dir=None, verbose=False):
        """
        Fetch data of `1950 system (pre-TOPS) codes`_.

        .. _`1950 system (pre-TOPS) codes`: http://www.railwaycodes.org.uk/depots/depots3.shtm

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param dump_dir: pathname of a directory where the data file is dumped, defaults to ``None``
        :type dump_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of 1950 system (pre-TOPS) codes and date of when the data was last updated
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Depots  # from pyrcs import Depots

            >>> depots = Depots()

            >>> s1950_codes = depots.fetch_1950_system_codes()
            >>> type(s1950_codes)
            dict
            >>> list(s1950_codes.keys())
            ['1950 system (pre-TOPS) codes', 'Last updated date']

            >>> depots.KEY_TO_1950_SYSTEM
            '1950 system (pre-TOPS) codes'

            >>> s1950_codes_dat = s1950_codes[depots.KEY_TO_1950_SYSTEM]
            >>> type(s1950_codes_dat)
            pandas.core.frame.DataFrame
            >>> s1950_codes_dat.head()
              Code        Depot name                                              Notes
            0   1A         Willesden              From 1950.  Became WN from 6 May 1973
            1   1B            Camden                      From 1950.  To 3 January 1966
            2   1C           Watford              From 1950.  Became WJ from 6 May 1973
            3   1D  Devons Road, Bow  Previously 13B to 9 June 1950.  Became 1J from...
            4   1D        Marylebone  Previously 14F to 31 August 1963.  Became ME f...
        """

        system_1950_data = fetch_data_from_file(
            cls=self, method='collect_1950_system_codes',
            data_name=re.sub(r' \(|\) | ', '-', self.KEY_TO_1950_SYSTEM).lower(), ext=".pickle",
            update=update, dump_dir=dump_dir, verbose=verbose)

        return system_1950_data

    def collect_gwr_codes(self, confirmation_required=True, verbose=False):
        """
        Collect `Great Western Railway (GWR) depot codes
        <http://www.railwaycodes.org.uk/depots/depots4.shtm>`_
        from source web page.

        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of GWR depot codes and date of when the data was last updated
        :rtype: dict or None

        **Examples**::

            >>> from pyrcs.other_assets import Depots  # from pyrcs import Depots

            >>> depots = Depots()

            >>> gwr_codes = depots.collect_gwr_codes()
            To collect data of GWR codes
            ? [No]|Yes: yes
            >>> type(gwr_codes)
            dict
            >>> list(gwr_codes.keys())
            ['GWR codes', 'Last updated date']

            >>> depots.KEY_TO_GWR
            'GWR codes'

            >>> gwr_codes_dat = gwr_codes[depots.KEY_TO_GWR]
            >>> type(gwr_codes_dat)
            dict
            >>> list(gwr_codes_dat.keys())
            ['Alphabetical codes', 'Numerical codes']

            >>> gwr_alpha_codes = gwr_codes_dat['Alphabetical codes']
            >>> type(gwr_alpha_codes)
            pandas.core.frame.DataFrame
            >>> gwr_alpha_codes.head()
                Code   Depot name
            0  ABEEG     Aberbeeg
            1    ABG     Aberbeeg
            2    AYN    Abercynon
            3   ABDR     Aberdare
            4    ABH  Aberystwyth
        """

        if confirmed(confirm_msg(self.KEY_TO_GWR), confirmation_required=confirmation_required):

            print_collect_msg(
                data_name=self.KEY_TO_GWR, verbose=verbose, confirmation_required=confirmation_required)

            gwr_depot_codes = None

            try:
                url = self.catalogue[self.KEY_TO_GWR]
                source = requests.get(url=url, headers=fake_requests_headers())

            except Exception as e:
                if verbose == 2:
                    print("Failed. ", end="")
                print_inst_conn_err(verbose=verbose, e=e)

            else:
                try:
                    soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

                    theads, tbodies = soup.find_all(name='thead'), soup.find_all(name='tbody')

                    tables = []
                    for thead, tbody in zip(theads, tbodies):
                        ths = [th.text for th in thead.find_all(name='th')]
                        trs = tbody.find_all(name='tr')

                        if len(ths) == 2:
                            table = parse_tr(trs=trs, ths=ths, as_dataframe=True)
                        else:
                            list_dat = [[td.text for td in tr.find_all('td')] for tr in trs]
                            table = pd.DataFrame(data=list_dat, columns=ths)

                        tables.append(table)

                    alphabetical_codes, numerical_codes = tables

                    span_tags = soup.find_all(name='span', attrs={'class': 'tab2'})
                    num_codes_dict = dict([
                        (int(span_tag.text), span_tag.next_sibling.replace(' = ', '').strip())
                        for span_tag in span_tags])

                    numerical_codes.rename(columns={'sort by division': 'Division'}, inplace=True)
                    numerical_codes.Division = numerical_codes.Code.map(
                        lambda x: num_codes_dict[int(str(x)[-1])])

                    h3_titles = [h3.text for h3 in soup.find_all('h3')]
                    gwr_depot_codes_data = dict(zip(h3_titles, [alphabetical_codes, numerical_codes]))

                    last_updated_date = get_last_updated_date(url)

                    gwr_depot_codes = {
                        self.KEY_TO_GWR: gwr_depot_codes_data,
                        self.KEY_TO_LAST_UPDATED_DATE: last_updated_date,
                    }

                    if verbose == 2:
                        print("Done.")

                    save_data_to_file(
                        self, data=gwr_depot_codes, data_name=self.KEY_TO_GWR, ext=".pickle",
                        verbose=verbose)

                except Exception as e:
                    print(f"Failed. {format_err_msg(e)}")

            return gwr_depot_codes

    def fetch_gwr_codes(self, update=False, dump_dir=None, verbose=False):
        """
        Fetch data of `Great Western Railway (GWR) depot codes`_.

        .. _`Great Western Railway (GWR) depot codes`:
            http://www.railwaycodes.org.uk/depots/depots4.shtm

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param dump_dir: pathname of a directory where the data file is dumped, defaults to ``None``
        :type dump_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of GWR depot codes and date of when the data was last updated
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Depots  # from pyrcs import Depots

            >>> depots = Depots()

            >>> gwr_codes = depots.fetch_gwr_codes()
            >>> type(gwr_codes)
            dict
            >>> list(gwr_codes.keys())
            ['GWR codes', 'Last updated date']

            >>> depots.KEY_TO_GWR
            'GWR codes'

            >>> gwr_codes_dat = gwr_codes[depots.KEY_TO_GWR]
            >>> type(gwr_codes_dat)
            dict
            >>> list(gwr_codes_dat.keys())
            ['Alphabetical codes', 'Numerical codes']

            >>> gwr_alpha_codes = gwr_codes_dat['Alphabetical codes']
            >>> type(gwr_alpha_codes)
            pandas.core.frame.DataFrame
            >>> gwr_alpha_codes.head()
                Code   Depot name
            0  ABEEG     Aberbeeg
            1    ABG     Aberbeeg
            2    AYN    Abercynon
            3   ABDR     Aberdare
            4    ABH  Aberystwyth
        """

        gwr_depot_codes = fetch_data_from_file(
            cls=self, method='collect_gwr_codes', data_name=self.KEY_TO_GWR, ext=".pickle",
            update=update, dump_dir=dump_dir, verbose=verbose)

        return gwr_depot_codes

    def fetch_codes(self, update=False, dump_dir=None, verbose=False):
        """
        Fetch data of `depot codes`_.

        .. _`depot codes`: http://www.railwaycodes.org.uk/depots/depots0.shtm

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param dump_dir: pathname of a directory where the data file is dumped, defaults to ``None``
        :type dump_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of depot codes and date of when the data was last updated
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Depots  # from pyrcs import Depots

            >>> depots = Depots()

            >>> depots_codes = depots.fetch_codes()

            >>> type(depots_codes)
            dict
            >>> list(depots_codes.keys())
            ['Depots', 'Last updated date']

            >>> depots.KEY
            'Depots'

            >>> depots_codes_dat = depots_codes[depots.KEY]
            >>> type(depots_codes_dat)
            dict
            >>> list(depots_codes_dat.keys())
            ['1950 system (pre-TOPS) codes',
             'Four digit pre-TOPS codes',
             'GWR codes',
             'Two character TOPS codes']

            >>> depots.KEY_TO_PRE_TOPS
            'Four digit pre-TOPS codes'
            >>> depots_codes_dat[depots.KEY_TO_PRE_TOPS].head()
               Code             Depot name          Region  Main Works site
            0  2000             Accrington  London Midland            False
            1  2001   Derby Litchurch Lane  London Midland             True
            2  2003              Blackburn  London Midland            False
            3  2004  Bolton Trinity Street  London Midland            False
            4  2006                Burnley  London Midland            False

            >>> depots.KEY_TO_TOPS
            'Two character TOPS codes'
            >>> depots_codes_dat[depots.KEY_TO_TOPS].head()
              Code  ...                Notes
            0   AB  ...          Closed 1987
            1   AB  ...
            2   AC  ...  Became WH from 1994
            3   AC  ...
            4   AD  ...
            [5 rows x 5 columns]
        """

        verbose_ = False if (dump_dir or not verbose) else (2 if verbose == 2 else True)

        depot_data = []
        for func in dir(self):
            if func.startswith('fetch_') and func != 'fetch_codes':
                depot_data.append(getattr(self, func)(
                    update=update, verbose=verbose_ if is_home_connectable() else False))

        depot_codes = {
            self.KEY: {next(iter(x)): next(iter(x.values())) for x in depot_data},
            self.KEY_TO_LAST_UPDATED_DATE: self.last_updated_date
        }

        if dump_dir is not None:
            save_data_to_file(
                self, data=depot_codes, data_name=self.KEY, ext=".pickle", dump_dir=dump_dir,
                verbose=verbose)

        return depot_codes
