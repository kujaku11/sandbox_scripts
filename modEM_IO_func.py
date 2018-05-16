import os
import numpy as np
import datetime

import vtk
from vtk.util import numpy_support as npsup

import discretize
import SimPEG as simpeg


def read_modem_models(model_file, ref_loc):
    '''
    Function to read in ModEM models into SimPEG/VTK

    Inputs:
        model_file - path to the modEM model file
        ref_loc - xyz reference location for the model and
        	mesh has to be in a metric reference frame

    Returns:
    	(mesh, mod_dict) - tuple containing the mesh and a model dict
    		with resistivity model.
    '''
    # Note: using UTM xyz convention

    # Read all the lines
    file_lines = np.genfromtxt(model_file, dtype=str, delimiter='\n')

    # Make the mesh
    nr_y, nr_x, nr_z, temp, val_type = file_lines[0].split()
    hy = np.array(file_lines[1].split(), float)[::-1]
    hx = np.array(file_lines[2].split(), float)
    hz = np.array(file_lines[3].split(), float)[::-1]

    # Calculate the SimPEG reference (SW - bottom point)
    x0 = ref_loc - np.array([np.sum(hx) / 2., np.sum(hy) / 2., np.sum(hz)])

    mesh = discretize.TensorMesh([hx, hy, hz], x0)

    # Read the model
    nr_mod_lines = int(nr_x) * int(nr_z)
    mod_modem_convention = np.concatenate(
        [np.array(line.split(), float)
         for line in file_lines[4:4 + nr_mod_lines]])
    mod_mat = mod_modem_convention.reshape(
        int(nr_y), int(nr_x), int(nr_z), order='F')[::-1, :, ::-1]
    mod_mat = np.transpose(mod_mat, (1, 0, 2))
    mod_vec = simpeg.mkvc(np.exp(mod_mat))

    # Write the vtk model
    mesh.writeVTK(model_file.split('.')[0] + '.vtr', {'Ohm*m': mod_vec})

    # Return the SimPEG mesh and model
    return (mesh, {'Ohm*m': mod_vec})
