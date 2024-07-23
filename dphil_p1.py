import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import rasterio
from rasterio.plot import show
import numpy as np
import urllib.request
from PIL import Image
import ee

# Authenticate and initialize the Earth Engine API
ee.Authenticate()
ee.Initialize(project='oxford-jihyeonjeong')

# 1. Renewable energy facility map
# Path to the Excel dataset / Sheet Name
dataset_path = 're_data/Global-Integrated-Power-June-2024.xlsx'
sheet_name = 'Powerfacilities'

# Read the dataset from the specified sheet using pandas
df = pd.read_excel(dataset_path, sheet_name=sheet_name)

# Convert the DataFrame to a GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry=[Point(xy) for xy in zip(df.Longitude, df.Latitude)])

# Set the coordinate reference system (CRS) to WGS84 (EPSG:4326)
gdf.crs = "EPSG:4326"

# 2. World map as background
# Path to the .shp file
shapefile_path = '01_country_shp/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp'

# Load the world map
world = gpd.read_file(shapefile_path)

# Ensure both GeoDataFrames are using the same CRS
if gdf.crs != world.crs:
    world = world.to_crs(gdf.crs)

# 3. Flood map 
# Path to the .tif file
tif_file_path = 'flooding_data_wri/inuncoast_rcp8p5_nosub_2050_rp0010_0.tif'

# Function to plot the map
def plot_map(ax, region_bounds=None, title="", is_local=False):
    # Plot the country land areas
    world.plot(ax=ax, color='lightgrey', edgecolor='grey', linewidth=0.2)
    
    # Plot the world map with borders only
    world.boundary.plot(ax=ax, edgecolor='grey', linewidth=0.2)

    # Plot the solar facilities
    if is_local:
        operating_facilities.plot(ax=ax, marker='o', color='green', markersize=1, label='Operating Facility', alpha=0.8)
        planned_facilities.plot(ax=ax, marker='o', color='red', markersize=1, label='Planned Facility', alpha=0.8)
    else:
        operating_facilities.plot(ax=ax, marker='o', color='green', markersize=0.1, label='Operating Facility', alpha=0.3)
        planned_facilities.plot(ax=ax, marker='o', color='red', markersize=0.1, label='Planned Facility', alpha=0.3)

    # Open the flood map TIFF file
    with rasterio.open(tif_file_path) as src:
        data = src.read(1)
        min_val = 0
        max_val = 5
        flood_map = show(src, ax=ax, cmap='Blues', vmin=min_val, vmax=max_val, alpha=1 if is_local else 0.8)

        # Adding the colorbar with log scale normalization
        cbar = plt.colorbar(flood_map.get_images()[0], ax=ax, orientation='vertical')
        cbar.set_label('Flood Risk Level')

    if region_bounds:
        ax.set_xlim(region_bounds[0], region_bounds[2])
        ax.set_ylim(region_bounds[1], region_bounds[3])

    ax.legend(markerscale=2)
    ax.set_title(title)

# Facility types
facility_types = ['solar', 'wind', 'hydropower']

# Regions to focus on
regions = {
    "Sri Lanka": [79.5, 5.5, 82, 10],  # [xmin, ymin, xmax, ymax]
    "Korea": [124, 33, 130, 39],
    "UK": [-11, 49, 2, 61]
}

# Loop through each facility type and create maps
for facility_type in facility_types:
    # Filter facilities by type
    selected_facilities = gdf[gdf['Type'].str.lower() == facility_type]
    operating_facilities = selected_facilities[selected_facilities['Status'] == 'operating']
    planned_facilities = selected_facilities[selected_facilities['Status'].isin(['construction', 'pre-construction', 'announced'])]

    # Plot global map
    fig, ax = plt.subplots(figsize=(15, 10))
    plot_map(ax, title=f"Global Map: {facility_type.capitalize()} Facilities with Flood Risk")
    plt.tight_layout()
    plt.savefig(f'global_{facility_type}_map.jpg', format='jpg', dpi=500)
    plt.close()

    # Plot local maps for each region
    for region_name, bounds in regions.items():
        fig, ax = plt.subplots(figsize=(10, 10))
        plot_map(ax, region_bounds=bounds, title=f"{region_name}: {facility_type.capitalize()} Facilities with Flood Risk", is_local=True)
        plt.tight_layout()
        plt.savefig(f'{region_name.lower().replace(" ", "_")}_{facility_type}_map.jpg', format='jpg', dpi=300)
        plt.close()
