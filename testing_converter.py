# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 00:22:58 2024

@author: tcatk
"""


import pandas as pd

def convert_csv_to_dly(csv_file, dly_file):
    df = pd.read_csv(csv_file)
    
    # Open the output .DLY file for writing
    with open(dly_file, 'w') as dlyf:
        # Process each row in the DataFrame
        for index, row in df.iterrows():
            year = row[0]
            month = row[1]
            day = row[2]
            value = row[3]
            value = row[4]
            
            #additional formatting may be needed for the .DLY file


# Example usage
convert_csv_to_dly('access_1_pr.csv', 'access_1_pr.dly')