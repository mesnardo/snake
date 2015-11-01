# scripts


A collection of Python and bash scripts used to process the numerical solution
of simulations run with one of the following code:
* [PetIBM]()
* [cuIBM]()
* [IBAMR]()
* [OpenFOAM]()

Some of the Python scripts calls the environment variable `$SCRIPTS`.
The variable can set by adding the following line to your `.bashrc` 
or `.bash_profile` file:

	> export SCRIPTS="/path/to/the/git/repository"


In addition, this repository contains some `resources` such as geometries used 
for the simulations or literature results for comparison.

The directory `styles` provides the matplotlib style-sheet used to plot 
the figures.


Suggestions and bug-fix are welcome.
Contact: `mesnardo@gwu.edu`
