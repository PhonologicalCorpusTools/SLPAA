import io
import re
import os

from PyQt5.QtWidgets import (
    QTableView,
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
    QAbstractItemView,
    QHeaderView,
    QCheckBox,
    QSlider,
    QTabWidget,
    QWidget,
    QSpacerItem,
    QFrame,
    QScrollArea,
    QMenu,
    QAction,
)

from PyQt5.QtSvg import QSvgRenderer, QGraphicsSvgItem

from PyQt5.QtCore import (
    Qt,
    QEvent,
    pyqtSignal,
    QItemSelectionModel,
    QPointF
)

from lexicon.module_classes import treepathdelimiter, LocationModule, PhonLocations, userdefinedroles as udr
from models.location_models import LocationTreeItem, LocationTableModel, LocationTreeModel, \
    LocationType, LocationPathsProxyModel, locn_options_body
from serialization_classes import LocationTreeSerializable
from gui.modulespecification_widgets import AddedInfoContextMenu, ModuleSpecificationPanel, \
    TreeListView, TreePathsListItemDelegate, TreeSearchComboBox

from constant import CONTRA, IPSI


class LocationTableView(QTableView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # set the table model
        locntablemodel = LocationTableModel(parent=self)
        self.setModel(locntablemodel)
        self.horizontalHeader().resizeSections(QHeaderView.Stretch)


class LocationOptionsSelectionPanel(QFrame):
    def __init__(self, treemodeltoload=None, displayvisualwidget=True, **kwargs):
        super().__init__(**kwargs)
        self.mainwindow = self.parent().mainwindow
        self.app_ctx = self.mainwindow.app_ctx
        self.showimagetabs = displayvisualwidget
        self.dominanthand = self.mainwindow.current_sign.signlevel_information.handdominance

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

        if treemodeltoload is not None and isinstance(treemodeltoload, LocationTreeModel):
            self.set_multiple_selection_from_content(self.treemodel.multiple_selection_allowed)

        self.setLayout(main_layout)

    def get_listed_paths(self):
        proxyModel = self.listproxymodel
        sourceModel = self.listmodel
        
        paths = [] 

        for row in range(proxyModel.rowCount()):
            sourceIndex = proxyModel.mapToSource(proxyModel.index(row, 0))
            path = sourceModel.data(sourceIndex, Qt.DisplayRole)
            paths.append(path)
        return paths
    
    def enableImageTabs(self, enable):
        if self.showimagetabs:
            self.imagetabwidget.setEnabled(enable)

    def clear_details(self):
        self.update_detailstable()

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
            proxyindex = self.pathslistview.currentIndex()  # TODO what if multiple are selected?
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
        self._treemodel = treemodel
        self._listmodel = treemodel.listmodel

    @property
    def listmodel(self):
        return self._listmodel

    @listmodel.setter
    def listmodel(self, listmodel):
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

        self.combobox = TreeSearchComboBox(parent=self)
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
            self.imagetabwidget = ImageTabWidget(treemodelreference=self, parent=self)
            self.imagetabwidget.region_selected.connect(self.handle_region_selected)
            selection_layout.addWidget(self.imagetabwidget)

        list_layout = self.create_list_layout()
        selection_layout.addLayout(list_layout)

        return selection_layout

    def handle_clearlisthighlights(self):
        self.pathslistview.selectionModel().clearSelection()

    def handle_region_selected(self, regionname, imageonly):
        if imageonly:
            return  # don't do any of the checking/selecting below

        # select that item, which also adds it to the visible location paths list
        matchingtreeitems = self.treemodel.findItems(regionname, Qt.MatchRecursive)
        for treeitem in matchingtreeitems:
            treeitem.setCheckState(Qt.Checked)

        # ensure that the newly-added item gets selected/highlighted in the visible location paths list
        matchinglistitems = [treeitem.listitem for treeitem in matchingtreeitems]
        for listitem in matchinglistitems:
            proxymodelindex = self.listproxymodel.mapFromSource(self.listmodel.indexFromItem(listitem))
            self.pathslistview.selectionModel().select(proxymodelindex, QItemSelectionModel.ClearAndSelect)

    def update_image(self):
        if not self.treemodel.locationtype.usesbodylocations():
            return

        selectedindexes = self.pathslistview.selectionModel().selectedIndexes()
        if len(selectedindexes) == 1:  # the image displayed reflects the (single) selection
            itemindex = selectedindexes[0]
            listitemindex = self.pathslistview.model().mapToSource(itemindex)
            selectedlistitem = self.pathslistview.model().sourceModel().itemFromIndex(listitemindex)
            selectedtreeitem = selectedlistitem.treeitem
            locationname = selectedtreeitem.text()
            loc, relside = location_and_relativeside(locationname)
            newimagepath = self.app_ctx.predefined_locations_yellow[loc][get_absolutehand(self.dominanthand, relside)][self.app_ctx.nodiv]
            self.imagetabwidget.handle_image_changed(newimagepath, locationname, False)
        else:  # 0 or >1 rows selected; the image is cleared
            self.imagetabwidget.currentWidget().clear()

    def update_detailstable(self):
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

        self.pathslistview = TreeListView()
        self.pathslistview.setItemDelegate(TreePathsListItemDelegate())
        self.pathslistview.setSelectionMode(QAbstractItemView.MultiSelection)
        self.pathslistview.setModel(self.listproxymodel)
        self.pathslistview.setMinimumWidth(300)
        self.pathslistview.installEventFilter(self)
        self.pathslistview.selectionModel().selectionChanged.connect(self.handle_selection_changed)

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

        self.multiple_selection_cb = QCheckBox("Allow multiple selection")
        self.multiple_selection_cb.clicked.connect(self.handle_toggle_multiple_selection)
        buttons_layout.addWidget(self.multiple_selection_cb)

        self.clearbutton = QPushButton("Clear")
        self.clearbutton.clicked.connect(self.clearlist)
        buttons_layout.addWidget(self.clearbutton)

        list_layout.addLayout(buttons_layout)

        self.detailstableview = LocationTableView()

        list_layout.addWidget(self.detailstableview)

        return list_layout

    def handle_selection_changed(self, selected=None, deselected=None):
        self.update_detailstable()
        self.update_image()
    
    def set_multiple_selection_from_content(self, multsel):
        self.multiple_selection_cb.setChecked(multsel)
    
    def handle_toggle_multiple_selection(self):
        self.treemodel.multiple_selection_allowed = self.multiple_selection_cb.isChecked()

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

    def __init__(self, moduletoload=None, showimagetabs=True, **kwargs):
        super().__init__(**kwargs)

        main_layout = QVBoxLayout()

        # This widget has two separate location trees, so that we can flip back and forth between
        # location types without losing intermediate information. However, once the save button is
        # clicked only the tree for the current location type is saved with the module.
        self.treemodel_body = None
        self.treemodel_spatial = None
        self.listmodel_body = None
        self.listmodel_spatial = None
        self.recreate_treeandlistmodels()

        loctypetoload = None
        # phonlocstoload = None
        treemodeltoload = None

        if moduletoload is not None and isinstance(moduletoload, LocationModule):
            self.existingkey = moduletoload.uniqueid
            loctypetoload = moduletoload.locationtreemodel.locationtype
            # phonlocstoload = moduletoload.phonlocs
            # make a copy, so that the module is not being edited directly via this layout
            # (otherwise "cancel" doesn't actually revert to the original contents)
            treemodeltoload = LocationTreeModel(LocationTreeSerializable(moduletoload.locationtreemodel))

        # create layout with buttons for location type (body, signing space, etc)
        # and for phonological locations (phonological, phonetic, etc)
        loctype_layout = self.create_loctype_layout()
        main_layout.addLayout(loctype_layout)

        # create panel containing search box, visual location selection (if applicable), list of selected options, and details table
        self.locationoptionsselectionpanel = LocationOptionsSelectionPanel(treemodeltoload=treemodeltoload, displayvisualwidget=showimagetabs, parent=self)
        main_layout.addWidget(self.locationoptionsselectionpanel)

        # set buttons and treemodel according to the existing module being loaded (if applicable)
        if moduletoload is not None and isinstance(moduletoload, LocationModule):
            self.set_loctype_buttons_from_content(loctypetoload)
            # self.set_phonloc_buttons_from_content(phonlocstoload)
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

    def multiple_selections_check(self):
        paths = self.locationoptionsselectionpanel.get_listed_paths()
        if len(paths) == 1:
            return False
        # if the multiple selections are parents of each other, doesn't count as multiple selections.
        for i in range(len(paths)):
            for j in range(i+1, len(paths)):
                if (paths[i] not in paths[j] and paths[j] not in paths[i]):
                    return True
        return False

    def validity_check(self):
        selectionsvalid = True
        warningmessage = "" 

        self.locationoptionsselectionpanel.refresh_listproxies()
        treemodel = self.getcurrenttreemodel()
        
        multiple_selections = self.multiple_selections_check()

        if self.getcurrentlocationtype().usesbodylocations() and multiple_selections and not treemodel.multiple_selection_allowed:
            selectionsvalid = False
            warningmessage = warningmessage + "Multiple locations have been selected but 'Allow multiple selection' is not checked."
        return selectionsvalid, warningmessage

    def getcurrentlocationtype(self):
        locationtype = LocationType(
            body=self.body_radio.isChecked(),
            signingspace=self.signingspace_radio.isChecked(),
            bodyanchored=self.signingspacebody_radio.isEnabled() and self.signingspacebody_radio.isChecked(),
            purelyspatial=self.signingspacespatial_radio.isEnabled() and self.signingspacespatial_radio.isChecked()
        )
        return locationtype

    def create_loctype_layout(self):
        loctype_layout = QHBoxLayout()

        loctype_layout.addWidget(QLabel("Location:"), alignment=Qt.AlignVCenter)

        body_layout = QHBoxLayout()
        self.body_radio = QRadioButton("Body")
        self.body_radio.setProperty('loctype', 'body')
        body_layout.addWidget(self.body_radio)
        body_layout.addSpacerItem(QSpacerItem(60, 0))  # TODO KV , QSizePolicy.Minimum, QSizePolicy.Maximum))
        body_box = QGroupBox()
        body_box.setLayout(body_layout)
        loctype_layout.addWidget(body_box, alignment=Qt.AlignVCenter)

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
        loctype_layout.addWidget(signingspace_box, alignment=Qt.AlignVCenter)
        loctype_layout.addStretch()

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

        return loctype_layout

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

        # ensure the first item in the selected locations list (if any) is selected/highlighted
        self.locationoptionsselectionpanel.pathslistview.setindex(-1)

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
            self.locationoptionsselectionpanel.multiple_selection_cb.setEnabled(btn != self.signingspacespatial_radio)
            self.enablelocationtools()

    def handle_toggle_locationtype(self, btn):
        if btn is not None and btn.isChecked():
            for b in self.signingspace_subgroup.buttons():
                b.setEnabled(btn == self.signingspace_radio)
            self.locationoptionsselectionpanel.multiple_selection_cb.setEnabled(
                self.signingspacespatial_radio.isChecked() == False 
                or self.signingspacespatial_radio.isEnabled() == False)

            self.enablelocationtools()

    def enablelocationtools(self):
        # self.refresh_listproxies()
        self.locationoptionsselectionpanel.treemodel = self.getcurrenttreemodel()
        self.locationoptionsselectionpanel.refresh_listproxies()
        # use current locationtype (from buttons) to determine whether/how things get enabled
        anyexceptpurelyspatial = self.getcurrentlocationtype().usesbodylocations() or self.getcurrentlocationtype().purelyspatial
        usesbodylocation = self.getcurrentlocationtype().usesbodylocations()
        enableimagetabs = usesbodylocation  # anyexceptpurelyspatial
        enablecomboboxandlistview = anyexceptpurelyspatial
        enabledetailstable = self.getcurrentlocationtype().usesbodylocations()

        self.locationoptionsselectionpanel.enableImageTabs(enableimagetabs)
        self.locationoptionsselectionpanel.combobox.setEnabled(enablecomboboxandlistview)
        self.locationoptionsselectionpanel.pathslistview.setEnabled(enablecomboboxandlistview)
        self.locationoptionsselectionpanel.update_detailstable()
        self.locationoptionsselectionpanel.detailstableview.setEnabled(enabledetailstable)

    def getsavedmodule(self, articulators, timingintervals, phonlocs, addedinfo, inphase):
        # phonlocs = self.getcurrentphonlocs()
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
            listindex = proxyindex.model().mapToSource(proxyindex)
            addedinfo = listindex.model().itemFromIndex(listindex).treeitem.addedinfo

            menu = AddedInfoContextMenu(addedinfo)
            menu.exec_(event.globalPos())

        return super().eventFilter(source, event)

    def clear(self):
        """Restore GUI to the defaults."""
        self.clear_loctype_buttons_to_default()
        self.clear_phonlocs_buttons()
        self.recreate_treeandlistmodels()
        
        # Reset selections
        self.locationoptionsselectionpanel.multiple_selection_cb.setChecked(False)
        self.locationoptionsselectionpanel.treemodel = self.getcurrenttreemodel()
        self.locationoptionsselectionpanel.refresh_listproxies()
        self.locationoptionsselectionpanel.clear_details()
        
        # Reset sort
        self.locationoptionsselectionpanel.reset_sort()
        
        # Reset zoom and link
        self.locationoptionsselectionpanel.imagetabwidget.reset_zoomfactor()
        self.locationoptionsselectionpanel.imagetabwidget.reset_link()
        
        # Reset all images and reset view to front panel
        self.locationoptionsselectionpanel.imagetabwidget.clear()
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
            
        self.locationoptionsselectionpanel.multiple_selection_cb.setEnabled(not loctype.purelyspatial)
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
    region_selected = pyqtSignal(str, bool)  # name of region, image only (vs also adding to selected paths list)

    def __init__(self, treemodelreference, **kwargs):
        super().__init__(**kwargs)
        self.mainwindow = self.parent().mainwindow
        self.app_ctx = self.mainwindow.app_ctx

        self.fronttab = SVGDisplayTab(treemodelreference, 'front', parent=self)
        self.fronttab.zoomfactor_changed.connect(self.handle_zoomfactor_changed)
        self.fronttab.linkbutton_toggled.connect(lambda ischecked:
                                                 self.handle_linkbutton_toggled(ischecked, self.fronttab))
        self.fronttab.region_selected.connect(self.handle_region_selected)
        self.addTab(self.fronttab, "Front")

        self.backtab = SVGDisplayTab(treemodelreference, 'back', parent=self)
        self.backtab.zoomfactor_changed.connect(self.handle_zoomfactor_changed)
        self.backtab.linkbutton_toggled.connect(lambda ischecked:
                                                self.handle_linkbutton_toggled(ischecked, self.backtab))
        self.backtab.region_selected.connect(self.handle_region_selected)
        self.addTab(self.backtab, "Back")

        # do we actually need a side tab? so far all regions are viewable from either front or back;
        # none are depicted from a side view
        # self.sidetab = SVGDisplayTab(treemodelreference, 'side', parent=self)
        # self.sidetab.zoomfactor_changed.connect(self.handle_zoomfactor_changed)
        # self.sidetab.linkbutton_toggled.connect(lambda ischecked:
        #                                         self.handle_linkbutton_toggled(ischecked, self.sidetab))
        # self.sidetab.region_selected.connect(self.region_selected.emit)
        # self.addTab(self.sidetab, "Side")

        self.alltabs = [self.fronttab, self.backtab]  # , self.sidetab]

    def setEnabled(self, enabled):
        if enabled:
            self.setToolTip("L-click to cycle through regions; R-click for menu; D key to toggle divisons; S key to select region")
        else:
            self.setToolTip("Visual interface available if a body location is specified")

        super().setEnabled(enabled)

    def handle_region_selected(self, regionname, imageonly):
        relevanttab = self.backtab if isbackview(regionname) else self.fronttab
        relevanttab.current_image_region = regionname
        self.region_selected.emit(regionname, imageonly)

    def handle_image_changed(self, newimagepath, loc, divisions=None):
        relevanttab = self.backtab if isbackview(loc) else self.fronttab
        self.setCurrentWidget(relevanttab)
        relevanttab.imgscroll.handle_image_changed(newimagepath)
        relevanttab.current_image_region = loc
        if divisions is not None:
            relevanttab.current_image_divisions = divisions

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

    def clear(self):
        for tab in self.alltabs:
            tab.clear()


def isbackview(loc):
    for backname in ["back of head", "behind ear", "buttocks"]:
        if backname in loc.lower():
            return True
    return False


class LocationAction(QAction):
    region_selected = pyqtSignal(str, bool)  # name of region, image only (vs also adding to selected paths list)

    def __init__(self, elid, app_ctx, depth=0, **kwargs):
        self.app_ctx = app_ctx
        self.dominantside = self.app_ctx.main_window.current_sign.signlevel_information.handdominance
        self.absoluteside = "R" if "Right" in elid else ("L" if "Left" in elid else "")
        self.name = self.app_ctx.predef_locns_descr_byfilename(elid).replace(self.app_ctx.contraoripsi, get_relativehand(self.dominantside, self.absoluteside))
        super().__init__(self.name, **kwargs)
        self.triggered.connect(self.handle_selection)
        self.depth = depth

    @property
    def depth(self):
        return self._depth

    @depth.setter
    def depth(self, new_depth):
        self._depth = new_depth
        leadingspaces = "  " * self.depth
        self.setText(leadingspaces + self.name)

    def handle_selection(self, imageonly=False):
        self.region_selected.emit(self.name, imageonly)


def location_and_relativeside(locationname):
    loc = locationname.replace(" - " + CONTRA, "").replace(" - " + IPSI, "")
    side = CONTRA if CONTRA in locationname else (IPSI if IPSI in locationname else "both/all")
    return loc, side


def location_and_absoluteside(locationname, dominantside):
    loc, relside = location_and_relativeside(locationname)
    absside = get_absolutehand(dominantside, relside)
    return loc, absside


def get_relativehand(dominantside, absoluteside):
    if absoluteside in ["both/all", ""]:
        return "both/all"
    else:
        return IPSI if dominantside == absoluteside else CONTRA


def get_absolutehand(dominantside, relativeside):
    if relativeside in ["both/all", ""]:
        return "both/all"
    elif relativeside == IPSI:
        return dominantside
    elif dominantside == "R":
        return "L"
    else:
        return "R"


class SVGDisplayTab(QWidget):
    zoomfactor_changed = pyqtSignal(int)
    linkbutton_toggled = pyqtSignal(bool)
    region_selected = pyqtSignal(str, bool)  # name of region, image only (vs also adding to selected paths list)

    def __init__(self, treemodelreference, frontbackside='front', **kwargs):
        super().__init__(**kwargs)
        mainwindow = self.parent().mainwindow
        self.app_ctx = mainwindow.app_ctx
        self.dominanthand = self.app_ctx.main_window.current_sign.signlevel_information.handdominance
        self.defaultimagepath = self.app_ctx.default_location_images[frontbackside]
        self.app_settings = mainwindow.app_settings
        self.treemodelreference = treemodelreference
        self.current_image_region = "all"
        self.current_image_divisions = False

        main_layout = QHBoxLayout()
        img_layout = QVBoxLayout()

        self.imgscroll = SVGDisplayScroll(self.defaultimagepath, self.app_ctx)
        self.imgscroll.zoomfactor_changed.connect(self.zoomfactor_changed.emit)
        img_layout.addWidget(self.imgscroll)
        self.imgscroll.img_clicked.connect(self.handle_img_clicked)
        self.imgscroll.key_released.connect(self.handle_key_released)
        main_layout.addLayout(img_layout)

        zoom_layout = QVBoxLayout()
        zoom_label = QLabel("Zoom")
        zoom_layout.addWidget(zoom_label)
        zoom_layout.setAlignment(zoom_label, Qt.AlignHCenter)

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
        self.link_button.toggled.connect(self.linkbutton_toggled.emit)
        zoom_layout.addWidget(self.link_button)
        zoom_layout.setAlignment(self.link_button, Qt.AlignHCenter)

        main_layout.addLayout(zoom_layout)
        self.setLayout(main_layout)

        self.setMinimumHeight(400)

    def clear(self):
        self.imgscroll.handle_image_changed(self.defaultimagepath)
        self.current_image_region = "all"
        self.current_image_divisions = False

    def handle_region_selected(self, locationname, imageonly):
        self.region_selected.emit(locationname, imageonly)
        locationname_noside = locationname.replace(" - " + CONTRA, "").replace(" - " + IPSI, "")

        # just assume yellow for now
        colour = "yellow"  # if "yellow" in imagefile else ("green" if "green" in imagefile else "violet")
        relativeside = IPSI if IPSI in locationname else (CONTRA if CONTRA in locationname else "")
        absoluteside = get_absolutehand(self.dominanthand, relativeside)
        divisions = self.app_ctx.div if self.current_image_divisions else self.app_ctx.nodiv
        newimagepath = self.app_ctx.predefined_locations_bycolour(colour)[locationname_noside][absoluteside][divisions]
        if not newimagepath:
            newimagepath = self.app_ctx.predefined_locations_bycolour(colour)[locationname_noside][absoluteside][self.app_ctx.nodiv]
        self.imgscroll.handle_image_changed(newimagepath)

    def handle_img_clicked(self, clickpoint, listofids, mousebutton):
        listofids = list(set(listofids))
        locnames = [self.app_ctx.predef_locns_descr_byfilename(elid) for elid in listofids]

        elementname_actions = []
        for idx, locname in enumerate(locnames):
            locationname_noside = locname.replace(" - " + self.app_ctx.contraoripsi, "")
            if locationname_noside in self.app_ctx.predefined_locations_key.keys():
                locact = LocationAction(listofids[idx], self.app_ctx)
                locact.region_selected.connect(self.handle_region_selected)
                elementname_actions.append(locact)

        # sort elementname_actions according to position in location tree
        elementname_actions = self.sortbylocationtree(elementname_actions, order="preorder")
        menunames = [locact.name for locact in elementname_actions]

        if mousebutton == Qt.RightButton:
            elementids_menu = QMenu()
            elementids_menu.addActions(elementname_actions)
            elementids_menu.exec_(clickpoint.toPoint())

        elif mousebutton == Qt.LeftButton:
            order = self.app_settings['location']['clickorder']

            if self.current_image_region in menunames:
                # start from where we are
                curidx = menunames.index(self.current_image_region)
                indexchange = 1 if order == 1 else -1
                nextidx = (curidx + indexchange) % len(menunames)
            else:
                # restart cycling through
                nextidx = 0 if order == 1 else -1

            if elementname_actions:  # might be empty if there's no location regions in the spot where the user clicked
                nextaction = elementname_actions[nextidx]
                # simulate triggering selection of this menu item (but without adding it to the selected list)
                nextaction.handle_selection(imageonly=True)

    # Sort LocationAction items in input list, according to their position in the location options tree.
    # The tree can be traversed either preorder (top-down) or postorder (bottom-up).
    # Also set the depths for the LocationAction items based on their corresponding depth in the tree.
    # Returns the sorted list of LocationAction items with updated depth info.
    def sortbylocationtree(self, locationactionslist, order="preorder"):
        if not locationactionslist:  # if it's empty, don't bother doing all the work below
            return locationactionslist

        names_depths_traversed = [(node.display_name, depth) for node, depth in locn_options_body.flatten(order)]
        names_depths_dict = dict(names_depths_traversed)
        namesonly = [name for name, depth in names_depths_traversed]

        # used Method #3 at https://www.geeksforgeeks.org/python-sort-list-according-to-other-list-order/
        sortorder_dict = {displayname: idx for idx, displayname in enumerate(namesonly)}
        actions_list = [(action, sortorder_dict[action.name]) for action in locationactionslist]
        actions_list.sort(key=lambda x: x[1])
        result = [action for action, index in actions_list]

        for action in result:
            action.depth = names_depths_dict[action.name]
        mindepth = min([action.depth for action in result])
        if mindepth > 0:
            for action in result:
                action.depth -= mindepth

        return result

    def handle_key_released(self, key):
        if key == Qt.Key_D:
            self.toggledivisions()
        elif key == Qt.Key_S:
            self.region_selected.emit(self.current_image_region, False)

    # toggle divisions (if available)
    def toggledivisions(self):
        imagepath = self.imgscroll.imagepath

        if self.current_image_divisions:
            # switch to no divisions
            newimagepath = imagepath.replace("_with_Divisions", "")
            self.imgscroll.handle_image_changed(newimagepath)
            self.current_image_divisions = False
        else:
            locationtext = self.current_image_region.replace(" - " + IPSI, "").replace(" - " + CONTRA, "")
            _, imagefile = os.path.split(imagepath)
            side = self.app_ctx.right if 'Right' in imagefile else (self.app_ctx.left if 'Left' in imagefile else self.app_ctx.both)
            # just assume yellow for now
            colour = "yellow"  #  if "yellow" in imagefile else ("green" if "green" in imagefile else "violet")
            newimagepath = self.app_ctx.predefined_locations_bycolour(colour)[locationtext][side][self.app_ctx.div]
            if newimagepath != "":
                self.imgscroll.handle_image_changed(newimagepath)
                self.current_image_divisions = True

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
    key_released = pyqtSignal(int)
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
        self.imagepath = imagepath

        self.renderer = QSvgRenderer(self.imagepath, parent=self)
        self.elementids = []
        self.gatherelementids(self.imagepath)
        self.scn = SVGGraphicsScene([], app_ctx, parent=self)
        self.scn.img_clicked.connect(self.img_clicked.emit)
        self.scn.key_released.connect(self.key_released.emit)
        self.scn.img_changed.connect(self.handle_image_changed)

        self.initializeSVGitems()

        self.vw = QGraphicsView(self.scn)
        self.img_layout.addWidget(self.vw)
        main_layout.addLayout(self.img_layout)
        self.setLayout(main_layout)

    def handle_image_changed(self, newimagepath):
        self.scn.clear()
        self.imagepath = newimagepath
        self.renderer.load(self.imagepath)
        self.elementids = []
        self.gatherelementids(self.imagepath)
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
    key_released = pyqtSignal(int)

    def __init__(self, svgitems, app_ctx, **kwargs):
        super().__init__(**kwargs)
        self.app_ctx = app_ctx
        for it in svgitems:
            self.addItem(it)

    def mouseReleaseEvent(self, event):
        mousebutton = event.button()
        scenepoint = QPointF(event.scenePos().x(), event.scenePos().y())
        screenpoint = QPointF(event.screenPos().x(), event.screenPos().y())
        items = self.items(scenepoint)
        clickedids = [it.elementId().strip("0") for it in items if it.elementId() != ""]
        self.img_clicked.emit(screenpoint, clickedids, mousebutton)

    def keyReleaseEvent(self, event):
        self.key_released.emit(event.key())

