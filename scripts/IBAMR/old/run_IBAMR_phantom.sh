#!/bin/sh


export PETSC_DIR=$HOME/src/petsc/3.5.2
export PETSC_ARCH=linux-opt

MPIRUN=$PETSC_DIR/$PETSC_ARCH/bin/mpirun
IBAMR_BUILD=$HOME/src/ibamr/ibamr-objs-opt
PROGRAM=$IBAMR_BUILD/examples/ConstraintIB/externalFlowBluffBody2dStabilized/externalFlowBluffBody2dStabilized
N=2

INPUT=input2d
BODY=cylinder2d


time $MPIRUN -n $N $PROGRAM $INPUT --body $BODY
