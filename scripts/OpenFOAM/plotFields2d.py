# file: plotFields2d.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# brief: Macro to run ParaView and plot variable in batch mode.


import argparse
import os
import sys

import numpy
from paraview.simple import *

sys.path.append(os.environ['SCRIPTS'])
from library import miscellaneous


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
  parser.add_argument('--vorticity', dest='plot_vorticity',
                      action='store_true',
                      help='plots the vorticity field')
  parser.add_argument('--pressure', dest='plot_pressure',
                      action='store_true',
                      help='plots the pressure field')
  parser.add_argument('--u-velocity', dest='plot_uvelocity',
                      action='store_true',
                      help='plots the u-velocity field')
  parser.add_argument('--v-velocity', dest='plot_vvelocity',
                      action='store_true',
                      help='plots the v-velocity field')
  parser.add_argument('--limits', dest='limits',
                      nargs=2, type=float, 
                      default=[-1.0, 1.0],
                      metavar=('min', 'max'),
                      help='Range to plot')
  parser.add_argument('--times', dest='times',
                      nargs=3, type=float, 
                      default=[None, None, None],
                      metavar=('start', 'end', 'increment'),
                      help='Range of times to plot')
  parser.add_argument('--bottom-left', dest='bottom_left',
                      nargs=2, type=float, 
                      default=[-2.0, -2.0],
                      metavar=('x', 'y'),
                      help='bottom-left corner of the rectangular view (x, y)')
  parser.add_argument('--top-right', dest='top_right',
                      nargs=2, type=float, 
                      default=[2.0, 2.0],
                      metavar=('x', 'y'),
                      help='top-right corner of the rectangular view (x, y)')
  parser.add_argument('--width', dest='width',
                      type=int, 
                      default=600,
                      help='figure width in pixels')
  parser.add_argument('--coeff', dest='coeff', 
                      type=float, 
                      default=1.0,
                      help='DEPRECATED -- coefficient to adjust the view')
  # parse given options file
  parser.add_argument('--options', 
                      type=open, action=miscellaneous.ReadOptionsFromFile,
                      help='path of the file with options to parse')
  print('done')
  return parser.parse_args()


def main():
  """Executes the ParaView macro to plot a variable field at various times."""
  parameters = parse_command_line()

  # display front patch and read pressure and velocity
  openfoam_file_name = '{}.OpenFOAM'.format(os.path.basename(os.path.normpath(parameters.directory)))
  reader = PV3FoamReader(FileName='{}/{}'.format(parameters.directory, openfoam_file_name))
  if parameters.plot_vorticity:
    print('[info] plotting vorticity field...')
    variable_name = 'vorticity'
    variable_nickname = 'vorticity'
  elif parameters.plot_pressure:
    print('[info] plotting pressure field...')
    variable_name = 'pressure'
    variable_nickname = 'p'
  elif parameters.plot_uvelocity:
    print('[info] plotting u-velocity field...')
    variable_name = 'u-velocity'
    variable_nickname = 'U'
  elif parameters.plot_vvelocity:
    print('[info] plotting v-velocity field...')
    variable_name = 'v-velocity'
    variable_nickname = 'U'
  else:
    print('[error] nothing to plot; use flag --vorticity, --u-velocity, '
          '--v-velocity, or --pressure')
    return
  reader.VolumeFields = [variable_nickname]
  reader.MeshParts = ['front - patch']

  # set up the view
  x_bl, y_bl = parameters.bottom_left
  x_tr, y_tr = parameters.top_right
  x_center, y_center = 0.5*(x_tr+x_bl), 0.5*(y_tr+y_bl)
  # coeff value below needs to be fully understood
  h = 0.5*(y_tr-y_bl) + parameters.coeff
  width = parameters.width
  height = width*(y_tr-y_bl)/(x_tr-x_bl)
  view = GetRenderView()
  view.ViewSize = [width, height]
  Render()
  view.CenterAxesVisibility = 0
  view.OrientationAxesVisibility = 0
  view.CameraPosition = [x_center, y_center, h]
  view.CameraFocalPoint = [x_center, y_center, 0.0]
  view.CameraViewUp = [0.0, 1.0, 0.0]
  view.CenterOfRotation = [0.0, 0.0, 1.0]
  view.CameraViewAngle = 90.0
  view.Background = [0.34, 0.34, 0.34]
  Render()

  # create images folder if does not exist
  rectangle = '{:.2f}_{:.2f}_{:.2f}_{:.2f}'.format(x_bl, y_bl, x_tr, y_tr)
  images_directory = '{}/images/{}_{}'.format(parameters.directory, variable_name, rectangle)
  if not os.path.isdir(images_directory):
    os.makedirs(images_directory)
  print('[info] save-directory: {}'.format(images_directory))

  if parameters.plot_vorticity:
    # edit color-map
    vorticity_min = float("{0:.2f}".format(parameters.limits[0]))
    vorticity_max = float("{0:.2f}".format(parameters.limits[1]))
    PVLookupTable = GetLookupTableForArray('vorticity', 3, 
                                           RGBPoints=[vorticity_min, 0.0, 0.0, 1.0, 
                                                      vorticity_max, 1.0, 0.0, 0.0], 
                                           VectorMode='Component', 
                                           VectorComponent=2, 
                                           NanColor=[0.0, 0.0, 0.0],
                                           ColorSpace='Diverging', 
                                           ScalarRangeInitialized=1.0, 
                                           LockScalarRange=1)
  elif parameters.plot_uvelocity:
    # edit color-map
    velocity_min = float("{0:.2f}".format(parameters.limits[0]))
    velocity_max = float("{0:.2f}".format(parameters.limits[1]))
    PVLookupTable = GetLookupTableForArray('U', 1, 
                                           RGBPoints=[velocity_min, 0.0, 0.0, 1.0, 
                                                      velocity_max, 1.0, 0.0, 0.0], 
                                           VectorMode='Component', 
                                           VectorComponent=0, 
                                           NanColor=[0.0, 0.0, 0.0],
                                           ColorSpace='Diverging', 
                                           ScalarRangeInitialized=1.0, 
                                           LockScalarRange=1)
  elif parameters.plot_vvelocity:
    # edit color-map
    velocity_min = float("{0:.2f}".format(parameters.limits[0]))
    velocity_max = float("{0:.2f}".format(parameters.limits[1]))
    PVLookupTable = GetLookupTableForArray('U', 2, 
                                           RGBPoints=[velocity_min, 0.0, 0.0, 1.0, 
                                                      velocity_max, 1.0, 0.0, 0.0], 
                                           VectorMode='Component', 
                                           VectorComponent=1,
                                           NanColor=[0.0, 0.0, 0.0],
                                           ColorSpace='Diverging', 
                                           ScalarRangeInitialized=1.0, 
                                           LockScalarRange=1)
  elif parameters.plot_pressure:
    # edit color-map
    pressure_min = float("{0:.2f}".format(parameters.limits[0]))
    pressure_max = float("{0:.2f}".format(parameters.limits[1]))
    PVLookupTable = GetLookupTableForArray('p', 1,
                                           RGBPoints=[pressure_min, 0.0, 0.0, 1.0,
                                                      pressure_max, 1.0, 0.0, 0.0],
                                           VectorMode='Magnitude',
                                           NanColor=[0.0, 0.0, 0.0],
                                           ColorSpace='HSV',
                                           ScalarRangeInitialized=1.0,
                                           LockScalarRange=1)

  # add scalar bar
  scalar_bar = CreateScalarBar(ComponentTitle='', 
                               Title=variable_name, 
                               Position2=[0.1, 0.5], 
                               Enabled=1, 
                               LabelFontSize=12, 
                               LabelColor=[0.0, 0.0, 0.0],
                               LookupTable=PVLookupTable,
                               TitleFontSize=12, 
                               TitleColor=[0.0, 0.0, 0.0], 
                               Position=[0.02, 0.25])
  view.Representations.append(scalar_bar)
  # show field
  data_representation = Show()
  data_representation.ColorArrayName = variable_nickname
  data_representation.LookupTable = PVLookupTable
  data_representation.ColorAttributeType = 'CELL_DATA'
  
  # add text to view
  text = Text()
  data_representation_3 = Show()
  data_representation_3.FontSize = 12
  data_representation_3.TextScaleMode = 2
  data_representation_3.Position = [0.02, 0.9]  # 0.0, 0.0: bottom-left
  data_representation_3.Color = [0.0, 0.0, 0.0]

  # get time values to plot
  if not parameters.times[1]:
    times = numpy.array(reader.TimestepValues)
  else: 
    time_start, time_end, time_increment = parameters.times
    times = numpy.arange(time_start, time_end+time_increment/2.0, time_increment)
  
  # time-loop to plot and save the vorticity field
  for time in times:
    print('[info] creating view at time: {}...'.format(time))
    view.ViewTime = time
    text.Text = 'time = {}'.format(time)
    WriteImage('{}/{}{:06.2f}.png'.format(images_directory, variable_name, time))


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))
