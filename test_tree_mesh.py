# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 09:40:14 2024

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
import numpy as np
import discretize.utils as dis_utils
from discretize import TreeMesh
from discretize.utils import mkvc

from mtpy.modeling.simpeg.make_2d_mesh import QuadTreeMesh

# =============================================================================

station_locations = np.array(
    [
        np.linspace(0, 50000, 10) + np.random.randint(500, 2000, size=10),
        np.zeros(10),
    ]
).T
frequencies = np.logspace(-3, 3, 9)


# qdtree = QuadTreeMesh(station_locations, frequencies)
qdtree = QuadTreeMesh(
    station_locations,
    frequencies,
    topography=station_locations,
    update_from_stations=True,
    topography_padding=[[0, 1], [0, 1], [0, 5]],
)
ax = qdtree.make_mesh()
# ax = mesh.plot_grid()

# ax.scatter(station_locations[:, 0], station_locations[:, 1], marker="v")
# ax.set_xlim(
#     station_locations[:, 0].min() - 10000, station_locations[:, 0].max() + 10000
# )
# ax.set_ylim(-2500, 500)


# xy = np.array([np.linspace(0, 50000, 10), np.zeros(10)])
# a = dis_utils.mesh_builder_xyz(
#     xy.T,
#     [1000, 10],
#     padding_distance=[[-50000, 100000], [-10000, 50000]],
#     depth_core=50000,
#     mesh_type="tree",
# )
# a.plot_grid()

# dx = 5  # minimum cell width (base mesh cell width) in x
# dy = 5  # minimum cell width (base mesh cell width) in y

# x_length = 300.0  # domain width in x
# y_length = 300.0  # domain width in y

# # Compute number of base mesh cells required in x and y
# nbcx = 2 ** int(np.round(np.log(x_length / dx) / np.log(2.0)))
# nbcy = 2 ** int(np.round(np.log(y_length / dy) / np.log(2.0)))

# # Define the base mesh
# hx = [(dx, nbcx)]
# hy = [(dy, nbcy)]
# mesh = TreeMesh([hx, hy], x0="CC")

# # Refine surface topography
# xx = mesh.nodes_x
# yy = -3 * np.exp((xx**2) / 100**2) + 50.0
# pts = np.c_[mkvc(xx), mkvc(yy)]
# padding = [[0, 2], [0, 2]]
# mesh.refine_surface(pts, padding_cells_by_level=padding, finalize=False)

# # Refine mesh near points
# xx = np.array([0.0, 10.0, 0.0, -10.0])
# yy = np.array([-20.0, -10.0, 0.0, -10])
# pts = np.c_[mkvc(xx), mkvc(yy)]
# mesh.refine_points(pts, padding_cells_by_level=[2, 2], finalize=False)

# mesh.finalize()

# mesh.plot_grid()
