#!/bin/sh

# file: generateSnappyHexMesh_parallel_colonialOne.sh
# author: Olivier Mesnard (mesnardo@gwu.edu)
# brief: Generates a mesh with SnappyHexMesh using N processors on Colonial One.

#SBATCH --job-name="sHMParallel"
#SBATCH --output=log%j.out
#SBATCH --error=log%j.err
#SBATCH --partition=short
#SBATCH --time=02:00:00
#SBATCH -n 4

N=4

module load openfoam/gcc/2.3.0

# source tool run functions
. $WM_PROJECT_DIR/bin/tools/RunFunctions

# clean previous mesh
find constant/polyMesh -type f \! -name 'blockMeshDict' -delete
rm -rf log.mesh
rm -rf processor*
mkdir log.mesh

# create dummy initial conditions folder
mv 0 0.org
mkdir 0

# create base mesh
runApplication blockMesh
mv log.blockMesh log.mesh

# decompose base mesh
cp system/decomposeParDict.hierarchical system/decomposeParDict
runApplication decomposePar
mv log.decomposePar log.mesh

# change tolerance criterion for face area on neighboring processors
# do not work for now
sed 's/0.0001/0.0001/g' processor*/constant/polyMesh/boundary -i

# create castellated mesh (using N processors)
cp system/decomposeParDict.ptscotch system/decomposeParDict
N=4 
# runParallel snappyHexMesh $N -overwrite -parallel
MPIRUN="/opt/OpenFOAM/ThirdParty-2.2.2/platforms/linux64Gcc/openmpi-1.6.3/bin/mpirun"
$MPIRUN -np $N snappyHexMesh -overwrite -parallel > log.snappyHexMesh
mv log.snappyHexMesh log.mesh

# reconstruct mesh
runApplication reconstructParMesh -mergeTol 1.0E-06 -latestTime
mv log.reconstructParMesh log.mesh

# extrude mesh in third direction
runApplication extrudeMesh
mv log.extrudeMesh log.mesh

# create patches
runApplication createPatch -overwrite
mv log.createPatch log.mesh

# check mesh quality
runApplication checkMesh
mv log.checkMesh log.mesh

# restore initial conditions folder
rm -rf 0
mv 0.org 0

# use simple method for decomposeParDict for the solver
cp system/decomposeParDict.simple system/decomposeParDict