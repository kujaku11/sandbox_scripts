# -*- coding: utf-8 -*-
"""
Created on Thu Apr 30 11:46:41 2015

@author: jpeacock-pr
"""

import osgeo.ogr as ogr
import os
import numpy as np

shp_fn = r"c:\Users\jpeacock-pr\Documents\LV\Maps\MT_stations_2015.shp"

def read_shape_file(shape_fn):
    """
    read shape file
    
    Returns
    -------------
        *points_arr* : array of points
        
        *proj* : projection of the points
    """
    if os.path.isfile(shape_fn) is False:
        return "Could not find {0}, check path".format(shape_fn)
    
    # Open shape file
    shape_data = ogr.Open(shape_fn)

    # Get the first layer
    layer = shape_data.GetLayer()
    # Initialize
    points = []
    # For each point,
    for index in xrange(layer.GetFeatureCount()):
        # Get
        feature = layer.GetFeature(index)
        geometry = feature.GetGeometryRef()
        # Make sure that it is a point
        if geometry.GetGeometryType() != ogr.wkbPoint: 
            raise IOError('This module can only load points')
        # Get pointCoordinates
        point_xy = geometry.GetX(), geometry.GetY()
        # Append
        points.append(point_xy)
        # Cleanup
        feature.Destroy()
    # Get spatial reference as proj4
    proj4 = layer.GetSpatialRef().ExportToProj4()
    # Cleanup
    shape_data.Destroy()
    
    points = np.array(points, dtype=[('east', np.float), ('north', np.float)])
   
    # Return
    return points, proj4
    
def convert_to_kml(shape_fn, kml_fn=None, station_stem='MT'):
    """
    convert a shape file to kml 
    """
    
    if kml_fn is None:
        kml_fn = '{0}.kml'.format(shape_fn[:-4])
        
    utm_points, proj = read_shape_file(shape_fn)

    kml_lines = []
    kml_lines.append('<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n')
    kml_lines.append('<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n')
    kml_lines.append('<Document>\n')    
    
    for ii, utm_point in enumerate(utm_points):
        kml_lines.append('{0}<Placemark>\n'.format(' '*2))
        kml_lines.append('{0}<name>{1}</name>\n'.format(' '*4,
                         '{0}{1:02}'.format(station_stem, ii)))
#        kml_lines.append('{0}<description>\n'.format(' '*4))
#        kml_lines.append('{0}<p>{1}</p>\n'.format(' '*8, 'MT station'))
#        kml_lines.append('{0}</description>\n'.format(' '*4))
        kml_lines.append('{0}<Point>\n'.format(' '*4))
        kml_lines.append('{0}<coordinates>{1:.4f},{2:.4f},{3:.4f}</coordinates>\n'.format(
                         ' '*6, utm_point['east'], utm_point['north'], 0))
        kml_lines.append('{0}</Point>\n'.format(' '*4))
        kml_lines.append('{0}</Placemark>\n'.format(' '*2))
     
    kml_lines.append('</Document>\n')
    kml_lines.append('</kml>\n')
    
    kml_fid = file(kml_fn, 'w')
    kml_fid.writelines(kml_lines)
    kml_fid.close()
    print 'Wrote kml file to: {0}'.format(kml_fn)
    
def convert_to_txt(shape_fn, txt_fn=None, station_stem='MT'):
    """
    convert shape file to text file
    """
    
    if txt_fn is None:
        txt_fn = '{0}.txt'.format(shape_fn[:-4])
        
    utm_points, proj = read_shape_file(shape_fn)
    
    txt_lines = []
    txt_lines.append('{0},{1},{2}\n'.format('station', 'lon', 'lat'))
    for ii, utm_point in enumerate(utm_points):
        station = '{0}{1:02}'.format(station_stem, ii)
        txt_lines.append('{0},{1:.4f},{2:.4f}\n'.format(station, 
                         utm_point['east'], utm_point['north']))
    
    txt_fid = file(txt_fn, 'w')
    txt_fid.writelines(txt_lines)
    txt_fid.close()
    print 'Wrote txt file to: {0}'.format(txt_fn)
#==============================================================================
# do the work
#==============================================================================
convert_to_kml(shp_fn)
convert_to_txt(shp_fn)
      