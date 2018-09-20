
import random

class Person:
    """The person class stores information about a person in the sim."""
    counter = 1
    def __init__ (self, mother, father, birthYear, sex, house, sec):
        self.mother = mother
        self.father = father
        self.children = []
        self.birthdate = birthYear
        self.careNeedLevel = 0
        self.dead = False
        self.partner = None
        if sex == 'random':
            self.sex = random.choice(['male', 'female'])
        else:
            self.sex = sex
        self.house = house
        self.sec = sec
        self.status = 'child'
        self.careRequired = 0
        self.careAvailable = 0
        self.movedThisYear = False
        self.id = Person.counter
        Person.counter += 1

class Population:
    """The population class stores a collection of persons."""
    def __init__ (self, initial, startYear,
                  minStartAge, maxStartAge):
        self.allPeople = []
        self.livingPeople = []
        for i in range(initial / 2):
            birthYear = startYear - random.randint(minStartAge,maxStartAge)
            newMan = Person(None, None,
                            birthYear, 'male', None, None )
            newWoman = Person(None, None,
                              birthYear, 'female', None, None )

            newMan.status = 'independent adult'
            newWoman.status = 'independent adult'
            
            newMan.partner = newWoman
            newWoman.partner = newMan
            
            self.allPeople.append(newMan)
            self.livingPeople.append(newMan)
            self.allPeople.append(newWoman)
            self.livingPeople.append(newWoman)

            
