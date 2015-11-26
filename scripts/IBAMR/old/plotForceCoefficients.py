#!/bin/python 
# file: plotForceCoefficients.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# brief: Plots and analyzes the force coefficients from an IBAMR simulation.


import os
import collections

import argparse
import numpy
import scipy.signal
import bokeh.plotting
import bokeh.models
import bokeh.io


TOOLS = 'pan, box_zoom, wheel_zoom, crosshair, hover, resize, reset'


def read_inputs():
  """Parses the command-line."""
  # create parser
  parser = argparse.ArgumentParser(description='Plots the force coefficients '
                                               'for an IBAMR simulation.',
                                   formatter_class = argparse.ArgumentDefaultsHelpFormatter)
  # fill parser with arguments
  parser.add_argument('--name', '-n', dest='name', type=str, 
                      default='IBAMR simulation',
                      help='name of the IBAMR simulation')
  parser.add_argument('--directory', '-d', dest='directory', type=str, 
                      default=os.getcwd(),
                      help='directory of the simulation')
  parser.add_argument('--force-file', '-ff', dest='force_file', type=str,
                      default='Cylinder2dStr/Cylinder2d_Drag_force_struct_no_0',
                      help='Path of the force file relative to the directory')
  parser.add_argument('--no-drag', dest='drag', action='store_false',
                      help='does not plot and analyze the drag coefficient')
  parser.add_argument('--no-lift', dest='lift', action='store_false',
                      help='does not plot and analyze the lift coefficient')
  parser.add_argument('--no-sideforce', dest='sideforce', action='store_false',
                      help='does not plot and analyze the side-force coefficient')
  parser.add_argument('--start', '-t1', dest='start', type=float, default=0.0,
                      help='starting-time to compute mean coefficients')
  parser.add_argument('--end', '-t2', dest='end', type=float, default=float('inf'),
                      help='ending-time to compute mean coefficients')
  parser.add_argument('--last-period', dest='last_period', action='store_true',
                      help='computes the mean coefficients over the last period')
  parser.add_argument('--order', dest='order', type=int, default=100,
                      help='number of points on each side to use for comparison '
                           'when calculating the extrema of the force coefficient')
  parser.add_argument('--extrema', dest='extrema', action='store_true',
                      help='displays the extrema on the figure')
  parser.add_argument('--guide', dest='guide', action='store_true',
                      help='displays guide-lines to check steady periodic regime')
  parser.set_defaults(drag=True, lift=True, sideforce=False, last_period=False,
                      extrema=False, guide=False)
  return parser.parse_args()


class ForceCoefficient(object):
  """Contains info about a force coefficient."""
  def __init__(self, name, times, values):
    """Stores the instantaneous force ceofficient.
    
    Parameters
    ----------
    name: str
      Description of the force coefficient.
    times: numpy.array(float)
      Discrete time.
    values: numpy.array(float)
      Intantaneous force coefficients.
    """
    self.name = name
    self.times = times
    self.values = values
      
  def get_mean(self, start=0.0, end=float('inf'), last_period=False, order=100):
    """Computes the mean coefficient.
    
    Parameters
    ----------
    start: float
      Starting time; default: 0.0.
    end: float
      Ending time; default: float('inf').
    last_period: bool
      Computes the mean coefficient over the last period; default: False.
    order: int
      When calculated over the last period, this is the number of points 
      on each side to use for comparison; default: 5.
    
    Returns
    -------
    start: float
      Starting-time considered for the mean value.
    end: float
      Ending-time considered for the mean value.
    mean: float
      The mean value.
    """
    if last_period:
      self.get_extrema(order=order)
      mask = numpy.arange(self.maxima[-2], self.maxima[-1]+1)
      start = self.times[self.maxima[-2]]
      end = self.times[self.maxima[-1]]
    else:
      end = min(end, self.times[-1]) 
      mask = numpy.where(numpy.logical_and(self.times >= start,
                                           self.times <= end))[0]
    self.mean = numpy.mean(self.values[mask])
    return start, end, self.mean

  def get_extrema(self, order=100):
    """Computes the extremum indices (minima and maxima) of the force coefficient.

    Parameters
    ----------
    order: int
      Number of points on each side to use for comparison; default: 5.

    Returns
    -------
    minima, maxima: numpy.1darray(int)
      Indices of the minima and extrema of the force coefficient.
    """
    minima = scipy.signal.argrelextrema(self.values, numpy.less_equal, order=order)[0][:-1]
    maxima = scipy.signal.argrelextrema(self.values, numpy.greater_equal, order=order)[0][:-1]
    # remove indices that are too close
    self.minima = minima[numpy.append(True, minima[1:]-minima[:-1] > order)]
    self.maxima = maxima[numpy.append(True, maxima[1:]-maxima[:-1] > order)]
    return self.minima, self.maxima

  def get_strouhal(self):
    """Computes the Strouhal number.

    Returns
    -------
    strouhal: float
      The Strouhal number.
    """
    start, end, _ = self.get_mean(last_period=True)
    try:
      self.strouhal = 1.0/(self.times[self.maxima[-1]]-self.times[self.maxima[-2]])
    except:
      self.strouhal = float('inf')
    return self.strouhal

  def plot(self, title=None, extrema=False, guide=False):
    """Plots the instantaneous force coefficient.
    
    Parameters
    ----------
    title: str
      Title of the figure; default: None.
    extrema: bool
      Displays extrema on the figure; default: False.
    guide: bool
      Displays guide-lines on the figure to check steady periodic regime; default: False.  

    Returns
    -------
    figure: bokeh object
      The figure to show.
    """
    figure = bokeh.plotting.figure(title=title,
                                   background_fill='lightgrey',
                                   plot_width=600, plot_height=300,
                                   tools=TOOLS)
    figure.ygrid.grid_line_color = 'white'
    figure.ygrid.grid_line_width = 2
    figure.xaxis.axis_label = 'time'
    figure.yaxis.axis_label = self.name
    figure.axis.major_label_text_font_size = '12pt'
    figure.axis.major_label_text_font_style = 'bold'
    figure.axis.axis_line_color = None
    figure.axis.minor_tick_out = 0
    figure.axis.major_tick_out = 0
    figure.axis.major_tick_in = 5
    figure.axis.major_tick_line_width = 2
    figure.axis.major_tick_line_color = 'white'
    hover = figure.select(dict(type=bokeh.models.HoverTool))
    hover.tooltips = [('time', '$x'), ('value', '$y')]
    figure.line(self.times, self.values,
                name='force-coefficient',
                size=12, color='blue', line_width=2, alpha=0.5)
    if extrema or guide:
      self.get_extrema()
    if extrema:
      figure.scatter(self.times[self.minima], self.values[self.minima],
                     name='minima',
                     size=6, color='blue', alpha=1.0)
      figure.scatter(self.times[self.maxima], self.values[self.maxima],
                     name='maxima',
                     size=6, color='red', alpha=1.0)
      hover.names = ['minima', 'maxima']
    if guide:
      figure.line(self.times, self.values[self.minima[-1]],
                  name='guide-minima',
                  size=12, color='blue', line_width=1, line_dash='4 4', alpha=1.0)
      figure.line(self.times, self.values[self.maxima[-1]],
                  name='guide-maxima',
                  size=12, color='red', line_width=1, line_dash='4 4', alpha=1.0)
    return figure


class IBAMRSimulation(object):
  """Contains info about force coefficients of a IBAMR simulation."""
  def __init__(self, name, directory):
    """Stores the name and the directory of the simulation.
    
    Parameters
    ----------
    name: str
      Name of the IBAMR simulation.
    directory: str
      Directory of the IBAMR simulation.
    """
    self.name = name
    self.directory = directory
  
  def read_force_coefficients(self, file_path, forces=['drag', 'lift']):
    """Reads from the file and stores the force coefficients.

    Parameters
    ----------
    file_path: str
      Path of the file containing the instantaneous forces.
    forces: list(str)
      List of forces to read from file; default: ['drag', 'lift'].
    """
    print('Reading file containing forces...')
    with open(file_path, 'r') as infile:
      data = numpy.loadtxt(infile, dtype=float)
    self.force_coefficients = collections.OrderedDict()
    if 'drag' in forces:
      print('Creating drag coefficient...')
      self.force_coefficients['drag'] = ForceCoefficient(name='drag coefficient',
                                                         times=data[:-1, 0], 
                                                         values=-2.0*data[:-1, 4])
    if 'lift' in forces:
      print('Creating lift coefficient...')
      self.force_coefficients['lift'] = ForceCoefficient(name='lift coefficient',
                                                         times=data[:-1, 0], 
                                                         values=-2.0*data[:-1, 5])
    if 'sideforce' in forces:
      print('Creating sideforce coefficient...')
      self.force_coefficients['lift'] = ForceCoefficient(name='sideforce coefficient',
                                                         times=data[:-1, 0], 
                                                         values=-data[:-1, 6])
  
  def plot_force_coefficients(self, forces=['drag', 'lift'], extrema=False,
                              guide=False, notebook=False):
    """Plots the instantaneous force coefficients.

    Parameters
    ----------
    forces: list(str)
      List of force coefficients to plot; default: ['drag', 'lift'].
    extrema: bool
      Displays the extrema on the figure; default:False.
    guide: bool
      Displays guide-lines on the figure to check steady periodic regime; default: False.
    notebook: bool
      Displays the figures within IPython Notebook if true; default: False.
    """
    print('Plotting force coefficients...')
    images_directory = '{}/images'.format(self.directory)
    if not os.path.isdir(images_directory):
      os.makedirs(images_directory)
    if notebook:
     bokeh.io.output_notebook()
    for name, force_coefficient in self.force_coefficients.iteritems():
      if name in forces:
        figure = force_coefficient.plot(title=self.name, extrema=extrema, guide=guide)
        if not notebook:
          bokeh.plotting.output_file('{}/{}Coefficient.html'.format(images_directory, name))
        bokeh.plotting.show(figure)

  def get_mean_coefficients(self, start=0.0, end=float('inf'), last_period=False, 
                            order=100, print_values=False):
    """Computes the mean force coefficients.

    Parameters
    ----------
    start: float
      Starting-time value to consider; default: 0.0.
    end: float
      Ending-time value to consider; default: float('inf').
    last_period: bool
      Computes the mean coefficients over the last period; default: False.
    order: int
      Number of points to consider for comparison on each side 
      when defining an extremum; default: 5.
    print_values: bool
      Prints the mean force coefficients if True; default: False.

    Returns
    -------
    means: dict('start', 'end', 'value')
      The mean force coefficients and the limits of integration.
    """
    print('Computing mean force coefficients...')
    self.means = {}
    for name, force_coefficient in self.force_coefficients.iteritems():
      start, end, value = self.force_coefficients[name].get_mean(start=start, 
                                                                 end=end, 
                                                                 last_period=last_period,
                                                                 order=order)
      self.means[name] = {'start': start, 'end': end, 'value': value}
    if print_values:
      self.print_mean_coefficients()
    return self.means

  def print_mean_coefficients(self):
    """Prints the mean force coefficients."""
    for name, force_coefficient in self.force_coefficients.iteritems():
      print('<{} coefficient> = {} \t ({}, {})'.format(name, 
                                                       self.means[name]['value'],
                                                       self.means[name]['start'],
                                                       self.means[name]['end']))

  def get_strouhal_number(self, print_values=False):
    """Computes the Strouhal number based on the instantaneous lift coefficient.

    Parameters
    ----------
    print_values: bool
      Prints the Strouhal number if True; default: False.

    Returns
    -------
    strouhal: float
      The Strouhal number.
    """
    if 'lift' in self.force_coefficients:
      print('Computing the Strouhal number...')
      self.strouhal = self.force_coefficients['lift'].get_strouhal()
    else:
      print('ERROR: lift not available, cannot compute the Strouhal number.')
      self.strouhal = None
    if print_values:
      self.print_strouhal_number()
    return self.strouhal

  def print_strouhal_number(self):
    """Prints the Strouhal number."""
    print('Strouhal number = {}'.format(self.strouhal))


def main():
  """Plots and analyzes the force coefficients from an IBAMR simulations."""
  # parse command-line
  parameters = read_inputs()

  # list forces to analyze
  forces = []
  if parameters.drag: forces.append('drag')
  if parameters.lift: forces.append('lift')
  if parameters.sideforce: forces.append('sideforce')

  simulation = IBAMRSimulation(name=parameters.name, directory=parameters.directory)
  simulation.read_force_coefficients(file_path='{}/{}'.format(parameters.directory, 
                                                              parameters.force_file),
                                     forces=forces)
  simulation.get_mean_coefficients(start=parameters.start, end=parameters.end,
                                   last_period=parameters.last_period,
                                   order=parameters.order,
                                   print_values=True)
  simulation.get_strouhal_number(print_values=True)
  simulation.plot_force_coefficients(forces=forces, extrema=parameters.extrema, 
                                     guide=parameters.guide)


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))
