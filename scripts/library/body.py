# file: Body.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Implementation of the class `Body`.


class Body(object):
  """Contains information about an immersed body."""
  def __init__(self, path):
    """Reads the body coordinates from given file.

    Parameters
    ----------
    path: string
      Path of the file containing the body coordinates.
    """
    self.path = path
    self.x, self.y = self.read_coordinates()

  def read_coordinates(self):
    """Reads the coordinates from file."""
    with open(self.path, 'r') as infile:
      return numpy.loadtxt(infile, dtype=float, skiprows=1, unpack=True)