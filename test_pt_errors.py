# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 14:11:43 2023

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================
import numpy as np
from mtpy.core import PhaseTensor

# =============================================================================
z = np.array([[0.1 - 1j, 2 + 1j], [-10 - 5j, 0.5 + 0.3j]])
z_error = np.array([[0.1, 0.05], [0.05, 0.1]])

pt = PhaseTensor(z=z, z_error=z_error)

z_real = np.real(z)
z_imag = np.imag(z)
det_real = np.linalg.det(z_real)

print(pt.pt_error)

# pt_err_array = np.zeros((2, 2))
# pt_error[:, 0, 0] = (
#     (
#         np.abs(-pt_array[:, 0, 0] * z_real[:, 1, 1] * z_error[:, 0, 0])
#         + np.abs(pt_array[:, 0, 0] * z_real[:, 0, 1] * z_error[:, 1, 0])
#         + np.abs(
#             (z_imag[:, 0, 0] - pt_array[:, 0, 0] * z_real[:, 0, 0])
#             * z_error[:, 1, 1]
#         )
#         + np.abs(
#             (-z_imag[:, 1, 0] + pt_array[:, 0, 0] * z_real[:, 1, 0])
#             * z_error[:, 0, 1]
#         )
#         + np.abs(z_real[:, 1, 1] * z_error[:, 0, 0])
#         + np.abs(z_real[:, 0, 1] * z_error[:, 1, 0])
#     ) / det_real
# )

# pt_error[:, 0, 1] = (
#  (
#         np.abs(-pt_array[:, 0, 1] * z_real[:, 1, 1] * z_error[:, 0, 0])
#         + np.abs(pt_array[:, 0, 1] * z_real[:, 0, 1] * z_error[:, 1, 0])
#         + np.abs(
#             (z_imag[:, 0, 1] - pt_array[:, 0, 1] * z_real[:, 0, 0])
#             * z_error[:, 1, 1]
#         )
#         + np.abs(
#             (-z_imag[:, 1, 1] + pt_array[:, 0, 1] * z_real[:, 1, 0])
#             * z_error[:, 0, 1]
#         )
#         + np.abs(z_real[:, 1, 1] * z_error[:, 0, 1])
#         + np.abs(z_real[:, 0, 1] * z_error[:, 1, 1])
#     ) / det_real
# )

# pt_error[:, 1, 0] = (
# (
#         np.abs(
#             (z_imag[:, 1, 0] - pt_array[:, 1, 0] * z_real[:, 1, 1])
#             * z_error[:, 0, 0]
#         )
#         + np.abs(pt_array[:, 1, 0] * z_real[:, 1, 0] * z_error[:, 0, 1])
#         + np.abs(
#             (-z_imag[:, 0, 0] + pt_array[:, 1, 0] * z_real[:, 0, 1])
#             * z_error[:, 1, 0]
#         )
#         + np.abs(-pt_array[:, 1, 0] * z_real[:, 0, 0] * z_error[:, 1, 1])
#         + np.abs(z_real[:, 0, 0] * z_error[:, 1, 0])
#         + np.abs(-z_real[:, 1, 0] * z_error[:, 0, 0])
#     ) / det_real
# )

# pt_error[:, 1, 1] = (
# (
#         np.abs(
#             (z_imag[:, 1, 1] - pt_array[:, 1, 1] * z_real[:, 1, 1])
#             * z_error[:, 0, 0]
#         )
#         + np.abs(pt_array[:, 1, 1] * z_real[:, 1, 0] * z_error[:, 0, 1])
#         + np.abs(
#             (-z_imag[:, 0, 1] + pt_array[:, 1, 1] * z_real[:, 0, 1])
#             * z_error[:, 1, 0]
#         )
#         + np.abs(-pt_array[:, 1, 1] * z_real[:, 0, 0] * z_error[:, 1, 1])
#         + np.abs(z_real[:, 0, 0] * z_error[:, 1, 1])
#         + np.abs(-z_real[:, 1, 0] * z_error[:, 0, 1])
#     ) / det_real
# )

# print(pt_err_array / 2)
