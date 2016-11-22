# -*- coding: utf-8 -*-
"""
Created on Mon Feb 23 10:26:13 2015

@author: jpeacock-pr
"""

import mtpy.core.mt as mt
import numpy as np
import scipy.interpolate as spi
import matplotlib.pyplot as plt
import mtpy.imaging.mtplot as mtplot

#edi_fn = r"c:\Users\jpeacock-pr\Google Drive\Antarctica\edi_files\S06E.edi"
edi_fn = r"c:\Users\jpeacock-pr\Google Drive\Mono_Basin\EDI_Files_dp\mb224_dp.edi"

mt_obj = mt.MT(edi_fn)

# we want to interpolate the impedance tensor so that different periods can be 
# estimated.  We can interpolate real and imaginary separate with a spline
# interpolation where x is period and y is impedance component
old_freq = mt_obj.Z.freq.copy()
new_freq = np.logspace(-2, 2, num=64)
#new_freq = mt_obj.Z.freq.copy()

new_z, new_tipper = mt_obj.interpolate(new_freq)
mt_obj.write_edi_file(new_fn='{0}_{1}.edi'.format(edi_fn[:-4], 'interp'),
                      new_Z=new_z, new_Tipper=new_tipper)

# test the new frequency range to be sure they can be interpolated
#if old_freq.min() > new_freq.min():
#    raise ValueError('New frequency minimum of {0:.5g}'.format(new_freq.min())+\
#                     ' is smaller than old frequency minimum of {0:.5g}'.format(old_freq.min())+\
#                     '.  The new frequency range needs to be within the '+\
#                     'bounds of the old one.')
#if old_freq.max() < new_freq.max():
#    raise ValueError('New frequency maximum of {0:.5g}'.format(new_freq.max())+\
#                     'is smaller than old frequency maximum of {0:.5g}'.format(old_freq.max())+\
#                     '.  The new frequency range needs to be within the '+\
#                     'bounds of the old one.')
#
#new_Z = mtz.Z(z_array=np.zeros((new_freq.shape[0], 2, 2), dtype='complex'),
#              zerr_array=np.zeros((new_freq.shape[0], 2, 2), freq=new_freq)



# interpolate each component of the impedance tensor and each real an imaginary
# part.  Also not going to do anything fancy with the error, just interpolate
# that as well.
#for ii in range(2):
#    for jj in range(2):
#        z_func_real = spi.interp1d(old_freq, mt_obj.Z.z[:, ii, jj].real,
#                                   kind='slinear')
#        z_func_imag = spi.interp1d(old_freq, mt_obj.Z.z[:, ii, jj].imag,
#                                   kind='slinear')
#        new_z[:, ii, jj] = z_func_real(new_freq)+1j*z_func_imag(new_freq)
#        
#        z_func_err = spi.interp1d(old_freq, mt_obj.Z.zerr[:, ii, jj],
#                                   kind='slinear')
#        new_z_err[:, ii, jj] = z_func_err(new_freq)
#        
#new_z_obj = mt.MTz.Z(z_array=new_z, zerr_array=new_z_err, freq=new_freq)
#mt_obj.write_edi_file(new_fn='{0}_{1}.edi'.format(mt_obj.fn[:-4], 'interp'),
#                      new_Z=new_z_obj)

#new_t = mt.MTz.Tipper(tipper_array=np.zeros((new_freq.shape[0], 1, 2), dtype='complex'),
#                      tippererr_array=np.zeros((new_freq.shape[0], 1, 2)),
#                      freq=new_freq)
#for jj in range(2):
#    t_func_real = spi.interp1d(old_freq, 
#                               mt_obj.Tipper.tipper[:, 0, jj].real,
#                               kind='slinear')
#    t_func_imag = spi.interp1d(old_freq, 
#                               mt_obj.Tipper.tipper[:, 0, jj].imag,
#                               kind='slinear')
#    new_t.tipper[:, 0, jj] = t_func_real(new_freq)+1j*t_func_imag(new_freq)
#    
#    t_func_err = spi.interp1d(old_freq, 
#                              mt_obj.Tipper.tippererr[:, 0, jj],
#                              kind='slinear')
#    new_t.tippererr[:, 0, jj] = t_func_err(new_freq)
##        
#new_z_obj = mt.MTz.Z(z_array=new_z, zerr_array=new_z_err, freq=new_freq)
#mt_obj.write_edi_file(new_fn='{0}_{1}.edi'.format(mt_obj.fn[:-4], 'interp'),
#                      new_Z=new_z_obj)
##rp_new = mtplot.plot_mt_response(fn='{0}_{1}.edi'.format(mt_obj.fn[:-4], 'interp'), 
##                                 plot_num=2, fig_num=2)
##rp_old = mtplot.plot_mt_response(fn=edi_fn, 
##                                 plot_num=2, fig_num=3)
compare_plot = mtplot.plot_multiple_mt_responses(fn_list=[edi_fn, 
                                                          '{0}_{1}.edi'.format(mt_obj.fn[:-4], 'interp')],
                                                 plot_style='compare', 
                                                 plot_tipper='yri')
#                                                   
#
#fig = plt.figure(1)
#fig.clf()
#ax1 = fig.add_subplot(1, 2, 1)
#ax2 = fig.add_subplot(1, 2, 2)
#
##l1, = ax1.loglog(1./mt_obj.Z.freq, mt_obj.Z.z[:, 0, 1].real, 'b', marker='*') 
##l2, = ax1.loglog(1./mt_obj.Z.freq, new_z[:, 0, 1].real, 'r', marker='v')
## 
##l1, = ax2.loglog(1./mt_obj.Z.freq, mt_obj.Z.z[:, 0, 1].imag, 'b', marker='*') 
##l2, = ax2.loglog(1./mt_obj.Z.freq, new_z[:, 0, 1].imag, 'r', marker='v') 
#l1, = ax1.loglog(1./mt_obj.Z.freq, mt_obj.Tipper.tipper[:, 0, 0].real, 
#                 'b', marker='*') 
#l2, = ax1.loglog(1./new_freq, new_t.tipper[:, 0, 0].real, 
#                 'r', marker='v')
#                 
#l1, = ax2.loglog(1./mt_obj.Z.freq, mt_obj.Tipper.tipper[:, 0, 1].imag, 
#                 'b', marker='*') 
#l2, = ax2.loglog(1./new_freq, new_t.tipper[:, 0, 1].imag, 
#                 'r', marker='v')
#
#line_list = [l1, l2]
#label_list = ['data', 'interp']
#
#for ax in [ax1,ax2]:
#    ax.legend(line_list, label_list)
#    ax.set_xlim(.01, 100)
#    ax.set_xlabel('Period')
#    ax.set_ylabel('Z_xy')
#
#
#plt.show()                                              
#                                                
                                