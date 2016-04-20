try:
  from pkg_resources import get_distribution

  __version__ = get_distribution('snake').version
except:
  pass