# file cleanSimulation.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# brief: Cleans a PetIBM simulation.


import os
import argparse


def parse_command_line():
  """Parses the command-line."""
  # create parser
  parser = argparse.ArgumentParser(description='Clean PetIBM case',
                        formatter_class= argparse.ArgumentDefaultsHelpFormatter)
  # fill parser with arguments
  parser.add_argument('--directories', dest='directories', 
                      type=str, nargs='+', 
                      default=[os.getcwd()],
                      help='directory of PetIBM simulation(s) to clean')
  parser.add_argument('--no-images', dest='images', 
                      action='store_false',
                      help='does not remove the images folder')
  parser.add_argument('--no-data', dest='data', 
                      action='store_false',
                      help='does not remove the data folder')
  parser.add_argument('--no-grid', dest='grid', 
                      action='store_false',
                      help='does not remove the grid file')
  parser.add_argument('--no-solution', dest='solution', 
                      action='store_false',
                      help='does not remove the numerical solution folders')
  parser.add_argument('--no-forces', dest='forces', 
                      action='store_false',
                      help='does not remove the forces data file')
  parser.add_argument('--no-vtk', dest='vtk_files', 
                      action='store_false',
                      help='does not remove .vtk_files folder')
  parser.add_argument('--no-logs', dest='logs', 
                      action='store_false',
                      help='does not remove log files')
  parser.add_argument('--no-tensors', dest='tensors', 
                      action='store_false',
                      help='does not remove folder containing tensors')
  parser.set_defaults(images=True, data=True, grid=True, solutions=True, 
                      forces=True, vtk_files=True, logs=True, tensors=True)
  return parser.parse_args()


def main():
  """Cleans PetIBM simulation(s)."""
  args = parse_command_line()

  for directory in args.directories:
    # get different paths to delete
    paths = {}
    if args.images:
      paths['images'] = '{}/images'.format(directory)
    if args.data:
      paths['data'] = '{}/data'.format(directory)
    if args.grid:
      paths['grid'] = '{}/grid.txt'.format(directory)
    if args.solution:
      paths['solution'] = '{}/0*'.format(directory)
    if args.forces:
      paths['forces'] = '{}/forces.txt'.format(directory)
    if args.vtk_files:
      paths['vtk_files'] = '{}/vtk_files'.format(directory)
    if args.logs:
      paths['logs'] = ('{0}/iterationCounts.txt '
                       '{0}/performanceSummary.txt '
                       '{0}/summary.log'.format(directory))
    if args.tensors:
      paths['tensors'] = ('{}/tensors'.format(directory))
    # delete appropriate files/folders
    print('[info] cleaning directory {}'.format(directory))
    for key, path in paths.iteritems():
      print('\t-> removing {} ...'.format(key))
      os.system('rm -rf {}'.format(path))


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))