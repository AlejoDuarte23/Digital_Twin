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

# Load data
_df = pd.read_excel("/Users/alejandroduarte/Documents/digital_twin_engine/preprocesing/GPS Setup 2.3-4.xlsx",sheet_name="20230422-20230508")

# Remove outliers
df = remove_outliers(_df)
df['Datetime'] = pd.to_datetime(df['Timestamp'].astype(str))

# Remove duplicate Datetime values
df = df.drop_duplicates(subset=['Datetime'])

# Generate GeoJSON DataFrame
gdf = generate_geojson(df=df)

# Drop unnecessary columns
gdf = gdf.drop(labels=['ID', 'Fecha', 'EquipmentId', 'Timestamp',
                    'Heading', 'Direction', 'FieldStatTypeCode'], axis=1)
gdf['Datetime'] = gdf['Datetime'].astype(str)
# Ensure the index is unique
timeseries_dict = gdf.set_index('Datetime').to_file("/Users/alejandroduarte/Documents/digital_twin_engine/gps_st_2_3_4_2.geojson",driver = 'GeoJson')
