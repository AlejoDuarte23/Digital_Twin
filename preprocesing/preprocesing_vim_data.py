import pandas as pd 
import numpy as np 
from datetime import timedelta
from enum import Enum


class Parameters(Enum):
    GEAR_SELECT_BY_OPERATOR = "Gear Select (By Operator)"
    LEFT_REAR_SUSPENSION_CYLINDER = "Left Rear Suspension Cylinder"
    ENGINE_SPEED = "Engine Speed"
    BOOST_PRESSURE = "Boost Pressure"
    ENGINE_LOAD = "Engine Load"
    GROUND_SPEED = "Ground Speed"
    PAYLOAD = "Payload"
    LEFT_FRONT_SUSPENSION_CYLINDER = "Left Front Suspension Cylinder"
    ACTUAL_GEAR_TRANSMISSION = "Actual Gear (Transmission)"
    RIGHT_FRONT_SUSPENSION_CYLINDER = "Right Front Suspension Cylinder"
    THROTTLE_POSITION = "Throttle Position"
    TRANSMISSION_GEAR = "Transmission Gear"
    ENGINE_COOLANT_TEMPERATURE = "Engine Coolant Temperature"
    RIGHT_REAR_SUSPENSION_CYLINDER = "Right Rear Suspension Cylinder"



    



def get_payload_timeseries(df):
    df_payload = df[df['Parameter']=='Payload']

    df_payload['ReadTime'] = pd.to_datetime(df_payload['ReadTime'], format='%d/%m/%y %H:%M')

    # Function to generate interpolated points within a single row
    def interpolate_points(row, next_row):
        num_points = row['Samples']
        time_diff = (next_row['ReadTime'] - row['ReadTime']).total_seconds() / num_points
        interpolated_times = [row['ReadTime'] + timedelta(seconds=i * time_diff) for i in range(num_points)]
        
        # Calculate the position where the median occurs
        if row['Median'] != row['Mean']:
            median_position = int((row['Median'] - row['Min']) / (row['Max'] - row['Min']) * num_points)
        else:
            median_position = num_points // 2
        
        # Linear interpolation around the median and mean values
        if row['Mean'] > row['Median']:
            first_half = np.linspace(row['Max'], row['Mean'], median_position, endpoint=False)
            second_half = np.linspace(row['Mean'], row['Min'], num_points - median_position)
        else:
            first_half = np.linspace(row['Min'], row['Mean'], median_position, endpoint=False)
            second_half = np.linspace(row['Mean'], row['Max'], num_points - median_position)
        
        interpolated_values = np.concatenate((first_half, second_half))
        
        return pd.DataFrame({'Timestamp': interpolated_times, 'Payload': interpolated_values})

    # List to hold all interpolated data
    interpolated_data = []

    # Iterate through the rows and interpolate points within each row
    for i in range(len(df_payload) - 1):
        row = df_payload.iloc[i]
        next_row = df_payload.iloc[i + 1]
        interpolated_data.append(interpolate_points(row, next_row))

    # Concatenate all interpolated data
    df_interpolated = pd.concat(interpolated_data, ignore_index=True)

    # Sort by Timestamp to ensure chronological order
    df_interpolated.sort_values(by='Timestamp', inplace=True)

    return df_interpolated


if __name__ == '__main__':
    df  = pd.read_excel("/Users/alejandroduarte/Documents/digital_twin_engine/VIMS Setup 2.3-4.xlsx")
    get_payload_timeseries(df)