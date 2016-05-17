# Snake

A collection of Python modules used to post-process the numerical solution
of simulations run with one of the following codes:
* [PetIBM](https://github.com/barbagroup/PetIBM)
* [cuIBM](https://github.com/barbaGroup/cuIBM)
* [IBAMR](https://github.com/IBAMR/IBAMR)
* [OpenFOAM](www.openfoam.com)

Installation:

    > python setup.py install


Some of the Python modules call the environment variable `$SNAKE` defined as the local directory of this repository.
The variable can be set by adding the following line to your `.bashrc` 
or `.bash_profile` file:

	> export SNAKE="/path/to/the/git/repository"


In addition, this repository contains some `resources` such as geometries used 
for the simulations or literature results for comparison.

Suggestions and bug-fix are welcome.
Contact: `mesnardo@gwu.edu`
