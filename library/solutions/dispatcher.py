# file: analytical.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Contains definition of classes for analytical solutions.


import os
import sys
import math

import numpy

from ..field import Field


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
    self.x_velocity, self.y_velocity = self.get_velocity()
    self.pressure = self.get_pressure()
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
    x_velocity, y_velocity: Field objects
      The velocity components.
    """
    # x-velocity on staggered grid
    x, y = self.grid[0][1:-1], 0.5*(self.grid[1][:-1]+self.grid[1][1:])
    X, Y = self.mapped_meshgrid(x, y)
    values = ( -self.amplitude*numpy.cos(X)*numpy.sin(Y)
               *math.exp(-2.0*(2.0*math.pi)**2*self.time/self.Re) )
    x_velocity = Field(x=x, y=y, values=values, time_step=0, label='x-velocity')
    # y-velocity on staggered grid
    x, y = 0.5*(self.grid[0][:-1]+self.grid[0][1:]), self.grid[1][1:-1]
    X, Y = self.mapped_meshgrid(x, y)
    values = ( self.amplitude*numpy.sin(X)*numpy.cos(Y)
               *math.exp(-2.0*(2.0*math.pi)**2*self.time/self.Re) )
    y_velocity = Field(x=x, y=y, values=values, time_step=0, label='y-velocity')
    return x_velocity, y_velocity

  def get_pressure(self):
    """Computes the analytical solution of the pressure field.

    Returns
    -------
    p: Field object
      The pressure field.
    """
    # pressure at cell-centers
    x, y = 0.5*(self.grid[0][:-1]+self.grid[0][1:]), 0.5*(self.grid[1][:-1]+self.grid[1][1:])
    X, Y = self.mapped_meshgrid(x, y)
    values = ( -0.25*(numpy.cos(2.0*X)+numpy.cos(2.0*Y))
               *math.exp(-4.0*(2.0*math.pi)**2*self.time/self.Re) )
    return Field(x=x, y=y, values=values, time_step=0, label='pressure')

  def plot_fields(self):
    """Plots the velocity and pressure fields."""
    self.x_velocity.plot_contour(field_range=[-1.0, 1.0, 101],
                                 directory='{}/images'.format(os.getcwd()),
                                 view=self.bottom_left+self.top_right,
                                 save_name='analytical')
    self.y_velocity.plot_contour(field_range=[-1.0, 1.0, 101],
                                 directory='{}/images'.format(os.getcwd()),
                                 view=self.bottom_left+self.top_right,
                                 save_name='analytical')
    self.pressure.plot_contour(field_range=[-0.5, 0.5, 101],
                               directory='{}/images'.format(os.getcwd()),
                               view=self.bottom_left+self.top_right,
                               save_name='analytical')


# dictionary that contains the plug-in classes
# key is a string that contains the name of the class
dispatcher = {'TaylorGreenVortex': TaylorGreenVortex}