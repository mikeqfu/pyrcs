"""
Update package data.
"""


import time

from pyhelpers.ops import confirmed

from .collector import LineData, OtherAssets
from .utils import get_site_map


def update_backup_data(verbose=False, time_gap=2):
    """
    Update data of the package's local backup.

    :param verbose: whether to print relevant information in console as the function runs,
        defaults to ``False``
    :type verbose: bool
    :param time_gap: time gap (in seconds) between the updating of different classes
    :type time_gap: int

    **Example**::

        >>> from pyrcs.updater import update_backup_data

        >>> update_backup_data(verbose=True)
    """

    if confirmed("To update the backup resources?"):

        # Site map
        print("Site map:")
        _ = get_site_map(update=True, confirmation_required=False, verbose=verbose)

        # Line data
        ld = LineData(update=True)
        ld.update(verbose=verbose, time_gap=time_gap)

        time.sleep(time_gap)

        # Other assets
        oa = OtherAssets(update=True)
        oa.update(verbose=verbose, time_gap=time_gap)

        if verbose:
            print("\nUpdate finished.")
