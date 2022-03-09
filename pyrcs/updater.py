"""
Update package data.
"""


import time

from .collector import LineData, OtherAssets
from .utils import *


def update_backup_data(verbose=False, time_gap=5):
    """
    Update data of the package's local backup.

    :param verbose: whether to print relevant information in console, defaults to ``False``
    :type verbose: bool
    :param time_gap: time gap (in seconds) between updating different classes, defaults to ``5``
    :type time_gap: int

    **Example**::

        >>> from pyrcs.updater import update_backup_data

        >>> update_backup_data(verbose=True)
    """

    if not is_home_connectable():
        print_connection_error(verbose=verbose)
        print("Unable to update the data.")

    else:
        if confirmed("To update the backup resources\n?"):

            # Site map
            print("\nSite map:")
            _ = get_site_map(update=True, confirmation_required=False, verbose=verbose)

            time.sleep(time_gap)

            # Line data
            ld = LineData(update=True)
            ld.update(confirmation_required=False, verbose=verbose, time_gap=time_gap)

            time.sleep(time_gap)

            # Other assets
            oa = OtherAssets(update=True)
            oa.update(confirmation_required=False, verbose=verbose, time_gap=time_gap)

            if verbose:
                print("\nUpdate finished.")
