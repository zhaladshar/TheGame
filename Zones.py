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
    def __init__(self, description, mainActionFg, performanceCount=0):
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
    def __init__(self, name, lvl=0, exp=0, unlocked=0):
        self.name = name
        self.lvl = lvl
        self.exp = exp
        self.unlocked = bool(unlocked)
        self.actions = ActionDict()
        self.results = {}
        self.lastResult = None
        self.appearance = None
        
    def addAction(self, action):
        self.actions[action.description] = action

    def addResult(self, result):
        self.results[result.description] = result

    def act(self, actionToExecuteText):
        self.appearance = None
        self.actions[actionToExecuteText].incrementCount()
        self.lastResult = self.actions[actionToExecuteText].getResult()

    def generateItemDrop(self, actionExecutedText, dbGameCursor):
        dbGameCursor.execute("""SELECT ZonesItemDrop.ItemIdNum, Items.Name
                            FROM ZonesItemDrop
                            JOIN Items ON ZonesItemDrop.ItemIdNum = Items.ItemId
                            WHERE Zone=? AND Action=?""",
                         (self.name, actionExecutedText))
        
        dropList = []
        for itemId, itemName in dbGameCursor:
            dropList.append((itemId, itemName))
        
        randomNum = random.randint(0, len(dropList) - 1)
        randomQty = random.randint(1, 4)
        
        return (randomQty, dropList[randomNum])

    def generateAnimal(self, actionExecutedText, dbGameCursor):
        dbGameCursor.execute("""SELECT ZonesItemDrop.ItemIdNum, Items.Name
                            FROM ZonesItemDrop
                            LEFT OUTER JOIN ItemsCategories
                            ON ZonesItemDrop.ItemIdNum = ItemsCategories.ItemId
                            LEFT OUTER JOIN Items
                            ON ZonesItemDrop.ItemIdNum = Items.ItemId
                            WHERE ZonesItemDrop.Zone=?  AND ZonesItemDrop.Action=? AND ItemsCategories.Category=?""",
                         (self.name, actionExecutedText, constants.ITM_CAT_ANIMAL))
        dropList = []
        for animalId, animalName in dbGameCursor:
            dropList.append((animalId, animalName))
        
        randomNum = random.randint(0, len(dropList) - 1)

        return dropList[randomNum]
    
    def generateCoinDrop(self):
        return random.randint(self.lvl, 5 * self.lvl)
