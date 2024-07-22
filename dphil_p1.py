import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import os
import glob
import rasterio
from rasterio.merge import merge
from rasterio.enums import Resampling
import numpy as np
from concurrent.futures import ThreadPoolExecutor

### 1. Renewable Energy (RE) data: "gdf" is the GeoDataFrame containing the RE data

# Path to the Excel dataset
dataset_path = 're_data/Global-Integrated-Power-June-2024.xlsx'

# Specify the sheet name from the file
sheet_name = 'Powerfacilities'

# Read the dataset from the specified sheet using pandas
df = pd.read_excel(dataset_path, sheet_name=sheet_name)

# Convert the DataFrame to a GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry=[Point(xy) for xy in zip(df.Longitude, df.Latitude)])

### 2. World map data: "world" is the GeoDataFrame containing the world map data
# Path to the .shp file
shapefile_path = 'ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp'

# Load the world map
world = gpd.read_file(shapefile_path)

# Set the coordinate reference system (CRS) to WGS84 (EPSG:4326)
gdf.crs = "EPSG:4326"

# Ensure both GeoDataFrames are using the same CRS
if gdf.crs != world.crs:
    world = world.to_crs(gdf.crs)

### 3. Extracting flood data from .tif files and merging them
# Path to the directory where the .tif files are stored
directory_path = "C:/Users/jjh68/OneDrive - Nexus365/hazard_data/flood_data1/rp500/"

# Find all .tif files in the directory
tif_files = glob.glob(os.path.join(directory_path, "*.tif"))

# Use a subset of files for testing
test_tif_files = tif_files[:]  # Use all files for testing

# List to hold in-memory datasets for merging
datasets = []

# Define a lower resampling factor
resampling_factor = 16

# Assume CRS for flood data if not specified
assumed_flood_crs = "EPSG:4326"  # Change this if you know the correct CRS

# Function to process a single .tif file
def process_tif_file(tif_file):
    with rasterio.open(tif_file) as src:
        # Check and set CRS if not already set
        if src.crs is None:
            src.crs = assumed_flood_crs
        
        # Calculate new shape
        data = src.read(
            out_shape=(
                src.count,
                int(src.height / resampling_factor),
                int(src.width / resampling_factor)
            ),
            resampling=Resampling.bilinear
        )

        # Check the resampled data
        print(f"Resampled data shape: {data.shape}")
        print(f"Resampled data min: {data.min()}, max: {data.max()}")

        # Update the dataset's transform attribute
        transform = src.transform * src.transform.scale(
            (src.width / data.shape[-1]),
            (src.height / data.shape[-2])
        )

        # Create a new in-memory dataset
        profile = src.profile
        profile.update(
            driver='GTiff',
            height=data.shape[1],
            width=data.shape[2],
            transform=transform,
            crs=src.crs
        )

        memfile = rasterio.io.MemoryFile()
        dataset = memfile.open(**profile)
        dataset.write(data)
        return dataset

# Process files in parallel
with ThreadPoolExecutor() as executor:
    datasets = list(executor.map(process_tif_file, test_tif_files))

# Merging the data
merged, transform = merge(datasets)

# Ensure the merged data has the correct CRS
if merged.crs is None:
    merged.crs = assumed_flood_crs

# Reproject the merged flood data to match the CRS of the world map
world_crs = world.crs.to_string()
merged_flood_data, merged_flood_transform = rasterio.warp.reproject(
    source=merged,
    destination=np.empty_like(merged),
    src_transform=transform,
    src_crs=merged.crs,
    dst_transform=transform,
    dst_crs=world_crs,
    resampling=Resampling.bilinear
)

# Calculate the extent of the reprojected flood data
flood_extent = rasterio.transform.array_bounds(merged_flood_data.shape[1], merged_flood_data.shape[2], merged_flood_transform)

### 4. Plotting the flood data only to ensure alignment
plt.figure(figsize=(10, 6))
plt.imshow(merged_flood_data[0], cmap='Blues', alpha=.5, extent=flood_extent)
plt.title('Flood Data Alone')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.savefig('flood_data_alone.jpg', format='jpg', dpi=300)
plt.show()
plt.close()

### 5. Plotting the global distribution of renewable energy facilities with flood data overlay

# Select a subset of facility types for testing
facility_types = ['solar']

# Calculate the common extent
common_extent = [
    min(world.total_bounds[0], flood_extent[0]),
    min(world.total_bounds[1], flood_extent[1]),
    max(world.total_bounds[2], flood_extent[2]),
    max(world.total_bounds[3], flood_extent[3])
]

# Iterate over each facility type and create a map
for facility_type in facility_types:
    # Filter for the selected facility types
    selected_facilities = gdf[gdf['Type'].str.lower() == facility_type]

    # Filter for "operating" facilities
    operating_facilities = selected_facilities[selected_facilities['Status'] == 'operating']
    print(f'Number of operating {facility_type}: {len(operating_facilities)}')

    # Filter for "planned" facilities (construction, pre-construction, announced)
    planned_statuses = ['construction', 'pre-construction', 'announced']
    planned_facilities = selected_facilities[selected_facilities['Status'].isin(planned_statuses)]
    print(f'Number of planned {facility_type}: {len(planned_facilities)}')

    # Plotting 
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot the world map with white fill and light grey borders
    world.plot(ax=ax, color='white', edgecolor='lightgrey')

    # Plot "operating" facilities in green
    operating_facilities.plot(ax=ax, marker='o', color='green', markersize=5, label=f'Operating {facility_type.title()}', alpha=0.6)

    # Plot "planned" facilities in red
    planned_facilities.plot(ax=ax, marker='o', color='red', markersize=5, label=f'Planned {facility_type.title()}', alpha=0.6)

    # Plot the flood data on top
    ax.imshow(merged_flood_data[0], cmap='Blues', alpha=0.5, extent=flood_extent)

    # Legend and titles
    ax.legend(markerscale=2)
    ax.set_title(f'Global Distribution of {facility_type.title()} Facilities with Flood Risk (Ver 0.1 - Ji)')

    # Ensure the coordinate limits are the same for all layers
    ax.set_xlim(common_extent[0], common_extent[2])
    ax.set_ylim(common_extent[1], common_extent[3])

    # Save the figure to a JPG file
    plt.tight_layout()      
    plt.savefig(f'{facility_type.replace("/", "_")}_facilities_flood_map.jpg', format='jpg', dpi=300)
    plt.close()
