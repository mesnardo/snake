# file: plotGridConvergence.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Plots the grid-convergence for the 2d lid-driven cavity case.


import os
import sys
import argparse
import math

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
  parser.set_defaults(show=True, last_three=False)
  # parse given options file
  parser.add_argument('--options', 
                      type=open, action=miscellaneous.ReadOptionsFromFile,
                      help='path of the file with options to parse')
  # return namespace
  return parser.parse_args()


def l2_norm(field):
  """Computes the L2-norm of a 2d array

  Parameters
  ----------
  field: 2D Numpy array
    The numerical solution.

  Returns
  -------
  l2: float
    The L2-norm.
  """
  j_start, j_end, j_stride = 0, field.shape[0]+1, 1
  i_start, i_end, i_stride = 0, field.shape[1]+1, 1
  return numpy.linalg.norm(field[j_start:j_end:j_stride, i_start:i_end:i_stride])


def compute_order(ratio, coarse, medium, fine):
  """Computes the observed order of convergence 
  using the solution on three grids.

  Parameters
  ----------
  ratio: float
    Grid-refinement ratio.
  coarse, medium, fine: Numpy array
    Solutions on three consecutive grids restricted on the coarsest grid.

  Returns
  -------
  alpha: float
    The observed order of convergence.
  """
  assert coarse.shape == medium.shape and coarse.shape == fine.shape
  return ( math.log(l2_norm(medium-coarse)/l2_norm(fine-medium))
           / math.log(ratio) )


def restriction(fine, coarse):
  """Restriction of the solution from a fine grid onto a coarse grid.

  Parameters
  ----------
  fine, coarse: ioPetIBM.Field
    Fine and coarse numerical solutions.

  Returns
  -------
  fine_on_coarse: ioPetIBM.Field
    The solution on the fine grid restricted to the coarse grid.
  """
  def intersection(a, b, tolerance=1.0E-06):
    return numpy.any(numpy.abs(a-b[:, numpy.newaxis]) <= tolerance, axis=0)
  mask_x = intersection(fine.x, coarse.x)
  mask_y = intersection(fine.y, coarse.y)
  # fake a class Field
  class Field(object):
    pass
  fine_on_coarse = Field()
  fine_on_coarse.x = fine.x[mask_x]
  fine_on_coarse.y = fine.y[mask_y]
  fine_on_coarse.values = numpy.array([fine.values[j][mask_x]
                                       for j in xrange(fine.y.size)
                                       if mask_y[j]])
  assert numpy.allclose(coarse.x, fine_on_coarse.x, rtol=1.0E-04)
  assert numpy.allclose(coarse.y, fine_on_coarse.y, rtol=1.0E-04)
  assert coarse.values.shape == fine_on_coarse.values.shape
  return fine_on_coarse


class SimulationSolution(object):
  def __init__(self, directory, time_step, software):
    """Reads the solution of a simulation at a given time-step.

    Parameters
    ----------
    directory: string
      Directory of the simulation.
    time_step: integer
      Time-step at which the solution is read.
    software: string
      Software used to compute the solution (currently supported: 'petibm', 'cuibm').
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
    self.grid = io.read_grid(self.directory)
    self.grid_spacing = self.get_grid_spacing()
    self.u, self.v = io.read_velocity(self.directory, self.time_step, self.grid)
    self.p = io.read_pressure(self.directory, self.time_step, self.grid)

  def get_grid_spacing(self):
    """Returns the grid-spacing of a uniform grid."""
    return (self.grid[0][-1]-self.grid[0][0])/(self.grid[0].size-1)

  def compute_error(self, exact):
    """Computes the error (relative to an exact solution) in the L2-norm.

    Parameters
    ----------
    exact: SimulationSolution object
      The 'exact' solution used as reference.
    """
    u_exact_restricted = restriction(exact.u, self.u)
    self.u.error = (l2_norm(self.u.values-u_exact_restricted.values)
                    /l2_norm(u_exact_restricted.values))
    v_exact_restricted = restriction(exact.v, self.v)
    self.v.error = (l2_norm(self.v.values-v_exact_restricted.values)
                    /l2_norm(v_exact_restricted.values))
    p_exact_restricted = restriction(exact.p, self.p)
    self.p.error = (l2_norm(self.p.values-p_exact_restricted.values)
                    /l2_norm(p_exact_restricted.values))
    

def get_observed_orders_convergence(cases,
                                    directory=os.getcwd(),
                                    save_name=None):
  """Computes the observed orders of convergence 
  for the velocity components and pressure using the solution 
  on three consecutive grids.

  Parameters
  ----------
  cases: list of SimulationSolution objects
    List containing the three cases.
  directory: string
    Shared path of case directories; default: current directory.
  save_name: string
    Name of the .dat file to write into; default: None (does not write).

  Returns
  -------
  alpha: dictionary of floats
    Contains the observed order of convergence for each variable.
  """
  print('[info] computing observed orders of convergence ...')
  coarse, medium, fine = cases
  ratio = coarse.grid_spacing/medium.grid_spacing
  alpha = {'u': compute_order(ratio,
                              coarse.u.values,
                              restriction(medium.u, coarse.u).values,
                              restriction(fine.u, coarse.u).values),
           'v': compute_order(ratio,
                              coarse.v.values,
                              restriction(medium.v, coarse.v).values,
                              restriction(fine.v, coarse.v).values),
           'p': compute_order(ratio,
                              coarse.p.values,
                              restriction(medium.p, coarse.p).values,
                              restriction(fine.p, coarse.p).values)}
  print('\n[info] observed orders of convergence:')
  print('\tu: {}'.format(alpha['u']))
  print('\tv: {}'.format(alpha['v']))
  print('\tp: {}'.format(alpha['p']))
  print('')
  if save_name:
    print('[info] writing orders into .dat file ...')
    file_path = '{}/{}.dat'.format(directory, save_name)
    with open(file_path, 'w') as outfile:
      outfile.write('u: {}\n'.format(alpha['u']))
      outfile.write('v: {}\n'.format(alpha['v']))
      outfile.write('p: {}\n'.format(alpha['p']))
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
  # plot errors in u-velocity
  ax.plot([case.grid_spacing for case in cases[:-1]], 
          [case.u.error for case in cases[:-1]], 
          label='u-velocity')
  # plot errors in v-velocity
  ax.plot([case.grid_spacing for case in cases[:-1]], 
          [case.v.error for case in cases[:-1]], 
          label='v-velocity')
  # plot errors in pressure
  ax.plot([case.grid_spacing for case in cases[:-1]], 
          [case.p.error for case in cases[:-1]], 
          label='pressure')
  # plot convergence-guides for first and second-orders
  h = numpy.linspace(cases[0].grid_spacing, cases[-1].grid_spacing, 101)
  ax.plot(h, h, label='$1^{st}$-order convergence', color='k')
  ax.plot(h, h**2, label='$2^{nd}$-order convergence', 
              color='k', linestyle='--')
  ax.legend()
  pyplot.xscale('log')
  pyplot.yscale('log')
  if save_name:
    print('[info] saving figure ...')
    pyplot.savefig('{}/{}.png'.format(directory, save_name))
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
                                    args.time_step, args.software))

  get_observed_orders_convergence((cases[-3:] if args.last_three else cases[:3]), 
                                  directory=args.directory,
                                  save_name=args.save_name)

  # grid convergence, comparison with finest grid
  # assumption: finest grid gives exact solution
  for index, case in enumerate(cases[:-1]):
    cases[index].compute_error(cases[-1])

  if args.save_name or args.show:
    plot_grid_convergence(cases, 
                          directory=args.directory, 
                          save_name=args.save_name, 
                          show=args.show)


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))