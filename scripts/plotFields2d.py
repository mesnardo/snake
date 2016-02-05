# file: plotFields2d.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Plots the contour of vorticity at saved time-steps.


import os
import sys
import argparse

sys.path.append('{}/scripts/library'.format(os.environ['SCRIPTS']))
import miscellaneous


def parse_command_line():
  """Parses the command-line."""
  print('[info] parsing the command-line ...'),
  # create parser
  parser = argparse.ArgumentParser(description='Plots the 2D vorticity, '
                                               'pressure and velocity fields',
                        formatter_class= argparse.ArgumentDefaultsHelpFormatter)
  # fill parser with arguments
  parser.add_argument('--software', dest='software',
                      type=str, choices=['cuibm', 'petibm'],
                      help='software used for the simulation')
  parser.add_argument('--directory', dest='directory', 
                      type=str, default=os.getcwd(), 
                      help='directory of the simulation')
  parser.add_argument('--binary', dest='binary',
                      action='store_true',
                      help='use flag if data written in binary format')
  # arguments about view
  parser.add_argument('--bottom-left', '-bl', dest='bottom_left', 
                      type=float, nargs='+', default=[float('-inf'), float('-inf')],
                      help='coordinates of the bottom-left corner of the view')
  parser.add_argument('--top-right', '-tr', dest='top_right', 
                      type=float, nargs='+', default=[float('inf'), float('inf')],
                      help='coordinates of the top-right corner of the view')
  # arguments about data to plot
  parser.add_argument('--field', dest='field_name',
                      type=str, choices=['vorticity', 'x-velocity', 'y-velocity', 'pressure'],
                      help='name of the fieldto plot')
  parser.add_argument('--range', dest='range',
                      type=float, nargs='+', default=(None, None, None),
                      help='field range to plot (min, max, number of levels)')
  # arguments about the immersed-boundary
  parser.add_argument('--bodies', dest='body_paths', 
                      nargs='+', type=str, default=[],
                      help='path of each body file to add to plots')
  # arguments about time-steps
  parser.add_argument('--time-steps', '-t', dest='time_steps', 
                      type=int, nargs='+', default=[],
                      help='time-steps to plot (initial, final, increment)')
  
  parser.add_argument('--subtract-simulation', dest='subtract',
                      nargs='+', default=[],
                      help='adds another simulation to subtract the field '
                           '(software, directory, binary) '
                           'to subtract fields.')

  # arguments about figure
  parser.add_argument('--save-name', dest='save_name',
                      type=str, default=None,
                      help='prefix used to create the save directory '
                           'and used as a generic file name')
  parser.add_argument('--width', dest='width', 
                      type=float, default=8.0,
                      help='width of the figure (in inches)')
  parser.add_argument('--dpi', dest='dpi', 
                      type=int, default=100,
                      help='dots per inch (resolution of the figure)')
  # parse given options file
  parser.add_argument('--options', 
                      type=open, action=miscellaneous.ReadOptionsFromFile,
                      help='path of the file with options to parse')
  print('done')
  # parse command-line
  return parser.parse_args()


def main():
  """Plots the the velocity, pressure and vorticity fields at saved time-steps
  for a two-dimensional simulation.
  """
  args = parse_command_line()
  
  # import appropriate library
  if args.software == 'cuibm':
    sys.path.append('{}/scripts/cuIBM'.format(os.environ['SCRIPTS']))
    import ioCuIBM as io
  elif args.software == 'petibm':
    sys.path.append('{}/scripts/PetIBM'.format(os.environ['SCRIPTS']))
    import ioPetIBM as io

  time_steps = io.get_time_steps(args.directory, args.time_steps)
  coords = io.read_grid(args.directory, binary=args.binary)
  bodies = [io.Body(path) for path in args.body_paths]

  for time_step in time_steps:
    field = io.get_field(args.field_name, args.directory, time_step, coords, 
                         binary=args.binary)

    if args.subtract:
      other = dict(zip(['software', 'directory', 'binary'], args.subtract))
      other_field = get_other_field(other['software'], 
                                    args.field_name, other['directory'], 
                                    time_step, coords, 
                                    binary=(True if other['binary'] == 'True' else False))
      difference = field.subtract(other_field, label='{}Subtract'.format(args.field_name))

    io.plot_contour((field if not args.subtract else difference), 
                    args.range,
                    directory=args.directory,
                    view=args.bottom_left+args.top_right,
                    bodies=bodies,
                    save_name=(field.label if not args.save_name else args.save_name),
                    width=args.width, dpi=args.dpi)


def get_other_field(software, field_name, directory, time_step, coords, binary=False):
  """Gets the field from another simulation at a given time-step 
  that has the same mesh-grid.

  Parameters
  ----------
  software: string
    Software used to compute the numerical solution.
  field_name: string
    Name of the field to get.
  directory: string
    Directory of the simulation.
  time_step: integer
    Time-step at which the solution is read.
  coords: list of numpy 1d arrays
    List of coordinates along each direction.
  binary: bool
    Set 'True' is solution written in binary format; default: False.

  Returns
  -------
  field: io2.Field object
    The field.
  """
  # import appropriate library
  if software == 'cuibm':
    sys.path.append('{}/scripts/cuIBM'.format(os.environ['SCRIPTS']))
    import ioCuIBM as io2
  elif software == 'petibm':
    sys.path.append('{}/scripts/PetIBM'.format(os.environ['SCRIPTS']))
    import ioPetIBM as io2
  return io2.get_field(field_name, directory, time_step, coords, binary=binary)


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))