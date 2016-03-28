import random

import UniversalClasses
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
    def __init__(self, description, mainActionFg, performanceCount):
        self.description = description
        self.mainAction = mainActionFg
        self.performanceCount = performanceCount
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

    def requirementsMet(self):
        met = True
        for req in self.requirements:
            if req.isRequirementMet() == False:
                met = False
        return met
    
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

    def incrementCount(self):
        self.performanceCount += 1
        
class Result:
    def __init__(self, description, likelihood, maxLikelihood, message):
        self.description = description
        self.likelihood = likelihood
        self.maxLikelihood = maxLikelihood
        self.actions = []
        self.message = message
        self.executionScript = []

    def addAction(self, action):
        self.actions.append(action)

    def addExecutionScript(self, executionScript):
        self.executionScript.append(executionScript)

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
        self.actions[actionToExecuteText].incrementCount()
        self.lastResult = self.actions[actionToExecuteText].getResult()

    def generateItemDrop(self, actionExecutedText, dbCursor):
        dbCursor.execute("""SELECT ZonesItemDrop.ItemIdNum, Items.Name
                            FROM ZonesItemDrop
                            JOIN Items ON ZonesItemDrop.ItemIdNum = Items.ItemId
                            WHERE Zone=? AND Action=?""",
                         (self.name, actionExecutedText))
        dropList = []
        for item in dbCursor:
            dropList.append((item[0], item[1]))

        randomNum = random.randint(0, len(dropList) - 1)
        randomQty = random.randint(1, 4)

        return (randomQty, dropList[randomNum])

    def generateAnimal(self, actionExecutedText, dbCursor):
        dbCursor.execute("""SELECT """)

    def generateCoinDrop(self):
        return random.randint(self.level, 5 * self.level)
