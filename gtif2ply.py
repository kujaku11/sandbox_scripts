#
# J. Rugis
# 03.10.12
#

import tifffile as tif

#--> set file name
#fname = r'c:\Users\jpeacock-pr\Documents\MonoBasin\Maps\MonoDEM\ASTER\MB_Crop.tif'
#fname = r'c:\Users\jpeacock-pr\Documents\MonoBasin\Maps\MonoDEM\n38w120\floatn38w120_13.tif'
#fname = r"c:\Users\jpeacock-pr\Documents\MonoBasin\Maps\MonoDEM\ASTER\MB_Crop_survey_area.tif"
fname = r"c:\Users\jpeacock\Documents\MonoBasin\Maps\MonoDEM\ASTER\LV16_Crop_survey_area.tif"
#
#line_name = 'profile4'
#fname = r"c:\Users\jpeacock-pr\Documents\MonoBasin\Maps\MonoDEM\ASTER\MB_map_{0}.tif".format(line_name)
#fname = r"c:\Users\jpeacock-pr\Google Drive\Antarctica\figures\antarctica_map_dem.tif"
#output_fn = r"c:\Users\jpeacock-pr\Google Drive\Antarctica\figures\antarctica_dem_overlay.ply"
#output_fn = r"c:\Users\jpeacock-pr\Documents\ParaviewFiles\mb_{0}.ply".format(line_name)
output_fn = r"c:\Users\jpeacock\Documents\LV\lv_3d_models\lv16_survey_area_dem.ply"

# read in file into a numpy array
im = tif.imread(fname)

# print some statistics about the image array 
#print
#print im.shape
#print im.min()
#print im.max()

#--> set some index values
Xfirst = 0
Xlast = im.shape[0]-1
Yfirst = 0
Ylast = im.shape[1]-1
#Xfirst = 0
#Xlast = 2500
#Yfirst = 8900
#Ylast = im.shape[1]-1

# compute the total number of samples in each direction
# need to add 1 because python goes from 0 to n-1
nx = 1 + Xlast - Xfirst
ny = 1 + Ylast - Yfirst

# get the number of vertices to be calculated
nv = nx * ny

# get the number of faces to be calculated
nf = 2 * (nx - 1) * (ny - 1)

#--> set the out put file
fout = open(output_fn, 'w')

#--> write some need lines
fout.write('ply\n')
fout.write('comment This is a comment!\n')
fout.write('format ascii 1.0\n')
fout.write('element vertex ' + str(nv) + '\n')
fout.write('property int x\n')
fout.write('property int y\n')
fout.write('property int z\n')
fout.write('element face ' + str(nf) + '\n')
fout.write('property list uchar int vertex_index\n')
fout.write('end_header\n')

# output vertices
for jj in range(ny): 
  for ii in range(nx):
    fout.write('{0:.0f} {1:.0f} {2:.2f} \n'.format(29.6*jj, 30.9*(nx-1-ii),
                                                   im[Xfirst+ii, Yfirst+jj]))

#ouput faces
idown = jdown = True
for jj in range(ny - 1):
  for ii in range(nx - 1):
    m = ii + jj * nx
    if idown:
      fout.write('3 '+str(m)+' '+str(m+1+nx)+' '+str(m+nx)+ '\n')
      fout.write('3 '+str(m)+' '+str(m+1)+' '+str(m+1+nx)+ '\n')
    else:
      fout.write('3 '+str(m)+' '+str(m+1)+' '+str(m+nx)+ '\n')
      fout.write('3 '+str(m+1)+' '+str(m+nx+1)+' '+str(m+nx)+ '\n')
    idown = not idown
  idown = jdown = not jdown
fout.close()

