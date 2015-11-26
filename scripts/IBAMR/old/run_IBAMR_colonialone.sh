#!/bin/sh

#SBATCH --job-name="name"
#SBATCH --output=log_name.out
#SBATCH --error=log_name.err
#SBATCH --partition=short
#SBATCH --time=00:30:00
#SBATCH -n 16


MPIRUN=/c1/apps/openmpi/1.8/gcc/4.7/cpu/bin/mpirun
IBAMR_BUILD=/groups/barbalab/src/ibamr/ibamr-objs-openmpi-1.8-gcc-4.7-opt
PROGRAM=$IBAMR_BUILD/examples/ConstraintIB/externalFlowBluffBody2dStabilized/externalFlowBluffBody2dStabilized

INPUT=input2d
BODY=flyingSnake2dAoA35ds004

time $MPIRUN $PROGRAM $INPUT --body $BODY
