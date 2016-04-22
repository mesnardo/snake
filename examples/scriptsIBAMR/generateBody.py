# file: generateBody.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Generates the body file.


import os

from snake.geometry import Geometry


body = Geometry(file_path='{}/resources/geometries/flyingSnake2d/'
                          'flyingSnake2dAoA35.dat'.format(os.environ['SNAKE']))
body.keep_inside(ds=0.004)
body.write(file_path='flyingSnake2dAoA35ds004filledInside.vertex')