
# coding: utf-8

# ## Interpolate a list of .edi files onto the same period range

# In[1]:

import os
import mtpy.core.mt as mt
import numpy as np


# In[2]:

edi_path = r"c:\Users\jpeacock\Documents\iMush\iMush_edited_edi_files_tipper_rot_geographic_north\Edited"
edi_list = [os.path.join(edi_path, edi_fn) for edi_fn in os.listdir(edi_path) if edi_fn.endswith('.edi')]


# In[3]:

save_path = os.path.join(edi_path, 'Interpolated')
if not os.path.isdir(save_path):
    os.mkdir(save_path)


# In[4]:

# make a new frequency list to interpolate on to [1000 Hz - 1000 sec]
interp_freq = 1./np.logspace(-np.log10(1000), np.log10(25000), num=64)
#interp_freq = np.logspace(np.log10(7.3242e-04), 3, num=48)


# In[5]:

for edi_fn in edi_list:
    mt_obj = mt.MT(edi_fn)
    new_f = interp_freq[np.where((interp_freq >= mt_obj.Z.freq.min()) & (interp_freq <= mt_obj.Z.freq.max()))]
    new_z_obj, new_t_obj = mt_obj.interpolate(new_f)
    new_edi_fn = os.path.join(save_path, os.path.basename(edi_fn))
    mt_obj.write_edi_file(new_fn=new_edi_fn, new_Z=new_z_obj, new_Tipper=new_t_obj)
    


# In[ ]:



