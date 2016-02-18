# file: plotGridConvergence.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Plots the grid-convergence for the 2d lid-driven cavity case.


import os
import sys
import argparse
import numpy
from matplotlib import pyplot
pyplot.style.use('{}/styles/mesnardo.mplstyle'.format(os.environ['SCRIPTS']))

sys.path.append('{}/scripts/library'.format(os.environ['SCRIPTS']))
import miscellaneous


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
  parser.add_argument('--periodic', dest='periodic',
                      type=str, nargs='+',
                      default=[],
                      help='PetIBM: list of directions with periodic boundary conditions')
  parser.add_argument('--binary', dest='binary',
                      action='store_true',
                      help='cuIBM: use flag if data written in binary format')
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


def restriction(field, grid):
  """Restriction of the field solution onto a coarser grid.
  Note: all nodes on the coarse grid are present in the fine grid.

  Parameters
  ----------
  field: Field object
    Field where solution will be restricted.
  grid: list of numpy array of floats
    Nodal stations in each direction of the coarser grid.

  Returns
  -------
  restricted_field: Field
    Field restricted onto the coarser grid.
  """
  def intersection(a, b, tolerance=1.0E-06):
    return numpy.any(numpy.abs(a-b[:, numpy.newaxis]) <= tolerance, axis=0)
  mask_x = intersection(field.x, grid[0])
  mask_y = intersection(field.y, grid[1])
  restricted_field = Field()
  restricted_field.x = field.x[mask_x]
  restricted_field.y = field.y[mask_y]
  restricted_field.values = numpy.array([field.values[j][mask_x]
                                       for j in xrange(field.y.size)
                                       if mask_y[j]])
  return restricted_field


# fake class Field (just used as a container)
class Field(object):
  def __init__(self):
    pass


class SimulationSolution(object):
  def __init__(self, directory, time_step, software, periodic=[], binary=False):
    """Reads the solution of a simulation at a given time-step.

    Parameters
    ----------
    directory: string
      Directory of the simulation.
    time_step: integer
      Time-step at which the solution is read.
    software: string
      Software used to compute the solution (currently supported: 'petibm', 'cuibm').
    periodic: list of strings
      Only supported from PetIBM solutions.
      List of directions with periodic boundary conditions; default: [].
    binary: boolean
      Only supported for cuIBM solutions. 
      Set 'True' if solution written in binary format; default: False.
    """
    # import appropriate library depending on software used
    if software == 'cuibm':
      sys.path.append('{}/scripts/cuIBM'.format(os.environ['SCRIPTS']))
      import ioCuIBM as io
    elif software == 'petibm':
      sys.path.append('{}/scripts/PetIBM'.format(os.environ['SCRIPTS']))
      import ioPetIBM as io
    print('[info] registering solution ...')
    print('\t- directory: {}'.format(directory))
    print('\t- software: {}'.format(software))
    print('\t- time-step: {}'.format(time_step))
    self.directory = directory
    self.time_step = time_step
    self.grid = io.read_grid(self.directory, binary=binary)
    self.grid_spacing = self.get_grid_spacing()
    self.u, self.v = io.read_velocity(self.directory, self.time_step, self.grid, 
                                      periodic=periodic, binary=binary)
    self.p = io.read_pressure(self.directory, self.time_step, self.grid, binary=binary)

  def get_grid_spacing(self):
    """Returns the grid-spacing of a uniform grid."""
    return (self.grid[0][-1]-self.grid[0][0])/(self.grid[0].size-1)

  def compute_errors(self, exact, reference):
    """Computes the errors (relative to an exact solution) in the L2-norm.

    Parameters
    ----------
    exact: SimulationSolution object
      The 'exact' solution used as reference.
    reference: SimulationSolution object
      Solution used as a reference for the grids.
    """
    field_names = ['u', 'v', 'p']
    for field_name in field_names:
      grid = [getattr(reference, field_name).x, getattr(reference, field_name).y]
      field = restriction(getattr(self, field_name), grid)
      exact_field = restriction(getattr(exact, field_name), grid)
      error = (  numpy.linalg.norm(field.values- exact_field.values)
               / numpy.linalg.norm(exact_field.values)  )
      setattr(getattr(self, field_name), 'error', error)


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
  coarse_field = restriction(getattr(coarse, field_name), grid)
  # get restricted field from medium solution
  medium_field = restriction(getattr(medium, field_name), grid)
  # get restricted field from fine solution
  fine_field = restriction(getattr(fine, field_name), grid)
  # observed order using the L2-norm
  return (  numpy.log(  numpy.linalg.norm(  medium_field.values
                                          - coarse_field.values  ) 
                      / numpy.linalg.norm(  fine_field.values
                                          - medium_field.values  )  )
          / numpy.log(ratio)  )


def get_observed_orders_convergence(cases,
                                    last_three=False,
                                    directory=os.getcwd(),
                                    save_name=None):
  """Computes the observed orders of convergence 
  for the velocity components and pressure using the solution 
  on three consecutive grids.

  Parameters
  ----------
  cases: list of SimulationSolution objects
    List containing the three cases.
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
  coarse, medium, fine = (cases[1:] if last_three else cases[:-1])
  ratio = coarse.grid_spacing/medium.grid_spacing
  field_names = ['u', 'v', 'p']
  alpha = {} # will contain observed order of convergence
  for field_name in field_names:
    grid = [getattr(cases[0], field_name).x, getattr(cases[0], field_name).y]
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


def plot_grid_convergence(cases, 
                          directory=os.getcwd(), save_name=None, show=False):
  """Plots the grid-convergence in a log-log figure.

  Parameters
  ----------
  cases: list of SimulationSolution objects
    List of the cases.
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
  field_names = ['u', 'v', 'p']
  for field_name in field_names:
    ax.plot([case.grid_spacing for case in cases],
            [getattr(case, field_name).error for case in cases],
            label=field_name, marker='o')
  # plot convergence-guides for first and second-orders
  h = numpy.linspace(1.0E-05, 1.0E+05, 101)
  ax.plot(h, h/max(cases[0].u.error, cases[0].p.error, cases[0].p.error), 
          label='$1^{st}$-order convergence', color='k')
  ax.plot(h, h**2/min(cases[0].u.error, cases[0].p.error, cases[0].p.error), 
          label='$2^{nd}$-order convergence', color='k', linestyle='--')
  ax.legend()
  ax.set_xlim(0.1*cases[-1].grid_spacing, 10.0*cases[0].grid_spacing)
  ax.set_ylim(0.1*min([getattr(case, field_name).error for case in cases for field_name in field_names]),
              10.0*max([getattr(case, field_name).error for case in cases for field_name in field_names]))
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
  cases = []
  for gridline_size in args.gridline_sizes:
    cases.append(SimulationSolution('{}/{}'.format(args.directory, gridline_size),
                                    args.time_step, args.software, 
                                    periodic=args.periodic, binary=args.binary))

  get_observed_orders_convergence(cases, 
                                  last_three=args.last_three,
                                  directory=args.directory,
                                  save_name=args.save_name)

  # analytical solution
  if args.analytical_plug:
    import analytical
    AnalyticalClass = analytical.dispatcher[args.analytical_plug[0]]
    exact = AnalyticalClass(cases[-1].grid, *args.analytical_plug[1:])
  else:
    exact = cases[-1] # assume finest grid contains exact solution if no analytical solution
    del cases[-1]

  # compute L2-norm errors
  for index, case in enumerate(cases):
    cases[index].compute_errors(exact, cases[0])

  # save and display error vs. grid-spacing
  if args.save_name or args.show:
    plot_grid_convergence(cases, 
                          directory=args.directory, 
                          save_name=args.save_name, 
                          show=args.show)


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))