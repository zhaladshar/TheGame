class Requirement:
    def __init__(self, objectToCheck, condition):
        self.objectToCheck = objectToCheck
        self.condition = condition

def isRequirementMet(self):
    if eval(str(self.objectToCheck) + self.condition) == True:
        return True
    else:
        return False
