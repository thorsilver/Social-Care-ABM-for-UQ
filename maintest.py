
from sim import Sim
import os
import cProfile
import pylab
import math
import matplotlib.pyplot as plt
import argparse
import json
import decimal
import numpy as np


def init_params():
    """Set up the simulation parameters."""
    p = {}

    ## The basics: starting population and year, etc.
    p['initialPop'] = 750
    p['startYear'] = 1860
    p['endYear'] = 2050
    p['thePresent'] = 2012
    p['statsCollectFrom'] = 1960
    p['minStartAge'] = 20
    p['maxStartAge'] = 40
    p['verboseDebugging'] = False
    p['singleRunGraphs'] = True
    p['favouriteSeed'] = None
    p['numRepeats'] = 1
    p['loadFromFile'] = False

    ## Mortality statistics
    p['baseDieProb'] = 0.0001
    p['babyDieProb'] = 0.005
    p['maleAgeScaling'] = 14.0
    p['maleAgeDieProb'] = 0.00021
    p['femaleAgeScaling'] = 15.5
    p['femaleAgeDieProb'] = 0.00019
    p['num5YearAgeClasses'] = 28

    ## Transitions to care statistics
    p['baseCareProb'] = 0.0002
    p['personCareProb'] = 0.0008
    ##p['maleAgeCareProb'] = 0.0008
    p['maleAgeCareScaling'] = 18.0
    ##p['femaleAgeCareProb'] = 0.0008
    p['femaleAgeCareScaling'] = 19.0
    p['numCareLevels'] = 5
    p['cdfCareTransition'] = [ 0.7, 0.9, 0.95, 1.0 ]
    p['careLevelNames'] = ['none','low','moderate','substantial','critical']
    p['careDemandInHours'] = [ 0.0, 8.0, 16.0, 30.0, 80.0 ]
    
    ## Availability of care statistics
    p['childHours'] = 5.0
    p['homeAdultHours'] = 30.0
    p['workingAdultHours'] = 25.0
    p['retiredHours'] = 60.0
    p['lowCareHandicap'] = 0.5
    p['hourlyCostOfCare'] = 20.0

    ## Fertility statistics
    p['growingPopBirthProb'] = 0.215
    p['steadyPopBirthProb'] = 0.13
    p['transitionYear'] = 1965
    p['minPregnancyAge'] = 17
    p['maxPregnancyAge'] = 42

    ## Class and employment statistics
    p['numOccupationClasses'] = 3
    p['occupationClasses'] = ['lower','intermediate','higher']
    p['cdfOccupationClasses'] = [ 0.6, 0.9, 1.0 ]

    ## Age transition statistics
    p['ageOfAdulthood'] = 17
    p['ageOfRetirement'] = 65
    
    ## Marriage and divorce statistics (partnerships really)
    p['basicFemaleMarriageProb'] = 0.25
    p['femaleMarriageModifierByDecade'] = [ 0.0, 0.5, 1.0, 1.0, 1.0, 0.6, 0.5, 0.4, 0.1, 0.01, 0.01, 0.0, 0.0, 0.0, 0.0, 0.0 ]
    p['basicMaleMarriageProb'] =  0.3 
    p['maleMarriageModifierByDecade'] = [ 0.0, 0.16, 0.5, 1.0, 0.8, 0.7, 0.66, 0.5, 0.4, 0.2, 0.1, 0.05, 0.01, 0.0, 0.0, 0.0 ]
    p['basicDivorceRate'] = 0.06
    p['variableDivorce'] = 0.06
    p['divorceModifierByDecade'] = [ 0.0, 1.0, 0.9, 0.5, 0.4, 0.2, 0.1, 0.03, 0.01, 0.001, 0.001, 0.001, 0.0, 0.0, 0.0, 0.0 ]
    
    ## Leaving home and moving around statistics
    p['probApartWillMoveTogether'] = 0.3
    p['coupleMovesToExistingHousehold'] = 0.3
    p['basicProbAdultMoveOut'] = 0.22
    p['probAdultMoveOutModifierByDecade'] = [ 0.0, 0.2, 1.0, 0.6, 0.3, 0.15, 0.03, 0.03, 0.01, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 ]
    p['basicProbSingleMove'] = 0.05
    p['probSingleMoveModifierByDecade'] = [ 0.0, 1.0, 1.0, 0.8, 0.4, 0.06, 0.04, 0.02, 0.02, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 ]
    p['basicProbFamilyMove'] = 0.03
    p['probFamilyMoveModifierByDecade'] = [ 0.0, 0.5, 0.8, 0.5, 0.2, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1 ]
    p['agingParentsMoveInWithKids'] = 0.1
    p['variableMoveBack'] = 0.1

    ## Description of the map, towns, and houses
    p['mapGridXDimension'] = 8
    p['mapGridYDimension'] = 12    
    p['townGridDimension'] = 40
    p['numHouseClasses'] = 3
    p['houseClasses'] = ['small','medium','large']
    p['cdfHouseClasses'] = [ 0.6, 0.9, 5.0 ]

    p['ukMap'] = [ [ 0.0, 0.1, 0.2, 0.1, 0.0, 0.0, 0.0, 0.0 ],
                   [ 0.1, 0.1, 0.2, 0.2, 0.3, 0.0, 0.0, 0.0 ],
                   [ 0.0, 0.2, 0.2, 0.3, 0.0, 0.0, 0.0, 0.0 ],
                   [ 0.0, 0.2, 1.0, 0.5, 0.0, 0.0, 0.0, 0.0 ],
                   [ 0.4, 0.0, 0.2, 0.2, 0.4, 0.0, 0.0, 0.0 ],
                   [ 0.6, 0.0, 0.0, 0.3, 0.8, 0.2, 0.0, 0.0 ],
                   [ 0.0, 0.0, 0.0, 0.6, 0.8, 0.4, 0.0, 0.0 ],
                   [ 0.0, 0.0, 0.2, 1.0, 0.8, 0.6, 0.1, 0.0 ],
                   [ 0.0, 0.0, 0.1, 0.2, 1.0, 0.6, 0.3, 0.4 ],
                   [ 0.0, 0.0, 0.5, 0.7, 0.5, 1.0, 1.0, 0.0 ],
                   [ 0.0, 0.0, 0.2, 0.4, 0.6, 1.0, 1.0, 0.0 ],
                   [ 0.0, 0.2, 0.3, 0.0, 0.0, 0.0, 0.0, 0.0 ] ]

    p['mapDensityModifier'] = 0.6
    p['ukClassBias'] = [
                    [ 0.0, -0.05, -0.05, -0.05, 0.0, 0.0, 0.0, 0.0 ],
                    [ -0.05, -0.05, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0 ],
                    [ 0.0, -0.05, -0.05, 0.0, 0.0, 0.0, 0.0, 0.0 ],
                    [ 0.0, -0.05, -0.05, 0.05, 0.0, 0.0, 0.0, 0.0 ],
                    [ -0.05, 0.0, -0.05, -0.05, 0.0, 0.0, 0.0, 0.0 ],
                    [ -0.05, 0.0, 0.0, -0.05, -0.05, -0.05, 0.0, 0.0 ],
                    [ 0.0, 0.0, 0.0, -0.05, -0.05, -0.05, 0.0, 0.0 ],
                    [ 0.0, 0.0, -0.05, -0.05, 0.0, 0.0, 0.0, 0.0 ],
                    [ 0.0, 0.0, -0.05, 0.0, -0.05, 0.0, 0.0, 0.0 ],
                    [ 0.0, 0.0, 0.0, -0.05, 0.0, 0.2, 0.15, 0.0 ],
                    [ 0.0, 0.0, 0.0, 0.0, 0.1, 0.2, 0.15, 0.0 ],
                    [ 0.0, 0.0, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0 ] ]

    ## Graphical interface details
    p['interactiveGraphics'] = True
    p['delayTime'] = 0.0
    p['screenWidth'] = 1300
    p['screenHeight'] = 700
    p['bgColour'] = 'black'
    p['mainFont'] = 'Helvetica 18'
    p['fontColour'] = 'white'
    p['dateX'] = 70
    p['dateY'] = 20
    p['popX'] = 70
    p['popY'] = 50
    p['pixelsInPopPyramid'] = 2000
    p['careLevelColour'] = ['blue','green','yellow','orange','red']
    p['houseSizeColour'] = ['brown','purple','yellow']
    p['pixelsPerTown'] = 56
    p['maxTextUpdateList'] = 22
    
    return p

p = init_params()

#######################################################
## A basic single run

def basicRun(p):
    s = Sim(p)
    tax = s.run()
    
#######################################################
## Batch run (no graphics)
    
def batchRun(num):
    p['interactiveGraphics'] = False
    dataFile = open('batchRunData.txt','w')
    for i in range ( 0, num ):
            print "Doing batch run: ", i
            taxList = []
            s = Sim(p)
            tax = s.run()
            taxList.append(tax)
            print "Social care cost per taxpayer: ", tax
            dataFile.write(str(i) + "\t" + str(tax) + "\n")
    dataFile.close()
    
#######################################################
## Retirement age run (no graphics)
 
def retireRun(reps):   
    taxMeans = []
    taxSEs = []
    p['verboseDebugging'] = False
    p['singleRunGraphs'] = False
    p['interactiveGraphics'] = False
    dataFile = open('retirementAgeData2.txt','w')
    #p['ageingParentList'] = [50, 55, 65, 70, 75, 80]    
    for variableCare in p['ageingParentList']:
            p['ageOfRetirement'] = variableCare
            print "Trying retirement age: ", variableCare
            taxList = []
            for i in range ( 0, reps ):
                print i,
                s = Sim(p)
                tax = s.run()
                taxList.append(tax)
                print tax
                dataFile.write(str(variableCare) + "\t" + str(i) + "\t" + str(tax) + "\n")
            taxMeans.append(pylab.mean(taxList))
            taxSEs.append(pylab.std(taxList) / math.sqrt(reps))
    
    dataFile.close()
    
    indices1 = pylab.arange(len(p['ageingParentList']))
    
    taxFig = pylab.figure()
    taxBar = taxFig.add_subplot(1,1,1)
    taxBar.bar(indices1, taxMeans, facecolor='red',
                 align='center', yerr=taxSEs, ecolor='black')
    taxBar.set_ylabel('Mean social care cost per taxpayer')
    taxBar.set_xlabel('Age of retirement')
    taxBar.set_xticks(indices1)
    taxBar.set_xticklabels(p['ageingParentList'])
    pylab.savefig('retirementAgeRunSet1.pdf')
    pylab.show()    

#######################################################
##runs for sensitivity analysis using GEM-SA
    
def gemRun(reps):    
    taxMeans = []
    taxSEs = []
    
    p['verboseDebugging'] = False
    p['singleRunGraphs'] = False
    p['interactiveGraphics'] = False
    
    dataFile = open('GEMSA data new.txt','a')
    meansFile = open('GEMSA means new.txt', 'a')
    outFile = open('GEMSA outputs new.txt', 'a')
    
#    agingParentList = [ 0.0, 0.1, 0.2, 0.4 ] 
#    careProbList = [ 0.0004, 0.0008, 0.0012, 0.0016 ] 
#    retiredHoursList = [ 20.0, 30.0, 40.0, 60.0 ] 
#    retiredAgeList = [ 60.0 ]
#    ageingParentList = [ 0.0, 0.1 ] 
#    careProbList = [ 0.0004 ] 
#    retiredHoursList = [ 20.0 ] 
#    retiredAgeList = [ 60.0 ]
    
    for variableCare in p['ageingParentList']:
        for variableProb in p['careProbList']:
            for variableRetired in p['retiredHoursList']:
                for variableAge in p['retiredAgeList']:
                    p['agingParentsMoveInWithKids'] = variableCare
                    p['personCareProb'] = variableProb
                    p['retiredHours'] = variableRetired
                    p['ageOfRetirement'] = variableAge
                    print "Trying parents-moving-in probability: ", variableCare
                    print "Trying person care probability: ", variableProb
                    print "Trying retired hours: ", variableRetired
                    print "Trying retirement age: ", variableAge
                    taxList = []
                    taxSum = 0.0
                    meansFile.write(str(variableCare) + "\t" + str(variableProb) + "\t" + str(variableRetired) + "\t" + str(variableAge) + "\n")
                    for i in range ( 0, reps ):
                        print i,
                        s = Sim(p)
                        tax, seed = s.run()
                        taxList.append(tax)
                        taxSum += tax
                        print tax
                        dataFile.write(str(seed) + "\t" + str(variableCare) + "\t" + str(variableProb) + "\t" + str(variableRetired) + "\t" + str(variableAge) + "\t" + str(tax) + "\n")    
                    taxMeans.append(pylab.mean(taxList))
                    outFile.write(str(taxSum/reps) + "\n")
                    taxSEs.append(pylab.std(taxList) / math.sqrt(reps))
    
    dataFile.close()
    meansFile.close()
    outFile.close()

#######################################################
##runs for sensitivity analysis using GEM-SA - LPtau and Maximin LH
    
def sensitivityRun(runtype, ageingList, careList, retiredHList, retiredAList, reps):    
    taxMeans = []
    taxSEs = []
    
    p['verboseDebugging'] = False
    p['singleRunGraphs'] = False
    p['interactiveGraphics'] = False
    
    dataFile = open(runtype + ' GEMSA data.txt','a')
    meansFile = open(runtype + ' GEMSA means.txt', 'a')
    outFile = open(runtype + ' GEMSA outputs.txt', 'a')
    
#    agingParentList = [ 0.0, 0.1, 0.2, 0.4 ] 
#    careProbList = [ 0.0004, 0.0008, 0.0012, 0.0016 ] 
#    retiredHoursList = [ 20.0, 30.0, 40.0, 60.0 ] 
#    retiredAgeList = [ 60.0 ]
#    ageingParentList = [ 0.0, 0.1 ] 
#    careProbList = [ 0.0004 ] 
#    retiredHoursList = [ 20.0 ] 
#    retiredAgeList = [ 60.0 ]
    
    for run in xrange(len(ageingList)):
        p['agingParentsMoveInWithKids'] = ageingList[run]
        p['personCareProb'] = careList[run]
        p['retiredHours'] = retiredHList[run]
        p['ageOfRetirement'] = retiredAList[run]
        print "Trying parents-moving-in probability: ", ageingList[run]
        print "Trying person care probability: ", careList[run]
        print "Trying retired hours: ", retiredHList[run]
        print "Trying retirement age: ", retiredAList[run]
        taxList = []
        taxSum = 0.0
        meansFile.write(str(ageingList[run]) + "\t" + str(careList[run]) + "\t" + str(retiredHList[run]) + "\t" + str(retiredAList[run]) + "\n")
        for i in range ( 0, reps ):
            print i,
            s = Sim(p)
            tax, seed = s.run()
            taxList.append(tax)
            taxSum += tax
            print tax
            dataFile.write(str(seed) + "\t" + str(ageingList[run]) + "\t" + str(careList[run]) + "\t" + str(retiredHList[run]) + "\t" + str(retiredAList[run]) + "\t" + str(tax) + "\n")    
        taxMeans.append(pylab.mean(taxList))
        outFile.write(str(taxSum/reps) + "\n")
        taxSEs.append(pylab.std(taxList) / math.sqrt(reps))
    
    dataFile.close()
    meansFile.close()
    outFile.close()


#######################################################
##runs for sensitivity analysis using GEM-SA - LPtau and Maximin LH
    
# def sensitivityLarge(runtype, ageingList, careList, retiredHList, retiredAList, baseDieList, babyDieList, personCareList, maleCareList, femaleCareList, \
#     childHoursList, homeAdultList, workingAdultList, lowCareList, growingBirthList, basicDivorceList, variableDivorceList, basicMaleMarriageList, \
#     basicFemaleMarriageList, probMoveList, moveHouseholdList, probMoveOutList, probMoveBackList, reps): 
def sensitivityLarge(runtype, input_list, reps):   
    taxMeans = []
    taxSEs = []
    
    p['verboseDebugging'] = False
    p['singleRunGraphs'] = False
    p['interactiveGraphics'] = False
    
    outFile = open(runtype + ' GEMSA outputs large.txt', 'a')
    
    for run in xrange(len(input_list[0])):
        print("Running simulation number {}...".format(run))
        print("Number of reps: {}".format(reps))
        sim_list = np.array(input_list)
        print(sim_list)
        p['agingParentsMoveInWithKids'] = sim_list[0,run]
        print(p['agingParentsMoveInWithKids'])
        p['personCareProb'] = sim_list[1,run]
        p['retiredHours'] = sim_list[2,run]
        p['ageOfRetirement'] = sim_list[3,run]
        p['baseDieProb'] = sim_list[4,run]
        p['babyDieProb'] = sim_list[5,run]
        p['personCareProb'] = sim_list[6,run]
        p['maleAgeCareScaling'] = sim_list[7,run]
        p['femaleAgeCareScaling'] = sim_list[8,run]
        p['childHours'] = sim_list[9,run]
        p['homeAdultHours'] = sim_list[10,run]
        p['workingAdultHours'] = sim_list[11,run]
        p['lowCareHandicap'] = sim_list[12,run]
        p['growingPopBirthProb'] = sim_list[13,run]
        p['basicDivorceRate'] = sim_list[14,run]
        p['variableDivorce'] = sim_list[15,run] 
        p['basicMaleMarriageProb'] =  sim_list[16,run]
        p['basicFemaleMarriageProb'] = sim_list[17,run]
        p['probApartWillMoveTogether'] = sim_list[18,run]
        p['coupleMovesToExistingHousehold'] = sim_list[19,run]
        p['basicProbAdultMoveOut'] = sim_list[20,run]
        p['variableMoveBack'] = sim_list[21,run]
        taxList = []
        taxSum = 0.0
        for i in range ( 0, reps ):
            print i,
            s = Sim(p)
            tax, seed = s.run()
            taxList.append(tax)
            taxSum += tax
            print tax
        taxMeans.append(pylab.mean(taxList))
        outFile.write(str(taxSum/reps) + "\n" + str(seed) + "\n")
        taxSEs.append(pylab.std(taxList) / math.sqrt(reps))
    
    outFile.close()

#######################################################
##runs for sensitivity analysis using GEM-SA - LPtau and Maximin LH, 10 params
 
def sensitivityTenParams(runtype, input_list, reps):   
    taxMeans = []
    taxSEs = []
    
    p['verboseDebugging'] = False
    p['singleRunGraphs'] = False
    p['interactiveGraphics'] = False
    
    outFile = open(runtype + ' GEMSA outputs.txt', 'a')
    
    for run in xrange(len(input_list[0])):
        print("Running simulation number {}...".format(run))
        print("Number of reps: {}".format(reps))
        sim_list = np.array(input_list)
        print(sim_list)
        p['agingParentsMoveInWithKids'] = sim_list[0,run]
        p['baseCareProb'] = sim_list[1,run]
        p['retiredHours'] = sim_list[2,run]
        p['ageOfRetirement'] = sim_list[3,run]
        p['personCareProb'] = sim_list[4,run]
        p['maleAgeCareScaling'] = sim_list[5,run]
        p['femaleAgeCareScaling'] = sim_list[6,run]
        p['childHours'] = sim_list[7,run]
        p['homeAdultHours'] = sim_list[8,run]
        p['workingAdultHours'] = sim_list[9,run]
        
        taxList = []
        taxSum = 0.0
        for i in range ( 0, reps ):
            print i,
            s = Sim(p)
            tax, seed = s.run()
            taxList.append(tax)
            taxSum += tax
            print tax
        taxMeans.append(pylab.mean(taxList))
        outFile.write(str(taxSum/reps) + "\t" + str(seed) + "\n")
        taxSEs.append(pylab.std(taxList) / math.sqrt(reps))
    
    outFile.close()

#######################################################
## A profiling run; use import pstats then p = pstats.Stats('profile.txt') then p.sort_stats('time').print_stats(10)
#cProfile.run('s.run()','profile.txt')

#######################################################
## Parse command line arguments

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
        epilog='Example: "maintest.py -f test.json -n 3" --- run 3 sims with test.json\'s params',
        formatter_class=argparse.RawTextHelpFormatter,
        prog='lives',
        usage='use "%(prog)s -h" for more information')
    group = parser.add_mutually_exclusive_group()
    parser.add_argument(
        '-f', '--file',
        help='parameters file in JSON format e.g. soylent.json')
    group.add_argument(
        '-n', '--num', metavar='N', type=int, default=0,
        help='number of runs to carry out.')
    group.add_argument('-r', '--retire', metavar='R', type=int, default=0, 
        help='retirement batch, number of iterations.')
    group.add_argument('-g', '--gem', metavar='G', type=int, default=0, 
        help='GEM-SA batch for sensitivity analysis, number of iterations.')
    group.add_argument('-l', '--lptau', metavar='L', type=int, default=0,
        help='sensitivity analysis batch with LPtau sampling.')
    group.add_argument('-m', '--maximin', metavar='M', type=int, default=0,
        help='sensitivity analysis batch with maximin latin hypercube sampling.')
    group.add_argument('-b', '--bigly', metavar='B', type=int, default=0,
        help='bigly sensitivity analysis batch with maximin latin hypercube sampling.')
    group.add_argument('-t', '--tenparams', metavar='T', type=int, default=0,
        help='10 parameter sensitivity analysis batch with maximin latin hypercube sampling.')
    args = parser.parse_args()
    print("~ Filename: {}".format(args.file))
    print("~ Number:   {}".format(args.num))
    print("~ Retire:   {}".format(args.retire))
    print("~ GEM-SA:   {}".format(args.gem))
    print("~ LPtau: {}".format(args.lptau))
    print("~ Maximin: {}".format(args.maximin))
    print("~ Big SA: {}".format(args.bigly))
    print("~Ten Params: {}".format(args.tenparams))
    if args.file:
        #agingParentList = json.load(retireList, parse_float=decimal.Decimal)
        res = loadParamFile (args.file, dict)
        print ("p = {}".format(dict))
        basicRun(dict)
    elif args.num >= 1:
        batchRun(args.num)
    elif args.retire:
        p['ageingParentList'] = []
        res = loadParamFile('retire.json', dict)
        print("List = {}".format(dict))
        retireRun(args.retire)
    elif args.gem:
        p['ageingParentList'] = [] 
        p['careProbList'] = [] 
        p['retiredHoursList'] = [] 
        p['retiredAgeList'] = []
        res = loadParamFile('gem.json', dict)
        print("List = {}".format(dict))
        gemRun(args.gem)
    elif args.lptau:
        sim_array = np.genfromtxt('lptau-4params.txt', delimiter=' ')
        sim_list = list(sim_array.T)
        # print(sim_list)
        ageingParentSettings = sim_list[0]
        careProbSettings = sim_list[1]
        retiredHoursSettings = sim_list[2]
        retiredAgeSettings = sim_list[3]
        # print(ageingParentSettings)
        # print(careProbSettings)
        # print(retiredHoursSettings)
        # print(retiredAgeSettings)
        sensitivityRun('LPtau', ageingParentSettings, careProbSettings, retiredHoursSettings, retiredAgeSettings, args.lptau)
    elif args.maximin:
        sim_array = np.genfromtxt('latinhypercube-4params.txt', delimiter=' ')
        sim_list = list(sim_array.T)
        # print(sim_list)
        ageingParentSettings = sim_list[0]
        careProbSettings = sim_list[1]
        retiredHoursSettings = sim_list[2]
        retiredAgeSettings = sim_list[3]
        # print(ageingParentSettings)
        # print(careProbSettings)
        # print(retiredHoursSettings)
        # print(retiredAgeSettings)
        sensitivityRun('Maximin', ageingParentSettings, careProbSettings, retiredHoursSettings, retiredAgeSettings, args.maximin)
    elif args.bigly:
        sim_array = np.genfromtxt('latinhypercube-22params.txt', delimiter=' ')
        sim_list = list(sim_array.T)
        #print(sim_list)
        np.savetxt('hypercube22_GEMSA_inputs.txt', sim_array, fmt='%1.8f', delimiter='\t', newline='\n')
        sensitivityLarge('hypercube22', sim_list, args.bigly)
    elif args.tenparams:
        sim_array = np.genfromtxt('lptau10-1600runsfull.txt', delimiter='\t')
        sim_list = list(sim_array.T)
        #print(sim_list)
        np.savetxt('LPtau1600runs_GEMSA_inputs.txt', sim_array, fmt='%1.8f', delimiter='\t', newline='\n')
        sensitivityTenParams('LPtau1600runs', sim_list, args.tenparams)

    else:
        basicRun(p)
    return dict
    
# Load the default values, overwriting and adding to the initial p values
loadParamFile("default.json", p)

# Load values based upon the command line file passed (if any).
loadCommandLine (p)
#print ("p = {}".format(p))