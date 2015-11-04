#!/bin/sh

# file: runCuIBM.sh
# author: Olivier Mesnard (mesnardo@gwu.edu)
# brief: Runs cuIBM.


CUIBM_DIR="/home/mesnardo/git/barbagroup/cuIBM"
CUIBM="$CUIBM_DIR/bin/cuIBM"

LOG_FILE="log.summary"

time $CUIBM -caseFolder $PWD >> $LOG_FILE