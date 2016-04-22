# file: plotForceCoefficientsCompareKrishnanEtAl2014.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Plots the instantaneous force coefficients
#              and compare to results from Krishnan et al. (2014).
# Run this script from the simulation directory.


import os

from snake.openfoam.simulation import OpenFOAMSimulation
from snake.cuibm.simulation import CuIBMSimulation


simulation = OpenFOAMSimulation(description='IcoFOAM')
simulation.read_forces(display_coefficients=True)
simulation.get_mean_forces(limits=[32.0, 64.0])
simulation.get_strouhal(limits=[32.0, 64.0], order=200)

krishnan = CuIBMSimulation(description='Krishnan et al. (2014)')
krishnan.read_forces(file_path='{}/resources/flyingSnake2d_cuibm_anush/'
                               'flyingSnake2dRe2000AoA35/forces'
                               ''.format(os.environ['SNAKE']))
krishnan.get_mean_forces(limits=[32.0, 64.0])
krishnan.get_strouhal(limits=[32.0, 64.0], order=200)

simulation.plot_forces(display_coefficients=True,
                       display_extrema=True, order=200,
                       limits=(0.0, 80.0, 0.0, 3.0),
                       other_simulations=krishnan,
                       other_coefficients=2.0,
                       save_name='forceCoefficientsCompareKrishnanEtAl2014')
dataframe = simulation.create_dataframe_forces(display_strouhal=True,
                                               display_coefficients=True)
dataframe2 = krishnan.create_dataframe_forces(display_strouhal=True,
                                              display_coefficients=True,
                                              coefficient=2.0)
dataframe = dataframe.append(dataframe2)
print(dataframe)
