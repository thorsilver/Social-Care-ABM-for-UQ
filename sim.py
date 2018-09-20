
from person import Person
from person import Population
from house import House
from house import Town
from house import Map
import random
import math
import pylab
import Tkinter
import struct
import time
import sys
import pprint
import pickle
import numpy as np
# from PIL import ImageTk         
# from PIL import Image



class Sim:
    """Instantiates a single run of the simulation."""    
    def __init__ (self, params):
        self.p = params

        ## Statistical tallies
        self.times = []
        self.pops = []
        self.avgHouseholdSize = []
        self.marriageTally = 0
        self.numMarriages = []
        self.divorceTally = 0
        self.numDivorces = []
        self.totalCareDemand = []
        self.totalCareSupply = []
        self.numTaxpayers = []
        self.totalUnmetNeed = []
        self.totalFamilyCare = []
        self.totalTaxBurden = []
        self.marriageProp = []

        ## Counters and storage
        self.year = self.p['startYear']
        self.pyramid = PopPyramid(self.p['num5YearAgeClasses'],
                                  self.p['numCareLevels'])
        self.textUpdateList = []

        if self.p['interactiveGraphics']:
            self.window = Tkinter.Tk()
            self.canvas = Tkinter.Canvas(self.window,
                                    width=self.p['screenWidth'],
                                    height=self.p['screenHeight'],
                                    background=self.p['bgColour'])


    def run(self):
        """Run the simulation from year start to year end."""

        #pprint.pprint(self.p)
        #raw_input("Happy with these parameters?  Press enter to run.")

        seed = time.time()
        random.seed(seed)

        self.initializePop()
        if self.p['interactiveGraphics']:
            self.initializeCanvas()        
        for self.year in range (self.p['startYear'],
                                self.p['endYear']+1):
            self.doOneYear()
            #if self.year == self.p['thePresent']:
            #    random.seed()

        if self.p['singleRunGraphs']:
            self.doGraphs()
    
        if self.p['interactiveGraphics']:
            print "Entering main loop to hold graphics up there."
            self.window.mainloop()

        return self.totalTaxBurden[-1], seed


    def initializePop(self):
        """
        Set up the initial population and the map.
        We may want to do this from scratch, and we may want to do it
        by loading things from a pre-generated file.
        """
        ## First the map, towns, and houses

        if self.p['loadFromFile'] == False:
            self.map = Map(self.p['mapGridXDimension'],
                           self.p['mapGridYDimension'],
                           self.p['townGridDimension'],
                           self.p['cdfHouseClasses'],
                           self.p['ukMap'],
                           self.p['ukClassBias'],
                           self.p['mapDensityModifier'] )
        else:
            self.map = pickle.load(open("initMap.txt","rb"))


        ## Now the people who will live on it

        if self.p['loadFromFile'] == False:
            self.pop = Population(self.p['initialPop'],
                                  self.p['startYear'],
                                  self.p['minStartAge'],
                                  self.p['maxStartAge'])
            ## Now put the people into some houses
            ## They've already been partnered up so put the men in first, then women to follow
            men = [x for x in self.pop.allPeople if x.sex == 'male']

            remainingHouses = []
            remainingHouses.extend(self.map.allHouses)
        
            for man in men:
                man.house = random.choice(remainingHouses)
                man.sec = man.house.size  ## This may not always work, assumes house classes = SEC classes!
                self.map.occupiedHouses.append(man.house)            
                remainingHouses.remove(man.house)
                woman = man.partner
                woman.house = man.house
                woman.sec = man.sec
                man.house.occupants.append(man)
                man.house.occupants.append(woman)

        else:
            self.pop = pickle.load(open("initPop.txt","rb"))

        ## Choose one house to be the display house
        self.displayHouse = self.pop.allPeople[0].house
        self.nextDisplayHouse = None

        #reading JH's fertility projections from a CSV into a numpy array
        self.fert_data = np.genfromtxt('babyrate.txt.csv', skip_header=0, delimiter=',')

        #reading JH's fertility projections from two CSVs into two numpy arrays
        self.death_female = np.genfromtxt('deathrate.fem.csv', skip_header=0, delimiter=',')
        self.death_male = np.genfromtxt('deathrate.male.csv', skip_header=0, delimiter=',')
        

        
    def doOneYear(self):
        """Run one year of simulated time."""

        ##print "Sim Year: ", self.year, "OH count:", len(self.map.occupiedHouses), "H count:", len(self.map.allHouses)
        self.doDeaths()
        self.doCareTransitions()
        self.doAgeTransitions()
        self.doBirths()
        self.doDivorces()
        self.doMarriages()
        self.doMovingAround()
        #print("Number of alive agents: {}".format(len(self.pop.livingPeople)))
        self.pyramid.update(self.year, self.p['num5YearAgeClasses'], self.p['numCareLevels'],
                            self.p['pixelsInPopPyramid'], self.pop.livingPeople)
        self.doStats()
        if (self.p['interactiveGraphics']):
            self.updateCanvas()
        

    def doDeaths(self):
        """Consider the possibility of death for each person in the sim."""
        for person in self.pop.livingPeople:
            age = self.year - person.birthdate
            ##use the empirical rates from 1951 onwards
            if self.year > 1950:
                age = self.year - person.birthdate
                if age > 109:
                    age = 109
                if person.sex == 'male':
                    maleDieProb = self.death_male[age, self.year-1950]
                    if random.random() < maleDieProb:
                        person.dead = True
                        self.pop.livingPeople.remove(person)
                        person.house.occupants.remove(person)
                        if len(person.house.occupants) == 0:
                            self.map.occupiedHouses.remove(person.house)
                            if (self.p['interactiveGraphics']):
                                self.canvas.itemconfig(person.house.icon, state='hidden')
                        if person.partner != None:
                            person.partner.partner = None
                        if person.house == self.displayHouse:
                            messageString = str(self.year) + ": #" + str(person.id) + " died aged " + str(age) + "." 
                            self.textUpdateList.append(messageString)
                if person.sex == 'female':
                    femaleDieProb = self.death_female[age, self.year-1950]
                    if random.random() < femaleDieProb:
                        person.dead = True
                        self.pop.livingPeople.remove(person)
                        person.house.occupants.remove(person)
                        if len(person.house.occupants) == 0:
                            self.map.occupiedHouses.remove(person.house)
                            if (self.p['interactiveGraphics']):
                                self.canvas.itemconfig(person.house.icon, state='hidden')
                        if person.partner != None:
                            person.partner.partner = None
                        if person.house == self.displayHouse:
                            messageString = str(self.year) + ": #" + str(person.id) + " died aged " + str(age) + "." 
                            self.textUpdateList.append(messageString)    
        ##use made-up rates prior to 1951
        else:
                babyDieProb = 0.0
                if age < 1:
                    babyDieProb = self.p['babyDieProb']
                if person.sex == 'male':
                    ageDieProb = ( ( math.exp( age /
                                               self.p['maleAgeScaling'] ) )
                                   * self.p['maleAgeDieProb'] )
                else:
                    ageDieProb = ( ( math.exp( age /
                                               self.p['femaleAgeScaling'] ) )
                                   * self.p['femaleAgeDieProb'] )
                dieProb = self.p['baseDieProb'] + babyDieProb + ageDieProb
                    
                
        ## Can't remove from list while iterating so we need this
        self.pop.livingPeople[:] = [x for x in self.pop.livingPeople if x.dead == False]                

    def doCareTransitions(self):
        """Consider the possibility of each person coming to require care."""
        peopleNotInCriticalCare = [x for x in self.pop.livingPeople if x.careNeedLevel < self.p['numCareLevels']-1]
        for person in peopleNotInCriticalCare:
            age = self.year - person.birthdate
            if person.sex == 'male':
                ageCareProb = ( ( math.exp( age /
                                            self.p['maleAgeCareScaling'] ) )
                               * self.p['personCareProb'] )
            else:
                ageCareProb = ( ( math.exp( age /
                                           self.p['femaleAgeCareScaling'] ) )
                               * self.p['personCareProb'] )
            careProb = self.p['baseCareProb'] + ageCareProb

            if random.random() < careProb:
                multiStepTransition = random.random()
                if multiStepTransition < self.p['cdfCareTransition'][0]:
                    person.careNeedLevel += 1
                elif multiStepTransition < self.p['cdfCareTransition'][1]:
                    person.careNeedLevel += 2
                elif multiStepTransition < self.p['cdfCareTransition'][2]:
                    person.careNeedLevel += 3
                else:
                    person.careNeedLevel += 4
                if person.careNeedLevel >= self.p['numCareLevels']:
                    person.careNeedLevel = self.p['numCareLevels'] - 1
                            
                if person.house == self.displayHouse:
                    messageString = str(self.year) + ": #" + str(person.id) + " now has "
                    messageString += self.p['careLevelNames'][person.careNeedLevel] + " care needs." 
                    self.textUpdateList.append(messageString)

    def doAgeTransitions(self):
        """Check whether people have moved on to a new status in life."""
        peopleNotYetRetired = [x for x in self.pop.livingPeople if x.status != 'retired']
        for person in peopleNotYetRetired:
            age = self.year - person.birthdate
            ## Do transitions to adulthood and retirement
            if age == self.p['ageOfAdulthood']:
                person.status = 'adult at home'
                if person.house == self.displayHouse:
                    self.textUpdateList.append(str(self.year) + ": #" + str(person.id) + " is now an adult.")
            elif age == self.p['ageOfRetirement']:
                person.status = 'retired'
                if person.house == self.displayHouse:
                    self.textUpdateList.append(str(self.year) + ": #" + str(person.id) + " has now retired.")

            ## If somebody is still at home but their parents have died, promote them to independent adult
            if person.status == 'adult at home' and person.mother.dead and person.father.dead:
                person.status = 'independent adult'
                if person.house == self.displayHouse:
                    self.textUpdateList.append(str(self.year) + ": #" + str(person.id) + "'s parents are both dead.")
                    
            ## If somebody is a *child* at home and their parents have died, they need to be adopted
            if person.status == 'child' and person.mother.dead and person.father.dead:
                if person.house == self.displayHouse:
                    self.textUpdateList.append(str(self.year) + ": #" + str(person.id) + "will now be adopted.")

                while True:
                    adoptiveMother = random.choice(self.pop.livingPeople)
                    if ( adoptiveMother.status != 'child'
                         and adoptiveMother.sex == 'female'
                         and adoptiveMother.partner != None ):
                        break

                person.mother = adoptiveMother
                adoptiveMother.children.append(person)
                person.father = adoptiveMother.partner
                adoptiveMother.partner.children.append(person)                

                if adoptiveMother.house == self.displayHouse:
                    self.textUpdateList.append(str(self.year) + ": #" + str(person.id) +
                                               " has been newly adopted by " + str(adoptiveMother.id)
                                               + "." )
                self.movePeopleIntoChosenHouse(adoptiveMother.house,person.house,[person])         

    def doBirths(self):
        """For each fertile woman check whether she gives birth."""

        marriedLadies = 0
        adultLadies = 0

        womenOfReproductiveAge = [x for x in self.pop.livingPeople
                                  if x.sex == 'female'
                                  and (self.year - x.birthdate) > self.p['minPregnancyAge']
                                  and (self.year - x.birthdate) < self.p['maxPregnancyAge']
                                  and x.partner != None ]
        #counting up marriage stats
        for person in self.pop.livingPeople:
            age = self.year - person.birthdate
            if person.sex == 'female' and age >=17:
                adultLadies += 1
                if person.partner != None:
                    marriedLadies += 1

        #printing out stats for troubleshooting and sanity check
        marriedPercentage = float(marriedLadies)/float(adultLadies)
##        print "Simulation year: ", self.year
##        print "Total pop: ", len(self.pop.livingPeople)
##        print "Married ladies: ", marriedLadies
##        print "Adult ladies: ", adultLadies
##        print "Married Percentage: ", marriedPercentage
        
        for woman in womenOfReproductiveAge:
                previousChildren = woman.children
                if self.year < 1951:
                    birthProb = self.p['growingPopBirthProb']
                else:
                    birthProb = (self.fert_data[(self.year - woman.birthdate)-16,self.year-1950])/marriedPercentage
                    ##print "Birth probability is: ", birthProb
                if random.random() < birthProb:
                    baby = Person(woman, woman.partner, self.year, 'random', woman.house, woman.sec )
                    self.pop.allPeople.append(baby)
                    self.pop.livingPeople.append(baby)
                    woman.house.occupants.append(baby)
                    woman.children.append(baby)
                    woman.partner.children.append(baby)
                    if woman.house == self.displayHouse:
                        messageString = str(self.year) + ": #" + str(woman.id) + " had a baby, #" + str(baby.id) + "." 
                        self.textUpdateList.append(messageString) 


    def doDivorces(self):
        menInRelationships = [x for x in self.pop.livingPeople if x.sex == 'male' and x.partner != None ]
        for man in menInRelationships:
            age = self.year - man.birthdate 

            ## This is here to manage the sweeping through of this parameter
            ## but only for the years after 2012
            if self.year < self.p['thePresent']:
                splitProb = self.p['basicDivorceRate'] * self.p['divorceModifierByDecade'][age/10]
            else:
                splitProb = self.p['variableDivorce'] * self.p['divorceModifierByDecade'][age/10]
                
            if random.random() < splitProb:
                wife = man.partner
                man.partner = None
                wife.partner = None
                self.divorceTally += 1
                distance = random.choice(['near','far'])
                if man.house == self.displayHouse:
                    messageString = str(self.year) + ": #" + str(man.id) + " splits with #" + str(wife.id) + "."
                    self.textUpdateList.append(messageString)
                self.findNewHouse([man],distance)
                

    def doMarriages(self):
        """
        Marriages were originally intended to be done locally, i.e.,
        there would be an annual matchmaking process within each town.
        But the population per town can be so low that this made
        marriages really hard to arrange. An Allee effect for humans,
        basically.  So marriages are sorted out with the entire
        population as a mating pool.
        """
        eligibleMen = []
        eligibleWomen = []

        for i in self.pop.livingPeople:
            if i.status != 'child' and i.partner == None:
                if i.sex == 'male':
                    eligibleMen.append(i)
                else:
                    eligibleWomen.append(i)


        if len(eligibleMen) > 0 and len (eligibleWomen) > 0:
            random.shuffle(eligibleMen)
            random.shuffle(eligibleWomen)

            interestedWomen = []
            for w in eligibleWomen:
                womanAge = self.year - w.birthdate
                womanMarriageProb = ( self.p['basicFemaleMarriageProb']
                                      * self.p['femaleMarriageModifierByDecade'][womanAge/10] )
                if random.random() < womanMarriageProb:
                    interestedWomen.append(w)

            for m in eligibleMen:
                manAge = self.year - m.birthdate
                manMarriageProb = ( self.p['basicMaleMarriageProb']
                                    * self.p['maleMarriageModifierByDecade'][manAge/10] )
                if ( random.random() < manMarriageProb ):
                    for w in interestedWomen:
                        womanAge = self.year - w.birthdate
                        diff = manAge - womanAge
                        if ( diff < 20 and diff > -5
                             and m.mother != w.mother ):
                            m.partner = w
                            w.partner = m
                            interestedWomen.remove(w)
                            self.marriageTally += 1
                            if m.house == self.displayHouse or w.house == self.displayHouse:
                                messageString = str(self.year) + ": #" + str(m.id) + " (age " + str(manAge) + ")"
                                messageString += " and #" + str(w.id) + " (age " + str(womanAge)
                                messageString += ") marry."
                                self.textUpdateList.append(messageString)
                            break
                            
                    
                
            


    def doMovingAround(self):
        """
        Various reasons why a person or family group might want to
        move around. People who are in partnerships but not living
        together are highly likely to find a place together. Adults
        still living at home might be ready to move out this year.
        Single people might want to move in order to find partners. A
        family might move at random for work reasons. Older people
        might move back in with their kids.
        """

        ## Need to keep track of this to avoid multiple moves
        for i in self.pop.livingPeople:
            i.movedThisYear = False
            
        for person in self.pop.livingPeople:
            if person.movedThisYear:
                continue

            age = self.year - person.birthdate
            ageClass = age / 10
            
            if ( person.partner != None
                 and person.house != person.partner.house ):
                ## so we have someone who lives apart from their partner...
                ## very likely they will change that
                if random.random() < self.p['probApartWillMoveTogether']:
                    peopleToMove = [person,person.partner]
                    peopleToMove += self.bringTheKids(person)
                    peopleToMove += self.bringTheKids(person.partner)
                    if random.random() < self.p['coupleMovesToExistingHousehold']:
                        myHousePop = len(person.house.occupants)
                        yourHousePop = len(person.partner.house.occupants)
                        if yourHousePop < myHousePop:
                            targetHouse = person.partner.house
                        else:
                            targetHouse = person.house
                        if person.house == self.displayHouse:
                            messageString = str(self.year) + ": #" + str(person.id) + " and #" + str(person.partner.id)
                            messageString += " move to existing household."
                            self.textUpdateList.append(messageString)
                        self.movePeopleIntoChosenHouse(targetHouse,person.house,peopleToMove)                        
                    else:
                        distance = random.choice(['here','near'])
                        if person.house == self.displayHouse:
                            messageString = str(self.year) + ": #" + str(person.id) + " moves out to live with #" + str(person.partner.id)
                            if len(peopleToMove) > 2:
                                messageString += ", bringing the kids"
                            messageString += "."
                            self.textUpdateList.append(messageString)
                        self.findNewHouse(peopleToMove,distance)                        

                    if person.status == 'adult at home':
                        person.status = 'independent adult'
                    if person.partner.status == 'adult at home':
                        person.partner.status = 'independent adult'

            elif ( person.status == 'adult at home'
                   and person.partner == None ):
                ## a single person who hasn't left home yet
                if random.random() < ( self.p['basicProbAdultMoveOut']
                                       * self.p['probAdultMoveOutModifierByDecade'][ageClass] ):
                    peopleToMove = [person]
                    peopleToMove += self.bringTheKids(person)
                    distance = random.choice(['here','near'])
                    if person.house == self.displayHouse:
                        messageString = str(self.year) + ": #" + str(person.id) + " moves out, aged " + str(self.year-person.birthdate) + "."
                        self.textUpdateList.append(messageString)
                    self.findNewHouse(peopleToMove,distance)
                    person.status = 'independent adult'
                    

            elif ( person.status == 'independent adult'
                   and person.partner == None ):
                ## a young-ish person who has left home but is still (or newly) single
                if random.random() < ( self.p['basicProbSingleMove']
                                       * self.p['probSingleMoveModifierByDecade'][ageClass] ):
                    peopleToMove = [person]
                    peopleToMove += self.bringTheKids(person)
                    distance = random.choice(['here','near'])
                    if person.house == self.displayHouse:
                        messageString = str(self.year) + ": #" + str(person.id) + " moves to meet new people."
                        self.textUpdateList.append(messageString)
                    self.findNewHouse(peopleToMove,distance)

            elif ( person.status == 'retired'
                   and len(person.house.occupants) == 1 ):
                ## a retired person who lives alone
                for c in person.children:
                    if ( c.dead == False ):
                        distance = self.manhattanDistance(person.house.town,c.house.town)
                        distance += 1.0
                        if self.year < self.p['thePresent']:
                            mbRate = self.p['agingParentsMoveInWithKids'] / distance
                        else:
                            mbRate = self.p['variableMoveBack'] / distance
                        if random.random() < mbRate:
                            peopleToMove = [person]
                            if person.house == self.displayHouse:
                                messageString = str(self.year) + ": #" + str(person.id) + " is going to live with one of their children."
                                self.textUpdateList.append(messageString)
                            self.movePeopleIntoChosenHouse(c.house,person.house,peopleToMove)
                            break
                        

            
            elif ( person.partner != None ):
                ## any other kind of married person, e.g., a normal family with kids
                if random.random() < ( self.p['basicProbFamilyMove']
                                       * self.p['probFamilyMoveModifierByDecade'][ageClass] ):
                    peopleToMove = [person,person.partner]
                    peopleToMove += self.bringTheKids(person)
                    peopleToMove += self.bringTheKids(person.partner)
                    distance = random.choice(['here,''near','far'])
                    if person.house == self.displayHouse:
                        messageString = str(self.year) + ": #" + str(person.id) + " and #" + str(person.partner.id) + " move house"
                        if len(peopleToMove) > 2:
                            messageString += " with kids"
                        messageString += "."
                        self.textUpdateList.append(messageString)
                    self.findNewHouse(peopleToMove,distance)
                


    def manhattanDistance(self,t1,t2):
        """Calculates the distance between two towns"""
        xDist = abs(t1.x - t2.x)
        yDist = abs(t1.y - t2.y)
        return xDist + yDist


    def bringTheKids(self,person):
        """Given a person, return a list of their dependent kids who live in the same house as them."""
        returnList = []
        for i in person.children:
            if ( i.house == person.house
                 and i.status == 'child'
                 and i.dead == False ):
                returnList.append(i)
        return returnList


    def findNewHouse(self,personList,preference):
        """Find an appropriate empty house for the named person and put them in it."""

        newHouse = None
        person = personList[0]
        departureHouse = person.house
        t = person.house.town

        if ( preference == 'here' ):
            ## Anything empty in this town of the right size?
            localPossibilities = [x for x in t.houses
                                  if len(x.occupants) < 1
                                  and person.sec == x.size ]
            if localPossibilities:
                newHouse = random.choice(localPossibilities)

        if ( preference == 'near' or newHouse == None ):
            ## Neighbouring towns?
            if newHouse == None:
                nearbyTowns = [ k for k in self.map.towns
                                if abs(k.x - t.x) <= 1
                                and abs(k.y - t.y) <= 1 ]
                nearbyPossibilities = []
                for z in nearbyTowns:
                    for w in z.houses:
                        if len(w.occupants) < 1 and person.sec == w.size:
                            nearbyPossibilities.append(w)
                if nearbyPossibilities:
                    newHouse = random.choice(nearbyPossibilities)

        if ( preference == 'far' or newHouse == None ):
            ## Anywhere at all?
            if newHouse == None:
                allPossibilities = []
                for z in self.map.allHouses:
                    if len(z.occupants) < 1 and person.sec == z.size:
                        allPossibilities.append(z)
                if allPossibilities:
                    newHouse = random.choice(allPossibilities)

        ## Quit with an error message if we've run out of houses
        if newHouse == None:
            print "No houses left for person of SEC " + str(person.sec)
            sys.exit()

        ## Actually make the chosen move
        self.movePeopleIntoChosenHouse(newHouse,departureHouse,personList)


    def movePeopleIntoChosenHouse(self,newHouse,departureHouse,personList):

        ## Put the new house onto the list of occupied houses if it was empty
        
        ## Move everyone on the list over from their former house to the new one
        for i in personList:
            oldHouse = i.house
            oldHouse.occupants.remove(i)
            if len(oldHouse.occupants) ==  0:
                self.map.occupiedHouses.remove(oldHouse)
                ##print "This house is now empty: ", oldHouse
                if (self.p['interactiveGraphics']):
                    self.canvas.itemconfig(oldHouse.icon, state='hidden')

            newHouse.occupants.append(i)
            i.house = newHouse
            i.movedThisYear = True

        ## This next is sloppy and will lead to loads of duplicates in the
        ## occupiedHouses list, but we don't want to miss any -- that's
        ## much worse -- and the problem will be solved by a conversion
        ## to set and back to list int he stats method in a moment

        self.map.occupiedHouses.append(newHouse)
        if (self.p['interactiveGraphics']):
            self.canvas.itemconfig(newHouse.icon, state='normal')

            
            
        ## Check whether we've moved into the display house
        if newHouse == self.displayHouse:
            self.textUpdateList.append(str(self.year) + ": New people are moving into " + newHouse.name)
            messageString = ""
            for k in personList:
                messageString += "#" + str(k.id) + " "
            self.textUpdateList.append(messageString)
            
                
        ## or out of it...
        if departureHouse == self.displayHouse:
            self.nextDisplayHouse = newHouse
                

    def doStats(self):
        """Calculate annual stats and store them appropriately."""

        self.times.append(self.year)

        currentPop = len(self.pop.livingPeople)
        self.pops.append(currentPop)

        ## Check for double-included houses by converting to a set and back again
        self.map.occupiedHouses = list(set(self.map.occupiedHouses))


        ## Check for overlooked empty houses
        emptyHouses = [x for x in self.map.occupiedHouses if len(x.occupants) == 0]
        for h in emptyHouses:
            self.map.occupiedHouses.remove(h)
            if (self.p['interactiveGraphics']):
                self.canvas.itemconfig(h.icon, state='hidden')

        ## Avg household size (easily calculated by pop / occupied houses)
        households = len(self.map.occupiedHouses)
        self.avgHouseholdSize.append( 1.0 * currentPop / households )

        self.numMarriages.append(self.marriageTally)
        self.marriageTally = 0
        self.numDivorces.append(self.divorceTally)            
        self.divorceTally = 0

        ## Care demand calculations: first, what's the basic demand and theoretical supply?
        totalCareDemandHours = 0
        totalCareSupplyHours = 0
        taxPayers = 0
        for person in self.pop.livingPeople:
            need = self.p['careDemandInHours'][person.careNeedLevel]
            person.careRequired = need
            totalCareDemandHours += need

            if person.status == 'child':
                supply = self.p['childHours']
            elif person.status == 'adult at home':
                supply = self.p['homeAdultHours']
                taxPayers += 1
            elif person.status == 'independent adult':
                supply = self.p['workingAdultHours']
                taxPayers += 1
            elif person.status == 'retired':
                supply = self.p['retiredHours']
            else:
                print "Shouldn't happen."
                sys.exit()

            if person.careNeedLevel > 1:
                supply = 0.0
            elif person.careNeedLevel == 1:
                supply *= self.p['lowCareHandicap']

            person.careAvailable = supply
            totalCareSupplyHours += supply
        
        self.totalCareDemand.append(totalCareDemandHours)
        self.totalCareSupply.append(totalCareSupplyHours)
        self.numTaxpayers.append(taxPayers)

        ## What actually happens to people: do they get the care they need?
        for person in self.pop.livingPeople:
            ## Can you get the care you need from your housemates?
            if person.careRequired > 0.000001:
                for donor in person.house.occupants:
                    if ( person != donor and donor.careAvailable > 0.000001 ):
                        if donor.careAvailable > person.careRequired:
                            swap = person.careRequired
                            person.careRequired = 0.0
                            donor.careAvailable -= swap
                            break
                        else:
                            swap = donor.careAvailable
                            donor.careAvailable = 0.0
                            person.careRequired -= swap
                            
            ## Can you get the care you need from your children if they live in the same town?
            if person.careRequired > 0.000001:
                for donor in person.children:
                    if ( person.house.town == donor.house.town and donor.careAvailable > 0.000001
                         and donor.dead == False ):
                        if donor.careAvailable > person.careRequired:
                            swap = person.careRequired
                            person.careRequired = 0.0
                            donor.careAvailable -= swap
                            break
                        else:
                            swap = donor.careAvailable
                            donor.careAvailable = 0.0
                            person.careRequired -= swap

        ## Now tally up the care situation, how much need is unmet, because that's the state's burden
        unmetNeed = 0.0
        for person in self.pop.livingPeople:
            unmetNeed += person.careRequired

        self.totalUnmetNeed.append(unmetNeed)

        if totalCareDemandHours == 0:
            familyCareRatio = 0.0
        else:
            familyCareRatio = ( totalCareDemandHours - unmetNeed ) / (1.0 * totalCareDemandHours)

        ##familyCareRatio = ( totalCareDemandHours - unmetNeed ) / (1.0 * (totalCareDemandHours+0.01))
        self.totalFamilyCare.append(familyCareRatio)

        taxBurden = ( unmetNeed * self.p['hourlyCostOfCare'] * 52.18 ) / ( taxPayers * 1.0 )
        self.totalTaxBurden.append(taxBurden)

        ## Count the proportion of adult women who are married
        totalAdultWomen = 0
        totalMarriedAdultWomen = 0

        for person in self.pop.livingPeople:
            age = self.year - person.birthdate
            if person.sex == 'female' and age >= 18:
                totalAdultWomen += 1
                if person.partner != None:
                    totalMarriedAdultWomen += 1
        marriagePropNow = float(totalMarriedAdultWomen) / float(totalAdultWomen)
        self.marriageProp.append(marriagePropNow)

        ## Some extra debugging stuff just to check that all
        ## the lists are behaving themselves
        if self.p['verboseDebugging']:
            peopleCount = 0
            for i in self.pop.allPeople:
                if i.dead == False:
                    peopleCount += 1
            print "True pop counting non-dead people in allPeople list = ", peopleCount

            peopleCount = 0
            for h in self.map.occupiedHouses:
                peopleCount += len(h.occupants)
            print "True pop counting occupants of all occupied houses = ", peopleCount

            peopleCount = 0
            for h in self.map.allHouses:
                peopleCount += len(h.occupants)
            print "True pop counting occupants of ALL houses = ", peopleCount

            tally = [ 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            for h in self.map.occupiedHouses:
                tally[len(h.occupants)] += 1
            for i in range(len(tally)):
                if tally[i] > 0:
                    print i, tally[i]
            print

            

        
        
                
    def initializeCanvas(self):
        """Put up a TKInter canvas window to animate the simulation."""
        self.canvas.pack()

        ## Draw some numbers for the population pyramid that won't be redrawn each time
        for a in range(0,self.p['num5YearAgeClasses']):
            self.canvas.create_text(170, 385 - (10 * a),
                                    text=str(5*a) + '-' + str(5*a+4),
                                    font='Helvetica 6',
                                    fill='white')

        ## Draw the overall map, including towns and houses (occupied houses only)
        for t in self.map.towns:
            xBasic = 580 + (t.x * self.p['pixelsPerTown'])
            yBasic = 15 + (t.y * self.p['pixelsPerTown'])
            self.canvas.create_rectangle(xBasic, yBasic,
                                         xBasic+self.p['pixelsPerTown'],
                                         yBasic+self.p['pixelsPerTown'],
                                         outline='grey',
                                         state = 'hidden' )

        for h in self.map.allHouses:
            t = h.town
            xBasic = 580 + (t.x * self.p['pixelsPerTown'])
            yBasic = 15 + (t.y * self.p['pixelsPerTown'])
            xOffset = xBasic + 2 + (h.x * 2)
            yOffset = yBasic + 2 + (h.y * 2)

            outlineColour = fillColour = self.p['houseSizeColour'][h.size]
            width = 1

            h.icon = self.canvas.create_rectangle(xOffset,yOffset,
                                                  xOffset + width, yOffset + width,
                                                  outline=outlineColour,
                                                  fill=fillColour,
                                                  state = 'normal' )

        self.canvas.update()
        time.sleep(0.5)
        self.canvas.update()

        for h in self.map.allHouses:
            self.canvas.itemconfig(h.icon, state='hidden')

        for h in self.map.occupiedHouses:
            self.canvas.itemconfig(h.icon, state='normal')

        self.canvas.update()
        self.updateCanvas()

    def updateCanvas(self):
        """Update the appearance of the graphics canvas."""

        ## First we clean the canvas off; some items are redrawn every time and others are not
        self.canvas.delete('redraw')

        ## Now post the current year and the current population size
        self.canvas.create_text(self.p['dateX'],
                                self.p['dateY'],
                                text='Year: ' + str(self.year),
                                font = self.p['mainFont'],
                                fill = self.p['fontColour'],
                                tags = 'redraw')
        self.canvas.create_text(self.p['popX'],
                                self.p['popY'],
                                text='Pop: ' + str(len(self.pop.livingPeople)),
                                font = self.p['mainFont'],
                                fill = self.p['fontColour'],
                                tags = 'redraw')

        self.canvas.create_text(self.p['popX'],
                                self.p['popY'] + 30,
                                text='Ever: ' + str(len(self.pop.allPeople)),
                                font = self.p['mainFont'],
                                fill = self.p['fontColour'],
                                tags = 'redraw')

        ## Also some other stats, but not on the first display
        if self.year > self.p['startYear']:
            self.canvas.create_text(350,20,
                                    text='Avg household: ' + str ( round ( self.avgHouseholdSize[-1] , 2 ) ),
                                    font = 'Helvetica 11',
                                    fill = 'white',
                                    tags = 'redraw')
            self.canvas.create_text(350,40,
                                    text='Marriages: ' + str(self.numMarriages[-1]),
                                    font = 'Helvetica 11',
                                    fill = 'white',
                                    tags = 'redraw')
            self.canvas.create_text(350,60,
                                    text='Divorces: ' + str(self.numDivorces[-1]),
                                    font = 'Helvetica 11',
                                    fill = 'white',
                                    tags = 'redraw')
            self.canvas.create_text(350,100,
                                    text='Total care demand: ' + str(round(self.totalCareDemand[-1], 0 ) ),
                                    font = 'Helvetica 11',
                                    fill = 'white',
                                    tags = 'redraw')
            self.canvas.create_text(350,120,
                                    text='Num taxpayers: ' + str(round(self.numTaxpayers[-1], 0 ) ),
                                    font = 'Helvetica 11',
                                    fill = 'white',
                                    tags = 'redraw')
            self.canvas.create_text(350,140,
                                    text='Family care ratio: ' + str(round(100.0 * self.totalFamilyCare[-1], 0 ) ) + "%",
                                    font = 'Helvetica 11',
                                    fill = 'white',
                                    tags = 'redraw')
            self.canvas.create_text(350,160,
                                    text='Tax burden: ' + str(round(self.totalTaxBurden[-1], 0 ) ),
                                    font = 'Helvetica 11',
                                    fill = 'white',
                                    tags = 'redraw')
            self.canvas.create_text(350,180,
                                    text='Marriage prop: ' + str(round(100.0 * self.marriageProp[-1], 0 ) ) + "%",
                                    font = 'Helvetica 11',
                                    fill = self.p['fontColour'],
                                    tags = 'redraw')

        

        ## Draw the population pyramid split by care categories
        for a in range(0,self.p['num5YearAgeClasses']):
            malePixel = 153
            femalePixel = 187
            for c in range(0,self.p['numCareLevels']):
                mWidth = self.pyramid.maleData[a,c]
                fWidth = self.pyramid.femaleData[a,c]

                if mWidth > 0:
                    self.canvas.create_rectangle(malePixel, 380 - (10*a),
                                                 malePixel - mWidth, 380 - (10*a) + 9,
                                                 outline=self.p['careLevelColour'][c],
                                                 fill=self.p['careLevelColour'][c],
                                                 tags = 'redraw')
                malePixel -= mWidth
                
                if fWidth > 0:
                    self.canvas.create_rectangle(femalePixel, 380 - (10*a),
                                                 femalePixel + fWidth, 380 - (10*a) + 9,
                                                 outline=self.p['careLevelColour'][c],
                                                 fill=self.p['careLevelColour'][c],
                                                 tags = 'redraw')
                femalePixel += fWidth

        ## Draw in the display house and the people who live in it
        if len(self.displayHouse.occupants) < 1:
            ## Nobody lives in the display house any more, choose another
            if self.nextDisplayHouse != None:
                self.displayHouse = self.nextDisplayHouse
                self.nextDisplayHouse = None
            else:
                self.displayHouse = random.choice(self.pop.livingPeople).house
                self.textUpdateList.append(str(self.year) + ": Display house empty, going to " + self.displayHouse.name + ".")
                messageString = "Residents: "
                for k in self.displayHouse.occupants:
                    messageString += "#" + str(k.id) + " "
                self.textUpdateList.append(messageString)
            

        outlineColour = self.p['houseSizeColour'][self.displayHouse.size]
        self.canvas.create_rectangle( 50, 450, 300, 650,
                                      outline = outlineColour,
                                      tags = 'redraw' )
        self.canvas.create_text ( 60, 660,
                                  text="Display house " + self.displayHouse.name,
                                  font='Helvetica 10',
                                  fill='white',
                                  anchor='nw',
                                  tags='redraw')
                                  

        ageBracketCounter = [ 0, 0, 0, 0, 0 ]

        for i in self.displayHouse.occupants:
            age = self.year - i.birthdate
            ageBracket = age / 20
            if ageBracket > 4:
                ageBracket = 4
            careClass = i.careNeedLevel
            sex = i.sex
            idNumber = i.id
            self.drawPerson(age,ageBracket,ageBracketCounter[ageBracket],careClass,sex,idNumber)
            ageBracketCounter[ageBracket] += 1


        ## Draw in some text status updates on the right side of the map
        ## These need to scroll up the screen as time passes

        if len(self.textUpdateList) > self.p['maxTextUpdateList']:
            excess = len(self.textUpdateList) - self.p['maxTextUpdateList']
            self.textUpdateList = self.textUpdateList[excess:excess+self.p['maxTextUpdateList']]

        baseX = 1035
        baseY = 30
        for i in self.textUpdateList:
            self.canvas.create_text(baseX,baseY,
                                    text=i,
                                    anchor='nw',
                                    font='Helvetica 9',
                                    fill = 'white',
                                    width = 265,
                                    tags = 'redraw')
            baseY += 30

        ## Finish by updating the canvas and sleeping briefly in order to allow people to see it
        self.canvas.update()
        if self.p['delayTime'] > 0.0:
            time.sleep(self.p['delayTime'])


    def drawPerson(self, age, ageBracket, counter, careClass, sex, idNumber):
        baseX = 70 + ( counter * 30 )
        baseY = 620 - ( ageBracket * 30 )

        fillColour = self.p['careLevelColour'][careClass]

        self.canvas.create_oval(baseX,baseY,baseX+6,baseY+6,
                                fill=fillColour,
                                outline=fillColour,tags='redraw')
        if sex == 'male':
            self.canvas.create_rectangle(baseX-2,baseY+6,baseX+8,baseY+12,
                                fill=fillColour,outline=fillColour,tags='redraw')
        else:
            self.canvas.create_polygon(baseX+2,baseY+6,baseX-2,baseY+12,baseX+8,baseY+12,baseX+4,baseY+6,
                                fill=fillColour,outline=fillColour,tags='redraw')
        self.canvas.create_rectangle(baseX+1,baseY+13,baseX+5,baseY+20,
                                     fill=fillColour,outline=fillColour,tags='redraw')
            
            
            
        self.canvas.create_text(baseX+11,baseY,
                                text=str(age),
                                font='Helvetica 6',
                                fill='white',
                                anchor='nw',
                                tags='redraw')
        self.canvas.create_text(baseX+11,baseY+8,
                                text=str(idNumber),
                                font='Helvetica 6',
                                fill='grey',
                                anchor='nw',
                                tags='redraw')


    def doGraphs(self):
        """Plot the graphs needed at the end of one run."""

        p1, = pylab.plot(self.times,self.pops,color="red")
        p2, = pylab.plot(self.times,self.numTaxpayers,color="blue")
        pylab.legend([p1, p2], ['Total population', 'Taxpayers'],loc='lower right')
        pylab.xlim(xmin=self.p['statsCollectFrom'])
        pylab.ylabel('Number of people')
        pylab.xlabel('Year')
        pylab.savefig('popGrowth.pdf')
        pylab.show()

        
        pylab.plot(self.times,self.avgHouseholdSize,color="red")
        pylab.xlim(xmin=self.p['statsCollectFrom'])
        pylab.ylabel('Average household size')
        pylab.xlabel('Year')
        pylab.savefig('avgHousehold.pdf')
        pylab.show()

##        pylab.plot(self.times,self.numMarriages)
##        pylab.ylabel('Number of marriages')
##        pylab.xlabel('Year')
##        pylab.savefig('numMarriages.pdf')
##
##        pylab.plot(self.times,self.numDivorces)
##        pylab.ylabel('Number of divorces')
##        pylab.xlabel('Year')
##        pylab.savefig('numDivorces.pdf')

        p1, = pylab.plot(self.times,self.totalCareDemand,color="red")
        p2, = pylab.plot(self.times,self.totalCareSupply,color="blue")
        pylab.xlim(xmin=self.p['statsCollectFrom'])
        pylab.legend([p1, p2], ['Care demand', 'Total theoretical supply'],loc='lower right')
        pylab.ylabel('Total hours per week')
        pylab.xlabel('Year')
        pylab.savefig('totalCareSituation.pdf')
        pylab.show()

        pylab.plot(self.times,self.totalFamilyCare,color="red")
        pylab.xlim(xmin=self.p['statsCollectFrom'])
        pylab.ylabel('Proportion of informal social care')
        pylab.xlabel('Year')
        pylab.savefig('informalCare.pdf')
        pylab.show()


        pylab.plot(self.times,self.totalTaxBurden,color="red")
        pylab.xlim(xmin=self.p['statsCollectFrom'])
        pylab.ylabel('Care costs in pounds per taxpayer per year')
        pylab.xlabel('Year')
        pylab.savefig('taxBurden.pdf')
        pylab.show()

        pylab.plot(self.times,self.marriageProp,color="red")
        pylab.xlim(xmin=self.p['statsCollectFrom'])
        pylab.ylabel('Proportion of married adult women')
        pylab.xlabel('Year')
        pylab.savefig('marriageProp.pdf')
        pylab.savefig('marriageProp.png')
        pylab.show()



class PopPyramid:
    """Builds a data object for storing population pyramid data in."""
    def __init__ (self, ageClasses, careLevels):
        self.maleData = pylab.zeros((ageClasses,careLevels),dtype=int)
        self.femaleData = pylab.zeros((ageClasses, careLevels),dtype=int)

    def update(self, year, ageClasses, careLevels, pixelFactor, people):
        ## zero the two arrays
        for a in range (ageClasses):
            for c in range (careLevels):
                self.maleData[a,c] = 0
                self.femaleData[a,c] = 0
        ## tally up who belongs in which category
        for i in people:
            ageClass = ( year - i.birthdate ) / 5
            if ageClass > ageClasses - 1:
                ageClass = ageClasses - 1
            careClass = i.careNeedLevel
            if i.sex == 'male':
                self.maleData[ageClass,careClass] += 1
            else:
                self.femaleData[ageClass,careClass] += 1

        ## normalize the totals into pixels
        total = len(people)        
        for a in range (ageClasses):
            for c in range (careLevels):
                self.maleData[a,c] = pixelFactor * self.maleData[a,c] / total
                self.femaleData[a,c] = pixelFactor * self.femaleData[a,c] / total
