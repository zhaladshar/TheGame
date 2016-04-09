class Requirement:
    def __init__(self, objToCheck, subObjToCheck, logicalCheck, condition):
        self.objToChk = objToCheck
        self.subObjToChk = subObjToCheck
        self.logicalCheck = logicalCheck
        self.condition = condition

    def isRequirementMet(self):
        if self.logicalCheck == "=":
            return getattr(self.objToChk, self.subObjToChk) == eval(self.condition)
        elif self.logicalCheck == ">":
            return getattr(self.objToChk, self.subObjToChk) > eval(self.condition)
        elif self.logicalCheck == ">=":
            return getattr(self.objToChk, self.subObjToChk) >= eval(self.condition)
        elif self.logicalCheck == "!=":
            return getattr(self.objToChk, self.subObjToChk) != eval(self.condition)
        elif self.logicalCheck == "<":
            return getattr(self.objToChk, self.subObjToChk) < eval(self.condition)
        elif self.logicalCheck == "<=":
            return getattr(self.objToChk, self.subObjToChk) <= eval(self.condition)
        else:
            return "ERROR"

class Quest:
    def __init__(self, description, status):
        self.description = description
        self.status = active
        self.requirementsToStart = []
        self.requirementsToEnd = []

    def addRequirement(self, startOrEnd, requirement):
        if startOrEnd == "start":
            self.requirementsToStart.append(requirement)
        else:
            self.requirementsToEnd.append(requirement)

    def requirementsMet(self, startOrEnd):
        met = True
        if startOrEnd == "start":
            requirementsList = self.requirementsToStart
        else:
            requirementsList = self.requirementsToEnd
            
        for req in requirementsList:
            if req.isRequirementMet() == False:
                met = False
        return met

class Artifact:
    def __init__(self, name, has=0):
        self.name = name
        self.owned = bool(has)

    def has(self, hasInt):
        self.owned = bool(hasInt)
