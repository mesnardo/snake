# file: plotGridConvergence.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Plots the grid-convergence for the 2d lid-driven cavity case.


import os
import sys
import argparse

import numpy
from matplotlib import pyplot
pyplot.style.use('{}/styles/mesnardo.mplstyle'.format(os.environ['SCRIPTS']))

sys.path.append(os.environ['SCRIPTS'])
from library import miscellaneous
from library.simulation import Simulation


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
                      type=str, choices=['petibm', 'cuibm'],
                      help='software used to compute the flows.')
  parser.add_argument('--sizes', dest='gridline_sizes',
                      type=str, nargs='+', default=[],
                      help='list of simulation sub-folders')
  parser.add_argument('--time-step', '-ts', dest='time_step', 
                      type=int,
                      help='time-step at which the solution will be read')
  parser.add_argument('--fields', dest='field_names',
                      type=str, nargs='+',
                      default=['x-velocity', 'y-velocity', 'pressure'],
                      help='list of fields to consider '
                           '(x-velocity, y-velocity, and/or pressure)')
  parser.add_argument('--save-name', dest='save_name',
                      type=str, default=None,
                      help='Name of the .png file to save')
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
  parser.add_argument('--analytical-plug', dest='analytical_plug',
                      type=str, nargs='+',
                      default=[],
                      help='class name followed by parameters required '
                           'to initialize the object')
  parser.set_defaults(show=True, last_three=False, binary=False)
  # parse given options file
  parser.add_argument('--options', 
                      type=open, action=miscellaneous.ReadOptionsFromFile,
                      help='path of the file with options to parse')
  # return namespace
  return parser.parse_args()


def observed_order_convergence(field_name, coarse, medium, fine, ratio, grid):
  """Computes the observed order of convergence  (L2-norm)
  using the solution on three consecutive grids with constant refinement ratio.

  Parameters
  ----------
  field_name: string
    Name of the field.
  coarse, medium, fine: Field objects
    Solutions on three consecutive grids restricted on the coarsest grid.
  ratio: float
    Grid-refinement ratio.
  grid: list of numpy arrays of floats
    Nodal stations in each direction used to restrict a solution.

  Returns
  -------
  alpha: float
    The observed order of convergence.
  """
  # get restricted field from coarse solution
  coarse_field = getattr(coarse, field_name.replace('-', '_')).restriction(grid)
  # get restricted field from medium solution
  medium_field = getattr(medium, field_name.replace('-', '_')).restriction(grid)
  # get restricted field from fine solution
  fine_field = getattr(fine, field_name.replace('-', '_')).restriction(grid)
  # observed order using the L2-norm
  return (  numpy.log(  numpy.linalg.norm(  medium_field.values
                                          - coarse_field.values  ) 
                      / numpy.linalg.norm(  fine_field.values
                                          - medium_field.values  )  )
          / numpy.log(ratio)  )


def get_observed_orders_convergence(simulations, field_names,
                                    last_three=False,
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
  last_three: boolean
    Set 'True' to compute the orders using the three finest grid; default: False.
  directory: string
    Shared path of case directories; default: current directory.
  save_name: string
    Name of the .dat file to write into; default: None (does not write).

  Returns
  -------
  alpha: dictionary of floats
    Contains the observed order of convergence for each variable.
  """
  label = ('last three' if last_three else 'first three')
  print('[info] computing observed orders of '
        'convergence using the {} grids...'.format(label))
  coarse, medium, fine = (simulations[-3:] if last_three else simulations[:2])
  ratio = coarse.get_grid_spacing()/medium.get_grid_spacing()
  alpha = {} # will contain observed order of convergence
  for field_name in field_names:
    # get grid (coarsest one) where solutions will be restricted
    grid = [getattr(simulations[0], field_name.replace('-', '_')).x, 
            getattr(simulations[0], field_name.replace('-', '_')).y]
    alpha[field_name] = observed_order_convergence(field_name, 
                                                   coarse, medium, fine, 
                                                   ratio, grid)
    print('\t{}: {}'.format(field_name, alpha[field_name]))
  print('')
  if save_name:
    print('[info] writing orders into .dat file ...')
    label = ('lastThree' if last_three else 'firstThree')
    file_path = '{}/{}_{}.dat'.format(directory, save_name, label)
    with open(file_path, 'w') as outfile:
      for field_name in field_names:
        outfile.write('{}: {}\n'.format(field_name, alpha[field_name]))
  return alpha


def plot_grid_convergence(simulations, field_names,
                          directory=os.getcwd(), save_name=None, show=False):
  """Plots the grid-convergence in a log-log figure.

  Parameters
  ----------
  simulations: list of Simulation objects
    List of the cases.
  field_names: list of strings
    Names of the fields to include in the figure.
  directory: string
    Shared path of all cases; default: current directory.
  save_name: string
    Name of the .png file to save; default: None (does not save).
  show: boolean
    Set 'True' if you want to display the figure; default: False. 
  """
  print('[info] plotting the grid convergence ...')
  fig, ax = pyplot.subplots(figsize=(6, 6))
  ax.grid(False)
  ax.set_xlabel('grid-spacing')
  ax.set_ylabel('$L_2$-norm error')
  for field_name in field_names:
    ax.plot([case.get_grid_spacing() for case in simulations],
            [getattr(case, 'errors')[field_name.replace('-', '_')] 
             for case in simulations],
            label=field_name, marker='o')
  # plot convergence-guides for first and second-orders
  h = numpy.linspace(1.0E-05, 1.0E+05, 101)
  ax.plot(h, h/max(value for value in simulations[0].errors.itervalues()), 
          label='$1^{st}$-order convergence', color='k')
  ax.plot(h, h**2/min(value for value in simulations[0].errors.itervalues()), 
          label='$2^{nd}$-order convergence', color='k', linestyle='--')
  ax.legend()
  ax.set_xlim(0.1*simulations[-1].get_grid_spacing(), 
              10.0*simulations[0].get_grid_spacing())
  ax.set_ylim(0.1*min(getattr(case, 'errors')[field_name.replace('-', '_')] 
                      for case in simulations 
                      for field_name in field_names),
              10.0*max(getattr(case, 'errors')[field_name.replace('-', '_')] 
                       for case in simulations 
                       for field_name in field_names))
  pyplot.xscale('log')
  pyplot.yscale('log')
  # save and display
  if save_name:
    print('[info] saving figure ...')
    images_directory = '{}/images'.format(directory)
    if not os.path.isdir(images_directory):
      print('[info] creating images directory: {} ...'.format(images_directory))
      os.makedirs(images_directory)
    pyplot.savefig('{}/{}.png'.format(images_directory, save_name))
  if show:
    print('[info] displaying figure ...')
    pyplot.show()


def main():
  """Computes the observed orders of convergence 
  of the velocity components and the pressure using three solutions 
  with consecutive grid-refinement.
  Plots the grid convergence.
  """
  args = parse_command_line()

  # get solution of simulations at given time-step
  simulations = []
  for gridline_size in args.gridline_sizes:
    simulation = Simulation(directory='{}/{}'.format(args.directory, gridline_size),
                            software=args.software)
    simulation.read_grid()
    simulation.read_fields(args.field_names, args.time_step,
                           periodic_directions=args.periodic_directions)
    simulations.append(simulation)

  get_observed_orders_convergence(simulations, args.field_names,
                                  last_three=args.last_three,
                                  directory=args.directory,
                                  save_name=args.save_name)

  # analytical solution
  if args.analytical_plug:
    import analytical
    AnalyticalClass = analytical.dispatcher[args.analytical_plug[0]]
    # compute the analytical solution on finest grid
    exact = AnalyticalClass(simulations[-1].grid, *args.analytical_plug[1:])
  else:
    exact = simulations[-1] # assume finest grid contains exact solution if no analytical solution
    del simulations[-1]

  # compute relative differences using L2-norm
  for index, simulation in enumerate(simulations):
    simulations[index].get_relative_differences(exact, simulations[0],
                                                field_names=args.field_names) 
  
  plot_grid_convergence(simulations, args.field_names,
                        directory=args.directory, 
                        save_name=args.save_name, 
                        show=args.show)


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))