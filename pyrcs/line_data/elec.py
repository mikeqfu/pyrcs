"""
Collect `section codes for overhead line electrification (OLE) installations
<http://www.railwaycodes.org.uk/electrification/mast_prefix0.shtm>`_.
"""

import itertools

from pyhelpers.dir import cd

from ..parser import *
from ..utils import *


def _collect_notes(h3):
    notes_ = []

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
    # h3 = h3.find_next('h3')
    sub_heading = get_heading_text(heading_tag=h3, elem_tag_name='em')

    notes = _collect_notes(h3=h3)

    data = {sub_heading: {'Codes': None, 'Notes': notes}}

    return data


def _collect_list_only(h3, ul):
    sub_heading = get_heading_text(heading_tag=h3, elem_tag_name='em')

    list_data = [get_hypertext(x) for x in ul.findChildren('li')]
    notes = _collect_notes(h3).strip().replace(' were:', '.')

    codes_with_list = {sub_heading: {'Codes': list_data, 'Notes': notes}}

    return codes_with_list


def _collect_codes_with_list(h3, ul):
    """
    'Blackpool Tramway',
    """

    sub_heading = get_heading_text(heading_tag=h3, elem_tag_name='em')

    data_1_key, data_2_key = 'Section codes', 'Known prefixes'
    table_1, table_2 = {data_1_key: None}, {data_2_key: None}

    # data_1
    table_1[data_1_key] = pd.DataFrame(
        data=[re.sub(r'[()]', '', x.text).split(' ', 1) for x in ul.findChildren('li')],
        columns=['Code', 'Area'])

    # data_2
    thead, tbody = h3.find_next('thead'), h3.find_next('tbody')
    ths, trs = [th.text for th in thead.find_all('th')], tbody.find_all('tr')
    dat_2 = parse_tr(trs=trs, ths=ths, as_dataframe=True)

    table_2[data_2_key] = dat_2

    # Notes
    notes = _collect_notes(h3)

    codes_with_list = {sub_heading: {**table_1, **table_2, 'Notes': notes}}

    return codes_with_list


def _collect_codes_and_notes(h3):
    """
    elec = Electrification()

    url = elec.catalogue[elec.KEY_TO_INDEPENDENT_LINES]
    source = requests.get(url=url, headers=fake_requests_headers())
    soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

    h3 = soup.find('h3')

    h3 = h3.find_next('h3')
    """

    codes_and_notes = None

    _, ul, table = h3.find_next(name='p'), h3.find_next(name='ul'), h3.find_next(name='table')

    if ul is not None:
        if ul.find_previous('h3') == h3:
            if table is not None:
                codes_and_notes = _collect_codes_with_list(h3=h3, ul=ul)
            else:
                codes_and_notes = _collect_list_only(h3=h3, ul=ul)

    if table is not None and codes_and_notes is None:
        if table.find_previous(name='h3') == h3:
            h3_ = table.find_previous(name='h3')
            codes = None
            thead, tbody = table.find_next(name='thead'), table.find_next(name='tbody')

            while h3_ == h3:
                ths, trs = [x.text for x in thead.find_all('th')], tbody.find_all('tr')
                dat = parse_tr(trs=trs, ths=ths, as_dataframe=True)
                codes_ = dat.applymap(
                    lambda x: re.sub(
                        pattern=r'\']\)?', repl=']',
                        string=re.sub(r'\(?\[\'', '[', x)).replace(
                        '\\xa0', '').replace('\r ', ' ').strip())

                codes = codes_ if codes is None else [codes, codes_]

                thead, tbody = thead.find_next(name='thead'), tbody.find_next(name='tbody')

                if tbody is None:
                    break
                else:
                    h3_ = tbody.find_previous(name='h3')

            notes = _collect_notes(h3=h3)

            sub_heading = get_heading_text(heading_tag=h3, elem_tag_name='em')
            codes_and_notes = {sub_heading: {'Codes': codes, 'Notes': notes}}

    if codes_and_notes is None:
        codes_and_notes = _collect_codes_without_list(h3=h3)

    return codes_and_notes


class Electrification:
    """
    A class for collecting `section codes for overhead line electrification (OLE) installations`_.

    .. _`section codes for overhead line electrification (OLE) installations`:
        http://www.railwaycodes.org.uk/electrification/mast_prefix0.shtm
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

        :ivar dict catalogue: catalogue of the data
        :ivar str last_updated_date: last update date
        :ivar str data_dir: path to the data directory
        :ivar str current_data_dir: path to the current data directory

        **Examples**::

            >>> from pyrcs.line_data import Electrification  # from pyrcs import Electrification

            >>> elec = Electrification()

            >>> print(elec.NAME)
            Section codes for overhead line electrification (OLE) installations

            >>> print(elec.URL)
            http://www.railwaycodes.org.uk/electrification/mast_prefix0.shtm
        """

        print_conn_err(verbose=verbose)

        self.catalogue = get_catalogue(url=self.URL, update=update, confirmation_required=False)

        self.last_updated_date = get_last_updated_date(url=self.URL)

        self.data_dir, self.current_data_dir = init_data_dir(self, data_dir, category="line-data")

    def _cdd(self, *sub_dir, **kwargs):
        """
        Change directory to package data directory and subdirectories (and/or a file).

        The directory for this module: ``"data\\line-data\\electrification"``.

        :param sub_dir: subdirectory or subdirectories (and/or a file)
        :type sub_dir: str
        :param kwargs: [optional] parameters of the function `pyhelpers.dir.cd`_
        :return: path to the backup data directory for the class
            :py:class:`~pyrcs.line_data.elec.Electrification`
        :rtype: str

        .. _`pyhelpers.dir.cd`:
            https://pyhelpers.readthedocs.io/en/latest/_generated/pyhelpers.dir.cd.html
        """

        path = cd(self.data_dir, *sub_dir, mkdir=True, **kwargs)

        return path

    @staticmethod
    def _cfm_msg(key):
        cfm_msg = "To collect section codes for OLE installations: {}\n?".format(key.lower())

        return cfm_msg

    @staticmethod
    def _collect_data(source):
        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

        data = {}
        h3 = soup.find('h3')
        while h3:
            data_ = _collect_codes_and_notes(h3=h3)

            if data_ is not None:
                data.update(data_)

            h3 = h3.find_next('h3')

        source.close()

        return data

    def collect_national_network_codes(self, confirmation_required=True, verbose=False):
        """
        Collect OLE section codes for
        `national network <http://www.railwaycodes.org.uk/electrification/mast_prefix1.shtm>`_
        from source web page.

        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: OLE section codes for National network
        :rtype: dict or None

        **Examples**::

            >>> from pyrcs.line_data import Electrification  # from pyrcs import Electrification

            >>> elec = Electrification()

            >>> nn_codes = elec.collect_national_network_codes()
            To collect section codes for OLE installations: national network
            ? [No]|Yes: yes
            >>> type(nn_codes)
            dict
            >>> list(nn_codes.keys())
            ['National network', 'Last updated date']

            >>> elec.KEY_TO_NATIONAL_NETWORK
            'National network'

            >>> nn_codes_dat = nn_codes[elec.KEY_TO_NATIONAL_NETWORK]
            >>> type(nn_codes_dat)
            dict
            >>> list(nn_codes_dat.keys())
            ['Traditional numbering system [distance and sequence]',
             'New numbering system [km and decimal]',
             'Codes not certain [confirmation is welcome]',
             'Suspicious data',
             'An odd one to complete the record',
             'LBSC/Southern Railway overhead system',
             'Codes not known']

            >>> tns_codes = nn_codes_dat['Traditional numbering system [distance and sequence]']
            >>> type(tns_codes)
            dict
            >>> list(tns_codes.keys())
            ['Codes', 'Notes']
            >>> tns_codes_dat = tns_codes['Codes']
            >>> tns_codes_dat.head()
              Code  ...                          Datum
            0    A  ...               Fenchurch Street
            1    A  ...             Newbridge Junction
            2    A  ...               Fenchurch Street
            3    A  ...  Guide Bridge Station Junction
            4   AB  ...

            [5 rows x 4 columns]
        """

        cfm_msg = self._cfm_msg(self.KEY_TO_NATIONAL_NETWORK)
        if confirmed(prompt=cfm_msg, confirmation_required=confirmation_required):

            print_collect_msg(
                data_name=self.KEY_TO_NATIONAL_NETWORK, verbose=verbose,
                confirmation_required=confirmation_required)

            national_network_ole = None

            try:
                url = self.catalogue[self.KEY_TO_NATIONAL_NETWORK]
                source = requests.get(url=url, headers=fake_requests_headers())

            except Exception as e:
                if verbose == 2:
                    print("Failed. ", end="")
                print_inst_conn_err(verbose=verbose, e=e)

            else:
                try:
                    national_network_ole_ = self._collect_data(source=source)

                    source.close()

                    last_updated_date = get_last_updated_date(url=url)

                    national_network_ole = {
                        self.KEY_TO_NATIONAL_NETWORK: national_network_ole_,
                        self.KEY_TO_LAST_UPDATED_DATE: last_updated_date,
                    }

                    if verbose == 2:
                        print("Done.")

                    save_data_to_file(
                        self, data=national_network_ole, data_name=self.KEY_TO_NATIONAL_NETWORK,
                        ext=".pickle", verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(e))

            return national_network_ole

    def fetch_national_network_codes(self, update=False, dump_dir=None, verbose=False):
        """
        Fetch OLE section codes for `national network`_.

        .. _`national network`: http://www.railwaycodes.org.uk/electrification/mast_prefix1.shtm

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param dump_dir: pathname of a directory where the data file is dumped, defaults to ``None``
        :type dump_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: OLE section codes for National network
        :rtype: dict or None

        **Examples**::

            >>> from pyrcs.line_data import Electrification  # from pyrcs import Electrification

            >>> elec = Electrification()

            >>> nn_codes = elec.fetch_national_network_codes()
            >>> type(nn_codes)
            dict
            >>> list(nn_codes.keys())
            ['National network', 'Last updated date']

            >>> elec.KEY_TO_NATIONAL_NETWORK
            'National network'

            >>> nn_codes_dat = nn_codes[elec.KEY_TO_NATIONAL_NETWORK]
            >>> type(nn_codes_dat)
            dict
            >>> list(nn_codes_dat.keys())
            ['Traditional numbering system [distance and sequence]',
             'New numbering system [km and decimal]',
             'Codes not certain [confirmation is welcome]',
             'Suspicious data',
             'An odd one to complete the record',
             'LBSC/Southern Railway overhead system',
             'Codes not known']

            >>> tns_codes = nn_codes_dat['Traditional numbering system [distance and sequence]']
            >>> type(tns_codes)
            dict
            >>> list(tns_codes.keys())
            ['Codes', 'Notes']
            >>> tns_codes_dat = tns_codes['Codes']
            >>> tns_codes_dat.head()
              Code  ...                          Datum
            0    A  ...               Fenchurch Street
            1    A  ...             Newbridge Junction
            2    A  ...               Fenchurch Street
            3    A  ...  Guide Bridge Station Junction
            4   AB  ...

            [5 rows x 4 columns]
        """

        national_network_ole = fetch_data_from_file(
            cls=self, method='collect_national_network_codes', data_name=self.KEY_TO_NATIONAL_NETWORK,
            ext=".pickle", update=update, dump_dir=dump_dir, verbose=verbose)

        return national_network_ole

    def get_indep_line_catalogue(self, update=False, verbose=False):
        """
        Get a catalogue for
        `independent lines <http://www.railwaycodes.org.uk/electrification/mast_prefix2.shtm>`_.

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: a list of independent line names
        :rtype: pandas.DataFrame

        **Examples**::

            >>> from pyrcs.line_data import Electrification  # from pyrcs import Electrification
            >>> from pyhelpers.settings import pd_preferences

            >>> pd_preferences(max_columns=1)

            >>> elec = Electrification()

            >>> indep_line_cat = elec.get_indep_line_catalogue()
            >>> indep_line_cat.head()
                                                         Feature  ...
            0                                    Beamish Tramway  ...
            1                                 Birkenhead Tramway  ...
            2                        Black Country Living Museum  ...
            3                                  Blackpool Tramway  ...
            4  Brighton and Rottingdean Seashore Electric Rai...  ...

            [5 rows x 3 columns]
        """

        data_name = "electrification-independent-lines"
        ext = ".pickle"
        path_to_file = cd_data("catalogue", data_name + ext)

        if os.path.isfile(path_to_file) and not update:
            indep_line_names = load_data(path_to_file)

        else:
            indep_line_names = get_page_catalogue(
                url=self.catalogue[self.KEY_TO_INDEPENDENT_LINES],
                head_tag_name='nav', head_tag_txt='Jump to: ', feature_tag_name='h3',
                verbose=verbose)

            # if bool(indep_line_names):
            #     save_data(indep_line_names, path_to_file, verbose=verbose)
            save_data_to_file(
                self, data=indep_line_names, data_name=data_name, ext=ext, dump_dir=cd_data("catalogue"),
                verbose=verbose)

        return indep_line_names

    def collect_indep_lines_codes(self, confirmation_required=True, verbose=False):
        """
        Collect OLE section codes for `independent lines`_ from source web page.

        .. _`independent lines`: http://www.railwaycodes.org.uk/electrification/mast_prefix2.shtm

        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: OLE section codes for independent lines
        :rtype: dict or None

        **Examples**::

            >>> from pyrcs.line_data import Electrification  # from pyrcs import Electrification

            >>> elec = Electrification()

            >>> indep_lines_codes = elec.collect_indep_lines_codes()
            To collect section codes for OLE installations: independent lines
            ? [No]|Yes: yes
            >>> type(indep_lines_codes)
            dict
            >>> list(indep_lines_codes.keys())
            ['Independent lines', 'Last updated date']

            >>> elec.KEY_TO_INDEPENDENT_LINES
            'Independent lines'

            >>> indep_lines_codes_dat = indep_lines_codes[elec.KEY_TO_INDEPENDENT_LINES]
            >>> type(indep_lines_codes_dat)
            dict
            >>> len(indep_lines_codes_dat)
            22
            >>> list(indep_lines_codes_dat.keys())
            ['Beamish Tramway',
             'Birkenhead Tramway',
             'Black Country Living Museum [Tipton]',
             'Blackpool Tramway',
             "Brighton and Rottingdean Seashore Electric Railway [Magnus Volk's 'Daddy Long Legs'...
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

            >>> indep_lines_codes_dat['Beamish Tramway']
            {'Codes': None, 'Notes': 'Masts do not appear labelled.'}
        """

        cfm_msg = self._cfm_msg(key=self.KEY_TO_INDEPENDENT_LINES)
        if confirmed(prompt=cfm_msg, confirmation_required=confirmation_required):

            print_collect_msg(
                data_name=self.KEY_TO_INDEPENDENT_LINES, verbose=verbose,
                confirmation_required=confirmation_required)

            independent_lines_ole = None

            try:
                url = self.catalogue[self.KEY_TO_INDEPENDENT_LINES]
                source = requests.get(url=url, headers=fake_requests_headers())

            except Exception as e:
                if verbose == 2:
                    print("Failed. ", end="")
                print_inst_conn_err(verbose=verbose, e=e)

            else:
                try:
                    independent_lines_ole_ = self._collect_data(source=source)

                    last_updated_date = get_last_updated_date(url=url)

                    independent_lines_ole = {
                        self.KEY_TO_INDEPENDENT_LINES: independent_lines_ole_,
                        self.KEY_TO_LAST_UPDATED_DATE: last_updated_date,
                    }

                    if verbose == 2:
                        print("Done.")

                    save_data_to_file(
                        self, data=independent_lines_ole, data_name=self.KEY_TO_INDEPENDENT_LINES,
                        ext=".pickle", verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(e))

            return independent_lines_ole

    def fetch_indep_lines_codes(self, update=False, dump_dir=None, verbose=False):
        """
        Fetch OLE section codes for `independent lines`_.

        .. _`independent lines`: http://www.railwaycodes.org.uk/electrification/mast_prefix2.shtm

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param dump_dir: pathname of a directory where the data file is dumped, defaults to ``None``
        :type dump_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: OLE section codes for independent lines
        :rtype: dict

        **Examples**::

            >>> from pyrcs.line_data import Electrification  # from pyrcs import Electrification

            >>> elec = Electrification()

            >>> indep_lines_codes = elec.fetch_indep_lines_codes()
            >>> type(indep_lines_codes)
            dict
            >>> list(indep_lines_codes.keys())
            ['Independent lines', 'Last updated date']

            >>> elec.KEY_TO_INDEPENDENT_LINES
            'Independent lines'

            >>> indep_lines_codes_dat = indep_lines_codes[elec.KEY_TO_INDEPENDENT_LINES]
            >>> type(indep_lines_codes_dat)
            dict
            >>> len(indep_lines_codes_dat)
            22
            >>> list(indep_lines_codes_dat.keys())
            ['Beamish Tramway',
             'Birkenhead Tramway',
             'Black Country Living Museum [Tipton]',
             'Blackpool Tramway',
             "Brighton and Rottingdean Seashore Electric Railway [Magnus Volk's 'Daddy Long Legs'...
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

            >>> indep_lines_codes_dat['Beamish Tramway']
            {'Codes': None, 'Notes': 'Masts do not appear labelled.'}
        """

        independent_lines_ole = fetch_data_from_file(
            cls=self, method='collect_indep_lines_codes', data_name=self.KEY_TO_INDEPENDENT_LINES,
            ext=".pickle", update=update, dump_dir=dump_dir, verbose=verbose)

        return independent_lines_ole

    def collect_ohns_codes(self, confirmation_required=True, verbose=False):
        """
        Collect codes for
        `overhead line electrification neutral sections
        <http://www.railwaycodes.org.uk/electrification/neutral.shtm>`_ (OHNS)
        from source web page.

        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: OHNS codes
        :rtype: dict or None

        **Examples**::

            >>> from pyrcs.line_data import Electrification  # from pyrcs import Electrification

            >>> elec = Electrification()

            >>> ohl_ns_codes = elec.collect_ohns_codes()
            To collect section codes for OLE installations: national network neutral sections
            ? [No]|Yes: yes

            >>> type(ohl_ns_codes)
            dict
            >>> list(ohl_ns_codes.keys())
            ['National network neutral sections', 'Last updated date']

            >>> elec.KEY_TO_OHNS
            'National network neutral sections'

            >>> ohl_ns_codes_dat = ohl_ns_codes[elec.KEY_TO_OHNS]
            >>> type(ohl_ns_codes_dat)
            dict
            >>> list(ohl_ns_codes_dat.keys())
            ['Codes', 'Notes']
            >>> ohl_ns_codes_dat['Codes']
                  ELR          OHNS Name  ...     Tracks                                 Dates
            0    ARG1         Rutherglen  ...
            1    ARG2    Finnieston East  ...       Down
            2    ARG2    Finnieston West  ...         Up
            3    AYR1   Shields Junction  ...     Up Ayr
            4    AYR1   Shields Junction  ...   Down Ayr
            ..    ...                ...  ...        ...                                   ...
            436   WWD       Law Junction  ...
            437   WWD  Holytown Junction  ...                           Installed October 2018
            438   XRC          Royal Oak  ...  Westbound
            439   YKR              Yoker  ...             Installed ??, removed ≈11 March 1979
            440   YKR            Dalmuir  ...             Installed ??, removed ≈11 March 1979

            [441 rows x 5 columns]
        """

        cfm_msg = self._cfm_msg(key=self.KEY_TO_OHNS)
        if confirmed(prompt=cfm_msg, confirmation_required=confirmation_required):

            print_collect_msg(
                data_name=self.KEY_TO_OHNS, verbose=verbose,
                confirmation_required=confirmation_required)

            ohns_codes = None

            try:
                url = self.catalogue[self.KEY_TO_OHNS]
                # header, neutral_sections_codes = pd.read_html(io=url)
                # neutral_sections_data.columns = header.columns.to_list()
                # neutral_sections_data.fillna('', inplace=True)
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
                    tbl = parse_tr(trs=trs, ths=ths)

                    delimiter = ',\t'

                    records = [[x.replace('\r (', delimiter).replace(" (['", delimiter).replace(
                        "'])", '').replace('\r', delimiter).replace("', '", delimiter).replace(
                        ' &ap;', '≈').strip(')') for x in dat]
                        for dat in tbl]

                    row_bak = records.copy()
                    for row in row_bak:
                        tracks, dates = row[3].split(delimiter), row[4].split(delimiter)
                        if len(tracks) > 1 and len(dates) > 1:
                            i = j = records.index(row)
                            for trk, date in zip(tracks, dates):
                                records.insert(i + 1, row[0:3] + [trk, date])
                                i += 1
                            del records[j]

                    neutral_sections_codes = pd.DataFrame(data=records, columns=ths)

                    notes = soup.find(name='div', attrs={'class': 'background'}).find_all(name='p')
                    notes = '\n'.join([txt.text for txt in notes]).replace('  ', ' ')

                    last_updated_date = get_last_updated_date(url=url)

                    ohns_codes = {
                        self.KEY_TO_OHNS: {'Codes': neutral_sections_codes, 'Notes': notes},
                        self.KEY_TO_LAST_UPDATED_DATE: last_updated_date,
                    }

                    if verbose == 2:
                        print("Done.")

                    save_data_to_file(
                        self, data=ohns_codes, data_name=self.KEY_TO_OHNS, ext=".pickle",
                        verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(e))

            return ohns_codes

    def fetch_ohns_codes(self, update=False, dump_dir=None, verbose=False):
        """
        Fetch codes for `overhead line electrification neutral sections`_ (OHNS).

        .. _`overhead line electrification neutral sections`:
            http://www.railwaycodes.org.uk/electrification/neutral.shtm

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param dump_dir: pathname of a directory where the data file is dumped, defaults to ``None``
        :type dump_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: OHNS codes
        :rtype: dict

        **Examples**::

            >>> from pyrcs.line_data import Electrification  # from pyrcs import Electrification

            >>> elec = Electrification()

            >>> ohl_ns_codes = elec.fetch_ohns_codes()

            >>> type(ohl_ns_codes)
            dict
            >>> list(ohl_ns_codes.keys())
            ['National network neutral sections', 'Last updated date']

            >>> elec.KEY_TO_OHNS
            'National network neutral sections'

            >>> ohl_ns_codes_dat = ohl_ns_codes[elec.KEY_TO_OHNS]
            >>> type(ohl_ns_codes_dat)
            dict
            >>> list(ohl_ns_codes_dat.keys())
            ['Codes', 'Notes']
            >>> ohl_ns_codes_dat['Codes']
                  ELR          OHNS Name  ...     Tracks                                 Dates
            0    ARG1         Rutherglen  ...
            1    ARG2    Finnieston East  ...       Down
            2    ARG2    Finnieston West  ...         Up
            3    AYR1   Shields Junction  ...     Up Ayr
            4    AYR1   Shields Junction  ...   Down Ayr
            ..    ...                ...  ...        ...                                   ...
            436   WWD       Law Junction  ...
            437   WWD  Holytown Junction  ...                           Installed October 2018
            438   XRC          Royal Oak  ...  Westbound
            439   YKR              Yoker  ...             Installed ??, removed ≈11 March 1979
            440   YKR            Dalmuir  ...             Installed ??, removed ≈11 March 1979

            [441 rows x 5 columns]
        """

        ohns_codes = fetch_data_from_file(
            cls=self, method='collect_ohns_codes', data_name=self.KEY_TO_OHNS, ext=".pickle",
            update=update, dump_dir=dump_dir, verbose=verbose)

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

        **Examples**::

            >>> from pyrcs.line_data import Electrification  # from pyrcs import Electrification

            >>> elec = Electrification()

            >>> rail_etz_codes = elec.collect_etz_codes()
            To collect section codes for OLE installations: national network energy tariff zones
            ? [No]|Yes: yes

            >>> type(rail_etz_codes)
            dict
            >>> list(rail_etz_codes.keys())
            ['National network energy tariff zones', 'Last updated date']

            >>> elec.KEY_TO_ENERGY_TARIFF_ZONES
            'National network energy tariff zones'

            >>> rail_etz_codes_dat = rail_etz_codes[elec.KEY_TO_ENERGY_TARIFF_ZONES]
            >>> type(rail_etz_codes_dat)
            dict
            >>> list(rail_etz_codes_dat.keys())
            ['Railtrack', 'Network Rail']

            >>> rail_etz_codes_dat['Railtrack']['Codes']
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

        cfm_msg = self._cfm_msg(key=self.KEY_TO_ENERGY_TARIFF_ZONES)
        if confirmed(prompt=cfm_msg, confirmation_required=confirmation_required):

            print_collect_msg(
                data_name=self.KEY_TO_ENERGY_TARIFF_ZONES, verbose=verbose,
                confirmation_required=confirmation_required)

            etz_ole = None

            url = self.catalogue[self.KEY_TO_ENERGY_TARIFF_ZONES]

            try:
                source = requests.get(url=url, headers=fake_requests_headers())

            except Exception as e:
                if verbose == 2:
                    print("Failed. ", end="")
                print_inst_conn_err(verbose=verbose, e=e)

            else:
                try:
                    etz_ole_ = self._collect_data(source=source)

                    last_updated_date = get_last_updated_date(url=url)

                    etz_ole = {
                        self.KEY_TO_ENERGY_TARIFF_ZONES: etz_ole_,
                        self.KEY_TO_LAST_UPDATED_DATE: last_updated_date,
                    }

                    if verbose == 2:
                        print("Done.")

                    save_data_to_file(
                        self, data=etz_ole, data_name=self.KEY_TO_ENERGY_TARIFF_ZONES, ext=".pickle",
                        verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(e))

            return etz_ole

    def fetch_etz_codes(self, update=False, dump_dir=None, verbose=False):
        """
        Fetch OLE section codes for `national network energy tariff zones`_.

        .. _`national network energy tariff zones`:
            http://www.railwaycodes.org.uk/electrification/tariff.shtm

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param dump_dir: pathname of a directory where the data file is dumped, defaults to ``None``
        :type dump_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: OLE section codes for national network energy tariff zones
        :rtype: dict

        **Examples**::

            >>> from pyrcs.line_data import Electrification  # from pyrcs import Electrification

            >>> elec = Electrification()

            >>> rail_etz_codes = elec.fetch_etz_codes()
            >>> type(rail_etz_codes)
            dict
            >>> list(rail_etz_codes.keys())
            ['National network energy tariff zones', 'Last updated date']

            >>> elec.KEY_TO_ENERGY_TARIFF_ZONES
            'National network energy tariff zones'

            >>> rail_etz_codes_dat = rail_etz_codes[elec.KEY_TO_ENERGY_TARIFF_ZONES]
            >>> type(rail_etz_codes_dat)
            dict
            >>> list(rail_etz_codes_dat.keys())
            ['Railtrack', 'Network Rail']

            >>> rail_etz_codes_dat['Railtrack']['Codes']
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

        etz_ole = fetch_data_from_file(
            cls=self, method='collect_etz_codes', data_name=self.KEY_TO_ENERGY_TARIFF_ZONES,
            ext=".pickle", update=update, dump_dir=dump_dir, verbose=verbose)

        return etz_ole

    def fetch_codes(self, update=False, dump_dir=None, verbose=False):
        """
        Fetch OLE section codes listed in the `Electrification`_ catalogue.

        .. _`Electrification`: http://www.railwaycodes.org.uk/electrification/mast_prefix0.shtm

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param dump_dir: pathname of a directory where the data file is dumped, defaults to ``None``
        :type dump_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: section codes for overhead line electrification (OLE) installations
        :rtype: dict

        **Examples**::

            >>> from pyrcs.line_data import Electrification  # from pyrcs import Electrification

            >>> elec = Electrification()

            >>> elec_codes = elec.fetch_codes()
            >>> type(elec_codes)
            dict
            >>> list(elec_codes.keys())
            ['Electrification', 'Last updated date']

            >>> elec.KEY
            'Electrification'

            >>> elec_codes_dat = elec_codes[elec.KEY]
            >>> type(elec_codes_dat)
            dict
            >>> list(elec_codes_dat.keys())
            ['National network energy tariff zones',
             'Independent lines',
             'National network',
             'National network neutral sections']
        """

        verbose_ = fetch_all_verbose(data_dir=dump_dir, verbose=verbose)

        codes = []
        for func in dir(self):
            if func.startswith('fetch_') and func != 'fetch_codes':
                codes.append(getattr(self, func)(update=update, verbose=verbose_))

        ole_section_codes = {
            self.KEY: {next(iter(x)): next(iter(x.values())) for x in codes},
            self.KEY_TO_LAST_UPDATED_DATE:
                max(next(itertools.islice(iter(x.values()), 1, 2)) for x in codes),
        }

        if dump_dir is not None:
            save_data_to_file(
                self, data=ole_section_codes, data_name=self.KEY, ext=".pickle", dump_dir=dump_dir,
                verbose=verbose)

        return ole_section_codes
