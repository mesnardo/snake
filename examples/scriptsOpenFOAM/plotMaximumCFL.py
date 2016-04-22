# file: plotMaximumCFL.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Plot the instantaneous maximum CFL number.
# Run this script from the simulation directory.


from snake.openfoam.simulation import OpenFOAMSimulation


simulation = OpenFOAMSimulation()
simulation.read_maximum_cfl('log.run/log.icoFoam')
simulation.get_mean_maximum_cfl(limits=(60.0, 80.0))
simulation.plot_maximum_cfl(display_extrema=True, order=200,
                            limits=(0.0, 100.0, 0.5, 2.0),
                            save_name='maximumCFL')
