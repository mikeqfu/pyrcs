"""Update package data."""

import time

from pyhelpers.ops import confirmed

from .collector import LineData, OtherAssets
from .parser import get_site_map
from .utils import is_home_connectable, print_conn_err


def _update_prepacked_data(verbose=False, interval=5, **kwargs):
    """
    Updates pre-packed data.

    :param verbose: Whether to print relevant information to the console; defaults to ``True``.
    :type verbose: bool | int
    :param interval: A time gap (in seconds) between updating different classes; defaults to ``5``.
    :type interval: int or float

    **Examples**::

        >>> from pyrcs._updater import _update_prepacked_data
        >>> _update_prepacked_data(verbose=True)
    """

    if not is_home_connectable():
        print_conn_err(verbose=verbose)
        print("Unable to update the data.")

    else:
        if confirmed("To update the backup/data resources\n?", **kwargs):

            # Site map
            print("\nSite map:")
            _ = get_site_map(update=True, confirmation_required=False, verbose=verbose)

            time.sleep(interval)

            # Line data
            ld = LineData(update=True)
            ld.update(confirmation_required=False, verbose=verbose, interval=interval)

            time.sleep(interval)

            # Other assets
            oa = OtherAssets(update=True)
            oa.update(confirmation_required=False, verbose=verbose, interval=interval)

            if verbose:
                print("\nUpdate finished.")
