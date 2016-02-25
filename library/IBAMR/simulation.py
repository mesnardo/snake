# file: ibamrSimulation.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Implementation of the class `IBAMRSimulation`.


import os

import numpy

from ..simulation import Simulation
from ..force import Force


class IBAMRSimulation(Simulation):
  """Contains info about a IBAMR simulation.
  Inherits from class Simulation.
  """
  def __init__(self):
    pass

  def read_forces(self, relative_file_path='dataIB/ib_Drag_force_struct_no_0', 
                  display_coefficients=False):
    """Reads forces from files.

    Parameters
    ----------
    relative_file_path: string
      Path (relative to the simulation directory) of the file containing the forces;
      default: 'dataIB/ib_Drag_force_struct_no_0'.
    display_coefficients: boolean
      Set to 'True' if force coefficients are required; 
      default: False (i.e. forces).
    """
    forces_path = '{}/{}'.format(self.directory, relative_file_path)
    print('[info] reading forces from {} ...'.format(forces_path)),
    with open(forces_path, 'r') as infile:
      times, force_x, force_y = numpy.loadtxt(infile, dtype=float, 
                                              usecols=(0, 4, 5), unpack=True)
    self.force_x = Force(times, force_x)
    self.force_y = Force(times, force_y)
    print('done')