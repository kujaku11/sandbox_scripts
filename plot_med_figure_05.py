# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 18:18:06 2019

@author: jpeacock
"""
import glob
from mtpy.core import mt

edi_list = [fn for fn in 
            glob.glob(r"c:\Users\jpeacock\OneDrive - DOI\med_report\data\saudi_edi_geographic\*.edi")
            if fn[-7:-4] in ['101', '204', '517', '921', '120', '508']]



count = 1
#for edi_fn, rot in zip(sorted(edi_list[0:1]), [-120]):
for edi_fn, rot in zip(sorted(edi_list), [-120, 10, -120, 10, -30, -120]):
    m1 = mt.MT(edi_fn)
    
    print(' --> Rotating {0} by {1:.0f}'.format(m1.station, rot))
    
    p = m1.plot_mt_response(plot_pt='n')
    p.xy_color = (.75, 0, 0)
    p.yx_color = (0, 0, .75)
    
    p.Z.rotate(rot)
    p.Tipper.rotate(rot)
    
    p.phase_limits = (0, 89.9)
    
    p.redraw_plot()
    
    p.axr.set_ylabel('Apparent Resistivity ($\Omega$m)', 
                     fontdict={'size':10, 'weight':'normal'})
    p.axp.set_ylabel('Phase Angle', fontdict={'size':10, 'weight':'normal'})
    
    p.fig.suptitle(m1.station, fontsize=12, fontweight='bold')
    
    if 'y' in p.plot_tipper:
        p.axt.set_ylabel('Tipper', fontdict={'size':10, 'weight':'normal'})
        p.axt.set_xlabel('Period (s)', fontdict={'size':10,'weight':'normal'})
    else:
        p.axp.set_xlabel('Period (s)', fontdict={'size':10,'weight':'normal'})
        
    p.update_plot()
    p.save_plot(r"c:\Users\jpeacock\OneDrive - DOI\med_report\report\figures\figure_05_{0:02}.svg".format(count),
                fig_dpi=300)
    count += 1 