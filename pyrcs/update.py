""" Update package data """

import os
import re
import time
from urllib.parse import urljoin

import bs4
import requests
from pyhelpers.ops import confirmed
from pyhelpers.store import load_pickle, save_pickle

from pyrcs.line_data import LineData
from pyrcs.other_assets import OtherAssets
from utils import cd_dat
from utils import fake_requests_headers


def source_url():
    """
    The homepage URL of the data source.

    :return: homepage URL
    :rtype: str
    """

    return 'http://www.railwaycodes.org.uk/'


def collect_site_map():
    """
    Collect data of the site map.

    :return: dictionary of site map data
    :rtype: dict
    """

    if confirmed("To collect the site map? "):

        url = urljoin(source_url(), '/misc/sitemap.shtm')
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
                    dat = urljoin(source_url(), dat_[0])
                else:
                    dat = [urljoin(source_url(), x) for x in dat_]
                site_map.update({h3[i]: dat})

            else:
                site_map_ = {}
                for ol in ol_tag:
                    k = ol.find_parent('ol').find_previous('li').get_text(strip=True)

                    if k not in site_map_.keys():
                        sub_li, sub_ol = ol.findChildren('li'), ol.findChildren('ol')

                        if sub_ol:
                            cat0 = [x.get_text(strip=True) for x in sub_li if not x.find('a')]
                            dat0 = [[urljoin(source_url(), a.get('href')) for a in x.find_all('a')] for x in sub_ol]
                            cat_name = ol.find_previous('li').get_text(strip=True)
                            if cat0:
                                site_map_.update({cat_name: dict(zip(cat0, dat0))})
                            else:
                                site_map_.update({cat_name: [x_ for x in dat0 for x_ in x]})
                            # cat_ = [x for x in cat_ if x not in cat0]

                        else:
                            cat_name_ = ol.find_previous('li').get_text(strip=True)
                            pat = r'.+(?= \(the thousands of mileage files)'
                            cat_name = re.search(pat, cat_name_).group(0) if re.match(pat, cat_name_) else cat_name_

                            dat0 = [urljoin(source_url(), x.a.get('href')) for x in sub_li]

                            site_map_.update({cat_name: dat0})

                site_map.update({h3[i]: site_map_})

            if i < len(h3) - 1:
                next_ol = next_ol.find_next('h3').find_next('ol')

        return site_map


def fetch_site_map(update=False, verbose=False):
    """
    Fetch the site map from the package data.

    :param update: whether to check on update and proceed to update the package data, defaults to ``False``
    :type update: bool
    :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
    :type verbose: bool
    :return: dictionary of site map data
    :rtype: dict

    **Examples**::

        from pyrcs.update import fetch_site_map

        verbose = True

        update = False
        fetch_site_map(update, verbose)

        update = True
        fetch_site_map(update, verbose)
    """

    path_to_pickle = cd_dat("site-map.pickle")

    print("Getting site map", end=" ... ") if verbose else ""

    if os.path.isfile(path_to_pickle) and not update:
        site_map = load_pickle(path_to_pickle)

    else:
        try:
            print("The package data is unavailable or needs to be updated ... ") if verbose else ""
            site_map = collect_site_map()
            print("Done.") if verbose else ""
            save_pickle(site_map, path_to_pickle, verbose=verbose)
        except Exception as e:
            site_map = None
            print("Failed. {}".format(e))

    return site_map


def update_backup_data(verbose=False):
    """
    Update package data.

    :param verbose: whether to print relevant information in console as the function runs, defaults to ``False``
    :type verbose: bool

    **Example**::

        verbose = True

        update_backup_data(verbose)
    """

    if confirmed("To update resources? "):

        line_dat = LineData()

        # ELR and mileages
        _ = line_dat.ELRMileages.fetch_elr(update=True, verbose=verbose)

        time.sleep(10)

        # Electrification
        _ = line_dat.Electrification.fetch_electrification_codes(update=True, verbose=verbose)

        time.sleep(10)

        # Location
        _ = line_dat.LocationIdentifiers.fetch_location_codes(update=True, verbose=verbose)
        _ = line_dat.LocationIdentifiers.fetch_additional_crs_note(update=True, verbose=verbose)
        _ = line_dat.LocationIdentifiers.fetch_other_systems_codes(update=True, verbose=verbose)

        time.sleep(10)

        # Line of routes
        _ = line_dat.LOR.fetch_lor_codes(update=True, verbose=verbose)
        _ = line_dat.LOR.fetch_elr_lor_converter(update=True, verbose=verbose)

        time.sleep(10)

        # Line names
        _ = line_dat.LineNames.fetch_line_names(update=True, verbose=verbose)

        """
        # Track diagrams
        """

        time.sleep(10)

        other_assets = OtherAssets()

        # Signal boxes
        _ = other_assets.SignalBoxes.fetch_signal_box_prefix_codes(update=True, verbose=verbose)
        _ = other_assets.SignalBoxes.fetch_non_national_rail_codes(update=True, verbose=verbose)

        time.sleep(10)

        # Tunnels
        _ = other_assets.Tunnels.fetch_railway_tunnel_lengths(update=True, verbose=verbose)

        time.sleep(10)

        # Viaducts
        _ = other_assets.Viaducts.fetch_railway_viaducts(update=True, verbose=verbose)

        time.sleep(10)

        # Stations
        _ = other_assets.Stations.fetch_station_locations(update=True, verbose=verbose)

        time.sleep(10)

        # Depots
        _ = other_assets.Depots.fetch_depot_codes(update=True, verbose=verbose)

        if verbose:
            print("\nUpdate finished.")
