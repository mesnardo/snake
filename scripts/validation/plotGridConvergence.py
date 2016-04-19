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

from snake import miscellaneous
from snake import convergence
from snake.simulation import Simulation
from snake.field import Field


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
  parser.add_argument('--plot-asymptotic-ranges', dest='plot_asymptotic_ranges',
                      action='store_true',
                      help='computes the GCI and plots the asymptotic ranges')
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


def main(args):
  """Grid convergence study.
  Computes the observed order of convergence using the solution on three 
  consecutive grids with constant grid refinement.
  Computes the Grid Convergence Index and plots the asymptotic ranges.
  Plots the log-log error versus grid-spacing.
  """
  # read numerical solutions
  simulations = collections.OrderedDict()
  for size in args.gridline_sizes:
    simulations[size] = Simulation(directory='{}/{}'.format(args.directory, size),
                                   description=size,
                                   software=args.software)
    simulations[size].read_grid()
    simulations[size].read_fields(args.field_names, args.time_step,
                                  periodic_directions=args.periodic_directions)

  for sizes in args.observed_order:
    alpha = convergence.get_observed_orders([simulations[size] for size in sizes], 
                                            args.field_names, 
                                            simulations[args.mask],
                                            directory=args.directory+'/data')
    if args.plot_asymptotic_ranges:
      convergence.plot_asymptotic_ranges([simulations[size] for size in sizes],
                                         alpha,
                                         simulations[args.mask],
                                         directory=args.directory+'/images')

  exact = convergence.get_exact_solution(simulations, args.mask, *args.analytical_solution)
  if args.plot_analytical_solution:
    exact.plot_fields(args.time_step, 
                      view=args.bottom_left+args.top_right, 
                      directory=args.directory+'/images')
  
  convergence.plot_grid_convergence(simulations.values(), exact, 
                                    mask=simulations[args.mask], 
                                    field_names=args.field_names,
                                    norms=args.norms,
                                    directory=args.directory+'/images',
                                    save_name=args.save_name,
                                    show=args.show)


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  args = parse_command_line()
  main(args)
  print('\n[{}] END\n'.format(os.path.basename(__file__)))