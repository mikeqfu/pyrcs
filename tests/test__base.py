"""
Test the module :py:mod:`pyrcs._base`.
"""

import inspect
import typing

import pandas as pd
import pytest

from pyrcs._base import _Base
from pyrcs.utils import format_confirmation_prompt


@pytest.fixture(scope='class')
def _b():
    return _Base()


class TestBase:

    @pytest.mark.parametrize('content_type', ['test-content-type', 123])
    def test__init_(self, content_type):
        _b_test = _Base(content_type=content_type)
        assert _b_test.catalogue is None
        assert _b_test.introduction is None

    def test__setup_data_dir(self, _b, tmp_path):
        data_dir, _ = _b._setup_data_dir(data_dir=tmp_path, category="line-data")
        assert data_dir == _b.data_dir

    @pytest.mark.parametrize(
        'confirmation_prompt', [None, 'To collect data', format_confirmation_prompt, lambda x: 1])
    @pytest.mark.parametrize('initial', [None, 'a'])
    def test__format_confirmation_message(self, _b, confirmation_prompt, initial):
        data_name = 'test_data_name'
        prompt = _b._format_confirmation_message(
            data_name=data_name, confirmation_prompt=confirmation_prompt, initial=initial)

        if initial is None:
            if confirmation_prompt is None:
                assert f'To collect data of {data_name}' in prompt
            elif isinstance(confirmation_prompt, str):
                assert prompt == 'To collect data'
            elif isinstance(confirmation_prompt, typing.Callable):
                if 'x' in inspect.signature(confirmation_prompt).parameters:
                    assert prompt == 1
                else:
                    assert f'To collect data of {data_name}' in prompt

        elif initial == 'a' and confirmation_prompt is None:
            assert f'beginning with "{initial}"' in prompt

    @pytest.mark.parametrize('key', [None, 'A'])
    @pytest.mark.parametrize('additional_fields', [None, {'B': 'additional_data'}])
    def test__fallback_data(self, _b, key, additional_fields):
        data = _b._fallback_data(key=key, additional_fields=additional_fields)
        if key:
            assert isinstance(data, dict)
            assert key in data and 'Last updated date' in data
            if additional_fields:
                if 'B' in additional_fields:
                    assert 'B' in data
        else:
            assert data is None

    @pytest.mark.parametrize('verbose', [False, True])
    @pytest.mark.parametrize('raise_error', [False, True])
    def test__collect_data_from_source(self, _b, verbose, raise_error, monkeypatch, capfd):
        # Setup catalogue with a valid entry and an entry that will trigger a connection error
        _b.catalogue = {
            'A': 'https://github.com/mikeqfu/pyrcs',
            'B': 'https://pyrcs-test.url'  # Invalid URL to trigger RequestException
        }
        data_name = 'test_data_name'

        # Test cancellation (input "No")
        monkeypatch.setattr('builtins.input', lambda _: "No")
        data = _b._collect_data_from_source(data_name, method=_b._fallback_data)
        assert data is None

        # Test execution (input "Yes")
        monkeypatch.setattr('builtins.input', lambda _: "Yes")

        # Scenario 1: URL is found (Initial 'A')
        if raise_error:
            with pytest.raises(TypeError, match="unexpected keyword argument 'source'"):
                _b._collect_data_from_source(
                    data_name, method=_b._fallback_data, initial='A', verbose=verbose,
                    raise_error=raise_error)
                out, _ = capfd.readouterr()
                if verbose:
                    assert "Collecting the data ..." in out and "Failed. Error:" in out

            with pytest.raises(ValueError, match='No data is available'):
                _b._collect_data_from_source(
                    data_name, method=_b._fallback_data, initial='C', raise_error=raise_error)

            with pytest.raises(ValueError, match='not found in `.catalogue`'):
                _b._collect_data_from_source(
                    data_name, method=_b._fallback_data, initial=None, raise_error=raise_error)

        else:
            data = _b._collect_data_from_source(
                data_name, method=_b._fallback_data, initial='A', raise_error=raise_error,
                verbose=verbose, false_arg=None)
            out, _ = capfd.readouterr()
            if verbose:
                assert "unexpected keyword argument 'false_arg'" in out
            assert isinstance(data, dict)
            assert data['A'] is None
            assert data[_b.KEY_TO_LAST_UPDATED_DATE] is None

            data = _b._collect_data_from_source(
                data_name, method=_b._fallback_data, initial='B', raise_error=raise_error,
                verbose=verbose)
            out, _ = capfd.readouterr()
            if verbose:
                assert 'Collecting the data ... ' in out and 'Failed' in out
            assert isinstance(data, dict)
            assert data['B'] is None
            assert data[_b.KEY_TO_LAST_UPDATED_DATE] is None

            data = _b._collect_data_from_source(
                data_name, method=_b._fallback_data, initial=None, raise_error=raise_error,
                verbose=verbose)
            out, _ = capfd.readouterr()
            if verbose:
                assert f'"{data_name}" not found in `.catalogue`' in out
            assert data is None

    @pytest.mark.parametrize('ext', ["pickle", None])
    def test__save_data_to_file(self, _b, ext, tmp_path, capfd):
        data_name = "test_data_name"
        _b._save_data_to_file(data=None, data_name=data_name, verbose=True)
        out, _ = capfd.readouterr()
        assert f'No data of "{data_name.title()}" has been freshly collected.' in out

        _b._save_data_to_file(
            data=pd.DataFrame(), data_name=data_name, ext=ext, dump_dir=tmp_path, verbose=2)
        out, _ = capfd.readouterr()
        assert f'{data_name}.' in out and "Done" in out

    @pytest.mark.parametrize('verbose', [False, True])
    @pytest.mark.parametrize('raise_error', [False, True])
    def test__fetch_data_from_file(self, _b, verbose, raise_error, capfd):
        data_name = 'test_data_name'
        method = 'test_method'

        if raise_error:
            with pytest.raises(AttributeError, match="no attribute 'test_method'"):
                _b._fetch_data_from_file(
                    data_name, method, verbose=verbose, raise_error=raise_error)
        else:
            _b._fetch_data_from_file(data_name, method, verbose=verbose, raise_error=raise_error)
            out, _ = capfd.readouterr()
            if verbose:
                assert "Error: '_Base' object has no attribute 'test_method'." in out


if __name__ == '__main__':
    pytest.main()
