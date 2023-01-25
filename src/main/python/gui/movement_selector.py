import os
import json
from copy import copy

from PyQt5.QtWidgets import (
    QFrame,
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
    QErrorMessage,
)

from PyQt5.QtCore import (
    Qt,
    QSize,
    QEvent,
    pyqtSignal
)

from gui.movement_view import MovementTreeModel, MovementTreeSerializable, MovementPathsProxyModel, TreeSearchComboBox, TreeListView, MovementTreeView
from gui.module_selector import ModuleSpecificationLayout, AddedInfoContextMenu
from lexicon.module_classes import MovementModule, delimiter, userdefinedroles as udr


# https://stackoverflow.com/questions/48575298/pyqt-qtreewidget-how-to-add-radiobutton-for-items
class TreeItemDelegate(QStyledItemDelegate):

    def createEditor(self, parent, option, index):
        theeditor = QStyledItemDelegate.createEditor(self, parent, option, index)
        theeditor.returnPressed.connect(self.returnkeypressed)
        return theeditor

    def setEditorData(self, editor, index):
        editor.setText(index.data(role=Qt.DisplayRole))

    def setModelData(self, editor, model, index):
        model.itemFromIndex(index).setData(editor.text(), role=Qt.DisplayRole)
        currentpath = model.itemFromIndex(index).data(role=Qt.UserRole+udr.pathdisplayrole)
        newpathlevels = currentpath.split(delimiter)
        newpathlevels[-1] = editor.text()
        model.itemFromIndex(index).setData(delimiter.join(newpathlevels), role=Qt.UserRole+udr.pathdisplayrole)

    def __init__(self):
        super().__init__()
        self.commitData.connect(self.validatedata)

    def returnkeypressed(self):
        print("return pressed")
        return True

    def validatedata(self, editor):
        # TODO KV right now validation looks exactly the same for all edits; is this desired behaviour?
        valstring = editor.text()
        isanumber = False
        if valstring.isnumeric():
            isanumber = True
            valnum = int(valstring)
        elif valstring.replace(".", "").isnumeric():
            isanumber = True
            valnum = float(valstring)
        if valstring not in ["", "#"] and (valnum % 0.5 != 0 or valnum < 1 or not isanumber):
            errordialog = QErrorMessage(editor.parent())
            errordialog.showMessage("Number of repetitions must be at least 1 and also a multiple of 0.5")
            editor.setText("#")
            # TODO KV is there a way to reset the focus on the editor to force the user to fix the value without just emptying the lineedit?
            # editor.setFocus()  # this creates an infinite loop

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


# TODO KV - add undo, ...


# TODO KV - copied from locationspecificationlayout - make sure contents are adjusted for movement
# class MovementSpecificationLayout(QVBoxLayout):
class MovementSpecificationLayout(ModuleSpecificationLayout):
    saved_movement = pyqtSignal(MovementTreeModel, dict, list, int)
    deleted_movement = pyqtSignal()

    def __init__(self, moduletoload=None, **kwargs):  # TODO KV app_ctx, movement_specifications,
        super().__init__(**kwargs)

        self.treemodel = MovementTreeModel()
        if moduletoload:
            if isinstance(moduletoload, MovementTreeModel):
                self.treemodel = MovementTreeSerializable(moduletoload).getMovementTreeModel()
                # self.treemodel = MovementModuleSerializable(mvmttreeonly=moduletoload).getMovementTreeModel()
            # elif isinstance(moduletoload, MovementTree):
            #     # TODO KV - make sure listmodel & listitems are also populated
            #     self.treemodel = moduletoload.getMovementTreeModel()
            elif isinstance(moduletoload, MovementModule):
                self.treemodel = MovementTreeSerializable(moduletoload.movementtreemodel).getMovementTreeModel()
            else:
                print("moduletoload must be either of type MovementTreeModel or of type MovementModule")
        else:
            self.treemodel.populate(self.treemodel.invisibleRootItem())

        self.listmodel = self.treemodel.listmodel

        self.comboproxymodel = MovementPathsProxyModel(wantselected=False) #, parent=self.listmodel
        self.comboproxymodel.setSourceModel(self.listmodel)

        self.listproxymodel = MovementPathsProxyModel(wantselected=True)
        self.listproxymodel.setSourceModel(self.listmodel)

        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Enter tree node"))  # TODO KV delete? , self))

        self.combobox = TreeSearchComboBox(self)
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

        self.addLayout(search_layout)

        selection_layout = QHBoxLayout()

        self.treedisplay = MovementTreeView()
        self.treedisplay.setItemDelegate(TreeItemDelegate())
        self.treedisplay.setHeaderHidden(True)
        self.treedisplay.setModel(self.treemodel)
        # TODO KV figure out adding number selector
        items = self.treemodel.findItems("Number of repetitions", Qt.MatchRecursive)
        repsindex = self.treemodel.indexFromItem(items[0].child(0, 0))
        self.treedisplay.openPersistentEditor(repsindex)
        self.treedisplay.installEventFilter(self)
        self.treedisplay.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.treedisplay.setMinimumWidth(400)

        selection_layout.addWidget(self.treedisplay)

        list_layout = QVBoxLayout()

        self.pathslistview = TreeListView()
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
        # self.sortcombo.completer().setCompletionMode(QCompleter.PopupCompletion)
        # self.sortcombo.currentTextChanged.connect(self.listproxymodel.sort(self.sortcombo.currentText()))
        self.sortcombo.currentTextChanged.connect(self.sort)
        buttons_layout.addWidget(self.sortcombo)
        buttons_layout.addStretch()

        self.clearbutton = QPushButton("Clear")
        self.clearbutton.clicked.connect(self.clearlist)
        buttons_layout.addWidget(self.clearbutton)

        list_layout.addLayout(buttons_layout)
        selection_layout.addLayout(list_layout)
        self.addLayout(selection_layout)

    def get_savedmodule_signal(self):
        return self.saved_movement

    def get_savedmodule_args(self):
        return (self.treemodel,)

    def get_deletedmodule_signal(self):
        return self.deleted_movement

    def sort(self):
        self.listproxymodel.updatesorttype(self.sortcombo.currentText())

    def eventFilter(self, source, event):
        # adapted from https://stackoverflow.com/questions/26021808/how-can-i-intercept-when-a-widget-loses-its-focus
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
            menu.info_added.connect(lambda newaddedinfo: self.updateaddedinfo(newaddedinfo, listindex.model().itemFromIndex(listindex).treeitem))
            menu.exec_(event.globalPos())

        return super().eventFilter(source, event)

    def updateaddedinfo(self, newaddedinfo, treeitem):  # TODO KV this shouldn't be necessary but seems to be anyway...?
        treeitem.addedinfo = newaddedinfo

    def refresh(self):
        self.refresh_treemodel()

    def clear(self):
        self.refresh_treemodel()

    def refresh_treemodel(self):
        self.treemodel = MovementTreeModel()  # movementparameters=movement_specifications)
        self.treemodel.populate(self.treemodel.invisibleRootItem())
        # items = self.treemodel.findItems("Number of repetitions", Qt.MatchRecursive)
        # repsindex = self.treemodel.indexFromItem(items[0].child(0, 0))
        # self.treedisplay.openPersistentEditor(repsindex)

        self.listmodel = self.treemodel.listmodel

        self.comboproxymodel.setSourceModel(self.listmodel)
        self.listproxymodel.setSourceModel(self.listmodel)
        self.combobox.setModel(self.comboproxymodel)
        self.combobox.setCurrentIndex(-1)
        self.treedisplay.setModel(self.treemodel)
        self.pathslistview.setModel(self.listproxymodel)

        # self.combobox.clear()

    def clearlist(self, button):
        numtoplevelitems = self.treemodel.invisibleRootItem().rowCount()
        for rownum in range(numtoplevelitems):
            self.treemodel.invisibleRootItem().child(rownum, 0).uncheck(force=True)

    def desiredwidth(self):
        return 500

    def desiredheight(self):
        return 700


# class MovementSelectorDialog(QDialog):
#     saved_movement = pyqtSignal(MovementTreeModel, dict)
#
#     def __init__(self, mainwindow, new_instance=False, moduletoload=None, hands=None, x_start=0, x_end=0, **kwargs):
#         super().__init__(**kwargs)
#         self.mainwindow = mainwindow
#         self.system_default_movement_specifications = mainwindow.system_default_movement
#
#         main_layout = QVBoxLayout()
#
#         self.hands_layout = HandSelectionLayout(hands)
#         main_layout.addLayout(self.hands_layout)
#         self.xslot_layout = XslotLinkingLayout(x_start, x_end, self.mainwindow)
#         main_layout.addLayout(self.xslot_layout)
#
#         self.movement_layout = MovementSpecificationLayout(moduletoload=moduletoload)
#         main_layout.addLayout(self.movement_layout)
#
#         separate_line = QFrame()
#         separate_line.setFrameShape(QFrame.HLine)
#         separate_line.setFrameShadow(QFrame.Sunken)
#         main_layout.addWidget(separate_line)
#
#         buttons = None
#         applytext = ""
#         if new_instance:
#             buttons = QDialogButtonBox.RestoreDefaults | QDialogButtonBox.Save | QDialogButtonBox.Apply | QDialogButtonBox.Cancel
#             applytext = "Save and close"
#         else:
#             buttons = QDialogButtonBox.RestoreDefaults | QDialogButtonBox.Apply | QDialogButtonBox.Cancel
#             applytext = "Save"
#
#         self.button_box = QDialogButtonBox(buttons, parent=self)
#         if new_instance:
#             self.button_box.button(QDialogButtonBox.Save).setText("Save and add another")
#         self.button_box.button(QDialogButtonBox.Apply).setText(applytext)
#
#         # TODO KV keep? from orig locationdefinerdialog:
#         #      Ref: https://programtalk.com/vs2/python/654/enki/enki/core/workspace.py/
#         self.button_box.clicked.connect(self.handle_button_click)
#
#         main_layout.addWidget(self.button_box)
#
#         self.setLayout(main_layout)
#         self.setMinimumSize(QSize(500, 700))
#
#     def handle_button_click(self, button):
#         standard = self.button_box.standardButton(button)
#
#         if standard == QDialogButtonBox.Cancel:
#             # TODO KV - BUG? - if we are editing an already-existing movement module, this seems to save anyway
#             self.reject()
#
#         elif standard == QDialogButtonBox.Save:  # save and add another
#             # save info and then refresh screen to enter next movemement module
#             self.saved_movement.emit(self.movement_layout.treemodel, self.hands_layout.gethands())
#             # self.movement_layout.clearlist(None)  # TODO KV should this use "restore defaults" instead?
#             self.hands_layout.clear()
#             self.movement_layout.refresh_treemodel()
#
#         elif standard == QDialogButtonBox.Apply:  # save and close
#             # save info and then close dialog
#             self.saved_movement.emit(self.movement_layout.treemodel, self.hands_layout.gethands())
#             self.accept()
#
#         elif standard == QDialogButtonBox.RestoreDefaults:  # restore defaults
#             # TODO KV -- where should the "defaults" be defined?
#             self.movement_layout.clearlist(button)
#             self.hands_layout.clear()
#
#     #     # elif standard == QDialogButtonBox.NoButton:
#     #     #     action_role = button.property('ActionRole')
#     #     #     if action_role == 'Export':
#     #     #         file_name, file_type = QFileDialog.getSaveFileName(self,
#     #     #                                                            self.tr('Export Locations'),
#     #     #                                                            os.path.join(
#     #     #                                                                self.app_settings['storage'][
#     #     #                                                                    'recent_folder'],
#     #     #                                                                'locations.json'),
#     #     #                                                            self.tr('JSON Files (*.json)'))
#     #     #
#     #     #         if file_name:
#     #     #             with open(file_name, 'w') as f:
#     #     #                 json.dump(self.location_tab.get_locations().get_attr_dict(), f, sort_keys=True, indent=4)
#     #     #
#     #     #             QMessageBox.information(self, 'Locations Exported',
#     #     #                                     'Locations have been successfully exported!')
#     #     #     elif action_role == 'Import':
#     #     #         file_name, file_type = QFileDialog.getOpenFileName(self, self.tr('Import Locations'),
#     #     #                                                            self.app_settings['storage']['recent_folder'],
#     #     #                                                            self.tr('JSON Corpus (*.json)'))
#     #     #         if file_name:
#     #     #             with open(file_name, 'r') as f:
#     #     #                 location_json = json.load(f)
#     #     #                 imported_locations = Locations(
#     #     #                     {loc_id: LocationParameter(name=param['name'],
#     #     #                                                image_path=param['image_path'],
#     #     #                                                location_polygons=param['location_polygons'],
#     #     #                                                default=param['default'])
#     #     #                      for loc_id, param in location_json.items()}
#     #     #                 )
#     #     #                 self.location_tab.import_locations(imported_locations)
#     #     #                 self.saved_locations.emit(self.location_tab.get_locations())
#
#         # TODO KV - continue copying from class LocationDefinerDialog in location_definer



