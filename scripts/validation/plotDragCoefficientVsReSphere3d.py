# file: plotDragCoefficientVsReSphere3d.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Plots the steady drag coefficient of a sphere versus Reynolds number 
#              and compares to experimental data (Roos and Willmarth, 1971).


import os
import sys
import argparse

import numpy
from matplotlib import pyplot

from snake import miscellaneous
from snake.simulation import Simulation
from snake.force import Force


def parse_command_line():
  """Parses the command-line and returns the namespace."""
  print('[info] parsing the command-line ...'),
  # create parser
  parser = argparse.ArgumentParser(description='Plots the drag coefficient vs. Re',
                        formatter_class= argparse.ArgumentDefaultsHelpFormatter)
  # fill parser with arguments
  parser.add_argument('--directories', dest='directories', 
                      type=str, nargs='+',
                      help='directory of each simulation to consider')
  parser.add_argument('--re', dest='re',
                      type=float, nargs='+',
                      help='Reynolds number for each simulation to consider')
  parser.add_argument('--software', dest='software',
                      type=str, 
                      choices=['cuibm', 'petibm'],
                      help='software used to generate solution')
  parser.add_argument('--description', dest='description',
                      type=str, 
                      default=None,
                      help='quick description of the group of simulations')
  parser.add_argument('--validation-data', dest='validation_data_path',
                      type=str, 
                      default=('{}/resources/validationData/'
                               'roos_willmarth_1971_sphere_dragCoefficient.dat'
                               ''.format(os.environ['SCRIPTS'])),
                      help='path of the validation data file')
  parser.add_argument('--limits', dest='plot_limits', 
                      type=float, nargs=4, 
                      default=[None, None, None, None],
                      metavar=('x-start', 'x-end', 'y-start', 'y-end'),
                      help='limits of the plot')
  parser.add_argument('--no-show', dest='show',
                      action='store_false',
                      help='does not display the figures')
  parser.add_argument('--save-name', dest='save_name',
                      type=str, 
                      default=None,
                      help='name of .png file to save')
  parser.add_argument('--save-directory', dest='save_directory',
                      type=str, 
                      default=os.getcwd(),
                      help='directory where to save the .png file')
  parser.set_defaults(show=True)
  # parse given options file
  parser.add_argument('--options', 
                      type=open, action=miscellaneous.ReadOptionsFromFile,
                      help='path of the file with options to parse')
  print('done')
  return parser.parse_args()


def plot_drag_coefficient(simulations, 
                          validation=None, 
                          save_directory=os.getcwd(), 
                          save_name=None, 
                          limits=None, 
                          show=False):
  """Plots the steady drag coefficient versus the Reynolds number
  and compares with experimental results from Roos and Willmarth (1971).

  Parameters
  ----------
  simulations: list of Simulation objects
    Simulations to take into account.
  validation: object, optional
    Contains the validation data to compare with;
    default: None.
  save_directory: string, optional
    Directory where to save the .png file;
    default: current directory.
  save_name: string, optional
    Name of .png file to save; 
    default: None (i.e. not saving the figure).
  limits: list of floats, optional
    x- and y-limits of the plot; 
    default: None.
  show: boolean, optional
    Set to 'True' to display the figure; 
    default: False.
  """
  print('[info] plotting the drag coefficient versus Reynolds number ...'),
  images_directory = '{}/images'.format(save_directory)
  if save_name and not os.path.isdir(images_directory):
    os.makedirs(images_directory)
  try:
    style_path = os.path.join(os.environ['SNAKE'], 'snake', 'styles',
                              'mesnardo.mplstyle')
    pyplot.style.use(style_path)
  except:
    pass
  kwargs_data = {'label': simulations[0].description,
                 'color': '#336699', 'linewidth': 0,
                 'markeredgewidth': 2, 'markeredgecolor': '#336699',
                 'markerfacecolor': '#336699',
                 'marker': 's', 'markersize': 8,
                 'zorder': 11}
  if validation:
    kwargs_validation= {'label': validation.description,
                        'color': '#993333', 'linewidth': 0,
                        'markeredgewidth': 2, 'markeredgecolor': '#993333',
                        'markerfacecolor': 'none',
                        'marker': 'o', 'markersize': 8,
                        'zorder': 10}
  fig, ax = pyplot.subplots(figsize=(8, 6))
  ax.grid(True, zorder=0)
  ax.set_xlabel('Reynolds number', fontsize=16)
  ax.set_ylabel('drag coefficient', fontsize=16)
  ax.plot([simu.re for simu in simulations], 
          [1.0/(numpy.pi*0.5**2)*simu.force_x.values[-1] for simu in simulations], 
          **kwargs_data)
  if validation:
    ax.plot(validation.re, 
            validation.cd, 
            **kwargs_validation)
  ax.axis(limits)
  ax.legend(prop={'size': 16})
  if save_name:
    pyplot.savefig(os.path.join(images_directory, save_name + '.png'))
  if show:
    pyplot.show()
  print('done')


class RoosWillmarth1971(object):
  """Contains info about the experimental data from Roos and Willmarth (1971)."""
  def __init__(self, file_path=None):
    """If provided, read the drag coefficient versus the Reynolds number from file.

    Parameters
    ----------
    file_path: string, optional
      Path of the file to read;
      default: None.
    """
    self.description = 'Roos and Willmarth (1971)'
    self.file_path = file_path
    if self.file_path:
      self.read_drag_coefficient(file_path)

  def read_drag_coefficient(self, file_path):
    """Reads the drag coefficient versus the Reynolds number from given file path.

    Parameters
    ----------
    file_path: string
      Path of the file to read.
    """
    print('[info] reading drag coefficient from file {} ...'.format(file_path)),
    with open(file_path, 'r') as infile:
      self.re, self.cd = numpy.loadtxt(infile, 
                                       dtype=float, comments='#', unpack=True)
    print('done')


def main(args):
  """Plots the steady drag coefficient of a sphere versus Reynolds number 
  and compares to experimental data (Roos and Willmarth, 1971)."""
  simulations = []
  for index, directory in enumerate(args.directories):
    simulations.append(Simulation(directory=directory,
                                  description=args.description,
                                  software=args.software,
                                  re=args.re[index]))
    simulations[-1].read_forces()

  roos_willmarth_1971 = RoosWillmarth1971(file_path=args.validation_data_path)

  plot_drag_coefficient(simulations, 
                        validation=roos_willmarth_1971,
                        save_directory=args.save_directory,
                        save_name=args.save_name,
                        limits=args.plot_limits,
                        show=args.show)


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  args = parse_command_line()
  main(args)
  print('\n[{}] END\n'.format(os.path.basename(__file__)))