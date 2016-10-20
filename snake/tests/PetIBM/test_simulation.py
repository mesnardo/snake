"""
Tests for the class `PetIBMSimulation`.
"""

import sys
import os

import numpy

sys.path.append(os.environ['SCRIPTS'])
from library.PetIBM.simulation import PetIBMSimulation


class PetIBMSimulationTest(object):
  def __init__(self):
    self.simulation = PetIBMSimulation()
    self.simulation.directory = os.getcwd()
    self.read_grid()
    self.read_velocity()
    self.read_pressure()

  def read_grid(self):
    print('\nPetIBMSimulation.read_grid() ...')
    x, y = numpy.linspace(0.0, 10.0, 11), numpy.linspace(-1.0, 1.0, 101)
    with open('grid_test.txt', 'w') as outfile:
      # write number of cells
      outfile.write('{}\t{}\n'.format(x.size - 1, y.size - 1))
      # write cell-boundaries in x-direction
      numpy.savetxt(outfile, x, fmt='%.6f')
      # write cell-boundaries in y-direction
      numpy.savetxt(outfile, y, fmt='%.6f')
    # call method to test
    self.simulation.read_grid(file_name='grid_test.txt')
    os.system('rm -f grid_test.txt')
    assert numpy.allclose(x, self.simulation.grid[0], atol=1.0E-06)
    assert numpy.allclose(y, self.simulation.grid[1], atol=1.0E-06)
    print('ok')

  def read_velocity(self):
    print('\nPetIBMSimulation.read_velocity() ...')
    x, y = numpy.linspace(0.0, 10.0, 11), numpy.linspace(-1.0, 1.0, 101)
    # create flux fields on staggered grid
    xu, yu = x[1: -1], 0.5 * (y[:-1] + y[1:])
    u = numpy.random.rand(yu.size, xu.size)
    qx = u * numpy.outer(y[1:] - y[:-1], numpy.ones(xu.size))
    xv, yv = 0.5 * (x[:-1] + x[1:]), y[1: -1]
    v = numpy.random.rand(yv.size, xv.size)
    qy = v * numpy.outer(numpy.ones(yv.size), x[1:] - x[:-1])
    # create directory where to save files
    directory = '{}/{:0>7}'.format(os.getcwd(), 0)
    if not os.path.isdir(directory):
      os.makedirs(directory)
    sys.path.append(os.path.join(os.environ['PETSC_DIR'],
                                 'bin',
                                 'pythonscripts'))
    import PetscBinaryIO
    # write fluxes
    vec = qx.flatten().view(PetscBinaryIO.Vec)
    file_path = '{}/qx.dat'.format(directory)
    PetscBinaryIO.PetscBinaryIO().writeBinaryFile(file_path, [vec, ])
    vec = qy.flatten().view(PetscBinaryIO.Vec)
    file_path = '{}/qy.dat'.format(directory)
    PetscBinaryIO.PetscBinaryIO().writeBinaryFile(file_path, [vec, ])
    # call method to test
    self.simulation.read_velocity(0)
    os.system('rm -rf 0000000')
    assert numpy.allclose(u, self.simulation.x_velocity.values, atol=1.0E-06)
    assert numpy.allclose(xu, self.simulation.x_velocity.x, atol=1.0E-06)
    assert numpy.allclose(yu, self.simulation.x_velocity.y, atol=1.0E-06)
    assert numpy.allclose(v, self.simulation.y_velocity.values, atol=1.0E-06)
    assert numpy.allclose(xv, self.simulation.y_velocity.x, atol=1.0E-06)
    assert numpy.allclose(yv, self.simulation.y_velocity.y, atol=1.0E-06)
    print('ok')

  def read_pressure(self):
    print('\nPetIBMSimulation.read_pressure() ...')
    x, y = numpy.linspace(0.0, 10.0, 11), numpy.linspace(-1.0, 1.0, 101)
    # create pressure field
    xp, yp = 0.5 * (x[:-1] + x[1:]), 0.5 * (y[:-1] + y[1:])
    p = numpy.random.rand(yp.size, xp.size)
    # create directory where to save files
    directory = '{}/{:0>7}'.format(os.getcwd(), 0)
    if not os.path.isdir(directory):
      os.makedirs(directory)
    sys.path.append(os.path.join(os.environ['PETSC_DIR'],
                                 'bin',
                                 'pythonscripts'))
    import PetscBinaryIO
    # write fluxes
    vec = p.flatten().view(PetscBinaryIO.Vec)
    file_path = '{}/phi.dat'.format(directory)
    PetscBinaryIO.PetscBinaryIO().writeBinaryFile(file_path, [vec, ])
    # call method to test
    self.simulation.read_pressure(0)
    os.system('rm -rf 0000000')
    assert numpy.allclose(p, self.simulation.pressure.values, atol=1.0E-06)
    assert numpy.allclose(xp, self.simulation.pressure.x, atol=1.0E-06)
    assert numpy.allclose(yp, self.simulation.pressure.y, atol=1.0E-06)
    print('ok')


if __name__ == '__main__':
  test = PetIBMSimulationTest()
