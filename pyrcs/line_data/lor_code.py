"""Collect `Line of Route (LOR/PRIDE) <http://www.railwaycodes.org.uk/pride/pride0.shtm>`_ codes."""

from pyhelpers.dir import cd

from ..parser import *
from ..utils import *


class LOR:
    """A class for collecting data of `Line of Route (LOR/PRIDE)`_.

    .. _`Line of Route (LOR/PRIDE)`: http://www.railwaycodes.org.uk/pride/pride0.shtm

    .. note::

        'LOR' and 'PRIDE' stands for 'Line Of Route' and 'Possession Resource Information Database',
        respectively.
    """

    #: Name of the data
    NAME = 'Possession Resource Information Database (PRIDE)/Line Of Route (LOR) codes'
    #: Short name of the data
    SHORT_NAME = 'Line of Route (LOR/PRIDE) codes'
    #: Key of the `dict <https://docs.python.org/3/library/stdtypes.html#dict>`_-type data
    KEY = 'LOR'
    #: Key of the dict-type data of prefixes
    KEY_P = 'Key to prefixes'
    #: Key of the dict-type data of *ELR/LOR converter*
    KEY_ELC = 'ELR/LOR converter'

    #: URL of the main web page of the data
    URL = urllib.parse.urljoin(home_page_url(), '/pride/pride0.shtm')

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

            >>> from pyrcs.line_data import LOR  # from pyrcs import LOR

            >>> lor = LOR()

            >>> print(lor.NAME)
            Possession Resource Information Database (PRIDE)/Line Of Route (LOR) codes

            >>> print(lor.URL)
            http://www.railwaycodes.org.uk/pride/pride0.shtm
        """

        print_conn_err(verbose=verbose)

        self.catalogue = get_catalogue(url=self.URL, update=update, confirmation_required=False)

        self.last_updated_date = get_last_updated_date(url=self.URL, parsed=True, as_date_type=False)

        self.data_dir, self.current_data_dir = init_data_dir(self, data_dir, category="line-data")

    def _cdd(self, *sub_dir, **kwargs):
        """
        Change directory to package data directory and subdirectories (and/or a file).

        The directory for this module: ``"data\\line-data\\lor"``.

        :param sub_dir: subdirectory or subdirectories (and/or a file)
        :type sub_dir: str
        :param kwargs: [optional] parameters of the function `pyhelpers.dir.cd`_
        :return: path to the backup data directory for the class
            :py:class:`~pyrcs.line_data.lor_code.LOR`
        :rtype: str

        .. _pyhelpers.dir.cd:
            https://pyhelpers.readthedocs.io/en/latest/_generated/pyhelpers.dir.cd.html
        """

        path = cd(self.data_dir, *sub_dir, mkdir=True, **kwargs)

        return path

    def get_keys_to_prefixes(self, prefixes_only=True, update=False, verbose=False):
        """
        Get the keys to PRIDE/LOR code prefixes.

        :param prefixes_only: whether to get only prefixes, defaults to ``True``
        :type prefixes_only: bool
        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console, defaults to ``True``
        :type verbose: bool or int
        :return: keys to LOR code prefixes
        :rtype: list or dict or None

        **Examples**::

            >>> from pyrcs.line_data import LOR  # from pyrcs import LOR

            >>> lor = LOR()

            >>> keys_to_pfx = lor.get_keys_to_prefixes()

            >>> print(keys_to_pfx)
            ['CY', 'EA', 'GW', 'LN', 'MD', 'NW', 'NZ', 'SC', 'SO', 'SW', 'XR']

            >>> keys_to_pfx = lor.get_keys_to_prefixes(prefixes_only=False)
            >>> type(keys_to_pfx)
            dict
            >>> list(keys_to_pfx.keys())
            ['Key to prefixes', 'Last updated date']

            >>> keys_to_pfx_codes = keys_to_pfx['Key to prefixes']
            >>> type(keys_to_pfx_codes)
            pandas.core.frame.DataFrame
            >>> keys_to_pfx_codes.head()
              Prefixes                                    Name
            0       CY                                   Wales
            1       EA         South Eastern: East Anglia area
            2       GW  Great Western (later known as Western)
            3       LN                  London & North Eastern
            4       MD       North West: former Midlands lines
        """

        data_name = "{}prefixes".format("" if prefixes_only else "keys-to-")
        ext = ".pickle"
        path_to_pickle = self._cdd(data_name + ext)

        if os.path.isfile(path_to_pickle) and not update:
            keys_to_prefixes = load_data(path_to_pickle)

        else:
            keys_to_prefixes = None

            try:
                source = requests.get(url=self.URL, headers=fake_requests_headers())

                soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')
                span_tags = soup.find_all(name='span', attrs={'class': 'tab2'})

                data = [(x.text, x.next_sibling.strip().replace('=  ', '')) for x in span_tags]

                lor_pref = pd.DataFrame(data=data, columns=['Prefixes', 'Name'])

            except Exception as e:
                verbose_ = True if (update and verbose != 2) else (False if verbose == 2 else verbose)
                if verbose_:
                    print("Failed. ", end="")
                print_inst_conn_err(update=update, verbose=verbose_, e=e)

            else:
                try:
                    if prefixes_only:
                        keys_to_prefixes = lor_pref.Prefixes.tolist()
                    else:
                        keys_to_prefixes = {
                            self.KEY_P: lor_pref,
                            self.KEY_TO_LAST_UPDATED_DATE: self.last_updated_date,
                        }

                    save_data_to_file(
                        self, data=keys_to_prefixes, data_name=data_name, ext=ext, verbose=verbose)

                except Exception as e:
                    print("Failed to get the keys to LOR prefixes. {}.".format(e))
                    if prefixes_only:
                        keys_to_prefixes = []
                    else:
                        keys_to_prefixes = {self.KEY_P: None, self.KEY_TO_LAST_UPDATED_DATE: None}

        return keys_to_prefixes

    def get_page_urls(self, update=False, verbose=False):
        """
        Get URLs to PRIDE/LOR codes with different prefixes.

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console, defaults to ``True``
        :type verbose: bool or int
        :return: a list of URLs of web pages hosting LOR codes for each prefix
        :rtype: list or None

        **Examples**::

            >>> from pyrcs.line_data import LOR  # from pyrcs import LOR

            >>> lor = LOR()

            >>> lor_urls = lor.get_page_urls()

            >>> lor_urls[:2]
            ['http://www.railwaycodes.org.uk/pride/pridecy.shtm',
             'http://www.railwaycodes.org.uk/pride/prideea.shtm']
        """

        data_name = "prefix-page-urls"
        ext = ".pickle"
        path_to_pickle = self._cdd(data_name + ext)

        if os.path.isfile(path_to_pickle) and not update:
            lor_page_urls = load_data(path_to_pickle)

        else:
            lor_page_urls = None

            try:
                source = requests.get(self.URL, headers=fake_requests_headers())

            except Exception as e:
                verbose_ = True if (update and verbose != 2) else (False if verbose == 2 else verbose)
                if verbose_:
                    print("Failed. ", end="")
                print_inst_conn_err(update=update, verbose=verbose_, e=e)

                lor_page_urls = load_data(path_to_pickle)

            else:
                try:
                    soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

                    links = soup.find_all(
                        name='a', href=re.compile('^pride|elrmapping'),
                        text=re.compile('.*(codes|converter|Historical)'))

                    lor_page_urls = list(dict.fromkeys([self.URL.replace(
                        os.path.basename(self.URL), x['href'])
                        for x in links]))

                    save_data_to_file(
                        self, data=lor_page_urls, data_name=data_name, ext=ext, verbose=verbose)

                except Exception as e:
                    print("Failed to get the URLs to LOR codes web pages. {}.".format(e))

        return lor_page_urls

    def _update_catalogue(self, confirmation_required=True, verbose=False):
        """
        Update catalogue data including keys to prefixes and LOR page URLs.

        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int

        **Examples**::

            >>> from pyrcs.line_data import LOR  # from pyrcs import LOR

            >>> lor = LOR()

            >>> lor._update_catalogue()
            To update catalogue
            ? [No]|Yes: yes
            Updating "keys-to-prefixes.pickle" at "pyrcs\\dat\\line-data\\lor" ... Done.
            Updating "prefix-page-urls.pickle" at "pyrcs\\dat\\line-data\\lor" ... Done.
        """

        if confirmed("To update catalogue\n?", confirmation_required=confirmation_required):
            self.get_keys_to_prefixes(prefixes_only=True, update=True, verbose=verbose)
            self.get_keys_to_prefixes(prefixes_only=False, update=True, verbose=2)
            self.get_page_urls(update=True, verbose=2)

    @staticmethod
    def _parse_h3_table(tbl, soup):

        # Parse the column of Line Name
        def _parse_line_name(x):
            # re.search('\w+.*(?= \(\[\')', x).group()
            # re.search('(?<=\(\[\')\w+.*(?=\')', x).group()
            try:
                line_name, line_name_note = x.split(' ([\'')
                line_name_note = line_name_note.strip('\'])')

            except ValueError:
                line_name, line_name_note = x, None

            return line_name, line_name_note

        thead, tbody = tbl
        ths = [x.text.replace('\n', ' ') for x in thead.find_all('th')]
        trs = tbody.find_all('tr')
        tbl = parse_tr(trs=trs, ths=ths, as_dataframe=True)
        line_name_info = tbl['Line Name'].map(_parse_line_name).apply(pd.Series)
        line_name_info.columns = ['Line Name', 'Line Name Note']
        codes_dat = pd.concat([tbl, line_name_info], axis=1, sort=False)

        try:
            note_dat_ = [
                (x['id'].title(), x.text.strip().replace('\xa0', ''))
                for x in soup.find('ol').findChildren('a')]
            note_dat = dict(note_dat_)

        except AttributeError:
            note_dat = dict([('Note', None)])

        return codes_dat, note_dat

    def collect_codes_by_prefix(self, prefix, update=False, verbose=False):
        """
        Collect `PRIDE/LOR codes <http://www.railwaycodes.org.uk/pride/pride0.shtm>`_ by a given prefix.

        :param prefix: prefix of LOR codes
        :type prefix: str
        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: LOR codes for the given ``prefix``
        :rtype: dict or None

        **Examples**::

            >>> from pyrcs.line_data import LOR  # from pyrcs import LOR

            >>> lor = LOR()

            >>> lor_codes_cy = lor.collect_codes_by_prefix(prefix='CY')
            >>> type(lor_codes_cy)
            dict
            >>> list(lor_codes_cy.keys())
            ['CY', 'Notes', 'Last updated date']

            >>> cy_codes = lor_codes_cy['CY']
            >>> type(cy_codes)
            pandas.core.frame.DataFrame
            >>> cy_codes.head()
                 Code  ... Line Name Note
            0   CY240  ...           None
            1  CY1540  ...           None

            [2 rows x 5 columns]

            >>> lor_codes_nw = lor.collect_codes_by_prefix(prefix='NW')
            >>> type(lor_codes_nw)
            dict
            >>> list(lor_codes_nw.keys())
            ['NW/NZ', 'Notes', 'Last updated date']
            >>> nw_codes = lor_codes_nw['NW/NZ']
            >>> nw_codes.head()
                 Code  ... Line Name Note
            0  NW1001  ...           None
            1  NW1002  ...           None
            2  NW1003  ...           None
            3  NW1004  ...           None
            4  NW1005  ...           None

            [5 rows x 5 columns]

            >>> lor_codes_xr = lor.collect_codes_by_prefix(prefix='XR')
            >>> xr_codes = lor_codes_xr['XR']
            >>> type(xr_codes)
            dict
            >>> list(xr_codes.keys())
            ['Current codes', 'Past codes']
            >>> xr_codes['Current codes']['XR'].head()
                Code  ... Line Name Note
            0  XR001  ...           None
            1  XR002  ...           None

            [2 rows x 5 columns]
        """

        valid_prefixes = self.get_keys_to_prefixes(prefixes_only=True)

        prefix_ = prefix.upper()

        assert prefix_ in valid_prefixes, "`prefix` must be one of {}".format(", ".join(valid_prefixes))

        data_name = "nw-nz" if prefix_ in ("NW", "NZ") else prefix_.lower()
        ext = ".pickle"
        path_to_pickle = self._cdd("prefixes", data_name + ext)

        if os.path.isfile(path_to_pickle) and not update:
            lor_codes_by_initials = load_data(path_to_pickle)

        else:
            if prefix_ in ("NW", "NZ"):
                url = home_page_url() + '/pride/pridenw.shtm'
                prefix_ = "NW/NZ"
            else:
                url = home_page_url() + '/pride/pride{}.shtm'.format(prefix_.lower())

            if verbose == 2:
                print("To collect LOR codes prefixed by \"{}\". ".format(prefix_), end=" ... ")

            lor_codes_by_initials = None

            try:
                source = requests.get(url=url, headers=fake_requests_headers())

            except Exception as e:
                if verbose == 2:
                    print("Failed. ", end="")
                print_inst_conn_err(verbose=verbose, e=e)

            else:
                try:
                    soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

                    h3, table = soup.find_all(name='h3'), soup.find_all(name='table')
                    if len(h3) == 0:
                        code_data, code_data_notes = self._parse_h3_table(table, soup=soup)
                        lor_codes_by_initials = {prefix_: code_data, 'Notes': code_data_notes}
                    else:
                        code_data_and_notes = [
                            dict(zip([prefix_, 'Notes'], self._parse_h3_table(x, soup=soup)))
                            for x in zip(*[iter(table)] * 2)]
                        lor_codes_by_initials = {
                            prefix_: dict(zip([x.text for x in h3], code_data_and_notes))}

                    last_updated_date = get_last_updated_date(url=url)

                    lor_codes_by_initials.update({self.KEY_TO_LAST_UPDATED_DATE: last_updated_date})

                    if verbose == 2:
                        print("Done.")

                    save_data_to_file(
                        self, data=lor_codes_by_initials, data_name=data_name,
                        ext=".pickle", dump_dir=self._cdd("prefixes"), verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(e))

        return lor_codes_by_initials

    def fetch_codes(self, update=False, dump_dir=None, verbose=False):
        """
        Fetch data of `PRIDE/LOR codes`_.

        .. _`PRIDE/LOR codes`: http://www.railwaycodes.org.uk/pride/pride0.shtm

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param dump_dir: pathname of a directory where the data file is dumped, defaults to ``None``
        :type dump_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: LOR codes
        :rtype: dict

        **Examples**::

            >>> from pyrcs.line_data import LOR  # from pyrcs import LOR

            >>> lor = LOR()

            >>> lor_codes_dat = lor.fetch_codes()
            >>> type(lor_codes_dat)
            dict
            >>> l_codes = lor_codes_dat['LOR']
            >>> type(l_codes)
            dict
            >>> list(l_codes.keys())
            ['CY', 'EA', 'GW', 'LN', 'MD', 'NW/NZ', 'SC', 'SO', 'SW', 'XR']

            >>> cy_codes = l_codes['CY']
            >>> type(cy_codes)
            dict
            >>> list(cy_codes.keys())
            ['CY', 'Notes', 'Last updated date']
            >>> cy_codes['CY']
                 Code  ... Line Name Note
            0   CY240  ...           None
            1  CY1540  ...           None

            [2 rows x 5 columns]
        """

        prefixes = self.get_keys_to_prefixes(prefixes_only=True, verbose=verbose)

        verbose_ = False if (dump_dir or not verbose) else (2 if verbose == 2 else True)

        lor_codes = [
            self.collect_codes_by_prefix(
                prefix=p, update=update, verbose=verbose_ if is_home_connectable() else False)
            for p in prefixes if p != 'NZ']

        if all(x is None for x in lor_codes):
            if update:
                print_inst_conn_err(verbose=verbose)
                print_void_msg(data_name=self.KEY.lower(), verbose=verbose)
            lor_codes = [
                self.collect_codes_by_prefix(prefix=p, update=False, verbose=verbose_)
                for p in prefixes if p != 'NZ']

        prefixes[prefixes.index('NW')] = 'NW/NZ'
        prefixes.remove('NZ')

        lor_data = {self.KEY: dict(zip(prefixes, lor_codes))}

        # Get the latest updated date
        last_updated_dates = (x[self.KEY_TO_LAST_UPDATED_DATE] for x, _ in zip(lor_codes, prefixes))
        latest_update_date = max(d for d in last_updated_dates if d is not None)

        lor_data.update({self.KEY_TO_LAST_UPDATED_DATE: latest_update_date})

        if dump_dir is not None:
            save_data_to_file(
                self, data=lor_data, data_name=self.KEY, ext=".pickle", dump_dir=dump_dir,
                verbose=verbose)

        return lor_data

    def collect_elr_lor_converter(self, confirmation_required=True, verbose=False):
        """
        Collect `ELR/LOR converter <http://www.railwaycodes.org.uk/pride/elrmapping.shtm>`_
        from source web page.

        :param confirmation_required: whether to confirm before proceeding, defaults to ``True``
        :type confirmation_required: bool
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of ELR/LOR converter
        :rtype: dict or None

        **Examples**::

            >>> from pyrcs.line_data import LOR  # from pyrcs import LOR

            >>> lor = LOR()

            >>> elr_lor_conv = lor.collect_elr_lor_converter()
            To collect data of ELR/LOR converter
            ? [No]|Yes: yes
            >>> type(elr_lor_conv)
            dict
            >>> list(elr_lor_conv.keys())
            ['ELR/LOR converter', 'Last updated date']

            >>> elr_loc_conv_data = elr_lor_conv['ELR/LOR converter']
            >>> type(elr_loc_conv_data)
            pandas.core.frame.DataFrame
            >>> elr_loc_conv_data.head()
                ELR  ...                                            LOR_URL
            0   AAV  ...  http://www.railwaycodes.org.uk/pride/pridesw.s...
            1   ABD  ...  http://www.railwaycodes.org.uk/pride/pridegw.s...
            2   ABE  ...  http://www.railwaycodes.org.uk/pride/prideln.s...
            3  ABE1  ...  http://www.railwaycodes.org.uk/pride/prideln.s...
            4  ABE2  ...  http://www.railwaycodes.org.uk/pride/prideln.s...

            [5 rows x 6 columns]
        """

        if confirmed("To collect data of {}\n?".format(self.KEY_ELC), confirmation_required):

            url = self.catalogue[self.KEY_ELC]

            if verbose == 2:
                print("Collecting data of {}".format(self.KEY_ELC), end=" ... ")

            elr_lor_converter = None

            try:
                # headers, elr_lor_dat = pd.read_html(io=url)
                # elr_lor_dat.columns = list(headers)
                source = requests.get(url=url, headers=fake_requests_headers())

            except Exception as e:
                if verbose == 2:
                    print("Failed. ", end="")
                print_inst_conn_err(verbose=verbose, e=e)

            else:
                try:
                    soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

                    thead, tbody = soup.find_all('thead')[0], soup.find_all('tbody')[0]
                    ths = thead.find_all('th')
                    trs = tbody.find_all(name='tr')

                    elr_lor_dat = parse_tr(trs=trs, ths=ths, as_dataframe=True)

                    elr_links = soup.find_all(name='td', text=re.compile(r'([A-Z]{3})(\d)?'))
                    lor_links = soup.find_all(name='a', href=re.compile(r'pride([a-z]{2})\.shtm#'))
                    #
                    # if len(elr_links) != len(elr_lor_dat):
                    #     duplicates = \
                    #         elr_lor_dat[elr_lor_dat.duplicated(['ELR', 'LOR code'], keep=False)]
                    #     for i in duplicates.index:
                    #         if not duplicates['ELR'].loc[i].lower() in elr_links[i]:
                    #             elr_links.insert(i, elr_links[i - 1])
                    #         if not lor_links[i].endswith(
                    #                 duplicates['LOR code'].loc[i].lower()):
                    #             lor_links.insert(i, lor_links[i - 1])
                    #
                    elr_lor_dat['ELR_URL'] = [
                        urllib.parse.urljoin(home_page_url(), x.a.get('href')) if x.a else None
                        for x in elr_links
                    ]
                    elr_lor_dat['LOR_URL'] = [
                        urllib.parse.urljoin(home_page_url(), 'pride/' + x.get('href'))
                        for x in lor_links
                    ]
                    #
                    elr_lor_converter = {
                        self.KEY_ELC: elr_lor_dat,
                        self.KEY_TO_LAST_UPDATED_DATE: get_last_updated_date(url)
                    }

                    if verbose == 2:
                        print("Done.")

                    save_data_to_file(
                        self, data=elr_lor_converter, data_name=re.sub(r"[/ ]", "-", self.KEY_ELC),
                        ext=".pickle", verbose=verbose)

                except Exception as e:
                    print("Failed. {}".format(e))

            return elr_lor_converter

    def fetch_elr_lor_converter(self, update=False, dump_dir=None, verbose=False):
        """
        Fetch data of `ELR/LOR converter`_.

        .. _`ELR/LOR converter`: http://www.railwaycodes.org.uk/pride/elrmapping.shtm

        :param update: whether to do an update check (for the package data), defaults to ``False``
        :type update: bool
        :param dump_dir: pathname of a directory where the data file is dumped, defaults to ``None``
        :type dump_dir: str or None
        :param verbose: whether to print relevant information in console, defaults to ``False``
        :type verbose: bool or int
        :return: data of ELR/LOR converter
        :rtype: dict

        **Examples**::

            >>> from pyrcs.line_data import LOR  # from pyrcs import LOR

            >>> lor = LOR()

            >>> elr_lor_conv = lor.fetch_elr_lor_converter()
            >>> type(elr_lor_conv)
            dict
            >>> list(elr_lor_conv.keys())
            ['ELR/LOR converter', 'Last updated date']

            >>> elr_loc_conv_data = elr_lor_conv['ELR/LOR converter']
            >>> type(elr_loc_conv_data)
            pandas.core.frame.DataFrame
            >>> elr_loc_conv_data.head()
                ELR  ...                                            LOR_URL
            0   AAV  ...  http://www.railwaycodes.org.uk/pride/pridesw.s...
            1   ABD  ...  http://www.railwaycodes.org.uk/pride/pridegw.s...
            2   ABE  ...  http://www.railwaycodes.org.uk/pride/prideln.s...
            3  ABE1  ...  http://www.railwaycodes.org.uk/pride/prideln.s...
            4  ABE2  ...  http://www.railwaycodes.org.uk/pride/prideln.s...

            [5 rows x 6 columns]
        """

        elr_lor_converter = fetch_data_from_file(
            cls=self, method='collect_elr_lor_converter', data_name=re.sub(r"[/ ]", "-", self.KEY_ELC),
            ext=".pickle", update=update, dump_dir=dump_dir, verbose=verbose)

        return elr_lor_converter
