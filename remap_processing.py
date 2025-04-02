# import numpy as np

# # Define the latitude and longitude ranges for Greenland
# lat_start, lat_end = 59, 84
# lon_start, lon_end = -74, -40

# xsize = 35
# ysize = 30

# # Create the grid
# latitudes = np.linspace(lat_start, lat_end, 30)
# longitudes = np.linspace(lon_start, lon_end, 35)

# # Create 2D arrays for the grid points
# lon2d, lat2d = np.meshgrid(longitudes, latitudes)

# # Flatten the arrays to match the expected format
# xvals = lon2d.flatten()
# yvals = lat2d.flatten()

# Print values to use in xvals and yvals
# print(f"xvals = {', '.join(map(str, xvals))}")
# print(f"yvals = {', '.join(map(str, yvals))}")


import numpy as np

# Grid size
xsize = 50
ysize = 20

# Define the starting points and increments
xfirst = (-6)
yfirst = (-12)
xinc = 1.0
yinc = 1.0

# Generate coordinate arrays
lon = np.linspace(xfirst, xfirst + (xsize - 1) * xinc, xsize)
lat = np.linspace(yfirst, yfirst + (ysize - 1) * yinc, ysize)

lon2d, lat2d = np.meshgrid(lon, lat)

# Save arrays to file
with open('1degree_curvilin2.txt', 'w') as f:
    f.write('gridtype  = curvilinear\n')
    f.write(f'gridsize  = {xsize * ysize}\n')
    f.write(f'xsize     = {xsize}\n')
    f.write(f'ysize     = {ysize}\n')
    f.write('xname     = lon\n')
    f.write('yname     = lat\n')
    f.write('xlongname = "longitude"\n')
    f.write('ylongname = "latitude"\n')
    f.write('xunits    = "degrees_east"\n')
    f.write('yunits    = "degrees_north"\n')
    f.write('xvals     = ')
    np.savetxt(f, lon2d.flatten(), fmt='%.2f', newline=' ')
    f.write('\nyvals     = ')
    np.savetxt(f, lat2d.flatten(), fmt='%.2f', newline=' ')
