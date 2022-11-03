import os

from PyQt5.QtCore import (
    Qt,
    QAbstractListModel,
    pyqtSignal,
    QModelIndex,
    QItemSelectionModel,
    QSortFilterProxyModel,
    QDateTime,
    QRectF
)

from PyQt5.Qt import (
    QStandardItem,
    QStandardItemModel
)

from PyQt5.QtGui import QPixmap

from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QListView,
    QVBoxLayout,
    QComboBox,
    QTreeView,
    QStyle,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem
)


# TODO KV - is this where I actually want to define these?
delimiter = ">"  # TODO KV - should this be user-defined in global settings? or maybe even in the mvmt window?
selectedrole = 0
pathdisplayrole = 1
mutuallyexclusiverole = 2
texteditrole = 3
lastingrouprole = 4
finalsubgrouprole = 5
subgroupnamerole = 6
nodedisplayrole = 7
timestamprole = 8

# radio button vs checkbox
rb = "radio button"  # ie mutually exclusive in group / at this level
cb = "checkbox"  # ie not mutually exlusive

# editable vs fixed
ed = "editable" 
fx = "fixed"  # ie not editable

# in subgroup?
subgroup = "subgroup"

# checked vs unchecked
c = True  # checked
u = False  # unchecked

# TODO KV: should be able to get rid of "fx" and "subgroup" (and maybe other?) options here...
# unless we're going to reference the same code (as for moevment) for building the tree & list models
locn_options_bodyanchored = {
    # ("No movement", fx, rb, u): {},
    ("Head", fx, rb, u): {
        ("Back of head", fx, rb, u): {},
        ("Top of head", fx, rb, u): {},
        ("Side of face", fx, rb, u): {
            ("Side of face - contra", fx, rb, u): {},
            ("Side of face - ipsi", fx, rb, u): {}
        },
        ("Face", fx, rb, u): {
            ("Temple", fx, rb, u): {
                ("Temple - contra", fx, rb, u): {},
                ("Temple - ipsi", fx, rb, u): {}
            },
            ("Above forehead (hairline)", fx, rb, u): {},
            ("Forehead", fx, rb, u): {},
            ("Eyebrow", fx, rb, u): {
                ("Eyebrow - contra", fx, rb, u): {},
                ("Eyebrow - ipsi", fx, rb, u): {},
                ("Between eyebrows", fx, rb, u): {}
            },
            ("Eye", fx, rb, u): {
                ("Eye - contra", fx, rb, u): {},
                ("Eye - ipsi", fx, rb, u): {},
                ("Outer corner of eye", fx, rb, u): {
                    ("Outer corner of eye - contra", fx, rb, u): {},
                    ("Outer corner of eye - ipsi", fx, rb, u): {}
                },
                ("Upper eyelid", fx, rb, u): {
                    ("Upper eyelid - contra", fx, rb, u): {},
                    ("Upper eyelid - ipsi", fx, rb, u): {}
                },
                ("Lower eyelid", fx, rb, u): {
                    ("Lower eyelid - contra", fx, rb, u): {},
                    ("Lower eyelid - ipsi", fx, rb, u): {}
                }
            },
            ("Cheek/nose", fx, rb, u): {
                ("Cheek", fx, rb, u): {
                    ("Cheek - contra", fx, rb, u): {},
                    ("Cheek - ipsi", fx, rb, u): {}
                },
                ("Maxillary process of zygomatic", fx, rb, u): {
                    ("Maxillary process of zygomatic - contra", fx, rb, u): {},
                    ("Maxillary process of zygomatic - ipsi", fx, rb, u): {}
                },
                ("Zygomatic process of temporal bone", fx, rb, u): {
                    ("Zygomatic process of temporal bone - contra", fx, rb, u): {},
                    ("Zygomatic process of temporal bone - ipsi", fx, rb, u): {}
                },
                ("Nose", fx, rb, u): {
                    ("Nose root", fx, rb, u): {},
                    ("Nose ridge", fx, rb, u): {},
                    ("Nose tip", fx, rb, u): {},
                    ("Septum", fx, rb, u): {}
                }
            },
            ("Below nose / philtrum", fx, rb, u): {},
            ("Mouth", fx, rb, u): {
                ("Lips", fx, rb, u): {
                    ("Upper lip", fx, rb, u): {},
                    ("Lower lip", fx, rb, u): {}
                },
                ("Corner of mouth - contra", fx, rb, u): {},
                ("Corner of mouth - ipsi", fx, rb, u): {},
                ("Teeth", fx, rb, u): {
                    ("Upper teeth", fx, rb, u): {},
                    ("Lower teeth", fx, rb, u): {}
                },
                ("Tongue", fx, rb, u): {},
            },
            ("Ear", fx, rb, u): {
                ("Ear - contra", fx, rb, u): {},
                ("Ear - ipsi", fx, rb, u): {},
                ("Mastoid process", fx, rb, u): {
                    ("Mastoid process - contra", fx, rb, u): {},
                    ("Mastoid process - ipsi", fx, rb, u): {}
                },
                ("Earlobe", fx, rb, u): {
                    ("Earlobe - contra", fx, rb, u): {},
                    ("Earlobe - ipsi", fx, rb, u): {}
                }
            },
            ("Jaw", fx, rb, u): {
                ("Jaw - contra", fx, rb, u): {},
                ("Jaw - ipsi", fx, rb, u): {}
            },
            ("Chin", fx, rb, u): {},
            ("Under chin", fx, rb, u): {}
        },
    },
    ("Neck", fx, rb, u): {},
    ("Torso", fx, rb, u): {
        ("Shoulder", fx, rb, u): {
            ("Shoulder - contra", fx, rb, u): {},
            ("Shoulder - ipsi", fx, rb, u): {}
        },
        ("Armpit", fx, rb, u): {
            ("Armpit - contra", fx, rb, u): {},
            ("Armpit - ipsi", fx, rb, u): {}
        },
        ("Sternum/clavicle area", fx, rb, u): {},
        ("Chest/breast area", fx, rb, u): {},
        ("Abdominal/waist area", fx, rb, u): {},
        ("Pelvis area", fx, rb, u): {},
        ("Hip", fx, rb, u): {
            ("Hip - contra", fx, rb, u): {},
            ("Hip - ipsi", fx, rb, u): {}
        },
        ("Groin", fx, rb, u): {},
        ("Buttocks", fx, rb, u): {
            ("Buttocks - contra", fx, rb, u): {},
            ("Buttocks - ipsi", fx, rb, u): {}
        }
    },
    ("Arm (contralateral)", fx, rb, u): {
        ("Upper arm", fx, rb, u): {
            ("Upper arm above biceps", fx, rb, u): {},
            ("Biceps", fx, rb, u): {}
        },
        ("Elbow", fx, rb, u): {},
        ("Forearm", fx, rb, u): {},
        ("Wrist", fx, rb, u): {}
    },
    ("Legs and feet", fx, rb, u): {
        ("Upper leg", fx, rb, u): {
            ("Upper leg - contra", fx, rb, u): {},
            ("Upper leg - ipsi", fx, rb, u): {}
        },
        ("Knee", fx, rb, u): {
            ("Knee - contra", fx, rb, u): {},
            ("Knee - ipsi", fx, rb, u): {}
        },
        ("Lower leg", fx, rb, u): {
            ("Lower leg - contra", fx, rb, u): {},
            ("Lower leg - ipsi", fx, rb, u): {}
        },
        ("Ankle", fx, rb, u): {
            ("Ankle - contra", fx, rb, u): {},
            ("Ankle - ipsi", fx, rb, u): {}
        },
        ("Foot", fx, rb, u): {
            ("Foot - contra", fx, rb, u): {},
            ("Foot - ipsi", fx, rb, u): {}
        }
    },
    ("Other hand", fx, rb, u): {
        ("Whole hand", fx, rb, u): {},
        ("Hand minus fingers", fx, rb, u): {},
        ("Heel of hand", fx, rb, u): {},
        ("Thumb", fx, rb, u): {},
        ("Fingers", fx, rb, u): {},
        ("Selected fingers", fx, rb, u): {},
        ("Selected fingers and Thumb", fx, rb, u): {},
        ("Finger 1", fx, rb, u): {},
        ("Finger 2", fx, rb, u): {},
        ("Finger 3", fx, rb, u): {},
        ("Finger 4", fx, rb, u): {},
        ("Between Thumb and Finger 1", fx, rb, u): {},
        ("Between Fingers 1 and 2", fx, rb, u): {},
        ("Between Fingers 2 and 3", fx, rb, u): {},
        ("Between Fingers 3 and 4", fx, rb, u): {},
    }
}

# TODO KV: should be able to get rid of "fx" and "subgroup" (and maybe other?) options here...
# unless we're going to reference the same code (as for moevment) for building the tree & list models
locn_options_signingspace = {  # TODO KV edit!
    # ("No movement", fx, rb, u): {},
    ("Head", fx, rb, u): {
        ("Back of head", fx, rb, u): {},
        ("Top of head", fx, rb, u): {},
        ("Side of face", fx, rb, u): {
            ("Side of face - contra", fx, rb, u): {},
            ("Side of face - ipsi", fx, rb, u): {}
        },
        ("Face", fx, rb, u): {
            ("Temple", fx, rb, u): {
                ("Temple - contra", fx, rb, u): {},
                ("Temple - ipsi", fx, rb, u): {}
            },
            ("Above forehead (hairline)", fx, rb, u): {},
            ("Forehead", fx, rb, u): {},
            ("Eyebrow", fx, rb, u): {
                ("Eyebrow - contra", fx, rb, u): {},
                ("Eyebrow - ipsi", fx, rb, u): {},
                ("Between eyebrows", fx, rb, u): {}
            },
            ("Eye", fx, rb, u): {
                ("Eye - contra", fx, rb, u): {},
                ("Eye - ipsi", fx, rb, u): {},
                ("Outer corner of eye", fx, rb, u): {
                    ("Outer corner of eye - contra", fx, rb, u): {},
                    ("Outer corner of eye - ipsi", fx, rb, u): {}
                },
                ("Upper eyelid", fx, rb, u): {
                    ("Upper eyelid - contra", fx, rb, u): {},
                    ("Upper eyelid - ipsi", fx, rb, u): {}
                },
                ("Lower eyelid", fx, rb, u): {
                    ("Lower eyelid - contra", fx, rb, u): {},
                    ("Lower eyelid - ipsi", fx, rb, u): {}
                }
            },
            ("Cheek/nose", fx, rb, u): {
                ("Cheek", fx, rb, u): {
                    ("Cheek - contra", fx, rb, u): {},
                    ("Cheek - ipsi", fx, rb, u): {}
                },
                ("Maxillary process of zygomatic", fx, rb, u): {
                    ("Maxillary process of zygomatic - contra", fx, rb, u): {},
                    ("Maxillary process of zygomatic - ipsi", fx, rb, u): {}
                },
                ("Zygomatic process of temporal bone", fx, rb, u): {
                    ("Zygomatic process of temporal bone - contra", fx, rb, u): {},
                    ("Zygomatic process of temporal bone - ipsi", fx, rb, u): {}
                },
                ("Nose", fx, rb, u): {
                    ("Nose root", fx, rb, u): {},
                    ("Nose ridge", fx, rb, u): {},
                    ("Nose tip", fx, rb, u): {},
                    ("Septum", fx, rb, u): {}
                }
            },
            ("Below nose / philtrum", fx, rb, u): {},
            ("Mouth", fx, rb, u): {
                ("Lips", fx, rb, u): {
                    ("Upper lip", fx, rb, u): {},
                    ("Lower lip", fx, rb, u): {}
                },
                ("Corner of mouth - contra", fx, rb, u): {},
                ("Corner of mouth - ipsi", fx, rb, u): {},
                ("Teeth", fx, rb, u): {
                    ("Upper teeth", fx, rb, u): {},
                    ("Lower teeth", fx, rb, u): {}
                },
                ("Tongue", fx, rb, u): {},
            },
            ("Ear", fx, rb, u): {
                ("Ear - contra", fx, rb, u): {},
                ("Ear - ipsi", fx, rb, u): {},
                ("Mastoid process", fx, rb, u): {
                    ("Mastoid process - contra", fx, rb, u): {},
                    ("Mastoid process - ipsi", fx, rb, u): {}
                },
                ("Earlobe", fx, rb, u): {
                    ("Earlobe - contra", fx, rb, u): {},
                    ("Earlobe - ipsi", fx, rb, u): {}
                }
            },
            ("Jaw", fx, rb, u): {
                ("Jaw - contra", fx, rb, u): {},
                ("Jaw - ipsi", fx, rb, u): {}
            },
            ("Chin", fx, rb, u): {},
            ("Under chin", fx, rb, u): {}
        },
    },
    ("Neck", fx, rb, u): {},
    ("Torso", fx, rb, u): {
        ("Shoulder", fx, rb, u): {
            ("Shoulder - contra", fx, rb, u): {},
            ("Shoulder - ipsi", fx, rb, u): {}
        },
        ("Armpit", fx, rb, u): {
            ("Armpit - contra", fx, rb, u): {},
            ("Armpit - ipsi", fx, rb, u): {}
        },
        ("Sternum/clavicle area", fx, rb, u): {},
        ("Chest/breast area", fx, rb, u): {},
        ("Abdominal/waist area", fx, rb, u): {},
        ("Pelvis area", fx, rb, u): {},
        ("Hip", fx, rb, u): {
            ("Hip - contra", fx, rb, u): {},
            ("Hip - ipsi", fx, rb, u): {}
        },
        ("Groin", fx, rb, u): {},
        ("Buttocks", fx, rb, u): {
            ("Buttocks - contra", fx, rb, u): {},
            ("Buttocks - ipsi", fx, rb, u): {}
        }
    },
    ("Arm (contralateral)", fx, rb, u): {
        ("Upper arm", fx, rb, u): {
            ("Upper arm above biceps", fx, rb, u): {},
            ("Biceps", fx, rb, u): {}
        },
        ("Elbow", fx, rb, u): {},
        ("Forearm", fx, rb, u): {},
        ("Wrist", fx, rb, u): {}
    },
    ("Legs and feet", fx, rb, u): {
        ("Upper leg", fx, rb, u): {
            ("Upper leg - contra", fx, rb, u): {},
            ("Upper leg - ipsi", fx, rb, u): {}
        },
        ("Knee", fx, rb, u): {
            ("Knee - contra", fx, rb, u): {},
            ("Knee - ipsi", fx, rb, u): {}
        },
        ("Lower leg", fx, rb, u): {
            ("Lower leg - contra", fx, rb, u): {},
            ("Lower leg - ipsi", fx, rb, u): {}
        },
        ("Ankle", fx, rb, u): {
            ("Ankle - contra", fx, rb, u): {},
            ("Ankle - ipsi", fx, rb, u): {}
        },
        ("Foot", fx, rb, u): {
            ("Foot - contra", fx, rb, u): {},
            ("Foot - ipsi", fx, rb, u): {}
        }
    },
    ("Other hand", fx, rb, u): {
        ("Whole hand", fx, rb, u): {},
        ("Hand minus fingers", fx, rb, u): {},
        ("Heel of hand", fx, rb, u): {},
        ("Thumb", fx, rb, u): {},
        ("Fingers", fx, rb, u): {},
        ("Selected fingers", fx, rb, u): {},
        ("Selected fingers and Thumb", fx, rb, u): {},
        ("Finger 1", fx, rb, u): {},
        ("Finger 2", fx, rb, u): {},
        ("Finger 3", fx, rb, u): {},
        ("Finger 4", fx, rb, u): {},
        ("Between Thumb and Finger 1", fx, rb, u): {},
        ("Between Fingers 1 and 2", fx, rb, u): {},
        ("Between Fingers 2 and 3", fx, rb, u): {},
        ("Between Fingers 3 and 4", fx, rb, u): {},
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
                # self.parentlayout.treedisplay.collapseAll()
                itemstoselect = gettreeitemsinpath(self.parentlayout.treemodel, self.currentText(), delim=delimiter)
                for item in itemstoselect:
                    if item.checkState() == Qt.Unchecked:
                        item.setCheckState(Qt.PartiallyChecked)
                    # self.parentlayout.treedisplay.setExpanded(item.index(), True)
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


# This class is a serializable form of the class LocationTreeModel, which is itself not pickleable.
# Rather than being based on QStandardItemModel, this one uses dictionary structures to convert to
# and from saveable form.
class LocationTree:

    def __init__(self, locnmodule):

        treenode = locnmodule.locationtreemodel.invisibleRootItem()
        self.hands = locnmodule.hands
        self.timingintervals = locnmodule.timingintervals

        self.numvals = {}
        self.checkstates = {}

        self.collectdata(treenode)

    def collectdata(self, treenode):

        if treenode is not None:
            for r in range(treenode.rowCount()):
                treechild = treenode.child(r, 0)
                if treechild is not None:
                    pathtext = treechild.data(Qt.UserRole + pathdisplayrole)
                    checkstate = treechild.checkState()
                    editable = treechild.isEditable()
                    if editable:
                        pathsteps = pathtext.split(delimiter)
                        parentpathtext = delimiter.join(pathsteps[:-1])
                        numericstring = pathsteps[-1]  # pathtext[lastdelimindex + 1:]
                        self.numvals[parentpathtext] = numericstring

                    self.checkstates[pathtext] = checkstate
                self.collectdata(treechild)

    def getLocationTreeModel(self):
        locntreemodel = LocationTreeModel()
        rootnode = locntreemodel.invisibleRootItem()
        locntreemodel.populate(rootnode)
        makelistmodel = locntreemodel.listmodel
        self.setvalues(rootnode)
        return locntreemodel

    def setvalues(self, treenode):
        if treenode is not None:
            for r in range(treenode.rowCount()):
                treechild = treenode.child(r, 0)
                if treechild is not None:
                    pathtext = treechild.data(Qt.UserRole + pathdisplayrole)
                    parentpathtext = treenode.data(Qt.UserRole + pathdisplayrole)
                    if parentpathtext in self.numvals.keys():
                        treechild.setText(self.numvals[parentpathtext])
                        treechild.setEditable(True)
                        pathtext = parentpathtext + delimiter + self.numvals[parentpathtext]
                    treechild.setCheckState(self.checkstates[pathtext])
                    self.setvalues(treechild)


class LocationTreeModel(QStandardItemModel):

    def __init__(self, **kwargs):  #  movementparameters=None,
        super().__init__(**kwargs)
        self._listmodel = None  # MovementListModel(self)
        self.itemChanged.connect(self.updateCheckState)
        self.dataChanged.connect(self.updatelistdata)

    def updatelistdata(self, topLeft, bottomRight):
        startitem = self.itemFromIndex(topLeft)
        startitem.updatelistdata()

    def updateCheckState(self, item):
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
            self.populate(parentnode, structure=locn_options_bodyanchored, pathsofar="")
        elif structure != {}:
            # internal node with substructure
            numentriesatthislevel = len(structure.keys())
            for idx, labelclassifierchecked_4tuple in enumerate(structure.keys()):
                label = labelclassifierchecked_4tuple[0]
                editable = labelclassifierchecked_4tuple[1]
                classifier = labelclassifierchecked_4tuple[2]
                checked = labelclassifierchecked_4tuple[3]
                ismutuallyexclusive = classifier == rb
                iseditable = editable == ed
                if label == subgroup:

                    # make the tree items in the subgroup and whatever nested structure they have
                    isfinal = False
                    if idx + 1 >= numentriesatthislevel:
                        # if there are no more items at this level
                        isfinal = True
                    self.populate(parentnode, structure=structure[labelclassifierchecked_4tuple], pathsofar=pathsofar, issubgroup=True, isfinalsubgroup=isfinal, subgroupname=subgroup+"_"+pathsofar+"_"+(str(classifier)))

                else:
                    # parentnode.setColumnCount(1)
                    thistreenode = LocationTreeItem(label, mutuallyexclusive=ismutuallyexclusive)
                    # thistreenode.setData(False, Qt.UserRole+selectedrole)  #  moved to MovementTreeItem.__init__()
                    thistreenode.setData(pathsofar + label, role=Qt.UserRole + pathdisplayrole)
                    thistreenode.setEditable(iseditable)
                    thistreenode.setCheckState(Qt.Checked if checked else Qt.Unchecked)
                    if issubgroup:
                        thistreenode.setData(subgroupname, role=Qt.UserRole+subgroupnamerole)
                        if idx + 1 == numentriesatthislevel:
                            thistreenode.setData(True, role=Qt.UserRole + lastingrouprole)
                            thistreenode.setData(isfinalsubgroup, role=Qt.UserRole + finalsubgrouprole)
                    self.populate(thistreenode, structure=structure[labelclassifierchecked_4tuple], pathsofar=pathsofar+label+delimiter)
                    parentnode.appendRow([thistreenode])

    @property
    def listmodel(self):
        if self._listmodel is None:
            self._listmodel = LocationListModel(self)
        return self._listmodel

    @listmodel.setter
    def listmodel(self, listmod):
        self._listmodel = listmod


# TODO KV: need a graphics view instead
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


class LocationTreeItem(QStandardItem):

    def __init__(self, txt="", listit=None, mutuallyexclusive=False, serializedlocnitem=None):
        super().__init__()
        
        if serializedlocnitem:
            self.setEditable(serializedlocnitem['editable'])
            self.setText(serializedlocnitem['text'])
            self.setCheckable(serializedlocnitem['checkable'])
            self.setCheckState(serializedlocnitem['checkstate'])
            self.setUserTristate(serializedlocnitem['usertristate'])
            self.setData(serializedlocnitem['selectedrole'], Qt.UserRole+selectedrole)
            self.setData(serializedlocnitem['texteditrole'], Qt.UserRole+texteditrole)
            self.setData(serializedlocnitem['timestamprole'], Qt.UserRole+timestamprole)
            self.setData(serializedlocnitem['mutuallyexclusiverole'], Qt.UserRole+mutuallyexclusiverole)
            self.setData(serializedlocnitem['displayrole'], Qt.DisplayRole)
            self.listitem = LocationListItem(serializedlistitem=serializedlocnitem['listitem'])
            self.listitem.treeitem = self
        else:
            self.setEditable(False)
            self.setText(txt)
            self.setCheckable(True)
            self.setCheckState(Qt.Unchecked)
            self.setUserTristate(False)
            self.setData(False, Qt.UserRole + selectedrole)
            self.setData(False, Qt.UserRole + texteditrole)
            self.setData(QDateTime.currentDateTimeUtc(), Qt.UserRole+timestamprole)

            if mutuallyexclusive:
                self.setData(True, Qt.UserRole+mutuallyexclusiverole)
            else:
                self.setData(False, Qt.UserRole+mutuallyexclusiverole)
            # self.setData(mutuallyexclusive, Qt.UserRole+mutuallyexclusiverole)

            self.listitem = listit
            if listit is not None:
                self.listitem.treeitem = self

    def serialize(self):
        return {
            'editable': self.isEditable(),
            'text': self.text(),
            'checkable': self.isCheckable(),
            'checkstate': self.checkState(),
            'usertristate': self.isUserTristate(),
            'timestamprole': self.data(Qt.UserRole+timestamprole),
            'selectedrole': self.data(Qt.UserRole + selectedrole),
            'texteditrole': self.data(Qt.UserRole + texteditrole),
            'mutuallyexclusiverole': self.data(Qt.UserRole+mutuallyexclusiverole),
            'displayrole': self.data(Qt.DisplayRole),
            # 'listitem': self.listitem.serialize()
        }

    def updatelistdata(self):
        if self.parent() and "Number of repetitions" in self.parent().data():
            previouslistitemtext = self.listitem.text()
            parentname = self.parent().text()
            updatetextstartindex = previouslistitemtext.index(parentname) + len(parentname + delimiter)
            if delimiter in previouslistitemtext[updatetextstartindex:]:
                updatetextstopindex = previouslistitemtext.index(delimiter, updatetextstartindex)
            else:
                updatetextstopindex = len(previouslistitemtext)+1
            selftext = self.text()
            self.listitem.updatetext(previouslistitemtext[:updatetextstartindex] + selftext + previouslistitemtext[updatetextstopindex:])

    def check(self, fully=True):
        self.setCheckState(Qt.Checked if fully else Qt.PartiallyChecked)
        self.listitem.setData(fully, Qt.UserRole+selectedrole)
        if fully:
            self.setData(QDateTime.currentDateTimeUtc(), Qt.UserRole+timestamprole)
            self.listitem.setData(QDateTime.currentDateTimeUtc(), Qt.UserRole+timestamprole)
        self.checkancestors()

        # gather siblings in order to deal with mutual exclusivity (radio buttons)
        siblings = self.collectsiblings()

        # if this is a radio button item, make sure none of its siblings are checked
        if self.data(Qt.UserRole+mutuallyexclusiverole):
            for sib in siblings:
                sib.uncheck(force=True)
        else:  # or if it has radio button siblings, make sure they are unchecked
            for me_sibling in [s for s in siblings if s.data(Qt.UserRole+mutuallyexclusiverole)]:
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

        mysubgroup = self.data(Qt.UserRole+subgroupnamerole)
        subgrouporgeneralsiblings = [sib for sib in siblings if sib.data(Qt.UserRole+subgroupnamerole) == mysubgroup or not sib.data(Qt.UserRole+subgroupnamerole)]

        # if I'm ME and in a subgroup, collect siblings from my subgroup and also those at my level but not in any subgroup
        if self.data(Qt.UserRole+mutuallyexclusiverole) and mysubgroup:
            return subgrouporgeneralsiblings
        # if I'm ME and not in a subgroup, collect all siblings from my level (in subgroups or no)
        elif self.data(Qt.UserRole+mutuallyexclusiverole):
            return siblings
        # if I'm *not* ME, collect all siblings from my level (in subgroups or no)
        # I'm not ME but my siblings might be
        else:
            return siblings

    def checkancestors(self):
        if self.checkState() == Qt.Unchecked:
            self.setCheckState(Qt.PartiallyChecked)
        if self.parent() is not None:
            self.parent().checkancestors()

    def uncheck(self, force=False):
        name = self.data()

        self.listitem.setData(False, Qt.UserRole+selectedrole)
        self.setData(False, Qt.UserRole+selectedrole)

        # TODO KV - can't just uncheck a radio button... or can we?

        if force:  # force-clear this item and all its descendants - have to start at the bottom?
            # self.forceuncheck()
            # force-uncheck all descendants
            if self.hascheckedchild():
                for r in range(self.rowCount()):
                    for c in range(self.columnCount()):
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

        if self.data(Qt.UserRole+mutuallyexclusiverole):
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


class LocationListItem(QStandardItem):

    def __init__(self, pathtxt="", nodetxt="", treeit=None, serializedlistitem=None):
        super().__init__()

        if serializedlistitem:
            self.setEditable(serializedlistitem['editable'])
            self.setText(serializedlistitem['text'])
            self.setData(serializedlistitem['nodedisplayrole'], Qt.UserRole+nodedisplayrole)
            self.setData(serializedlistitem['timestamprole'], Qt.UserRole+timestamprole)
            self.setCheckable(serializedlistitem['checkable'])
            self.setData(serializedlistitem['selectedrole'], Qt.UserRole+selectedrole)
        else:
            self.setEditable(False)
            self.setText(pathtxt)
            self.setData(nodetxt, Qt.UserRole+nodedisplayrole)
            self.setData(QDateTime.currentDateTimeUtc(), Qt.UserRole+timestamprole)
            self.setCheckable(False)
            self.treeitem = treeit
            if treeit is not None:
                self.treeitem.listitem = self
            self.setData(False, Qt.UserRole+selectedrole)

    # def serialize(self):
    #     serialized = {
    #         'editable': self.isEditable(),
    #         'text': self.text(),
    #         'nodedisplayrole': self.data(Qt.UserRole+nodedisplayrole),
    #         'timestamprole': self.data(Qt.UserRole+timestamprole),
    #         'checkable': self.isCheckable(),
    #         'selectedrole': self.data(Qt.UserRole+selectedrole)
    #     }
    #     return serialized

    def updatetext(self, txt=""):
        self.setText(txt)

    def unselectpath(self):
        self.treeitem.uncheck()

    def selectpath(self):
        self.treeitem.check(fully=True)


class LocationPathsProxyModel(QSortFilterProxyModel):

    def __init__(self, parent=None, wantselected=None):
        super(LocationPathsProxyModel, self).__init__(parent)
        self.wantselected = wantselected
        self.setSortCaseSensitivity(Qt.CaseInsensitive)

    def filterAcceptsRow(self, source_row, source_parent):
        if self.wantselected is None:
            source_index = self.sourceModel().index(source_row, 0, source_parent)
            text = self.sourceModel().index(source_row, 0, source_parent).data()
            return True
        else:
            source_index = self.sourceModel().index(source_row, 0, source_parent)
            isselected = source_index.data(role=Qt.UserRole+selectedrole)
            path = source_index.data(role=Qt.UserRole+pathdisplayrole)
            text = self.sourceModel().index(source_row, 0, source_parent).data()
            return self.wantselected == isselected

    def updatesorttype(self, sortbytext=""):
        if "alpha" in sortbytext and "path" in sortbytext:
            self.setSortRole(Qt.DisplayRole)
            self.sort(0)
        elif "alpha" in sortbytext and "node" in sortbytext:
            self.setSortRole(Qt.UserRole+nodedisplayrole)
            self.sort(0)
        elif "tree" in sortbytext:
            self.sort(-1)  # returns to sort order of underlying model
        elif "select" in sortbytext:
            self.setSortRole(Qt.UserRole+timestamprole)
            self.sort(0)


class LocationGraphicsView(QGraphicsView):

    def __init__(self, frontorback='front', parent=None, viewer_size=400):
        super().__init__(parent=parent)

        self.viewer_size = viewer_size

        self._scene = QGraphicsScene(parent=self)
        # TODO KV - this needs to be a resource path, not local
        imagepath = "./body_hands_" + frontorback + ".png"
        self._pixmap = QPixmap(imagepath)
        self._photo = QGraphicsPixmapItem(self._pixmap)
        # self._photo.setPixmap(QPixmap("../../resources/base/default_location_images/upper_body.jpg"))
        self._scene.addItem(self._photo)
        # self._scene.addPixmap(QPixmap("./body_hands_front.png"))
        self.setScene(self._scene)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.fitInView()

    def fitInView(self, scale=True):
        rect = QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
            self.scale(1 / unity.width(), 1 / unity.height())
            scenerect = self.transform().mapRect(rect)
            factor = min(self.viewer_size / scenerect.width(), self.viewer_size / scenerect.height())
            self.factor = factor
            # viewrect = self.viewport().rect()
            # factor = min(viewrect.width() / scenerect.width(), viewrect.height() / scenerect.height())
            self.scale(factor, factor)


class LocationListModel(QStandardItemModel):

    def __init__(self, treemodel=None):
        super().__init__()
        self.treemodel = treemodel
        if self.treemodel is not None:
            # build this listmodel from the treemodel
            treeparentnode = self.treemodel.invisibleRootItem()
            self.populate(treeparentnode)
            self.treemodel.listmodel = self

    # def serialize(self):
    #     serialized = []
    #     for rownum in range(self.rowCount()):
    #         serialized.append(self.item(rownum, 0).serialize())
    #     return serialized

    def populate(self, treenode):
        # colcount = 1  # TODO KV treenode.columnCount()
        for r in range(treenode.rowCount()):
            # for colnum in range(colcount):
            treechild = treenode.child(r, 0)
            if treechild is not None:
                pathtext = treechild.data(role=Qt.UserRole+pathdisplayrole)
                nodetext = treechild.data(Qt.DisplayRole)
                listitem = LocationListItem(pathtxt=pathtext, nodetxt=nodetext, treeit=treechild)  # also sets treeitem's listitem
                self.appendRow(listitem)
                self.populate(treechild)

    def setTreemodel(self, treemod):
        self.treemodel = treemod


class TreeListView(QListView):

    def __init__(self):
        super().__init__()

    # def selectionChanged(self, selected, deselected):
    #     allselectedindexes = self.selectionModel().selectedIndexes()
    #     # print("all selected", [i.data() for i in allselectedindexes])

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
