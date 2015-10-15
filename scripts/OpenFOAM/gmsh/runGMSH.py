#!/usr/bin/python

# file: runGMSH.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# brief: Runs GMSH to generate 2D extruded mesh.


import argparse
import os


def parse_command_line():
  """Parses the command-line."""
  # create parser
  parser = argparse.ArgumentParser(description='Runs GMSH to generate '
                                               'a 2D extruded mesh',
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  # fill parser with arguments
  parser.add_argument('--geo', dest='geo_path', type=str,
                      help='path of the .geo file')
  return parser.parse_args()


def main():
  """Runs GMSH to generate a 2D extruded mesh."""
  parameters = parse_command_line()
  # run GMSH in batch mode (-3: 3D generation, -format msh: output format)
  os.system('gmsh {} -3 -format msh'.format(parameters.geo_path))


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))