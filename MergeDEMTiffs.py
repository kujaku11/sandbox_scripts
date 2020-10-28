# -*- coding: utf-8 -*-
"""
Created on Fri May 03 11:41:18 2013

@author: jpeacock-pr
"""

import tifffile as tif
import matplotlib.pyplot as plt
import os
import numpy as np

# --> set path to .tif files
fnpath = r"c:\Users\jpeacock\Documents\MonoBasin\Maps\MonoDEM\ASTER"

# --> set a path to save file to
# svpath = r"c:\Users\jpeacock-pr\Documents\MonoBasin\Maps\MonoDEM\ASTER\MB_map_profile2.tif"
svpath = r"c:\Users\jpeacock\Documents\MonoBasin\Maps\MonoDEM\ASTER\LV16_Crop_survey_area.tif"

# --> set the files from upper left corner to lower right corner
fnlst = [
    os.path.join(fnpath, "ASTGTM2_" + ss + "_dem.tif")
    for ss in ["N38W120", "N38W119", "N37W120", "N37W119"]
]

# --> open the files individually
im1 = tif.imread(fnlst[0], 0)
im2 = tif.imread(fnlst[1], 0)
im3 = tif.imread(fnlst[2], 0)
im4 = tif.imread(fnlst[3], 0)

# ==============================================================================
#  For cropping input the pixel number for each plot
#  Note that the way the images are read in is with columns (x) is north
#  and rows (y) is east
# ==============================================================================
# --> Mono Basin
# profile 1
# xy1 = np.array([[3600, im1.shape[0]], [2900, im1.shape[1]]])
# xy2 = np.array([[3600, im2.shape[0]], [0, 1080]])
# xy3 = np.array([[0, 630], [2900, im3.shape[1]]])
# xy4 = np.array([[0, 630], [0, 1080]])
#
##profile 2
# xy1 = np.array([[3600, im1.shape[0]], [2900, im1.shape[1]]])
# xy2 = np.array([[3600, im2.shape[0]], [0, 1080]])
# xy3 = np.array([[0, 585], [2900, im3.shape[1]]])
# xy4 = np.array([[0, 585], [0, 1080]])

##profile 3
# xy1 = np.array([[3600, im1.shape[0]], [2900, im1.shape[1]]])
# xy2 = np.array([[3600, im2.shape[0]], [0, 1080]])
# xy3 = np.array([[0, 345], [2900, im3.shape[1]]])
# xy4 = np.array([[0, 345], [0, 1080]])

##profile 4
# xy1 = np.array([[3600, im1.shape[0]], [2900, im1.shape[1]]])
# xy2 = np.array([[3600, im2.shape[0]], [0, 1080]])
# xy3 = np.array([[0, 285], [2900, im3.shape[1]]])
# xy4 = np.array([[0, 285], [0, 1080]])

##--> Long Valley
# xy1 = np.array([[3600, im1.shape[0]], [3000, im1.shape[1]]])
# xy2 = np.array([[3600, im2.shape[0]], [0, 1400]])
# xy3 = np.array([[0, 1600], [3000, im3.shape[1]]])
# xy4 = np.array([[0, 1600], [0, 1400]])

###--> long valley modem model
# xy1 = np.array([[2000, im1.shape[0]], [2000, im1.shape[1]]])
# xy2 = np.array([[2000, im2.shape[0]], [0, 3000]])
# xy3 = np.array([[0, 3000], [2000, im3.shape[1]]])
# xy4 = np.array([[0, 3000], [0, 3000]])
#
# nx = (xy1[0,1]-xy1[0,0])+(xy3[0,1]-xy3[0,0])
# ny = (xy1[1,1]-xy1[1,0])+(xy2[1,1]-xy2[1,0])
#
##create an array to put the data into
# mtif = np.zeros((nx,ny))
#
## NW corner
# x1 = xy1[0,1]-xy1[0,0]
# y1 = xy1[1,1]-xy1[1,0]
# mtif[0:x1, 0:y1] = im1[xy1[0,0]:xy1[0,1], xy1[1,0]:xy1[1,1]]
#
## NE corner
# x2 = xy2[0,1]-xy2[0,0]
# y2 = xy2[1,1]-xy2[1,0]
# mtif[0:x2, y1:y1+y2] = im2[xy2[0,0]:xy2[0,1], xy2[1,0]:xy2[1,1]]
#
## SW corner
# x3 = xy3[0,1]-xy3[0,0]
# y3 = xy3[1,1]-xy3[1,0]
# mtif[x1:x1+x3, 0:y3] = im3[xy3[0,0]:xy3[0,1], xy3[1,0]:xy3[1,1]]
#
## SE corner
# x4 = xy4[0,1]-xy4[0,0]
# y4 = xy4[1,1]-xy4[1,0]
# mtif[x1:x1+x4, y3:y3+y4] = im4[xy4[0,0]:xy4[0,1], xy4[1,0]:xy4[1,1]]
#
# new_x, new_y = np.meshgrid(np.arange(0, mtif.shape[0], 8),
#                           np.arange(0, mtif.shape[1], 8), indexing='ij')
# mtif_resample = mtif[new_x, new_y]
##--> long valley 16 map
xy1 = np.array([[3600, im1.shape[0]], [3250, im1.shape[1]]])
xy2 = np.array([[3600, im2.shape[0]], [0, 1500]])
xy3 = np.array([[700, 1800], [3250, im3.shape[1]]])
xy4 = np.array([[700, 1800], [0, 1500]])

nx = (xy1[0, 1] - xy1[0, 0]) + (xy3[0, 1] - xy3[0, 0])
ny = (xy1[1, 1] - xy1[1, 0]) + (xy2[1, 1] - xy2[1, 0])

# create an array to put the data into
mtif = np.zeros((nx, ny))

# NW corner
x1 = xy1[0, 1] - xy1[0, 0]
y1 = xy1[1, 1] - xy1[1, 0]
mtif[0:x1, 0:y1] = im1[xy1[0, 0] : xy1[0, 1], xy1[1, 0] : xy1[1, 1]]

# NE corner
x2 = xy2[0, 1] - xy2[0, 0]
y2 = xy2[1, 1] - xy2[1, 0]
mtif[0:x2, y1 : y1 + y2] = im2[xy2[0, 0] : xy2[0, 1], xy2[1, 0] : xy2[1, 1]]

# SW corner
x3 = xy3[0, 1] - xy3[0, 0]
y3 = xy3[1, 1] - xy3[1, 0]
mtif[x1 : x1 + x3, 0:y3] = im3[xy3[0, 0] : xy3[0, 1], xy3[1, 0] : xy3[1, 1]]

# SE corner
x4 = xy4[0, 1] - xy4[0, 0]
y4 = xy4[1, 1] - xy4[1, 0]
mtif[x1 : x1 + x4, y3 : y3 + y4] = im4[xy4[0, 0] : xy4[0, 1], xy4[1, 0] : xy4[1, 1]]

new_x, new_y = np.meshgrid(
    np.arange(0, mtif.shape[0], 8), np.arange(0, mtif.shape[1], 8), indexing="ij"
)
mtif_resample = mtif[new_x, new_y]

## write ascii file
# asc_fid = file(r"c:\Users\jpeacock-pr\Documents\LV\Maps\dem_modem.asc", 'w')
# asc_fid.write('{0:<14}{1:<.0f}\n'.format('ncols', mtif_resample.shape[0]))
# asc_fid.write('{0:<14}{1:<.0f}\n'.format('nrows', mtif_resample.shape[1]))
# asc_fid.write('{0:<14}{1:<.10f}\n'.format('xllcorner', -119.44444444444))
# asc_fid.write('{0:<14}{1:<.10f}\n'.format('yllcorner', 37.1666666666))
# asc_fid.write('{0:<14}{1:<.10f}\n'.format('cellsize', .00222222222222222))
# asc_fid.write('{0:<14}{1:<.0f}\n'.format('NODATA_value', -9999))
#
# for ii in range(mtif_resample.shape[1]):
#    asc_fid.write(' '.join(['{0:.0f}'.format(ff)
#                            for ff in mtif_resample[:, -ii]])+'\n')
#
# asc_fid.close()
# ------------Save .tiff file----------------------------
tif.imsave(svpath, mtif)

print "Saved file to {0}".format(svpath)

fig = plt.figure(2)
fig.clf()
ax = fig.add_subplot(1, 1, 1, aspect="equal")
figim = ax.imshow(mtif_resample, cmap="gist_earth", vmin=1600, vmax=4000)
plt.colorbar(figim)
plt.show()


# fig2 = plt.figure(2)
# plt.clf()
# plt.rcParams['figure.subplot.hspace'] = 0.0
# plt.rcParams['figure.subplot.wspace'] = 0.0
#
# for ii,im in enumerate([im1,im2,im3,im4],1):
#    ax = fig2.add_subplot(2,2,ii,aspect='equal')
#    ax.imshow(im,vmin=64, vmax=4330)
#    ax.set_title('{0:}'.format(ii),fontdict={'size':12,'weight':'bold'})
#    if ii==1 or ii==2:
#        plt.setp(ax.xaxis.get_ticklabels(), visible=False)
#    if ii==2 or ii==4:
#        plt.setp(ax.yaxis.get_ticklabels(), visible=False)
# plt.show()
