# file:setup.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Setup.


import sys
from setuptools import setup


def main():
  if sys.version_info[0] != 2:
    sys.exit('Only supports Python 2.7')

  setup(name='snake',
        version='0.1',
        description=('Personal collection of Python scripts '
                     'to post-process the snake reproducibility case-study'),
        platforms='Unix',
        license='MIT',
        author='Olivier Mesnard',
        author_email='mesnardo@gwu.edu')


if __name__ == '__main__':
  main()