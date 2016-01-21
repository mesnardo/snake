# file: copy_missing_files.py
# author: Olivier Mesnard (mesnardo@gwu.edu)
# brief: Copies missing file.

import sys
import os
import shutil

def copy_missing_file(missing_file):
	print('missing file: {}'.format(missing_file))
	folder = os.path.dirname(missing_file)
	boost_source = '{}/src/boost/1.57.0'.format(os.environ['HOME'])
	boost_destination = '{}/tmp/petibm/PetIBM/external/boost-1.57.0'.format(os.environ['HOME'])
	try:
		os.makedirs('{}/{}'.format(boost_destination, folder))
	except:
		pass
	shutil.copy('{}/{}'.format(boost_source, missing_file), 
				'{}/{}'.format(boost_destination, folder))
	return


def main(args):
	missing_file = 'tmp'
	while(missing_file != None):
		missing_file = None
		os.system('make 2> make.log')
		with open('make.log', 'r') as infile:
			for line in infile:
				if 'fatal error:' in line:
					missing_file = line.split()[-6][:-1]
					break
		if missing_file != None:
			copy_missing_file(missing_file)
	return


if __name__ == '__main__':
	main(sys.argv)
