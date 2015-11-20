# file: plotFields2d.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Generates .png files of the two-dimensional vorticity field.
# running: visit -nowin -cli -s plotFields2d.py <arguments>


import os
import sys
import math
import argparse


def parse_command_line():
  """Parses the command-line."""
  print('[info] parsing the command-line ...'),
  # create the parser
  parser = argparse.ArgumentParser(description='Plots the vorticity field with VisIt',
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  # fill the parser with arguments
  parser.add_argument('--directory', dest='directory', 
                      type=str, default=os.getcwd(),
                      help='directory of the IBAMR simulation')
  parser.add_argument('--body-name', dest='body_name',
                      type=str,
                      help='name of the body file (without the .vertex extension)')
  parser.add_argument('--vorticity', dest='plot_vorticity',
                      action='store_true',
                      help='plots the vorticity field')
  parser.add_argument('--limits', dest='limits',
                      nargs='+', type=float, default=(-1.0, 1.0),
                      help='Range to plot (min, max)')
  parser.add_argument('--steps', dest='steps',
                      nargs='+', type=int, default=(None, None, None),
                      help='steps to plot (min, max, increment)')
  parser.add_argument('--bottom-left', dest='bottom_left',
                      nargs='+', type=float, default=(-2.0, -2.0),
                      help='bottom-left corner of the rectangular view (x, y)')
  parser.add_argument('--top-right', dest='top_right',
                      nargs='+', type=float, default=(2.0, 2.0),
                      help='top-right corner of the rectangular view (x, y)')
  parser.add_argument('--width', dest='width',
                      type=int, default=600,
                      help='figure width in pixels')
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
  return parser.parse_args()


def main():
  """Plots the two-dimensional field with VisIt."""
  args = parse_command_line()

  field_name = ('vorticity' if args.plot_vorticity else sys.exit())
  view = args.bottom_left + args.top_right
  view_string = '{:.2f}_{:.2f}_{:.2f}_{:.2f}'.format(*view)
  images_directory = '{}/images/{}_{}'.format(args.directory, field_name, view_string)
  if not os.path.isdir(images_directory):
    os.makedirs(images_directory)

  width = args.width
  height = int(math.ceil(width*(view[3]-view[1])/(view[2]-view[0])))

  # Visit 2.8.2 log file
  ScriptVersion = "2.8.2"
  if ScriptVersion != Version():
      print "This script is for VisIt %s. It may not work with version %s" % (ScriptVersion, Version())
  ShowAllWindows()

  # display body
  OpenDatabase("localhost:{}/numericalResults/lag_data.visit".format(args.directory), 0)
  AddPlot("Mesh", "{}_vertices".format(args.body_name), 1, 1)
  DrawPlots()
  MeshAtts = MeshAttributes()
  MeshAtts.legendFlag = 0
  MeshAtts.lineStyle = MeshAtts.SOLID  # SOLID, DASH, DOT, DOTDASH
  MeshAtts.lineWidth = 0
  MeshAtts.meshColor = (0, 0, 0, 255)
  MeshAtts.outlineOnlyFlag = 0
  MeshAtts.errorTolerance = 0.01
  MeshAtts.meshColorSource = MeshAtts.Foreground  # Foreground, MeshCustom
  MeshAtts.opaqueColorSource = MeshAtts.Background  # Background, OpaqueCustom
  MeshAtts.opaqueMode = MeshAtts.Auto  # Auto, On, Off
  MeshAtts.pointSize = 0.05
  MeshAtts.opaqueColor = (255, 255, 255, 255)
  MeshAtts.smoothingLevel = MeshAtts.None  # None, Fast, High
  MeshAtts.pointSizeVarEnabled = 0
  MeshAtts.pointSizeVar = "default"
  MeshAtts.pointType = MeshAtts.Point  # Box, Axis, Icosahedron, Octahedron, Tetrahedron, SphereGeometry, Point, Sphere
  MeshAtts.showInternal = 0
  MeshAtts.pointSizePixels = 2
  MeshAtts.opacity = 1
  SetPlotOptions(MeshAtts)

  # display vorticity field
  OpenDatabase("localhost:{}/numericalResults/dumps.visit".format(args.directory), 0)
  HideActivePlots()
  AddPlot("Pseudocolor", "Omega", 1, 1)
  DrawPlots()
  PseudocolorAtts = PseudocolorAttributes()
  PseudocolorAtts.scaling = PseudocolorAtts.Linear  # Linear, Log, Skew
  PseudocolorAtts.skewFactor = 1
  PseudocolorAtts.limitsMode = PseudocolorAtts.OriginalData  # OriginalData, CurrentPlot
  PseudocolorAtts.minFlag = 1
  PseudocolorAtts.min = args.limits[0]
  PseudocolorAtts.maxFlag = 1
  PseudocolorAtts.max = args.limits[1]
  PseudocolorAtts.centering = PseudocolorAtts.Natural  # Natural, Nodal, Zonal
  PseudocolorAtts.colorTableName = "RdBu"
  PseudocolorAtts.invertColorTable = 1
  PseudocolorAtts.opacityType = PseudocolorAtts.FullyOpaque  # ColorTable, FullyOpaque, Constant, Ramp, VariableRange
  PseudocolorAtts.opacityVariable = ""
  PseudocolorAtts.opacity = 1
  PseudocolorAtts.opacityVarMin = 0
  PseudocolorAtts.opacityVarMax = 1
  PseudocolorAtts.opacityVarMinFlag = 0
  PseudocolorAtts.opacityVarMaxFlag = 0
  PseudocolorAtts.pointSize = 0.05
  PseudocolorAtts.pointType = PseudocolorAtts.Point  # Box, Axis, Icosahedron, Octahedron, Tetrahedron, SphereGeometry, Point, Sphere
  PseudocolorAtts.pointSizeVarEnabled = 0
  PseudocolorAtts.pointSizeVar = "default"
  PseudocolorAtts.pointSizePixels = 2
  PseudocolorAtts.lineType = PseudocolorAtts.Line  # Line, Tube, Ribbon
  PseudocolorAtts.lineStyle = PseudocolorAtts.SOLID  # SOLID, DASH, DOT, DOTDASH
  PseudocolorAtts.lineWidth = 0
  PseudocolorAtts.tubeDisplayDensity = 10
  PseudocolorAtts.tubeRadiusSizeType = PseudocolorAtts.FractionOfBBox  # Absolute, FractionOfBBox
  PseudocolorAtts.tubeRadiusAbsolute = 0.125
  PseudocolorAtts.tubeRadiusBBox = 0.005
  PseudocolorAtts.varyTubeRadius = 0
  PseudocolorAtts.varyTubeRadiusVariable = ""
  PseudocolorAtts.varyTubeRadiusFactor = 10
  PseudocolorAtts.endPointType = PseudocolorAtts.None  # None, Tails, Heads, Both
  PseudocolorAtts.endPointStyle = PseudocolorAtts.Spheres  # Spheres, Cones
  PseudocolorAtts.endPointRadiusSizeType = PseudocolorAtts.FractionOfBBox  # Absolute, FractionOfBBox
  PseudocolorAtts.endPointRadiusAbsolute = 1
  PseudocolorAtts.endPointRadiusBBox = 0.005
  PseudocolorAtts.endPointRatio = 2
  PseudocolorAtts.renderSurfaces = 1
  PseudocolorAtts.renderWireframe = 0
  PseudocolorAtts.renderPoints = 0
  PseudocolorAtts.smoothingLevel = 0
  PseudocolorAtts.legendFlag = 1
  PseudocolorAtts.lightingFlag = 1
  SetPlotOptions(PseudocolorAtts)
  TimeSliderNextState()
  TimeSliderPreviousState()
  # Begin spontaneous state
  View2DAtts = View2DAttributes()
  View2DAtts.windowCoords = (-2, 15, -5, 5)
  View2DAtts.viewportCoords = (0, 1, 0, 1)
  View2DAtts.fullFrameActivationMode = View2DAtts.Auto  # On, Off, Auto
  View2DAtts.fullFrameAutoThreshold = 100
  View2DAtts.xScale = View2DAtts.LINEAR  # LINEAR, LOG
  View2DAtts.yScale = View2DAtts.LINEAR  # LINEAR, LOG
  View2DAtts.windowValid = 1
  SetView2D(View2DAtts)
  # End spontaneous state

  View2DAtts = View2DAttributes()
  View2DAtts.windowCoords = (view[0], view[2], view[1], view[3])
  View2DAtts.viewportCoords = (0, 1, 0, 1)
  View2DAtts.fullFrameActivationMode = View2DAtts.Auto  # On, Off, Auto
  View2DAtts.fullFrameAutoThreshold = 100
  View2DAtts.xScale = View2DAtts.LINEAR  # LINEAR, LOG
  View2DAtts.yScale = View2DAtts.LINEAR  # LINEAR, LOG
  View2DAtts.windowValid = 1
  SetView2D(View2DAtts)

  # Logging for SetAnnotationObjectOptions is not implemented yet.
  AnnotationAtts = AnnotationAttributes()
  AnnotationAtts.axes2D.visible = 1
  AnnotationAtts.axes2D.autoSetTicks = 1
  AnnotationAtts.axes2D.autoSetScaling = 1
  AnnotationAtts.axes2D.lineWidth = 0
  AnnotationAtts.axes2D.tickLocation = AnnotationAtts.axes2D.Inside  # Inside, Outside, Both
  AnnotationAtts.axes2D.tickAxes = AnnotationAtts.axes2D.BottomLeft  # Off, Bottom, Left, BottomLeft, All
  AnnotationAtts.axes2D.xAxis.title.visible = 0
  AnnotationAtts.axes2D.xAxis.title.font.font = AnnotationAtts.axes2D.xAxis.title.font.Courier  # Arial, Courier, Times
  AnnotationAtts.axes2D.xAxis.title.font.scale = 1
  AnnotationAtts.axes2D.xAxis.title.font.useForegroundColor = 1
  AnnotationAtts.axes2D.xAxis.title.font.color = (0, 0, 0, 255)
  AnnotationAtts.axes2D.xAxis.title.font.bold = 1
  AnnotationAtts.axes2D.xAxis.title.font.italic = 1
  AnnotationAtts.axes2D.xAxis.title.userTitle = 0
  AnnotationAtts.axes2D.xAxis.title.userUnits = 0
  AnnotationAtts.axes2D.xAxis.title.title = "X-Axis"
  AnnotationAtts.axes2D.xAxis.title.units = ""
  AnnotationAtts.axes2D.xAxis.label.visible = 1
  AnnotationAtts.axes2D.xAxis.label.font.font = AnnotationAtts.axes2D.xAxis.label.font.Courier  # Arial, Courier, Times
  AnnotationAtts.axes2D.xAxis.label.font.scale = 1
  AnnotationAtts.axes2D.xAxis.label.font.useForegroundColor = 1
  AnnotationAtts.axes2D.xAxis.label.font.color = (0, 0, 0, 255)
  AnnotationAtts.axes2D.xAxis.label.font.bold = 1
  AnnotationAtts.axes2D.xAxis.label.font.italic = 1
  AnnotationAtts.axes2D.xAxis.label.scaling = 0
  AnnotationAtts.axes2D.xAxis.tickMarks.visible = 1
  AnnotationAtts.axes2D.xAxis.tickMarks.majorMinimum = 0
  AnnotationAtts.axes2D.xAxis.tickMarks.majorMaximum = 1
  AnnotationAtts.axes2D.xAxis.tickMarks.minorSpacing = 0.02
  AnnotationAtts.axes2D.xAxis.tickMarks.majorSpacing = 0.2
  AnnotationAtts.axes2D.xAxis.grid = 0
  AnnotationAtts.axes2D.yAxis.title.visible = 0
  AnnotationAtts.axes2D.yAxis.title.font.font = AnnotationAtts.axes2D.yAxis.title.font.Courier  # Arial, Courier, Times
  AnnotationAtts.axes2D.yAxis.title.font.scale = 1
  AnnotationAtts.axes2D.yAxis.title.font.useForegroundColor = 1
  AnnotationAtts.axes2D.yAxis.title.font.color = (0, 0, 0, 255)
  AnnotationAtts.axes2D.yAxis.title.font.bold = 1
  AnnotationAtts.axes2D.yAxis.title.font.italic = 1
  AnnotationAtts.axes2D.yAxis.title.userTitle = 0
  AnnotationAtts.axes2D.yAxis.title.userUnits = 0
  AnnotationAtts.axes2D.yAxis.title.title = "Y-Axis"
  AnnotationAtts.axes2D.yAxis.title.units = ""
  AnnotationAtts.axes2D.yAxis.label.visible = 1
  AnnotationAtts.axes2D.yAxis.label.font.font = AnnotationAtts.axes2D.yAxis.label.font.Courier  # Arial, Courier, Times
  AnnotationAtts.axes2D.yAxis.label.font.scale = 1
  AnnotationAtts.axes2D.yAxis.label.font.useForegroundColor = 1
  AnnotationAtts.axes2D.yAxis.label.font.color = (0, 0, 0, 255)
  AnnotationAtts.axes2D.yAxis.label.font.bold = 1
  AnnotationAtts.axes2D.yAxis.label.font.italic = 1
  AnnotationAtts.axes2D.yAxis.label.scaling = 0
  AnnotationAtts.axes2D.yAxis.tickMarks.visible = 1
  AnnotationAtts.axes2D.yAxis.tickMarks.majorMinimum = 0
  AnnotationAtts.axes2D.yAxis.tickMarks.majorMaximum = 1
  AnnotationAtts.axes2D.yAxis.tickMarks.minorSpacing = 0.02
  AnnotationAtts.axes2D.yAxis.tickMarks.majorSpacing = 0.2
  AnnotationAtts.axes2D.yAxis.grid = 0
  AnnotationAtts.userInfoFlag = 0
  AnnotationAtts.userInfoFont.font = AnnotationAtts.userInfoFont.Arial  # Arial, Courier, Times
  AnnotationAtts.userInfoFont.scale = 1
  AnnotationAtts.userInfoFont.useForegroundColor = 1
  AnnotationAtts.userInfoFont.color = (0, 0, 0, 255)
  AnnotationAtts.userInfoFont.bold = 0
  AnnotationAtts.userInfoFont.italic = 0
  AnnotationAtts.databaseInfoFlag = 1
  AnnotationAtts.timeInfoFlag = 1
  AnnotationAtts.databaseInfoFont.font = AnnotationAtts.databaseInfoFont.Arial  # Arial, Courier, Times
  AnnotationAtts.databaseInfoFont.scale = 1
  AnnotationAtts.databaseInfoFont.useForegroundColor = 1
  AnnotationAtts.databaseInfoFont.color = (0, 0, 0, 255)
  AnnotationAtts.databaseInfoFont.bold = 0
  AnnotationAtts.databaseInfoFont.italic = 0
  AnnotationAtts.databaseInfoExpansionMode = AnnotationAtts.File  # File, Directory, Full, Smart, SmartDirectory
  AnnotationAtts.databaseInfoTimeScale = 1
  AnnotationAtts.databaseInfoTimeOffset = 0
  AnnotationAtts.legendInfoFlag = 1
  AnnotationAtts.backgroundColor = (255, 255, 255, 255)
  AnnotationAtts.foregroundColor = (0, 0, 0, 255)
  AnnotationAtts.gradientBackgroundStyle = AnnotationAtts.Radial  # TopToBottom, BottomToTop, LeftToRight, RightToLeft, Radial
  AnnotationAtts.gradientColor1 = (0, 0, 255, 255)
  AnnotationAtts.gradientColor2 = (0, 0, 0, 255)
  AnnotationAtts.backgroundMode = AnnotationAtts.Solid  # Solid, Gradient, Image, ImageSphere
  AnnotationAtts.backgroundImage = ""
  AnnotationAtts.imageRepeatX = 1
  AnnotationAtts.imageRepeatY = 1
  AnnotationAtts.axesArray.visible = 1
  AnnotationAtts.axesArray.ticksVisible = 1
  AnnotationAtts.axesArray.autoSetTicks = 1
  AnnotationAtts.axesArray.autoSetScaling = 1
  AnnotationAtts.axesArray.lineWidth = 0
  AnnotationAtts.axesArray.axes.title.visible = 1
  AnnotationAtts.axesArray.axes.title.font.font = AnnotationAtts.axesArray.axes.title.font.Arial  # Arial, Courier, Times
  AnnotationAtts.axesArray.axes.title.font.scale = 1
  AnnotationAtts.axesArray.axes.title.font.useForegroundColor = 1
  AnnotationAtts.axesArray.axes.title.font.color = (0, 0, 0, 255)
  AnnotationAtts.axesArray.axes.title.font.bold = 0
  AnnotationAtts.axesArray.axes.title.font.italic = 0
  AnnotationAtts.axesArray.axes.title.userTitle = 0
  AnnotationAtts.axesArray.axes.title.userUnits = 0
  AnnotationAtts.axesArray.axes.title.title = ""
  AnnotationAtts.axesArray.axes.title.units = ""
  AnnotationAtts.axesArray.axes.label.visible = 1
  AnnotationAtts.axesArray.axes.label.font.font = AnnotationAtts.axesArray.axes.label.font.Arial  # Arial, Courier, Times
  AnnotationAtts.axesArray.axes.label.font.scale = 1
  AnnotationAtts.axesArray.axes.label.font.useForegroundColor = 1
  AnnotationAtts.axesArray.axes.label.font.color = (0, 0, 0, 255)
  AnnotationAtts.axesArray.axes.label.font.bold = 0
  AnnotationAtts.axesArray.axes.label.font.italic = 0
  AnnotationAtts.axesArray.axes.label.scaling = 0
  AnnotationAtts.axesArray.axes.tickMarks.visible = 1
  AnnotationAtts.axesArray.axes.tickMarks.majorMinimum = 0
  AnnotationAtts.axesArray.axes.tickMarks.majorMaximum = 1
  AnnotationAtts.axesArray.axes.tickMarks.minorSpacing = 0.02
  AnnotationAtts.axesArray.axes.tickMarks.majorSpacing = 0.2
  AnnotationAtts.axesArray.axes.grid = 0
  SetAnnotationAttributes(AnnotationAtts)
  SetActiveWindow(1)

  Source("/opt/visit/2.8.2/linux-x86_64/bin/makemovie.py")
  ToggleCameraViewMode()

  for step in xrange(args.steps[0], args.steps[1]+1, args.steps[2]):
    print('[step {}] creating and saving the field ...'.format(step))
    SetTimeSliderState(step)
    RenderingAtts = RenderingAttributes()
    RenderingAtts.antialiasing = 0
    RenderingAtts.multiresolutionMode = 0
    RenderingAtts.multiresolutionCellSize = 0.002
    RenderingAtts.geometryRepresentation = RenderingAtts.Surfaces  # Surfaces, Wireframe, Points
    RenderingAtts.displayListMode = RenderingAtts.Auto  # Never, Always, Auto
    RenderingAtts.stereoRendering = 0
    RenderingAtts.stereoType = RenderingAtts.CrystalEyes  # RedBlue, Interlaced, CrystalEyes, RedGreen
    RenderingAtts.notifyForEachRender = 0
    RenderingAtts.scalableActivationMode = RenderingAtts.Auto  # Never, Always, Auto
    RenderingAtts.scalableAutoThreshold = 2000000
    RenderingAtts.specularFlag = 0
    RenderingAtts.specularCoeff = 0.6
    RenderingAtts.specularPower = 10
    RenderingAtts.specularColor = (255, 255, 255, 255)
    RenderingAtts.doShadowing = 0
    RenderingAtts.shadowStrength = 0.5
    RenderingAtts.doDepthCueing = 0
    RenderingAtts.depthCueingAutomatic = 1
    RenderingAtts.startCuePoint = (-10, 0, 0)
    RenderingAtts.endCuePoint = (10, 0, 0)
    RenderingAtts.compressionActivationMode = RenderingAtts.Never  # Never, Always, Auto
    RenderingAtts.colorTexturingFlag = 1
    RenderingAtts.compactDomainsActivationMode = RenderingAtts.Never  # Never, Always, Auto
    RenderingAtts.compactDomainsAutoThreshold = 256
    SetRenderingAttributes(RenderingAtts)
    SaveWindowAtts = SaveWindowAttributes()
    SaveWindowAtts.outputToCurrentDirectory = 0
    SaveWindowAtts.outputDirectory = images_directory
    SaveWindowAtts.fileName = '{}{:0>7}'.format(field_name, step)
    SaveWindowAtts.family = 0
    SaveWindowAtts.format = SaveWindowAtts.PNG  # BMP, CURVE, JPEG, OBJ, PNG, POSTSCRIPT, POVRAY, PPM, RGB, STL, TIFF, ULTRA, VTK, PLY
    SaveWindowAtts.width = width
    SaveWindowAtts.height = height
    SaveWindowAtts.screenCapture = 0
    SaveWindowAtts.saveTiled = 0
    SaveWindowAtts.quality = 80
    SaveWindowAtts.progressive = 0
    SaveWindowAtts.binary = 0
    SaveWindowAtts.stereo = 0
    SaveWindowAtts.compression = SaveWindowAtts.PackBits  # None, PackBits, Jpeg, Deflate
    SaveWindowAtts.forceMerge = 0
    SaveWindowAtts.resConstraint = SaveWindowAtts.NoConstraint  # NoConstraint, EqualWidthHeight, ScreenProportions
    SaveWindowAtts.advancedMultiWindowSave = 0
    SetSaveWindowAttributes(SaveWindowAtts)
    SaveWindow()

  return

if __name__ == '__main__':
  print('\n[START] {}\n'.format(os.path.basename(__file__)))
  main()
  print('\n[END] {}\n'.format(os.path.basename(__file__)))
  sys.exit()