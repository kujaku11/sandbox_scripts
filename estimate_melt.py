# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 16:44:42 2019

@author: jpeacock
"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import rock_properties as rp
                    
label_dict = {'phi_r':{'title':'Rock', 'x_label':'Percent'},
              'phi_f':{'title':'Fluid', 'x_label':'Percent'},
              'res':{'title':'Bulk Rock', 'x_label':'Resistivity ($\Omega \cdot m$)'},
              'sigma_f':{'title':'Fluid Resistivity', 'x_label':'Resistivity ($\Omega \cdot m$)'}}

g = rp.Glover()
g.phase_01.from_dict({'sigma':1./1E4, 'phi':.88, 'm':.05, 'label':'rock'})
#g.phase_02.from_dict({'sigma':1./.5, 'phi':.08, 'm':3., 'label':'EDL'})
#g.phase_02.from_dict({'sigma':1./1, 'phi':.04, 'm':1.5, 'label':'fluids'})
g.phase_02.from_dict({'sigma':1./5, 'phi':.05, 'm':1.05, 'label':'fluids'})

res_min, res_max = (28, 40)
n = int(1E4)
res_dict = {'res':[], 'phi_r':[], 'phi_f':[], 'sigma_f':[]}
for phi_r, sigma_f in zip(np.random.normal(.85, .15, n), 
                          np.random.lognormal(.015, .4, n)):
    if phi_r > 1:
        continue
    g.phase_01.phi = phi_r
    g.phase_02.phi = 1 - phi_r
    g.phase_02.sigma = sigma_f
    res = g.estimate_resistivity()
    if res >= res_min and res <= res_max: 
        res_dict['res'].append(res)
        res_dict['phi_r'].append(g.phase_01.phi)
        res_dict['phi_f'].append(g.phase_02.phi)
        res_dict['sigma_f'].append(1./g.phase_02.sigma)
    

df = pd.DataFrame(res_dict)

fig = plt.figure(1, dpi=150)
fig.clf()
for ii, col in enumerate(df.columns, 1): 
    ax = fig.add_subplot(2, 2, ii)
    best_d, best_p, params = rp.get_best_distribution(df[col])
    
    
    if col not in ['res']:
        num, bins, patches = ax.hist(df[col], bins=100, density=1)
        pdf, pdf_min, pdf_max = rp.fit_distribution(bins, params, best_d)
        f, = ax.plot(bins, pdf)
    elif col in ['res']:
        num, bins, patches = ax.hist(df[col], bins=np.logspace(np.log10(res_min),
                          np.log10(res_max), 100), density=1)
        pdf, pdf_min, pdf_max = rp.fit_distribution(bins, params, best_d)
        f, = ax.plot(bins, pdf)
        #ax.set_xscale('log')
    ax.set_xlabel(label_dict[col]['x_label'])
    ax.set_title(label_dict[col]['title'])
    ax.grid(which='major', ls=':', lw=.75, color=(.6, .6, .6))
    ax.set_axisbelow(True)
    mlk = bins[np.where(pdf == pdf.max())][0]
    lk, = ax.plot([mlk, mlk], [0, num.max()], 
                         lw=3, ls=':', color='k')
    l_max, = ax.plot([pdf_max, pdf_max],
                       [0, num.max()], lw=3, ls=':', color=(.5, .5, .5))
    
    l_min, = ax.plot([pdf_min, pdf_min], [0, num.max()], 
                     lw=3, ls=':', color=(.5, .5, .5))
    l2, = ax.plot([None, None], [None, None], 'b', ls='none')
    mlk_data = bins[np.where(num == num.max())][0]
    ax.legend([l2, l2, lk, l_min, l_max, l2], 
              ['distribution = {0}'.format(best_d),
               'data mode = {0:<5.4g}'.format(mlk_data),
               'fit mode = {0:<5.4g}'.format(mlk),
               '50th min = {0:<5.4g}'.format(pdf_min),
               '50th max = {0:<5.4g}'.format(pdf_max)],
               loc='best')
#    if col in ['sigma_f']:
#        labels = 1./ax.get_xticks()
#        labels[labels==np.inf] = 0
#        labels = ['{0:.1f}'.format(ll) for ll in labels]
#        labels[0] = ''
#        ax.set_xticklabels(labels)
#        ax.set_xlim(.25, 2.5)
fig.tight_layout()
plt.show()
### steam
#g.phase_01.from_dict({'sigma':1./1E8, 'phi':.88, 'm':.05, 'label':'rock'})
#g.phase_02.from_dict({'sigma':1./.5, 'phi':.08, 'm':2., 'label':'EDL'})
#g.phase_03.from_dict({'sigma':1./.01, 'phi':.04, 'm':3.5,
#                      'label':'pyrite'})
##g.phase_04.from_dict({'sigma':1./1000, 'phi':.04, 'm':2,
##                      'label':'steam'})
#g.phase_04.from_dict({'sigma':1./1000, 'phi':.04, 'm':2,
#                      'label':'inclusion'})

#g.phase_01.from_dict({'sigma':1./100, 'phi':1-s, 'm':.5, 'label':'rock'})
#g.phase_02.from_dict({'sigma':1./1000, 'phi':s, 'm':1.5, 'label':'steam'})
#g.phase_03.from_dict({'sigma':1./.01, 'phi':.05, 'm':3.5,
#                      'label':'pyrite'})
    
#res_min, res_max = (20, 50)
#r_dict = {'res':[], 'phi_r':[], 'phi_f':[], 'phi_p':[]}
#for phi_r in np.linspace(.85, .99, num=400):
#    for phi_f in np.linspace(0, .15, num=400):
#        for phi_p in np.linspace(0, .05, num=400):
#            if phi_r + phi_f + phi_p == 1:
#                g.phase_01.phi = phi_r
#                g.phase_02.phi = phi_f
#                g.phase_03.phi = phi_p
#                res = g.estimate_resistivity()
#                if res >= res_min and res <= res_max: 
#                    r_dict['res'].append(res)
#                    r_dict['phi_r'].append(phi_r)
#                    r_dict['phi_f'].append(phi_f)
#                    r_dict['phi_p'].append(phi_p)
#                    
#df = pd.DataFrame(r_dict)
#df.hist(bins=50)
                
#res_min, res_max = (60, 95)
#r_dict = {'res':[], 'phi_r':[], 'phi_f':[], 'phi_p':[], 'phi_s':[]}
#for phi_r in np.linspace(.87, .88, num=100):
#    for phi_f in np.linspace(.05, .07, num=100):
#        for phi_p in np.linspace(.0, .01, num=100):
#            for phi_s in np.linspace(0, .1, num=400):
#                if phi_r + phi_f + phi_p + phi_s == 1:
#                    g.phase_01.phi = phi_r
#                    g.phase_02.phi = phi_f
#                    g.phase_03.phi = phi_p
#                    g.phase_04.phi = phi_s
#                    res = g.estimate_resistivity()
#                    if res >= res_min and res <= res_max: 
#                        r_dict['res'].append(res)
#                        r_dict['phi_r'].append(phi_r)
#                        r_dict['phi_f'].append(phi_f)
#                        r_dict['phi_p'].append(phi_p)
#                        r_dict['phi_s'].append(phi_s)
#                    
#df = pd.DataFrame(res_dict)
#df.hist(bins=50)    
    
#print('resistivity = {0}'.format(g.estimate_resistivity()))
#g.plot()



#def glover(phase_dict, sigma_1, phi_1, m_1, sigma_2, phi_2, m_2, 
#           sigma_3=None, phi_3=None, m_3=None):
#    sigma_eff = sigma_1 * phi_1**m_1 + sigma_2 * phi_2**m_2
#    if sigma_3 is not None:
#        sigma_eff += sigma_3 * phi_3**m_3
#
#    return sigma_eff
#
#phi_3 = .05
#m_3 = 3.6;
#sigma_3 = 100
#sigma_rock = 1./100
#saturation = np.linspace(phi_3, .95, 25)
#s = 1./glover(sigma_rock, .95-saturation, .5,
#              1./1000, saturation, 1.5, 
#              sigma_3, phi_3, m_3)

#plt.plot(saturation, s)

#s_interp = interpolate.interp1d(s, saturation, kind='slinear',
#                                bounds_error=False, 
#                                fill_value=np.NAN,
#                                assume_sorted=False)
#
#m = modem.Model()
#m.read_model_file(fn)
#
#res = s_interp(m.res_model.copy().flatten()).reshape(m.res_model.shape)
#
#m.res_model = res.copy()
#m.write_model_file(model_fn_basename='gz_saturation.rho')
#m.write_vtk_file(vtk_fn_basename='gz_saturation')


