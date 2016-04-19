# file: plotForceCoefficientsCompareIBAMR.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Plots the instantaneous force coefficients 
#              and compare to the results obtained with IBAMR.
# Run this script from the simulation directory.


import os

from snake.simulation import Simulation
from snake.petibm.simulation import PetIBMSimulation


simulation = PetIBMSimulation(description='PetIBM (present)')
simulation.read_forces()
simulation.get_mean_forces(limits=[32.0, 64.0])
simulation.get_strouhal(limits=[32.0, 64.0], order=200)

ibamr = Simulation(description='IBAMR',
                   directory='{}/simulations_IBAMR/flyingSnake2d/'
                             'discretizedBody/flyingSnake2dRe2000AoA35_20151115'
                             ''.format(os.environ['HOME']),
                   software='ibamr')
ibamr.read_forces()
ibamr.get_mean_forces(limits=[32.0, 64.0])
ibamr.get_strouhal(limits=[32.0, 64.0], order=200)

simulation.plot_forces(display_coefficients=True, 
                       coefficient=2.0,
                       display_extrema=True, order=200,
                       limits=(0.0, 80.0, 0.0, 3.0),
                       other_simulations=ibamr, 
                       other_coefficients=-2.0,
                       save_name='forceCoefficientsCompareIBAMR')

dataframe = simulation.create_dataframe_forces(display_strouhal=True,
                                               display_coefficients=True,
                                               coefficient=2.0)
dataframe = dataframe.append(ibamr.create_dataframe_forces(display_strouhal=True,
                                                           display_coefficients=True,
                                                           coefficient=-2.0))
print(dataframe)
