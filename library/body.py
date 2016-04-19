# file: Body.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Implementation of the class `Body`.


import numpy


class Body(object):
  """Contains information about an immersed body."""
  def __init__(self, file_path, label=None):
    """Reads the body coordinates from given file.

    Parameters
    ----------
    path: string
      Path of the file containing the body coordinates.
    label: string, optional
      Label of the body;
      default: None.
    """
    self.label = label
    self.file_path = file_path
    self.x, self.y = self.read_coordinates()

  def read_coordinates(self):
    """Reads the coordinates from file."""
    print('[info] reading body coordinates from file {} ...'.format(self.file_path))
    with open(self.file_path, 'r') as infile:
      return numpy.loadtxt(infile, dtype=float, skiprows=1, unpack=True)