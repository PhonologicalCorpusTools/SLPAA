import os
import json
from PyQt5.QtWidgets import (
    QFrame,
    QGridLayout,
    QLineEdit,
    QPushButton,
    QDialog,
    QHBoxLayout,
    QListView,
    QVBoxLayout,
    QFileDialog,
    QWidget,
    QTabWidget,
    QTabBar,
    QDialogButtonBox,
    QMessageBox,
    QSlider,
    QTreeView,
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
    QErrorMessage
)

from PyQt5.QtCore import (
    Qt,
    QAbstractListModel,
    pyqtSignal,
    QSize,
    QEvent
)

from gui.movement_view import MovementTreeModel, MovementListModel, MovementPathsProxyModel, TreeSearchComboBox, TreeListView, mutuallyexclusiverole, texteditrole, lastingrouprole, finalsubgrouprole, subgroupnamerole, MovementTreeView, MovementTreeItem

# https://stackoverflow.com/questions/48575298/pyqt-qtreewidget-how-to-add-radiobutton-for-items
class Delegate(QStyledItemDelegate):

    # # how to make sure this only gets used for # of repetitions?
    # def createEditor(self, parent, option, index):
    #     if index.parent().data(Qt.DisplayRole) == "Number of repetitions": # if index.data(Qt.DisplayRole) == "How many":
    #         editor = RepEditor(parent)  # QLineEdit(parent)
    #         # editor.setText("# reps")
    #         return editor
    #     else:
    #         QStyledItemDelegate.createEditor(parent, option, index)

    def createEditor(self, parent, option, index):
        theeditor = QStyledItemDelegate.createEditor(self, parent, option, index)
        # theeditor.__class__ = RepsEditor
        theeditor.returnPressed.connect(self.returnkeypressed)
        return theeditor

    # # how to make sure this only gets used for # of repetitions?
    # def setEditorData(self, editor, index):
    #     if index.parent().data(Qt.DisplayRole) == "Number of repetitions": # if index.data(Qt.DisplayRole) == "How many":
    #         value = index.data(index, Qt.EditRole)
    #         editor.setText(value)
    #     else:
    #         QStyledItemDelegate.setEditorData(editor, index)
    #
    # def setModelData(self, editor, model, index):
    #     if index.parent().data(Qt.DisplayRole) == "Number of repetitions": # if index.data(Qt.DisplayRole) == "How many":
    #         value = editor.text()
    #         model.setData(index, value, Qt.EditRole)
    #     else:
    #         QStyledItemDelegate.setModelData(editor, model, index)
    #
    # def updateEditorGeometry(self, editor, option, index):
    #     editor.setGeometry(option.rect)

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
        if index.data(Qt.UserRole+mutuallyexclusiverole):
            widget = option.widget
            style = widget.style() if widget else QApplication.style()
            opt = QStyleOptionButton()
            opt.rect = option.rect
            opt.text = index.data()
            opt.state |= QStyle.State_On if index.data(Qt.CheckStateRole) else QStyle.State_Off
            style.drawControl(QStyle.CE_RadioButton, opt, painter, widget)
            if index.data(Qt.UserRole + lastingrouprole) and not index.data(Qt.UserRole + finalsubgrouprole):
                painter.drawLine(opt.rect.bottomLeft(), opt.rect.bottomRight())
        else:
            QStyledItemDelegate.paint(self, painter, option, index)
            if index.data(Qt.UserRole + lastingrouprole) and not index.data(Qt.UserRole + finalsubgrouprole):
                opt = QStyleOptionFrame()
                opt.rect = option.rect
                painter.drawLine(opt.rect.bottomLeft(), opt.rect.bottomRight())

#
# class RepsEditor(QLineEdit):
#
#     def returnPressed(self):
#         print("return pressed")  # ... and hopefully nothing else happens!
#         # super().returnPressed()


# TODO KV - add undo, ...


# TODO KV - copied from locationspecificationlayout - make sure contents are adjusted for movement
class MovementSpecificationLayout(QVBoxLayout):
    def __init__(self, moduletoload=None, **kwargs):  # TODO KV app_ctx, movement_specifications,
        super().__init__(**kwargs)

        print("loading movementspecificationlayout with", "brand new" if moduletoload is None else "existing", "model")
        self.treemodel = MovementTreeModel()  # movementparameters=movement_specifications)
        if moduletoload is not None:
            self.treemodel = moduletoload
        self.rootNode = self.treemodel.invisibleRootItem()
        if moduletoload is None:
            self.treemodel.populate(self.rootNode)

        self.listmodel = MovementListModel(self.treemodel)

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
        self.treedisplay.setItemDelegate(Delegate())
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
        return super().eventFilter(source, event)

    def clearlist(self, button):
        numtoplevelitems = self.treemodel.invisibleRootItem().rowCount()
        for rownum in range(numtoplevelitems):
            self.treemodel.invisibleRootItem().child(rownum, 0).uncheck(force=True)

    # TODO KV - from location
    # def get_movement_value(self):
    #     movement_value_dict = {
    #         # 'start': self.start_location_group_layout.get_location_value(),
    #         # 'end': self.end_location_group_layout.get_location_value()
    #     }
    #
    #     return movement_value_dict

    # todo kv - from location
    # def clear(self, movement_specifications, app_ctx):
    #     pass
    #     # self.hand_switch.setChecked(True)
    #     # self.start_location_group_layout.clear(location_specifications, app_ctx)
    #     # self.end_location_group_layout.clear(location_specifications, app_ctx)

    # todo kv
    # def set_value(self, value):
    #     self.start_location_group_layout.set_value(value.start)
    #     self.end_location_group_layout.set_value(value.end)
#
# class RepSelectorWidget(QWidget):
#
#     def __init__(self, *args, **kwargs):
#         super(RepSelectorWidget, self).__init__(*args, **kwargs)
#
#         layout = QHBoxLayout()
#         self._label = QLabel("Number:")
#         layout.addWidget(self._label)
#
#         self._text = QLineEdit("")
#         layout.addWidget(self._text)
#
#         self.setLayout(layout)

#
# class RepEditor(QWidget):
#
#     def __init__(self, parent, *args, **kwargs):
#         super().__init__(parent, *args, **kwargs)
#
#         layout = QHBoxLayout(self)
#         self._label = QLabel("Number:")
#         layout.addWidget(self._label)
#
#         self._text = QLineEdit("enter #")
#         layout.addWidget(self._text)
#
#         self.setLayout(layout)
#
#     def text(self):
#         return self._text.text()
#
#     def setText(self, text):
#         self._text.setText(text)


class MovementSelectorDialog(QDialog):
    saved_movement = pyqtSignal(MovementTreeModel)

    def __init__(self, mainwindow, enable_addnew=False, moduletoload=None, **kwargs):
        super().__init__(**kwargs)
        self.mainwindow = mainwindow
        self.system_default_movement_specifications = mainwindow.system_default_movement

        self.movement_layout = MovementSpecificationLayout(moduletoload=moduletoload)

        main_layout = QVBoxLayout()
        main_layout.addLayout(self.movement_layout)

        separate_line = QFrame()
        separate_line.setFrameShape(QFrame.HLine)
        separate_line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separate_line)

        buttons = None
        applytext = ""
        if enable_addnew:
            buttons = QDialogButtonBox.RestoreDefaults | QDialogButtonBox.Save | QDialogButtonBox.Apply | QDialogButtonBox.Cancel
            applytext = "Save and close"
        else:
            buttons = QDialogButtonBox.RestoreDefaults | QDialogButtonBox.Apply | QDialogButtonBox.Cancel
            applytext = "Save"

        self.button_box = QDialogButtonBox(buttons, parent=self)
        if enable_addnew:
            self.button_box.button(QDialogButtonBox.Save).setText("Save and add another")
        self.button_box.button(QDialogButtonBox.Apply).setText(applytext)

    #     # TODO KV keep? from orig locationdefinerdialog: Ref: https://programtalk.com/vs2/python/654/enki/enki/core/workspace.py/
        self.button_box.clicked.connect(self.handle_button_click)

        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)
        self.setMinimumSize(QSize(500, 700))

    def handle_button_click(self, button):
        standard = self.button_box.standardButton(button)

        if standard == QDialogButtonBox.Cancel:
            self.reject()

        elif standard == QDialogButtonBox.Save:  # save and next
            # save info and then refresh screen to enter next movemement module
            self.saved_movement.emit(self.movement_layout.treemodel)
            self.movement_layout.clearlist(None)  # TODO KV should this use "restore defaults" instead?

        elif standard == QDialogButtonBox.Apply:  # save and close
            # save info and then close dialog
            self.saved_movement.emit(self.movement_layout.treemodel)
            self.accept()

    #     # elif standard == QDialogButtonBox.NoButton:
    #     #     action_role = button.property('ActionRole')
    #     #     if action_role == 'Export':
    #     #         file_name, file_type = QFileDialog.getSaveFileName(self,
    #     #                                                            self.tr('Export Locations'),
    #     #                                                            os.path.join(
    #     #                                                                self.app_settings['storage'][
    #     #                                                                    'recent_folder'],
    #     #                                                                'locations.json'),
    #     #                                                            self.tr('JSON Files (*.json)'))
    #     #
    #     #         if file_name:
    #     #             with open(file_name, 'w') as f:
    #     #                 json.dump(self.location_tab.get_locations().get_attr_dict(), f, sort_keys=True, indent=4)
    #     #
    #     #             QMessageBox.information(self, 'Locations Exported',
    #     #                                     'Locations have been successfully exported!')
    #     #     elif action_role == 'Import':
    #     #         file_name, file_type = QFileDialog.getOpenFileName(self, self.tr('Import Locations'),
    #     #                                                            self.app_settings['storage']['recent_folder'],
    #     #                                                            self.tr('JSON Corpus (*.json)'))
    #     #         if file_name:
    #     #             with open(file_name, 'r') as f:
    #     #                 location_json = json.load(f)
    #     #                 imported_locations = Locations(
    #     #                     {loc_id: LocationParameter(name=param['name'],
    #     #                                                image_path=param['image_path'],
    #     #                                                location_polygons=param['location_polygons'],
    #     #                                                default=param['default'])
    #     #                      for loc_id, param in location_json.items()}
    #     #                 )
    #     #                 self.location_tab.import_locations(imported_locations)
    #     #                 self.saved_locations.emit(self.location_tab.get_locations())

        # TODO KV - continue copying from class LocationDefinerDialog in location_definer
