# file: plotCenterlineVelocitiesLidDrivenCavity2d.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Plots the centerline velocities for lid-driven cavity flow case
#              and compares with experimental data from Ghia et al. (1982).


import os
import sys
import argparse

import numpy
from matplotlib import pyplot

from snake import miscellaneous
from snake.simulation import Simulation
from snake.field import Field


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
                               'ghia_et_al_1982_lid_driven_cavity.dat'.format(os.environ['SNAKE'])),
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
  return ( Field(y=y, values=u, label='x-velocity'), 
           Field(x=x, values=v, label='y-velocity') )


def main(args):
  """Plots and writes the velocity components at the centerline of the cavity
  and compares with experimental results form Ghia et al. (1982).
  """
  # register simulation
  simulation = Simulation(directory=args.directory, 
                          software=args.software)
  
  # get time-step
  if not args.time_step:
    args.time_step = simulation.get_time_steps()[-1]
  
  simulation.read_grid()
  simulation.read_fields(['x-velocity', 'y-velocity'], args.time_step)

  # read validation data from Ghia et al. (1982)
  u, v = get_validation_data(args.validation_data_path, args.Re)

  software_name = {'petibm': 'PetIBM', 'cuibm': 'cuIBM'}
  plot_settings = {'label': software_name[args.software],
                   'color': '#336699', 'linestyle': '-', 'linewidth': 3,
                   'zorder': 10}
  validation_plot_settings = {'label': 'Ghia et al. (1982)',
                              'color': '#993333', 'linewidth': 0,
                              'markeredgewidth': 2, 'markeredgecolor': '#993333',
                              'markerfacecolor': 'none',
                              'marker': 'o', 'markersize': 8,
                              'zorder': 10}

  save_directory = os.path.join(simulation.directory, 'images')
  if not os.path.isdir(save_directory):
    os.makedirs(save_directory)
  simulation.fields['x-velocity'].plot_vertical_gridline_values(0.5,
                              plot_settings=plot_settings,
                              plot_limits=[0.0, 1.0, -0.75, 1.25],
                              save_directory=save_directory,
                              show=args.show,
                              validation_data=(u.y, u.values),
                              validation_plot_settings=validation_plot_settings,
                              style=os.path.join(os.environ['SNAKE'],
                                                 'snake', 
                                                 'styles', 
                                                 'mesnardo.mplstyle'))
  simulation.fields['y-velocity'].plot_horizontal_gridline_values(0.5,
                              plot_settings=plot_settings,
                              plot_limits=[0.0, 1.0, -0.75, 1.25],
                              save_directory=save_directory,
                              show=args.show,
                              validation_data=(v.x, v.values),
                              validation_plot_settings=validation_plot_settings,
                              style=os.path.join(os.environ['SNAKE'],
                                                 'snake', 
                                                 'styles', 
                                                 'mesnardo.mplstyle'))


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  args = parse_command_line()
  main(args)
  print('\n[{}] END\n'.format(os.path.basename(__file__)))