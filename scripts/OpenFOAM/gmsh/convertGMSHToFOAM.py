# file: convertGMSHToFOAM.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# brief: Changes the boundary patches in folder constant/polyMesh.


import os
import argparse


def parse_command_line():
  """Parses the command-line."""
  # create the parser
  print('[info] parsing the command-line ...'),
  parser = argparse.ArgumentParser(description='Change the boundary patches '
                                   'in the file constant/polyMesh/boundary '
                                   'of the OpenFOAM case',
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  # fill the parser with arguments
  parser.add_argument('--directory', dest='directory', 
                      type=str, 
                      default=os.getcwd(),
                      help='directory of the OpenFOAM simulation')
  parser.add_argument('--mesh', dest='mesh_path', 
                      type=str, 
                      default='{}/*.msh'.format(os.getcwd()),
                      help='path of the GMSH .msh file')
  parser.add_argument('--body-name', dest='body_name',
                      type=str, 
                      default='body',
                      help='name of the body patch used in OpenFOAM')
  print('done')
  return parser.parse_args()


def main():
  """Changes the boundary patches in the file constant/polyMesh/boundary
  of the OpenFOAM case.
  """
  parameters = parse_command_line()

  log_path = '{}/mesh.log'.format(parameters.directory)
  # run OpenFOAM utility gmshToFoam
  os.system('gmshToFoam -case {} {} > {}'.format(parameters.directory, 
                                                 parameters.mesh_path, 
                                                 log_path))
  # read the current boundary file
  boundary_path = '{}/constant/polyMesh/boundary'.format(parameters.directory)
  with open(boundary_path, 'r') as infile:
    lines = infile.readlines()
  # change boundary patches
  for i, line in enumerate(lines):
    if 'front' in line or 'back' in line:
      lines[i+2] = lines[i+2].replace('patch', 'empty')
    elif 'top' in line or 'bottom' in line:
      lines[i+2] = lines[i+2].replace('patch', 'symmetryPlane')
    elif 'inlet' in line:
      lines[i+3] = lines[i+3].replace('patch', 'inlet')
    elif 'outlet' in line:
      lines[i+3] = lines[i+3].replace('patch', 'outlet')
    elif args.body_name in line:
      lines[i+2] = lines[i+2].replace('patch', 'wall')
      lines[i+3] = lines[i+3].replace('patch', 'wall')
  # write the new boundary file
  with open(boundary_path, 'w') as outfile:
    outfile.write(''.join(lines))
  # check the quality of the mesh
  os.system('checkMesh -case {} >> {}'.format(parameters.directory, log_path))


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))