from PyQt5.QtWidgets import (
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
    QStyleOptionViewItem,
    QApplication,
    QHeaderView,
    QStyleOptionFrame,
    QFrame
)

from PyQt5.QtCore import (
    Qt,
    QEvent,
    QItemSelectionModel
)

from lexicon.module_classes import userdefinedroles as udr, MovementModule
from models.movement_models import MovementTreeModel, MovementPathsProxyModel, MovementTreeItem
from serialization_classes import MovementTreeSerializable
from gui.modulespecification_widgets import AddedInfoContextMenu, ModuleSpecificationPanel, TreeListView, TreePathsListItemDelegate, TreeSearchComboBox
from constant import HAND


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

    # similar to QTreeView.setExpanded(index, True), but makes sure all ancestors are expanded too, on the way down to this node
    def setPathExpanded(self, targettreeitem):
        nodes = []  # building the list from lowest to highest
        curitem = targettreeitem.parent()  # don't include the target item, because we don't need to see (or hide) its children
        while curitem is not None:
            nodes.append(curitem)
            curitem = curitem.parent()

        nodes.reverse()  # now goes from root down to our target node

        for treeitem in nodes:
            self.setExpanded(treeitem.index(), True)

# Ref: https://stackoverflow.com/questions/48575298/pyqt-qtreewidget-how-to-add-radiobutton-for-items
class MvmtTreeItemDelegate(QStyledItemDelegate):

    def paint(self, painter, option, index):
        
        if index.data(Qt.UserRole+udr.mutuallyexclusiverole):
            widget = option.widget
            style = widget.style() if widget else QApplication.style()
            opt = QStyleOptionButton()
            opt.rect = option.rect
            opt.text = index.data()
            opt.state |= QStyle.State_On if index.data(Qt.CheckStateRole) else QStyle.State_Off
            style.drawControl(QStyle.CE_RadioButton, opt, painter, widget)
            if index.data(Qt.UserRole+udr.firstingrouprole) and not index.data(Qt.UserRole+udr.firstsubgrouprole):
                painter.drawLine(opt.rect.topLeft(), opt.rect.topRight())
        elif index.data(Qt.UserRole+udr.nocontrolrole): 
            widget = option.widget
            style = widget.style() if widget else QApplication.style()
            opt = QStyleOptionViewItem(option)
            self.initStyleOption(opt, index)  
            opt.features &= ~QStyleOptionViewItem.HasCheckIndicator # Turn off HasCheckIndicator
            style.drawControl(QStyle.CE_ItemViewItem, opt, painter, widget)
        else:
            QStyledItemDelegate.paint(self, painter, option, index)
            if index.data(Qt.UserRole+udr.firstingrouprole) and not index.data(Qt.UserRole+udr.firstsubgrouprole):
                opt = QStyleOptionFrame()
                opt.rect = option.rect
                painter.drawLine(opt.rect.topLeft(), opt.rect.topRight())


class MovementSpecificationPanel(ModuleSpecificationPanel):

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

        # create layout with combobox for searching movement items
        search_layout = self.create_search_layout()
        main_layout.addLayout(search_layout)

        # create layout with movement options tree view as well as a list view for selected movement options
        selection_layout = self.create_selection_layout()
        main_layout.addLayout(selection_layout)

        separate_line = QFrame()
        separate_line.setFrameShape(QFrame.HLine)
        separate_line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separate_line)

        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

    def create_search_layout(self):
        search_layout = QHBoxLayout()

        search_layout.addWidget(QLabel("Enter tree node"))

        self.combobox = TreeSearchComboBox(parent=self)
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
        self.combobox.item_selected.connect(self.selectlistitem)
        search_layout.addWidget(self.combobox)

        return search_layout

    def create_selection_layout(self):

        selection_layout = QHBoxLayout()

        self.treedisplay = MovementTreeView()
        self.treedisplay.setItemDelegate(MvmtTreeItemDelegate())
        self.treedisplay.setHeaderHidden(True)
        self.treedisplay.setModel(self.treemodel)

        userspecifiableitems = self.treemodel.findItemsByRoleValues(Qt.UserRole + udr.isuserspecifiablerole, [1, 2, 3])
        editableitems = [it.editablepart() for it in userspecifiableitems]
        for it in editableitems:
            self.treedisplay.openPersistentEditor(self.treemodel.indexFromItem(it))

        self.treedisplay.installEventFilter(self)
        self.treedisplay.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.treedisplay.setMinimumWidth(400)

        selection_layout.addWidget(self.treedisplay)

        list_layout = QVBoxLayout()

        self.pathslistview = TreeListView()
        self.pathslistview.setItemDelegate(TreePathsListItemDelegate())
        self.pathslistview.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.pathslistview.setModel(self.listproxymodel)
        self.pathslistview.setMinimumWidth(400)
        self.pathslistview.installEventFilter(self)

        list_layout.addWidget(self.pathslistview)

        buttons_layout = QHBoxLayout()

        sortlabel = QLabel("Sort by:")
        buttons_layout.addWidget(sortlabel)

        self.sortcombo = QComboBox()
        self.sortcombo.addItems(
            ["order in tree (default)", "alpha by full path", "alpha by lowest node", "order of selection"])
        self.sortcombo.setInsertPolicy(QComboBox.NoInsert)
        self.sortcombo.currentTextChanged.connect(self.sort)
        buttons_layout.addWidget(self.sortcombo)
        buttons_layout.addStretch()

        self.clearbutton = QPushButton("Clear")
        self.clearbutton.clicked.connect(self.clearlist)
        buttons_layout.addWidget(self.clearbutton)

        list_layout.addLayout(buttons_layout)
        selection_layout.addLayout(list_layout)

        return selection_layout

    def selectlistitem(self, treeitem):
        if isinstance(treeitem, MovementTreeItem):
            self.treedisplay.collapseAll()
            self.treedisplay.setPathExpanded(treeitem)

        listmodelindex = self.listmodel.indexFromItem(treeitem.listitem)
        listproxyindex = self.listproxymodel.mapFromSource(listmodelindex)
        self.pathslistview.selectionModel().select(listproxyindex, QItemSelectionModel.ClearAndSelect)

    def getsavedmodule(self, articulators, timingintervals, phonlocs, addedinfo, inphase):
        movmod = MovementModule(self.treemodel,
                                articulators=articulators,
                                timingintervals=timingintervals,
                                phonlocs=phonlocs,
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
