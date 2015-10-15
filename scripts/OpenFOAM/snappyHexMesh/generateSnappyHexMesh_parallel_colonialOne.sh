#!/bin/sh

#SBATCH --job-name="sHMParallel"
#SBATCH --output=log.%j.out
#SBATCH --error=log.%j.err
#SBATCH --partition=short
#SBATCH --time=02:00:00
#SBATCH -n 4

N=4

module load openfoam/gcc/2.3.0

# source tool run functions
. $WM_PROJECT_DIR/bin/tools/RunFunctions

# Remove previous mesh and keep dictionary for blockMesh
find constant/polyMesh -type f \! -name 'blockMeshDict' -delete
# clean previous mesh
rm -f log.*
rm -f constant/triSurface/*.eMesh
rm -rf constant/extendedFeatureEdgeMesh
rm -rf processor*

# make dummy initial conditions folder
mv 0 0.org
mkdir 0

# create base mesh
runApplication blockMesh

# create edge mesh for boxes
runApplication surfaceFeatureExtract

# decompose base mesh
cp system/decomposeParDict.hierarchical system/decomposeParDict
runApplication decomposePar

# create castellated mesh (run in parallel)
cp system/decomposeParDict.ptscotch system/decomposeParDict
runParallel snappyHexMesh $N -overwrite -parallel

# reconstruct mesh
runApplication reconstructParMesh -mergeTol 1.0E-06 -latestTime

# extrude mesh in the z-direction
runApplication extrudeMesh

# create patches
runApplication createPatch -overwrite

# check mesh quality
runApplication checkMesh

# set back initial conditions folder
rm -rf 0
mv 0.org 0

# use simple method for decomposeParDict
cp system/decomposeParDict.simple system/decomposeParDict
