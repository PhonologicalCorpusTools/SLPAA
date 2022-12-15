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
    QGroupBox,
    QAbstractItemView,
    QStyledItemDelegate,
    QLineEdit,
    QStyle,
    QStyleOptionButton,
    QApplication,
    QHeaderView,
    QListView,
    QStyleOptionFrame,
    QErrorMessage,
    QCheckBox,
    QSpinBox,
    QSlider,
    QTabWidget,
    QWidget,
    QSpacerItem,
    QSizePolicy
)

from PyQt5.QtCore import (
    Qt,
    QSize,
    QEvent,
    pyqtSignal,
    QItemSelectionModel
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

from gui.location_view import LocationTreeModel, LocationTableModel, LocationTableView, LocationPathsProxyModel, TreeSearchComboBox, TreeListView, LocationGraphicsView, LocationTreeItem
from gui.module_selector import ModuleSpecificationLayout, AddedInfoContextMenu
# from gui.xslot_graphics import XslotLinkingLayout
from gui.module_selector import HandSelectionLayout
from lexicon.module_classes import delimiter, userdefinedroles as udr


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


class ImageDisplayTab(QWidget):
    zoomfactor_changed = pyqtSignal(int)
    linkbutton_toggled = pyqtSignal(bool)

    def __init__(self, app_ctx, frontorback='front', **kwargs):
        super().__init__(**kwargs)

        main_layout = QHBoxLayout()

        # TODO KV graphics view!
        self.imagedisplay = LocationGraphicsView(app_ctx, frontorback)
        # self.imagedisplay.setMinimumWidth(400)

        zoom_layout = QVBoxLayout()

        self.zoom_slider = QSlider(Qt.Vertical)
        self.zoom_slider.setMinimum(1)
        self.zoom_slider.setMaximum(10)
        self.zoom_slider.setValue(0)
        self.zoom_slider.valueChanged.connect(self.zoom)
        zoom_layout.addWidget(self.zoom_slider)
        zoom_layout.setAlignment(self.zoom_slider, Qt.AlignHCenter)

        self.link_button = QPushButton("Link")
        self.link_button.setCheckable(True)
        self.link_button.toggled.connect(lambda ischecked: self.linkbutton_toggled.emit(ischecked))
        zoom_layout.addWidget(self.link_button)
        zoom_layout.setAlignment(self.link_button, Qt.AlignHCenter)

        main_layout.addWidget(self.imagedisplay)
        main_layout.addLayout(zoom_layout)

        self.setLayout(main_layout)

    def zoom(self, scale):
        trans_matrix = self.imagedisplay.transform()
        trans_matrix.reset()
        trans_matrix = trans_matrix.scale(scale * self.imagedisplay.factor, scale * self.imagedisplay.factor)
        self.imagedisplay.setTransform(trans_matrix)

        self.zoomfactor_changed.emit(scale)

    def force_zoom(self, scale):
        self.blockSignals(True)
        self.zoom_slider.blockSignals(True)
        self.zoom(scale)
        self.zoom_slider.setValue(scale)
        self.blockSignals(False)
        self.zoom_slider.blockSignals(False)

    def force_link(self, ischecked):
        self.blockSignals(True)
        self.link_button.setChecked(ischecked)
        self.blockSignals(False)


# TODO KV - add undo, ...

# TODO KV there's another class with the same name in panel.py
class LocationSpecificationLayout(ModuleSpecificationLayout):
    saved_location = pyqtSignal(LocationTreeModel, bool, bool, dict, list, int)

    def __init__(self, mainwindow, moduletoload=None, **kwargs):  # TODO KV , movement_specifications,
        super().__init__(**kwargs)

        self.temptestactionstate = False
        self.checknoteactionstate = True
        self.checknoteactiontext = ""

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

        loctype_phonloc_layout = QHBoxLayout()

        loctype_phonloc_layout.addWidget(QLabel("Location:"), alignment=Qt.AlignVCenter)

        body_layout = QHBoxLayout()

        self.body_radio = QRadioButton("Body")
        self.body_radio.setProperty('loctype', 'body')
        body_layout.addWidget(self.body_radio)
        body_layout.addSpacerItem(QSpacerItem(150, 0))  # TODO KV , QSizePolicy.Minimum, QSizePolicy.Maximum))
        body_box = QGroupBox()
        body_box.setLayout(body_layout)
        loctype_phonloc_layout.addWidget(body_box, alignment=Qt.AlignVCenter)

        signingspace_layout = QHBoxLayout()

        self.signingspace_radio = QRadioButton("Signing space  (")
        self.signingspace_radio.setProperty('loctype', 'signingspace')
        # loctype_layout.addWidget(self.signingspace_radio)
        signingspace_layout.addWidget(self.signingspace_radio)

        self.signingspacebody_radio = QRadioButton('body-anchored  /')
        self.signingspacebody_radio.setProperty('loctype', 'signingspace_body')
        signingspace_layout.addWidget(self.signingspacebody_radio)
        self.signingspacespatial_radio = QRadioButton('purely spatial  )')
        self.signingspacespatial_radio.setProperty('loctype', 'signingspace_spatial')
        signingspace_layout.addWidget(self.signingspacespatial_radio)
        signingspace_box = QGroupBox()
        signingspace_box.setLayout(signingspace_layout)
        loctype_phonloc_layout.addWidget(signingspace_box, alignment=Qt.AlignVCenter)
        loctype_phonloc_layout.addStretch()

        self.loctype_group = QButtonGroup()
        self.loctype_group.addButton(self.body_radio)
        self.loctype_group.addButton(self.signingspace_radio)
        self.signingspace_group = QButtonGroup()
        self.signingspace_group.addButton(self.signingspacebody_radio)
        self.signingspace_group.addButton(self.signingspacespatial_radio)
        self.loctype_group.buttonToggled.connect(lambda: self.handle_toggle_locationtype(self.loctype_group.checkedButton()))
        self.signingspace_group.buttonToggled.connect(lambda: self.handle_toggle_signingspacetype(self.signingspace_group.checkedButton()))

        phonological_layout = QVBoxLayout()
        self.phonological_cb = QCheckBox("Phonological location")
        phonological_layout.addWidget(self.phonological_cb)
        # phonological_layout.addWidget(QLabel("Phonological location"))
        phonological_sublayout = QHBoxLayout()
        self.majorphonloc_cb = QCheckBox("Major")
        self.minorphonloc_cb = QCheckBox("Minor")
        # TODO KV these should only be active if phonological location checkbox is checked
        # phonological_sublayout.addStretch()ips
        # phonological_sublayout.addWidget(QLabel("["))
        phonological_sublayout.addWidget(self.majorphonloc_cb)  # , alignment=Qt.AlignVCenter)
        phonological_sublayout.addWidget(self.minorphonloc_cb)  # , alignment=Qt.AlignVCenter)
        # phonological_sublayout.addWidget(QLabel("]"))
        phonological_sublayout.addStretch()
        phonological_layout.addLayout(phonological_sublayout)

        phonetic_layout = QVBoxLayout()
        self.phonetic_cb = QCheckBox("Phonetic location")
        phonetic_layout.addWidget(self.phonetic_cb)
        phonetic_layout.addStretch()

        loctype_phonloc_layout.addLayout(phonological_layout)
        loctype_phonloc_layout.addLayout(phonetic_layout)
        loctype_phonloc_layout.addStretch()

        self.addLayout(loctype_phonloc_layout)

        # TODO KV - do something with major / minor location info

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
        self.combobox.item_selected.connect(self.selectlistitem)
        # tct = TreeClickTracker(self)  todo kv
        # self.combobox.installEventFilter(tct)
        search_layout.addWidget(self.combobox)

        self.addLayout(search_layout)

        selection_layout = QHBoxLayout()

        self.imagetabs = QTabWidget()
        self.fronttab = ImageDisplayTab(mainwindow.app_ctx, 'front')
        self.fronttab.zoomfactor_changed.connect(self.handle_zoomfactor_changed)
        self.fronttab.linkbutton_toggled.connect(lambda ischecked: self.handle_linkbutton_toggled(ischecked, self.fronttab))
        self.imagetabs.addTab(self.fronttab, "Front")
        self.backtab = ImageDisplayTab(mainwindow.app_ctx, 'back')
        self.backtab.zoomfactor_changed.connect(self.handle_zoomfactor_changed)
        self.backtab.linkbutton_toggled.connect(lambda ischecked: self.handle_linkbutton_toggled(ischecked, self.backtab))
        self.imagetabs.addTab(self.backtab, "Back")

        selection_layout.addWidget(self.imagetabs)

        list_layout = QVBoxLayout()

        self.pathslistview = TreeListView()
        self.pathslistview.setSelectionMode(QAbstractItemView.MultiSelection)
        self.pathslistview.setModel(self.listproxymodel)
        self.pathslistview.setMinimumWidth(300)
        self.pathslistview.installEventFilter(self)
        self.pathslistview.selectionModel().selectionChanged.connect(self.update_detailstable)

        list_layout.addWidget(self.pathslistview)

        buttons_layout = QHBoxLayout()

        sortlabel = QLabel("Sort by:")
        buttons_layout.addWidget(sortlabel)

        self.sortcombo = QComboBox()
        self.sortcombo.addItems(
            ["order in tree (default)", "alpha by full path", "alpha by lowest node", "order of selection"])
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

        self.detailstableview = LocationTableView()
        # TODO KV set model, checkboxes, etc

        list_layout.addWidget(self.detailstableview)

        selection_layout.addLayout(list_layout)
        self.addLayout(selection_layout)

        if moduletoload is not None:
            pass
            # TODO KV implement for when we're loading an existing location module
        else:
            for btn in self.loctype_group.buttons() + self.signingspace_group.buttons():
                if mainwindow.app_settings['location']['loctype'] == btn.property('loctype'):
                    btn.setChecked(True)
                    break

        self.enable_location_tools(self.loctype_group.checkedButton() == self.body_radio
                                   or self.signingspace_group.checkedButton() is not None)

    def selectlistitem(self, locationtreeitem):
        listmodelindex = self.listmodel.indexFromItem(locationtreeitem.listitem)
        listproxyindex = self.listproxymodel.mapFromSource(listmodelindex)
        self.pathslistview.selectionModel().select(listproxyindex, QItemSelectionModel.ClearAndSelect)

    def update_detailstable(self, selected, deselected):
        selectedindexes = self.pathslistview.selectionModel().selectedIndexes()
        if len(selectedindexes) == 1:  # the details pane reflects the (single) selection
            itemindex = selectedindexes[0]
            listitemindex = self.pathslistview.model().mapToSource(itemindex)
            selectedlistitem = self.pathslistview.model().sourceModel().itemFromIndex(listitemindex)
            self.detailstableview.setModel(selectedlistitem.treeitem.detailstable)
        else:  # 0 or >1 rows selected; the details pane is blank
            self.detailstableview.setModel(LocationTreeItem().detailstable)

        self.detailstableview.horizontalHeader().resizeSections(QHeaderView.Stretch)

    def handle_zoomfactor_changed(self, scale):
        if self.fronttab.link_button.isChecked() or self.backtab.link_button.isChecked():
            self.fronttab.force_zoom(scale)
            self.backtab.force_zoom(scale)

    def handle_linkbutton_toggled(self, ischecked, thistab):
        othertab = self.fronttab if thistab == self.backtab else self.backtab
        othertab.force_link(ischecked)
        othertab.force_zoom(thistab.zoom_slider.value())
        # self.backtab.force_link(ischecked)

    def enable_location_tools(self, enable):
        self.combobox.setEnabled(enable)
        self.pathslistview.setEnabled(enable)
        self.detailstableview.setEnabled(enable)
        self.imagetabs.setEnabled(enable)

    def handle_toggle_signingspacetype(self, btn):
        self.signingspace_radio.setChecked(btn is not None)
        self.enable_location_tools(btn is not None)

        if btn == self.signingspacebody_radio:
            # TODO KV set image and search tool to signing space (body-anchored) content
            if self.treemodel.locationtype != 'body':
                self.treemodel.locationtype = 'body'
                self.refresh_treemodel()
        elif btn == self.signingspacespatial_radio:
            # TODO KV set image and search tool to signing space (purely spatial) content
            if self.treemodel.locationtype != 'purelyspatial':
                self.treemodel.locationtype = 'purelyspatial'
                self.refresh_treemodel()

    def handle_toggle_locationtype(self, btn):
        for btn in self.signingspace_group.buttons():
            btn.setEnabled(self.loctype_group.checkedButton() == self.signingspace_radio)
        self.enable_location_tools(self.loctype_group.checkedButton() == self.body_radio)

        if btn == self.body_radio:
            # TODO KV set image and search tool to body-anchored content
            if self.treemodel.locationtype != 'body':
                self.treemodel.locationtype = 'body'
                self.refresh_treemodel()
        elif btn == self.signingspace_radio:
            # TODO KV leave image and search tool disabled
            pass

    def get_savedmodule_signal(self):
        return self.saved_location

    def get_savedmodule_args(self):
        return (self.treemodel, self.majorphonloc_cb.isChecked(), self.minorphonloc_cb.isChecked())

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
            proxyindex = self.pathslistview.currentIndex()
            listindex = proxyindex.model().mapToSource(proxyindex)
            addedinfo = listindex.model().itemFromIndex(listindex).treeitem.addedinfo

            menu = AddedInfoContextMenu(addedinfo)
            menu.exec_(event.globalPos())

        return super().eventFilter(source, event)

    def refresh(self):
        self.refresh_treemodel()

    def clear(self):
        self.refresh_treemodel()

    def refresh_treemodel(self):
        locationtype = self.treemodel.locationtype
        self.treemodel = LocationTreeModel()  # movementparameters=movement_specifications)
        self.treemodel.locationtype = locationtype
        self.treemodel.populate(self.treemodel.invisibleRootItem())

        self.listmodel = self.treemodel.listmodel

        self.comboproxymodel.setSourceModel(self.listmodel)
        self.listproxymodel.setSourceModel(self.listmodel)
        self.combobox.setModel(self.comboproxymodel)
        self.combobox.setCurrentIndex(-1)
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
