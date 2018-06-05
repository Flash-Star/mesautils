#!/usr/bin/env python
"""
Set inlist parameter from a MESA inlist given a specific namelist to put it in.

Prints 'parametererror' if the namelist cannot be found.

Prints 'fileerror' if the inlist cannot be opened.

Donald E. Willcox
"""
import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument("inlist", type=str, help="Supply the MESA inlist file for which to set the parameter.")
parser.add_argument("-o", "--outlist", type=str, required=True, help="Output inlist file.")
parser.add_argument("-n", "--namelist", type=str, required=True,
                    help="Name of input namelist in which to set the parameter.")
parser.add_argument("-p", "--parameter", type=str, required=True, 
                    help="Name of input parameter to set in the inlist.")
parser.add_argument("-i", "--integer", type=int, help="Integer value of parameter.")
parser.add_argument("-b", "--boolean", type=str, help="Boolean value ('true' or 'false') of parameter.")
parser.add_argument("-f", "--float", type=float, help="Float value of parameter.")
parser.add_argument("-s", "--string", type=str, help="String value of parameter.")
args = parser.parse_args()

def getparametervalue():
    if args.integer:
        value = args.integer
    elif args.boolean:
        if args.boolean.lower() == 'true' or args.boolean.lower() == 't':
            value = '.true.'
        else:
            value = '.false.'
    elif args.float:
        value = '{}'.format(args.float).replace('e','d').replace('E','D')
    elif args.string:
        value = "'{}'".format(args.string)
    else:
        print('novalueerror')
        exit()
    return value

def getinlist():
    try:
        f = open(args.inlist, 'r')
    except:
        print('fileerror')
        exit()
    else:
        lines = [l for l in f]
        return lines

def setoutlist(value, lines):
    # Construct output inlist file setting args.parameter to value.
    nre = re.compile('\A&(.*)\Z')
    pre = re.compile('\A{}\s*=\s*(.*)\Z'.format(args.parameter))
    found_namelist = False
    inserted_parameter = False
    outlines = []
    for line in lines:
        oline = line
        ls = line.strip()
        m = nre.match(ls)
        if m:
            if m.group(1)==args.namelist:
                found_namelist = True
            else:
                found_namelist = False
            outlines.append(oline)
        elif found_namelist:
            if not inserted_parameter:
                outlines.append('      {} = {}\n'.format(args.parameter, value))
                inserted_parameter = True
            mp = pre.match(ls)
            if not mp:
                outlines.append(oline)
        else:
            outlines.append(oline)
    return outlines

def writeoutlist(outlines):
    fo = open(args.outlist, 'w')
    for l in outlines:
        fo.write(l)
    fo.close()

if __name__ == "__main__":
    param_value  = getparametervalue()
    inlist_lines = getinlist()
    outlist_lines = setoutlist(param_value, inlist_lines)
    writeoutlist(outlist_lines)
