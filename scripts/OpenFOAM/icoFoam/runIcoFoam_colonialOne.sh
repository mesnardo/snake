#!/bin/sh

#SBATCH --job-name="OFfs25n32"
#SBATCH --output=log%j.out
#SBATCH --error=log%j.err
#SBATCH --partition=short
#SBATCH --time=48:00:00
#SBATCH -n 32

module load openfoam/gcc/2.3.0

# source tool run functions
. $WM_PROJECT_DIR/bin/tools/RunFunctions

# decompose domain for parrallel run
runApplication decomposePar

# run icofoam
time runParallel icoFoam -parallel
