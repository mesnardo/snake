#!/bin/sh

# file: generateSnappyHexMesh_serial_colonialOne.sh
# author: Olivier Mesnard (mesnardo@gwu.edu)
# brief: Generates a mesh with snappyHexMesh on 1 processor on Colonial One.

#SBATCH --job-name="sHMSerial"
#SBATCH --output=log%j.out
#SBATCH --error=log%j.err
#SBATCH --partition=short
#SBATCH --time=02:00:00
#SBATCH -n 1

module load openfoam/gcc/2.3.0

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
