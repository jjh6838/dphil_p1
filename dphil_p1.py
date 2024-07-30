import pandas as pd
import geopandas as gpd
import numpy as np
from matplotlib.colors import TwoSlopeNorm
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from shapely.geometry import Point
from shapely.geometry import LineString
import rasterio
from rasterio.plot import show
import ee
from scipy.ndimage import distance_transform_edt

# 1. Importing inputs
# Authenticate and initialize the Earth Engine API
ee.Authenticate()
ee.Initialize(project='oxford-jihyeonjeong')

# Renewable energy facility map
dataset_path = 're_data/Global-Integrated-Power-June-2024.xlsx'
sheet_name = 'Powerfacilities'

# Read the dataset from the specified sheet using pandas
df = pd.read_excel(dataset_path, sheet_name=sheet_name)

# Convert the DataFrame to a GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry=[Point(xy) for xy in zip(df.Longitude, df.Latitude)])

# Set the coordinate reference system (CRS) to WGS84 (EPSG:4326)
gdf.crs = "EPSG:4326"

# World map as background
shapefile_path = '01_country_shp/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp'
world = gpd.read_file(shapefile_path)

# Ensure both GeoDataFrames are using the same CRS
if gdf.crs != world.crs:
    world = world.to_crs(gdf.crs)

# Flood maps (RCP 8.5, 2050, 10-year return period)
tif_file_path1 = 'flooding_data_wri/inuncoast_rcp8p5_nosub_2050_rp0010_0.tif'
tif_file_path2 = 'flooding_data_wri/inunriver_rcp8p5_00000NorESM1-M_2050_rp00010.tif'

# 2. Function to plot the maps
def plot_map(ax, region_bounds=None, title="", is_local=False):
    if region_bounds:
        bounds = region_bounds
    else:
        bounds = world.total_bounds  # Default to global

    world.plot(ax=ax, color="grey", edgecolor='black', linewidth=0.1, alpha=0.1)

    with rasterio.open(tif_file_path1) as src1:
        window = rasterio.windows.from_bounds(*bounds, transform=src1.transform)
        data1_crop = src1.read(1, window=window)
        data1_crop[data1_crop <= 0] = np.nan
        data1_log = np.log1p(data1_crop)
        
        vmin, vmax = np.nanmin(data1_log), np.nanmax(data1_log)
        vcenter = np.nanmedian(data1_log)
        if vmin >= vcenter or vcenter >= vmax:
            vcenter = (vmin + vmax) / 2

        norm = TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
        img1 = ax.imshow(data1_log, cmap='Blues', norm=norm, extent=(bounds[0], bounds[2], bounds[1], bounds[3]), alpha=0.7)
        plt.colorbar(img1, ax=ax, orientation='vertical', fraction=0.02, pad=0.1,label='Log-scaled Coastal Flood Risk Level')

    with rasterio.open(tif_file_path2) as src2:
        window = rasterio.windows.from_bounds(*bounds, transform=src2.transform)
        data2_crop = src2.read(1, window=window)
        data2_crop[data2_crop <= 0] = np.nan
        data2_log = np.log1p(data2_crop)
        
        vmin, vmax = np.nanmin(data2_log), np.nanmax(data2_log)
        vcenter = np.nanmedian(data2_log)
        if vmin >= vcenter or vcenter >= vmax:
            vcenter = (vmin + vmax) / 2

        norm = TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
        img2 = ax.imshow(data2_log, cmap='Oranges', norm=norm, extent=(bounds[0], bounds[2], bounds[1], bounds[3]), alpha=0.7)
        plt.colorbar(img2, ax=ax, orientation='vertical', fraction=0.02, pad=0.2, label='Log-scaled River Flood Risk Level')

    if is_local:
        operating_facilities.plot(ax=ax, marker='o', color='green', markersize=5, label='Operating Facility', alpha=0.8)
        planned_facilities.plot(ax=ax, marker='o', color='red', markersize=5, label='Planned Facility', alpha=0.8)
    else:
        operating_facilities.plot(ax=ax, marker='o', color='green', markersize=0.15, label='Operating Facility', alpha=0.3)
        planned_facilities.plot(ax=ax, marker='o', color='red', markersize=0.15, label='Planned Facility', alpha=0.3)

    for facility in gdf.itertuples():
        # Get the facility's point
        facility_point = facility.geometry

        # Calculate the distance to the nearest coastal flood risk point
        with rasterio.open(tif_file_path1) as src1:
            coastal_data = src1.read(1, window=window)
            coastal_mask = np.isnan(coastal_data)
            coastal_distances = distance_transform_edt(coastal_mask)
            min_dist_coastal = coastal_distances.min()
            # Get the coordinates of the nearest flood risk point
            closest_coastal = np.unravel_index(coastal_distances.argmin(), coastal_distances.shape)
            closest_coastal_point = src1.xy(closest_coastal[0], closest_coastal[1])
            line_to_coastal = LineString([facility_point, closest_coastal_point])
            ax.plot(*line_to_coastal.xy, color='blue', linewidth=1, alpha=0.5)

        # Calculate the distance to the nearest river flood risk point
        with rasterio.open(tif_file_path2) as src2:
            river_data = src2.read(1, window=window)
            river_mask = np.isnan(river_data)
            river_distances = distance_transform_edt(river_mask)
            min_dist_river = river_distances.min()
            # Get the coordinates of the nearest flood risk point
            closest_river = np.unravel_index(river_distances.argmin(), river_distances.shape)
            closest_river_point = src2.xy(closest_river[0], closest_river[1])
            line_to_river = LineString([facility_point, closest_river_point])
            ax.plot(*line_to_river.xy, color='orange', linewidth=1, alpha=0.5)

    ax.legend(markerscale=4)
    ax.set_title(title)
    if region_bounds:
        ax.set_xlim(region_bounds[0], region_bounds[2])
        ax.set_ylim(region_bounds[1], region_bounds[3])

# 3. Plotting the maps
facility_types = ['solar']
regions = {
    "Korea": [124, 33, 130, 39],
}

for facility_type in facility_types:
    selected_facilities = gdf[gdf['Type'].str.lower() == facility_type]
    operating_facilities = selected_facilities[selected_facilities['Status'] == 'operating']
    planned_facilities = selected_facilities[selected_facilities['Status'].isin(['construction', 'pre-construction', 'announced'])]

    for region_name, bounds in regions.items():
        fig, ax = plt.subplots(figsize=(16, 9))
        plot_map(ax, region_bounds=bounds, title=f"{region_name}: {facility_type.capitalize()} Facilities with Flood Risk", is_local=True)
        plt.tight_layout()
        plt.savefig(f'outputs/{region_name.lower().replace(" ", "_")}_{facility_type}_map.jpg', format='jpg', dpi=300)
        plt.close()