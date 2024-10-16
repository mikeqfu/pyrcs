"""
Converts data to a certain format.
"""

import copy
import numbers

import numpy as np
import pandas as pd


# == Convert mileage data ==========================================================================


def fix_mileage(mileage):
    """
    Fixes mileage data (associated with an ELR).

    :param mileage: The mileage data.
    :type mileage: str | float | None
    :return: The fixed mileage data in the form of *<miles>.<yards>*.
    :rtype: str

    **Examples**::

        >>> from pyrcs.converter import fix_mileage
        >>> fixed_mileage = fix_mileage(mileage=29.011)
        >>> fixed_mileage
        '29.0110'
        >>> fixed_mileage = fix_mileage(mileage='.1100')
        >>> fixed_mileage
        '0.1100'
        >>> fixed_mileage = fix_mileage(mileage=29)
        >>> fixed_mileage
        '29.0000'
    """

    if isinstance(mileage, float):
        mileage_ = fix_mileage(str(mileage))

    elif mileage and mileage != '0':
        if '.' in str(mileage):
            miles, yards = str(mileage).split('.')
            if miles == '':
                miles = '0'
        else:
            miles, yards = str(mileage), '0'
        if len(yards) < 4:
            yards += '0' * (4 - len(yards))
        mileage_ = '.'.join([miles, yards])

    else:
        mileage_ = copy.copy(mileage)

    return mileage_


def yard_to_mileage(yard, as_str=True):
    """
    Converts yards to mileages.

    :param yard: The yard data.
    :type yard: int | float | None
    :param as_str: Whether to return as a string value; defaults to ``True``.
    :type as_str: bool
    :return: The mileage in the form of *<miles>.<yards>* or *<miles>.<yards>*.
    :rtype: str | float

    **Examples**::

        >>> from pyrcs.converter import yard_to_mileage
        >>> mileage_dat = yard_to_mileage(yard=396)
        >>> mileage_dat
        '0.0396'
        >>> mileage_dat = yard_to_mileage(yard=396, as_str=False)
        >>> mileage_dat
        0.0396
        >>> mileage_dat = yard_to_mileage(yard=None)
        >>> mileage_dat
        ''
        >>> mileage_dat = yard_to_mileage(yard=1760)
        >>> mileage_dat
        '1.0000'
        >>> mileage_dat = yard_to_mileage(yard=12330)
        >>> mileage_dat
        '7.0010'
    """

    if pd.notnull(yard) and yard != '':
        yd = int(yard)
        # mileage_mi = measurement.measures.Distance(yd=yards).mi
        mileage_mi = np.floor(yd / 1760)
        # mileage_yd = measurement.measures.Distance(mi=mileage_mi).yd
        mileage_yd = yd - int(mileage_mi * 1760)

        if mileage_yd == 1760:
            mileage_mi += 1
            mileage_yd = 0

        mileage = mileage_mi + round(mileage_yd / (10 ** 4), 4)
        if as_str:
            mileage = str('%.4f' % mileage)

    else:
        mileage = '' if as_str else np.nan

    return mileage


def mileage_to_yard(mileage):
    """
    Converts mileages to yards.

    :param mileage: The mileage (used by Network Rail).
    :type mileage: float | int | str
    :return: The corresponding yards.
    :rtype: int

    **Examples**::

        >>> from pyrcs.converter import mileage_to_yard
        >>> yards_dat = mileage_to_yard(mileage='0.0396')
        >>> yards_dat
        396
        >>> yards_dat = mileage_to_yard(mileage=0.0396)
        >>> yards_dat
        396
        >>> yards_dat = mileage_to_yard(mileage=1.0396)
        >>> yards_dat
        2156
    """

    if isinstance(mileage, (int, float, numbers.Integral, numbers.Rational)):
        mileage = mileage_num_to_str(mileage)

    miles, yards = map(float, mileage.split('.'))

    yards += int(miles * 1760)  # int(measurement.measures.Distance(mi=miles).yd)

    return int(yards)


def mile_chain_to_mileage(mile_chain):
    """
    Converts *<miles>.<chains>* to *<miles>.<yards>*.

    :param mile_chain: Mileage data presented in the form of *<miles>.<chains>*.
    :type mile_chain: str | numpy.nan | None
    :return: The corresponding mileage in the form of '<miles>.<yards>'.
    :rtype: str

    **Examples**::

        >>> from pyrcs.converter import mile_chain_to_mileage
        >>> # AAM 0.18 Tewkesbury Junction with ANZ (84.62)
        >>> mileage_data = mile_chain_to_mileage(mile_chain='0.18')
        >>> mileage_data
        '0.0396'
        >>> # None, nan or ''
        >>> mileage_data = mile_chain_to_mileage(mile_chain=None)
        >>> mileage_data
        ''
    """

    if pd.notna(mile_chain) and mile_chain != '':
        miles, chains = map(float, str(mile_chain).split('.'))
        yards = chains * 22.0  # measurement.measures.Distance(chain=chains).yd
        network_rail_mileage = '%.4f' % (miles + round(yards / (10 ** 4), 4))
    else:
        network_rail_mileage = ''

    return network_rail_mileage


def mileage_to_mile_chain(mileage):
    """
    Converts *<miles>.<yards>* to *<miles>.<chains>*.

    :param mileage: The mileage data presented in the form of *<miles>.<yards>*.
    :type mileage: str | numpy.nan | None
    :return: The corresponding mileage presented in the form of *<miles>.<chains>*.
    :rtype: str

    **Examples**::

        >>> from pyrcs.converter import mileage_to_mile_chain
        >>> mile_chain_data = mileage_to_mile_chain(mileage='0.0396')
        >>> mile_chain_data
        '0.18'
        >>> mile_chain_data = mileage_to_mile_chain(mileage=1.0396)
        >>> mile_chain_data
        '1.18'
        >>> # None, nan or ''
        >>> miles_chains_dat = mileage_to_mile_chain(mileage=None)
        >>> miles_chains_dat
        ''
    """

    if pd.notna(mileage) and mileage != '':
        miles, yards = map(float, str(mileage).split('.'))
        chains = yards / 22.0  # measurement.measures.Distance(yard=yards).chain
        miles_chains = '%.2f' % (miles + round(chains / (10 ** 2), 2))
    else:
        miles_chains = ''

    return miles_chains


def mile_yard_to_mileage(mile, yard, as_numeric=True):
    """
    Converts mile and yard to mileage.

    :param mile: The mile data.
    :type mile: float | int
    :param yard: The yard data.
    :type yard: float | int
    :param as_numeric: Whether to return a numeric value; defaults to ``True``.
    :type as_numeric: bool
    :return: The corresponding mileage data in the form of *<miles>.<yards>*.
    :rtype: str | float

    **Examples**::

        >>> from pyrcs.converter import mile_yard_to_mileage
        >>> m, y = 10, 1500
        >>> mileage_data = mile_yard_to_mileage(mile=m, yard=y)
        >>> mileage_data
        10.15
        >>> mileage_data = mile_yard_to_mileage(mile=m, yard=y, as_numeric=False)
        >>> mileage_data
        '10.1500'
        >>> m, y = 10, 500
        >>> mileage_data = mile_yard_to_mileage(mile=m, yard=y, as_numeric=False)
        >>> mileage_data
        '10.0500'
    """

    mile_, yard_ = map(str, (mile, yard))
    if len(yard_) < 4:
        yard_ = '0' * (4 - len(yard_)) + yard_

    mileage = mile_ + '.' + yard_

    if as_numeric:
        mileage = mileage_str_to_num(mileage)

    return mileage


def mileage_str_to_num(mileage):
    """
    Converts string-type mileage to its corresponding numerical value.

    :param mileage: The string-type mileage data in the form of *<miles>.<yards>*.
    :type mileage: str
    :return: The corresponding numerical-type mileage.
    :rtype: float

    **Examples**::

        >>> from pyrcs.converter import mileage_str_to_num
        >>> mileage_num = mileage_str_to_num(mileage='0.0396')
        >>> mileage_num
        0.0396
        >>> mileage_num = mileage_str_to_num(mileage='')
        >>> mileage_num
        nan
    """

    mileage_ = np.nan if mileage == '' else round(float(mileage), 4)

    return mileage_


def mileage_num_to_str(mileage):
    """
    Converts numerical-type Network Rail mileage to string-type one.

    :param mileage: The numerical-type mileage data.
    :type mileage: float | None
    :return: The corresponding string-type mileage in the form of *<miles>.<yards>*.
    :rtype: str

    **Examples**::

        >>> from pyrcs.converter import mileage_num_to_str
        >>> mileage_str = mileage_num_to_str(mileage=0.0396)
        >>> mileage_str
        '0.0396'
        >>> mileage_str = mileage_num_to_str(mileage=None)
        >>> mileage_str
        ''
    """

    if pd.notnull(mileage) or mileage == 0:
        mileage_ = '%.4f' % round(float(mileage), 4)
    else:
        mileage_ = ''

    return mileage_


def shift_mileage_by_yard(mileage, shift_yards, as_numeric=True):
    """
    Shifts the given mileage by a specified number of yards.

    :param mileage: The initial mileage (associated with an ELR).
    :type mileage: float | int | str
    :param shift_yards: The number of yards by which to shift the given mileage.
    :type shift_yards: int | float
    :param as_numeric: If ``True``, returns the result as a numeric type; defaults to ``True``.
    :type as_numeric: bool
    :return: The mileage shifted by the specified number of yards.
    :rtype: float | str

    **Examples**::

        >>> from pyrcs.converter import shift_mileage_by_yard
        >>> n_mileage = shift_mileage_by_yard(mileage='0.0396', shift_yards=220)
        >>> n_mileage
        0.0616
        >>> n_mileage = shift_mileage_by_yard(mileage='0.0396', shift_yards=221)
        >>> n_mileage
        0.0617
        >>> n_mileage = shift_mileage_by_yard(mileage=10, shift_yards=220)
        >>> n_mileage
        10.022
    """

    yards = mileage_to_yard(mileage=mileage) + shift_yards
    shifted_mileage = yard_to_mileage(yard=yards)

    if as_numeric:
        shifted_mileage = mileage_str_to_num(mileage=shifted_mileage)

    return shifted_mileage


# == Convert other data ============================================================================


def fix_stanox(stanox):
    """
    Standardises the format of a given
    `STANOX (station number) <https://wiki.openraildata.com/index.php?title=STANOX_Areas>`_.

    :param stanox: The STANOX code to be standardised.
    :type stanox: str | int | None
    :return: The standardised STANOX as a string.
    :rtype: str

    **Examples**::

        >>> from pyrcs.converter import fix_stanox
        >>> fixed_stanox = fix_stanox(stanox=65630)
        >>> fixed_stanox
        '65630'
        >>> fixed_stanox = fix_stanox(stanox='2071')
        >>> fixed_stanox
        '02071'
        >>> fixed_stanox = fix_stanox(stanox=2071)
        >>> fixed_stanox
        '02071'
    """

    if isinstance(stanox, str):
        stanox_ = copy.copy(stanox)
    else:  # isinstance(stanox, (int, float)) or stanox is None
        stanox_ = '' if pd.isna(stanox) else str(int(stanox))

    if len(stanox_) < 5 and stanox_ != '':
        stanox_ = '0' * (5 - len(stanox_)) + stanox_

    return stanox_


def kilometer_to_yard(km):
    """
    Converts a distance from kilometres to yards.

    :param km: The distance in kilometres to convert.
    :type km: int | float | None
    :return: The equivalent distance in yards.
    :rtype: float

    **Examples**::

        >>> from pyrcs.converter import kilometer_to_yard
        >>> kilometer_to_yard(1)
        1093.6132983377079
    """

    yards = np.nan if km is None else float(km) * 1093.6132983377079

    return yards
