# -*- coding: utf-8 -*-
"""
Created on Thu Mar 20 13:12:40 2014

@author: jpeacock-pr
"""

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np


def arrhenius(temperature, wtp_h2o, pressure=1):
    """
    melt resistivity of rhyolite from Gaillard [2004]
    
    """
    R = 8.314 #units are kJ/mol/K
    sigma_0 = -78.9*np.log(wtp_h2o)+754
    Ea =  -2925*np.log(wtp_h2o)+64132
    
    return sigma_0*np.exp(-(Ea+2*pressure)/(R*temperature))
    
def dacite_arrhenius(temperature, wtp_h2o, pressure=1):
    """
    melt resistivity of dacite from Laumonier 2014
    """
    
    a1 = -0.064
    a2 = 5.96
    a3 = 1.06e-5
    a4 = 2.49e-5
    a5 = -6146.
    a6 = 88440.
    a7 = 0.176
    a8 = 0.388    
    
    R = 8.314 #units are kJ/mol/K
    sigma_0 = np.exp((a1*wtp_h2o+a2)*pressure+a3*wtp_h2o+a4)
    Ea = a5*wtp_h2o+a6
    delta_v = a7*wtp_h2o+a8
    
    return sigma_0*np.exp(-(Ea+pressure*delta_v)/(R*temperature))
    
def basalt_arrhenius(temperature, wtp_k2o):
    """
    electrical resistivity from Gaillard [2005]
    
    """

    a1 = 0.742
    a2 = -0.105
    b1 = 4.742
    b2 = -0.60
    
    a = a1+a2*wtp_k2o
    b = b1+b2*wtp_k2o
    
    return np.exp(a+b/temperature)
    
def nernst_einstein(mobility, charge, concentration, temperature, haven):
    """
    nernst-einstein equation for electrical conductivity of melt
    """
    k = 1.3806e-23
    sigma_melt = mobility*charge**2*concentration/(k*temperature*haven)
    
    return sigma_melt
    
def modified_brick(sigma_1, sigma_2, percent_2):
    """
    modified brick mising model
    
    sigma_1 is the resistivity of the host material
    sigma_2 is the resistivity of the filling material
    percent_2 is the percentage of the filling material
    """
    
    s1 = sigma_1
    s2 = sigma_2
    p1 = percent_2    
    n = 2./3
    
    sigma_eff = s2*(s2*(p1**n-1)-s1*p1**n)/s1*(p1-p1**n)-s2*(p1**n-p1-1)
    
    sigma_eff = np.nan_to_num(sigma_eff)
    
    return sigma_eff
    
def modified_archies(sigma_1, sigma_2, percent_2, m=1.05):
    """
    modified archies law
    
    sigma_1 is the resistivity of the host material
    sigma_2 is the resistivity of the filling material
    percent_2 is the percentage of the filling material
    """
    s1 = sigma_1
    s2 = sigma_2
    p2 = 1-percent_2
    
    p = np.log(1-p2**m)/np.log(1-p2)
    
    sigma_eff = s1*(1-p2)**p+s2*p2**m
    
    return sigma_eff
    
def hs_lower(sigma_1, sigma_2, percent_2):
    """
    hashin-shtrickman lower bound
    
    sigma_1 is the resistivity of the host material
    sigma_2 is the resistivity of the filling material
    percent_2 is the percentage of the filling material
    """
    
    s1 = sigma_1
    s2 = sigma_2
    p2 = 1-percent_2
    
    sigma_eff = s1*(1+(3*p2*(s2-s1))/(3*s1+(1-p2)*(s2-s1)))
    
    return sigma_eff
    
def viscosity(T, ob, h2o, sigma):
    """
    estimate viscosity from resistivity
    """
    
    log_nu = 41.09-1.5e5/T+2.48*h2o+139.4*ob-31.25*np.log(sigma)
    nu = np.exp(log_nu)    
    
    return nu
    
def calculate_ob(concentration_dict):
    """
    calculate optical bacisity using the formulation from Zhang [2010]
    and parameters from Duffy and Ingram [1975], following Pommier, [2013]
    
    concentration_dict must have keys:
        - ['Al', 'Ca', 'Fe', 'H', 'K', 'Mg', 'Mn', 'Na', 'Si']
        
    values are percent concentrations for each oxide
    
    """
    # dictionary of lambda ob values from Duffy
    lob= {'K':1.4, 'Na':1.15, 'Mg':0.78, 'Mn':1.0, 'Fe':1.0, 'Si':0.48, 
          'Al':0.6, 'Ca':1.0, 'H':0.47}
               
    xd = dict(concentration_dict)
    
    if xd['Ca']+xd['Mg'] >= xd['Al']:
        A = 2*lob['Si']*xd['Si']+3*lob['Al']*xd['Al']+lob['Fe']*xd['Fe']+\
            lob['Mn']*xd['Mn']+lob['Mg']*(xd['Mg']+xd['Ca']-xd['Al'])+\
            .5*lob['Na']*xd['Na']+ .5*lob['K']*xd['K']+lob['H']*xd['H']
            
        B = 2**xd['Si']+3*xd['Al']+xd['Fe']+xd['Mn']+\
            (xd['Mg']+xd['Ca']-xd['Al'])+.5*xd['Na']+.5*xd['K']+xd['H']
            
    elif xd['Ca']+xd['Mg'] < xd['Al']:
        A = 2*lob['Si']*xd['Si']+3*lob['Al']*xd['Al']+lob['Fe']*xd['Fe']+\
            lob['Mn']*xd['Mn']+lob['Mg']*xd['Mg']+lob['Ca']*xd['Ca']+\
            .5*lob['Na']*xd['Na']+ .5*lob['K']*xd['K']+lob['H']*xd['H']
            
        B = 2**xd['Si']+3*xd['Al']+xd['Fe']+xd['Mn']+xd['Mg']+xd['Ca']+\
            .5*xd['Na']+.5*xd['K']+xd['H']
            
    return A/B
               
    
#==============================================================================
# input values
#==============================================================================
T = np.arange(725, 1100, step=20)+273.5           # temperature array
T_r = 825.+273.5                          # rhyolite temperature
T_d = 900.+273.5                          # dacite temperature


melt_percent = np.arange(0, 51, 5)/100.   # melt percent array

sigma_regional = 1./100

ob_rhyolite_dict = {'K':.047, 'Na':.038, 'Mg':.0001, 'Mn':.0006, 'Fe':.012, 
                    'Si':0.75, 'Al':0.123, 'Ca':.005, 'H':0.03}
ob_dacite_dict = {'K':.04, 'Na':.04, 'Mg':.0007, 'Mn':.01, 'Fe':.023, 
                    'Si':0.63, 'Al':0.16, 'Ca':.03, 'H':0.03}

ob_rhyolite = 1-calculate_ob(ob_rhyolite_dict)
ob_dacite = 1-calculate_ob(ob_dacite_dict)

wtp_h2o_min = 1.0
wtp_h2o_max = 5.0



#==============================================================================
# plot
#==============================================================================
plt.close('all')
plt.rcParams['font.size'] = 7
plt.rcParams['figure.subplot.hspace'] = .3
plt.rcParams['figure.subplot.top'] = .9
plt.rcParams['figure.subplot.bottom'] = .1
plt.rcParams['figure.subplot.left'] = .16
plt.rcParams['figure.subplot.right'] = .97
plt.rcParams['grid.linewidth'] = .15
plt.rcParams['grid.color'] = (.5, .5, .5)

label_font_dict = {'size':8, 'weight':'bold'}
ylabel_coords = (-.135, .5)
xlabel_coords = (.5, -.125)

fig = plt.figure(1, figsize=[3, 4], dpi=300)
ax = fig.add_subplot(2, 1, 1)
#ax2 = fig.add_subplot(3, 1, 2)
ax3 = fig.add_subplot(2, 1, 2)

plt.cla()
line_list = []
label_list = []

line_list2 = []
label_list2 = []

line_list3 = []
label_list3 = []

line_list_mp = []
label_list_mp = []

for wtp_h2o in np.arange(wtp_h2o_min, wtp_h2o_max+1, 1.0):
    if wtp_h2o == 0:
        wtp_h2o = .01
        
    #--> plot resistivity vs. temperature
    line_color = tuple(3*[.9-.9*wtp_h2o/(wtp_h2o_max)])
    sigma_a = arrhenius(T, wtp_h2o, pressure=.5)
    line_rhyolite, = ax.plot(1./sigma_a, T-273.5,
                      '-',
                      marker='s',
                      ms=2, 
                      lw=.5, 
                      color=line_color, 
                      mfc=line_color,
                      mec=line_color)
                      
    sigma_d = dacite_arrhenius(T, wtp_h2o, pressure=1.2)
#    line_color_d = (.75-wtp_h2o/wtp_h2o_max, 
#                    1, 
#                    .75-wtp_h2o/wtp_h2o_max)
    line_dacite, = ax.plot(1./sigma_d, T-273.5,
                      '-.',
                      marker='o',
                      ms=2, 
                      lw=.5, 
                      color=line_color,
                      mfc=line_color,
                      mec=line_color)
    line_dacite.set_dashes((3,1))
    
#    #--> plot viscosity vs melt resistivity                        
#    sigma_a = arrhenius(T, wtp_h2o)
#    # plot rhyolite
#    nu_rhyolite = viscosity(T_r, ob_rhyolite, wtp_h2o, sigma_a)
#    line_nu_rhyolite, = ax2.semilogy(1./sigma_a, nu_rhyolite,
#                         '-', 
#                         lw=.5, 
#                         marker='s',
#                         ms=2,
#                         mec=line_color,
#                         color=line_color)
#    
#    # plot dacite 
#    sigma_a = dacite_arrhenius(T, wtp_h2o)                
#    nu_dacite = viscosity(T_d, ob_dacite, wtp_h2o, sigma_a)
#    line_nu_dacite, = ax2.semilogy(1./sigma_a, nu_dacite,
#                     '-.', 
#                     lw=.5, 
#                     marker='o',
#                     ms=2,
#                     mec=line_color,
#                     color=line_color)
#    line_nu_dacite.set_dashes((3, 1))
    if wtp_h2o == wtp_h2o_max:
        #--> line list for viscosity
#        line_list3.append(line_nu_rhyolite)
#        label_list3.append('rhyolite')
#        line_list3.append(line_nu_dacite)
#        label_list3.append('dacite')
        
        #--> line list for melt resistivity vs. temperature
        line_list2.append(line_rhyolite)
        label_list2.append('rhyolite')
        line_list2.append(line_dacite)
        label_list2.append('dacite')
#                     

    line_list.append(line_rhyolite)
    label_list.append(' {0:.0f}% $H_2O$'.format(wtp_h2o))
#    line_list.append(l2)
#    label_list.append('$H_2O$ {0:.1f}%'.format(wtp_h2o))
    
     #--> plot melt percentage vs. bulk resistivity
    sigma_melt = arrhenius(T_r, wtp_h2o)
    sigma_ma_low = modified_archies(sigma_regional, sigma_melt, 1-melt_percent)
    sigma_ma_low[0] = sigma_regional
                 
    line_melt_percent, = ax3.semilogx(1./sigma_ma_low, melt_percent,
                       '-',
                       lw=.5,
                       marker='s',
                       ms=1.5,
                       mec=line_color,
                       color=line_color)
                       
    sigma_melt = dacite_arrhenius(T_d, wtp_h2o)
    sigma_ma_low = modified_archies(sigma_regional, sigma_melt, 1-melt_percent)
    sigma_ma_low[0] = sigma_regional
                 
    line_melt_percent_dacite, = ax3.semilogx(1./sigma_ma_low, melt_percent,
                       '-.',
                       lw=.5,
                       marker='o',
                       ms=1.5,
                       mec=line_color,
                       color=line_color)
    line_melt_percent_dacite.set_dashes((3, 1))


#make a legend on top of the figure for water percent
fig.legend(line_list, label_list, 
           loc='upper center',
           prop={'size':6},
           ncol=5,
           markerscale=.5,
           handletextpad=.05,
           columnspacing=.05)
           
#--> resitivity vs temperature 
ax.fill_between([0, 12], [750, 750], [850, 850], 
                color=(.75, .75, .75), 
                alpha=.35)   
ax.set_ylabel('Temperature ($^\circ$C)', 
               fontdict=label_font_dict)
ax.set_xlabel('Melt Resistivity ($\Omega \cdot$m)', 
               fontdict=label_font_dict)
ax.legend(line_list2, label_list2, loc='upper right', prop={'size':6},
          ncol=1)
ax.xaxis.set_minor_locator(MultipleLocator(.25))
ax.xaxis.set_major_locator(MultipleLocator(1))
ax.grid(which='major')
ax.set_xlim(0, 11.5)

#--> resistivity vs. viscosity

#ax2.fill_between([1.4, 2.2], [10**0, 10**0], [10**10, 10**10], 
#                color=(.75, .75, .75), 
#                alpha=.35)
#                
#ax2.set_ylim(10**2, 10**8)
#ax2.set_xlim(0, 10)
#ax2.set_ylabel('Viscosity (Pa$\cdot$m)', 
#               fontdict=label_font_dict)
#ax2.set_xlabel('Melt Resistivity ($\Omega \cdot$m)', 
#               fontdict=label_font_dict)
##ax2.xaxis.set_minor_locator(MultipleLocator(.1))
#ax2.grid(which='major', color=(.85, .85, .85))
#ax2.legend(line_list3, label_list3, loc='upper right', prop={'size':6},
#          ncol=1)
          

#--> resistivity vs. melt percent
ax3.fill_between([5, 15], [0, 0], [.5, .5], 
                color=(.75, .75, .75), 
                alpha=.35)
                
ax3.set_ylabel('Melt Percent', 
               fontdict=label_font_dict)
ax3.set_xlabel('Bulk Resistivity ($\Omega \cdot$m)', 
               fontdict=label_font_dict)
ax3.set_ylim(0, 1)
ax3.set_xlim(0, 1/sigma_regional)
ax3.yaxis.set_minor_locator(MultipleLocator(.05))
ax3.yaxis.grid(which='both')
ax3.xaxis.grid(which='both')
ax3.legend(line_list2, label_list2, loc='upper right', prop={'size':6},
          ncol=1)

#ax3.legend(line_list3, label_list3, loc='upper right', prop={'size':6},
#          ncol=1)

ax.text(.23, 715, 'a',
        fontdict=label_font_dict,
        horizontalalignment='left',
        verticalalignment='bottom',
        bbox={'facecolor':'w', 'alpha':1})

#ax2.text(1.225, 10**2+100, 'b',
#        fontdict=label_font_dict,
#        horizontalalignment='left',
#        verticalalignment='bottom',
#        bbox={'facecolor':'w', 'alpha':1})

ax3.text(2.2, .02, 'b',
        fontdict=label_font_dict,
        horizontalalignment='left',
        verticalalignment='bottom',
        bbox={'facecolor':'w', 'alpha':1})

#set grid lines behind all objects
for xx in [ax, ax3]:
    xx.yaxis.set_label_coords(ylabel_coords[0], ylabel_coords[1])
    xx.xaxis.set_label_coords(xlabel_coords[0], xlabel_coords[1])
    [line.set_zorder(3) for line in xx.lines]

#fig.savefig(r"c:\Users\jpeacock-pr\Google Drive\JVG\mb_resistivities_plot.svg", 
#            dpi=300)


