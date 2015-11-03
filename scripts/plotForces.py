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
  parser.add_argument('--type', dest='simulation_type',
                      type=str,
                      help='type of simulation (openfoam, cuibm, petibm, ibamr)')
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
  parser.add_argument('--strouhal', dest='strouhal',
                      action='store_true', 
                      help='computes the Strouhal number based on lift history')
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
  # default options
  parser.set_defaults(display_drag=True, display_lift=True, show=True)
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
  # return namespace
  return parser.parse_args()


def get_SimulationClass(simulation_type):
  """Gets the appropriate class.

  Parameters
  ----------
  simulation_type: string
    Description of the type of simulation (openfoam, cuibm, petibm)
  """
  if simulation_type == 'openfoam':
    return forces.OpenFOAMSimulation
  elif simulation_type == 'cuibm':
    return forces.CuIBMSimulation
  elif simulation_type == 'petibm':
    return forces.PetIBMSimulation
  elif simulation_type == 'ibamr':
    return forces.IBAMRSimulation
  else:
    print('[error] type should be "openfoam", "cuibm", "petibm", or "ibamr"')
    exit(0)


def main():
  """Plots the instantaneous force coefficients."""
  parameters = parse_command_line()
  # create master simulation
  SimulationClass = get_SimulationClass(parameters.simulation_type)
  master = SimulationClass(name=parameters.description,
                           directory=parameters.directory,
                           output=True)
  master.read_forces(force_coefficients=parameters.display_coefficients,
                     coefficient=parameters.coefficient)
  master.get_means(limits=parameters.average_limits, 
                   last_period=parameters.last_period, order=parameters.order,
                   force_coefficients=parameters.display_coefficients,
                   output=True)
  if parameters.strouhal:
    master.get_strouhal(output=True)
  
  # get info about other simulations used for comparison
  slaves = []
  nb_others_parameters = 4
  num_others = len(parameters.others)/nb_others_parameters
  for index in xrange(num_others):
    slave_type = parameters.others[index*nb_others_parameters + 0]
    slave_directory = parameters.others[index*nb_others_parameters + 1]
    slave_description = parameters.others[index*nb_others_parameters + 2]
    slave_coefficient = float(parameters.others[index*nb_others_parameters + 3])
    SimulationClass = get_SimulationClass(slave_type)
    slaves.append(SimulationClass(name=slave_description,
                                  directory=slave_directory,
                                  output=True))
    slaves[-1].read_forces(force_coefficients=parameters.display_coefficients,
                           coefficient=slave_coefficient)
    slaves[-1].get_means(limits=parameters.average_limits, 
                         last_period=parameters.last_period, 
                         order=parameters.order,
                         force_coefficients=parameters.display_coefficients,
                         output=True)
    if parameters.strouhal:
      slaves[-1].get_strouhal(output=True)

  # plot instantaneous forces (or force coefficients)
  master.plot_forces(display_drag=parameters.display_drag,
                     display_lift=parameters.display_lift,
                     limits=parameters.plot_limits,
                     save=parameters.save, show=parameters.show, output=True,
                     display_extrema=parameters.display_extrema, 
                     order=parameters.order,
                     display_gauge=parameters.display_gauge,
                     other_simulations=slaves)


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))
