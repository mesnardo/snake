# file: Field.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Implementation of the class `Field`.


import os

import numpy
from matplotlib import pyplot, cm
# load default style of matplotlib figures
pyplot.style.use('{}/styles/mesnardo.mplstyle'.format(os.environ['SCRIPTS']))
from mpl_toolkits.axes_grid1.inset_locator import inset_axes


class Field(object):
  """Contains information about a field (pressure for example)."""
  def __init__(self, x=None, y=None, values=None, time_step=None, label=None):
    """Initializes the field by its grid and its values.

    Parameters
    ----------
    x, y: Numpy 1d arrays of float
      Coordinates of the grid-nodes in each direction; default: None, None.
    values: Numpy 1d array of float
      Nodal values of the field; default: None.
    time_step: integer
      Time-step; default: None.
    label: string
      Description of the field; default: None.
    """
    self.label = label
    self.time_step = time_step
    self.x, self.y = x, y
    self.values = values

  def subtract(self, other, label=None):
    """Subtract a given field to the current one.

    Parameters
    ----------
    other: Field object
      The field that is subtracted.
    label: string, optional
      Label of the Field object to create;
      default: None (will be <current label>).
    """
    if not label:
      label = self.label
    # check the two solutions share the same grid
    atol = 1.0E-06
    assert numpy.allclose(self.x, other.x, atol=atol)
    assert numpy.allclose(self.y, other.y, atol=atol)
    assert self.values.shape == other.values.shape
    return Field(label=label,
                 time_step=self.time_step,
                 x=self.x, y=self.y, 
                 values=self.values-other.values)

  def restriction(self, grid, atol=1.0E-06):
    """Restriction of the field solution onto a coarser grid.
    Note: all nodes on the coarse grid are present in the fine grid.

    Parameters
    ----------
    grid: list of 1d arrays of floats
      Nodal stations in each direction of the coarser grid.
    atol: float, optional
      Absolute tolerance used to define shared nodes between two grids;
      default: 1.0E-06.

    Returns
    -------
    restricted_field: Field object
      Field restricted onto the coarser grid.
    """
    def intersection(a, b, atol=atol):
      return numpy.any(numpy.abs(a-b[:, numpy.newaxis]) <= atol, axis=0)
    mask_x = intersection(self.x, grid[0], atol=atol)
    mask_y = intersection(self.y, grid[1], atol=atol)
    return Field(x=self.x[mask_x], y=self.y[mask_y], 
                 values=numpy.array([self.values[j][mask_x] 
                                     for j in xrange(self.y.size)
                                     if mask_y[j]]),
                 time_step=self.time_step,
                 label=self.label+'-restricted')

  def get_difference(self, exact, mask, norm='L2'):
    """Returns the difference between two fields in a given norm.

    Parameters
    ----------
    exact: Field object
      The exact solution to compare with.
    mask: Field object
      Field whose grid is used as a mask;
      default: None.
    norm: string
      Norm used;
      default: L2 (L2-norm).

    Returns
    -------
    difference: float
      The difference using the indicated norm.
    """
    norms = {'L2': None, 'Linf': numpy.inf}
    grid = [mask.x, mask.y]
    field_restricted = self.restriction(grid)
    exact_restricted = exact.restriction(grid)
    return numpy.linalg.norm(field_restricted.values-exact_restricted.values, 
                             ord=norms[norm])

  def get_gridline_values(self, x=None, y=None):
    """Returns the field values along either a vertical or an horizontal
    gridline.

    The vertical gridline is defined by its x-position.
    The horizontal gridline is defined by its y-position.

    Parameters
    ----------
    x: float, optional
      x-position of the vertical gridline;
      default: None.
    y: float, optional
      y-position of the horizontal gridline;
      default: None.

    Returns
    -------
    array: 1d array of floats
      The field values along the gridline.
    """
    if (x and y) or not (x or y):
      print('[error] use either x or y keyword arguments '
            'to define the gridline position')
      return
    elif x:
      return get_vertical_gridline_values(x)
    elif y:
      return get_horizontal_gridline_values(y)

  def get_vertical_gridline_values(self, x):
    """Returns field values along a vertical gridline defined by its x-position.

    If the x-position of the gridline does not match any gridline 
    of the Cartesian grid, we interpolate the values.

    Parameters
    ----------
    x: float
      x-position of the vertical gridline.

    Returns
    -------
    u: 1d array of floats
      The (interpolated) field values along the vertical gridline.
    """
    indices = numpy.where(numpy.abs(self.x-x) <= 1.0E-06)[0]
    if indices.size == 0:
      i = numpy.where(self.x > x)[0][0]
      return ( (abs(self.x[i]-x)*self.values[:, i-1]
               +abs(self.x[i-1]-x)*self.values[:, i])
              /abs(self.x[i]-self.x[i-1]) )
    else:
      i = indices[0]
      return self.values[:, i]

  def get_horizontal_gridline_values(self, y):
    """Returns field values along an horizontal gridline defined by its y-position.

    If the y-position of the gridline does not match any gridline 
    of the Cartesian grid, we interpolate the values.

    Parameters
    ----------
    y: float
      y-position of the horizontal gridline.

    Returns
    -------
    u: 1d array of floats
      The (interpolated) field values along the horizontal gridline.
    """
    indices = numpy.where(numpy.abs(self.y-y) <= 1.0E-06)[0]
    if indices.size == 0:
      j = numpy.where(self.y > y)[0][0]
      return ( (abs(self.y[j]-y)*self.values[j-1, :]
               +abs(self.y[j-1]-y)*self.values[j, :])
              /abs(self.y[j]-self.y[j-1]) )
    else:
      j = indices[0]
      return self.values[j, :]

  def plot_vertical_gridline_values(self, x,
                                    boundaries=(None, None),
                                    plot_settings={},
                                    plot_limits=(None, None, None, None),
                                    save_directory=None,
                                    show=False,
                                    validation_data=None,
                                    validation_plot_settings={}):
    """Plots the field values along a group of vertical gridlines.

    Parameters
    ----------
    x: list of floats
      Group of vertical gridlines defined by their x-position.
    boundaries: 2-tuple of floats, optional
      Gridline limits to consider;
      default: (None, None) (the entire gridline)
    plot_settings: dictionary of (string, object) items, optional
      Contains optional arguments to call pyplot.plot function 
      for the gridline data;
      default: empty dictionary.
    plot_limits: 4-tuple of floats, optional
      Limits of the plot (x-start, x-end, y-start, y-end);
      default: (None, None, None, None)
    save_directory: string, optional
      Directory where to save the figure;
      default: None (does not save).
    show: boolean, optional
      Set 'True' if you want to display the figure;
      default: False.
    validation_data: 2-tuple of 1d arrays of floats, optional
      Validation data to add to the figure (1st array contains the y-stations,
      2nd array contains the values at the stations);
      default: None.
    validation_plot_settings: dictionary of (string, object) items, optional
      Contains optional arguments to call pyplot.plot function 
      for the validation data;
      default: empty dictionary.
    """
    print('[info] plotting field values along vertical gridline(s) ...'),
    fig, ax = pyplot.subplots(figsize=(6, 6))
    ax.grid(True, zorder=0)
    ax.set_xlabel('y-coordinate', fontsize=16)
    ax.set_ylabel('{} along vertical gridline'.format(self.label), fontsize=16)
    if not isinstance(x, (list, tuple)):
      x = [x]
    for x_target in x:
      y, u = self.y, self.get_vertical_gridline_values(x_target)
      if all(boundaries):
        mask = numpy.where(numpy.logical_and(y >= boundaries[0], 
                                             y <= boundaries[1]))[0]
        y, u = y[mask], u[mask]
      ax.plot(y, u, label='x={}'.format(x_target), **plot_settings)
    if validation_data != None:
      y, u = validation_data
      if all(boundaries):
        mask = numpy.where(numpy.logical_and(y >= boundaries[0], 
                                             y <= boundaries[1]))[0]
        y, u = y[mask], u[mask]
      ax.plot(y, u, **validation_plot_settings)
    ax.axis(plot_limits)
    ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    ax.legend(prop={'size': 16})
    if save_directory and os.path.isdir(save_directory):
      pyplot.savefig('{}/{}VerticalGridline{:0>7}.png'.format(save_directory, 
                                                              self.label, 
                                                              self.time_step))
    if show:
      pyplot.show()
    print('done')

  def plot_horizontal_gridline_values(self, y,
                                      boundaries=(None, None),
                                      plot_settings={},
                                      plot_limits=(None, None, None, None),
                                      save_directory=None,
                                      show=False,
                                      validation_data=None,
                                      validation_plot_settings={}):
    """Plots the field values along a group of horizontal gridlines.

    Parameters
    ----------
    y: list of floats
      Group of horizontal gridlines defined by their y-position.
    boundaries: 2-tuple of floats, optional
      Gridline limits to consider;
      default: (None, None) (the entire gridline)
    plot_settings: dictionary of (string, object) items, optional
      Contains optional arguments to call pyplot.plot function 
      for the gridline data;
      default: empty dictionary.
    plot_limits: 4-tuple of floats, optional
      Limits of the plot (x-start, x-end, y-start, y-end);
      default: (None, None, None, None)
    save_directory: string, optional
      Directory where to save the figure;
      default: None (does not save).
    show: boolean, optional
      Set 'True' if you want to display the figure;
      default: False.
    validation_data: 2-tuple of 1d arrays of floats, optional
      Validation data to add to the figure (1st array contains the y-stations,
      2nd array contains the values at the stations);
      default: None.
    validation_plot_settings: dictionary of (string, object) items, optional
      Contains optional arguments to call pyplot.plot function 
      for the validation data;
      default: empty dictionary.
    """
    print('[info] plotting field values along horizontal gridline(s) ...'),
    fig, ax = pyplot.subplots(figsize=(6, 6))
    ax.grid(True, zorder=0)
    ax.set_xlabel('x-coordinate', fontsize=16)
    ax.set_ylabel('{} along horizontal gridline'.format(self.label), fontsize=16)
    if not isinstance(y, (list, tuple)):
      y = [y]
    for y_target in y:
      x, u = self.x, self.get_horizontal_gridline_values(y_target)
      if all(boundaries):
        mask = numpy.where(numpy.logical_and(x >= boundaries[0], 
                                             x <= boundaries[1]))[0]
        x, u = x[mask], u[mask]
      ax.plot(x, u, label='y={}'.format(y_target), **plot_settings)
    if validation_data != None:
      x, u = validation_data
      if all(boundaries):
        mask = numpy.where(numpy.logical_and(x >= boundaries[0], 
                                             x <= boundaries[1]))[0]
        x, u = x[mask], u[mask]
      ax.plot(x, u, **validation_plot_settings)
    ax.axis(plot_limits)
    ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    ax.legend(prop={'size': 16})
    if save_directory and os.path.isdir(save_directory):
      pyplot.savefig('{}/{}HorizontalGridline{:0>7}.png'.format(save_directory, 
                                                                self.label, 
                                                                self.time_step))
    if show:
      pyplot.show()
    print('done')

  def plot_contour(self, 
                   field_range=None, 
                   filled_contour=True,
                   view=[float('-inf'), float('-inf'), float('inf'), float('inf')],
                   bodies=[],
                   save_name=None,
                   directory=os.getcwd(), 
                   width=8.0, 
                   dpi=100): 
    """Plots and saves the field.

    Parameters
    ----------
    field_range: list of floats
      Min, max and number of contours to plot; default: None.
    filled_contour: boolean
      Set 'True' to create a filled contour;
      default: True.
    view: list of floats
      Bottom-left and top-right coordinates of the rectangular view to plot;
      default: the whole domain.
    bodies: list of Body objects
      The immersed bodies to add to the figure; default: [] (no immersed body).
    save_name: string
      Prefix used to create the images directory and to save the .png files; 
      default: None.
    directory: string
      Directory where to save the image; default: current directory.
    width: float
      Width of the figure (in inches); default: 8.
    dpi: int
      Dots per inch (resolution); default: 100
    """
    if abs(self.values.min()-self.values.max()) <= 1.0E-06:
      print('[warning] uniform field; plot contour skipped!')
      return
    # create images directory
    save_name = (self.label if not save_name else save_name)
    images_directory = '{}/{}_{:.2f}_{:.2f}_{:.2f}_{:.2f}'.format(directory, 
                                                                  save_name, 
                                                                  *view)
    if not os.path.isdir(images_directory):
      print('[info] creating images directory: {} ...'.format(images_directory))
      os.makedirs(images_directory)

    print('[info] plotting the {} contour ...'.format(self.label))
    height = width*(view[3]-view[1])/(view[2]-view[0])
    fig, ax = pyplot.subplots(figsize=(width, height), dpi=dpi)
    ax.tick_params(axis='x', labelbottom='off')
    ax.tick_params(axis='y', labelleft='off')
    # create filled contour
    if field_range:
      levels = numpy.linspace(*field_range)
      print('[info] min={}, max={}'.format(self.values.min(), self.values.max()))
      colorbar_ticks = numpy.linspace(field_range[0], field_range[1], 5)
      colorbar_format = '%.01f'
    else:
      levels = numpy.linspace(self.values.min(), self.values.max(), 101)
      print('min={}, max={}, steps={}'.format(levels[0], levels[-1], levels.size))
      colorbar_ticks = numpy.linspace(self.values.min(), self.values.max(), 3)
      colorbar_format= '%.04f'
    color_map = {'pressure': cm.jet, 'vorticity': cm.RdBu_r,
                 'x-velocity': cm.RdBu_r, 'y-velocity': cm.RdBu_r}
    X, Y = numpy.meshgrid(self.x, self.y)
    contour_type = ax.contourf if filled_contour else ax.contour
    cont = contour_type(X, Y, self.values, 
                        levels=levels, extend='both', 
                        cmap=(cm.RdBu_r if self.label not in color_map.keys()
                                        else color_map[self.label]))
    ains = inset_axes(pyplot.gca(), width='30%', height='2%', loc=3)
    cont_bar = fig.colorbar(cont, 
                            cax=ains, orientation='horizontal',
                            ticks=colorbar_ticks, format=colorbar_format)
    cont_bar.ax.tick_params(labelsize=10) 
    ax.text(0.05, 0.12, self.label, transform=ax.transAxes, fontsize=10)
    cont_bar.ax.xaxis.set_ticks_position('top')
    # draw body
    for body in bodies:
      ax.plot(body.x, body.y, 
              color='black', linewidth=1, linestyle='-')
    # set limits
    ax.set_xlim(view[::2])
    ax.set_ylim(view[1::2])
    ax.set_aspect('equal')
    # save image
    image_path = '{}/{}{:0>7}.png'.format(images_directory, self.label, self.time_step)
    pyplot.savefig(image_path, dpi=dpi, bbox_inches='tight', pad_inches=0)
    pyplot.close()