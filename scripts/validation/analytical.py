# file: analytical.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Contains definition of classes for analytical solutions.


import os
import sys
import math
import numpy


class TaylorGreenVortex(object):
  """Analytical plug-in for the Taylor-Green vortex case."""
  def __init__(self, grid, time, Re, amplitude):
    """Computes the velocities and pressure fields on a given grid.

    Parameters
    ----------
    grid: 2d numpy array of floats
      Contains the stations along the gridline in each direction.
    time: string
      Time at which the analytical solution is computed.
    Re: string
      Reynolds number.
    amplitude: string
      Amplitude of the Taylor-Green vortex.
    """
    # parameters from the command-line are stored as strings and require to be converted
    self.time = float(time)
    self.amplitude = float(amplitude)
    self.Re = float(Re)
    self.grid = grid
    self.bottom_left = [grid[0][0], grid[1][0]]
    self.top_right = [grid[0][-1], grid[1][-1]]
    self.u, self.v = self.get_velocity()
    self.p = self.get_pressure()
    self.plot_fields()

  def mapped_meshgrid(self, x, y):
    """Maps the grid to a $[0,2\pi]x[0,2\pi]$ domain and returns the mesh-grid.

    Parameters
    ----------
    x, y: 1d numpy arrays of floats
      Stations along a grid-line.

    Returns
    -------
    X, Y: numpy meshgrid
      The mesh-grid.
    """
    X1, X2 = 0.0, 2.0*math.pi
    x = X1 + (X2-X1)*(x-self.bottom_left[0])/(self.top_right[0]-self.bottom_left[0])
    y = X1 + (X2-X1)*(y-self.bottom_left[1])/(self.top_right[1]-self.bottom_left[1])
    return numpy.meshgrid(x, y)

  def get_velocity(self):
    """Computes the analytical solution of the velocity field.

    Returns
    -------
    u, v: Field objects
      The velocity components.
    """
    u = Field()
    u.label = 'u-velocity'
    u.time_step = 1 # does not matter
    u.x, u.y = self.grid[0][1:-1], 0.5*(self.grid[1][:-1]+self.grid[1][1:])
    X, Y = self.mapped_meshgrid(u.x, u.y)
    u.values = -self.amplitude*numpy.cos(X)*numpy.sin(Y)*math.exp(-2.0*(2.0*math.pi)**2*self.time/self.Re)
    v = Field()
    v.label = 'v-velocity'
    v.time_step = 1 # does not matter
    v.x, v.y = 0.5*(self.grid[0][:-1]+self.grid[0][1:]), self.grid[1][1:-1]
    X, Y = self.mapped_meshgrid(v.x, v.y)
    v.values = self.amplitude*numpy.sin(X)*numpy.cos(Y)*math.exp(-2.0*(2.0*math.pi)**2*self.time/self.Re)
    return u, v

  def get_pressure(self):
    """Computes the analytical solution of the pressure field.

    Returns
    -------
    p: Field object
      The pressure field.
    """
    p = Field()
    p.label = 'pressure'
    p.time_step = 1 # does not matter
    p.x, p.y = 0.5*(self.grid[0][:-1]+self.grid[0][1:]), 0.5*(self.grid[1][:-1]+self.grid[1][1:])
    X, Y = self.mapped_meshgrid(p.x, p.y)
    p.values = -0.25*(numpy.cos(2.0*X)+numpy.cos(2.0*Y))*math.exp(-4.0*(2.0*math.pi)**2*self.time/self.Re)
    return p

  def plot_fields(self):
    """Plots the velocity and pressure fields."""
    sys.path.append('{}/scripts/PetIBM'.format(os.environ['SCRIPTS']))
    import ioPetIBM
    ioPetIBM.plot_contour(self.u, 
                          field_range=[-1.0, 1.0, 101],
                          view=self.bottom_left+self.top_right, 
                          save_name='{}_analytical'.format(self.u.label))
    ioPetIBM.plot_contour(self.v, 
                          field_range=[-1.0, 1.0, 101],
                          view=self.bottom_left+self.top_right, 
                          save_name='{}_analytical'.format(self.v.label))
    ioPetIBM.plot_contour(self.p, 
                          field_range=[-0.5, 0.5, 101],
                          view=self.bottom_left+self.top_right, 
                          save_name='{}_analytical'.format(self.p.label))


# dictionary that contains the plug-in classes
# key is a string that contains the name of the class
dispatcher = {'TaylorGreenVortex': TaylorGreenVortex}


# fake class Field
class Field(object):
  def __init__(self):
    pass