import os
import json
from fractions import Fraction
from PyQt5.QtWidgets import (
    QFrame,
    QPushButton,
    QRadioButton,
    QDialog,
    QHBoxLayout,
    QVBoxLayout,
    QDialogButtonBox,
    QComboBox,
    QLabel,
    QCompleter,
    QButtonGroup,
    QAbstractItemView,
    QStyledItemDelegate,
    QStyle,
    QStyleOptionButton,
    QApplication,
    QHeaderView,
    QStyleOptionFrame,
    QErrorMessage,
    QCheckBox,
    QSpinBox,
    QSlider,
    QTabWidget,
    QWidget
)

from PyQt5.QtCore import (
    Qt,
    QSize,
    QEvent,
    pyqtSignal
)

from PyQt5.QtGui import (
    QPixmap,
    QColor,
    QPen,
    QBrush,
    QPolygonF,
    QTextOption,
    QFont
)

from gui.location_view import LocationTreeModel, LocationTree, LocationPathsProxyModel, TreeSearchComboBox, TreeListView, LocationGraphicsView, mutuallyexclusiverole, lastingrouprole, finalsubgrouprole, pathdisplayrole, delimiter
# from gui.xslot_graphics import XslotRectButton
# from gui.signtype_selector import SigntypeSelectorDialog
# from gui.handshape_selector import HandshapeSelectorDialog
# from lexicon.lexicon_classes import GlobalHandshapeInformation
from gui.module_selector import ModuleSpecificationLayout
# from gui.xslot_graphics import XslotLinkingLayout
from gui.module_selector import HandSelectionLayout


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
        currentpath = model.itemFromIndex(index).data(role=Qt.UserRole+pathdisplayrole)
        newpathlevels = currentpath.split(delimiter)
        newpathlevels[-1] = editor.text()
        model.itemFromIndex(index).setData(delimiter.join(newpathlevels), role=Qt.UserRole+pathdisplayrole)

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


class ImageDisplayTab(QWidget):
    def __init__(self, frontorback='front', **kwargs):
        super().__init__(**kwargs)

        main_layout = QHBoxLayout()

        # TODO KV graphics view!
        self.imagedisplay = LocationGraphicsView(frontorback)
        # self.imagedisplay.setMinimumWidth(400)

        self.zoom_slider = QSlider(Qt.Vertical)
        self.zoom_slider.setMinimum(1)
        self.zoom_slider.setMaximum(10)
        self.zoom_slider.setValue(0)
        self.zoom_slider.valueChanged.connect(self.zoom)

        main_layout.addWidget(self.imagedisplay)
        main_layout.addWidget(self.zoom_slider)

        self.setLayout(main_layout)

    def zoom(self, scale):
        trans_matrix = self.imagedisplay.transform()
        trans_matrix.reset()
        trans_matrix = trans_matrix.scale(scale * self.imagedisplay.factor, scale * self.imagedisplay.factor)
        self.imagedisplay.setTransform(trans_matrix)


# TODO KV - add undo, ...

# TODO KV there's another class with the same name in panel.py
class LocationSpecificationLayout(ModuleSpecificationLayout):
    saved_location = pyqtSignal(LocationTreeModel, dict, list)

    def __init__(self, app_settings, moduletoload=None, **kwargs):  # TODO KV , movement_specifications,
        super().__init__(**kwargs)

        self.treemodel = LocationTreeModel()  # movementparameters=movement_specifications)
        # if moduletoload is not None:
        #     self.treemodel = moduletoload
        # self.rootNode = self.treemodel.invisibleRootItem()
        if moduletoload:
            if isinstance(moduletoload, LocationTreeModel):
                self.treemodel = moduletoload
            # elif isinstance(moduletoload, MovementTree):
            #     # TODO KV - make sure listmodel & listitems are also populated
            #     self.treemodel = moduletoload.getMovementTreeModel()
            else:
                print("moduletoload must be of type LocationTreeModel")
        else:
            # self.treemodel.populate(self.rootNode)
            self.treemodel.populate(self.treemodel.invisibleRootItem())

        self.listmodel = self.treemodel.listmodel

        self.comboproxymodel = LocationPathsProxyModel(wantselected=False) #, parent=self.listmodel
        self.comboproxymodel.setSourceModel(self.listmodel)

        self.listproxymodel = LocationPathsProxyModel(wantselected=True)
        self.listproxymodel.setSourceModel(self.listmodel)

        locationtype_layout = QHBoxLayout()
        locationtype_layout.addWidget(QLabel("Location:"))

        self.bodyanchored_radio = QRadioButton("Body-anchored")
        self.bodyanchored_radio.setProperty('locationtype', 'bodyanchored')
        self.signingspace_radio = QRadioButton("Signing space")
        self.signingspace_radio.setProperty('locationtype', 'signingspace')
        self.locationtype_buttongroup = QButtonGroup()
        self.locationtype_buttongroup.addButton(self.bodyanchored_radio)
        self.locationtype_buttongroup.addButton(self.signingspace_radio)
        self.locationtype_buttongroup.buttonToggled.connect(lambda: self.handle_toggle_locationtype(self.locationtype_buttongroup.checkedButton()))
        locationtype_layout.addWidget(self.bodyanchored_radio)
        locationtype_layout.addWidget(self.signingspace_radio)
        locationtype_layout.addStretch()

        self.addLayout(locationtype_layout)

        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Enter tree node"))  # TODO KV delete? , self))

        self.combobox = TreeSearchComboBox(self)
        self.combobox.setModel(self.comboproxymodel)
        self.combobox.setCurrentIndex(-1)
        self.combobox.adjustSize()
        self.combobox.setEditable(True)
        self.combobox.setInsertPolicy(QComboBox.NoInsert)
        self.combobox.setFocusPolicy(Qt.StrongFocus)
        self.combobox.completer().setCaseSensitivity(Qt.CaseInsensitive)
        self.combobox.completer().setFilterMode(Qt.MatchContains)
        self.combobox.completer().setCompletionMode(QCompleter.PopupCompletion)
        # tct = TreeClickTracker(self)  todo kv
        # self.combobox.installEventFilter(tct)
        search_layout.addWidget(self.combobox)

        self.addLayout(search_layout)

        selection_layout = QHBoxLayout()

        self.imagetabs = QTabWidget()
        self.fronttab = ImageDisplayTab('front')
        self.imagetabs.addTab(self.fronttab, "Front")
        self.backtab = ImageDisplayTab('back')
        self.imagetabs.addTab(self.backtab, "Back")

        # self.treedisplay = MovementTreeView()
        # self.treedisplay.setItemDelegate(TreeItemDelegate())
        # self.treedisplay.setHeaderHidden(True)
        # self.treedisplay.setModel(self.treemodel)
        # # TODO KV figure out adding number selector
        # items = self.treemodel.findItems("Number of repetitions", Qt.MatchRecursive)
        # repsindex = self.treemodel.indexFromItem(items[0].child(0, 0))
        # self.treedisplay.openPersistentEditor(repsindex)
        # self.treedisplay.installEventFilter(self)
        # self.treedisplay.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        # self.treedisplay.setMinimumWidth(400)

        selection_layout.addWidget(self.imagetabs)

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

        if moduletoload is not None:
            pass
            # TODO KV implement for when we're loading an existing location module
        else:
            for btn in self.locationtype_buttongroup.buttons():
                if app_settings['location']['locationtype'] == btn.property('locationtype'):
                    btn.setChecked(True)
                    break

        self.enable_location_tools(self.locationtype_buttongroup.checkedButton() is not None)

    def enable_location_tools(self, enable):
        self.combobox.setEnabled(enable)
        self.pathslistview.setEnabled(enable)
        self.imagetabs.setEnabled(enable)

    def handle_toggle_locationtype(self, btn):
        self.enable_location_tools(btn is not None)

        if btn == self.bodyanchored_radio:
            # TODO KV set image and search tool to body-anchored content
            pass
        elif btn == self.signingspace_radio:
            # TODO KV set image and search tool to signing space content
            pass

    def get_savedmodule_signal(self):
        return self.saved_location

    def get_savedmodule_args(self):
        return (self.treemodel,)

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

    def refresh(self):
        self.refresh_treemodel()

    def clear(self):
        self.refresh_treemodel()

    def refresh_treemodel(self):
        self.treemodel = LocationTreeModel()  # movementparameters=movement_specifications)
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
