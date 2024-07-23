import ee
import geemap
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import urllib.request

# Authenticate and initialize the Earth Engine API
ee.Authenticate()
ee.Initialize(project='oxford-jihyeonjeong')

# Load the ESA WorldCover dataset
dataset = ee.ImageCollection('ESA/WorldCover/v200').first()

# Define visualization parameters
visualization = {
    'bands': ['Map'],
    'min': 0,
    'max': 100,
    'palette': [
        '006400', '228B22', '7FFFD4', '32CD32', '00FF00', 'ADFF2F',
        'FF0000', 'FFD700', 'FFA500', '808080', '0000FF', '00FFFF',
        '191970', '000080'
    ]
}

# Get the URL for the image
url = dataset.getThumbURL({
    'min': 0,
    'max': 100,
    'dimensions': 1024,
    'palette': visualization['palette']
})

# Print the URL for debugging
print("URL:", url)

# Open the URL and read the image
with urllib.request.urlopen(url) as url_response:
    img = np.array(Image.open(url_response))

# Check the shape of the image array
print("Image shape:", img.shape)

# Plot the data using Matplotlib
fig, ax = plt.subplots(figsize=(15, 10))

# Plot the Earth Engine image (no extent for global view)
ax.imshow(img)

# Set title and labels
ax.set_title("ESA WorldCover Global Map")
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")

# Show the plot
plt.savefig('google_engine_landcover_map.jpg', format='jpg', dpi=300)
plt.close()

