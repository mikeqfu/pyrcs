"""Test the module :py:mod:`pyrcs.converter`."""

import pandas as pd
import pytest


class TestConverter:

    @staticmethod
    def test_fix_mileage():
        from pyrcs.converter import fix_mileage

        fixed_mileage = fix_mileage(mileage=29.011)
        assert fixed_mileage == '29.0110'

        fixed_mileage = fix_mileage(mileage='.1100')
        assert fixed_mileage == '0.1100'

        fixed_mileage = fix_mileage(mileage=29)
        assert fixed_mileage == '29.0000'

    @staticmethod
    def test_yard_to_mileage():
        from pyrcs.converter import yard_to_mileage

        mileage_dat = yard_to_mileage(yard=396)
        assert mileage_dat == '0.0396'

        mileage_dat = yard_to_mileage(yard=396, as_str=False)
        assert mileage_dat == 0.0396

        mileage_dat = yard_to_mileage(yard=None)
        assert mileage_dat == ''

        mileage_dat = yard_to_mileage(yard=1760)
        assert mileage_dat == '1.0000'

        mileage_dat = yard_to_mileage(yard=12330)
        assert mileage_dat == '7.0010'

    @staticmethod
    def test_mileage_to_yard():
        from pyrcs.converter import mileage_to_yard

        yards_dat = mileage_to_yard(mileage='0.0396')
        assert yards_dat == 396

        yards_dat = mileage_to_yard(mileage=0.0396)
        assert yards_dat == 396

        yards_dat = mileage_to_yard(mileage=1.0396)
        assert yards_dat == 2156

    @staticmethod
    def test_mile_chain_to_mileage():
        from pyrcs.converter import mile_chain_to_mileage

        # AAM 0.18 Tewkesbury Junction with ANZ (84.62)
        mileage_data = mile_chain_to_mileage(mile_chain='0.18')
        assert mileage_data == '0.0396'

        # None, nan or ''
        mileage_data = mile_chain_to_mileage(mile_chain=None)
        assert mileage_data == ''

    @staticmethod
    def test_mileage_to_mile_chain():
        from pyrcs.converter import mileage_to_mile_chain

        mile_chain_data = mileage_to_mile_chain(mileage='0.0396')
        assert mile_chain_data == '0.18'

        mile_chain_data = mileage_to_mile_chain(mileage=1.0396)
        assert mile_chain_data == '1.18'

        # None, nan or ''
        miles_chains_dat = mileage_to_mile_chain(mileage=None)
        assert miles_chains_dat == ''

    @staticmethod
    def test_mile_yard_to_mileage():
        from pyrcs.converter import mile_yard_to_mileage

        m, y = 10, 1500

        mileage_data = mile_yard_to_mileage(mile=m, yard=y)
        assert mileage_data == 10.15

        mileage_data = mile_yard_to_mileage(mile=m, yard=y, as_numeric=False)
        assert mileage_data == '10.1500'

        m, y = 10, 500

        mileage_data = mile_yard_to_mileage(mile=m, yard=y, as_numeric=False)
        assert mileage_data == '10.0500'

    @staticmethod
    def test_mileage_str_to_num():
        from pyrcs.converter import mileage_str_to_num

        mileage_num = mileage_str_to_num(mileage='0.0396')
        assert mileage_num == 0.0396

        mileage_num = mileage_str_to_num(mileage='')
        assert pd.isna(mileage_num)

    @staticmethod
    def test_mileage_num_to_str():
        from pyrcs.converter import mileage_num_to_str

        mileage_str = mileage_num_to_str(mileage=0.0396)
        assert mileage_str == '0.0396'

        mileage_str = mileage_num_to_str(mileage=None)
        assert mileage_str == ''

    @staticmethod
    def test_shift_mileage_by_yard():
        from pyrcs.converter import shift_mileage_by_yard

        n_mileage = shift_mileage_by_yard(mileage='0.0396', shift_yards=220)
        assert n_mileage == 0.0616

        n_mileage = shift_mileage_by_yard(mileage='0.0396', shift_yards=221)
        assert n_mileage == 0.0617

        n_mileage = shift_mileage_by_yard(mileage=10, shift_yards=220)
        assert n_mileage == 10.022

    @staticmethod
    def test_fix_stanox():
        from pyrcs.converter import fix_stanox

        fixed_stanox = fix_stanox(stanox=65630)
        assert fixed_stanox == '65630'

        fixed_stanox = fix_stanox(stanox='2071')
        assert fixed_stanox == '02071'

        fixed_stanox = fix_stanox(stanox=2071)
        assert fixed_stanox == '02071'

    @staticmethod
    def test_kilometer_to_yard():
        from pyrcs.converter import kilometer_to_yard

        assert kilometer_to_yard(1) == 1093.6132983377079


if __name__ == '__main__':
    pytest.main()
