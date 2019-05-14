""" Settings """

import numpy as np
import pandas as pd


# Set preferences for displaying results
def np_preferences(reset=False):
    if not reset:
        np.core.arrayprint._line_width = 120
    else:
        np.core.arrayprint._line_width = 80  # 75


# Set preferences for displaying results
def pd_preferences(reset=False):
    if not reset:
        pd.set_option('display.precision', 2)
        pd.set_option('expand_frame_repr', False)  # Set the representation of DataFrame NOT to wrap
        pd.set_option('display.width', 600)  # Set the display width
        pd.set_option('precision', 4)
        pd.set_option('display.max_columns', 100)
        pd.set_option('display.max_rows', 20)
        pd.set_option('io.excel.xlsx.writer', 'xlsxwriter')
        pd.set_option('mode.chained_assignment', None)
        pd.set_option('display.float_format', lambda x: '%.4f' % x)
    else:
        pd.reset_option('all')


np_preferences(reset=False)
pd_preferences(reset=False)
