# file: writePhysicalSurfaces.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# brief: Writes physical surfaces into .geo file.


import argparse

import numpy


def parse_command_line():
  """Parses the command-line."""
  print('[info] parsing the command-line ...'),
  # create parser
  parser = argparse.ArgumentParser(description='Write physical surfaces '
                                               'into .geo file',
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  # fill parser with arguments
  parser.add_argument('--geo', dest='geo_path', 
                      type=str,
                      help='path of the .geo file')
  parser.add_argument('--back', dest='back', 
                      type=int,
                      help='identification number of the back surface')
  parser.add_argument('--front', dest='front', 
                      type=int,
                      help='identification number of the front surface')
  parser.add_argument('--inlet', dest='inlet', 
                      type=int,
                      help='identification number of the inlet surface')
  parser.add_argument('--outlet', dest='outlet', 
                      type=int,
                      help='identification number of the outlet surface')
  parser.add_argument('--bottom', dest='bottom', 
                      type=int,
                      help='identification number of the bottom surface')
  parser.add_argument('--top', dest='top', 
                      type=int,
                      help='identification number of the top surface')
  parser.add_argument('--body-name', dest='body_name', 
                      type=str, default='body',
                      help='name of the OpenFOAM patch for the body')
  parser.add_argument('--body', dest='body', 
                      type=int, nargs='+',
                      help='starting and ending identification numbers '
                           'followed by the increment')
  print('done')
  return parser.parse_args()


def main():
  """Writes physical surfaces into the .geo file."""
  parameters = parse_command_line()
  # write physical surfaces into .geo file
  with open(parameters.geo_path, 'a') as outfile:
    outfile.write('\n// physical surfaces\n')
    outfile.write('Physical Surface("back") = {{}};\n'.format(parameters.back))
    outfile.write('Physical Surface("front") = {{}};\n'.format(parameters.front))
    outfile.write('Physical Surface("inlet") = {{}};\n'.format(parameters.inlet))
    outfile.write('Physical Surface("outlet") = {{}};\n'.format(parameters.outlet))
    outfile.write('Physical Surface("bottom") = {{}};\n'.format(parameters.bottom))
    outfile.write('Physical Surface("top") = {{}};\n'.format(parameters.top))
    body_indices = ', '.join([str(i) for i in numpy.arange(parameters.body[0], 
                                                           parameters.body[1]+1,
                                                           parameters.body[2])])
    outfile.write('Physical Surface("{}") = {{}};\n'.format(parameters.body_name,
                                                            body_indices)) 
            

if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))