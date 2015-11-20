#!/usr/bin/env python

# file: plotCenterlineVelocitiesLidDrivenCavity2d.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Plots the centerline velocities for lid-driven cavity flow case
#              and compare with experimental data from Ghia et al. (1982).


import os
import sys
import argparse

import numpy
from matplotlib import pyplot


def parse_command_line():
  """Parses the command-line."""
  print('[info] parsing the command-line ...'),
  # create parser
  parser = argparse.ArgumentParser(description='Plots centerline velocities '
                                               'for lid-driven cavity flow',
                        formatter_class= argparse.ArgumentDefaultsHelpFormatter)
  # fill parser with arguments
  parser.add_argument('--directory', dest='directory', 
                      type=str, default=os.getcwd(),
                      help='directory of the simulation')
  parser.add_argument('--type', dest='simulation_type',
                      type=str,
                      help='type of simulation (petibm or cuibm)')
  parser.add_argument('--re', '-re', dest='Re', 
                      type=float, default='100',
                      help='Reynolds number of the flow')
  parser.add_argument('--time-step', '-ts', dest='time_step', 
                      type=int, default=None,
                      help='time-step to plot')
  parser.add_argument('--validation-data', dest='validation_data_path',
                      type=str, 
                      default=('{}/resources/validationData/'
                               'ghia_et_al_1982_lid_driven_cavity.dat'.format(os.environ['SCRIPTS'])),
                      help='path of the validation data file')
  parser.add_argument('--no-show', dest='show',
                      action='store_false',
                      help='does not display the figures')
  parser.add_argument('--save-name', dest='save_name',
                      type=str, default=None,
                      help='shared saving file name')
  parser.set_defaults(show=True)
  # parse given options file
  class LoadFromFile(argparse.Action):
    """Container to read parameters from file."""
    def __call__(self, parser, namespace, values, option_string=None):
      """Fills the namespace with parameters read in file."""
      with values as f:
        parser.parse_args(f.read().split(), namespace)
  parser.add_argument('--file', 
                      type=open, action=LoadFromFile,
                      help='path of the file with options to parse')
  print('done')
  return parser.parse_args()


def sanity_checks(args):
  """Performs some checks on the command-line arguments.

  Parameters
  ----------
  args: Namespace
    Namespace containing the command-line arguments.
  """
  sain = True
  if not os.path.isdir(args.directory):
    print('[error] {} is not a directory'.format(args.directory)); sain = False
  elif not os.path.isfile(args.validation_data_path):
    print('[error] {} is not a file'.format(args.validation_data_path)); sain = False
  elif args.time_step and not(os.path.isdir('{}/{:0>7}'.format(args.directory, args.time_step))):
    print('[error] {} is not a saved time-step'); sain = False
  elif args.simulation_type not in ['petibm', 'cuibm']:
    print('[error] wrong simulation type'); sain = False
  if not sain:
    sys.exit()


def get_validation_data(path, Re):
  """Gets the validation data.

  Parameters
  ----------
  path: string
    Path of the file containing the validation data.
  Re: float
    Reynolds number of the simulation.
  """
  Re = str(int(round(Re)))
  # column indices in file with experimental results
  cols = {'100'  : {'u': 1, 'v': 7},
          '1000' : {'u': 2, 'v': 8},
          '3200' : {'u': 3, 'v': 9},
          '5000' : {'u': 4, 'v': 10},
          '10000': {'u': 5, 'v': 11}}

  with open(path, 'r') as infile:
    y, u = numpy.loadtxt(infile, dtype=float, usecols= (0, cols[Re]['u']), unpack=True)
  with open(path, 'r') as infile:
    x, v = numpy.loadtxt(infile, dtype=float, usecols= (6, cols[Re]['v']), unpack=True)
  return {'y': y, 'u': u, 'x': x, 'v': v}

def plot_centerline_velocities(u, v, grid, validation_data, 
                               directory=os.getcwd(), save_name=None, 
                               show=False):
  """Plots the centerline velocities and compares to experimental results
  from Ghia et al. (1982).

  Parameters
  ----------
  u, v: instances of class Field
    x- and y- velocity fields.
  grid: lists of floats
    x- and y-coordinates along a grid-line of the Cartesian structured mesh.
  directory: string
    Directory of the simulation; default: $PWD.
  save_name: string
    Common name of files to save; default: None (does not save the figures).
  show: bool
    Displays the figures; default: False.
  """
  nx, ny = grid[0].size-1, grid[1].size-1
  images_directory = '{}/images'.format(directory)
  if save_name and not os.path.isdir(images_directory):
    os.makedirs(images_directory)
  pyplot.style.use('{}/styles/mesnardo.mplstyle'.format(os.environ['SCRIPTS']))
  kwargs_data = {'label': 'PetIBM',
                 'color': '#336699', 'linestyle': '-', 'linewidth': 2,
                 'zorder': 10}
  kwargs_validation_data = {'label': 'Ghia et al. (1982)',
                            'color': '#993333', 'linewidth': 0,
                            'markeredgewidth': 2, 'markeredgecolor': '#993333',
                            'markerfacecolor': 'none',
                            'marker': 'o', 'markersize': 4,
                            'zorder': 10}

  print('[info] plotting the u-velocity along vertical centerline ...'),
  fig, ax = pyplot.subplots(figsize=(6, 6))
  ax.grid(True, zorder=0)
  ax.set_xlabel('y-coordinate')
  ax.set_ylabel('u-velocity along vertical centerline')
  u_centerline = (u.values[:, nx/2] if nx%2 == 0 
                  else 0.5*(u.values[:, nx/2-1]+u.values[:, nx/2+1]))
  ax.plot(u.y, u_centerline, **kwargs_data)
  ax.plot(validation_data['y'], validation_data['u'], **kwargs_validation_data)
  ax.axis([0.0, 1.0, -0.75, 1.25])
  ax.legend()
  if save_name:
    pyplot.savefig('{}/{}_uCenterline{:0>7}.png'.format(images_directory, 
                                                        save_name, 
                                                        u.time_step))
    data_path = '{}/{}_uCenterline{:0>7}.dat'.format(images_directory, 
                                                     save_name, 
                                                     u.time_step)
    with open(data_path, 'w') as outfile:
      numpy.savetxt(outfile, numpy.c_[u.y, u_centerline], 
                    fmt='%.6f', delimiter='\t',
                    header='u-velocity along vertical centerline')
  if show:
    pyplot.show()
  print('done')
  print('[info] plotting the v-velocity along horizontal centerline ...'),
  fig, ax = pyplot.subplots(figsize=(6, 6))
  ax.grid(True, zorder=0)
  ax.set_xlabel('x-coordinate')
  ax.set_ylabel('v-velocity along horizontal centerline')
  v_centerline = (v.values[ny/2, :] if ny%2 == 0 
                  else 0.5*(v.values[ny/2-1, :]+v.values[ny/2+1, :]))
  ax.plot(v.x, v_centerline, **kwargs_data)
  ax.plot(validation_data['x'], validation_data['v'], **kwargs_validation_data)
  ax.axis([0.0, 1.0, -0.75, 1.25])
  ax.legend()
  if save_name:
    pyplot.savefig('{}/{}_vCenterline{:0>7}.png'.format(images_directory, 
                                                        save_name, 
                                                        v.time_step))
    data_path = '{}/{}_vCenterline{:0>7}.dat'.format(images_directory, 
                                                     save_name, 
                                                     v.time_step)
    with open(data_path, 'w') as outfile:
      numpy.savetxt(outfile, numpy.c_[u.y, u_centerline], 
                    fmt='%.6f', delimiter='\t',
                    header='v-velocity along horizonatal centerline')
  if show:
    pyplot.show()
  print('done')


def main():
  """Plots and writes the velocity components at the centerline of the cavity
  and compares with experimental results form Ghia et al. (1982).
  """
  args = parse_command_line()
  sanity_checks(args)
  if args.simulation_type == 'cuibm':
    sys.path.append('{}/scripts/cuIBM'.format(os.environ['SCRIPTS']))
    import ioCuIBM as io
  elif args.simulation_type == 'petibm':
    sys.path.append('{}/scripts/PetIBM'.format(os.environ['SCRIPTS']))
    import ioPetIBM as io

  if not args.time_step:
    args.time_step = io.get_time_steps(args.directory)[-1]
  
  print('[info] simulation: {}'.format(args.directory))
  print('[info] time-step: {}'.format(args.time_step))
  print('[info] Reynolds number: {}'.format(args.Re))

  grid = io.read_grid(args.directory)
  u, v = io.read_velocity(args.directory, args.time_step, grid)

  validation_data = get_validation_data(args.validation_data_path, args.Re)

  if args.save_name or args.show:
    plot_centerline_velocities(u, v, grid, validation_data, 
                               directory=args.directory, save_name=args.save_name, 
                               show=args.show)


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))