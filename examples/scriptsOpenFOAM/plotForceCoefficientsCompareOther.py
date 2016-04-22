# file: plotForceCoefficientsCompareOther.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Plots the instantaneous force coefficients
#              and compare to results from previous simulation.
# Run this script from the simulation directory.


from snake.openfoam.simulation import OpenFOAMSimulation


simulation = OpenFOAMSimulation(description='present')
simulation.read_forces(display_coefficients=True)
simulation.get_mean_forces(limits=[32.0, 64.0])
simulation.get_strouhal(limits=[32.0, 64.0], order=200)

other = OpenFOAMSimulation(description='other',
                           directory='')
other.read_forces(display_coefficients=True)
other.get_mean_forces(limits=[32.0, 64.0])
other.get_strouhal(limits=[32.0, 64.0], order=200)

simulation.plot_forces(display_coefficients=True,
                       display_extrema=True, order=200,
                       limits=(0.0, 80.0, 0.0, 3.0),
                       other_simulations=other,
                       other_coefficients=1.0,
                       save_name='forceCoefficientsCompareOther')
dataframe = simulation.create_dataframe_forces(display_strouhal=True,
                                               display_coefficients=True)
dataframe2 = other.create_dataframe_forces(display_strouhal=True,
                                           display_coefficients=True)
dataframe = dataframe.append(dataframe2)
print(dataframe)
