# file: openfoamSimulation.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Implementation of the class `OpenFOAMSimulation`.


import os

import numpy

from ..simulation import Simulation
from ..force import Force


class OpenFOAMSimulation(Simulation):
  def __init__(self):
    pass

  def read_forces(self, display_coefficients=False):
    """Reads forces from files.

    Parameters
    ----------
    display_coefficients: boolean
      Set to 'True' if force coefficients are required; default: False (i.e. forces).
    """
    if display_coefficients:
      info = {'directory': '{}/postProcessing/forceCoeffs'.format(self.directory),
              'description': 'force-coefficients',
              'usecols': (0, 2, 3)}
    else:
      info = {'directory': '{}/postProcessing/forces'.format(self.directory),
              'description': 'forces',
              'usecols': (0, 2, 3)}
    # backward compatibility from 2.2.2 to 2.0.1
    if not os.path.isdir(info['directory']):
      info['directory'] = '{}/forces'.format(self.directory)
      info['usecols'] = (0, 1, 2)
    print('[info] reading {} in {} ...'.format(info['description'], info['directory']))
    subdirectories = sorted(os.listdir(info['directory']))
    times = numpy.empty(0)
    force_x, force_y = numpy.empty(0), numpy.empty(0)
    for subdirectory in subdirectories:
      forces_path = '{}/{}/{}.dat'.format(info['directory'], subdirectory, os.path.basename(info['directory']))
      with open(forces_path, 'r') as infile:
        t, fx, fy = numpy.loadtxt(infile, dtype=float, comments='#', 
                                  usecols=info['usecols'], unpack=True)
      times = numpy.append(times, t)
      force_x, force_y = numpy.append(force_x, fx), numpy.append(force_y, fy)
    self.force_x = Force(times, force_x)
    self.force_y = Force(times, force_y)