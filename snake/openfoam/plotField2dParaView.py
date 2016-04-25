# file: plotField2dParaView.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Plots the 2D solution from an OpenFOAM simulation using ParaView.
# cli: pvbatch plotField2dParaView.py <arguments>


import os
import sys
import argparse

import numpy
from paraview.simple import *

sys.path.append(os.environ['SNAKE'])
from snake import miscellaneous


def parse_command_line():
  """Parses the command-line."""
  print('[info] parsing command-line...'),
  # create the parser
  parser = argparse.ArgumentParser(description='Plots the vorticity field with ParaFOAM',
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  # fill the parser with arguments
  parser.add_argument('--directory', dest='directory', 
                      type=str, 
                      default=os.getcwd(),
                      help='directory of the OpenFOAM simulation')
  parser.add_argument('--field', dest='field_name',
                      type=str,
                      choices=['vorticity', 'pressure', 'x-velocity', 'y-velocity'],
                      help='name of the field to plot')
  parser.add_argument('--range', dest='field_range',
                      type=float, nargs=2, 
                      default=(-1.0, 1.0),
                      metavar=('min', 'max'),
                      help='range of the field to plot')
  parser.add_argument('--times', dest='times',
                      type=float, nargs=3, 
                      default=(None, None, None),
                      metavar=('min', 'max', 'increment'),
                      help='times to plot')
  parser.add_argument('--view', dest='view',
                      type=float, nargs=4,
                      default=(-2.0, -2.0, 2.0, 2.0),
                      metavar=('x-bl', 'y-bl', 'x-tr', 'y-tr'),
                      help='bottom-left coordinates followed by top-right '
                           'coordinates of the view to display')
  parser.add_argument('--width', dest='width',
                      type=int, 
                      default=800,
                      help='figure width in pixels')
  # parse given options file
  parser.add_argument('--options', 
                      type=open, action=miscellaneous.ReadOptionsFromFile,
                      help='path of the file with options to parse')
  print('done')
  return parser.parse_args()


def plot_field_contours(field_name, 
                        field_range=(-1.0, 1.0),
                        directory=os.getcwd(),
                        view=(-2.0, -2.0, 2.0, 2.0), 
                        times=(None, None, None),
                        width=800):
  openfoam_file_name = '{}.OpenFOAM'.format(os.path.basename(os.path.normpath(directory)))
  reader = PV4FoamReader(FileName=os.path.join(directory, openfoam_file_name))
  print('[info] plotting {} field ...'.format(field_name))
  variable_names = {'vorticity': 'vorticity',
                    'pressure': 'p',
                    'x-velocity': 'U',
                    'y-velocity': 'U'}
  reader.VolumeFields = [variable_names[field_name]]
  reader.MeshParts = ['front - patch']
  # set view
  render_view = create_render_view(view=view, width=width)
  # grab times available
  if not any(times):
    times = numpy.array(reader.TimestepValues)
  else:
    times = numpy.arange(times[0], times[1]+times[2]/2.0, times[2])
  # create images directory
  view_str = '{:.2f}_{:.2f}_{:.2f}_{:.2f}'.format(*view)
  images_directory = os.path.join(directory, 'images',
                                  field_name + '_' + view_str)
  if not os.path.isdir(images_directory):
    os.makedirs(images_directory)
  print('[info] .png files will be saved in: {}'.format(images_directory))
  # edit colormap
  PVLookupTable = edit_colormap(field_name, field_range)
  # add a scalar bar
  scalar_bar = add_scalar_bar(field_name, PVLookupTable)
  # update view
  render_view.Representations.append(scalar_bar)
  # show field
  data_representation = Show()
  data_representation.ColorArrayName = variable_names[field_name]
  data_representation.LookupTable = PVLookupTable
  data_representation.ColorAttributeType = 'CELL_DATA'
  # add text to view
  text = Text()
  data_representation_3 = Show()
  data_representation_3.FontSize = 12
  data_representation_3.TextScaleMode = 2
  data_representation_3.Position = [0.02, 0.9]  # 0.0, 0.0: bottom-left
  data_representation_3.Color = [0.0, 0.0, 0.0]
  # plot and save requested contours
  for time in times:
    print('[info] creating view at {} time-units ...'.format(time))
    render_view.ViewTime = time
    text.Text = 'time = {}'.format(time)
    WriteImage(os.path.join(images_directory,
                            '{}{:06.2f}.png'.format(field_name, time)))


def create_render_view(view=(-2.0, -2.0, 2.0, 2.0), width=800):
  center = [0.5*(view[0]+view[2]), 0.5*(view[1]+view[3])]
  h = 1.0 + 0.5*abs(view[3]-view[1])
  height = int(width*abs(view[3]-view[1])/abs(view[2]-view[0]))
  render_view = GetRenderView()
  render_view.ViewSize = [width, height]
  Render() # needed
  render_view.CenterAxesVisibility = 0
  render_view.OrientationAxesVisibility = 0
  render_view.CameraPosition = [center[0], center[1], h]
  render_view.CameraFocalPoint = [center[0], center[1], 0.0]
  render_view.CameraViewUp = [0.0, 1.0, 0.0]
  render_view.CenterOfRotation = [0.0, 0.0, 1.0]
  render_view.CameraViewAngle = 90.0
  render_view.Background = [0.34, 0.34, 0.34]
  Render()
  return render_view


def edit_colormap(field_name, field_range):
  mode = {'vorticity': {'variable': 'vorticity',
                        'vectormode': 'Component', 
                        'vectorcomponent': 2,
                        'colorspace': 'Diverging'}, 
          'x-velocity': {'variable': 'U',
                         'vectormode': 'Component', 
                         'vectorcomponent': 0,
                         'colorspace': 'Diverging'}, 
          'y-velocity': {'variable': 'U',
                         'vectormode': 'Component', 
                         'vectorcomponent': 1,
                         'colorspace': 'Diverging'}, 
          'pressure': {'variable': 'p',
                       'vectormode': 'Magnitude', 
                       'vectorcomponent': 0,
                       'colorspace': 'HSV'}, }
  min_range, max_range = round(field_range[0], 2), round(field_range[1], 2)
  return GetLookupTableForArray(mode[field_name]['variable'], 
                                mode[field_name]['vectorcomponent']+1, 
                                RGBPoints=[min_range, 0.0, 0.0, 1.0, 
                                           max_range, 1.0, 0.0, 0.0], 
                                VectorMode=mode[field_name]['vectormode'], 
                                VectorComponent=mode[field_name]['vectorcomponent'], 
                                NanColor=[0.0, 0.0, 0.0],
                                ColorSpace=mode[field_name]['colorspace'], 
                                ScalarRangeInitialized=1.0, 
                                LockScalarRange=1)


def add_scalar_bar(field_name, PVLookupTable):
  return CreateScalarBar(ComponentTitle='', 
                         Title=field_name,  
                         Enabled=1, 
                         LabelFontSize=12, 
                         LabelColor=[0.0, 0.0, 0.0],
                         LookupTable=PVLookupTable,
                         TitleFontSize=12, 
                         TitleColor=[0.0, 0.0, 0.0], 
                         Orientation='Horizontal',
                         Position=[0.04, 0.1],
                         Position2=[0.2, 0.1])


def main(args):
  plot_field_contours(args.field_name, 
                      field_range=args.field_range, 
                      directory=args.directory,
                      view=args.view, 
                      times=args.times,
                      width=args.width)


if __name__ == '__main__':
  args = parse_command_line()
  main(args)