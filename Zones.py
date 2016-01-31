import random

import Requirements
import constants

class ActionDict(dict):
    def __init__(self):
        super().__init__()

    def getMainActions(self):
        actionList = []
        for actionKey in self:
            if self[actionKey].mainAction == 1:
                actionList.append(self[actionKey])
        return actionList
    
class Action:
    def __init__(self, description, mainAction):
        self.description = description
        self.mainAction = mainAction
        self.results = []
        self.failedResult = None
        self.requirements = []
        self.attributesImproved = []

    def addResult(self, result):
        if result.likelihood == -1:
            self.failedResult = result
        else:
            self.results.append(result)

    def addRequirement(self, requirement):
        self.requirements.append(requirement)

    def addAttributeImproved(self, attributeImproved):
        self.attributesImproved.append(attributeImproved)

    def getResult(self):
        randomNum = random.uniform(0, 1)
        interval = 0.0
        intervalList = []
        
        # Build interval list of 2-tuple, where the name of the result is the
        # first element and the cumulative interval is the second element.
        for resultNum in range(len(self.results)):
            interval += self.results[resultNum].likelihood
            intervalList.append(interval)
        
        # Find where randomNum falls in the intervalList. This will correspond
        # to the position of the result. If result is -1, use the fail result.
        result = -1
        for intervalNum in range(len(intervalList)):
            if randomNum <= intervalList[intervalNum] and result == -1:
                result = intervalNum
        
        if result == -1:
            return self.failedResult
        else:
            return self.results[result]
        
class Result:
    def __init__(self, description, likelihood, maxLikelihood):
        self.description = description
        self.likelihood = likelihood
        self.maxLikelihood = maxLikelihood
        self.actions = []

    def addAction(self, action):
        self.actions.append(action)

class Zone:
    def __init__(self, name, level, exp, unlocked):
        self.name = name
        self.level = level
        self.exp = exp
        if unlocked == 0:
            self.unlocked = False
        else:
            self.unlocked = True
        self.actions = ActionDict()
        self.results = {}
        self.lastResult = None
        
    def addAction(self, action):
        self.actions[action.description] = action

    def addResult(self, result):
        self.results[result.description] = result

    def act(self, actionToExecuteText):
        self.lastResult = self.actions[actionToExecuteText].getResult()

if __name__ == "__main__":
    random.seed()
    
    forest = Zone("Forest", 1, 0)
    
    wander = Action("Wander")
    forage = Action("Forage")
    climb = Action("Climb")
    chop = Action("Chop")
    makeTown = Action("Make a town")
    drink = Action("Drink")
    soakFeet = Action("Soak Feet")
    lookAtOneself = Action("Look at yourself")
    pray = Action("Pray")
    follow = Action("Follow")
    trap = Action("Trap")

    wander_res1 = Result("Found a tree", .10, .25)
    wander_res2 = Result("Found a clearing", 0.005, 0.005)
    wander_res3 = Result("Found a stream", .07, .15)
    wander_res4 = Result("Found a shrine", .025, .05)
    wander_resfail = Result("Found nothing exciting", 1, 1)
    forage_res1 = Result("Found food/item", .15, .15)
    forage_res2 = Result("Found tracks", .01, .01)
    forage_resfail = Result("Found nothing", 1, 1)
    follow_res1 = Result("Found an animal", .2, .2)
    climb_res1 = Result("Found food/item", .1, .1)
    lookAtOneself_res1 = Result("Found a coin", .2, .2)

    wander.addResult(wander_res1)
    wander.addResult(wander_res2)
    wander.addResult(wander_res3)
    wander.addResult(wander_res4)
    wander.addFailedResult(wander_resfail)
    forage.addResult(forage_res1)
    forage.addResult(forage_res2)
    forage.addFailedResult(forage_resfail)
    follow.addResult(follow_res1)
    climb.addResult(climb_res1)
    lookAtOneself.addResult(lookAtOneself_res1)
    
    forest.addAction(wander)
    forest.addAction(forage)
    wander_res1.addAction(climb)
    wander_res1.addAction(chop)
    wander_res2.addAction(makeTown)
    wander_res3.addAction(drink)
    wander_res3.addAction(soakFeet)
    wander_res3.addAction(lookAtOneself)
    wander_res4.addAction(pray)
    follow_res1.addAction(trap)
