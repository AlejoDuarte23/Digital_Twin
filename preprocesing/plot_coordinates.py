import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import contextily as ctx
import matplotlib.pyplot as plt
from scipy import stats
import numpy as np 

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
    ax.set_xlim(gdf_web_mercator.geometry.bounds.minx.min() - 4500,
                gdf_web_mercator.geometry.bounds.maxx.max() + 4500)
    ax.set_ylim(gdf_web_mercator.geometry.bounds.miny.min() - 4500,
                gdf_web_mercator.geometry.bounds.maxy.max() + 4500)

    plt.show()

def generate_geojson(df):
    geometry = [Point(xy) for xy in zip(df['PositionX'], df['PositionY'])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry)
    gdf.crs = 'EPSG:3116'
    gdf = gdf.to_crs(epsg=3857)
    
    # Convert GeoDataFrame to GeoJSON
    gdf.to_file("GPS_ST_2_3_4.geojson", driver='GeoJSON')

    return gdf

if "__name__" == "__main__":
    _df = pd.read_excel("/Users/alejandroduarte/Documents/digital_twin_engine/preprocesing/GPS Setup 2.3-4.xlsx")

    df = remove_outliers(_df)
    #geojson = generate_geojson(df=df)
    plot_basempaps(df)
