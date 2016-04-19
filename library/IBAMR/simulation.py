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
    super(IBAMRSimulation, self).__init__(description=description, 
                                          directory=directory, 
                                          software='ibamr', 
                                          **kwargs)

  def read_forces(self, file_path=None, labels=None):
    """Reads forces from files.

    Parameters
    ----------
    relative_file_path: string
      Path of the file containing the forces;
      default: None.
    labels: list of strings, optional
      Label of each force to read;
      default: None.
    """
    if not file_path:
      file_path = '{}/dataIB/ib_Drag_force_struct_no_0'.format(self.directory)
    print('[info] reading forces from {} ...'.format(forces_path)),
    with open(forces_path, 'r') as infile:
      times, force_x, force_y = numpy.loadtxt(infile, dtype=float, 
                                              usecols=(0, 4, 5), unpack=True)
    self.forces.append(Force(times, force_x, '$F_x$'))
    self.forces.append(Force(times, force_y, '$F_y$'))
    print('done')