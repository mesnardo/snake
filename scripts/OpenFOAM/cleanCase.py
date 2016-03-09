#!/usr/bin/python

# file: cleanCase.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# brief: Clean an OpenFOAM simulation directory.


import argparse
import os


def parse_command_line():
  """Parses the command-line."""
  print('[info] parsing the command-line ...'),
  # create the parser
  parser = argparse.ArgumentParser(description='Cleans an OpenFOAM '
                         'simulation folder',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  # fill the parser with arguments
  parser.add_argument('--directory', dest='directory', 
                      type=str, 
                      default=os.getcwd(),
                      help='directory of the OpenFOAM case')
  parser.add_argument('--no-images', dest='images', 
                      action='store_false',
                      help='does not remove the images folder')
  parser.add_argument('--no-processors', dest='processors', 
                      action='store_false',
                      help='does not remove processor folders')
  parser.add_argument('--no-solutions', dest='solutions', 
                      action='store_false',
                      help='does not remove solution folders')
  parser.add_argument('--no-logs', dest='logs', 
                      action='store_false',
                      help='does not remove log files')
  parser.add_argument('--no-post-processing', dest='post_processing', 
                      action='store_false',
                      help='does not remove the post-processing folder')
  parser.set_defaults(images=True, processors=True, solutions=True, logs=True,
                      post_processing=True)
  print('done')
  return parser.parse_args()


def main():
  """Cleans an OpenFOAM simulation case."""
  # parse the command-line
  parameters = parse_command_line()

  # store different paths into a dictionary if no flag
  parts = {}
  if parameters.images:
    parts['images'] = '{}/images'.format(parameters.directory)
  if parameters.processors:
    parts['processors'] = '{}/processor*'.format(parameters.directory)
  if parameters.solutions:
    parts['solutions'] = '{0}/[1-9]* {0}/0.*'.format(parameters.directory)
  if parameters.logs:
    parts['logs'] = '{}/*log*'.format(parameters.directory)
  if parameters.post_processing:
    parts['post-processing'] = '{}/postProcessing'.format(parameters.directory)

  # remove paths that are in the dictionary
  print('Directory: {}'.format(parameters.directory))
  for key, part in parts.iteritems():
    print('\t--> deleting {} ...'.format(key)),
    os.system('rm -rf {}'.format(part))
    print('done')


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))