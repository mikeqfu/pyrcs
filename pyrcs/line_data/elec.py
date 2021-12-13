"""
Collect `section codes for overhead line electrification (OLE) installations
<http://www.railwaycodes.org.uk/electrification/mast_prefix0.shtm>`_.
"""

import itertools
import urllib.error
import urllib.parse

from pyhelpers.dir import cd
from pyhelpers.store import load_pickle

from pyrcs.utils import *
from pyrcs.utils import _cd_dat


def _collect_notes(h3):
    notes_ = []

    # h4 = h3.find_next('h4')
    # if h4:
    #     previous_h3 = h4.find_previous('h3')
    #     if previous_h3 == h3 and h4.text == 'Notes':
    #         notes_1 = dict(
    #             (x.a.get('id').title(), x.get_text(strip=True).replace('\xa0', ''))
    #             for x in h4.find_next('ol') if x != '\n')
    #         if notes_1:
    #             notes_.append(notes_1)

    next_p = h3.find_next('p')
    if next_p is not None:
        h3_ = next_p.find_previous('h3')
        while h3_ == h3:
            notes_2 = get_hypertext(hypertext_tag=next_p, hyperlink_tag_name='a')
            if notes_2:
                notes_2 = notes_2. \
                    replace(' Section codes known at present are:', ''). \
                    replace('Known prefixes are:', ' ')
                notes_.append(notes_2)

            next_p = next_p.find_next('p')
            if next_p is None:
                break
            else:
                h3_ = next_p.find_previous('h3')

    notes = ' '.join(notes_).replace('  ', ' ')

    if not notes:
        notes = None

    # if isinstance(notes, list):
    #     notes = ' '.join(notes)

    # ex_note_tag = note_tag.find_next('ol')
    # if ex_note_tag:
    #     previous_h3 = ex_note_tag.find_previous('h3')
    #     if previous_h3 == h3:
    #         dat = list(
    #             re.sub(r'[()]', '', x.text).split(' ', 1) for x in ex_note_tag.find_all('li'))
    #         li = pd.DataFrame(data=dat, columns=['Initial', 'Code'])
    #         notes = [notes, li]

    return notes


def _collect_codes_without_list(h3):
    """
    h3 = h3.find_next('h3')
    """
    sub_heading = get_heading(heading_tag=h3, elem_name='em')

    notes = _collect_notes(h3=h3)

    data = {sub_heading: {'Codes': None, 'Notes': notes}}

    return data


def _collect_list_only(h3, ul):
    sub_heading = get_heading(heading_tag=h3, elem_name='em')

    list_data = [get_hypertext(x) for x in ul.findChildren('li')]
    notes = _collect_notes(h3).strip().replace(' were:', '.')

    codes_with_list = {sub_heading: {'Codes': list_data, 'Notes': notes}}

    return codes_with_list


def _collect_codes_with_list(h3, ul):
    """
    'Blackpool Tramway',
    """

    sub_heading = get_heading(heading_tag=h3, elem_name='em')

    data_1_key, data_2_key = 'Section codes', 'Known prefixes'
    table_1, table_2 = {data_1_key: None}, {data_2_key: None}

    # data_1
    table_1[data_1_key] = pd.DataFrame(
        data=[re.sub(r'[()]', '', x.text).split(' ', 1) for x in ul.findChildren('li')],
        columns=['Code', 'Area'])

    # data_2
    thead, tbody = h3.find_next('thead'), h3.find_next('tbody')
    ths, trs = [th.text for th in thead.find_all('th')], tbody.find_all('tr')
    dat_2 = pd.DataFrame(data=parse_tr(header=ths, trs=trs), columns=ths)

    table_2[data_2_key] = dat_2

    # Notes
    notes = _collect_notes(h3)

    # next_p = p.find_next('p')  # .find_next('p')
    # while next_p.find_previous('h3') == h3:
    #     note_2 = next_p.text
    #     table_2[data_2_key]['Notes'].append(note_2)
    #     next_p = next_p.find_next('p')
    #     if next_p is None:
    #         break

    codes_with_list = {sub_heading: {**table_1, **table_2, 'Notes': notes}}

    return codes_with_list


def _collect_codes_and_notes(h3):
    """
    elec = Electrification()

    url = elec.Catalogue[elec.INDEPENDENT_LINES_KEY]
    source = requests.get(url=url, headers=fake_requests_headers(randomized=True))
    soup = bs4.BeautifulSoup(markup=source.text, features='html.parser')

    h3 = soup.find('h3')

    h3 = h3.find_next('h3')
    """
    codes_and_notes = None

    p, ul, table = h3.find_next('p'), h3.find_next('ul'), h3.find_next('table')

    if ul is not None:
        if ul.find_previous('h3') == h3:
            if table is not None:
                codes_and_notes = _collect_codes_with_list(h3=h3, ul=ul)
            else:
                codes_and_notes = _collect_list_only(h3=h3, ul=ul)

    if table is not None and codes_and_notes is None:
        if table.find_previous('h3') == h3:
            h3_ = table.find_previous('h3')
            codes = None
            thead, tbody = table.find_next('thead'), table.find_next('tbody')

            while h3_ == h3:
                ths = [x.text for x in thead.find_all('th')]
                trs = tbody.find_all('tr')
                dat = pd.DataFrame(data=parse_tr(header=ths, trs=trs), columns=ths)
                codes_ = dat.applymap(
                    lambda x: re.sub(
                        pattern=r'\']\)?', repl=']',
                        string=re.sub(r'\(?\[\'', '[', x)).replace(
                        '\\xa0', '').replace('\r ', ' ').strip())

                codes = codes_ if codes is None else [codes, codes_]

                thead, tbody = thead.find_next('thead'), tbody.find_next('tbody')

                if tbody is None:
                    break
                else:
                    h3_ = tbody.find_previous('h3')

            notes = _collect_notes(h3=h3)

            sub_heading = get_heading(heading_tag=h3, elem_name='em')
            codes_and_notes = {sub_heading: {'Codes': codes, 'Notes': notes}}

    if codes_and_notes is None:
        codes_and_notes = _collect_codes_without_list(h3=h3)

    return codes_and_notes


class Electrification:
    """
    A class for collecting section codes for OLE installations.
    """

    #: Name of the data
    NAME = 'Section codes for overhead line electrification (OLE) installations'
    #: Key of the `dict <https://docs.python.org/3/library/stdtypes.html#dict>`_-type data
    KEY = 'Electrification'

    #: Key of the dict-type data of the '*national network*'
    KEY_TO_NATIONAL_NETWORK = 'National network'
    #: Key of the dict-type data of the '*independent lines*'
    KEY_TO_INDEPENDENT_LINES = 'Independent lines'
    #: Key of the dict-type data of the '*overhead line electrification neutral sections (OHNS)*'
    KEY_TO_OHNS = 'National network neutral sections'
    #: Key of the dict-type data of the '*UK railway electrification tariff zones*'
    KEY_TO_ENERGY_TARIFF_ZONES = 'National network energy tariff zones'

    #: URL of the main web page of the data
    URL = urllib.parse.urljoin(home_page_url(), '/electrification/mast_prefix0.shtm')

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

        :ivar str url: URL of the data web page
        :ivar str last_updated_date: last update date
        :ivar dict catalogue: catalogue of the data
        :ivar str data_dir: path to the data directory
        :ivar str current_data_dir: path to the current data directory

        **Example**::

            >>> from pyrcs.line_data import Electrification
            >>> # from pyrcs import Electrification

            >>> elec = Electrification()

            >>> print(elec.NAME)
            Electrification masts and related features

            >>> print(elec.URL)
            http://www.railwaycodes.org.uk/electrification/mast_prefix0.shtm
        """

        print_connection_error(verbose=verbose)

        self.last_updated_date = get_last_updated_date(url=self.URL)

        self.catalogue = get_catalogue(url=self.URL, update=update, confirmation_required=False)

        self.data_dir, self.current_data_dir = init_data_dir(self, data_dir, category="line-data")

    @staticmethod
    def _cfm_msg(code_key):
        cfm_msg = "To collect section codes for OLE installations: {}\n?".format(code_key.lower())
        return cfm_msg

    @staticmethod
    def _collect_data(source):
        soup = bs4.BeautifulSoup(markup=source.text, features='html.parser')

        data = {}
        h3 = soup.find('h3')
        while h3:
            data_ = _collect_codes_and_notes(h3=h3)

            if data_ is not None:
                data.update(data_)

            h3 = h3.find_next('h3')

        return data

    def _cdd_elec(self, *sub_dir, **kwargs):
        """
        Change directory to package data directory and subdirectories (and/or a file).

        The directory for this module: ``"dat\\line-data\\electrification"``.

        :param sub_dir: subdirectory or subdirectories (and/or a file)
        :type sub_dir: str
        :param kwargs: optional parameters of `pyhelpers.dir.cd`_
        :return: path to the backup data directory for the class ``Electrification``
        :rtype: str

        .. _pyhelpers.dir.cd:
            https://pyhelpers.readthedocs.io/en/latest/_generated/pyhelpers.dir.cd.html
        """

        path = cd(self.data_dir, *sub_dir, mkdir=True, **kwargs)

        return path

    def collect_national_network_codes(self, confirmation_required=True, verbose=False):
        """
        Collect OLE section codes for `national network
        <http://www.railwaycodes.org.uk/electrification/mast_prefix1.shtm>`_
        from source web page.

        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: OLE section codes for National network
        :rtype: dict or None

        **Example**::

            >>> from pyrcs.line_data import Electrification
            >>> # from pyrcs import Electrification

            >>> elec = Electrification()

            >>> nn_dat = elec.collect_national_network_codes()
            To collect section codes for OLE installations: national network
            ? [No]|Yes: yes

            >>> type(nn_dat)
            dict
            >>> list(nn_dat.keys())
            ['National network', 'Last updated date']

            >>> elec.KEY_TO_NATIONAL_NETWORK
            'National network'

            >>> nn_codes = nn_dat[elec.KEY_TO_NATIONAL_NETWORK]
            >>> type(nn_codes)
            dict
            >>> list(nn_codes.keys())
            ['Traditional numbering system [distance and sequence]',
             'New numbering system [km and decimal]',
             'Codes not certain [confirmation is welcome]',
             'Suspicious data',
             'An odd one to complete the record',
             'LBSC/Southern Railway overhead system',
             'Codes not known']

            >>> nn_codes['Traditional numbering system [distance and sequence]']['Codes']
                      Code  ...                          Datum
            0            A  ...               Fenchurch Street
            1            A  ...             Newbridge Junction
            2            A  ...               Fenchurch Street
            3            A  ...  Guide Bridge Station Junction
            4           AB  ...
            ..         ...  ...                            ...
            547         YW  ...   Camden Road Central Junction
            548          0  ...                    Kings Cross
            549          1  ...                    Kings Cross
            550  no prefix  ...                     Manchester
            551  no prefix  ...

            [552 rows x 4 columns]
        """

        cfm_msg = self._cfm_msg(self.KEY_TO_NATIONAL_NETWORK)
        if confirmed(prompt=cfm_msg, confirmation_required=confirmation_required):

            print_collect_msg(
                data_name=self.KEY_TO_NATIONAL_NETWORK, verbose=verbose,
                confirmation_required=confirmation_required)

            url = self.catalogue[self.KEY_TO_NATIONAL_NETWORK]

            national_network_ole = None

            try:
                source = requests.get(url=url, headers=fake_requests_headers(randomized=True))
            except requests.exceptions.ConnectionError:
                print("Failed. ") if verbose == 2 else ""
                print_conn_err(verbose=verbose)

            else:
                try:
                    national_network_ole_ = self._collect_data(source=source)

                    # soup = bs4.BeautifulSoup(markup=source.text, features='html.parser')

                    # h3 = soup.find('h3')
                    # while h3:
                    #     header_tag = h3.find_next('table')
                    #     if header_tag:
                    #         header = [x.text for x in header_tag.find_all('th')]
                    #
                    #         temp = parse_tr(header, header_tag.find_next('table').find_all('tr'))
                    #         table = pd.DataFrame(temp, columns=header)
                    #         table = table.applymap(
                    #             lambda x:
                    #             re.sub(r'\']\)?', ']', re.sub(r'\(?\[\'', '[', x)).replace(
                    #                 '\\xa0', '').replace('\r ', ' '))
                    #     else:
                    #         table = pd.DataFrame(
                    #             data=(x.text.replace('\r ', ' ') for x in h3.find_all_next('li')),
                    #             columns=['Unknown_codes'])
                    #
                    #     # Notes
                    #     notes = {'Notes': None}
                    #     if h3.find_next_sibling().name == 'p':
                    #         next_p = h3.find_next('p')
                    #         if next_p.find_previous('h3') == h3:
                    #             notes['Notes'] = next_p.text.replace('\xa0', '')
                    #
                    #     note_tag = h3.find_next('h4')
                    #     if note_tag and note_tag.text == 'Notes':
                    #         notes_ = dict((x.a.get('id').title(),
                    #                        x.get_text(strip=True).replace('\xa0', ''))
                    #                       for x in soup.find('ol') if x != '\n')
                    #         if notes['Notes'] is None:
                    #             # noinspection PyTypedDict
                    #             notes['Notes'] = notes_
                    #         else:
                    #             notes['Notes'] = [notes['Notes'], notes_]
                    #
                    #     # re.search(r'(\w ?)+(?=( \((\w ?)+\))?)', h3.text).group(0).strip()
                    #     dk = []
                    #     for x in h3.contents:
                    #         if x.name == 'em':
                    #             dk.append('[' + x.text + ']')
                    #         else:
                    #             dk.append(x.text)
                    #     data_key = ''.join(dk)
                    #
                    #     national_network_ole_.update({data_key: {'Codes': table, **notes}})
                    #
                    #     h3 = h3.find_next('h3')

                    source.close()

                    last_updated_date = get_last_updated_date(url=url)

                    national_network_ole = {
                        self.KEY_TO_NATIONAL_NETWORK: national_network_ole_,
                        self.KEY_TO_LAST_UPDATED_DATE: last_updated_date,
                    }

                    if verbose == 2:
                        print("Done.")

                    path_to_pickle = make_pickle_pathname(self, self.KEY_TO_NATIONAL_NETWORK)
                    save_pickle(national_network_ole, path_to_pickle, verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(e))

            return national_network_ole

    def fetch_national_network_codes(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch OLE section codes for `national network
        <http://www.railwaycodes.org.uk/electrification/mast_prefix1.shtm>`_
        from local backup.

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param pickle_it: whether to save the data as a pickle file, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of a folder where the pickle file is to be saved, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: OLE section codes for National network
        :rtype: dict or None

        **Example**::

            >>> from pyrcs.line_data import Electrification
            >>> # from pyrcs import Electrification

            >>> elec = Electrification()

            >>> nn_dat = elec.fetch_national_network_codes()
            >>> type(nn_dat)
            dict
            >>> list(nn_dat.keys())
            ['National network', 'Last updated date']

            >>> elec.KEY_TO_NATIONAL_NETWORK
            'National network'

            >>> nn_codes = nn_dat[elec.KEY_TO_NATIONAL_NETWORK]
            >>> type(nn_codes)
            dict
            >>> list(nn_codes.keys())
            ['Traditional numbering system [distance and sequence]',
             'New numbering system [km and decimal]',
             'Codes not certain [confirmation is welcome]',
             'Suspicious data',
             'An odd one to complete the record',
             'LBSC/Southern Railway overhead system',
             'Codes not known']

            >>> nn_codes['Traditional numbering system [distance and sequence]']['Codes']
                      Code  ...                          Datum
            0            A  ...               Fenchurch Street
            1            A  ...             Newbridge Junction
            2            A  ...               Fenchurch Street
            3            A  ...  Guide Bridge Station Junction
            4           AB  ...
            ..         ...  ...                            ...
            547         YW  ...   Camden Road Central Junction
            548          0  ...                    Kings Cross
            549          1  ...                    Kings Cross
            550  no prefix  ...                     Manchester
            551  no prefix  ...

            [552 rows x 4 columns]
        """

        path_to_pickle = make_pickle_pathname(self, data_name=self.KEY_TO_NATIONAL_NETWORK)

        if os.path.isfile(path_to_pickle) and not update:
            national_network_ole = load_pickle(path_to_pickle)

        else:
            national_network_ole = self.collect_national_network_codes(
                confirmation_required=False,
                verbose=collect_in_fetch_verbose(data_dir=data_dir, verbose=verbose))

            if national_network_ole is not None:
                data_to_pickle(
                    self, data=national_network_ole, data_name=self.KEY_TO_NATIONAL_NETWORK,
                    pickle_it=pickle_it, data_dir=data_dir, verbose=verbose)

            else:
                print_void_msg(data_name=self.KEY_TO_NATIONAL_NETWORK, verbose=verbose)
                national_network_ole = load_pickle(path_to_pickle)

        return national_network_ole

    def get_indep_line_catalogue(self, update=False, verbose=False):
        """
        Get names of `independent lines
        <http://www.railwaycodes.org.uk/electrification/mast_prefix2.shtm>`_.

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: a list of independent line names
        :rtype: pandas.DataFrame

        **Example**::

            >>> from pyrcs.line_data import Electrification
            >>> # from pyrcs import Electrification
            >>> from pyhelpers.settings import pd_preferences

            >>> pd_preferences(max_columns=1)

            >>> elec = Electrification()

            >>> independent_lines = elec.get_indep_line_catalogue()
            >>> independent_lines
                                                          Feature  ...
            0                                     Beamish Tramway  ...
            1                                  Birkenhead Tramway  ...
            2                         Black Country Living Museum  ...
            3                                   Blackpool Tramway  ...
            4   Brighton and Rottingdean Seashore Electric Rai...  ...
            ..                                                ...  ...
            17                                     Seaton Tramway  ...
            18                                Sheffield Supertram  ...
            19                          Snaefell Mountain Railway  ...
            20  Summerlee, Museum of Scottish Industrial Life ...  ...
            21                                  Tyne & Wear Metro  ...

            [22 rows x 3 columns]
        """

        path_to_pickle = _cd_dat("catalogue", "electrification-independent-lines.pickle")

        if os.path.isfile(path_to_pickle) and not update:
            indep_line_names = load_pickle(path_to_pickle)

        else:
            url = self.catalogue[self.KEY_TO_INDEPENDENT_LINES]
            indep_line_names = get_page_catalogue(
                url=url, head_tag='nav', head_txt='Jump to: ', feature_tag='h3', verbose=verbose)

            if indep_line_names is not None:
                save_pickle(indep_line_names, path_to_pickle, verbose=verbose)

        return indep_line_names

    def collect_indep_lines_codes(self, confirmation_required=True, verbose=False):
        """
        Collect OLE section codes for `independent lines
        <http://www.railwaycodes.org.uk/electrification/mast_prefix2.shtm>`_
        from source web page.

        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: OLE section codes for independent lines
        :rtype: dict or None

        **Example**::

            >>> from pyrcs.line_data import Electrification
            >>> # from pyrcs import Electrification

            >>> elec = Electrification()

            >>> il_ole_dat = elec.collect_indep_lines_codes()
            To collect section codes for OLE installations: independent lines
            ? [No]|Yes: yes
            >>> type(il_ole_dat)
            dict
            >>> list(il_ole_dat.keys())
            ['Independent lines', 'Last updated date']

            >>> elec.KEY_TO_INDEPENDENT_LINES
            'Independent lines'

            >>> il_ole_codes = il_ole_dat[elec.KEY_TO_INDEPENDENT_LINES]
            >>> len(il_ole_codes)
            22
            >>> type(il_ole_codes)
            dict
            >>> list(il_ole_codes.keys())
            ['Beamish Tramway',
             'Birkenhead Tramway',
             'Black Country Living Museum [Tipton]',
             'Blackpool Tramway',
             "Brighton and Rottingdean Seashore Electric Railway [Magnus Volk's 'Daddy ...
             'Channel Tunnel',
             'Croydon Tramlink',
             'East Anglia Transport Museum [Lowestoft]',
             'Edinburgh Tramway',
             'Heath Park Tramway [Cardiff]',
             'Heaton Park Tramway [Manchester]',
             'Iarnród Éireann',
             'Luas [Dublin]',
             'Manchester Metrolink',
             'Manx Electric Railway',
             'Midland Metro [West Midlands]',
             'Nottingham Express Transit',
             'Seaton Tramway',
             'Sheffield Supertram',
             'Snaefell Mountain Railway',
             'Summerlee, Museum of Scottish Industrial Life Tramway',
             'Tyne & Wear Metro']

            >>> il_ole_codes['Beamish Tramway']
            {'Codes': None, 'Notes': 'Masts do not appear labelled.'}
        """

        cfm_msg = self._cfm_msg(code_key=self.KEY_TO_INDEPENDENT_LINES)
        if confirmed(prompt=cfm_msg, confirmation_required=confirmation_required):

            print_collect_msg(
                data_name=self.KEY_TO_INDEPENDENT_LINES, verbose=verbose,
                confirmation_required=confirmation_required)

            independent_lines_ole = None

            url = self.catalogue[self.KEY_TO_INDEPENDENT_LINES]

            try:
                source = requests.get(url=url, headers=fake_requests_headers(randomized=True))
            except requests.exceptions.ConnectionError:
                print("Failed. ") if verbose == 2 else ""
                print_conn_err(verbose=verbose)

            else:
                try:
                    independent_lines_ole_ = self._collect_data(source=source)

                    source.close()

                    last_updated_date = get_last_updated_date(url=url)

                    print("Done.") if verbose == 2 else ""

                    independent_lines_ole = {
                        self.KEY_TO_INDEPENDENT_LINES: independent_lines_ole_,
                        self.KEY_TO_LAST_UPDATED_DATE: last_updated_date,
                    }

                    path_to_pickle = make_pickle_pathname(self, self.KEY_TO_INDEPENDENT_LINES)
                    save_pickle(independent_lines_ole, path_to_pickle, verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(e))

            return independent_lines_ole

    def fetch_indep_lines_codes(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch OLE section codes for `independent lines
        <http://www.railwaycodes.org.uk/electrification/mast_prefix2.shtm>`_
        from local backup.

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param pickle_it: whether to save the data as a pickle file, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of a folder where the pickle file is to be saved, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: OLE section codes for independent lines
        :rtype: dict

        **Example**::

            >>> from pyrcs.line_data import Electrification
            >>> # from pyrcs import Electrification

            >>> elec = Electrification()

            >>> il_ole_dat = elec.fetch_indep_lines_codes()
            >>> type(il_ole_dat)
            dict
            >>> list(il_ole_dat.keys())
            ['Independent lines', 'Last updated date']

            >>> elec.KEY_TO_INDEPENDENT_LINES
            'Independent lines'

            >>> il_ole_codes = il_ole_dat[elec.KEY_TO_INDEPENDENT_LINES]
            >>> len(il_ole_codes)
            22
            >>> type(il_ole_codes)
            dict
            >>> list(il_ole_codes.keys())
            ['Beamish Tramway',
             'Birkenhead Tramway',
             'Black Country Living Museum [Tipton]',
             'Blackpool Tramway',
             "Brighton and Rottingdean Seashore Electric Railway [Magnus Volk's ...,
             'Channel Tunnel',
             'Croydon Tramlink',
             'East Anglia Transport Museum [Lowestoft]',
             'Edinburgh Tramway',
             'Heath Park Tramway [Cardiff]',
             'Heaton Park Tramway [Manchester]',
             'Iarnród Éireann',
             'Luas [Dublin]',
             'Manchester Metrolink',
             'Manx Electric Railway',
             'Midland Metro [West Midlands]',
             'Nottingham Express Transit',
             'Seaton Tramway',
             'Sheffield Supertram',
             'Snaefell Mountain Railway',
             'Summerlee, Museum of Scottish Industrial Life Tramway',
             'Tyne & Wear Metro']

            >>> il_ole_codes['Beamish Tramway']
            {'Codes': None, 'Notes': 'Masts do not appear labelled.'}
        """

        path_to_pickle = make_pickle_pathname(self, data_name=self.KEY_TO_INDEPENDENT_LINES)

        if os.path.isfile(path_to_pickle) and not update:
            independent_lines_ole = load_pickle(path_to_pickle)

        else:
            independent_lines_ole = self.collect_indep_lines_codes(
                confirmation_required=False,
                verbose=collect_in_fetch_verbose(data_dir=data_dir, verbose=verbose))

            if independent_lines_ole is not None:
                data_to_pickle(
                    self, data=independent_lines_ole, data_name=self.KEY_TO_INDEPENDENT_LINES,
                    pickle_it=pickle_it, data_dir=data_dir, verbose=verbose)

            else:
                print_void_msg(data_name=self.KEY_TO_INDEPENDENT_LINES, verbose=verbose)
                independent_lines_ole = load_pickle(path_to_pickle)

        return independent_lines_ole

    def collect_ohns_codes(self, confirmation_required=True, verbose=False):
        """
        Collect codes for `overhead line electrification neutral sections
        <http://www.railwaycodes.org.uk/electrification/neutral.shtm>`_ (OHNS)
        from source web page.

        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: OHNS codes
        :rtype: dict or None

        **Example**::

            >>> from pyrcs.line_data import Electrification
            >>> # from pyrcs import Electrification

            >>> elec = Electrification()

            >>> ohns_dat = elec.collect_ohns_codes()
            To collect section codes for OLE installations: national network neutral sections
            ? [No]|Yes: yes

            >>> type(ohns_dat)
            dict
            >>> list(ohns_dat.keys())
            ['National network neutral sections', 'Last updated date']

            >>> elec.KEY_TO_OHNS
            'National network neutral sections'

            >>> ohns_data = ohns_dat[elec.KEY_TO_OHNS]
            >>> type(ohns_data)
            dict
            >>> list(ohns_data.keys())
            ['Codes', 'Notes']
            >>> ohns_data['Codes']
                  ELR          OHNS Name  ...     Tracks                             Dates
            0    ARG1         Rutherglen  ...
            1    ARG2    Finnieston East  ...       Down
            2    ARG2    Finnieston West  ...         Up
            3    AYR1   Shields Junction  ...     Up Ayr
            4    AYR1   Shields Junction  ...   Down Ayr
            ..    ...                ...  ...        ...                               ...
            488   WWD       Law Junction  ...
            489   WWD  Holytown Junction  ...                           Installed Octob...
            490   XRC          Royal Oak  ...  Westbound
            491   YKR              Yoker  ...             Installed ??, removed ≈11 Mar...
            492   YKR            Dalmuir  ...             Installed ??, removed ≈11 Mar...

            [493 rows x 5 columns]
        """

        cfm_msg = self._cfm_msg(code_key=self.KEY_TO_OHNS)
        if confirmed(prompt=cfm_msg, confirmation_required=confirmation_required):

            print_collect_msg(
                data_name=self.KEY_TO_OHNS, verbose=verbose,
                confirmation_required=confirmation_required)

            ohns_codes = None

            url = self.catalogue[self.KEY_TO_OHNS]

            try:
                # header, neutral_sections_codes = pd.read_html(io=url)
                source = requests.get(url=url, headers=fake_requests_headers(randomized=True))
            except (urllib.error.URLError, socket.gaierror):
                print("Failed. ") if verbose == 2 else ""
                print_conn_err(verbose=verbose)

            else:
                try:
                    # neutral_sections_data.columns = header.columns.to_list()
                    # neutral_sections_data.fillna('', inplace=True)

                    soup = bs4.BeautifulSoup(markup=source.text, features='html.parser')
                    thead, tbody = soup.find('thead'), soup.find('tbody')

                    ths = [th.text for th in thead.find_all('th')]
                    trs = tbody.find_all('tr')
                    tbl = parse_tr(header=ths, trs=trs)

                    tbl_ = [[x.replace('\r ', ' ').replace(" (['", ', ').replace(
                        "'])", '').replace('\\r', '').replace("', '", ', ').replace(
                        ' &ap;', '≈') for x in dat]
                        for dat in tbl]

                    tbl_copy = tbl_.copy()
                    for dat in tbl_copy:
                        tracks, dates = dat[3].split(', '), dat[4].split(', ')
                        if len(tracks) > 1 and len(dates) > 1:
                            idx = tbl_.index(dat)
                            for trk, date in zip(tracks, dates):
                                tbl_.insert(idx + 1, dat[0:3] + [trk, date])
                                idx += 1

                    neutral_sections_codes = pd.DataFrame(data=tbl_, columns=ths)

                    notes = soup.find('div', {'class': 'background'}).find_all('p')
                    notes = '\n'.join([txt.text for txt in notes]).replace('  ', ' ')

                    last_updated_date = get_last_updated_date(url=url)

                    print("Done.") if verbose == 2 else ""

                    source.close()

                    ohns_codes = {
                        self.KEY_TO_OHNS: {'Codes': neutral_sections_codes, 'Notes': notes},
                        self.KEY_TO_LAST_UPDATED_DATE: last_updated_date,
                    }

                    path_to_pickle = make_pickle_pathname(self, data_name=self.KEY_TO_OHNS)
                    save_pickle(ohns_codes, path_to_pickle, verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(e))

            return ohns_codes

    def fetch_ohns_codes(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch codes for `overhead line electrification neutral sections
        <http://www.railwaycodes.org.uk/electrification/neutral.shtm>`_ (OHNS)
        from local backup.

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param pickle_it: whether to save the data as a pickle file, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of a folder where the pickle file is to be saved, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: OHNS codes
        :rtype: dict

        **Example**::

            >>> from pyrcs.line_data import Electrification
            >>> # from pyrcs import Electrification

            >>> elec = Electrification()

            >>> ohns_dat = elec.fetch_ohns_codes()

            >>> type(ohns_dat)
            dict
            >>> list(ohns_dat.keys())
            ['National network neutral sections', 'Last updated date']

            >>> elec.KEY_TO_OHNS
            'National network neutral sections'

            >>> ohns_data = ohns_dat[elec.KEY_TO_OHNS]
            >>> type(ohns_data)
            dict
            >>> list(ohns_data.keys())
            ['Codes', 'Notes']
            >>> ohns_data['Codes']
                  ELR          OHNS Name  ...     Tracks                             Dates
            0    ARG1         Rutherglen  ...
            1    ARG2    Finnieston East  ...       Down
            2    ARG2    Finnieston West  ...         Up
            3    AYR1   Shields Junction  ...     Up Ayr
            4    AYR1   Shields Junction  ...   Down Ayr
            ..    ...                ...  ...        ...                               ...
            488   WWD       Law Junction  ...
            489   WWD  Holytown Junction  ...                           Installed Octob...
            490   XRC          Royal Oak  ...  Westbound
            491   YKR              Yoker  ...             Installed ??, removed ≈11 Mar...
            492   YKR            Dalmuir  ...             Installed ??, removed ≈11 Mar...

            [493 rows x 5 columns]
        """

        path_to_pickle = make_pickle_pathname(self, data_name=self.KEY_TO_OHNS)

        if os.path.isfile(path_to_pickle) and not update:
            ohns_codes = load_pickle(path_to_pickle)

        else:
            ohns_codes = self.collect_ohns_codes(
                confirmation_required=False,
                verbose=collect_in_fetch_verbose(data_dir=data_dir, verbose=verbose))

            if ohns_codes is not None:
                data_to_pickle(
                    self, data=ohns_codes, data_name=self.KEY_TO_OHNS,
                    pickle_it=pickle_it, data_dir=data_dir, verbose=verbose)

            else:
                print_void_msg(data_name=self.KEY_TO_OHNS, verbose=verbose)
                ohns_codes = load_pickle(path_to_pickle)

        return ohns_codes

    def collect_etz_codes(self, confirmation_required=True, verbose=False):
        """
        Collect OLE section codes for `national network energy tariff zones
        <http://www.railwaycodes.org.uk/electrification/tariff.shtm>`_
        from source web page.

        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: OLE section codes for national network energy tariff zones
        :rtype: dict or None

        **Example**::

            >>> from pyrcs.line_data import Electrification
            >>> # from pyrcs import Electrification

            >>> elec = Electrification()

            >>> etz_ole_dat = elec.collect_etz_codes()
            To collect section codes for OLE installations: national network energy tariff zones
            ? [No]|Yes: yes

            >>> type(etz_ole_dat)
            dict
            >>> list(etz_ole_dat.keys())
            ['National network energy tariff zones', 'Last updated date']

            >>> elec.KEY_TO_ENERGY_TARIFF_ZONES
            'National network energy tariff zones'

            >>> tariff_zone_codes = etz_ole_dat[elec.KEY_TO_ENERGY_TARIFF_ZONES]
            >>> type(tariff_zone_codes)
            dict
            >>> list(tariff_zone_codes.keys())
            ['Railtrack', 'Network Rail']

            >>> tariff_zone_codes['Railtrack']['Codes']
               Code                   Energy tariff zone
            0    EA                          East Anglia
            1    EC                 East Coast Main Line
            2    GE                      Great Eastern †
            3    LT                                LTS †
            4    MD                    Midland Main Line
            5    ME                         Merseyside †
            6    MS  Merseyside (North West DC traction)
            7    NE                           North East
            8    NL           North London (DC traction)
            9    SC                             Scotland
            10   SO                                South
            11   SW                           South West
            12   WA                        West Anglia †
            13   WC                West Coast/North West
        """

        cfm_msg = self._cfm_msg(code_key=self.KEY_TO_ENERGY_TARIFF_ZONES)
        if confirmed(prompt=cfm_msg, confirmation_required=confirmation_required):

            print_collect_msg(
                data_name=self.KEY_TO_ENERGY_TARIFF_ZONES, verbose=verbose,
                confirmation_required=confirmation_required)

            etz_ole = None

            url = self.catalogue[self.KEY_TO_ENERGY_TARIFF_ZONES]

            try:
                source = requests.get(url=url, headers=fake_requests_headers(randomized=True))
            except requests.exceptions.ConnectionError:
                print("Failed. ") if verbose == 2 else ""
                print_conn_err(verbose=verbose)

            else:
                try:
                    etz_ole_ = self._collect_data(source=source)
                    source.close()

                    last_updated_date = get_last_updated_date(
                        url=self.catalogue[self.KEY_TO_ENERGY_TARIFF_ZONES])

                    if verbose == 2:
                        print("Done.")

                    etz_ole = {
                        self.KEY_TO_ENERGY_TARIFF_ZONES: etz_ole_,
                        self.KEY_TO_LAST_UPDATED_DATE: last_updated_date,
                    }

                    path_to_pickle = make_pickle_pathname(self, self.KEY_TO_ENERGY_TARIFF_ZONES)
                    save_pickle(etz_ole, path_to_pickle, verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(e))

            return etz_ole

    def fetch_etz_codes(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch OLE section codes for `national network energy tariff zones
        <http://www.railwaycodes.org.uk/electrification/tariff.shtm>`_
        from source web page.

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param pickle_it: whether to save the data as a pickle file, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of a folder where the pickle file is to be saved, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: OLE section codes for national network energy tariff zones
        :rtype: dict

        **Example**::

            >>> from pyrcs.line_data import Electrification
            >>> # from pyrcs import Electrification

            >>> elec = Electrification()

            >>> etz_ole_dat = elec.fetch_etz_codes()
            >>> type(etz_ole_dat)
            dict
            >>> list(etz_ole_dat.keys())
            ['National network energy tariff zones', 'Last updated date']

            >>> elec.KEY_TO_ENERGY_TARIFF_ZONES
            'National network energy tariff zones'

            >>> tariff_zone_codes = etz_ole_dat[elec.KEY_TO_ENERGY_TARIFF_ZONES]
            >>> type(tariff_zone_codes)
            dict
            >>> list(tariff_zone_codes.keys())
            ['Railtrack', 'Network Rail']

            >>> tariff_zone_codes['Railtrack']['Codes']
               Code                   Energy tariff zone
            0    EA                          East Anglia
            1    EC                 East Coast Main Line
            2    GE                      Great Eastern †
            3    LT                                LTS †
            4    MD                    Midland Main Line
            5    ME                         Merseyside †
            6    MS  Merseyside (North West DC traction)
            7    NE                           North East
            8    NL           North London (DC traction)
            9    SC                             Scotland
            10   SO                                South
            11   SW                           South West
            12   WA                        West Anglia †
            13   WC                West Coast/North West
        """

        path_to_pickle = make_pickle_pathname(self, data_name=self.KEY_TO_ENERGY_TARIFF_ZONES)

        if os.path.isfile(path_to_pickle) and not update:
            etz_ole = load_pickle(path_to_pickle)

        else:
            etz_ole = self.collect_etz_codes(
                confirmation_required=False,
                verbose=collect_in_fetch_verbose(data_dir=data_dir, verbose=verbose))

            if etz_ole is not None:
                data_to_pickle(
                    self, data=etz_ole, data_name=self.KEY_TO_ENERGY_TARIFF_ZONES,
                    pickle_it=pickle_it, data_dir=data_dir, verbose=verbose)

            else:
                print_void_msg(data_name=self.KEY_TO_ENERGY_TARIFF_ZONES, verbose=verbose)
                etz_ole = load_pickle(path_to_pickle)

        return etz_ole

    def fetch_elec_codes(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch OLE section codes in `electrification`_ catalogue.

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param pickle_it: whether to save the data as a pickle file, defaults to ``False``
        :type pickle_it: bool
        :param data_dir: name of a folder where the pickle file is to be saved, defaults to ``None``
        :type data_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: section codes for overhead line electrification (OLE) installations
        :rtype: dict

        .. _`electrification`: http://www.railwaycodes.org.uk/electrification/mast_prefix0.shtm

        **Example**::

            >>> from pyrcs.line_data import Electrification
            >>> # from pyrcs import Electrification

            >>> elec = Electrification()

            >>> electrification_data = elec.fetch_elec_codes()
            >>> type(electrification_data)
            dict
            >>> list(electrification_data.keys())
            ['Electrification', 'Last updated date']

            >>> elec.KEY
            'Electrification'

            >>> electrification_codes = electrification_data[elec.KEY]
            >>> type(electrification_codes)
            dict
            >>> list(electrification_codes.keys())
            ['National network energy tariff zones',
             'Independent lines',
             'National network',
             'National network neutral sections']
        """

        verbose_ = fetch_all_verbose(data_dir=data_dir, verbose=verbose)

        codes = []
        for func in dir(self):
            if func.startswith('fetch_') and func != 'fetch_elec_codes':
                codes.append(getattr(self, func)(update=update, verbose=verbose_))

        ole_section_codes = {
            self.KEY: {next(iter(x)): next(iter(x.values())) for x in codes},
            self.KEY_TO_LAST_UPDATED_DATE: max(
                next(itertools.islice(iter(x.values()), 1, 2)) for x in codes),
        }

        data_to_pickle(
            self, data=ole_section_codes, data_name=self.KEY,
            pickle_it=pickle_it, data_dir=data_dir, verbose=verbose)

        return ole_section_codes
