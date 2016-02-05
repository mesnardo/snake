# file: ioPetIBM.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Collection of IO functions for PetIBM.


import os
import sys

import numpy
from matplotlib import pyplot, cm
# load default style of matplotlib figures
pyplot.style.use('{}/styles/mesnardo.mplstyle'.format(os.environ['SCRIPTS']))
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

sys.path.append(os.path.join(os.environ['PETSC_DIR'], 'bin', 'pythonscripts'))
import PetscBinaryIO


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
    label: string
      Label of the new field; default: None.

    Returns
    -------
    field: Field object
      The field difference.
    """
    return Field(x=self.x, y=self.y, values=self.values-other.values, 
                 time_step=self.time_step, label=label)



class Body(object):
  """Contains information about an immersed body."""
  def __init__(self, path):
    """Reads the body coordinates from given file.

    Parameters
    ----------
    path: string
      Path of the file containing the body coordinates.
    """
    self.path = path
    self.x, self.y = self.read_coordinates()

  def read_coordinates(self):
    """Reads the coordinates from file."""
    with open(self.path, 'r') as infile:
      return numpy.loadtxt(infile, dtype=float, skiprows=1, unpack=True)


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


def read_grid(case_directory, binary=False):
  """Reads the coordinates from the file grid.txt.

  Parameters
  ----------
  case_directory: str
    Directory of the simulation.

  Returns
  -------
  grid: Numpy array
    Coordinates of the grid-nodes in each direction.
  binary: bool
    Useless here. (Set `True` if grid is a binary file; default: False.)
  """
  print('[info] reading the grid ...'),
  grid_path = '{}/grid.txt'.format(case_directory)
  with open(grid_path, 'r') as infile:
    nCells = numpy.array([int(n) for n in infile.readline().strip().split()])
    coords = numpy.loadtxt(infile, dtype=float)
  print('done')
  return numpy.array(numpy.split(coords, numpy.cumsum(nCells[:-1]+1)))


def get_field(field_name, directory, time_step, coords, binary=False):
  """Gets the field at a given time-step and the mesh-grid. 

  Parameters
  ----------
  field_name: string
    Name of the field to get.
  directory: string
    Directory of the simulation.
  time_step: integer
    Time-step at which the solution is read.
  coords: list of numpy 1d arrays
    List of coordinates along each direction.
  binary: bool
    Set 'True' is solution written in binary format; default: False.

  Returns
  -------
  field: Field object
    The field.
  """
  if field_name == 'vorticity':
    return compute_vorticity(directory, time_step, coords, binary=binary)
  elif field_name == 'x-velocity':
    return read_velocity(directory, time_step, coords, binary=binary)[0]
  elif field_name == 'y-velocity':
    return read_velocity(directory, time_step, coords, binary=binary)[1]
  elif field_name == 'pressure':
    return read_pressure(directory, time_step, coords, binary=binary)
  else:
    print('[error] Field {} provided is not in the list {}'.format(field_name,
                                                                   known_field_names))
    sys.exit()


def read_velocity(case_directory, time_step, coords, periodic=[], binary=False):
  """Reads the velocity field at a given time-step.

  Parameters
  ----------
  case_directory: str
    Directory of the simulation.
  time_step: int
    Time-step at which the field will be read.
  coords: Numpy array
    Coordinates in each direction.
  periodic: list(str)
    List of directions with periodic boundary conditions.
  binary: bool
    Useless here. (Set `True` if grid is a binary file; default: False.)

  Returns
  -------
  field_vector: list(Field)
    List containing the velocity field in each direction.
  """
  print('[time-step {}] reading velocity field ...'.format(time_step)),
  dim3 = (True if len(coords) == 3 else False)
  x, y, z = coords[0], coords[1], (None if not dim3 else coords[2])
  # compute cell-widths
  dx, dy, dz = x[1:]-x[:-1], y[1:]-y[:-1], (None if not dim3 else z[1:]-z[:-1])
  # number of of cells
  nx, ny, nz = dx.size, dy.size, (None if not dim3 else dz.size)
  # folder with numerical solution
  time_step_directory = '{}/{:0>7}'.format(case_directory, time_step)
  # read x-flux
  flux_path = '{}/qx.dat'.format(time_step_directory)
  qx = PetscBinaryIO.PetscBinaryIO().readBinaryFile(flux_path)[0]
  # read y-flux
  flux_path = '{}/qy.dat'.format(time_step_directory)
  qy = PetscBinaryIO.PetscBinaryIO().readBinaryFile(flux_path)[0]
  # get velocity nodes coordinates
  xu, yu = x[1:-1], 0.5*(y[:-1]+y[1:])
  xv, yv = 0.5*(x[:-1]+x[1:]), y[1:-1]
  if dim3:
    # get third-dimension coordinate of x-velocity nodes
    zu = 0.5*(z[:-1]+z[1:])
    # compute x-velocity field
    qx = qx.reshape((nz, ny, (nx if 'x' in periodic else nx-1)))
    u = ( qx[:, :, :(-1 if 'x' in periodic else None)]
          /reduce(numpy.multiply, numpy.ix_(dz, dy, numpy.ones(nx-1))) )
    # get third-dimension coordinate of y-velocity nodes
    zv = 0.5*(z[:-1]+z[1:])
    # compute y-velocity field
    qy = qy.reshape((nz, (ny if 'y' in periodic else ny-1), nx))
    v = ( qy[:, :(-1 if 'y' in periodic else None), :]
          /reduce(numpy.multiply, numpy.ix_(dz, numpy.ones(ny-1), dx)) )
    # read z-flux
    flux_path = '{}/qz.dat'.format(time_step_directory)
    qz = PetscBinaryIO.PetscBinaryIO().readBinaryFile(flux_path)[0]
    # get coordinates of z-velocity nodes
    xw, yw, zw = 0.5*(x[:-1]+x[1:]), 0.5*(y[:-1]+y[1:]), z[1:-1]
    # compute z-velocity field
    qz = qz.reshape(((nz if 'z' in periodic else nz-1), ny, nx))
    w = ( qz[:(-1 if 'z' in periodic else None), :, :]
          /reduce(numpy.multiply, numpy.ix_(numpy.ones(nz-1), dy, dx)) )
    # tests
    assert (zu.size, yu.size, xu.size) == u.shape
    assert (zv.size, yv.size, xv.size) == v.shape
    assert (zw.size, yw.size, xw.size) == w.shape
    print('done')
    return [Field(x=xu, y=yu, z=zu, time_step=time_step, values=u, label='u-velocity'),
            Field(x=xv, y=yv, z=zv, time_step=time_step, values=v, label='v-velocity'),
            Field(x=xw, y=yw, z=zw, time_step=time_step, values=w, label='w-velocity')]
  else:
    # compute x-velocity field
    qx = qx.reshape((ny, (nx if 'x' in periodic else nx-1)))
    u = qx[:, :(-1 if 'x' in periodic else None)]/numpy.outer(dy, numpy.ones(nx-1))
    # compute y-velocity field
    qy = qy.reshape(((ny if 'y' in periodic else ny-1), nx))
    v = qy[:(-1 if 'y' in periodic else None), :]/numpy.outer(numpy.ones(ny-1), dx)
    # tests
    assert (yu.size, xu.size) == u.shape
    assert (yv.size, xv.size) == v.shape
    print('done')
    return [Field(x=xu, y=yu, time_step=time_step, values=u, label='u-velocity'), 
            Field(x=xv, y=yv, time_step=time_step, values=v, label='v-velocity')]


def read_pressure(case_directory, time_step, coords, binary=False):
  """Reads the pressure fields from file given the time-step.

  Parameters
  ----------
  case_directory: str
    Directory of the simulation.
  time_step: int
    Time-step at which the field will be read.
  coords: Numpy array
    Grid coordinates in each direction.
  binary: bool
    Useless here. (Set `True` if grid is a binary file; default: False.)

  Returns
  -------
  pressure: Field
    The pressure field.
  """
  print('[time-step {}] reading the pressure field ...'.format(time_step)),
  dim3 = (True if len(coords) == 3 else False)
  x, y, z = coords[0], coords[1], (None if not dim3 else coords[2])
  # folder with numerical solution
  time_step_directory = '{}/{:0>7}'.format(case_directory, time_step)
  # pressure
  pressure_path = '{}/phi.dat'.format(time_step_directory)
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
    print('done')
    return Field(x=xp, y=yp, z=zp, values=p, label='pressure')
  else:
    # compute pressure field
    p = p.reshape((ny, nx))
    # tests
    assert (yp.size, xp.size) == p.shape
    print('done')
    return Field(x=xp, y=yp, time_step=time_step, values=p, label='pressure')


def write_vtk(field, case_directory, time_step, name, 
              view=[[float('-inf'), float('-inf'), float('-inf')], 
                    [float('inf'), float('inf'), float('inf')]],
              stride=1):
  """Writes the field in a .vtk file.

  Parameters
  ----------
  field: Field
    Field to write.
  case_directory: str
    Directory of the simulation.
  time_step: int
    Time-step to write.
  name: str
    Name of the field.
  view: list(float)
    Bottom-left and top-right coordinates of the rectangulat view to write;
    default: the whole domain is written.
  stride: int
    Stride at which the field is written; default: 1.
  """
  print('Write the {} field into .vtk file ...'.format(name))
  if type(field) is not list:
    field = [field]
  try:
    dim3 = field[0].z.all()
  except:
    dim3 = False
  scalar = (True if len(field) == 1 else False)
  # get mask for the view
  mx = numpy.where(numpy.logical_and(field[0].x > view[0][0],
                                     field[0].x < view[1][0]))[0][::stride]
  my = numpy.where(numpy.logical_and(field[0].y > view[0][1],
                                     field[0].y < view[1][1]))[0][::stride]
  if dim3:
    mz = numpy.where(numpy.logical_and(field[0].z > view[0][2],
                                       field[0].z < view[1][2]))[0][::stride]
  # create directory where .vtk file will be saved
  vtk_directory = '{}/vtk_files/{}'.format(case_directory, name)
  if not os.path.isdir(vtk_directory):
    print('Make directory: {}'.format(vtk_directory))
    os.makedirs(vtk_directory)
  vtk_file_path = '{}/{}{:0>7}.vtk'.format(vtk_directory, name, time_step)
  # get coordinates within the view
  x = field[0].x[mx]
  y = field[0].y[my]
  z = (None if not dim3 else field[0].z[mz])
  nx, ny, nz = x.size, y.size, (1 if not dim3 else z.size)
  # write .vtk file
  with open(vtk_file_path, 'w') as outfile:
    outfile.write('# vtk DataFile Version 3.0\n')
    outfile.write('contains {} field\n'.format(name))
    outfile.write('ASCII\n')
    outfile.write('DATASET RECTILINEAR_GRID\n')
    outfile.write('DIMENSIONS {} {} {}\n'.format(nx, ny, nz))
    outfile.write('X_COORDINATES {} double\n'.format(nx))
    numpy.savetxt(outfile, x, fmt='%f')
    outfile.write('Y_COORDINATES {} double\n'.format(ny))
    numpy.savetxt(outfile, y, fmt='%f')
    outfile.write('Z_COORDINATES {} double\n'.format(nz))
    if dim3:
      numpy.savetxt(outfile, z, fmt='%f')
    else:
      outfile.write('0.0\n')
    outfile.write('POINT_DATA {}\n'.format(nx*ny*nz))
    if scalar:
      outfile.write('\nSCALARS {} double 1\nLOOKUP_TABLE default\n'.format(name))
      if dim3:
        values = field[0].values[mz[0]:mz[-1]+1, 
                                 my[0]:my[-1]+1, 
                                 mx[0]:mx[-1]+1]
      else:
        values = field[0].values[my[0]:my[-1]+1, 
                                 mx[0]:mx[-1]+1]
      numpy.savetxt(outfile, values.flatten(), 
                    fmt='%.6f', delimiter='\t')
    else:
      outfile.write('\nVECTORS {} double\n'.format(name))
      if dim3:
        values_x = field[0].values[mz[0]:mz[-1]+1, 
                                   my[0]:my[-1]+1, 
                                   mx[0]:mx[-1]+1]
        values_y = field[1].values[mz[0]:mz[-1]+1, 
                                   my[0]:my[-1]+1, 
                                   mx[0]:mx[-1]+1]
        values_z = field[2].values[mz[0]:mz[-1]+1, 
                                   my[0]:my[-1]+1, 
                                   mx[0]:mx[-1]+1]
        numpy.savetxt(outfile, 
                      numpy.c_[values_x.flatten(), 
                               values_y.flatten(), 
                               values_z.flatten()],
                      fmt='%.6f', delimiter='\t')
      else:
        values_x = field[0].values[my[0]:my[-1]+1, 
                                      mx[0]:mx[-1]+1]
        values_y = field[1].values[my[0]:my[-1]+1, 
                                      mx[0]:mx[-1]+1]
        numpy.savetxt(outfile, numpy.c_[values_x.flatten(),
                                        values_y.flatten()],
                      fmt='%6f', delimiter='\t')    


def plot_contour(field, field_range, 
                 directory=os.getcwd(),
                 view=[float('-inf'), float('-inf'), float('inf'), float('inf')],
                 bodies=[],
                 save_name=None, width=8.0, dpi=100): 
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
  bodies: list of Body objects
    The immersed bodies to add to the figure; default: [] (no immersed body).
  save_name: string
    Prefix used to create the images directory and to save the .png files; default: None.
  width: float
    Width of the figure (in inches); default: 8.
  dpi: int
    Dots per inch (resolution); default: 100
  """
  # create images directory
  x_left = ('left' if view[0] == float('-inf') else '{:.2f}'.format(view[0]))
  y_bottom = ('bottom' if view[1] == float('-inf') else '{:.2f}'.format(view[1]))
  x_right = ('right' if view[2] == float('inf') else '{:.2f}'.format(view[2]))
  y_top = ('top' if view[3] == float('inf') else '{:.2f}'.format(view[3]))
  save_name = (field.label if not save_name else save_name)
  images_directory = '{}/images/{}_{}_{}_{}_{}'.format(directory, save_name, 
                                                       x_left, y_bottom, x_right, y_top)
  if not os.path.isdir(images_directory):
    print('[info] creating images directory: {} ...'.format(images_directory)),
    os.makedirs(images_directory)
    print('done')

  print('[info] plotting the {} contour ...'.format(field.label)),
  x_start, x_end = max(view[0], field.x.min()), min(view[2], field.x.max())
  y_start, y_end = max(view[1], field.y.min()), min(view[3], field.y.max())
  height = width*(y_end-y_start)/(x_end-x_start)
  fig, ax = pyplot.subplots(figsize=(width, height), dpi=dpi)
  ax.tick_params(axis='x', labelbottom='off')
  ax.tick_params(axis='y', labelleft='off')
  # create filled contour
  if field_range:
    levels = numpy.linspace(*field_range)
  else:
    levels = numpy.linspace(field.values.min(), field.values.max(), 101)
  color_map = {'pressure': cm.jet, 'vorticity': cm.RdBu_r,
               'x-velocity': cm.RdBu_r, 'x-velocity': cm.RdBu_r}
  X, Y = numpy.meshgrid(field.x, field.y)
  cont = ax.contourf(X, Y, field.values, 
                     levels=levels, extend='both', 
                     cmap=(cm.RdBu_r if field.label not in color_map.keys()
                                     else color_map[field.label]))
  # create colorbar
  if field_range:
    colorbar_ticks = numpy.linspace(field_range[0], field_range[1], 5)
  else:
    colorbar_ticks = numpy.linspace(field.values.min(), field.values.max(), 5)
  ains = inset_axes(pyplot.gca(), width='30%', height='2%', loc=3)
  cont_bar = fig.colorbar(cont, 
                          cax=ains, orientation='horizontal',
                          ticks=colorbar_ticks, format='%.01f')
  cont_bar.ax.tick_params(labelsize=10) 
  ax.text(0.05, 0.12, field.label, transform=ax.transAxes, fontsize=10)
  cont_bar.ax.xaxis.set_ticks_position('top')
  # draw body
  for body in bodies:
    ax.plot(body.x, body.y, 
            color='black', linewidth=1, linestyle='-')
  # set limits
  ax.axis([x_start, x_end, y_start, y_end])
  ax.set_aspect('equal')
  # save image
  image_path = '{}/{}{:0>7}.png'.format(images_directory, field.label, field.time_step)
  pyplot.savefig(image_path, dpi=dpi, bbox_inches='tight', pad_inches=0)
  pyplot.close()
  print('done')


def compute_vorticity(directory, time_step, coords, binary=False):
  """Computes the vorticity field for a two-dimensional simulation.

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
  vorticity: ioPetIBM.Field object
    The vorticity field.
  """
  u, v = read_velocity(directory, time_step, coords, binary=binary)
  print('[time-step {}] computing the vorticity field ...'.format(time_step)),
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
  return Field(x=xw, y=yw, values=w, time_step=time_step, label='vorticity')


if __name__ == '__main__':
  pass