# -*- coding: utf-8 -*-
"""
Created on Mon Sep 26 12:32:29 2016

@author: jpeacock
"""

import os
import shutil
import mtpy.usgs.zen_processing as zp
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

#==============================================================================
# local parameters
#==============================================================================
coil_calibration_path = r"/mnt/hgfs/MT/birrp_calibrations"
birrp_path = r"/home/peacock/Documents/birrp52/SourceCode/birrp52_big"
local_path = r"/mnt/hgfs/MT/MNP2019"
#copy_edi_path = os.path.join(local_path, 'EDI_Files_birrp')
station_df = pd.read_csv(r"/mnt/hgfs/MT/MNP2019/processing_combined.csv")

b_param_dict = {'ilev': 0,
                'c2threshb':.45,
                'c2threshe':.45,
                'c2thresh1':.45,
                'ainuin':.9999,
                'ainlin':.0000,
                'nar':9}

kwargs_dict = {'calibration_list':['2254', '2264', '2274', '2284', '2294',
                                '2304', '2314', '2324', '2334', '2344',
                                '2844', '2854', '3214'],
               '_max_nread':25000000}
#==============================================================================
# Station to process and remote reference
#==============================================================================
for row in station_df.itertuples():
    edi_list = []
    station = row.station
    local_station_path = os.path.join(local_path, station)
    rr_list = [None]+[[rr] for rr in [row.rr_station_01, row.rr_station_02,
                                    row.rr_station_03] if isinstance(rr, str)]
    c_list = []
    for rr in rr_list[1:]:
        c_list.append(rr[0])
    if len(c_list) > 1:
        rr_list.append(c_list)
    for rr_station in rr_list:
        with zp.Capturing() as output:
            if rr_station is not None:
                if isinstance(rr_station, list):
                    rr_local_station_path = []
                    for rr in rr_station:
                        rr_local_station_path.append(os.path.join(local_path, rr))
                else:
                    rr_local_station_path = os.path.join(local_path, rr_station)
                b_param_dict['ilev'] = 1
            else:
                rr_local_station_path = None
                b_param_dict['ilev'] = 0

            #==========================================================================
            # Process data
            #==========================================================================

            zp_obj = zp.Z3D2EDI(station_z3d_dir=local_station_path,
                                rr_station_z3d_dir=rr_local_station_path,
                                station_ts_dir=os.path.join(local_station_path, 'TS'))
            zp_obj.birrp_exe = birrp_path
            zp_obj.coil_cal_path = coil_calibration_path
            zp_obj.get_calibrations()
            try:
                plot_obj, comb_edi_fn = zp_obj.process_data(df_list=[4],
                                                            notch_dict={4:None},
                                                            max_blocks=4,
                                                            sr_dict={4096:(1000., 25),
                                                                     256:(24.999, .1),
                                                                     4:(.1, .00001)},
                                                            use_blocks_dict={4:[0]},
                                                            birrp_param_dict=b_param_dict,
                                                            plot=False,
                                                            **kwargs_dict)

                edi_list.append(comb_edi_fn)
                plt.close('all')
            except Exception as error:
                print('WARNING: Skipping {0}, rr = {1}'.format(station,
                                                                rr_station))
                print('Error: {0}'.format(error))

        if len(edi_list) > 0:
            try:
                rp = zp_obj.plot_responses(edi_list)
                rp.fig.savefig(Path(local_path).joinpath('{0}.png'.format(station)),
                           dpi=300)
                plt.close('all')
            except Exception as error:
                print('ERROR: could not plot {0}'.format(station))
        with open(os.path.join(local_path,
                               '{0}_processing.log'.format(station)), 'w') as log_fid:
            log_fid.write('\n'.join(output))

# cp_edi_fn = os.path.join(copy_edi_path, station+'.edi')
# shutil.copy(comb_edi_fn, cp_edi_fn)
# print('--> Copied {0} to {1}'.format(comb_edi_fn, cp_edi_fn))