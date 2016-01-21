# file: plotCFL.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# brief: Plots the instantaneous maximum CFL number.


import argparse
import os
import sys

import numpy
from scipy import signal
from matplotlib import pyplot

sys.path.append('{}/scripts/library'.format(os.environ['SCRIPTS']))
import miscellaneous


def parse_command_line():
  """Parses the command-line."""
  print('[info] parsing command-line ...'),
  # create the parser
  parser = argparse.ArgumentParser(description='Plots the maximum CFL number over time',
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  # fill the parser with arguments
  parser.add_argument('--directory', dest='directory', 
                      type=str, default=os.getcwd(),
                      help='directory of the simulation')
  parser.add_argument('--path', dest='file_path', 
                      type=str,
                      help='path of the IcoFOAM logging file')
  parser.add_argument('--average', dest='average_limits', 
                      type=float, nargs='+', default=[0.0, float('inf')],
                      help='time limits to compute averaged cfl')
  parser.add_argument('--no-show', dest='show', 
                      action='store_false',
                      help='does not display the figure')
  parser.add_argument('--save-name', dest='save_name', 
                      type=str, default=None,
                      help='name of the figure of save')
  parser.add_argument('--limits', dest='plot_limits', 
                      type=float, nargs='+', default=[None, None, None, None],
                      help='limits of the plot')
  parser.add_argument('--extrema', dest='display_extrema', 
                      action='store_true',
                      help='displays the forces extrema')
  parser.add_argument('--order', dest='order', 
                      type=int, default=5,
                      help='number of side-points used for comparison to get extrema')
  # default options
  parser.set_defaults(show=True)
  # parse given options file
  parser.add_argument('--options', 
                      type=open, action=miscellaneous.ReadOptionsFromFile,
                      help='path of the file with options to parse')
  print('done')
  return parser.parse_args()


def read_maximum_cfl(file_path):
  """Reads the instantaneous maximum CFL number from a given file.

  Parameters
  ----------
  file_path: string
    Path of the logging file containing the instantaneous maximum CFL number.

  Returns
  -------
  time: numpy array of float
    Discrete time values.
  cfl: numpy array of float
    Discrete maximum CFL values
  """
  print('[info] reading file {} ...'.format(file_path)),
  with open(file_path, 'r') as infile:
    time = numpy.array([float(line.split()[-1]) 
                        for line in infile if line.startswith('Time = ')])
  with open(file_path, 'r') as infile:
    cfl = numpy.array([float(line.split()[-1]) 
                        for line in infile if line.startswith('Courant Number mean')])
  assert(time.shape == cfl.shape)
  print('done')
  return time, cfl


def get_mean(time, array, limits=[0.0, float('inf')], output=False):
  """Computes the mean force.

  Parameters
  ----------
  time: numpy array of floats
    Discrete time values.
  array: numpy array of floats
    Array to use to compute the mean value.
  limits: list of floats
    Time-limits to compute the mean value; default: [0.0, float('inf')].
  output: bool
    Set 'True' to display the time-averaged value; default: False.

  Returns
  -------
  start, end: floats
    Time-limits used to compute the mean value.
  mean: float
    The mean value.
  """
  print('[info] computing the mean value ...'),
  mask = numpy.where(numpy.logical_and(time >= limits[0],
                                       time <= limits[1]))[0]
  start, end = time[mask[0]], time[mask[-1]]
  mean = numpy.mean(array[mask])
  if output:
    print('\n[info] averaging the maximum CFL '
          'number between {} and {} time-units:'.format(start, end))
    print('\t<max(CFL)> = {}\n'.format(mean))
  print('done')
  return start, end, mean


def get_extrema(array, order=5):
  """Computes masks (i.e. arrays of indices) of the extrema of the force.

  Parameters
  ----------
  array: numpy array
    Array on which to define the extrema.
  order: integer
    Number of neighboring points used to define an extremum; default: 5.

  Returns
  -------
  minima: Numpy array of integers
    Index of minima.
  maxima: Numpy array of integers
    Index of maxima.
  """
  print('[info] computing extrema ...'),
  minima = signal.argrelextrema(array, numpy.less_equal, order=order)[0][:-1]
  maxima = signal.argrelextrema(array, numpy.greater_equal, order=order)[0][:-1]
  # remove indices that are too close
  minima = minima[numpy.append(True, minima[1:]-minima[:-1] > order)]
  maxima = maxima[numpy.append(True, maxima[1:]-maxima[:-1] > order)]
  print('done')
  return minima, maxima


def plot_cfl(time, cfl, 
             display_extrema=False, order=5, 
             limits=[0.0, float('inf'), 0.0, float('inf')],
             directory=os.getcwd(), save_name=None,
             show=True):
  """Plots the instantaneous maximum CFL number.

  Parameters
  ----------
  time: numpy array of floats
    Discrete time values.
  cfl: numpy array of floats
    Maximum CFL values.
  display_extrema: bool
    Set 'True' to emphasize the extrema of the curves; default: False.
  order: int
    Number of neighbors used on each side to define an extremum; default: 5.
  limits: list of floats
    Limits of the axes [xmin, xmax, ymin, ymax]; default: [0.0, +inf, 0.0, +inf].
  directory: string
    Directory of the simulation; default: $PWD.
  save_name: string
    Name of the .PNG file to save; default: None (does not save).
  show: bool
    Set 'True' to display the figure; default: False.
  """
  print('[info] plotting cfl ...')
  pyplot.style.use('{}/styles/mesnardo.mplstyle'.format(os.environ['SCRIPTS']))
  color = '#386cb0'
  fig, ax = pyplot.subplots(figsize=(8, 6))
  pyplot.grid(True, zorder=0)
  pyplot.xlabel('time')
  pyplot.ylabel('maximum CFL')
  pyplot.plot(time, cfl, color=color, linestyle='-', zorder=10)
  if display_extrema:
    minima, maxima = get_extrema(cfl, order=order)
    pyplot.scatter(time[minima], cfl[minima], c=color, marker='o', zorder=10)
    pyplot.scatter(time[maxima], cfl[maxima], c=color, marker='o', zorder=10)
  pyplot.axis(limits)
  if save_name:
    images_directory = '{}/images'.format(directory)
    print('[info] saving figure in directory {} ...'.format(images_directory))
    if not os.path.isdir(images_directory):
      os.makedirs(images_directory)
    pyplot.savefig('{}/{}.png'.format(images_directory, save_name))
  if show:
    print('[info] displaying figure ...')
    pyplot.show()
  pyplot.close()


def main():
  """Plots the instantaneous maximum CFL number."""
  args = parse_command_line()
  time, cfl = read_maximum_cfl(args.file_path)
  get_mean(time, cfl,  limits=args.average_limits, output=True)
  plot_cfl(time, cfl, 
           display_extrema=args.display_extrema, order=args.order,
           limits=args.plot_limits, 
           directory=args.directory, save_name=args.save_name,
           show=args.show)


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))