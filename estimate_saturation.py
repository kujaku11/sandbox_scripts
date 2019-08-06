# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 16:44:42 2019

@author: jpeacock
"""
import numpy as np
#from mtpy.modeling import modem
#from scipy import interpolate
import matplotlib.pyplot as plt
import pandas as pd

fn = r"c:\Users\jpeacock\Documents\Geysers\modem_inv\inv04\gz_rm50_z03_c05_107.rho"

class RockPhase(object):
    """
    simple class for a rock phase
    """
    
    def __init__(self, sigma=None, phi=None, m=None, **kwargs):
        self.sigma = sigma
        self.phi = phi
        self.m = m
        
        for key, item in kwargs.items():
            setattr(self, key, item)
            
    def from_dict(self, phase_dict):
        """
        read in values from dictionary
        """
        for key, item in phase_dict.items():
            setattr(self, key, item)
        
        
    def is_phase(self):
        """
        test if all attributes are full
        """
        
        if type(self.sigma) is type(None) and type(self.phi) is type(None) \
           and type(self.m) is type(None):
            return False
        else:
            return True
        
    def calculate_phase(self):
        """
        calculate the contribution of a given phase
        """
        if self.is_phase():
            return self.sigma * self.phi**self.m
        else:
            return 0

class Glover(object):
    """
    estimate modified archies equation for multiple phases
    """
    
    def __init__(self):
        self._max_phase = 4
        
        for ii in range(self._max_phase):
            setattr(self, 'phase_{0:02}'.format(ii+1), RockPhase())
            
    @property
    def num_phases(self):
        """
        get the number of phases
        """
        num_phases = 0
        for ii in range(self._max_phase):
            if getattr(self, 'phase_{0:02}'.format(ii+1)).is_phase(): 
                num_phases += 1
        return num_phases
                
    def estimate_resistivity(self):
        """
        estimate resistivity from different given phases
        """
        res = 0
        for ii in range(self.num_phases):
            phase = getattr(self, 'phase_{0:02}'.format(ii+1))
            res += phase.calculate_phase()
            
        return 1./res
    
    @property
    def x(self):
        """
        get the x axis 
        """
        x = self.phase_01.phi
        if type(x) is float:
            x = np.array([x])
        for ii in range(self.num_phases):
            phase = getattr(self, 'phase_{0:02}'.format(ii+1))
            try:
                if len(phase.phi) > len(x):
                    x = phase.phi
            except TypeError:
                pass
                    
        return x
    
    def plot(self):
        """
        plot resistivity contributions
        """
        
        fig = plt.figure()
        fig.clf()
        
        ax_01 = fig.add_subplot(2, 1, 1)
        ax_02 = fig.add_subplot(2, 1, 2, sharex=ax_01)
        line_list = []
        label_list = []
        for ii in range(self.num_phases):
            phase = getattr(self, 'phase_{0:02}'.format(ii+1))
            line, = ax_01.plot(phase.phi, 1./phase.calculate_phase())
            line_list.append(line)
            label_list.append(phase.label)
            
        ax_01.legend(line_list, label_list)
        line, = ax_02.plot(self.x[::-1], self.estimate_resistivity(), 'r')
        
        for ax in [ax_01, ax_02]:
            ax.set_ylabel('Resistivity ($\Omega \cdot m$)')
            ax.set_xlabel('Percent Contribution')
            ax.set_yscale('log')
        
        plt.show()
            
s = np.linspace(0, .95)
g = Glover()
g.phase_01.from_dict({'sigma':1./10000, 'phi':.88, 'm':.05, 'label':'rock'})
g.phase_02.from_dict({'sigma':1./.5, 'phi':.08, 'm':2., 'label':'EDL'})
g.phase_03.from_dict({'sigma':1./.01, 'phi':.04, 'm':3.5,
                      'label':'pyrite'})
g.phase_04.from_dict({'sigma':1./1000, 'phi':.04, 'm':2,
                      'label':'steam'})
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
                
res_min, res_max = (60, 340)
r_dict = {'res':[], 'phi_r':[], 'phi_f':[], 'phi_p':[], 'phi_s':[]}
for phi_r in np.linspace(.87, .99, num=100):
    for phi_f in np.linspace(.0, .13, num=100):
        for phi_p in np.linspace(.0, .05, num=100):
            for phi_s in np.linspace(0, .1, num=400):
                if phi_r + phi_f + phi_p + phi_s == 1:
                    g.phase_01.phi = phi_r
                    g.phase_02.phi = phi_f
                    g.phase_03.phi = phi_p
                    g.phase_04.phi = phi_s
                    res = g.estimate_resistivity()
                    if res >= res_min and res <= res_max: 
                        r_dict['res'].append(res)
                        r_dict['phi_r'].append(phi_r)
                        r_dict['phi_f'].append(phi_f)
                        r_dict['phi_p'].append(phi_p)
                        r_dict['phi_s'].append(phi_s)
                    
df = pd.DataFrame(r_dict)
df.hist(bins=50)    
    
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


