#!/usr/bin/env python

# file: plotForces.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Plots the instantaneous forces or force coefficients.


import os
import sys
import argparse

sys.path.append('{}/libraries'.format(os.environ['PYSCRIPTS']))
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
  parser.add_argument('--openfoam', dest='openfoam',
                      action='store_true',
                      help='flag to use for OpenFOAM simulation')
  parser.add_argument('--display-coefficients', dest='display_coefficients',
                      action='store_true',
                      help='flag to plot the force coefficients, not the forces')
  parser.add_argument('--coefficient', dest='coefficient',
                      type=float, default=1.0,
                      help='force to force coefficient converter')
  parser.add_argument('--average', dest='average_limits', 
                      type=float, nargs='+', default=[0.0, float('inf')],
                      help='temporal limits to consider to average forces')
  parser.add_argument('--no-show', dest='show', 
                      action='store_false',
                      help='does not display the figure')
  parser.add_argument('--save-name', dest='save', 
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
  parser.set_defaults(display_drag=True, display_lift=True, show=True)
  return parser.parse_args()


def main():
  """Plots the instantaneous force coefficients."""
  parameters = parse_command_line()
  if parameters.openfoam:
    simulation = forces.OpenFOAMSimulation(name=parameters.description, 
                                           directory=parameters.directory, 
                                           output=True)
  else:
    print('[error] use flag for simulation type')
    return
  simulation.read_forces(force_coefficients=parameters.display_coefficients)
  simulation.get_means(limits=parameters.average_limits)
  simulation.plot_forces(display_drag=parameters.display_drag,
                         display_lift=parameters.display_lift,
                         limits=parameters.plot_limits,
                         save=parameters.save, show=parameters.show, output=True,
                         display_extrema=parameters.display_extrema, 
                         order=parameters.order,
                         display_gauge=parameters.display_gauge)


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))