"""
Import a MESA profile file and place it on a uniform grid by mass-weighted
averaging regions of the MESA profile where the grid is denser than the 
uniform grid and interpolating in regions where the MESA grid is more widely
spaced than the uniform grid.

Parameters controlling the program...
Dr: uniform grid spacing
cubic, quad, linear: only one of these can be True, they set interpolation type.
gridFileName: name of the uniform grid profile to write out
mesaInProfileName: name of the MESA profile to read

Author: Donald E. Willcox
Last Modified: May 2, 2015

Copyright 2015 Donald E. Willcox

This file is part of mesa2flash.

mesa2flash is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

mesa2flash is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with mesa2flash.  If not, see <http://www.gnu.org/licenses/>.
"""
from mpi4py import MPI
import numpy as np
import math
import argparse
from collections import OrderedDict
from MesaProfile import MesaProfile
from MapMesaComposition import MapMesaComposition
from Nuclides import Nuclides

parser = argparse.ArgumentParser()
parser.add_argument('MESA_INPUT_FILE', type=str, help='Name of the input MESA profile.')
parser.add_argument('-o', '--output', type=str, help='Name of the output file to write.')
parser.add_argument('-drcm', '--delta_radius_cm', type=float, help='Step size to use in radius in units of cm.')
parser.add_argument('-ip', '--interpolation', type=int, help='Interpolation type to use. 1 = Linear, 2 = Quadratic, 3 = Cubic. Cubic can suffer from continuity issues, so be careful. I recommend quadratic. This will not enforce HSE, you need WDBuilder to post-process the output this program creates in order to obtain HSE.')
parser.add_argument('-mfx', '--map_abundances_flash', action='store_true', help='Map the MESA abundances to FLASH reduced composition: C12, O16, Ne20, Ne22.')
args = parser.parse_args()

# Global MPI information
mpi_comm = MPI.COMM_WORLD
mpi_size = mpi_comm.Get_size()
mpi_rank = mpi_comm.Get_rank()

cmperRsun = 6.955e10

### Import MESA Profile & Broadcast to all Processes ###
if (mpi_rank == 0):
    mesa = MesaProfile()
    mesaInProfileName = args.MESA_INPUT_FILE
    mesa.setInProfileName(mesaInProfileName)
    mesa.readProfile()
    mstar = mesa.getStar()
else:
    mstar = None

######
### Specify Output Parameters ###
# Specify uniform grid file to write
gridFileName = args.output
# Specify separation between radius points in the uniform grid
Dr = args.delta_radius_cm # units are in cm! (1.0e5 = 1km)
# Specify the interpolation type (only ONE of cubic, quad, or linear may be True)
cubic = False
quad = False
linear = False

if args.interpolation == 1:
  linear = True
elif args.interpolation == 2:
  quad = True
elif args.interpolation == 3:
  cubic = True
else: 
  print 'ERROR: YOU MUST SPECIFY AN INTERPOLATION TYPE VIA THE -ip OPTION.'

# Set variables determining the interpolation order
## poly_n: polynomial order
if (cubic and not quad and not linear):
    poly_n = 3
elif (not cubic and quad and not linear):
    poly_n = 2
elif (not cubic and not quad and linear):
    poly_n = 1
else:
    print 'ERROR: no unique interpolation scheme chosen'
    sys.exit()

######
if (mpi_rank == 0):
    ### Map MESA Abundances to FLASH Composition ###
    if args.map_abundances_flash:
        mapper = MapMesaComposition()
        fcomp = mapper.getmap(mstar)
        for k in fcomp.keys():
            mstar[k] = fcomp[k]
        vars = OrderedDict([('density',0),('temperature',1),('c12',2),('o16',3),('ne20',4),('ne22',5)])
        varx = OrderedDict([('c12',2),('o16',3),('ne20',4),('ne22',5)])
    else:
        nucs = Nuclides()
        vars_list = [('density',0),('temperature',1),('ye',2)]
        start_varx = len(vars_list)
        varx_list = []
        for k in mstar.keys():
            if nucs.is_nuclide(k):
                varx_list.append((k,start_varx))
                start_varx += 1
        vars_list += varx_list
        varx = OrderedDict(varx_list)
        vars = OrderedDict(vars_list)
        
    ### Create useful data structures ###
    # Number of MESA zones
    npts = len(mstar['zone'])
    
    # Create a field for radius in cm instead of Rsun units
    mstar['radiuscm'] = cmperRsun*mstar['radius']
    # From looking at the MESA source and particularly star/defaults/profile_columns.list and star/public/star_data.inc Q&A section,
    # it is apparent that 'radius' is the outer cell boundary at each zone and 'rmid' is the volume-centered radius of the cell.
    # NOTE: here I assume that the MESA parameter R_center, the radius of the outer edge of the core, is 0
    # R_center is the inner radius of the innermost MESA zone.
    # Create a field for inner zone radii
    mstar['rcminner'] = np.array([0.0 for i in range(npts)])
    mstar['rcminner'][0] = 0.0
    mstar['rcminner'][1:npts] = np.array([mstar['radiuscm'][i-1] for i in range(1,npts)])
    mstar['rad_cm_ctr'] = (0.5*(mstar['radiuscm']**3 + mstar['rcminner']**3))**(1.0/3.0)    

    mstar['density'] = 10.0**mstar['logRho']
    
    #mstar['volume'] is the volume per zone in cm^3.
    #mstar['volume'] = ((4.0*np.pi/3.0)*(mstar['radiuscm']**2 + 2.0*mstar['radiuscm']*mstar['rcminner'] + mstar['rcminner']**2)*
    #                                    (mstar['radiuscm']-mstar['rcminner']))
    mstar['volume'] = ((4.0*np.pi/3.0)*(mstar['radiuscm']**2 + mstar['radiuscm']*mstar['rcminner'] + mstar['rcminner']**2)*
                                        (mstar['radiuscm']-mstar['rcminner']))
else:
    npts = None
    vars = None
    varx = None

# Pass data from root to processes
npts = mpi_comm.bcast(npts,root=0)    
vars = mpi_comm.bcast(vars,root=0)
varx = mpi_comm.bcast(varx,root=0)
mstar = mpi_comm.bcast(mstar,root=0)

# make the uniform grid data structure
ugrid = OrderedDict([])

r_int_cont = [] # For index i, contains a list of indices in rad_m which
		# fall into the interval corresponding to gridData[rad_indx,i].
		# If the interval associated with gridData[rad_indx,i] is empty		
                # then r_int_cont[i] will be an empty list.
r_int_empty = [] # Is a list of indices i for which r_int_cont[i] is empty
r_int_empty_zones = [] # For each entry in r_int_empty, record the mesa zone you're in
######
### Make a Uniform Grid, Figure Out MESA zone geometry and grid overlaps ###

if(mpi_rank == 0):
    # Find how big to make the uniform grid
    ngridpts = (int(math.floor((mstar['radiuscm'][-1] - mstar['rcminner'][0])/Dr))+1)
    
    print 'last modeldata radius: ' + str(mstar['radiuscm'][-1])
    ugrid_to_scatter = OrderedDict([]) 
    # Construct the uniform grid radius points
    ugrid_to_scatter['rad_cm_ctr'] = np.array([0.0 for i in range(ngridpts)])
    ugrid_to_scatter['rad_cm_inn'] = np.array([0.0 for i in range(ngridpts)])
    ugrid_to_scatter['rad_cm_out'] = np.array([0.0 for i in range(ngridpts)])
    ugrid_to_scatter['rad_cm_inn'][0] = mstar['rcminner'][0]
    ugrid_to_scatter['rad_cm_ctr'][0] = ugrid_to_scatter['rad_cm_inn'][0] + Dr/2
    ugrid_to_scatter['rad_cm_out'][0] = ugrid_to_scatter['rad_cm_inn'][0] + Dr
    for i in range(1,ngridpts):
        ugrid_to_scatter['rad_cm_inn'][i] = ugrid_to_scatter['rad_cm_inn'][i-1] + Dr
        ugrid_to_scatter['rad_cm_ctr'][i] = ugrid_to_scatter['rad_cm_ctr'][i-1] + Dr
        ugrid_to_scatter['rad_cm_out'][i] = ugrid_to_scatter['rad_cm_out'][i-1] + Dr    
    
    print 'last griddata radius: ' + str(ugrid_to_scatter['rad_cm_out'][-1])
    for k in vars.keys():
        ugrid_to_scatter[k] = np.array([0.0 for i in range(ngridpts)])
    
    ugkeys = ugrid_to_scatter.keys()

else:
    ngridpts = None
    ugkeys = None    

ugkeys = mpi_comm.bcast(ugkeys,root=0)

# Rearrange ugrid data to prepare for scatter
if (mpi_rank == 0):
    elements_rank = [int(math.floor(ngridpts/mpi_size)) for i in range(mpi_size)]
    elements_rank[-1] = elements_rank[-1] + (ngridpts-sum(elements_rank))
    start_rank = [sum(elements_rank[0:i]) for i in range(mpi_size)]
    start_rank[0] = 0
else:
    ugrid_to_scatter = None
    elements_rank = None
    ugrid = OrderedDict([])

elements_rank = mpi_comm.bcast(elements_rank,root=0)

for k in ugkeys:
    ugrid[k] = np.empty(elements_rank[mpi_rank],dtype=np.float64)

if (mpi_rank == 0):
    for k in ugkeys:
        ugrid[k] = [ugrid_to_scatter[k][start_rank[i]:start_rank[i]+elements_rank[i]] for i in range(mpi_size)]

for k in ugkeys:
    ugrid[k] = mpi_comm.scatter(ugrid[k],root=0)

#!don: find out if the scatter worked properly, yes it seems to have worked
print 'Rank: ' + str(mpi_rank) + ' ugrid is... ' + str(ugrid) + ' length: ' + str(len(ugrid['rad_cm_inn']))
print 'Rank: ' + str(mpi_rank) + ' elements_rank is... ' + str(elements_rank)

ngridpts_rank = len(ugrid[ugkeys[0]])
    
# Find which model points fall into which uniform grid intervals & vice-versa
print 'Rank: ' + str(mpi_rank) + ' starting to find overlaps.'
for i in range(0,ngridpts_rank):
	rint_cont = []	
        j_contains = []
	for j in range(0,npts):
		if((mstar['rcminner'][j] >= ugrid['rad_cm_inn'][i]) and 
                    (mstar['radiuscm'][j] <= ugrid['rad_cm_out'][i])):
			rint_cont.append(j)
                if((mstar['rcminner'][j] < ugrid['rad_cm_inn'][i] and mstar['radiuscm'][j] > ugrid['rad_cm_inn'][i])
                    or (mstar['radiuscm'][j] > ugrid['rad_cm_out'][i] and mstar['rcminner'][j] < ugrid['rad_cm_out'][i])):
                    j_contains.append(j) 
	r_int_cont.append(rint_cont)
        if len(rint_cont) == 0:
            r_int_empty.append(i)
            r_int_empty_zones.append(j_contains)
print 'Rank: ' + str(mpi_rank) + ' completed finding overlaps.'

######

print 'Rank: ' + str(mpi_rank) + ' beginning mass-averaging.'
# Compute the mass-averaged quantities for each non-empty uniform grid interval !Parallelize!
for i in range(0,ngridpts_rank):
	if(len(r_int_cont[i]) != 0):
	        # Interval [ugrid['rad_cm_inn'][i],ugrid['rad_cm_out'][i]]
		# Compute edge contributions

		## Set Left Edge Data, 0 if there is a model point at ri (i=0)
		leftData = np.array([0.0 for v in vars.keys()])
		k = r_int_cont[i][0]
                leftVol = 0.0
                leftMass = 0.0
		## If we aren't at the first point and no model point at r ...
		if((i!=0 or mpi_rank!=0) and ugrid['rad_cm_inn'][i]!=mstar['rcminner'][k]):
                    leftData = np.array([mstar[v][k-1] for v in vars.keys()])
                    ri = ugrid['rad_cm_inn'][i]
                    ro = mstar['radiuscm'][k-1]
                    leftVol = (ri**2 + ri*ro + ro**2)*(ro-ri)
                    leftMass = mstar['density'][k-1]*leftVol
                    for vark,varv in vars.iteritems():
                        if vark != 'density':
                            leftData[varv] = leftData[varv]*leftMass # divide and multiply by total left Mass
                    leftData[vars['density']] = (leftMass**2)/leftVol
                            
		## Set Right Edge Data
		### 0 for the quantities if we are at the last grid interval
		rightData = np.array([0.0 for v in vars.keys()])
                rightVol = 0.0
                rightMass = 0.0
		# ki: index to the model point just beyond the last in this grid interval
		ro = ugrid['rad_cm_out'][i]
		ki = r_int_cont[i][-1]+1
		if (ki!=npts):
                    ri = mstar['rcminner'][ki]
                    if (ri < ro): 
                        rightData = np.array([mstar[v][ki] for v in vars.keys()])
                        rightVol = (ro**2 + ro*ri + ri**2)*(ro-ri)
                        rightMass = mstar['density'][ki]*rightVol
                        for vark,varv in vars.iteritems():
                            if vark != 'density':
                                rightData[varv] = rightData[varv]*rightMass 
                        rightData[vars['density']] = (rightMass**2)/rightVol

		## Perform the averaging to fill the uniform grid
		### Get partial sum over the MESA zones fully inside the uniform grid interval
		intervalData = np.array([0.0 for v in vars.keys()])
                intervalMass = 0.0
                intervalVol = 0.0
		for k in r_int_cont[i][0:-1]:
                    ri = mstar['rcminner'][k]
                    ro = mstar['radiuscm'][k]
                    kVol = (ro**2 + ro*ri + ri**2)*(ro-ri)
                    kMass = mstar['density'][k]*kVol
                    intervalVol = intervalVol + kVol
                    intervalMass = intervalMass + kMass
                    kData = np.array([mstar[v][k] for v in vars.keys()])
                    intervalData = intervalData + kMass*kData
		sumData = intervalData+leftData+rightData 
		sumMass = leftMass + rightMass + intervalMass
                sumVol = leftVol + rightVol + intervalVol 
                for vark,varv in vars.iteritems():
                    if vark != 'density':
                        ugrid[vark][i] = sumData[varv]/sumMass
                ugrid['density'][i] = sumMass/sumVol
                if (i==0):
                    print 'Rank: ' + str(mpi_rank) + ', r_int_cont[0]: ' + str(r_int_cont[i]) + ', leftMass: ' + str(leftMass) + ', rightMass: ' + str(rightMass) + ', intervalMass: ' + str(intervalMass)
                # Some print statements possibly useful diagnostically
#                print 'r_int_cont[i]: ' + str(r_int_cont[i])
#                print 'leftMass: ' + str(leftMass)
#                print 'rightMass: ' + str(rightMass)
#                print 'intervalMass: ' + str(intervalMass)
#                print 'leftVol: ' + str(leftVol)
#                print 'rightVol: ' + str(rightVol)
#                print 'intervalVol: ' +  str(intervalVol)
print 'Rank: ' + str(mpi_rank) + ' completed mass-averaging.'        
                
# Mass-averaged quantities for all non-empty grid intervals have been computed.
# Now interpolate between grid intervals to compute quantities for the empty 
# grid intervals.
prevkB = 0
prevkC = 0
coef_t = np.array([0.0,0.0,0.0,0.0]) # coefficients for poly interp up to 3rd order
coeffs = OrderedDict([(k,coef_t) for k in vars.keys()])

def dinject(u,m):
    # u: index of cell in ugrid to inject into
    # m: index of cell in mstar to inject from
    global ugrid
    global mstar
    global vars
    for vark in vars.keys():
        ugrid[vark][u] = mstar[vark][m]

print 'Rank: ' + str(mpi_rank) + ' beginning interpolation.'
for i in range(len(r_int_empty)): # !Parallelize!
# The quantities in the empty grid intervals are set by quadratic interpolation
# depending only on the quantities in the previous and next non-empty intervals
# Once an empty grid interval's values are computed, it is not used for 
# further interpolation if, e.g., there are several consecutive empty intervals
# Neither the first nor the last grid intervals should be empty so we
# don't have to worry about them here.

        if (r_int_empty[i] == 0 or r_int_empty[i] == ngridpts_rank-1):
            print 'Rank: ' + str(mpi_rank) + ', r_int_empty: ' + str(r_int_empty[i]) + ', r_int_empty_zones: ' + str(r_int_empty_zones[i]) + ', rad_cm_ctr[i]: ' + str(ugrid['rad_cm_ctr'][r_int_empty[i]])

        nz = len(r_int_empty_zones[i])
        if nz==2:
            kB = r_int_empty_zones[i][0]
            kC = r_int_empty_zones[i][1]
        elif nz==1:
            j = r_int_empty[i]
            k = r_int_empty_zones[i][0]
            if ((k==npts-1) or (k!=0 and (ugrid['rad_cm_ctr'][j] < mstar['rad_cm_ctr'][k]))):
                kB = k-1
                kC = k
            elif (k==0 or (ugrid['rad_cm_ctr'][j] > mstar['rad_cm_ctr'][k])):
                kB = k
                kC = k+1
            else:
                # Do direct injection if the grid and mstar cell centers exactly line up
                dinject(j,k)
                continue
        else:
            print 'ERROR: nz neither 2 nor 1, nz=' + str(nz)
            sys.exit()

       # print 'kB: ' + str(kB)
       # print 'kC: ' + str(kC)
       # print 'nz: ' + str(nz)
       # print 'r_int_empty[' + str(i) + ']: ' + str(r_int_empty[i])
       # print 'r_int_empty_zones[' + str(i) + ']: ' + str(r_int_empty_zones[i])

        ## Do interpolation if you can't reuse the previous coefficients
        if ((kB != prevkB or kC != prevkC)):
#            print 'kB: ' + str(kB)
#            print 'kC: ' + str(kC)
            # Find quadratic coefficients for all variables via least-squares fitting
            # using two model points on either side if they exist, otherwise shift to an extra left or right
            if cubic:
                klist = [kB-1,kB,kC,kC+1]
                if(kB == 0):
                    klist = [kB,kC,kC+1,kC+2]
                elif(kC == npts-1):
                    klist = [kB-2,kB-1,kB,kC]
            elif quad:
                klist = [kB-1,kB,kC]
                if(kB == 0):
                    klist = [kB,kC,kC+1]
            elif linear:
                klist = [kB,kC]
#            print 'klist: ' + str(klist)
            rpows = np.array([[(mstar['rad_cm_ctr'][ki])**n for ki in klist] for n in range(0,2*poly_n+1)])
            rmat = np.array([[sum(rpows[j]) for j in range(k+poly_n,k-1,-1)] for k in range(poly_n,-1,-1)])
            for vark in vars.keys():
                #Solve an equation of the form rmat*coeffs=fmat
                fvec = np.array([mstar[vark][ki] for ki in klist])
                fmat = np.array([np.dot(fvec,rpows[j]) for j in range(poly_n,-1,-1)])
                coeffs[vark] = np.linalg.solve(rmat,fmat)  

        rgrid = ugrid['rad_cm_ctr'][r_int_empty[i]]
        for vark in vars.keys():
            ugrid[vark][r_int_empty[i]] = sum([coeffs[vark][-(j+1)]*(rgrid**j) for j in range(poly_n,-1,-1)])
           
    ## Following is a test case for the linear interpolation above 
       # if(linear):
       #     kB = r_int_cont[kB][-1]
       #     kC = r_int_cont[kC][0]
       #     rB = mstar['rad_cm_ctr'][kB]
       #     rC = mstar['rad_cm_ctr'][kC]
       #     rgrid = ugrid['rad_cm_ctr'][r_int_empty[i]]
       #     for vark in vars.keys():
       #         ugrid[vark][r_int_empty[i]] = mstar[vark][kB] + (mstar[vark][kC]-mstar[vark][kB])*(rgrid-rB)/(rC-rB)

        prevkB = kB
        prevkC = kC
print 'Rank: ' + str(mpi_rank) + ' completed interpolation.'

## Now renormalize all abundances (in case mass-averaging and quadratic interpolation broke normalization)
for i in range(0,ngridpts_rank):
    sumx = 0.0
    for x in varx.keys():
        sumx = sumx + ugrid[x][i]
    for x in varx.keys():
        ugrid[x][i] = ugrid[x][i]/sumx

def esf(x):
        return '{0:0.15e}'.format(x)

# Bring parallel data back to main
if (mpi_rank == 0):
    print 'Gathering ugrid data.'
for k in ugkeys:
    ugrid[k] = mpi_comm.gather(ugrid[k],root=0)

if (mpi_rank == 0):
    # Convert ugrid to ugrid_from_gather
    #ugrid_from_gather = OrderedDict([])
    #for k in ugkeys:
    #    ugrid_from_gather[k] = np.empty(ngridpts,np.float64)
    #    for i in range(mpi_size):
    #        ugrid_from_gather[k][start_rank[i]:elements_rank[i]+start_rank[i]] = ugrid[k][i]

    print 'Rank: ' + str(mpi_rank) + ' printing grid data.'
    # All grid intervals have now been computed, time to print out the grid data...
    gridFile = open(gridFileName,'w')
    
    ## Write header
    modelHeader = '#  ' + 'radius  '
    for vark in vars.keys():
        modelHeader = modelHeader + vark + '  '
    gridFile.write(modelHeader + '\n')
    
    ## Write number of grid points
    gridFile.write(str(ngridpts)+'\n')
    
    ## Write the grid data
    for i in range(mpi_size):
        for j in range(elements_rank[i]):
    	    gridFile.write(str(esf(ugrid['rad_cm_ctr'][i][j])) + ' ')
    	    for vark in vars.keys():
    		gridFile.write(str(esf(ugrid[vark][i][j])) + ' ')
    	    gridFile.write('\n')
    
    ## Close the grid file
    gridFile.close()
    
