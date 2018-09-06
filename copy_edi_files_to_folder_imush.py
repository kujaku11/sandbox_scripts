# -*- coding: utf-8 -*-
"""
Created on Wed Sep 05 14:24:18 2018

@author: jpeacock
"""

import os
import shutil
import sciencebasepy as sb

archive_dir = r"g:\iMUSH\Archive"
edi_dir = r"g:\imush_edi"
png_dir = r"g:\imush_png"
page_id = '5ad77f06e4b0e2c2dd25e798'

session = sb.SbSession()
session.loginc('jpeacock@usgs.gov')
              
child_ids = session.get_child_ids(page_id)
c_dict = {}
for c_id in child_ids:
    c = session.get_item(c_id)
    c_dict[c['title']] = c_id

#for station in os.listdir(archive_dir):
for station in ['mshF010']:
    try:
        child_id = c_dict['station {0}'.format(station)]
        child_item = session.get_item(child_id)
        session.upload_file_to_item(child_item, 
                                    os.path.join(archive_dir,
                                                 station,
                                                 station+'.edi'))
#        session.upload_file_to_item(child_item, 
#                                    os.path.join(archive_dir,
#                                                 station,
#                                                 station+'.png'))
    except KeyError:
        print('No Child for {0}'.format(station))
#    edi_fn = os.path.join(edi_dir, fn)
#    archive_path = os.path.join(archive_dir, station)
#    if os.path.exists(archive_path):
#        shutil.copy(edi_fn, 
#                    os.path.join(archive_path, fn))
#        shutil.copy(os.path.join(png_dir, station+'.png'),
#                    os.path.join(archive_path, station+'.png'))
#    else:
#        print('Missing {0}'.format(station))
        
        