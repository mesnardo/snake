"""
Tests functions of the module `convergence`.
"""

import numpy

from snake.field import Field
from snake import convergence


def test_same_grid():
  """
  Computes the observed order of convergence using three solutions
  on the same grid.

  The first and last fields are a zero-solution; the middle solution is random.
  Therefore, no matter the norm used, we expect an order of convergence of 0.
  """
  # create grid
  x, y = numpy.linspace(0.0, 1.0, 11), numpy.linspace(0.0, 10.0, 51)
  # create three fields on the same grid
  field1 = Field(x=x, y=y, time_step=0, label='field1',
                 values=numpy.zeros((y.size, x.size)))
  field2 = Field(x=x, y=y, time_step=0, label='field2',
                 values=numpy.random.rand(y.size, x.size))
  field3 = Field(x=x, y=y, time_step=0, label='field3',
                 values=numpy.zeros((y.size, x.size)))
  # compute observed order of convergence in L2-norm
  p = convergence.get_observed_order(field1, field2, field3,
                                     3, [field1.x, field1.y])
  assert p == 0.0
  # compute observed order of convergence in Linf-norm
  p = convergence.get_observed_order(field1, field2, field3,
                                     3, [field1.x, field1.y],
                                     order=numpy.inf)
  assert p == 0.0


def test_three_grids(nx=11, ny=11, ratio=3, offset=0):
  """
  Computes the observed order of convergence using the solution on three
  consecutive grids with constant refinement ratio.

  The solution on the finest grid is random.
  The solution of the medium grid is the finest solution restricted
  and incremented by 1.
  The solution of the coarsest grid is the finest solution restricted
  and incremented by 1+ratio.
  Therefore, no matter the norm used, we expect an order of convergence of 1.

  Parameters
  ----------
  nx, ny: integers, optional
    Number of grid-points along each direction on the grid used a mask
    to project the three solutions;
    default: 11, 11.
  ratio: integer, optional
    Grid refinement ratio;
    default: 3.
  offset: integer, optional
    Position of the coarsest grid relatively to the mask grid;
    default: 0 (the coarsest solution is defined on the mask grid)
  """
  # grid used as mask
  grid = [numpy.random.random(nx), numpy.random.random(ny)]
  # create fields
  fine = Field(values=numpy.random.rand(ny * ratio**(offset + 2),
                                        nx * ratio**(offset + 2)),
               label='fine')
  medium = Field(values=fine.values[::ratio, ::ratio] + 1.0,
                 label='medium')
  coarse = Field(values=fine.values[::ratio**2, ::ratio**2] + (1.0 + ratio),
                 label='coarse')
  # fill nodal stations
  coarse.x = numpy.ones(nx * ratio**offset)
  coarse.y = numpy.ones(ny * ratio**offset)
  coarse.x[::ratio**offset] = grid[0][:]
  coarse.y[::ratio**offset] = grid[1][:]
  medium.x = numpy.ones(nx * ratio**(offset + 1))
  medium.y = numpy.ones(ny * ratio**(offset + 1))
  medium.x[::ratio**(offset + 1)] = grid[0][:]
  medium.y[::ratio**(offset + 1)] = grid[1][:]
  fine.x = numpy.ones(nx * ratio**(offset + 2))
  fine.y = numpy.ones(ny * ratio**(offset + 2))
  fine.x[::ratio**(offset + 2)] = grid[0][:]
  fine.y[::ratio**(offset + 2)] = grid[1][:]
  # compute observed order of convergence
  p = convergence.get_observed_order(coarse, medium, fine, ratio, grid)
  assert p == 1.0
  p = convergence.get_observed_order(coarse, medium, fine, ratio, grid,
                                     order=numpy.inf)
  assert p == 1.0


def main():
  test_same_grid()
  test_three_grids(nx=11, ny=11, ratio=2, offset=0)
  test_three_grids(nx=11, ny=11, ratio=2, offset=1)
  test_three_grids(nx=10, ny=21, ratio=3, offset=0)
  test_three_grids(nx=21, ny=10, ratio=3, offset=1)


if __name__ == '__main__':
  main()
