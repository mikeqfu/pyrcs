"""
Collect `CRS, NLC, TIPLOC and STANOX codes <http://www.railwaycodes.org.uk/crs/crs0.shtm>`_.
"""

import collections
import os
import re
import string
import urllib.parse

import bs4
import pandas as pd
import requests
from pyhelpers._cache import _format_err_msg
from pyhelpers.dirs import cd, validate_dir
from pyhelpers.ops import confirmed, fake_requests_headers
from pyhelpers.store import load_data, save_data

from pyrcs.parser import get_catalogue, get_hypertext, get_last_updated_date, get_page_catalogue, \
    parse_date, parse_tr
from pyrcs.utils import collect_in_fetch_verbose, confirm_msg, fetch_data_from_file, home_page_url, \
    init_data_dir, is_home_connectable, print_collect_msg, print_conn_err, print_inst_conn_err, \
    print_void_msg, save_data_to_file, validate_initial


class LocationIdentifiers:
    """
    A class for collecting data of
    `location identifiers <http://www.railwaycodes.org.uk/crs/crs0.shtm>`_
    (including `other systems' station codes <http://www.railwaycodes.org.uk/crs/crs1.shtm>`_).
    """

    #: Name of the data
    NAME = 'CRS, NLC, TIPLOC and STANOX codes'
    #: Key of the `dict <https://docs.python.org/3/library/stdtypes.html#dict>`_-type data
    KEY = 'LocationID'

    #: Key of the dict-type data of the '*other systems*'
    KEY_TO_OTHER_SYSTEMS = 'Other systems'
    #: Key of the dict-type data of the '*multiple station codes explanatory note*'
    KEY_TO_MSCEN = 'Multiple station codes explanatory note'
    #: Key of the dict-type data of *additional notes*
    KEY_TO_ADDITIONAL_NOTES = 'Additional notes'

    #: URL of the main web page of the data
    URL = urllib.parse.urljoin(home_page_url(), '/crs/crs0.shtm')

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

            >>> from pyrcs.line_data import LocationIdentifiers
            >>> # from pyrcs import LocationIdentifiers

            >>> lid = LocationIdentifiers()

            >>> lid.NAME
            'CRS, NLC, TIPLOC and STANOX codes'

            >>> lid.URL
            'http://www.railwaycodes.org.uk/crs/crs0.shtm'
        """

        print_conn_err(verbose=verbose)

        self.introduction = self._get_introduction(verbose=False)

        self.catalogue = get_catalogue(url=self.URL, update=update, confirmation_required=False)

        mscen_url = urllib.parse.urljoin(home_page_url(), '/crs/crs2.shtm')
        self.catalogue.update({self.KEY_TO_MSCEN: mscen_url})

        self.other_systems_catalogue = get_page_catalogue(url=self.catalogue[self.KEY_TO_OTHER_SYSTEMS])

        self.data_dir, self.current_data_dir = init_data_dir(
            self, data_dir=data_dir, category="line-data", cluster="crs-nlc-tiploc-stanox")
        # cluster = re.sub(r",| codes| and", "", self.NAME.lower()).replace(" ", "-")

    def _cdd(self, *sub_dir, mkdir=True, **kwargs):
        """
        Change directory to package data directory and subdirectories (and/or a file).

        The directory for this module: ``"data\\line-data\\crs-nlc-tiploc-stanox"``.

        :param sub_dir: subdirectory or subdirectories (and/or a file)
        :type sub_dir: str
        :param mkdir: whether to create the specified directory, defaults to ``True``
        :type mkdir: bool
        :param kwargs: [optional] parameters of the function `pyhelpers.dir.cd`_
        :return: path to the backup data directory for the class
            :py:class:`~pyrcs.line_data.loc_id.LocationIdentifiers`
        :rtype: str

        .. _pyhelpers.dir.cd:
            https://pyhelpers.readthedocs.io/en/latest/_generated/pyhelpers.dir.cd.html
        """

        kwargs.update({'mkdir': mkdir})
        path = cd(self.data_dir, *sub_dir, **kwargs)

        return path

    def _get_introduction(self, verbose=False):
        """
        Get introductory text on the main web page of the data. (Incomplete.)

        :param verbose: whether to print relevant information in console, defaults to ``True``
        :type verbose: bool or int
        :return: introductory text for the data of this cluster
        :rtype: str
        """

        introduction = None

        try:
            source = requests.get(url=self.URL, headers=fake_requests_headers())

        except requests.exceptions.ConnectionError:
            print_inst_conn_err(verbose=verbose)

        else:
            soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

            h3s = soup.find_all('h3')

            h3 = h3s[0]

            p = h3.find_next(name='p')
            prev_h3, prev_h4 = p.find_previous(name='h3'), p.find_previous(name='h4')

            intro_paras = []
            while prev_h3 == h3 and prev_h4 is None:
                para_text = p.text.replace('  ', ' ')
                intro_paras.append(para_text)

                p = p.find_next(name='p')
                prev_h3, prev_h4 = p.find_previous(name='h3'), p.find_previous(name='h4')

            introduction = '\n'.join(intro_paras)

        return introduction

    @staticmethod
    def _collect_list(p, list_head_tag):
        notes = p.text.strip('thus:', '.')

        elements = [get_hypertext(x) for x in list_head_tag.findChildren('li')]

        list_data = {
            'Notes': notes,
            'BulletPoints': elements,
        }

        return list_data

    @staticmethod
    def _parse_note_page(note_url, parser='html.parser', verbose=False):
        """
        Parse addition note page.

        :param note_url: URL link of the target web page
        :type note_url: str
        :param parser: the `parser`_ to use for `bs4.BeautifulSoup`_, defaults to ``'html.parser'``
        :type parser: str
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: parsed texts
        :rtype: list

        .. _`parser`:
            https://www.crummy.com/software/BeautifulSoup/bs4/doc/
            index.html#specifying-the-parser-to-use
        .. _`bs4.BeautifulSoup`:
            https://www.crummy.com/software/BeautifulSoup/bs4/doc/index.html

        **Examples**::

            >>> from pyrcs.line_data import LocationIdentifiers
            >>> # from pyrcs import LocationIdentifiers

            >>> lid = LocationIdentifiers()

            >>> url = 'http://www.railwaycodes.org.uk/crs/crs2.shtm'

            >>> parsed_note_dat = lid._parse_note_page(note_url=url)
            >>> parsed_note_dat[3]
                               Location  CRS CRS_alt1 CRS_alt2
            0           Glasgow Central  GLC      GCL
            1      Glasgow Queen Street  GLQ      GQL
            2                   Heworth  HEW      HEZ
            3      Highbury & Islington  HHY      HII      XHZ
            4    Lichfield Trent Valley  LTV      LIF
            5     Liverpool Lime Street  LIV      LVL
            6   Liverpool South Parkway  LPY      ALE
            7         London St Pancras  STP      SPL      SPX
            8                   Retford  RET      XRO
            9   Smethwick Galton Bridge  SGB      GTI
            10                 Tamworth  TAM      TAH
            11       Willesden Junction  WIJ      WJH      WJL
            12   Worcestershire Parkway  WOP      WPH
        """

        try:
            source = requests.get(note_url, headers=fake_requests_headers())

        except Exception as e:
            print_inst_conn_err(verbose=verbose, e=e)
            return None

        web_page_text = bs4.BeautifulSoup(markup=source.text, features=parser).find_all(['p', 'pre'])
        parsed_text = [x.text for x in web_page_text if isinstance(x.next_element, str)]

        parsed_note = []
        for x in parsed_text:
            if '\n' in x:
                text = re.sub('\t+', ',', x).replace('\t', ' ').replace('\xa0', '').split('\n')
            else:
                text = x.replace('\t', ' ').replace('\xa0', '')

            if isinstance(text, list):
                text = [[x.strip() for x in t.split(',')] for t in text if t != '']
                temp = pd.DataFrame(text, columns=['Location', 'CRS', 'CRS_alt1', 'CRS_alt2'])
                parsed_note.append(temp.fillna(''))
            else:
                to_remove = ['click the link', 'click your browser', 'Thank you', 'shown below']
                if text != '' and not any(t in text for t in to_remove):
                    parsed_note.append(text)

        return parsed_note

    def collect_explanatory_note(self, confirmation_required=True, verbose=False):
        """
        Collect note about CRS code from source web page.

        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of multiple station codes explanatory note
        :rtype: dict or None

        **Examples**::

            >>> from pyrcs.line_data import LocationIdentifiers
            >>> # from pyrcs import LocationIdentifiers

            >>> lid = LocationIdentifiers()

            >>> exp_note = lid.collect_explanatory_note()
            To collect data of Multiple station codes explanatory note
            ? [No]|Yes: yes
            >>> type(exp_note)
            dict
            >>> list(exp_note.keys())
            ['Multiple station codes explanatory note', 'Notes', 'Last updated date']

            >>> lid.KEY_TO_MSCEN
            'Multiple station codes explanatory note'

            >>> exp_note_dat = exp_note[lid.KEY_TO_MSCEN]
            >>> type(exp_note_dat)
            pandas.core.frame.DataFrame
            >>> exp_note_dat.head()
                             Location  CRS CRS_alt1 CRS_alt2
            0         Glasgow Central  GLC      GCL
            1    Glasgow Queen Street  GLQ      GQL
            2                 Heworth  HEW      HEZ
            3    Highbury & Islington  HHY      HII      XHZ
            4  Lichfield Trent Valley  LTV      LIF
        """

        cfm_msg = confirm_msg(data_name=self.KEY_TO_MSCEN)
        if confirmed(prompt=cfm_msg, confirmation_required=confirmation_required):

            print_collect_msg(
                self.KEY_TO_MSCEN, verbose=verbose, confirmation_required=confirmation_required)

            note_url = self.catalogue[self.KEY_TO_MSCEN]
            explanatory_note_ = self._parse_note_page(note_url=note_url, verbose=False)

            if explanatory_note_ is None:
                if verbose == 2:
                    print("Failed. ", end="")

                print_inst_conn_err(verbose=verbose)

                explanatory_note = None

            else:
                try:
                    explanatory_note, notes = {}, []

                    for x in explanatory_note_:
                        if isinstance(x, str):
                            if 'Last update' in x:
                                lud = {self.KEY_TO_LAST_UPDATED_DATE: parse_date(x, as_date_type=False)}
                                explanatory_note.update(lud)
                            else:
                                notes.append(x)
                        else:
                            explanatory_note.update({self.KEY_TO_MSCEN: x})

                    explanatory_note.update({'Notes': notes})

                    # Rearrange the dict
                    explanatory_note = {
                        k: explanatory_note[k]
                        for k in [self.KEY_TO_MSCEN, 'Notes', self.KEY_TO_LAST_UPDATED_DATE]
                    }

                    if verbose == 2:
                        print("Done.")

                    save_data_to_file(
                        self, data=explanatory_note, data_name=self.KEY_TO_MSCEN, ext=".pkl",
                        verbose=verbose)

                except Exception as e:
                    print(f"Failed. {_format_err_msg(e)}")
                    explanatory_note = None

            return explanatory_note

    def fetch_explanatory_note(self, update=False, dump_dir=None, verbose=False):
        """
        Fetch multiple station codes explanatory note.

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param dump_dir: pathname of a directory where the data file is dumped, defaults to ``None``
        :type dump_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of multiple station codes explanatory note
        :rtype: dict

        **Examples**::

            >>> from pyrcs.line_data import LocationIdentifiers
            >>> # from pyrcs import LocationIdentifiers

            >>> lid = LocationIdentifiers()

            >>> exp_note = lid.fetch_explanatory_note()
            >>> type(exp_note)
            dict
            >>> list(exp_note.keys())
            ['Multiple station codes explanatory note', 'Notes', 'Last updated date']

            >>> lid.KEY_TO_MSCEN
            'Multiple station codes explanatory note'

            >>> exp_note_dat = exp_note[lid.KEY_TO_MSCEN]
            >>> type(exp_note_dat)
            pandas.core.frame.DataFrame
            >>> exp_note_dat.head()
                             Location  CRS CRS_alt1 CRS_alt2
            0         Glasgow Central  GLC      GCL
            1    Glasgow Queen Street  GLQ      GQL
            2                 Heworth  HEW      HEZ
            3    Highbury & Islington  HHY      HII      XHZ
            4  Lichfield Trent Valley  LTV      LIF
        """

        explanatory_note = fetch_data_from_file(
            cls=self, method='collect_explanatory_note', data_name=self.KEY_TO_MSCEN,
            ext=".pkl", update=update, dump_dir=dump_dir, verbose=verbose)

        return explanatory_note

    # -- CRS, NLC, TIPLOC and STANOX ---------------------------------------------------------------

    @staticmethod
    def _location_name(x):
        """
        Parse location name (and its associated note).

        :param x: location name (in raw data)
        :type x: str or None
        :return: location name and note (if any)
        :rtype: tuple

        **Examples**::

            >>> from pyrcs.line_data import LocationIdentifiers
            >>> # from pyrcs import LocationIdentifiers

            >>> lid = LocationIdentifiers()

            >>> dat = lid._location_name(None)
            >>> dat
            ('', '')

            >>> dat = lid._location_name('Abbey Wood')
            >>> dat
            ('Abbey Wood', '')

            >>> dat = lid._location_name('Abercynon (formerly Abercynon South)')
            >>> dat
            ('Abercynon', 'formerly Abercynon South')

            >>> dat = lid._location_name('Allerton (reopened as Liverpool South Parkway)')
            >>> dat
            ('Allerton', 'reopened as Liverpool South Parkway')

            >>> dat = lid._location_name('Ashford International [domestic portion]')
            >>> dat
            ('Ashford International', 'domestic portion')

            >>> dat = lid._location_name('Ayr [unknown feature]')
            >>> dat
            ('Ayr', 'unknown feature')

            >>> dat = lid._location_name('Birkenhead Hamilton Square [see Hamilton Square]')
            >>> dat
            ('Birkenhead Hamilton Square', 'see Hamilton Square')
        """

        if not x:
            x_, note = '', ''

        else:
            # Location name
            d = re.search(r'.*(?= \[[\"\']\()', x)
            if d is not None:
                x_ = d.group(0)
            elif ' [unknown feature' in x:  # ' [unknown feature, labelled "do not use"]' in x
                x_ = re.search(r'\w.*(?= \[unknown feature(, )?)', x).group(0)
            elif ') [formerly' in x:
                x_ = re.search(r'.*(?= \[formerly)', x).group(0)
            elif '✖' in x:
                x_ = re.search(r'.*(?=✖)', x).group(0)
            else:
                x_tmp = re.search(r'(?=[\[(]).*(?<=[])])|(?=\().*(?<=\) \[)', x)
                if x_tmp is not None:
                    x_tmp = x_tmp.group(0)
                    x_pat = re.compile(r'[Oo]riginally |'
                                       r'[Ff]ormerly |'
                                       r'[Ll]ater |'
                                       r'[Pp]resumed |'
                                       r' \(was |'
                                       r' \(in |'
                                       r' \(at |'
                                       r' \(also |'
                                       r' \(second code |'
                                       r'\?|'
                                       r'\n|'
                                       r' \(\[\'|'
                                       r' \(definition unknown\)|'
                                       r' \(reopened |'
                                       r'( portion])$|'
                                       r'[Ss]ee ')
                    x_ = ' '.join(x.replace(x_tmp, '').split()) if re.search(x_pat, x) else x
                else:
                    x_ = x

            # Note
            y_ = x.replace(x_, '', 1).strip()
            if y_ == '':
                note = ''
            elif '✖' in y_:
                note = re.search(r'(?<=✖).*', y_).group(0)
            else:
                note_ = re.search(r'(?<=[\[(])[\w ,?]+(?=[])])', y_)
                if note_ is None:
                    note_ = re.search(
                        r'(?<=(\[[\'\"]\()|(\([\'\"]\[)|(\) \[)).*(?=(\)[\'\"]])|(][\'\"]\))|])', y_)
                elif '"now deleted"' in y_ and y_.startswith('(') and y_.endswith(')'):
                    note_ = re.search(r'(?<=\().*(?=\))', y_)

                note = note_.group(0) if note_ is not None else ''
                if note.endswith('\'') or note.endswith('"'):
                    note = note[:-1]

            if 'STANOX ' in x_ and 'STANOX ' in x and note == '':
                x_ = x[0:x.find('STANOX')].strip()
                note = x[x.find('STANOX'):]

        return x_, note

    @staticmethod
    def _amendment_to_location_names():
        """Create a replacement dictionary for location name amendments.

        :return: dictionary of regular-expression amendments to location names
        :rtype: dict

        **Examples**::

            >>> from pyrcs.line_data import LocationIdentifiers
            >>> # from pyrcs import LocationIdentifiers

            >>> lid = LocationIdentifiers()

            >>> loc_name_amendment_dict = lid._amendment_to_location_names()

            >>> list(loc_name_amendment_dict.keys())
            ['Location']
        """

        location_name_amendment_dict = {
            'Location': {re.compile(r' And | \+ '): ' & ',
                         re.compile(r'-By-'): '-by-',
                         re.compile(r'-In-'): '-in-',
                         re.compile(r'-En-Le-'): '-en-le-',
                         re.compile(r'-La-'): '-la-',
                         re.compile(r'-Le-'): '-le-',
                         re.compile(r'-On-'): '-on-',
                         re.compile(r'-The-'): '-the-',
                         re.compile(r' Of '): ' of ',
                         re.compile(r'-Super-'): '-super-',
                         re.compile(r'-Upon-'): '-upon-',
                         re.compile(r'-Under-'): '-under-',
                         re.compile(r'-Y-'): '-y-'}}

        return location_name_amendment_dict

    def _parse_location_name(self, data):
        """
        Parse the location names of the preprocessed data.

        :param data: preprocessed data of the location codes
        :type data: pandas.DataFrame
        """

        # Collect additional information as note
        data[['Location', 'Location_Note']] = pd.DataFrame(
            data['Location'].map(self._location_name).to_list())

        # # Debugging
        # for i, x in enumerate(data['Location']):
        #     try:
        #         _parse_location_name(x)
        #     except Exception:
        #         print(i)
        #         break

        # Regulate location names
        data.replace(self._amendment_to_location_names(), regex=True, inplace=True)

    @staticmethod
    def _extra_annotations():
        extra_annotations = [
            ('✖Earlier code ', '✖Later code'),
            ('✖Later code ', '✖Earlier code'),
            ('✖Earlier code, soon replaced ', '✖Later code introduced before station opened'),
            ('✖Later code introduced before station opened ', '✖Earlier code, soon replaced'),
            ('✖Original code ', '✖Later code'),
            ('✖Later code ', '✖Original code'),
            ('✖Original code ', '✖Later code from station opening'),
            ('✖Later code from station opening ', '✖Original code'),
            ('✖Newer designation? ', '✖Older designation?'),
            ('✖Older designation? ', '✖Newer designation?'),
            ('✖Both codes quoted with equal reliability ',
             '✖Both codes quoted with equal reliability'),
            ('✖Code used by operational research software ',
             '✖Code as used by National Rail Enquiries and other public systems'),
            ('✖Code as used by National Rail Enquiries and other public systems ',
             '✖Code used by operational research software'),
            ('✖Code assigned in error ', '✖Corrected code'),
            ('✖Original code ', '✖Later code after becoming part of national network'),
            ('✖Later code after becoming part of national network ', '✖Original code'),
            ('✖Code used after station reopened ', '✖Code used until station reopened'),
            ('✖Code used until station reopened ', '✖Code used after station reopened'),
            ('✖Code used after nearby station reopened ', '✖Code used until nearby station reopened'),
            ('✖Code used until nearby station reopened ', '✖Code used after nearby station reopened'),
            ('✖Original code; see also CRS explanation ', '✖Later code; see also CRS explanation'),
            ('✖Later code; see also CRS explanation ', '✖Original code; see also CRS explanation'),
            ('✖Most sources state LOUNOC, some have LOUNGOC ',
             '✖Most sources state LOUNOC, some have LOUNGOC'),
            ("✖Code may start with 'R' ", "✖Code may start with 'B'"),
            ("✖Code may start with 'B' ", "✖Code may start with 'R'"),
            ('✖Older designation when station open ', '✖Newer designation once station closed'),
            ('✖Newer designation once station closed ', '✖Older designation when station open'),
            ('✖Original code when named Butlins Penychain ', '✖Later code after renaming Penychain'),
            ('✖Later code after renaming Penychain ', '✖Original code when named Butlins Penychain'),
            ('✖Earlier code ',
             '✖Later code after East London Line operated as part of national network'),
            ('✖Code should be ROODENDGD but some listings show this as RO0DENDGD (with zero digit) ',
             '✖Code should be ROODENDGD but some listings show this as RO0DENDGD (with zero digit)'),
            ('✖Earlier code? ', '✖Later code'),
            ('✖See CRS explanation ', '✖Code believed listed in error'),
            ('✖Code is 56582 but some sources have 56782 ',
             '✖Code is 56582 but some sources have 56782'),
            ('✖Code should be 79251 but one source has 79521 ',
             '✖Code should be 79251 but one source has 79521'),
            ('✖Code is 56540 but some sources have 56450 ',
             '✖Code is 56540 but some sources have 56450'),
            ('✖Earlier code ', '✖Later code; also see CRS explanation'),
            ('✖Later code ', '✖Possibly earlier code'),
            ('✖Code is 142505 but is also reported as 145505 ',
             '✖Code is 142505 but is also reported as 145505'),
            ('✖Earlier code ', '✖Later code after station closed'),
        ]

        return extra_annotations

    @staticmethod
    def _count_sep(x):
        if '\r\n' in x:
            r_n_counts = x.count('\r\n')
        elif '\r' in x:
            r_n_counts = x.count('\r')
        else:  # Ad hoc
            if '~LO\n' in x:
                x = x.replace('~LO\n', '')
            # elif any(all(a_ in x for a_ in a) for a in self._extra_annotations()):
            #     temp = [
            #         x.replace(a[0], f'{a[0][:-1]}\n') for a in self._extra_annotations()
            #         if a[0] in x and x.endswith(a[1])]
            #     x = temp[0]
            r_n_counts = x.count('\n')
        return r_n_counts

    @staticmethod
    def _split_dat_and_note(x):
        if '\r\n' in x:
            x_ = x.split('\r\n')
        elif '\r' in x:
            x_ = x.split('\r')
        elif '\n' in x:
            if '~LO\n' in x:  # Ad hoc
                x = x.replace('~LO\n', '')
            x_ = x.split('\n')
        else:
            x_ = x
        return x_

    @staticmethod
    def _fix_special_cases(data):
        x1 = 'Ely Papworth Sidings English Welsh & Scottish Railway International\n' \
             'Ely Papworth Sidings DB Schenker International'
        if x1 in data['Location'].values:
            x1_ = 'Ely Papworth Sidings English Welsh & Scottish Railway International\n' \
                  'Ely Papworth Sidings DB Schenker International\n' \
                  'Ely Papworth Sidings DB Schenker International'
            data.loc[data['Location'] == x1, 'Location'] = x1_

        return data

    def _cleanse_mult_alt_codes(self, data):
        """
        Cleanse multiple alternatives for every code column.

        :param data: preprocessed data of the location codes
        :type data: pandas.DataFrame
        :return: cleansed data of the location codes where multiple alternatives are replicated
        :rtype: pandas.DataFrame
        """

        data_ = data.copy()
        data_ = self._fix_special_cases(data_)

        code_col_names = ['Location', 'CRS', 'NLC', 'TIPLOC', 'STANME', 'STANOX']

        r_n_counts = data_[code_col_names].map(self._count_sep)
        # # Debugging:
        # for col in code_col_names:
        #     for i, x in enumerate(data_[col]):
        #         try:
        #             lid._count_sep(x)
        #         except Exception:
        #             print(col, i, x)
        #             break

        r_n_counts_ = r_n_counts.mul(-1).add(r_n_counts.max(axis=1), axis='index')

        for col in code_col_names:
            for i in data_.index:
                d = r_n_counts_.loc[i, col]
                x = data_.loc[i, col]
                if d > 0:
                    if '\r\n' in x:
                        if col == 'Location':
                            data_.loc[i, col] = x + ''.join(['\r\n' + x.split('\r\n')[-1]] * d)
                        else:
                            data_.loc[i, col] = x + ''.join(['\r\n'] * d)
                    elif '\r' in x:
                        if col == 'Location':
                            data_.loc[i, col] = x + ''.join(['\r' + x.split('\r')[-1]] * d)
                        else:
                            data_.loc[i, col] = x + ''.join(['\r'] * d)
                    else:  # e.g. '\n' in dat:
                        if col == 'Location':
                            data_.loc[i, col] = '\n'.join([x] * (d + 1))
                        else:
                            data_.loc[i, col] = x + ''.join(['\n'] * d)
                # elif any(all(a_ in x for a_ in a) for a in self._extra_annotations()):
                #     temp = [
                #         x.replace(a[0], f'{a[0][:-1]}\n') for a in self._extra_annotations()
                #         if a[0] in x and x.endswith(a[1])]
                #     data_.loc[i, col] = temp[0]

        data_[code_col_names] = data_[code_col_names].map(self._split_dat_and_note)

        data_ = data_.explode(code_col_names, ignore_index=True)

        temp = data_.select_dtypes(['object'])
        data_[temp.columns] = temp.apply(lambda x_: x_.str.strip())

        return data_

    @staticmethod
    def _get_code_note(x):
        """
        Get note for every code column.

        :param x: raw data of a given code
        :type x: str or None
        :return: extra information (if any) about the given code
        :rtype: str

        **Examples**::

            >>> from pyrcs.line_data import LocationIdentifiers
            >>> # from pyrcs import LocationIdentifiers

            >>> lid = LocationIdentifiers()

            >>> lid._get_code_note('860260✖Earlier code')
            ('860260', 'Earlier code')
        """

        if x:
            if '✖' in x:
                x_, note = x.split('✖')

            else:  # Search for notes
                n1 = re.search(r'(?<=[\[(])[\w,? ]+(?=[)\]])', x)

                if n1 is not None:
                    note = n1.group(0)
                    x_ = x.replace(note, '').strip('[(\')] ')

                    n2 = re.search(r'[\w ,]+(?= [\[(\'])', note)  # Strip redundant characters
                    if n2 is not None:
                        note = n2.group(0)

                else:
                    x_, note = x, ''

        else:
            x_, note = x, ''

        return x_, note

    def _get_code_notes(self, data):
        """
        Get notes for every code column.

        :param data: preprocessed data of the location codes
        :type data: pandas.DataFrame
        """

        codes_col_names = ['CRS', 'NLC', 'TIPLOC', 'STANME', 'STANOX']

        for col in codes_col_names:
            data[[col, col + '_Note']] = pd.DataFrame(
                data[col].map(self._get_code_note).to_list(), index=data.index)
        # # Debugging:
        # for col in codes_col_names:
        #     for i, x in enumerate(data[col]):
        #         try:
        #             lid._get_code_note(x)
        #         except Exception:
        #             print(col, i, x)
        #             break

    @staticmethod
    def _stanox_note(x):  # Parse STANOX note
        """
        Parse STANOX note.

        :param x: STANOX note
        :type x: str or None
        :return: stanox and its corresponding note
        :rtype: tuple
        """

        if x in ('-', '') or x is None:
            stanox, note = '', ''

        else:
            if re.match(r'\d{5}$', x):
                stanox = x
                note = ''

            elif re.match(r'\d{5}\*$', x):
                stanox = x.rstrip('*')
                note = 'Pseudo STANOX'

            elif re.match(r'\d{5} \w.*', x):
                stanox = re.search(r'\d{5}', x).group()
                note = re.search(r'(?<= )\w.*', x).group()

            else:
                d = re.search(r'[\w *,]+(?= [\[(\'])', x)
                stanox = d.group() if d is not None else x
                note = 'Pseudo STANOX' if '*' in stanox else ''
                n = re.search(r'(?<=[\[(\'])[\w, ]+.(?=[)\]\'])', x)

                if n is not None:
                    note = '; '.join(x for x in [note, n.group()] if x != '')

                if '(' not in note and note.endswith(')'):
                    note = note.rstrip(')')

        return stanox, note

    def _parse_stanox_note(self, data):
        """
        Parse the note for STANOX.

        :param data: preprocessed data of the location codes
        :type data: pandas.DataFrame
        """

        col_name = 'STANOX'
        note_col_name = col_name + '_Note'

        if not data.empty:
            parsed_dat = data[col_name].map(self._stanox_note).to_list()
            data[[col_name, note_col_name]] = pd.DataFrame(parsed_dat, index=data.index)
        else:
            # No data is available on the web page for the given 'key_word'
            data[note_col_name] = data[col_name]

        data[col_name] = data[col_name].str.replace('-', '')

    def _get_additional_notes(self, data, beginning_with, soup):
        if any('see note' in crs_note for crs_note in data['CRS_Note']):
            loc_idx = [i for i, crs_n in enumerate(data['CRS_Note']) if 'see note' in crs_n]

            # web_page_text = bs4.BeautifulSoup(markup=source.text, features='html.parser')

            note_urls = [
                urllib.parse.urljoin(self.catalogue[beginning_with], x['href'])
                for x in soup.find_all('a', href=True, string='note')]
            add_notes = [self._parse_note_page(note_url, verbose=False) for note_url in note_urls]

            additional_notes = dict(zip(data['CRS'].iloc[loc_idx], add_notes))
        else:
            additional_notes = None

        return additional_notes

    def collect_codes_by_initial(self, initial, update=False, verbose=False):
        """
        Collect `CRS, NLC, TIPLOC, STANME and STANOX codes
        <http://www.railwaycodes.org.uk/crs/crs0.shtm>`_ for a given initial letter.

        :param initial: initial letter of station/junction name or certain word for specifying URL
        :type initial: str
        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of locations beginning with the given initial letter and
            date of when the data was last updated
        :rtype: dict

        **Examples**::

            >>> from pyrcs.line_data import LocationIdentifiers
            >>> # from pyrcs import LocationIdentifiers

            >>> lid = LocationIdentifiers()

            >>> loc_a_codes = lid.collect_codes_by_initial(initial='a')
            >>> type(loc_a_codes)
            dict
            >>> list(loc_a_codes.keys())
            ['A', 'Additional notes', 'Last updated date']

            >>> loc_a_codes_dat = loc_a_codes['A']
            >>> type(loc_a_codes_dat)
            pandas.core.frame.DataFrame
            >>> loc_a_codes_dat.head()
                                          Location CRS  ... STANME_Note STANOX_Note
            0                 1999 Reorganisations      ...
            1                                   A1      ...
            2                       A463 Traded In      ...
            3  A483 Road Scheme Supervisors Closed      ...
            4                               Aachen      ...
            [5 rows x 12 columns]
        """

        beginning_with = validate_initial(initial)

        path_to_pickle = self._cdd("a-z", beginning_with.lower() + ".pkl")

        if os.path.isfile(path_to_pickle) and not update:
            location_codes_initial = load_data(path_to_pickle)

        else:
            if verbose == 2:
                print(f"Collecting data of locations beginning with '{beginning_with}'", end=" ... ")

            location_codes_initial = {
                beginning_with: None,
                self.KEY_TO_ADDITIONAL_NOTES: None,
                self.KEY_TO_LAST_UPDATED_DATE: None,
            }

            url = self.catalogue[beginning_with]

            try:
                source = requests.get(url=url, headers=fake_requests_headers())
            except Exception as e:
                if verbose == 2:
                    print("Failed. ", end="")
                print_inst_conn_err(verbose=verbose, e=e)

            else:
                try:
                    # Get a raw DataFrame
                    soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

                    thead, tbody = soup.find('thead'), soup.find('tbody')
                    ths = [th.text.strip() for th in thead.find_all('th')]
                    trs = tbody.find_all('tr')

                    dat = parse_tr(trs=trs, ths=ths, sep=None, as_dataframe=True)
                    dat = dat.replace({'\b-\b': '', '\xa0\xa0': ' ', '&half;': ' and 1/2'}, regex=True)

                    data = dat.replace({'\xa0': ''}, regex=True)

                    # Parse location names and their corresponding notes
                    self._parse_location_name(data=data)

                    # Cleanse multiple alternatives for every code column
                    data = self._cleanse_mult_alt_codes(data=data)

                    # Get note for every code column
                    self._get_code_notes(data=data)

                    # Further parse STANOX note
                    self._parse_stanox_note(data=data)

                    additional_notes = self._get_additional_notes(
                        data=data, beginning_with=beginning_with, soup=soup)

                    location_codes_initial = {
                        beginning_with: data,
                        self.KEY_TO_ADDITIONAL_NOTES: additional_notes,
                        self.KEY_TO_LAST_UPDATED_DATE: get_last_updated_date(url=url),
                    }

                    if verbose == 2:
                        print("Done.")

                    save_data(location_codes_initial, path_to_pickle, verbose=verbose)

                except Exception as e:
                    print(f"Failed. {_format_err_msg(e)}")

        return location_codes_initial

    @staticmethod
    def _parse_code(x):
        protocol = 'https://'

        if '; ' in x and protocol in x:
            temp = x.split('; ')
            x0, x1 = temp[0], [y.split(protocol) for y in temp if protocol in y][0]
            x1 = ' ('.join([x1[0], protocol + x1[1]]) + ')'
            x_ = [x0, x1]
        else:
            x_ = [x, '']

        return x_

    def _parse_tbl_dat(self, h3_or_h4):
        tbl_dat = h3_or_h4.find_next('thead'), h3_or_h4.find_next('tbody')
        thead, tbody = tbl_dat
        ths = [x.text for x in thead.find_all('th')]
        trs = tbody.find_all('tr')
        tbl = parse_tr(trs=trs, ths=ths, as_dataframe=True)

        if 'Code' in tbl.columns:
            if tbl.Code.str.contains('https://').sum() > 0:
                temp = tbl['Code'].map(self._parse_code)
                tbl_ext = pd.DataFrame(zip(*temp)).T
                tbl_ext.columns = ['Code', 'Code_extra']
                del tbl['Code']
                tbl = pd.concat([tbl, tbl_ext], axis=1, sort=False)

        return tbl

    # -- Other systems -----------------------------------------------------------------------------

    def collect_other_systems_codes(self, confirmation_required=True, verbose=False):
        """
        Collect data of `other systems' station codes`_ from source web page.

        .. _`other systems' station codes`: http://www.railwaycodes.org.uk/crs/crs1.shtm

        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: codes of other systems
        :rtype: dict or None

        **Examples**::

            >>> from pyrcs.line_data import LocationIdentifiers
            >>> # from pyrcs import LocationIdentifiers

            >>> lid = LocationIdentifiers()

            >>> os_codes = lid.collect_other_systems_codes()
            To collect data of Other systems
            ? [No]|Yes: yes
            >>> type(os_codes)
            dict
            >>> list(os_codes.keys())
            ['Other systems', 'Last updated date']

            >>> lid.KEY_TO_OTHER_SYSTEMS
            'Other systems'

            >>> os_codes_dat = os_codes[lid.KEY_TO_OTHER_SYSTEMS]
            >>> type(os_codes_dat)
            collections.defaultdict
            >>> list(os_codes_dat.keys())
            ['Córas Iompair Éireann (Republic of Ireland)',
             'Crossrail',
             'Croydon Tramlink',
             'Docklands Light Railway',
             'Manchester Metrolink',
             'Translink (Northern Ireland)',
             'Tyne & Wear Metro']
        """

        cfm_msg = confirm_msg(data_name=self.KEY_TO_OTHER_SYSTEMS)
        if confirmed(prompt=cfm_msg, confirmation_required=confirmation_required):

            print_collect_msg(
                self.KEY_TO_OTHER_SYSTEMS, verbose=verbose, confirmation_required=confirmation_required)

            other_systems_codes = None

            try:
                url = self.catalogue[self.KEY_TO_OTHER_SYSTEMS]
                source = requests.get(url=url, headers=fake_requests_headers())

            except Exception as e:
                if verbose == 2:
                    print("Failed. ", end="")
                print_inst_conn_err(verbose=verbose, e=e)

            else:
                try:
                    soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

                    other_systems_codes = collections.defaultdict(dict)

                    for h3 in soup.find_all('h3'):
                        h4 = h3.find_next('h4')

                        if h4 is not None:
                            while h4:
                                prev_h3 = h4.find_previous('h3')
                                if prev_h3.text == h3.text:
                                    other_systems_codes[h3.text].update(
                                        {h4.text: self._parse_tbl_dat(h4)})
                                    h4 = h4.find_next('h4')
                                elif h3.text not in other_systems_codes.keys():
                                    other_systems_codes.update({h3.text: self._parse_tbl_dat(h3)})
                                    break
                                else:
                                    break
                        else:
                            other_systems_codes.update({h3.text: self._parse_tbl_dat(h3)})

                    other_systems_codes = {
                        self.KEY_TO_OTHER_SYSTEMS: other_systems_codes,
                        self.KEY_TO_LAST_UPDATED_DATE: get_last_updated_date(url),
                    }

                    if verbose == 2:
                        print("Done.")

                    save_data_to_file(
                        self, data=other_systems_codes, data_name=self.KEY_TO_OTHER_SYSTEMS,
                        ext=".pkl", verbose=verbose)

                except Exception as e:
                    print(f"Failed. {_format_err_msg(e)}")

            return other_systems_codes

    def fetch_other_systems_codes(self, update=False, dump_dir=None, verbose=False):
        """
        Fetch data of `other systems' station codes`_.

        .. _`other systems' station codes`: http://www.railwaycodes.org.uk/crs/crs1.shtm

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param dump_dir: pathname of a directory where the data file is dumped, defaults to ``None``
        :type dump_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: codes of other systems
        :rtype: dict

        **Examples**::

            >>> from pyrcs.line_data import LocationIdentifiers
            >>> # from pyrcs import LocationIdentifiers

            >>> lid = LocationIdentifiers()

            >>> os_codes = lid.fetch_other_systems_codes()
            >>> type(os_codes)
            dict
            >>> list(os_codes.keys())
            ['Other systems', 'Last updated date']

            >>> lid.KEY_TO_OTHER_SYSTEMS
            'Other systems'

            >>> os_codes_dat = os_codes[lid.KEY_TO_OTHER_SYSTEMS]
            >>> type(os_codes_dat)
            collections.defaultdict
            >>> list(os_codes_dat.keys())
            ['Córas Iompair Éireann (Republic of Ireland)',
             'Crossrail',
             'Croydon Tramlink',
             'Docklands Light Railway',
             'Manchester Metrolink',
             'Translink (Northern Ireland)',
             'Tyne & Wear Metro']
        """

        other_systems_codes = fetch_data_from_file(
            cls=self, method='collect_other_systems_codes', data_name=self.KEY_TO_OTHER_SYSTEMS,
            ext=".pkl", update=update, dump_dir=dump_dir, verbose=verbose)

        return other_systems_codes

    def fetch_codes(self, update=False, dump_dir=None, verbose=False):
        """
        Fetch `CRS, NLC, TIPLOC, STANME and STANOX codes`_ and `other systems' station codes`_.

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param dump_dir: pathname of a directory where the data file is dumped, defaults to ``None``
        :type dump_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of location codes and date of when the data was last updated
        :rtype: dict

        .. _`CRS, NLC, TIPLOC, STANME and STANOX codes`: http://www.railwaycodes.org.uk/crs/crs0.shtm
        .. _`other systems' station codes`: http://www.railwaycodes.org.uk/crs/crs1.shtm

        **Examples**::

            >>> from pyrcs.line_data import LocationIdentifiers
            >>> # from pyrcs import LocationIdentifiers

            >>> lid = LocationIdentifiers()

            >>> loc_codes = lid.fetch_codes()
            >>> type(loc_codes)
            dict
            >>> list(loc_codes.keys())
            ['LocationID', 'Other systems', 'Additional notes', 'Last updated date']

            >>> lid.KEY
            'LocationID'

            >>> loc_codes_dat = loc_codes[lid.KEY]
            >>> type(loc_codes_dat)
            pandas.core.frame.DataFrame
            >>> loc_codes_dat.head()
                                          Location CRS  ... STANME_Note STANOX_Note
            0                                   A1      ...
            1                       A463 Traded In      ...
            2  A483 Road Scheme Supervisors Closed      ...
            3                               Aachen      ...
            4                     AA Holidays S524      ...
            [5 rows x 12 columns]
        """

        verbose_1 = collect_in_fetch_verbose(data_dir=dump_dir, verbose=verbose)

        # Get every data table
        verbose_2 = verbose_1 if is_home_connectable() else False
        data = [
            self.collect_codes_by_initial(initial=x, update=update, verbose=verbose_2)
            for x in string.ascii_lowercase
        ]

        if all(d[x] is None for d, x in zip(data, string.ascii_uppercase)):
            if update:
                print_inst_conn_err(verbose=verbose)
                print_void_msg(data_name=self.KEY, verbose=verbose)

            data = [
                self.collect_codes_by_initial(initial=x, update=False, verbose=verbose_1)
                for x in string.ascii_lowercase
            ]

        # Select DataFrames only
        loc_codes_data = (item[x] for item, x in zip(data, string.ascii_uppercase))
        loc_codes_data_tbl = pd.concat(loc_codes_data, ignore_index=True, sort=False)

        # Likely errors in 'STANME' and 'STANOX' (spotted occasionally)
        err_cols = ['STANME', 'STANOX']

        row_idx = loc_codes_data_tbl[loc_codes_data_tbl.Location == 'Selby Melmerby Estates'].index[0]
        loc_codes_data_tbl.loc[row_idx, err_cols] = ['', '']

        row_idx = loc_codes_data_tbl[loc_codes_data_tbl.Location == 'Selby Potter Group'].index[0]
        loc_codes_data_tbl.loc[row_idx, err_cols] = loc_codes_data_tbl.loc[row_idx, err_cols].values

        # Get the latest updated date
        last_updated_dates = (
            item[self.KEY_TO_LAST_UPDATED_DATE] for item, _ in zip(data, string.ascii_uppercase))
        latest_update_date = max(d for d in last_updated_dates if d is not None)

        # Get other systems codes
        other_systems_codes = self.fetch_other_systems_codes(
            update=update, verbose=verbose_1)[self.KEY_TO_OTHER_SYSTEMS]

        # Get additional note
        additional_notes = self.fetch_explanatory_note(update=update, verbose=verbose_1)

        # Create a dict to include all information
        location_codes = {
            self.KEY: loc_codes_data_tbl,
            self.KEY_TO_OTHER_SYSTEMS: other_systems_codes,
            self.KEY_TO_ADDITIONAL_NOTES: additional_notes,
            self.KEY_TO_LAST_UPDATED_DATE: latest_update_date,
        }

        if dump_dir is not None:
            save_data_to_file(
                self, data=location_codes, data_name=self.KEY, ext=".pkl", dump_dir=dump_dir,
                verbose=verbose)

        return location_codes

    def make_xref_dict(self, keys, initials=None, main_key=None, as_dict=False, drop_duplicates=False,
                       dump_it=False, dump_dir=None, verbose=False):
        """
        Make a dict/dataframe for location code data for the given ``keys``.

        :param keys: one or a sublist of ['CRS', 'NLC', 'TIPLOC', 'STANOX', 'STANME']
        :type keys: str or list
        :param initials: one or a sequence of initials for which the codes are used, defaults to ``None``
        :type initials: str or list or None
        :param main_key: key of the returned dictionary (when ``as_dict=True``), defaults to ``None``
        :type main_key: str or None
        :param as_dict: whether to return a dictionary, defaults to ``False``
        :type as_dict: bool
        :param drop_duplicates: whether to drop duplicates, defaults to ``False``
        :type drop_duplicates: bool
        :param dump_it: whether to save the location codes dictionary, defaults to ``False``
        :type dump_it: bool
        :param dump_dir: pathname of a directory where the data file is dumped, defaults to ``None``
        :type dump_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: dictionary or a data frame for location code data for the given ``keys``
        :rtype: dict or pandas.DataFrame or None

        **Examples**::

            >>> from pyrcs.line_data import LocationIdentifiers
            >>> # from pyrcs import LocationIdentifiers

            >>> lid = LocationIdentifiers()

            >>> stanox_dictionary = lid.make_xref_dict(keys='STANOX')
            >>> type(stanox_dictionary)
            pandas.core.frame.DataFrame
            >>> stanox_dictionary.head()
                                      Location
            STANOX
            00005                       Aachen
            04309           Abbeyhill Junction
            04311        Abbeyhill Signal E811
            04308   Abbeyhill Turnback Sidings
            88601                   Abbey Wood

            >>> s_t_dictionary = lid.make_xref_dict(keys=['STANOX', 'TIPLOC'], initials='a')
            >>> type(s_t_dictionary)
            pandas.core.frame.DataFrame
            >>> s_t_dictionary.head()
                                              Location
            STANOX TIPLOC
            00005  AACHEN                       Aachen
            04309  ABHLJN           Abbeyhill Junction
            04311  ABHL811       Abbeyhill Signal E811
            04308  ABHLTB   Abbeyhill Turnback Sidings
            88601  ABWD                     Abbey Wood

            >>> ks = ['STANOX', 'TIPLOC']
            >>> ini = 'b'
            >>> main_k = 'Data'
            >>> s_t_dictionary = lid.make_xref_dict(ks, ini, main_k, as_dict=True)
            >>> type(s_t_dictionary)
            dict
            >>> list(s_t_dictionary.keys())
            ['Data']
            >>> list(s_t_dictionary['Data'].keys())[:5]
            [('55115', ''),
             ('23490', 'BABWTHL'),
             ('38306', 'BACHE'),
             ('66021', 'BADESCL'),
             ('81003', 'BADMTN')]
        """

        valid_keys = {'CRS', 'NLC', 'TIPLOC', 'STANOX', 'STANME'}
        assert_msg = f"`keys` must be one of {valid_keys}."

        if isinstance(keys, str):
            assert keys in valid_keys, assert_msg
            keys = [keys]
        else:  # isinstance(keys, list):
            assert all(x in valid_keys for x in keys), assert_msg

        if main_key:
            assert isinstance(main_key, str), "`main_key` must be a string."

        if initials is not None:
            if isinstance(initials, str):
                initials = [validate_initial(initials, as_is=True)]
            else:  # e.g. isinstance(initials, list)
                assert all(x in set(string.ascii_letters) for x in initials)
            temp = [self.collect_codes_by_initial(x, verbose=verbose)[x.upper()] for x in initials]
            location_codes = pd.concat(temp, axis=0, ignore_index=True, sort=False)
        else:
            location_codes = self.fetch_codes(verbose=verbose)[self.KEY]

        if verbose == 2:
            print("To make/update a location code dictionary", end=" ... ")

        try:  # Deep cleansing location_code
            key_locid = location_codes[['Location'] + keys]
            key_locid = key_locid.query(' | '.join(['{} != \'\''.format(k) for k in keys]))

            if drop_duplicates:
                locid_subset = key_locid.drop_duplicates(subset=keys, keep='first')
                locid_dupe = None

            else:  # drop_duplicates is False or None
                locid_subset = key_locid.drop_duplicates(subset=keys, keep=False)

                dupl_temp_1 = key_locid[key_locid.duplicated(['Location'] + keys, keep=False)]
                dupl_temp_2 = key_locid[key_locid.duplicated(keys, keep=False)]
                duplicated_1 = dupl_temp_2[dupl_temp_1.eq(dupl_temp_2)].dropna().drop_duplicates()
                duplicated_2 = dupl_temp_2[~dupl_temp_1.eq(dupl_temp_2)].dropna()
                duplicated = pd.concat([duplicated_1, duplicated_2], axis=0, sort=False)
                locid_dupe = duplicated.groupby(keys).agg(tuple)
                locid_dupe.Location = locid_dupe.Location.map(lambda x: x[0] if len(set(x)) == 1 else x)

            locid_subset.set_index(keys, inplace=True)
            location_codes_ref = pd.concat([locid_subset, locid_dupe], axis=0, sort=False)

            if as_dict:
                location_codes_ref_dict = location_codes_ref.to_dict()
                if main_key is None:
                    location_codes_dictionary = location_codes_ref_dict['Location']
                else:
                    location_codes_ref_dict[main_key] = location_codes_ref_dict.pop('Location')
                    location_codes_dictionary = location_codes_ref_dict
            else:
                location_codes_dictionary = location_codes_ref

            if verbose == 2:
                print("Successfully.")

            if dump_it:
                dump_dir_ = validate_dir(dump_dir) if dump_dir else self._cdd("xref-dicts")
                data_name = "-".join(keys) + ("" if initials is None else "-" + "".join(initials))
                ext = ".json" if as_dict and len(keys) == 1 else ".pkl"

                save_data_to_file(
                    self, data=location_codes_dictionary, data_name=data_name, ext=ext,
                    dump_dir=dump_dir_, verbose=verbose)

        except Exception as e:
            print(f"Failed. {_format_err_msg(e)}")
            location_codes_dictionary = None

        return location_codes_dictionary
