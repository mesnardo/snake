# file: generateGEOFile.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Generate .geo file to be read by GMSH


import argparse
import os
import sys

sys.path.append('library')
import GEOFile


def parse_command_line():
  """Parses the command-line."""
  print('-> parsing command-line... '),
  # create the parser
  parser = argparse.ArgumentParser(description='Generates a .geo file',
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  # fill the parser with arguments
  parser.add_argument('--body-file', dest='body_file_path', 
                      type=str,
                      help='path of file with body coordinates')
  parser.add_argument('--body-name', dest='body_name', 
                      type=str, default='body',
                      help='name of the patch used in OpenFOAM')
  parser.add_argument('--save-name', dest='save_name', 
                      type=str, default='mesh_info',
                      help='name of the .geo file (without extension)')
  parser.add_argument('--save-dir', dest='save_dir', 
                      type=str, default=os.getcwd(),
                      help='directory where to save .geo file')
  parser.add_argument('--bottom-left', '-bl', dest='bottom_left', 
                      type=float, nargs='+', default=[-20.0, -20.0],
                      help='coordinates of the bottom-left corner of the '
                           'computational domain')
  parser.add_argument('--top-right', '-tr', dest='top_right', 
                      type=float, nargs='+', default=[20.0, 20.0],
                      help='coordinates of the top-right corner of the '
                           'computational domain')
  parser.add_argument('--n-inlet', dest='n_inlet', 
                      type=int, default=20,
                      help='number of points on inlet boundary')
  parser.add_argument('--level', dest='level', 
                      type=int, default=0,
                      help='level of refinement on the body')
  parser.add_argument('--box', dest='boxes', 
                      type=float, nargs='+',
                      help='adds refinement boxes (x_bl, y_bl, x_tr, y_tr, level)')
  print('done')
  return parser.parse_args()


def main():
  """Generates a .geo file that will be read by GMSH to generate the mesh."""
  parameters = parse_command_line()

  domain = GEOFile.Domain(bottom_left=parameters.bottom_left,
                          top_right=parameters.top_right,
                          n_inlet=parameters.n_inlet)

  body = GEOFile.Body(parameters.body_name, domain)
  body.read_coordinates_from_file(parameters.body_file_path)

  # write .geo file
  geo_path = '%s/%s.geo' % (args.save_dir, args.geo_name)
  with open(geo_path, 'w') as outfile:
    # write characteristic-lengths
    outfile.write('cl_exterior = %f;\n' % cl_exterior)
    outfile.write('cl_body = %f;\n' % cl_body)
    # write body points
    outfile.write('// body points\n')
    for i in xrange(n):
      outfile.write('Point(%d) = {%f, %f, 0.0};\n' 
              % (i+1, x[i], y[i]))
      #outfile.write('Point(%d) = {%f, %f, 0.0, %f};\n' 
              #% (i+1, x[i], y[i], cl_body))
    # write body lines
    outfile.write('// body lines\n')
    for i in xrange(n-1):
      outfile.write('Line(%d) = {%d, %d};\n' % (i+1, i+1, i+2))
    outfile.write('Line(%d) = {%d, %d};\n' % (n, n, 1))
    # write domain points
    outfile.write('// domain points\n')
    outfile.write('Point(%d) = {%f, %f, 0.0, %f};\n' 
            % (n+1, args.bl[0], args.bl[1], cl_exterior))
    outfile.write('Point(%d) = {%f, %f, 0.0, %f};\n' 
            % (n+2, args.tr[0], args.bl[1], cl_exterior))
    outfile.write('Point(%d) = {%f, %f, 0.0, %f};\n' 
            % (n+3, args.tr[0], args.tr[1], cl_exterior))
    outfile.write('Point(%d) = {%f, %f, 0.0, %f};\n' 
            % (n+4, args.bl[0], args.tr[1], cl_exterior))
    # write domain lines
    outfile.write('// domain lines\n')
    outfile.write('Line(%d) = {%d, %d};\n' % (n+1, n+1, n+2))
    outfile.write('Line(%d) = {%d, %d};\n' % (n+2, n+2, n+3))
    outfile.write('Line(%d) = {%d, %d};\n' % (n+3, n+3, n+4))
    outfile.write('Line(%d) = {%d, %d};\n' % (n+4, n+4, n+1))
    # write body line-loop
    outfile.write('// body line-loop\n')
    outfile.write('Line Loop(1) = {%s};\n' 
            % ', '.join(['%s' % str(i+1) for i in xrange(n)]))
    # write domain line-loop
    outfile.write('// domain line-loop\n')
    outfile.write('Line Loop(2) = {%s};\n' 
            % ', '.join(['%s' % str(n+i) for i in [1, 2, 3, 4]]))
    # write plane surface
    outfile.write('// plane surface\n')
    outfile.write('Plane Surface(1) = {1, 2};\n')
    # physical volume
    outfile.write('// physical volume\n')
    outfile.write('Physical Volume(1) = {1};\n')
    # create box fields
    if args.boxes:
      counter_fields = 0
      n_buffer = 10 # number of cells between levels of refinement
      n_boxes = len(args.boxes)/5
      for i in xrange(n_boxes):
        index_box = 5*i
        # parameters of the box
        counter_fields += 1
        box = {'id': counter_fields,
             'x_bl': args.boxes[index_box+0], 
             'y_bl': args.boxes[index_box+1],
             'x_tr': args.boxes[index_box+2], 
             'y_tr': args.boxes[index_box+3],
             'cl_in': cl_exterior/2.0**args.boxes[index_box+4], 
             'cl_out': cl_exterior}
        write_box(box, outfile)
        # smooth transition between the box and the exterior
        while 2.0*box['cl_in'] < cl_exterior:
          counter_fields += 1
          # parameters of the box at the next level
          box['id'] = counter_fields
          box['cl_in'] *= 2.0
          box['x_bl'] -= (n_buffer-1)*box['cl_in']
          box['y_bl'] -= (n_buffer-1)*box['cl_in']
          box['x_tr'] += (n_buffer-1)*box['cl_in']
          box['y_tr'] += (n_buffer-1)*box['cl_in']
          write_box(box, outfile)
      # write background field (Min)
      counter_fields += 1
      outfile.write('// background field\n')
      outfile.write('Field[%d] = Min;\n' % (counter_fields))
      outfile.write('Field[%d].FieldsList = {%s};\n' 
              % (counter_fields,
                 ', '.join([str(i) 
                    for i in xrange(1, counter_fields)])))
      outfile.write('Background Field = %d;\n' % (counter_fields))
    # write physical surfaces
    outfile.write('// physical surfaces\n')
    outfile.write('Physical Surface("back") = {%d};\n' % (1))
    outfile.write('Physical Surface("front") = {%d};\n' % (6*n+26))
    outfile.write('Physical Surface("inlet") = {%d};\n' % (6*n+13))
    outfile.write('Physical Surface("outlet") = {%d};\n' % (6*n+21))
    outfile.write('Physical Surface("bottom") = {%d};\n' % (6*n+25))
    outfile.write('Physical Surface("top") = {%d};\n' % (6*n+17))
    outfile.write('Physical Surface("%s") = {%s};\n'
            % (args.body_name, 
               ', '.join([str(i) 
                  for i in numpy.arange(2*n+13, 6*n+10, 4)])))
    # recombine and extrude to get a 3D mesh with 1 cell in 3rd-direction
    outfile.write('// GMSH parameters\n')
    outfile.write('Recombine Surface{1} = 0;\n')
    outfile.write('Mesh.Algorithm = 8;\n')  # DelQuad algorithm
    outfile.write('Extrude {0, 0, 1} {'
            '\nSurface{1};\nLayers{1};\nRecombine;\n'
            '}\n')
    outfile.write('Mesh.Smoothing = 100;\n')
    outfile.write('General.ExpertMode = 1;\n')


if __name__ == '__main__':
  main()
