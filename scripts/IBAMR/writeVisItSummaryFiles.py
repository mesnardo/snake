#!/bin/python

# \file writeIBAMRVisItSummaryFiles.py
# \author Olivier Mesnard (mesnardo@gwu.edu)
# \brief Writes summary files for VisIt with list of sub-directories to look into.


import os
import argparse

import numpy


def parse_command_line():
  """Parses the command-line."""
  print('[info] parsing the command-line ...'),
  # create parser
  parser = argparse.ArgumentParser(description='Writes summary files for VisIt '
                                               'wit list of sub-directories '
                                               'to look into',
                                   formatter_class = argparse.ArgumentDefaultsHelpFormatter)
  # fill parser with arguments
  parser.add_argument('--directory', dest='directory', 
                      type=str, 
                      default=os.getcwd(),
                      help='directory where to save Visit summary files')
  parser.add_argument('--time-steps', '-n', dest='time_steps', 
                      type=int, nargs=3,
                      metavar=('start', 'end', 'increment'),
                      help='range of time-steps to consider')
  print('done')
  return parser.parse_args()


def main():
  """Writes summary files for Visit 
  with list of sub-directories to look into.
  """
  # parse command-line
  parameters = parse_command_line()

  # list of SAMRAI files to VisIt
  dumps_visit = numpy.array(['visit_dump.{0:05}/summary.samrai'.format(n)
                             for n in xrange(parameters.time_steps[0],
                                             parameters.time_steps[1]+1,
                                             parameters.time_steps[2])])
  # list of SILO file to VisIt
  lag_data_visit = numpy.array(['lag_data.cycle_{0:06d}/lag_data.cycle_{0:06d}.summary.silo'.format(n)
                                for n in xrange(parameters.time_steps[0],
                                                parameters.time_steps[1]+1,
                                                parameters.time_steps[2])])
  # write files
  print('directory: {}\n'.format(parameters.directory))
  with open('{}/dumps.visit'.format(parameters.directory), 'w') as outfile:
    print('writing dumps.visit file...')
    numpy.savetxt(outfile, dumps_visit, fmt='%s')
  with open('{}/lag_data.visit'.format(parameters.directory), 'w') as outfile:
    print('writing lag_data.visit file...')
    numpy.savetxt(outfile, lag_data_visit, fmt='%s')

  return


if __name__ == '__main__':
  print('\nSTART\n')
  main()
  print('\nDONE\n')