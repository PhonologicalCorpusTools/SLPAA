from PyQt5.QtCore import (
    Qt,
    QAbstractListModel,
    pyqtSignal,
    QModelIndex,
    QItemSelectionModel,
    QSortFilterProxyModel
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
    QComboBox
)

#from PyQt5.QtGui import ()


# TODO KV - is this where I actually want to define these?
delimiter = ">"  # TODO KV - should this be use-defined in global settings? or maybe even in the mvmt window?
selectedrole = 0
pathdisplayrole = 1
mutuallyexclusiverole = 2
texteditrole = 3

# strDict = {
#     "Animal": {
#         "mammal": {
#             "anteater": {},
#             "whale": {},
#             "wolf": {}
#         },
#         "insect": {
#             "ant": {},
#             "wasp": {},
#         },
#     },
#     "Plant": {
#         "tree": {
#             "Oak": {},
#             "Western Red Cedar": {},
#             "Alder": {}
#         },
#         "flower": {
#             "margeurite": {},
#             "foxglove": {},
#             "hydrangea": {},
#         },
#         "algae": {},
#     },
#     "Fungus": {
#         "mushroom": {
#             "oyster": {},
#             "morel": {},
#             "portobello": {}
#         },
#         "yeast": {},
#     },
#     "Awesome": {
#         "rainbow": {},
#         "aurora": {},
#         "meteor": {},
#         "wolf": {},
#     },
# }

mvmtOptionsDict = {
    "No movement": {},
    "Perceptual shape": {
        "Straight": {
            "Interacts with subsequent straight movement": {
                "Movement contours cross (e.g. X)": {},
                "Subsequent movement starts at end of first movement (e.g. ↘↗)": {},
                "Subsequent movement starts in same location as start of first movement (e.g. ↖↗)": {},
                "Subsequent movement ends in same location as end of first movement (e.g. ↘↙)": {}
            },
            "Doesn't interact with subsequent straight movement": {}
        },
        "Arc": {},
        "Circle": {},
        "Zigzag": {},
        "Loop (travelling circles)": {},
        "None of these": {}
    },
    "Joint-specific movements": {
        "Nodding/un-nodding": {
            "Nodding": {},  # TODO KV autofills to flexion of wrist
            "Un-nodding": {}  # TODO KV autofills to extension of wrist
        },
        "Pivoting": {
            "Radial": {},  # TODO KV autofills to wrist radial deviation
            "Ulnar": {}  # TODO KV autofills to wrist ulnar deviation
        },
        "Twisting": {
            "Pronation": {},  # TODO KV autofills to Proximal radioulnar pronation
            "Supination": {}  # TODO KV autofills to Proximal radioulnar supination
        },
        "Closing/Opening": {
            "Closing": {},  # TODO KV autofills to flexion of [selected finger, all joints]
            "Opening": {}  # TODO KV autofills to extension of [selected finger, all joints]
        },
        "Pinching/unpinching": {
            "Pinching (Morgan 2017)": {},  # TODO KV autofills to adduction of thumb base joint
            "Unpinching": {}  # TODO KV autofills to (abduction of thumb base joint? - not specific in google doc)
        },
        "Flattening/Straightening": {
            "Flattening/hinging": {},  # TODO KV autofills to flexion of [selected finger base joints]
            "Straightening": {}  # TODO KV autofills to extension of [selected finger base joints]
        },
        "Hooking/Unhooking": {
            "Hooking/clawing": {},  # TODO KV autofills to flexion of [selected finger non-base joints]
            "Unhooking": {}  # TODO KV autofills to extension of [selected finger non-base joints]
        },
        "Spreading/Unspreading": {
            "Spreading": {},  # TODO KV autofills to abduction of [selected finger base joints]
            "Unspreading": {}  # TODO KV autofills to adduction of [selected finger base joints]
        },
        "Rubbing": {
            "Thumb crossing over palm": {},  # TODO KV autofills to TBD
            "Thumb moving away from palm": {}  # TODO KV autofills to TBD
        },
        "Wiggling/Fluttering": {},  # TODO KV autofills to both flexion and extension of selected finger base joints
        "None of these": {}
    },
    "Joint movements": {
        "Complex / multi-joint": {},  # from Yurika: if this is selected, the expectation is that nothing else below would be selected, though I guess people could...
        "Shoulder": {
            "Flexion": {},
            "Extension": {},
            "Abduction": {},
            "Adduction": {},
            "Posterior rotation": {},
            "Anterior rotation": {},
            "Protraction": {},  # (like when we do ‘shoulder’ push ups with straight arms)
            "Retraction": {},  # (like when we do ‘shoulder’ push ups with straight arms)
            "Depression": {},
            "Elevation": {},
            "Circumduction": {}
        },
        "Elbow": {
            "Flexion": {},
            "Extension": {},
            "Circumduction": {}
        },
        "Radio-ulnar": {
            "Pronation": {},
            "Supination": {}
        },
        "Wrist": {
            "Flexion": {},
            "Extension": {},
            "Radial deviation": {},
            "Ulnar deviation": {},
            "Circumduction": {}
        },
        "Thumb base / metacarpophalangeal": {
            "Flexion": {},
            "Extension": {},
            "Abduction": {},
            "Adduction": {},
            "Circumduction": {},
            "Opposition": {}
        },
        "Thumb non-base / interphalangeal": {
            "Flexion": {},
            "Extension": {}
        },
        "Finger base / metacarpophalangeal": {
            "Flexion": {},
            "Extension": {},
            "Abduction": {},
            "Adduction": {},
            "Circumduction": {}
        },
        "Finger non-base / interphalangeal": {
            "Flexion": {},
            "Extension": {}
        }
    },
    "Axis, direction, and plane": {  # TODO KV only coded if 1. Perceptual shape is coded. If not, auto-fill everything as ‘not relevant’
        # "Axis direction": {  # Choose up to one from each column to get the complete direction
        #     # TODO KV three columns x 2 rows
        #     "Up": {},
        #     "Down": {},
        #     "Distal": {},
        #     "Proximal": {},
        #     "Right": {},
        #     "Left": {},
        #     "Not relevant": {}
        # },
        "Axis direction": {
            "subgroups1": [
                {
                    "Up": {},
                    "Down": {}
                },
                {
                    "Distal": {},
                    "Proximal": {}
                },
                {
                    "Right": {},
                    "Left": {}
                }
            ],
            "Not relevant": {}
        },
        "Plane": {  # TODO KV choose as many as needed, but only one direction per plane
            "Mid-sagittal": {
                "Clockwise": {},
                "Counterclockwise": {}
            },
            "Horizontal": {
                "Clockwise": {},
                "Counterclockwise": {}
            },
            "Vertical": {
                "Clockwise": {},
                "Counterclockwise": {}
            },
            "Not relevant": {}  # TODO KV Auto-select this if movement is straight or the axis is not relevant
        },
        # "Plane direction": {  # TODO KV choose only one (radio button)
        #     "Clockwise": {},
        #     "Counterclockwise": {},
        #     "Not relevant": {}  # TODO KV Auto-select this if ‘not relevant’ is selected for plane
        # }
    },
    "Movement characteristics": {
        "Repetition": {
            "Single": {},
            "Repeated": {
                "How many": {},  # TODO KV
                "Location of repetition": {
                    "Same location": {},
                    "Different location": {  # Choose up to one from each column as needed
                        # TODO KV three columns x 2 rows
                        "Up": {},
                        "Down": {},
                        "Distal": {},
                        "Proximal": {},
                        "Right": {},
                        "Left": {}
                    },
                }
            }
        },
        "Trill": {
            "Not trilled": {},
            "Trilled": {}
        },
        "Directionality": {
            "Unidirectional": {},
            "Bidirectional": {}
        }
    }
}


class TreeSearchComboBox(QComboBox):

    def __init__(self, parentlayout=None):
        super().__init__() #  todo kv parent)
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


class MovementTreeModel(QStandardItemModel):

    def __init__(self, movementparameters=None, **kwargs):
        super().__init__(**kwargs)
        self.movementparameters = movementparameters  # TODO KV   or [] (or {} or...)
        self.listmodel = None
        self.itemChanged.connect(self.updateCheckState)

    def setListmodel(self, listmod):
        self.listmodel = listmod

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

    def populate(self, parentnode, structure={}, pathsofar=""):
        if structure == {} and pathsofar != "":
            # base case (leaf node); don't build any more nodes
            pass
        elif structure == {} and pathsofar == "":
            # no parameters; build a tree from the default structure
            self.setColumnCount(countColumns(mvmtOptionsDict))
            self.populate(parentnode, structure=mvmtOptionsDict, pathsofar="")  # TODO KV define a default structure somewhere (see constant.py)
        elif structure != {}:
            # internal node with substructure
            for label in structure.keys():
                if label.startswith("subgroups"):
                    # should be followed by a list of dictionaries, each of which will get their own column
                    colnum = 0
                    for subgroup in structure[label]:
                        # make a column for this list of entries
                        # assume no further structure to populate within each node
                        thecolumn = []
                        for sublabel in subgroup.keys():
                            thistreenode = MovementTreeItem(sublabel, mutuallyexclusive=True)
                            thistreenode.setData(pathsofar + sublabel, role=Qt.UserRole+pathdisplayrole)
                            thecolumn.append(thistreenode)
                        parentnode.appendColumn(thecolumn)
                        colnum += 1
                else:
                    # parentnode.setColumnCount(1)
                    thistreenode = MovementTreeItem(label)
                    # thistreenode.setData(False, Qt.UserRole+selectedrole) moved to MovementTreeItem.__init__()
                    thistreenode.setData(pathsofar + label, role=Qt.UserRole + pathdisplayrole)
                    self.populate(thistreenode, structure=structure[label], pathsofar=pathsofar+label+delimiter)
                    parentnode.appendRow([thistreenode])

    def listmodel(self):
        if self.listmodel is None:
            self.listmodel = MovementListModel(self)
        return self.listmodel

################# TODO KV below is copied from CorpusModel
    #
    # def data(self, index, role):
    #     if role == Qt.DisplayRole:
    #         return self.glosses[index.row()]
    #
    # def rowCount(self, index):
    #     return len(self.glosses)


class MovementTreeItem(QStandardItem):

    def __init__(self, txt="", listit=None, mutuallyexclusive=False):
        super().__init__()

        self.setEditable(False)
        self.setText(txt)
        self.setCheckable(True)
        self.setCheckState(Qt.Unchecked)
        self.setUserTristate(False)
        self.setData(False, Qt.UserRole + selectedrole)
        self.setData(False, Qt.UserRole + texteditrole)

        # TODO KV do this somewhere/somehow better
        if mutuallyexclusive or txt in ["No movement", "Trilled", "Not trilled", "Unidirectional", "Bidirectional", "Clockwise", "Counterclockwise"]:
            self.setData(True, Qt.UserRole+mutuallyexclusiverole)
        elif txt == "How many":
            self.setEditable(True)
        else:
            self.setData(False, Qt.UserRole+mutuallyexclusiverole)
        # self.setData(mutuallyexclusive, Qt.UserRole+mutuallyexclusiverole)

        self.listitem = listit
        if listit is not None:
            self.listitem.treeitem = self

    def check(self, fully=True):
        tempitemname = self.text()
        self.setCheckState(Qt.Checked if fully else Qt.PartiallyChecked)
        self.listitem.setData(fully, Qt.UserRole+selectedrole)
        # self.setData(fully, Qt.UserRole+selectedrole)  # TODO KV causes infinite recursion
        self.checkancestors()

        # gather siblings in order to deal with mutual exclusivity (radio buttons)

        # siblings = []
        # siblingnames = []
        siblings = self.collectsiblings()
        siblingnames = [sib.text() for sib in siblings]

        # if this is a radio button item, make sure none of its siblings are checked
        if self.data(Qt.UserRole+mutuallyexclusiverole):
            for sib in siblings:
                sib.uncheck(force=True)
            # TODO KV
            # numsiblingsincludingself = self.parent().rowCount()
            # for snum in range(numsiblingsincludingself):
            #     sibling = self.parent().child(snum, 0)
            #     if sibling.index() != self.index():  # ie, it's actually a sibling
            #         sibling.uncheck()
        else:  # or if it has radio button siblings, make sure they are unchecked
            for me_sibling in [s for s in siblings if s.data(Qt.UserRole+mutuallyexclusiverole)]:
                me_sibling.uncheck(force=True)

    def collectsiblings(self):
        # TODO KV: if I'm mutually exclusive, collect siblings from my column and also column 0 (ok, but actually? what if there are two sets of subgroups?)
        # if I'm not ME, collect siblings from my column and also any ME ones from other columns
        thiscolnum = self.column()
        siblings = []
        parent = self.parent()
        if parent is None:
            parent = self.model().invisibleRootItem()
        numsiblingsincludingself = parent.rowCount()
        tempthisnodetext = self.text()
        if self.data(Qt.UserRole+mutuallyexclusiverole):
            for snum in range(numsiblingsincludingself):
                sibling = parent.child(snum, thiscolnum)
                if sibling is None:
                    sibling = parent.child(snum, 0)
                siblingtext = sibling.text()
                if sibling.index() != self.index():  # ie, it's actually a sibling
                    siblings.append(sibling)
        else:  # I'm not ME but my siblings might be
            for rownum in range(numsiblingsincludingself):
                for colnum in range(parent.columnCount()):
                    sibling = parent.child(rownum, colnum)
                    if sibling is not None and sibling.index() != self.index():
                        siblings.append(sibling)
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
    #
    # def forceuncheck(self):
    #
    #     self.setCheckState(Qt.Unchecked)
    #     # force-uncheck all descendants
    #     if self.hascheckedchild():
    #         for r in range(self.rowCount()):
    #             self.child(r, 0).forceuncheck()
    #

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

    def __init__(self, txt="", treeit=None):
        super().__init__()

        self.setEditable(False)
        self.setText(txt)
        self.setCheckable(False)
        self.treeitem = treeit
        if treeit is not None:
            self.treeitem.listitem = self
        self.setData(False, Qt.UserRole+selectedrole)

    def unselectpath(self):
        self.treeitem.uncheck()

    def selectpath(self):
        self.treeitem.check(fully=True)


class MovementPathsProxyModel(QSortFilterProxyModel):

    def __init__(self, parent=None, wantselected=None):
        super(MovementPathsProxyModel, self).__init__(parent)
        self.wantselected = wantselected

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
        colcount = treenode.columnCount()
        for r in range(treenode.rowCount()):
            if colcount == 0:
                # TODO KV the if might not ever get used (assuming we're using multi columns for axis direction pairs)
                print("TODO KV colcount is zero")
                treechild = treenode.child(r, 0)
                path = treechild.data(role=Qt.UserRole+pathdisplayrole)
                listitem = MovementListItem(txt=path, treeit=treechild)  # also sets treeitem's listitem
                self.appendRow(listitem)
                self.populate(treechild)
            else:
                # there are multiple columns; none have further descendants
                for colnum in range(colcount):
                    treechild = treenode.child(r, colnum)
                    if treechild is not None:
                        path = treechild.data(role=Qt.UserRole+pathdisplayrole)
                        listitem = MovementListItem(txt=path, treeit=treechild)  # also sets treeitem's listitem
                        self.appendRow(listitem)
                        self.populate(treechild)
                        # not necessary because shouldn't go any deeper
                        # self.populate(treechild)


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


# TODO KV fix up for movement
# class MovementView(QWidget):
#     # selected_gloss = pyqtSignal(str)
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#
#         main_layout = QVBoxLayout()
#         self.setLayout(main_layout)
#
#         # TODO: maybe make this editable
#         # self.corpus_title = QLineEdit(corpus_title, parent=self)
#         main_layout.addWidget(self.corpus_title)
#
#         self.corpus_model = CorpusModel(parent=self)
#         self.corpus_view = QListView(parent=self)
#         self.corpus_view.setModel(self.corpus_model)
#         self.corpus_view.clicked.connect(self.handle_selection)
#         main_layout.addWidget(self.corpus_view)
#
#     def handle_selection(self, index):
#         gloss = self.corpus_model.glosses[index.row()]
#         self.selected_gloss.emit(gloss)
#
#     def updated_glosses(self, glosses, current_gloss):
#         self.corpus_model.glosses.clear()
#         self.corpus_model.glosses.extend(glosses)
#         self.corpus_model.glosses.sort()
#         self.corpus_model.layoutChanged.emit()
#
#         index = self.corpus_model.glosses.index(current_gloss)
#
#         # Ref: https://www.qtcentre.org/threads/32007-SetSelection-QListView-Pyqt
#         self.corpus_view.selectionModel().setCurrentIndex(self.corpus_view.model().index(index, 0),
#                                                           QItemSelectionModel.SelectCurrent)
#
#     def remove_gloss(self, gloss):
#         self.corpus_model.glosses.remove(gloss)
#         self.corpus_model.layoutChanged.emit()
#         self.corpus_view.clearSelection()
#
#     def clear(self):
#         self.corpus_title.setText('Untitled')
#
#         self.corpus_model.glosses.clear()
#         self.corpus_model.layoutChanged.emit()
#         self.corpus_view.clearSelection()


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
                        if len(higherpath) == len(pathitemslists)-1:  # TODO
                            validpaths.append(higherpath + [lastitem])
    elif len(pathitemslists) == 1:  # the path is only 1 level long (but possibly with multiple options)
        for lastitem in pathitemslists[0]:
            # if lastitem.parent() == .... used to be if topitem.childCount() == 0:
            validpaths.append([lastitem])
    else:
        validpaths = []
        # TODO pass?
        # nothing to add to paths - this case shouldn't ever happen
    return validpaths


def countColumns(dictionary):
    maxcols = 0
    for k in dictionary.keys():
        if k.startswith("subgroups"):
            numcols = len(dictionary[k])
            maxcols = max([maxcols, numcols])
        else:
            maxbelow = countColumns(dictionary[k])
            maxcols = max([maxcols, maxbelow])
    return maxcols
