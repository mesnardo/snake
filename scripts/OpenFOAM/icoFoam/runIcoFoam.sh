#!/bin/sh

# file: runIcoFoam.sh
# author: Olivier Mesnard (mesnardo@gwu.edu)
# brief: Runs IcoFOAM in serial.


# source tool run functions
. $WM_PROJECT_DIR/bin/tools/RunFunctions

mkdir log.run

# run icofoam
time runApplication icoFoam
mv log.icoFoam log.run