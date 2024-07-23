import ee
import geemap

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

# Create a map centered on the dataset
Map = geemap.Map(center=[0, 0], zoom=3)

# Add the dataset layer to the map
Map.addLayer(dataset, visualization, 'Landcover')

# Display the map
Map.addLayerControl()  # This adds the layer control to the map
Map
