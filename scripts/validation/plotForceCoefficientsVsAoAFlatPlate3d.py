# file: plotForceCoefficientsVsAoAFlatPlate3d.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Plots the lift and drag coefficients for a 3d flat-plate 
#              with different angles of attack


import os
import argparse
import collections

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
  parser.add_argument('--software', dest='software',
                      type=str, 
                      choices=['petibm'],
                      help='software used to generate solution')
  parser.add_argument('--directory', dest='directory',
                      type=str,
                      default=os.getcwd(),
                      help='main directory containing series directories')
  parser.add_argument('--series', dest='series', 
                      type=str, nargs='+',
                      help='directory of each series of simulations')
  parser.add_argument('--descriptions', dest='descriptions',
                      type=str, nargs='+',
                      help='description for each series of simulations')
  parser.add_argument('--angles', dest='angles',
                      type=float, nargs='+',
                      help='list of angles of attack to consider')
  parser.add_argument('--coefficient', dest='coefficient',
                      type=float,
                      default=1.0,
                      help='coefficient to convert force into force coefficient')
  parser.add_argument('--validation-data', dest='validation_data',
                      type=str, nargs='+',
                      default=None,
                      help='path of files containing Taira (2008) data')
  parser.add_argument('--limits', dest='plot_limits', 
                      type=float, nargs=4, 
                      default=[None, None, None, None],
                      metavar=('x-start', 'x-end', 'y-start', 'y-end'),
                      help='limits of the plot')
  parser.add_argument('--no-show', dest='show',
                      action='store_false',
                      help='does not display the figures')
  parser.add_argument('--save-names', dest='save_names',
                      type=str, nargs='+',
                      default=None,
                      help='name of .png files to save')
  parser.add_argument('--save-directory', dest='save_directory',
                      type=str, 
                      default=os.getcwd(),
                      help='directory where to save the .png files')
  parser.set_defaults(show=True)
  # parse given options file
  parser.add_argument('--options', 
                      type=open, action=miscellaneous.ReadOptionsFromFile,
                      help='path of the file with options to parse')
  print('done')
  return parser.parse_args()


class TairaEtAl2007FlatPlate(object):
  """Contains experimental force coefficients for various angles-of-attack
  of a flat-plate with aspect-ratio 2.

  The experimental results are reported in Taira et al. (2007) and Taira (2008).
  """
  def __init__(self):
    pass

  def read_drag_coefficients(self, file_path):
    """Reads the angles-of-attack and the drag coefficients from file.

    Parameters
    ----------
    file_path: string
      Path of the file containing the angles and drag coefficients.
    """
    print('[info] reading drag coefficients from file {} ...'.format(file_path))
    with open(file_path, 'r') as infile:
      angles, values = numpy.loadtxt(infile, dtype=float, comments='#', unpack=True)
    self.cd = [angles, values]

  def read_lift_coefficients(self, file_path):
    """Reads the angles-of-attack and the lift coefficients from file.

    Parameters
    ----------
    file_path: string
      Path of the file containing the angles and lift coefficients.
    """
    print('[info] reading lift coefficients from file {} ...'.format(file_path))
    with open(file_path, 'r') as infile:
      angles, values = numpy.loadtxt(infile, dtype=float, comments='#', unpack=True)
    self.cl = [angles, values]


def plot_coefficients_vs_angles(simulations, validation, 
                                coefficient=1.0,
                                save_directory=os.getcwd(),
                                save_names=[],
                                limits=[],
                                show=False):
  """Plots the force coefficients versus the angle-of-attack of the flat-plate.

  Parameters
  ----------
  simulations: dictionary of lists of Simulation objects
    Contains info about all simulations to consider.
  validation: TairaEtAl2007FlatPlate object
    Contains experimental results reported by Taira et al. (2007).
  coefficient: float, optional
    Scale value to convert a force into a force coefficient;
    default: 1.0.
  save_directory: string, optional
    Directory where to create the `images` folder;
    default: current directory.
  save_names: list of strings, optional
    Name of the files to save;
    default: [] (does not save figures)
  limits: list of floats, optional
    Limits of the plot (x-limits followed by y-limits);
    default: [].
  show: boolean, optional
    Set `True` to display the figures;
    default: False.
  """
  print('[info] plotting the coefficients versus the angle-of-attack ...'),
  images_directory = os.path.join(save_directory, 'images')
  if save_names and not os.path.isdir(images_directory):
    os.makedirs(images_directory)
  try:
    style_path = os.path.join(os.environ['SNAKE'], 'snake', 'styles',
                              'mesnardo.mplstyle')
    pyplot.style.use(style_path)
  except:
    pass
  software_labels = {'petibm': 'PetIBM'}
  fig, ax = pyplot.subplots(figsize=(8, 6))
  color_cycle = ax._get_lines.prop_cycler
  markers = iter(['o', '^', 'v'])
  ax.grid(True)
  ax.set_xlabel('angle of attack (deg)', fontsize=18)
  ax.set_ylabel('drag coefficient', fontsize=18)
  # experimental data
  ax.scatter(validation.cd[0], validation.cd[1], 
             label='Taira et al. (2007)',
             marker='s', s=40, 
             facecolors='none', edgecolors='#1B9E77', 
             zorder=3)
  # numerical data
  for description, series in simulations.iteritems():
    ax.scatter([simulation.angle for simulation in series],
               [coefficient*simulation.forces[0].values[-1] for simulation in series],
               label='{} - {}'.format(software_labels[series[0].software], description),
               marker=next(markers), s=80,
               facecolors='none', 
               edgecolors=next(color_cycle)['color'],
               linewidth=1.5,
               zorder=4)
  ax.legend(loc='upper left', prop={'size': 18})
  ax.axis(limits)
  if save_names:
    pyplot.savefig(os.path.join(images_directory, save_names[0] + '.png'))
  if show:
    pyplot.show()
    pyplot.close()
  fig, ax = pyplot.subplots(figsize=(8, 6))
  color_cycle = ax._get_lines.prop_cycler
  markers = iter(['o', '^', 'v'])
  ax.grid(True)
  ax.set_xlabel('angle of attack (deg)', fontsize=18)
  ax.set_ylabel('lift coefficient', fontsize=18)
  # experimental data
  ax.scatter(validation.cl[0], validation.cl[1], 
             label='Taira et al. (2007)',
             marker='s', s=40, 
             facecolors='none', edgecolors='#1B9E77', 
             zorder=3)
  # numerical data
  for description, series in simulations.iteritems():
    ax.scatter([simulation.angle for simulation in series],
               [coefficient*simulation.forces[1].values[-1] for simulation in series],
               label='{} - {}'.format(software_labels[series[0].software], description),
               marker=next(markers), s=80,
               facecolors='none', 
               edgecolors=next(color_cycle)['color'],
               linewidth=1.5,
               zorder=4)
  ax.legend(loc='upper left', prop={'size': 18})
  ax.axis(limits)
  if save_names:
    pyplot.savefig(os.path.join(images_directory, save_names[1] + '.png'))
  if show:
    pyplot.show()
    pyplot.close()
  print('done')


def main(args):
  """Plots the lift and drag coefficients versus the angle-of-attack of the
  flat-plate and compares to experimental results reported by 
  Taira et al. (2007) and Taira (2008).
  """
  simulations = collections.OrderedDict()
  for description, series in zip(args.descriptions, args.series):
    series_directory = os.path.join(args.directory, series)
    subfolders = sorted([folder for folder in os.listdir(series_directory) 
                         if os.path.isdir(os.path.join(series_directory, folder))])
    simulations[description] = []
    for i, subfolder in enumerate(subfolders):
      simulation_directory = os.path.join(series_directory, subfolder)
      simulations[description].append(Simulation(directory=simulation_directory,
                                                 software=args.software,
                                                 angle=args.angles[i]))
      simulations[description][-1].read_forces()

  experiment = TairaEtAl2007FlatPlate()
  experiment.read_drag_coefficients(args.validation_data[0])
  experiment.read_lift_coefficients(args.validation_data[1])

  plot_coefficients_vs_angles(simulations, experiment, 
                              coefficient=args.coefficient,
                              save_directory=args.save_directory,
                              save_names=args.save_names,
                              limits=args.plot_limits,
                              show=args.show)



if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  args = parse_command_line()
  main(args)
  print('\n[{}] END\n'.format(os.path.basename(__file__)))