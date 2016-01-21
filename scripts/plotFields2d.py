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
  parser.add_argument('--type', dest='simulation_type',
                      type=str, 
                      help='type of simulation (cuibm or petibm)')
  parser.add_argument('--directory', dest='case_directory', 
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
  parser.add_argument('--field', dest='field',
                      type=str,
                      help='field name to plot '
                           '(vorticity, u-velocity, v-velocity, pressure)')
  parser.add_argument('--range', dest='range',
                      type=float, nargs='+', default=(None, None, None),
                      help='field range to plot (min, max, number of levels)')
  # arguments about the immmersed-boundary
  parser.add_argument('--bodies', dest='body_paths', 
                      nargs='+', type=str, default=[],
                      help='path of each body file to add to plots')
  # arguments about time-steps
  parser.add_argument('--time-steps', '-t', dest='time_steps', 
                      type=int, nargs='+', default=[],
                      help='time-steps to plot (initial, final, increment)')
  # arguments about figure
  parser.add_argument('--width', dest='width', 
                      type=float, default=8.0,
                      help='width of the figure (in inches)')
  parser.add_argument('--dpi', dest='dpi', 
                      type=int, default=100,
                      help='dots per inch (resoltion of the figure)')
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
  if args.simulation_type == 'cuibm':
    sys.path.append('{}/scripts/cuIBM'.format(os.environ['SCRIPTS']))
    import ioCuIBM as io
  elif args.simulation_type == 'petibm':
    sys.path.append('{}/scripts/PetIBM'.format(os.environ['SCRIPTS']))
    import ioPetIBM as io
  else:
    print('[error] incorrect simulation-type (choose "cuibm" or "petibm")')
    exit(1)


  time_steps = io.get_time_steps(args.case_directory, args.time_steps)
  coords = io.read_grid(args.case_directory, binary=args.binary)
  bodies = [io.Body(path) for path in args.body_paths]

  for time_step in time_steps:
    if args.field == 'vorticity':
      field = io.compute_vorticity(args.case_directory, time_step, coords, 
                                   binary=args.binary)
    elif args.field in ['u-velocity', 'x-velocity']:
      field, _ = io.read_velocity(args.case_directory, time_step, coords, 
                                  binary=args.binary)
    elif args.field in ['v-velocity', 'y-velocity']:
      _, field = io.read_velocity(args.case_directory, time_step, coords, 
                                  binary=args.binary)
    elif args.field == 'pressure':
      field = io.read_pressure(args.case_directory, time_step, coords, 
                               binary=args.binary)

    io.plot_contour(field, args.range,
                    directory=args.case_directory,
                    view=args.bottom_left+args.top_right,
                    bodies=bodies,
                    width=args.width, dpi=args.dpi)


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))