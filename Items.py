class Milestone:
	def __init__(self, name, ttComp, canColl, collUsesUp):
		self.name = name

		if ttComp < 0:
			self.timeToCompletion = float("inf")
		else:
			self.timeToCompletion = ttComp

		self.canCollect = canColl
		self.collectionUsesUp = collUsesUp
		self.attributes = []

	def printMilestone(self):
		print("('" + self.name + "'", self.timeToCompletion, self.canCollect, str(self.collectionUsesUp) + ") ", end ="")

	def addAttributes(self, itemGenId, itemGenQty, itemGenTime, itemFailId):
		self.attributes.append((itemGenId, itemGenQty, itemGenTime, itemFailId))

class Item:
    def __init__(self, idNum, name, qty=None):
        self.idNum = idNum
        self.name = name
        if qty == "" or qty == None:
            self.qty = 0
        else:
            self.qty = qty
        self.inherents = []
        self.components = {}
        self.milestones = {}

    def addInherent(self, inherent):
        self.inherents.append(inherent)

    def addMilestone(self, inherent, milestone):
        if inherent not in self.milestones.keys():
            self.milestones[inherent] = []

        self.milestones[inherent].append(milestone)

    def addMilestoneAttributes(self, inherent, milestone, itemProduced, qtyProduced, timeToProduce, itemFailed):
        for each in self.milestones[inherent]:
            if each.name == milestone:
                each.addAttributes(itemProduced, qtyProduced, timeToProduce, itemFailed)

    def addComponent(self, inherent, componentId, componentQty):
        if inherent not in self.components.keys():
            self.components[inherent] = {}
        
        self.components[inherent][componentId] = componentQty

    def printItem(self):
        print("Name:", self.name)
        print("Qty:", self.qty)
        print("Inherents:", self.inherents)
        if self.milestones.keys():
            print("Milestones: ", end="")
            for i in self.milestones.keys():
                print("'" + i + "': ", end="")

                for j in self.milestones[i]:
                    j.printMilestone()
                print("\n", end="")
        else:
            print("Milestones:")

        print("Milestone Attributes: ", end="")
        for i in self.milestones.keys():
            print("'" + i + "': ", end="")
            for j in self.milestones[i]:
                print("'" + j.name + "': ", end="")
                for k in j.attributes:
                    print(k, end="")
                    print(" ", end="")
        print("")

        if self.components.keys():
            print("Components: ", end="")
            for i in self.components.keys():
                print("'" + str(i) + "':", end="")

                for j in self.components[i].keys():
                    print("(%d, %s) " % (j, self.components[i][j]), end="")
        else:
            print("Components:")
