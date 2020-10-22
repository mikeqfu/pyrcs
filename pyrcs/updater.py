"""
Update package data.
"""

import os
import re
import time
from urllib.parse import urljoin

import bs4
import requests
from pyhelpers.ops import confirmed
from pyhelpers.store import load_pickle, save_pickle

from . import LineData, OtherAssets
from .utils import cd_dat, fake_requests_headers, homepage_url


def collect_site_map(confirmation_required=True):
    """
    Collect data of the `site map <http://www.railwaycodes.org.uk/misc/sitemap.shtm>`_
    from source web page.

    :param confirmation_required: whether to prompt a message for confirmation to proceed,
        defaults to ``True``
    :type confirmation_required: bool
    :return: dictionary of site map data
    :rtype: dict

    **Examples**::

        >>> from pyrcs.updater import collect_site_map

        >>> site_map_dat = collect_site_map()
        To collect the site map? [No]|Yes: yes

        >>> type(site_map_dat)
        <class 'dict'>
        >>> print(list(site_map_dat.keys()))
        ['Home', 'Line data', 'Other assets', '"Legal/financial" lists', 'Miscellaneous']
    """

    if confirmed("To collect the site map?", confirmation_required=confirmation_required):

        url = urljoin(homepage_url(), '/misc/sitemap.shtm')
        source = requests.get(url, headers=fake_requests_headers())
        soup = bs4.BeautifulSoup(source.text, 'lxml')

        # <h3>
        h3 = [x.get_text(strip=True) for x in soup.find_all('h3')]

        site_map = {}

        # Next <ol>
        next_ol = soup.find('h3').find_next('ol')

        for i in range(len(h3)):

            li_tag, ol_tag = next_ol.findChildren('li'), next_ol.findChildren('ol')

            if not ol_tag:
                dat_ = [x.find('a').get('href') for x in li_tag]
                if len(dat_) == 1:
                    dat = urljoin(homepage_url(), dat_[0])
                else:
                    dat = [urljoin(homepage_url(), x) for x in dat_]
                site_map.update({h3[i]: dat})

            else:
                site_map_ = {}
                for ol in ol_tag:
                    k = ol.find_parent('ol').find_previous('li').get_text(strip=True)

                    if k not in site_map_.keys():
                        sub_li, sub_ol = ol.findChildren('li'), ol.findChildren('ol')

                        if sub_ol:
                            cat0 = [x.get_text(strip=True) for x in sub_li
                                    if not x.find('a')]
                            dat0 = [[urljoin(homepage_url(), a.get('href'))
                                     for a in x.find_all('a')] for x in sub_ol]
                            cat_name = ol.find_previous('li').get_text(strip=True)
                            if cat0:
                                site_map_.update({cat_name: dict(zip(cat0, dat0))})
                            else:
                                site_map_.update(
                                    {cat_name: [x_ for x in dat0 for x_ in x]})
                            # cat_ = [x for x in cat_ if x not in cat0]

                        else:
                            cat_name_ = ol.find_previous('li').get_text(strip=True)
                            pat = r'.+(?= \(the thousands of mileage files)'
                            cat_name = re.search(pat, cat_name_).group(0) \
                                if re.match(pat, cat_name_) else cat_name_

                            dat0 = [urljoin(homepage_url(), x.a.get('href'))
                                    for x in sub_li]

                            site_map_.update({cat_name: dat0})

                site_map.update({h3[i]: site_map_})

            if i < len(h3) - 1:
                next_ol = next_ol.find_next('h3').find_next('ol')

        return site_map


def fetch_site_map(update=False, confirmation_required=True, verbose=False):
    """
    Fetch the `site map <http://www.railwaycodes.org.uk/misc/sitemap.shtm>`_
    from the package data.

    :param update: whether to check on update and proceed to update the package data,
        defaults to ``False``
    :type update: bool
    :param confirmation_required: whether to prompt a message for confirmation to proceed,
        defaults to ``True``
    :type confirmation_required: bool
    :param verbose: whether to print relevant information in console as the function runs,
        defaults to ``False``
    :type verbose: bool, int
    :return: dictionary of site map data
    :rtype: dict

    **Examples**::

        >>> from pyrcs.updater import fetch_site_map

        >>> site_map_dat = fetch_site_map()

        >>> type(site_map_dat)
        <class 'dict'>
        >>> print(site_map_dat['Home'])
        http://www.railwaycodes.org.uk/index.shtml
    """

    path_to_pickle = cd_dat("site-map.pickle", mkdir=True)

    print("Getting site map", end=" ... ") if verbose == 2 else ""

    if os.path.isfile(path_to_pickle) and not update:
        site_map = load_pickle(path_to_pickle)

    else:
        try:
            if verbose == 2:
                print("The package data is unavailable or needs to be updated ... ")
            site_map = collect_site_map(confirmation_required=confirmation_required)
            print("Done.") if verbose == 2 else ""
            save_pickle(site_map, path_to_pickle, verbose=verbose)
        except Exception as e:
            site_map = None
            print("Failed. {}".format(e))

    return site_map


def update_backup_data(verbose=False, time_gap=5):
    """
    Update package data.

    :param verbose: whether to print relevant information in console as the function runs,
        defaults to ``False``
    :type verbose: bool
    :param time_gap: time gap (in seconds) between the updating of different classes
    :type time_gap: int

    **Example**::

        >>> from pyrcs.updater import update_backup_data

        >>> update_backup_data(verbose=True)
    """

    if confirmed("To update resources? "):

        # Site map
        _ = fetch_site_map(update=True, confirmation_required=False, verbose=verbose)

        line_dat = LineData(update=True)

        # ELR and mileages
        _ = line_dat.ELRMileages.fetch_elr(update=True, verbose=verbose)

        time.sleep(time_gap)

        # Electrification
        _ = line_dat.Electrification.fetch_elec_codes(update=True,
                                                      verbose=verbose)

        time.sleep(time_gap)

        # Location
        _ = line_dat.LocationIdentifiers.fetch_location_codes(update=True,
                                                              verbose=verbose)

        time.sleep(time_gap)

        # Line of routes
        _ = line_dat.LOR.get_keys_to_prefixes(prefixes_only=True, update=True,
                                              verbose=verbose)
        _ = line_dat.LOR.get_keys_to_prefixes(prefixes_only=False, update=True,
                                              verbose=verbose)
        _ = line_dat.LOR.get_lor_page_urls(update=True, verbose=verbose)
        _ = line_dat.LOR.fetch_lor_codes(update=True, verbose=verbose)
        _ = line_dat.LOR.fetch_elr_lor_converter(update=True, verbose=verbose)

        time.sleep(time_gap)

        # Line names
        _ = line_dat.LineNames.fetch_line_names(update=True, verbose=verbose)

        time.sleep(time_gap)

        # Track diagrams
        _ = line_dat.TrackDiagrams.fetch_sample_catalogue(update=True,
                                                          verbose=verbose)

        time.sleep(time_gap)

        other_assets = OtherAssets(update=True)

        # Signal boxes
        _ = other_assets.SignalBoxes.fetch_signal_box_prefix_codes(update=True,
                                                                   verbose=verbose)
        _ = other_assets.SignalBoxes.fetch_non_national_rail_codes(update=True,
                                                                   verbose=verbose)

        time.sleep(time_gap)

        # Tunnels
        _ = other_assets.Tunnels.fetch_tunnel_lengths(update=True,
                                                      verbose=verbose)

        time.sleep(time_gap)

        # Viaducts
        _ = other_assets.Viaducts.fetch_railway_viaducts(update=True, verbose=verbose)

        time.sleep(time_gap)

        # Stations
        _ = other_assets.Stations.fetch_railway_station_data(update=True, verbose=verbose)

        time.sleep(time_gap)

        # Depots
        _ = other_assets.Depots.fetch_depot_codes(update=True, verbose=verbose)

        time.sleep(time_gap)

        # Features
        _ = other_assets.Features.fetch_features_codes(update=True, verbose=verbose)

        if verbose:
            print("\nUpdate finished.")
