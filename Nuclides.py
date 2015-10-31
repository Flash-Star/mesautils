"""
This module provides data structures and functions for storing nuclear
reaction network data and identifying nuclei with their (n,z) values.

The (n,z) data is provided by nuclides.xml, obtained from the JINA nuclide 
database (https://groups.nscl.msu.edu/jina/nucdatalib/tools).

Copyright 2015 Donald E. Willcox

This file is part of nucplotlib.

    nucplotlib is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    nucplotlib is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with nucplotlib.  If not, see <http://www.gnu.org/licenses/>.
"""
import numpy as np
import xml.etree.ElementTree as etree

class Nuclide:
	def __init__(self,n=None,z=None,x=None):
		self.n = int(n)
		self.z = int(z)
		self.a = self.n + self.z
		if x.all():
			self.x = np.array(x)
		else:
			self.x = []

	def set_abundance(self,x):
		self.x = np.array(x)

class Nuclides:
	def __init__(self):	
		self.nucdata = []
		self.time = []
		self.xlen = None
	
		## Create a nuclide look-up table for Z and N mapping	
		self.nuclide_lut = {}
		# put in neutrons and protons, named as they appear from TORCH
                self.nuclide_lut['h1'] = {'abb':'h', 'z':1, 'a':1, 'n':0}
                self.nuclide_lut['h2'] = {'abb':'h', 'z':1, 'a':2, 'n':1}
                self.nuclide_lut['h3'] = {'abb':'h', 'z':1, 'a':3, 'n':2}
		self.nuclide_lut['neut'] = {'abb':'neut', 'z':0, 'a':1, 'n':1}
		self.nuclide_lut['prot'] = {'abb':'prot', 'z':1, 'a':1, 'n':0}
		# Load Reaclib V1.0 Masses from a reaclib 'nuclides.xml' file
		try:
			tree = etree.parse('nuclides.xml')
		except:
			print 'Error: nuclides.xml missing or corrupt!'
			exit()
		nuc_xml = tree.iter('nuclide')
		for entry in nuc_xml:
			nuc_entry = {}
			nuc_entry['nuc'] = entry.attrib['nuc']
			nuc_entry['z'] = int(entry.attrib['zvalue'])
			nuc_entry['a'] = int(entry.attrib['mvalue'])
			nuc_entry['n'] = nuc_entry['a']-nuc_entry['z']
			self.nuclide_lut[entry.attrib['comp']] = nuc_entry

        def is_nuclide(self,abbrev):
                if abbrev.lower() in self.nuclide_lut:
                        return True
                else:
                        return False
                        
	def clr_dataset(self):
		self.nucdata = []
		self.time = []
		self.xlen = None

	def add_nuc(self,abbrev=None,x=None,n=None,z=None):
		if abbrev:
			# Preferentially lookup isotope n and z using abbrev.
			this_nuclide = self.nuclide_lut[abbrev.lower()]
			nn = this_nuclide['n']
			zz = this_nuclide['z']
		else:
			nn = int(n)
			zz = int(z)
		nuc = Nuclide(nn,zz,x)
		self.nucdata.append(nuc)
		if not self.xlen and x.all():
			self.xlen = len(x)
		elif self.xlen and x.all():
			if (self.xlen != len(x)):
				print 'Error: unequal abundance vector lengths!'
				exit()

	def set_time(self,time):
		self.time = np.array(time)
		if not self.xlen:
			self.xlen = len(time)
		else:
			if (self.xlen != len(time)):
				print 'Error: unequal abundance vector lengths!'
				exit()
				
	def load_dataset(self,data):
		# data should be a dictionary keyed by isotope abbreviations
		# values should be numpy arrays
		# additional k,v pairs which are not isotopes may be present.
		
		# load time if present
		if 'time' in data:
			self.set_time(data['time'])

		# load any isotopes present as identified by abbreviation
		dsk = [k.lower() for k in data.keys()]
		for nuc in self.nuclide_lut.keys():
			if nuc in dsk:
				self.add_nuc(abbrev=nuc,x=data[nuc])

	def get_range_nz(self):
		# returns maximum and minimum n and z values in the dataset
		# returns a dictionary d:
		# d = {'n': [min_n,max_n], 'z': [min_z,max_z]}
		d = {}
		n = [-1,-1]
		z = [-1,-1]
		for nuc in self.nucdata:
			if n[0] == -1:
				n[0] = nuc.n
			else:
				n[0] = min([n[0],nuc.n])
			n[1] = max([n[1],nuc.n])	
			if z[0] == -1:
				z[0] = nuc.z
			else:
				z[0] = min([z[0],nuc.z])
			z[1] = max([z[1],nuc.z])	
		d['n'] = n
		d['z'] = z
		return d
			
