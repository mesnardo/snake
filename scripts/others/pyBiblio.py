# file: pyBiblio.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# brief: Library manager.


import os
import re
import argparse


class ReferenceManager(object):
  """Contains info about each note written."""
  def __init__(self, directory=None):
    """Reads the notes in a given directory in a recursive way.

    Parameters
    ----------
    directory: string
      Directory containing the notes; default: None.
    """
    self.notes = self.get_notes(directory=directory)

  def get_notes(self, directory=None):
    """Lists the notes and parses each one.

    Returns an error if the directory does not exist.

    Parameters
    ----------
    directory: string
      Directory containing the notes; default: None.

    Returns
    -------
    notes: dictionary of PaperNote objects
      Dictionary containing the notes.
    """
    if not os.path.exists(directory):
      print('directory: {}'.format(directory))
      print('[error] literature directory does not exist')
      exit(0)
    notes = {}
    for (directory, _, files) in os.walk(directory):
      for f in files:
        if 'template' not in f:
          note = PaperNote(os.path.join(directory, f))
          if note.key:
            notes[note.key] = note
    return notes

  def print_info_notes(self):
    """Prints info about each note of the reference manager."""
    for key, note in self.notes.iteritems():
      note.print_info()

  def search_notes(self, keys=[], keywords=[], authors=[], years=[], connection=None):
    """Prints notes that match given criteria.

    Parameters
    ----------
    keys: list of strings
      List of keys to look for; default: [].
    keywords: list of strings
      List of keywords to look for; default: [].
    authors: list of strings
      List of authors to look for; default: [].
    years: list of integers
      List of years to look for; default: [].
    connection: string
      Key of the note to print connections with; default: None.
    """
    for key in keys:
      self.notes[key].print_info()
    for keyword in keywords:
      for note in self.notes.itervalues():
        if note.search(keyword=keyword):
          note.print_info()
    for author in authors:
      for note in self.notes.itervalues():
        if note.search(author=author):
          note.print_info()
    for year in years:
      for note in self.notes.itervalues():
        if note.search(year=year):
          note.print_info()
    if connection:
      self.notes[connection].print_info()
      for note in self.notes.itervalues():
        if note.search(connection=connection):
          note.print_info()

  def pull_brief_note(self, key=None):
    """Pulls the brief notes about a paper given its key.

    Parameters
    ----------
    key: string
      Key of the paper; default: None.
    """
    if key in self.notes.keys():
      self.notes[key].pull_brief()
        

class PaperNote(object):
  """Contains information about a note."""
  def __init__(self, note_path):
    """Parses the note.

    Parameters
    ----------
    note_path: string
      Path of the note (markdown file).
    """
    self.path = note_path
    self.key = None
    self.title = None
    self.authors = []
    self.year = None
    self.keywords = []
    self.citations = None
    self.connections = []
    self.parse_info()

  def print_info(self):
    """Prints information about the paper."""
    if not self.key:
      return
    print('-'*80)
    print('- path: {}'.format(self.path))
    print('- key: {}'.format(self.key))
    print('- title: {}'.format(self.title))
    print('- authors: {}'.format(', '.join(self.authors)))
    print('- year: {}'.format(self.year))
    print('- citations: {}, {}'.format(self.citations['count'], self.citations['info']))
    print('- keywords: {}'.format(', '.join(self.keywords)))
    if self.connections:
      print('- list of connections:')
      for key, reason in self.connections.iteritems():
        print('  - key: {}'.format(key))
        print('  - reason: {}'.format(reason))
    print('-'*80)

  def parse_info(self):
    """Parses the note to look for paper characteristics."""
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
      self.citations = self.set('citations', lines)
      self.connections = self.set('connections', lines)

  def set(self, look_for, lines):
    """Sets the different information about the paper read in the note.

    Parameters
    ----------
    look_for: string
      The keyword in the note to look for.
    lines: list of strings
      Relevant lines of the note.
    """
    if look_for == 'connections':
      return self.set_connections(lines)
    for line in lines:
      if re.search(look_for, line):
        if look_for == 'key':
          return line.split(':')[-1].strip()
        elif look_for == 'title':
          return line.split(':')[-1].strip()
        elif look_for == 'authors':
          return re.findall(r"[\w']+", line.split(':')[-1])
        elif look_for == 'year':
          return int(line.split(':')[-1].strip())
        elif look_for == 'citations':
          line_split = line.strip().split(':')[-1].split(',')
          count = int(line_split[0])
          info = line_split[1]
          return {'count': count, 'info': info} 
        elif look_for == 'keywords':
          return [keyword.strip() 
                  for keyword in re.findall(r"[^,;]+", line.split(':')[-1])]

  def set_connections(self, lines):
    """Sets the connections of the paper with other papers.

    Parameters
    ----------
    lines: list of strings
      Relevant lines of the notes.

    Returns
    -------
    connections: disctionary of strings
      Contains the connections and the reasons of those connections.
    """
    connections = {}
    for line in lines:
      if re.search('connection', line):
        connection = line.strip().split(':')[1]
        if connection:
          line_split = connection.strip().split('[')
          key, reason = line_split[0].strip(), line_split[1][:-1]
          connections[key] = reason
    return connections

  def search(self, key=None, keyword=None, author=None, year=None, connection=None):
    """Checks if the paper matches given criteria.

    Parameters
    ----------
    key: string
      Key to match; default: None.
    keyword: string
      Keyword to match; default: None.
    author: string
      Author to match; default: None.
    year: integer
      Year to match; default: None.
    connection: string
      Key of the paper to look for possible connection; default: None.

    Returns
    -------
    1 or 0 depending whether the paper matches or not.
    """
    if key:
      return key == self.key
    elif keyword:
      return keyword.lower() in [k.lower() for k in self.keywords]
    elif author:
      return author.lower() in [a.lower() for a in self.authors]
    elif year:
      return year == self.year
    elif connection:
      return connection in self.connections.keys()

  def pull_brief(self):
    """Pulls the brief paragraph about the paper from the note."""
    with open(self.path, 'r') as infile:
      lines = infile.readlines()
    index_start, index_end = None, None
    for index, line in enumerate(lines):
      if re.search('## In brief', line) and not index_end:
        index_start = index + 1
      if re.search('## In details', line) and index_start:
        index_end = index - 2
    self.print_info()
    lines = '\n'.join(lines[index_start: index_end])
    print('\nIn brief:\n')
    print('\n'.join(line.strip() for line in re.findall(r'.{1,80}(?:\s+|$)', lines)))


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
  parser.add_argument('--connection', dest='connection',
                      type=str,
                      help='key of the note to print connections with')
  parser.add_argument('--pull', dest='pull_brief', 
                      type=str, default=None,
                      help='key of the paper from which to pull the brief note')
  return parser.parse_args()
        

def main():
  """Main function. 
  Creates the reference manager and submit the command-line request.
  """
  parameters = parse_command_line()
  manager = ReferenceManager(directory=parameters.directory)
  manager.search_notes(keys=parameters.keys, keywords=parameters.keywords,
                       authors=parameters.authors, years=parameters.years,
                       connection=parameters.connection)
  manager.pull_brief_note(key=parameters.pull_brief)


if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))