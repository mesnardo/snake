# file: miscellaneous.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# brief: Contains diverse functions and classes.


import argparse


class ReadOptionsFromFile(argparse.Action):
    """Container to read parameters from file."""
    def __call__(self, parser, namespace, values, option_string=None):
      """Fills the namespace with parameters read in file."""
      with values as infile:
        lines = [element for line in infile.readlines()
                 for element in line.strip().split()
                 if not line.startswith('#')]
        parser.parse_args(lines, namespace)