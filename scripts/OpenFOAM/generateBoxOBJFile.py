#!/usr/bin/env python

# file: generateBoxOBJFile.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# brief: Generate a triangulated 2D box and export as .OBJ file.


import argparse
import os
import sys

sys.path.append('/home/mesnardo/simulations_OpenFOAM/scripts/library')
import OBJFile


def parse_command_line():
  """Parses the command-line."""
  print('[info] parsing command-line... '),
  # create the parser
  parser = argparse.ArgumentParser(description='Generates a 2D triangulated '
                                               'box and writes into a Wavefront OBJ file',
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  # fill the parser with arguments
  parser.add_argument('--bottom-left', '-bl', dest='bottom_left', 
                      type=float, nargs='+', default=[-2.0, -2.0],
                      help='coordinates of the bottom-left corner of the box')
  parser.add_argument('--top-right', '-tr', dest='top_right', 
                      type=float, nargs='+', default=[2.0, 2.0],
                      help='coordinates of the top-right corner of the box')
  parser.add_argument('-z', dest='z', 
                      type=float, default=0.0,
                      help='z-coordinate of the 2d box')
  parser.add_argument('-n', dest='n', 
                      type=int, nargs='+', default=[100, 100],
                      help='number of points in the x- and y- directions')
  parser.add_argument('--name', dest='name', 
                      type=str, default='box',
                      help='name of the OBJ file (without the extension)')
  parser.add_argument('--save-dir', dest='save_directory', 
                      type=str, default=os.getcwd(),
                      help='directory where to save the .obj file')
  print('done')
  return parser.parse_args()


def main():
  """Generates a 2D triangulated box and writes in Wavefront OBJ file."""
  parameters = parse_command_line()
  box = OBJFile.Box2d(parameters.name, 
                      bottom_left=parameters.bottom_left, top_right=parameters.top_right,
                      n=parameters.n, z=parameters.z)
  box.write(parameters.save_directory)
  

if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))