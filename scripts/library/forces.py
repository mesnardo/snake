#!/usr/bin/python

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
    time_min, time_max: floats
      The temporal limits of the average.
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
      start, end = self.times[mask[0]], self.times[mask[-1]]
    return {'value': numpy.mean(self.values[mask]), 
            'start': self.times[mask[0]],
            'end': self.times[mask[-1]]}

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
      return {'min': math.absolute(self.values[minima[-1]] - mean),
              'max': math.absolute(self.values[maxima[-1]] - mean)}
    else:
      return {'min': numpy.absolute(self.values[minima] - mean),
              'max': numpy.absolute(self.values[maxima] - mean)}

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

  def get_means(self, limits=[0.0, float('inf')], last_period=False, order=5, 
                force_coefficients=False, output=False):
    fx_mean = self.force_x.get_mean(limits=limits, last_period=last_period, order=order)
    fy_mean = self.force_y.get_mean(limits=limits, last_period=last_period, order=order)
    if output:
      fx_name = ('<cd>' if force_coefficients else '<fx>')
      fy_name = ('<cl>' if force_coefficients else '<fy>')
      print('Averaging forces in x-direction between {} and {}:'.format(fx_mean['start'], 
                                                                        fx_mean['end']))
      print('\t{} = {}'.format(fx_name, fx_mean['value']))
      print('Averaging forces in y-direction between {} and {}:'.format(fy_mean['start'], 
                                                                        fy_mean['end']))
      print('\t{} = {}'.format(fy_name, fy_mean['value']))
    return fx_mean, fy_mean

  def get_strouhal(self, L=1.0, U=1.0, order=5, output=False):
    """Computes the Strouhal number based on the frequency of the lift force.

    The frequency is beased on the lift history and is computed using the minima
    of the lift curve.

    Parameters
    ----------
    L: float
      Characteristics length of the body; default: 1.0.
    U: float
      Characteristics velocity of the body; default: 1.0.
    order: integer
      Number of neighbors used on each side to define an extremum; default: 5.
    output: bool
      Set 'True' if you want to print the Strouhal number; default: False.

    Returns
    -------
    strouhal: float
      The Strouhal number.
    """
    minima, _ = self.force_y.get_extrema(order=order)
    frequencies = 1.0/(self.force_y.times[minima[1:]] - self.force_y.times[minima[:-1]])
    strouhal = frequencies[-1]*L/U
    if output:
      print('Estimating the Strouhal number:')
      print('\tSt = {} (previous: {}, {})'.format(strouhal, 
                                                  frequencies[-2]*U/L, 
                                                  frequencies[-3]*U/L))
    return strouhal

  def plot_forces(self, display_lift=True, display_drag=True,
                  limits=[0.0, float('inf'), 0.0, float('inf')],
                  title=None, save=None, show=False, output=False,
                  display_extrema=False, order=5, display_gauge=False,
                  other_simulations=[]):
    """Displays the forces into a figure."""
    if output:
      print('[info] plotting forces... ')
    pyplot.style.use('{}/styles/mesnardo.mplstyle'.format(os.environ['SCRIPTS']))
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
                  label=('{} - {}'.format(self.name.replace('_', ' '), force.name) if self.name
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
    for simulation in other_simulations:
      forces = []
      if display_drag:
        forces.append(simulation.force_x)
      if display_lift:
        forces.append(simulation.force_y)
      for force in forces:
        color = next(color_cycle)
        pyplot.plot(force.times, force.values,
                    label=('{} - {}'.format(simulation.name.replace('_', ' '), force.name) if simulation.name
                           else force.name),
                    color=color, linestyle='--', zorder=10)
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

  def read_forces(self, force_coefficients=False, coefficient=1.0):
    """Reads forces from files.

    Parameters
    ----------
    force_coefficients: boolean
      Set to 'True' if force coefficients are required; default: False (i.e. forces).
    """
    key = 'forceCoeffs' if force_coefficients else 'forces'
    forces_directory = '{}/postProcessing/{}'.format(self.directory, key)
    usecols=(0, 2, 3)
    # backward compatibility from 2.2.2 to 2.0.1
    if not os.path.isdir(forces_directory):
      forces_directory = '{}/forces'.format(self.directory)
      usecols=(0, 1, 2)
    subdirectories = sorted(os.listdir(forces_directory))
    times = numpy.empty(0)
    force_x, force_y = numpy.empty(0), numpy.empty(0)
    for subdirectory in subdirectories:
      forces_path = '{}/{}/{}.dat'.format(forces_directory, subdirectory, key)
      with open(forces_path, 'r') as infile:
        t, fx, fy = numpy.loadtxt(infile, dtype=float, comments='#', 
                                  usecols=usecols, unpack=True)
      times = numpy.append(times, t)
      force_x, force_y = numpy.append(force_x, fx), numpy.append(force_y, fy)
    self.force_x = Force(times, coefficient*force_x, 
                         name=('$C_d$' if force_coefficients else '$F_x$'))
    self.force_y = Force(times, coefficient*force_y, 
                         name=('$C_l$' if force_coefficients else '$F_y$'))


class CuIBMSimulation(Simulation):
  """Contains information about a cuIBM simulation."""
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

  def read_forces(self, force_coefficients=False, coefficient=1.0):
    """Reads forces from files.

    Parameters
    ----------
    force_coefficients: boolean
      Set to 'True' if force coefficients are required; default: False (i.e. forces).
    coefficient: float
      Force to force-coefficient scale; default: 1.0.
    """
    forces_path = '{}/forces'.format(self.directory)
    with open(forces_path, 'r') as infile:
      times, force_x, force_y = numpy.loadtxt(infile, dtype=float, 
                                              usecols=(0, 1, 2), unpack=True)
    self.force_x = Force(times, coefficient*force_x,
                         name=('$C_d$' if force_coefficients else '$F_x$'))
    self.force_y = Force(times, coefficient*force_y,
                         name=('$C_l$' if force_coefficients else '$F_y$'))

class PetIBMSimulation(Simulation):
  """Contains information about a PetIBM simulation."""
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

  def read_forces(self, force_coefficients=False, coefficient=1.0):
    """Reads forces from files.

    Parameters
    ----------
    force_coefficients: boolean
      Set to 'True' if force coefficients are required; default: False (i.e. forces).
    coefficient: float
      Force to force-coefficient scale; default: 1.0.
    """
    forces_path = '{}/forces.txt'.format(self.directory)
    with open(forces_path, 'r') as infile:
      times, force_x, force_y = numpy.loadtxt(infile, dtype=float, 
                                              usecols=(0, 1, 2), unpack=True)
    self.force_x = Force(times, coefficient*force_x,
                         name=('$C_d$' if force_coefficients else '$F_x$'))
    self.force_y = Force(times, coefficient*force_y,
                         name=('$C_l$' if force_coefficients else '$F_y$'))


class IBAMRSimulation(Simulation):
  """Contains information about a IBAMR simulation."""
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

  def read_forces(self, force_coefficients=False, coefficient=1.0):
    """Reads forces from files.

    Parameters
    ----------
    force_coefficients: boolean
      Set to 'True' if force coefficients are required; default: False (i.e. forces).
    coefficient: float
      Force to force-coefficient scale; default: 1.0.
    """
    forces_path = '{}/dataIB/ib_Drag_force_struct_no_0'.format(self.directory)
    with open(forces_path, 'r') as infile:
      times, force_x, force_y = numpy.loadtxt(infile, dtype=float, 
                                              usecols=(0, 4, 5), unpack=True)
    self.force_x = Force(times, coefficient*force_x,
                         name=('$C_d$' if force_coefficients else '$F_x$'))
    self.force_y = Force(times, coefficient*force_y,
                         name=('$C_l$' if force_coefficients else '$F_y$'))