

# historical + GCM CSV file Maker
#begining year of this simulation should be 1979?
#simulation duration should be 122 year

import pandas as pd
import fortranformat as ff

def main():
    # Step 1: Read calibration data as DataFrame 
    #calibration_data is already in file, data ranges from 1/1/1977 to 9/30/2000
    calibration_df = pd.read_csv('calibration_data.csv')

    # Step 2: Concatenate Year, Month, and Day into a new 'Date' column
    calibration_df['Date'] = pd.to_datetime(calibration_df[['Year', 'Month', 'Day']])

    # Step 3: Identify End Date from Last Row of Calibration Data
    end_date = calibration_df['Date'].iloc[-1]  # Extracting end date from the last row of 'Date' column
    #print("End Date:", end_date) #-optional code to verify the correct end date

    # Step 4: Read historical data as DataFrame
    historical_df = pd.read_csv('WREMESONET.dly', delimiter=' ')

    # Step 5: Extract historical data until End Date
    historical_df['Date'] = pd.to_datetime(historical_df['Date']) # Ensure 'Date' column is parsed as datetime

    # Step 6: Make a different DataFrame df_historical 
    df_historical = historical_df[historical_df['Date'] <= end_date]

    # Step 7: Read GCM data as DataFrame df_climate
    df_climate = pd.read_csv('gfdlcm345_1.csv', header=0, error_bad_lines=False, warn_bad_lines=True)
    #this will be titled something like access45_1.csv

    # Step 8: Extract GCM data from End Date + 1 till End of Century (2099-1-31)
    end_of_century = pd.to_datetime('2099-1-31')
    df_2_climate = df_climate[(df_climate['Date'] > end_date) & (df_climate['Date'] <= end_of_century)]

    # Step 9: Concatenate df_historical and df_2_climate as df_weather
    df_weather = pd.concat([df_historical, df_2_climate], ignore_index=True)

    # Step 10: Save DataFrame as CSV
    df_weather.to_csv('weather_data.csv', index=False)

    # Step 11: Convert CSV File into DLY 
    # Function to convert row to .dly format using fortranformatter
    def write_line_ff(df_row):
        yr = int(df_row[0])
        mm = int(df_row[1])
        dd = int(df_row[2])
        tmax = float(df_row[3])
        tmin = float(df_row[4])
        prcp = float(df_row[5])

        # Sample data didn't have these columns, assuming None
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

        # Convert date to formatted string
        date_str = f"{yr:4d}{mm:02d}{dd:02d}"

        # Format the line using the write_format
        line_write = write_format.write([yr, mm, dd, sr, tmax, tmin, prcp, rhum, ws, date_str])
        return line_write
    
    with open('weather_data.dly', 'w') as f:
       for index, row in df_weather.iterrows():
           line_write = write_line_ff(row)
           f.write(line_write + '\n')
    
    
    print("Complete")

main()
