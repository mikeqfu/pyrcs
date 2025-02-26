"""
Collects data of British `railway bridges <http://www.railwaycodes.org.uk/bridges/bridges0.shtm>`_.
"""

import os
import re
import urllib.parse

import bs4
from pyhelpers.ops import split_list_by_size

from .._base import _Base
from ..parser import _get_last_updated_date
from ..utils import home_page_url


class Bridges(_Base):
    """
    A class for collecting data of
    `railway bridges <http://www.railwaycodes.org.uk/bridges/bridges0.shtm>`_.
    """

    #: The name of the data.
    NAME: str = 'Railway bridges'
    #: The key for accessing the data.
    KEY: str = 'Bridges'
    #: The URL of the main webpage for the data.
    URL: str = urllib.parse.urljoin(home_page_url(), '/bridges/bridges0.shtm')
    #: The key used to reference the last updated date in the data.
    KEY_TO_LAST_UPDATED_DATE: str = 'Last updated date'

    def __init__(self, data_dir=None, update=False, verbose=True):
        """
        :param data_dir: Directory where the data is stored; defaults to ``None``.
        :type data_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``True``.
        :type verbose: bool | int

        :ivar dict catalogue: The catalogue of the data.
        :ivar str last_updated_date: The date when the data was last updated.
        :ivar str data_dir: The path to the directory containing the data.
        :ivar str current_data_dir: The path to the current data directory.

        **Examples**::

            >>> from pyrcs.line_data import Bridges  # alternatively, from pyrcs import Bridges
            >>> bdg = Bridges()
            >>> bdg.NAME
            'Railway bridges'
            >>> bdg.URL
            'http://www.railwaycodes.org.uk/bridges/bridges0.shtm'
        """

        super().__init__(
            data_dir=data_dir, content_type='introduction', data_category="line-data",
            update=update, verbose=verbose)

    def _parse_h4_ul_li(self, h4_ul_li):
        h4_ul_li_contents = h4_ul_li.contents

        h4_ul_li_dict = {}
        if len(h4_ul_li_contents) == 1:
            h4_ul_li_content = h4_ul_li_contents[0]

            text = h4_ul_li_content.get_text(strip=True)
            href = h4_ul_li_content.get('href')

        else:  # len(h4_ul_li_contents) == 2:
            span_a_href, suppl_text = h4_ul_li_contents
            if not isinstance(suppl_text, str):
                suppl_text, span_a_href = h4_ul_li_contents

            text = span_a_href.get_text(strip=True)
            if suppl_text:
                text += ' ' + suppl_text

            href = span_a_href.find('a').get('href')

        link = urllib.parse.urljoin(os.path.dirname(self.URL) + '/', href)
        h4_ul_li_dict.update({text: link})

        return h4_ul_li_dict

    def _parse_h4(self, h4):
        h4_txt = h4.get_text(strip=True)

        h4_dat = None

        h4_ul = h4.find_next(name='ul')
        if isinstance(h4_ul, bs4.Tag):
            h4_ul_lis = h4_ul.find_all(name='li')
            h4_dat = {}
            for h4_ul_li in h4_ul_lis:
                h4_dat.update(self._parse_h4_ul_li(h4_ul_li))

        elif h4_ul is None:
            h4_pre = h4.find_next('pre')
            if isinstance(h4_pre, bs4.Tag):
                h4_dat = dict([x.split('\t') for x in h4_pre.text.split('\n')])

        return {h4_txt: h4_dat}

    def _parse_source(self, source, verbose=False):
        """
        Scrapes the data of `railway bridges`_ from its source webpage.

        .. _`railway bridges`: http://www.railwaycodes.org.uk/bridges/bridges0.shtm

        :param source: HTTP response containing the webpage content.
        :type source: requests.Response
        :param verbose: Whether to print relevant information in the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing railway bridge data and the date of the last update.
        :rtype: dict
        """

        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

        h4_list = soup.find_all(name='h4')

        data = {k: v for h4 in h4_list for k, v in self._parse_h4(h4).items()}

        # Key to text presentation conventions
        keys_h3 = h4_list[-1].find_next(name='h3')
        keys_p_contents = keys_h3.find_next('p').contents

        keys_p_contents_ = []
        for x in keys_p_contents:
            if isinstance(x, str):
                y = re.sub(r'( = +)|\n', '', x).capitalize()
            else:
                y = x.get_text(strip=True)
            keys_p_contents_.append(y)

        sub_dict = split_list_by_size(keys_p_contents_, sub_len=2)
        keys_dict = {keys_h3.text: {k: v for k, v in sub_dict}}

        data.update(keys_dict)

        last_updated_date = _get_last_updated_date(soup=soup, parsed=True)
        data = {self.KEY: data, self.KEY_TO_LAST_UPDATED_DATE: last_updated_date}

        if verbose in {True, 1}:
            print("Done.")

        self._save_data_to_file(data, data_name=self.KEY, ext=".json", verbose=verbose, indent=4)

        return data

    def collect_codes(self, confirmation_required=True, verbose=False, raise_error=False):
        """
        Collects the data of `railway bridges`_ from its source webpage.

        .. _`railway bridges`: http://www.railwaycodes.org.uk/bridges/bridges0.shtm

        :param confirmation_required: Whether user confirmation is required;
            if ``confirmation_required=True`` (default), prompts the user for confirmation
            before proceeding with data collection.
        :type confirmation_required: bool
        :param verbose: Whether to print relevant information in the console; defaults to ``False``.
        :type verbose: bool | int
        :param raise_error: Whether to raise the provided exception;
            if ``raise_error=False`` (default), the error will be suppressed.
        :type raise_error: bool
        :return: A dictionary containing railway bridge data and the date of the last update,
            or ``None`` if no data is collected.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.line_data import Bridges  # from pyrcs import Bridges
            >>> bdg = Bridges()
            >>> bdg_codes = bdg.collect_codes(verbose=True)
            To collect data of railway bridges
            ? [No]|Yes: yes
            >>> type(bdg_codes)
            dict
            >>> list(bdg_codes.keys())
            ['East Coast Main Line',
             'Midland Main Line',
             'West Coast Main Line',
             'Scotland',
             'Elizabeth Line',
             'London Overground',
             'Anglia',
             'London Underground',
             'Key to text presentation conventions']
            >>> bdg_codes['Key to text presentation conventions']
            {'Bold': 'Existing bridges',
             'Bold italic': 'Existing locations',
             'Light italic': 'Former/historical locations',
             'Red': 'Stations',
             'Deep red': 'Level crossings',
             'Brown': 'Ventilation shafts',
             'Purple': 'Junctions',
             'Black,grey': 'Bridges and culverts',
             'Green': 'Tunnel portals',
             'Bright blue': 'Viaducts',
             'Deep blue': 'Boundaries'}
        """

        data = self._collect_data_from_source(
            data_name=self.NAME.lower(), method=self._parse_source, url=self.URL,
            confirmation_required=confirmation_required, verbose=verbose, raise_error=raise_error)

        return data

    def fetch_codes(self, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetches the codes of `railway bridges`_.

        .. _`railway bridges`: http://www.railwaycodes.org.uk/bridges/bridges0.shtm

        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing railway bridge data and the date of the last update,
            or ``None`` if no data is retrieved.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.line_data import Bridges  # from pyrcs import Bridges
            >>> bdg = Bridges()
            >>> bdg_codes = bdg.fetch_codes()
            >>> type(bdg_codes)
            dict
            >>> list(bdg_codes.keys())
            ['East Coast Main Line',
             'West Coast Main Line',
             'Scotland',
             'Elizabeth Line',
             'London Overground',
             'Anglia',
             'London Underground',
             'Addendum',
             'Key to text presentation conventions']
            >>> bdg_codes['Key to text presentation conventions']
            {'Bold': 'Existing bridges',
             'Bold italic': 'Existing locations',
             'Light italic': 'Former/historical locations',
             'Red': 'Stations',
             'Deep red': 'Level crossings',
             'Brown': 'Ventilation shafts',
             'Purple': 'Junctions',
             'Black,grey': 'Bridges and culverts',
             'Green': 'Tunnel portals',
             'Bright blue': 'Viaducts',
             'Deep blue': 'Boundaries'}
        """

        args = {
            'data_name': self.KEY,
            'method': self.collect_codes,
            'ext': ".json",
        }
        kwargs.update(args)

        data = self._fetch_data_from_file(
            update=update, dump_dir=dump_dir, verbose=verbose, **kwargs)

        return data
