from PyQt5.QtWidgets import (
    QListView,
    QTreeView,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QComboBox,
    QLabel,
    QCompleter,
    QAbstractItemView,
    QStyledItemDelegate,
    QStyle,
    QStyleOptionButton,
    QApplication,
    QHeaderView,
    QStyleOptionFrame,
    QFrame
)

from PyQt5.QtCore import (
    Qt,
    QEvent,
)

from lexicon.module_classes import delimiter, userdefinedroles as udr, MovementModule
from models.movement_models import MovementTreeModel, MovementPathsProxyModel
from serialization_classes import MovementTreeSerializable
from gui.modulespecification_widgets import AddedInfoContextMenu, ModuleSpecificationPanel
from constant import HAND


class MvmtTreeSearchComboBox(QComboBox):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.refreshed = True
        self.lasttextentry = ""
        self.lastcompletedentry = ""

    def keyPressEvent(self, event):
        key = event.key()
        modifiers = event.modifiers()

        if key == Qt.Key_Right:  # TODO KV and modifiers == Qt.NoModifier:

            if self.currentText():
                self.parent().treedisplay.collapseAll()
                itemstoselect = gettreeitemsinpath(self.parent().treemodel,
                                                   self.currentText(),
                                                   delim=delimiter)
                for item in itemstoselect:
                    if item.checkState() == Qt.Unchecked:
                        item.setCheckState(Qt.PartiallyChecked)
                    self.parent().treedisplay.setExpanded(item.index(), True)
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
            else:  # ie, not self.lastcompletedentry
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


class MovementTreeView(QTreeView):

    # Ref: adapted from https://stackoverflow.com/questions/68069548/checkbox-with-persistent-editor
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


class MvmtTreeListView(QListView):

    def __init__(self):
        super().__init__()

    def keyPressEvent(self, event):
        key = event.key()
        # modifiers = event.modifiers()

        if key == Qt.Key_Delete or key == Qt.Key_Backspace:
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


# Ref: https://stackoverflow.com/questions/48575298/pyqt-qtreewidget-how-to-add-radiobutton-for-items
class MvmtTreeItemDelegate(QStyledItemDelegate):

    # def createEditor(self, parent, option, index):
    #     theeditor = QStyledItemDelegate.createEditor(self, parent, option, index)
    #     theeditor.returnPressed.connect(self.returnkeypressed)
    #     return theeditor
    #
    # def setEditorData(self, editor, index):
    #     editor.setText(index.data(role=Qt.DisplayRole))
    #
    # def setModelData(self, editor, model, index):
    #     editableitem = model.itemFromIndex(index)
    #     if isinstance(editableitem, QStandardItem) and not isinstance(editableitem, MovementTreeItem) and not isinstance(editableitem, MovementListItem):
    #         # then this is the editable part of a movement tree item
    #         treeitem = editableitem.parent().child(editableitem.row(), 0)
    #         editableitem.setData(editor.text(), role=Qt.DisplayRole)
    #
    # def __init__(self):
    #     super().__init__()
    #     self.commitData.connect(self.validatedata)

    def returnkeypressed(self):
        print("return pressed")
        return True

    def paint(self, painter, option, index):
        if index.data(Qt.UserRole+udr.mutuallyexclusiverole):
            widget = option.widget
            style = widget.style() if widget else QApplication.style()
            opt = QStyleOptionButton()
            opt.rect = option.rect
            opt.text = index.data()
            opt.state |= QStyle.State_On if index.data(Qt.CheckStateRole) else QStyle.State_Off
            style.drawControl(QStyle.CE_RadioButton, opt, painter, widget)
            if index.data(Qt.UserRole+udr.lastingrouprole) and not index.data(Qt.UserRole+udr.finalsubgrouprole):
                painter.drawLine(opt.rect.bottomLeft(), opt.rect.bottomRight())
        else:
            QStyledItemDelegate.paint(self, painter, option, index)
            if index.data(Qt.UserRole+udr.lastingrouprole) and not index.data(Qt.UserRole+udr.finalsubgrouprole):
                opt = QStyleOptionFrame()
                opt.rect = option.rect
                painter.drawLine(opt.rect.bottomLeft(), opt.rect.bottomRight())



class MovementSpecificationPanel(ModuleSpecificationPanel):
    # see_relations = pyqtSignal()

    def __init__(self, moduletoload=None, **kwargs):
        super().__init__(**kwargs)

        main_layout = QVBoxLayout()

        self.treemodel = MovementTreeModel()
        if moduletoload is not None:
            if isinstance(moduletoload, MovementModule):
                self.existingkey = moduletoload.uniqueid
                self.treemodel = MovementTreeModel(MovementTreeSerializable(moduletoload.movementtreemodel))
            else:
                print("moduletoload must be of type MovementModule")
        else:
            self.treemodel.populate(self.treemodel.invisibleRootItem())

        self.listmodel = self.treemodel.listmodel

        self.comboproxymodel = MovementPathsProxyModel(wantselected=False)
        self.comboproxymodel.setSourceModel(self.listmodel)

        self.listproxymodel = MovementPathsProxyModel(wantselected=True)
        self.listproxymodel.setSourceModel(self.listmodel)

        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Enter tree node"))  # TODO KV delete? , self))

        self.combobox = MvmtTreeSearchComboBox(parent=self)
        self.combobox.setModel(self.comboproxymodel)
        self.combobox.setCurrentIndex(-1)
        self.combobox.adjustSize()
        self.combobox.setEditable(True)
        self.combobox.setInsertPolicy(QComboBox.NoInsert)
        self.combobox.setFocusPolicy(Qt.StrongFocus)
        self.combobox.setEnabled(True)
        self.combobox.completer().setCaseSensitivity(Qt.CaseInsensitive)
        self.combobox.completer().setFilterMode(Qt.MatchContains)
        self.combobox.completer().setCompletionMode(QCompleter.PopupCompletion)
        # tct = TreeClickTracker(self)  todo kv
        # self.combobox.installEventFilter(tct)
        search_layout.addWidget(self.combobox)

        # self.addLayout(search_layout)
        main_layout.addLayout(search_layout)

        selection_layout = QHBoxLayout()

        self.treedisplay = MovementTreeView()
        self.treedisplay.setItemDelegate(MvmtTreeItemDelegate())
        self.treedisplay.setHeaderHidden(True)
        self.treedisplay.setModel(self.treemodel)

        userspecifiableitems = self.treemodel.findItemsByRoleValues(Qt.UserRole+udr.isuserspecifiablerole, [1, 2, 3])
        editableitems = [it.editablepart() for it in userspecifiableitems]
        for it in editableitems:
            self.treedisplay.openPersistentEditor(self.treemodel.indexFromItem(it))

        self.treedisplay.installEventFilter(self)
        self.treedisplay.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.treedisplay.setMinimumWidth(400)

        selection_layout.addWidget(self.treedisplay)

        list_layout = QVBoxLayout()

        self.pathslistview = MvmtTreeListView()
        self.pathslistview.setSelectionMode(QAbstractItemView.MultiSelection)
        self.pathslistview.setModel(self.listproxymodel)
        self.pathslistview.setMinimumWidth(400)
        self.pathslistview.installEventFilter(self)

        list_layout.addWidget(self.pathslistview)

        buttons_layout = QHBoxLayout()

        sortlabel = QLabel("Sort by:")
        buttons_layout.addWidget(sortlabel)

        self.sortcombo = QComboBox()
        self.sortcombo.addItems(["order in tree (default)", "alpha by full path", "alpha by lowest node", "order of selection"])
        self.sortcombo.setInsertPolicy(QComboBox.NoInsert)
        self.sortcombo.currentTextChanged.connect(self.sort)
        buttons_layout.addWidget(self.sortcombo)
        buttons_layout.addStretch()

        self.clearbutton = QPushButton("Clear")
        self.clearbutton.clicked.connect(self.clearlist)
        buttons_layout.addWidget(self.clearbutton)

        list_layout.addLayout(buttons_layout)
        selection_layout.addLayout(list_layout)
        main_layout.addLayout(selection_layout)

        separate_line = QFrame()
        separate_line.setFrameShape(QFrame.HLine)
        separate_line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separate_line)

        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

    def getsavedmodule(self, articulators, timingintervals, addedinfo, inphase):
        movmod = MovementModule(self.treemodel,
                                articulators=articulators,
                                timingintervals=timingintervals,
                                addedinfo=addedinfo,
                                inphase=inphase)
        if self.existingkey is not None:
            movmod.uniqueid = self.existingkey
        else:
            self.existingkey = movmod.uniqueid
        return movmod

    def sort(self):
        self.listproxymodel.updatesorttype(self.sortcombo.currentText())

    def eventFilter(self, source, event):
        # Ref: adapted from https://stackoverflow.com/questions/26021808/how-can-i-intercept-when-a-widget-loses-its-focus
        # if (event.type() == QEvent.FocusOut):  # and source is items[0].child(0, 0)):
        #     print('TODO KV eventFilter: focus out', source)
        #     # return true here to bypass default behaviour
        # return super().eventFilter(source, event)

        if event.type() == QEvent.KeyPress:
            key = event.key()
            if key == Qt.Key_Enter:
                print("enter pressed")
            # TODO KV return true??
        elif event.type() == QEvent.ContextMenu and source == self.pathslistview:
            proxyindex = self.pathslistview.currentIndex()  # TODO KV what if multiple are selected?
            # proxyindex = self.pathslistview.selectedIndexes()[0]
            listindex = proxyindex.model().mapToSource(proxyindex)
            addedinfo = listindex.model().itemFromIndex(listindex).treeitem.addedinfo

            menu = AddedInfoContextMenu(addedinfo)
            menu.exec_(event.globalPos())

        return super().eventFilter(source, event)

    def handle_articulator_changed(self, articulator):
        enable_jointspecmvmts = articulator == HAND
        self.treemodel.setNodeEnabledRecursive("Joint-specific movements", enable_jointspecmvmts)

    def refresh(self):
        self.refresh_treemodel()

    def clear(self):
        self.refresh_treemodel()

    def refresh_treemodel(self):
        # refresh tree model, including changing sort_by option to the default
        self.treemodel = MovementTreeModel()
        self.treemodel.populate(self.treemodel.invisibleRootItem())

        self.listmodel = self.treemodel.listmodel

        self.comboproxymodel.setSourceModel(self.listmodel)
        self.listproxymodel.setSourceModel(self.listmodel)
        self.combobox.setModel(self.comboproxymodel)
        self.combobox.setCurrentIndex(-1)
        self.treedisplay.setModel(self.treemodel)
        self.pathslistview.setModel(self.listproxymodel)

        self.sortcombo.setCurrentIndex(0)  # change 'sort by' option to the first item of the list.

        # self.combobox.clear()

    def clearlist(self, button):
        numtoplevelitems = self.treemodel.invisibleRootItem().rowCount()
        for rownum in range(numtoplevelitems):
            self.treemodel.invisibleRootItem().child(rownum, 0).uncheck(force=True)

    def desiredwidth(self):
        return 500

    def desiredheight(self):
        return 700
