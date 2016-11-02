from __future__ import print_function

f = open('profile75_uniform_composition.dat','r')
f.readline()
f.readline()
## Test to make sure abundances are normalized

for l in f:
    ls = l.split()
    x = sum([float(y) for y in ls[3:]])
    if abs(x-1.0) > 1.0e-15:
        print('Error: unnormalized')

f.close()
    
