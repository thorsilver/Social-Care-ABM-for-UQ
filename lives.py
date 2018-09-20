#!/usr/bin/python
# Adjunct to the main.py file for the 'lives' simulation program

import argparse
import json

def loadParamFile(file, dict):
    """
    Given a JSON filename and a dictionary, return the dictionary with
    the file's fields merged into it.
    Example: if the initial dictionary is
    dict['bobAge'] = 90 and dict['samAge']=20 and the JSON data is
    {'age':{'bob':40, 'fred':35}}
    the returned dictionary contains the following data values:
    dict['bobAge'] = 40, dict['fredAge'] = 35, dict['samAge'] = 20
    """
    json_data = open(file).read()
    data = json.loads(json_data)

    for group in data:
        fields = data.get(group)
        if type({}) == type(fields):
            # Group of fields - create name from item and group
            for item in fields:
                name = item + group[:1].upper() + group[1:]
                value = data [group][item]
                dict [name] = value
        else:
            # Single data value - naming is assumed to be correct case
            dict [group] = fields

    return dict

def loadCommandLine(dict):
    """Process the command line, loading params file (if required). The dict
    argument will be augmented with data from the user-specified parameters
    file (if required), otherwise will return the dict argument unchanged"""
    parser = argparse.ArgumentParser(
        description='lives v1.0: complex social behaviour simulation.',
        epilog='Example: "lives -f test.json -n 3" --- run 3 sims with test.json\'s params',
        formatter_class=argparse.RawTextHelpFormatter,
        prog='lives',
        usage='use "%(prog)s -h" for more information')
    parser.add_argument(
        '-f', '--file',
        help='parameters file in JSON format e.g. postdoc.json')
    parser.add_argument(
        '-n', '--num', metavar='N', type=int, default=1,
        help='number of runs to carry out. Not needed if N=1')
    parser.add_argument(
        '-r', '--retire', action='store_true',
        help='batch run for retirement')
    args = parser.parse_args()
    print("~ Filename: {}".format(args.file))
    print("~ Number:   {}".format(args.num))
    print("~ Retire:   {}".format(args.retire))
    if args.file:
        res = loadParamFile (args.file, dict)

    return dict

# Some test data
# p['favouriteSeed'] will remain untouched
# p['ageScalingMale'] will be overwritten with the data file's
#  'ageScalingMale' value
# many other values will be added to p from the data file
p = {}
p ['favouriteSeed'] = None
p ['ageScalingMale'] = 12345

# Load the default values, overwriting and adding to the initial p values
loadParamFile("default.json", p)

# Load values based upon the command line file passed (if any).
loadCommandLine (p)
print ("p = {}".format(p))
