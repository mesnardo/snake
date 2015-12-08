#!/usr/bin/python

# file: plotForces.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Plots the instantaneous forces or force coefficients.


import os
import sys
import argparse

sys.path.append('{}/scripts/library'.format(os.environ['SCRIPTS']))
import forces


def parse_command_line():
  """Parses the command-line."""
  # create parser
  parser = argparse.ArgumentParser(description='Plots the instantaneous forces',
                        formatter_class= argparse.ArgumentDefaultsHelpFormatter)
  # fill parser with arguments
  parser.add_argument('--directory', dest='directory', 
                      type=str, default=os.getcwd(), 
                      help='directory of the simulation')
  parser.add_argument('--description', dest='description',
                      type=str, default=None,
                      help='quick description of the simulation')
  parser.add_argument('--software', '--type', dest='software',
                      type=str,
                      help='software used for simulation '
                           '(openfoam, cuibm, petibm, ibamr)')
  parser.add_argument('--display-coefficients', dest='display_coefficients',
                      action='store_true',
                      help='flag to plot the force coefficients, not the forces')
  parser.add_argument('--coefficient', dest='coefficient',
                      type=float, default=1.0,
                      help='force to force coefficient converter')
  # comparison with other simulations
  parser.add_argument('--others', dest='others',
                      nargs='+', default=[],
                      help='Other simulations used for comparison. '
                           'For each supplemental simulation, provides the following: '
                           'type, directory, description, coefficient')
  # plotting parameters
  parser.add_argument('--average', dest='average_limits', 
                      type=float, nargs='+', default=[0.0, float('inf')],
                      help='temporal limits to consider to average forces')
  parser.add_argument('--average-last', dest='last_period', 
                      action='store_true',
                      help='averages forces over the last period')
  parser.add_argument('--strouhal', dest='n_periods_strouhal',
                      type=int, default=0, 
                      help='computes the Strouhal number based on lift history '
                           'and over a given number of last periods')
  parser.add_argument('--no-show', dest='show', 
                      action='store_false',
                      help='does not display the figure')
  parser.add_argument('--save-name', dest='save_name', 
                      type=str, default=None,
                      help='name of the figure of save')
  parser.add_argument('--limits', dest='plot_limits', 
                      type=float, nargs='+', default=[None, None, None, None],
                      help='limits of the plot')
  parser.add_argument('--no-drag', dest='display_drag', 
                      action='store_false',
                      help='does not display the force in the x-direction')
  parser.add_argument('--no-lift', dest='display_lift', 
                      action='store_false',
                      help='does not display the force in the y-direction')
  parser.add_argument('--extrema', dest='display_extrema', 
                      action='store_true',
                      help='displays the forces extrema')
  parser.add_argument('--order', dest='order', 
                      type=int, default=5,
                      help='number of side-points used for comparison to get extrema')
  parser.add_argument('--gauge', dest='display_gauge', 
                      action='store_true',
                      help='display gauges to check the convergence')
  # default options
  parser.set_defaults(display_drag=True, display_lift=True, show=True)
  # parse given options file
  class LoadFromFile(argparse.Action):
    """Container to read parameters from file."""
    def __call__(self, parser, namespace, values, option_string=None):
      """Fills the namespace with parameters read in file."""
      with values as infile:
        lines = [element for line in infile.readlines()
                 for element in line.strip().split()
                 if not line.startswith('#')]
        parser.parse_args(lines, namespace)
  parser.add_argument('--options', 
                      type=open, action=LoadFromFile,
                      help='path of the file with options to parse')

  # return namespace
  return parser.parse_args()


def main():
  """Plots the instantaneous force coefficients."""
  args = parse_command_line()
  simulations = []
  # register main simulation
  simulations.append(forces.Simulation(description=args.description, 
                                       directory=args.directory,
                                       software=args.software,
                                       coefficient=args.coefficient))
  # register other simulations used for comparison
  keys = ['software', 'directory', 'description', 'coefficient']
  for values in zip(*[iter(args.others)]*len(keys)):
    other = dict(zip(keys, values))
    simulations.append(forces.Simulation(description=other['description'], 
                                         directory=other['directory'],
                                         software=other['software'],
                                         coefficient=float(other['coefficient'])))

  # read and compute some statistics
  for index, simulation in enumerate(simulations):
    simulations[index].read_forces(display_coefficients=args.display_coefficients)
    simulation.get_means(limits=args.average_limits, 
                         last_period=args.last_period, 
                         order=args.order,
                         display_coefficients=args.display_coefficients)
    if args.n_periods_strouhal > 0:
      simulation.get_strouhal(n_periods=args.n_periods_strouhal, 
                              order=args.order)

  # plot instantaneous forces (or force coefficients)
  simulations[0].plot_forces(display_drag=args.display_drag,
                             display_lift=args.display_lift,
                             display_extrema=args.display_extrema, 
                             order=args.order,
                             display_gauge=args.display_gauge,
                             other_simulations=simulations[1:],
                             limits=args.plot_limits,
                             save_name=args.save_name, 
                             show=args.show)


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))