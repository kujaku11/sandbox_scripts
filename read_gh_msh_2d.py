# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 15:35:49 2017

@author: jpeacock
"""

import numpy as np
import matplotlib.pyplot as plt
import mtpy.modeling.modem as modem

# =============================================================================
# Read in Graham's Model
# =============================================================================
gh_fn = r"c:\Users\jpeacock\Documents\iMush\modem_inv\paul_final_model\Hill_2D\MSH_Adams_2D"

gh_model = np.loadtxt(gh_fn)

x = np.array(sorted(list(set(gh_model[:, 0]))))/1000.-564
y = np.array(sorted(list(set(gh_model[:, 1]))))/1000.*-1

gh_res = gh_model[:, 2].reshape((y.size, x.size))

gh_x_grid, gh_y_grid = np.meshgrid(x, y)

# =============================================================================
# Read in Paul's model
# =============================================================================
pb_fn = r"c:\Users\jpeacock\Documents\iMush\modem_inv\paul_final_model\Z4T3_cov0p2x2_L1E2_NLCG_061.rho"

m_obj = modem.Model()
m_obj.read_model_file(pb_fn)

msh_index = np.where(m_obj.grid_north == -31000)[0][0]
pb_x_grid, pb_y_grid = np.meshgrid(m_obj.grid_east[0:-1]/1000.+12, 
                                   m_obj.grid_z[0:-1]/1000.)
pb_res = m_obj.res_model[msh_index, :, :].T

# =============================================================================
# Plot the 2 models together
# =============================================================================
font_dict = {'size':10, 'weight':'bold'}

fig = plt.figure(1, [5., 6], dpi=300)
fig.subplots_adjust(hspace=.08, left=.01, right=.92, bottom=.12, top=.9)
ax_gh = fig.add_subplot(2, 1, 1, aspect='equal')
im_gh = ax_gh.pcolormesh(gh_x_grid, 
                         gh_y_grid,
                         np.log10(gh_res), 
                         cmap='jet_r',
                         vmin=-1, 
                         vmax=4)

ax_gh.set_ylabel('Depth (km)', fontdict=font_dict)
ax_gh.set_xlim(-20, 60)
ax_gh.set_ylim(40, 0)
ax_gh.tick_params(labelbottom='off')

ax_pb = fig.add_subplot(2, 1, 2, aspect='equal')
im_pb = ax_pb.pcolormesh(pb_x_grid, 
                         pb_y_grid,
                         np.log10(pb_res), 
                         cmap='jet_r',
                         vmin=-1, 
                         vmax=4)

ax_pb.set_xlabel('Distance (km)', fontdict=font_dict)
ax_pb.set_ylabel('Depth (km)', fontdict=font_dict)
ax_pb.set_xlim(-20, 60)
ax_pb.set_ylim(40, 0)

cb_ax = fig.add_axes([.83, .30, .03, .5])
cb = plt.colorbar(im_gh, cax=cb_ax)
cb.set_label('Resistivity (Ohm-m)', fontdict=font_dict)
cb.set_ticks([-1, 0, 1, 2, 3, 4])
cb.set_ticklabels(['$10^{-1}$', '$10^{0}$', '$10^{1}$', '$10^{2}$', 
                   '$10^{3}$', '$10^{4}$'])
cb.update_ticks()
plt.show()

fig.savefig(r"c:\Users\jpeacock\Documents\iMush\Figures\msh_compare_gh.pdf",
            dpi=300)
