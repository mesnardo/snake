#!/bin/sh

# file: runIcoFoam_colonialOne.sh
# author: Olivier Mesnard (mesnardo@gwu.edu)
# brief: Runs IcoFOAM on multi-nodes on Colonial One.

#SBATCH --job-name="OFfs25n32"
#SBATCH --output=log%j.out
#SBATCH --error=log%j.err
#SBATCH --partition=short
#SBATCH --time=48:00:00
#SBATCH -n 32

module load openfoam/gcc/2.3.0

# remove previous run
rm -rf log.run && mkdir log.run

# source tool run functions
. $WM_PROJECT_DIR/bin/tools/RunFunctions

# decompose domain for parrallel run
runApplication decomposePar
mv log.decomposePar log.run

# run icofoam
time runParallel icoFoam -parallel
mv log.icoFoam log.run