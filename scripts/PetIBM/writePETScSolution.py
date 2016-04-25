# file: createInitialPETScSolution.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Creates the initial solution and write in a PETSc-readable format.

import sys
import os
import argparse

import numpy

from snake import miscellaneous


def parse_command_line():
  """Parses the command-line."""
  print('[info] parsing the command-line ...'),
  # create parser
  parser = argparse.ArgumentParser(description='Creates and writes initial fields '
                                               'in PETSc-readable files',
                        formatter_class= argparse.ArgumentDefaultsHelpFormatter)
  # fill parser with arguments
  parser.add_argument('--directory', dest='directory', 
                      type=str, default=os.getcwd(), 
                      help='directory of the simulation')
  # arguments about grid
  parser.add_argument('--bottom-left', '-bl', dest='bottom_left', 
                      type=float, nargs=2, 
                      default=[float('-inf'), float('-inf')],
                      metavar=('x', 'y'),
                      help='coordinates of the bottom-left corner of the view')
  parser.add_argument('--top-right', '-tr', dest='top_right', 
                      type=float, nargs=2, 
                      default=[float('inf'), float('inf')],
                      metavar=('x', 'y'),
                      help='coordinates of the top-right corner of the view')
  parser.add_argument('--n', '-n', dest='n_cells',
                      type=int, nargs=2,
                      metavar=('nx', 'ny'),
                      help='number of cells in each direction')
  parser.add_argument('--periodic', dest='periodic_directions',
                      type=str, nargs='+', 
                      default=[],
                      help='list of directions with periodic boundary conditions')
  parser.add_argument('--solution', dest='solution',
                      type=str, nargs='+',
                      default=None,
                      help='class name followed by parameters required '
                           'to write the fields into PETSc-readable files')
  # parse given options file
  parser.add_argument('--options', 
                      type=open, action=miscellaneous.ReadOptionsFromFile,
                      help='path of the file with options to parse')
  print('done')
  # parse command-line
  return parser.parse_args()


def main(args):
  """Creates the initial velocity field on a staggered grid.
  Converts the velocity components into fluxes.
  Writes the fluxes and the pressure (zeros) into files.
  """
  # create nodal stations along each direction
  grid = [numpy.linspace(args.bottom_left[i], args.top_right[i], args.n_cells[i]+1) 
          for i in range(len(args.n_cells))]
  from library.solutions.dispatcher import dispatcher
  SolutionClass = dispatcher[args.solution[0]]
  arguments = grid + args.solution[1:]
  solution = SolutionClass(*arguments)
  solution.write_fields_petsc_format(*arguments,
                                     periodic_directions=args.periodic_directions,
                                     directory=args.directory)


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  args = parse_command_line()
  main(args)
  print('\n[{}] END\n'.format(os.path.basename(__file__)))