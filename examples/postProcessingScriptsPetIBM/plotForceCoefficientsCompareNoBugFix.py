# file: plotForceCoefficients.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Plots the instantaneous force coefficients 
#              and compare to the results obtained with a previous version 
#              of PetIBM with a bug in the discrete delta function.
# Run this script from the simulation directory.


import os

from snake.petibm.simulation import PetIBMSimulation


simulation = PetIBMSimulation(description='PetIBM (bug-fix)')
simulation.read_forces()
simulation.get_mean_forces(limits=[32.0, 64.0])
simulation.get_strouhal(limits=[32.0, 64.0], order=200)

previous = PetIBMSimulation(description='PetIBM (previous)',
                            directory='{}/simulations_PetIBM/flyingSnake/2d/'
                                      'cuibmGrid/velocityCGPoissonBiCGStab/'
                                      'flyingSnake2dRe2000AoA35_20150807'
                                      ''.format(os.environ['HOME']))
previous.read_forces()
previous.get_mean_forces(limits=[32.0, 64.0])
previous.get_strouhal(limits=[32.0, 64.0], order=200)

simulation.plot_forces(display_coefficients=True, 
                       coefficient=2.0,
                       display_extrema=True, order=200,
                       limits=(0.0, 80.0, 0.0, 3.0),
                       other_simulations=previous, 
                       other_coefficients=2.0,
                       save_name='forceCoefficientsCompareNoBugFix')

dataframe = simulation.create_dataframe_forces(display_strouhal=True,
                                               display_coefficients=True,
                                               coefficient=2.0)
dataframe = dataframe.append(previous.create_dataframe_forces(display_strouhal=True,
                                      display_coefficients=True,
                                      coefficient=2.0))
print(dataframe)