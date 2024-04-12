#
# J. Rugis
# 03.10.12
#

# import tifffile as tif
from pathlib import Path
import rasterio

# --> set file name
# fname = r'c:\Users\jpeacock-pr\Documents\MonoBasin\Maps\MonoDEM\ASTER\MB_Crop.tif'
# fname = r'c:\Users\jpeacock-pr\Documents\MonoBasin\Maps\MonoDEM38w120\floatn38w120_13.tif'
# fname = r"c:\Users\jpeacock-pr\Documents\MonoBasin\Maps\MonoDEM\ASTER\MB_Crop_survey_area.tif"
# fname = r"c:\Users\jpeacock\Documents\MonoBasin\Maps\MonoDEM\ASTER\LV16_Crop_survey_area.tif"
# fname = Path(r"c:\Users\jpeacock\Downloads\exportImage.tif")
fname = Path(
    r"c:\Users\jpeacock\OneDrive - DOI\MonoBasin\MB_Crop_survey_area_dem.tif"
)
#
# line_name = 'profile4'
# fname = r"c:\Users\jpeacock-pr\Documents\MonoBasin\Maps\MonoDEM\ASTER\MB_map_{0}.tif".format(line_name)
# fname = r"c:\Users\jpeacock-pr\Google Drive\Antarctica\figures\antarctica_map_dem.tif"
# output_fn = r"c:\Users\jpeacock-pr\Google Drive\Antarctica\figures\antarctica_dem_overlay.ply"
# output_fn = r"c:\Users\jpeacock-pr\Documents\ParaviewFiles\mb_{0}.ply".format(line_name)
output_fn = fname.parent.joinpath(f"{fname.stem}.ply")

# read in file into a numpy array
# im = tif.imread(fname)
im = rasterio.open(fname, "r+")
elev = im.read()[0]

# print some statistics about the image array
# print
# print im.shape
# print im.min()
# print im.max()

# --> set some index values
# Xfirst = 0
# Xlast = im.shape[0] - 1
# Yfirst = 0
# Ylast = im.shape[1] - 1
# # Xfirst = 0
# # Xlast = 2500
# # Yfirst = 8900
# # Ylast = im.shape[1]-1

# compute the total number of samples in each direction
# need to add 1 because python goes from 0 to n-1
# nx = 1 + Xlast - Xfirst
# ny = 1 + Ylast - Yfirst

nx = im.height
ny = im.width

# get the number of vertices to be calculated
nv = nx * ny

# get the number of faces to be calculated
nf = 2 * (nx - 1) * (ny - 1)

# --> set the out put file
with open(output_fn, "w") as fout:
    lines = []
    # --> write some need lines
    lines.append("ply")
    lines.append("comment This is a comment!")
    lines.append("format ascii 1.0")
    lines.append(f"element vertex {nv}")
    lines.append("property int x")
    lines.append("property int y")
    lines.append("property int z")
    lines.append(f"element face {nf}")
    lines.append("property list uchar int vertex_index")
    lines.append("end_header")

    # output vertices
    for jj in range(ny):
        for ii in range(nx):
            lines.append(
                f"{29.6 * jj:.0f} {30.9 * (nx - 1 - ii):.0f} {elev[ii, jj]:.2f}"
            )

    # ouput faces
    idown = jdown = True
    for jj in range(ny - 1):
        for ii in range(nx - 1):
            m = ii + jj * nx
            if idown:
                lines.append(f"3 {str(m)} {str(m + 1 + nx)} {str(m + nx)}")
                lines.append(f"3 {str(m)} {str(m + 1)} {str(m + 1 + nx)}")
            else:
                lines.append(f"3 {str(m)} {str(m + 1)} {str(m + nx)}")
                lines.append(f"3 {str(m + 1)} {str(m + nx + 1)} {str(m + nx)}")
            idown = not idown

    fout.write("\n".join(lines))
