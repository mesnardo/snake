# file: generateGridParameters.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Generates the cartesianMesh.yaml file for stretched grids.


import argparse
import sys
import os

sys.path.append(os.environ['SCRIPTS'])
from library import miscellaneous
from library.cartesianMesh import StructuredCartesianMesh

def parse_command_line():
  """Parses the command-line with module argparse."""
  print('[info] parsing the command-line ...'),
  # create parser
  parser = argparse.ArgumentParser(description='Generates cartesianMesh.yaml '
                                               'file for a uniform region '
                                               'surrounded by a stretched grid',
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  # fill parser with arguments
  parser.add_argument('--input', dest='input',
                      type=str,
                      default='cartesianMesh.yaml',
                      help='path of the Yaml file to read')
  parser.add_argument('--output', dest='output',
                      type=str,
                      default=None,
                      help='path of the file to write in Yaml format')

  # parse given options file
  parser.add_argument('--options', 
                      type=open, action=miscellaneous.ReadOptionsFromFile,
                      help='path of the file with options to parse')
  # parse command-line
  print('done')
  return parser.parse_args()


def main():
  """Creates cartesianMesh.yaml file for stretched grid."""
  args = parse_command_line()
  mesh = StructuredCartesianMesh()
  data = mesh.read_yaml_file(file_path=args.input)
  mesh.generate(data)
  if args.output:
    mesh.write_yaml_file(file_path=args.output)
  mesh.write('gridOlivier.txt')

if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))