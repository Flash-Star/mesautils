#!/usr/bin/env python
"""
Get inlist parameters from a MESA inlist.

Prints 'parametererror' if a parameter cannot be found.

Prints 'fileerror' if the inlist cannot be opened.

Donald E. Willcox
"""
import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument("inlist", type=str, help="Supply the MESA inlist file from which to get the parameters.")
parser.add_argument("-p", "--parameters", type=str, nargs="+", required=True, 
                    help="Name of input parameters to retrieve from inlist.")
args = parser.parse_args()

def getparams(ifile):
    # Given an inlist file, retrieve the --parameters
    v = {}
    relist = [re.compile('\A{}\s*=\s*(.*)\Z'.format(p)) for p in args.parameters]
    refound = [False for p in args.parameters]
    for line in ifile:
        ls = line.strip()
        for i, (p, pre) in enumerate(zip(args.parameters, relist)):
            if not refound[i]:
                m = pre.match(ls)
                if m:
                    v[p] = m.group(1)
                    refound[i] = True
    return v

def sanitycheck(v):
    for p in args.parameters:
        try:
            assert(p in v.keys())
        except:
            print('parametererror')
            exit()

def printparams(v):
    # Print the parameters in the order they were passed as --parameters.
    # Print one parameter per line as they could have spaces if they are strings.
    for p in args.parameters:
        print(v[p])

if __name__ == "__main__":
    try:
        f = open(args.inlist, 'r')
    except:
        print('fileerror')
        exit()
    else:
        # Get list of parameter values in order they were passed as --parameters
        v = getparams(f)
        sanitycheck(v)
        f.close()
        printparams(v)
