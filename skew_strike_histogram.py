# -*- coding: utf-8 -*-
"""
Created on Wed May 07 13:56:51 2014


plot skew angle and strike in a histogram

@author: jpeacock-pr
"""

#==============================================================================
# Imports
#==============================================================================
import mtpy.core.mt as mt
import matplotlib.pyplot as plt
import numpy as np
import mtpy.analysis.geometry as mt_geometry
from matplotlib.ticker import MultipleLocator
import os
import scipy.signal as sps

#==============================================================================
# 
#==============================================================================
edi_path = r"c:\Users\jpeacock\Google Drive\Mono_Basin\INV_EDI_FILES"

station_list = ['mb{0:03}'.format(ii) for ii in [178, 177, 220, 176, 222, 221, 
                175, 224, 225, 188, 235, 236, 237, 190, 226, 179, 180, 181, 
                231, 189, 237, 232, 191, 192, 182, 197, 198, 196, 199, 200, 
                203, 300, 301, 302, 303, 315, 316, 317, 318, 320, 305, 323, 
                326, 327, 328, 342, 306, 307, 308, 309, 311, 339, 168, 
                167, 162, 164, 165, 169, 170, 171, 172, 174, 173]]
pw_station_list = ['lv{0:02}'.format(ii) for ii in [22, 21, 20, 14, 15, 16, 
                   17, 18, 19, 4, 12, 3, 2, 13, 10, 9, 6, 7, 8, 24]] 
                   
edi_list = [os.path.join(edi_path, '{0}.edi'.format(ss)) for ss in 
            station_list+pw_station_list]
#edi_path = r"d:\Peacock\MTData\EDI_Files\GeographicNorth"
#edi_path = r"c:\Users\jpeacock\Google Drive\Mono_Basin\EDI_Files"
#edi_list = [os.path.join(edi_path, edi) for edi in os.listdir(edi_path)
#            if edi.find('.edi') > 0]
#                
#edi_path = r"c:\Users\jpeacock-pr\Google Drive\Antarctica\edi_files\geographic_north"
#
#station_list = ['S{0:02}'.format(ii) for ii in [1, 2, 4, 5, 7, 8, 9, 10, 12,
#                                                13, 14, 15, 16, 17, 18]]+\
#               ['L{0:02}'.format(ii) for ii in [1]]
#edi_list = [os.path.join(edi_path, '{0}.edi'.format(ss)) for ss in station_list]
#                
strike_color = (.5, .5, .5)
                
period_ranges = np.arange(-3, 4, 1)

bw = 5
histrange = (0, 360)

mt_list = [mt.MT(fn=edi) for edi in edi_list]

period_list = []
for mt_obj in mt_list:
    period_list.extend(1./mt_obj.Z.freq)
    
period_list = np.array(sorted(set(period_list), reverse=False))

num_period = period_list.shape[0]
num_station = len(mt_list) 

skew_arr = np.zeros((num_period, num_station))
skew_arr_3 = np.zeros((num_period, num_station))
strike_pt_arr = np.zeros((num_period, num_station))
strike_tip_arr = np.zeros((num_period, num_station))
strike_tip_arr_im = np.zeros((num_period, num_station))

ellip_arr = np.zeros((num_period, num_station))

period_dict = dict([(np.round(key, 5), value)
                     for value, key in enumerate(period_list)])


for st_index, mt_obj in enumerate(mt_list):
    #make a dictionary that coorelates with index values
    st_period_dict = dict([(np.round(key, 5), value)
                           for value, key in enumerate(1./mt_obj.Z.freq)])    
    
    #get dimensionality of mt response
    dim_2d = mt_geometry.dimensionality(z_object=mt_obj.Z, beta_threshold=3)
    
    st_ellip = mt_obj.pt.ellipticity[0]
    #get strike angle and skew from phase tensor
    st_strike = (90-mt_obj.pt.azimuth[0])%360
    st_skew = 2.*mt_obj.pt.beta[0]
    if mt_obj.Tipper.tipper is not None:
        st_tip_strike = (-mt_obj.Tipper.angle_real+180)%360
        st_tip_strike_im = (180-mt_obj.Tipper.angle_imag)%360
        
    else:
        st_tip_strike = np.zeros(mt_obj.Z.freq.shape[0])
        st_tip_strike_im = np.zeros(mt_obj.Z.freq.shape[0])
    
    #fill the arrays with data
    for st_key, strike, d_2d, strike_tip, strike_tip_im, ellip in zip(
                                                st_period_dict.keys(), 
                                                st_strike, dim_2d, 
                                                st_tip_strike,
                                                st_tip_strike_im,
                                                st_ellip):
        per_index = period_dict[st_key] 
 
       #fill strike array if the dimensionality is 2D
        if d_2d == 2:
            strike_pt_arr[per_index, st_index] = strike
            strike_tip_arr[per_index, st_index] = strike_tip
            strike_tip_arr_im[per_index, st_index] = strike_tip_im
        
        #fill skew angle array
        st_period_index = st_period_dict[st_key]
        if abs(st_skew[st_period_index]) >= 5.5: 
            skew_arr[per_index, st_index] = 1
        
        #fill skew angle array
        if abs(st_skew[st_period_index]) >= 3.5: 
            skew_arr_3[per_index, st_index] = 1
            
        #fill ellipticity array
        if st_ellip[st_period_index] > 0.1:
            ellip_arr[per_index, st_index] = 1

#get plotting skew as the count of number of stations with skew above 6    
plot_skew = skew_arr.sum(axis=1)
plot_skew = sps.medfilt(plot_skew, kernel_size=5)
plot_skew_3 = skew_arr_3.sum(axis=1)
plot_skew_3 = sps.medfilt(plot_skew_3, kernel_size=5)
plot_ellip = sps.medfilt(ellip_arr.sum(axis=1), kernel_size=5)
   
#==============================================================================
# plot
#==============================================================================
plt.rcParams['font.size'] = 10
plt.rcParams['figure.subplot.left'] = .12
plt.rcParams['figure.subplot.top'] = .98
plt.rcParams['figure.subplot.right'] = .97
plt.rcParams['figure.subplot.bottom'] = .12

fig = plt.figure(1, [4, 4], dpi=300)
plt.clf()
ax = fig.add_subplot(1,1,1)
ax.grid(True, color=(.75, .75, .75), alpha=.35)

#plot ellipticity
l2, = ax.semilogx(period_list, plot_ellip, color=(.5, .5, .5), lw=2)
ax.fill_between(period_list, 0, plot_ellip, facecolor=(.75, .75, .75))
#ax.set_ylabel('Strike (deg)', fontdict={'size':9, 'weight':'bold', 
#                                     'color':(.5, .5, .5)})
                                     
#l1, = ax.semilogx(period_list, plot_skew_3, color=(.5, .5, .5), lw=2)
#ax.fill_between(period_list, 0, plot_skew_3, facecolor=(.75, .75, .75))
l1, = ax.semilogx(period_list, plot_skew, color='k', lw=2)
ax.fill_between(period_list, 0, plot_skew, facecolor=(.5, .5, .5))
ax.set_xlabel('Period (s)', fontdict={'size':12, 'weight':'bold'})
ax.set_ylabel('Number of Stations', fontdict={'size':12, 'weight':'bold'})
ax.set_xlim(.001, 1000)
ax.set_ylim(0, 84.9)
ax.yaxis.set_major_locator(MultipleLocator(10))
ax.yaxis.set_ticklabels(['0', '0', '10', '20','30', '40', '50', '60', '', '' ])



ax.legend([l1, l2], ['$|\Psi|$ > 6', '$\epsilon$ > 0.1'],
           loc='lower right', prop={'size':12, 'weight':'bold'},
            borderaxespad=.1)
 #-----Plot Histograms of the strike angles-----------------------------
#plot specs
#plt.rcParams['figure.subplot.hspace'] = .3
#plt.rcParams['figure.subplot.wspace'] = .3
plot_period_ranges = period_ranges[0:-1]
pr = float(plot_period_ranges.shape[0])
sax = plt.rcParams['figure.subplot.right']-plt.rcParams['figure.subplot.left']
for jj, bb in enumerate(plot_period_ranges, 0):
    axpt = fig.add_axes(([.12+jj/pr*sax, .80, sax/pr, sax/pr]), polar=True)
    #axtp = fig.add_axes(([.1+jj/pr*sax, .79-sax/pr, sax/pr, sax/pr]), polar=True)


    #make a list of indicies for each decades    
    binlist=[]
    for ii,ff in enumerate(period_list):
        if ff >= 10**bb and ff <= 10**(bb+1):
            binlist.append(ii)
            
    #extract just the subset for each decade
    pt_sub = strike_pt_arr[binlist,:]
    tp_sub = strike_tip_arr[binlist,:]
    tp_sub_im = strike_tip_arr_im[binlist,:]
    
    tp_sub = np.append(tp_sub, tp_sub_im)
    tp_sub = np.append(tp_sub, pt_sub)
    
    #----------compute the historgram for the tipper strike
    trhist = np.histogram(tp_sub[np.nonzero(tp_sub)].flatten(),
                          bins=360/bw,
                          range=histrange)
    
    #make a bar graph with each bar being width of bw degrees                               
    bartr = axpt.bar((trhist[1][:-1])*np.pi/180,
                            trhist[0],
                            width=bw*np.pi/180)
    
    #set color of the bars according to the number in that bin
    #tipper goes from dark blue (low) to light blue (high)                        
    for cc,bar in enumerate(bartr):
        fc = float(trhist[0][cc])/trhist[0].max()*.75
        bar.set_facecolor((fc, fc, fc))
                
    
#    #------------estimate the histogram for the decade for invariants and pt
#    pthist = np.histogram(pt_sub[np.nonzero(pt_sub)].flatten(),
#                          bins=360/bw,
#                          range=histrange)
#    
#    #plot the histograms    
#    barpt = axpt.bar((pthist[1][:-1])*np.pi/180,
#                           pthist[0],
#                           width=bw*np.pi/180)
#    
#    #set the color of the bars according to the number in that bin
#    #pt goes from green (low) to orange (high)
#    for cc,bar in enumerate(barpt):
#        fc = float(pthist[0][cc])/pthist[0].max()
#        bar.set_facecolor((fc, fc, fc))
        
#    #-----------compute the historgram for the tipper strike imaginary
#    trhist_im = np.histogram(tp_sub_im[np.nonzero(tp_sub)].flatten(),
#                          bins=360/bw,
#                          range=histrange)
#    
#    #make a bar graph with each bar being width of bw degrees                               
#    bartr_im = axtp.bar((trhist_im[1][:-1])*np.pi/180,
#                            trhist_im[0],
#                            width=bw*np.pi/180)
#    
#    #set color of the bars according to the number in that bin
#    #tipper goes from dark blue (low) to light blue (high)                        
#    for cc,bar in enumerate(bartr_im):
#        fc = float(trhist_im[0][cc])/trhist_im[0].max()
#        bar.set_facecolor((fc, 0, 0))
                
        
    #make axis look correct with N to the top at 90.
    for aa, axh in enumerate([axpt]):
        axh.set_xlim(0,2*np.pi)
        #set multiple locator to be every 15 degrees
        #axh.xaxis.set_major_locator(MultipleLocator(30*np.pi/180))
        axh.set_thetagrids(np.arange(0, 360, 30), frac=1.2)
        #axh.set_rmax(180)
        #set labels on the correct axis
        axh.xaxis.set_ticklabels(['','','',
                                  'N','','',
                                  '','','',
                                  '','',''])
        #make a light grid
        axh.grid(alpha=.25)
        axh.yaxis.set_major_locator(MultipleLocator(60))
        #axh.set_ylim(0, 180)
        #axh.xaxis.labelpad = 50
        
        plt.setp(axh.yaxis.get_ticklabels(),visible=False)


plt.show()

    
    
    
