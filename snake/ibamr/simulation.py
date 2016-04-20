# file: ibamrSimulation.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Implementation of the class `IBAMRSimulation`.


import os
import sys

import numpy

from ..simulation import Simulation
from ..force import Force


class IBAMRSimulation(Simulation):
  """Contains info about a IBAMR simulation.
  Inherits from class Simulation.
  """
  def __init__(self, description=None, directory=os.getcwd(), **kwargs):
    """Initializes by calling the parent constructor.

    Parameters
    ----------
    description: string, optional
      Description of the simulation;
      default: None.
    directory: string, optional
      Directory of the simulation;
      default: present working directory.
    """
    super(IBAMRSimulation, self).__init__(description=description, 
                                          directory=directory, 
                                          software='ibamr', 
                                          **kwargs)

  def read_forces(self, file_path=None, labels=None):
    """Reads forces from files.

    Parameters
    ----------
    relative_file_path: string
      Path of the file containing the forces;
      default: None.
    labels: list of strings, optional
      Label of each force to read;
      default: None.
    """
    if not file_path:
      file_path = '{}/dataIB/ib_Drag_force_struct_no_0'.format(self.directory)
    print('[info] reading forces from {} ...'.format(file_path)),
    with open(file_path, 'r') as infile:
      times, force_x, force_y = numpy.loadtxt(infile, dtype=float, 
                                              usecols=(0, 4, 5), unpack=True)
    self.forces.append(Force(times, force_x, '$F_x$'))
    self.forces.append(Force(times, force_y, '$F_y$'))
    print('done')

  def write_visit_summary_files(self, time_steps):
    """Writes summary files for Visit 
    with list of sub-directories to look into.

    Parameters
    ----------
    time_steps: 3-tuple of integers
      Staring and and ending time_steps followed by the time-step increment.
    """
    print('[info] writing summary files for VisIt ...'),
    time_steps = numpy.arange(time_steps[0], time_steps[1]+1, time_steps[2])
    # list of SAMRAI files to VisIt
    dumps_visit = numpy.array(['visit_dump.{0:05}/summary.samrai'
                               ''.format(time_step) for time_step in time_steps])
    # list of SILO file to VisIt
    lag_data_visit = numpy.array(['lag_data.cycle_{0:06d}/lag_data.cycle_{0:06d}.summary.silo'
                                  ''.format(time_step) for time_step in time_steps])
    # write files
    with open('{}/dumps.visit'.format(self.directory), 'w') as outfile:
      numpy.savetxt(outfile, dumps_visit, fmt='%s')
    with open('{}/lag_data.visit'.format(self.directory), 'w') as outfile:
      numpy.savetxt(outfile, lag_data_visit, fmt='%s')
    print('done')

  def plot_field_contours_visit(self, field_name,
                                field_range, 
                                body=None,
                                solution_folder='numericalSolution',
                                states=(0, 2**10000, 1),
                                view=(-2.0, -2.0, 2.0, 2.0), 
                                width=800):
    """Plots the contour of a given field using VisIt.

    Parameters
    ----------
    field_name: string
      Name of field to plot;
      choices: vorticity, pressure, velocity-magnitude, x-velocity, y-velocity.
    field_range: 2-tuple of floats
      Range of the field to plot (min, max).
    body: string, optional
      Name of the immersed body;
      default: None.
    solution_folder: string, optional
      Relative path of the folder containing the numerical solution;
      default: 'numericalSolution'.
    states: 3-tuple of integers, optional
      Limits of index of the states to plot followed by the increment;
      default: (0, 20000, 1).
    view: 4-tuple of floats, optional
      Bottom-left and top-right coordinates of the view to display;
      default: (-2.0, -2.0, 2.0, 2.0).
    width: integer, optional
      Width (in pixels) of the figure;
      default: 800. 
    """
    info = {}
    info['vorticity'] = {'variable': 'Omega',
                         'color-table': 'RdBu',
                         'invert-color-table': 1}
    info['pressure'] = {'variable': 'P',
                        'color-table': 'hot',
                        'invert-color-table': 0}
    info['velocity-magnitude'] = {'variable': 'U_magnitude',
                                  'color-table': 'RdBu',
                                  'invert-color-table': 1}
    info['x-velocity'] = {'variable': 'U_x',
                          'color-table': 'RdBu',
                          'invert-color-table': 1}
    info['y-velocity'] = {'variable': 'U_y',
                          'color-table': 'RdBu',
                          'invert-color-table': 1}
    # define dimensions of domain to plot
    height = int(math.ceil(width*(view[3]-view[1])/(view[2]-view[0])))
    # create images directory
    view_string = '{:.2f}_{:.2f}_{:.2f}_{:.2f}'.format(*view)
    images_directory = '{}/images/{}_{}'.format(self.directory, 
                                                field_name, 
                                                view_string)
    if not os.path.isdir(images_directory):
      print('[info] creating images directory {} ...'.format(images_directory))
      os.makedirs(images_directory)
    # check VisIt version
    script_version = '2.8.2'
    current_version = Version()
    if script_version != current_version:
      print('[warning] This script was created with VisIt-{}.'.format(script_version))
      print('[warning] It may not work with version {}'.format(current_version))

    ShowAllWindows()

    # display body
    if body:
      OpenDatabase("{}:{}/{}/lag_data.visit".format(GetLocalHostName(), 
                                                    self.directory, 
                                                    solution_folder), 0)
      AddPlot("Mesh", "{}_vertices".format(body), 1, 1)
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
    OpenDatabase("{}:{}/{}/dumps.visit".format(GetLocalHostName(), 
                                               self.directory, 
                                               solution_folder), 0)
    HideActivePlots()
    AddPlot("Pseudocolor", info[field_name]['variable'], 1, 1)
    DrawPlots()
    PseudocolorAtts = PseudocolorAttributes()
    PseudocolorAtts.scaling = PseudocolorAtts.Linear  # Linear, Log, Skew
    PseudocolorAtts.skewFactor = 1
    PseudocolorAtts.limitsMode = PseudocolorAtts.OriginalData  # OriginalData, CurrentPlot
    PseudocolorAtts.minFlag = 1
    PseudocolorAtts.min = field_range[0]
    PseudocolorAtts.maxFlag = 1
    PseudocolorAtts.max = field_range[1]
    PseudocolorAtts.centering = PseudocolorAtts.Natural  # Natural, Nodal, Zonal
    PseudocolorAtts.colorTableName = info[field_name]['color-table']
    PseudocolorAtts.invertColorTable = info[field_name]['invert-color-table']
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
    # colorbar of pseudocolor plot
    legend = GetAnnotationObject(GetPlotList().GetPlots(2).plotName)
    legend.xScale = 1
    legend.yScale = 0.5
    legend.numberFormat = '%# -9.2g'
    legend.orientation = legend.HorizontalBottom
    legend.managePosition = 0
    legend.position = (0.05, 0.10)
    legend.fontFamily = legend.Courier
    legend.fontBold = 1
    legend.fontHeight = 0.05
    legend.drawMinMax = 0
    legend.drawTitle = 0
    print('[info] legend settings:')
    print(legend)

    # set up view
    View2DAtts = View2DAttributes()
    View2DAtts.windowCoords = (view[0], view[2], view[1], view[3])
    View2DAtts.viewportCoords = (0, 1, 0, 1)
    View2DAtts.fullFrameActivationMode = View2DAtts.Auto  # On, Off, Auto
    View2DAtts.fullFrameAutoThreshold = 100
    View2DAtts.xScale = View2DAtts.LINEAR  # LINEAR, LOG
    View2DAtts.yScale = View2DAtts.LINEAR  # LINEAR, LOG
    View2DAtts.windowValid = 1
    print('[info] view settings:')
    print(View2DAtts)
    SetView2D(View2DAtts)

    # Logging for SetAnnotationObjectOptions is not implemented yet.
    AnnotationAtts = AnnotationAttributes()
    AnnotationAtts.axes2D.visible = 1
    AnnotationAtts.axes2D.autoSetTicks = 1
    AnnotationAtts.axes2D.autoSetScaling = 1
    AnnotationAtts.axes2D.lineWidth = 0
    AnnotationAtts.axes2D.tickLocation = AnnotationAtts.axes2D.Inside  # Inside, Outside, Both
    AnnotationAtts.axes2D.tickAxes = AnnotationAtts.axes2D.BottomLeft  # Off, Bottom, Left, BottomLeft, All
    # x-axis
    AnnotationAtts.axes2D.xAxis.title.visible = 0 # hide x-axis title
    AnnotationAtts.axes2D.xAxis.label.visible = 0 # hide x-axis label
    AnnotationAtts.axes2D.xAxis.tickMarks.visible = 0 # hide x-axis tick marks
    AnnotationAtts.axes2D.xAxis.grid = 0 # no grid
    # y-axis
    AnnotationAtts.axes2D.yAxis.title.visible = 0 # hide y-axis title
    AnnotationAtts.axes2D.yAxis.label.visible = 0 # hide y-axis label
    AnnotationAtts.axes2D.yAxis.tickMarks.visible = 0 # hide y-axis tick marks
    AnnotationAtts.axes2D.yAxis.grid = 0 # no grid
    AnnotationAtts.userInfoFlag = 0 # hide text with user's name 
    # settings for legend
    AnnotationAtts.databaseInfoFlag = 0
    AnnotationAtts.timeInfoFlag = 0
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
    AnnotationAtts.axesArray.visible = 0
    SetAnnotationAttributes(AnnotationAtts)
    print('[info] annotation settings:')
    print(AnnotationAtts)
    SetActiveWindow(1)

    # create time-annotation
    time_annotation = CreateAnnotationObject('Text2D')
    time_annotation.position = (0.05, 0.95)
    time_annotation.fontFamily = 1
    time_annotation.fontBold = 0
    time_annotation.height = 0.03
    print('[info] time-annotation:')
    print(time_annotation)

    # check number of states available
    if states[1] > TimeSliderGetNStates():
      print('[warning] maximum number of states available is {}'.format(TimeSliderGetNStates()))
      print('[warning] setting new final state ...')
      states[1] = TimeSliderGetNStates()

    # loop over saved time-steps
    states = numpy.arange(states[0], states[1]+1, states[2])
    for state in states:
      SetTimeSliderState(state)
      time = float(Query('Time')[:-1].split()[-1])
      print('\n[state {}] time: {} - creating and saving the field ...'.format(state, time))
      time_annotation.text = 'Time: {0:.3f}'.format(time)

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
      SaveWindowAtts.fileName = '{}{:0>7}'.format(field_name, state)
      SaveWindowAtts.family = 0
      SaveWindowAtts.format = SaveWindowAtts.PNG  # BMP, CURVE, JPEG, OBJ, PNG, POSTSCRIPT, POVRAY, PPM, RGB, STL, TIFF, ULTRA, VTK, PLY
      SaveWindowAtts.width = width
      SaveWindowAtts.height = height
      SaveWindowAtts.screenCapture = 0
      SaveWindowAtts.saveTiled = 0
      SaveWindowAtts.quality = 100
      SaveWindowAtts.progressive = 0
      SaveWindowAtts.binary = 0
      SaveWindowAtts.stereo = 0
      SaveWindowAtts.compression = SaveWindowAtts.PackBits  # None, PackBits, Jpeg, Deflate
      SaveWindowAtts.forceMerge = 0
      SaveWindowAtts.resConstraint = SaveWindowAtts.NoConstraint  # NoConstraint, EqualWidthHeight, ScreenProportions
      SaveWindowAtts.advancedMultiWindowSave = 0
      SetSaveWindowAttributes(SaveWindowAtts)
      
      SaveWindow()
      sys.exit(0)

  def counter_average_number_cells_visit(self, 
                                         solution_folder='numericalSolution',
                                         states=(0, 20000, 1),
                                         time_limits=(0.0, float('inf'))):
    """Calculates the number of cells in the mesh on average.

    Parameters
    ----------
    solution_folder: string, optional
      Relative path of the folder containing the numerical solution;
      default: 'numericalSolution'.
    states: 3-tuple of integers, optional
      Starting and ending states of the solution to consider followed by the increment;
      default: (0, 20000, 1).
    time_limits: 2-tuple of floats, optional
      Time-limits to consider for the average;
      default: (0, inf).

    Returns
    -------
    mean: float
      Average number of cells in the mesh.
    """
    OpenDatabase('{}:{}/{}/dumps.visit'.format(GetLocalHostName(), 
                                               self.directory, 
                                               solution_folder), 0)
    AddPlot('Mesh', 'amr_mesh', 1, 1)
    DrawPlots()
    SetQueryFloatFormat('%g')
    
    times, n_cells = [], []
    # check number of states available
    if states[1] > TimeSliderGetNStates():
      print('[warning] maximum number of states available is {}'.format(TimeSliderGetNStates()))
      print('[warning] setting new final state ...')
      states[1] = TimeSliderGetNStates()
    states = numpy.arange(states[0], states[1]+1, states[2])
    for state in states:
      SetTimeSliderState(state)
      times.append(float(Query('Time')[:-1].split()[-1]))
      n_cells.append(int(Query('NumZones')[:-1].split()[-1]))
      print('[step {}] time: {} ; number of cells: {}'.format(state, 
                                                              times[-1], 
                                                              n_cells[-1]))
    # compute average number of cells
    sum_n_cells, count = 0, 0
    for index, time in enumerate(times):
      if count == 0:
        start = time
      if time_limits[0] <= time <= time_limits[1]:
        sum_n_cells += n_cells[index]
        count += 1
        end = time
    mean = sum_n_cells/count
    print('[info] average number of cells between {} and {}: {}'.format(start, 
                                                                        end, 
                                                                        mean))
    return mean