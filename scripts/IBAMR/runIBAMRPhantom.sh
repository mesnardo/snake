#!/bin/sh

# file: runIBAMRPhantom.sh
# author: Olivier Mesnard (mesnardo@gwu.edu)
# brief: Runs IBAMR for an external flow (using the Constraint IB method).


N=2

export PETSC_DIR="$HOME/src/petsc/3.5.2"
export PETSC_ARCH="linux-opt"
MPIRUN="$PETSC_DIR/$PETSC_ARCH/bin/mpirun"

IBAMR_BUILD="$HOME/src/ibamr/ibamr-objs-opt"
PROGRAM="$IBAMR_BUILD/examples/ConstraintIB/externalFlowBluffBody2dStabilized/externalFlowBluffBody2dStabilized"

INPUT="input2d"
STRUCTURE="flyingSnake2dAoA35ds004"

time $MPIRUN -n $N $PROGRAM $INPUT --body $STRUCTURE \
	-stokes_ksp_rtol 1.0E-10 \
	-velocity_ksp_rtol 1.0E-02 \
	-pressure_ksp_rtol 1.0E-02
