# file: plotForceCoefficientsCompare.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Plots the instantaneous force coefficients 
#              and compare to other results.
# Run this script from the simulation directory.


import os

from snake.simulation import Simulation
from snake.petibm.simulation import PetIBMSimulation


simulation = PetIBMSimulation(description='PetIBM (present)')
simulation.read_forces()
simulation.get_mean_forces(limits=[32.0, 64.0])
simulation.get_strouhal(limits=[32.0, 64.0], order=200)

other = Simulation(description='',
                   directory='',
                   software='')
other.read_forces()
other.get_mean_forces(limits=[32.0, 64.0])
other.get_strouhal(limits=[32.0, 64.0], order=200)

simulation.plot_forces(display_coefficients=True, 
                       coefficient=2.0,
                       display_extrema=True, order=200,
                       limits=(0.0, 80.0, 0.0, 3.0),
                       other_simulations=other, 
                       other_coefficients=2.0,
                       save_name='forceCoefficientsCompare')

dataframe = simulation.create_dataframe_forces(display_strouhal=True,
                                               display_coefficients=True,
                                               coefficient=2.0)
dataframe = dataframe.append(other.create_dataframe_forces(display_strouhal=True,
                                                           display_coefficients=True,
                                                           coefficient=2.0))
print(dataframe)
