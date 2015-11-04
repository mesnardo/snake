#!/usr/bin/env python

# file: plotVorticity.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Plots the contour of vorticity at saved time-steps.


import os
import sys
import argparse

sys.path.append('{}/scripts/cuIBM'.format(os.environ['SCRIPTS']))
import ioCuIBM


def parse_command_line():
  """Parses the command-line."""
  print('[info] parsing the command-line ... '),
  # create parser
  parser = argparse.ArgumentParser(description='Plots the 2D vorticity, '
                                               'pressure and velocity fields',
                        formatter_class= argparse.ArgumentDefaultsHelpFormatter)
  # fill parser with arguments
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
  parser.add_argument('--velocity', dest='velocity', 
                      action='store_true',
                      help='plots the velocity fields')
  parser.add_argument('--pressure', dest='pressure', 
                      action='store_true',
                      help='plots the pressure field')
  parser.add_argument('--vorticity', dest='vorticity', 
                      action='store_true',
                      help='plots the vorticity field')
  parser.add_argument('--vorticity-range', '-wr', dest='vorticity_range', 
                      type=float, nargs='+', default=[-1.0, 1.0, 11],
                      help='vorticity range (min, max, number of levels)')
  parser.add_argument('--u-range', '-ur', dest='u_range', 
                      type=float, nargs='+', default=[-1.0, 1.0, 11],
                      help='u-velocity range (min, max, number of levels)')
  parser.add_argument('--v-range', '-vr', dest='v_range', 
                      type=float, nargs='+', default=[-1.0, 1.0, 11],
                      help='v-velocity range (min, max, number of levels)')
  parser.add_argument('--pressure-range', '-pr', dest='pressure_range', 
                      type=float, nargs='+', default=[-1.0, 1.0, 11],
                      help='pressure range (min, max, number of levels)')
  # arguments about time-steps
  parser.add_argument('--time-steps', '-t', dest='time_steps', 
                      type=int, nargs='+', default=[],
                      help='time-steps to plot (initial, final, increment)')
  # arguments about figure
  parser.add_argument('--size', dest='size', 
                      type=float, nargs='+', default=[8.0, 8.0],
                      help='size (width and height) of the figure to save (in inches)')
  parser.add_argument('--dpi', dest='dpi', 
                      type=int, default=100,
                      help='dots per inch (resoltion of the figure)')
  # parse given options file
  class LoadFromFile(argparse.Action):
    """Container to read parameters from file."""
    def __call__(self, parser, namespace, values, option_string=None):
      """Fills the namespace with parameters read in file."""
      with values as f:
        parser.parse_args(f.read().split(), namespace)
  parser.add_argument('--file', 
                      type=open, action=LoadFromFile,
                      help='path of the file with options to parse')
  print('done')
  # parse command-line
  return parser.parse_args()








def main():
  """Plots the the velocity, pressure and vorticity fields at saved time-steps
  for a two-dimensional simulation.
  """
  args = parse_command_line()
  print('[info] case directory: {}'.format(args.case_directory))

  time_steps = ioCuIBM.get_time_steps(args.case_directory, args.time_steps)
 
  # create directory where images will be saved
  images_directory = '{}/images'.format(args.case_directory)
  print('[info] images directory: {}'.format(images_directory))
  if not os.path.isdir(images_directory):
    os.makedirs(images_directory)

  coords = ioCuIBM.read_grid(args.case_directory, binary=args.binary)

  for time_step in time_steps:
    if args.velocity or args.vorticity:
      u, v = ioCuIBM.read_velocity(args.case_directory, time_step, coords, 
                                   binary=args.binary)
      if args.velocity:
        # plot u-velocity field
        image_path = '{}/uVelocity{:0>7}.png'.format(images_directory, time_step)
        ioCuIBM.plot_contour(u, args.u_range, image_path, 
                             view=args.bottom_left+args.top_right,
                             size=args.size, dpi=args.dpi)
        # plot v-velocity field
        image_path = '{}/vVelocity{:0>7}.png'.format(images_directory, time_step)
        ioCuIBM.plot_contour(v, args.v_range, image_path, 
                             view=args.bottom_left+args.top_right,
                             size=args.size, dpi=args.dpi)
      if args.vorticity:
        w = ioCuIBM.compute_vorticity(u, v)
        # plot vorticity field
        image_path = '{}/vorticity{:0>7}.png'.format(images_directory, time_step)
        ioCuIBM.plot_contour(w, args.vorticity_range, image_path, 
                             view=args.bottom_left+args.top_right,
                             size=args.size, dpi=args.dpi)
    if args.pressure:
      p = ioCuIBM.read_pressure(args.case_directory, time_step, coords, 
                                binary=args.binary)
      # plot pressure field
      image_path = '{}/pressure{:0>7}.png'.format(images_directory, time_step)
      ioCuIBM.plot_contour(p, args.pressure_range, image_path, 
                           view=args.bottom_left+args.top_right,
                           size=args.size, dpi=args.dpi)


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))