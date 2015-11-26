#!/bin/python

# file: getSpeedUp.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# brief: Gets the speed-up of parallel simulations compared to serial one.


import os
import linecache

import argparse


def read_inputs():
  """Parse the command-line."""
  # create parser
  parser = argparse.ArgumentParser(description='Gets the speed-up',
                        formatter_class= argparse.ArgumentDefaultsHelpFormatter)
  # fill parser with arguments
  parser.add_argument('--series', dest='series', type=str, default=os.getcwd(),
                      help='series of simulations to consider')
  parser.add_argument('--simulations', dest='simulations', type=int, nargs='+',
                      default=['n1', 'n2', 'n4', 'n8', 'n16', 'n32', 'n64', 'n128'],
                      help='parallel simulations to consider')
  return parser.parse_args()


def get_wall_time(file_path):
  """Parses the file to get the wall-time in seconds.

  Parameters
  ----------
  file_path: str
    Path of the file containing the wall-time info.

  Returns
  -------
  wall_time: float
    Wall-time in seconds (milliseconds precision).
  """
  line = linecache.getline(file_path, 2).split()[-1]
  minutes, rest = line.split('m')
  seconds, rest = rest.split('.')
  milliseconds, rest = rest.split('s')
  wall_time = 60.0*int(minutes)+int(seconds)+1.0E-03*int(milliseconds)
  return wall_time


def main():
  """Gets the speed-up of parallel simulations compared to serial one."""
  parameters = read_inputs()
  wall_times, speed_ups = [], []
  outfile_path = '{}/speedUps.txt'.format(parameters.series)
  outfile = open(outfile_path, 'w')
  for simulation in parameters.simulations:
    log_file = '{0}/{1}/log_{1}.err'.format(parameters.series, simulation)
    wall_times.append(get_wall_time(log_file))
    speed_ups.append(wall_times[0]/wall_times[-1])
    text = 'simulation: {}\t\twall-time:{:.2f}\t\tspeed-up:{:2f}'.format(simulation,
                                                                         wall_times[-1],
                                                                         speed_ups[-1])
    print(text)
    outfile.write(text+'\n')
  outfile.close()


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))