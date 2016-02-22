# file: plotCenterlineVelocitiesLidDrivenCavity2d.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Plots the centerline velocities for lid-driven cavity flow case
#              and compares with experimental data from Ghia et al. (1982).


import os
import sys
import argparse

import numpy
from matplotlib import pyplot

from ..library import miscellaneous
from ..library.field import Field


def parse_command_line():
  """Parses the command-line."""
  print('[info] parsing the command-line ...'),
  # create parser
  parser = argparse.ArgumentParser(description='Plots centerline velocities '
                                               'for lid-driven cavity flow',
                        formatter_class= argparse.ArgumentDefaultsHelpFormatter)
  # fill parser with arguments
  parser.add_argument('--directory', dest='directory', 
                      type=str, 
                      default=os.getcwd(),
                      help='directory of the simulation')
  parser.add_argument('--software', dest='software',
                      type=str, 
                      choices=['petibm', 'cuibm'],
                      help='software used for the simulation')
  parser.add_argument('--re', '-re', dest='Re', 
                      type=float, 
                      choices=[100, 1000, 3200, 5000],
                      help='Reynolds number of the flow')
  parser.add_argument('--time-step', '-ts', dest='time_step', 
                      type=int, 
                      default=None,
                      help='time-step to plot')
  parser.add_argument('--validation-data', dest='validation_data_path',
                      type=str, 
                      default=('{}/resources/validationData/'
                               'ghia_et_al_1982_lid_driven_cavity.dat'.format(os.environ['SCRIPTS'])),
                      help='path of the validation data file')
  parser.add_argument('--no-show', dest='show',
                      action='store_false',
                      help='does not display the figures')
  parser.set_defaults(show=True)
  # parse given options file
  parser.add_argument('--options', 
                      type=open, action=miscellaneous.ReadOptionsFromFile,
                      help='path of the file with options to parse')
  print('done')
  # return namespace
  return parser.parse_args()


def get_validation_data(path, Re):
  """Gets the validation data.

  Parameters
  ----------
  path: string
    Path of the file containing the validation data.
  Re: float
    Reynolds number of the simulation.

  Returns
  -------
  d: 2-tuple of Field objects
    Contains stations and velocity values along center-lines 
    (vertical and horizontal).
  """
  Re = str(int(round(Re)))
  # column indices in file with experimental results
  cols = {'100'  : {'u': 1, 'v': 7},
          '1000' : {'u': 2, 'v': 8},
          '3200' : {'u': 3, 'v': 9},
          '5000' : {'u': 4, 'v': 10},
          '10000': {'u': 5, 'v': 11}}

  with open(path, 'r') as infile:
    y, u, x, v = numpy.loadtxt(infile, 
                               dtype=float, 
                               usecols=(0, cols[Re]['u'], 6, cols[Re]['v']),
                               unpack=True)
  return Field(y=y, values=u), Field(x=x, values=v)


def main():
  """Plots and writes the velocity components at the centerline of the cavity
  and compares with experimental results form Ghia et al. (1982).
  """
  args = parse_command_line()
  
  # register simulation
  simulation = Simulation(directory=args.directory, 
                          software=args.software)
  
  # get time-step
  if not args.time_step:
    simulation.get_time_steps()
    args.time_step = simulation.time_steps[-1]
  
  simulation.read_grid()
  simulation.read_fields(['x-velocity', 'y-velocity'], args.time_step)

  # read validation data from Ghia et al. (1982)
  u, v = get_validation_data(args.validation_data_path, args.Re)

  simulation.plot_centerline_velocities(validation_data={'x-velocity': u, 
                                                         'y-velocity': v},
                                        show=args.show)


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))