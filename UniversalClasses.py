import threading
import constants
import time

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
    def __init__(self, idNum, description, storyQuest, status=constants.QST_NOT_START):
        self.idNum = idNum
        self.description = description
        self.status = status
        self.storyQuest = storyQuest
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

    def start(self):
        self.status = constants.QST_START

    def complete(self):
        self.status = constants.QST_DONE

class Artifact:
    def __init__(self, name, has=0):
        self.name = name
        self.owned = bool(has)

    def has(self, hasInt):
        self.owned = bool(hasInt)

class QueueManager(threading.Thread):
    def __init__(self):
        super().__init__()
        self.list = []
        self.die = False

    def checkForCompletion(self):
        for item in self.list:
            if item.evaluate() == True:
                print("Item done")
                item.execFuncs()
                self.remove(item)
            else:
                print("Not done")

    def add(self, item):
        self.list.append(item)

    def remove(self, item):
        self.list.pop(self.list.index(item))

    def run(self):
        while True:
            if self.die == True:
                return
         
            self.checkForCompletion()
            time.sleep(3)

    def kill(self):
        self.die = True

    def join(self):
        self.kill()
        super().join()
      
    def cancel(self):
        self.thread.cancel()

if __name__ == "__main__":
    class Test:
        def __init__(self):
            self.a = 1
    class QMItem:
        def __init__(self, obj, subobj, func, list_):
            self.objectToChk = obj
            self.subObjectToChk = subobj
            self.funcToEval = func
            self.funcsToDoOnTrue = list_
        def evaluate(self):
            return getattr(self.objectToChk, self.funcToEval)("start")
        def execFuncs(self):
            for func in self.funcsToDoOnTrue:
                func()
    t = Test()
    
    q = Quest("Pray 5 times at a shrine", constants.QST_NOT_START)
    req = Requirement(t, "a", "=", "2")
    q.addRequirement("start", req)

    qmi = QMItem(q, q.requirementsMet.__name__, q.requirementsMet.__name__, [q.start])
    qm = QueueManager()
    qm.add(qmi)
    qm.start()
    #t = threading.Timer(5, qm.checkForCompletion)
    #t.start()
