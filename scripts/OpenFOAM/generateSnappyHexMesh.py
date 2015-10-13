#!/usr/bin/python

# file: generateSnappyHexMesh.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# brief: Generates a SnappyHexMesh grid compatible with OpenFOAM.


import os
import subprocess
import argparse


def parse_command_line():
  """Parses the command-line."""
  print('[argparse] parsing command-line... '),
  # create the parser
  parser = argparse.ArgumentParser(description='Generates a SnappyHexMesh grid',
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  # fill the parser with arguments
  parser.add_argument('--directory', dest='directory', 
                      type=str, default=os.getcwd(),
                      help='directory of the OpenFOAM simulation')
  parser.add_argument('--log', dest='log_file', 
                      type=str, default='mesh.log',
                      help='name of the logging file')
  print('done')
  return parser.parse_args()


def main():
  """Generates a SnappyHexMesh grid compatible with OpenFOAM."""
  parameters = parse_command_line()
  print('[info] simulation directory: {}'.format(parameters.directory))
  os.chdir(parameters.directory)
  log_file = open(parameters.log_file, 'w')
  # remove previous mesh and keep the dictionary for blockMesh
  print('[info] cleaning directory constant/polyMesh... ')
  os.system('find constant/polyMesh -type f \! -name "blockMeshDict" -delete')
  # create the base mesh
  print('[blockMesh] creating the base mesh... ')
  subprocess.call('blockMesh', shell=True, stdout=log_file)
  # create eged mesh for boxes
  print('[surfaceFeatureExtract] creating edge mesh of boxes... ')
  subprocess.call('surfaceFeatureExtract', shell=True, stdout=log_file)
  # create castelated mesh
  print('[snappyHexMesh] generating castelated mesh... ')
  subprocess.call('snappyHexMesh -parallel -overwrite', shell=True, stdout=log_file)
  # extrude mesh in spanwise direction
  print('[extrudeMesh] extruding mesh in spanwise direction... ')
  subprocess.call('extrudeMesh', shell=True, stdout=log_file)
  # create patches
  print('[createPatch] creating patches... ')
  subprocess.call('createPatch -overwrite', shell=True, stdout=log_file)
  # check mesh quality
  print('[checkMesh] checking mesh quality... ')
  subprocess.call('checkMesh', shell=True, stdout=log_file)


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))