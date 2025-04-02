import numpy as np

# Define the ranges for longitude and latitude
lon_start = -51.9314501375155
lon_end = 6.54818300296634
lat_start = 58.1678756792473
lat_end = 81.9001007312219

# Calculate the number of grid points needed
lon_points = 60
lat_points = 25

# Generate the xvals and yvals with appropriate resolution
xvals = np.linspace(lon_start, lon_end, lon_points)
yvals = np.linspace(lat_start, lat_end, lat_points)

# Initialize strings to store formatted xvals and yvals
formatted_xvals = ""
formatted_yvals = ""

# Format xvals
for val in xvals:
    formatted_xvals += f"{val:.12f} "

# Format yvals
for val in yvals:
    formatted_yvals += f"{val:.12f} "

# Create the grid description with the formatted values
grid_description = f"""
gridtype  = curvilinear
gridsize  = {len(xvals) * len(yvals)}
xsize     = {len(xvals)}
ysize     = {len(yvals)}
xname     = lon
xdimname  = rlon
xlongname = "longitude"
xunits    = "degrees_east"
yname     = lat
ydimname  = rlat
ylongname = "latitude"
yunits    = "degrees_north"
xvals     = {formatted_xvals.strip()}
yvals     = {formatted_yvals.strip()}
scanningMode = 64

gridtype  = projection
gridsize  = {len(xvals) * len(yvals)}
xsize     = {len(xvals)}
ysize     = {len(yvals)}
xname     = rlon
xlongname = "longitude in rotated pole grid"
xunits    = "degrees"
yname     = rlat
ylongname = "latitude in rotated pole grid"
yunits    = "degrees"
xfirst    = -7.75
xinc      = 1.0
yfirst    = -12.9
yinc      = 1.0
scanningMode = 64
grid_mapping = rotated_pole
grid_mapping_name = rotated_latitude_longitude
grid_north_pole_latitude = 18.f
grid_north_pole_longitude = 142.5f
proj4_params = "-m 57.295779506 +proj=ob_tran +o_proj=latlon +o_lat_p=18.0 +lon_0=-37.5"
proj_parameters = "-m 57.295779506 +proj=ob_tran +o_proj=latlon +o_lat_p=18.0 +lon_0=-37.5"
projection_name = "rotated_latitude_longitude"
long_name = "projection details"
"""

# Write the grid description to a file
with open("1degree_grid_description.txt", "w") as file:
    file.write(grid_description)

print("Grid description written to 1degree_grid_description.txt")
