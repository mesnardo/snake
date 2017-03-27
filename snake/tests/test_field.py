"""
Tests for the class `Field`.
"""

import numpy

from snake.field import Field


class FieldTest(object):
  def __init__(self):
    x, y = numpy.linspace(0.0, 10.0, 9 * 4), numpy.linspace(-1.0, 1.0, 9 * 5)
    self.field = Field(x=x, y=y, time_step=0,
                       values=numpy.random.rand(y.size, x.size),
                       label='test')
    self.restriction()
    self.get_difference()
    self.subtract()

  def restriction(self):
    print('\nField.restriction() ...'),
    field1 = self.field.restriction([self.field.x, self.field.y])
    field2 = self.field.restriction([self.field.x[::3], self.field.y[::3]])
    field3 = self.field.restriction([self.field.x[::9], self.field.y[::9]])
    assert numpy.allclose(field1.x, self.field.x, atol=1.0E-06)
    assert numpy.allclose(field1.y, self.field.y, atol=1.0E-06)
    assert numpy.allclose(field1.values, self.field.values, atol=1.0E-06)
    assert numpy.allclose(field2.x, self.field.x[::3], atol=1.0E-06)
    assert numpy.allclose(field2.y, self.field.y[::3], atol=1.0E-06)
    assert numpy.allclose(field2.values, self.field.values[::3, ::3],
                          atol=1.0E-06)
    assert numpy.allclose(field3.x, self.field.x[::9], atol=1.0E-06)
    assert numpy.allclose(field3.y, self.field.y[::9], atol=1.0E-06)
    assert numpy.allclose(field3.values, self.field.values[::9, ::9],
                          atol=1.0E-06)
    print('ok')

  def get_difference(self):
    print('\nField.get_difference() ...'),
    assert (self.field.get_difference(self.field,
                                      self.field,
                                      norm='L2') == 0.0)
    assert (self.field.get_difference(self.field,
                                      self.field,
                                      norm='Linf') == 0.0)
    print('ok')

  def subtract(self):
    print('\nField.subtract() ...'),
    self.field.subtract(self.field)
    assert numpy.allclose(self.field.values,
                          numpy.zeros_like(self.field.values),
                          atol=1.0E-06)
    print('ok')


if __name__ == '__main__':
  test = FieldTest()
