#!/bin/sh python

# file: plotScaling.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# brief: Plots the wall-time versus the process count.


import os
import sys
import argparse

import numpy

import logSummaryReader


def read_inputs():
  parser = argparse.ArgumentParser(description='Plots the instantaneous forces',
                        formatter_class= argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument('--series-dir', dest='series_directory', type=str, 
                      nargs='+', default=os.getcwd(), 
                      help='directory of each series')
  parser.add_argument('--descriptions', dest='descriptions', type=str, nargs='+',
                      default=['no-description'],
                      help='description of each series series')
  parser.add_argument('--nprocs', dest='nprocs_list', type=int, nargs='+',
                      default=[1, 2, 4, 8, 16, 32, 64, 128],
                      help='list of number of processors')
  parser.add_argument('--save', dest='save', action='store_true',
                      help='saves the plot as a .png file')
  parser.add_argument('--save-dir', dest='save_directory', type=str, 
                      default=os.getcwd(),
                      help='directory where to save .png file')
  parser.add_argument('--save-name', dest='save_name', type=str, 
                      default='wallTimeVsProcessCount', 
                      help='name of the .png file to save')
  parser.add_argument('--average', dest='average', action='store_true',
                      help='averages the series')
  parser.add_argument('--breakdown', dest='breakdown', action='store_true',
                      help='plots the breakdown of a series')
  parser.add_argument('--show', dest='show', action='store_true',
                      help='plots the wall-time versus the process count')
  return parser.parse_args()


def main():
  parameters = read_inputs()
  n_series = len(parameters.series_directory)
  if not (len(parameters.descriptions) == n_series):
    for i in xrange(n_series):
      parameters.descriptions = [None for i in xrange(n_series)]
  series_list = []
  for i, directory in enumerate(parameters.series_directory):
    series_list.append(logSummaryReader.Series(directory,
                                               nprocs=numpy.array(parameters.nprocs_list),
                                               description=parameters.descriptions[i]))
  save_path = ('{}/{}'.format(parameters.save_directory, parameters.save_name)
               if parameters.save else None)
  logSummaryReader.plot_wall_time_vs_process_count(series_list, 
                                                   save=save_path,
                                                   show=parameters.show)
  if parameters.average and len(series_list) > 0:
    average_series = logSummaryReader.AveragedSeries(series_list=series_list, description='average')
    logSummaryReader.plot_wall_time_vs_process_count([average_series], show=parameters.show)

  if parameters.breakdown:
    logSummaryReader.plot_breakdown_series(series_list[0], show=parameters.show)


if __name__ == "__main__":
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))