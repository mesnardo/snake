#!/bin/sh

# file: generateSnappyHexMesh_serial.sh
# author: Olivier Mesnard (mesnardo@gwu.edu)
# brief: Generates a mesh with snappyHexMesh on 1 processor.


# source tool run functions
. $WM_PROJECT_DIR/bin/tools/RunFunctions

# clean previous mesh
find constant/polyMesh -type f \! -name 'blockMeshDict' -delete
rm -rf log.mesh
mkdir log.mesh

# create base mesh
runApplication blockMesh
mv log.blockMesh log.mesh

# create castellated mesh
runApplication snappyHexMesh -overwrite
mv log.snappyHexMesh log.mesh

# extrude mesh in third direction
runApplication extrudeMesh
mv log.extrudeMesh log.mesh

# create patches
runApplication createPatch -overwrite
mv log.createPatch log.mesh

# check mesh quality
runApplication checkMesh
mv log.checkMesh log.mesh