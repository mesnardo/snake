import numpy as np
from matplotlib.pyplot import *

CFL = []
inFile =  open('./log_0_20','r')
for line in inFile:
	if ('Courant Number mean' in str(line)):
		field = line.split()
		CFL.append(float(field[len(field)-1]))
inFile.close()

inFile = open('./log_20_30','r')
for line in inFile:
	if ('Courant Number mean' in str(line)):
		field = line.split()
		CFL.append(float(field[len(field)-1]))
inFile.close()

inFile = open('./log_30_40','r')
for line in inFile:
	if ('Courant Number mean' in str(line)):
		field = line.split()
		CFL.append(float(field[len(field)-1]))
inFile.close()

figure(0)
grid(True)
plot(CFL,linewidth=2)
show()
