# file: plotDragCoefficientsCylinder2d.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Plots the instantaneous drag coefficient and compares to 
#              numerical results from Koumoutsakos and Leonard (1995).


import os
import sys
import argparse

import numpy
from matplotlib import pyplot

sys.path.append('{}/scripts/library'.format(os.environ['SCRIPTS']))
import forces


def parse_command_line():
  """Parses the command-line."""
  print('[info] parsing the command-line ...'),
  # create parser
  parser = argparse.ArgumentParser(description='Plots the drag coefficient',
                        formatter_class= argparse.ArgumentDefaultsHelpFormatter)
  # fill parser with arguments
  parser.add_argument('--directory', dest='directory', 
                      type=str, default=os.getcwd(),
                      help='directory of the simulation')
  parser.add_argument('--type', dest='simulation_type',
                      type=str,
                      help='type of simulation (petibm or cuibm)')
  parser.add_argument('--description', dest='description',
                      type=str, default=None,
                      help='quick description of the simulation')
  parser.add_argument('--re', '-re', dest='Re', 
                      type=float,
                      help='Reynolds number of the flow')
  parser.add_argument('--validation-data', dest='validation_data_path',
                      type=str,
                      help='path of the validation data file')
  parser.add_argument('--limits', dest='plot_limits', 
                      type=float, nargs='+', default=[None, None, None, None],
                      help='limits of the plot')
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
  elif args.Re not in [40, 550, 3000]:
    print('[error] wrong Reynolds number (40, 550, or 3000)'); sain = False
  elif args.simulation_type not in ['petibm', 'cuibm']:
    print('[error] wrong simulation type'); sain = False
  if not sain:
    sys.exit()


def get_SimulationClass(simulation_type):
  """Gets the appropriate class.

  Parameters
  ----------
  simulation_type: string
    Description of the type of simulation (openfoam, cuibm, petibm)
  """
  if simulation_type == 'cuibm':
    return forces.CuIBMSimulation
  elif simulation_type == 'petibm':
    return forces.PetIBMSimulation
  else:
    print('[error] type should be "cuibm" or "petibm"')
    sys.exit()


class KoumoutsakosLeonard1995(object):
  """Container to store results from Koumoutsakos and Leonard (1995)."""
  def __init__(self):
    """Initializes."""
    self.name = 'Koumoutsakos and Leonard (1995)'

  def read_drag(self, path):
    """Reads the instantaneous drag coefficients from given file.

    Parameters
    ----------
    path: string
      Path of the file containing the instantaneous drag coefficients.
    """
    print('[info] reading drag coefficients from Koumoutsakos and Leonard (1995) ...'),
    with open(path, 'r') as infile:
      times, drag = numpy.loadtxt(infile, dtype=float, comments='#', unpack=True)
    self.force_x = forces.Force(0.5*times, drag, name='$C_d$')
    print('done')


def plot_drag_coefficients(simulation, validation_data, 
                           directory=os.getcwd(), save_name=None, 
                           limits=None, show=False):
  """Plots the instantaneous drag coefficients 
  and compares with Koumoutsakos and Leonard (1995).

  Parameters
  ----------
  simulation: instance of class Simulation
    Object containing the instantaneous forces.
  validation_data: instance of class KoumoutsakosLeonard1995
    Object containing the results from Koumoutsakos and Leonard (1995).
  directory: string
    Directory of the simulation; default: $PWD.
  save_name: string
    File name to save; default: None (not saving the figure).
  limits: list of floats
    x- and y-limits of the plot; default: None.
  show: bool
    Set to 'True' to display the figure; default: False.
  """
  print('[info] plotting the drag coefficients ...'),
  images_directory = '{}/images'.format(directory)
  if save_name and not os.path.isdir(images_directory):
    os.makedirs(images_directory)
  pyplot.style.use('{}/styles/mesnardo.mplstyle'.format(os.environ['SCRIPTS']))
  kwargs_data = {'label': 'PetIBM',
                 'color': '#336699', 'linestyle': '-', 'linewidth': 2,
                 'zorder': 10}
  kwargs_validation_data = {'label': validation_data.name,
                            'color': '#993333', 'linewidth': 0,
                            'markeredgewidth': 2, 'markeredgecolor': '#993333',
                            'markerfacecolor': 'none',
                            'marker': 'o', 'markersize': 4,
                            'zorder': 10}
  fig, ax = pyplot.subplots(figsize=(6, 6))
  ax.grid(True, zorder=0)
  ax.set_xlabel('non-dimensional time')
  ax.set_ylabel('drag coefficient')
  ax.plot(simulation.force_x.times, simulation.force_x.values, **kwargs_data)
  ax.plot(validation_data.force_x.times, validation_data.force_x.values, **kwargs_validation_data)
  ax.axis(limits)
  ax.legend()
  if save_name:
    pyplot.savefig('{}/{}.png'.format(images_directory, save_name))
  if show:
    pyplot.show()
  print('done')


def main():
  """Plots the instantaneous drag coefficient 
  and compares to Koumoutsakos and Leonard (1995).
  """
  args = parse_command_line()
  sanity_checks(args)
  
  print('[info] simulation: {}'.format(args.directory))
  print('[info] Reynolds number: {}'.format(args.Re))


  SimulationClass = get_SimulationClass(args.simulation_type)
  simulation = SimulationClass(directory=args.directory, name=args.description)
  simulation.read_forces(force_coefficients=True, coefficient=2.0)

  validation_data = KoumoutsakosLeonard1995()
  validation_data.read_drag(args.validation_data_path)

  plot_drag_coefficients(simulation, validation_data, 
                         directory=args.directory, save_name=args.save_name,
                         limits=args.plot_limits, show=args.show)


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))