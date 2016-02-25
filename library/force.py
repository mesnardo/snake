# file: force.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Implementation of the class `Force`.


import numpy
from scipy import signal


class Force(object):
  """Contains info about a force."""
  def __init__(self, times, values):
    """Initializes the force with given values.

    Parameters
    ----------
    times: Numpy array of float
      Discrete time.
    values: Numpy array of float
      Instantaneous values of the force.
    """
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