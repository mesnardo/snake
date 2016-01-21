# file: generateBoxOBJFile.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# brief: Generates a triangulated 2D box and exports data as .OBJ file.


import argparse
import os
import sys

import OBJFile


def parse_command_line():
  """Parses the command-line."""
  print('[info] parsing command-line ...'),
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
                      help='number of points in the x- and y-directions')
  parser.add_argument('--name', dest='name', 
                      type=str, default='box',
                      help='name of the OBJ file (without the extension)')
  parser.add_argument('--save-directory', dest='save_directory', 
                      type=str, default=os.getcwd(),
                      help='directory where to save the .obj file')
  print('done')
  return parser.parse_args()


def main():
  """Generates a 2D triangulated box and writes in Wavefront OBJ file."""
  args = parse_command_line()
  box = OBJFile.Box2d(args.name, 
                      bottom_left=args.bottom_left, top_right=args.top_right,
                      n=args.n, z=args.z)
  box.write(args.save_directory)
  

if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))