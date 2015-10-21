#!/bin/sh

# file: runIcoFoam.sh
# author: Olivier Mesnard (mesnardo@gwu.edu)
# brief: Runs IcoFOAM in serial.


# remove previous run
rm -rf log.run && mkdir log.run

# source tool run functions
. $WM_PROJECT_DIR/bin/tools/RunFunctions

# run icofoam
runApplication icoFoam
mv log.icofoam log.run