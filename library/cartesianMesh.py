# file: cartesianMesh.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Implementation of the class StructuredCartesianMesh and its sub-classes.


import os
import math
import numpy
import yaml
from operator import mul
from decimal import Decimal


class Segment(object):
  def __init__(self, start, end, width, 
               stretch_ratio=1.0, aspect_ratio=1.0, precision=6, reverse=False):
    self.start, self.end = start, end
    self.width = width
    self.create_nodes(stretch_ratio=stretch_ratio, aspect_ratio=aspect_ratio,
                      precision=precision, reverse=reverse)
    self.nb_divisions = self.nodes.size-1
    print('[info] start={} \t actual={}'.format(self.start, self.nodes[0]))
    print('[info] end={} \t actual={}'.format(self.end, self.nodes[-1]))

  def create_nodes(self, 
                   stretch_ratio=1.0, aspect_ratio=1.0, 
                   precision=6, reverse=False):
    if abs(stretch_ratio-1.0) > 1.0E-06:
      self.stretch_ratio, self.nodes = self.get_optimal_stretched_array(
                                                            stretch_ratio, 
                                                            precision=precision, 
                                                            reverse=reverse)
    elif abs(aspect_ratio-1.0) > 1.0E-06:
      stretch_ratio= self.compute_stretch_ratio(aspect_ratio,
                                                precision=precision)
      self.stretch_ratio, self.nodes = self.get_optimal_stretched_array(
                                                            stretch_ratio, 
                                                            precision=precision, 
                                                            reverse=reverse)
    else:
      self.stretch_ratio = 1.0
      self.nodes = numpy.arange(self.start, self.end+self.width/2.0, self.width, 
                        dtype=numpy.float64)

  def compute_stretch_ratio(self, aspect_ratio, 
                            precision=6):
    length = abs(self.end-self.start)
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
    return r

  def compute_stretch_ratio(self, stretch_ratio=1.0, aspect_ratio=1.0, 
                            precision=6):
    length = abs(self.end-self.start)
    width = self.width
    candidate_ratio = stretch_ratio
    precision_ratio = abs(Decimal(str(candidate_ratio)).as_tuple().exponent)
    while precision_ratio <= precision:
      ratio = candidate_ratio
      n = int(round(math.log(1.0-(1.0-ratio)*length/width)/math.log(ratio)))
      candidate_length = width*(1.0-ratio**n)/(1.0-ratio)
      candidate_aspect_ratio = ratio**(n-1)
      if abs(aspect_ratio-1.0) < 1.0E-06 and candidate_aspect_ratio < aspect_ratio:
        candidate_ratio += (0.1)**precision_ratio
        precision_ratio += 1
      elif candidate_length < length:
        candidate_ratio += (0.1)**precision_ratio
        precision_ratio += 1
      else:
        candidate_ratio -= (0.1)**precision_ratio
    return candidate_ratio


  def get_geometric_progression(self, n, start, ratio):
    array = numpy.empty(n, dtype=numpy.float64)
    array[0], array[1:] = start, ratio
    return numpy.cumprod(array)

  def to_name(self, ratio):
    length = abs(self.end-self.start)
    width = self.width
    n_float = math.log(1.0-(1.0-ratio)*length/width)/math.log(r)
    n = int(round(n_float))
    length_inf = width*(1.0-r**n)/(1.0-r)
    length_sup = width*(1.0-r**(n+1))/(1.0-r)



    if abs(length-length_inf) < abs(length-length_sup):
      ratio += 0.1**precision_ratio


  def get_optimal_stretched_array(self, stretch_ratio, precision=6, reverse=False):
    print('[info] computing optimal stretched array ...')
    length = abs(self.end-self.start)
    precision_ratio = abs(Decimal(str(stretch_ratio)).as_tuple().exponent)
    candidate_ratio = stretch_ratio if abs(stretch_ratio-1.0)
    while precision_ratio <= precision:
      ratio = candidate_ratio
      widths = [0.0, self.width]
      while sum(widths) < length:
        widths.append(ratio*widths[-1])
      n = len(widths)-1
      diff = length - self.width*(1.0-ratio**n)/(1.0-ratio)
      print(n, diff)
      if abs(sum(widths)-length) < abs(sum(widths[:-1])-length):
        precision_ratio += 1
        candidate_ratio -= (0.1)**precision_ratio
      else:
        candidate_ratio += (0.1)**precision_ratio
    print('[info] stretching ratio:')
    print('\ttarget: {}'.format(stretch_ratio))
    print('\toptimal: {}'.format(ratio))
    if not reverse:
      return ratio, self.start+numpy.cumsum(widths, dtype=numpy.float64)
    else:
      return 1.0/ratio, (self.end-numpy.cumsum(widths, dtype=numpy.float64))[::-1]

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
        data['subDomains'][index]['precision'] = 6
      if 'aspectRatio' not in node.keys():
        data['subDomains'][index]['aspectRatio'] = 1.0
      if 'stretchRatio' not in node.keys():
        data['subDomains'][index]['stretchRatio'] = 1.0
      self.segments.append(Segment(start, end, 
                                   width=node['width'], 
                                   stretch_ratio=node['stretchRatio'],
                                   aspect_ratio=node['aspectRatio'],
                                   precision=node['precision'],
                                   reverse=node['reverse']))
    self.nb_divisions = sum(segment.nb_divisions for segment in self.segments)

  def get_nodes(self, precision=6):
    return numpy.unique(numpy.concatenate(([numpy.round(segment.nodes, precision) 
                                            for segment in self.segments])))


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

  def get_number_cells(self):
    nb_divisions = []
    for gridline in self.gridlines:
      nb_divisions.append(gridline.nb_divisions)
    return reduce(mul, nb_divisions, 1), nb_divisions

  def generate(self, data):
    print('[info] generating Cartesian grid ...')
    for node in data:
      self.gridlines.append(GridLine(node))

  def write_gridlines(self, file_path, precision=6):
    print('[info] writing grid nodes into {} ...'.format(file_path))
    _, nb_cells_directions = self.get_number_cells()
    with open(file_path, 'w') as outfile:
      outfile.write('\t'.join(str(nb) for nb in nb_cells_directions)+'\n')
      for gridline in self.gridlines:
        numpy.savetxt(outfile, gridline.get_nodes(precision=6))

  def read_yaml_file(self, file_path):
    print('[info] reading grid parameters from {} ...'.format(file_path))
    with open(file_path, 'r') as infile:
      return yaml.load(infile)

  def write_yaml_file(self, file_path):
    print('[info] writing grid parameters into {} ...'.format(file_path))
    data = []
    for gridline in self.gridlines:
      data.append(gridline.generate_yaml_info())
    nb_cells, nb_cells_directions = self.get_number_cells()
    with open(file_path, 'w') as outfile:
      outfile.write('# {}\n'.format(os.path.basename(file_path)))
      outfile.write('# {} = {}\n\n'.format('x'.join(str(nb) for nb in nb_cells_directions), 
                                         nb_cells))
      outfile.write(yaml.dump(data, default_flow_style=False))

  def plot_gridlines(self):
    from matplotlib import pyplot
    pyplot.style.use('{}/styles/mesnardo.mplstyle'.format(os.environ['SCRIPTS']))
    pyplot.grid()
    for index, gridline in enumerate(self.gridlines):
      nodes = gridline.get_nodes()
      widths = nodes[1:]-nodes[:-1]
      stations = 0.5*(nodes[:-1]+nodes[1:])
      print nodes.size
      pyplot.scatter(gridline.get_nodes(), index*numpy.ones(gridline.nb_divisions+1))
      pyplot.plot(stations, widths)
    pyplot.show()