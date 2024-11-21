# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
# =============================================================================

from mtpy import MTCollection

from mtpy_data import (
    FWD_CONDUCTIVE_CUBE_PROFILE_LIST,
    FWD_FAULTS_PROFILE_LIST,
    FWD_LAYERED_HALFSPACE_PROFILE_LIST,
    FWD_NEAR_SURFACE_CONDUCTIVE_CUBE_PROFILE_LIST,
    FWD_RESISTIVE_CUBE_PROFILE_LIST,
    FWD_NE_CONDUCTOR_PROFILE_LIST,
    FWD_NE_FAULTS_PROFILE_LIST,
)

with MTCollection() as mc:
    mc.open_collection(
        r"c:\Users\jpeacock\OneDrive - DOI\Documents\GitHub\iris-mt-course-2022\data\transfer_functions\forward_profiles.h5"
    )

    mc.add_tf(FWD_CONDUCTIVE_CUBE_PROFILE_LIST, new_survey="conductive_cube")
    mc.add_tf(FWD_FAULTS_PROFILE_LIST, new_survey="faults")
    mc.add_tf(
        FWD_LAYERED_HALFSPACE_PROFILE_LIST, new_survey="layered_halfspace"
    )
    mc.add_tf(
        FWD_NEAR_SURFACE_CONDUCTIVE_CUBE_PROFILE_LIST,
        new_survey="near_surface_conductor",
    )
    mc.add_tf(FWD_RESISTIVE_CUBE_PROFILE_LIST, new_survey="resistive_cube")
    mc.add_tf(FWD_NE_CONDUCTOR_PROFILE_LIST, new_survey="ne_conductor")
    mc.add_tf(FWD_NE_FAULTS_PROFILE_LIST, new_survey="ne_faults")
