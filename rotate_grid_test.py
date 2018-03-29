# -*- coding: utf-8 -*-
"""
Created on Wed Jul 09 08:52:57 2014

@author: jpeacock-pr
"""
import numpy as np
import os
import mtpy.core.mt as mt
import matplotlib.pyplot as plt

edipath = r"d:\Peacock\MTData\EDI_Folders\LV_EDI_Files"
edilst = [mt.MT(os.path.join(edipath, edi)) for edi in os.listdir(edipath)[0:20]
          if edi.find('.edi') > 0]

cell_size_east = 500.
cell_size_north = 500.
pad_east=12
pad_north = 12 
pad_stretch_h = 1.2
pad_stretch_v = 1.5

mesh_rotation_angle = 30.

cos_ang = np.cos(np.deg2rad(mesh_rotation_angle))
sin_ang = np.sin(np.deg2rad(mesh_rotation_angle))
rot_matrix = np.matrix(np.array([[cos_ang, sin_ang], 
                                 [-sin_ang, cos_ang]]))

n_stations = len(edilst)
#make a structured array to put station location information into
station_locations = np.zeros(n_stations,
                                  dtype=[('station','|S10'),
                                         ('lat', np.float),
                                         ('lon', np.float),
                                         ('east', np.float),
                                         ('north', np.float),
                                         ('zone', '|S4'),
                                         ('rel_east', np.float),
                                         ('rel_north', np.float),
                                         ('elev', np.float)])
#get station locations in meters
for ii, mt_obj in enumerate(edilst):
    station_locations[ii]['lat'] = mt_obj.lat
    station_locations[ii]['lon'] = mt_obj.lon
    station_locations[ii]['station'] = mt_obj.station
    station_locations[ii]['east'] = mt_obj.east
    station_locations[ii]['north'] = mt_obj.north
    station_locations[ii]['elev'] = mt_obj.elev
    station_locations[ii]['zone'] = mt_obj.utm_zone

#remove the average distance to get coordinates in a relative space
station_locations['rel_east'] = station_locations['east']-\
                                     station_locations['east'].mean()
station_locations['rel_north'] = station_locations['north']-\
                                      station_locations['north'].mean()

#--> rotate grid if necessary
#to do this rotate the station locations because ModEM assumes the
#input mesh is a lateral grid.
#needs to be 90 - because North is assumed to be 0 but the rotation
#matrix assumes that E is 0.
if mesh_rotation_angle != 0:
    cos_ang = np.cos(np.deg2rad(mesh_rotation_angle))
    sin_ang = np.sin(np.deg2rad(mesh_rotation_angle))
    rot_matrix = np.matrix(np.array([[cos_ang, sin_ang], 
                                     [-sin_ang, cos_ang]]))
                                     
    coords = np.array([station_locations['rel_east'],
                       station_locations['rel_north']])
    
    #rotate the relative station locations
    new_coords = np.array(np.dot(rot_matrix, coords))
    
    station_locations['rel_east'][:] = new_coords[0, :]
    station_locations['rel_north'][:] = new_coords[1, :]
    
    print 'Rotated stations by {0:.1f} deg clockwise from N'.format(
                                            mesh_rotation_angle)
 
#translate the stations so they are relative to 0,0
east_center = (station_locations['rel_east'].max()-
                np.abs(station_locations['rel_east'].min()))/2
north_center = (station_locations['rel_north'].max()-
                np.abs(station_locations['rel_north'].min()))/2

#remove the average distance to get coordinates in a relative space
station_locations['rel_east'] -= east_center
station_locations['rel_north'] -= north_center
        
#find the edges of the grid
west = station_locations['rel_east'].min()-cell_size_east/2
east = station_locations['rel_east'].max()+cell_size_east/2
south = station_locations['rel_north'].min()-cell_size_north/2
north = station_locations['rel_north'].max()+cell_size_north/2

#new_west = west*cos_ang+south*sin_ang
#new_east = east*cos_ang+north*sin_ang
#new_south = -west*sin_ang+south*cos_ang
#new_north = -east*sin_ang+north*cos_ang 

#west = np.round(new_west, -2)
#east= np.round(new_east, -2)
#south= np.round(new_south, -2)
#north = np.round(new_north, -2)
west = np.round(west, -2)
east= np.round(east, -2)
south= np.round(south, -2)
north = np.round(north, -2)

#-------make a grid around the stations from the parameters above------
#--> make grid in east-west direction
#cells within station area
east_gridr = np.arange(start=west, stop=east+cell_size_east,
                       step=cell_size_east)

#padding cells in the east-west direction
for ii in range(1, pad_east+1):
    east_0 = float(east_gridr[-1])
    west_0 = float(east_gridr[0])
    add_size = np.round(cell_size_east*pad_stretch_h*ii, -2)
    pad_w = west_0-add_size
    pad_e = east_0+add_size
    east_gridr = np.insert(east_gridr, 0, pad_w)
    east_gridr = np.append(east_gridr, pad_e)
    
    
#--> need to make sure none of the stations lie on the nodes
for s_east in sorted(station_locations['rel_east']):
    try:
        node_index = np.where(abs(s_east-east_gridr) < 
                             .02*cell_size_east)[0][0]
        if s_east-east_gridr[node_index] > 0:
            east_gridr[node_index] -= .02*cell_size_east
        elif s_east-east_gridr[node_index] < 0:
            east_gridr[node_index] += .02*cell_size_east
    except IndexError:
        continue
    

#--> make grid in north-south direction 
#N-S cells with in station area
north_gridr = np.arange(start=south, stop=north+cell_size_north, 
                        step=cell_size_north)

#padding cells in the east-west direction
for ii in range(1, pad_north+1):
    south_0 = float(north_gridr[0]) 
    north_0 = float(north_gridr[-1])
    add_size = np.round(cell_size_north*pad_stretch_h*ii, -2)
    pad_s = south_0-add_size
    pad_n = north_0+add_size
    north_gridr = np.insert(north_gridr, 0, pad_s)
    north_gridr = np.append(north_gridr, pad_n)
    
#--> need to make sure none of the stations lie on the nodes
for s_north in sorted(station_locations['rel_north']):
    try:
        node_index = np.where(abs(s_north-north_gridr) < 
                             .02*cell_size_north)[0][0]
        if s_north-north_gridr[node_index] > 0:
            north_gridr[node_index] -= .02*cell_size_north
        elif s_north-north_gridr[node_index] < 0:
            north_gridr[node_index] += .02*cell_size_north
    except IndexError:
        continue
    
##--> make depth grid
#log_z = np.logspace(np.log10(z1_layer), 
#                    np.log10(z_target_depth-np.logspace(np.log10(z1_layer), 
#                    np.log10(z_target_depth), 
#                    num=n_layers)[-2]), 
#                    num=n_layers-pad_z)
#z_nodes = np.array([zz-zz%10**np.floor(np.log10(zz)) for zz in 
#                   log_z])
##padding cells in the east-west direction
#for ii in range(1, pad_z+1):
#    z_0 = np.float(z_nodes[-2])
#    pad_d = np.round(z_0*pad_stretch_v*ii, -2)
#    z_nodes = np.append(z_nodes, pad_d)                  
#
##make an array of absolute values
#z_grid = np.array([z_nodes[:ii+1].sum() for ii in range(z_nodes.shape[0])])


#--> rotate the nodes to align with stations
#east_gridr = east_gridr*cos_ang+north_gridr.max()*sin_ang
#north_gridr = -east_gridr.min()*sin_ang+north_gridr*cos_ang

#---Need to make an array of the individual cell dimensions for
#   modem
east_nodes = east_gridr.copy().flatten()    
nx = east_gridr.shape[0]
east_nodes[:nx/2] = np.array([abs(east_gridr[ii]-east_gridr[ii+1]) 
                                  for ii in range(int(nx/2))])
east_nodes[nx/2:] = np.array([abs(east_gridr[ii]-east_gridr[ii+1]) 
                                  for ii in range(int(nx/2)-1, nx-1)])

north_nodes = north_gridr.copy().flatten()
ny = north_gridr.shape[0]
north_nodes[:ny/2] = np.array([abs(north_gridr[ii]-north_gridr[ii+1]) 
                               for ii in range(int(ny/2))])
north_nodes[ny/2:] = np.array([abs(north_gridr[ii]-north_gridr[ii+1]) 
                               for ii in range(int(ny/2)-1, ny-1)])
                        
#--put the grids into coordinates relative to the center of the grid
east_grid = east_nodes.copy()
east_grid[:int(nx/2)] = -np.array([east_nodes[ii:int(nx/2)].sum() 
                                   for ii in range(int(nx/2))])
east_grid[int(nx/2):] = np.array([east_nodes[int(nx/2):ii+1].sum() 
                                 for ii in range(int(nx/2), nx)])-\
                                 east_nodes[int(nx/2)]
                        
north_grid = north_nodes.copy()
north_grid[:int(ny/2)] = -np.array([north_nodes[ii:int(ny/2)].sum() 
                                    for ii in range(int(ny/2))])
north_grid[int(ny/2):] = np.array([north_nodes[int(ny/2):ii+1].sum() 
                                    for ii in range(int(ny/2),ny)])-\
                                    north_nodes[int(ny/2)]

#compute grid center
center_east = -east_nodes.__abs__().sum()/2
center_north = -north_nodes.__abs__().sum()/2
center_z = 0
grid_center = np.array([center_north, center_east, center_z])

#make nodes attributes
nodes_east = east_nodes
nodes_north = north_nodes
#nodes_z = z_nodes        
grid_east = east_grid
grid_north = north_grid
#grid_z = z_grid
    
#--> print out useful information                    
print '-'*15
print '   Number of stations = {0}'.format(len(station_locations))
print '   Dimensions: '
print '      e-w = {0}'.format(east_grid.shape[0])
print '      n-s = {0}'.format(north_grid.shape[0])
#print '       z  = {0} (without 7 air layers)'.format(z_grid.shape[0])
print '   Extensions: '
print '      e-w = {0:.1f} (m)'.format(east_nodes.__abs__().sum())
print '      n-s = {0:.1f} (m)'.format(north_nodes.__abs__().sum())
#print '      0-z = {0:.1f} (m)'.format(nodes_z.__abs__().sum())

print '  Mesh rotated by: {0:.1f} deg clockwise positive from N'.format(mesh_rotation_angle)
print '-'*15

#if _utm_cross is True:
#    print '{0} {1} {2}'.format('-'*25, 'NOTE', '-'*25)
#    print '   Survey crosses UTM zones, be sure that stations'
#    print '   are properly located, if they are not, adjust parameters'
#    print '   _utm_grid_size_east and _utm_grid_size_north.'
#    print '   these are in meters and represent the utm grid size'
#    print ' Example: '
#    print ' >>> modem_model._utm_grid_size_east = 644000'
#    print ' >>> modem_model.make_mesh()'
#    print ''
#    print '-'*56

#def plot_mesh(east_limits=None, north_limits=None, z_limits=None,
#              **kwargs):
#    """
#    
#    Arguments:
#    ----------
#        **east_limits** : tuple (xmin,xmax)
#                         plot min and max distances in meters for the 
#                         E-W direction.  If None, the east_limits
#                         will be set to furthest stations east and west.
#                         *default* is None
#                    
#        **north_limits** : tuple (ymin,ymax)
#                         plot min and max distances in meters for the 
#                         N-S direction.  If None, the north_limits
#                         will be set to furthest stations north and south.
#                         *default* is None
#                    
#        **z_limits** : tuple (zmin,zmax)
#                        plot min and max distances in meters for the 
#                        vertical direction.  If None, the z_limits is
#                        set to the number of layers.  Z is positive down
#                        *default* is None
#    """

kwargs={}    
fig_size = kwargs.pop('fig_size', [6, 6])
fig_dpi = kwargs.pop('fig_dpi', 300)
fig_num = kwargs.pop('fig_num', 3)

station_marker = kwargs.pop('station_marker', 'v')
marker_color = kwargs.pop('station_color', 'b')
marker_size = kwargs.pop('marker_size', 2)

line_color = kwargs.pop('line_color', 'k')
line_width = kwargs.pop('line_width', .5)

plt.rcParams['figure.subplot.hspace'] = .3
plt.rcParams['figure.subplot.wspace'] = .3
plt.rcParams['figure.subplot.left'] = .12
plt.rcParams['font.size'] = 7

fig = plt.figure(fig_num, figsize=fig_size, dpi=fig_dpi)
plt.clf()

#make a rotation matrix to rotate data
#cos_ang = np.cos(np.deg2rad(mesh_rotation_angle))
#sin_ang = np.sin(np.deg2rad(mesh_rotation_angle))
#neg_cos_ang = np.cos(np.deg2rad(-mesh_rotation_angle))
#neg_sin_ang = np.sin(np.deg2rad(-mesh_rotation_angle))
#
#neg_rot_matrix = np.array([[neg_cos_ang, neg_sin_ang], 
#                           [-neg_sin_ang, neg_cos_ang]])

cos_ang = 1
sin_ang = 0
#--->plot map view    
ax1 = fig.add_subplot(1, 1, 1, aspect='equal')


#plot station locations
#st_arr = np.array([station_locations['rel_east'], 
#                   station_locations['rel_north']])
#plot_east, plot_north = np.array(np.dot(neg_rot_matrix, st_arr))

plot_east = station_locations['rel_east']
plot_north = station_locations['rel_north']

#plot_east and plot_north come out as type matrix, need to change that
plot_east = np.array(plot_east)
plot_east = plot_east.flatten()
plot_north = np.array(plot_north)
plot_north = plot_north.flatten()

ax1.scatter(plot_east,
            plot_north, 
            marker=station_marker,
            c=marker_color,
            s=marker_size)
                        

east_line_xlist = []
east_line_ylist = []   
north_min = grid_north.min()         
north_max = grid_north.max()
        
for xx in grid_east:
    east_line_xlist.extend([xx*cos_ang+north_max*sin_ang, 
                            xx*cos_ang+north_min*sin_ang])
    east_line_xlist.append(None)
    east_line_ylist.extend([-xx*sin_ang+north_max*cos_ang, 
                            -xx*sin_ang+north_min*cos_ang])
    east_line_ylist.append(None)
ax1.plot(east_line_xlist,
              east_line_ylist,
              lw=line_width,
              color=line_color)

north_line_xlist = []
north_line_ylist = [] 
east_max = grid_east.max()
east_min = grid_east.min()
for yy in grid_north:
    north_line_xlist.extend([east_min*cos_ang+yy*sin_ang,
                             east_max*cos_ang+yy*sin_ang])
    north_line_xlist.append(None)
    north_line_ylist.extend([-east_min*sin_ang+yy*cos_ang, 
                             -east_max*sin_ang+yy*cos_ang])
    north_line_ylist.append(None)
ax1.plot(north_line_xlist,
              north_line_ylist,
              lw=line_width,
              color=line_color)


ax1.set_xlim(plot_east.min()-10*cell_size_east,
             plot_east.max()+10*cell_size_east)


ax1.set_ylim(plot_north.min()-10*cell_size_north,
             plot_north.max()+ 10*cell_size_east)

    
ax1.set_ylabel('Northing (m)', fontdict={'size':9,'weight':'bold'})
ax1.set_xlabel('Easting (m)', fontdict={'size':9,'weight':'bold'})

#plt.show()