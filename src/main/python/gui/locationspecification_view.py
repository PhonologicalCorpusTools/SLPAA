
from PyQt5.QtWidgets import (
    QListView,
    QTableView,
    QTreeView,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
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
)

from PyQt5.QtWebEngineWidgets import QWebEngineView

from PyQt5.QtCore import (
    QRectF,
    QUrl,
    Qt,
    QEvent,
    pyqtSignal,
    QItemSelectionModel
)

from PyQt5.QtGui import (
    QPixmap
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

    def __init__(self, parentlayout=None):
        super().__init__()
        self.refreshed = True
        self.lasttextentry = ""
        self.lastcompletedentry = ""
        self.parentlayout = parentlayout

    def keyPressEvent(self, event):
        key = event.key()
        modifiers = event.modifiers()

        if key == Qt.Key_Right:  # TODO KV and modifiers == Qt.NoModifier:

            if self.currentText():
                # self.parentlayout.treedisplay.collapseAll()
                itemstoselect = gettreeitemsinpath(self.parentlayout.getcurrenttreemodel(),
                                                   self.currentText(),
                                                   delim=delimiter)
                for item in itemstoselect:
                    if item.checkState() == Qt.Unchecked:
                        item.setCheckState(Qt.PartiallyChecked)
                    # self.parentlayout.treedisplay.setExpanded(item.index(), True)
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


class LocationGraphicsView(QGraphicsView):

    def __init__(self, app_ctx, frontorback='front', parent=None, viewer_size=400, specificpath=""):
        super().__init__(parent=parent)

        self.viewer_size = viewer_size

        self._scene = QGraphicsScene(parent=self)
        imagepath = app_ctx.default_location_images['body_hands_' + frontorback]
        if specificpath != "":
            imagepath = specificpath

        # if specificpath.endswith('.svg'):
        #     self._photo = LocationSvgView()
        #     self._photo.load(QUrl(imagepath))
        #     self._scene.addWidget(self._photo)
        #     self.show()
        # else:
        self._pixmap = QPixmap(imagepath)
        self._photo = QGraphicsPixmapItem(self._pixmap)
        self._scene.addItem(self._photo)
        # self._photo.setPixmap(QPixmap("gui/upper_body.jpg"))

        # self._scene.addPixmap(QPixmap("./body_hands_front.png"))
        self.setScene(self._scene)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.fitInView()

    def fitInView(self, scale=True):
        rect = QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
            self.scale(1 / unity.width(), 1 / unity.height())
            scenerect = self.transform().mapRect(rect)
            factor = min(self.viewer_size / scenerect.width(), self.viewer_size / scenerect.height())
            self.factor = factor
            # viewrect = self.viewport().rect()
            # factor = min(viewrect.width() / scenerect.width(), viewrect.height() / scenerect.height())
            self.scale(factor, factor)


class LocationSvgView(QGraphicsView):

    def __init__(self, parent=None, viewer_size=600, specificpath=""):
        super().__init__(parent=parent)

        self.viewer_size = viewer_size

        self._scene = QGraphicsScene(parent=self)

        self.svg = QWebEngineView()
        # self.svg.urlChanged.connect(self.shownewurl)

        # dir_path = os.path.dirname(os.path.realpath(__file__))
        # print("dir_path", dir_path)
        # cwd = os.getcwd()
        # print("cwd", cwd)

        imageurl = QUrl.fromLocalFile(specificpath)
        self.svg.load(imageurl)
        self.svg.show()
        self._scene.addWidget(self.svg)
        # self._photo.setPixmap(QPixmap("gui/upper_body.jpg"))

        # self._scene.addPixmap(QPixmap("./body_hands_front.png"))
        self.setScene(self._scene)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
    #     self.fitInView()
    #
    # def fitInView(self, scale=True):
    #     rect = QRectF(self._photo.pixmap().rect())
    #     if not rect.isNull():
    #         self.setSceneRect(rect)
    #         unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
    #         self.scale(1 / unity.width(), 1 / unity.height())
    #         scenerect = self.transform().mapRect(rect)
    #         factor = min(self.viewer_size / scenerect.width(), self.viewer_size / scenerect.height())
    #         self.factor = factor
    #         # viewrect = self.viewport().rect()
    #         # factor = min(viewrect.width() / scenerect.width(), viewrect.height() / scenerect.height())
    #         self.scale(factor, factor)

    # TODO KV probably don't need this after all
    def shownewurl(self, newurl):
        self.svg.show()


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


# TODO KV - add undo, ...

class LocationSpecificationPanel(ModuleSpecificationPanel):
    # module_saved = pyqtSignal(LocationTreeModel, PhonLocations, LocationType, dict, list, AddedInfo, int)
    # module_deleted = pyqtSignal()

    def __init__(self, moduletoload=None, **kwargs):  # mainwindow,
        super().__init__(**kwargs)
        self.mainwindow = self.parent().mainwindow

        main_layout = QVBoxLayout()

        # This widget has three separate location trees, so that we can flip back and forth between
        # location types without losing intermediate information. However, once the save button is
        # clicked only the tree for the current location type is saved with the module.
        self.treemodel_body = None
        self.treemodel_spatial = None
        self.treemodel_axis = None
        self.listmodel_axis = None
        self.listmodel_body = None
        self.listmodel_spatial = None
        self.recreate_treeandlistmodels()

        if moduletoload is not None and isinstance(moduletoload, LocationModule):
            loctypetoload = moduletoload.locationtreemodel.locationtype
            phonlocstoload = moduletoload.phonlocs
            # make a copy, so that the module is not being edited directly via this layout
            # (otherwise "cancel" doesn't actually revert to the original contents)
            treemodeltoload = LocationTreeModel(LocationTreeSerializable(moduletoload.locationtreemodel))

        # create layout with buttons for location type (body, signing space, etc)
        # and for phonological locations (phonological, phonetic, etc)
        # loctype_phonloc_layout = QHBoxLayout()
        # self.create_loctype_phonloc_layout(loctype_phonloc_layout)
        loctype_phonloc_layout = self.create_loctype_phonloc_layout()
        # self.addLayout(loctype_phonloc_layout)
        main_layout.addLayout(loctype_phonloc_layout)

        # set buttons and treemodel according to the existing module being loaded (if applicable)
        if moduletoload is not None:
            self.set_loctype_buttons_from_content(loctypetoload)
            self.set_phonloc_buttons_from_content(phonlocstoload)
            self.setcurrenttreemodel(treemodeltoload)
        else:
            self.clear_loctype_buttons_to_default()

        # create list proxies (for search and for selected options list)
        # and set them to refer to list model for current location type
        self.comboproxymodel = LocationPathsProxyModel(wantselected=False)
        self.comboproxymodel.setSourceModel(self.getcurrentlistmodel())
        self.listproxymodel = LocationPathsProxyModel(wantselected=True)
        self.listproxymodel.setSourceModel(self.getcurrentlistmodel())

        # create layout with combobox for searching location items
        # search_layout = QHBoxLayout()
        # self.create_search_layout(search_layout)
        search_layout = self.create_search_layout()
        # self.addLayout(search_layout)
        main_layout.addLayout(search_layout)

        # create layout with visual selection widget (whether image or tree) and list view for selected location options
        # selection_layout = QHBoxLayout()
        # self.build_selection_layout(selection_layout)
        selection_layout = self.create_selection_layout()
        # self.addLayout(selection_layout)
        main_layout.addLayout(selection_layout)

        self.setLayout(main_layout)

        self.enablelocationtools()

    def create_selection_layout(self):
        selection_layout = QHBoxLayout()

        self.locationselectionwidget = LocationSelectionWidget(treemodel=self.getcurrenttreemodel(), parent=self)
        selection_layout.addWidget(self.locationselectionwidget)

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

        selection_layout.addLayout(list_layout)

        return selection_layout

    def create_search_layout(self):
        search_layout = QHBoxLayout()

        search_layout.addWidget(QLabel("Enter tree node"))

        self.combobox = LocnTreeSearchComboBox(self)
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

    def getcurrentlocationtype(self):
        locationtype = LocationType(
            body=self.body_radio.isChecked(),
            signingspace=self.signingspace_radio.isChecked(),
            bodyanchored=self.signingspacebody_radio.isEnabled() and self.signingspacebody_radio.isChecked(),
            purelyspatial=self.signingspacespatial_radio.isEnabled() and self.signingspacespatial_radio.isChecked(),
            axis=self.axis_radio.isChecked()
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

        axis_layout = QHBoxLayout()

        self.axis_radio = QRadioButton("Axis of relation")
        self.axis_radio.setProperty('loctype', 'axis')
        axis_layout.addWidget(self.axis_radio)
        axis_layout.addSpacerItem(QSpacerItem(40, 0))  # TODO KV , QSizePolicy.Minimum, QSizePolicy.Maximum))
        axis_box = QGroupBox()
        axis_box.setLayout(axis_layout)
        loctype_phonloc_layout.addWidget(axis_box, alignment=Qt.AlignVCenter)

        loctype_phonloc_layout.addStretch()

        self.loctype_subgroup = QButtonGroup()
        self.loctype_subgroup.addButton(self.body_radio)
        self.loctype_subgroup.addButton(self.signingspace_radio)
        self.loctype_subgroup.addButton(self.axis_radio)
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
        if self.getcurrentlocationtype().axis:
            return self.treemodel_axis
        elif self.getcurrentlocationtype().usesbodylocations():
            return self.treemodel_body
        elif self.getcurrentlocationtype().purelyspatial:
            return self.treemodel_spatial
        else:
            return LocationTreeModel()

    def getcurrentlistmodel(self):
        if self.getcurrentlocationtype().axis:
            return self.listmodel_axis
        elif self.getcurrentlocationtype().usesbodylocations():
            return self.listmodel_body
        elif self.getcurrentlocationtype().purelyspatial:
            return self.listmodel_spatial
        else:
            return LocationTreeModel().listmodel

    def setcurrenttreemodel(self, tm):
        if self.getcurrentlocationtype().axis:
            self.treemodel_axis = tm
        elif self.getcurrentlocationtype().usesbodylocations():
            self.treemodel_body = tm
        elif self.getcurrentlocationtype().purelyspatial:
            self.treemodel_spatial = tm

        self.setcurrentlistmodel(self.getcurrenttreemodel().listmodel)

    def setcurrentlistmodel(self, lm):
        if self.getcurrentlocationtype().axis:
            self.listmodel_axis = lm
        elif self.getcurrentlocationtype().usesbodylocations():
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
    #
    # def handle_zoomfactor_changed(self, scale):
    #     if self.fronttab.link_button.isChecked() or self.backtab.link_button.isChecked():
    #         self.fronttab.force_zoom(scale)
    #         self.backtab.force_zoom(scale)
    #
    # def handle_linkbutton_toggled(self, ischecked, thistab):
    #     othertab = self.fronttab if thistab == self.backtab else self.backtab
    #     othertab.force_link(ischecked)
    #     othertab.force_zoom(thistab.zoom_slider.value())
    #     # self.backtab.force_link(ischecked)

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
        self.refresh_listproxies()
        # use current locationtype (from buttons) to determine whether/how things get enabled
        anyexceptpurelyspatial = self.getcurrentlocationtype().usesbodylocations() \
                                 or self.getcurrentlocationtype().purelyspatial \
                                 or self.getcurrentlocationtype().axis
        enableselectionwidget = anyexceptpurelyspatial
        enablecomboboxandlistview = anyexceptpurelyspatial
        enabledetailstable = self.getcurrentlocationtype().usesbodylocations()

        self.locationselectionwidget.setlocationtype(self.getcurrentlocationtype(), treemodel=self.getcurrenttreemodel())
        self.locationselectionwidget.setEnabled(enableselectionwidget)

        self.combobox.setEnabled(enablecomboboxandlistview)
        self.pathslistview.setEnabled(enablecomboboxandlistview)

        self.update_detailstable(None, None)
        self.detailstableview.setEnabled(enabledetailstable)

    def getsavedmodule(self, handsdict, timingintervals, addedinfo, inphase):
        phonlocs = self.getcurrentphonlocs()
        return LocationModule(self.getcurrenttreemodel(),
                              hands=handsdict,
                              timingintervals=timingintervals,
                              addedinfo=addedinfo,
                              phonlocs=phonlocs,
                              inphase=inphase)

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
            # treeitem = listindex.model().itemFromIndex(listindex).treeitem
            # addedinfo = copy(treeitem.addedinfo)
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
        self.clear_loctype_buttons_to_default()
        self.clear_phonlocs_buttons()
        self.recreate_treeandlistmodels()
        self.refresh_listproxies()
        self.clear_details()
        self.locationselectionwidget.setlocationtype(None)

    def recreate_treeandlistmodels(self):
        self.treemodel_body = LocationTreeModel()
        self.treemodel_body.locationtype = LocationType(body=True)
        self.treemodel_body.populate(self.treemodel_body.invisibleRootItem())
        self.treemodel_spatial = LocationTreeModel()
        self.treemodel_spatial.locationtype = LocationType(signingspace=True, purelyspatial=True)
        self.treemodel_spatial.populate(self.treemodel_spatial.invisibleRootItem())
        self.treemodel_axis = LocationTreeModel()
        self.treemodel_axis.locationtype = LocationType(axis=True)
        self.treemodel_axis.populate(self.treemodel_axis.invisibleRootItem())

        self.listmodel_body = self.treemodel_body.listmodel
        self.listmodel_spatial = self.treemodel_spatial.listmodel
        self.listmodel_axis = self.treemodel_axis.listmodel

    def clear_loctype_buttons_to_default(self):
        defaultloctype = LocationType()
        loctype_setting = self.mainwindow.app_settings['location']['loctype']
        if loctype_setting == 'axis':
            defaultloctype.axis = True
        elif loctype_setting == 'body':
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

        if loctype.axis:
            self.axis_radio.setChecked(True)
        elif loctype.body:
            self.body_radio.setChecked(True)
        elif loctype.signingspace:
            self.signingspace_radio.setChecked(True)
            if loctype.purelyspatial:
                self.signingspacespatial_radio.setChecked(True)
            elif loctype.bodyanchored:
                self.signingspacebody_radio.setChecked(True)

        for btn in self.signingspace_subgroup.buttons():
            btn.setEnabled(not loctype.axis and not loctype.body)

        self.loctype_subgroup.setExclusive(True)
        self.signingspace_subgroup.setExclusive(True)
        self.loctype_subgroup.blockSignals(False)
        self.signingspace_subgroup.blockSignals(False)

    def clear_details(self):
        self.update_detailstable(None, None)

    def refresh_listproxies(self):

        self.comboproxymodel.setSourceModel(self.getcurrentlistmodel())
        self.listproxymodel.setSourceModel(self.getcurrentlistmodel())
        self.combobox.setModel(self.comboproxymodel)
        self.combobox.setCurrentIndex(-1)
        self.pathslistview.setModel(self.listproxymodel)

    def clearlist(self, button):
        numtoplevelitems = self.getcurrenttreemodel().invisibleRootItem().rowCount()
        for rownum in range(numtoplevelitems):
            self.getcurrenttreemodel().invisibleRootItem().child(rownum, 0).uncheck(force=True)

    def desiredwidth(self):
        return 500

    def desiredheight(self):
        return 700


class LocationSelectionWidget(QStackedWidget):

    def __init__(self, treemodel, locationtype=None, **kwargs):  # mainwindow,
        super().__init__(**kwargs)
        self.mainwindow = self.parent().mainwindow

        # self.imageslayout = QHBoxLayout()
        self.imagetabs = QTabWidget()
        self.fronttab = ImageDisplayTab(self.mainwindow.app_ctx, 'front')
        self.fronttab.zoomfactor_changed.connect(self.handle_zoomfactor_changed)
        self.fronttab.linkbutton_toggled.connect(lambda ischecked:
                                                 self.handle_linkbutton_toggled(ischecked, self.fronttab))
        self.imagetabs.addTab(self.fronttab, "Front")
        self.backtab = ImageDisplayTab(self.mainwindow.app_ctx, 'back')
        self.backtab.zoomfactor_changed.connect(self.handle_zoomfactor_changed)
        self.backtab.linkbutton_toggled.connect(lambda ischecked:
                                                self.handle_linkbutton_toggled(ischecked, self.backtab))
        self.imagetabs.addTab(self.backtab, "Back")
        # self.imageslayout.addWidget(self.imagetabs)
        self.addWidget(self.imagetabs)

        # self.treelayout = QHBoxLayout()
        self.axistreewidget = AxisTreeWidget(treemodel)
        # self.treelayout.addWidget(self.axistreewidget)
        self.addWidget(self.axistreewidget)

        self.setlocationtype(locationtype)

    def setlocationtype(self, locationtype, treemodel=None):
        # print("setlocationtype")
        if treemodel is not None:
            self.axistreewidget.treemodel = treemodel
        if locationtype is not None and locationtype.axis:
            # self.setLayout(self.treelayout)
            # print("setting current widget to axistreewidget")
            # tempprinttreemodel(self.axistreewidget.treemodel)
            self.setCurrentWidget(self.axistreewidget)
        else:
            # self.setLayout(self.imageslayout)
            self.setCurrentWidget(self.imagetabs)

    def handle_zoomfactor_changed(self, scale):
        if self.fronttab.link_button.isChecked() or self.backtab.link_button.isChecked():
            self.fronttab.force_zoom(scale)
            self.backtab.force_zoom(scale)

    def handle_linkbutton_toggled(self, ischecked, thistab):
        othertab = self.fronttab if thistab == self.backtab else self.backtab
        othertab.force_link(ischecked)
        othertab.force_zoom(thistab.zoom_slider.value())
        # self.backtab.force_link(ischecked)


class ImageDisplayTab(QWidget):
    zoomfactor_changed = pyqtSignal(int)
    linkbutton_toggled = pyqtSignal(bool)

    def __init__(self, app_ctx, frontorback='front', specificpath="", **kwargs):
        super().__init__(**kwargs)

        main_layout = QHBoxLayout()

        self.imagedisplay = LocationGraphicsView(app_ctx, frontorback=frontorback, specificpath=specificpath)
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


class AxisTreeWidget(QWidget):
    # zoomfactor_changed = pyqtSignal(int)
    # linkbutton_toggled = pyqtSignal(bool)

    def __init__(self, treemodel, **kwargs):
        super().__init__(**kwargs)

        main_layout = QHBoxLayout()

        self._treemodel = treemodel

        self.treedisplay = LocationTreeView()
        self.treedisplay.setItemDelegate(LocationTreeItemDelegate())
        self.treedisplay.setHeaderHidden(True)
        self.treedisplay.setModel(self.treemodel)

        # self.treedisplay.installEventFilter(self)
        # self.treedisplay.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # TODO KV this causes a crash
        self.treedisplay.setMinimumWidth(400)

        main_layout.addWidget(self.treedisplay)

        self.setLayout(main_layout)

    @property
    def treemodel(self):
        # if self._treemodel is None:
        #     self._treemodel = LocationTreeModel(self)
        return self._treemodel

    @treemodel.setter
    def treemodel(self, treemod):
        self._treemodel = treemod
        self.treedisplay.setModel(self._treemodel)


# Ref: https://stackoverflow.com/questions/48575298/pyqt-qtreewidget-how-to-add-radiobutton-for-items
# TODO KV can this be combined with the one for movement?
class LocationTreeItemDelegate(QStyledItemDelegate):

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

