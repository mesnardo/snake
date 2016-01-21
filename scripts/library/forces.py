# file: forces.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Collection of classes and functions to post-process forces 
#              acting on bodies.


import os
import sys

import numpy
from scipy import signal
from matplotlib import pyplot


class Force(object):
  """Contains info about a force."""
  def __init__(self, times, values, description=None):
    """Initializes the force with given values.

    Parameters
    ----------
    times: Numpy array of float
      Discrete time.
    values: Numpy array of float
      Instantaneous values of the force.
    description: string
      Description of the force; default: None.
    """
    self.description = description
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
  def __init__(self, description=None, directory=os.getcwd(), software=None, 
               coefficient=1.0):
    """Registers the simulations.

    Parameters
    ----------
    description: string
      Description of the simulation; default: None.
    directory: string
      Directory of the simulation; default: current working directory.
    software: string
      Name of the software used for the simulation; default: None.
    """
    self.description = description
    self.directory = directory
    self.software = software
    self.coefficient = coefficient
    self.print_registration()
    self.derive_class()

  def print_registration(self):
    """Prints global details of the simulation"""
    print('[info] registering simulation ...')
    print('\tdirectory: {}'.format(self.directory))
    print('\tdescription: {}'.format(self.description))
    print('\tsoftware: {}'.format(self.software))

  def derive_class(self):
    """Finds the appropriate child class based on the software used."""
    classDerivations = {'cuibm': CuIBMSimulation, 
                        'petibm': PetIBMSimulation, 
                        'openfoam': OpenFOAMSimulation,
                        'ibamr': IBAMRSimulation}
    try:
      self.__class__ = classDerivations[self.software]
    except KeyError:
      print('[error] software indicated: {}'.format(self.software))
      print('[error] simulation type should be one of the followings: '
            '{}'.format(derivations.keys()))
      sys.exit(0)

  def get_means(self, limits=[0.0, float('inf')], last_period=False, order=5, 
                display_coefficients=False):
    """Computes the time-averaged forces (or force-coefficients).

    Parameters
    ----------
    limits: list of floats
      Time-limits used to compute the mean; default: [0.0, +inf].
    last_period: bool
      Set 'True' if only the last period define the time-limits; default: False.
    order: int
      Number of neighboring points used to define an extremum; default: 5.

    Returns
    -------
    fx_mean, fy_mean: dict
      Time-limits and mean value for forces in each direction.
    """
    fx_mean = self.force_x.get_mean(limits=limits, last_period=last_period, order=order)
    fy_mean = self.force_y.get_mean(limits=limits, last_period=last_period, order=order)
    fx_name = ('<cd>' if display_coefficients else '<fx>')
    fy_name = ('<cl>' if display_coefficients else '<fy>')
    print('[info] averaging forces in x-direction between {} and {}:'.format(fx_mean['start'], 
                                                                             fx_mean['end']))
    print('\t{} = {}'.format(fx_name, fx_mean['value']))
    print('[info] averaging forces in y-direction between {} and {}:'.format(fy_mean['start'], 
                                                                             fy_mean['end']))
    print('\t{} = {}'.format(fy_name, fy_mean['value']))
    return fx_mean, fy_mean

  def get_strouhal(self, L=1.0, U=1.0, n_periods=1, order=5):
    """Computes the Strouhal number based on the frequency of the lift force.

    The frequency is beased on the lift history and is computed using the minima
    of the lift curve.

    Parameters
    ----------
    L: float
      Characteristics length of the body; default: 1.0.
    U: float
      Characteristics velocity of the body; default: 1.0.
    n_periods: integer
      Number of periods (starting from end) to average the Strouhal number; default: 1.
    order: integer
      Number of neighbors used on each side to define an extremum; default: 5.

    Returns
    -------
    strouhal: float
      The Strouhal number.
    """
    minima, _ = self.force_y.get_extrema(order=order)
    strouhals = L/U/( self.force_y.times[minima[-n_periods:]] 
                    - self.force_y.times[minima[-n_periods-1:-1]] )
    strouhal = strouhals.mean()
    print('[info] estimating the Strouhal number over the last {} period(s):'.format(n_periods))
    print('\tSt = {}'.format(strouhal))
    print('\tSt values used to average: {}'.format(strouhals))
    return strouhal

  def plot_forces(self, display_lift=True, display_drag=True,
                  limits=[0.0, float('inf'), 0.0, float('inf')],
                  title=None, save_name=None, show=False,
                  display_extrema=False, order=5, display_gauge=False,
                  other_simulations=[]):
    """Displays the forces into a figure.

    Parameters
    ----------
    display_lift: bool
      Set 'True' if the lift curve should be added to the figure; default: True.
    display_drag: bool
      Set 'True' if the drag curve should be added to the figure; default: True.
    limits: list of floats
      Limits of the axes [xmin, xmax, ymin, ymax]; default: [0.0, +inf, 0.0, +inf].
    title: string
      Title of the figure; default: None.
    save_name: string
      Name of the .PNG file to save; default: None (does not save).
    show: bool
      Set 'True' to display the figure; default: False.
    display_extrema: bool
      Set 'True' to emphasize the extrema of the curves; default: False.
    order: int
      Number of neighbors used on each side to define an extremum; default: 5.
    display_gauge: bool
      Set 'True' to display gauges to judge steady regime; default: False.
    other_simulations: list of Simulation objects
      List of other simulations to add to plot; default: [].
    """
    print('[info] plotting forces ...')
    pyplot.style.use('{}/styles/mesnardo.mplstyle'.format(os.environ['SCRIPTS']))
    fig, ax = pyplot.subplots(figsize=(8, 6))
    color_cycle = ax._get_lines.color_cycle
    pyplot.grid(True, zorder=0)
    pyplot.xlabel('time')
    pyplot.ylabel('forces' if self.force_x.description == '$F_x$' 
                           else 'force coefficients')
    forces = []
    if display_drag:
      forces.append(self.force_x)
    if display_lift:
      forces.append(self.force_y)
    for force in forces:
      color = next(color_cycle)
      pyplot.plot(force.times, force.values,
                  label=('{} - {}'.format(self.description.replace('_', ' '), 
                                          force.description) 
                         if self.description
                         else force.description),
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
                    label=('{} - {}'.format(simulation.description.replace('_', ' '), 
                                            force.description) 
                           if simulation.description
                           else force.description),
                    color=color, linestyle='--', zorder=10)
    pyplot.legend()
    pyplot.axis(limits)
    if title:
      pyplot.title(title)
    if save_name:
      images_directory = '{}/images'.format(self.directory)
      print('[info] saving figure in directory {} ...'.format(images_directory))
      if not os.path.isdir(images_directory):
        os.makedirs(images_directory)
      pyplot.savefig('{}/{}.png'.format(images_directory, save_name))
    if show:
      print('[info] displaying figure ...')
      pyplot.show()
    pyplot.close()


class OpenFOAMSimulation(Simulation):
  """Contains information about an OpenFOAM simulation."""
  def __init__(self):
    pass

  def read_forces(self, display_coefficients=False):
    """Reads forces from files.

    Parameters
    ----------
    display_coefficients: boolean
      Set to 'True' if force coefficients are required; default: False (i.e. forces).
    """
    if display_coefficients:
      info = {'directory': '{}/postProcessing/forceCoeffs'.format(self.directory),
              'description': 'force-coefficients',
              'x-direction': '$C_d$',
              'y-direction': '$C_l$',
              'usecols': (0, 2, 3)}
    else:
      info = {'directory': '{}/postProcessing/forces'.format(self.directory),
              'description': 'forces',
              'x-direction': '$F_x$',
              'y-direction': '$F_y$',
              'usecols': (0, 2, 3)}
    # backward compatibility from 2.2.2 to 2.0.1
    if not os.path.isdir(info['directory']):
      info['directory'] = '{}/forces'.format(self.directory)
      info['usecols'] = (0, 1, 2)
    print('[info] reading {} in {} ...'.format(info['description'], info['directory'])),
    subdirectories = sorted(os.listdir(info['directory']))
    times = numpy.empty(0)
    force_x, force_y = numpy.empty(0), numpy.empty(0)
    for subdirectory in subdirectories:
      forces_path = '{}/{}/{}.dat'.format(info['directory'], subdirectory, os.path.basename(info['directory']))
      with open(forces_path, 'r') as infile:
        t, fx, fy = numpy.loadtxt(infile, dtype=float, comments='#', 
                                  usecols=info['usecols'], unpack=True)
      times = numpy.append(times, t)
      force_x, force_y = numpy.append(force_x, fx), numpy.append(force_y, fy)
    self.force_x = Force(times, self.coefficient*force_x, 
                         description=info['x-direction'])
    self.force_y = Force(times, self.coefficient*force_y, 
                         description=info['y-direction'])
    print('done')


class CuIBMSimulation(Simulation):
  """Contains information about a cuIBM simulation."""
  def __init__(self):
    pass

  def read_forces(self, display_coefficients=False):
    """Reads forces from files.

    Parameters
    ----------
    display_coefficients: boolean
      Set to 'True' if force coefficients are required; default: False (i.e. forces).
    """
    forces_path = '{}/forces'.format(self.directory)
    print('[info] reading values from {} ...'.format(forces_path)),
    with open(forces_path, 'r') as infile:
      times, force_x, force_y = numpy.loadtxt(infile, dtype=float, 
                                              usecols=(0, 1, 2), unpack=True)
    self.force_x = Force(times, self.coefficient*force_x,
                         description=('$C_d$' if display_coefficients else '$F_x$'))
    self.force_y = Force(times, self.coefficient*force_y,
                         description=('$C_l$' if display_coefficients else '$F_y$'))
    print('done')


class PetIBMSimulation(Simulation):
  """Contains information about a PetIBM simulation."""
  def __init__(self):
    pass

  def read_forces(self, display_coefficients=False):
    """Reads forces from files.

    Parameters
    ----------
    display_coefficients: boolean
      Set to 'True' if force coefficients are required; default: False (i.e. forces).
    """
    forces_path = '{}/forces.txt'.format(self.directory)
    print('[info] reading values from {} ...'.format(forces_path)),
    with open(forces_path, 'r') as infile:
      times, force_x, force_y = numpy.loadtxt(infile, dtype=float, 
                                              usecols=(0, 1, 2), unpack=True)
    self.force_x = Force(times, self.coefficient*force_x,
                         description=('$C_d$' if display_coefficients else '$F_x$'))
    self.force_y = Force(times, self.coefficient*force_y,
                         description=('$C_l$' if display_coefficients else '$F_y$'))
    print('done')


class IBAMRSimulation(Simulation):
  """Contains information about a IBAMR simulation."""
  def __init__(self):
    pass

  def read_forces(self, display_coefficients=False):
    """Reads forces from files.

    Parameters
    ----------
    display_coefficients: boolean
      Set to 'True' if force coefficients are required; default: False (i.e. forces).
    """
    forces_path = '{}/dataIB/ib_Drag_force_struct_no_0'.format(self.directory)
    print('[info] reading values from {} ...'.format(forces_path)),
    with open(forces_path, 'r') as infile:
      times, force_x, force_y = numpy.loadtxt(infile, dtype=float, 
                                              usecols=(0, 4, 5), unpack=True)
    self.force_x = Force(times, self.coefficient*force_x,
                         description=('$C_d$' if display_coefficients else '$F_x$'))
    self.force_y = Force(times, self.coefficient*force_y,
                         description=('$C_l$' if display_coefficients else '$F_y$'))
    print('done')