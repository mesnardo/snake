# file: openfoamSimulation.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Implementation of the class `OpenFOAMSimulation`.


import os

import numpy

from ..simulation import Simulation
from ..force import Force


class OpenFOAMSimulation(Simulation):
  """Contains info about a OpenFOAM simulation.
  Inherits from class Simulation.
  """
  def __init__(self, description=None, directory=os.getcwd(), **kwargs):
    """Initializes by calling the parent constructor.

    Parameters
    ----------
    description: string, optional
      Description of the simulation;
      default: None.
    directory: string, optional
      Directory of the simulation;
      default: present working directory.
    """
    super(OpenFOAMSimulation, self).__init__(description=description, 
                                             directory=directory, 
                                             software='openfoam', 
                                             **kwargs)

  def read_forces(self, display_coefficients=False, labels=None):
    """Reads forces from files.

    Parameters
    ----------
    display_coefficients: boolean, optional
      Set to 'True' if force coefficients are required; 
      default: False (i.e. forces).
    labels: list of strings, optional
      Label of each force to read;
      default: None.
    """
    if display_coefficients:
      info = {'directory': '{}/postProcessing/forceCoeffs'.format(self.directory),
              'description': 'force-coefficients'}
      if not labels:
        labels = ['$C_d$', '$C_l$']
    else:
      info = {'directory': '{}/postProcessing/forces'.format(self.directory),
              'description': 'forces'}
      if not labels:
        labels = ['$F_x$', '$F_y$']
    info['usecols'] = (0, 2, 3)
    info['labels'] = labels
    # backward compatibility from 2.2.2 to 2.0.1
    if not os.path.isdir(info['directory']):
      info['directory'] = '{}/forces'.format(self.directory)
      info['usecols'] = (0, 1, 2)
    # end of backward compatibility
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
    # set Force objects
    self.forces.append(Force(times, force_x, label=labels[0]))
    self.forces.append(Force(times, force_y, label=labels[1]))