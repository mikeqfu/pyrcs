"""
Collect data of `signal box prefix codes <http://www.railwaycodes.org.uk/signal/signal_boxes0.shtm>`_.
"""

import collections
import string
import urllib.parse

import bs4
import pandas as pd

from .._base import _Base
from ..parser import _get_last_updated_date, parse_tr
from ..utils import collect_in_fetch_verbose, home_page_url, is_home_connectable, \
    print_inst_conn_err, print_void_msg, validate_initial


class SignalBoxes(_Base):
    """
    A class for collecting data of
    `signal box prefix codes <http://www.railwaycodes.org.uk/signal/signal_boxes0.shtm>`_.
    """

    #: The name of the data.
    NAME: str = 'Signal box prefix codes'
    #: The key for accessing the data.
    KEY: str = 'Signal boxes'

    #: The key for accessing the data of *non-national rail*.
    KEY_TO_NON_NATIONAL_RAIL: str = 'Non-National Rail'
    #: The key for accessing the data of *Ireland*.
    KEY_TO_IRELAND: str = 'Ireland'
    #: The key for accessing the data of
    #: *WR (Western region) MAS (multiple aspect signalling) dates*.
    KEY_TO_WRMASD: str = 'WR MAS dates'
    #: The key for accessing the data of *bell codes*.
    KEY_TO_BELL_CODES: str = 'Bell codes'

    #: The URL of the main web page for the data.
    URL: str = urllib.parse.urljoin(home_page_url(), '/signal/signal_boxes0.shtm')

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

            >>> from pyrcs.other_assets import SignalBoxes  # from pyrcs import SignalBoxes
            >>> sb = SignalBoxes()
            >>> sb.NAME
            'Signal box prefix codes'
            >>> sb.URL
            'http://www.railwaycodes.org.uk/signal/signal_boxes0.shtm'
        """

        super().__init__(
            data_dir=data_dir, content_type='catalogue', data_category="other-assets",
            update=update, verbose=verbose)

    def _collect_prefix_codes(self, initial, source, verbose=False):
        initial_ = validate_initial(x=initial)

        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')
        thead, tbody = soup.find('thead'), soup.find('tbody')

        ths = [th.get_text(strip=True) for th in thead.find_all('th')]
        trs = tbody.find_all('tr')
        signal_boxes_data_table = parse_tr(trs=trs, ths=ths, as_dataframe=True)

        signal_box_prefix_codes = {
            initial_: signal_boxes_data_table,
            self.KEY_TO_LAST_UPDATED_DATE: _get_last_updated_date(soup)
        }

        if verbose in {True, 1}:
            print("Done.")

        self._save_data_to_file(
            data=signal_box_prefix_codes, data_name=initial_, sub_dir="a-z", verbose=verbose)

        return signal_box_prefix_codes

    def collect_prefix_codes(self, initial, confirmation_required=True, verbose=False,
                             raise_error=False):
        """
        Collects `signal box prefix codes`_ for a given initial letter from the source web page.

        .. _`signal box prefix codes`: http://www.railwaycodes.org.uk/signal/signal_boxes0.shtm

        :param initial: The initial letter (e.g. ``'a'``, ``'z'``) of signal box prefix code.
        :type initial: str
        :param confirmation_required: Whether user confirmation is required;
            if ``confirmation_required=True`` (default), prompts the user for confirmation
            before proceeding with data collection.
        :type confirmation_required: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :param raise_error: Whether to raise the provided exception;
            if ``raise_error=False`` (default), the error will be suppressed.
        :type raise_error: bool
        :return: A dictionary containing data of signal box prefix codes whose initial letters are
            the specified ``initial`` and the date of when the data was last updated.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import SignalBoxes  # from pyrcs import SignalBoxes
            >>> sb = SignalBoxes()
            >>> sb_a_codes = sb.collect_prefix_codes(initial='a')
            >>> type(sb_a_codes)
            dict
            >>> list(sb_a_codes.keys())
            ['A', 'Last updated date']
            >>> sb_a_codes_dat = sb_a_codes['A']
            >>> type(sb_a_codes_dat)
            pandas.core.frame.DataFrame
            >>> sb_a_codes_dat.head()
              Code               Signal Box  ...            Closed        Control to
            0   AF  Abbey Foregate Junction  ...
            1   AJ           Abbey Junction  ...  16 February 1992     Nuneaton (NN)
            2    R           Abbey Junction  ...  16 February 1992     Nuneaton (NN)
            3   AW               Abbey Wood  ...      13 July 1975      Dartford (D)
            4   AE         Abbey Works East  ...   1 November 1987  Port Talbot (PT)
            [5 rows x 8 columns]
        """

        initial_ = validate_initial(x=initial)

        signal_box_prefix_codes = self._collect_data_from_source(
            data_name=self.NAME.lower(), method=self._collect_prefix_codes, initial=initial_,
            confirmation_required=confirmation_required, verbose=verbose, raise_error=raise_error)

        return signal_box_prefix_codes

    def fetch_prefix_codes(self, initial=None, update=False, dump_dir=None, verbose=False,
                           **kwargs):
        """
        Fetches data of `signal box prefix codes`_.

        .. _`signal box prefix codes`: http://www.railwaycodes.org.uk/signal/signal_boxes0.shtm

        :param initial: The initial letter (e.g. ``'a'``, ``'z'``) of signal box prefix code;
            defaults to ``None``.
        :type initial: str
        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the data of signal box prefix codes and
            the date whey they were last updated.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import SignalBoxes  # from pyrcs import SignalBoxes
            >>> sb = SignalBoxes()
            >>> sb_prefix_codes = sb.fetch_prefix_codes()
            >>> type(sb_prefix_codes)
            dict
            >>> list(sb_prefix_codes.keys())
            ['Signal boxes', 'Last updated date']
            >>> sb.KEY
            'Signal boxes'
            >>> sb_prefix_codes_dat = sb_prefix_codes[sb.KEY]
            >>> type(sb_prefix_codes_dat)
            pandas.core.frame.DataFrame
            >>> sb_prefix_codes_dat.head()
              Code               Signal Box  ...            Closed        Control to
            0   AF  Abbey Foregate Junction  ...
            1   AJ           Abbey Junction  ...  16 February 1992     Nuneaton (NN)
            2    R           Abbey Junction  ...  16 February 1992     Nuneaton (NN)
            3   AW               Abbey Wood  ...      13 July 1975      Dartford (D)
            4   AE         Abbey Works East  ...   1 November 1987  Port Talbot (PT)
            [5 rows x 8 columns]
        """

        if initial:
            args = {
                'data_name': validate_initial(initial),
                'method': self.collect_prefix_codes,
                'sub_dir': "a-z",
                'initial': initial,
            }
            kwargs.update(args)

            signal_box_prefix_codes = self._fetch_data_from_file(
                update=update, dump_dir=dump_dir, verbose=verbose, **kwargs)

        else:

            verbose_1 = collect_in_fetch_verbose(data_dir=dump_dir, verbose=verbose)
            verbose_2 = verbose_1 if is_home_connectable() else False

            # Get every data table
            data = [
                self.fetch_prefix_codes(initial=x, update=update, verbose=verbose_2)
                for x in string.ascii_lowercase]

            if all(d[x] is None for d, x in zip(data, string.ascii_uppercase)):
                if update:
                    print_inst_conn_err(verbose=verbose)
                    print_void_msg(data_name=self.KEY.lower(), verbose=verbose)

                data = [
                    self.fetch_prefix_codes(initial=x, update=False, verbose=verbose_1)
                    for x in string.ascii_lowercase]

            # Select DataFrames only
            signal_boxes_codes_ = (item[x] for item, x in zip(data, string.ascii_uppercase))
            signal_boxes_codes = pd.concat(signal_boxes_codes_, ignore_index=True)

            # Get the latest updated date
            last_updated_dates = (item[self.KEY_TO_LAST_UPDATED_DATE] for item in data)
            latest_update_date = max(d for d in last_updated_dates if d is not None)

            # Create a dict to include all information
            signal_box_prefix_codes = {
                self.KEY: signal_boxes_codes,
                self.KEY_TO_LAST_UPDATED_DATE: latest_update_date
            }

        if dump_dir:
            self._save_data_to_file(
                data=signal_box_prefix_codes, data_name=self.KEY, dump_dir=dump_dir,
                verbose=verbose)

        return signal_box_prefix_codes

    def _collect_non_national_rail_codes(self, source, verbose=False):
        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

        non_national_rail_codes = {}

        for h in soup.find_all('h3'):
            # Get the name of the non-national rail
            non_national_rail_name = h.text

            # Find text descriptions
            desc = h.find_next('p')
            desc_text = desc.text.replace('\xa0', '')
            more_desc = desc.find_next('p')
            while more_desc.find_previous('h3') == h:
                desc_text = '\n'.join([desc_text, more_desc.text.replace('\xa0', '')])
                more_desc = more_desc.find_next('p')
                if more_desc is None:
                    break

            # Get table data
            tbl_dat = desc.find_next('table')
            if tbl_dat.find_previous('h3').text == non_national_rail_name:
                ths = [th.text for th in tbl_dat.find_all('th')]  # header
                # trs = tbl_dat.find_next('table').find_all('tr')
                trs = tbl_dat.find_all('tr')
                data = parse_tr(trs=trs, ths=ths, as_dataframe=True)
            else:
                data = None

            # Update data dict
            non_national_rail_codes_ = {
                'Codes': data,
                'Notes': desc_text.replace('\xa0', '').strip(),
            }
            non_national_rail_codes[non_national_rail_name] = non_national_rail_codes_

        non_national_rail_codes_data = {
            self.KEY_TO_NON_NATIONAL_RAIL: non_national_rail_codes,
            self.KEY_TO_LAST_UPDATED_DATE: _get_last_updated_date(soup),
        }

        if verbose in {True, 1}:
            print("Done.")

        self._save_data_to_file(
            data=non_national_rail_codes_data, data_name=self.KEY_TO_NON_NATIONAL_RAIL,
            verbose=verbose)

        return non_national_rail_codes_data

    def collect_non_national_rail_codes(self, confirmation_required=True, verbose=False,
                                        raise_error=False):
        """
        Collects signal box prefix codes for `non-national rail
        <http://www.railwaycodes.org.uk/signal/signal_boxesX.shtm>`_ from the source web page.

        :param confirmation_required: Whether user confirmation is required;
            if ``confirmation_required=True`` (default), prompts the user for confirmation
            before proceeding with data collection.
        :type confirmation_required: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :param raise_error: Whether to raise the provided exception;
            if ``raise_error=False`` (default), the error will be suppressed.
        :type raise_error: bool
        :return: A dictionary containing the signal box prefix codes for non-national rail and
            the date when they were last updated, or ``None`` if no data is collected.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.other_assets import SignalBoxes  # from pyrcs import SignalBoxes
            >>> sb = SignalBoxes()
            >>> nnr_codes = sb.collect_non_national_rail_codes()
            To collect data of non-national rail signal box prefix codes
            ? [No]|Yes: yes
            >>> type(nnr_codes)
            dict
            >>> list(nnr_codes.keys())
            ['Non-National Rail', 'Last updated date']
            >>> sb.KEY_TO_NON_NATIONAL_RAIL
            'Non-National Rail'
            >>> nnr_codes_dat = nnr_codes[sb.KEY_TO_NON_NATIONAL_RAIL]
            >>> type(nnr_codes_dat)
            dict
            >>> list(nnr_codes_dat.keys())
            ['Croydon Tramlink signals',
             'Docklands Light Railway signals',
             'Edinburgh Tramway signals',
             'Glasgow Subway signals',
             'London Underground signals',
             'Luas signals',
             'Manchester Metrolink signals',
             'Midland Metro signals',
             'Nottingham Tram signals',
             'Sheffield Supertram signals',
             'Tyne & Wear Metro signals',
             "Heritage, minor and miniature railways and other 'special' signals"]
            >>> lu_signals_codes = nnr_codes_dat['London Underground signals']
            >>> type(lu_signals_codes)
            dict
            >>> list(lu_signals_codes.keys())
            ['Codes', 'Notes']
            >>> type(lu_signals_codes['Codes'])
            pandas.core.frame.DataFrame
            >>> lu_signals_codes['Codes'].head()
              Code  ... Became or taken over by (where known)
            0  BMX  ...                                     -
            1    A  ...                                     -
            2    S  ...                                     -
            3    X  ...                                     -
            4    R  ...                                     -
            [5 rows x 5 columns]
        """

        data_name = self.KEY_TO_NON_NATIONAL_RAIL.lower() + " signal box prefix codes"

        non_national_rail_codes_data = self._collect_data_from_source(
            data_name=data_name, method=self._collect_non_national_rail_codes,
            url=self.catalogue[self.KEY_TO_NON_NATIONAL_RAIL],
            confirmation_required=confirmation_required, verbose=verbose, raise_error=raise_error)

        return non_national_rail_codes_data

    def fetch_non_national_rail_codes(self, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetches signal box prefix codes for `non-national rail`_.

        .. _`non-national rail`: http://www.railwaycodes.org.uk/signal/signal_boxesX.shtm

        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the signal box prefix codes for non-national rail and
            the date when they were last updated.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import SignalBoxes  # from pyrcs import SignalBoxes
            >>> sb = SignalBoxes()
            >>> nnr_codes = sb.fetch_non_national_rail_codes()
            >>> type(nnr_codes)
            dict
            >>> list(nnr_codes.keys())
            ['Non-National Rail', 'Last updated date']
            >>> sb.KEY_TO_NON_NATIONAL_RAIL
            'Non-National Rail'
            >>> nnr_codes_dat = nnr_codes[sb.KEY_TO_NON_NATIONAL_RAIL]
            >>> type(nnr_codes_dat)
            dict
            >>> list(nnr_codes_dat.keys())
            ['Croydon Tramlink signals',
             'Docklands Light Railway signals',
             'Edinburgh Tramway signals',
             'Glasgow Subway signals',
             'London Underground signals',
             'Luas signals',
             'Manchester Metrolink signals',
             'Midland Metro signals',
             'Nottingham Tram signals',
             'Sheffield Supertram signals',
             'Tyne & Wear Metro signals',
             "Heritage, minor and miniature railways and other 'special' signals"]
            >>> lu_signals_codes = nnr_codes_dat['London Underground signals']
            >>> type(lu_signals_codes)
            dict
            >>> list(lu_signals_codes.keys())
            ['Codes', 'Notes']
            >>> type(lu_signals_codes['Codes'])
            pandas.core.frame.DataFrame
            >>> lu_signals_codes['Codes'].head()
              Code  ... Became or taken over by (where known)
            0  BMX  ...                                     -
            1    A  ...                                     -
            2    S  ...                                     -
            3    X  ...                                     -
            4    R  ...                                     -
            [5 rows x 5 columns]
        """

        args = {
            'data_name': self.KEY_TO_NON_NATIONAL_RAIL,
            'method': self.collect_non_national_rail_codes,
        }
        kwargs.update(args)

        non_national_rail_codes_data = self._fetch_data_from_file(
            update=update, dump_dir=dump_dir, verbose=verbose, **kwargs)

        return non_national_rail_codes_data

    def _collect_ireland_codes(self, source, verbose=False):
        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

        thead, tbody = soup.find('thead'), soup.find('tbody')

        ths = [th.text for th in thead.find_all(name='th')]
        trs = tbody.find_all(name='tr')
        ireland_codes = parse_tr(trs=trs, ths=ths, as_dataframe=True)

        notes_ = soup.find('h4').find_next('ol').find_all('li')
        notes = [li.text for li in notes_]

        ireland_codes_data = {
            self.KEY_TO_IRELAND: ireland_codes,
            'Notes': notes,
            self.KEY_TO_LAST_UPDATED_DATE: _get_last_updated_date(soup),
        }

        if verbose in {True, 1}:
            print("Done.")

        self._save_data_to_file(
            data=ireland_codes_data, data_name=self.KEY_TO_IRELAND, verbose=verbose)

        return ireland_codes_data

    def collect_ireland_codes(self, confirmation_required=True, verbose=False, raise_error=False):
        """
        Collects data of `Irish signal cabin prefix codes
        <http://www.railwaycodes.org.uk/signal/signal_boxes1.shtm>`_ from the source web page.

        :param confirmation_required: Whether user confirmation is required;
            if ``confirmation_required=True`` (default), prompts the user for confirmation
            before proceeding with data collection.
        :type confirmation_required: bool
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :param raise_error: Whether to raise the provided exception;
            if ``raise_error=False`` (default), the error will be suppressed.
        :type raise_error: bool
        :return: A dictionary containing the data of Irish signal cabin prefix codes and
            the date when they were last updated, or ``None`` if no data is collectd.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.other_assets import SignalBoxes  # from pyrcs import SignalBoxes
            >>> sb = SignalBoxes()
            >>> ireland_sb_codes = sb.collect_ireland_codes()
            To collect data of signal box prefix codes of Ireland
            ? [No]|Yes: yes
            >>> type(ireland_sb_codes)
            dict
            >>> list(ireland_sb_codes.keys())
            ['Ireland', 'Notes', 'Last updated date']
            >>> sb.KEY_TO_IRELAND
            'Ireland'
            >>> ireland_sb_codes_dat = ireland_sb_codes[sb.KEY_TO_IRELAND]
            >>> type(ireland_sb_codes_dat)
            pandas.core.frame.DataFrame
            >>> ireland_sb_codes_dat.head()
               Code Signal Cabin                    Note
            0    AD     Adelaide
            1    AN       Antrim
            2    AE      Athlone
            3  AE R                      Distant signals
            4    XG               Level crossing signals
        """

        data_name = "signal box prefix codes of " + self.KEY_TO_IRELAND

        ireland_codes_data = self._collect_data_from_source(
            data_name=data_name, method=self._collect_ireland_codes,
            url=self.catalogue[self.KEY_TO_IRELAND], additional_fields='Notes',
            confirmation_required=confirmation_required, verbose=verbose, raise_error=raise_error)

        return ireland_codes_data

    def fetch_ireland_codes(self, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetches data of `Irish signal cabin prefix codes`_.

        .. _`Irish signal cabin prefix codes`:
            http://www.railwaycodes.org.uk/signal/signal_boxes1.shtm

        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the data of Irish signal cabin prefix codes and
            the date when they were last updated.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import SignalBoxes  # from pyrcs import SignalBoxes
            >>> sb = SignalBoxes()
            >>> ireland_sb_codes = sb.fetch_ireland_codes()
            >>> type(ireland_sb_codes)
            dict
            >>> list(ireland_sb_codes.keys())
            ['Ireland', 'Notes', 'Last updated date']
            >>> sb.KEY_TO_IRELAND
            'Ireland'
            >>> ireland_sb_codes_dat = ireland_sb_codes[sb.KEY_TO_IRELAND]
            >>> type(ireland_sb_codes_dat)
            pandas.core.frame.DataFrame
            >>> ireland_sb_codes_dat.head()
               Code Signal Cabin                    Note
            0    AD     Adelaide
            1    AN       Antrim
            2    AE      Athlone
            3  AE R                      Distant signals
            4    XG               Level crossing signals
        """

        kwargs.update({'data_name': self.KEY_TO_IRELAND, 'method': self.collect_ireland_codes})

        ireland_codes_data = self._fetch_data_from_file(
            update=update, dump_dir=dump_dir, verbose=verbose, **kwargs)

        return ireland_codes_data

    @staticmethod
    def _parse_tbl_dat(h3_or_h4, ths):
        trs = []
        tr = h3_or_h4.find_next('tr')
        while tr:
            if not tr.td.has_attr('colspan'):
                trs.append(tr)
                tr = tr.find_next('tr')
            else:
                break

        tbl = parse_tr(trs=trs, ths=ths, as_dataframe=True)

        return tbl

    def _collect_wr_mas_dates(self, source, verbose=False):
        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

        ths = [th.text for th in soup.find('thead').find_all('th')]

        wr_mas_dates = collections.defaultdict(dict)

        for h3 in soup.find_all('h3'):
            h4 = h3.find_next('h4')

            if h4 is not None:
                while h4:
                    prev_h3 = h4.find_previous('h3')
                    if prev_h3.text == h3.text:
                        wr_mas_dates[h3.text].update({h4.text: self._parse_tbl_dat(h4, ths)})
                        h4 = h4.find_next('h4')
                    elif h3.text not in wr_mas_dates.keys():
                        wr_mas_dates.update({h3.text: self._parse_tbl_dat(h3, ths)})
                        break
                    else:
                        break

            else:
                wr_mas_dates.update({h3.text: self._parse_tbl_dat(h3, ths)})

        wr_mas_dates_data = {
            self.KEY_TO_WRMASD: wr_mas_dates,
            self.KEY_TO_LAST_UPDATED_DATE: _get_last_updated_date(soup),
        }

        if verbose in {True, 1}:
            print("Done.")

        self._save_data_to_file(
            data=wr_mas_dates_data, data_name=self.KEY_TO_WRMASD, verbose=verbose)

        return wr_mas_dates_data

    def collect_wr_mas_dates(self, confirmation_required=True, verbose=False, raise_error=False):
        """
        Collects data of `WR (western region) MAS (multiple aspect signalling) dates
        <http://www.railwaycodes.org.uk/signal/dates.shtm>`_
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
        :return: A dictionary containing the data of WR MAS dates and
            the date when they were last updated, or ``None`` if no data is collected.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.other_assets import SignalBoxes  # from pyrcs import SignalBoxes
            >>> sb = SignalBoxes()
            >>> sb_wr_mas_dates = sb.collect_wr_mas_dates()
            To collect data of WR MAS dates
            ? [No]|Yes: yes
            >>> type(sb_wr_mas_dates)
            dict
            >>> list(sb_wr_mas_dates.keys())
            ['WR MAS dates', 'Last updated date']
            >>> sb.KEY_TO_WRMASD
            'WR MAS dates'
            >>> sb_wr_mas_dates_dat = sb_wr_mas_dates[sb.KEY_TO_WRMASD]
            >>> type(sb_wr_mas_dates_dat)
            collections.defaultdict
            >>> list(sb_wr_mas_dates_dat.keys())
            ['Paddington-Hayes',
             'Birmingham',
             'Plymouth',
             'Reading-Hayes',
             'Newport Multiple Aspect Signalling']
            >>> sb_wr_mas_dates_dat['Paddington-Hayes']
              Stage             Date                        Area
            0    1A    12 April 1953               Hayes-Hanwell
            1    1B    20 March 1955        Hanwell-Acton Middle
            2    1C  1 February 1959  Acton West-Friars Junction
        """

        wr_mas_dates_data = self._collect_data_from_source(
            data_name=self.KEY_TO_WRMASD, method=self._collect_wr_mas_dates,
            confirmation_required=confirmation_required, verbose=verbose, raise_error=raise_error)

        return wr_mas_dates_data

    def fetch_wr_mas_dates(self, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetches data of `WR (western region) MAS (multiple aspect signalling) dates`_.

        .. _`WR (western region) MAS (multiple aspect signalling) dates`:
            http://www.railwaycodes.org.uk/signal/dates.shtm

        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the data of WR MAS dates and
            the date when they were last updated.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import SignalBoxes  # from pyrcs import SignalBoxes
            >>> sb = SignalBoxes()
            >>> sb_wr_mas_dates = sb.fetch_wr_mas_dates()
            >>> type(sb_wr_mas_dates)
            dict
            >>> list(sb_wr_mas_dates.keys())
            ['WR MAS dates', 'Last updated date']
            >>> sb.KEY_TO_WRMASD
            'WR MAS dates'
            >>> sb_wr_mas_dates_dat = sb_wr_mas_dates[sb.KEY_TO_WRMASD]
            >>> type(sb_wr_mas_dates_dat)
            collections.defaultdict
            >>> list(sb_wr_mas_dates_dat.keys())[:5]
            ['Paddington-Hayes',
             'Birmingham',
             'Plymouth',
             'Reading-Hayes',
             'Newport Multiple Aspect Signalling']
            >>> sb_wr_mas_dates_dat['Paddington-Hayes']
              Stage             Date                        Area
            0    1A    12 April 1953               Hayes-Hanwell
            1    1B    20 March 1955        Hanwell-Acton Middle
            2    1C  1 February 1959  Acton West-Friars Junction
        """

        kwargs.update({'data_name': self.KEY_TO_WRMASD, 'method': self.collect_wr_mas_dates})

        wr_mas_dates_data = self._fetch_data_from_file(
            update=update, dump_dir=dump_dir, verbose=verbose, **kwargs)

        return wr_mas_dates_data

    def _collect_bell_codes(self, source, verbose=False):
        soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

        bell_codes_ = {}
        h3s = soup.find_all('h3')
        for h3 in h3s:
            tbl = h3.find_next('table')
            trs, ths = tbl.find_all('tr'), [th.text for th in tbl.find_all('th')]
            dat = parse_tr(trs=trs, ths=ths, as_dataframe=True)

            notes = h3.find_next('p').text

            bell_codes_.update({h3.text: {'Codes': dat, 'Notes': notes}})

        bell_codes = {
            self.KEY_TO_BELL_CODES: bell_codes_,
            self.KEY_TO_LAST_UPDATED_DATE: _get_last_updated_date(soup=soup),
        }

        if verbose in {True, 1}:
            print("Done.")

        self._save_data_to_file(data=bell_codes, data_name=self.KEY_TO_BELL_CODES, verbose=verbose)

        return bell_codes

    def collect_bell_codes(self, confirmation_required=True, verbose=False, raise_error=False):
        """
        Collects data of `bell codes <http://www.railwaycodes.org.uk/signal/bellcodes.shtm>`_
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
        :return: A dictionary containing the data of bell codes and
            the date when they were last updated, or ``None`` if no data is collected.
        :rtype: dict | None

        **Examples**::

            >>> from pyrcs.other_assets import SignalBoxes  # from pyrcs import SignalBoxes
            >>> sb = SignalBoxes()
            >>> sb_bell_codes = sb.collect_bell_codes()
            To collect data of Bell codes
            ? [No]|Yes: yes
            >>> type(sb_bell_codes)
            dict
            >>> list(sb_bell_codes.keys())
            ['Bell codes', 'Last updated date']
            >>> sb.KEY_TO_BELL_CODES
            'Bell codes'
            >>> sb_bell_codes_dat = sb_bell_codes[sb.KEY_TO_BELL_CODES]
            >>> type(sb_bell_codes_dat)
            collections.OrderedDict
            >>> list(sb_bell_codes_dat.keys())
            ['Network Rail codes',
             'Southern Railway codes',
             'Lancashire & Yorkshire Railway codes']
            >>> sb_nr_bell_codes = sb_bell_codes_dat['Network Rail codes']
            >>> type(sb_nr_bell_codes)
            dict
            >>> list(sb_nr_bell_codes.keys())
            ['Codes', 'Notes']
            >>> sb_nr_bell_codes_dat = sb_nr_bell_codes['Codes']
            >>> type(sb_nr_bell_codes_dat)
            pandas.core.frame.DataFrame
            >>> sb_nr_bell_codes_dat.head()
                Code                                       Meaning
            0      1                                Call attention
            1    1-1             Answer telephone [withdrawn 2007]
            2  1-1-6           Police assistance urgently required
            3    1-2  Signaller required on telephone [added 2007]
            4  1-2-1                             Train approaching
        """

        bell_codes = self._collect_data_from_source(
            data_name=self.KEY_TO_BELL_CODES, method=self._collect_bell_codes,
            confirmation_required=confirmation_required, verbose=verbose, raise_error=raise_error)

        return bell_codes

    def fetch_bell_codes(self, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetches data of `bell codes`_.

        .. _`bell codes`: http://www.railwaycodes.org.uk/signal/bellcodes.shtm

        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the data of bell codes and
            the date when they were last updated.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import SignalBoxes  # from pyrcs import SignalBoxes
            >>> sb = SignalBoxes()
            >>> sb_bell_codes = sb.fetch_bell_codes()
            >>> type(sb_bell_codes)
            dict
            >>> list(sb_bell_codes.keys())
            ['Bell codes', 'Last updated date']
            >>> sb.KEY_TO_BELL_CODES
            'Bell codes'
            >>> sb_bell_codes_dat = sb_bell_codes[sb.KEY_TO_BELL_CODES]
            >>> type(sb_bell_codes_dat)
            collections.OrderedDict
            >>> list(sb_bell_codes_dat.keys())
            ['Network Rail codes',
             'Southern Railway codes',
             'Lancashire & Yorkshire Railway codes']
            >>> sb_nr_bell_codes = sb_bell_codes_dat['Network Rail codes']
            >>> type(sb_nr_bell_codes)
            dict
            >>> list(sb_nr_bell_codes.keys())
            ['Codes', 'Notes']
            >>> sb_nr_bell_codes_dat = sb_nr_bell_codes['Codes']
            >>> type(sb_nr_bell_codes_dat)
            pandas.core.frame.DataFrame
            >>> sb_nr_bell_codes_dat.head()
                Code                                       Meaning
            0      1                                Call attention
            1    1-1             Answer telephone [withdrawn 2007]
            2  1-1-6           Police assistance urgently required
            3    1-2  Signaller required on telephone [added 2007]
            4  1-2-1                             Train approaching
        """

        kwargs.update({'data_name': self.KEY_TO_BELL_CODES, 'method': self.collect_bell_codes})

        bell_codes = self._fetch_data_from_file(
            update=update, dump_dir=dump_dir, verbose=verbose, **kwargs)

        return bell_codes
