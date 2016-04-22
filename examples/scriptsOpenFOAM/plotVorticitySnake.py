# file: plotVorticitySnake.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Plots the 2D vorticity field near the snake.
# Run this script from the simulation directory.


from snake.openfoam.simulation import OpenFOAMSimulation


simulation = OpenFOAMSimulation()
simulation.plot_field_contours_paraview('vorticity',
                                        field_range=(-5.0, 5.0),
                                        view=(-0.75, -1.0, 1.50, 1.0),
                                        times=(0.0, 100.0, 2.0),
                                        width=800)
