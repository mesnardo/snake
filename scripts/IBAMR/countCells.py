# file: countCells.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# brief: Counts the number of cells in IBAMR mesh.
#        cli: visit -nowin -cli -s countCells.py <options>


import os
import sys
import argparse
import socket

from snake import miscellaneous


def parse_command_line():
  """Parses the command-line."""
  print('[info] parsing the command-line ...'),
  # create the parser
  parser = argparse.ArgumentParser(description='Counts the number of cells in IBAMR mesh',
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  # fill the parser with arguments
  parser.add_argument('--directory', dest='directory', 
                      type=str, 
                      default=os.getcwd(),
                      help='directory of the IBAMR simulation')
  parser.add_argument('--solution-folder', dest='solution_folder',
                      type=str, 
                      default='numericalSolution',
                      help='name of folder containing the solution in time')
  parser.add_argument('--steps', dest='steps',
                      type=int, nargs=3, 
                      default=(None, None, None),
                      metavar=('start', 'end', 'increment'),
                      help='steps to plot')
  parser.add_argument('--average', dest='average_limits', 
                      type=float, nargs=2, 
                      default=[0.0, float('inf')],
                      metavar=('time-start', 'time-end'),
                      help='temporal limits to consider to average forces')
  # parse given options file
  parser.add_argument('--options', 
                      type=open, action=miscellaneous.ReadOptionsFromFile,
                      help='path of the file with options to parse')
  print('done')
  return parser.parse_args()


def get_mean(times, n_cells, limits=[0.0, float('inf')]):
  """Computes the average number of cells.

  Parameters
  ----------
  times: list of floats
    Time values.
  n_cells: list of integers
    Number of cells in the mesh at each time value.
  limits: list of floats, optional
    Time-limits used to compute the average; 
    default: [0.0, +inf].

  Returns
  -------
  mean: integer
    Time-averaged number of cells in the mesh.
  """
  sum_n_cells, count = 0, 0
  for index, time in enumerate(times):
    if count == 0:
      start = time
    if limits[0] <= time <= limits[1]:
      sum_n_cells += n_cells[index]
      count += 1
      end = time
  mean = sum_n_cells/count
  print('[info] average number of cells between {} and {}: {}'.format(start, end, mean))
  return mean


def main():
  """Counts the number of cells in IBAMR mesh."""
  args = parse_command_line()

  OpenDatabase('{}:{}/{}/dumps.visit'.format(socket.gethostname(), 
                                             args.directory, 
                                             args.solution_folder), 0)
  AddPlot('Mesh', 'amr_mesh', 1, 1)
  DrawPlots()
  SetQueryFloatFormat('%g')
  
  times, n_cells = [], []
  for step in xrange(args.steps[0], args.steps[1]+1, args.steps[2]):
    try:
      SetTimeSliderState(step)
    except:
      break
    times.append(float(Query('Time')[:-1].split()[-1]))
    n_cells.append(int(Query('NumZones')[:-1].split()[-1]))
    print('[step {}] time: {} ; number of cells: {}'.format(step, times[-1], n_cells[-1]))

  get_mean(times, n_cells, limits=args.average_limits)

  return


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))
  sys.exit()