# -*- coding: utf-8 -*-
"""
Created on Fri Nov 18 11:19:40 2016

@author: jpeacock
"""
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
import numpy as np
import mtpy.modeling.modem_new as modem

model_obj = modem.Model()
model_obj.read_model_file(r"c:\Users\jpeacock\Documents\Geothermal\Washington\MSH\inversions\mshn_avg_all.rho")

fig = plt.figure(1)
ax = mplot3d.Axes3D(fig)

# Face 1
x1 = np.array([[0, 1, 1, 0, 0],
               [0, 0, 0, 0, 0]])
y1 = np.array([[0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0]])
z1 = np.array([[0, 0, 1, 1, 0],
               [0, 0, 0, 0, 0]])
# Face 2
x2 = np.array([[0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0]])
y2 = np.array([[0, 1, 1, 0, 0],
               [0, 0, 0, 0, 0]])
z2 = np.array([[0, 0, 1, 1, 0],
               [0, 0, 0, 0, 0]])
# Face 3
x3 = np.array([[0, 1, 1, 0, 0],
               [0, 0, 0, 0, 0]])
y3 = np.array([[0, 0, 1, 1, 0],
               [0, 0, 0, 0, 0]])
z3 = np.array([[1, 1, 1, 1, 1],
               [1, 1, 1, 1, 1]])
# Face 4
x4 = np.array([[0, 1, 1, 0, 0],
               [0, 0, 0, 0, 0]])
y4 = np.array([[1, 1, 1, 1, 1],
               [1, 1, 1, 1, 1]])
z4 = np.array([[0, 0, 1, 1, 0],
               [0, 0, 0, 0, 0]])
# Face 5
x5 = np.array([[0, 0, 1, 1, 0],
               [0, 0, 0, 0, 0]])
y5 = np.array([[0, 1, 1, 0, 0],
               [0, 0, 0, 0, 0]])
z5 = np.array([[0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0]])
# Face 6
x6 = np.array([[1, 1, 1, 1, 1],
               [1, 1, 1, 1, 1]])
y6 = np.array([[0, 1, 1, 0, 0],
               [0, 0, 0, 0, 0]])
z6 = np.array([[0, 0, 1, 1, 0],
               [0, 0, 0, 0, 0]])


ax.plot_surface(x1,y1,z1)
ax.plot_surface(x2,y2,z2)
ax.plot_surface(x3,y3,z3)
ax.plot_surface(x4,y4,z4)
ax.plot_surface(x5,y5,z5)
ax.plot_surface(x6,y6,z6)

plt.show()
