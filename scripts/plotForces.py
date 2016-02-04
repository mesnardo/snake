# file: plotForces.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Plots the instantaneous forces or force coefficients.


import os
import sys
import argparse

sys.path.append('{}/scripts/library'.format(os.environ['SCRIPTS']))
import forces
import miscellaneous


def parse_command_line():
  """Parses the command-line."""
  print('[info] parsing command-line ...')
  # create parser
  parser = argparse.ArgumentParser(description='Plots the instantaneous forces',
                        formatter_class= argparse.ArgumentDefaultsHelpFormatter)
  # fill parser with arguments
  simulation_info = parser.add_argument_group('simulation info')
  simulation_info.add_argument('--directory', dest='directory', 
                      type=str, default=os.getcwd(), 
                      help='directory of the simulation')
  simulation_info.add_argument('--description', dest='description',
                      type=str, default=None,
                      help='quick description of the simulation')
  simulation_info.add_argument('--software', '--type', dest='software',
                      type=str, 
                      choices=['openfoam', 'cuibm', 'petibm', 'ibamr'],
                      help='software used for simulation')
  simulation_info.add_argument('--display-coefficients', dest='display_coefficients',
                      action='store_true',
                      help='flag to plot the force coefficients, not the forces')
  simulation_info.add_argument('--coefficient', dest='coefficient',
                      type=float, default=1.0,
                      help='force to force coefficient converter')

  parser.add_argument('--add-simulation', dest='others',
                      action='append', nargs='+', default=[],
                      help='adds another simulation '
                           '(software, directory, description, coefficient) '
                           'for comparison.')

  stats_info = parser.add_argument_group('statistics info')
  stats_info.add_argument('--average', dest='average_limits', 
                      type=float, nargs='+', default=[0.0, float('inf')],
                      help='temporal limits to consider to average forces')
  stats_info.add_argument('--average-last', dest='last_period', 
                      action='store_true',
                      help='averages forces over the last period')
  stats_info.add_argument('--strouhal', dest='strouhal',
                      type=float, nargs='+', default=[0, float('inf')], 
                      help='averages the Strouhal number over a given number of '
                           'last oscillations based on the lift curve '
                           'ending at a given time')
  stats_info.add_argument('--order', dest='order', 
                      type=int, default=5,
                      help='number of side-points used for comparison to get extrema')

  plot_info = parser.add_argument_group('plot info')
  plot_info.add_argument('--no-show', dest='show', 
                      action='store_false',
                      help='does not display the figure')
  plot_info.add_argument('--no-save', dest='save',
                         action='store_false',
                         help='does not save the figure')
  plot_info.add_argument('--save-name', dest='save_name', 
                      type=str, default=None,
                      help='name of the figure of save')
  plot_info.add_argument('--limits', dest='plot_limits', 
                      type=float, nargs='+', default=[None, None, None, None],
                      help='limits of the plot')
  plot_info.add_argument('--no-drag', dest='display_drag', 
                      action='store_false',
                      help='does not display the force in the x-direction')
  plot_info.add_argument('--no-lift', dest='display_lift', 
                      action='store_false',
                      help='does not display the force in the y-direction')
  plot_info.add_argument('--extrema', dest='display_extrema', 
                      action='store_true',
                      help='displays the forces extrema')
  plot_info.add_argument('--gauge', dest='display_gauge', 
                      action='store_true',
                      help='display gauges to check the convergence')
  # default options
  parser.set_defaults(display_drag=True, display_lift=True, show=True, save=True)
  # parse given options file
  parser.add_argument('--options', 
                      type=open, action=miscellaneous.ReadOptionsFromFile,
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
  for other in args.others:
    info = dict(zip(['software', 'directory', 'description', 'coefficient'], other))
    simulations.append(forces.Simulation(description=info['description'],
                                         directory=info['directory'],
                                         software=info['software'],
                                         coefficient=float(info['coefficient'])))
  # read and compute some statistics
  for index, simulation in enumerate(simulations):
    simulations[index].read_forces(display_coefficients=args.display_coefficients)
    simulation.get_means(limits=args.average_limits, 
                         last_period=args.last_period, 
                         order=args.order)
    if args.strouhal[0] > 0:
      simulation.get_strouhal(n_periods=args.strouhal[0], 
                              end_time=args.strouhal[1],
                              order=args.order)
  # plot instantaneous forces (or force coefficients)
  simulations[0].plot_forces(display_drag=args.display_drag,
                             display_lift=args.display_lift,
                             display_coefficients=args.display_coefficients,
                             display_extrema=args.display_extrema, 
                             order=args.order,
                             display_gauge=args.display_gauge,
                             other_simulations=simulations[1:],
                             limits=args.plot_limits,
                             save_name=args.save_name, 
                             show=args.show)
  # display time-averaged values in table
  print(simulations[0].create_dataframe(other_simulations=simulations[1:],
                                        display_coefficients=args.display_coefficients))


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))