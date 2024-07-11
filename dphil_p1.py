import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
from other_data.ldc_list import ldc_countries
import itertools

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

### (Pending) LDC overlapping
# Filter for LDC countries
# ldc_world = world[world['ISO_A3'].isin(ldc_countries)]

# Perform a left join to include all records from gdf
# all_solar_projects = gpd.sjoin(gdf, ldc_world, how="left", predicate='intersects')

# Filter out records that did not match, i.e., where 'index_right' is NaN
# non_ldc_solar_projects = all_solar_projects[all_solar_projects.index_right.isna()]

# Perform a spatial join between the solar projects and LDC countries
# ldc_solar_projects = gpd.sjoin(gdf, ldc_world, how="inner", predicate='intersects')
###

### (Pending) Define colors for each project type
# color_map = {
#     'solar': 'red',
#     'wind': 'orange',
#     'hydropower': 'green',
#     'bioenergy': 'blue',
#     'geothermal': 'brown',
#     'nuclear': 'cyan',
#     'coal': 'purple',
#     'oil/gas': 'pink',
# }
###

### 3. Plotting the global distribution of renewable energy facilities

# Select the facility types to plot
facility_types = ['solar', 'wind', 'hydropower', 'oil/gas']

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

    # Plot the world map as the background
    world.plot(ax=ax, color='lightgray')

    # Plot "operating" facilities in green
    operating_facilities.plot(ax=ax, marker='o', color='green', markersize=1, label=f'Operating {facility_type.title()}', alpha=0.15)

    # Plot "planned" facilities in red
    planned_facilities.plot(ax=ax, marker='o', color='red', markersize=1, label=f'Planned {facility_type.title()}', alpha=0.15)

    # Legend and titles
    ax.legend(markerscale=5)
    ax.set_title(f'Global Distribution of {facility_type.title()} Facilities (Ver 0.1 - Ji)')

    # Save the figure to a JPG file
    plt.tight_layout()      
    plt.savefig(f'{facility_type.replace("/", "_")}_facilities_map.jpg', format='jpg', dpi=300)
    plt.close()