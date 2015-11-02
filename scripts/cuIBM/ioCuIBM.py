#!/usr/bin/env python

# file: ioCuIBM.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Collection of IO functions for cuIBM.


import sys
import struct

import numpy


class Field(object):
  """Contains information about a field (pressure for example)."""
  def __init__(self, x=None, y=None, values=None, label=None):
    """Initializes the field by its grid and its values.

    Parameters
    ----------
    x, y: Numpy 1d arrays of float
      Coordinates of the grid-nodes in each direction; default: None, None.
    values: Numpy 1d array of float
      Nodal values of the field; default: None.
    label: string
      Description of the field; default: None.
    """
    self.label = label
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
  # get info about the grid
  nx, ny = coords[0].size-1, coords[1].size-1
  x, y = coords
  dx, dy = x[1:]-x[:-1], y[1:]-y[:-1]
  # read fluxes from file
  flux_file = '{}/{:0>7}'.format(directory, time_step)
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
  return (Field(x[1:-1], 0.5*(y[:-1]+y[1:]), u, label='u-velocity'), 
          Field(0.5*(x[:-1]+x[1:]), y[1:-1], v, label='v-velocity'))


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
  # get info about mesh-grid
  nx, ny = coords[0].size-1, coords[1].size-1
  # read pressure from file
  lambda_file = '{}/{:0>7}'.format(directory, time_step)
  if binary:
    with open(lambda_file, 'rb') as infile:
      nlambda = struct.unpack('i', infile.read(4))[0]
      p = numpy.array(struct.unpack('d'*nlambda, infile.read(8*nlambda)))[:nx*ny]
  else:
    with open(lambda_file, 'r') as infile:
      nlambda = int(infile.readline())
      p = numpy.loadtxt(infile, dtype=float)[:nx*ny]
  return Field(0.5*(x[:-1]+x[1:]), 0.5*(y[:-1]+y[1:]), p, label='pressure')


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
  mask_file = '{}/mask.txt'.format(directory)
  mask = numpy.loadtxt(mask_file, dtype=int)
  offset = (nx-1) * ny
  return mask[:offset], mask[offset:]


if __name__ == '__main__':
  pass