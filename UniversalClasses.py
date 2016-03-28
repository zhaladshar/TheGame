class Requirement:
    def __init__(self, objectToCheck, logicalCheck, condition):
        self.objectToCheck = objectToCheck
        self.logicalCheck = logicalCheck
        self.condition = condition

    def isRequirementMet(self):
        if self.logicalCheck == "=":
            return self.objectToCheck == eval(self.condition)
        elif self.logicalCheck == ">":
            return self.objectToCheck > eval(self.condition)
        elif self.logicalCheck == ">=":
            return self.objectToCheck >= eval(self.condition)
        elif self.logicalCheck == "!=":
            return self.objectToCheck != eval(self.condition)
        elif self.logicalCheck == "<":
            return self.objectToCheck < eval(self.condition)
        elif self.logicalCheck == "<=":
            return self.objectToCheck <= eval(self.condition)
        else:
            return "ERROR"

class Quest:
    def __init__(self, description, status):
        self.description = description
        self.status = active
        self.requirementsToStart = []
        self.requirementsToEnd = []

    def addRequirement(self, requirement):
        self.requirements.append(requirement)

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
