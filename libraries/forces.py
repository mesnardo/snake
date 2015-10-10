#!/usr/bin/env python

# file: forces.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Collection of classes and functions to post-process forces 
#              acting on bodies.


import os

import numpy
from scipy import signal
from matplotlib import pyplot


class Force(object):
  """Contains info about a force."""
  def __init__(self, times, values, name=None):
    """Initializes the force with given values.

    Parameters
    ----------
    times: Numpy array of float
      Discrete time.
    values: Numpy array of float
      Instantaneous values of the force.
    name: string
      Description of the force; default: None.
    """
    self.name = name
    self.times = times
    self.values = values

  def get_mean(self, limits=[0.0, float('inf')], last_period=False, order=5):
    """Computes the mean force.

    Parameters
    ----------
    limits: list of floats
      Time-limits to compute the mean value; default: [0.0, float('inf')].
    last_period: boolean
      If 'True': computes the mean value over the last period; default: False.
    order: integer
      If 'last_period=True': number of neighbors used to define an extremum; default: 5.

    Returns
    -------
    mean: float
      The mean force.
    """
    if last_period:
      minima, maxima = self.get_extrema(order=order)
      if minima[-1] > maxima[-1]:
        mask = numpy.arange(minima[-2], minima[-1]+1)
      else:
        mask = numpy.arange(maxima[-2], maxima[-1]+1)
    else:
      mask = numpy.where(numpy.logical_and(self.times >= limits[0],
                                           self.times <= limits[1]))[0]
      # remove doublons
      _, mask_uniqueness = numpy.unique(self.times, return_index=True)
      mask = list(set(mask) & set(mask_uniqueness)) 
    return numpy.mean(self.values[mask])

  def get_deviations(self, limits=[0.0, float('inf')], order=5, last_period=False):
    """Computes the deviations around the mean value.

    Parameters
    ----------
    limits: list of floats
      Time-limits to compute the mean value; default: [0.0, float('inf')].
    order: integer
      Number of neighboring points used to define an extremum; default: 5.
    last_period: boolean
      If 'True': computes the deviations over the last period; default: False.

    Returns
    -------
    min_deviations: float or Numpy array of floats
      Distances between the minima and the mean value.
    max_deviations: float or Numpy array of floats
      Distances between the maxima and the mean value. 
    """
    mean = self.get_mean(limits=limits, last_period=last_period, order=order)
    minima, maxima = self.get_extrema(order=order)
    if last_period:
      return (math.absolute(self.values[minima[-1]] - mean), 
              math.absolute(self.values[maxima[-1]] - mean))
    else:
      return (numpy.absolute(self.values[minima] - mean), 
              numpy.absolute(self.values[maxima] - mean))

  def get_extrema(self, order=5):
    """Computes masks (i.e. arrays of indices) of the extrema of the force.

    Parameters
    ----------
    order: integer
      Number of neighboring points used to define an extremum; default: 5.

    Returns
    -------
    minima: Numpy array of integers
      Index of minima.
    maxima: Numpy array of integers
      Index of maxima.
    """
    minima = signal.argrelextrema(self.values, numpy.less_equal, order=order)[0][:-1]
    maxima = signal.argrelextrema(self.values, numpy.greater_equal, order=order)[0][:-1]
    # remove indices that are too close
    minima = minima[numpy.append(True, minima[1:]-minima[:-1] > order)]
    maxima = maxima[numpy.append(True, maxima[1:]-maxima[:-1] > order)]
    return minima, maxima


class Simulation(object):
  """Simulation manager."""
  def __init__(self, name=None, directory=os.getcwd(), output=False):
    """Initialization (stores simulation directory).

    Parameters
    ----------
    directory: string
      Directory of the simulation; default: current working directory.
    output: boolean
      If 'True': prints simulation directory; default: False.
    """
    self.name = name
    self.directory = directory
    self.force_x, self.force_y = None, None
    if output:
      print('[info] simulation name: {}'.format(self.name))
      print('[info] simulation directory: {}'.format(self.directory))

  def get_means(self, limits=[0.0, float('inf')], last_period=False, order=5):
    return (self.force_x.get_mean(limits=limits, last_period=last_period, order=order), 
            self.force_y.get_mean(limits=limits, last_period=last_period, order=order))

  def plot_forces(self, display_lift=True, display_drag=True,
                  limits=[0.0, float('inf'), 0.0, float('inf')],
                  title=None, save=None, show=False, output=False,
                  display_extrema=False, order=5, display_gauge=False):
    """Displays the forces into a figure."""
    if output:
      print('[info] plotting forces... ')
    pyplot.style.use('{}/styles/mesnardo.mplstyle'.format(os.environ['PYSCRIPTS']))
    fig, ax = pyplot.subplots(figsize=(8, 6))
    color_cycle = ax._get_lines.color_cycle
    pyplot.grid(True, zorder=0)
    pyplot.xlabel('time')
    pyplot.ylabel('forces' if self.force_x.name == '$F_x$' else 'force coefficients')
    forces = []
    if display_drag:
      forces.append(self.force_x)
    if display_lift:
      forces.append(self.force_y)
    for force in forces:
      color = next(color_cycle)
      pyplot.plot(force.times, force.values,
                  label=('{} - {}'.format(self.name, force.name) if self.name
                         else force.name),
                  color=color, linestyle='-', zorder=10)
      if display_extrema:
        minima, maxima = force.get_extrema(order=order)
        pyplot.scatter(force.times[minima], force.values[minima],
                       c=color, marker='o', zorder=10)
        pyplot.scatter(force.times[maxima], force.values[maxima],
                       c=color, marker='o', zorder=10)
        if display_gauge:
          pyplot.axhline(force.values[minima[-1]],
                         color=color, linestyle=':', zorder=10)
          pyplot.axhline(force.values[maxima[-1]],
                         color=color, linestyle=':', zorder=10)
    pyplot.legend()
    pyplot.axis(limits)
    if title:
      pyplot.title(title)
    if save:
      images_directory = '{}/images'.format(self.directory)
      if output:
        print('[info] saving figure in directory {}...'.format(images_directory))
      if not os.path.isdir(images_directory):
        os.makedirs(images_directory)
      pyplot.savefig('{}/{}.png'.format(images_directory, save))
    if show:
      if output:
        print('[info] displaying figure...')
      pyplot.show()
    pyplot.close()


class OpenFOAMSimulation(Simulation):
  """Contains information about an OpenFOAM simulation."""
  def __init__(self, name=None, directory=os.getcwd(), output=False):
    """Initialization (stores simulation directory).

    Parameters
    ----------
    directory: string
      Directory of the simulation; default: current working directory.
    output: boolean
      If 'True': prints simulation directory; default: False.
    """
    Simulation.__init__(self, name=name, directory=directory, output=output)

  def read_forces(self, force_coefficients=False):
    """Reads forces from files."""
    key = 'forceCoeffs' if force_coefficients else 'forces'
    forces_directory = '{}/postProcessing/{}'.format(self.directory, key)  
    subdirectories = sorted(os.listdir(forces_directory))
    times = numpy.empty(0)
    force_x, force_y = numpy.empty(0), numpy.empty(0)
    for subdirectory in subdirectories:
      forces_path = '{}/{}/{}.dat'.format(forces_directory, subdirectory, key)
      with open(forces_path, 'r') as infile:
        t, fx, fy = numpy.loadtxt(infile, dtype=float, usecols=(0, 2, 3), unpack=True)
      times = numpy.append(times, t)
      force_x, force_y = numpy.append(force_x, fx), numpy.append(force_y, fy)
    self.force_x = Force(times, force_x, 
                         name=('$C_d$' if key == 'forceCoeffs' else '$F_x$'))
    self.force_y = Force(times, force_y, 
                         name=('$C_l$' if key == 'forceCoeffs' else '$F_y$'))