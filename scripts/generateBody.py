# file: generateBody.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Generates a body file.


import os
import sys
import argparse

from snake import geometry
from snake import miscellaneous


def parse_command_line():
  """Parses the command-line."""
  print('[info] parsing the command-line ...'),
  # create parser
  parser = argparse.ArgumentParser(description='Geometry discretization',
                        formatter_class= argparse.ArgumentDefaultsHelpFormatter)
  # fill parser with arguments
  # geometry arguments
  parser.add_argument('--type', dest='body_type', 
                      type=str,
                      choices=['file', 'circle', 'line', 'rectangle', 'sphere'],
                      help='type of body')
  parser.add_argument('--file', '-f', dest='file_path', 
                      type=str,
                      help='path of the coordinates file')
  parser.add_argument('--circle', dest='circle', 
                      type=float, nargs=3,
                      default=[0.5, 0.0, 0.0],
                      metavar=('radius', 'x-center', 'y-center'),
                      help='radius and center-coordinates of the circle')
  parser.add_argument('--line', '-l', dest='line', 
                      type=float, nargs=3,
                      default=[1.0, 0.0, 0.0],
                      metavar=('length', 'x-start', 'y-start'),
                      help='length and starting-point of the line')
  parser.add_argument('--rectangle', dest='rectangle', 
                      type=float, nargs=4,
                      default=[0.0, 0.0, 1.0, 1.0],
                      metavar=('x-start', 'y-start', 'x-end', 'y-end'),
                      help='bottom-left and top-right coordinates')
  parser.add_argument('--sphere', dest='sphere', 
                      type=float, nargs=4,
                      default=[0.5, 0.0, 0.0, 0.0],
                      metavar=('radius', 'x-center', 'y-center', 'z-center'),
                      help='radius and center-coordinates of the sphere')
  # discretization arguments
  parser.add_argument('--n', '-n', dest='n', 
                      type=int, 
                      default=None,
                      help='number of divisions')
  parser.add_argument('--ds', '-ds', dest='ds', 
                      type=float, 
                      default=None,
                      help='target segment-length')
  # geometry modification arguments
  parser.add_argument('--rotation', '-r', dest='rotation', 
                      type=float, nargs=3, 
                      default=None,
                      metavar=('x', 'y', 'z'),
                      help='center of rotation')
  parser.add_argument('--roll', dest='roll', 
                      type=float, 
                      default=0.0,
                      help='roll angle')
  parser.add_argument('--yaw', dest='yaw', 
                      type=float, 
                      default=0.0,
                      help='yaw angle')
  parser.add_argument('--pitch', dest='pitch', 
                      type=float, 
                      default=0.0,
                      help='pitch angle')
  parser.add_argument('--mode', dest='mode', 
                      type=str, 
                      choices=['deg', 'rad'], default='deg',
                      help='angles in degrees or radians')
  parser.add_argument('--translation', '-t', dest='translation', 
                      type=float, nargs=3, 
                      default=[0.0, 0.0, 0.0],
                      metavar=('x-disp', 'y-disp', 'z-disp'),
                      help='displacement in each directions')
  parser.add_argument('--scale', '-s', dest='scale', 
                      type=float, 
                      default=1.0,
                      help='scaling factor for 2D geometry')
  parser.add_argument('--extrusion-limits', dest='extrusion_limits', 
                      type=float, nargs=2,
                      metavar=('start', 'end'),
                      help='limits of the cylinder in the third direction')
  parser.add_argument('--extrusion-n', dest='extrusion_n',
                      type=int,
                      default=None,
                      help='number of divisions in the extrusion direction')
  parser.add_argument('--extrusion-ds', dest='extrusion_ds',
                      type=float,
                      default=None,
                      help='resolution in the extrusion direction')
  parser.add_argument('--extrusion-force', dest='extrusion_force', 
                      action='store_true',
                      help='forces the limits of extrusion')
  parser.add_argument('--inside', dest='keep_inside',
                      action='store_true',
                      help='keep points inside boundary')
  # output arguments
  parser.add_argument('--save-name', dest='save_name', 
                      type=str, 
                      default='new_body', 
                      help='name of the new body file')
  parser.add_argument('--extension', dest='extension', 
                      type=str, 
                      default='body',
                      help='extension of the output file')
  parser.add_argument('--save-dir', dest='save_directory', 
                      type=str, 
                      default=os.getcwd(),
                      help='directory where body file will be saved')
  parser.add_argument('--no-save', dest='save', 
                      action='store_false',
                      help='does not save the geometry into a file')
  parser.add_argument('--show', dest='show', 
                      action='store_true',
                      help='displays the geometry')
  parser.set_defaults(save=True)
  # parse given options file
  parser.add_argument('--options', 
                      type=open, action=miscellaneous.ReadOptionsFromFile,
                      help='path of the file with options to parse')
  print('done')
  return parser.parse_args()


def main(args):
  """Generates a file containing the coordinates of a body."""
  # generate the geometry
  if args.body_type == 'file':
    body = geometry.Geometry(file_path=args.file_path)
  elif args.body_type == 'circle':
    body = geometry.Circle(radius=args.circle[0], 
                           center=geometry.Point(args.circle[1], args.circle[2]),
                           n=args.n, ds=args.ds)
  elif args.body_type == 'line':
    body = geometry.Line(length=args.line[0],
                         start=geometry.Point(args.line[1], args.line[2]),
                         n=args.n, ds=args.ds)
  elif args.body_type == 'rectangle':
    body = geometry.Rectangle(bottom_left=geometry.Point(args.rectangle[0],
                                                         args.rectangle[1]),
                              top_right=geometry.Point(args.rectangle[2],
                                                       args.rectangle[3]),
                              nx=args.n, ny=args.n, ds=args.ds)
  elif args.body_type == 'sphere':
    body = geometry.Sphere(radius=args.sphere[0],
                           center=geometry.Point(args.sphere[1], 
                                                 args.sphere[2],
                                                 args.sphere[3]),
                           n=args.n, ds=args.ds)
  body.scale(ratio=args.scale)
  body.rotation(center=args.rotation, 
                roll=args.roll, yaw=args.yaw, pitch=args.pitch, mode=args.mode)
  body.translation(displacement=args.translation)
  if body.dimensions == 2 and args.keep_inside:
    body.keep_inside(ds=args.ds)
  elif body.dimensions == 2 and args.body_type == 'file':
    body.discretization(n=args.n, ds=args.ds)
  if body.dimensions == 2 and args.extrusion_limits:
    if args.extrusion_ds or args.extrusion_n:
      body = body.extrusion(limits=args.extrusion_limits, 
                            n=args.extrusion_n, 
                            ds=args.extrusion_ds, 
                            force=args.extrusion_force)
  if args.save:
      output_path = '{}/{}.{}'.format(args.save_directory, 
                                      args.save_name, 
                                      args.extension)
      body.write(file_path=output_path)
  if args.show:
      body.plot()


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  args = parse_command_line()
  main(args)
  print('\n[{}] END\n'.format(os.path.basename(__file__)))