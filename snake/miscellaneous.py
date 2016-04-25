# file: miscellaneous.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# brief: Contains diverse functions and classes.


import os
import sys
import re
import argparse
import collections

try:
  import numpy
  from scipy import misc
  from matplotlib import pyplot, gridspec
except:
  pass
try:
  style_path = os.path.join(os.environ['SNAKE'], 'snake',
                            'styles', 'mesnardo.mplstyle')
  pyplot.style.use(style_path)
except:
  pass

try:
  from IPython.display import HTML, Image, display
  import ipywidgets
except ImportError:
  print('[warning] could not import ipywidgets')


class RedirectOutput(object):
  """Context manager to redirect stdout to a given file."""
  def __init__(self, stdout=''):
    self.stdout = stdout

  def __enter__(self):
    self.sys_stdout = sys.stdout

    if self.stdout:
      sys.stdout = open(self.stdout, 'w')

  def __exit__(self, exc_type, exc_value, traceback):
    sys.stdout = self.sys_stdout


class ReadOptionsFromFile(argparse.Action):
  """Container to read parameters from file."""
  def __call__(self, parser, namespace, values, option_string=None):
    """Fills the namespace with parameters read in file."""
    with values as infile:
      lines = [element for line in infile.readlines()
                   for element in line.strip().split()
                    if not line.startswith('#')]
      lines = [os.path.expandvars(line) if '$' in line else line 
               for line in lines[:]]
    parser.parse_args(lines, namespace)


def display_image(figure):
  if not os.path.isfile(figure):
    print('Image not available')
  display(Image(figure))


def get_images(directory, prefix=None, steps=None):
  """Returns the list of image paths of interest.

  Parameters
  ----------
  directory: string
    Directory with images.
  prefix: string
    Prefix shared by all images; default: None.
  steps: list of integers
    List of time-steps to consider; default: None.

  Returns
  -------
  images: list of strings
    List containing the absolute path of each image of interest.
  """
  if not os.path.isdir(directory):
    print('[error] {} is not a directory'.format(directory))
    return
  try:
    check = not any(steps)
  except:
    check = not steps
  if check:
    images =  sorted([os.path.join(directory, image) 
                      for image in os.listdir(directory)])
  else:
    if not prefix:
      prefix = re.match(r"([a-z]+)([0-9]+)", 
                        os.listdir(directory)[0], 
                        re.I).groups()[0]
    if all(isinstance(step, int) for step in steps):
      images = [os.path.join(directory, '{}{:0>7}.png'.format(prefix, step))
                for step in steps]
    else:
      images = [os.path.join(directory, '{}{:06.2f}.png'.format(prefix, step))
                for step in steps]
  return images


def create_slider(values, description='value'):
  """Returns the widget slider.
  
  Parameters
  ----------
  values: list of floats
    Values to store in the widget.
  description: string
    A description of the widget; default: 'value'.
  """
  return ipywidgets.FloatSlider(description=description, value=values[0],
                                min=values[0], max=round(values[-1], 2), 
                                step=values[1]-values[0])


def get_forces(path=None, limits=[0.0, float('inf')]):
  """Reads the forces from file.

  Parameters
  ----------
  path: string
    Path of the forces file; default: None.
  limits: list of floats
    Time-limits of interest; default: [0.0, inf].

  Returns
  -------
  forces: dict of Numpy 1d arrays of floats
    Keys are 'time' (discrete time), 'x', and 'y' (forces in x- and y-directions).
  """
  if not path:
    paths_to_test = [os.path.join(os.getcwd(), file_name) 
                     for file_name in ['forces', 'forces.txt']]
    for path_to_test in paths_to_test:
      file_in_directory = os.path.isfile(file_test)
      if os.path.isfile(path_to_test):
        path = path_to_test
  with open(path, 'r') as infile:
    time, fx, fy = numpy.loadtxt(infile, dtype=float, 
                                 comments='#', unpack=True)
  mask = numpy.where(numpy.logical_and(time >= limits[0],
                                       time <= limits[1]))[0]
  return {'time': time[mask], 'x': fx[mask], 'y': fy[mask]}


def plot_forces(ax, forces, tic=None, ylim=[0.0, 1.5]):
  """Plots forces on given axes.

  Parameters
  ----------
  ax: Axes
    The axes to draw to.
  forces: dict of Numpy 1d arrays of floats
    Keys are 'time' (discrete time), 'x', and 'y' (forces in x- and y-directions).
  tic: float
    Vertical line to plot (used as a gauge); default: None.
  ylim: list of floats
    y-limits of the axes; default: [0.0, 1.5].

  Returns
  -------
  ax: Axes
    The augmented axes.
  """
  ax.grid(True, zorder=0)
  ax.set_xlabel('time')
  ax.set_ylabel('forces')
  line_fx, = ax.plot(forces['time'], forces['x'], label='$f_x$',
                     color='#1b9e77', linestyle='-', linewidth=2,
                     zorder=10)
  line_fy, = ax.plot(forces['time'], forces['y'], label='$f_y$',
                     color='#d95f02', linestyle='-', linewidth=2,
                     zorder=10)
  ax.axvline(tic, color='grey',linestyle='--', linewidth=2, zorder=10)
  ax.legend(fontsize=20)
  ax.set_ylim(ylim)
  return ax


def plot_image(ax, image_path):
  """Displays an given image on a given axes.

  Parameters
  ----------
  ax: Axes
    The axes to work on.
  image_path: string
    Path of the image to display.

  Returns
  -------
  ax: Axes
    The augmented axes.
  """
  pyplot.axis('off')
  ax.imshow(misc.imread(image_path))
  return ax


def displayer(directories=[os.getcwd()], time=(), openfoam=False):
  """Interactively displays multiple images in a Jupyter Notebook with ipywidgets.

  Parameters
  ----------
  directories: list of strings, optional
    Path of folders containing images to display;
    default: current directory.
  time: 3-tuple, optional
    Temporal limits and time-increment to choose which images to display;
    default: empty tuple (all images in the folder).
  openfoam: boolean, optional
    Set 'True' if OpenFOAM simulation;
    default: False (not an OpenFOAM simulation).

  Returns
  -------
  The interactive display.
  """
  # check parameter is a list, if not convert into a list
  try:
    assert isinstance(directories, (list, tuple))
    assert not isinstance(directories, basestring)
  except:
    directories = [directories]
  all_images = []
  if not time:
    for directory in directories:
      all_images.append(get_images(directory))
    slider = create_slider(description='index', values=numpy.arange(len(all_images[0])))
  else:
    times = numpy.arange(time[0], time[1]+time[2]/2.0, time[2])
    if openfoam:
      steps = times
    else:
      steps = numpy.rint(times/time[3]).astype(int)
    for directory in directories:
      all_images.append(get_images(directory, steps=steps))
    slider = create_slider(description='time', values=times)

  def create_view(tic):
    if not time:
      index = int(round(tic))
    else:
      index = numpy.where(numpy.abs(times-tic) <= 1.0E-06)[0][0]
    for images in all_images:
      display(Image(filename=images[index]))

  ipywidgets.interact(create_view, tic=slider)


def displayer_with_forces(images_directory=os.getcwd(), forces_path=None,
                          time=(), ylim=[0.0, 3.0], openfoam=False):
  """Displays images and forces interactively in a notebook.

  Parameters
  ----------
  images_directory: string
    Directory containing images to display; default: $PWD.
  forces_path: string
    Path of the forces file; default: None (do not display forces).
  time: tuple of floats
    Contains info about times to display 
    (start, end, saving-increment, time-increment);
    default: () (display all images and only images).
  ylim: list of floats
    y-axis limits of the forces plot; default: [0.0, 3.0].
  openfoam: bool
    Set to 'True' if OpenFOAM simulation 
    (images do not have the same naming convention); 
    default: False.
  """
  if not os.path.isdir(images_directory):
    print('[error] {} is not a directory'.format(images_directory))
    return
  elif not time:
    images = get_images(images_directory)
    slider = create_slider(description='index', values=numpy.arange(len(images)))
    forces_path = None
  else:
    times = numpy.arange(time[0], time[1]+time[2]/2.0, time[2])
    if openfoam:
      steps = times
    else:
      steps = numpy.rint(times/time[3]).astype(int)
    images = get_images(images_directory, steps=steps)
    slider = create_slider(description='time', values=times)
  if forces_path:
    forces = get_forces(path=forces_path, limits=list(time[:2]))

  def create_view(tic):
    if not time:
      index = int(round(tic))
    else:
      index = numpy.where(numpy.abs(times-tic) <= 1.0E-06)[0][0]
    if not forces_path:
      display(Image(filename=images[index]))
    else:
      fig = pyplot.figure(num=0, figsize=(15, 15))
      gs = gridspec.GridSpec(2, 1, height_ratios=[1, 5])
      ax0 = pyplot.subplot(gs[0])
      plot_forces(ax0, forces, tic=tic, ylim=ylim)
      ax1 = pyplot.subplot(gs[1])
      plot_image(ax1, images[index])

  ipywidgets.interact(create_view, tic=slider)


def load_style(file_path):
  """Loads the style.

  Parameters
  ----------
  file_path: string
    Path of the .css file.
  """
  style_path = os.path.join(os.environ['SNAKE'], 'snake', 
                            'styles', 'mesnardo.css')
  style = HTML(open(style_path ,'r').read())
  display(style)
