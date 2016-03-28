# file: cuibmSimulation.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Implementation of the class `CuIBMSimulation`.


import os
import struct

import numpy

from ..simulation import Simulation, BarbaGroupSimulation
from ..field import Field
from ..force import Force


class CuIBMSimulation(Simulation, BarbaGroupSimulation):
  """Contains info about a cuIBM simulation.
  Inherits from classes Simulation and BarbaGroupSimulation.
  """
  def __init__(self):
    pass

  def read_grid(self, file_name='grid'):
    """Reads the computational grid from file.
    
    Parameters
    ----------
    file_name: string
      Name of the file containing nodal stations of the grid along each direction;
      default: 'grid'.
    """
    print('[info] reading grid from file ...'),
    grid_file = '{}/{}'.format(self.directory, file_name)
    # test if file written in binary format
    textchars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})
    is_binary_string = lambda bytes: bool(bytes.translate(None, textchars))
    binary_format = is_binary_string(open(grid_file, 'rb').read(1024))
    if binary_format:
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
    self.grid = x, y
    print('done')

  def read_velocity(self, time_step, **kwargs):
    """Reads the velocity field from solution file at a given time-step.

    Parameters
    ----------
    time_step: integer
      Time-step at which to read the fluxes.
    """
    print('[time-step {}] reading velocity field from file ...'.format(time_step)),
    # get info about the grid
    x, y = self.grid
    nx, ny = x.size-1, y.size-1
    dx, dy = x[1:]-x[:-1], y[1:]-y[:-1]
    # read fluxes from file
    flux_file = '{}/{:0>7}/q'.format(self.directory, time_step)
    # test if file written in binary format
    textchars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})
    is_binary_string = lambda bytes: bool(bytes.translate(None, textchars))
    binary_format = is_binary_string(open(flux_file, 'rb').read(1024))
    if binary_format:
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
    # set velocity Field objects
    self.x_velocity = Field(x=x[1:-1], y=0.5*(y[:-1]+y[1:]), 
                            values=u.reshape(ny, nx-1), 
                            time_step=time_step, label='x-velocity')
    self.y_velocity = Field(x=0.5*(x[:-1]+x[1:]), y=y[1:-1], 
                            values=v.reshape(ny-1, nx), 
                            time_step=time_step, label='y-velocity')
    print('done')

  def read_pressure(self, time_step):
    """Reads pressure field from solution file at given time-step.
    
    Parameters
    ----------
    time_step: integer
      Time-step at which to read the pressure field.
    """
    print('[time-step {}] reading pressure field from file ...'.format(time_step)),
    # get info about mesh-grid
    x, y = self.grid
    nx, ny = x.size-1, y.size-1
    # read pressure from file
    lambda_file = '{}/{:0>7}/lambda'.format(self.directory, time_step)
    # test if file written in binary format
    textchars = bytearray({7,8,9,10,12,13,27} | set(range(0x20, 0x100)) - {0x7f})
    is_binary_string = lambda bytes: bool(bytes.translate(None, textchars))
    binary_format = is_binary_string(open(lambda_file, 'rb').read(1024))
    if binary_format:
      with open(lambda_file, 'rb') as infile:
        nlambda = struct.unpack('i', infile.read(4))[0]
        p = numpy.array(struct.unpack('d'*nlambda, infile.read(8*nlambda)))[:nx*ny]
    else:
      with open(lambda_file, 'r') as infile:
        nlambda = int(infile.readline())
        p = numpy.loadtxt(infile, dtype=float)[:nx*ny]
    # set pressure Field object
    self.pressure = Field(x=0.5*(x[:-1]+x[1:]), y=0.5*(y[:-1]+y[1:]), 
                          values=p.reshape(nx, ny), 
                          time_step=time_step ,label='pressure')
    print('done')

  def read_forces(self, file_name='forces', display_coefficients=False):
    """Reads forces from files.

    Parameters
    ----------
    file_name: string
      Name of the file containing the forces; 
      default: 'forces'.
    display_coefficients: boolean
      Set to 'True' if force coefficients are required; 
      default: False (i.e. forces).
    """
    print('[info] reading forces from file ...'),
    forces_path = '{}/{}'.format(self.directory, file_name)
    with open(forces_path, 'r') as infile:
      times, force_x, force_y = numpy.loadtxt(infile, dtype=float, 
                                              usecols=(0, 1, 2), unpack=True)
    # set Force objects
    self.force_x = Force(times, force_x)
    self.force_y = Force(times, force_y)
    print('done')