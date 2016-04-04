from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sqlite3
import sys
import os.path
import Player
import Zones
import Items
import UniversalClasses
import constants

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
            label = QLabel(value.name + " - " + str(value.lvl) + "\nExp: " + str(value.exp) + "/" + str(value.expToLevelUp()))
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

class PlayerSelector(QDialog):
    playerName = pyqtSignal(str)
    
    def __init__(self, listOfNames):
        super().__init__()

        self.listOfPlayers = QListWidget()
        self.listOfPlayers.addItems(listOfNames)
        self.listOfPlayers.currentRowChanged.connect(self.updateNameEdit)
        self.okButton = QPushButton("OK")
        self.okButton.released.connect(self.submit)
        self.deleteButton = QPushButton("Delete")
        self.nameEdit = QLineEdit()

        mainLayout = QVBoxLayout()
        layout = QHBoxLayout()
        layout.addWidget(self.listOfPlayers)

        buttonLayout = QVBoxLayout()
        buttonLayout.addWidget(self.okButton)
        buttonLayout.addWidget(self.deleteButton)
        buttonLayout.addStretch()

        layout.addLayout(buttonLayout)

        mainLayout.addLayout(layout)
        mainLayout.addWidget(self.nameEdit)
        self.setLayout(mainLayout)

        self.listOfPlayers.setCurrentRow(0)
        if self.listOfPlayers:
            self.nameEdit.setText(self.listOfPlayers.currentItem().text())

        self.setWindowTitle("Player Select")
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        
    def submit(self):
        self.playerName.emit(self.nameEdit.text())
        self.accept()

    def updateNameEdit(self, rowNum):
        self.nameEdit.setText(self.listOfPlayers.item(rowNum).text())
        
class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mainWidget = QWidget()
        self.dbGameConnection = sqlite3.connect("GameDB.db")
        self.dbGameCursor = self.dbGameConnection.cursor()
        self.dbPlayerConnection = None
        self.dbPlayerCursor = None
        self.ini = {}
        self.person = Player.Player()
        self.personName = None
        self.messages = {}

        # Initialize gameplay variables. If LAST_PLAYER is null string,
        # prompt to create player and then 
        filePtr = open(constants.INI_FILE, "r")
        iniLines = filePtr.readlines()
        for line in iniLines:
            split = line.split(" = ")
            if split[0] == "PLAYERS":
                # If there are no old players, the right split will be a null
                # string.  This should not be a value in the player list, so
                # suppress adding it.
                if split[1] == "":
                    self.ini[split[0]] = []
                else:
                    self.ini[split[0]] = split[1].split("|")
            else:
                self.ini[split[0]] = split[1]
        filePtr.close()

        # Do player login
        loginDialog = PlayerSelector(self.ini["PLAYERS"])
        loginDialog.playerName.connect(self.getName)
        if loginDialog.exec_():
            if os.path.isfile(self.personName + ".db"):
                self.dbPlayerConnection = sqlite3.connect(self.personName +
                                                          ".db")
                self.dbPlayerCursor = self.dbPlayerConnection.cursor()
            else:
                self.ini["PLAYERS"].append(self.personName)
                self.dbPlayerConnection = sqlite3.connect(self.personName +
                                                          ".db")
                self.dbPlayerCursor = self.dbPlayerConnection.cursor()
                self.buildPlayerDB()
        
        # Import general game data
        self.importGameData()
        self.importPlayerData()

        # Do layout
        self.mainLayout = QHBoxLayout()
        self.mainLayout.setSpacing(0)
        self.rightLayout = QVBoxLayout()
        self.rightTopLayout = QHBoxLayout()

        # Switcher widget will hold all the various views, like player
        # information, inventory, zones, etc.
        self.switcherWidget = SwitcherWidget(self.person)
        self.switcherWidget.setFixedWidth(200)
        mainAreaWidget = ZoneWidget(self.person.zones["Forest"], self)
        mainAreaWidget.publishMessage.connect(self.publishMessage)
        germanAreaLabel = QLabel("German")
        zoneStatsLabel = QLabel("Zone stats")
        self.messageBox = MessageTextBox()

        self.mainLayout.addWidget(self.switcherWidget)
        self.rightTopLayout.addWidget(self.messageBox)
        self.rightTopLayout.addWidget(mainAreaWidget)
        self.rightLayout.addLayout(self.rightTopLayout)
        self.rightLayout.addWidget(germanAreaLabel)
        self.mainLayout.addLayout(self.rightLayout)

        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)

    def getName(self, text):
        self.personName = text

    def publishMessage(self, text):
        self.messageBox.moveCursor(QTextCursor.Start)
        self.messageBox.insertPlainText(str(text) + "\n")

    def importGameData(self):
        # Import item data
        self.dbGameCursor.execute("""SELECT ItemId, Name FROM Items""")
        entries = self.dbGameCursor.fetchall()

        for row in entries:
            newItem = Items.Item(row[0], row[1])

	    # Add inherents
            self.dbGameCursor.execute("SELECT Items.ItemId, Inherents.InherentName FROM (Items INNER JOIN ItemsInherents ON Items.ItemId = ItemsInherents.ItemId) INNER JOIN Inherents ON ItemsInherents.InherentName = Inherents.InherentName WHERE (Items.ItemId=?);", (row[0],))
            for entry in self.dbGameCursor:
                newItem.addInherent(entry[1])

	    # Add milestones
            self.dbGameCursor.execute("SELECT Items.ItemId, Inherents.InherentName, ItemsMilestones.ItemMilestone, ItemsMilestones.TimeToCompletion, ItemsMilestones.CanCollect, ItemsMilestones.CollectionUsesUp FROM ((Items INNER JOIN ItemsInherents ON Items.ItemId = ItemsInherents.ItemId) INNER JOIN Inherents ON ItemsInherents.InherentName = Inherents.InherentName) INNER JOIN ItemsMilestones ON (ItemsInherents.InherentName = ItemsMilestones.ItemInherent) AND (ItemsInherents.ItemId = ItemsMilestones.ItemId) WHERE (Items.ItemId=?) ORDER BY ItemsMilestones.MilestoneOrder;", (row[0],))
            for entry in self.dbGameCursor:
                newItem.addMilestone(entry[1], Items.Milestone(entry[2], entry[3], entry[4], entry[5]))

            # Add milestone attributes
            self.dbGameCursor.execute("SELECT ItemsMilestones.ItemId, Inherents.InherentName, ItemsMilestones.ItemMilestone, ItemsMilestonesAttributes.ItemGeneratedId, ItemsMilestonesAttributes.ItemGeneratedQty, ItemsMilestonesAttributes.ItemGeneratedTime, ItemsMilestonesAttributes.ItemFailedId FROM (ItemsMilestones INNER JOIN ItemsMilestonesAttributes ON (ItemsMilestones.ItemMilestone = ItemsMilestonesAttributes.Milestone) AND (ItemsMilestones.ItemId = ItemsMilestonesAttributes.ItemId)) INNER JOIN Inherents ON ItemsMilestones.ItemInherent = Inherents.InherentName WHERE (ItemsMilestones.ItemId=?);", (row[0],))
            for entry in self.dbGameCursor:
                newItem.addMilestoneAttributes(entry[1], entry[2], entry[3], entry[4], entry[5], entry[6])

	    # Add components
            self.dbGameCursor.execute("SELECT Items.ItemId, Inherents.InherentName, ItemsComponents.ComponentId, ItemsComponents.ComponentQty FROM ((Items INNER JOIN ItemsInherents ON Items.ItemId = ItemsInherents.ItemId) INNER JOIN Inherents ON ItemsInherents.InherentName = Inherents.InherentName) INNER JOIN ItemsComponents ON (ItemsInherents.InherentName = ItemsComponents.ItemInherent) AND (ItemsInherents.ItemId = ItemsComponents.ItemId) WHERE (Items.ItemId=?);", (row[0],))
            for entry in self.dbGameCursor:
                newItem.addComponent(entry[1], entry[2], entry[3])

            self.person.inventory.addItemToInventory(newItem)
	    
        # Import messages
        self.dbGameCursor.execute("SELECT * FROM Messages")
        for each in self.dbGameCursor:
            self.messages[each[0]] = each[1]
            
        # Import player data
        self.dbGameCursor.execute("SELECT * FROM PlayerAttributes")
        for each in self.dbGameCursor:
            self.person.addAttribute(Player.Attribute(each[0], each[1]))

        # Import zone data
        self.dbGameCursor.execute("SELECT * FROM Zones")
        for each in self.dbGameCursor:
            self.person.addZone(Zones.Zone(each[0]))

        self.dbGameCursor.execute("SELECT * FROM ZonesActions")
        for each in self.dbGameCursor:
            action = Zones.Action(each[1], each[2])
            self.person.zones[each[0]].addAction(action)

        self.dbGameCursor.execute("""SELECT ZonesResults.Zone, ZonesResults.ResultName,
                                        ZonesResults.Likelihood, ZonesResults.MaxLikelihood,
                                        Messages.Text
                                 FROM ZonesResults
                                 LEFT OUTER JOIN Messages
                                 ON ZonesResults.Message = Messages.idNum""")
        for each in self.dbGameCursor:
            result = Zones.Result(each[1], each[2], each[3], each[4])
            self.person.zones[each[0]].addResult(result)

        self.dbGameCursor.execute("SELECT * FROM ZonesResultsExecutionScripts")
        for each in self.dbGameCursor:
            self.person.zones[each[0]].results[each[1]].addExecutionScript(each[2])

        self.dbGameCursor.execute("SELECT * FROM ZonesActionsXResults")
        for each in self.dbGameCursor:
            if each[1] == "Action":
                actionToPair = self.person.zones[each[0]].actions[each[2]]
                resultToBePaired = self.person.zones[each[0]].results[each[4]]

                actionToPair.addResult(resultToBePaired)
            elif each[1] == "Result":
                resultToPair = self.person.zones[each[0]].results[each[2]]
                actionToBePaired = self.person.zones[each[0]].actions[each[4]]

                resultToPair.addAction(actionToBePaired)

        # Import requirements
        self.dbGameCursor.execute("SELECT * FROM Requirements")
        for each in self.dbGameCursor:
            req = UniversalClasses.Requirement(eval("self.person." + each[0]), each[1], each[2], each[3])
            eval("self.person." + each[4] + ".addRequirement(req)")

    def importPlayerData(self):
        self.dbPlayerCursor.execute("SELECT * FROM Inventory")
        for itemId, qty in self.dbPlayerCursor:
            self.person.inventory[itemId].qty = qty

        self.dbPlayerCursor.execute("SELECT * FROM PlayerAttributes")
        for attr, lvl, exp in self.dbPlayerCursor:
            self.person.attributes[attr].lvl = lvl
            self.person.attributes[attr].exp = exp

        self.dbPlayerCursor.execute("SELECT * FROM Zones")
        for zone, lvl, exp, unl in self.dbPlayerCursor:
            self.person.zones[zone].lvl = lvl
            self.person.zones[zone].exp = exp
            self.person.zones[zone].unlocked = bool(unl)

        self.dbPlayerCursor.execute("SELECT * FROM ZonesActions")
        for zone, action, count in self.dbPlayerCursor:
            self.person.zones[zone].actions[action].performanceCount = count

    def exportPlayerData(self):
        self.dbPlayerCursor.execute("DELETE FROM Inventory")
        for itemId, item in self.person.inventory.items():
            self.dbPlayerCursor.execute("INSERT INTO Inventory VALUES (?, ?)",
                                        (itemId, item.qty))
        
        for attrName, attr in self.person.attributes.items():
            self.dbPlayerCursor.execute("""UPDATE PlayerAttributes
                                           SET Level=?, Exp=?
                                           WHERE Attribute=?""",
                                        (attr.lvl, attr.exp, attrName))
        
        for zoneName, zone in self.person.zones.items():
            self.dbPlayerCursor.execute("""UPDATE Zones
                                           SET Level=?, Exp=?, Unlocked=?
                                           WHERE Name=?""",
                                        (zone.lvl, zone.exp, int(zone.unlocked), zoneName))
        
        for zoneName, zone in self.person.zones.items():
            for actionName, action in zone.actions.items():
                self.dbPlayerCursor.execute("""UPDATE ZonesActions
                                               SET PerformanceCount=?
                                               WHERE Zone=? AND ActionName=?""",
                                            (action.performanceCount, zoneName, actionName))
        self.dbPlayerConnection.commit()
        
    def buildPlayerDB(self):
        # Build tables
        self.dbPlayerCursor.execute("""CREATE TABLE Inventory
                                      (ItemId INTEGER,
                                       Qty    REAL,
                                       PRIMARY KEY(ItemId)
                                      )""")
        self.dbPlayerCursor.execute("""CREATE TABLE PlayerAttributes
                                      (Attribute    TEXT,
                                       Level        INTEGER,
                                       Exp          REAL,
                                       PRIMARY KEY(Attribute)
                                      )""")
        self.dbPlayerCursor.execute("""CREATE TABLE Zones
                                      (Name     TEXT,
                                       Level    INTEGER,
                                       Exp      REAL,
                                       Unlocked INTEGER,
                                       PRIMARY KEY(Name)
                                      )""")
        self.dbPlayerCursor.execute("""CREATE TABLE ZonesActions
                                      (Zone             TEXT,
                                       ActionName       TEXT,
                                       PerformanceCount INTEGER
                                      )""")
        
        # Enter initial data into rows in tables
        self.dbGameCursor.execute("SELECT Name FROM PlayerAttributes")
        for attribute in self.dbGameCursor:
            self.dbPlayerCursor.execute("""INSERT INTO PlayerAttributes VALUES
                                           (?, 1, 0)""", (attribute[0],))

        self.dbGameCursor.execute("SELECT Name FROM Zones")
        for zone in self.dbGameCursor:
            self.dbPlayerCursor.execute("""INSERT INTO Zones VALUES
                                           (?, 1, 0, 0)""", (zone[0],))
        self.dbPlayerCursor.execute("""UPDATE Zones SET Unlocked=1
                                       WHERE Name='Forest'""")

        self.dbGameCursor.execute("SELECT Zone, ActionName FROM ZonesActions")
        for zone, action in self.dbGameCursor:
            self.dbPlayerCursor.execute("""INSERT INTO ZonesActions VALUES
                                           (?, ?, 0)""", (zone, action))
        
        self.dbPlayerConnection.commit()

    def closeEvent(self, event):
        print(self.ini["PLAYERS"])
        print("|".join(self.ini["PLAYERS"]))
        self.exportPlayerData()
        filePtr = open(constants.INI_FILE, "w")
        for ini in self.ini:
            if ini == "PLAYERS":
                filePtr.write("%s = %s" % (ini, "|".join(self.ini[ini])))
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = Window()
    form.show()
    app.exec_()
