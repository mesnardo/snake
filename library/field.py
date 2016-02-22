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

  def subtract(self, other):
    """Subtract a given field to the current one.

    Parameters
    ----------
    other: Field object
      The field that is subtracted.
    """
    assert numpy.allclose(self.x, other.x, atol=1.0E-04)
    assert numpy.allclose(self.y, other.y, atol=1.0E-04)
    assert self.values.shape == other.values.shape
    self.values -= other.values
    self.label += '-subtracted'

  def restriction(self, grid):
    """Restriction of the field solution onto a coarser grid.
    Note: all nodes on the coarse grid are present in the fine grid.

    Parameters
    ----------
    grid: list of numpy arrays of floats
      Nodal stations in each direction of the coarser grid.

    Returns
    -------
    restricted_field: Field object
      Field restricted onto the coarser grid.
    """
    def intersection(a, b, tolerance=1.0E-06):
      return numpy.any(numpy.abs(a-b[:, numpy.newaxis]) <= tolerance, axis=0)
    mask_x = intersection(self.x, grid[0])
    mask_y = intersection(self.y, grid[1])
    restricted_field = Field()
    restricted_field.x = self.x[mask_x]
    restricted_field.y = self.y[mask_y]
    restricted_field.values = numpy.array([self.values[j][mask_x]
                                         for j in xrange(self.y.size)
                                         if mask_y[j]])
    return restricted_field

  def get_relative_difference(self, exact, grid):
    """Computes the difference (relative to an exact solution) in the L2-norm.

    Parameters
    ----------
    exact: Field object
      The 'exact' solution used as reference.
    grid: list of two 1d numpy arrays of floats
      Nodal stations in each direction used to restrict fields.

    Returns
    -------
    error: float
      The relative difference in the L2-norm of the field with an exact field.
    """
    field_restricted = self.restriction(grid)
    exact_restricted = exact.restriction(grid)
    return (  numpy.linalg.norm(field_restricted.values- exact_restricted.values)
            / numpy.linalg.norm(exact_restricted.values)  )

  def plot_contour(self, 
                   field_range=None, 
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
    # create images directory
    save_name = (self.label if not save_name else save_name)
    images_directory = '{}/{}_{:.2f}_{:.2f}_{:.2f}_{:.2f}'.format(directory, 
                                                                  save_name, 
                                                                  *view)
    if not os.path.isdir(images_directory):
      print('[info] creating images directory: {} ...'.format(images_directory)),
      os.makedirs(images_directory)
      print('done')

    print('[info] plotting the {} contour ...'.format(self.label)),
    height = width*(view[3]-view[1])/(view[2]-view[0])
    fig, ax = pyplot.subplots(figsize=(width, height), dpi=dpi)
    ax.tick_params(axis='x', labelbottom='off')
    ax.tick_params(axis='y', labelleft='off')
    # create filled contour
    if field_range:
      levels = numpy.linspace(*field_range)
      colorbar_ticks = numpy.linspace(field_range[0], field_range[1], 5)
    else:
      levels = numpy.linspace(self.values.min(), self.values.max(), 101)
      colorbar_ticks = numpy.linspace(self.values.min(), self.values.max(), 3)
    color_map = {'pressure': cm.jet, 'vorticity': cm.RdBu_r,
                 'x-velocity': cm.RdBu_r, 'y-velocity': cm.RdBu_r}
    X, Y = numpy.meshgrid(self.x, self.y)
    cont = ax.contourf(X, Y, self.values, 
                       levels=levels, extend='both', 
                       cmap=(cm.RdBu_r if self.label not in color_map.keys()
                                       else color_map[self.label]))
    ains = inset_axes(pyplot.gca(), width='30%', height='2%', loc=3)
    cont_bar = fig.colorbar(cont, 
                            cax=ains, orientation='horizontal',
                            ticks=colorbar_ticks, format='%.01f')
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
    print('done')