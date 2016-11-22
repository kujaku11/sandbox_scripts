# -*- coding: utf-8 -*-
"""
Created on Wed Apr 06 10:50:30 2016

@author: jpeacock
"""
import numpy as np

try:
    import scipy.stats.distributions as ssd 
    ssd_test = True
except ImportError:
    print 'Need scipy.stats.distributions to compute spectra errors'
    print 'Could not find scipy.stats.distributions, check distribution'
    ssd_test = False

class idx(object):
    def __init__(self, comp_list):
        for ii, comp in enumerate(comp_list):
            setattr(self, comp, ii)

#fn = r"d:\Peacock\MTData\EDI_Files\mb018.edi"
#fn = r"c:\Users\jpeacock\Documents\s_arrhanesBugs\Jess\EDI_files\104A.edi"
fn = r"C:\Users\jpeacock\Documents\SaudiArabia\edi_files_fixed_lon\519_rr.edi"
#header_list = []
#m_list = []
#meas_find = False
#count = 0
nfreq = 60
with open(fn, 'r') as fid:
    data_lines = fid.readlines()[54:]
            


# make some empty arrays
#z_arr = np.zeros((nfreq, 2, 2), dtype=np.complex)
#z_err_arr = np.zeros((nfreq, 2, 2), dtype=np.float)
#z_rot = np.zeros(nfreq, dtype=np.float)
#
#freq_arr = np.zeros(nfreq, dtype=np.float)
#t_arr = np.zeros((nfreq, 1, 2), dtype=np.complex)        
#t_err_arr = np.zeros((nfreq, 1, 2), dtype=np.float)        

data_dict = {}
avgt_dict = {}
data_find = False
for line in data_lines:
    if line.lower().find('>spectra') == 0 and line.find('!') == -1:
        line_list = line[1:].strip().split()
        data_find = True
        
        # frequency will be the key
        try:
            key = float(line_list[1].split('=')[1])
            data_dict[key] = []
            avgt_dict[key] = float(line_list[4].split('=')[1])
        except ValueError:
            print 'did not find frequency key'

    elif data_find == True and line.find('>') == -1 and line.find('!') == -1:
        data_dict[key] += [float(ll) for ll in line.strip().split()]
    
    elif line.find('>spectra') == -1:
        data_find = False
        
    
comp_list = ['hx', 'hy', 'hz', 'ex', 'ey', 'rhx', 'rhy']
cc = idx(comp_list) 

z_arr = np.zeros((len(data_dict.keys()), 2, 2), dtype=np.complex)
t_arr = np.zeros((len(data_dict.keys()), 1, 2), dtype=np.complex)

z_err_arr = np.zeros_like(z_arr, dtype=np.float)
t_err_arr = np.zeros_like(t_arr, dtype=np.float)

freq_arr = np.array(sorted(data_dict.keys(), reverse=True))
        
for kk, key in enumerate(freq_arr):
    spectra_arr = np.reshape(np.array(data_dict[key]), 
                             (len(comp_list), len(comp_list)))
                             
    # compute cross powers
    s_arr = np.zeros_like(spectra_arr, dtype=np.complex)
    for ii in range(s_arr.shape[0]):
        for jj in range(ii, s_arr.shape[0]):
            if ii == jj:
                s_arr[ii, jj] = (spectra_arr[ii, jj])
            else:
                #minus sign for complex conjugation
                # original spectra data are of form <A,B*>, but we need 
                # the order <B,A*>...
                # this is achieved by complex conjugation of the original entries
                s_arr[ii, jj] = np.complex(spectra_arr[jj, ii],
                                           -spectra_arr[ii, jj])
                #keep complex conjugated entries in the lower triangular matrix:
                s_arr[jj, ii] = np.complex(spectra_arr[jj, ii],
                                           spectra_arr[ii, jj])
                                           
    #use formulas from Bahr/s_arrimpson to convert the s_arrpectra into Z entries
    # the entries of s_arr are sorted like
    # <X,X*>  <X,Y*>  <X,Z*>  <X,En*>  <X,Ee*>  <X,Rx*>  <X,Ry*>
    #         <Y,Y*>  <Y,Z*>  <Y,En*>  <Y,Ee*>  <Y,Rx*>  <Y,Ry*> 
    # .....

    # note: the sorting can be influenced by wrong order of indices - 
    # the list 'idx' takes care of that

    z_arr[kk, 0, 0] = s_arr[cc.ex, cc.rhx]*s_arr[cc.hy, cc.rhy]-\
                                s_arr[cc.ex, cc.rhy]*s_arr[cc.hy, cc.rhx] 
    z_arr[kk, 0, 1] = s_arr[cc.ex, cc.rhy]*s_arr[cc.hx, cc.rhx]-\
                                s_arr[cc.ex, cc.rhx]*s_arr[cc.hx, cc.rhy] 
    z_arr[kk, 1, 0] = s_arr[cc.ey, cc.rhx]*s_arr[cc.hy, cc.rhy]-\
                                s_arr[cc.ey, cc.rhy]*s_arr[cc.hy, cc.rhx] 
    z_arr[kk, 1, 1] = s_arr[cc.ey, cc.rhy]*s_arr[cc.hx, cc.rhx]-\
                                s_arr[cc.ey, cc.rhx]*s_arr[cc.hx, cc.rhy]

    z_arr[kk] /= (s_arr[cc.hx, cc.rhx]*s_arr[cc.hy, cc.rhy]-\
                        s_arr[cc.hx, cc.rhy]*s_arr[cc.hy, cc.rhx])

    # 68% Quantil of the Fisher distribution:
    z_det = np.real(s_arr[cc.hx, cc.hx]*s_arr[cc.hy, cc.hy]-\
                        s_arr[cc.hx, cc.hy]*s_arr[cc.hy, cc.hx])

    sigma_quantil = ssd.f.ppf(0.68, 4, avgt_dict[key]-4)
    
    #1) Ex
    a =  s_arr[cc.ex, cc.hx]*s_arr[cc.hy, cc.hy]-\
                s_arr[cc.ex, cc.hy]*s_arr[cc.hy, cc.hx]  
    b =  s_arr[cc.ex, cc.hy]*s_arr[cc.hy, cc.hy]- \
                s_arr[cc.ex, cc.hx]*s_arr[cc.hx, cc.hy]
    a /= z_det
    b /= z_det  

    psi_squared = np.real(1./s_arr[cc.ex, cc.ex].real*\
                    (a*s_arr[cc.hx, cc.ex]+b*s_arr[cc.hy, cc.ex]))
    epsilon_squared = 1.-psi_squared

    scaling = sigma_quantil*4/(avgt_dict[key]-4.)*\
                epsilon_squared/z_det*s_arr[cc.ex, cc.ex].real
    z_err_arr[kk, 0, 0] = np.sqrt(scaling*s_arr[cc.hy, cc.hy].real)
    z_err_arr[kk, 0, 1] = np.sqrt(scaling*s_arr[cc.hx, cc.hx].real)


    #2) Ey
#    a =  s_arr[idx[4],idx[0]] * s_arr[idx[1],idx[1]] - \
#            s_arr[idx[4],idx[1]] * s_arr[idx[1],idx[0]] 
#    b =  s_arr[idx[4],idx[1]] * s_arr[idx[0],idx[0]] -\
#             s_arr[idx[4],idx[0]] * s_arr[idx[0],idx[1]] 
#    a /= Zdet
#    b /= Zdet  
#
#    psi_squared = np.real(1./np.real(s_arr[idx[4],idx[4]]) * \
#                    (a*s_arr[idx[0],idx[4]]+b*s_arr[idx[1],idx[4]]))
#    epsilon_squared = 1.-psi_squared
#
#    scaling = sigma_quantil*4/(avgt-4.)*epsilon_squared/Zdet*\
#                np.real(s_arr[idx[4],idx[4]])
#    zerr_array[1,0] = np.sqrt(scaling*np.real(s_arr[idx[1],idx[1]]))
#    zerr_array[1,1] = np.sqrt(scaling*np.real(s_arr[idx[0],idx[0]]))

    a =  s_arr[cc.ey, cc.hx]*s_arr[cc.hy, cc.hy]-\
                s_arr[cc.ey, cc.hy]*s_arr[cc.hy, cc.hx]  
    b =  s_arr[cc.ey, cc.hy]*s_arr[cc.hx, cc.hx]- \
                s_arr[cc.ey, cc.hx]*s_arr[cc.hx, cc.hy]
    a /= z_det
    b /= z_det  

    psi_squared = np.real(1./np.real(s_arr[cc.ey, cc.ey])*\
                    (a*s_arr[cc.hx, cc.ey]+b*s_arr[cc.hy, cc.ey]))
    epsilon_squared = 1.-psi_squared

    scaling = sigma_quantil*4/(avgt_dict[key]-4.)*\
                epsilon_squared/z_det*np.real(s_arr[cc.ey, cc.ey])
    z_err_arr[kk, 1, 0] = np.sqrt(scaling*np.real(s_arr[cc.hy, cc.hy]))
    z_err_arr[kk, 1, 1] = np.sqrt(scaling*np.real(s_arr[cc.hx, cc.hx]))


    #if HZ information is present:
    if len(comp_list) > 5:
        t_arr[kk, 0, 0] = s_arr[cc.hz, cc.rhx]*s_arr[cc.hy, cc.rhy]-\
                            s_arr[cc.hz, cc.rhy]*s_arr[cc.hy, cc.rhx] 
        t_arr[kk, 0, 1] = s_arr[cc.hz, cc.rhy]*s_arr[cc.hx, cc.rhx]-\
                            s_arr[cc.hz, cc.rhx]*s_arr[cc.hx, cc.rhy] 

        t_arr[kk] /= z_det

        #3) Tipper
#        a =  s_arr[idx[2],idx[0]] * s_arr[idx[1],idx[1]] - \
#                        s_arr[idx[2],idx[1]] * s_arr[idx[1],idx[0]] 
#        b =  s_arr[idx[2],idx[1]] * s_arr[idx[0],idx[0]] - \
#                        s_arr[idx[2],idx[0]] * s_arr[idx[0],idx[1]] 
#        a /= Zdet
#        b /= Zdet  
#
#        psi_squared = np.real(1./np.real(s_arr[idx[2],idx[2]]) * \
#                        (a* s_arr[idx[0],idx[2]] + b *s_arr[idx[1],idx[2]]))
#        epsilon_squared = 1.-psi_squared
#        scaling = sigma_quantil*4/(avgt-4.)*epsilon_squared/Zdet*\
#                            np.real(s_arr[idx[2],idx[2]])
#
#        tippererr_array[0,0] = np.sqrt(scaling*np.real(s_arr[idx[1],idx[1]]))
#        tippererr_array[0,1] = np.sqrt(scaling*np.real(s_arr[idx[0],idx[0]]))
        
        a =  s_arr[cc.hz, cc.hx]*s_arr[cc.hy, cc.hy]-\
                s_arr[cc.hz, cc.hy]*s_arr[cc.hy, cc.hx]  
        b =  s_arr[cc.hz, cc.hy]*s_arr[cc.hx, cc.hx]- \
                    s_arr[cc.hz, cc.hx]*s_arr[cc.hx, cc.hy]
        a /= z_det
        b /= z_det  
    
        psi_squared = np.real(1./np.real(s_arr[cc.hz, cc.hz])*\
                        (a*s_arr[cc.hx, cc.hz]+b*s_arr[cc.hy, cc.hz]))
        epsilon_squared = 1.-psi_squared
    
        scaling = sigma_quantil*4/(avgt_dict[key]-4.)*\
                    epsilon_squared/z_det*np.real(s_arr[cc.hz, cc.hz])
        t_err_arr[kk, 0, 0] = np.sqrt(scaling*np.real(s_arr[cc.hy, cc.hy]))
        t_err_arr[kk, 0, 1] = np.sqrt(scaling*np.real(s_arr[cc.hx, cc.hx]))

#
#    z_det = (s_arr[0, 5]*s_arr[1, 6]-s_arr[0, 6]*s_arr[1, 5])
#
#    z_arr[kk, 0, 0] = s_arr[3, 5]*s_arr[1, 6]-s_arr[3, 6]*s_arr[1, 5] 
#    z_arr[kk, 0, 1] = s_arr[3, 6]*s_arr[0, 5]-s_arr[3, 5]*s_arr[0, 6] 
#    z_arr[kk, 1, 0] = s_arr[4, 5]*s_arr[1, 6]-s_arr[4, 6]*s_arr[1, 5] 
#    z_arr[kk, 1, 1] = s_arr[4, 6]*s_arr[0, 5]-s_arr[4, 5]*s_arr[0, 6]
#
#    z_arr[kk] /= z_det
#    
#    #if HZ information is present:
#    if len(comp_list) > 5:
#        t_arr[kk, 0, 0] = s_arr[2, 5]*s_arr[1, 6]-\
#                            s_arr[2, 6]*s_arr[1, 5] 
#        t_arr[kk, 0, 1] = s_arr[2, 6]*s_arr[0, 5]-\
#                            s_arr[2, 5]*s_arr[0, 6] 
#
#        t_arr[kk] /= z_det
#
#freq_arr = np.array(data_dict['freq'], dtype=np.float)
#z_rot = np.array(data_dict['zrot'], dtype=np.float)
#
## make Z 
#z_arr = np.zeros((nfreq, 2, 2), dtype=np.complex)
#z_err_arr = np.zeros((nfreq, 2, 2), dtype=np.float)
#
#z_arr[:, 0, 0] = np.array(data_dict['zxxr'])+np.array(data_dict['zxxi'])*1j
#z_arr[:, 0, 1] = np.array(data_dict['zxyr'])+np.array(data_dict['zxyi'])*1j
#z_arr[:, 1, 0] = np.array(data_dict['zyxr'])+np.array(data_dict['zyxi'])*1j
#z_arr[:, 1, 1] = np.array(data_dict['zyyr'])+np.array(data_dict['zyyi'])*1j
#
#z_err_arr[:, 0, 0] = np.array(data_dict['zxx.var'])
#z_err_arr[:, 0, 1] = np.array(data_dict['zxy.var'])
#z_err_arr[:, 1, 0] = np.array(data_dict['zyx.var'])
#z_err_arr[:, 1, 1] = np.array(data_dict['zyy.var'])
#
#t_arr = np.zeros((nfreq, 1, 2), dtype=np.complex)        
#t_err_arr = np.zeros((nfreq, 1, 2), dtype=np.float) 
#
#if 'txr.exp' in data_dict.keys():
#    t_arr[:, 0, 0] = np.array(data_dict['txr.exp'])+np.array(data_dict['txi.exp'])*1j
#    t_arr[:, 0, 1] = np.array(data_dict['tyr.exp'])+np.array(data_dict['tyi.exp'])*1j
#    
#    t_err_arr[:, 0, 0] = np.array(data_dict['txvar.exp'])    
#    t_err_arr[:, 0, 1] = np.array(data_dict['tyvar.exp']) 
#    
#else:
#    print 'Could not find any Tipper data.'
#
#
#hdict = {}
#for hline in header_list:
#    h_list = hline.split('=')
#    key = h_list[0]
#    value = h_list[1]
#    hdict[key] = value
        
        
#info_list = []
#info_find = False
#phoenix_file = False
#phoenix_list_02 = []
#count = 0
#with open(fn, 'r') as fid:
#    for line in fid:
#        if line.find('>') == 0:
#            count += 1
#            if line.lower().find('info') > 0:
#                info_find = True
#            else:
#                info_find = False
#            if count > 2 and info_find == False:
#                break
#        elif count > 1 and line.find('>') != 0 and info_find == True:
#            if line.lower().find('run information') >= 0:
#                phoenix_file = True
#            if phoenix_file == True and len(line) > 40:
#                info_list.append(line[0:37].strip())
#                phoenix_list_02.append(line[38:].strip())
#            else:
#                if len(line.strip()) > 1:
#                    info_list.append(line.strip())  
#                    
#info_list += phoenix_list_02
#
##                
#new_info_list = []
#phoenix_file = False
#for line in info_list:
#    # get rid of empty lines
#    lt = str(line).strip()
#    if len(lt) > 1:
#        # check for phoenix format
#        if line.find('>') == 0:
#            pass
##        if line.lower().find('run information') >= 0:
##            phoenix_file = True
##            new_info_list_02 = []
##        if phoenix_file == True and len(line) > 40:
##            new_info_list.append(line[0:37].strip())
##            new_info_list_02.append(line[38:].strip())
#        else:
#            new_info_list.append(line.strip())

