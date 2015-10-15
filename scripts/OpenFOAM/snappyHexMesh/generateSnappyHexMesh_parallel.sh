#!/bin/sh


# source tool run functions
. $WM_PROJECT_DIR/bin/tools/RunFunctions

# Remove previous mesh and keep the dictionary for blockMesh
find constant/polyMesh -type f \! -name 'blockMeshDict' -delete
# clean previous mesh
rm -f log.*
rm -f constant/triSurface/*.eMesh
rm -rf constant/extendedFeatureEdgeMesh
rm -rf processor*

# create dummy initial conditions folder
mv 0 0.org
mkdir 0

# create the base mesh
runApplication blockMesh

# create edge mesh for boxes
runApplication surfaceFeatureExtract

# decompose the base mesh
cp system/decomposeParDict.hierarchical system/decomposeParDict
runApplication decomposePar

# create the castellated mesh (run in parallel)
cp system/decomposeParDict.ptscotch system/decomposeParDict
N=4
runParallel snappyHexMesh $N -overwrite -parallel
MPIRUN="/opt/OpenFOAM/ThirdParty-2.2.2/platforms/linux64Gcc/openmpi-1.6.3/bin/mpirun"
$MPIRUN -np $N snappyHexMesh -overwrite -parallel > log.snappyHexMesh

# reconstruct mesh
runApplication reconstructParMesh -mergeTol 1.0E-06 -latestTime

# extrude the mesh in the z-direction
runApplication extrudeMesh

# create patches
runApplication createPatch -overwrite

# check the quality of the mesh
runApplication checkMesh

# set back initial conditions folder
rm -rf 0
mv 0.org 0

# use simple method for decomposeParDict
cp system/decomposeParDict.simple system/decomposeParDict
