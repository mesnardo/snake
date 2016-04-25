# file: generateBodyOBJFile.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# brief: Convert input coordinates file into a OBJ file.


import os
import argparse

from snake.openfoam import OBJFile
from snake import miscellaneous


def parse_command_line():
  """Parses the command-line."""
  print('[info] parsing command-line ...'),
  # create the parser
  parser = argparse.ArgumentParser(description='Generates an .OBJ file '
                                               'that will be readable by OpenFOAM '
                                               'mesh generator: SnappyHexMesh',
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  # parser = argparse.ArgumentParser(description='Generates an .OBJ file '
  #                                              'that will be readable by OpenFOAM '
  #                                              'mesh generator: SnappyHexMesh')
  # fill the parser with arguments
  parser.add_argument('--file', dest='file_path', 
                      type=str,
                      metavar=('<path>'),
                      help='path of the coordinates file to convert')
  parser.add_argument('--name', dest='name', 
                      type=str,
                      metavar=('<name>'),
                      help='name of the .OBJ file generated (no extension)')
  parser.add_argument('--extrusion-limits', dest='extrusion_limits',
                      type=float, nargs=2,
                      default=[0.0, 1.0],
                      metavar=('start', 'end'),
                      help='limits of the extrusion in the 3rd direction')
  parser.add_argument('--save-directory', dest='save_directory', 
                      type=str, 
                      default=os.getcwd(),
                      metavar=('<directory>'),
                      help='directory where to save the .obj file')
  # parse given options file
  parser.add_argument('--options', 
                      type=open, action=miscellaneous.ReadOptionsFromFile,
                      metavar=('<path>'),
                      help='path of the file with options to parse')
  print('done')
  return parser.parse_args()


def main():
  """Generates an .OBJ file from a given coordinates file."""
  args = parse_command_line()
  body = OBJFile.Body2d(args.file_path, 
                        name=args.name,
                        extrusion_limits=args.extrusion_limits)
  body.write(save_directory=args.save_directory)


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))