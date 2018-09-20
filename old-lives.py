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
    """Process the command line, loading params file (if required)."""
    parser = argparse.ArgumentParser(
        description='lives v1.0: complex social behaviour simulation.',
        prog='lives',
        epilog='Example: \'lives -f test.json -n 3\' --- run 3 sims using test.json\'s parameters')
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
    # print("~ Filename: {}".format(args.file))
    # print("~ Number:   {}".format(args.num))
    # print("~ Retire:   {}".format(args.retire))
    if args.file:
        res = loadParamFile (args.file, dict)

    return dict


# Some test data
# p['favouriteSeed'] will remain untouched
# p['ageScalingMale'] will be overwritten with the data file's 'ageScalingMale' value
# many other values will be added to p from the data file
p = {}
p ['favouriteSeed'] = None
p ['ageScalingMale'] = 12345
# print ("p = {}".format(p))

# Load the default values, overwriting and adding to the initial p values
loadParamFile("default.json", p)
# print ("p = {}".format(p))

# Load values based upon the command line file passed (if any).
loadCommandLine (p)
print ("p = {}".format(p))

""" Using the following command line call: 
python lives.py -f lives_data.json
The result is
p = {'ageScalingMale': 12345, 'favouriteSeed': None}
p = {'ageScalingMale': 14.0, u'ageMaxstart': 40, u'ageCareScalingMale': 10.0, u'careProbBase': 0.0002, u'popBirthProbSteady': 0.13, u'ageMinstart': 20, 'favouriteSeed': None, u'yearCurrent': 2012, u'careProbPerson': 0.0008, u'hoursWorkingadult': 25.0, u'dieProbFemaleage': 0.00019, u'ageAdulthood': 17, u'ageRetirement': 65, u'dieProbBase': 0.0001, u'yearCollectfrom': 1960, u'pregnancyAgeMin': 17, u'yearStart': 1860, u'ageScalingFemale': 15.5, u'dieProbMaleage': 0.00021, u'occupationClassesNum': 3, u'hoursRetired': 60.0, u'yearTransition': 1965, u'dieProbBaby': 0.005, u'yearEnd': 2050, u'pregnancyAgeMax': 42, u'ageCareScalingFemale': 19.0, u'popBirthProbGrowing': 0.215, u'hoursHomeadult': 30.0, u'hoursChild': 5.0}
"""
