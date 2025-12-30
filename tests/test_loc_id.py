"""
Test the module :py:mod:`pyrcs.line_data.loc_id`.
"""

from unittest.mock import MagicMock, patch

import bs4
import pandas as pd
import pytest

from pyrcs.line_data.loc_id import LocationIdentifiers


def test__parse_raw_location_name():
    from pyrcs.line_data.loc_id import _parse_raw_location_name

    # if not x (None or Empty string)
    assert _parse_raw_location_name(None) == ('', '')
    assert _parse_raw_location_name('') == ('', '')

    # '✖' in x_
    assert _parse_raw_location_name('Preston ✖ Now closed') == ('Preston', 'Now closed')
    assert _parse_raw_location_name('✖Only Note') == ('', 'Only Note')

    # 'STANOX ' in x_
    assert _parse_raw_location_name('York STANOX 82001') == ('York', 'STANOX 82001')
    assert _parse_raw_location_name('Station Name STANOX 12345') == ('Station Name', 'STANOX 12345')

    # Regex match for brackets [match is True] - keyword_pattern.search(note_part) is True
    assert _parse_raw_location_name('Abercynon (formerly Abercynon South)') == \
           ('Abercynon', 'formerly Abercynon South')
    assert _parse_raw_location_name('Ashford International [domestic portion]') == \
           ('Ashford International', 'domestic portion')
    assert _parse_raw_location_name('Ayr [unknown feature]') == \
           ('Ayr', 'unknown feature')

    # any(char in x_ for char in '()[]') is True (Standard format)
    assert _parse_raw_location_name('Paddington (["(now platform 1)"])') == \
           ('Paddington', 'now platform 1')
    assert _parse_raw_location_name('Leeds ("[originally Leeds station]")') == \
           ('Leeds', 'originally Leeds station')

    # Regex match is True but keyword is missing (still matches any(char in x_))
    assert _parse_raw_location_name('Leeds (Without keywords)') == ('Leeds (Without keywords)', '')

    # Regex match is False (No brackets/parentheses)
    assert _parse_raw_location_name('Abbey Wood') == ('Abbey Wood', '')
    assert _parse_raw_location_name('  Paddington  ') == ('Paddington', '')

    # Edge case - Parentheses at the very start
    assert _parse_raw_location_name('(now deleted)') == ('', 'now deleted')


def test__extra_annotations():
    from pyrcs.line_data.loc_id import _extra_annotations

    assert isinstance(_extra_annotations(), list)


def test__count_sep():
    from pyrcs.line_data.loc_id import _count_sep

    # Test Windows style
    assert _count_sep("Line1\r\nLine2\r\nLine3") == 2
    # Test Legacy Mac style
    assert _count_sep("Line1\rLine2") == 1
    # Test Unix style
    assert _count_sep("Line1\nLine2") == 1
    # Test Ad hoc ~LO case
    assert _count_sep("~LO\nLine1\nLine2") == 1


def test__split_dat_and_note():
    from pyrcs.line_data.loc_id import _split_dat_and_note

    assert _split_dat_and_note("A\r\nB") == ["A", "B"]
    assert _split_dat_and_note("A\rB") == ["A", "B"]
    assert _split_dat_and_note("A\nB") == ["A", "B"]
    assert _split_dat_and_note("A") == "A"


def test__parse_code_note():
    from pyrcs.line_data.loc_id import _parse_code_note

    assert _parse_code_note('860260✖Earlier code') == ('860260', 'Earlier code')  # Test ✖
    assert _parse_code_note('860260 [Old Code]') == ('860260', 'Old Code')  # Test brackets
    assert _parse_code_note('ABC (Note)') == ('ABC', 'Note')  # Test parentheses
    assert _parse_code_note('12345') == ('12345', '')  # Test no note


def test__stanox_note():
    from pyrcs.line_data.loc_id import _stanox_note

    # Standard 5-digit
    assert _stanox_note('12345') == ('12345', '')
    # Pseudo STANOX with asterisk
    assert _stanox_note('12345*') == ('12345', 'Pseudo STANOX')
    # STANOX with trailing note
    assert _stanox_note('12345 Main Line') == ('12345', 'Main Line')
    # Complex case with brackets
    assert _stanox_note('12345* (formerly 54321)') == ('12345', 'Pseudo STANOX; formerly 54321')
    # Empty cases
    assert _stanox_note('-') == ('', '')


def test__parse_mult_alt_codes():
    from pyrcs.line_data.loc_id import _parse_mult_alt_codes

    # Mock _fix_exceptional_cases to avoid external dependencies during this unit test
    with patch('pyrcs.line_data.loc_id._fix_exceptional_cases', side_effect=lambda x: x):
        # --- 1. Test Windows Style Newlines (\r\n) ---
        # Coverage: 'if \r\n in x' block (Lines 269-273)
        df_win = pd.DataFrame({
            'Location': ['London\r\nBridge'],  # 1 sep. Max is 2. d = 1.
            'CRS': ['LBG\r\nLB2\r\nLB3'],  # 2 seps.
            'NLC': ['1\r\n2\r\n3'],
            'TIPLOC': ['A\r\nB\r\nC'],
            'STANME': ['X\r\nY\r\nZ'],
            'STANOX': ['1\r\n2\r\n3']
        })
        res_win = _parse_mult_alt_codes(df_win)
        assert len(res_win) == 3
        # Line 271: Location repeats the last split segment
        assert res_win.loc[2, 'Location'] == 'Bridge'
        # Line 273: Codes append empty strings via trailing newlines

        # --- 2. Test Legacy Mac Style Newlines (\r) ---
        # Coverage: 'elif \r in x' block (Lines 274-278)
        df_mac = pd.DataFrame({
            'Location': ['Allerton'],  # 0 seps. Max is 1. d = 1.
            'CRS': ['ALN\rLVP'],  # 1 sep.
            'NLC': ['1\r2'],
            'TIPLOC': ['A\rB'],
            'STANME': ['X\rY'],
            'STANOX': ['1\r2']
        })
        res_mac = _parse_mult_alt_codes(df_mac)
        assert len(res_mac) == 2
        # Line 276: Location repeats if no separator originally found
        assert res_mac.loc[1, 'Location'] == 'Allerton'

        # --- 3. Test Standard Unix Style Newlines (\n) ---
        # Coverage: 'else' block (Lines 279-283)
        df_unix = pd.DataFrame({
            'Location': ['Bletchley'],  # d = 1.
            'CRS': ['BLY\nBLU'],  # Max seps = 1.
            'NLC': ['1\n2'],
            'TIPLOC': ['A\nB'],
            'STANME': ['X\nY'],
            'STANOX': ['1\n2']
        })
        res_unix = _parse_mult_alt_codes(df_unix)
        assert len(res_unix) == 2
        # Line 281: Location uses '\n'.join for padding
        assert res_unix.loc[1, 'Location'] == 'Bletchley'

        # --- 4. Test Code Padding (The 'else' branches inside newline checks) ---
        # This ensures that non-Location columns get empty strings when padded
        df_pad = pd.DataFrame({
            'Location': ['A\nB\nC'],
            'CRS': ['CRS_A'],  # d = 2.
            'NLC': ['NLC_A\nNLC_B\nNLC_C'],
            'TIPLOC': ['T_A\nT_B\nT_C'],
            'STANME': ['S_A\nS_B\nS_C'],
            'STANOX': ['X_A\nX_B\nX_C']
        })
        res_pad = _parse_mult_alt_codes(df_pad)
        # Line 283: CRS 'x' didn't have \n, so it falls to else and appends \n * d
        assert res_pad.loc[1, 'CRS'] == ''
        assert res_pad.loc[2, 'CRS'] == ''

        # --- 5. Test Whitespace Cleaning ---
        # Coverage: Final temp.apply(lambda x_: x_.str.strip())
        df_dirty = pd.DataFrame({
            'Location': ['  Paddington  '],
            'CRS': [' PAD '],
            'NLC': [' 308700 '],
            'TIPLOC': [' PADTON '],
            'STANME': [' PADDINGTN '],
            'STANOX': [' 73000 ']
        })
        res_dirty = _parse_mult_alt_codes(df_dirty)
        assert res_dirty.loc[0, 'Location'] == 'Paddington'
        assert res_dirty.loc[0, 'CRS'] == 'PAD'


def test__parse_stanox_note():
    from pyrcs.line_data.loc_id import _parse_stanox_note

    df = pd.DataFrame({'STANOX': ['12345', '67890*', '55555 Additional Info']})

    result = _parse_stanox_note(df)

    assert 'STANOX_Note' in result.columns
    assert result.loc[1, 'STANOX'] == '67890'
    assert result.loc[1, 'STANOX_Note'] == 'Pseudo STANOX'
    assert result.loc[2, 'STANOX_Note'] == 'Additional Info'


def test__format_structured_note():
    """
    Test the dynamic DataFrame construction and column scaling.
    """
    from pyrcs.line_data.loc_id import _format_structured_note

    # Case 1: Standard literal tab and newline characters
    text_1 = "Abbey Wood\tABW\nAllerton\tALN\tLVP\tLSP"
    df_1 = _format_structured_note(text_1)

    assert isinstance(df_1, pd.DataFrame)
    assert df_1.columns.tolist() == ['Location', 'CRS1', 'CRS2', 'CRS3']
    assert df_1.iloc[0]['Location'] == 'Abbey Wood'
    assert df_1.iloc[1]['CRS3'] == 'LSP'

    # Case 2: Handle literal string escapes (\\t instead of \t)
    text_2 = "Bletchley\\tBLY\\tBLU"
    df_2 = _format_structured_note(text_2)
    assert df_2.columns.tolist() == ['Location', 'CRS1', 'CRS2']
    assert df_2.iloc[0]['CRS2'] == 'BLU'

    # Case 3: Mixed delimiters (tabs and commas)
    text_3 = "Heworth\tHEW,HEZ"
    df_3 = _format_structured_note(text_3)
    assert df_3.columns.tolist() == ['Location', 'CRS1', 'CRS2']

    # Case 4: Empty or invalid input
    assert _format_structured_note("").empty
    assert _format_structured_note("NoTabsHere").empty


@pytest.fixture(scope='class')
def lid():
    return LocationIdentifiers()


class TestLocationIdentifiers:

    def test__parse_notes_page(self, lid):
        """
        Test parsing logic for HTML responses containing <p> and <pre> tags.
        """
        # Create a mock source object
        mock_source = MagicMock()
        mock_source.ok = True
        # HTML containing a narrative paragraph and a structured tab-separated paragraph
        mock_source.content = b"""
        <html>
            <body>
                <p>This is a valid note about a station.</p>
                <p>Thank you for visiting, click the link below.</p>
                <p>TabStation\tTS1\tTS2</p>
                <pre>Structured Data from pre span parser</pre>
            </body>
        </html>
        """

        notes, _ = lid._parse_notes_page(mock_source)

        assert isinstance(notes, list)
        assert len(notes) == 3  # 1st <p>, 3rd <p> (formatted), <pre> (df)

        # Verify narrative note
        assert "This is a valid note" in notes[0]

        # Verify boilerplate was removed (the "Thank you" paragraph)
        assert not any("Thank you" in str(n) for n in notes)

        # Verify tabbed <p> was converted to DataFrame
        assert isinstance(notes[1], pd.DataFrame)
        assert notes[1].iloc[0]['Location'] == 'TabStation'

        # Verify <pre> content
        assert isinstance(notes[2], pd.DataFrame)
        assert 'location_name' in notes[2].columns

    def test__parse_crs_notes(self, lid):
        """
        Test the mapping of CRS codes to their respective parsed notes via network requests.
        """
        # Setup mock data - A DataFrame where some rows say 'see note'
        data = pd.DataFrame({
            'CRS': ['XYZ', 'ABC', 'DEF'],
            'CRS_Note': ['Standard', 'see note (1)', 'see note (2)']
        })

        # Setup mock soup - HTML with <a> tags containing 'note' (case insensitive)
        html_content = b"""
        <html>
            <a href="note1.shtm">Note 1</a>
            <a href="note2.shtm">Note 2</a>
        </html>
        """
        soup = bs4.BeautifulSoup(html_content, 'html.parser')

        # Mock dependencies
        lid.catalogue.update({'AA': 'http://example.com/'})

        # Mock Response objects for the network calls
        mock_resp1 = MagicMock()
        mock_resp2 = MagicMock()

        # Mock the return value of _parse_notes_page
        # Return a list containing a dummy string or DataFrame for each call
        parsed_note_1 = "Note content for ABC"
        parsed_note_2 = pd.DataFrame([['Station', 'STN']], columns=['Location', 'CRS'])

        with patch('requests.Session.get') as mock_get:
            # Side effect to return different responses for the two 'see note' links
            mock_get.side_effect = [mock_resp1, mock_resp2]

            with patch.object(LocationIdentifiers, '_parse_notes_page') as mock_parse:
                # Side effect to return our mock notes
                mock_parse.side_effect = [([parsed_note_1], None), ([parsed_note_2], None)]

                # 4. Execute the method
                result = lid._parse_crs_notes(data, 'AA', soup)

                # 5. Assertions
                assert result is not None
                assert len(result) == 2  # Only 'ABC' and 'DEF' had 'see note'

                # Check mapping accuracy
                assert result['ABC'] == parsed_note_1
                assert isinstance(result['DEF'], pd.DataFrame)
                assert result['DEF'].iloc[0]['CRS'] == 'STN'

                # Ensure the correct URLs were constructed
                expected_url1 = 'http://example.com/note1.shtm'
                assert mock_get.call_args_list[0][0][0] == expected_url1

    def test_fetch_loc_id_fallback_condition(self, lid):
        # 1. Define the side effect with a guard for initial=None
        def side_effect(initial=None, update=False, **kwargs):
            if initial is None:
                # This allows the 'else' block of the REAL method to run
                return original_method(initial=None, update=update, **kwargs)

            char = initial.upper()
            if update:
                # Simulate failure: triggers the 'if all(... is None)' condition
                return {char: None, lid.KEY_TO_LAST_UPDATED_DATE: None}
            else:
                # Simulate fallback success
                df = pd.DataFrame({'Location': ['Test'], 'CRS': [char]})
                return {char: df, lid.KEY_TO_LAST_UPDATED_DATE: '2025-12-24'}

        # 2. Store the original method and swap it with our mock
        original_method = lid.fetch_loc_id
        lid.fetch_loc_id = MagicMock(side_effect=side_effect)

        try:
            # 3. Execution: This now correctly handles the initial None
            result = lid.fetch_loc_id(initial=None, update=True)

            # 4. Assertions
            # 1 (initial) + 26 (updates) + 26 (fallbacks) = 53
            assert lid.fetch_loc_id.call_count == 53
            assert not result[lid.KEY].empty

        finally:
            # 5. Restore the original method so other tests aren't affected
            lid.fetch_loc_id = original_method

    @pytest.mark.parametrize('update', [True, False])
    def test_fetch_notes(self, lid, update):
        notes = lid.fetch_notes(update=update, verbose=True)

        assert isinstance(notes, dict)
        assert list(notes.keys()) == [lid.KEY_TO_NOTES, lid.KEY_TO_LAST_UPDATED_DATE]

        notes_dat = notes[lid.KEY_TO_NOTES][lid.KEY_TO_MSCEN]
        assert isinstance(notes_dat, list)

    @pytest.mark.parametrize('update', [True, False])
    def test_collect_codes_by_initial(self, lid, update):
        loc_a = lid.fetch_loc_id(initial='a', update=update, verbose=True)

        assert isinstance(loc_a, dict)
        assert list(loc_a.keys()) == ['A', 'Notes', 'Last updated date']

        loc_a_codes = loc_a['A']
        assert isinstance(loc_a_codes, pd.DataFrame)

    @pytest.mark.parametrize('update', [True, False])
    def test_fetch_other_systems_codes(self, lid, update):
        os_codes = lid.fetch_other_systems_codes(update=update, verbose=True)

        assert isinstance(os_codes, dict)
        assert list(os_codes.keys()) == ['Other systems', 'Last updated date']
        os_codes_dat = os_codes[lid.KEY_TO_OTHER_SYSTEMS]
        assert isinstance(os_codes_dat, dict)

    def test_fetch_codes(self, lid, tmp_path, capfd):
        loc_codes = lid.fetch_codes(dump_dir=tmp_path, verbose=2)

        out, _ = capfd.readouterr()
        assert "Saving" in out and "Done." in out

        assert isinstance(loc_codes, dict)
        assert list(loc_codes.keys()) == [
            'Location ID', 'Other systems', 'Notes', 'Last updated date']

        loc_codes_dat = loc_codes[lid.KEY]
        assert isinstance(loc_codes_dat, pd.DataFrame)

    @pytest.mark.parametrize('drop_duplicates', [False, True])
    @pytest.mark.parametrize('main_key', [None, 'Data'])
    def test_make_xref_dict(self, lid, drop_duplicates, main_key, capfd, tmp_path):
        stanox_dictionary = lid.make_xref_dict(keys='STANOX')
        assert isinstance(stanox_dictionary, pd.DataFrame)

        s_t_dictionary = lid.make_xref_dict(
            keys=['STANOX', 'TIPLOC'], initials='a', drop_duplicates=drop_duplicates, verbose=2)
        out, _ = capfd.readouterr()
        assert "Generating location code dictionary" in out and "Done." in out
        assert isinstance(s_t_dictionary, pd.DataFrame)

        s_t_dictionary = lid.make_xref_dict(
            keys=['STANOX', 'TIPLOC'], initials='b', main_key=main_key, as_dict=True, verbose=2,
            dump_it=True, dump_dir=tmp_path)
        out, _ = capfd.readouterr()
        assert "Saving" in out and "Done." in out
        assert isinstance(s_t_dictionary, dict)
        if main_key:
            assert list(s_t_dictionary.keys()) == ['Data']

        with pytest.raises(ValueError, match=r"`keys` must be one of .*, but got \['ABC'\]."):
            _ = lid.make_xref_dict(keys='ABC')

        with pytest.raises(TypeError, match='`main_key` must be a string.'):
            _ = lid.make_xref_dict(keys='STANOX', main_key=123)

        with pytest.raises(ValueError, match='must be a string or a list of letters'):
            _ = lid.make_xref_dict(keys='STANOX', initials=['a', 1])


if __name__ == '__main__':
    pytest.main()
