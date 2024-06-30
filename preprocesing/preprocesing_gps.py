import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import contextily as ctx
import matplotlib.pyplot as plt
from scipy import stats
import numpy as np
import json
def remove_outliers(df, threshold=3):
    z_scores = np.abs(stats.zscore(df[['PositionX', 'PositionY']]))
    
    # Get indices of the data points with z-scores above the threshold
    outlier_indices = np.where(z_scores > threshold)[0]
    
    # Drop the outliers from the DataFrame
    df_no_outliers = df.drop(df.iloc[outlier_indices].index)
    
    return df_no_outliers

def plot_basempaps(df):
    geometry = [Point(xy) for xy in zip(df['PositionX'], df['PositionY'])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry)
    gdf.crs = 'EPSG:3116'
    gdf_web_mercator = gdf.to_crs(epsg=3857)
    fig, ax = plt.subplots(figsize=(10, 10))
    gdf_web_mercator.plot(ax=ax, color='yellow', markersize=5, marker='x', edgecolor='black')

    # Add the basemap without attribution text
    ctx.add_basemap(ax, source=ctx.providers.Esri.WorldImagery, attribution="")

    # Set the plot limits to focus on the region of interest
    ax.set_xlim(gdf_web_mercator.geometry.bounds.minx.min() - 50,
                gdf_web_mercator.geometry.bounds.maxx.max() + 50)
    ax.set_ylim(gdf_web_mercator.geometry.bounds.miny.min() - 50,
                gdf_web_mercator.geometry.bounds.maxy.max() + 50)

    plt.show()

def generate_geojson(df):
    geometry = [Point(xy) for xy in zip(df['PositionX'], df['PositionY'])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry)
    gdf.crs = 'EPSG:3116'
    #gdf = gdf.to_crs(epsg=3857)
    gdf = gdf.to_crs(epsg=4326)
    
    return gdf


def main(excel_file_path:str, sheet_name:str, geojson_file_path:str) -> dict:
    # Load data
    _df = pd.read_excel(excel_file_path,sheet_name=sheet_name)

    # Remove outliers
    df = remove_outliers(_df)
    df['Datetime'] = pd.to_datetime(df['Timestamp'].astype(str))

    # Remove duplicate Datetime values
    df = df.drop_duplicates(subset=['Datetime'])

    # Generate GeoJSON DataFrame
    gdf = generate_geojson(df=df)

    # Drop unnecessary columns
    #gdf = gdf.drop(labels=['ID', 'Fecha', 'EquipmentId', 'Timestamp',
    #                   'Heading', 'Direction', 'FieldStatTypeCode'], axis=1)
    gdf = gdf.drop(labels=['Id','EquipmentId', 'Timestamp',
                        'Heading', 'Direction', 'FieldStatTypeCode'], axis=1)
    gdf['Datetime'] = gdf['Datetime'].astype(str)
    # Ensure the index is unique
    timeseries_dict = gdf.set_index('Datetime').to_file(geojson_file_path,driver = 'GeoJson')

    return timeseries_dict


if __name__ == '__main__':
    excel_file_path = "/Users/alejandroduarte/Documents/digital_twin_engine/preprocesing/Datos GPS equipo 022-429 - Mayo-22 hasta Abril-5 2023.xlsx"
    sheet_name1 = "20230323"
    geojson_file_path1 = "/Users/alejandroduarte/Documents/digital_twin_engine/preprocesing/gps_03_23.geojson"

    sheet_name2 = "20230402"
    geojson_file_path2 = "/Users/alejandroduarte/Documents/digital_twin_engine/preprocesing/gps_04_02.geojson"

    sheet_name3 = "20230325"
    geojson_file_path3 = "/Users/alejandroduarte/Documents/digital_twin_engine/preprocesing/gps_03_25.geojson"

    data_list = [(sheet_name1, geojson_file_path1), (sheet_name2, geojson_file_path2), (sheet_name3, geojson_file_path3)]       

    for sheet_name, geojson_file_path in data_list:
        main(excel_file_path, sheet_name, geojson_file_path)
