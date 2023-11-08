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
    QFrame
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

    def __init__(self, **kwargs):  # parentlayout=None,
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


class LocationGraphicsViewSVG(QWebEngineView):

    def __init__(self, app_ctx, frontorback='front', specificpath="", **kwargs):
        super().__init__(**kwargs)

        imagepath = app_ctx.temp_test_images['sample_' + frontorback]
        if specificpath != "":
            imagepath = specificpath
        imageurl = QUrl.fromLocalFile(imagepath)
        self.load(imageurl)

        self.focusProxy().installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj is self.focusProxy() and event.type() == QEvent.Type.Wheel:
            # print(event.angleDelta())
            print("zoomfactor:", self.zoomFactor())
            print("view pos:", self.pos())
            # print("graphicsProxyWidget():", self.graphicsProxyWidget())
            print("wheelevent pos:", event.position())
            print("wheelevent global pos:", event.globalPosition())
            print("wheelevent global pos, mapped to view:", self.mapFromGlobal(event.globalPosition().toPoint()))
            print("-----------------------------------------")
            oldpos = event.position()
            self.page().runJavaScript("window.scrollTo({x}, {y});".format(x='400', y='400'))
            # min 0.29999998956918206 / max 4.900000058114528
            result = super().eventFilter(obj, event)
        else:
            result = super().eventFilter(obj, event)

        return result
        # return super().eventFilter(obj, event)


    # def wheelEvent(self, e):
    #     print("zoomfactor:", self.zoomFactor())
    #     e.ignore()


class LocationGraphicsView(QGraphicsView):

    # def __init__(self, imagepath, **kwargs):
    #     super().__init__(**kwargs)
    #     main_layout = QHBoxLayout()
    #
    #     self.svg = QWebEngineView()
    #     imageurl = QUrl.fromLocalFile(imagepath)
    #     self.svg.load(imageurl)
    #     main_layout.addWidget(self.svg)
    #     # self.svg.show()
    #     self.setLayout(main_layout)


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


class LocationGraphicsView_old(QGraphicsView):

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


class LocationSvgView_webengine(QGraphicsView):

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


class LocationSvgView_qsvg(QGraphicsView):

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
        # self.mainwindow = self.parent().mainwindow
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
        
        # self.locationoptionsselectionpanel.imagetabwidget
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

        # self.fronttab = ImageDisplayTab(self.mainwindow.app_ctx, 'front')
        self.fronttab = ImageDisplayTabSVG(self.mainwindow.app_ctx, 'front')
        self.fronttab.zoomfactor_changed.connect(self.handle_zoomfactor_changed)
        self.fronttab.linkbutton_toggled.connect(lambda ischecked:
                                                 self.handle_linkbutton_toggled(ischecked, self.fronttab))
        self.addTab(self.fronttab, "Front")
        # self.backtab = ImageDisplayTab(self.mainwindow.app_ctx, 'back')
        self.backtab = ImageDisplayTabSVG(self.mainwindow.app_ctx, 'back')
        self.backtab.zoomfactor_changed.connect(self.handle_zoomfactor_changed)
        self.backtab.linkbutton_toggled.connect(lambda ischecked:
                                                self.handle_linkbutton_toggled(ischecked, self.backtab))
        self.addTab(self.backtab, "Back")

    def handle_zoomfactor_changed(self, scale):
        if self.fronttab.link_button.isChecked() or self.backtab.link_button.isChecked():
            self.fronttab.force_zoom(scale)
            self.backtab.force_zoom(scale)

    def handle_linkbutton_toggled(self, ischecked, thistab):
        othertab = self.fronttab if thistab == self.backtab else self.backtab
        othertab.force_link(ischecked)
        othertab.force_zoom(thistab.zoom_slider.value())
        # self.backtab.force_link(ischecked)
        
    def reset_zoomfactor(self):
        """Reset the zoom factor for this image display to zero zoom and back to the front tab."""
        self.fronttab.zoom_slider.setValue(0)
        self.backtab.zoom_slider.setValue(0)
        self.fronttab.force_zoom(self.fronttab.zoom_slider.value())
        self.backtab.force_zoom(self.backtab.zoom_slider.value())
        
    def reset_link(self):
        """Unlink zoom buttons between front/back."""
        self.handle_linkbutton_toggled(False, self.fronttab)
        self.handle_linkbutton_toggled(False, self.backtab)
        

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


class ImageDisplayTabSVG(QWidget):
    zoomfactor_changed = pyqtSignal(int)
    linkbutton_toggled = pyqtSignal(bool)

    def __init__(self, app_ctx, frontorback='front', specificpath="", **kwargs):
        super().__init__(**kwargs)

        main_layout = QHBoxLayout()

        self.svgdisplay = LocationGraphicsViewSVG(app_ctx, frontorback=frontorback, specificpath=specificpath, parent=self)

        zoom_layout = QVBoxLayout()

        self.zoom_slider = QSlider(Qt.Vertical)
        self.zoom_slider.setMinimum(1)
        self.zoom_slider.setMaximum(20)
        self.zoom_slider.setValue(4)
        self.zoom_slider.valueChanged.connect(self.zoom)
        zoom_layout.addWidget(self.zoom_slider)
        zoom_layout.setAlignment(self.zoom_slider, Qt.AlignHCenter)

        self.link_button = QPushButton("Link")
        self.link_button.setCheckable(True)
        self.link_button.toggled.connect(lambda ischecked: self.linkbutton_toggled.emit(ischecked))
        zoom_layout.addWidget(self.link_button)
        zoom_layout.setAlignment(self.link_button, Qt.AlignHCenter)

        main_layout.addWidget(self.svgdisplay)
        main_layout.addLayout(zoom_layout)

        self.setLayout(main_layout)

    def zoom(self, scale):
        self.svgdisplay.setZoomFactor(scale/4)
        # trans_matrix = self.imagedisplay.transform()
        # trans_matrix.reset()
        # trans_matrix = trans_matrix.scale(scale * self.imagedisplay.factor, scale * self.imagedisplay.factor)
        # self.imagedisplay.setTransform(trans_matrix)

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

