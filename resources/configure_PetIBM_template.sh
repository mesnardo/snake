#!/bin/sh

export PETSC_DIR="/home/mesnardo/src/petsc/3.5.2"
export PETSC_ARCH="linux-opt"

export PETIBM_DIR="/home/mesnardo/git/barbagroup/PetIBM"

$PETIBM_DIR/configure --prefix=$PWD \
	CC=$PETSC_DIR/$PETSC_ARCH/bin/mpicc \
	CXX=$PETSC_DIR/$PETSC_ARCH/bin/mpicxx \
	CXXFLAGS="-g -O3 -std=c++0x"
