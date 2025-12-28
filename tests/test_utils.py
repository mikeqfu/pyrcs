"""
Test the module :py:mod:`pyrcs.utils`.
"""

import unittest.mock

import pandas as pd
import pytest


def test_home_page_url():
    from pyrcs.utils import home_page_url

    assert home_page_url() == 'http://www.railwaycodes.org.uk/'


def test_is_str_float():
    from pyrcs.utils import is_str_float

    assert not is_str_float(None)
    assert not is_str_float('')
    assert not is_str_float('a')
    assert is_str_float('1')
    assert is_str_float('1.1')
    assert not is_str_float('nan', finite_only=True)
    assert is_str_float('inf')

    assert not is_str_float(is_str_float)


def test_validate_initial(capfd):
    from pyrcs.utils import validate_initial

    assert validate_initial('x') == 'X'
    assert validate_initial('x', as_is=True) == 'x'

    with pytest.raises(TypeError, match="`initial` must be a string"):
        _ = validate_initial(1)

    with pytest.raises(ValueError, match="it must be a single letter"):
        _ = validate_initial('xyz')


def test_get_collect_verbosity_for_fetch():
    from pyrcs.utils import get_collect_verbosity_for_fetch

    assert not get_collect_verbosity_for_fetch(data_dir="data", verbose=True)
    assert not get_collect_verbosity_for_fetch(data_dir="data", verbose=2)

    assert get_collect_verbosity_for_fetch(data_dir="", verbose=True)
    assert not get_collect_verbosity_for_fetch(data_dir="", verbose=False)
    assert get_collect_verbosity_for_fetch(data_dir="", verbose=2) == 2


def test_get_batch_fetch_verbosity():
    from pyrcs.utils import get_batch_fetch_verbosity

    assert not get_batch_fetch_verbosity(data_dir="data", verbose=True)
    assert get_batch_fetch_verbosity(data_dir="", verbose=True)

    with unittest.mock.patch(f'pyrcs.utils.is_home_connectable') as mock_connectable:
        mock_connectable.return_value = False
        assert not get_batch_fetch_verbosity(data_dir="data", verbose=2)
        assert not get_batch_fetch_verbosity(data_dir="", verbose=True)


def test_format_confirmation_prompt():
    from pyrcs.utils import format_confirmation_prompt

    msg = format_confirmation_prompt(data_name="Railway Codes")
    assert msg == 'To collect data of Railway Codes\n?'


@pytest.mark.parametrize('initial', [None, 'abc'])
@pytest.mark.parametrize('confirmation_required', [True, False])
def test_print_collection_message(capfd, initial, confirmation_required):
    from pyrcs.utils import print_collection_message

    data_name = "Railway Codes"

    # print_collection_message(data_name, verbose=True, confirmation_required=confirmation_required)
    # out, _ = capfd.readouterr()
    # assert out.startswith('Collecting the data ... ')
    #
    # print_collection_message(data_name, verbose=True, confirmation_required=False)
    # out, _ = capfd.readouterr()
    # assert out.startswith(f'Collecting the data of {data_name} ... ')

    print_collection_message(
        data_name=data_name, initial=initial, verbose=True,
        confirmation_required=confirmation_required)
    out, _ = capfd.readouterr()
    if initial and not confirmation_required:
        assert out.startswith(f'Collecting the data of {data_name} ({initial}) ... ')
    elif confirmation_required:
        assert out.startswith('Collecting the data ... ')
    else:
        assert out.startswith(f'Collecting the data of {data_name} ... ')


def test_print_instance_connection_error(capfd):
    from pyrcs.utils import print_instance_connection_error

    assert print_instance_connection_error(verbose=False) is None

    print_instance_connection_error(verbose=2)
    out, _ = capfd.readouterr()
    assert out == 'Failed. The Internet connection is not available.\n'

    print_instance_connection_error(update=True, verbose=True)
    out, _ = capfd.readouterr()
    assert out == 'The Internet connection is not available. Failed to update the data.\n'

    with pytest.raises(TypeError, match="exceptions"):
        print_instance_connection_error(verbose=True, raise_error=True)
        out, _ = capfd.readouterr()
        assert out == 'The Internet connection is not available.\n'


def test_print_void_collection_message(capfd):
    from pyrcs.utils import print_void_collection_message

    print_void_collection_message(data_name="Railway Codes", verbose=True)
    out, _ = capfd.readouterr()
    assert out == 'No data of "Railway Codes" has been freshly collected.\n'


def test_cd_data():
    from pyrcs.utils import cd_data
    from pyhelpers.dirs import normalize_pathname
    import os

    path_to_dat_dir = cd_data(data_dir="data")
    assert normalize_pathname(os.path.relpath(path_to_dat_dir)) == normalize_pathname('pyrcs\\data')


def test_fetch_location_names_errata():
    from pyrcs.utils import fetch_location_names_errata

    repl_dict = fetch_location_names_errata()
    assert isinstance(repl_dict, dict)

    repl_dict = fetch_location_names_errata(regex=True, as_dataframe=True)
    assert isinstance(repl_dict, pd.DataFrame)


@pytest.mark.parametrize('regex', [False, True])
def test__update_location_names_errata(regex, monkeypatch, capfd):
    from pyrcs.utils import _update_location_names_errata

    new_items = {"Leeds Balm Rd Loco (Fhh)": "Leeds Balm Road Loco Freightliner Heavy Haul"}

    monkeypatch.setattr('builtins.input', lambda _: "Yes")
    _update_location_names_errata(new_items, regex=regex, verbose=True)
    out, _ = capfd.readouterr()
    assert "Updating" in out and "Done." in out

    monkeypatch.setattr('builtins.input', lambda _: "No")
    _update_location_names_errata(new_items, regex=False, verbose=True)
    out, _ = capfd.readouterr()
    assert "Cancelled." in out


if __name__ == '__main__':
    pytest.main()
