import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import rasterio
from rasterio.plot import show
import numpy as np
from matplotlib.colors import TwoSlopeNorm
import ee

# 1. Importing inputs
# Authenticate and initialize the Earth Engine API
ee.Authenticate()
ee.Initialize(project='oxford-jihyeonjeong')

# Renewable energy facility map
# Path to the Excel dataset / Sheet Name
dataset_path = 're_data/Global-Integrated-Power-June-2024.xlsx'
sheet_name = 'Powerfacilities'

# Read the dataset from the specified sheet using pandas
df = pd.read_excel(dataset_path, sheet_name=sheet_name)

# Convert the DataFrame to a GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry=[Point(xy) for xy in zip(df.Longitude, df.Latitude)])

# Set the coordinate reference system (CRS) to WGS84 (EPSG:4326)
gdf.crs = "EPSG:4326"

# World map as background
# Path to the .shp file
shapefile_path = '01_country_shp/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp'

# Load the world map
world = gpd.read_file(shapefile_path)

# Ensure both GeoDataFrames are using the same CRS
if gdf.crs != world.crs:
    world = world.to_crs(gdf.crs)

# Flood maps (RCP 8.5, 2050, 10-year return period)
# Path to the .tif file (coastal flood map)
tif_file_path1 = 'flooding_data_wri/inuncoast_rcp8p5_nosub_2050_rp0010_0.tif'
# Path to the .tif file (river flood map)
tif_file_path2 = 'flooding_data_wri/inunriver_rcp8p5_00000NorESM1-M_2050_rp00010.tif'

# 2. Function to plot the maps
def plot_map(ax, region_bounds=None, title="", is_local=False):
    if region_bounds:
        bounds = region_bounds
    else:
        bounds = [124, 33, 130, 39]  # Default to South Korea

    # Plot the country land areas first with lower alpha
    world.plot(ax=ax, color="lightgrey", edgecolor='grey', linewidth=0.5, alpha=0.5)

    # Open and plot the coastal flood map TIFF file
    with rasterio.open(tif_file_path1) as src1:
        data1 = src1.read(1)
        data1[data1 <= 0] = np.nan  # Set zero and negative values to NaN
        window = rasterio.windows.from_bounds(*bounds, transform=src1.transform)
        data1_crop = src1.read(1, window=window)
        data1_crop[data1_crop <= 0] = np.nan  # Set zero and negative values to NaN
        data1_log = np.log1p(data1_crop)
        
        vmin = np.nanmin(data1_log)
        vmax = np.nanmax(data1_log)
        vcenter = np.nanmedian(data1_log)
        if vmin >= vcenter or vcenter >= vmax:
            vcenter = (vmin + vmax) / 2

        norm = TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
        img1 = ax.imshow(data1_log, cmap='Blues', norm=norm, extent=(bounds[0], bounds[2], bounds[1], bounds[3]), alpha=0.7)
        plt.colorbar(img1, ax=ax, orientation='vertical', fraction=0.02, pad=0.04, label='Log-scaled Coastal Flood Risk Level')

    # Open and plot the river flood map TIFF file
    with rasterio.open(tif_file_path2) as src2:
        data2 = src2.read(1)
        data2[data2 <= 0] = np.nan  # Set zero and negative values to NaN
        window = rasterio.windows.from_bounds(*bounds, transform=src2.transform)
        data2_crop = src2.read(1, window=window)
        data2_crop[data2_crop <= 0] = np.nan  # Set zero and negative values to NaN
        data2_log = np.log1p(data2_crop)
        
        vmin = np.nanmin(data2_log)
        vmax = np.nanmax(data2_log)
        vcenter = np.nanmedian(data2_log)
        if vmin >= vcenter or vcenter >= vmax:
            vcenter = (vmin + vmax) / 2

        norm = TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
        img2 = ax.imshow(data2_log, cmap='Oranges', norm=norm, extent=(bounds[0], bounds[2], bounds[1], bounds[3]), alpha=0.7)
        plt.colorbar(img2, ax=ax, orientation='vertical', fraction=0.02, pad=0.04, label='Log-scaled River Flood Risk Level')

    # Plot the solar facilities
    if is_local:
        operating_facilities.plot(ax=ax, marker='o', color='green', markersize=5, label='Operating Facility', alpha=0.8)
        planned_facilities.plot(ax=ax, marker='o', color='red', markersize=5, label='Planned Facility', alpha=0.8)
    else:
        operating_facilities.plot(ax=ax, marker='o', color='green', markersize=0.15, label='Operating Facility', alpha=0.3)
        planned_facilities.plot(ax=ax, marker='o', color='red', markersize=0.15, label='Planned Facility', alpha=0.3)

    ax.legend(markerscale=2)
    ax.set_title(title)
    if region_bounds:
        ax.set_xlim(region_bounds[0], region_bounds[2])
        ax.set_ylim(region_bounds[1], region_bounds[3])

# 3. Plotting the maps
# Facility types
facility_types = ['solar']

# Regions to focus on
regions = {
    "Korea": [124, 33, 130, 39],
}

# Loop through each facility type and create maps
for facility_type in facility_types:
    # Filter facilities by type
    selected_facilities = gdf[gdf['Type'].str.lower() == facility_type]
    operating_facilities = selected_facilities[selected_facilities['Status'] == 'operating']
    planned_facilities = selected_facilities[selected_facilities['Status'].isin(['construction', 'pre-construction', 'announced'])]

    # Plot global map (commented out for testing)
    # fig, ax = plt.subplots(figsize=(15, 10))
    # plot_map(ax, title=f"Global Map: {facility_type.capitalize()} Facilities with Flood Risk")
    # plt.tight_layout()
    # plt.savefig(f'outputs/global_{facility_type}_map.jpg', format='jpg', dpi=300)
    # plt.close()

    # Plot local maps for each region (Korea only for testing)
    for region_name, bounds in regions.items():
        fig, ax = plt.subplots(figsize=(10, 10))
        plot_map(ax, region_bounds=bounds, title=f"{region_name}: {facility_type.capitalize()} Facilities with Flood Risk", is_local=True)
        plt.tight_layout()
        plt.savefig(f'outputs/{region_name.lower().replace(" ", "_")}_{facility_type}_map.jpg', format='jpg', dpi=300)
        plt.close()
