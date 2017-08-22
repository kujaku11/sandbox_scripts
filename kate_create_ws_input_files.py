# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 09:39:39 2017

@author: a1193899
"""

import mtpy.modeling.ws3dinv as ws
import os
import os.path as op
import numpy as np
edi_path = r"c:\Users\jrpeacock\Documents\kates_data"
edi_list = [op.join(edi_path,edi) for edi in os.listdir(edi_path)
            if edi.endswith('.edi')]
#edi_list = [os.path.join(edi_path, edi) for edi in edi_path if edi.find('.edi') > 0]
 # create an evenly space period list in log space
p_list = np.logspace(np.log10(.001), np.log10(1000), 12)

save_path=r'c:\Users\jrpeacock\Documents\kates_data\Inv_01'
#2) make a grid from the stations themselves with 200m cell spacing
wsmesh = ws.WSMesh(edi_list=edi_list,
                   cell_size_east=12500, 
                   cell_size_north=12500)
wsmesh.save_path=save_path
wsmesh.make_mesh()
# check to see if the mesh is what you think it should be
#wsmesh.plot_mesh()
# all is good write the mesh file 
wsmesh.res_list = np.logspace(-1, 3, 8)
wsmesh.write_initial_file(save_path=save_path)
 # note this will write a file with relative station locations
 #change the starting model to be different than a halfspace

mm = ws.WSModelManipulator(initial_fn=wsmesh.initial_fn)
 # an interactive gui will pop up to change the resistivity model
#once finished write a new initial file
mm.rewrite_initial_file()
#3) write data file
wsdata = ws.WSData(edi_list=edi_list, 
                   period_list=p_list, 
                   station_fn=wsmesh.station_fn)
wsdata.save_path=save_path
wsdata.write_data_file()

 #4) plot mt response to make sure everything looks ok
#rp = ws.PlotResponse(data_fn=wsdata.data_fn)
#5) make startup file
sws = ws.WSStartup(data_fn=wsdata.data_fn, initial_fn=mm.initial_fn)
sws.save_path=save_path
sws.error_tol=5
sws.write_startup_file()