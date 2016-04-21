# file: plotForceCoefficients.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Plots the instantaneous force coefficients.
# Run this script from the simulation directory.


from snake.petibm.simulation import PetIBMSimulation


simulation = PetIBMSimulation()
simulation.read_forces()
simulation.get_mean_forces(limits=[32.0, 64.0])
simulation.get_strouhal(limits=[32.0, 64.0], order=200)

simulation.plot_forces(display_coefficients=True, 
                       coefficient=2.0,
                       display_extrema=True, order=200,
                       limits=(0.0, 80.0, 0.0, 3.0),
                       save_name='forceCoefficients')
dataframe = simulation.create_dataframe_forces(display_strouhal=True,
                                               display_coefficients=True,
                                               coefficient=2.0)
print(dataframe)
