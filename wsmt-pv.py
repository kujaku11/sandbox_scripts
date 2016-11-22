######################################################################
#
# Create vtk format file from WSMT output model file
#   - changes units from meters to kilometers
#
# 15.05.2012
# Institute of Earth Science and Engineering
# J Rugis
#
######################################################################
#

from evtk.hl import gridToVTK, pointsToVTK 
import numpy as np
import os

####################----INPUTS----#########################################

#directory path to where the model files are written to
dirpath=r"c:\MinGW32-xy\Peacock\wsinv3d\MB_AMT\Inv5"
#dirpath=r"/mnt/hgfs/peacock/wsinv3d/MB_AMT/TestLinearFault/Smooth"

#path to save the created files
savepath=r"c:\MinGW32-xy\Peacock\ParaviewFiles"
#savepath=r"/mnt/hgfs/peacock/wsinv3d/MB_AMT/ParaviewFiles"
#savepath=r"/mnt/hgfs/jp/Documents/ParaviewFiles/MB_AMT"

#name of inversion files
fn_str = 'MonoBasinAMT_rough'

#iteration number
ni = 5

#save string
fn_sv_str = 'Tester'

# WSMT output model file
WSMTmodel = os.path.join(dirpath,fn_str+'_model.{0:02}'.format(ni))

# WSMT initial response file
WSMTresp = os.path.join(dirpath,fn_str+'_resp.{0:02}'.format(ni))

# VTK file to create   
VTKresist = os.path.join(savepath,fn_sv_str+'_Iter{0:02}'.format(ni)+'_res')

 # VTK file to create            
VTKstations = os.path.join(savepath,fn_sv_str+'_Iter{0:02}'.format(ni)+'_sta')         
#####################################################################


f = open(WSMTmodel, 'r')

# skip first line in file 
f.readline()

# read x,y,z mesh dimensions
dims = []
list = f.readline().split()
for n in range(3):
  dims.append(int(list[n]))
size = dims[0]*dims[1]*dims[2]
print 'Mesh     ', dims
print 'Data     ', size

# read x,y,z spacing
#  (depends on line break only after final value)
spacing = []
for n in range(3):
  i=0
  while i < dims[n]:
    list = f.readline().split()
    for j in range(len(list)):
      spacing.append(float(list[j])/1000.0) 
      i += 1

# read mt data
#  (depends on line break only after final value)
mt = np.zeros(size)
i=0
while i < size:
  list = f.readline().split()
  for j in range(len(list)):
    mt[i] = float(list[j])
    i += 1

# calc x coordinates of vtk mesh
xdist = 0 # calculate total x distance
for i in range(dims[0]):
  xdist += spacing[i]
x = np.zeros(dims[0]+1)
x[0] = -0.5 * xdist # zero center of model
for i in range(dims[0]):
  x[i+1] = x[i] + spacing[i]

# calc y coordinates of vtk mesh
ydist = 0 # calculate total y distance
for i in range(dims[1]):
  ydist += spacing[dims[0] + i]
y = np.zeros(dims[1]+1)
y[0] = -0.5 * ydist # zero center of model
for i in range(dims[1]):
  y[i+1] = y[i] + spacing[dims[0] + i]

# calc z coordinates of vtk mesh
z = np.zeros(dims[2]+1)
z[0] = 0.0
for i in range(dims[2]):
  z[i+1] = z[i] + spacing[dims[0] + dims[1] + i]

# output to vtk format
mtNS = np.zeros((dims[0],dims[1],dims[2])) # North-to-South conversion
n=0
for k in range(dims[2]):
  for j in range(dims[1]):
    for i in range(dims[0]):
      mtNS[(dims[0]-1)-i,j,k] = mt[n]
      n += 1
gridToVTK(VTKresist, x, y, z, cellData = {'resistivity' : mtNS})

f.close()

f = open(WSMTresp, 'r')

# get station count
list = f.readline().split()
nstations = int(list[0])
print 'Stations ', nstations

# read x locations
f.readline() #skip line
x = np.zeros(nstations)
i=0
while i < nstations:
  list = f.readline().split()
  for j in range(len(list)):
    x[i] = float(list[j])/1000.0
    i += 1

# read y locations
f.readline() #skip line
y = np.zeros(nstations)
i=0
while i < nstations:
  list = f.readline().split()
  for j in range(len(list)):
    y[i] = float(list[j])/1000.0
    i += 1

# set z locations
z = np.zeros(nstations)

# output to vtk format
dummy = np.zeros(nstations)
for j in range(nstations):
  dummy[j] = 1.0
pointsToVTK(VTKstations, x, y, z, data = {"value" : dummy})

f.close()


print 'Created Resistivity File: ',VTKresist
print 'Created Station File: ',VTKstations

