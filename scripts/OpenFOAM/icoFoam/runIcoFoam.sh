#!/bin/sh

# file: runIcoFoam.sh
# author: Olivier Mesnard (mesnardo@gwu.edu)
# brief: Runs IcoFOAM in serial.


# source tool run functions
. $WM_PROJECT_DIR/bin/tools/RunFunctions

# remove previous run
rm -rf log.run && mkdir log.run

# run icofoam
runApplication icoFoam
mv log.icoFoam log.run