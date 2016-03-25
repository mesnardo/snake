# file: decayingVortices.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Implementation of the class `DecayingVortices`.


import os
import sys
import math

import numpy

from ..field import Field


class DecayingVortices(object):
  """Analytical plug-in for the decaying vortices case."""
  def __init__(self, x, y, time, Re, amplitude):
    """Computes the velocities and pressure fields on a given grid.

    Parameters
    ----------
    x, y: 2d numpy array of floats
      Contains the stations along the gridline in each direction.
    time: string
      Time at which the analytical solution is computed.
    Re: string
      Reynolds number.
    amplitude: string
      Amplitude of the Taylor-Green vortex.
    """
    self.bottom_left, self.top_right = [x[0], y[0]], [x[-1], y[-1]]
    self.x_velocity, _ = self.get_velocity(x[1:-1], 
                                           0.5*(y[:-1]+y[1:]), 
                                           float(time), float(Re), float(amplitude))
    _, self.y_velocity = self.get_velocity(0.5*(x[:-1]+x[1:]), 
                                           y[1:-1], 
                                           float(time), float(Re), float(amplitude))
    self.pressure = self.get_pressure(0.5*(x[:-1]+x[1:]), 
                                      0.5*(y[:-1]+y[1:]), 
                                      float(time), float(Re))

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
    X1, X2 = 0.0, 2.0*numpy.pi
    x = X1 + (X2-X1)*(x-self.bottom_left[0])/(self.top_right[0]-self.bottom_left[0])
    y = X1 + (X2-X1)*(y-self.bottom_left[1])/(self.top_right[1]-self.bottom_left[1])
    return numpy.meshgrid(x, y)

  def get_velocity(self, x, y, time, Re, amplitude):
    """Computes the analytical solution of the velocity field.

    Parameters
    ----------
    x, y: 1d numpy arrays of floats
      Nodal stations along each direction.
    time: float
      The time.
    Re: float
      The Reynolds number.
    amplitude: float
      amplitude of the vortices.

    Returns
    -------
    x_velocity, y_velocity: Field objects
      The velocity components.
    """
    X, Y = self.mapped_meshgrid(x, y)
    return (Field(x=x, y=y, label='x-velocity',
                  values=( -amplitude*numpy.cos(X)*numpy.sin(Y)
                           *math.exp(-2.0*(2.0*numpy.pi)**2*time/Re) )),
            Field(x=x, y=y, label='y-velocity',
                  values=( amplitude*numpy.sin(X)*numpy.cos(Y)
                           *math.exp(-2.0*(2.0*numpy.pi)**2*time/Re) )))

  def get_pressure(self, x, y, time, Re):
    """Computes the analytical solution of the pressure field.

    Parameters
    ----------
    x, y: 1d numpy arrays of floats
      Nodal stations along each direction.
    time: float
      The time.
    Re: float
      The Reynolds number.

    Returns
    -------
    p: Field object
      The pressure field.
    """
    X, Y = self.mapped_meshgrid(x, y)
    return Field(x=x, y=y, label='pressure', 
                 values=( -0.25*(numpy.cos(2.0*X)+numpy.cos(2.0*Y))
                          *math.exp(-4.0*(2.0*numpy.pi)**2*time/Re) ))

  def plot_fields(self, time_step, 
                  view=[float('-inf'), float('-inf'), float('inf'), float('inf')], 
                  directory=os.getcwd()+'/images',
                  save_name='analytical'):
    """Plots the velocity and pressure fields.

    Parameters
    ----------
    time_step: integer
      Index used to as a suffix for the file names.
    view: 4-list of floats, optional
      Bottom-left and top-right coordinates of the view to plot;
      default: entire domain.
    directory: string, optional
      Directory where to save the images;
      default: <current directory>/images.
    save_name: string, optional
      Prefix of the folder name that will contain the .png files;
      default: 'analytical'.
    """
    self.x_velocity.time_step = time_step
    self.y_velocity.time_step = time_step
    self.pressure.time_step = time_step
    self.x_velocity.plot_contour(directory=directory, view=view, save_name=save_name)
    self.y_velocity.plot_contour(directory=directory, view=view, save_name=save_name)
    self.pressure.plot_contour(directory=directory, view=view, save_name=save_name)

  def write_fields_petsc_format(self, x, y, time, Re, amplitude,
                                periodic_directions=None, 
                                directory=os.getcwd()):
    """Computes and writes velocity and pressure fields into PETSc-readable files.
    The files are saved in the sub-folder 0000000.

    Parameters
    ----------
    x, y: 1d numpy arrays of floats
      Nodal stations along each direction.
    time: float
      The time at which the solution is computed.
    Re: float
      The Reynolds number.
    amplitude: float
      The amplitude of the vortices.
    periodic_directions: list of strings
      Directions with periodic condition at the ends;
      default: None
    directory: string
      Directory of the simulation;
      default: current directory.
    """
    # create flux fields on staggered grid
    n_xu = x.size - (1 if 'x' in periodic_directions else 2)
    xu, yu = x[1: n_xu+1], 0.5*(y[:-1]+y[1:])
    qx = ( self.get_velocity(xu, yu, float(time), float(Re), float(amplitude))[0].values 
          *numpy.outer(y[1:]-y[:-1], numpy.ones(n_xu)) )
    n_yv = y.size - (1 if 'y' in periodic_directions else 2)
    xv, yv = 0.5*(x[:-1]+x[1:]), y[1: n_yv+1]
    qy = ( self.get_velocity(xv, yv, float(time), float(Re), float(amplitude))[1].values
          *numpy.outer(numpy.ones(n_yv), x[1:]-x[:-1]) )
    # create directory where to save files
    directory = '{}/{:0>7}'.format(directory, 0)
    if not os.path.isdir(directory):
      print('[info] creating directory: {} ...'.format(directory))
      os.makedirs(directory)
    sys.path.append(os.path.join(os.environ['PETSC_DIR'], 'bin', 'pythonscripts'))
    import PetscBinaryIO
    # write fluxes
    vec = qx.flatten().view(PetscBinaryIO.Vec)
    file_path = '{}/qx.dat'.format(directory)
    print('[info] writing fluxes in x-direction in file {} ...'.format(file_path))
    PetscBinaryIO.PetscBinaryIO().writeBinaryFile(file_path, [vec,])
    vec = qy.flatten().view(PetscBinaryIO.Vec)
    file_path = '{}/qy.dat'.format(directory)
    print('[info] writing fluxes in y-direction in file {} ...'.format(file_path))
    PetscBinaryIO.PetscBinaryIO().writeBinaryFile(file_path, [vec,])
    # write pressure -- pressure field set to zero everywhere
    vec = numpy.zeros((y.size-1, x.size-1)).flatten().view(PetscBinaryIO.Vec)
    file_path = '{}/phi.dat'.format(directory)
    print('[info] writing pressure in file {} ...'.format(file_path))
    PetscBinaryIO.PetscBinaryIO().writeBinaryFile(file_path, [vec,])