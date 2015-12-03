#!/bin/sh

# file: configurePetIBMOsborne.sh
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Configures PetIBM on Osborne.


PETSC_DIR="/Users/mesnardo/src/petsc/3.5.2"
PETSC_ARCH="arch-darwin-c-opt"

PETIBM_DIR="/Users/mesnardo/git/barbagroup/PetIBM"

$PETIBM_DIR/configure --prefix=$PWD \
  CC=$PETSC_DIR/$PETSC_ARCH/bin/mpicc \
  CXX=$PETSC_DIR/$PETSC_ARCH/bin/mpicxx \
  CXXFLAGS="-g -O3 -stdlib=libc++ -std=c++11"
