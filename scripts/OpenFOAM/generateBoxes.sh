#!/bin/sh 

SCRIPT="/home/mesnardo/simulations_OpenFOAM/scripts/generateBoxOBJFile.py"

# generates the boxes (as OBJ file) used for refinement
# box1
python $SCRIPT --name box1 --bottom-left -6.54 -8.02 --top-right 9.50 8.02 -n 200 200
# box2
python $SCRIPT --name box2 --bottom-left -3.32 -4.80 --top-right 6.28 4.80 -n 200 200
# box3
python $SCRIPT --name box3 --bottom-left -1.73 -3.21 --top-right 4.69 3.21 -n 220 220
# box4
python $SCRIPT --name box4 --bottom-left -0.92 -2.40 --top-right 3.88 2.40 -n 220 220
# box5
python $SCRIPT --name box5 --bottom-left -0.52 -2.00 --top-right 3.48 2.00 -n 200 200
