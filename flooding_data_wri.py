import os
import rasterio
import matplotlib.pyplot as plt
import pickle

# Define file paths
tif_path = r'C:\Users\jjh68\OneDrive\Desktop\dphil_p1\flooding_data_wri\inuncoast_rcp8p5_wtsub_2050_rp1000_0.tif'
pickle_path = r'C:\Users\jjh68\OneDrive\Desktop\dphil_p1\flooding_data_wri\inuncoast_rcp8p5_wtsub_2050_rp1000_0.pickle'

# Function to read and plot the .tif file
def read_and_plot_tif(tif_path):
    with rasterio.open(tif_path) as src:
        # Read the data
        data = src.read(1)
        
        # Plot the data
        plt.figure(figsize=(10, 10))
        plt.imshow(data, cmap='viridis')
        plt.colorbar(label='Flooding Level')
        plt.title('Flooding Data from TIF')
        plt.xlabel('X coordinate')
        plt.ylabel('Y coordinate')
        plt.show()

        # Print metadata
        metadata = src.meta
        print("Metadata for the TIF file:")
        for key, value in metadata.items():
            print(f"{key}: {value}")

# Function to load and inspect the .pickle file
def load_and_inspect_pickle(pickle_path):
    with open(pickle_path, 'rb') as f:
        data = pickle.load(f)
        
        # Inspect the data (example: if it's a dictionary)
        if isinstance(data, dict):
            print("Data from the pickle file (Dictionary):")
            for key, value in data.items():
                print(f"{key}: {value}")
   
        # If the data is a list or numpy array, you can plot or print it
        elif isinstance(data, list):
            print("Data from the pickle file (List):")
            for item in data:
                print(item)
            # Example plot if it's numerical data
            if all(isinstance(i, (int, float)) for i in data):
                plt.figure(figsize=(10, 5))
                plt.plot(data)
                plt.title('Flooding Data from Pickle (List)')
                plt.xlabel('Index')
                plt.ylabel('Value')
                plt.show()

        elif isinstance(data, np.ndarray):
            print("Data from the pickle file (NumPy Array):")
            print(data)
            # Plot if it's a 1D or 2D array
            if data.ndim == 1:
                plt.figure(figsize=(10, 5))
                plt.plot(data)
                plt.title('Flooding Data from Pickle (1D Array)')
                plt.xlabel('Index')
                plt.ylabel('Value')
                plt.show()
            elif data.ndim == 2:
                plt.figure(figsize=(10, 10))
                plt.imshow(data, cmap='viridis')
                plt.colorbar(label='Value')
                plt.title('Flooding Data from Pickle (2D Array)')
                plt.xlabel('X coordinate')
                plt.ylabel('Y coordinate')
                plt.show()
        else:
            print("Data type not recognized. Here is the raw data:")
            print(data)

# Call the functions to read and display the data
read_and_plot_tif(tif_path)
load_and_inspect_pickle(pickle_path)
