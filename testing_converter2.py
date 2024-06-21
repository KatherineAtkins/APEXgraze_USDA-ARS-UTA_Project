# -*- coding: utf-8 -*-
"""
Created on Fri Jun 21 12:33:34 2024

@author: tcatk
"""

import pandas as pd
import fortranformat as ff

# convert file to .dly format using fortranformatter
def write_line_ff(df_row):
    yr = int(df_row[0])
    mm = int(df_row[1])
    dd = int(df_row[2])
    rcp45 = float(df_row[3])
    rcp85 = float(df_row[4])

    # adding this part to make the "define format based on available columns" part work
    sr = None
    rhum = None
    ws = None

    # Define format based on available columns
    if sr is None and rhum is None and ws is None:
        write_format = ff.FortranRecordWriter('(I6, I4, I4, A6, F6.1, F6.1, F6.2, A6, A6, A25)')
    elif rhum is None and ws is None:
        write_format = ff.FortranRecordWriter('(I6, I4, I4, F6.1, F6.1, F6.1, F6.2, A6, A6, A25)')
    elif sr is None and ws is None:
        write_format = ff.FortranRecordWriter('(I6, I4, I4, A6, F6.1, F6.1, F6.2, F6.1, A6, A25)')
    elif sr is None and rhum is None:
        write_format = ff.FortranRecordWriter('(I6, I4, I4, A6, F6.1, F6.1, F6.2, A6, F6.1, A25)')
    else:
        write_format = ff.FortranRecordWriter('(I6, I4, I4, F6.1, F6.1, F6.1, F6.2, F6.1, F6.1, A25)')
    # mathcing reference script
    line_write = write_format.write([yr, mm, dd, sr, rcp45, rcp85, None, rhum, ws])
    return line_write

# convert CSV file to .dly file but original file doesn't have headers
def convert_csv_to_dly(csv_file, dly_file):
    df = pd.read_csv(csv_file, header=None)
    # Convert row to .dly format using write_line_ff function
    with open(dly_file, 'w') as f:
        for index, row in df.iterrows():
            line_write = write_line_ff(row)
            f.write(line_write + '\n')

# naming the files to match the function
csv_file = 'miroc5pr.csv'
dly_file = 'miroc5pr2.dly'

# Convert CSV file to .dly file
convert_csv_to_dly(csv_file, dly_file)