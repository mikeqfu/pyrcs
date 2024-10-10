"""
Test the module :py:mod:`pyrcs.utils`.
"""

import pandas as pd
import pytest


def test_home_page_url():
    from pyrcs.utils import home_page_url

    assert home_page_url() == 'http://www.railwaycodes.org.uk/'


def test_is_str_float():
    from pyrcs.utils import is_str_float

    assert is_str_float('') is False
    assert is_str_float('a') is False
    assert is_str_float('1')
    assert is_str_float('1.1')


def test_validate_initial(capfd):
    from pyrcs.utils import validate_initial

    assert validate_initial('x') == 'X'

    assert validate_initial('x', as_is=True) == 'x'

    with pytest.raises(Exception) as e:
        validate_initial('xyz')
        assert str(e.value) == '`x` must be a single letter.'


def test_collect_in_fetch_verbose():
    from pyrcs.utils import collect_in_fetch_verbose

    assert collect_in_fetch_verbose(data_dir="data", verbose=True) is False


def test_fetch_all_verbose():
    from pyrcs.utils import fetch_all_verbose

    assert fetch_all_verbose(data_dir="data", verbose=True) is False


def test_confirm_msg():
    from pyrcs.utils import confirm_msg

    msg = confirm_msg(data_name="Railway Codes")
    assert msg == 'To collect data of Railway Codes\n?'


def test_print_collect_msg(capfd):
    from pyrcs.utils import print_collect_msg

    print_collect_msg("Railway Codes", verbose=2, confirmation_required=True)
    out, _ = capfd.readouterr()
    assert out == 'Collecting the data ... '

    print_collect_msg("Railway Codes", verbose=2, confirmation_required=False)
    out, _ = capfd.readouterr()
    assert out == 'Collecting the data of "Railway Codes" ... '


def test_print_inst_conn_err(capfd):
    from pyrcs.utils import print_inst_conn_err

    print_inst_conn_err(verbose=True)
    out, _ = capfd.readouterr()
    assert out == 'The Internet connection is not available.\n'

    print_inst_conn_err(update=True, verbose=True, e='')
    out, _ = capfd.readouterr()
    assert out == 'Failed to update the data.\n'


def test_print_void_msg(capfd):
    from pyrcs.utils import print_void_msg

    print_void_msg(data_name="Railway Codes", verbose=True)
    out, _ = capfd.readouterr()
    assert out == 'No data of "Railway Codes" has been freshly collected.\n'


def test_cd_data():
    from pyrcs.utils import cd_data
    import os

    path_to_dat_dir = cd_data(data_dir="data")
    assert os.path.relpath(path_to_dat_dir) == 'pyrcs\\data'


def test_init_data_dir():
    from pyrcs.utils import init_data_dir
    from pyrcs.line_data import Bridges
    import os

    bridges = Bridges()

    dat_dir, current_dat_dir = init_data_dir(bridges, data_dir="data", category="line-data")
    assert os.path.relpath(dat_dir) == 'data'

    assert os.path.relpath(current_dat_dir) == 'data'


def test_make_file_pathname():
    from pyrcs.utils import make_file_pathname
    from pyrcs.line_data import Bridges
    import os

    bridges = Bridges()

    example_pathname = make_file_pathname(bridges, data_name="example-data", ext=".pickle")
    assert os.path.relpath(example_pathname) == 'pyrcs\\data\\line-data\\bridges\\example-data.pickle'


def test_fetch_location_names_errata():
    from pyrcs.utils import fetch_location_names_errata

    repl_dict = fetch_location_names_errata()
    assert isinstance(repl_dict, dict)

    repl_dict = fetch_location_names_errata(regex=True, as_dataframe=True)
    assert isinstance(repl_dict, pd.DataFrame)


def test_fetch_data_from_file(capfd):
    from pyrcs.utils import fetch_data_from_file

    data = fetch_data_from_file(
        cls_instance=None, method=None, data_name=None, ext=None, update=None, dump_dir=None,
        verbose=True)
    out, _ = capfd.readouterr()
    assert out == "Some errors occurred when fetching the data. " \
                  "'NoneType' object has no attribute 'lower'.\n"
    assert data is None


if __name__ == '__main__':
    pytest.main()
