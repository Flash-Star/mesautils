"""
This class maps abundances from a MESA profile to a reduced set for FLASH.

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
import numpy as np
from collections import OrderedDict

# Map abundances to set of C12, O16, Ne20, Ne22 for flash!
class MapMesaComposition:
	def __init__(self):
		self.fmap = OrderedDict([('c12',np.array([])),
					('o16',np.array([])),
					('ne20',np.array([])),
					('ne22',np.array([]))])
	def getmap(self,ms):
		## Maintain constant C12 abundance
		self.fmap['c12'] = ms['c12']
		## Determine Ne22 abundance from model Ye
		self.fmap['ne22'] = np.maximum(22.0*(0.5-ms['ye']), 0.0)
		## Normalization requires Ne20 + O16 abundances = xother
		xother = 1.0 - self.fmap['c12'] - self.fmap['ne22']
		## Ne20/O16 ratio remains constant
		rneo = ms['ne20']/ms['o16']
		## Use rneo and xother constraints to find Ne20 and O16 abundances
		self.fmap['o16'] = xother/(rneo+1.0)
		self.fmap['ne20'] = rneo*xother/(rneo+1.0)
		for k in self.fmap.keys():
			ms[k] = self.fmap[k]
		return ms	
