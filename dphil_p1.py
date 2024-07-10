import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
from other_data.ldc_list import ldc_countries

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

# Create subplots with adjusted layout
fig, axs = plt.subplots(1, 2, figsize=(20, 5))

# Plot the world map on the first subplot
world.plot(ax=axs[0], color='lightgrey')

# Highlight LDC countries with a more vibrant color
ldc_world.plot(ax=axs[0], color='lightblue', alpha=0.9)

# Overlay LDC solar projects with larger markers and more transparency
ldc_solar_projects.plot(ax=axs[0], marker='o', color='blue', markersize=1, alpha=0.1, label='LDC Solar Projects')

# Overlay non-LDC solar projects with larger markers and more transparency
non_ldc_solar_projects.plot(ax=axs[0], marker='o', color='red', markersize=1, alpha=0.1, label='Non-LDC Solar Projects')

# Enhance titles and labels
axs[0].set_title('Solar Power Projects Distribution', fontsize=16)
axs[0].set_xlabel('Longitude', fontsize=10)
axs[0].set_ylabel('Latitude', fontsize=10)
axs[0].legend()

# Step 1: Group by 'Country' and count the number of facilities
facilities_per_country = ldc_solar_projects.groupby('Country/area').size()

# Step 2: Sort the counts in descending order
facilities_per_country_sorted = facilities_per_country.sort_values(ascending=False)

# Plot the bar graph with a more contrasting color and adjust layout
facilities_per_country_sorted.plot(kind='bar', ax=axs[1], color='darkgreen', alpha=0.7)

# Enhance titles and labels for the bar graph
axs[1].set_title('Number of Solar Power Facilities per LDC Country', fontsize=16)
axs[1].set_xlabel('Country', fontsize=10)
axs[1].set_ylabel('Number of Facilities', fontsize=10)
axs[1].tick_params(axis='x', rotation=90)  # Rotate country names for better readability

plt.tight_layout()
plt.show()


