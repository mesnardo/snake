# file: generateVTKFiles.py
# author: Olivier Mesnard (mesnardo@gwu.edu), Anush Krishnan (anush@bu.edu)
# description: Write numerical field solution into .vtk file.


import os
import sys
import argparse

import numpy

sys.path.append(os.environ['SCRIPTS'])
from library import miscellaneous
from library.simulation import Simulation


def parse_command_line():
  """Parses the command-line."""
  print('[info] parsing the command-line ...'),
  # create parser
  parser = argparse.ArgumentParser(description='Writes field into .vtk file',
                        formatter_class= argparse.ArgumentDefaultsHelpFormatter)
  # fill parser with arguments
  parser.add_argument('--directory', dest='directory', 
                      type=str, 
                      default=os.getcwd(), 
                      help='directory of the simulation')
  parser.add_argument('--software', dest='software',
                      type=str, 
                      choices=['cuibm', 'petibm'],
                      help='Software used to generate numerical solution')
  parser.add_argument('--fields', dest='field_names', 
                      type=str, nargs='+', 
                      default=['velocity', 'pressure'],
                      help='list of fields to generate')
  parser.add_argument('--bottom-left', '-bl', dest='bottom_left', 
                      type=float, nargs='+', 
                      default=[float('-inf'), float('-inf'), float('-inf')],
                      metavar=('x', 'y', 'z'),
                      help='coordinates of the bottom-left corner')
  parser.add_argument('--top-right', '-tr', dest='top_right', 
                      type=float, nargs='+', 
                      default=[float('inf'), float('inf'), float('inf')],
                      metavar=('x', 'y', 'z'),
                      help='coordinates of the top-right corner')
  parser.add_argument('--time-steps', '-ts', dest='time_steps', 
                      type=int, nargs=3, 
                      default=None,
                      metavar=('start', 'end', 'increment'),
                      help='time-steps to convert')
  parser.add_argument('--stride', '-s', dest='stride', 
                      type=int, 
                      default=1,
                      help='stride at which vector are written')
  parser.add_argument('--periodic', dest='periodic_directions', 
                      type=str, nargs='+', 
                      default=[], 
                      help='direction(s) (x and/or y and/or z) '
                           'with periodic boundary conditions')
  # parse given options file
  parser.add_argument('--options', 
                      type=open, action=miscellaneous.ReadOptionsFromFile,
                      help='path of the file with options to parse')
  print('done')
  # return namespace
  return parser.parse_args()


def main(args):
  """Writes the numerical solution into .vtk files."""
  # parse command-line
  simulation = Simulation(directory=args.directory, software=args.software)

  time_steps = simulation.get_time_steps(args.case_directory, args.time_steps)

  simulation.read_grid()

  for time_step in time_steps:
    if 'velocity' in args.field_names:
      simulation.read_fields(['x-velocity', 'y-velocity', 'z-velocity'], time_step,
                             periodic_directions=args.periodic_directions)
      # need to get velocity at cell-centers, not staggered arrangement
      simulation.get_velocity_cell_centers()
      simulation.write_vtk('velocity', 
                           view=[args.bottom_left, args.top_right],
                           stride=args.stride)
    if 'pressure' in args.field_names:
      simulation.read_fields(['pressure'], time_step)
      simulation.write_vtk('pressure',
                           view=[args.bottom_left, args.top_right],
                           stride=args.stride)


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  args = parse_command_line()
  main(args)
  print('\n[{}] END\n'.format(os.path.basename(__file__)))