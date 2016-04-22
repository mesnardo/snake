# file: plotVelocityMagnitudeSnake.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Plots the 2D velocity-magnitude field near the snake.
# Run this script from the simulation directory.


from snake.ibamr.simulation import IBAMRSimulation


simulation = IBAMRSimulation()

simulation.plot_field_contours_visit('velocity-magnitude', (0.0, 2.0),
                                     body='flyingSnake2dAoA35ds004filledInside',
                                     solution_folder='numericalSolution',
                                     view=(-0.75, -1.0, 1.50, 1.0),
                                     width=800)
