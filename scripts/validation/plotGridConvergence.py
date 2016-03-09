# file: plotGridConvergence.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Plots the grid-convergence for the 2d lid-driven cavity case.


import os
import sys
import argparse
import collections

import numpy
from matplotlib import pyplot
pyplot.style.use('{}/styles/mesnardo.mplstyle'.format(os.environ['SCRIPTS']))

sys.path.append(os.environ['SCRIPTS'])
from library import miscellaneous
from library.simulation import Simulation
from library.field import Field


def parse_command_line():
  """Parses the command-line."""
  # create parser
  parser = argparse.ArgumentParser(description='Convergence for the '
                                               'lid-driven cavity case',
                        formatter_class= argparse.ArgumentDefaultsHelpFormatter)
  # fill parser with arguments
  parser.add_argument('--directory', dest='directory', 
                      type=str,
                      default=os.getcwd(),
                      help='directory containing the simulation folders')
  parser.add_argument('--software', dest='software',
                      type=str, 
                      choices=['petibm', 'cuibm'],
                      help='software used to compute the flows.')
  parser.add_argument('--sizes', dest='gridline_sizes',
                      type=str, nargs='+', 
                      default=[],
                      help='list of simulation sub-folders')
  parser.add_argument('--mask', dest='mask',
                      type=str,
                      help='size of the gridline used as a mask')
  parser.add_argument('--observed-order', dest='observed_order',
                      action='append', nargs=3, type=str,
                      help='ordered 3-list of simulations used to estimate '
                           'the order of convergence')
  parser.add_argument('--time-step', '-ts', dest='time_step', 
                      type=int,
                      help='time-step at which the solution will be read')
  parser.add_argument('--fields', dest='field_names',
                      type=str, nargs='+',
                      default=['pressure', 'x-velocity', 'y-velocity'],
                      help='list of fields to consider '
                           '(x-velocity, y-velocity, and/or pressure)')
  parser.add_argument('--norms', dest='norms',
                      type=str, nargs='+', 
                      choices=['L2', 'Linf'],
                      default=['L2'],
                      help='norms used to compute the errors')
  parser.add_argument('--save-name', dest='save_name',
                      type=str, 
                      default=None,
                      help='name of the .png file to save')
  parser.add_argument('--no-show', dest='show', 
                      action='store_false',
                      help='does not display the figure')
  parser.add_argument('--last-three', dest='last_three',
                      action='store_true',
                      help='uses the three finest grids to compute '
                           'the observed order of convergence')
  parser.add_argument('--periodic', dest='periodic_directions',
                      type=str, nargs='+',
                      default=[],
                      help='PetIBM: directions with periodic boundary conditions')
  parser.add_argument('--analytical-solution', dest='analytical_solution',
                      type=str, nargs='+',
                      default=[],
                      help='class name followed by parameters required '
                           'to initialize the object')
  parser.add_argument('--plot-analytical-solution', dest='plot_analytical_solution',
                      action='store_true',
                      help='plots the analytical fields')
  parser.add_argument('--bottom-left', '-bl', dest='bottom_left',
                      type=float, nargs=2,
                      default=None,
                      metavar=('x', 'y'),
                      help='bottom-left corner of the domain')
  parser.add_argument('--top-right', '-tr', dest='top_right',
                      type=float, nargs=2,
                      default=None,
                      metavar=('x', 'y'),
                      help='top-right corner of the domain')
  parser.set_defaults(show=True, last_three=False, binary=False)
  # parse given options file
  parser.add_argument('--options', 
                      type=open, action=miscellaneous.ReadOptionsFromFile,
                      help='path of the file with options to parse')
  # return namespace
  return parser.parse_args()


def get_observed_orders_convergence(simulations, field_names, mask,
                                    directory=os.getcwd(),
                                    save_name=None):
  """Computes the observed orders of convergence 
  for the velocity components and pressure using the solution 
  on three consecutive grids.

  Parameters
  ----------
  simulations: list of Simulation objects
    Contains the simulations.
  field_names: list of strings
    List of field names whose observed order of convergence will be computed.
  mask: Simulation object
    Simulation whose grids are used as a mask.
  directory: string, optional
    Shared path of case directories; default: current directory.
  save_name: string, optional
    Name of the .dat file to write into; default: None (does not write).

  Returns
  -------
  alpha: dictionary of floats
    Contains the observed order of convergence for each variable.
  """
  print('[info] computing observed orders of '
        'convergence using the grids {} ...'.format([case.description for case in simulations]))
  coarse, medium, fine = simulations
  ratio = coarse.get_grid_spacing()/medium.get_grid_spacing()
  alpha = {} # will contain observed order of convergence
  for field_name in field_names:
    # get grid (coarsest one) where solutions will be restricted
    attribute_name = field_name.replace('-', '_')
    grid = [getattr(mask, attribute_name).x, getattr(mask, attribute_name).y]
    alpha[field_name], asymptotic = observed_order_convergence(field_name, 
                                                               coarse, medium, fine, 
                                                               ratio, grid)
    asymptotic.plot_contour(field_range=(0.0, 2.0, 101), 
                            view=[coarse.grid[0][0], coarse.grid[1][0],
                                  coarse.grid[0][-1], coarse.grid[1][-1]],
                            directory='{}/images/gci/{}_{}_{}'.format(directory,
                                                                      coarse.description,
                                                                      medium.description,
                                                                      fine.description))
  if save_name:
    print('[info] writing orders into .dat file ...')
    time_step = getattr(mask, attribute_name).time_step
    file_path = '{}/{}_{}_{}_{}_{:0>7}.dat'.format(directory, 
                                                   save_name, 
                                                   coarse.description,
                                                   medium.description,
                                                   fine.description, 
                                                   time_step)
    with open(file_path, 'w') as outfile:
      for field_name in field_names:
        outfile.write('{}: {}\n'.format(field_name, alpha[field_name]))
  return alpha


def main():
  """Computes the observed orders of convergence 
  of the velocity components and the pressure using three solutions 
  with consecutive grid-refinement.
  Plots the grid convergence.
  """
  args = parse_command_line()

  simulations = collections.OrderedDict()
  for size in args.gridline_sizes:
    simulations[size] = Simulation(directory='{}/{}'.format(args.directory, size),
                                   description=size,
                                   software=args.software)
    simulations[size].read_grid()
    simulations[size].read_fields(args.field_names, args.time_step,
                                  periodic_directions=args.periodic_directions)

  for sizes in args.observed_order:
    alpha = get_observed_orders_convergence([simulations[size] for size in sizes], 
                                            args.field_names, 
                                            simulations[args.mask],
                                            directory=args.directory+'/data',
                                            save_name=args.save_name)
    for field_name in alpha.iterkeys():
      asymptotic_range = get_asym  
    asymptotic.plot_contour(field_range=(0.0, 2.0, 101), 
                            view=[coarse.grid[0][0], coarse.grid[1][0],
                                  coarse.grid[0][-1], coarse.grid[1][-1]],
                            directory='{}/images/gci/{}_{}_{}'.format(directory,
                                                                      coarse.description,
                                                                      medium.description,
                                                                      fine.description))


  exact = get_exact_solution(simulations, *args.analytical_solution)
  if args.plot_analytical_solution:
    exact.plot_fields(args.time_step, 
                      view=args.bottom_left+args.top_right, 
                      directory=args.directory)
  
  plot_grid_convergence(simulations, exact, 
                        mask=simulations[args.mask], 
                        field_names=args.field_names,
                        norms=args.norms,
                        directory=args.directory,
                        save_name=args.save_name,
                        show=args.show)


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))