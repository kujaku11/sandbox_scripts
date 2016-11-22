
# coding: utf-8

# In[1]:

import os
import mtpy.imaging.mtplot as mtplot
import numpy as np


# In[2]:

edi_path_imush = r"c:\Users\jpeacock\Documents\iMush\iMush_edited_edi_files_JRP\Interpolated"
edi_list_imush = [os.path.join(edi_path_imush, edi_fn) for edi_fn in os.listdir(edi_path_imush) if edi_fn.endswith('.edi')]


# In[3]:

edi_path_mshn = r"c:\Users\jpeacock\Documents\Geothermal\Washington\MSH\INV_EDI_Files\Interpolated"
edi_list_mshn = [os.path.join(edi_path_mshn, edi_fn) for edi_fn in os.listdir(edi_path_mshn) if edi_fn.endswith('.edi')]


# In[ ]:

ptm = mtplot.plot_pt_map(fn_list=edi_list_imush+edi_list_mshn,
                         plot_freq=.198, 
                         plot_yn='n',
                         fig_size=[6,5],
                         image_dict={'file':r"c:\Users\jpeacock\Documents\iMush\imush_basemap_google_earth.jpg",
                                     'extent':(-123.78, -120.068, 47.23444, 45.45071)})
 

# In[ ]:
ptm.plot_tipper = 'yri'
ptm.arrow_head_length = .01
ptm.arrow_head_width = .01
ptm.arrow_lw = .5
ptm.ellipse_size = .01
ptm.arrow_size = .1
ptm.arrow_color_real = (.8, .8, .8)
ptm.arrow_color_imag = (.1, .1, .1)
ptm.plot()

for ii, ff in enumerate(np.logspace(-3, 3, 48)[::-1]):
    try:
        ptm.plot_freq = ff
        ptm.redraw_plot()
        ptm.save_figure(r"c:\Users\jpeacock\Documents\iMush\iMush_edited_edi_files_JRP\Interpolated\PT_Maps\{0:02}_pt_map.png".format(ii),
                        fig_dpi=1200)
    except:
        pass
    


# In[ ]:



