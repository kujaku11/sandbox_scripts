# -*- coding: utf-8 -*-
"""
Created on Thu May 28 12:36:55 2015

@author: jpeacock-pr
"""

import mtpy.usgs.zen as zen
from cStringIO import StringIO
import sys
import os

station_dir = r"d:\Peacock\MTData\Test\mb666" 

# this should capture all the print statements from zen
class Capturing(list):
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self
    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        sys.stdout = self._stdout
        
with Capturing() as output:
    z2edi = zen.Z3D_to_edi(station_dir)
    rp = z2edi.process_data(df_list=[256])
    
log_fid = open(os.path.join(station_dir, 'Processing.log'), 'w')
log_fid.write('\n'.join(output))
log_fid.close()