# -*- coding: utf-8 -*-
"""
Created on Fri Jul 11 12:30:32 2014

@author: jpeacock-pr
"""


import numpy as np
import mtpy.modeling.modem_new as modem

mfn = r"c:\MinGW32-xy\Peacock\ModEM\WS_StartingModel_01\Modular_NLCG_000.rho"

mdm = modem.Model()
mdm.read_model_file(mfn)

grid_z = mdm.grid_z.copy()
dscale = 1000
res_model = mdm.res_model.copy()

period = 50
# ==============================================================================
# ESTIMATE SKIN DEPTH FOR MODEL
# ==============================================================================
# def estimate_skin_depth(res_model, grid_z, period, dscale=1000):
#    """
#    estimate the skin depth from the resistivity model assuming that
#
#        delta_skin ~ 500 * sqrt(rho_a*T)
#
#    Arguments:
#    -----------
#        **resmodel** : np.ndarray (n_north, n_east, n_z)
#                       array of resistivity values for model grid
#
#        **grid_z** : np.ndarray (n_z)
#                     array of depth layers in m or km, be sure to change
#                     dscale accordingly
#
#        **period** : float
#                     period in seconds to estimate a skin depth for
#
#        **dscale** : [1000 | 1]
#                     scaling value to scale depth estimation to meters (1) or
#                     kilometers (1000)
#
#    Outputs:
#    ---------
#        **depth** : float
#                    estimated skin depth in units according to dscale
#
#        **depth_index** : int
#                          index value of grid_z that corresponds to the
#                          estimated skin depth.
#    """
if dscale == 1000:
    ms = "km"
if dscale == 1:
    ms = "m"
# find the apparent resisitivity of each depth slice within the station area
apparent_res_xy = np.array(
    [res_model[6:-6, 6:-6, 0 : ii + 1].mean() for ii in range(grid_z.shape[0])]
)

# calculate the period for each skin depth
skin_depth_period = np.array(
    [(zz / (500.0)) ** 2 * (1 / rho_a) for zz, rho_a in zip(grid_z, apparent_res_xy)]
)

# match the period
try:
    period_index = np.where(skin_depth_period >= period)[0][0]
except IndexError:
    period_index = len(skin_depth_period) - 1

# get the depth slice
depth = grid_z[period_index]

print "-" * 60
print " input period                   {0:.6g} (s)".format(period)
print " estimated skin depth period    {0:.6g} (s)".format(
    skin_depth_period[period_index]
)
print " estimate apparent resisitivity {0:.0f} (Ohm-m)".format(
    apparent_res_xy[period_index].mean()
)
print " estimated depth                {0:.6g} ({1})".format(depth, ms)
print " index                          {0}".format(period_index)
print "-" * 60
