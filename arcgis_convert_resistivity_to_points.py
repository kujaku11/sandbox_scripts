'''
compare resistivity from 3D depth slices with geology
'''

##Import modules, initial settings
import sys, string, os, time, csv, arcpy
import numpy as np


## Print start time
starttime = time.clock()
print("Starting  " + time.strftime("%I:%M:%S", time.localtime()))

## Toolboxes ect...
arcpy.gp.overwriteOutput = True
arcpy.CheckOutExtension("spatial")
arcpy.CheckOutExtension("GeoStats")

# User Inputs:
input_path = r'c:\Users\jpeacock\OneDrive - DOI\Geysers\depth_slices' # Folder with input data
output_path = r'c:\Users\jpeacock\Documents\ClearLake\GIS\resistivity' # Folder where outputs will be located
geology_shp = r'c:\Users\jpeacock\Documents\ClearLake\GIS\geology_units_slim.shp'

rastersToSample = sorted([fn for fn in os.listdir(input_path) if fn.endswith('.tif')])
sort_dict = {}
for fn in rastersToSample:
    find_01 = fn.find('_') + 1
    if fn.count('m') > 1:
        find_02 = fn.find('m', 4)
        find_01 += 1
        scale = -1
    else:
        find_02 = fn.find('m')
        scale = 1
    depth = int(fn[find_01:find_02]) * scale
    sort_dict[depth] = fn

raster_list = []
for key in sorted(sort_dict.keys()):
    raster_list.append(sort_dict[key])


'''
Setup
'''

studyAreaRasterName = raster_list[0] # Name of study area raster
samplingPointsName = 'resistivity_sampling.shp'# Name of Sampling Points File

# Set Geoprocessing environments: snap, extent, mask, cell size equal to study area raster
studyAreaRaster = os.path.join(input_path, studyAreaRasterName)
rastExtent = arcpy.sa.Raster(studyAreaRaster).extent
arcpy.env.extent = rastExtent
arcpy.env.snapRaster = studyAreaRaster
arcpy.env.mask = studyAreaRaster
pdCellSize = int(float(str(arcpy.GetRasterProperties_management(studyAreaRaster, "CELLSIZEX"))))
print('Cell Size = ' + str(pdCellSize))

'''
Geoprocessing
'''

# Create study area points from study area raster
studyAreaPoints = os.path.join(output_path, samplingPointsName)
arcpy.RasterToPoint_conversion(studyAreaRaster, studyAreaPoints, "Value")
arcpy.DeleteField_management(studyAreaPoints, "GRID_CODE")
arcpy.AddXY_management(studyAreaPoints)


# Sample rasters to point file
for rastLayer in raster_list[:]:
    StudyAreaPointsTemp = os.path.join(output_path, 'tempPts1.shp')
    evidenceRaster = os.path.join(input_path, rastLayer)
    arcpy.gp.ExtractValuesToPoints_sa(studyAreaPoints, evidenceRaster, StudyAreaPointsTemp, "NONE", "VALUE_ONLY")
    arcpy.AddField_management(StudyAreaPointsTemp, os.path.splitext(rastLayer)[0], "DOUBLE", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")
    arcpy.CalculateField_management(StudyAreaPointsTemp, os.path.splitext(rastLayer)[0], "!RASTERVALU!", "PYTHON", "")
    arcpy.DeleteField_management(StudyAreaPointsTemp, "RASTERVALU")
    arcpy.CopyFeatures_management(StudyAreaPointsTemp, studyAreaPoints, "", "0", "0", "0")
    arcpy.Delete_management(StudyAreaPointsTemp, "")


# Sample geology to point file
StudyAreaPointsTemp = os.path.join(output_path, 'tempPts2.shp')
arcpy.SpatialJoin_analysis(studyAreaPoints, geology_shp, StudyAreaPointsTemp, "#", "#")
arcpy.CopyFeatures_management(StudyAreaPointsTemp, studyAreaPoints, "", "0", "0", "0")
arcpy.Delete_management(StudyAreaPointsTemp, "")


'''
Finishing up, Clock
'''
stoptime = time.clock()
print "Done  " + time.strftime("%I:%M:%S", time.localtime())
elapsed = stoptime-starttime
print "Elapsed time in seconds "
print elapsed
