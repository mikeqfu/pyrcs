"""
Collects `telegraph codes <http://www.railwaycodes.org.uk/misc/telegraph.shtm>`_.
"""

import urllib.parse

import bs4

from .._base import _Base
from ..parser import _get_last_updated_date, parse_tr
from ..utils import cd_data, home_page_url


def _parse_telegraph_in_use_term(x):
    if x == '♠':
        y = 'cross industry term used in 1939'

    elif x == '†':
        y = 'cross industry term used in 1939 and still used by BR in the 1980s'

    else:
        y = x

    return y


class Telegraph(_Base):
    """
    A class for `telegraph code words <http://www.railwaycodes.org.uk/features/telegraph.shtm>`_.
    """

    #: The name of the data.
    NAME: str = 'Telegraph code words'
    #: The key for accessing the data.
    KEY: str = 'Telegraphic codes'
    #: The URL of the main web page for the data.
    URL: str = urllib.parse.urljoin(home_page_url(), '/features/telegraph.shtm')
    #: The key used to reference the last updated date in the data.
    KEY_TO_LAST_UPDATED_DATE: str = 'Last updated date'

    def __init__(self, data_dir=None, update=False, verbose=True):
        """
        :param data_dir: The name of the directory for storing the data; defaults to ``None``.
        :type data_dir: str | None
        :param update: Whether to check for updates to the catalogue; defaults to ``False``.
        :type update: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``True``.
        :type verbose: bool | int

        :ivar dict catalogue: The catalogue of the data.
        :ivar str last_updated_date: The date when the data was last updated.
        :ivar str data_dir: The path to the directory containing the data.
        :ivar str current_data_dir: The path to the current data directory.

        **Examples**::

            >>> from pyrcs.other_assets import Telegraph  # from pyrcs import Telegraph
            >>> tel = Telegraph()
            >>> tel.NAME
            'Telegraph code words'
        """

        super().__init__(
            data_dir=data_dir, data_category="other-assets", update=update, verbose=verbose)

    def _collect_codes(self, source, verbose=False):
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

        telegraph_code_words = {
            self.KEY: telegraph_code_words_dat,
            self.KEY_TO_LAST_UPDATED_DATE: _get_last_updated_date(soup=soup),
        }

        if verbose in {True, 1}:
            print("Done.")

        self._save_data_to_file(
            data=telegraph_code_words, data_name=self.KEY, dump_dir=cd_data("features"),
            verbose=verbose)

        return telegraph_code_words

    def collect_codes(self, confirmation_required=True, verbose=False, raise_error=False):
        """
        Collects data of
        `telegraph code words <http://www.railwaycodes.org.uk/misc/telegraph.shtm>`_
        from the source web page.

        :param confirmation_required: Whether user confirmation is required;
            if ``confirmation_required=True`` (default), prompts the user for confirmation
            before proceeding with data collection.
        :type confirmation_required: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :param raise_error: Whether to raise the provided exception;
            if ``raise_error=False`` (default), the error will be suppressed.
        :type raise_error: bool
        :return: A dictionary containing the data of telegraph code words and
            the date they were last updated, or ``None`` if no data is collected.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.other_assets import Telegraph  # from pyrcs import Telegraph
            >>> tel = Telegraph()
            >>> tel_codes = tel.collect_codes()
            To collect data of telegraphic codes
            ? [No]|Yes: yes
            >>> type(tel_codes)
            dict
            >>> list(tel_codes.keys())
            ['Telegraphic codes', 'Last updated date']
            >>> tel.KEY
            'Telegraphic codes'
            >>> tel_codes_dat = tel_codes[tel.KEY]
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

        telegraph_code_words = self._collect_data_from_source(
            data_name=self.KEY.lower(), method=self._collect_codes, url=self.URL,
            confirmation_required=confirmation_required,
            confirmation_prompt=f"To collect data of {self.KEY.lower()}\n?",
            verbose=verbose, raise_error=raise_error)

        return telegraph_code_words

    def fetch_codes(self, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetches the data of `telegraph code words`_.

        .. _`telegraph code words`: http://www.railwaycodes.org.uk/misc/telegraph.shtm

        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the data of telegraph code words and
            the date they were last updated.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Telegraph  # from pyrcs import Telegraph
            >>> tel = Telegraph()
            >>> tel_codes = tel.fetch_codes()
            >>> type(tel_codes)
            dict
            >>> list(tel_codes.keys())
            ['Telegraphic codes', 'Last updated date']
            >>> tel.KEY
            'Telegraphic codes'
            >>> tel_codes_dat = tel_codes[tel.KEY]
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

        args = {
            'data_name': self.KEY,
            'method': self.collect_codes,
            'data_dir': cd_data("features"),
        }
        kwargs.update(args)

        telegraph_code_words = self._fetch_data_from_file(
            update=update, dump_dir=dump_dir, verbose=verbose, **kwargs)

        return telegraph_code_words
