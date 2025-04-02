#!/usr/bin/env python3.10

import netCDF4

# def get_netcdf_version(file_path):
#     nc = netCDF4.Dataset(file_path, 'r')
#     version = nc.file_format
#     nc.close()
#     return version

# file_path = 'X_EUC12_fullvar_smth3_aero_2000-01-01.nc'
# version = get_netcdf_version(file_path)
# print("NetCDF version:", version)


import xarray as xr

# Open the original NetCDF file
ds = xr.open_dataset('/home/vmarko/VU/BSC_project/RCM-Emulator/X_EUC12_fullvar_smth3_aero_2000-01-01.nc')

# Extract grid-related information
# For example, let's assume latitude and longitude are the grid coordinates
# You may need to adjust this based on your specific dataset
lat = ds['lat']
lon = ds['lon']

# Create a new dataset with grid information
grid_ds = xr.Dataset({'lat': lat, 'lon': lon})

# Add x and y coordinates to the new dataset
grid_ds['x'] = range(len(lon))
grid_ds['y'] = range(len(lat))

# Save the new dataset as a NetCDF file
grid_ds.to_netcdf('/home/vmarko/VU/BSC_project/RCM-Emulator/grid_info.nc')
