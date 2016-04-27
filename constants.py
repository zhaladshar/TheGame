# Initialization constants
INI_FILE = "thegame.ini"


    ######################
    # Interface constants
    ######################

# Constants to change the views of the selector widget
INTFC_SLCTR_PLYR = "Pl"
INTFC_SLCTR_INV = "Inv"
INTFC_SLCTR_QST = "Q"

INTFC_SLCTR_PLYR_POS = 0
INTFC_SLCTR_INV_POS = 1
INTFC_SLCTR_QST_POS = 2

INTFC_SLCTR_LIST = [INTFC_SLCTR_PLYR, INTFC_SLCTR_INV, INTFC_SLCTR_QST]

INTFC_SLCTR = {INTFC_SLCTR_PLYR: INTFC_SLCTR_PLYR_POS,
               INTFC_SLCTR_INV: INTFC_SLCTR_INV_POS,
               INTFC_SLCTR_QST: INTFC_SLCTR_QST_POS}

# Constants to change views of the player display
# (sub-widget to selector widget)
INTFC_PLYR_DISP_ATTR = "Attributes"
INTFC_PLYR_DISP_SKLL = "Skills"

INTFC_PLYR_DISP_ATTR_POS = 0
INTFC_PLYR_DISP_SKLL_POS = 1

INTFC_PLYR_DISP = {INTFC_PLYR_DISP_ATTR: INTFC_PLYR_DISP_ATTR_POS,
                   INTFC_PLYR_DISP_SKLL: INTFC_PLYR_DISP_SKLL_POS}

# Constants to change views of the inventory display
INTFC_INV_INV = "Inventory"
INTFC_INV_ART = "Artifacts"

INTFC_INV_INV_POS = 0
INTFC_INV_ART_POS = 1

INTFC_INV_LIST = [INTFC_INV_INV, INTFC_INV_ART]

INTFC_INV = {INTFC_INV_INV: INTFC_INV_INV_POS,
             INTFC_INV_ART: INTFC_INV_ART_POS}


    ######################
    # Player constants
    ######################

# List of player attributes
STRENGTH_ATTR = "Strength"
DEXTERITY_ATTR = "Dexterity"
STAMINA_ATTR = "Stamina"
INTELLIGENCE_ATTR = "Intelligence"
WISDOM_ATTR = "Wisdom"
NOBILITY_ATTR = "Nobility"
PERCEPTION_ATTR = "Perception"
LUCK_ATTR = "Luck"
CHARISMA_ATTR = "Charisma"
LEADERSHIP_ATTR = "Leadership"
PIETY_ATTR = "Piety"
STEALTH_ATTR = "Stealth"

PLAYER_ATTRIBUTES = [STRENGTH_ATTR, DEXTERITY_ATTR, STAMINA_ATTR,
                     INTELLIGENCE_ATTR, WISDOM_ATTR, NOBILITY_ATTR,
                     PERCEPTION_ATTR, LUCK_ATTR, CHARISMA_ATTR,
                     LEADERSHIP_ATTR, PIETY_ATTR, STEALTH_ATTR]

# List of zones
FOREST_ZONE = "Forest"

ZONES = [FOREST_ZONE]

# List of item categories
ITM_CAT_ANIMAL = "ANIMAL"

# List of quest statuses
QST_NOT_START = "Not started"
QST_START = "Started"
QST_DONE = "Completed"
