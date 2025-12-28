"""
Collects codes of infrastructure features.

This category includes:

    - `HABD and WILD <http://www.railwaycodes.org.uk/misc/habdwild.shtm>`_
    - `Water troughs <http://www.railwaycodes.org.uk/misc/troughs.shtm>`_
    - `Telegraph codes <http://www.railwaycodes.org.uk/misc/telegraph.shtm>`_
    - `Driver/guard buzzer codes <http://www.railwaycodes.org.uk/misc/buzzer.shtm>`_
"""

import inspect
import itertools

from .buzzer import Buzzer
from .habd_wild import HabdWild
from .telegraph import Telegraph
from .trough import WaterTroughs
from .._base import _Base
from ..utils import get_batch_fetch_verbosity, is_homepage_connectable


class Features(_Base):
    """
    A class for collecting data of several infrastructure features, including
    *HABDs and WILDs*, *water troughs locations*, *telegraph code words* and *buzzer codes*.
    """

    #: The name of the data.
    NAME: str = 'Infrastructure features'
    #: The key for accessing the data.
    KEY: str = 'Features'

    #: The key for accessing the data of *HABD* and *WILD*.
    KEY_TO_HABD_WILD: str = HabdWild.KEY
    #: The key for accessing the data of *water troughs*.
    KEY_TO_TROUGH: str = WaterTroughs.KEY
    #: The key for accessing the data of *telegraph codes*.
    KEY_TO_TELEGRAPH: str = Telegraph.KEY
    #: The key for accessing the data of *buzzer codes*.
    KEY_TO_BUZZER: str = Buzzer.KEY

    #: The URL of the main web page for the data.
    URL: str = HabdWild.URL

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

            >>> from pyrcs.other_assets import Features  # from pyrcs import Features
            >>> feats = Features()
            >>> feats.NAME
            'Infrastructure features'
        """

        super().__init__(
            data_dir=data_dir, content_type='catalogue', data_category="other-assets",
            update=update, verbose=verbose)

    @staticmethod
    def _get_classes_in_module(verbose=False):
        # noinspection PyShadowingNames
        """
        Retrieve all classes imported within the current module, excluding locally defined classes.

        This function inspects the global namespace of the module to find all imported classes,
        excluding those defined within the module itself. The ``_Base`` class is also excluded.

        :param verbose: Whether to print the imported class names and objects to the console.
        :type verbose: bool
        :return: A list of tuples containing the names and objects of imported classes.
        :rtype: list[tuple[str, type]]

        **Examples**::

            >>> from pyrcs.other_assets import Features  # from pyrcs import Features
            >>> feats = Features()
            >>> imported_classes = feats._get_classes_in_module()
            >>> imported_classes
            [('HABDWILD', pyrcs.other_assets.habd_wild.HABDWILD),
             ('Buzzer', pyrcs.other_assets.buzzer.Buzzer),
             ('Telegraph', pyrcs.other_assets.telegraph.Telegraph),
             ('WaterTroughs', pyrcs.other_assets.trough.WaterTroughs)]
        """

        # Get the current module's global namespace
        current_module = globals()

        # Filter for classes
        imported_classes = []
        for name, obj in current_module.items():
            if inspect.isclass(obj) and obj.__module__ != __name__ and name != '_Base':
                imported_classes.append((name, obj))

        if verbose:  # Get and print all classes
            for name, cls in imported_classes:
                print(f"Imported class name: {name}, Imported class: {cls}")

        return imported_classes

    def fetch_codes(self, update=False, dump_dir=None, verbose=False, **kwargs):
        """
        Fetches data of infrastructure features.

        Including:

            - `HABD and WILD <http://www.railwaycodes.org.uk/misc/habdwild.shtm>`_
            - `Water troughs <http://www.railwaycodes.org.uk/misc/troughs.shtm>`_
            - `Telegraph codes <http://www.railwaycodes.org.uk/misc/telegraph.shtm>`_
            - `Driver/guard buzzer codes <http://www.railwaycodes.org.uk/misc/buzzer.shtm>`_

        :param update: Whether to check for updates to the package data; defaults to ``False``.
        :type update: bool
        :param dump_dir: The path to a directory where the data file will be saved;
            defaults to ``None``.
        :type dump_dir: str | None
        :param verbose: Whether to print relevant information to the console; defaults to ``False``.
        :type verbose: bool | int
        :return: A dictionary containing the data of features codes and
            the date they were last updated.
        :rtype: dict

        **Examples**::

            >>> from pyrcs.other_assets import Features  # from pyrcs import Features
            >>> feats = Features()
            >>> feats_codes = feats.fetch_codes()
            >>> type(feats_codes)
            dict
            >>> list(feats_codes.keys())
            ['Features', 'Last updated date']
            >>> feats.KEY
            'Features'
            >>> feats_codes_dat = feats_codes[feats.KEY]
            >>> type(feats_codes_dat)
            dict
            >>> list(feats_codes_dat.keys())
            ['Buzzer codes', 'HABD and WILD', 'Telegraphic codes', 'Water troughs']
            >>> water_troughs_locations = feats_codes_dat[feats.KEY_TO_TROUGH]
            >>> type(water_troughs_locations)
            pandas.core.frame.DataFrame
            >>> water_troughs_locations.head()
                ELR  ... Length (Yard)
            0   BEI  ...           NaN
            1   BHL  ...    620.000000
            2  CGJ2  ...      0.666667
            3  CGJ6  ...    561.000000
            4  CGJ6  ...    560.000000
            [5 rows x 6 columns]
            >>> hw_codes_dat = feats_codes_dat[feats.KEY_TO_HABD_WILD]
            >>> type(hw_codes_dat)
            dict
            >>> list(hw_codes_dat.keys())
            ['HABD', 'WILD']
            >>> habd_dat = hw_codes_dat['HABD']
            >>> type(habd_dat)
            pandas.core.frame.DataFrame
            >>> habd_dat.head()
                ELR  ...                                              Notes
            0  BAG2  ...
            1  BAG2  ...  installed 29 September 1997, later moved to 74...
            2  BAG2  ...                             previously at 74m 51ch
            3  BAG2  ...                          removed 29 September 1997
            4  BAG2  ...           present in 1969, later moved to 89m 00ch
            [5 rows x 5 columns]
            >>> wild_dat = hw_codes_dat['WILD']
            >>> type(wild_dat)
            pandas.core.frame.DataFrame
            >>> wild_dat.head()
                ELR  ...                                              Notes
            0  AYR3  ...
            1  BAG2  ...
            2  BML1  ...
            3  BML1  ...
            4  CGJ3  ...  moved to 183m 68ch from 8 September 2018 / mov...
            [5 rows x 5 columns]
        """

        verbose_ = get_batch_fetch_verbosity(data_dir=dump_dir, verbose=verbose)

        features_codes_dat = []

        for (_, cls) in self._get_classes_in_module():
            dat = cls().fetch_codes(
                update=update, verbose=verbose_ if is_homepage_connectable() else False, **kwargs)
            features_codes_dat.append(dat)

        features_codes = {
            self.KEY: {next(iter(x)): next(iter(x.values())) for x in features_codes_dat},
            self.KEY_TO_LAST_UPDATED_DATE:
                max(next(itertools.islice(iter(x.values()), 1, 2)) for x in features_codes_dat),
        }

        if dump_dir is not None:
            self._save_data_to_file(
                data=features_codes, data_name=self.KEY, dump_dir=dump_dir, verbose=verbose)

        return features_codes
