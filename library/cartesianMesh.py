# file: cartesianMesh.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Implementation of the class CartesianMesh and its sub-classes.


import math
import numpy
import yaml


class Segment(object):
  def __init__(self, start, end, width, aspect_ratio=1.0, precision=2, reverse=False):
    self.start, self.end = start, end
    self.width = width
    if abs(aspect_ratio-1.0) <= 1.0E-06:
      self.nodes = self.create_uniform()
      self.stretch_ratio = 1.0
    else:
      self.nodes, self.stretch_ratio = self.create_stretched(aspect_ratio=aspect_ratio, 
                                                             precision=precision, 
                                                             reverse=reverse)
    self.nb_divisions = self.nodes.size-1

  def create_uniform(self):
    return numpy.arange(self.start, self.end+self.width/2.0, self.width, 
                        dtype=numpy.float64)

  def create_stretched(self, aspect_ratio, precision=2, reverse=False):
    length = abs(self.start-self.end)
    h = self.width
    current_precision = 1
    next_ratio = 2.0
    while current_precision <= precision:
      r = next_ratio
      n = int(round(math.log(1.0 - length/h*(1.0-r))/math.log(r)))
      ar = r**(n-1)
      if ar < aspect_ratio:
        next_ratio += (0.1)**current_precision
        current_precision += 1
      else:
        next_ratio -= (0.1)**current_precision
    if reverse:
      r = 1.0/r
    nodes = numpy.empty(n, dtype=numpy.float64)
    nodes[0] = self.start
    nodes[1:] = r
    return numpy.cumprod(nodes), r

  def generate_yaml_info(self):
    info = {}
    info['end'] = self.end
    info['cells'] = self.nb_divisions
    info['stretchRatio'] = self.stretch_ratio
    return info


class GridLine(object):
  def __init__(self, data):
    self.label = data['direction']
    self.start = data['start']
    self.end = data['subDomains'][-1]['end']
    self.segments = []
    for index, node in enumerate(data['subDomains']):
      if index == 0:
        start = self.start
      else:
        start = data['subDomains'][index-1]['end']
      end = node['end']
      if 'reverse' not in node.keys():
        data['subDomains'][index]['reverse'] = False
      if 'precision' not in node.keys():
        data['subDomains'][index]['precision'] = 2
      if 'aspectRatio' not in node.keys():
        data['subDomains'][index]['aspectRatio'] = 1.0
      self.segments.append(Segment(start, end, 
                                   width=node['width'], 
                                   aspect_ratio=node['aspectRatio'],
                                   precision=node['precision'],
                                   reverse=node['reverse']))
    self.nb_divisions = sum(segment.nb_divisions for segment in self.segments)

  def get_nodes(self):
    return numpy.concatenate(([segment.nodes for segment in self.segments]))

  def generate_yaml_info(self):
    info = {}
    info['direction'] = self.label
    info['start'] = self.start
    info['subDomains'] = []
    for segment in self.segments:
      info['subDomains'].append(segment.generate_yaml_info())
    return info


class StructuredCartesianMesh(object):
  """Contains info related to the stretched grid."""
  def __init__(self):
    self.gridlines = []

  def generate(self, data):
    print('[info] generating Cartesian grid ...')
    for node in data:
      self.gridlines.append(GridLine(node))

  def write(self, file_path):
    print('[info] writing grid nodes into {} ...'.format(file_path))
    nb_divisions, nodes_list = [], []
    for gridline in self.gridlines:
      nb_divisions.append(gridline.nb_divisions)
      nodes_list.append(gridline.get_nodes())
    with open(file_path, 'w') as outfile:
      outfile.write('{}\n'.format('\t'.join(str(line.nb_divisions) for line 
                                                                   in self.gridlines)))
      for nodes in nodes_list:
        numpy.savetxt(outfile, nodes)

  def read_yaml_file(self, file_path):
    print('[info] reading grid parameters from {} ...'.format(file_path))
    with open(file_path, 'r') as infile:
      return yaml.load(infile)

  def write_yaml_file(self, file_path):
    print('[info] writing grid parameters into {} ...'.format(file_path))
    data = []
    for gridline in self.gridlines:
      data.append(gridline.generate_yaml_info())
    with open(file_path, 'w') as outfile:
      outfile.write(yaml.dump(data, default_flow_style=False))