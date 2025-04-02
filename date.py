from netCDF4 import Dataset, num2date
import numpy as np

# Open the dataset
dataset = Dataset('/mnt/d/RACMO/HIST/2degree-remapnn-somevariables-fullgreenland.KNMI-1950-2014.FGRN11.BN_RACMO2.3p2_CESM2_FGRN11.DD.nc')

# Access the time variable
time_var = dataset.variables['time']

# Identify the calendar type
if hasattr(time_var, 'calendar'):
    calendar_type = time_var.calendar
else:
    calendar_type = 'standard'
print(f"Calendar type: {calendar_type}")

# Convert cftime objects to datetime objects if necessary
time_values = time_var[:]
datetime_values = num2date(time_values, units=time_var.units, calendar=calendar_type)
years = np.asarray([dt.year for dt in datetime_values])

print(years)
