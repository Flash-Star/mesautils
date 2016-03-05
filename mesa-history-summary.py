"""
Make a HR diagram given a mesa history file.

Donald Willcox
"""
from MesaProfile import MesaProfile
import argparse
import matplotlib.pyplot as plt
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("infile", type=str, help="Supply the MESA history file from which to make the HR diagram.")
args = parser.parse_args()

ms = MesaProfile(args.infile)
s = ms.star

# Plot Log Luminosity vs. Star Age (yr)
fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(np.log10(s['star_age']),s['log_L'])
plt.xlabel('$\\mathrm{Log_{10}}$ Star Age (yr)')
plt.ylabel('$\\mathrm{Log_{10}}~L/L_{\\odot}$')
plt.tight_layout()
plt.savefig("lumi-age.pdf")

# Plot HR diagram
plt.clf()
fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(s['log_Teff'],s['log_L'])
plt.xlabel('$\\mathrm{Log_{10}~T_{eff}~(K)}$')
plt.gca().invert_xaxis()
plt.ylabel('$\\mathrm{Log_{10}}~L/L_{\\odot}$')
plt.tight_layout()
plt.savefig("lumi-teff.pdf")
