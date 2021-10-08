"""
Collect `section codes for overhead line electrification (OLE) installations
<http://www.railwaycodes.org.uk/electrification/mast_prefix0.shtm>`_.
"""

import copy
import urllib.error
import urllib.parse

from pyhelpers.dir import cd, validate_input_data_dir

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

    url = elec.Catalogue[elec.IndependentLinesKey]
    source = requests.get(url=url, headers=fake_requests_headers(randomized=True))
    soup = bs4.BeautifulSoup(markup=source.text, features='lxml')

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

    :param data_dir: name of data directory, defaults to ``None``
    :type data_dir: str or None
    :param update: whether to do an update check (for the package data), defaults to ``False``
    :type update: bool
    :param verbose: whether to print relevant information in console, defaults to ``True``
    :type verbose: bool or int

    :ivar str Name: name of the data
    :ivar str Key: key of the dict-type data
    :ivar str HomeURL: URL of the main homepage
    :ivar str SourceURL: URL of the data web page
    :ivar str LUDKey: key of the last updated date
    :ivar str LUD: last updated date
    :ivar dict Catalogue: catalogue of the data
    :ivar str DataDir: path to the data directory
    :ivar str CurrentDataDir: path to the current data directory

    :ivar str NationalNetworkKey: key of the dict-type data of national network
    :ivar str NationalNetworkPickle: name of the pickle file of national network data
    :ivar str IndependentLinesKey: key of the dict-type data of independent lines
    :ivar str IndependentLinesPickle: name of the pickle file of independent lines data
    :ivar str OhnsKey: key of the dict-type data of OHNS
    :ivar str OhnsPickle: name of the pickle file of OHNS data
    :ivar str TariffZonesKey: key of the dict-type data of tariff zones
    :ivar str TariffZonesPickle: name of the pickle file of tariff zones data

    **Example**::

        >>> # from pyrcs import Electrification
        >>> from pyrcs.line_data import Electrification

        >>> elec = Electrification()

        >>> print(elec.Name)
        Electrification masts and related features

        >>> print(elec.SourceURL)
        http://www.railwaycodes.org.uk/electrification/mast_prefix0.shtm
    """

    def __init__(self, data_dir=None, update=False, verbose=True):
        """
        Constructor method.
        """
        if not is_internet_connected():
            print_connection_error(verbose=verbose)

        self.Name = 'Electrification masts and related features'  #: Name of data category
        self.Key = 'Electrification'

        self.HomeURL = homepage_url()  #: URL to the homepage
        self.SourceURL = urllib.parse.urljoin(self.HomeURL, '/electrification/mast_prefix0.shtm')

        self.LUDKey = 'Last updated date'  #: Key to last updated date
        self.LUD = get_last_updated_date(url=self.SourceURL, parsed=True, as_date_type=False)

        self.Catalogue = get_catalogue(
            url=self.SourceURL, update=update, confirmation_required=False)

        if data_dir:
            self.DataDir = validate_input_data_dir(data_dir)
        else:
            self.DataDir = _cd_dat("line-data", self.Key.lower().replace(" ", "-"))
        self.CurrentDataDir = copy.copy(self.DataDir)

        self.NationalNetworkKey = 'National network'
        self.NationalNetworkPickle = self.NationalNetworkKey.lower().replace(" ", "-")
        self.IndependentLinesKey = 'Independent lines'
        self.IndependentLinesPickle = self.IndependentLinesKey.lower().replace(" ", "-")
        self.OhnsKey = 'National network neutral sections'
        self.OhnsPickle = self.OhnsKey.lower().replace(" ", "-")
        self.TariffZonesKey = 'National network energy tariff zones'
        self.TariffZonesPickle = self.TariffZonesKey.lower().replace(" ", "-")

    def _cdd_elec(self, *sub_dir, **kwargs):
        """
        Change directory to package data directory and sub-directories (and/or a file).

        The directory for this module: ``"dat\\line-data\\electrification"``.

        :param sub_dir: sub-directory or sub-directories (and/or a file)
        :type sub_dir: str
        :param kwargs: optional parameters of `pyhelpers.dir.cd`_
        :return: path to the backup data directory for the class ``Electrification``
        :rtype: str

        .. _pyhelpers.dir.cd:
            https://pyhelpers.readthedocs.io/en/latest/_generated/pyhelpers.dir.cd.html
        """

        path = cd(self.DataDir, *sub_dir, mkdir=True, **kwargs)

        return path

    @staticmethod
    def _collect_data(source):
        soup = bs4.BeautifulSoup(markup=source.text, features='lxml')

        data = {}
        h3 = soup.find('h3')
        while h3:
            data_ = _collect_codes_and_notes(h3=h3)

            if data_ is not None:
                data.update(data_)

            h3 = h3.find_next('h3')

        return data

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

            >>> # from pyrcs import Electrification
            >>> from pyrcs.line_data import Electrification

            >>> elec = Electrification()

            >>> nn_dat = elec.collect_national_network_codes()
            To collect section codes for OLE installations: national network
            ? [No]|Yes: yes

            >>> type(nn_dat)
            dict
            >>> list(nn_dat.keys())
            ['National network', 'Last updated date']

            >>> elec.NationalNetworkKey
            'National network'

            >>> nn_codes = nn_dat[elec.NationalNetworkKey]
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
            546         YW  ...   Camden Road Central Junction
            547          0  ...                    Kings Cross
            548          1  ...                    Kings Cross
            549  no prefix  ...                     Manchester
            550  no prefix  ...

            [551 rows x 4 columns]
        """

        if confirmed("To collect section codes for OLE installations: {}\n?".format(
                self.NationalNetworkKey.lower()),
                confirmation_required=confirmation_required):

            national_network_ole = None

            if verbose == 2:
                print("Collecting the codes for {}".format(self.NationalNetworkKey.lower()),
                      end=" ... ")

            url = self.Catalogue[self.NationalNetworkKey]

            try:
                source = requests.get(url=url, headers=fake_requests_headers(randomized=True))
            except requests.exceptions.ConnectionError:
                print("Failed. ") if verbose == 2 else ""
                print_conn_err(verbose=verbose)

            else:
                try:
                    national_network_ole_ = self._collect_data(source=source)

                    # soup = bs4.BeautifulSoup(markup=source.text, features='lxml')

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
                        self.NationalNetworkKey: national_network_ole_,
                        self.LUDKey: last_updated_date,
                    }

                    print("Done.") if verbose == 2 else ""

                    path_to_pickle = self._cdd_elec(self.NationalNetworkPickle + ".pickle")
                    save_pickle(national_network_ole, path_to_pickle, verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(e))

            return national_network_ole

    def fetch_national_network_codes(self, update=False, pickle_it=False, data_dir=None,
                                     verbose=False):
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

            >>> # from pyrcs import Electrification
            >>> from pyrcs.line_data import Electrification

            >>> elec = Electrification()

            >>> nn_dat = elec.fetch_national_network_codes()
            >>> type(nn_dat)
            dict
            >>> list(nn_dat.keys())
            ['National network', 'Last updated date']

            >>> elec.NationalNetworkKey
            'National network'

            >>> nn_codes = nn_dat[elec.NationalNetworkKey]
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
            546         YW  ...   Camden Road Central Junction
            547          0  ...                    Kings Cross
            548          1  ...                    Kings Cross
            549  no prefix  ...                     Manchester
            550  no prefix  ...

            [551 rows x 4 columns]
        """

        path_to_pickle = self._cdd_elec(self.NationalNetworkPickle + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            national_network_ole = load_pickle(path_to_pickle)

        else:
            verbose_ = False if data_dir or not verbose else (2 if verbose == 2 else True)

            national_network_ole = self.collect_national_network_codes(
                confirmation_required=False, verbose=verbose_)

            if national_network_ole:  # codes_for_ole is not None
                if pickle_it and data_dir:
                    self.CurrentDataDir = validate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(
                        self.CurrentDataDir, self.NationalNetworkPickle + ".pickle")
                    save_pickle(national_network_ole, path_to_pickle, verbose=verbose)

            else:
                print("No data of {} has been freshly collected.".format(
                    self.NationalNetworkKey.lower()))
                national_network_ole = load_pickle(path_to_pickle)

        return national_network_ole

    def get_indep_line_catalogue(self, verbose=False, update=False):
        """
        Get names of `independent lines
        <http://www.railwaycodes.org.uk/electrification/mast_prefix2.shtm>`_.

        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :return: a list of independent line names
        :rtype: pandas.DataFrame

        **Example**::

            >>> # from pyrcs import Electrification
            >>> from pyrcs.line_data import Electrification
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
            indep_line_names = get_page_catalogue(
                url=self.Catalogue[self.IndependentLinesKey], head_tag='nav',
                head_txt='Jump to: ', feature_tag='h3',
                verbose=verbose)

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

            >>> # from pyrcs import Electrification
            >>> from pyrcs.line_data import Electrification

            >>> elec = Electrification()

            >>> il_ole_dat = elec.collect_indep_lines_codes()
            To collect section codes for OLE installations: independent lines
            ? [No]|Yes: yes
            >>> type(il_ole_dat)
            dict
            >>> list(il_ole_dat.keys())
            ['Independent lines', 'Last updated date']

            >>> elec.IndependentLinesKey
            'Independent lines'

            >>> il_ole_codes = il_ole_dat[elec.IndependentLinesKey]
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

        if confirmed("To collect section codes for OLE installations: {}\n?".format(
                self.IndependentLinesKey.lower()),
                confirmation_required=confirmation_required):

            if verbose == 2:
                print("Collecting the codes for {}".format(self.IndependentLinesKey.lower()),
                      end=" ... ")

            independent_lines_ole = None

            url = self.Catalogue[self.IndependentLinesKey]

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
                        self.IndependentLinesKey: independent_lines_ole_,
                        self.LUDKey: last_updated_date,
                    }

                    pickle_filename_ = self.IndependentLinesKey.lower().replace(" ", "-")
                    path_to_pickle = self._cdd_elec(pickle_filename_ + ".pickle")
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

            >>> # from pyrcs import Electrification
            >>> from pyrcs.line_data import Electrification

            >>> elec = Electrification()

            >>> il_ole_dat = elec.fetch_indep_lines_codes()
            >>> type(il_ole_dat)
            dict
            >>> list(il_ole_dat.keys())
            ['Independent lines', 'Last updated date']

            >>> elec.IndependentLinesKey
            'Independent lines'

            >>> il_ole_codes = il_ole_dat[elec.IndependentLinesKey]
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

        pickle_filename = self.IndependentLinesKey.lower().replace(" ", "-") + ".pickle"
        path_to_pickle = self._cdd_elec(pickle_filename)

        if os.path.isfile(path_to_pickle) and not update:
            independent_lines_ole = load_pickle(path_to_pickle)

        else:
            verbose_ = False if data_dir or not verbose else (2 if verbose == 2 else True)

            independent_lines_ole = self.collect_indep_lines_codes(
                confirmation_required=False, verbose=verbose_)

            if independent_lines_ole:  # codes_for_independent_lines is not None
                if pickle_it and data_dir:
                    self.CurrentDataDir = validate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, pickle_filename)
                    save_pickle(independent_lines_ole, path_to_pickle, verbose=verbose)

            else:
                print("No data of {} has been freshly collected.".format(
                    self.IndependentLinesKey.lower()))
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

            >>> # from pyrcs import Electrification
            >>> from pyrcs.line_data import Electrification

            >>> elec = Electrification()

            >>> ohns_dat = elec.collect_ohns_codes()
            To collect section codes for OLE installations: national network neutral sections
            ? [No]|Yes: yes

            >>> type(ohns_dat)
            dict
            >>> list(ohns_dat.keys())
            ['National network neutral sections', 'Last updated date']

            >>> elec.OhnsKey
            'National network neutral sections'

            >>> ohns_data = ohns_dat[elec.OhnsKey]
            >>> type(ohns_data)
            dict
            >>> list(ohns_data.keys())
            ['Codes', 'Notes']
            >>> ohns_data['Codes']
                  ELR          OHNS Name  ...     Tracks                          Dates
            0    ARG1         Rutherglen  ...
            1    ARG2    Finnieston East  ...       Down
            2    ARG2    Finnieston West  ...         Up
            3    AYR1   Shields Junction  ...     Up Ayr
            4    AYR1   Shields Junction  ...   Down Ayr
            ..    ...                ...  ...        ...                           ...
            487   WWD       Law Junction  ...
            488   WWD  Holytown Junction  ...                   Installed October 2018
            489   XRC          Royal Oak  ...  Westbound
            490   YKR              Yoker  ...             Installed ??, removed≈11 ...
            491   YKR            Dalmuir  ...             Installed ??, removed≈11 ...

            [492 rows x 5 columns]
        """

        if confirmed("To collect section codes for OLE installations: {}\n?".format(
                self.OhnsKey.lower()), confirmation_required=confirmation_required):

            if verbose == 2:
                print("Collecting data of {}".format(self.OhnsKey.lower()), end=" ... ")

            ohns_codes = None

            url = self.Catalogue[self.OhnsKey]

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

                    soup = bs4.BeautifulSoup(markup=source.text, features='lxml')
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
                        self.OhnsKey: {'Codes': neutral_sections_codes, 'Notes': notes},
                        self.LUDKey: last_updated_date,
                    }

                    path_to_pickle = self._cdd_elec(self.OhnsPickle + ".pickle")
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

            >>> # from pyrcs import Electrification
            >>> from pyrcs.line_data import Electrification

            >>> elec = Electrification()

            >>> ohns_dat = elec.fetch_ohns_codes()

            >>> type(ohns_dat)
            dict
            >>> list(ohns_dat.keys())
            ['National network neutral sections', 'Last updated date']

            >>> elec.OhnsKey
            'National network neutral sections'

            >>> ohns_data = ohns_dat[elec.OhnsKey]
            >>> type(ohns_data)
            dict
            >>> list(ohns_data.keys())
            ['Codes', 'Notes']
            >>> ohns_data['Codes']
                  ELR          OHNS Name  ...     Tracks                          Dates
            0    ARG1         Rutherglen  ...
            1    ARG2    Finnieston East  ...       Down
            2    ARG2    Finnieston West  ...         Up
            3    AYR1   Shields Junction  ...     Up Ayr
            4    AYR1   Shields Junction  ...   Down Ayr
            ..    ...                ...  ...        ...                           ...
            487   WWD       Law Junction  ...
            488   WWD  Holytown Junction  ...                   Installed October 2018
            489   XRC          Royal Oak  ...  Westbound
            490   YKR              Yoker  ...             Installed ??, removed≈11 ...
            491   YKR            Dalmuir  ...             Installed ??, removed≈11 ...

            [492 rows x 5 columns]
        """

        path_to_pickle = self._cdd_elec(self.OhnsPickle + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            ohns_codes = load_pickle(path_to_pickle)

        else:
            verbose_ = False if data_dir or not verbose else (2 if verbose == 2 else True)

            ohns_codes = self.collect_ohns_codes(confirmation_required=False, verbose=verbose_)

            if ohns_codes:  # ohns is not None
                if pickle_it and data_dir:
                    self.CurrentDataDir = validate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir, self.OhnsPickle + ".pickle")
                    save_pickle(ohns_codes, path_to_pickle, verbose=verbose)
            else:
                print("No data of section codes for {} has been freshly collected.".format(
                    self.OhnsKey.lower()))
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

            >>> # from pyrcs import Electrification
            >>> from pyrcs.line_data import Electrification

            >>> elec = Electrification()

            >>> etz_ole_dat = elec.collect_etz_codes()
            To collect section codes for OLE installations: national network energy tariff zones
            ? [No]|Yes: yes

            >>> type(etz_ole_dat)
            dict
            >>> list(etz_ole_dat.keys())
            ['National network energy tariff zones', 'Last updated date']

            >>> elec.TariffZonesKey
            'National network energy tariff zones'

            >>> tariff_zone_codes = etz_ole_dat[elec.TariffZonesKey]
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

        if confirmed("To collect section codes for OLE installations: {}\n?".format(
                self.TariffZonesKey.lower()),
                confirmation_required=confirmation_required):

            if verbose == 2:
                print("Collecting the codes for {}".format(self.TariffZonesKey.lower()),
                      end=" ... ")

            etz_ole = None

            url = self.Catalogue[self.TariffZonesKey]

            try:
                source = requests.get(url=url, headers=fake_requests_headers(randomized=True))
            except requests.exceptions.ConnectionError:
                print("Failed. ") if verbose == 2 else ""
                print_conn_err(verbose=verbose)

            else:
                try:
                    etz_ole_ = self._collect_data(source=source)

                    # soup = bs4.BeautifulSoup(markup=source.text, features='lxml')
                    #
                    # etz_ole_ = {}
                    # h3 = soup.find('h3')
                    # while h3:
                    #     header_tag, table = h3.find_next('table'), None
                    #     if header_tag:
                    #         if header_tag.find_previous('h3') == h3:
                    #             header = [x.text for x in header_tag.find_all('th')]
                    #             temp = parse_tr(
                    #                 header, header_tag.find_next('table').find_all('tr'))
                    #             table = pd.DataFrame(temp, columns=header)
                    #             table = table.applymap(
                    #                 lambda x:
                    #                 re.sub(
                    #                     r'\']\)?', ']', re.sub(r'\(?\[\'', '[', x)).replace(
                    #                     '\\xa0', '').strip())
                    #
                    #     notes, next_p = [], h3.find_next('p')
                    #     previous_h3 = next_p.find_previous('h3')
                    #     while previous_h3 == h3:
                    #         notes.append(next_p.text.replace('\xa0', ''))
                    #         next_p = next_p.find_next('p')
                    #         try:
                    #             previous_h3 = next_p.find_previous('h3')
                    #         except AttributeError:
                    #             break
                    #     notes = ' '.join(notes).strip()
                    #
                    #     etz_ole_.update({h3.text: table, 'Notes': notes})
                    #
                    #     h3 = h3.find_next_sibling('h3')

                    source.close()

                    last_updated_date = get_last_updated_date(self.Catalogue[self.TariffZonesKey])

                    print("Done.") if verbose == 2 else ""

                    etz_ole = {self.TariffZonesKey: etz_ole_, self.LUDKey: last_updated_date}

                    path_to_pickle = self._cdd_elec(self.TariffZonesPickle + ".pickle")
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

            >>> # from pyrcs import Electrification
            >>> from pyrcs.line_data import Electrification

            >>> elec = Electrification()

            >>> etz_ole_dat = elec.fetch_etz_codes()
            >>> type(etz_ole_dat)
            dict
            >>> list(etz_ole_dat.keys())
            ['National network energy tariff zones', 'Last updated date']

            >>> elec.TariffZonesKey
            'National network energy tariff zones'

            >>> tariff_zone_codes = etz_ole_dat[elec.TariffZonesKey]
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

        path_to_pickle = self._cdd_elec(self.TariffZonesPickle + ".pickle")

        if os.path.isfile(path_to_pickle) and not update:
            etz_ole = load_pickle(path_to_pickle)

        else:
            verbose_ = False if data_dir or not verbose else (2 if verbose == 2 else True)

            etz_ole = self.collect_etz_codes(confirmation_required=False, verbose=verbose_)

            if etz_ole:  # codes_for_energy_tariff_zones is not None
                if pickle_it and data_dir:
                    self.CurrentDataDir = validate_input_data_dir(data_dir)
                    path_to_pickle = os.path.join(self.CurrentDataDir,
                                                  self.TariffZonesPickle + ".pickle")
                    save_pickle(etz_ole, path_to_pickle, verbose=verbose)

            else:
                print("No data of {} has been freshly collected.".format(
                    self.TariffZonesKey.lower()))
                etz_ole = load_pickle(path_to_pickle)

        return etz_ole

    def fetch_elec_codes(self, update=False, pickle_it=False, data_dir=None, verbose=False):
        """
        Fetch OLE section codes in `electrification
        <http://www.railwaycodes.org.uk/electrification/mast_prefix0.shtm>`_ catalogue.

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

        **Example**::

            >>> from pyrcs.line_data import Electrification

            >>> elec = Electrification()

            >>> electrification_data = elec.fetch_elec_codes()
            >>> type(electrification_data)
            dict
            >>> list(electrification_data.keys())
            ['Electrification', 'Last updated date']

            >>> elec.Key
            'Electrification'

            >>> electrification_codes = electrification_data[elec.Key]
            >>> type(electrification_codes)
            dict
            >>> list(electrification_codes.keys())
            ['National network energy tariff zones',
             'Independent lines',
             'National network',
             'National network neutral sections']
        """

        verbose_ = False if (data_dir or not verbose) else (2 if verbose == 2 else True)

        codes = []
        for func in dir(self):
            if func.startswith('fetch_') and func != 'fetch_elec_codes':
                codes.append(getattr(self, func)(
                    update=update, verbose=verbose_ if is_internet_connected() else False))

        ole_section_codes = {
            self.Key: {next(iter(x)): next(iter(x.values())) for x in codes},
            self.LUDKey:
                max(next(itertools.islice(iter(x.values()), 1, 2)) for x in codes)}

        if pickle_it and data_dir:
            pickle_filename = self.Name.lower().replace(" ", "-") + ".pickle"
            self.CurrentDataDir = validate_input_data_dir(data_dir)
            path_to_pickle = os.path.join(self.CurrentDataDir, pickle_filename)
            save_pickle(ole_section_codes, path_to_pickle, verbose=verbose)

        return ole_section_codes
