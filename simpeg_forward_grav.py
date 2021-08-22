"""
PF: Gravity: Inversion Linear
=============================

Create a synthetic block model and calculate forward model

"""

# =============================================================================
# Imports
# =============================================================================
import numpy as np
import matplotlib.pyplot as plt

from SimPEG import Mesh
from SimPEG import Utils
from SimPEG import Maps
from SimPEG import PF

# =============================================================================
# Inputs
# =============================================================================
### cell width in kilometers?
dx = 2.0
dy = 2
dz = 2

nx = 30
ny = 30
nz = 10

pad_x = 5
pad_y = 5
pad_z = 5

pad_x_factor = 1.3
pad_y_factor = 1.3
pad_z_factor = 1.3

# =============================================================================
#
# =============================================================================
### ( initial width, number of cells, increase by factor)
### (pad, center, pad)
hx_ind = [(dx, pad_x, -pad_x_factor), (dx, nx), (dx, pad_x, pad_x_factor)]
hy_ind = [(dy, pad_y, -pad_y_factor), (dy, ny), (dy, pad_y, pad_y_factor)]
hz_ind = [(dz, pad_z, -pad_z_factor), (dz, nz), (3.5, 1), (2, 5)]

### make a mesh
mesh = Mesh.TensorMesh([hx_ind, hy_ind, hz_ind], "CCC")

# Get index of the center
mid_x = int(mesh.nCx / 2)
mid_y = int(mesh.nCy / 2)

# Lets create a simple Gaussian topo and set the active cells
[xx, yy] = np.meshgrid(mesh.vectorNx, mesh.vectorNy)
zz = -np.exp((xx ** 2 + yy ** 2) / 75 ** 2) + mesh.vectorNz[-1]

### We would usually load a topofile
topo = np.c_[Utils.mkvc(xx), Utils.mkvc(yy), Utils.mkvc(zz)]

### Go from topo to array of indices of active cells
active_cells = Utils.surface2ind_topo(mesh, topo, "N")
active_cells = np.where(active_cells)[0]
num_cells = len(active_cells)

### Create and array of observation points
x_receiver = np.linspace(-30.0, 30.0, 20)
y_receiver = np.linspace(-30.0, 30.0, 20)
X_r, Y_r = np.meshgrid(x_receiver, y_receiver)

### Move the observation points 5m (?) above the topo
Z_r = -np.exp((X_r ** 2 + Y_r ** 2) / 75 ** 2) + mesh.vectorNz[-1] + 0.001

### Create a GRAVsurvey
### make an array of station locations
rx_loc = np.c_[Utils.mkvc(X_r.T), Utils.mkvc(Y_r.T), Utils.mkvc(Z_r.T)]

# put these into a potential field gravity object
rx_loc = PF.BaseGrav.RxObs(rx_loc)

# need to make the source field be the gravity station locations
grav_src_field = PF.BaseGrav.SrcField([rx_loc])
grav_survey = PF.BaseGrav.LinearSurvey(grav_src_field)

# We can now create a density model and generate data
# Here a simple block in half-space
model = np.zeros((mesh.nCx, mesh.nCy, mesh.nCz))
model[(mid_x - 5) : (mid_x - 1), (mid_y - 2) : (mid_y + 2), -10:-6] = 2.75
model[(mid_x + 1) : (mid_x + 5), (mid_y - 2) : (mid_y + 2), -10:-6] = -1.75
model_vec = Utils.mkvc(model)
model_vec = model_vec[active_cells]

# Mape the active cells from the mesh
active_map = Maps.InjectActiveCells(mesh, active_cells, -100)

# Create reduced identity map
identity_map = Maps.IdentityMap(nP=num_cells)

# Create the forward model operator
grav_fwd = PF.Gravity.GravityIntegral(mesh, rhoMap=identity_map, actInd=active_cells)

## Pair the survey and problem
grav_survey.pair(grav_fwd)

# Compute linear forward operator and compute some data
data = grav_fwd.fields(model_vec)

## Add noise and uncertainties
## We add some random Gaussian noise (1nT)
# data = d + np.random.randn(len(d))*1e-3
# wd = np.ones(len(data))*1e-3  # Assign flat uncertainties
#

# grav_survey.dobs = data
# grav_survey.std = wd
# grav_survey.mtrue = model

im_cb, ax = Utils.PlotUtils.plot2Ddata(rx_loc.locs, data)
plt.colorbar(im_cb)
plt.scatter(X_r, Y_r, marker="o", s=1)

fig = plt.figure()
ax1 = fig.add_subplot(1, 2, 1, aspect="equal")
l = mesh.plotSlice(
    active_map * model_vec, ind=11, ax=ax1, normal="Z", grid=True, clim=(-2, 2)
)
ax2 = fig.add_subplot(1, 2, 2, aspect="equal", sharex=ax1)
l = mesh.plotSlice(
    active_map * model_vec, ax=ax2, normal="Y", grid=True, clim=(-2, 2), ind=mid_x
)
plt.colorbar(l[0])
plt.show()

## Create sensitivity weights from our linear forward operator
# rxLoc = survey.srcField.rxList[0].locs
# wr = np.sum(prob.G**2., axis=0)**0.5
# wr = (wr/np.max(wr))
#
## Create a regularization
# reg = Regularization.Sparse(mesh, indActive=actv, mapping=idenMap)
# reg.cell_weights = wr
# reg.norms = np.c_[0, 0, 0, 0]
#
## Data misfit function
# dmis = DataMisfit.l2_DataMisfit(survey)
# dmis.W = Utils.sdiag(1/wd)
#
## Add directives to the inversion
# opt = Optimization.ProjectedGNCG(maxIter=100, lower=-1., upper=1.,
#                                 maxIterLS=20, maxIterCG=10,
#                                 tolCG=1e-3)
# invProb = InvProblem.BaseInvProblem(dmis, reg, opt)
# betaest = Directives.BetaEstimate_ByEig(beta0_ratio=1e-1)
#
## Here is where the norms are applied
## Use pick a threshold parameter empirically based on the distribution of
## model parameters
# IRLS = Directives.Update_IRLS(
#    f_min_change=1e-4, maxIRLSiter=30, coolEpsFact=1.5, beta_tol=1e-1,
# )
# saveDict = Directives.SaveOutputEveryIteration(save_txt=False)
# update_Jacobi = Directives.UpdatePreconditioner()
# inv = Inversion.BaseInversion(
#    invProb, directiveList=[IRLS, betaest, update_Jacobi, saveDict]
# )
#
## Run the inversion
# m0 = np.ones(nC)*1e-4  # Starting model
# mrec = inv.run(m0)
#
# if plotIt:
#    # Here is the recovered susceptibility model
#    ypanel = midx
#    zpanel = -7
#    m_l2 = actvMap * invProb.l2model
#    m_l2[m_l2 == -100] = np.nan
#
#    m_lp = actvMap * mrec
#    m_lp[m_lp == -100] = np.nan
#
#    m_true = actvMap * model
#    m_true[m_true == -100] = np.nan
#
#    vmin, vmax = mrec.min(), mrec.max()
#
#    # Plot the data
#    Utils.PlotUtils.plot2Ddata(rxLoc, data)
#
#    plt.figure()
#
#    # Plot L2 model
#    ax = plt.subplot(321)
#    mesh.plotSlice(m_l2, ax=ax, normal='Z', ind=zpanel,
#                   grid=True, clim=(vmin, vmax))
#    plt.plot(([mesh.vectorCCx[0], mesh.vectorCCx[-1]]),
#             ([mesh.vectorCCy[ypanel], mesh.vectorCCy[ypanel]]), color='w')
#    plt.title('Plan l2-model.')
#    plt.gca().set_aspect('equal')
#    plt.ylabel('y')
#    ax.xaxis.set_visible(False)
#    plt.gca().set_aspect('equal', adjustable='box')
#
#    # Vertical section
#    ax = plt.subplot(322)
#    mesh.plotSlice(m_l2, ax=ax, normal='Y', ind=midx,
#                   grid=True, clim=(vmin, vmax))
#    plt.plot(([mesh.vectorCCx[0], mesh.vectorCCx[-1]]),
#             ([mesh.vectorCCz[zpanel], mesh.vectorCCz[zpanel]]), color='w')
#    plt.title('E-W l2-model.')
#    plt.gca().set_aspect('equal')
#    ax.xaxis.set_visible(False)
#    plt.ylabel('z')
#    plt.gca().set_aspect('equal', adjustable='box')
#
#    # Plot Lp model
#    ax = plt.subplot(323)
#    mesh.plotSlice(m_lp, ax=ax, normal='Z', ind=zpanel,
#                   grid=True, clim=(vmin, vmax))
#    plt.plot(([mesh.vectorCCx[0], mesh.vectorCCx[-1]]),
#             ([mesh.vectorCCy[ypanel], mesh.vectorCCy[ypanel]]), color='w')
#    plt.title('Plan lp-model.')
#    plt.gca().set_aspect('equal')
#    ax.xaxis.set_visible(False)
#    plt.ylabel('y')
#    plt.gca().set_aspect('equal', adjustable='box')
#
#    # Vertical section
#    ax = plt.subplot(324)
#    mesh.plotSlice(m_lp, ax=ax, normal='Y', ind=midx,
#                   grid=True, clim=(vmin, vmax))
#    plt.plot(([mesh.vectorCCx[0], mesh.vectorCCx[-1]]),
#             ([mesh.vectorCCz[zpanel], mesh.vectorCCz[zpanel]]), color='w')
#    plt.title('E-W lp-model.')
#    plt.gca().set_aspect('equal')
#    ax.xaxis.set_visible(False)
#    plt.ylabel('z')
#    plt.gca().set_aspect('equal', adjustable='box')
#
#    # Plot True model
#    ax = plt.subplot(325)
#    mesh.plotSlice(m_true, ax=ax, normal='Z', ind=zpanel,
#                   grid=True, clim=(vmin, vmax))
#    plt.plot(([mesh.vectorCCx[0], mesh.vectorCCx[-1]]),
#             ([mesh.vectorCCy[ypanel], mesh.vectorCCy[ypanel]]), color='w')
#    plt.title('Plan true model.')
#    plt.gca().set_aspect('equal')
#    plt.xlabel('x')
#    plt.ylabel('y')
#    plt.gca().set_aspect('equal', adjustable='box')
#
#    # Vertical section
#    ax = plt.subplot(326)
#    mesh.plotSlice(m_true, ax=ax, normal='Y', ind=midx,
#                   grid=True, clim=(vmin, vmax))
#    plt.plot(([mesh.vectorCCx[0], mesh.vectorCCx[-1]]),
#             ([mesh.vectorCCz[zpanel], mesh.vectorCCz[zpanel]]), color='w')
#    plt.title('E-W true model.')
#    plt.gca().set_aspect('equal')
#    plt.xlabel('x')
#    plt.ylabel('z')
#    plt.gca().set_aspect('equal', adjustable='box')
#
#    # Plot convergence curves
#    fig, axs = plt.figure(), plt.subplot()
#    axs.plot(saveDict.phi_d, 'k', lw=2)
#    axs.plot(
#        np.r_[IRLS.iterStart, IRLS.iterStart],
#        np.r_[0, np.max(saveDict.phi_d)], 'k:'
#    )
#
#    twin = axs.twinx()
#    twin.plot(saveDict.phi_m, 'k--', lw=2)
#    axs.text(
#        IRLS.iterStart, np.max(saveDict.phi_d)/2.,
#        'IRLS Steps', va='bottom', ha='center',
#        rotation='vertical', size=12,
#        bbox={'facecolor': 'white'}
#    )
#
#    axs.set_ylabel('$\phi_d$', size=16, rotation=0)
#    axs.set_xlabel('Iterations', size=14)
#    twin.set_ylabel('$\phi_m$', size=16, rotation=0)
#
# plt.show()
#
##if __name__ == '__main__':
##    run()
##    plt.show()
