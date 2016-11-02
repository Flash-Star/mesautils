from __future__ import print_function
from MesaProfile import MesaProfile
from Nuclides import Nuclides

mesa = MesaProfile()
mesa.setInProfileName('profile75.data')
mesa.readProfile()
mstar = mesa.getStar()

nucs = Nuclides()

l = []
for k in mstar.keys():
    if nucs.is_nuclide(k):
        l.append(k)

print(l)
