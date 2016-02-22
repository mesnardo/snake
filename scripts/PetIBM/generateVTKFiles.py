# file: generateVTKFiles.py
# author: Olivier Mesnard (mesnardo@gwu.edu), Anush Krishnan (anush@bu.edu)
# description: Converts PETSc output to .vtk format.


import os
import argparse

import numpy

from ..library.simulation import Simulation


def parse_command_line():
  """Parses the command-line."""
  # create parser
  parser = argparse.ArgumentParser(description='Converts PETSc output to VTK '
                                               'format for 3D case',
                        formatter_class= argparse.ArgumentDefaultsHelpFormatter)
  # fill parser with arguments
  parser.add_argument('--directory', dest='directory', 
                      type=str, 
                      default=os.getcwd(), 
                      help='directory of the simulation')
  parser.add_argument('--fields', dest='field_names', 
                      type=str, nargs='+', 
                      default=['velocity', 'pressure'],
                      help='list of fields to generate')
  parser.add_argument('--bottom-left', '-bl', dest='bottom_left', 
                      type=float, nargs='+', 
                      default=[float('-inf'), float('-inf'), float('-inf')],
                      help='coordinates of the bottom-left corner')
  parser.add_argument('--top-right', '-tr', dest='top_right', 
                      type=float, nargs='+', 
                      default=[float('inf'), float('inf'), float('inf')],
                      help='coordinates of the top-right corner')
  parser.add_argument('--time-steps', '-t', dest='time_steps', 
                      type=int, nargs='+', 
                      default=[],
                      help='time-steps to convert (start, end, increment)')
  parser.add_argument('--stride', '-s', dest='stride', 
                      type=int, 
                      default=1,
                      help='stride at which vector are written')
  parser.add_argument('--periodic', dest='periodic_directions', 
                      type=str, nargs='+', default=[], 
                      help='direction(s) (x and/or y and/or z) '
                           'with periodic boundary conditions')
  # parse command-line
  return parser.parse_args()


def interpolate_cell_centers(velocity):
  """Interpolates the velocity field at the cell-centers.

  Parameters
  ----------
  velocity: list(ioPetIBM.Field)
    Velocity field on a staggered grid.

  Returns
  -------
  velocity: list(ioPetIBM.Field)
    Velocity field at cell-centers.
  """
  dim3 = (True if len(velocity) == 3 else False)
  x_centers, y_centers = velocity[1].x[1:-1], velocity[0].y[1:-1]
  u, v = velocity[0].values, velocity[1].values
  if dim3:
    z_centers = velocity[0].z[1:-1]
    w = velocity[2].values
    u = 0.5*(u[1:-1, 1:-1, :-1] + u[1:-1, 1:-1, 1:])
    v = 0.5*(v[1:-1, :-1, 1:-1] + v[1:-1:, 1:, 1:-1])
    w = 0.5*(w[:-1, 1:-1, 1:-1] + w[1:, 1:-1, 1:-1])
    # tests
    assert (z_centers.size, y_centers.size, x_centers.size) == u.shape
    assert (z_centers.size, y_centers.size, x_centers.size) == v.shape
    assert (z_centers.size, y_centers.size, x_centers.size) == w.shape
    return [ioPetIBM.Field(x=x_centers, y=y_centers, z=z_centers, values=u),
            ioPetIBM.Field(x=x_centers, y=y_centers, z=z_centers, values=v),
            ioPetIBM.Field(x=x_centers, y=y_centers, z=z_centers, values=w)]
  else:
    u = 0.5*(u[1:-1, :-1] + u[1:-1, 1:])
    v = 0.5*(v[:-1, 1:-1] + v[1:, 1:-1])
    # tests
    assert (y_centers.size, x_centers.size) == u.shape
    assert (y_centers.size, x_centers.size) == v.shape
    return [ioPetIBM.Field(x=x_centers, y=y_centers, values=u),
            ioPetIBM.Field(x=x_centers, y=y_centers, values=v)]


def main():
  """Converts PETSc output to .vtk format."""
  # parse command-line
  args = parse_command_line()

  simulation = Simulation(directory=args.directory, software='petibm')

  time_steps = simulation.get_time_steps(args.case_directory, args.time_steps)

  simulation.read_grid()

  for time_step in time_steps:
    if 'velocity' in args.field_names:
      simulation.read_fields(['x-velocity', 'y-velocity', 'z-velocity'], time_step,
                             periodic_directions=args.periodic_directions)
      # need to get velocity at cell-centers, not staggered arrangement
      simulation.get_velocity_cell_centers()
      simulation.get_velocity_cell_centers('velocity', 
                                           view=[args.bottom_left, args.top_right],
                                           stride=args.stride)
    if 'pressure' in args.field_names:
      simulation.read_fields(['pressure'], time_step)
      simulation.write_vtk('pressure',
                           view=[args.bottom_left, args.top_right],
                           stride=args.stride)


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))