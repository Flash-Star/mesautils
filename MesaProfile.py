"""
This class provides data structures and functions for reading a MESA profile.

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

class MesaProfile:
        def __call__(self, pname=None):
                self.__init__(pname)
                
	def __init__(self, pname=None):
		self.inProfileName = pname

		# Data structures
		## The header is stored as a dictionary
		self.head = OrderedDict([])
		self.head_fields = []
		## The zone data is stored as a list of dictionaries
		self.zone = []
		self.zone_fields = []
		## The star data structure is a dictionary of numpy arrays
		self.star = OrderedDict([])

                if pname:
                        self.setInProfileName(pname)
                        if 'profile' in pname:
                                self.readProfile()
                        elif 'history' in pname:
                                self.readHistory()
                        else:
                                raise ValueError('input must have \'profile\' or \'history\' in file name.')
        
	# Function declarations
	def setInProfileName(self,iPN):
		self.inProfileName = iPN

	def getStar(self):
		return self.star

	def fillDict(self,d,k,v):
		## Fill a dictionary given a list of keys and values
		## Typecast values as either int or float depending on the presence of a '.'
		for i in range(0,len(k)):
			# Detect float vs int and typecast accordingly
			if (v[i].find('.') == -1): # value is an int
				d[k[i]] = int(v[i])
			else: # value is a float
				d[k[i]] = float(v[i])
		return d 

	def getHeadFields(self):
		return self.head_fields

	def getZoneFields(self):
		return self.zone_fields

	def zone2star(self,z,s):
		# Get number of zones
		nz = len(z)

		# Iterate over all zone fields
		for f in z[0].keys():
		# Fill a numpy array with the values for each zone field
		# NOTE: reversed means lower indices are closer to r=0, 
		# contrary to MESA zone indexing (MESA starts indexing zones at edge of star).
			s[f] = np.array([zi[f] for zi in reversed(z)])

		# Return star data structure
		return s

	def readProfile(self):
		# Open mesa profile
		self.fin = open(self.inProfileName,'r')

		# Read mesa profile into data structures for header and zones
		## Get indices for header fields
		self.fin.readline()
		self.head_fields = self.fin.readline()
		self.head_fields = self.head_fields.split()
		self.head_values = self.fin.readline()
		self.head_values = self.head_values.split()
		self.head = self.fillDict(OrderedDict([]),self.head_fields,self.head_values)
		# Read zone data from profile into structure zone
		self.fin.readline()
		self.fin.readline()
		self.zone_fields = self.fin.readline()
		self.zone_fields = self.zone_fields.split()
		for l in self.fin:
			self.zone.append(self.fillDict(OrderedDict([]),self.zone_fields,l.split()))

		# Profile has been fully read into memory, close it
		self.fin.close()
		# Convert zone data structure to star data structure
		self.star = self.zone2star(self.zone,self.star)
		# Add header to star data structure
		for k,v in self.head.iteritems():
			self.star[k] = v

	def str2num(self,s):
		try:
			num = float(s)
		except ValueError:
			num = int(s)
		return num

	def readHistory(self):
		# Open mesa history file
		self.fin = open(self.inProfileName,'r')
		
		self.fin.readline()
		self.head_fields = self.fin.readline()
		self.head_fields = self.head_fields.split()
		self.head_values = self.fin.readline()
		self.head_values = self.head_values.split()
		self.head = self.fillDict(OrderedDict([]),self.head_fields,self.head_values)
		
		self.fin.readline()
		self.fin.readline()

		# Read time series data from the rest of the file
		self.tzone_fields = self.fin.readline()
		self.tzone_fields = self.tzone_fields.split()
		self.star = OrderedDict([])
		for tzf in self.tzone_fields:
			self.star[tzf] = []
		for l in self.fin:
			ls = l.split()
			for k,v in zip(self.tzone_fields,ls):
				self.star[k].append(self.str2num(v))
		# now convert to np arrays
		for k in self.star.keys():
			self.star[k] = np.array(self.star[k])
			
