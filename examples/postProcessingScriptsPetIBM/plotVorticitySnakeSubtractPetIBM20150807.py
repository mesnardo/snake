# file: plotVorticitySnakeSubtractPetIBM20150807.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Plots the 2D vorticity field near the snake
#              and subtract the solution from previous simulation.
# Run this script from the simulation directory.


import os

from snake.petibm.simulation import PetIBMSimulation
from snake.body import Body


simulation = PetIBMSimulation()
simulation.read_grid()

other = PetIBMSimulation(description='PetIBM (previous)',
                         directory='{}/simulations_PetIBM/flyingSnake/2d/'
                                   'cuibmGrid/velocityCGPoissonBiCGStab/'
                                   'flyingSnake2dRe2000AoA35_20150807'
                                   ''.format(os.environ['HOME']))
other.read_grid()

body = Body(file_path='flyingSnake2dAoA35ds0.004.body')

for time_step in simulation.get_time_steps():
  simulation.read_fields('vorticity', time_step)
  other.read_fields('vorticity', time_step)
  simulation.subtract(other, 'vorticity', 'vorticity-subtracted')
  simulation.plot_contour('vorticity-subtracted',
                          field_range=[-5.0, 5.0, 101],
                          filled_contour=True,
                          view=[-0.75, -1.0, 1.50, 1.0],
                          bodies=body,
                          width=8.0)