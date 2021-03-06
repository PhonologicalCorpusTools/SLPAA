from PyQt5.QtCore import (
    Qt,
    QAbstractListModel,
    pyqtSignal,
    QModelIndex,
    QItemSelectionModel,
    QSortFilterProxyModel,
    QDateTime
)

from PyQt5.Qt import (
    QStandardItem,
    QStandardItemModel
)

from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QListView,
    QVBoxLayout,
    QComboBox,
    QTreeView,
    QStyle
)


#from PyQt5.QtGui import ()


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

rb = "radio button"  # ie mutually exclusive in group / at this level
cb = "checkbox"  # ie not mutually exlusive
ed = "editable" 
fx = "fixed"  # ie not editable
subgroup = "subgroup"

c = True  # checked
u = False  # unchecked

mvmtOptionsDict = {
    ("No movement", fx, rb, u): {},
    ("Movement type", fx, cb, u): {
        ("Perceptual shape", fx, rb, u): {
            ("Shape", fx, cb, u): {  # all mutually exclusive (straight vs arc vs ...)
                (subgroup, None, 0, None): {
                    ("Straight", fx, rb, u): {
                        ("Interacts with subsequent straight movement", fx, rb, u): {
                            ("Movement contours cross (e.g. X)", fx, rb, u): {},
                            ("Subsequent movement starts at end of first (e.g. ↘↗)", fx, rb, u): {},
                            ("Subsequent movement starts in same location as start of first (e.g. ↖↗)", fx, rb, u): {},
                            ("Subsequent movement ends in same location as end of first (e.g. ↘↙)", fx, rb, u): {}
                        },
                        ("Doesn't interact with subsequent straight movement", fx, rb, u): {}
                    },
                    ("Arc", fx, rb, u): {},
                    ("Circle", fx, rb, u): {},
                    ("Zigzag", fx, rb, u): {},
                    ("Loop (travelling circles)", fx, rb, u): {},
                    ("None of these", fx, rb, u): {}
                }
            },
            ("Axis direction", fx, cb, u): {  # Choose up to one from each axis to get the complete direction
                (subgroup, None, 0, None): {
                    ("Up", fx, rb, u): {},
                    ("Down", fx, rb, u): {}
                },
                (subgroup, None, 1, None): {
                    ("Distal", fx, rb, u): {},
                    ("Proximal", fx, rb, u): {}
                },
                (subgroup, None, 2, None): {
                    ("Right", fx, rb, u): {},
                    ("Left", fx, rb, u): {}
                },
                ("Not relevant", fx, rb, u): {}
            },
            ("Plane", fx, cb, u): {  # choose as many as needed, but only one direction per plane
                ("Mid-sagittal", fx, cb, u): {
                    (subgroup, None, 0, None): {
                        ("Clockwise", fx, rb, u): {},
                        ("Counterclockwise", fx, rb, u): {}
                    },
                },
                ("Horizontal", fx, cb, u): {
                    (subgroup, None, 0, None): {
                        ("Clockwise", fx, rb, u): {},
                        ("Counterclockwise", fx, rb, u): {}
                    },
                },
                ("Vertical", fx, cb, u): {
                    (subgroup, None, 0, None): {
                        ("Clockwise", fx, rb, u): {},
                        ("Counterclockwise", fx, rb, u): {}
                    },
                },
                ("Not relevant", fx, rb, u): {}  # TODO KV Auto-select this if movement is straight or the axis is not relevant
            },
        },
        # mutually exclusive @ level of pivoting, twisting, etc. and also within (nodding vs unnodding)
        ("Joint-specific movements", fx, rb, u): {
            ("Nodding/un-nodding", fx, rb, u): {
                (subgroup, None, 0, None): {
                    ("Nodding", fx, rb, u): {},  # TODO KV autofills to flexion of wrist (but *ask* before auto-unfilling if nodding is unchecked)
                    ("Un-nodding", fx, rb, u): {}  # TODO KV autofills to extension of wrist
                }
            },
            ("Pivoting", fx, rb, u): {
                (subgroup, None, 0, None): {
                    ("Radial", fx, rb, u): {},  # TODO KV autofills to wrist radial deviation
                    ("Ulnar", fx, rb, u): {}  # TODO KV autofills to wrist ulnar deviation
                }
            },
            ("Twisting", fx, rb, u): {
                (subgroup, None, 0, None): {
                    ("Pronation", fx, rb, u): {},  # TODO KV autofills to Proximal radioulnar pronation
                    ("Supination", fx, rb, u): {}  # TODO KV autofills to Proximal radioulnar supination
                }
            },
            ("Closing/Opening", fx, rb, u): {
                (subgroup, None, 0, None): {
                    ("Closing", fx, rb, u): {},  # TODO KV autofills to flexion of [selected finger, all joints]
                    ("Opening", fx, rb, u): {}  # TODO KV autofills to extension of [selected finger, all joints]
                }
            },
            ("Pinching/unpinching", fx, rb, u): {
                (subgroup, None, 0, None): {
                    ("Pinching (Morgan 2017)", fx, rb, u): {},  # TODO KV autofills to adduction of thumb base joint
                    ("Unpinching", fx, rb, u): {}  # TODO KV autofills to (abduction of thumb base joint? - not specific in google doc)
                }
            },
            ("Flattening/Straightening", fx, rb, u): {
                (subgroup, None, 0, None): {
                    ("Flattening/hinging", fx, rb, u): {},  # TODO KV autofills to flexion of [selected finger base joints]
                    ("Straightening", fx, rb, u): {}  # TODO KV autofills to extension of [selected finger base joints]
                }
            },
            ("Hooking/Unhooking", fx, rb, u): {
                (subgroup, None, 0, None): {
                    ("Hooking/clawing", fx, rb, u): {},  # TODO KV autofills to flexion of [selected finger non-base joints]
                    ("Unhooking", fx, rb, u): {}  # TODO KV autofills to extension of [selected finger non-base joints]
                }
            },
            ("Spreading/Unspreading", fx, rb, u): {
                (subgroup, None, 0, None): {
                    ("Spreading", fx, rb, u): {},  # TODO KV autofills to abduction of [selected finger base joints]
                    ("Unspreading", fx, rb, u): {}  # TODO KV autofills to adduction of [selected finger base joints]
                }
            },
            ("Rubbing", fx, rb, u): {
                (subgroup, None, 0, None): {
                    ("Thumb crossing over palm", fx, rb, u): {},  # TODO KV autofills to TBD
                    ("Thumb moving away from palm", fx, rb, u): {}  # TODO KV autofills to TBD
                }
            },
            ("Wiggling/Fluttering", fx, rb, u): {},  # TODO KV autofills to both flexion and extension of selected finger base joints
            ("None of these", fx, rb, u): {}
        }
    },
    ("Joint activity", fx, cb, u): {
        ("Complex / multi-joint", fx, cb, u): {},  # from Yurika: if this is selected, the expectation is that nothing else below would be selected, though I guess people could...
        ("Shoulder", fx, cb, u): {
            (subgroup, None, 0, None): {
                ("Flexion", fx, rb, u): {},
                ("Extension", fx, rb, u): {},
            },
            (subgroup, None, 1, None): {
                ("Abduction", fx, rb, u): {},
                ("Adduction", fx, rb, u): {},
            },
            (subgroup, None, 2, None): {
                ("Posterior rotation", fx, rb, u): {},
                ("Anterior rotation", fx, rb, u): {},
            },
            (subgroup, None, 3, None): {
                ("Protraction", fx, rb, u): {},
                ("Retraction", fx, rb, u): {},
            },
            (subgroup, None, 4, None): {
                ("Depression", fx, rb, u): {},
                ("Elevation", fx, rb, u): {},
            },
            (subgroup, None, 5, None): {
                ("Circumduction", fx, cb, u): {}
            },
        },
        ("Elbow", fx, cb, u): {
            (subgroup, None, 0, None): {
                ("Flexion", fx, rb, u): {},
                ("Extension", fx, rb, u): {},
            },
            (subgroup, None, 1, None): {
                ("Circumduction", fx, cb, u): {}
            },
        },
        ("Radio-ulnar", fx, cb, u): {
            (subgroup, None, 0, None): {
                ("Pronation", fx, rb, u): {},
                ("Supination", fx, rb, u): {},
            }
        },
        ("Wrist", fx, cb, u): {
            (subgroup, None, 0, None): {
                ("Flexion", fx, rb, u): {},
                ("Extension", fx, rb, u): {},
            },
            (subgroup, None, 1, None): {
                ("Radial deviation", fx, rb, u): {},
                ("Ulnar deviation", fx, rb, u): {},
            },
            (subgroup, None, 2, None): {
                ("Circumduction", fx, cb, u): {}
            },
        },
        ("Thumb base / metacarpophalangeal", fx, cb, u): {
            (subgroup, None, 0, None): {
                ("Flexion", fx, rb, u): {},
                ("Extension", fx, rb, u): {},
            },
            (subgroup, None, 1, None): {
                ("Abduction", fx, rb, u): {},
                ("Adduction", fx, rb, u): {},
            },
            (subgroup, None, 2, None): {
                ("Circumduction", fx, cb, u): {},
                ("Opposition", fx, cb, u): {}
            }
        },
        ("Thumb non-base / interphalangeal", fx, cb, u): {
            (subgroup, None, 0, None): {
                ("Flexion", fx, rb, u): {},
                ("Extension", fx, rb, u): {},
            }
        },
        ("Finger base / metacarpophalangeal", fx, cb, u): {
            (subgroup, None, 0, None): {
                ("Flexion", fx, rb, u): {},
                ("Extension", fx, rb, u): {},
            },
            (subgroup, None, 1, None): {
                ("Abduction", fx, rb, u): {},
                ("Adduction", fx, rb, u): {},
            },
            (subgroup, None, 2, None): {
                ("Circumduction", fx, cb, u): {}
            },
        },
        ("Finger non-base / interphalangeal", fx, cb, u): {
            (subgroup, None, 0, None): {
                ("Flexion", fx, rb, u): {},
                ("Extension", fx, rb, u): {},
            }
        }
    },
    ("Movement characteristics", fx, cb, u): {
        ("Repetition", fx, cb, u): {
            ("Single", fx, rb, u): {},
            ("Repeated", fx, rb, u): {
                ("Number of repetitions", fx, cb, u): {
                    ("#", ed, cb, u): {}
                },  # TODO KV
                ("Location of repetition", fx, cb, u): {
                    ("Same location", fx, rb, u): {},
                    ("Different location", fx, rb, u): {  # Choose up to one from each column as needed
                        (subgroup, None, 0, None): {
                            ("Up", fx, rb, u): {},
                            ("Down", fx, rb, u): {}
                        },
                        (subgroup, None, 1, None): {
                            ("Distal", fx, rb, u): {},
                            ("Proximal", fx, rb, u): {}
                        },
                        (subgroup, None, 2, None): {
                            ("Right", fx, rb, u): {},
                            ("Left", fx, rb, u): {}
                        }
                    }
                }
            }
        },
        ("Trill", fx, cb, u): {
            (subgroup, None, 0, None): {
                ("Not trilled", fx, rb, u): {},
                ("Trilled", fx, rb, u): {}
            }
        },
        ("Directionality", fx, cb, u): {
            (subgroup, None, 0, None): {
                ("Unidirectional", fx, rb, u): {},
                ("Bidirectional", fx, rb, u): {}
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


# This class is a serializable form of the class TODO MovementTreeModel, which is itself not pickleable.
# Rather than being based on QStandardItemModel, this one uses dictionary structures to convert to
# and from saveable form.
class MovementTree:

    def __init__(self, mvmtmodule):

        treenode = mvmtmodule.movementtreemodel.invisibleRootItem()
        self.hands = mvmtmodule.hands
        self.timingintervals = mvmtmodule.timingintervals

        self.numvals = {}
        self.checkstates = {}

        # self.mvmtlist = MovementList(mvmtmodule.listmodel)

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

    def getMovementTreeModel(self):
        mvmttreemodel = MovementTreeModel()
        rootnode = mvmttreemodel.invisibleRootItem()
        mvmttreemodel.populate(rootnode)
        makelistmodel = mvmttreemodel.listmodel
        self.setvalues(rootnode)
        return mvmttreemodel

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


class MovementTreeModel(QStandardItemModel):

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
            self.populate(parentnode, structure=mvmtOptionsDict, pathsofar="")
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
                    thistreenode = MovementTreeItem(label, mutuallyexclusive=ismutuallyexclusive)
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
            self._listmodel = MovementListModel(self)
        return self._listmodel

    @listmodel.setter
    def listmodel(self, listmod):
        self._listmodel = listmod


################# TODO KV below is copied from CorpusModel
    #
    # def data(self, index, role):
    #     if role == Qt.DisplayRole:
    #         return self.glosses[index.row()]
    #
    # def rowCount(self, index):
    #     return len(self.glosses)


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

    def __init__(self, txt="", listit=None, mutuallyexclusive=False, serializedmvmtitem=None):
        super().__init__()
        
        if serializedmvmtitem:
            self.setEditable(serializedmvmtitem['editable'])
            self.setText(serializedmvmtitem['text'])
            self.setCheckable(serializedmvmtitem['checkable'])
            self.setCheckState(serializedmvmtitem['checkstate'])
            self.setUserTristate(serializedmvmtitem['usertristate'])
            self.setData(serializedmvmtitem['selectedrole'], Qt.UserRole+selectedrole)
            self.setData(serializedmvmtitem['texteditrole'], Qt.UserRole+texteditrole)
            self.setData(serializedmvmtitem['timestamprole'], Qt.UserRole+timestamprole)
            self.setData(serializedmvmtitem['mutuallyexclusiverole'], Qt.UserRole+mutuallyexclusiverole)
            self.setData(serializedmvmtitem['displayrole'], Qt.DisplayRole)
            self.listitem = MovementListItem(serializedlistitem=serializedmvmtitem['listitem'])
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


class MovementListItem(QStandardItem):

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


class MovementListModel(QStandardItemModel):

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
                listitem = MovementListItem(pathtxt=pathtext, nodetxt=nodetext, treeit=treechild)  # also sets treeitem's listitem
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
