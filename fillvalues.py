import netCDF4 as nc

# Path to your NetCDF file
file_path = '/mnt/d/RACMO/1degree-upvars+precip-1960-1970-result.nc'  # Replace with your actual file path

# Open the NetCDF file in append mode
dataset = nc.Dataset(file_path, 'r+')

# Create the rotated_pole variable (int type)
rotated_pole = dataset.createVariable('rotated_pole2', 'i4')

# Add the specified attributes to the rotated_pole variable
rotated_pole.proj_parameters = "-m 57.295779506 +proj=ob_tran +o_proj=latlon +o_lat_p=18.0 +lon_0=-37.5"
rotated_pole.projection_name = "rotated_latitude_longitude"
rotated_pole.long_name = "projection details"
rotated_pole.proj4_params = "-m 57.295779506 +proj=ob_tran +o_proj=latlon +o_lat_p=18.0 +lon_0=-37.5"
rotated_pole.grid_north_pole_longitude = "142.5f"
rotated_pole.grid_mapping_name = "rotated_latitude_longitude"
rotated_pole.grid_north_pole_latitude = "18.0f"

# Close the dataset to write changes to the file
dataset.close()
