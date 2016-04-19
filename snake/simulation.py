# file: Simulation.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Information related to a simulation.


import os
import sys

import numpy
from matplotlib import pyplot
try:
  pyplot.style.use('{}/styles/mesnardo.mplstyle'.format(os.environ['SNAKE']))
except:
  pass
import pandas

from .field import Field
from .force import Force


class Simulation(object):
  """Simulation manager."""
  def __init__(self, description=None, directory=os.getcwd(), software=None, **kwargs):
    """Registers the simulations.

    Parameters
    ----------
    description: string
      Description of the simulation; default: None.
    directory: string
      Directory of the simulation; default: current working directory.
    software: string
      Name of the software used for the simulation; default: None.
    **kwargs: dictionary
      Other attributes to create.
    """
    try:
      self.description = description.replace('_', ' ')
    except:
      self.description = description
    self.directory = directory
    self.software = software
    for key, value in kwargs.iteritems():
      setattr(self, key, value)
    self.print_registration()
    self.derive_class()
    self.fields = {}
    self.forces = []

  def print_registration(self):
    """Prints global details of the simulation"""
    print('[info] registering simulation ...')
    print('\t- directory: {}'.format(self.directory))
    print('\t- description: {}'.format(self.description))
    print('\t- software: {}'.format(self.software))

  def derive_class(self):
    """Finds the appropriate child class based on the software used."""
    if self.software == 'cuibm':
      from .cuibm.simulation import CuIBMSimulation
      self.__class__ = CuIBMSimulation
    elif self.software == 'petibm':
      from .petibm.simulation import PetIBMSimulation
      self.__class__ = PetIBMSimulation
    elif self.software == 'openfoam':
      from .openfoam.simulation import OpenFOAMSimulation
      self.__class__ = OpenFOAMSimulation
    elif self.software == 'ibamr':
      from .ibamr.simulation import IBAMRSimulation
      self.__class__ = IBAMRSimulation
    else:
      print('[error] software indicated: {}'.format(self.software))
      print('[error] simulation type should be one of the followings: '
            'cuibm, petibm, openfoam, or ibamr')
      sys.exit(0)

  def get_mean_forces(self, limits=(0.0, float('inf')), last_period=False, order=5):
    """Computes the time-averaged forces (or force-coefficients).

    Parameters
    ----------
    limits: 2-list of floats, optional
      Time-limits used to compute the mean; 
      default: [0.0, +inf].
    last_period: boolean, optional
      Set 'True' if only the last period define the time-limits; 
      default: False.
    order: integer, optional
      Number of neighboring points used to define an extremum; 
      default: 5.
    """
    for index, force in enumerate(self.forces):
      self.forces[index].get_mean(limits=limits, last_period=last_period, order=order)

  def get_strouhal(self, 
                   L=1.0, U=1.0, 
                   limits=(0.0, float('inf')), order=5, 
                   index=1):
    """Computes the Strouhal number based on the frequency of the force signal.

    Parameters
    ----------
    L: float, optional
      Characteristics length of the body; 
      default: 1.0.
    U: float, optional
      Characteristics velocity of the body; 
      default: 1.0.
    limits: 2-tuple of floats, optional
      Time-limits used as reference to compute the Strouhal number; 
      default: (0.0, inf).
    order: integer, optional
      Number of neighbors used on each side to define an extremum; 
      default: 5.
    index: integer, optional
      Index of the list of forces to use to compute the Strouhal number;
      default: 1 (most of the time, 1 corresponds to the lift force).
    """
    return self.forces[index].get_strouhal(L=L, U=U, limits=limits, order=order)

  def plot_forces(self, 
                  indices=None, labels=None,
                  display_coefficients=False, coefficient=1.0,
                  limits=[0.0, float('inf'), 0.0, float('inf')],
                  save_name=None, show=False,
                  display_extrema=False, order=5, display_guides=False, fill_between=False,
                  other_simulations=[], other_coefficients=[]):
    """Displays the forces into a figure.

    Parameters
    ----------
    indices: list of integers, optional
      List of the index of each force to display;
      default: None (all forces).
    labels: list of strings, optional
      Labels for each force to display;
      default: None (default labels are set).
    display_coefficients: boolean, optional
      Set 'True' if plotting force coefficients instead of forces; 
      default: False.
    coefficient: float, optional
      scale coefficient to convert a force in a force coefficient; 
      default: 1.0.
    limits: 4-list of floats, optional
      Limits of the axes [xmin, xmax, ymin, ymax]; 
      default: [0.0, +inf, 0.0, +inf].
    save_name: string, optional
      Name of the .PNG file to save; 
      default: None (does not save).
    show: boolean, optional
      Set 'True' to display the figure; 
      default: False.
    display_extrema: boolean, optional
      Set 'True' to emphasize the extrema of the curves; 
      default: False.
    order: integer, optional
      Number of neighbors used on each side to define an extreme; 
      default: 5.
    display_guides: boolean, optional
      Set 'True' to display guides to judge steady regime; 
      default: False.
    fill_between: boolean, optional
      Set 'True' to fill between lines defined by the extrema; 
      default: False.
    other_simulations: list of Simulation objects, optional
      List of other simulations to add to plot; 
      default: [].
    other_coefficients: list of floats, optional
      Scale coefficients for each other simulation; 
      default: [].
    """
    if not (save_name or show):
      return
    print('[info] plotting forces ...')
    fig, ax = pyplot.subplots(figsize=(8, 6))
    color_cycle = ax._get_lines.prop_cycler
    ax.grid(True, zorder=0)
    ax.set_xlabel('time')
    ax.set_ylabel('force coefficients' if display_coefficients else 'forces')
    if not labels:
      labels = (['$C_d$', '$C_l$', '$C_m$'] if display_coefficients
                else ['$F_x$', '$F_y$', '$F_z$'])
    if not indices:
      indices = numpy.arange(0, len(self.forces)+1, 1)
    for index, force in enumerate(self.forces):
      if index not in indices:
        continue
      color = next(color_cycle)['color']
      line, = ax.plot(force.times, coefficient*force.values,
              label=' - '.join(filter(None, [self.description, labels[index]])),
              color=color, linestyle='-', zorder=9)
      if display_extrema:
        minima, maxima = force.get_extrema(order=order)
        ax.scatter(force.times[minima], coefficient*force.values[minima],
                   c=color, marker='o', zorder=10)
        ax.scatter(force.times[maxima], coefficient*force.values[maxima],
                   c=color, marker='o', zorder=10)
        if fill_between:
          line.remove()
          ax.plot(force.times[minima], coefficient*force.values[minima],
                  color='white', linestyle='-', zorder=9)
          ax.plot(force.times[maxima], coefficient*force.values[maxima],
                  color='white', linestyle='-', zorder=9)
          times = numpy.concatenate((force.times[minima], 
                                     force.times[maxima][::-1]))
          values = coefficient*numpy.concatenate((force.values[minima], 
                                                  force.values[maxima][::-1]))
          ax.fill(times, values, 
                  label=' - '.join(filter(None, [self.description, labels[index]])),
                  facecolor=color, alpha=0.8, zorder=8)
        if display_guides:
          ax.axhline(coefficient*force.values[minima[-1]],
                     color=color, linestyle=':', zorder=10)
          ax.axhline(coefficient*force.values[maxima[-1]],
                     color=color, linestyle=':', zorder=10)
    
    for i, simulation in enumerate(other_simulations):
      for index, force in enumerate(simulation.forces):
        if index not in indices:
          continue
        color = next(color_cycle)['color']
        line, = ax.plot(force.times, other_coefficients[i]*force.values,
                        label=' - '.join(filter(None, [simulation.description, labels[index]])),
                        color=color, linestyle='--', zorder=9)
        if fill_between:
          line.remove()
          minima, maxima = force.get_extrema(order=order)
          ax.scatter(force.times[minima], other_coefficients[i]*force.values[minima],
                     c=color, marker='o', zorder=10)
          ax.scatter(force.times[maxima], other_coefficients[i]*force.values[maxima],
                     c=color, marker='o', zorder=10)
          ax.plot(force.times[minima], other_coefficients[i]*force.values[minima],
                  color='white', linestyle='-', zorder=9)
          ax.plot(force.times[maxima], other_coefficients[i]*force.values[maxima],
                  color='white', linestyle='-', zorder=9)
          times = numpy.concatenate((force.times[minima], 
                                     force.times[maxima][::-1]))
          values = other_coefficients[index]*numpy.concatenate((force.values[minima], 
                                                                force.values[maxima][::-1]))
          ax.fill(times, values, 
                  label=' - '.join(filter(None, [simulation.description, info[index]])),
                  facecolor=color, alpha=0.5, zorder=7)
    legend = ax.legend()
    legend.set_zorder(20) # put legend on top
    ax.axis(limits)
    if save_name:
      images_directory = '{}/images'.format(self.directory)
      print('[info] saving figure {}.png in directory {} ...'.format(save_name, images_directory))
      if not os.path.isdir(images_directory):
        os.makedirs(images_directory)
      pyplot.savefig('{}/{}.png'.format(images_directory, save_name))
    if show:
      print('[info] displaying figure ...')
      pyplot.show()
    pyplot.close()

  def create_dataframe_forces(self, 
                              indices=None, display_strouhal=False, columns=None,
                              display_coefficients=False, coefficient=1.0,
                              other_simulations=[], other_coefficients=[]):
    """Creates a data frame with Pandas to display 
    time-averaged forces (or force coefficients).

    Parameters
    ----------
    indices: list of integers, optional
      List of the index of each force to display in the dataframe;
      default: None (all forces);
    display_strouhal: boolean, optional
      Set 'True' to display the mean Strouhal number in the dataframe;
      default: False.
    display_coefficients: boolean, optional
      Set 'True' if force coefficients are to be displayed; 
      default: False.
    coefficient: float, optional
      Scale factor to convert a force into a force-coefficient; 
      default: 1.0.
    other_simulations: list of Simulation objects, optional
      List of other simulations used for comparison; 
      default: [].
    other_coefficients: list of floats, optional
      List of scale factors of other simulations; 
      default: [].

    Returns
    -------
    dataframe: Pandas dataframe
      The dataframe of the simulation.
    """
    print('[info] instantaneous signals are averaged between '
          '{} and {} time-units.'.format(self.forces[0].mean['start'], 
                                         self.forces[0].mean['end']))
    descriptions = ['<no description>' if not self.description else self.description]
    if not indices:
      indices = numpy.arange(0, len(self.forces)+1, 1)
    if not columns:
      columns = (['<Cd>', '<Cl>', '<Cm>'] if display_coefficients else ['<Fx>', '<Fy>', '<Fz>'])
    columns = numpy.array(columns)
    values = []
    for index, force in enumerate(self.forces):
      if index not in indices:
        continue
      values.append('{0:.4f}'.format(coefficient*force.mean['value']))
    dataframe = pandas.DataFrame([values],
                                 index=descriptions,
                                 columns=columns[indices])
    if display_strouhal:
      strouhal = self.forces[1].strouhal
      print('[info] Strouhal number is averaged '
            'over the {} periods of the lift curve '
            'between {} and {} time-units.'
            ''.format(strouhal['n-periods'],
                      strouhal['time-limits'][0], strouhal['time-limits'][1]))
      dataframe['<St>'] = '{0:.4f}'.format(strouhal['mean'])
    for index, simulation in enumerate(other_simulations):
      dataframe = dataframe.append(simulation.create_dataframe_forces(
                                        indices=indices,
                                        display_strouhal=display_strouhal,
                                        display_coefficients=display_coefficients,
                                        coefficient=other_coefficients[index]))
    return dataframe