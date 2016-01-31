class Attribute:
    def __init__(self, name, exp, value):
        self.name = name
        self.exp = exp
        self.value = value

    def __str__(self):
        string = self.name + "\n" + "Level: " + str(self.value) + "\n" + "Exp: " + str(self.exp)
        return string

    def expToLevelUp(self):
        return 1000

    def expUp(self, exp):
        self.exp += exp

        if self.exp >= self.expToLevelUp():
            self.levelUp()
            
    def levelUp(self):
        self.value += 1
        self.exp -= self.expToLevelUp()
        
class Player:
    def __init__(self):
        self.viewables = ["Attributes", "Skills"]
        self.attributes = {}
        self.skills = {}
        self.zones = {}

    def addAttribute(self, attribute):
        self.attributes[attribute.name] = attribute

    def addSkill(self, skill):
        self.skills[skill.name] = skill

    def addZone(self, zone):
        self.zones[zone.name] = zone
