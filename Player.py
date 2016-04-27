class Attribute:
    def __init__(self, idNum, name, exp=0, lvl=0):
        self.idNum = idNum
        self.name = name
        self.exp = exp
        self.lvl = lvl

    def __str__(self):
        string = self.name + "\n" + "Level: " + str(self.lvl) + "\n" + "Exp: " + str(self.exp)
        return string

    def expToLevelUp(self):
        return 1000

    def expUp(self, exp):
        self.exp += exp

        if self.exp >= self.expToLevelUp():
            self.levelUp()
            
    def levelUp(self):
        self.lvl += 1
        self.exp -= self.expToLevelUp()

class Inventory(dict):
    def __init__(self):
        super().__init__()

    def addItemToInventory(self, item):
        self[item.idNum] = item

    def invUp(self, itemId, qty):
        self[itemId].qty += qty

class Player:
    def __init__(self):
        self.attributes = {}
        self.skills = {}
        self.inventory = Inventory()
        self.zones = {}
        self.quests = {}
        self.artifacts = {}

    def addAttribute(self, attribute):
        self.attributes[attribute.name] = attribute

    def addSkill(self, skill):
        self.skills[skill.name] = skill

    def addZone(self, zone):
        self.zones[zone.name] = zone

    def addQuest(self, quest):
        self.quests[quest.idNum] = quest

    def addArtifact(self, artifact):
        self.artifacts[artifact.name] = artifact

    def addItemToInventory(self, itemId, qty):
        self.inventory.invUp(itemId, qty)
