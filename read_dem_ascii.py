# -*- coding: utf-8 -*-
"""
Created on Mon Oct 26 11:34:05 2015

@author: jpeacock
"""
import numpy as np
import mtpy.utils.latlongutmconversion as ll2utm


ascii_fn = r"c:\Users\jpeacock\Documents\SanPabloBay\sp_10mtopo_bathy.asc"
cell_size = 50.
rot_90 = 3
model_center = (548890., 4221350.)


dfid = file(ascii_fn, 'r')
d_dict = {}
for ii in range(6):
    dline = dfid.readline()
    dline = dline.strip().split()
    key = dline[0].strip().lower()
    value = float(dline[1].strip())
    d_dict[key] = value
    
x0 = d_dict['xllcorner']
y0 = d_dict['yllcorner']
nx = int(d_dict['ncols'])
ny = int(d_dict['nrows'])
cs = d_dict['cellsize']

# read in the elevation data
elevation = np.zeros((nx, ny))

for ii in range(1, int(ny)+2):
    dline = dfid.readline()
    if len(str(dline)) > 1:
        #needs to be backwards because first line is the furthest north row.
        elevation[:, -ii] = np.array(dline.strip().split(' '), dtype='float')
    else:
        break
dfid.close()

# create lat and lon arrays from the dem fle
lon = np.arange(x0, x0+cs*(nx), cs)
lat = np.arange(y0, y0+cs*(ny), cs)

# calculate the lower left and uper right corners of the grid in meters
ll_en = ll2utm.LLtoUTM(23, lat[0], lon[0])
ur_en = ll2utm.LLtoUTM(23, lat[-1], lon[-1])

# estimate cell sizes for each dem measurement
d_east = abs(ll_en[1]-ur_en[1])/nx
d_north = abs(ll_en[2]-ur_en[2])/ny

# calculate the number of new cells
num_cells = int(cell_size/np.mean([d_east, d_north]))

# make easting and northing arrays in meters corresponding to lat and lon
east = np.arange(ll_en[1], ur_en[1], d_east)
north = np.arange(ll_en[2], ur_en[2], d_north)

#resample the data accordingly
new_east = east[np.arange(0, east.shape[0], num_cells)]
new_north = north[np.arange(0, north.shape[0], num_cells)]
new_x, new_y = np.meshgrid(np.arange(0, east.shape[0], num_cells),
                           np.arange(0, north.shape[0], num_cells),
                           indexing='ij') 
elevation = elevation[new_x, new_y]

# estimate the shift of the DEM to relative model coordinates
shift_east = new_east.mean()-model_center[0]
shift_north = new_north.mean()-model_center[1]

# shift the easting and northing arrays accordingly so the DEM and model
# are collocated.
new_east = (new_east-new_east.mean())+shift_east
new_north = (new_north-new_north.mean())+shift_north

# need to rotate cause I think I wrote the dem backwards
elevation = np.rot90(elevation, rot_90)