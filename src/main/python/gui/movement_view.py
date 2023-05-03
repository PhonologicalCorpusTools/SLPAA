from copy import copy
import re

from PyQt5.QtCore import (
    Qt,
    # QAbstractListModel,
    # pyqtSignal,
    # QModelIndex,
    # QItemSelectionModel,
    QSortFilterProxyModel,
    QDateTime
)

from PyQt5.Qt import (
    QStandardItem,
    QStandardItemModel
)

from PyQt5.QtWidgets import (
    # QWidget,
    # QLabel,
    # QLineEdit,
    QListView,
    # QVBoxLayout,
    QComboBox,
    QTreeView,
    QStyle,
    QMessageBox
)

from lexicon.module_classes import delimiter, userdefinedroles as udr
from lexicon.module_classes2 import AddedInfo
from gui.location_view import ParameterModuleSerializable

# for backwards compatibility
specifytotalcycles_str = "Specify total number of cycles"
numberofreps_str = "Number of repetitions"

rb = "radio button"  # ie mutually exclusive in group / at this level
cb = "checkbox"  # ie not mutually exlusive
ed_1 = "editable level 1"  # ie value is editable but restricted to numbers that are >= 1 and multiples of 0.5
ed_2 = "editable level 2"  # ie value is editable but restricted to numbers
ed_3 = "editable level 3" # ie value is editable and unrestricted
fx = "fixed"  # ie value is not editable
subgroup = "subgroup"

c = True  # checked
u = False  # unchecked

mvmtOptionsDict = {
    ("No movement", fx, rb, u, 0): {},
    ("Movement type", fx, cb, u, 1): {
        ("Perceptual shape", fx, rb, u, 2): {
            ("Shape", fx, cb, u, 3): {  # all mutually exclusive (straight vs arc vs ...)
                (subgroup, None, 0, None, 4): {
                    ("Straight", fx, rb, u, 5): {
                        ("Interacts with subsequent straight movement", fx, rb, u, 6): {
                            ("Movement contours cross (e.g. X)", fx, rb, u, 7): {},
                            ("Subsequent movement starts at end of first (e.g. ↘↗)", fx, rb, u, 8): {},
                            ("Subsequent movement starts in same location as start of first (e.g. ↖↗)", fx, rb, u, 9): {},
                            ("Subsequent movement ends in same location as end of first (e.g. ↘↙)", fx, rb, u, 10): {}
                        },
                        ("Doesn't interact with subsequent straight movement", fx, rb, u, 11): {}
                    },
                    ("Arc", fx, rb, u, 12): {},
                    ("Circle", fx, rb, u, 13): {},
                    ("Zigzag", fx, rb, u, 14): {},
                    ("Loop (travelling circles)", fx, rb, u, 15): {},
                    ("None of these", fx, rb, u, 16): {}
                }
            },
            ("Axis direction", fx, cb, u, 17): {  # Choose up to one from each axis to get the complete direction
                # ("H1 and H2 move in opposite directions", fx, cb, u, 18): {},
                (subgroup, None, 0, None, 18): {
                    ("H1 and H2 move toward each other", fx, rb, u, 18.1): {},
                    ("H1 and H2 move away from each other", fx, rb, u, 18.2): {},
                },
                (subgroup, None, 1, None, 19): {
                    ("Horizontal", fx, cb, u, 19.1): {
                        (subgroup, None, 0, None, 20): {
                            ("Ipsilateral", fx, rb, u, 21): {},  # TODO KV or toward H1
                            ("Contralateral", fx, rb, u, 22): {}  # TODO KV or toward H2
                        },
                    },
                    ("Vertical", fx, cb, u, 23): {
                        (subgroup, None, 0, None, 24): {
                            ("Up", fx, rb, u, 25): {},
                            ("Down", fx, rb, u, 26): {}
                        },
                    },
                    ("Sagittal", fx, cb, u, 27): {
                        (subgroup, None, 0, None, 28): {
                            ("Distal", fx, rb, u, 29): {},
                            ("Proximal", fx, rb, u, 30): {}
                        },
                    },
                },
                ("Not relevant", fx, rb, u, 31): {}  # TODO KV Auto-select this if movement is straight or the axis is not relevant
            },
            ("Plane", fx, cb, u, 32): {  # choose as many as needed, but only one direction per plane
                ("H1 and H2 move in opposite directions", fx, cb, u, 33): {},
                ("Horizontal", fx, cb, u, 34): {
                    (subgroup, None, 0, None, 35): {
                        ("Ipsilateral from top of circle", fx, rb, u, 36): {},
                        ("Contralateral from top of circle", fx, rb, u, 37): {}
                        # ("Clockwise", fx, rb, u): {},  # TODO KV or Ipsilateral from the top of the circle
                        # ("Counterclockwise", fx, rb, u): {}  # TODO KV or Contralateral from the top of the circle
                    },
                },
                ("Vertical", fx, cb, u, 38): {
                    (subgroup, None, 0, None, 39): {
                        ("Ipsilateral from top of circle", fx, rb, u, 40): {},
                        ("Contralateral from top of circle", fx, rb, u, 41): {}
                        # ("Clockwise", fx, rb, u): {},  # TODO KV or Ipsilateral from the top of the circle
                        # ("Counterclockwise", fx, rb, u): {}  # TODO KV or Contralateral from the top of the circle
                    },
                },
                ("Sagittal", fx, cb, u, 42): {
                    (subgroup, None, 0, None, 43): {
                        ("Distal from top of circle", fx, rb, u, 44): {},
                        ("Proximal from top of circle", fx, rb, u, 45): {}
                        # ("Clockwise", fx, rb, u): {},
                        # ("Counterclockwise", fx, rb, u): {}
                    },
                },
                ("Not relevant", fx, rb, u, 46): {}  # TODO KV Auto-select this if movement is straight or the axis is not relevant
            },
        },
        # mutually exclusive @ level of pivoting, twisting, etc. and also within (nodding vs unnodding)
        ("Joint-specific movements", fx, rb, u, 47): {
            ("Nodding/un-nodding", fx, rb, u, 48): {
                (subgroup, None, 0, None, 49): {
                    ("Nodding", fx, rb, u, 50): {},  # TODO KV autofills to flexion of wrist (but *ask* before auto-unfilling if nodding is unchecked)
                    ("Un-nodding", fx, rb, u, 51): {}  # TODO KV autofills to extension of wrist
                }
            },
            ("Pivoting", fx, rb, u, 52): {
                (subgroup, None, 0, None, 53): {
                    ("Radial", fx, rb, u, 54): {},  # TODO KV autofills to wrist radial deviation
                    ("Ulnar", fx, rb, u, 55): {}  # TODO KV autofills to wrist ulnar deviation
                }
            },
            ("Twisting", fx, rb, u, 56): {
                (subgroup, None, 0, None, 57): {
                    ("Pronation", fx, rb, u, 58): {},  # TODO KV autofills to Proximal radioulnar pronation
                    ("Supination", fx, rb, u, 59): {}  # TODO KV autofills to Proximal radioulnar supination
                }
            },
            ("Closing/Opening", fx, rb, u, 60): {
                (subgroup, None, 0, None, 61): {
                    ("Closing", fx, rb, u, 62): {},  # TODO KV autofills to flexion of [selected finger, all joints]
                    ("Opening", fx, rb, u, 63): {}  # TODO KV autofills to extension of [selected finger, all joints]
                }
            },
            ("Pinching/unpinching", fx, rb, u, 64): {
                (subgroup, None, 0, None, 65): {
                    ("Pinching (Morgan 2017)", fx, rb, u, 66): {},  # TODO KV autofills to adduction of thumb base joint
                    ("Unpinching", fx, rb, u, 67): {}  # TODO KV autofills to (abduction of thumb base joint? - not specific in google doc)
                }
            },
            ("Flattening/Straightening", fx, rb, u, 68): {
                (subgroup, None, 0, None, 69): {
                    ("Flattening/hinging", fx, rb, u, 70): {},  # TODO KV autofills to flexion of [selected finger base joints]
                    ("Straightening", fx, rb, u, 71): {}  # TODO KV autofills to extension of [selected finger base joints]
                }
            },
            ("Hooking/Unhooking", fx, rb, u, 72): {
                (subgroup, None, 0, None, 73): {
                    ("Hooking/clawing", fx, rb, u, 74): {},  # TODO KV autofills to flexion of [selected finger non-base joints]
                    ("Unhooking", fx, rb, u, 75): {}  # TODO KV autofills to extension of [selected finger non-base joints]
                }
            },
            ("Spreading/Unspreading", fx, rb, u, 76): {
                (subgroup, None, 0, None, 77): {
                    ("Spreading", fx, rb, u, 78): {},  # TODO KV autofills to abduction of [selected finger base joints]
                    ("Unspreading", fx, rb, u, 79): {}  # TODO KV autofills to adduction of [selected finger base joints]
                }
            },
            ("Rubbing", fx, rb, u, 80): {
                (subgroup, None, 0, None, 81): {
                    ("Thumb crossing over palm", fx, rb, u, 82): {},  # TODO KV autofills to TBD
                    ("Thumb moving away from palm", fx, rb, u, 83): {}  # TODO KV autofills to TBD
                }
            },
            ("Wiggling/Fluttering", fx, rb, u, 84): {},  # TODO KV autofills to both flexion and extension of selected finger base joints
            ("None of these", fx, rb, u, 85): {}
        },
        ("Handshape change", fx, rb, u, 86): {}
    },
    ("Joint activity", fx, cb, u, 87): {
        ("Complex / multi-joint", fx, cb, u, 88): {},  # from Yurika: if this is selected, the expectation is that nothing else below would be selected, though I guess people could...
        ("Shoulder", fx, cb, u, 89): {
            (subgroup, None, 0, None, 90): {
                ("Flexion", fx, rb, u, 91): {},
                ("Extension", fx, rb, u, 92): {},
            },
            (subgroup, None, 1, None, 93): {
                ("Abduction", fx, rb, u, 94): {},
                ("Adduction", fx, rb, u, 95): {},
            },
            (subgroup, None, 2, None, 96): {
                ("Posterior rotation", fx, rb, u, 97): {},
                ("Anterior rotation", fx, rb, u, 98): {},
            },
            (subgroup, None, 3, None, 99): {
                ("Protraction", fx, rb, u, 100): {},
                ("Retraction", fx, rb, u, 101): {},
            },
            (subgroup, None, 4, None, 102): {
                ("Depression", fx, rb, u, 103): {},
                ("Elevation", fx, rb, u, 104): {},
            },
            (subgroup, None, 5, None, 105): {
                ("Circumduction", fx, cb, u, 106): {}
            },
        },
        ("Elbow", fx, cb, u, 107): {
            (subgroup, None, 0, None, 108): {
                ("Flexion", fx, rb, u, 109): {},
                ("Extension", fx, rb, u, 110): {},
            },
            (subgroup, None, 1, None, 111): {
                ("Circumduction", fx, cb, u, 112): {}
            },
        },
        ("Radio-ulnar", fx, cb, u, 113): {
            (subgroup, None, 0, None, 114): {
                ("Pronation", fx, rb, u, 115): {},
                ("Supination", fx, rb, u, 116): {},
            }
        },
        ("Wrist", fx, cb, u, 117): {
            (subgroup, None, 0, None, 118): {
                ("Flexion", fx, rb, u, 119): {},
                ("Extension", fx, rb, u, 120): {},
            },
            (subgroup, None, 1, None, 121): {
                ("Radial deviation", fx, rb, u, 122): {},
                ("Ulnar deviation", fx, rb, u, 123): {},
            },
            (subgroup, None, 2, None, 124): {
                ("Circumduction", fx, cb, u, 125): {}
            },
        },
        ("Thumb base / metacarpophalangeal", fx, cb, u, 126): {
            (subgroup, None, 0, None, 127): {
                ("Flexion", fx, rb, u, 128): {},
                ("Extension", fx, rb, u, 129): {},
            },
            (subgroup, None, 1, None, 130): {
                ("Abduction", fx, rb, u, 131): {},
                ("Adduction", fx, rb, u, 132): {},
            },
            (subgroup, None, 2, None, 133): {
                ("Circumduction", fx, cb, u, 134): {},
                ("Opposition", fx, cb, u, 135): {}
            }
        },
        ("Thumb non-base / interphalangeal", fx, cb, u, 136): {
            (subgroup, None, 0, None, 137): {
                ("Flexion", fx, rb, u, 138): {},
                ("Extension", fx, rb, u, 139): {},
            }
        },
        ("Finger base / metacarpophalangeal", fx, cb, u, 140): {
            (subgroup, None, 0, None, 141): {
                ("Flexion", fx, rb, u, 142): {},
                ("Extension", fx, rb, u, 143): {},
            },
            (subgroup, None, 1, None, 144): {
                ("Abduction", fx, rb, u, 145): {},
                ("Adduction", fx, rb, u, 146): {},
            },
            (subgroup, None, 2, None, 147): {
                ("Circumduction", fx, cb, u, 148): {}
            },
        },
        ("Finger non-base / interphalangeal", fx, cb, u, 149): {
            (subgroup, None, 0, None, 150): {
                ("Flexion", fx, rb, u, 151): {},
                ("Extension", fx, rb, u, 152): {},
            }
        }
    },
    ("Movement characteristics", fx, cb, u, 153): {
        ("Repetition", fx, cb, u, 154): {
            ("Single", fx, rb, u, 155): {},
            ("Repeated", fx, rb, u, 156): {
                (specifytotalcycles_str, ed_1, cb, u, 156): {
                    # ("#", ed, cb, u, 157): {
                    ("This number is a minimum", fx, cb, u, 158): {},
                    # },
                },
                ("Location of repetition", fx, cb, u, 159): {
                    ("Same location", fx, rb, u, 160): {},
                    ("Different location", fx, rb, u, 161): {  # Choose up to one from each column as needed
                        ("Horizontal", fx, cb, u, 162): {
                            # (subgroup, None, 2, None): {
                            ("Ipsilateral", fx, rb, u, 163): {},  # TODO KV default ipsi/contra; can choose right/left in settings
                            ("Contralateral", fx, rb, u, 164): {}
                            # }
                        },
                        ("Vertical", fx, cb, u, 165): {
                            # (subgroup, None, 0, None): {
                            ("Up", fx, rb, u, 166): {},
                            ("Down", fx, rb, u, 167): {}
                            # },
                        },
                        ("Sagittal", fx, cb, u, 168): {
                            # (subgroup, None, 1, None): {
                            ("Distal", fx, rb, u, 169): {},
                            ("Proximal", fx, rb, u, 170): {}
                            # },
                        },
                    }
                }
            }
        },
        ("Trill", fx, cb, u, 171): {
            (subgroup, None, 0, None, 172): {
                ("Not trilled", fx, rb, u, 173): {},
                ("Trilled", fx, rb, u, 174): {}
            }
        },
        ("Directionality", fx, cb, u, 175): {
            (subgroup, None, 0, None, 176): {
                ("Unidirectional", fx, rb, u, 177): {},
                ("Bidirectional", fx, rb, u, 178): {}
            }
        },
        ("Additional characteristics", fx, cb, u, 179): {
            ("Size", fx, cb, u, 180): {
                (subgroup, None, 0, None, 181): {
                    ("Big", fx, rb, u, 182): {},
                    ("Normal", fx, rb, u, 183): {},
                    ("Small", fx, rb, u, 184): {},
                    ("Other", ed_3, rb, u, 185): {},
                },
                (subgroup, None, 1, None, 187): {
                    ("Relative to", ed_3, cb, u, 188): {},
                }
            },
            ("Speed", fx, cb, u, 190): {
                (subgroup, None, 0, None, 191): {
                    ("Fast", fx, rb, u, 192): {},
                    ("Normal", fx, rb, u, 193): {},
                    ("Slow", fx, rb, u, 194): {},
                    ("Other", ed_3, rb, u, 195): {},
                },
                (subgroup, None, 1, None, 197): {
                    ("Relative to", ed_3, cb, u, 198): {},
                }
            },
            ("Force", fx, cb, u, 200): {
                (subgroup, None, 0, None, 201): {
                    ("Strong", fx, rb, u, 202): {},
                    ("Normal", fx, rb, u, 203): {},
                    ("Weak", fx, rb, u, 204): {},
                    ("Other", ed_3, rb, u, 205): {},
                },
                (subgroup, None, 1, None, 207): {
                    ("Relative to", ed_3, cb, u, 208): {},
                }
            },
            ("Tension", fx, cb, u, 210): {
                (subgroup, None, 0, None, 211): {
                    ("Tense", fx, rb, u, 212): {},
                    ("Normal", fx, rb, u, 213): {},
                    ("Lax", fx, rb, u, 214): {},
                    ("Other", ed_3, rb, u, 215): {},
                },
                (subgroup, None, 1, None, 217): {
                    ("Relative to", ed_3, cb, u, 218): {},
                }
            }
        }
    }
}


class TreeSearchComboBox(QComboBox):

    def __init__(self, parentlayout=None):
        super().__init__()
        self.refreshed = True
        self.lasttextentry = ""
        self.lastcompletedentry = ""
        self.parentlayout = parentlayout

    def keyPressEvent(self, event):
        key = event.key()
        modifiers = event.modifiers()

        if key == Qt.Key_Right:  # TODO KV and modifiers == Qt.NoModifier:

            if self.currentText():
                self.parentlayout.treedisplay.collapseAll()
                itemstoselect = gettreeitemsinpath(self.parentlayout.treemodel, self.currentText(), delim=delimiter)
                for item in itemstoselect:
                    if item.checkState() == Qt.Unchecked:
                        item.setCheckState(Qt.PartiallyChecked)
                    self.parentlayout.treedisplay.setExpanded(item.index(), True)
                itemstoselect[-1].setCheckState(Qt.Checked)
                self.setCurrentIndex(-1)

        if key == Qt.Key_Period and modifiers == Qt.ControlModifier:
            if self.refreshed:
                self.lasttextentry = self.currentText()
                self.refreshed = False

            if self.lastcompletedentry:
                # cycle to first line of next entry that starts with the last-entered text
                foundcurrententry = False
                foundnextentry = False
                i = 0
                while self.completer().setCurrentRow(i) and not foundnextentry:
                    completionoption = self.completer().currentCompletion()
                    if completionoption.lower().startswith(self.lastcompletedentry.lower()):
                        foundcurrententry = True
                    elif foundcurrententry and self.lasttextentry.lower() in completionoption.lower() and not completionoption.lower().startswith(self.lastcompletedentry.lower()):
                        foundnextentry = True
                        if delimiter in completionoption[len(self.lasttextentry):]:
                            self.setEditText(
                                completionoption[:completionoption.index(delimiter, len(self.lasttextentry)) + 1])
                        else:
                            self.setEditText(completionoption)
                        self.lastcompletedentry = self.currentText()
                    i += 1
            else:
            # if not self.lastcompletedentry:
                # cycle to first line of first entry that starts with the last-entered text
                foundnextentry = False
                i = 0
                while self.completer().setCurrentRow(i) and not foundnextentry:
                    completionoption = self.completer().currentCompletion()
                    if completionoption.lower().startswith(self.lasttextentry.lower()):
                        foundnextentry = True
                        if delimiter in completionoption[len(self.lasttextentry):]:
                            self.setEditText(
                                completionoption[:completionoption.index(delimiter, len(self.lasttextentry)) + 1])
                        else:
                            self.setEditText(completionoption)
                        self.lastcompletedentry = self.currentText()
                    i += 1

        else:
            self.refreshed = True
            self.lasttextentry = ""
            self.lastcompletedentry = ""
            super().keyPressEvent(event)


# This class is a serializable form of the class MovementTreeModel, which is itself not pickleable.
# Rather than being based on QStandardItemModel, this one uses dictionary structures to convert to
# and from saveable form.
class MovementTreeSerializable:

    def __init__(self, mvmttreemodel):

        # creates a full serializable copy of the movement tree, eg for saving to disk
        treenode = mvmttreemodel.invisibleRootItem()

        self.numvals = {}  # deprecated
        self.stringvals = {}  # deprecated
        self.checkstates = {}
        self.addedinfos = {}
        self.userspecifiedvalues = {}

        self.collectdatafromMovementTreeModel(treenode)

    def collectdatafromMovementTreeModel(self, treenode):
        if treenode is not None:
            for r in range(treenode.rowCount()):
                treechild = treenode.child(r, 0)
                if treechild is not None:
                    pathtext = treechild.data(Qt.UserRole + udr.pathdisplayrole)
                    checkstate = treechild.checkState()
                    addedinfo = treechild.addedinfo
                    self.addedinfos[pathtext] = copy(addedinfo)
                    iseditable = treechild.data(Qt.UserRole + udr.isuserspecifiablerole) != fx
                    userspecifiedvalue = treechild.data(Qt.UserRole + udr.userspecifiedvaluerole)
                    if iseditable:
                        self.userspecifiedvalues[pathtext] = userspecifiedvalue

                    self.checkstates[pathtext] = checkstate
                self.collectdatafromMovementTreeModel(treechild)

    def getMovementTreeModel(self):
        mvmttreemodel = MovementTreeModel()
        rootnode = mvmttreemodel.invisibleRootItem()
        mvmttreemodel.populate(rootnode)
        makelistmodel = mvmttreemodel.listmodel  # TODO KV   what is this? necessary?
        self.backwardcompatibility()
        self.setvaluesinMovementTreeModel(rootnode)
        return mvmttreemodel

    def backwardcompatibility(self):
        hadtoaddusv = False
        if not hasattr(self, 'userspecifiedvalues'):
            self.userspecifiedvalues = {}
            hadtoaddusv = True
        for stored_dict in [self.checkstates, self.addedinfos]:  # self.numvals, self.stringvals,
            pairstoadd = {}
            keystoremove = []
            for k in stored_dict.keys():

                # 1. "H1 and H2 move in different directions" (under either axis driectin or plane, in perceptual shape)
                #   --> "H1 and H2 move in opposite directions"
                # 2. Then later... "H1 and H2 move in opposite directions" (under axis direction only)
                #   --> "H1 and H2 move toward each other" (along with an independent addition of "... away ...")
                if "H1 and H2 move in different directions" in k:
                    if "Axis direction" in k:
                        pairstoadd[k.replace("in different directions", "toward each other")] = stored_dict[k]
                        keystoremove.append(k)
                    elif "Plane" in k:
                        pairstoadd[k.replace("move in different directions", "move in opposite directions")] = stored_dict[k]
                        keystoremove.append(k)
                elif "H1 and H2 move in opposite directions" in k and "Axis direction" in k:
                    pairstoadd[k.replace("in opposite directions", "toward each other")] = stored_dict[k]
                    keystoremove.append(k)

                if hadtoaddusv:

                    if k.endswith(specifytotalcycles_str) or k.endswith(numberofreps_str):
                        pairstoadd[k.replace(numberofreps_str, specifytotalcycles_str)] = stored_dict[k]
                        keystoremove.append(k)

                    elif "This number is a minimum" in k:
                        pairstoadd[k.replace(delimiter + "#" + delimiter, delimiter)] = stored_dict[k]
                        keystoremove.append(k)

                    elif (specifytotalcycles_str + delimiter in k or numberofreps_str + delimiter in k):
                        # then we're looking at the item that stores info about the specified number of repetitions
                        newkey = k.replace(numberofreps_str, specifytotalcycles_str)
                        newkey = newkey[:newkey.index(specifytotalcycles_str+delimiter) + len(specifytotalcycles_str)]
                        remainingtext = ""
                        if specifytotalcycles_str in k:
                            remainingtext = k[k.index(specifytotalcycles_str + delimiter) + len(specifytotalcycles_str + delimiter):]
                        elif numberofreps_str in k:
                            remainingtext = k[k.index(specifytotalcycles_str + delimiter) + len(numberofreps_str + delimiter):]

                        if len(remainingtext) > 0 and delimiter not in remainingtext and remainingtext != "#":
                            numcycles = remainingtext
                            self.userspecifiedvalues[newkey] = numcycles

            for oldkey in keystoremove:
                stored_dict.pop(oldkey)

            for newkey in pairstoadd.keys():
                stored_dict[newkey] = pairstoadd[newkey]

    def setvaluesinMovementTreeModel(self, treenode):
        if treenode is not None:
            for r in range(treenode.rowCount()):
                treechild = treenode.child(r, 0)
                if treechild is not None:
                    pathtext = treechild.data(Qt.UserRole + udr.pathdisplayrole)
                    if pathtext in self.checkstates.keys():
                        treechild.setCheckState(self.checkstates[pathtext])

                    if pathtext in self.addedinfos.keys():
                        treechild.addedinfo = copy(self.addedinfos[pathtext])

                    if pathtext in self.userspecifiedvalues.keys():
                        # this also updates the associated list item as well as its display
                        treechild.setData(self.userspecifiedvalues[pathtext], Qt.UserRole + udr.userspecifiedvaluerole)
                        treechild.editablepart().setText(self.userspecifiedvalues[pathtext])

                    self.setvaluesinMovementTreeModel(treechild)


# This class is a serializable form of the class MovementModule, which is itself not pickleable
# due to its component MovementTreeModel.
class MovementModuleSerializable(ParameterModuleSerializable):

    def __init__(self, mvmtmodule):
        super().__init__(mvmtmodule)

        # creates a full serializable copy of the movement module, eg for saving to disk
        self.inphase = mvmtmodule.inphase
        self.movementtree = MovementTreeSerializable(mvmtmodule.movementtreemodel)
    #
    # def getMovementTreeModel(self):
    #     mvmttreemodel = MovementTreeModel()
    #     rootnode = mvmttreemodel.invisibleRootItem()
    #     mvmttreemodel.populate(rootnode)
    #     makelistmodel = mvmttreemodel.listmodel
    #     self.setvalues(rootnode)
    #     return mvmttreemodel


class MovementTreeModel(QStandardItemModel):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._listmodel = None  # MovementListModel(self)
        self.setColumnCount(2)
        self.itemChanged.connect(self.updateCheckState)
        self.dataChanged.connect(self.updaterelateddata)

    # def tempprinttreemodel(self):
    #     print("treemodel contents...")
    #     # print("location type: ", tm.locationtype)
    #     self.tempprinttmhelper(self.invisibleRootItem())
    #
    # def tempprinttmhelper(self, node, indent=""):
    #     for r in range(node.rowCount()):
    #         ch = node.child(r, 0)
    #         ch_edit = node.child(r, 1)
    #         edit_text = ch_edit.text()
    #         usvrole = node.data(Qt.UserRole+udr.userspecifiedvaluerole)  # this is None
    #         print(indent + ch.text() + " / checked " + str(ch.checkState()) + " / edit_text " + edit_text)  #  + " / usvrole " + usvrole)
    #         self.tempprinttmhelper(ch, indent=indent + " ")

    def findItemsByRoleValues(self, role, possiblevalues, parentnode=None):
        if not isinstance(possiblevalues, list):
            possiblevalues = [possiblevalues]
        if parentnode is None:
            parentnode = self.invisibleRootItem()

        items = []
        numchildren = parentnode.rowCount()
        for i in range(numchildren):
            child = parentnode.child(i, 0)
            roledata = child.data(role)
            matches = [roledata == pv for pv in possiblevalues]
            if True in matches:
                items.append(child)

            subresults = self.findItemsByRoleValues(role, possiblevalues, parentnode=child)
            items.extend(subresults)
        return items

    def updaterelateddata(self, topLeft, bottomRight):
        editableitem = self.itemFromIndex(topLeft)
        if isinstance(editableitem, QStandardItem) and not isinstance(editableitem, MovementTreeItem) and not isinstance(editableitem, MovementListItem):

            proposedtext = editableitem.text()

            treeitem = editableitem.parent().child(editableitem.row(), 0)
            userspecifiability = treeitem.data(Qt.UserRole+udr.isuserspecifiablerole)
            previoustext = treeitem.data(Qt.UserRole+udr.userspecifiedvaluerole)
            updatedtext = self.validateeditedtext(proposedtext, userspecifiability, previoustext)

            editableitem.setText("specify" if updatedtext == "" else updatedtext)
            treeitem.setData("" if updatedtext == "specify" else updatedtext, role=Qt.UserRole+udr.userspecifiedvaluerole) # this auto-updates the list item and its display as well
            if treeitem.data(role=Qt.UserRole+udr.userspecifiedvaluerole) != "" and treeitem.checkState() != Qt.Checked:
                treeitem.check(fully=True)

    def validateeditedtext(self, proposedtext, userspecifiability, previoustext):
        valid = False
        if proposedtext == "specify" or proposedtext == "":
            valid = True
        if userspecifiability == ed_1:
            if proposedtext.isnumeric():
                num = int(proposedtext)
                valid = num >= 1
            elif proposedtext.replace(".", "").isnumeric():
                num = float(proposedtext)
                valid = (num >= 1) and (num % 0.5 == 0)
        elif userspecifiability == ed_2:
            valid = proposedtext.replace(".", "").isnumeric()
        elif userspecifiability == ed_3:
            valid = True

        updatedtext = proposedtext if valid else previoustext

        if updatedtext != proposedtext:
            # revert to previous value
            messagestring = "Invalid text: this field must be "
            if userspecifiability == ed_1:
                messagestring += ">= 1 and a multiple of 0.5"
            elif userspecifiability == ed_2:
                messagestring += "numeric"
            elif userspecifiability == ed_3:
                messagestring += "anything (unrestricted)"
            QMessageBox.critical(None, "Warning", messagestring)

        return updatedtext


    def updateCheckState(self, item):
        if not isinstance(item, MovementTreeItem):
            # eg, if it's just a QStandardItem representing the editable part of a treeitem
            return
        thestate = item.checkState()
        if thestate == Qt.Checked:
            # TODO KV then the user must have checked it,
            #  so make sure to partially-fill ancestors and also look at ME siblings
            item.check(fully=True)
        elif thestate == Qt.PartiallyChecked:
            # TODO KV then the software must have updated it based on some other user action
            # make sure any ME siblings are unchecked
            item.check(fully=False)
        elif thestate == Qt.Unchecked:
            # TODO KV then either...
            # (1) the user unchecked it and we have to uncheck ancestors and look into ME siblings, or
            # (2) it was unchecked as a (previously partially-checked) ancestor of a user-unchecked node, or
            # (3) it was force-unchecked as a result of ME/sibling interaction
            item.uncheck(force=False)
        # if thestate in [Qt.Checked, Qt.PartiallyChecked]:
        #     item.check(thestate == Qt.Checked)
        # else:
        #     item.uncheck()

    def populate(self, parentnode, structure={}, pathsofar="", issubgroup=False, isfinalsubgroup=True, subgroupname=""):
        if structure == {} and pathsofar != "":
            # base case (leaf node); don't build any more nodes
            pass
        elif structure == {} and pathsofar == "":
            # no parameters; build a tree from the default structure
            # TODO KV define a default structure somewhere (see constant.py)
            self.populate(parentnode, structure=mvmtOptionsDict, pathsofar="")
        elif structure != {}:
            # internal node with substructure
            numentriesatthislevel = len(structure.keys())
            for idx, labelclassifierchecked_5tuple in enumerate(structure.keys()):
                label = labelclassifierchecked_5tuple[0]
                userspecifiability = labelclassifierchecked_5tuple[1]
                classifier = labelclassifierchecked_5tuple[2]
                checked = labelclassifierchecked_5tuple[3]
                node_id = labelclassifierchecked_5tuple[4]
                ismutuallyexclusive = classifier == rb
                iseditable = userspecifiability != fx
                if label == subgroup:

                    # make the tree items in the subgroup and whatever nested structure they have
                    isfinal = False
                    if idx + 1 >= numentriesatthislevel:
                        # if there are no more items at this level
                        isfinal = True
                    self.populate(parentnode, structure=structure[labelclassifierchecked_5tuple], pathsofar=pathsofar, issubgroup=True, isfinalsubgroup=isfinal, subgroupname=subgroup+"_"+pathsofar+"_"+(str(classifier)))

                else:
                    thistreenode = MovementTreeItem(label, mutuallyexclusive=ismutuallyexclusive)
                    thistreenode.setData(userspecifiability, Qt.UserRole+udr.isuserspecifiablerole)
                    editablepart = QStandardItem()
                    editablepart.setEditable(iseditable)
                    editablepart.setText("specify" if iseditable else "")
                    thistreenode.setData(pathsofar + label, role=Qt.UserRole + udr.pathdisplayrole)
                    thistreenode.setCheckState(Qt.Checked if checked else Qt.Unchecked)
                    if issubgroup:
                        thistreenode.setData(subgroupname, role=Qt.UserRole+udr.subgroupnamerole)
                        if idx + 1 == numentriesatthislevel:
                            thistreenode.setData(True, role=Qt.UserRole + udr.lastingrouprole)
                            thistreenode.setData(isfinalsubgroup, role=Qt.UserRole + udr.finalsubgrouprole)
                    self.populate(thistreenode, structure=structure[labelclassifierchecked_5tuple], pathsofar=pathsofar+label+delimiter)
                    parentnode.appendRow([thistreenode, editablepart])

    @property
    def listmodel(self):
        if self._listmodel is None:
            self._listmodel = MovementListModel(self)
        return self._listmodel

    @listmodel.setter
    def listmodel(self, listmod):
        self._listmodel = listmod


class MovementTreeView(QTreeView):

    # adapted from https://stackoverflow.com/questions/68069548/checkbox-with-persistent-editor
    def edit(self, index, trigger, event):
        # if the edit involves an index change, there's no event
        if (event and index.column() == 0 and index.flags() & Qt.ItemIsUserCheckable and event.type() in (event.MouseButtonPress, event.MouseButtonDblClick) and event.button() == Qt.LeftButton and self.isPersistentEditorOpen(index)):
            opt = self.viewOptions()
            opt.rect = self.visualRect(index)
            opt.features |= opt.HasCheckIndicator
            checkRect = self.style().subElementRect(
                QStyle.SE_ItemViewItemCheckIndicator,
                opt, self)
            if event.pos() in checkRect:
                if index.data(Qt.CheckStateRole):
                    self.model().itemFromIndex(index).uncheck()
                else:
                    self.model().itemFromIndex(index).check()
        return super().edit(index, trigger, event)


class MovementTreeItem(QStandardItem):

    def __init__(self, txt="", listit=None, mutuallyexclusive=False, addedinfo=None, serializedmvmtitem=None):
        super().__init__()

        self.setEditable(False)

        if serializedmvmtitem:
            self.setText(serializedmvmtitem['text'])
            self.setCheckable(serializedmvmtitem['checkable'])
            self.setCheckState(serializedmvmtitem['checkstate'])
            self.setUserTristate(serializedmvmtitem['usertristate'])
            self.setData(serializedmvmtitem['selectedrole'], Qt.UserRole+udr.selectedrole)
            # self.setData(serializedmvmtitem['texteditrole'], Qt.UserRole+udr.texteditrole)
            self.setData(serializedmvmtitem['timestamprole'], Qt.UserRole+udr.timestamprole)
            self.setData(serializedmvmtitem['isuserspecifiablerole'], Qt.UserRole+udr.isuserspecifiablerole)
            self.setData(serializedmvmtitem['userspecifiedvaluerole'], Qt.UserRole+udr.userspecifiedvaluerole)
            self.setData(serializedmvmtitem['mutuallyexclusiverole'], Qt.UserRole+udr.mutuallyexclusiverole)
            self.setData(serializedmvmtitem['displayrole'], Qt.DisplayRole)
            self._addedinfo = serializedmvmtitem['addedinfo']
            self.listitem = MovementListItem(serializedlistitem=serializedmvmtitem['listitem'])
            self.listitem.treeitem = self
        else:
            self.setText(txt)
            self.setCheckable(True)
            self.setCheckState(Qt.Unchecked)
            self.setUserTristate(False)
            self.setData(False, Qt.UserRole+udr.selectedrole)
            # self.setData(False, Qt.UserRole+udr.texteditrole)
            self.setData(QDateTime.currentDateTimeUtc(), Qt.UserRole+udr.timestamprole)
            self.setData(fx, Qt.UserRole+udr.isuserspecifiablerole)
            self.setData("", Qt.UserRole+udr.userspecifiedvaluerole)
            self._addedinfo = addedinfo if addedinfo is not None else AddedInfo()

            if mutuallyexclusive:
                self.setData(True, Qt.UserRole+udr.mutuallyexclusiverole)
            else:
                self.setData(False, Qt.UserRole+udr.mutuallyexclusiverole)

            self.listitem = listit
            if listit is not None:
                self.listitem.treeitem = self

    def __repr__(self):
        return '<MovementTreeItem: ' + repr(self.text()) + '>'

    def setData(self, value, role=Qt.DisplayRole):
        super().setData(value, role)

        if role == Qt.UserRole + udr.userspecifiedvaluerole and hasattr(self, "listitem") and self.listitem is not None:
            # also update the associated list item (and its displayed value)
            self.listitem.setData(value, role)

    def serialize(self):
        return {
            'text': self.text(),
            'checkable': self.isCheckable(),
            'checkstate': self.checkState(),
            'usertristate': self.isUserTristate(),
            'selectedrole': self.data(Qt.UserRole+udr.selectedrole),
            # 'texteditrole': self.data(Qt.UserRole+udr.texteditrole),
            'timestamprole': self.data(Qt.UserRole+udr.timestamprole),
            'mutuallyexclusiverole': self.data(Qt.UserRole+udr.mutuallyexclusiverole),
            'displayrole': self.data(Qt.DisplayRole),
            'isuserspecifiablerole': self.data(Qt.UserRole+udr.isuserspecifiablerole),
            'userspecifiedvaluerole': self.data(Qt.UserRole+udr.userspecifiedvaluerole),
            'addedinfo': self._addedinfo,
            'nodetypeID': self._nodetypeID
            # 'listitem': self.listitem.serialize()  # TODO KV why not? the constructor uses it...
        }

    def editablepart(self):
        return self.parent().child(self.row(), 1)

    @property
    def addedinfo(self):
        return self._addedinfo

    @addedinfo.setter
    def addedinfo(self, addedinfo):
        self._addedinfo = addedinfo if addedinfo is not None else AddedInfo()

    @property
    def nodetypeID(self):
        return self._nodetypeID

    @nodetypeID.setter
    def nodetypeID(self, nodetypeID):
        self._nodetypeID = nodetypeID if nodetypeID is not None else -1

    def check(self, fully=True):
        self.setCheckState(Qt.Checked if fully else Qt.PartiallyChecked)
        self.listitem.setData(fully, Qt.UserRole+udr.selectedrole)
        if fully:
            self.setData(QDateTime.currentDateTimeUtc(), Qt.UserRole+udr.timestamprole)
            self.listitem.setData(QDateTime.currentDateTimeUtc(), Qt.UserRole+udr.timestamprole)
        self.checkancestors()

        # gather siblings in order to deal with mutual exclusivity (radio buttons)
        siblings = self.collectsiblings()

        # if this is a radio button item, make sure none of its siblings are checked
        if self.data(Qt.UserRole+udr.mutuallyexclusiverole):
            for sib in siblings:
                sib.uncheck(force=True)
        else:  # or if it has radio button siblings, make sure they are unchecked
            for me_sibling in [s for s in siblings if s.data(Qt.UserRole+udr.mutuallyexclusiverole)]:
                me_sibling.uncheck(force=True)

    def collectsiblings(self):

        siblings = []
        parent = self.parent()
        if not parent:
            parent = self.model().invisibleRootItem()
        numsiblingsincludingself = parent.rowCount()
        for snum in range(numsiblingsincludingself):
            sibling = parent.child(snum, 0)
            if sibling.index() != self.index():  # ie, it's actually a sibling
                siblings.append(sibling)

        mysubgroup = self.data(Qt.UserRole+udr.subgroupnamerole)
        subgrouporgeneralsiblings = [sib for sib in siblings if sib.data(Qt.UserRole+udr.subgroupnamerole) == mysubgroup or not sib.data(Qt.UserRole+udr.subgroupnamerole)]
        subgroupsiblings = [sib for sib in siblings if sib.data(Qt.UserRole+udr.subgroupnamerole) == mysubgroup]

        # if I'm ME and in a subgroup, collect siblings from my subgroup and also those at my level but not in any subgroup
        if self.data(Qt.UserRole+udr.mutuallyexclusiverole) and mysubgroup:
            return subgrouporgeneralsiblings
        # if I'm ME and not in a subgroup, collect all siblings from my level (in subgroups or no)
        elif self.data(Qt.UserRole+udr.mutuallyexclusiverole):
            return siblings
        # if I'm *not* ME but I'm in a subgroup, collect all siblings from my subgroup and also those at my level but not in any subgroup
        elif not self.data(Qt.UserRole + udr.mutuallyexclusiverole) and mysubgroup:
            return subgrouporgeneralsiblings
        # if I'm *not* ME and not in a subgroup, collect all siblings from my level (in subgroups or no)
        elif not self.data(Qt.UserRole+udr.mutuallyexclusiverole):
            return siblings

    def checkancestors(self):
        if self.checkState() == Qt.Unchecked:
            self.setCheckState(Qt.PartiallyChecked)
        if self.parent() is not None:
            self.parent().checkancestors()

    def uncheck(self, force=False):
        name = self.data()

        self.listitem.setData(False, Qt.UserRole+udr.selectedrole)
        self.setData(False, Qt.UserRole+udr.selectedrole)

        # TODO KV - can't just uncheck a radio button... or can we?

        if force:  # force-clear this item and all its descendants - have to start at the bottom?
            # self.forceuncheck()
            # force-uncheck all descendants
            if self.hascheckedchild():
                for r in range(self.rowCount()):
                    for c in [0]:  # range(self.columnCount()):
                        ch = self.child(r, c)
                        if ch is not None:
                            ch.uncheck(force=True)
            self.setCheckState(Qt.Unchecked)
        elif self.hascheckedchild():
            self.setCheckState(Qt.PartiallyChecked)
        else:
            self.setCheckState(Qt.Unchecked)
            if self.parent() is not None:
                self.parent().uncheckancestors()

        if self.data(Qt.UserRole+udr.mutuallyexclusiverole):
            pass
            # TODO KV is this relevant? shouldn't be able to uncheck anyway
        elif True:  # has a mutually exclusive sibling
            pass
            # might one of those sibling need to be checked, if none of the boxes are?

    def uncheckancestors(self):
        if self.checkState() == Qt.PartiallyChecked and not self.hascheckedchild():
            self.setCheckState(Qt.Unchecked)
            if self.parent() is not None:
                self.parent().uncheckancestors()

    def hascheckedchild(self):
        foundone = False
        numrows = self.rowCount()
        numcols = self.columnCount()
        r = 0
        while not foundone and r < numrows:
            c = 0
            while not foundone and c < numcols:
                child = self.child(r, c)
                if child is not None:
                    foundone = child.checkState() in [Qt.Checked, Qt.PartiallyChecked]
                c += 1
            r += 1
        return foundone


class MovementListItem(QStandardItem):

    def __init__(self, pathtxt="", nodetxt="", treeit=None, serializedlistitem=None):
        super().__init__()

        if serializedlistitem:
            self.setEditable(serializedlistitem['editable'])
            self.setText(serializedlistitem['text'])
            self.setData(serializedlistitem['nodedisplayrole'], Qt.UserRole+udr.nodedisplayrole)
            self.setData(serializedlistitem['timestamprole'], Qt.UserRole+udr.timestamprole)
            self.setCheckable(serializedlistitem['checkable'])
            self.setData(serializedlistitem['selectedrole'], Qt.UserRole+udr.selectedrole)
        else:
            self.setEditable(False)
            self.setText(pathtxt)
            self.setData(nodetxt, Qt.UserRole+udr.nodedisplayrole)
            self.setData(QDateTime.currentDateTimeUtc(), Qt.UserRole+udr.timestamprole)
            self.setCheckable(False)
            self.treeitem = treeit
            if treeit is not None:
                self.treeitem.listitem = self
            self.setData(False, Qt.UserRole+udr.selectedrole)

    def setData(self, value, role=Qt.DisplayRole):
        super().setData(value, role)
        if role == Qt.UserRole + udr.userspecifiedvaluerole and hasattr(self, "treeitem") and self.treeitem is not None:

            if self.treeitem.data(Qt.UserRole+udr.isuserspecifiablerole):
                currentlistdisplay = self.data(Qt.DisplayRole)
                newlistdisplay = re.sub(" \[.*\]$", "", currentlistdisplay)
                if value != "":
                    newlistdisplay += " [" + value + "]"
                self.setData(newlistdisplay, Qt.DisplayRole)

    def __repr__(self):
        return '<MovementListItem: ' + repr(self.text()) + '>'

    def updateuserspecifiedvalue(self, usv):
        self.setData()

    def unselectpath(self):
        self.treeitem.uncheck()

    def selectpath(self):
        self.treeitem.check(fully=True)


class MovementPathsProxyModel(QSortFilterProxyModel):

    def __init__(self, parent=None, wantselected=None):
        super(MovementPathsProxyModel, self).__init__(parent)
        self.wantselected = wantselected
        self.setSortCaseSensitivity(Qt.CaseInsensitive)

    def filterAcceptsRow(self, source_row, source_parent):
        if self.wantselected is None:
            source_index = self.sourceModel().index(source_row, 0, source_parent)
            text = self.sourceModel().index(source_row, 0, source_parent).data()
            return True
        else:
            source_index = self.sourceModel().index(source_row, 0, source_parent)
            isselected = source_index.data(role=Qt.UserRole+udr.selectedrole)
            path = source_index.data(role=Qt.UserRole+udr.pathdisplayrole)
            text = self.sourceModel().index(source_row, 0, source_parent).data()
            return self.wantselected == isselected

    def updatesorttype(self, sortbytext=""):
        if "alpha" in sortbytext and "path" in sortbytext:
            self.setSortRole(Qt.DisplayRole)
            self.sort(0)
        elif "alpha" in sortbytext and "node" in sortbytext:
            self.setSortRole(Qt.UserRole+udr.nodedisplayrole)
            self.sort(0)
        elif "tree" in sortbytext:
            self.sort(-1)  # returns to sort order of underlying model
        elif "select" in sortbytext:
            self.setSortRole(Qt.UserRole+udr.timestamprole)
            self.sort(0)


class MovementListModel(QStandardItemModel):

    def __init__(self, treemodel=None):
        super().__init__()
        self.treemodel = treemodel
        if self.treemodel is not None:
            # build this listmodel from the treemodel
            treeparentnode = self.treemodel.invisibleRootItem()
            self.populate(treeparentnode)
            self.treemodel.listmodel = self

    def populate(self, treenode):
        for r in range(treenode.rowCount()):
            treechild = treenode.child(r, 0)
            if treechild is not None:
                pathtext = treechild.data(role=Qt.UserRole+udr.pathdisplayrole)
                nodetext = treechild.data(Qt.DisplayRole)
                listitem = MovementListItem(pathtxt=pathtext, nodetxt=nodetext, treeit=treechild)  # also sets treeitem's listitem
                self.appendRow(listitem)
                self.populate(treechild)

    def setTreemodel(self, treemod):
        self.treemodel = treemod


class TreeListView(QListView):

    def __init__(self):
        super().__init__()

    def keyPressEvent(self, event):
        key = event.key()
        # modifiers = event.modifiers()

        if key == Qt.Key_Delete:
            indexesofselectedrows = self.selectionModel().selectedRows()
            selectedlistitems = []
            for itemindex in indexesofselectedrows:
                listitemindex = self.model().mapToSource(itemindex)
                listitem = self.model().sourceModel().itemFromIndex(listitemindex)
                selectedlistitems.append(listitem)
            for listitem in selectedlistitems:
                listitem.unselectpath()
            # self.model().dataChanged.emit()


def gettreeitemsinpath(treemodel, pathstring, delim="/"):
    pathlist = pathstring.split(delim)
    pathitemslists = []
    for level in pathlist:
        pathitemslists.append(treemodel.findItems(level, Qt.MatchRecursive))
    validpathsoftreeitems = findvaliditemspaths(pathitemslists)
    return validpathsoftreeitems[0]


def findvaliditemspaths(pathitemslists):
    validpaths = []
    if len(pathitemslists) > 1:  # the path is longer than 1 level
        # pathitemslistslotohi = pathitemslists[::-1]
        for lastitem in pathitemslists[-1]:
            for secondlastitem in pathitemslists[-2]:
                if lastitem.parent() == secondlastitem:
                    higherpaths = findvaliditemspaths(pathitemslists[:-2]+[[secondlastitem]])
                    for higherpath in higherpaths:
                        if len(higherpath) == len(pathitemslists)-1:  # TODO KV
                            validpaths.append(higherpath + [lastitem])
    elif len(pathitemslists) == 1:  # the path is only 1 level long (but possibly with multiple options)
        for lastitem in pathitemslists[0]:
            # if lastitem.parent() == .... used to be if topitem.childCount() == 0:
            validpaths.append([lastitem])
    else:
        # nothing to add to paths - this case shouldn't ever happen because base case is length==1 above
        # but just in case...
        validpaths = []

    return validpaths
