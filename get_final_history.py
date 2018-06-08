#!/usr/bin/env python
"""
Get the final value of fields (column names) in a MESA history file.

Pass the desired fields as command line arguments to '--fields' and
their final values will be returned, space delimited.

Relies on mesautils, part of Flash-Star.

Donald E. Willcox
"""
from MesaProfile import MesaProfile
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("infile", type=str, help="Supply the MESA history file from which to get the field values.")
parser.add_argument("-f", "--fields", type=str, nargs="+", default=["star_mass"],
                    help="Name of the field(s) for which to get the final values. Default is 'star_mass'.")
args = parser.parse_args()

ms = MesaProfile(args.infile)
s = ms.star

v = []
for k in args.fields:
    try:
        assert(k in s.keys())
    except:
        print('fieldnotfounderror')
        exit()
    else:
        v.append('{}'.format(s[k][-1]))

values = ' '.join(v)
print(values)
