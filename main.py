
from sim import Sim
import os
import cProfile
import pylab
import math
import matplotlib.pyplot as plt


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
    p['townGridDimension'] = 25
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

s = Sim(p)
tax = s.run()

##runs for sensitivity analysis using GEM-SA
##taxMeans = []
##taxSEs = []
##
##p['verboseDebugging'] = False
##p['singleRunGraphs'] = False
##p['interactiveGraphics'] = False
##
##dataFile = open('GEMSA data new.txt','a')
##meansFile = open('GEMSA means new.txt', 'a')
##
##agingParentList = [ 0.0, 0.1, 0.2, 0.4 ] 
##careProbList = [ 0.0004, 0.0008, 0.0012, 0.0016 ] 
##retiredHoursList = [ 20.0, 30.0, 40.0, 60.0 ] 
##retiredAgeList = [ 60.0 ]
##
##for variableCare in agingParentList:
##    for variableProb in careProbList:
##        for variableRetired in retiredHoursList:
##            for variableAge in retiredAgeList:
##                p['agingParentsMoveInWithKids'] = variableCare
##                p['personCareProb'] = variableProb
##                p['retiredHours'] = variableRetired
##                p['ageOfRetirement'] = variableAge
##                print "Trying parents-moving-in probability: ", variableCare
##                print "Trying person care probability: ", variableProb
##                print "Trying retired hours: ", variableRetired
##                print "Trying retirement age: ", variableAge
##                taxList = []
##                taxSum = 0.0
##                meansFile.write(str(variableCare) + "\t" + str(variableProb) + "\t" + str(variableRetired) + "\t" + str(variableAge) + "\t")
##                for i in range ( 0, p['numRepeats'] ):
##                    print i,
##                    s = Sim(p)
##                    tax = s.run()
##                    taxList.append(tax)
##                    taxSum += tax
##                    print tax
##                    dataFile.write(str(variableCare) + "\t" + str(variableProb) + "\t" + str(variableRetired) + "\t" + str(variableAge) + "\t" + str(tax) + "\n")    
##                taxMeans.append(pylab.mean(taxList))
##                meansFile.write(str(taxSum/p['numRepeats']) + "\n")
##                taxSEs.append(pylab.std(taxList) / math.sqrt(p['numRepeats']))
##
##dataFile.close()
##meansFile.close()

##taxMeans = []
##taxSEs = []
##
##p['verboseDebugging'] = False
##p['singleRunGraphs'] = False
##p['interactiveGraphics'] = False
##
##dataFile = open('retirementAgeData2.txt','w')
##
##agingParentList = [ 50, 55, 65, 70, 75, 80 ]
##
##for variableCare in agingParentList:
##        p['ageOfRetirement'] = variableCare
##        print "Trying retirement age: ", variableCare
##        taxList = []
##        for i in range ( 0, p['numRepeats'] ):
##            print i,
##            s = Sim(p)
##            tax = s.run()
##            taxList.append(tax)
##            print tax
##            dataFile.write(str(i) + "\t" + str(tax) + "\n")
##        taxMeans.append(pylab.mean(taxList))
##        taxSEs.append(pylab.std(taxList) / math.sqrt(p['numRepeats']))
##
##dataFile.close()
##
##indices1 = pylab.arange(len(agingParentList))
##
##taxFig = pylab.figure()
##taxBar = taxFig.add_subplot(1,1,1)
##taxBar.bar(indices1, taxMeans, facecolor='red',
##             align='center', yerr=taxSEs, ecolor='black')
##taxBar.set_ylabel('Mean social care cost per taxpayer')
##taxBar.set_xlabel('Age of retirement')
##taxBar.set_xticks(indices1)
##taxBar.set_xticklabels(agingParentList)
##pylab.savefig('retirementAgeRunSet1.pdf')
##pylab.show()







#######################################################
## A profiling run; use import pstats then p = pstats.Stats('profile.txt') then p.sort_stats('time').print_stats(10)
#cProfile.run('s.run()','profile.txt')

