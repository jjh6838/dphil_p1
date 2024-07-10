import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
from other_data.ldc_list import ldc_countries
import itertools

# Path to the Excel dataset
dataset_path = 're_data/Global-Integrated-Power-June-2024.xlsx'

# Specify the sheet name to be read from the file
sheet_name = 'Powerfacilities'

# Read the dataset from the specified sheet using pandas
df = pd.read_excel(dataset_path, sheet_name=sheet_name)

# Convert the DataFrame to a GeoDataFrame
# Assuming 'Latitude' and 'Longitude' are the column names
gdf = gpd.GeoDataFrame(df, geometry=[Point(xy) for xy in zip(df.Longitude, df.Latitude)])

# Replace the path below with the actual path to the .shp file on your system
shapefile_path = 'ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp'

# Load the world map
world = gpd.read_file(shapefile_path)

# Set the coordinate reference system (CRS) to WGS84 (EPSG:4326)
gdf.crs = "EPSG:4326"

# Ensure both GeoDataFrames are using the same CRS
if gdf.crs != world.crs:
    world = world.to_crs(gdf.crs)

# Filter for LDC countries
ldc_world = world[world['ISO_A3'].isin(ldc_countries)]

# Perform a left join to include all records from gdf
all_solar_projects = gpd.sjoin(gdf, ldc_world, how="left", predicate='intersects')

# Filter out records that did not match, i.e., where 'index_right' is NaN
non_ldc_solar_projects = all_solar_projects[all_solar_projects.index_right.isna()]

# Perform a spatial join between the solar projects and LDC countries
ldc_solar_projects = gpd.sjoin(gdf, ldc_world, how="inner", predicate='intersects')


# Plotting
# Define colors for each project type
color_map = {
    'solar': 'red',
    'wind': 'orange',
    'hydropower': 'green',
    'bioenergy': 'blue',
    'geothermal': 'brown',
    'nuclear': 'cyan',
    'coal': 'purple',
    'oil/gas': 'pink',
}

project_types = gdf['Type'].unique()

# Ensure there are 8 unique project types
assert len(project_types) == 8, "There must be exactly 8 unique project types."

# Create a 2x4 grid of subplots
fig, axs = plt.subplots(2, 4, figsize=(20, 10))
axs = axs.flatten()  # Flatten the 2D array of axes to easily iterate over it

for i, project_type in enumerate(project_types):
    world.plot(ax=axs[i], color='lightgray')  # World map as the background
    subset = gdf[gdf['Type'] == project_type]
    color = color_map[project_type.lower()]
    subset.plot(ax=axs[i], marker='o', markersize=1, label=project_type, alpha=0.1, color=color)
    axs[i].legend()
    axs[i].set_title(f'Global Distribution of {project_type.upper()} Facilities')

# Adjust layout to prevent overlap
plt.tight_layout()
plt.show()