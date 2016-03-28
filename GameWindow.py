from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sqlite3
import sys
import Player
import Zones
import Items
import UniversalClasses

class EmitButton(QPushButton):
    released = pyqtSignal(str)
    
    def __init__(self, text):
        super().__init__(text)

    def mouseReleaseEvent(self, event):
        self.released.emit(self.text())

class PlayerDisplayWidget(QWidget):
    def __init__(self, valuesToDisplay):
        super().__init__()
        self.valuesToDisplay = valuesToDisplay
        self.layout = QVBoxLayout()
        
        self.buildDisplay()
        self.setLayout(self.layout)

    def buildDisplay(self):
        listOfValues = list(self.valuesToDisplay.values())
        sortedList = sorted(listOfValues, key=lambda x: x.name)

        for value in sortedList:
            label = QLabel(value.name + " - " + str(value.value) + "\nExp: " + str(value.exp) + "/" + str(value.expToLevelUp()))
            self.layout.addWidget(label)
        self.layout.addStretch(1)
            
class PersonDetailWidget(QWidget):
    def __init__(self, person):
        super().__init__()
        self.person = person

        self.layout = QVBoxLayout()
        self.selectorCombo = QComboBox()
        self.selectorCombo.addItems(self.person.viewables)
        self.viewer = PlayerDisplayWidget(self.person.attributes)

        self.layout.addWidget(self.selectorCombo)
        self.layout.addWidget(self.viewer)
        self.setLayout(self.layout)
        
class SwitcherWidget(QWidget):
    def __init__(self, person):
        super().__init__()
        self.switcher = QStackedWidget()
        self.personalDetailWidget = PersonDetailWidget(person)

        self.switcher.addWidget(self.personalDetailWidget)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.switcher)
        self.setLayout(self.layout)

class MessageTextBox(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)

class ZoneActionsBox(QWidget):
    action = pyqtSignal(str)
    
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        layout = QVBoxLayout()
        self.zoneActionLayout = QVBoxLayout()
        self.resultsActionLayout = QVBoxLayout()

        layout.addLayout(self.zoneActionLayout)
        layout.addSpacing(1)
        layout.addLayout(self.resultsActionLayout)
        layout.addStretch(1)

        self.populateZoneActions()
        self.populateResultsActions()

        self.setLayout(layout)

    def populateZoneActions(self):
        for action in self.parent.zone.actions.getMainActions():
            if action.requirementsMet() == True:
                button = EmitButton(action.description)
                button.released.connect(self.emitAction)
                self.zoneActionLayout.addWidget(button)

    def populateResultsActions(self):
        # Remove all old widgets from resultsActionLayout
        while self.resultsActionLayout.count() > 0:
            layoutItem = self.resultsActionLayout.takeAt(0)
            layoutItem.widget().deleteLater()

        # Populate resultsActionLayout with new action buttons based on
        # what the self.zone.lastResult is
        if self.parent.zone.lastResult:
            if self.parent.zone.lastResult.actions:
                for action in self.parent.zone.lastResult.actions:
                    if action.requirementsMet() == True:
                        button = EmitButton(action.description)
                        button.released.connect(self.emitAction)
                        self.resultsActionLayout.addWidget(button)

    def emitAction(self, textOfAction):
        self.action.emit(textOfAction)

class ZoneWidget(QWidget):
    publishMessage = pyqtSignal(str)
    
    def __init__(self, zone, parent):
        super().__init__()
        self.zone = zone
        self.parent = parent
        self.title = QLabel(zone.name)
        self.actionsBox = ZoneActionsBox(self)
        self.actionsBox.action.connect(self.executeAction)
        
        self.layout = QVBoxLayout()        
        
        titleLayout = QHBoxLayout()
        titleLayout.addStretch(1)
        titleLayout.addWidget(self.title)
        titleLayout.addStretch(1)
        self.layout.addLayout(titleLayout)

        bodyLayout = QHBoxLayout()
        bodyLayout.addWidget(self.actionsBox)
        self.layout.addLayout(bodyLayout)

        self.setLayout(self.layout)
        
    def executeAction(self, textOfAction):
        # Acquire result of action
        self.zone.act(textOfAction)

        # Parse the execution script of the result
        for script in self.zone.lastResult.executionScript:
            self.parseExecutionScript(script, textOfAction)
            
        self.actionsBox.populateResultsActions()

    def parseExecutionScript(self, script, textOfAction):
        msgTuple = None
        if script == "ITEM_DROP":
            itemTuple = self.zone.generateItemDrop(textOfAction,
                                                   self.parent.dbCursor)
            msgTuple = (itemTuple[0], itemTuple[1][1])
        elif script == "PBLSH_MSG":
            if self.zone.lastResult.description == "Found a tree":
                msgTuple = ("a", "tree")
            elif self.zone.lastResult.description == "Found a stream":
                msgTuple = ("a", "stream")
            elif self.zone.lastResult.description == "Found a clearing":
                msgTuple = ("a", "clearing")
            elif self.zone.lastResult.description == "Found a shrine":
                msgTuple = ("a", "shrine")
        elif script == "MONEY_DROP":
            moneyAmt = self.zone.generateCoinDrop()
            msgTuple = (moneyAmt, "gold coin")
        elif script == "GEN_ANIMAL":
            pass
        elif script == "STAT_UP":
            pass
        self.emitPublishMessage(self.zone.lastResult.message, msgTuple)
        
    def emitPublishMessage(self, text, params=None):
        # Fill '_' with text, if there is any
        if params:
            for param in params:
                text = text.replace("_", str(param), 1)
        self.publishMessage.emit(text)
        
class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mainWidget = QWidget()
        self.dbConnection = sqlite3.connect("GameDB.db")
        self.dbCursor = self.dbConnection.cursor()
        self.person = Player.Player()
        self.messages = {}
        
        self.importData()

        # Do layout
        self.mainLayout = QHBoxLayout()
        self.mainLayout.setSpacing(0)
        self.rightLayout = QVBoxLayout()
        self.rightTopLayout = QHBoxLayout()

        # Switcher widget will hold all the various views, like player
        # information, inventory, zones, etc.
        self.switcherWidget = SwitcherWidget(self.person)
        self.switcherWidget.setFixedWidth(200)
        mainAreaLabel = ZoneWidget(self.person.zones["Forest"], self)
        mainAreaLabel.publishMessage.connect(self.publishMessage)
        germanAreaLabel = QLabel("German")
        zoneStatsLabel = QLabel("Zone stats")
        self.messageBox = MessageTextBox()

        self.mainLayout.addWidget(self.switcherWidget)
        self.rightTopLayout.addWidget(self.messageBox)
        self.rightTopLayout.addWidget(mainAreaLabel)
        self.rightLayout.addLayout(self.rightTopLayout)
        self.rightLayout.addWidget(germanAreaLabel)
        self.mainLayout.addLayout(self.rightLayout)

        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)

    def publishMessage(self, text):
        self.messageBox.moveCursor(QTextCursor.Start)
        self.messageBox.insertPlainText(str(text) + "\n")

    def importData(self):
        # Import item data
        self.dbCursor.execute("""SELECT Items.ItemId, Items.Name, Inventory.Qty
                                 FROM Items LEFT OUTER JOIN Inventory
                                 ON Items.ItemId = Inventory.ItemId""")
        entries = self.dbCursor.fetchall()

        for row in entries:
            newItem = Items.Item(row[0], row[1], row[2])

	    # Add inherents
            self.dbCursor.execute("SELECT Items.ItemId, Inherents.InherentName FROM (Items INNER JOIN ItemsInherents ON Items.ItemId = ItemsInherents.ItemId) INNER JOIN Inherents ON ItemsInherents.InherentName = Inherents.InherentName WHERE (Items.ItemId=?);", (row[0],))
            for entry in self.dbCursor:
                newItem.addInherent(entry[1])

	    # Add milestones
            self.dbCursor.execute("SELECT Items.ItemId, Inherents.InherentName, ItemsMilestones.ItemMilestone, ItemsMilestones.TimeToCompletion, ItemsMilestones.CanCollect, ItemsMilestones.CollectionUsesUp FROM ((Items INNER JOIN ItemsInherents ON Items.ItemId = ItemsInherents.ItemId) INNER JOIN Inherents ON ItemsInherents.InherentName = Inherents.InherentName) INNER JOIN ItemsMilestones ON (ItemsInherents.InherentName = ItemsMilestones.ItemInherent) AND (ItemsInherents.ItemId = ItemsMilestones.ItemId) WHERE (Items.ItemId=?) ORDER BY ItemsMilestones.MilestoneOrder;", (row[0],))
            for entry in self.dbCursor:
                newItem.addMilestone(entry[1], Items.Milestone(entry[2], entry[3], entry[4], entry[5]))

            # Add milestone attributes
            self.dbCursor.execute("SELECT ItemsMilestones.ItemId, Inherents.InherentName, ItemsMilestones.ItemMilestone, ItemsMilestonesAttributes.ItemGeneratedId, ItemsMilestonesAttributes.ItemGeneratedQty, ItemsMilestonesAttributes.ItemGeneratedTime, ItemsMilestonesAttributes.ItemFailedId FROM (ItemsMilestones INNER JOIN ItemsMilestonesAttributes ON (ItemsMilestones.ItemMilestone = ItemsMilestonesAttributes.Milestone) AND (ItemsMilestones.ItemId = ItemsMilestonesAttributes.ItemId)) INNER JOIN Inherents ON ItemsMilestones.ItemInherent = Inherents.InherentName WHERE (ItemsMilestones.ItemId=?);", (row[0],))
            for entry in self.dbCursor:
                newItem.addMilestoneAttributes(entry[1], entry[2], entry[3], entry[4], entry[5], entry[6])

	    # Add components
            self.dbCursor.execute("SELECT Items.ItemId, Inherents.InherentName, ItemsComponents.ComponentId, ItemsComponents.ComponentQty FROM ((Items INNER JOIN ItemsInherents ON Items.ItemId = ItemsInherents.ItemId) INNER JOIN Inherents ON ItemsInherents.InherentName = Inherents.InherentName) INNER JOIN ItemsComponents ON (ItemsInherents.InherentName = ItemsComponents.ItemInherent) AND (ItemsInherents.ItemId = ItemsComponents.ItemId) WHERE (Items.ItemId=?);", (row[0],))
            for entry in self.dbCursor:
                newItem.addComponent(entry[1], entry[2], entry[3])

            self.person.inventory.addItemToInventory(newItem)
	    
        # Import messages
        self.dbCursor.execute("SELECT * FROM Messages")
        for each in self.dbCursor:
            self.messages[each[0]] = each[1]
            
        # Import player data
        self.dbCursor.execute("SELECT * FROM PlayerAttributes")
        for each in self.dbCursor:
            self.person.addAttribute(Player.Attribute(each[0], each[2], each[1]))

        # Import zone data
        self.dbCursor.execute("SELECT * FROM Zones")
        for each in self.dbCursor:
            self.person.addZone(Zones.Zone(each[0], each[1], each[2], each[3]))

        self.dbCursor.execute("SELECT * FROM ZonesActions")
        for each in self.dbCursor:
            action = Zones.Action(each[1], each[2], each[3])
            self.person.zones[each[0]].addAction(action)

        self.dbCursor.execute("""SELECT ZonesResults.Zone, ZonesResults.ResultName,
                                        ZonesResults.Likelihood, ZonesResults.MaxLikelihood,
                                        Messages.Text
                                 FROM ZonesResults
                                 LEFT OUTER JOIN Messages
                                 ON ZonesResults.Message = Messages.idNum""")
        for each in self.dbCursor:
            result = Zones.Result(each[1], each[2], each[3], each[4])
            self.person.zones[each[0]].addResult(result)

        self.dbCursor.execute("SELECT * FROM ZonesResultsExecutionScripts")
        for each in self.dbCursor:
            self.person.zones[each[0]].results[each[1]].addExecutionScript(each[2])

        self.dbCursor.execute("SELECT * FROM ZonesActionsXResults")
        for each in self.dbCursor:
            if each[1] == "Action":
                actionToPair = self.person.zones[each[0]].actions[each[2]]
                resultToBePaired = self.person.zones[each[0]].results[each[4]]

                actionToPair.addResult(resultToBePaired)
            elif each[1] == "Result":
                resultToPair = self.person.zones[each[0]].results[each[2]]
                actionToBePaired = self.person.zones[each[0]].actions[each[4]]

                resultToPair.addAction(actionToBePaired)

        # Import requirements
        self.dbCursor.execute("SELECT * FROM Requirements")
        for each in self.dbCursor:
            req = UniversalClasses.Requirement(eval("self.person." + each[0]), each[1], each[2])
            eval("self.person." + each[3] + ".addRequirement(req)")
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = Window()
    form.show()
    app.exec_()
