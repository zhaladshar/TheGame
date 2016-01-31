from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sqlite3
import sys
import Player
import Zones

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

class ZoneActionsBox(QWidget):
    def __init__(self, zone):
        super().__init__()
        self.zone = zone

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
        for action in self.zone.actions.getMainActions():
            button = EmitButton(action.description)
            button.released.connect(self.executeAction)
            self.zoneActionLayout.addWidget(button)

    def populateResultsActions(self):
        # Remove all old widgets from resultsActionLayout
        while self.resultsActionLayout.count() > 0:
            layoutItem = self.resultsActionLayout.takeAt(0)
            layoutItem.widget().deleteLater()

        # Populate resultsActionLayout with new action buttons based on
        # what the self.zone.lastResult is
        if self.zone.lastResult:
            if self.zone.lastResult.actions:
                for action in self.zone.lastResult.actions:
                    button = EmitButton(action.description)
                    button.released.connect(self.executeAction)
                    self.resultsActionLayout.addWidget(button)

    def executeAction(self, textOfAction):
        # Acquire result of action
        self.zone.act(textOfAction)
        self.populateResultsActions()
        
class ZoneWidget(QWidget):
    def __init__(self, zone):
        super().__init__()
        self.zone = zone
        self.title = QLabel(zone.name)
        self.messageTextBox = MessageTextBox()
        self.actionsBox = ZoneActionsBox(zone)
        
        self.layout = QVBoxLayout()        
        
        titleLayout = QHBoxLayout()
        titleLayout.addStretch(1)
        titleLayout.addWidget(self.title)
        titleLayout.addStretch(1)
        self.layout.addLayout(titleLayout)

        bodyLayout = QHBoxLayout()
        bodyLayout.addWidget(self.messageTextBox)
        bodyLayout.addWidget(self.actionsBox)
        self.layout.addLayout(bodyLayout)

        self.setLayout(self.layout)
        
class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mainWidget = QWidget()
        self.dbConnection = sqlite3.connect("GameDB.db")
        self.dbCursor = self.dbConnection.cursor()
        self.person = Player.Player()
        
        self.importData()

        # Do layout
        self.mainLayout = QHBoxLayout()
        self.mainLayout.setSpacing(0)
        self.mainRightLayout = QVBoxLayout()
        self.mainRightBottomLayout = QHBoxLayout()

        # Switcher widget will hold all the various views, like player
        # information, inventory, zones, etc.
        self.switcherWidget = SwitcherWidget(self.person)
        self.switcherWidget.setFixedWidth(200)
        mainAreaLabel = ZoneWidget(self.person.zones["Forest"])
        germanAreaLabel = QLabel("German")
        zoneStatsLabel = QLabel("Zone stats")

        self.mainLayout.addWidget(self.switcherWidget)
        self.mainRightLayout.addWidget(mainAreaLabel)
        self.mainRightBottomLayout.addWidget(germanAreaLabel)
        self.mainRightBottomLayout.addWidget(zoneStatsLabel)

        self.mainRightLayout.addLayout(self.mainRightBottomLayout)
        self.mainLayout.addLayout(self.mainRightLayout)

        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)

    def importData(self):
        self.dbCursor.execute("SELECT * FROM PlayerAttributes")
        for each in self.dbCursor:
            self.person.addAttribute(Player.Attribute(each[0], each[2], each[1]))

        self.dbCursor.execute("SELECT * FROM Zones")
        for each in self.dbCursor:
            self.person.addZone(Zones.Zone(each[0], each[1], each[2], each[3]))

        self.dbCursor.execute("SELECT * FROM ZonesActions")
        for each in self.dbCursor:
            action = Zones.Action(each[1], each[2])
            self.person.zones[each[0]].addAction(action)

        self.dbCursor.execute("SELECT * FROM ZonesResults")
        for each in self.dbCursor:
            result = Zones.Result(each[1], each[2], each[3])
            self.person.zones[each[0]].addResult(result)

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
                                     
if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = Window()
    form.show()
    app.exec_()
