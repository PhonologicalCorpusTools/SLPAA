import io, re, random

from PyQt5.QtWidgets import (
    QListView,
    QTableView,
    QTreeView,
    QGraphicsView,
    QGraphicsScene,
    QPushButton,
    QRadioButton,
    QHBoxLayout,
    QVBoxLayout,
    QComboBox,
    QLabel,
    QCompleter,
    QButtonGroup,
    QGroupBox,
    QStackedWidget,
    QAbstractItemView,
    QHeaderView,
    QCheckBox,
    QSlider,
    QTabWidget,
    QWidget,
    QSpacerItem,
    QSizePolicy,
    QStyledItemDelegate,
    QStyleOptionButton,
    QStyle,
    QStyleOptionFrame,
    QApplication,
    QFrame,
    QScrollArea,
    QPlainTextEdit,
    QMenu,
    QAction
)

from PyQt5.QtSvg import QSvgRenderer, QGraphicsSvgItem

from PyQt5.QtCore import (
    Qt,
    QEvent,
    pyqtSignal,
    QItemSelectionModel,
    QPointF
)

from lexicon.module_classes import delimiter, LocationModule, PhonLocations, userdefinedroles as udr
from models.location_models import LocationTreeItem, LocationTableModel, LocationTreeModel, \
    LocationType, LocationPathsProxyModel
from serialization_classes import LocationTreeSerializable
from gui.modulespecification_widgets import AddedInfoContextMenu, ModuleSpecificationPanel


class LocationTreeView(QTreeView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked)


class LocnTreeSearchComboBox(QComboBox):
    item_selected = pyqtSignal(LocationTreeItem)

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
                itemstoselect = gettreeitemsinpath(self.parent().treemodel,
                                                   self.currentText(),
                                                   delim=delimiter)
                for item in itemstoselect:
                    if item.checkState() == Qt.Unchecked:
                        item.setCheckState(Qt.PartiallyChecked)
                itemstoselect[-1].setCheckState(Qt.Checked)
                self.item_selected.emit(itemstoselect[-1])
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
                    elif foundcurrententry and self.lasttextentry.lower() in completionoption.lower() \
                            and not completionoption.lower().startswith(self.lastcompletedentry.lower()):
                        foundnextentry = True
                        if delimiter in completionoption[len(self.lasttextentry):]:
                            self.setEditText(
                                completionoption[:completionoption.index(delimiter, len(self.lasttextentry)) + 1])
                        else:
                            self.setEditText(completionoption)
                        self.lastcompletedentry = self.currentText()
                    i += 1
            else:
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


class LocnTreeListView(QListView):

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


class LocationTableView(QTableView):
    def __init__(self, locationtreeitem=None, **kwargs):
        super().__init__(**kwargs)

        # set the table model
        locntablemodel = LocationTableModel(parent=self)
        self.setModel(locntablemodel)
        self.horizontalHeader().resizeSections(QHeaderView.Stretch)


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


class LocationOptionsSelectionPanel(QFrame):
    def __init__(self, treemodeltoload=None, displayvisualwidget=True, **kwargs):
        super().__init__(**kwargs)
        self.mainwindow = self.parent().mainwindow
        self.showimagetabs = displayvisualwidget

        main_layout = QVBoxLayout()

        self._treemodel = None
        self._listmodel = None
        self.treemodel = LocationTreeModel()
        if treemodeltoload is not None and isinstance(treemodeltoload, LocationTreeModel):
            self.treemodel = treemodeltoload

        # create list proxies (for search and for selected options list)
        # and set them to refer to list model for current location type
        self.comboproxymodel = LocationPathsProxyModel(wantselected=False)
        self.comboproxymodel.setSourceModel(self.listmodel)
        self.listproxymodel = LocationPathsProxyModel(wantselected=True)
        self.listproxymodel.setSourceModel(self.listmodel)

        # create layout with combobox for searching location items
        search_layout = self.create_search_layout()
        main_layout.addLayout(search_layout)

        # create layout with image-based selection widget (if applicable) and list view for selected location options
        selection_layout = self.create_selection_layout()
        main_layout.addLayout(selection_layout)

        self.setLayout(main_layout)

    def enableImageTabs(self, enable):
        if self.showimagetabs:
            self.imagetabwidget.setEnabled(enable)

    def clear_details(self):
        self.update_detailstable(None, None)

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

    @property
    def treemodel(self):
        return self._treemodel

    @treemodel.setter
    def treemodel(self, treemodel):
        # TODO KV - validate?
        self._treemodel = treemodel
        self._listmodel = treemodel.listmodel

    @property
    def listmodel(self):
        return self._listmodel

    @listmodel.setter
    def listmodel(self, listmodel):
        # TODO KV - validate?
        self._listmodel = listmodel

    def refresh_listproxies(self):

        self.comboproxymodel.setSourceModel(self.listmodel)
        self.listproxymodel.setSourceModel(self.listmodel)
        self.combobox.setModel(self.comboproxymodel)
        self.combobox.setCurrentIndex(-1)
        self.pathslistview.setModel(self.listproxymodel)

    def create_search_layout(self):
        search_layout = QHBoxLayout()

        search_layout.addWidget(QLabel("Enter tree node"))

        self.combobox = LocnTreeSearchComboBox(parent=self)
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

        return search_layout

    def selectlistitem(self, locationtreeitem):
        listmodelindex = self.listmodel.indexFromItem(locationtreeitem.listitem)
        listproxyindex = self.listproxymodel.mapFromSource(listmodelindex)
        self.pathslistview.selectionModel().select(listproxyindex, QItemSelectionModel.ClearAndSelect)

    def create_selection_layout(self):
        selection_layout = QHBoxLayout()

        if self.showimagetabs:
            self.imagetabwidget = ImageTabWidget(treemodel=self.treemodel, parent=self)
            selection_layout.addWidget(self.imagetabwidget)

        list_layout = self.create_list_layout()
        selection_layout.addLayout(list_layout)

        return selection_layout

    def update_detailstable(self, selected=None, deselected=None):
        selectedindexes = self.pathslistview.selectionModel().selectedIndexes()
        if len(selectedindexes) == 1:  # the details pane reflects the (single) selection
            itemindex = selectedindexes[0]
            listitemindex = self.pathslistview.model().mapToSource(itemindex)
            selectedlistitem = self.pathslistview.model().sourceModel().itemFromIndex(listitemindex)
            self.detailstableview.setModel(selectedlistitem.treeitem.detailstable)
        else:  # 0 or >1 rows selected; the details pane is blank
            self.detailstableview.setModel(LocationTreeItem().detailstable)

        self.detailstableview.horizontalHeader().resizeSections(QHeaderView.Stretch)

    def create_list_layout(self):

        list_layout = QVBoxLayout()

        self.pathslistview = LocnTreeListView()
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

        return list_layout

    def clearlist(self, button):
        numtoplevelitems = self.treemodel.invisibleRootItem().rowCount()
        for rownum in range(numtoplevelitems):
            self.treemodel.invisibleRootItem().child(rownum, 0).uncheck(force=True)

    def sort(self):
        self.listproxymodel.updatesorttype(self.sortcombo.currentText())
        
    
    def reset_sort(self):
        """Reset sort option to default."""
        self.sortcombo.setCurrentIndex(0)
        self.sort()


class LocationSpecificationPanel(ModuleSpecificationPanel):
    # see_relations = pyqtSignal()

    def __init__(self, moduletoload=None, showimagetabs=True, **kwargs):
        super().__init__(**kwargs)
        self.showimagetabs = showimagetabs

        main_layout = QVBoxLayout()

        # This widget has three separate location trees, so that we can flip back and forth between
        # location types without losing intermediate information. However, once the save button is
        # clicked only the tree for the current location type is saved with the module.
        self.treemodel_body = None
        self.treemodel_spatial = None
        self.listmodel_body = None
        self.listmodel_spatial = None
        self.recreate_treeandlistmodels()

        loctypetoload = None
        phonlocstoload = None
        treemodeltoload = None

        if moduletoload is not None and isinstance(moduletoload, LocationModule):
            self.existingkey = moduletoload.uniqueid
            loctypetoload = moduletoload.locationtreemodel.locationtype
            phonlocstoload = moduletoload.phonlocs
            # make a copy, so that the module is not being edited directly via this layout
            # (otherwise "cancel" doesn't actually revert to the original contents)
            treemodeltoload = LocationTreeModel(LocationTreeSerializable(moduletoload.locationtreemodel))

        # create layout with buttons for location type (body, signing space, etc)
        # and for phonological locations (phonological, phonetic, etc)
        loctype_phonloc_layout = self.create_loctype_phonloc_layout()
        main_layout.addLayout(loctype_phonloc_layout)

        # create panel containing search box, visual location selection (if applicable), list of selected options, and details table
        self.locationoptionsselectionpanel = LocationOptionsSelectionPanel(treemodeltoload=treemodeltoload, displayvisualwidget=showimagetabs, parent=self)
        main_layout.addWidget(self.locationoptionsselectionpanel)

        # set buttons and treemodel according to the existing module being loaded (if applicable)
        if moduletoload is not None and isinstance(moduletoload, LocationModule):
            self.set_loctype_buttons_from_content(loctypetoload)
            self.set_phonloc_buttons_from_content(phonlocstoload)
            self.setcurrenttreemodel(treemodeltoload)
        else:
            self.clear_loctype_buttons_to_default()

        separate_line = QFrame()
        separate_line.setFrameShape(QFrame.HLine)
        separate_line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separate_line)

        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        self.enablelocationtools()

    def getcurrentlocationtype(self):
        locationtype = LocationType(
            body=self.body_radio.isChecked(),
            signingspace=self.signingspace_radio.isChecked(),
            bodyanchored=self.signingspacebody_radio.isEnabled() and self.signingspacebody_radio.isChecked(),
            purelyspatial=self.signingspacespatial_radio.isEnabled() and self.signingspacespatial_radio.isChecked()
        )
        return locationtype

    def getcurrentphonlocs(self):
        phonlocs = PhonLocations(
            phonologicalloc=self.phonological_cb.isChecked(),
            majorphonloc=self.majorphonloc_cb.isEnabled() and self.majorphonloc_cb.isChecked(),
            minorphonloc=self.minorphonloc_cb.isEnabled() and self.minorphonloc_cb.isChecked(),
            phoneticloc=self.phonetic_cb.isChecked()
        )
        return phonlocs

    def create_loctype_phonloc_layout(self):
        loctype_phonloc_layout = QHBoxLayout()

        loctype_phonloc_layout.addWidget(QLabel("Location:"), alignment=Qt.AlignVCenter)

        body_layout = QHBoxLayout()
        self.body_radio = QRadioButton("Body")
        self.body_radio.setProperty('loctype', 'body')
        body_layout.addWidget(self.body_radio)
        body_layout.addSpacerItem(QSpacerItem(60, 0))  # TODO KV , QSizePolicy.Minimum, QSizePolicy.Maximum))
        body_box = QGroupBox()
        body_box.setLayout(body_layout)
        loctype_phonloc_layout.addWidget(body_box, alignment=Qt.AlignVCenter)

        signingspace_layout = QHBoxLayout()

        self.signingspace_radio = QRadioButton("Signing space  (")
        self.signingspace_radio.setProperty('loctype', 'signingspace')
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

        self.loctype_subgroup = QButtonGroup()
        self.loctype_subgroup.addButton(self.body_radio)
        self.loctype_subgroup.addButton(self.signingspace_radio)
        self.signingspace_subgroup = QButtonGroup()
        self.signingspace_subgroup.addButton(self.signingspacebody_radio)
        self.signingspace_subgroup.addButton(self.signingspacespatial_radio)
        self.loctype_subgroup.buttonToggled.connect(lambda btn, wastoggled:
                                                    self.handle_toggle_locationtype(self.loctype_subgroup.checkedButton()))
        self.signingspace_subgroup.buttonToggled.connect(lambda btn, wastoggled:
                                                         self.handle_toggle_signingspacetype(self.signingspace_subgroup.checkedButton()))

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

        return loctype_phonloc_layout

    def getcurrenttreemodel(self):
        if self.getcurrentlocationtype().usesbodylocations():
            # distinguish between body and body_anchored
            self.treemodel_body.locationtype = self.getcurrentlocationtype()
            return self.treemodel_body
        elif self.getcurrentlocationtype().purelyspatial:
            return self.treemodel_spatial
        elif self.getcurrentlocationtype().signingspace:
            treemodel = LocationTreeModel()
            treemodel.locationtype = self.getcurrentlocationtype()
            return treemodel
        else:
            return LocationTreeModel()

    def getcurrentlistmodel(self):
        if self.getcurrentlocationtype().usesbodylocations():
            return self.listmodel_body
        elif self.getcurrentlocationtype().purelyspatial:
            return self.listmodel_spatial
        elif self.getcurrentlocationtype().signingspace:
            treemodel = LocationTreeModel()
            treemodel.locationtype = self.getcurrentlocationtype()
            return treemodel.listmodel
        else:
            return LocationTreeModel().listmodel

    def setcurrenttreemodel(self, tm):
        if self.getcurrentlocationtype().usesbodylocations():
            self.treemodel_body = tm
        elif self.getcurrentlocationtype().purelyspatial:
            self.treemodel_spatial = tm

        self.setcurrentlistmodel(self.getcurrenttreemodel().listmodel)

    def setcurrentlistmodel(self, lm):
        if self.getcurrentlocationtype().usesbodylocations():
            self.listmodel_body = lm
        elif self.getcurrentlocationtype().purelyspatial:
            self.listmodel_spatial = lm

    def check_phonologicalloc_cb(self, checked):
        self.phonological_cb.setChecked(True)

    def enable_majorminorphonological_cbs(self, checked):
        self.majorphonloc_cb.setEnabled(checked)
        self.minorphonloc_cb.setEnabled(checked)

    def selectlistitem(self, locationtreeitem):
        listmodelindex = self.getcurrentlistmodel().indexFromItem(locationtreeitem.listitem)
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

    def handle_toggle_signingspacetype(self, btn):
        if btn is not None and btn.isChecked():
            self.signingspace_radio.setChecked(True)
        self.enablelocationtools()  # TODO KV should this be inside the if?

    def handle_toggle_locationtype(self, btn):
        if btn is not None and btn.isChecked():
            for b in self.signingspace_subgroup.buttons():
                b.setEnabled(btn == self.signingspace_radio)
        self.enablelocationtools()  # TODO KV should this be inside the if?

    def enablelocationtools(self):
        # self.refresh_listproxies()
        self.locationoptionsselectionpanel.treemodel = self.getcurrenttreemodel()
        self.locationoptionsselectionpanel.refresh_listproxies()
        # use current locationtype (from buttons) to determine whether/how things get enabled
        anyexceptpurelyspatial = self.getcurrentlocationtype().usesbodylocations() or self.getcurrentlocationtype().purelyspatial
        enableimagetabs = anyexceptpurelyspatial
        enablecomboboxandlistview = anyexceptpurelyspatial
        enabledetailstable = self.getcurrentlocationtype().usesbodylocations()

        # self.locationoptionsselectionpanel.locationselectionwidget.setlocationtype(self.getcurrentlocationtype(), treemodel=self.getcurrenttreemodel())
        self.locationoptionsselectionpanel.enableImageTabs(enableimagetabs)
        self.locationoptionsselectionpanel.combobox.setEnabled(enablecomboboxandlistview)
        self.locationoptionsselectionpanel.pathslistview.setEnabled(enablecomboboxandlistview)
        self.locationoptionsselectionpanel.update_detailstable(None, None)
        self.locationoptionsselectionpanel.detailstableview.setEnabled(enabledetailstable)

    def getsavedmodule(self, articulators, timingintervals, addedinfo, inphase):
        phonlocs = self.getcurrentphonlocs()
        locmod = LocationModule(self.getcurrenttreemodel(),
                                articulators=articulators,
                                timingintervals=timingintervals,
                                addedinfo=addedinfo,
                                phonlocs=phonlocs,
                                inphase=inphase)
        if self.existingkey is not None:
            locmod.uniqueid = self.existingkey
        else:
            self.existingkey = locmod.uniqueid
        return locmod

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

    def set_phonloc_buttons_from_content(self, phonlocs):
        self.clear_phonlocs_buttons()
        self.majorphonloc_cb.setChecked(phonlocs.majorphonloc)
        self.minorphonloc_cb.setChecked(phonlocs.minorphonloc)
        self.phonological_cb.setChecked(phonlocs.phonologicalloc)
        self.phonetic_cb.setChecked(phonlocs.phoneticloc)

    def clear_phonlocs_buttons(self):
        self.majorphonloc_cb.setChecked(False)
        self.minorphonloc_cb.setChecked(False)
        self.phonological_cb.setChecked(False)
        self.phonetic_cb.setChecked(False)
        self.majorphonloc_cb.setEnabled(True)
        self.minorphonloc_cb.setEnabled(True)

    def clear(self):
        """Restore GUI to the defaults."""
        self.clear_loctype_buttons_to_default()
        self.clear_phonlocs_buttons()
        self.recreate_treeandlistmodels()
        
        # Reset selections
        self.locationoptionsselectionpanel.treemodel = self.getcurrenttreemodel()
        self.locationoptionsselectionpanel.refresh_listproxies()
        self.locationoptionsselectionpanel.clear_details()
        
        # Reset sort
        self.locationoptionsselectionpanel.reset_sort()
        
        # Reset zoom and link
        self.locationoptionsselectionpanel.imagetabwidget.reset_zoomfactor()
        self.locationoptionsselectionpanel.imagetabwidget.reset_link()
        
        # Reset view to front panel
        self.locationoptionsselectionpanel.imagetabwidget.setCurrentIndex(0)

        # Update panels given default selections/disables panels
        self.enablelocationtools()


    def recreate_treeandlistmodels(self):
        self.treemodel_body = LocationTreeModel()
        self.treemodel_body.locationtype = LocationType(body=True)
        self.treemodel_body.populate(self.treemodel_body.invisibleRootItem())
        self.treemodel_spatial = LocationTreeModel()
        self.treemodel_spatial.locationtype = LocationType(signingspace=True, purelyspatial=True)
        self.treemodel_spatial.populate(self.treemodel_spatial.invisibleRootItem())

        self.listmodel_body = self.treemodel_body.listmodel
        self.listmodel_spatial = self.treemodel_spatial.listmodel

    def clear_loctype_buttons_to_default(self):
        defaultloctype = LocationType()
        loctype_setting = self.mainwindow.app_settings['location']['loctype']
        if loctype_setting == 'body':
            defaultloctype.body = True
        elif loctype_setting.startswith('signingspace'):
            defaultloctype.signingspace = True
            if loctype_setting == 'signingspace_spatial':
                defaultloctype.purelyspatial = True
            elif loctype_setting == 'signingspace_body':
                defaultloctype.bodyanchored = True
        self.set_loctype_buttons_from_content(defaultloctype)

    def set_loctype_buttons_from_content(self, loctype):

        self.loctype_subgroup.blockSignals(True)
        self.signingspace_subgroup.blockSignals(True)
        self.loctype_subgroup.setExclusive(False)
        self.signingspace_subgroup.setExclusive(False)

        for btn in self.loctype_subgroup.buttons() + self.signingspace_subgroup.buttons():
            btn.setChecked(False)

        if loctype.body:
            self.body_radio.setChecked(True)
        elif loctype.signingspace:
            self.signingspace_radio.setChecked(True)
            if loctype.purelyspatial:
                self.signingspacespatial_radio.setChecked(True)
            elif loctype.bodyanchored:
                self.signingspacebody_radio.setChecked(True)

        for btn in self.signingspace_subgroup.buttons():
            btn.setEnabled(not loctype.body)

        self.loctype_subgroup.setExclusive(True)
        self.signingspace_subgroup.setExclusive(True)
        self.loctype_subgroup.blockSignals(False)
        self.signingspace_subgroup.blockSignals(False)

    def clearlist(self, button):
        numtoplevelitems = self.getcurrenttreemodel().invisibleRootItem().rowCount()
        for rownum in range(numtoplevelitems):
            self.getcurrenttreemodel().invisibleRootItem().child(rownum, 0).uncheck(force=True)

    def desiredwidth(self):
        return 500

    def desiredheight(self):
        return 700


class ImageTabWidget(QTabWidget):

    def __init__(self, treemodel, **kwargs):
        super().__init__(**kwargs)
        self.mainwindow = self.parent().mainwindow

        self.fronttab = SVGDisplayTab(self.mainwindow.app_ctx, 'front')
        self.fronttab.zoomfactor_changed.connect(self.handle_zoomfactor_changed)
        self.fronttab.linkbutton_toggled.connect(lambda ischecked:
                                                 self.handle_linkbutton_toggled(ischecked, self.fronttab))
        self.addTab(self.fronttab, "Front")
        self.backtab = SVGDisplayTab(self.mainwindow.app_ctx, 'back')
        self.backtab.zoomfactor_changed.connect(self.handle_zoomfactor_changed)
        self.backtab.linkbutton_toggled.connect(lambda ischecked:
                                                self.handle_linkbutton_toggled(ischecked, self.backtab))
        self.addTab(self.backtab, "Back")
        self.sidetab = SVGDisplayTab(self.mainwindow.app_ctx, 'side')
        self.sidetab.zoomfactor_changed.connect(self.handle_zoomfactor_changed)
        self.sidetab.linkbutton_toggled.connect(lambda ischecked:
                                                self.handle_linkbutton_toggled(ischecked, self.sidetab))
        self.addTab(self.sidetab, "Side")

        self.alltabs = [self.fronttab, self.backtab, self.sidetab]

    def handle_zoomfactor_changed(self, scale):
        if True in [tab.link_button.isChecked() for tab in self.alltabs]:
            for tab in self.alltabs:
                tab.force_zoom(scale)

    def handle_linkbutton_toggled(self, ischecked, thistab):
        othertabs = [tab for tab in self.alltabs if tab != thistab]
        for othertab in othertabs:
            othertab.force_link(ischecked)
            othertab.force_zoom(thistab.zoom_slider.value())

    def reset_zoomfactor(self):
        """Reset the zoom factor for this image display to zero zoom, and back to the front tab."""
        for tab in self.alltabs:
            tab.zoom_slider.setValue(0)
            tab.force_zoom(tab.zoom_slider.value())

    def reset_link(self):
        """Unlink zoom buttons between front/back/side."""
        for tab in self.alltabs:
            self.handle_linkbutton_toggled(False, tab)


class LocationAction(QAction):

    # hand_matrix = {
    #     "R": {
    #         "contra": "L",
    #         "ipsi": "R"
    #     },
    #     "L": {
    #         "contra": "R",
    #         "ipsi": "L"
    #     }
    # }

    def __init__(self, elid, svgscrollarea, app_ctx, **kwargs):
        self.app_ctx = app_ctx
        self.dominantside = self.app_ctx.main_window.current_sign.signlevel_information.handdominance
        self.absoluteside = "R" if "Right" in elid else ("L" if "Left" in elid else "")
        self.name = self.app_ctx.predefined_locations_description_byfilename[elid].replace(self.app_ctx.contraoripsi, self.get_relativehand())
        super().__init__(self.name, **kwargs)
        self.svgscrollarea = svgscrollarea
        self.triggered.connect(self.getnewimage)

    def get_relativehand(self):
        return "ipsi" if self.dominantside == self.absoluteside else "contra"

    def getnewimage(self):
        selectedside = self.absoluteside or self.app_ctx.both
        name = self.name.replace(" - contra", "").replace(" - ipsi", "")
        self.svgscrollarea.handle_image_changed(self.app_ctx.predefined_locations_yellow[name][selectedside][self.app_ctx.nodiv])


class SVGDisplayTab(QWidget):
    zoomfactor_changed = pyqtSignal(int)
    linkbutton_toggled = pyqtSignal(bool)

    def __init__(self, app_ctx, frontbackside='front', specificpath="", **kwargs):
        super().__init__(**kwargs)
        self.app_ctx = app_ctx
        if specificpath != "":
            imagepath = specificpath
        else:
            imagepath = app_ctx.temp_test_images['sample_' + frontbackside]

        main_layout = QHBoxLayout()
        img_layout = QVBoxLayout()

        self.imgscroll = SVGDisplayScroll(imagepath, app_ctx)
        self.imgscroll.zoomfactor_changed.connect(lambda scale: self.zoomfactor_changed.emit(scale))
        # main_layout.addWidget(self.imgscroll)
        img_layout.addWidget(self.imgscroll)
        # self.bodypart_note = QPlainTextEdit("last clicked: n/a")
        # self.bodypart_note.setMaximumHeight(90)
        # img_layout.addWidget(self.bodypart_note)
        # self.imgscroll.img_clicked.connect(lambda listofids: self.bodypart_note.setPlainText("last clicked: " + " / ".join(listofids)))
        self.imgscroll.img_clicked.connect(self.handle_img_clicked)
        main_layout.addLayout(img_layout)

        zoom_layout = QVBoxLayout()
        self.zoom_slider = QSlider(Qt.Vertical, parent=self)
        self.zoom_slider.setMinimum(1)
        self.zoom_slider.setMaximum(9)
        self.zoom_slider.setValue(0)
        self.zoom_slider.valueChanged.connect(self.imgscroll.zoom)
        self.imgscroll.zoom(1)
        zoom_layout.addWidget(self.zoom_slider)
        zoom_layout.setAlignment(self.zoom_slider, Qt.AlignHCenter)

        self.link_button = QPushButton("Link")
        self.link_button.setCheckable(True)
        self.link_button.toggled.connect(lambda ischecked: self.linkbutton_toggled.emit(ischecked))
        zoom_layout.addWidget(self.link_button)
        zoom_layout.setAlignment(self.link_button, Qt.AlignHCenter)

        main_layout.addLayout(zoom_layout)
        self.setLayout(main_layout)

        self.setMinimumHeight(400)

    def handle_img_clicked(self, clickpoint, listofids, mousebutton):
        listofids = list(set(listofids))
        print("IDs at click " + str(len(listofids)) + ":", listofids)
        # self.bodypart_note.setPlainText("last clicked: " + ", ".join(listofids))
        if mousebutton == Qt.RightButton:
            print("right button released at", clickpoint.toPoint())
            # elementid_actions = [QAction(elid) for elid in listofids]
            # elementnames = [self.app_ctx.predefined_locations_description_byfilename[elid] for elid in listofids if elid in self.app_ctx.predefined_locations_description_byfilename.keys()]
            # elementname_actions = [LocationAction(elementname, self.imgscroll, self.app_ctx) for elementname in elementnames]
            elementname_actions = [LocationAction(elid, self.imgscroll, self.app_ctx) for elid in listofids if elid in self.app_ctx.predefined_locations_description_byfilename.keys()]
            elementids_menu = QMenu()
            elementids_menu.addActions(elementname_actions)
            print("about to create menu at", clickpoint)
            elementids_menu.exec_(clickpoint.toPoint())
        elif mousebutton == Qt.LeftButton:
            print("left button released at", clickpoint.toPoint())
        # elif mousebutton == Qt.MiddleButton:
        #     print("middle button released at", clickpoint.toPoint())

    def force_zoom(self, scale):
        self.blockSignals(True)
        self.zoom_slider.blockSignals(True)
        self.imgscroll.zoom(scale)
        self.zoom_slider.setValue(scale)
        self.blockSignals(False)
        self.zoom_slider.blockSignals(False)

    def force_link(self, ischecked):
        self.blockSignals(True)
        self.link_button.setChecked(ischecked)
        self.blockSignals(False)


class SVGDisplayScroll(QScrollArea):
    img_clicked = pyqtSignal(QPointF, list, int)
    zoomfactor_changed = pyqtSignal(int)
    factor_from_scale = {
        1: 0.20,
        2: 0.25,
        3: 0.33,
        4: 0.50,
        5: 1.0,
        6: 2.0,
        7: 3.0,
        8: 4.0,
        9: 5.0
    }

    def __init__(self, imagepath, app_ctx, **kwargs):
        super().__init__(**kwargs)

        main_layout = QHBoxLayout()

        self.img_layout = QHBoxLayout()

        self.renderer = QSvgRenderer(imagepath, parent=self)
        self.elementids = []
        self.gatherelementids(imagepath)
        self.scn = SVGGraphicsScene([], app_ctx, parent=self)
        self.scn.img_clicked.connect(lambda clickpoint, listofids, mousebutton: self.img_clicked.emit(clickpoint, listofids, mousebutton))
        self.scn.img_changed.connect(self.handle_image_changed)

        self.initializeSVGitems()

        self.vw = QGraphicsView(self.scn)
        self.img_layout.addWidget(self.vw)
        main_layout.addLayout(self.img_layout)
        self.setLayout(main_layout)

    def handle_image_changed(self, newimagepath):
        self.scn.clear()
        self.renderer.load(newimagepath)
        self.elementids = []
        self.gatherelementids(newimagepath)
        self.initializeSVGitems()

    def gatherelementids(self, svgfilepath):
        elementids = []
        with io.open(svgfilepath, "r") as svgfile:
            for ln in svgfile:
                idmatches = re.match('.*id="(.*?)".*', ln)
                if idmatches:
                    elementids.append(idmatches.group(1))
        self.elementids = elementids

    def initializeSVGitems(self):
        # for elementid in ["WHOLE_ARM", "WHOLE_ARM-2", "WHOLE_ARM-3", "WHOLE_ARM-4", "LOWER_TORSO-2", "UPPER_TORSO", "UPPER_TORSO-2", "UPPER_TORSO-3", "UPPER_TORSO-4", "UPPER_TORSO-5", "UPPER_TORSO-6", "UPPER_TORSO-7", "UPPER_TORSO-8", "SHOULDER", "SHOULDER-2"]:
        for elementid in self.elementids:
            if self.renderer.elementExists(elementid):
                elementx = self.renderer.boundsOnElement(elementid).x()
                elementy = self.renderer.boundsOnElement(elementid).y()
                currentsvgitem = QGraphicsSvgItem()
                currentsvgitem.setSharedRenderer(self.renderer)
                currentsvgitem.setElementId(elementid)
                currentsvgitem.setPos(elementx, elementy)
                self.scn.addItem(currentsvgitem)
        allsvgitem = QGraphicsSvgItem()
        allsvgitem.setSharedRenderer(self.renderer)
        allsvgitem.setElementId("")
        self.scn.addItem(allsvgitem)

    def zoom(self, scale):
        factor = self.factor_from_scale[scale]

        trans_matrix = self.vw.transform()
        trans_matrix.reset()
        trans_matrix = trans_matrix.scale(factor, factor)
        self.vw.setTransform(trans_matrix)

        self.zoomfactor_changed.emit(scale)


class SVGGraphicsScene(QGraphicsScene):
    img_clicked = pyqtSignal(QPointF, list, int)
    img_changed = pyqtSignal(str)

    def __init__(self, svgitems, app_ctx, **kwargs):
        super().__init__(**kwargs)
        self.app_ctx = app_ctx
        for it in svgitems:
            self.addItem(it)

    def mouseReleaseEvent(self, event):
        # print("mouse release in svg graphics scene")
        # print("     pos():", event.pos().x(), event.pos().y())
        # print("     scenePos():", event.scenePos().x(), event.scenePos().y())
        # print("     itemsBoundingRect():", self.itemsBoundingRect().x(), self.itemsBoundingRect().y(), self.itemsBoundingRect().width(), self.itemsBoundingRect().height())
        mousebutton = event.button()
        scenepoint = QPointF(event.scenePos().x(), event.scenePos().y())
        screenpoint = QPointF(event.screenPos().x(), event.screenPos().y())
        items = self.items(scenepoint)
        clickedids = [it.elementId() for it in items if it.elementId() != ""]
        # possible_ids_for_image = [clicked_id for clicked_id in clickedids if clicked_id in self.app_ctx.predefined_locations_test.keys()]
        # random_id = possible_ids_for_image[random.randrange(0, len(possible_ids_for_image))]
        # random_image = self.app_ctx.predefined_locations_test[random_id]
        # self.img_changed.emit(random_image)
        # print("randomly chose sub-image:", random_id)
        # allids = [it.elementId() for it in self.items()]
        # # print("all IDs (" + str(len(allids)) + "):", allids)
        self.img_clicked.emit(screenpoint, clickedids, mousebutton)


# # Ref: https://stackoverflow.com/questions/48575298/pyqt-qtreewidget-how-to-add-radiobutton-for-items
# # TODO KV can this be combined with the one for movement?
# class LocationTreeItemDelegate(QStyledItemDelegate):
#
#     def paint(self, painter, option, index):
#         if index.data(Qt.UserRole+udr.mutuallyexclusiverole):
#             widget = option.widget
#             style = widget.style() if widget else QApplication.style()
#             opt = QStyleOptionButton()
#             opt.rect = option.rect
#             opt.text = index.data()
#             opt.state |= QStyle.State_On if index.data(Qt.CheckStateRole) else QStyle.State_Off
#             style.drawControl(QStyle.CE_RadioButton, opt, painter, widget)
#             if index.data(Qt.UserRole+udr.lastingrouprole) and not index.data(Qt.UserRole+udr.finalsubgrouprole):
#                 painter.drawLine(opt.rect.bottomLeft(), opt.rect.bottomRight())
#         else:
#             QStyledItemDelegate.paint(self, painter, option, index)
#             if index.data(Qt.UserRole+udr.lastingrouprole) and not index.data(Qt.UserRole+udr.finalsubgrouprole):
#                 opt = QStyleOptionFrame()
#                 opt.rect = option.rect
#                 painter.drawLine(opt.rect.bottomLeft(), opt.rect.bottomRight())

