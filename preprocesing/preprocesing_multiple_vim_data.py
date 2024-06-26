import pandas as pd
import numpy as np
from datetime import timedelta
from enum import Enum
import json

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

def interpolate_points(row, next_row, parameter):
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
    
    return pd.DataFrame({'Timestamp': interpolated_times, parameter: interpolated_values})

def get_timeseries(df, selected_parameters):
    df['ReadTime'] = pd.to_datetime(df['ReadTime'], format='%d/%m/%y %H:%M')
    
    all_interpolated_data = []

    for param in selected_parameters:
        param_value = param.value
        df_param = df[df['Parameter'] == param_value]
        
        # List to hold all interpolated data for this parameter
        interpolated_data = []

        # Iterate through the rows and interpolate points within each row
        for i in range(len(df_param) - 1):
            row = df_param.iloc[i]
            next_row = df_param.iloc[i + 1]
            interpolated_data.append(interpolate_points(row, next_row, param_value))

        # Concatenate all interpolated data for this parameter
        if interpolated_data:
            df_interpolated_param = pd.concat(interpolated_data, ignore_index=True)
            all_interpolated_data.append(df_interpolated_param)

    # Merge all parameter dataframes on 'Timestamp'
    if all_interpolated_data:
        df_merged = all_interpolated_data[0]
        for df_interpolated in all_interpolated_data[1:]:
            df_merged = pd.merge_asof(df_merged.sort_values('Timestamp'), df_interpolated.sort_values('Timestamp'), on='Timestamp')

        # Convert the dataframe to a dictionary with 'Timestamp' as the key
        df_merged['Timestamp'] = df_merged['Timestamp'].astype(str)
        timeseries_dict = df_merged.set_index('Timestamp').to_dict(orient='index')
    else:
        timeseries_dict = {}

    return timeseries_dict

if __name__ == '__main__':
    df  = pd.read_excel("/Users/alejandroduarte/Documents/digital_twin_engine/preprocesing/VIMS Setup 2.3-4.xlsx")
    selected_parameters = [
        Parameters.GROUND_SPEED,
        Parameters.PAYLOAD,
        Parameters.RIGHT_FRONT_SUSPENSION_CYLINDER,
        Parameters.LEFT_FRONT_SUSPENSION_CYLINDER,
        Parameters.RIGHT_REAR_SUSPENSION_CYLINDER,
        Parameters.LEFT_REAR_SUSPENSION_CYLINDER,
                ]
    timeseries_dict = get_timeseries(df, selected_parameters)
    with open("set_up_2_3_4_.json", "w") as file:
        json.dump(timeseries_dict, file, indent=4)

    