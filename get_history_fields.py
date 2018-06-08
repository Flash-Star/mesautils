#!/usr/bin/env python
"""
Get the fields (column names) in a MESA history file.

Relies on mesautils, part of Flash-Star.

Donald E. Willcox
"""
from MesaProfile import MesaProfile
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("infile", type=str, help="Supply the MESA history file from which to get the fields.")
args = parser.parse_args()

ms = MesaProfile(args.infile)
s = ms.star

for k in s.keys():
    print(k)
