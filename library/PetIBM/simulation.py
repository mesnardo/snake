# file: PetIBMSimulation.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Implementation of the class `PetIBMSimulation`.


import os
import sys

import numpy

sys.path.append(os.path.join(os.environ['PETSC_DIR'], 'bin', 'pythonscripts'))
import PetscBinaryIO

from ..simulation import Simulation, BarbaGroupSimulation
from ..field import Field
from ..force import Force


class PetIBMSimulation(Simulation, BarbaGroupSimulation):
  """Contains info about a PetIBM simulation.
  Inherits from classes Simulation and BarbaGroupSimulation.
  """
  def __init__(self):
    pass

  def read_grid(self, file_name='grid.txt'):
    """Reads the coordinates from the file grid.txt.

    Parameters
    ----------
    file_name: string
      Name of file containing grid-node stations along each direction; 
      default: 'grid.txt'.
    """
    print('[info] reading the grid ...'),
    grid_path = '{}/{}'.format(self.directory, file_name)
    with open(grid_path, 'r') as infile:
      nCells = numpy.array([int(n) for n in infile.readline().strip().split()])
      coords = numpy.loadtxt(infile, dtype=float)
    self.grid = numpy.array(numpy.split(coords, numpy.cumsum(nCells[:-1]+1)))
    print('done')

  def read_velocity(self, time_step, periodic_directions=[]):
    """Reads the velocity field at a given time-step.

    Parameters
    ----------
    time_step: integer
      Time-step at which the field will be read.
    periodic_directions: list of strings
      Directions that have periodic boundary conditions; 
      default: [].
    """
    print('[time-step {}] reading velocity field ...'.format(time_step)),
    dim3 = (True if len(self.grid) == 3 else False)
    # get stations, cell-widths, and number of cells in x- and y-directions
    x, y = self.grid[:2]
    dx, dy = x[1:]-x[:-1], y[1:]-y[:-1]
    nx, ny = dx.size, dy.size
    # get stations, cell-widths, and number of cells in z-direction
    if dim3:
      z = self.grid[2]
      dz = z[1:]-z[:-1]
      nz = dz.size
    # folder with numerical solution
    folder = '{}/{:0>7}'.format(self.directory, time_step)
    # read fluxes in x- and y-directions
    qx = PetscBinaryIO.PetscBinaryIO().readBinaryFile('{}/qx.dat'.format(folder))[0]
    qy = PetscBinaryIO.PetscBinaryIO().readBinaryFile('{}/qy.dat'.format(folder))[0]
    # get cell-faces stations hosting velocity nodes along x- and y-directions
    xu, yu = x[1:-1], 0.5*(y[:-1]+y[1:])
    xv, yv = 0.5*(x[:-1]+x[1:]), y[1:-1]
    if dim3:
      # get stations of x-velocity nodes along z-direction
      zu = 0.5*(z[:-1]+z[1:])
      # compute x-velocity from x-flux
      qx = qx.reshape((nz, ny, (nx if 'x' in periodic_directions else nx-1)))
      u = ( qx[:, :, :(-1 if 'x' in periodic_directions else None)]
            /reduce(numpy.multiply, numpy.ix_(dz, dy, numpy.ones(nx-1))) )
      # get stations of y-velocity nodes along z-direction
      zv = 0.5*(z[:-1]+z[1:])
      # compute y-velocity from y-flux
      qy = qy.reshape((nz, (ny if 'y' in periodic_directions else ny-1), nx))
      v = ( qy[:, :(-1 if 'y' in periodic_directions else None), :]
            /reduce(numpy.multiply, numpy.ix_(dz, numpy.ones(ny-1), dx)) )
      # read fluxes in z-direction
      qz = PetscBinaryIO.PetscBinaryIO().readBinaryFile('{}/qz.dat'.format(folder))[0]
      # get stations of y-velocity nodes along x-, y-, and z-directions
      xw, yw, zw = 0.5*(x[:-1]+x[1:]), 0.5*(y[:-1]+y[1:]), z[1:-1]
      # compute z-velocity from z-flux
      qz = qz.reshape(((nz if 'z' in periodic_directions else nz-1), ny, nx))
      w = ( qz[:(-1 if 'z' in periodic_directions else None), :, :]
            /reduce(numpy.multiply, numpy.ix_(numpy.ones(nz-1), dy, dx)) )
      # set Field objects
      self.x_velocity = Field(x=xu, y=yu, z=zu, values=u, 
                              time_step=time_step, label='x-velocity')
      self.y_velocity = Field(x=xv, y=yv, z=zv, values=v, 
                              time_step=time_step, label='y-velocity')
      self.z_velocity = Field(x=xw, y=yw, z=zw, values=w, 
                              time_step=time_step, label='z-velocity')
    else:
      # compute x-velocity from x-flux
      qx = qx.reshape((ny, (nx if 'x' in periodic_directions else nx-1)))
      u = qx[:, :(-1 if 'x' in periodic_directions else None)]/numpy.outer(dy, numpy.ones(nx-1))
      # compute y-velocity from y-flux
      qy = qy.reshape(((ny if 'y' in periodic_directions else ny-1), nx))
      v = qy[:(-1 if 'y' in periodic_directions else None), :]/numpy.outer(numpy.ones(ny-1), dx)
      # set Field objects
      self.x_velocity = Field(x=xu, y=yu, values=u, 
                              time_step=time_step, label='x-velocity')
      self.y_velocity = Field(x=xv, y=yv, values=v, 
                              time_step=time_step, label='y-velocity')
    print('done')

  def read_pressure(self, time_step):
    """Reads the pressure fields from file given the time-step.

    Parameters
    ----------
    time_step: integer
      Time-step at which the field will be read.
    """
    print('[time-step {}] reading the pressure field ...'.format(time_step)),
    dim3 = (True if len(self.grid) == 3 else False)
    # get stations, cell-widths, and number of cells in x- and y-directions
    x, y = self.grid[:2]
    xp, yp = 0.5*(x[:-1]+x[1:]), 0.5*(y[:-1]+y[1:])
    nx, ny = xp.size, yp.size
    # get stations, cell-widths, and number of cells in z-direction
    if dim3:
      z = self.grid[2]
      zp = 0.5*(z[:-1]+z[1:])
      nz = zp.size
    # folder with numerical solution
    folder = '{}/{:0>7}'.format(self.directory, time_step)
    # read pressure
    p = PetscBinaryIO.PetscBinaryIO().readBinaryFile('{}/phi.dat'.format(folder))[0]
    # set pressure Field object
    if dim3:
      self.pressure = Field(x=xp, y=yp, z=zp, values=p.reshape((nz, ny, nx)), 
                            time_step=time_step, label='pressure')
    else:
      self.pressure = Field(x=xp, y=yp, values=p.reshape((ny, nx)), 
                            time_step=time_step, label='pressure')
    print('done')

  def read_forces(self, file_name='forces.txt', display_coefficients=False):
    """Reads forces from files.

    Parameters
    ----------
    file_name: string
      Name of the file containing the forces; 
      default: 'forces.txt'.
    display_coefficients: boolean
      Set to 'True' if force coefficients are required; 
      default: False (i.e. forces).
    """
    forces_path = '{}/{}'.format(self.directory, file_name)
    print('[info] reading forces from file {} ...'.format(forces_path)),
    with open(forces_path, 'r') as infile:
      times, force_x, force_y = numpy.loadtxt(infile, dtype=float, 
                                              usecols=(0, 1, 2), unpack=True)
    # set Force objects
    self.force_x = Force(times, force_x)
    self.force_y = Force(times, force_y)
    print('done')