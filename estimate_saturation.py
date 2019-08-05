# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 16:44:42 2019

@author: jpeacock
"""
import numpy as np
#from mtpy.modeling import modem
#from scipy import interpolate
import matplotlib.pyplot as plt

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
            
        return res
    
    def plot(self):
        """
        plot resistivity contributions
        """
        
        fig = plt.figure()
        fig.clf()
        
        ax = fig.add_subplot(1, 1, 1)
        
        line_list = []
        label_list = []
        for ii in range(self.num_phases):
            phase = getattr(self, 'phase_{0:02}'.format(ii+1))
            res = phase.calculate_phase()
            line, = ax.plot(1./res)
            line_list.append(line)
            label_list.append(phase.label)
            
        line, = ax.plot(1./self.estimate_resistivity())
        line_list.append(line)
        label_list.append('Total')
        ax.legend(line_list, label_list)
        
        ax.set_ylabel('Resistivity ($\Omega \cdot m$)')
        ax.set_yscale('log')
        
        plt.show()
            
s = np.linspace(0, .95)
g = Glover()
g.phase_01.from_dict({'sigma':1./10000, 'phi':1-s, 'm':.5, 'label':'rock'})
g.phase_02.from_dict({'sigma':1./10000, 'phi':s, 'm':1.5, 'label':'steam'})
g.phase_03.from_dict({'sigma':1./.001, 'phi':.05, 'm':3.5,
                      'label':'pyrite'})
print('resistivity = {0}'.format(g.estimate_resistivity()))
g.plot()



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


