#!/bin/bash

# Example Run Script
# For more details, run `$ python UniformMesaGrid.py --help`
# profile75.data is the input MESA profile to put on a uniform grid in this example
# -ip is the interpolation type flag which can take the following values
## -ip=1 : Linear 
## -ip=2 : Quadratic
## -ip=3 : Cubic
# -drcm specifies the radial grid thickness in units of cm
# -o specifies the name of the output file to create
# The use of the flag -mfx will map abundances to a reduced set of nuclides for FLASH (C12, O16, Ne20, Ne22)

mpiexec -np 6 python UniformMesaGrid.py -o gridded_profile75_original_X-ye.dat -drcm=4e5 -ip=2 -mfx profile75.data
