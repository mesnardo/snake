#!/bin/sh


# source tool run functions
. $WM_PROJECT_DIR/bin/tools/RunFunctions

# Remove previous mesh and keep the dictionary for blockMesh
find constant/polyMesh -type f \! -name 'blockMeshDict' -delete
# clean previous mesh
rm -f log.*
rm -f constant/triSurface/*.eMesh
rm -rf constant/extendedFeatureEdgeMesh

# create the base mesh
runApplication blockMesh

# create edge mesh for boxes
runApplication surfaceFeatureExtract

# create the castellated mesh
runApplication snappyHexMesh -overwrite

# extrude the mesh in the z-direction
runApplication extrudeMesh

# create patches
runApplication createPatch -overwrite

# check the quality of the mesh
runApplication checkMesh
