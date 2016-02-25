# file: generateBodyOBJFile.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# brief: Convert input coordinates file into a OBJ file.


import os
import argparse
import sys

sys.path.append(os.environ['SCRIPTS'])
from library.OpenFOAM import OBJFile


def parse_command_line():
  """Parses the command-line."""
  print('[info] parsing command-line ...'),
  # create the parser
  parser = argparse.ArgumentParser(description='Generates an .OBJ file '
                                               'that will be readable by OpenFOAM '
                                               'mesh generator: SnappyHexMesh',
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  # fill the parser with arguments
  parser.add_argument('--file', dest='file_path', 
                      type=str,
                      help='path of the coordinates file to convert')
  parser.add_argument('--name', dest='name', 
                      type=str,
                      help='name of the .OBJ file generated (no extension)')
  parser.add_argument('--save-directory', dest='save_directory', 
                      type=str, default=os.getcwd(),
                      help='directory where to save the .obj file')
  print('done')
  return parser.parse_args()


def main():
  """Generates an .OBJ file from a given coordinates file."""
  args = parse_command_line()
  body = OBJFile.Body2d(args.name, args.file_path)
  body.write(save_directory=args.save_directory)


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))