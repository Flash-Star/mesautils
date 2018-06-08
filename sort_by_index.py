#!/usr/bin/env python
"""
Sorts grid results for a grid of MESA runs by the index
of the grid sample. The index is the first column of the data line.

This script ignores the first line as the header and outputs
a sorted version of the input file.

Donald E. Willcox
"""
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("infile", type=str, help="Supply the grid results file to sort by index.")
parser.add_argument("-o", "--outfile", type=str, 
                    help="Supply the name of the sorted grid results file to write. (Default is [infile].sorted)")
args = parser.parse_args()

if not args.outfile:
    outfile = "{}.sorted".format(args.infile)
else:
    outfile = args.outfile

fin = open(args.infile, 'r')

header = fin.readline()

unsorted_lines = []
for line in fin:
    ls = line.strip().split()
    index = int(ls[0])
    unsorted_lines.append([index, line])
fin.close()

# Sort the lines by index
sorted_lines = sorted(unsorted_lines, key=lambda x: x[0])

# Write to output file
fout = open(outfile, 'w')
fout.write(header)
for entry in sorted_lines:
    line = entry[1]
    fout.write(line)
fout.close()

