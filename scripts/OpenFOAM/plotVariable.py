#!/opt/OpenFOAM/ThirdParty-2.2.2/platforms/linux64Gcc/paraview-3.12.0/bin/pvbatch

# file: plotVariable.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Macro to run ParaView and plot variable in batch mode.


import argparse
import os

import numpy
from paraview.simple import *


def parse_command_line():
  """Parses the command-line."""
  # create the parser
  parser = argparse.ArgumentParser(description='Plots the vorticity field with ParaFOAM',
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  # fill the parser with arguments
  parser.add_argument('--directory', dest='directory', 
            type=str, default=os.getcwd(),
            help='directory of the OpenFOAM simulation')
  parser.add_argument('--vorticity', dest='plot_vorticity',
                      action='store_true',
                      help='plots the vorticity field')
  parser.add_argument('--pressure', dest='plot_pressure',
                      action='store_true',
                      help='plots the pressure field')
  parser.add_argument('--limits', dest='limits',
                      nargs='+', type=float,
                      help='Range to plot (min, max)')
  parser.add_argument('--times', dest='times',
                      nargs='+', type=float, default=[0.0, float('inf'), None],
                      help='Range of times to plot (min, max, increment)')
  parser.add_argument('--bottom-left', dest='bottom_left',
                      nargs='+', type=float, default=[-2.0, -2.0],
                      help='bottom-left corner of the rectangular view (x, y)')
  parser.add_argument('--top-right', dest='top_right',
                      nargs='+', type=float, default=[2.0, 2.0],
                      help='top-right corner of the rectangular view (x, y)')
  parser.add_argument('--width', dest='width',
                      type=int, default=600,
                      help='figure width in pixels')
  parser.add_argument('--coeff', dest='coeff', 
                      type=float, default=1.0,
                      help='WIP: coefficient to adjust the view')
  return parser.parse_args()


def main():
  """Executes the ParaView macro to plot a variable field at various times."""
  parameters = parse_command_line()

  # create images folder if does not exist
  images_path = '{}/images'.format(parameters.directory)
  if not os.path.isdir(images_path):
    os.makedirs(images_path)

  # display front patch and read pressure and velocity
  openfoam_file_name = '{}.OpenFOAM'.format(os.path.basename(os.path.normpath(parameters.directory)))
  reader = PV3FOAMReader(FileName='{}/{}'.format(parameters.directory, openfoam_file_name))
  if parameters.pressure
  reader.VolumeFields = []
  if parameters.plot_vorticity:
    variable_name = 'vorticity'
    reader.VolumeFields.append('vorticity')
  elif parameters.plot_pressure:
    variable_name = 'pressure'
    reader.VolumeFields.append('p')
  reader.MeshParts = ['front - patch']

  # set up the view
  x_bl, y_bl = parameters.bottom_left
  x_tr, y_tr = parameters.top_right
  x_center, y_center = 0.5*(x_tr+x_bl), 0.5*(y_tr+y_bl)
  # coeff value below needs to be fully understood
  h = 0.5*(y_tr-y_bl) + args.coeff
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
  data_representation.ColorArrayName = ('vorticity' if parameters.plot_vorticity
                                        'p' elif parameters.plot_pressure)
  data_representation.LookupTable = PVLookupTable
  data_representation.ColorAttributeType = 'CELL_DATA'
  
  # add text to view
  text = Text()
  data_representation_3 = Show()
  data_representation_3.FontSize = 12
  data_representation_3.TextScaleMode = 2
  data_representation_3.Position = [0.02, 0.9]  # 0.0, 0.0: bottom-left
  data_representation_3.Color = [0.0, 0.0, 0.0]

  # get time-steps to plot
  time_steps = numpy.array(reader.TimestepValues)
  start, end, every = parameters.times
  time_steps = numpy.arange(start, end+every/2.0, every)
  
  # time-loop to plot and save the vorticity field
  for time_step in time_steps:
    print('Time: {}'.format(time_step))
    view.ViewTime = time_step
    text.Text = 'time = {}'.format(time_step)
    WriteImage('{}/{}{}.png'.format(images_path, variable_name, time_step))


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))