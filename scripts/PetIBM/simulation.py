# file: PetIBMSimulation.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Implementation of the class `PetIBMSimulation`.


import os
import sys

import numpy

sys.path.append(os.path.join(os.environ['PETSC_DIR'], 'bin', 'pythonscripts'))
import PetscBinaryIO

from ..library.simulation import Simulation, BarbaGroupSimulation
from ..library.force import Force


class PetIBMSimulation(Simulation, BarbaGroupSimulation):
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

  def read_velocity(self, time_step):
    """Reads the velocity field at a given time-step.

    Parameters
    ----------
    time_step: integer
      Time-step at which the field will be read.
    """
    print('[time-step {}] reading velocity field ...'.format(time_step)),
    dim3 = (True if len(coords) == 3 else False)
    x, y, z = coords[0], coords[1], (None if not dim3 else coords[2])
    # compute cell-widths
    dx, dy, dz = x[1:]-x[:-1], y[1:]-y[:-1], (None if not dim3 else z[1:]-z[:-1])
    # number of of cells
    nx, ny, nz = dx.size, dy.size, (None if not dim3 else dz.size)
    # folder with numerical solution
    solution_directory = '{}/{:0>7}'.format(self.directory, time_step)
    # read x-flux
    flux_path = '{}/qx.dat'.format(solution_directory)
    qx = PetscBinaryIO.PetscBinaryIO().readBinaryFile(flux_path)[0]
    # read y-flux
    flux_path = '{}/qy.dat'.format(solution_directory)
    qy = PetscBinaryIO.PetscBinaryIO().readBinaryFile(flux_path)[0]
    # get velocity nodes coordinates
    xu, yu = x[1:-1], 0.5*(y[:-1]+y[1:])
    xv, yv = 0.5*(x[:-1]+x[1:]), y[1:-1]
    if dim3:
      # get third-dimension coordinate of x-velocity nodes
      zu = 0.5*(z[:-1]+z[1:])
      # compute x-velocity field
      qx = qx.reshape((nz, ny, (nx if 'x' in self.periodic_directions else nx-1)))
      u = ( qx[:, :, :(-1 if 'x' in self.periodic_directions else None)]
            /reduce(numpy.multiply, numpy.ix_(dz, dy, numpy.ones(nx-1))) )
      # get third-dimension coordinate of y-velocity nodes
      zv = 0.5*(z[:-1]+z[1:])
      # compute y-velocity field
      qy = qy.reshape((nz, (ny if 'y' in self.periodic_directions else ny-1), nx))
      v = ( qy[:, :(-1 if 'y' in self.periodic_directions else None), :]
            /reduce(numpy.multiply, numpy.ix_(dz, numpy.ones(ny-1), dx)) )
      # read z-flux
      flux_path = '{}/qz.dat'.format(solution_directory)
      qz = PetscBinaryIO.PetscBinaryIO().readBinaryFile(flux_path)[0]
      # get coordinates of z-velocity nodes
      xw, yw, zw = 0.5*(x[:-1]+x[1:]), 0.5*(y[:-1]+y[1:]), z[1:-1]
      # compute z-velocity field
      qz = qz.reshape(((nz if 'z' in self.periodic_directions else nz-1), ny, nx))
      w = ( qz[:(-1 if 'z' in self.periodic_directions else None), :, :]
            /reduce(numpy.multiply, numpy.ix_(numpy.ones(nz-1), dy, dx)) )
      # tests
      assert (zu.size, yu.size, xu.size) == u.shape
      assert (zv.size, yv.size, xv.size) == v.shape
      assert (zw.size, yw.size, xw.size) == w.shape
      self.x_velocity = Field(x=xu, y=yu, z=zu, time_step=time_step, values=u, label='x-velocity')
      self.y_velocity = Field(x=xu, y=yu, z=zu, time_step=time_step, values=u, label='y-velocity')
      self.z_velocity = Field(x=xu, y=yu, z=zu, time_step=time_step, values=u, label='z-velocity')
    else:
      # compute x-velocity field
      qx = qx.reshape((ny, (nx if 'x' in self.periodic_directions else nx-1)))
      u = qx[:, :(-1 if 'x' in self.periodic_directions else None)]/numpy.outer(dy, numpy.ones(nx-1))
      # compute y-velocity field
      qy = qy.reshape(((ny if 'y' in self.periodic_directions else ny-1), nx))
      v = qy[:(-1 if 'y' in self.periodic_directions else None), :]/numpy.outer(numpy.ones(ny-1), dx)
      # tests
      assert (yu.size, xu.size) == u.shape
      assert (yv.size, xv.size) == v.shape
      self.x_velocity = Field(x=xu, y=yu, time_step=time_step, values=u, label='x-velocity')
      self.y_velocity = Field(x=xu, y=yu, time_step=time_step, values=u, label='y-velocity')
    print('done')

  def read_pressure(self, time_step):
    """Reads the pressure fields from file given the time-step.

    Parameters
    ----------
    time_step: integer
      Time-step at which the field will be read.
    """
    print('[time-step {}] reading the pressure field ...'.format(time_step)),
    dim3 = (True if len(coords) == 3 else False)
    x, y, z = coords[0], coords[1], (None if not dim3 else coords[2])
    # folder with numerical solution
    solution_directory = '{}/{:0>7}'.format(self.directory, time_step)
    # pressure
    pressure_path = '{}/phi.dat'.format(solution_directory)
    p = PetscBinaryIO.PetscBinaryIO().readBinaryFile(pressure_path)[0]
    # get pressure nodes coordinates
    xp, yp = 0.5*(x[:-1]+x[1:]), 0.5*(y[:-1]+y[1:])
    nx, ny = xp.size, yp.size
    if dim3:
      # get third-dimension coordinates of pressure nodes
      zp = 0.5*(z[:-1]+z[1:])
      nz = zp.size
      # compute pressure field
      p = p.reshape((nz, ny, nx))
      # tests
      assert (zp.size, yp.size, xp.size) == p.shape
      self.pressure = Field(x=xp, y=yp, z=zp, values=p, label='pressure')
    else:
      # compute pressure field
      p = p.reshape((ny, nx))
      # tests
      assert (yp.size, xp.size) == p.shape
      self.pressure = Field(x=xp, y=yp, time_step=time_step, values=p, label='pressure')
    print('done')

  def read_forces(self, file_name='forces.txt', display_coefficients=False):
    """Reads forces from files.

    Parameters
    ----------
    file_name: string
      Name of the file containing the forces; default: 'forces.txt'.
    display_coefficients: boolean
      Set to 'True' if force coefficients are required; default: False (i.e. forces).
    """
    print('[info] reading forces from file ...'),
    forces_path = '{}/{}'.format(self.directory, file_name)
    with open(forces_path, 'r') as infile:
      times, force_x, force_y = numpy.loadtxt(infile, dtype=float, 
                                              usecols=(0, 1, 2), unpack=True)
    self.force_x = Force(times, force_x)
    self.force_y = Force(times, force_y)
    print('done')