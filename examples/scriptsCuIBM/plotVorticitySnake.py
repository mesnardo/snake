# file: plotVorticitySnake.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Plots the 2D vorticity field near the snake.
# Run this script from the simulation directory.


from snake.cuibm.simulation import CuIBMSimulation


simulation = CuIBMSimulation()
simulation.read_grid()

for time_step in simulation.get_time_steps():
  simulation.read_fields('vorticity', time_step)
  simulation.plot_contour('vorticity',
                          field_range=[-5.0, 5.0, 101],
                          filled_contour=True,
                          view=[-0.75, -1.0, 1.50, 1.0],,
                          width=8.0)