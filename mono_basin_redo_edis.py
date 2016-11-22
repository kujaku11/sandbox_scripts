# -*- coding: utf-8 -*-
"""
Created on Thu Sep 25 14:27:36 2014

@author: jpeacock-pr
"""

import mtpy.usgs.zonge as zonge
import os
import mtpy.imaging.mtplot as mtplot
import mtpy.utils.configfile as mtconfig
import matplotlib.pyplot as plt

#station_info_fn = r"d:\Peacock\MTData\MB_June2013\June2013_Info.cfg"
#station_info_fn = r"d:\Peacock\MTData\MB_Sept2013\StationInfo_sept2013.cfg"
#station_info_fn = r"d:\Peacock\MTData\MB_Nov2013\StationInfo_Nov2013.cfg"
station_info_fn = r"d:\Peacock\MTData\MB_May2014\StationInfo_May2014.cfg"
#
station_dict = mtconfig.read_survey_configfile(station_info_fn)

#station_path = r"d:\Peacock\MTData\MB_Sept2013"
#station_path = r"d:\Peacock\MTData\MB_June2013"
#station_path = r"d:\Peacock\MTData\MB_Nov2013"
station_path = r"d:\Peacock\MTData\MB_May2014"


dp_ps_path = r"c:\Users\jpeacock-pr\Google Drive\Mono_Basin\EDI_Files"
 
station_list = sorted(station_dict.keys())

for station in station_list[40:]:
    station = station.lower()
    mtft_fn = os.path.join(station_path, station, 'Merged','mtft24.cfg')
    if os.path.isfile(mtft_fn) is True:
        svfn_ga = os.path.join(station_path, station, '{0}_ga.edi'.format(station))
        za = zonge.ZongeMTAvg()
        za.avg_dict = {'ex':'6', 'ey':'6'}
        edi_ga = za.write_edi(os.path.join(station_path, station, 'Merged'), 
                              station, 
                              survey_cfg_file=station_info_fn, 
                              mtft_cfg_file=mtft_fn,
                              save_path=svfn_ga,
                              copy_path=r"d:\Peacock\MTData\EDI_Files_ga", 
                              avg_ext='ga.avg')
                              
        svfn_dp = os.path.join(station_path, station, '{0}_dp.edi'.format(station))
        za = zonge.ZongeMTAvg()
        za.avg_dict = {'ex':'6', 'ey':'6'}
        edi_dp = za.write_edi(os.path.join(station_path, station, 'Merged'), 
                              station, 
                              survey_cfg_file=station_info_fn, 
                              mtft_cfg_file=mtft_fn,
                              save_path=svfn_dp,
                              copy_path=r"d:\Peacock\MTData\EDI_Files_dp", 
                              avg_ext='dp.avg')
                              
        svfn_ps = os.path.join(station_path, station, '{0}_ps.edi'.format(station))
        za = zonge.ZongeMTAvg()
        za.avg_dict = {'ex':'6', 'ey':'6'}
        edi_ps = za.write_edi(os.path.join(station_path, station, 'Merged'), 
                              station, 
                              survey_cfg_file=station_info_fn, 
                              mtft_cfg_file=mtft_fn,
                              save_path=svfn_ps,
                              copy_path=r"d:\Peacock\MTData\EDI_Files_ps", 
                              avg_ext='ps.avg')
        
        #add on the already phase smoothed and d+ edis if they exis
        edi_dp_ps = os.path.join(dp_ps_path, '{0}.edi'.format(station)) 
        if os.path.isfile(edi_dp_ps) is True:
            plot_edi_list = [edi_ga, edi_dp, edi_ps, edi_dp_ps] 
        
        else:
            plot_edi_list = [edi_ga, edi_dp, edi_ps]
        
        #--> plot the responses, sometimes craps out if there is no tipper, henc
        #    the try statement
        try:                      
            rpm = mtplot.plot_multiple_mt_responses(fn_list=plot_edi_list,
                                                    plot_style='compare',
                                                    plot_pt='y',
                                                    plot_tipper='yr')
        except IndexError:
            rpm = mtplot.plot_multiple_mt_responses(fn_list=plot_edi_list,
                                                    plot_style='compare',
                                                    plot_pt='y')                            
        rpm.fig.savefig(r"d:\Peacock\MTData\Response_plots\{0}.png".format(station),
                        fig_dpi=1200)
                        
        plt.close('all')
    else:
        print '==> Skipping {0}'.format(station)
            

