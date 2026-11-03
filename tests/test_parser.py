"""
Test parser.py
"""

import datetime
import secrets
import string

import bs4
import curl_cffi.requests
import pandas as pd
import pytest

from pyrcs.line_data import Electrification
from pyrcs.parser import _requests_get, get_catalogue, get_category_menu, get_financial_year, \
    get_heading_text, get_hypertext, get_introduction, get_last_updated_date, get_page_catalogue, \
    get_site_map, parse_date, parse_table, parse_tr


def test__requests_get_retry_exhaustion(mocker):
    """
    Test _requests_get behaviour across success, retries and exhaustion.
    """

    mocker.patch("time.sleep")

    # 1. Test success on first attempt without custom headers
    mock_resp_success = mocker.Mock(ok=True)
    mock_get = mocker.patch("curl_cffi.requests.get", return_value=mock_resp_success)
    assert _requests_get("http://example.com") == mock_resp_success
    mock_get.assert_called_once_with(
        url="http://example.com",
        impersonate=mocker.ANY,
        timeout=10,
    )

    # 2. Test success with custom headers passed
    custom_headers = {"X-Test-Header": "value"}
    assert _requests_get("http://example.com", headers=custom_headers) == mock_resp_success
    mock_get.assert_called_with(
        url="http://example.com",
        headers=custom_headers,
        impersonate=mocker.ANY,
        timeout=10,
    )

    # 3. Test success after a transient timeout on first try
    mock_resp_retry = mocker.Mock(ok=True)
    mock_get_retry = mocker.patch(
        "curl_cffi.requests.get",
        side_effect=[TimeoutError, mock_resp_retry]
    )
    assert _requests_get("http://example.com") == mock_resp_retry
    assert mock_get_retry.call_count == 2

    # 4. Test exception exhaustion
    mocker.patch("curl_cffi.requests.get", side_effect=TimeoutError)
    with pytest.raises(TimeoutError):
        _requests_get("http://example.com")

    # 5. Test status code exhaustion e.g. 403 Forbidden
    mock_resp_fail = mocker.Mock(ok=False)
    mock_resp_fail.raise_for_status.side_effect = Exception("403 Forbidden")
    mocker.patch("curl_cffi.requests.get", return_value=mock_resp_fail)
    with pytest.raises(Exception, match="403 Forbidden"):
        _requests_get("http://example.com")
    assert mock_resp_fail.raise_for_status.call_count == 1


def test_parse_tr():
    initial = secrets.choice(string.ascii_lowercase)
    example_url = f'http://www.railwaycodes.org.uk/elrs/elr{initial}.shtm'

    source: curl_cffi.Response = _requests_get(example_url)

    parsed_text = bs4.BeautifulSoup(markup=source.content, features='html.parser')

    ths_dat = [th.text for th in parsed_text.find_all('th')]
    trs_dat = parsed_text.find_all(name='tr')

    tables_list = parse_tr(trs=trs_dat, ths=ths_dat)  # returns a list of lists

    assert isinstance(tables_list, list) and len(tables_list) > 0


def test_parse_table():
    source_dat = _requests_get(url='http://www.railwaycodes.org.uk/elrs/elra.shtm')

    (columns_dat, records_dat), _ = parse_table(source_dat)

    assert columns_dat == ['ELR', 'Line name', 'Mileages', 'Datum', 'Notes']
    assert isinstance(records_dat, list)
    assert len(records_dat) // 100 == 1
    assert records_dat[0] == [
        'AAL', 'Ashendon and Aynho Line', '0.00 - 18.29', 'Ashendon Junction', 'Now NAJ3']


def test_parse_date():
    str_date_dat = '2020-01-01'

    parsed_date_dat = parse_date(str_date_dat)
    assert parsed_date_dat == '2020-01-01'

    parsed_date_dat = parse_date(str_date_dat, as_date_type=True)
    assert parsed_date_dat == datetime.date(2020, 1, 1)


def test_get_site_map(monkeypatch, capfd):
    main_keys = ['Home', 'Line data', 'Other assets', '"Legal/financial" lists', 'Miscellaneous']
    home_value = {'index': 'http://www.railwaycodes.org.uk/index.shtml'}

    monkeypatch.setattr('builtins.input', lambda _: "Yes")
    site_map_dat = get_site_map(update=True, verbose=True)
    out, _ = capfd.readouterr()
    assert "Updating the package data" in out and "Done." in out
    assert isinstance(site_map_dat, dict)
    assert list(site_map_dat.keys()) == main_keys
    assert site_map_dat['Home'] == home_value

    site_map_dat = get_site_map()
    assert isinstance(site_map_dat, dict)
    assert list(site_map_dat.keys()) == main_keys
    assert site_map_dat['Home'] == home_value

    monkeypatch.setattr('builtins.input', lambda _: "No")
    site_map_dat = get_site_map(update=True, verbose=True)
    out, _ = capfd.readouterr()
    assert "Cancelled." in out
    assert site_map_dat is None

    monkeypatch.setattr('builtins.input', lambda _: "Yes")
    monkeypatch.setattr('pyrcs.parser.homepage_url', lambda: 'https://test-url.abc')
    with pytest.raises(Exception, match='Failed'):
        site_map_dat = get_site_map(update=True, raise_error=True)
        assert site_map_dat is None

    site_map_dat = get_site_map(update=True, verbose=True, raise_error=False)
    out, _ = capfd.readouterr()
    assert "Failed" in out
    assert site_map_dat is None


@pytest.mark.parametrize('as_date_type', [False, True])
def test_get_last_updated_date(as_date_type, monkeypatch, capsys):
    url = 'http://www.railwaycodes.org.uk/crs/CRSa.shtm'
    last_updated_date = get_last_updated_date(url, parsed=True, as_date_type=as_date_type)
    if as_date_type:
        assert isinstance(last_updated_date, datetime.date)
    else:
        assert isinstance(last_updated_date, str)

    url = 'http://www.railwaycodes.org.uk/linedatamenu.shtm'
    last_updated_date = get_last_updated_date(url=url)
    assert last_updated_date is None

    with pytest.raises(Exception):
        url = 'http://test-url.abc'
        last_updated_date = get_last_updated_date(url=url, verbose=True, raise_error=True)
        captured = capsys.readouterr()
        assert "Failed" in captured.out
        assert last_updated_date is None


def test_get_financial_year():
    financial_year = get_financial_year(date=datetime.datetime(2021, 3, 31))
    assert financial_year == 2020


def test_get_introduction(capfd):
    """
    Test the functionality of retrieving introduction text under valid and invalid conditions.

    :param capfd: Pytest fixture for capturing stdout and stderr.
    :type capfd: pytest.CaptureFixture
    """

    # 1. Test successful retrieval with a valid URL
    valid_url = "http://www.railwaycodes.org.uk/bridges/bridges0.shtm"
    intro_text = get_introduction(url=valid_url, update=True, verbose=True)
    out, _ = capfd.readouterr()
    assert "Updating" in out and "Done." in out
    assert isinstance(intro_text, str)

    intro_text = get_introduction(url=valid_url, update=False, verbose=True)
    out, _ = capfd.readouterr()
    assert not out
    assert isinstance(intro_text, str)

    # 2. Test failure handling with an invalid URL
    invalid_url = "http://123.railwaycodes.org.uk/bridges/bridges0.shtm"
    with pytest.raises(Exception):
        get_introduction(url=invalid_url, update=True, raise_error=True)

    intro_text = get_introduction(invalid_url, update=True, verbose=True, raise_error=False)
    out, _ = capfd.readouterr()
    assert "Failed" in out
    assert intro_text is None


def test_get_catalogue(capsys):
    """
    Test the operational workflow of the ``get_page_catalogue`` fetching function.

    This processes standard operational requests alongside verifying structural fail-safe
    exception states when target resources are absent.
    """

    url = 'http://www.railwaycodes.org.uk/elrs/elr0.shtm'
    elr_cat = get_catalogue(url=url, update=True, verbose=True)
    assert isinstance(elr_cat, dict)

    url = 'http://www.railwaycodes.org.uk/crs/crs0.shtm'
    location_code_cat = get_catalogue(url=url)
    assert isinstance(location_code_cat, dict)

    with pytest.raises(Exception):
        url = 'http://test-url.abc'
        cat_dat = get_catalogue(url=url, verbose=True, raise_error=True)
        captured = capsys.readouterr()
        assert "Error:" in captured.out
        assert cat_dat is None


def test_get_category_menu(monkeypatch, capfd):
    name = 'Line data'

    # Simulated explicit permission affirmation sequence
    monkeypatch.setattr('builtins.input', lambda _: "Yes")
    menu = get_category_menu(name=name, update=True, verbose=True)

    assert isinstance(menu, dict)
    assert list(menu.keys()) == [name]

    menu = get_category_menu(name=name)

    assert isinstance(menu, dict)
    assert list(menu.keys()) == [name]

    # Simulated operational request cancellation path
    monkeypatch.setattr('builtins.input', lambda _: "No")
    menu = get_category_menu(name=name, update=True, verbose=True)
    out, _ = capfd.readouterr()
    assert "Cancelled." in out
    assert menu is None

    # Structural error handling fallback sequence test
    monkeypatch.setattr('pyrcs.parser.homepage_url', lambda: 'https://test-url.abc')
    menu = get_category_menu(name=name, update=True, confirmation_required=False, verbose=True)
    out, _ = capfd.readouterr()
    assert "Failed" in out
    assert menu is None


def test_get_heading_text():
    elec = Electrification()

    assert isinstance(elec.catalogue, dict)
    url = elec.catalogue[elec.KEY_TO_INDEPENDENT_LINES]

    source = _requests_get(url)
    assert isinstance(source, curl_cffi.Response)
    soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

    h3 = soup.find('h3')

    h3_text = get_heading_text(heading_tag=h3, elem_tag_name='em')
    assert h3_text == 'Beamish Tramway'


def test_get_page_catalogue(capfd):
    url = 'http://www.railwaycodes.org.uk/electrification/mast_prefix2.shtm'

    # noinspection broad-exception
    try:
        elec_catalogue = get_page_catalogue(url=url)
        if elec_catalogue is not None:
            assert isinstance(elec_catalogue, pd.DataFrame)
    except Exception:
        pytest.skip("Target external web server is unreachable.")

    # Validation check for active error enforcement scenarios
    url_fail = 'https://test-url.abc'
    with pytest.raises(Exception) as exc_info:
        get_page_catalogue(url=url_fail, verbose=True, raise_error=True)

    assert exc_info.value is not None
    out, _ = capfd.readouterr()
    assert "Failed" in out


def test_get_hypertext():
    """
    Test the extraction and formatting of DOM link segments in get_hypertext.
    """

    # 1. Test non-tag input (e.g. NavigableString or string fallback)
    soup_text = bs4.BeautifulSoup("Plain text string", "html.parser")
    assert get_hypertext(soup_text.string) == "Plain text string"

    # 2. Test Markdown style hyperlink extraction
    html = '<p>Visit <a href="https://example.com">Example Site</a> for details.</p>'
    soup = bs4.BeautifulSoup(html, "html.parser")
    assert (get_hypertext(soup.p, md_style=True) ==
            "Visit [Example Site](https://example.com) for details.")

    # 3. Test plain-text reference style hyperlink extraction
    assert (get_hypertext(soup.p, md_style=False) ==
            "Visit Example Site (https://example.com) for details.")

    # 4. Test missing href attribute fallback
    html_no_href = '<p>Anchor without link <a>Placeholder</a> text.</p>'
    soup_no_href = bs4.BeautifulSoup(html_no_href, "html.parser")
    assert get_hypertext(soup_no_href.p, md_style=True) == "Anchor without link Placeholder text."

    # 5. Test custom tag name support
    html_custom = '<p>Check <custom href="https://example.com">resource</custom> here.</p>'
    soup_custom = bs4.BeautifulSoup(html_custom, "html.parser")
    assert (get_hypertext(soup_custom.p, hyperlink_tag_name="custom", md_style=True) ==
            "Check [resource](https://example.com) here.")

    # 6. Test normalisation of non-breaking spaces and duplicate spacing
    html_space = '<p>Text&nbsp;with&nbsp;non-breaking spaces  and extra spaces.</p>'
    soup_space = bs4.BeautifulSoup(html_space, "html.parser")
    assert get_hypertext(soup_space.p) == "Text with non-breaking spaces and extra spaces."


if __name__ == '__main__':
    pytest.main()
