"""
Update package data.
"""

import time

from .collector import LineData, OtherAssets
from .utils import *


def update_prepacked_data(verbose=False, interval=5):
    """
    Update pre-packed data.

    :param verbose: whether to print relevant information in console, defaults to ``False``
    :type verbose: bool
    :param interval: time gap (in seconds) between updating different classes, defaults to ``5``
    :type interval: int

    **Example**::

        >>> from pyrcs.updater import update_prepacked_data

        >>> update_prepacked_data(verbose=True)
    """

    if not is_home_connectable():
        print_connection_error(verbose=verbose)
        print("Unable to update the data.")

    else:
        if confirmed("To update the backup resources\n?"):

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
