#!/usr/bin/env python

# file: ioCuIBM.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Collection of IO functions for cuIBM.


import os
import sys
import struct

import numpy
from matplotlib import pyplot, cm
# load default style of matplotlib figures
pyplot.style.use('{}/styles/mesnardo.mplstyle'.format(os.environ['SCRIPTS']))


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


def get_time_steps(case_directory, time_steps_range=[]):
  """Returns a list of the time-steps to post-process.

  Parameters
  ----------
  case_directory: str
    Directory of the simulation.
  time_steps_range: list(int)
    Initial, final and stride of the time-steps to consider.
  """
  if len(time_steps_range) == 3:
    return range(time_steps_range[0],
                 time_steps_range[1]+1,
                 time_steps_range[2])
  else:
    return sorted(int(folder) for folder in os.listdir(case_directory)
                              if folder[0] == '0')


def read_grid(directory, binary=False):
  """Reads the computational grid from file.
  
  Parameters
  ----------
  directory: string
    Directory of the simulation.
  binary: bool
    Set `True` if grid is a binary file; default: False.

  Returns
  -------
  x, y: Numpy 1d arrays of float
    Coordinates along a grid-line in each direction.
  """
  print('[info] reading grid file ...'),
  grid_file = '{}/grid'.format(directory)
  if binary:
    with open(grid_file, 'rb') as infile:
      # x-direction
      nx = struct.unpack('i', infile.read(4))[0]
      x = numpy.array(struct.unpack('d'*(nx+1), infile.read(8*(nx+1))))
      # y-direction
      ny = struct.unpack('i', infile.read(4))[0]
      y = numpy.array(struct.unpack('d'*(ny+1), infile.read(8*(ny+1))))
  else:
    with open(grid_file, 'r') as infile:
      data = numpy.loadtxt(infile, dtype=float)
      # x-direction
      nx = int(data[0])
      x, data = data[1:nx+2], data[nx+2:]
      # y-direction
      ny = int(data[0])
      y = data[1:]
  print('done')
  return x, y


def read_velocity(directory, time_step, coords, binary=False):
  """Reads the velocity field from solution file at a given time-step.

  Parameters
  ----------
  directory: string
    Directory of the simulation.
  time_step: integer
    Time-step at which to read the fluxes.
  coords: Numpy array of float
    Cell-centered coordinates of the mesh.
  binary: bool
    Set `True` if binary format; default: False.

  Returns
  -------
  u, v: Field objects
    Information about the u- and v-velocities (nodes and values).
  """
  print('[time-step {}] reading velocity field from file ...'.format(time_step)),
  # get info about the grid
  nx, ny = coords[0].size-1, coords[1].size-1
  x, y = coords
  dx, dy = x[1:]-x[:-1], y[1:]-y[:-1]
  # read fluxes from file
  flux_file = '{}/{:0>7}/q'.format(directory, time_step)
  if binary:
    with open(flux_file, 'rb') as infile:
      nq = struct.unpack('i', infile.read(4))[0]
      q = numpy.array(struct.unpack('d'*nq, infile.read(8*nq)))
  else:
    with open(flux_file, 'r') as infile:
      nq = int(infile.readline())
      q = numpy.loadtxt(infile, dtype=float)
  # u-velocities
  u = numpy.empty((nx-1)*ny, dtype=float)
  for j in xrange(ny):
    for i in xrange(nx-1):
      u[j*(nx-1)+i] = q[j*(nx-1)+i] / dy[j]
  # v-velocities
  offset = u.size
  v = numpy.empty(nx*(ny-1), dtype=float)
  for j in xrange(ny-1):
    for i in xrange(nx):
      v[j*nx+i] = q[offset+j*nx+i] / dx[i]
  print('done')
  return (Field(x=x[1:-1], y=0.5*(y[:-1]+y[1:]), 
                values=u.reshape(ny, nx-1), 
                time_step=time_step, label='u-velocity'), 
          Field(x=0.5*(x[:-1]+x[1:]), y=y[1:-1], 
                values=v.reshape(ny-1, nx), 
                time_step=time_step, label='v-velocity'))


def read_pressure(directory, time_step, coords, binary=False):
  """Reads pressure field from solution file at given time-step.
  
  Parameters
  ----------
  directory: string
    Directory of the simulation.
  time_step: integer
    Time-step at which to read the pressure field.
  coords: Numpy 1d arrays of float
    Mesh-grid coordinates.
  binary: bool
    Set `True` iif written in binary format; default: False.

  Returns
  -------
  p: Field object
    Information about the pressure field (nodes and values).
  """
  print('[time-step {}] reading pressure field from file ...'.format(time_step)),
  # get info about mesh-grid
  nx, ny = coords[0].size-1, coords[1].size-1
  x, y = coords
  # read pressure from file
  lambda_file = '{}/{:0>7}/lambda'.format(directory, time_step)
  if binary:
    with open(lambda_file, 'rb') as infile:
      nlambda = struct.unpack('i', infile.read(4))[0]
      p = numpy.array(struct.unpack('d'*nlambda, infile.read(8*nlambda)))[:nx*ny]
  else:
    with open(lambda_file, 'r') as infile:
      nlambda = int(infile.readline())
      p = numpy.loadtxt(infile, dtype=float)[:nx*ny]
  print('done')
  return Field(x=0.5*(x[:-1]+x[1:]), y=0.5*(y[:-1]+y[1:]), 
               values=p.reshape(nx, ny), 
               time_step=time_step ,label='pressure')


def read_mask(directory, nx, ny):
  """Reads the mask file.
  
  Parameters
  ----------
  directory: string
    Directory of the simulation.
  nx, ny: integers
    Number of cells in each x- and y-directions.

  Returns
  -------
  mask: Numpy 1d array of integers
    Masks in the x- and y-directions.
  """
  print('[info] reading the mask from file ... '),
  mask_file = '{}/mask.txt'.format(directory)
  mask = numpy.loadtxt(mask_file, dtype=int)
  offset = (nx-1) * ny
  print('done')
  return mask[:offset], mask[offset:]


def plot_contour(field, field_range, 
                 directory=os.getcwd(),
                 view=[float('-inf'), float('-inf'), float('inf'), float('inf')],
                 size=[8.0, 8.0], dpi=100): 
  """Plots and saves the field.

  Parameters
  ----------
  field: ioCuIBM.Field instance
    Nodes and values of the field.
  field_range: list(float)
    Min, max and number of countours to plot.
  directory: str
    Parent directory where to save the images: default: $PWD.
  view: list(float)
    Bottom-left and top-right coordinates of the rectangular view to plot;
    default: the whole domain.
  size: list(float)
    Size (width and height) of the figure to save (in inches); default: [8, 8].
  dpi: int
    Dots per inch (resolution); default: 100
  """
  x_left = ('left' if view[0] == float('-inf') else '{:.2f}'.format(view[0]))
  y_bottom = ('bottom' if view[1] == float('-inf') else '{:.2f}'.format(view[1]))
  x_right = ('right' if view[2] == float('inf') else '{:.2f}'.format(view[2]))
  y_top = ('top' if view[3] == float('inf') else '{:.2f}'.format(view[3]))
  images_directory = '{}/images/{}_{}_{}_{}_{}'.format(directory, field.label, 
                                                       x_left, y_bottom, x_right, y_top)
  if not os.path.isdir(images_directory):
    print('[info] creating images directory: {} ...'.format(images_directory)),
    os.makedirs(images_directory)
    print('done')
  print('[info] plotting the {} contour ...'.format(field.label)),
  fig, ax = pyplot.subplots(figsize=(size[0], size[1]), dpi=dpi)
  pyplot.xlabel('$x$')
  pyplot.ylabel('$y$')
  if field_range:
    levels = numpy.linspace(field_range[0], field_range[1], field_range[2])
    colorbar_ticks = numpy.linspace(field_range[0], field_range[1], 5)
  else:
    levels = numpy.linspace(field.values.min(), field.values.max(), 101)
    colorbar_ticks = numpy.linspace(field.values.min(), field.values.max(), 5)
  X, Y = numpy.meshgrid(field.x, field.y)
  color_map = {'pressure': cm.jet, 'vorticity': cm.RdBu_r,
               'u-velocity': cm.RdBu_r, 'v-velocity': cm.RdBu_r}
  cont = ax.contourf(X, Y, field.values, 
                     levels=levels, extend='both', 
                     cmap=color_map[field.label])
  cont_bar = fig.colorbar(cont, label=field.label, 
                          orientation='horizontal', format='%.02f', 
                          ticks=colorbar_ticks)
  x_start, x_end = max(view[0], field.x.min()), min(view[2], field.x.max())
  y_start, y_end = max(view[1], field.y.min()), min(view[3], field.y.max())
  ax.axis([x_start, x_end, y_start, y_end])
  ax.set_aspect('equal')
  image_path = '{}/{}{:0>7}.png'.format(images_directory, field.label, field.time_step)
  pyplot.savefig(image_path, dpi=dpi)
  pyplot.close()
  print('done')


def compute_vorticity(u, v):
  """Computes the vorticity field for a two-dimensional simulation.

  Parameters
  ----------
  u, v: ioCuIBM.Field objects
    u-velocity and v-velocity fields.

  Returns
  -------
  vorticity: ioCuIBM.Field object
    The vorticity field.
  """
  print('[info] computing the vorticity field ...'),
  mask_x = numpy.where(numpy.logical_and(u.x > v.x[0], u.x < v.x[-1]))[0]
  mask_y = numpy.where(numpy.logical_and(v.y > u.y[0], v.y < u.y[-1]))[0]
  # vorticity nodes at cell vertices intersection
  xw, yw = 0.5*(v.x[:-1]+v.x[1:]), 0.5*(u.y[:-1]+u.y[1:])
  # compute vorticity
  w = ( (v.values[mask_y, 1:] - v.values[mask_y, :-1])
        / numpy.outer(numpy.ones(yw.size), v.x[1:]-v.x[:-1])
      - (u.values[1:, mask_x] - u.values[:-1, mask_x])
        / numpy.outer(u.y[1:]-u.y[:-1], numpy.ones(xw.size)) )
  print('done')
  return Field(x=xw, y=yw, 
               values=w, 
               time_step=u.time_step, label='vorticity')


if __name__ == '__main__':
  pass