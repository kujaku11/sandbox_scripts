#!/usr/bin/env python

from setuptools import setup

setup(name='science-base-automation',
      version='0.1',
      description='Automatically create and populate ScienceBase pages with metadata and data files based on standards at USGS Woods Hole Coastal and Marine Science Center.',
      author='Emily Sturdivant',
      author_email='esturdivant@usgs.gov',
      url='https://github.com/esturdivant-usgs/science-base-automation',
      packages=[],
      python_requires='~=3.3',
      install_requires=['lxml'],
     )
