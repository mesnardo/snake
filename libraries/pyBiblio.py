#!/bin/sh/env python

# file: pyBiblio.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# brief: Library for reference management.


import os
import re
import argparse


class ReferenceManager(object):
  def __init__(self, directory=None):
    self.notes = self.get_notes(directory=directory)

  def get_notes(self, directory=None):
    notes = []
    for (directory, _, files) in os.walk('/home/mesnardo/git/mesnardo/phdBook/literature'):
      for f in files:
        notes.append(PaperNote(os.path.join(directory, f)))
    return notes

  def print_info_notes(self):
    for note in self.notes:
      note.print_info()

  def print_notes(self, key=None, author=None, keyword=None, year=None):
    for note in self.notes:
      note.get(key=key, keyword=keyword, author=author, year=year)


class PaperNote(object):
  def __init__(self, note_path):
    self.path = note_path
    self.key = None
    self.title = None
    self.authors = []
    self.year = None
    self.keywords = []
    self.connections = []
    self.parse_info()

  def print_info(self):
    if not self.key:
      return
    print('#'*80)
    print('- path: {}'.format(self.path))
    print('- key: {}'.format(self.key))
    print('- title: {}'.format(self.title))
    print('- authors: {}'.format(', '.join(self.authors)))
    print('- year: {}'.format(self.year))
    print('- keywords: {}'.format(' | '.join(self.keywords)))
    if self.connections:
      print('- list of connections:')
      for connection in self.connections:
        print('\t- key: {}'.format(connection['key']))
        print('\t- reason: {}'.format(connection['reason']))
    print('#'*80)

  def parse_info(self):
    look_for = '## pyBiblio'
    with open(self.path, 'r') as infile:
      lines = infile.readlines()
    index_start, index_end = None, None
    for index, line in enumerate(lines):
      match = re.search(look_for, line)
      if match and not index_start:
        index_start = index
      elif match and index_start:
        index_end = index
        break
    if index_start and index_end:
      lines = lines[index_start: index_end]
      self.key = self.set('key', lines)
      self.title = self.set('title', lines)
      self.authors = self.set('authors', lines)
      self.year = self.set('year', lines)
      self.keywords = self.set('keywords', lines)
      self.connections = self.set('connections', lines)

  def set(self, look_for, lines):
    if look_for == 'connections':
      return self.set_connections(lines)
    for line in lines:
      if re.search(look_for, line):
        if look_for == 'key':
          return line.split(':')[-1].strip()
        if look_for == 'title':
          return line.split(':')[-1].strip()
        if look_for == 'authors':
          return re.findall(r"[\w']+", line.split(':')[-1])
        if look_for == 'year':
          return int(line.split(':')[-1].strip())
        if look_for == 'keywords':
          return [keyword.strip() 
                  for keyword in re.findall(r"[^,;]+", line.split(':')[-1])]

  def set_connections(self, lines):
    connections = []
    for line in lines:
      if re.search('connection', line):
        data = line.strip().split(':')[-1].strip().split(',')
        connections.append({'key': data[0].strip(), 'reason': data[1].strip()})
    return connections

  def get(self, key=None, author=None, keyword=None, year=None):
    if key and key == self.key:
      self.print_info()
    if author and author in self.authors:
      self.print_info()
    if keyword and keyword in self.keywords:
      self.print_info()
    if year and year == self.year:
      self.print_info()


def parse_command_line():
  """Parses the command-line."""
  # create parser
  parser = argparse.ArgumentParser(description='Reference manager',
                        formatter_class= argparse.ArgumentDefaultsHelpFormatter)
  # fill parser with arguments
  parser.add_argument('--directory', dest='directory', 
                      type=str, default='/home/mesnardo/git/mesnardo/phdBook/literature', 
                      help='directory containing literature notes')
  parser.add_argument('--key', dest='keys',
                      nargs='+', type=str, default=[],
                      help='Looking for papers with given key(s)')
  parser.add_argument('--keyword', dest='keywords',
                      nargs='+', type=str, default=[],
                      help='Looking for papers with given keyword(s)')
  parser.add_argument('--author', dest='authors',
                      nargs='+', type=str, default=[],
                      help='Looking for papers with given author(s)')
  parser.add_argument('--year', dest='years', 
                      nargs='+', type=int, default=[],
                      help='Looking for papers with given year(s)')
  return parser.parse_args()
        

def main():
  parameters = parse_command_line()
  manager = ReferenceManager(directory=parameters.directory)
  for key in parameters.keys:
    manager.print_notes(key=key)
  for keyword in parameters.keywords:
    manager.print_notes(keyword=keyword)
  for author in parameters.authors:
    manager.print_notes(author=author)
  for year in parameters.years:
    manager.print_notes(year=year)


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))