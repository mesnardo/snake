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
import miscellaneous


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
  parser.add_argument('--software', dest='software',
                      type=str, choices=['cuibm', 'petibm'],
                      help='software used to generate solution')
  parser.add_argument('--description', dest='description',
                      type=str, default=None,
                      help='quick description of the simulation')
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
  parser.add_argument('--options', 
                      type=open, action=miscellaneous.ReadOptionsFromFile,
                      help='path of the file with options to parse')
  print('done')
  return parser.parse_args()


class KoumoutsakosLeonard1995(object):
  """Container to store results from Koumoutsakos and Leonard (1995)."""
  def __init__(self):
    """Initializes."""
    self.description = 'Koumoutsakos and Leonard (1995)'

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
    self.force_x = forces.Force(0.5*times, drag)
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
  kwargs_data = {'label': simulation.description,
                 'color': '#336699', 'linestyle': '-', 'linewidth': 2,
                 'zorder': 10}
  kwargs_validation_data = {'label': validation_data.description,
                            'color': '#993333', 'linewidth': 0,
                            'markeredgewidth': 2, 'markeredgecolor': '#993333',
                            'markerfacecolor': 'none',
                            'marker': 'o', 'markersize': 4,
                            'zorder': 10}
  fig, ax = pyplot.subplots(figsize=(6, 6))
  ax.grid(True, zorder=0)
  ax.set_xlabel('non-dimensional time')
  ax.set_ylabel('drag coefficient')
  ax.plot(simulation.force_x.times, 
          simulation.coefficient*simulation.force_x.values, 
          **kwargs_data)
  ax.plot(validation_data.force_x.times, 
          validation_data.force_x.values, 
          **kwargs_validation_data)
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
  
  print('[info] simulation: {}'.format(args.directory))

  simulation = forces.Simulation(directory=args.directory, description=args.description,
                                 software=args.software, coefficient=2.0)
  simulation.read_forces(display_coefficients=True)

  validation_data = KoumoutsakosLeonard1995()
  validation_data.read_drag(args.validation_data_path)

  plot_drag_coefficients(simulation, validation_data, 
                         directory=args.directory, save_name=args.save_name,
                         limits=args.plot_limits, show=args.show)


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))