"""
Test parser.py
"""

import datetime

import bs4
import pandas as pd
import pytest
import requests


def test_parse_tr():
    from pyrcs.parser import parse_tr

    example_url = 'http://www.railwaycodes.org.uk/elrs/elra.shtm'
    source = requests.get(example_url)
    parsed_text = bs4.BeautifulSoup(markup=source.content, features='html.parser')
    ths_dat = [th.text for th in parsed_text.find_all('th')]
    trs_dat = parsed_text.find_all(name='tr')

    tables_list = parse_tr(trs=trs_dat, ths=ths_dat)  # returns a list of lists

    assert isinstance(tables_list, list)
    assert len(tables_list) // 100 == 1
    assert tables_list[0] == [
        'AAL', 'Ashendon and Aynho Line', '0.00 - 18.29', 'Ashendon Junction', 'Now NAJ3']


def test_parse_table():
    from pyrcs.parser import parse_table

    source_dat = requests.get(url='http://www.railwaycodes.org.uk/elrs/elra.shtm')

    (columns_dat, records_dat), _ = parse_table(source_dat)

    assert columns_dat == ['ELR', 'Line name', 'Mileages', 'Datum', 'Notes']
    assert isinstance(records_dat, list)
    assert len(records_dat) // 100 == 1
    assert records_dat[0] == [
        'AAL', 'Ashendon and Aynho Line', '0.00 - 18.29', 'Ashendon Junction', 'Now NAJ3']


def test_parse_date():
    from pyrcs.parser import parse_date

    str_date_dat = '2020-01-01'

    parsed_date_dat = parse_date(str_date_dat)
    assert parsed_date_dat == '2020-01-01'

    parsed_date_dat = parse_date(str_date_dat, as_date_type=True)
    assert parsed_date_dat == datetime.date(2020, 1, 1)


def test_get_site_map(monkeypatch, capfd):
    from pyrcs.parser import get_site_map

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
    from pyrcs.parser import get_last_updated_date

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
    from pyrcs.parser import get_financial_year

    financial_year = get_financial_year(date=datetime.datetime(2021, 3, 31))
    assert financial_year == 2020


@pytest.mark.parametrize('update', [False, True])
@pytest.mark.parametrize('raise_error', [False, True])
def test_get_introduction(update, raise_error, capfd):
    from pyrcs.parser import get_introduction

    url = 'http://www.railwaycodes.org.uk/bridges/bridges0.shtm'

    intro_text = get_introduction(url=url, update=update, verbose=True)
    out, _ = capfd.readouterr()
    if update:
        assert "Updating" in out and "Done." in out
    assert isinstance(intro_text, str)

    url_ = url.replace('railwaycodes', '123')
    if raise_error:
        with pytest.raises(Exception):
            get_introduction(url=url_, update=True, raise_error=raise_error)

    else:
        intro_text = get_introduction(url=url_, update=True, raise_error=raise_error)
        assert intro_text is None

        intro_text = get_introduction(url=url_, update=True, verbose=True, raise_error=raise_error)
        out, _ = capfd.readouterr()
        assert intro_text is None
        assert "Failed" in out


def test_get_catalogue(capsys):
    from pyrcs.parser import get_catalogue

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
    from pyrcs.parser import get_category_menu

    name = 'Line data'

    monkeypatch.setattr('builtins.input', lambda _: "Yes")
    menu = get_category_menu(name=name, update=True, verbose=True)

    assert isinstance(menu, dict)
    assert list(menu.keys()) == [name]

    menu = get_category_menu(name=name)

    assert isinstance(menu, dict)
    assert list(menu.keys()) == [name]

    monkeypatch.setattr('builtins.input', lambda _: "No")
    menu = get_category_menu(name=name, update=True, verbose=True)
    out, _ = capfd.readouterr()
    assert "Cancelled." in out
    assert menu is None

    monkeypatch.setattr('pyrcs.parser.homepage_url', lambda: 'https://test-url.abc')
    menu = get_category_menu(name=name, update=True, confirmation_required=False, verbose=True)
    out, _ = capfd.readouterr()
    assert "Failed" in out
    assert menu is None


def test_get_heading_text():
    from pyrcs.parser import get_heading_text
    from pyrcs.line_data import Electrification
    from pyhelpers.ops import fake_requests_headers

    elec = Electrification()

    url = elec.catalogue[elec.KEY_TO_INDEPENDENT_LINES]
    source = requests.get(url=url, headers=fake_requests_headers())
    soup = bs4.BeautifulSoup(markup=source.content, features='html.parser')

    h3 = soup.find('h3')

    h3_text = get_heading_text(heading_tag=h3, elem_tag_name='em')
    assert h3_text == 'Beamish Tramway'


def test_get_page_catalogue(capfd):
    from pyrcs.parser import get_page_catalogue

    url = 'http://www.railwaycodes.org.uk/electrification/mast_prefix2.shtm'
    elec_catalogue = get_page_catalogue(url=url)
    assert isinstance(elec_catalogue, pd.DataFrame)

    url = 'https://test-url.abc'
    with pytest.raises(Exception):
        page_catalogue = get_page_catalogue(url=url, verbose=True, raise_error=True)
        out, _ = capfd.readouterr()
        assert "Failed" in out
        assert page_catalogue is None


def test_get_hypertext():
    from pyrcs.parser import get_hypertext
    from pyrcs.line_data import Electrification

    elec = Electrification()

    url = elec.catalogue[elec.KEY_TO_INDEPENDENT_LINES]
    source = requests.get(url)
    soup = bs4.BeautifulSoup(source.content, 'html.parser')

    h3 = soup.find('h3')

    p = h3.find_all_next('p')[8]
    assert isinstance(p, bs4.element.Tag)

    hyper_txt = get_hypertext(hypertext_tag=p, md_style=True)
    assert isinstance(hyper_txt, str)


if __name__ == '__main__':
    pytest.main()
