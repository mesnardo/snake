#!/bin/sh

# file: runCuIBMColonialOne.sh
# author: Olivier Mesnard (mesnardo@gwu.edu)
# brief: Runs cuIBM on Colonial One.


#SBATCH --job-name="cuI1k25"
#SBATCH --output=log%j.out
#SBATCH --error=log%j.err
#SBATCH --partition=gpu
#SBATCH --time=48:00:00
#SBATCH -n 1


CUIBM_DIR="/home/mesnardo/git/barbagroup/cuIBM"
CUIBM="$CUIBM_DIR/bin/cuIBM"

LOG_FILE="log.summary"

time $CUIBM -caseFolder $PWD >> $LOG_FILE