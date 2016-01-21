#!/bin/sh 

# file: generateRefinementBoxes.sh
# author: Olivier Mesnard (mesnardo@gwu.edu)
# brief: Script to generate 2d refinement boxes as OBJ files.


SCRIPTPATH="$SCRIPTS/scripts/OpenFOAM/generateBoxOBJFile.py"

python $SCRIPTPATH --name boxWake \
                   --bottom-left -2.0 -4.0 \
                   --top-right 15.0 4.0 \
                   -n 700 300 \
                   --save-directory ./constant/triSurface
python $SCRIPTPATH --name boxNear \
                   --bottom-left -1.0 -2.0 \
                   --top-right 15.0 2.0 \
                   -n 800 500 \
                   --save-directory ./constant/triSurface