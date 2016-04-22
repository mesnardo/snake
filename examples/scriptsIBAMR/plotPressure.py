# file: plotPressure.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Plots the 2D pressure field.
# Run this script from the simulation directory.


from snake.ibamr.simulation import IBAMRSimulation


simulation = IBAMRSimulation()

simulation.plot_field_contours_visit('pressure', (-1.0, 0.5),
                                     body='flyingSnake2dAoA35ds004filledInside',
                                     solution_folder='numericalSolution',
                                     view=(-15.0, -15.0, 15.0, 15.0),
                                     width=800)
