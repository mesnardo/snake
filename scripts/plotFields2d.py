# file: plotFields2d.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Plots the contour of vorticity at saved time-steps.


import os
import sys
import argparse

sys.path.append(os.environ['SCRIPTS'])
from library import miscellaneous
from library.simulation import Simulation
from library.body import Body


def parse_command_line():
  """Parses the command-line."""
  print('[info] parsing the command-line ...'),
  # create parser
  parser = argparse.ArgumentParser(description='Plots the 2D vorticity, '
                                               'pressure and velocity fields',
                        formatter_class= argparse.ArgumentDefaultsHelpFormatter)
  # fill parser with arguments
  parser.add_argument('--software', dest='software',
                      type=str, 
                      choices=['cuibm', 'petibm'],
                      help='software used for the simulation')
  parser.add_argument('--directory', dest='directory', 
                      type=str, 
                      default=os.getcwd(), 
                      help='directory of the simulation')
  # arguments about view
  parser.add_argument('--bottom-left', '-bl', dest='bottom_left', 
                      type=float, nargs=2, 
                      default=[float('-inf'), float('-inf')],
                      metavar=('x', 'y'),
                      help='coordinates of the bottom-left corner of the view')
  parser.add_argument('--top-right', '-tr', dest='top_right', 
                      type=float, nargs=2, 
                      default=[float('inf'), float('inf')],
                      metavar=('x', 'y'),
                      help='coordinates of the top-right corner of the view')
  # arguments about data to plot
  parser.add_argument('--field', dest='field_name',
                      type=str, 
                      choices=['vorticity', 'x-velocity', 'y-velocity', 'pressure'],
                      help='name of the field to plot')
  parser.add_argument('--no-filled-contour', dest='filled_contour',
                      action='store_false',
                      help='use flag to create a filled contour, '
                           'otherwise a simple contour is used')
  parser.add_argument('--range', dest='range',
                      type=float, nargs=3, 
                      default=None,
                      metavar=('min', 'max', 'n-levels'),
                      help='field range to plot')
  parser.add_argument('--periodic', dest='periodic_directions',
                      type=str, nargs='+', 
                      default=[],
                      help='for PetIBM solutions: list of directions with '
                           'periodic boundary conditions')
  # arguments about the immersed-boundary
  parser.add_argument('--bodies', dest='body_paths', 
                      type=str, nargs='+', 
                      default=[],
                      help='path of each body file to add to plots')
  # arguments about time-steps
  parser.add_argument('--time-steps', '-t', dest='time_steps_range', 
                      type=int, nargs=3, 
                      default=None,
                      metavar=('initial', 'final', 'increment'),
                      help='time-steps to plot')
  
  parser.add_argument('--subtract-simulation', dest='subtract_simulation',
                      type=str, nargs=2, 
                      default=None,
                      metavar=('software', 'directory'),
                      help='adds another simulation to subtract the field')

  # arguments about figure
  parser.add_argument('--save-name', dest='save_name',
                      type=str, 
                      default=None,
                      help='prefix used to create the save directory '
                           'and used as a generic file name')
  parser.add_argument('--width', dest='width', 
                      type=float, 
                      default=8.0,
                      help='width of the figure (in inches)')
  parser.add_argument('--dpi', dest='dpi', 
                      type=int, 
                      default=100,
                      help='dots per inch (resolution of the figure)')
  # parse given options file
  parser.add_argument('--options', 
                      type=open, action=miscellaneous.ReadOptionsFromFile,
                      help='path of the file with options to parse')
  parser.set_defaults(filled_contour=True)
  print('done')
  # parse command-line
  return parser.parse_args()


def main(args):
  """Plots the the velocity, pressure, or vorticity fields at saved time-steps
  for a two-dimensional simulation.
  """
  simulation = Simulation(directory=args.directory, software=args.software)
  time_steps = simulation.get_time_steps(time_steps_range=args.time_steps_range)
  simulation.read_grid()
  bodies = [Body(path) for path in args.body_paths]

  if args.subtract_simulation:
    info = dict(zip(['software', 'directory'], 
                    args.subtract_simulation))
    other = Simulation(**info)
    other.read_grid()

  for time_step in time_steps:
    simulation.read_fields([args.field_name], time_step, 
                           periodic_directions=args.periodic_directions)
    
    field_name = (args.field_name if not args.subtract_simulation
                                  else args.field_name+'-subtracted')
    if args.subtract_simulation:
      other.read_fields([args.field_name], time_step, 
                        periodic_directions=args.periodic_directions)
      simulation.subtract(other, args.field_name, field_name)

    simulation.plot_contour(field_name,
                            field_range=args.range,
                            filled_contour=args.filled_contour,
                            view=args.bottom_left+args.top_right,
                            bodies=bodies,
                            save_name=args.save_name,
                            width=args.width, 
                            dpi=args.dpi)


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  args = parser_command_line()
  main(args)
  print('\n[{}] END\n'.format(os.path.basename(__file__)))