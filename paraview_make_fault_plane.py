"""
make a fault plane from a csv file of verticies, following the method of

J. Rugis


"""

import numpy as np


fn = r"c:\Users\jpeacock\Documents\Geothermal\Washington\MSH\MSH_NorthFault_nodes.csv"
output_fn = '{0}.ply'.format(fn[:-4])

# model center
east_0 = 555703.-253
north_0 = 5132626.0+26

# read in file into a numpy array
fault = np.loadtxt(fn,
                   delimiter=',',
                   skiprows=1,
                   dtype={'names': ('east', 'north', 'z'),
                          'formats': (np.float, np.float, np.float)})

#--> set some index values
nx = fault['east'].shape[0]
ny = fault['north'].shape[0]

# get the number of vertices to be calculated
nv = nx

# get the number of faces to be calculated
nf = 2*(nx-1)

#--> set the out put file
flines = []

#--> write some need lines
flines.append('ply\n')
flines.append('comment This is a comment!\n')
flines.append('format ascii 1.0\n')
flines.append('element vertex ' + str(nv) + '\n')
flines.append('property int x\n')
flines.append('property int y\n')
flines.append('property int z\n')
flines.append('element face ' + str(nf) + '\n')
flines.append('property list uchar int vertex_index\n')
flines.append('end_header\n')

# output vertices
for f_arr in fault:
    flines.append('{0:.0f} {1:.0f} {2:.2f}\n'.format((f_arr['north']-north_0)/1000.,
                                                     (f_arr['east']-east_0)/1000.,
                                                     -f_arr['z']/1000.))

#ouput faces
idown = jdown = True
for jj in range(ny - 1):
    for ii in range(nx - 1):
        m = ii + jj * nx
        if idown:
            flines.append('3 '+str(m)+' '+str(m+1+nx)+' '+str(m+nx)+ '\n')
            flines.append('3 '+str(m)+' '+str(m+1)+' '+str(m+1+nx)+ '\n')
        else:
            flines.append('3 '+str(m)+' '+str(m+1)+' '+str(m+nx)+ '\n')
            flines.append('3 '+str(m+1)+' '+str(m+nx+1)+' '+str(m+nx)+ '\n')
        idown = not idown
    idown = jdown = not jdown
  
with open(output_fn, 'w') as fid:
    fid.write(''.join(flines))

