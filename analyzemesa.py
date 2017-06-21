#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
from collections import OrderedDict
from MesaProfile import MesaProfile
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("dataset", type=str, help="Name of the input dataset.")
parser.add_argument("-o", "--output", type=str, help="Name of the output dataset file to write.")
args = parser.parse_args()

# Set output file name if not supplied
if args.output:
        outputfile = args.output
else:
        outputfile = 'mapped_' + args.dataset

# Set constant centimeters per solar radius
cmperRsun = 6.955e10

# Read the input MESA profile
mesa = MesaProfile()
mesa.setInProfileName(args.dataset)
mesa.readProfile()
mstar = mesa.getStar()

# Create a field for radius in cm instead of Rsun units
mstar['radiuscm'] = cmperRsun*mstar['radius']

print('Mass: ' + str(mstar['mass'][-1]))

# Generate some plots with matplotlib
## Abundances
plt.figure(1)
fig = plt.gcf()
ax1 = fig.add_axes([0.1,0.1,0.8,0.8])
mstar['Xother'] = 1.0 - mstar['c12'] - mstar['o16'] - mstar['ne20'] - mstar['ne22'] - mstar['na23'] - mstar['mg24']
c12,o16,ne20,ne22,na23,mg24,Xother = ax1.plot(mstar['mass'],mstar['c12'],'b',
		mstar['mass'],mstar['o16'],'g',
		mstar['mass'],mstar['ne20'],'r',
		mstar['mass'],mstar['ne22'],'Cyan',
		mstar['mass'],mstar['na23'],'Violet',
		mstar['mass'],mstar['mg24'],'GoldenRod',
		mstar['mass'],mstar['Xother'],'Black'
		)
fig.legend((c12,o16,ne20,ne22,na23,mg24,Xother),('$^{12}C$','$^{16}O$','$^{20}Ne$','$^{22}Ne$','$^{23}Na$','$^{24}Mg$','Other'),'right') 
plt.xlabel('Mass ($M_\\odot$)')
plt.ylabel('Mass Fractions')
plt.title('Selected MESA Model Abundances')

## Density Profile
plt.figure(2)
fig = plt.gcf()
ax1 = fig.add_axes([0.1,0.1,0.8,0.8])
Rhoplot = ax1.plot(mstar['radiuscm'],10.0**mstar['logRho'],'b')
plt.xlabel('Radius (cm)')
plt.ylabel('Density ($g/cm^3$)')
#plt.xlim([0,5e7])
#plt.ylim([0.6e9,2.0e9])
plt.title('Central Density Profile')

## Zone radius separation (dr) distribution
dr = np.array([mstar['radiuscm'][i+1]-mstar['radiuscm'][i] for i in range(0,len(mstar['radiuscm'])-1)])
mindr = min(dr)

print('Minimum Radius Separation: ' + str(mindr))

plt.figure(3)
fig = plt.gcf()
ax1 = fig.add_axes([0.1,0.1,0.8,0.8])
ax1.plot(mstar['radiuscm'][0:-1],dr,'b')
plt.xlabel('Radius')
plt.ylabel('Radius Separation dr')
plt.title('Radius Separation vs. Radius')

plt.figure(4)
fig = plt.gcf()
ax1 = fig.add_axes([0.1,0.1,0.8,0.8])
ax1.hist(dr,10000)
plt.xlabel('Radius Separation dr')
plt.title('Histogram of Radius Separation')

## Show all plots
plt.show()

# Map abundances to set of C12, O16, Ne20, Ne22 for flash!
fmap = {'c12':np.array([]),'o16':np.array([]),'ne20':np.array([]),'ne22':np.array([])}
## Maintain constant C12 abundance
fmap['c12'] = mstar['c12']
## Determine Ne22 abundance from model Ye
fmap['ne22'] = 22.0*(0.5-mstar['ye'])
## Normalization requires Ne20 + O16 abundances = xother
xother = 1.0 - fmap['c12'] - fmap['ne22']
## Ne20/O16 ratio remains constant
rneo = mstar['ne20']/mstar['o16']
## Use rneo and xother constraints to find Ne20 and O16 abundances
fmap['o16'] = xother/(rneo+1.0)
fmap['ne20'] = rneo*xother/(rneo+1.0)

# Write new abundances to output file (one line per zone)
## Note we assume normalization so o16 makes up the difference!
## Note mesa's radius units are Rsun so I convert to cm for output
## Format is:
## l.1: # radius         dens           temp        c12          ne20          ne22
## l.2: [Number of lines to follow]
## l.3: data according to header
fout = open(outputfile,'w')
fout.write('# radius         dens           pres           temp        c12          ne20          ne22\n')
numpts = len(fmap['c12']) # Can use something else if, e.g. you mass-average
fout.write(str(numpts) + '\n')

def esf(x):
	return '{0:0.15e}'.format(x)

for i in range(0,numpts):
	fout.write(esf(mstar['radiuscm'][i]) + '  ' +
			esf(10.0**mstar['logRho'][i]) + '  ' + 
			esf(mstar['pressure'][i]) + '  ' + 
			esf(mstar['temperature'][i]) + '  ' +
			esf(fmap['c12'][i]) + '  ' +
			esf(fmap['ne20'][i]) + '  ' +
			esf(fmap['ne22'][i]) + '\n')

# All done, save file!
fout.close()
