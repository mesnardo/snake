# Snake

A collection of Python modules to post-process the numerical solution
of simulations run with one of the following software:
* [PetIBM](https://github.com/barbagroup/PetIBM)
* [cuIBM](https://github.com/barbaGroup/cuIBM)
* [IBAMR](https://github.com/IBAMR/IBAMR)
* [OpenFOAM](www.openfoam.com)

## Installation

    > python setup.py install

## Dependencies (last tested)

* Python-2.7 or Python-3.5
* Numpy-1.11.1
* Scipy-0.17.1
* Matplotlib-1.5.3
* PETSc-3.7.4 (only the Python scripts are needed; optional, for PetIBM post-processing)
* VisIt-2.12.1 (optional, for IBAMR post-processing)
* OpenFOAM-2.3.1 and ThirdParty-2.3.1 (optional, for OpenFOAM post-processing)

## Notes

Some of the modules call the environment variable `$SNAKE` defined as the local directory of the `snake` repository.
The variable can be set by adding the following line to your `.bashrc` 
or `.bash_profile` file:

    > export SNAKE="/path/to/snake/git/repository"

The module for PetIBM calls the environment variable `$PETSC_DIR` defined as the local directory of PETSc.
The variable can be set by adding the following line to your `.bashrc` 
or `.bash_profile` file:

    > export PETSC_DIR="/path/to/petsc"


Some examples to post-process the numerical solution from the four codes are provided in the `examples` folder.

In addition, this repository contains some `resources` such as geometries used 
for the simulations or literature results for comparison.

Suggestions and bug-fix are welcome.
Contact: `mesnardo@gwu.edu`
