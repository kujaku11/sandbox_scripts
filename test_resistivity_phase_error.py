# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 10:01:28 2024

@author: jpeacock
"""

# =============================================================================
# Imports
# =============================================================================

# =============================================================================
import numpy as np


def calculate_apparent_resistivity_phase_error(Z, delta_Z, period):
    # Constants
    a = 0.2 * period
    # Permeability of free space
    # Calculate apparent resistivity
    rho_a = np.abs(Z) ** 2 * a
    # Partial derivatives for error propagation
    d_rhoa_dZ = 2 * np.abs(Z) * a
    d_rhoa_dperiod = 0
    # Calculate apparent resistivity error
    delta_rho_a = np.sqrt(
        (d_rhoa_dZ * delta_Z) ** 2 + (d_rhoa_dperiod * period) ** 2
    )
    # Calculate phase angle
    phase_angle = np.rad2deg(np.angle(Z))
    # Partial derivatives for phase error
    d_phi_dReZ = -np.imag(Z) / np.real(Z) ** 2
    d_phi_dImZ = 1 / np.real(Z)
    # Calculate phase error
    delta_phi = np.rad2deg(
        1
        / (1 + (np.imag(Z) / np.real(Z)) ** 2)
        * np.sqrt(
            (d_phi_dReZ * delta_Z.real) ** 2 + (d_phi_dImZ * delta_Z.imag) ** 2
        )
    )
    return rho_a, delta_rho_a, phase_angle, delta_phi


# Example usage
Z = 10 + 5j
# Impedance (complex number)
delta_Z = 0.1
# Impedance error (complex number)
period = 1.0
# Period
(
    rho_a,
    delta_rho_a,
    phase_angle,
    delta_phi,
) = calculate_apparent_resistivity_phase_error(Z, delta_Z, period)
print("Apparent Resistivity:", rho_a)
print("Apparent Resistivity Error:", delta_rho_a)
print("Phase Angle:", phase_angle)
print("Phase Error:", delta_phi)
