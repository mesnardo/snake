#!/bin/sh python

# file: generate2dCylinder.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# brief: Generates a file containing the 2d coordinates of a cylinder.


import os
import math

import argparse
import numpy


def read_inputs():
  """Parses the command-line."""
  # create parser
  parser = argparse.ArgumentParser(description='Generates cylinder2d.vertex.',
						formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  # fill parser with arguments
  parser.add_argument('--case', dest='case_directory', type=str, 
                      default=os.getcwd(),
					  help='directory of the simulation')
  parser.add_argument('-n', dest='n', type=int,
                      help='number of segments on the cylinder')
  parser.add_argument('-ds', dest='ds', type=float,
                      help='target-length between two consecutive points')
  # parse command-line
  return parser.parse_args()


def main():
  """Generates and writes the coordinates of a 2d circular cylinder."""
  
  parameters = read_inputs()
  
  R = 0.5
  xc, yc = 0.0, 0.0
  
  if not (parameters.n or parameters.ds):
	  print('ERROR: missing the number of segments or the target segment-length.')
	  exit(0)
  elif parameters.n:
  	N = parameters.n
	ds = 2.0*math.pi*R/N
  elif parameters.ds:
  	ds = parameters.ds
	N = int(math.ceil(2.0*math.pi*R/ds))

  theta = numpy.linspace(0.0, 2.0*math.pi, N+1)[:-1]
  x, y = xc+R*numpy.cos(theta), yc+R*numpy.sin(theta)

  print('Radius: {}'.format(R))
  print('Number of segments: {}'.format(N))
  print('Segment-length: {}'.format(2.0*math.pi*R/N))

  file_path = '{}/cylinder2d.vertex'.format(parameters.case_directory)
  with open(file_path, 'w') as outfile:
    outfile.write('{}\n'.format(N))
    numpy.savetxt(outfile, numpy.c_[x, y], fmt='%.6f', delimiter='\t')


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))
