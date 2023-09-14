"""
Collect data of British `railway bridges <http://www.railwaycodes.org.uk/bridges/bridges0.shtm>`_.
"""

import os
import re
import urllib.parse

import bs4
import requests
from pyhelpers.dirs import cd
from pyhelpers.ops import confirmed, fake_requests_headers, split_list_by_size

from ..parser import get_introduction, get_last_updated_date
from ..utils import fetch_data_from_file, format_err_msg, home_page_url, init_data_dir, \
    print_collect_msg, print_conn_err, print_inst_conn_err, save_data_to_file


class Bridges:
    """
    A class for collecting data of
    `railway bridges <http://www.railwaycodes.org.uk/bridges/bridges0.shtm>`_.
    """

    #: Name of the data
    NAME = 'Railway bridges'
    #: Key of the `dict <https://docs.python.org/3/library/stdtypes.html#dict>`_-type data
    KEY = 'Bridges'
    #: URL of the main web page of the data
    URL = urllib.parse.urljoin(home_page_url(), '/bridges/bridges0.shtm')
    #: Key of the data of the last updated date
    KEY_TO_LAST_UPDATED_DATE = 'Last updated date'

    def __init__(self, data_dir=None, verbose=True):
        """
        :param data_dir: name of data directory, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``True``
        :type verbose: bool or int

        :ivar dict catalogue: catalogue of the data
        :ivar str last_updated_date: last update date
        :ivar str data_dir: path to the data directory
        :ivar str current_data_dir: path to the current data directory

        **Examples**::

            >>> from pyrcs.line_data import Bridges  # from pyrcs import Bridges

            >>> bdg = Bridges()

            >>> bdg.NAME
            'Railway bridges'

            >>> bdg.URL
            'http://www.railwaycodes.org.uk/bridges/bridges0.shtm'
        """

        print_conn_err(verbose=verbose)

        self.introduction = get_introduction(url=self.URL, verbose=verbose)

        self.last_updated_date = get_last_updated_date(url=self.URL, parsed=True, as_date_type=False)

        self.data_dir, self.current_data_dir = init_data_dir(self, data_dir, category="line-data")

    def _cdd(self, *sub_dir, **kwargs):
        """
        Change directory to package data directory and subdirectories (and/or a file).

        The directory for this module: ``"data\\line-data\\bridges"``.

        :param sub_dir: subdirectory or subdirectories (and/or a file)
        :type sub_dir: str
        :param kwargs: [optional] parameters of the function `pyhelpers.dir.cd`_
        :return: pathname of the backup data directory for the class
            :py:class:`~pyrcs.line_data.bridges.Bridges`
        :rtype: str

        .. _`pyhelpers.dir.cd`:
            https://pyhelpers.readthedocs.io/en/latest/_generated/pyhelpers.dir.cd.html
        """

        pathname = cd(self.data_dir, *sub_dir, mkdir=True, **kwargs)

        return pathname

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

    def collect_codes(self, confirmation_required=True, verbose=False):
        """
        Collect codes of `railway bridges`_ from source web page.

        .. _`railway bridges`: http://www.railwaycodes.org.uk/bridges/bridges0.shtm

        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of railway bridges and date of when the data was last updated
        :rtype: dict or None

        **Examples**::

            >>> from pyrcs.line_data import Bridges  # from pyrcs import Bridges

            >>> bdg = Bridges()

            >>> bdg_codes = bdg.collect_codes()
            To collect data of railway bridges
            ? [No]|Yes: yes
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

        data_name = f"data of {self.NAME.lower()}"

        if confirmed(f"To collect {data_name}\n?", confirmation_required=confirmation_required):

            print_collect_msg(
                data_name=data_name, verbose=verbose, confirmation_required=confirmation_required)

            bridges_data = None

            try:
                # url = 'http://www.railwaycodes.org.uk/bridges/bridges0.shtm'
                # source = requests.get(url, headers=fake_requests_headers(randomized=True))
                source = requests.get(url=self.URL, headers=fake_requests_headers())

            except Exception as e:
                if verbose == 2:
                    print("Failed. ", end="")
                print_inst_conn_err(verbose=verbose, e=e)

            else:
                try:
                    soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

                    h4s = soup.find_all(name='h4')

                    bridges_data = {}
                    for h4 in h4s:
                        h4_text = h4.get_text(strip=True)

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
                                # noinspection PyTypeChecker
                                h4_dat = dict([x.split('\t') for x in h4_pre.text.split('\n')])

                        bridges_data.update({h4_text: h4_dat})

                    # Key to text presentation conventions
                    keys_h3 = h4s[-1].find_next(name='h3')
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

                    bridges_data.update(keys_dict)

                    if verbose == 2:
                        print("Done.")

                    save_data_to_file(
                        self, data=bridges_data, data_name=self.KEY, ext=".json", verbose=verbose,
                        indent=4)

                except Exception as e:
                    print(f"Failed. {format_err_msg(e)}")

            return bridges_data

    def fetch_codes(self, update=False, dump_dir=None, verbose=False):
        """
        Fetch codes of `railway bridges`_.

        .. _`railway bridges`: http://www.railwaycodes.org.uk/bridges/bridges0.shtm

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param dump_dir: pathname of a directory where the data file is dumped, defaults to ``None``
        :type dump_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of railway bridges and date of when the data was last updated
        :rtype: dict or None

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

        bridges_data = fetch_data_from_file(
            cls=self, method='collect_codes', data_name=self.KEY, ext=".json",
            update=update, dump_dir=dump_dir, verbose=verbose)

        return bridges_data
