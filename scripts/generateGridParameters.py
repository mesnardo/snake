# file: generateGridParameters.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Generates the cartesianMesh.yaml file for stretched grids.


import argparse
import sys
import os
import re
import math

from .library import miscellaneous


def parse_command_line():
  """Parses the command-line with module argparse."""
  # create parser
  parser = argparse.ArgumentParser(description='Generates cartesianMesh.yaml '
                                               'file for a uniform region '
                                               'surrounded by a stretched grid',
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  # fill parser with arguments
  parser.add_argument('--directory', dest='directory',
                      type=str, default=os.getcwd(),
                      help='directory of the simulation')
  parser.add_argument('--bottom-left', '-bl', dest='bottom_left',
                      type=float, nargs='+',
                      help='position of the bottom-left corner of the domain')
  parser.add_argument('--top-right', '-tr', dest='top_right',
                      type=float, nargs='+',
                      help='position of the top-right corner of the domain')
  parser.add_argument('--bottom-left-uniform', '-blu', dest='bottom_left_uniform',
                      type=float, nargs='+',
                      help='position of the bottom-left corner of the uniform region')
  parser.add_argument('--top-right-uniform', '-tru', dest='top_right_uniform',
                      type=float, nargs='+',
                      help='position of the top-right corner of the uniform region')
  parser.add_argument('--ds', '-ds', dest='ds',
                      type=float, nargs='+',
                      help='cell-widths in the uniform region')
  parser.add_argument('--aspect-ratio', '-ar', dest='aspect_ratio',
                      type=float, nargs='+',
                      help='aspect-ratio between the width of the external '
                           'boundary cells (start and end) '
                           ' and the cell-width in the uniform region '
                           'in each direction between ')

  parser.add_argument('--precision', dest='precision', type=int, default=2,
                      help='precision of the aspect ratio computed')
  parser.add_argument('--save-name', dest='save_name',
                      type=str,
                      default='cartesianMesh.yaml',
                      help='name of the file to create')


  # parse given options file
  parser.add_argument('--options', 
                      type=open, action=miscellaneous.ReadOptionsFromFile,
                      help='path of the file with options to parse')
  # parse command-line
  return parser.parse_args()


class CartesianMesh(object):
  """Contains info related to the stretched grid."""
  def __init__(self):
    self.directions = []

  def add_direction(self, name, regions=[]):
    """Adds information about one direction.

    Parameters
    ----------
    name: string
      Name of the direction ('x', 'y', or 'z').
    regions: list of instances of the classes UniformGridLine or StretchedGridLine
      List containing information about the regions 
      that forms the grid-line along a direction; default: [].
    """
    self.directions.append({'name': name, 'regions': regions})

  def write_yaml_file(self, path='{}/cartesianMesh.yaml'.format(os.getcwd())):
    """Writes the file cartesianMesh.yaml into the simulation directory.

    Parameters
    ----------
    path: string
      Path of the file to write; default: <current directory>/cartesianMesh.yaml.
    """
    print('[info] writing {} ...'.format(path)),
    with open(path, 'w') as outfile:
      outfile.write('# {}\n\n'.format(os.path.basename(path)))
      for direction in self.directions:
        outfile.write('- direction: {}\n'.format(direction['name']))
        outfile.write('  start: {}\n'.format(direction['regions'][0].start))
        outfile.write('  subDomains:\n')
        for region in direction['regions']: 
          outfile.write('    - end: {}\n'.format(region.end))
          outfile.write('      cells: {}\n'.format(region.n))
          outfile.write('      stretchRatio: {}\n'.format(region.stretching_ratio))
        outfile.write('\n')
    print('done')


class UniformGridLine(object):
  """Contains information about a uniform grid-line."""
  def __init__(self, start, end, h):
    """Sets the information about the uniform grid-line.

    Parameters
    ----------
    start: float
      Stating point of the line.
    end: float
      Ending point of the line.
    h: float
      Segment-length used to divide the line.
    """
    self.start, self.end = start, end
    self.length = abs(self.end-self.start)
    self.h = h
    self.n = int(round(self.length/self.h))
    if abs(self.n - self.length/self.h) > 1.0E-08:
      print('Choose a mesh spacing such that the uniform region is an '
            'integral multiple of it')
      sys.exit(1)
    self.stretching_ratio = 1.0


class StretchedGridLine(object):
  """Contains information about a stretched grid-line."""
  def __init__(self, start, end, h, aspect_ratio, precision):
    """Sets information about the stretched grid-line.

    Parameters
    ----------
    start: float
      Stating point of the line.
    end: float
      Ending point of the line.
    h: float
      Segment-length just before the stretched line.
    aspect_ratio: float
      Ratio between the previous segment-length and the biggest segment-length.
    precision: integer
      Number of decimals required to approximate the stretching ratio.
    """
    self.start, self.end = start, end
    self.length = abs(self.end-self.start)
    self.stretching_ratio, self.n = self.compute_ratio(h, aspect_ratio, precision) 

  def compute_ratio(self, h, aspect_ratio, precision):
    """Computes the stretching ratio and number of cells.

    Parameters
    ----------
    h: float
      Segment-length just before the stretched line.
    aspect_ratio: float
      Ratio between the previous segment-length and the biggest segment-length.
    precision: integer
      Number of decimals required to approximate the stretching ratio.

    Returns
    -------
    r: float
      The stretching ratio.
    n: integer
      THe number of segments that composes the grid-line.
    """
    current_precision = 1
    next_ratio = 2.0
    while current_precision <= precision:
      r = next_ratio
      n = int(round(math.log(1.0 - self.length/h*(1.0-r))/math.log(r)))
      ar = r**(n-1)
      if ar < aspect_ratio:
        next_ratio += (0.1)**current_precision
        current_precision += 1
      else:
        next_ratio -= (0.1)**current_precision
    return r, n


def main():
  """Creates cartesianMesh.yaml file for stretched grid."""
  args = parse_command_line()
  mesh = CartesianMesh()

  directions = list(['x', 'y', 'z'])[:len(args.bottom_left)]
  for d, name in enumerate(directions):
    regions = []
    regions.append(StretchedGridLine(args.bottom_left[d], 
                                     args.bottom_left_uniform[d], 
                                     args.ds[d], 
                                     args.aspect_ratio[2*d], 
                                     args.precision))
    regions[-1].stretching_ratio = 1.0/regions[-1].stretching_ratio
    regions.append(UniformGridLine(args.bottom_left_uniform[d],
                                   args.top_right_uniform[d],
                                   args.ds[d]))
    regions.append(StretchedGridLine(args.top_right_uniform[d], 
                                     args.top_right[d], 
                                     args.ds[d], 
                                     args.aspect_ratio[2*d+1], 
                                     args.precision))
    mesh.add_direction(name, regions)

  mesh.write_yaml_file('{}/{}'.format(args.directory, args.save_name))


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))