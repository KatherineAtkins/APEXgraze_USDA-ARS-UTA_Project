


#creating an automated system via series of functions for "combining_trial_data" script
#prior to running, you must have a calibration data set with dates, historical data set, and Global Circulation Model (GCM) of predictions
#make sure your various column names match what is being used in the code


import warnings
import pandas as pd
import fortranformat as ff

warnings.filterwarnings('ignore')

#Step 1: Process calibration data to fine the end_dat
def process_calibration_data(file_name):
    # Read calibration data as DataFrame
    calibration_df = pd.read_csv(file_name)
    
    if not {'Year', 'Month', 'Day'}.issubset(calibration_df.columns):
        raise ValueError("The calibration data must contain 'Year', 'Month', and 'Day' columns.")
    
    #Concatenate Year, Month, and Day into a new 'Date' column
    calibration_df['Date'] = pd.to_datetime(calibration_df[['Year', 'Month', 'Day']])
    
    #Identify End Date from the Last Row of Calibration Data
    end_date = calibration_df['Date'].iloc[-1]
    
    return calibration_df, end_date

#Step 2: Historical data.dly processing (convert from .dly to .csv for concatonating)
#this will be used to create historical_df
def read_dly_file(file_name):
    # Read the .dly file
    with open(file_name, 'r') as file:
        lines = file.readlines()
    
    # Define the format for reading the .dly file
    read_format = ff.FortranRecordReader('(I6, I4, I4, A6, F6.1, F6.1, F6.2, A6, A6, A25)')
    
    # Process each line and read into DataFrame
    weather_lines = [read_format.read(line) for line in lines]
    
    # Convert to DataFrame
    df = pd.DataFrame(weather_lines, columns=['YEAR', 'MONTH', 'DAY', 'SRAD (J/m2)', 
                                              'TMAX (°C)', 'TMIN (°C)', 'PRCP (mm)', 
                                              'RHUM', 'WIND (m/s)', 'DATE'])
    
    # Convert 'DATE' column to datetime format
    df['DATE'] = pd.to_datetime(df[['YEAR', 'MONTH', 'DAY']])
    
    # Return DataFrame with relevant columns
    return df[['YEAR', 'MONTH', 'DAY', 'TMAX (°C)', 'TMIN (°C)', 'PRCP (mm)', 'DATE']]

#Step 3: GCM data processing from end_date to end of century
def process_gcm_data(gcm_file, historical_df, end_date, output_csv):
    # Read GCM data as DataFrame
    df_climate = pd.read_csv(gcm_file, header=0)
    
    # Check column names
    if not {'YEAR', 'MONTH', 'DAY'}.issubset(df_climate.columns):
        raise ValueError("The GCM data must contain 'YEAR', 'MONTH', and 'DAY' columns.")
    
    # Extract GCM data from End Date + 1 to End of Century (2099-12-31)
    end_of_century = pd.to_datetime('2099-12-31')
    df_climate['DATE'] = pd.to_datetime(df_climate[['YEAR', 'MONTH', 'DAY']])
    df_2_climate = df_climate[(df_climate['DATE'] > end_date) & (df_climate['DATE'] <= end_of_century)]
    
    # Concatenate historical data and GCM data
    df_weather = pd.concat([historical_df, df_2_climate], ignore_index=True)
    
    # Save DataFrame as CSV
    df_weather.to_csv(output_csv, index=False)
    print(f"Weather data saved to {output_csv}")

#Step 5: converting new .csv to .dly (APEX readable format)
def write_line_ff(df_row):
    yr = int(df_row[0])
    mm = int(df_row[1])
    dd = int(df_row[2])
    tmax = float(df_row[3])
    tmin = float(df_row[4])
    prcp = float(df_row[5])

    # data doesn't have/need these columns
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


def convert_csv_to_dly(output_csv, dly_file_output):
    df = pd.read_csv(output_csv, header=0)
    # Convert row to .dly format using write_line_ff function
    with open(dly_file_output, 'w') as f:
        for index, row in df.iterrows():
            line_write = write_line_ff(row)
            f.write(line_write + '\n')
            

# Run the functions
if __name__ == "__main__":
    # File paths
    calibration_file = 'calibration_data.csv'
    dly_file = 'WREMESONET.dly'
    gcm_file = '8_miroc5_85.csv'
    output_csv = '8_miroc5_85_weather_data_automated!.csv'
    dly_file_output = '8_miroc5_85_weather_data_automated.dly'
    
    # Process calibration data to get end_date
    calibration_df, end_date = process_calibration_data(calibration_file)
    
    # Read historical data from the .dly file
    historical_df = read_dly_file(dly_file)
    
    # Filter historical data based on end_date
    historical_df = historical_df[historical_df['DATE'] <= end_date]

    # Process GCM data
    process_gcm_data(gcm_file, historical_df, end_date, output_csv)
    
    # Convert CSV file to .dly format
    convert_csv_to_dly(output_csv, dly_file_output)
    
    print("Processing complete. The CSV and DLY files have been created.")

