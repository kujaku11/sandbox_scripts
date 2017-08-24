# -*- coding: utf-8 -*-
"""
Created on Fri Apr 14 14:47:48 2017

@author: jrpeacock
"""

from osgeo import ogr
from osgeo import osr

import osr

def utm_getZone(longitude):
    return (int(1+(longitude+180.0)/6.0))

def utm_isNorthern(latitude):
    if (latitude < 0.0):
        return 0;
    else:
        return 1;


   
lat = 38.0; lon  = -50.0
utm_zone = utm_getZone(lon); #print "utm_zone: "; print utm_zone
is_northern = utm_isNorthern(lat); #print "is_northern: "; print

   
## set utm coordinate system
utm_cs = osr.SpatialReference()
utm_cs.SetWellKnownGeogCS('WGS84')
utm_cs.SetUTM(utm_zone,is_northern);
   
## set wgs84 coordinate system
wgs84_cs = utm_cs.CloneGeogCS(); #print "\nwgs84_cs:"; print
wgs84_cs.ExportToPrettyWkt()
   
## set the transform wgs84_to_utm and do the transform
transform_WGS84_To_UTM = osr.CoordinateTransformation(wgs84_cs,utm_cs)
utm_points = list(transform_WGS84_To_UTM.TransformPoint(lon,lat));
print "utm_points: "; print utm_points
   
## set the transform utm_to_wgs84 and do the transform
transform_UTM_To_WGS84 = osr.CoordinateTransformation(utm_cs,wgs84_cs)
latlon_points = list(transform_UTM_To_WGS84.TransformPoint(utm_points[0],
                                                           utm_points[1]))
print "latlon_points: "; print latlon_points

#source = osr.SpatialReference()
#source.ImportFromEPSG(4326)
#
#target = osr.SpatialReference()
#target.ImportFromEPSG(3857)
#
#transform = osr.CoordinateTransformation(source, target)
#
#point = ogr.Geometry(ogr.wkbPoint)
##point.AddPoint(-118, 40.0)
##  
##point.Transform(transform)
##
##print point.ExportToWkt()