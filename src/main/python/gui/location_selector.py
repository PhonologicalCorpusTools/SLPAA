import os
import json
from copy import copy

from PyQt5.QtWidgets import (
    QFrame,
    QPushButton,
    QRadioButton,
    QHBoxLayout,
    QVBoxLayout,
    QComboBox,
    QLabel,
    QCompleter,
    QButtonGroup,
    QGroupBox,
    QAbstractItemView,
    QHeaderView,
    QCheckBox,
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

from gui.location_view import LocationTreeModel, LocationTreeSerializable, LocationTableView, LocationPathsProxyModel, TreeSearchComboBox, TreeListView, LocationGraphicsView, LocationTreeItem
from gui.module_selector import ModuleSpecificationLayout, AddedInfoContextMenu
from lexicon.module_classes import LocationModule, PhonLocations, LocationType


class ImageDisplayTab(QWidget):
    zoomfactor_changed = pyqtSignal(int)
    linkbutton_toggled = pyqtSignal(bool)

    def __init__(self, app_ctx, frontorback='front', **kwargs):
        super().__init__(**kwargs)

        main_layout = QHBoxLayout()

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
    saved_location = pyqtSignal(LocationTreeModel, PhonLocations, LocationType, dict, list, int)
    deleted_location = pyqtSignal()

    def __init__(self, mainwindow, moduletoload=None, **kwargs):
        super().__init__(**kwargs)

        self.mainwindow = mainwindow
        self.treemodel = LocationTreeModel()
        if moduletoload:
            if isinstance(moduletoload, LocationModule):
                self.treemodel = LocationTreeSerializable(moduletoload.locationtreemodel).getLocationTreeModel()
                self.locationtype = copy(self.treemodel.locationtype)
                self.lastlocationtypewithlist = LocationType()
                self.phonlocs = copy(moduletoload.phonlocs)
            # elif isinstance(moduletoload, MovementTree):
            #     # TODO KV - make sure listmodel & listitems are also populated
            #     self.treemodel = moduletoload.getMovementTreeModel()
            else:
                # we have to have the entire module (not just the tree) because of the Phonological Locations info
                print("moduletoload must be of type LocationModule")
        else:
            self.treemodel.populate(self.treemodel.invisibleRootItem())
            self.phonlocs = PhonLocations()
            self.locationtype = LocationType()
            self.lastlocationtypewithlist = LocationType()

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

        self.signingspacebody_radio = QRadioButton("body-anchored  /")
        self.signingspacebody_radio.setProperty('loctype', 'signingspace_body')
        signingspace_layout.addWidget(self.signingspacebody_radio)
        self.signingspacespatial_radio = QRadioButton("purely spatial  )")
        self.signingspacespatial_radio.setProperty('loctype', 'signingspace_spatial')
        signingspace_layout.addWidget(self.signingspacespatial_radio)
        signingspace_box = QGroupBox()
        signingspace_box.setLayout(signingspace_layout)
        loctype_phonloc_layout.addWidget(signingspace_box, alignment=Qt.AlignVCenter)
        loctype_phonloc_layout.addStretch()

        # self.loctype_maingroup = QButtonGroup()
        # self.loctype_maingroup.setExclusive(False)
        self.loctype_subgroup = QButtonGroup()
        self.loctype_subgroup.addButton(self.body_radio)
        self.loctype_subgroup.addButton(self.signingspace_radio)
        self.signingspace_subgroup = QButtonGroup()
        self.signingspace_subgroup.addButton(self.signingspacebody_radio)
        self.signingspace_subgroup.addButton(self.signingspacespatial_radio)
        # self.loctype_maingroup.addButton(self.body_radio)
        # self.loctype_maingroup.addButton(self.signingspace_radio)
        # self.loctype_maingroup.addButton(self.signingspacebody_radio)
        # self.loctype_maingroup.addButton(self.signingspacespatial_radio)
        # self.loctype_maingroup.buttonToggled.connect(lambda: self.handle_toggle_loctype(self.loctype_subgroup.checkedButton(), self.signingspace_subgroup.checkedButton()))
        self.loctype_subgroup.buttonToggled.connect(lambda btn, wastoggled: self.handle_toggle_locationtype(self.loctype_subgroup.checkedButton()))
        self.signingspace_subgroup.buttonToggled.connect(lambda btn, wastoggled: self.handle_toggle_signingspacetype(self.signingspace_subgroup.checkedButton()))
        # self.loctype_maingroup.buttonToggled.connect(lambda: self.handle_toggle_locationtyp)

        phonological_layout = QVBoxLayout()
        self.phonological_cb = QCheckBox("Phonological location")
        self.phonological_cb.toggled.connect(self.enable_majorminorphonological_cbs)
        phonological_layout.addWidget(self.phonological_cb)
        phonological_sublayout = QHBoxLayout()
        self.majorphonloc_cb = QCheckBox("Major")
        self.majorphonloc_cb.toggled.connect(self.check_phonologicalloc_cb)
        self.minorphonloc_cb = QCheckBox("Minor")
        self.minorphonloc_cb.toggled.connect(self.check_phonologicalloc_cb)
        phonological_sublayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        phonological_sublayout.addWidget(self.majorphonloc_cb)
        phonological_sublayout.addWidget(self.minorphonloc_cb)
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
        search_layout.addWidget(self.combobox)

        self.addLayout(search_layout)

        selection_layout = QHBoxLayout()

        self.imagetabs = QTabWidget()
        self.fronttab = ImageDisplayTab(self.mainwindow.app_ctx, 'front')
        self.fronttab.zoomfactor_changed.connect(self.handle_zoomfactor_changed)
        self.fronttab.linkbutton_toggled.connect(lambda ischecked: self.handle_linkbutton_toggled(ischecked, self.fronttab))
        self.imagetabs.addTab(self.fronttab, "Front")
        self.backtab = ImageDisplayTab(self.mainwindow.app_ctx, 'back')
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

        # set location type radio buttons as per saved module or global settings
        if moduletoload is not None:  # load from an existing module
            self.refresh_loctype()
        else:  # apply from global settings
            self.default_loctype()

        self.enablelocationtools(self.loctype_subgroup.checkedButton() == self.body_radio
                                 or self.signingspace_subgroup.checkedButton() is not None)

        self.refresh()

    def check_phonologicalloc_cb(self, checked):
        self.phonological_cb.setChecked(True)

    def enable_majorminorphonological_cbs(self, checked):
        self.majorphonloc_cb.setEnabled(checked)
        self.minorphonloc_cb.setEnabled(checked)

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

    def enablelocationtools(self, enable):
        self.combobox.setEnabled(enable)
        self.pathslistview.setEnabled(enable)
        self.detailstableview.setEnabled(enable)
        self.imagetabs.setEnabled(enable)

    def handle_toggle_signingspacetype(self, btn):
        previouslocationtype = copy(self.treemodel.locationtype)
        if previouslocationtype.usesbodylocations() or previouslocationtype.purelyspatial:
            self.lastlocationtypewithlist = previouslocationtype

        self.signingspace_radio.setChecked(btn is not None)
        # if not self.treemodel.locationtype.signingspace:
        #     self.treemodel.locationtype.signingspace = True
        # self.enable_location_tools(btn is not None)

        if btn == self.signingspacebody_radio:
            if not self.treemodel.locationtype.bodyanchored:
                self.treemodel.locationtype.bodyanchored = True
        elif btn == self.signingspacespatial_radio:
            if not self.treemodel.locationtype.purelyspatial:
                self.treemodel.locationtype.purelyspatial = True

        self.populate_enable_locationtools() #previouslocationtype)

    def handle_toggle_locationtype(self, btn):
        previouslocationtype = copy(self.treemodel.locationtype)
        if previouslocationtype.usesbodylocations() or previouslocationtype.purelyspatial:
            self.lastlocationtypewithlist = previouslocationtype

        for b in self.signingspace_subgroup.buttons():
            b.setEnabled(self.loctype_subgroup.checkedButton() == self.signingspace_radio)

        if btn == self.body_radio:
            if not self.treemodel.locationtype.body:
                self.treemodel.locationtype.body = True
        elif btn == self.signingspace_radio:
            if not self.treemodel.locationtype.signingspace:
                self.treemodel.locationtype.signingspace = True

        self.populate_enable_locationtools()  # previouslocationtype)

    def populate_enable_locationtools(self): #, previouslocationtype):
        newlocationtype = self.treemodel.locationtype
        if newlocationtype.locationoptions_changed(self.lastlocationtypewithlist):  # previouslocationtype):
            self.clear_treemodel()
        # set image and search tool to appropriate (either body or spatial) content
        self.enablelocationtools(newlocationtype.usesbodylocations() or newlocationtype.purelyspatial)

    def get_savedmodule_signal(self):
        return self.saved_location

    def get_deletedmodule_signal(self):
        return self.deleted_location

    def get_savedmodule_args(self):
        phonlocs = PhonLocations(
            phonologicalloc=self.phonological_cb.isChecked(),
            majorphonloc=self.majorphonloc_cb.isEnabled() and self.majorphonloc_cb.isChecked(),
            minorphonloc=self.minorphonloc_cb.isEnabled() and self.minorphonloc_cb.isChecked(),
            phoneticloc=self.phonetic_cb.isChecked()
        )
        locationtype = LocationType(
            body=self.body_radio.isChecked(),
            signingspace=self.signingspace_radio.isChecked(),
            bodyanchored=self.signingspacebody_radio.isEnabled() and self.signingspacebody_radio.isChecked(),
            purelyspatial=self.signingspacespatial_radio.isEnabled() and self.signingspacespatial_radio.isChecked()
        )
        self.treemodel.locationtype = locationtype

        return (self.treemodel, phonlocs, locationtype)

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
            # treeitem = listindex.model().itemFromIndex(listindex).treeitem
            # addedinfo = copy(treeitem.addedinfo)
            addedinfo = listindex.model().itemFromIndex(listindex).treeitem.addedinfo

            menu = AddedInfoContextMenu(addedinfo)
            menu.exec_(event.globalPos())

        return super().eventFilter(source, event)

    def refresh(self):
        # self.refresh_treemodel()
        self.refresh_phonlocs()
        self.refresh_loctype()

    def refresh_loctype(self):
        loctype = self.treemodel.locationtype
        self.body_radio.setChecked(loctype.body)
        self.signingspace_radio.setChecked(loctype.signingspace)
        self.signingspacebody_radio.setChecked(loctype.bodyanchored)
        self.signingspacespatial_radio.setChecked(loctype.purelyspatial)

    def refresh_phonlocs(self):
        self.majorphonloc_cb.setChecked(self.phonlocs.majorphonloc)
        self.minorphonloc_cb.setChecked(self.phonlocs.minorphonloc)
        self.phonological_cb.setChecked(self.phonlocs.phonologicalloc)
        self.phonetic_cb.setChecked(self.phonlocs.phoneticloc)
        if self.phonlocs.allfalse():
            self.majorphonloc_cb.setEnabled(True)
            self.minorphonloc_cb.setEnabled(True)

    def clear(self):
        self.clear_treemodel()
        self.clear_details()
        self.clear_loctype()
        self.clear_phonlocs()

    def clear_loctype(self):
        self.locationtype = LocationType()
        self.default_loctype()

    def default_loctype(self):
        self.loctype_subgroup.setExclusive(False)
        self.signingspace_subgroup.setExclusive(False)
        for btn in self.signingspace_subgroup.buttons() + self.loctype_subgroup.buttons():
            tempsetting = self.mainwindow.app_settings['location']['loctype']
            tempproperty = btn.property('loctype')
            # if self.mainwindow.app_settings['location']['loctype'] == btn.property('loctype'):
            #     btn.setChecked(True)
            #     break  # TODO KV why break??
            btn.setChecked(self.mainwindow.app_settings['location']['loctype'] == btn.property('loctype'))
        self.loctype_subgroup.setExclusive(True)
        self.signingspace_subgroup.setExclusive(True)
        if self.locationtype.allfalse():
            for btn in self.signingspace_subgroup.buttons():
                btn.setEnabled(True)

    def clear_phonlocs(self):
        self.phonlocs = PhonLocations()
        self.refresh_phonlocs()

    def clear_details(self):
        self.update_detailstable(None, None)

    def clear_treemodel(self):
        locationtype = copy(self.treemodel.locationtype)
        self.treemodel = LocationTreeModel()  # recreate from scratch
        self.treemodel.locationtype = locationtype  # give it the same location type it had before
        self.treemodel.populate(self.treemodel.invisibleRootItem())

        self.listmodel = self.treemodel.listmodel

        self.comboproxymodel.setSourceModel(self.listmodel)
        self.listproxymodel.setSourceModel(self.listmodel)
        self.combobox.setModel(self.comboproxymodel)
        self.combobox.setCurrentIndex(-1)
        self.pathslistview.setModel(self.listproxymodel)

        # self.combobox.clear()
        self.clear_details()

    def clearlist(self, button):
        numtoplevelitems = self.treemodel.invisibleRootItem().rowCount()
        for rownum in range(numtoplevelitems):
            self.treemodel.invisibleRootItem().child(rownum, 0).uncheck(force=True)

    def desiredwidth(self):
        return 500

    def desiredheight(self):
        return 700
