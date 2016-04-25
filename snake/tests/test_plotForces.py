# file: test_plotForces.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# description: Tests the script `plotForces.py` with different options files.


import os


def main():
  script = '{}/scripts/plotForces.py'.format(os.environ['SCRIPTS'])
  directory = '{}/tests/scriptsOptions'.format(os.environ['SCRIPTS'])
  file_paths = [os.path.join(directory, f) for f in os.listdir(directory) 
                if os.path.isfile(os.path.join(directory, f))]

  for path in file_paths:
    print('\n{0} TEST: {1} {0}\n'.format(10*'#', os.path.basename(path)))
    os.system('python {} --options {}'.format(script, path))

if __name__ == '__main__':
  print('\n[{}] START\n'.format(os.path.basename(__file__)))
  main()
  print('\n[{}] END\n'.format(os.path.basename(__file__)))