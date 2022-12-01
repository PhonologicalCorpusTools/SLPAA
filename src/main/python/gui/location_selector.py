import os
import json
from fractions import Fraction
from PyQt5.QtWidgets import (
    QFrame,
    QPushButton,
    QWidgetAction,
    QAction,
    QMenu,
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
        # self.link_checkbox = QCheckBox("Link")
        # self.link_checkbox.toggled.connect(lambda ischecked: self.linkcheckbox_toggled.emit(ischecked))
        # zoom_layout.addWidget(self.link_checkbox)
        # zoom_layout.setAlignment(self.link_checkbox, Qt.AlignHCenter)

        # self.link_checkbox.toggled.connect(lambda ischecked: self.linkcheckbox_toggled.emit(ischecked))
        # self.link_button.toggled.connect(lambda ischecked: self.linkcheckbox_toggled.emit(ischecked))

        main_layout.addWidget(self.imagedisplay)
        # main_layout.addWidget(self.zoom_slider)
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

        # TODO KV temp - these need to live in the model item itself
        self.uncertain_action_state = False
        self.uncertain_action_text = ""
        self.estimate_action_state = False
        self.estimate_action_text = ""
        self.varies_action_state = False
        self.varies_action_text = ""
        self.exceptional_action_state = False
        self.exceptional_action_text = ""
        self.notspecified_action_state = False
        self.notspecified_action_text = ""

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

        # label_layout = QVBoxLayout()
        # label_layout.addWidget(QLabel("Location:"))
        # label_layout.addStretch()
        # loctype_phonloc_layout.addLayout(label_layout)
        loctype_phonloc_layout.addWidget(QLabel("Location:"), alignment=Qt.AlignVCenter)

        # bodyanchored_layout = QVBoxLayout()
        # self.bodyanchored_radio = QRadioButton("Body-anchored")
        # self.bodyanchored_radio.setProperty('loctype', 'body')
        # bodyanchored_layout.addWidget(self.bodyanchored_radio)
        # bodyanchored_layout.addStretch()
        # loctype_layout.addLayout(bodyanchored_layout)

        # signingspace_layout = QVBoxLayout()
        # self.signingspace_radio = QRadioButton("Signing space")
        # self.signingspace_radio.setProperty('loctype', 'signingspace')
        # signingspace_layout.addWidget(self.signingspace_radio)
        #
        # signingspaceoptions_spacedlayout = QHBoxLayout()
        # signingspaceoptions_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        # signingspaceoptions_layout = QVBoxLayout()
        # self.signingspacebody_radio = QRadioButton('(body-anchored)')
        # self.signingspacebody_radio.setProperty('loctype', 'signingspace_body')
        # signingspaceoptions_layout.addWidget(self.signingspacebody_radio)
        # self.signingspacespatial_radio = QRadioButton('(purely spatial)')
        # self.signingspacespatial_radio.setProperty('loctype', 'signingspace_spatial')
        # signingspaceoptions_layout.addWidget(self.signingspacespatial_radio)
        # signingspaceoptions_spacedlayout.addLayout(signingspaceoptions_layout)
        # signingspace_layout.addLayout(signingspaceoptions_spacedlayout)
        # loctype_layout.addLayout(signingspace_layout)
        # loctype_layout.addStretch()

        body_layout = QHBoxLayout()

        # bodyanchored_layout = QVBoxLayout()
        self.body_radio = QRadioButton("Body")
        self.body_radio.setProperty('loctype', 'body')
        body_layout.addWidget(self.body_radio)
        body_layout.addSpacerItem(QSpacerItem(100, 0))  # TODO KV , QSizePolicy.Minimum, QSizePolicy.Maximum))
        body_box = QGroupBox()
        body_box.setLayout(body_layout)
        loctype_phonloc_layout.addWidget(body_box, alignment=Qt.AlignVCenter)
        # bodyanchored_layout.addStretch()
        # loctype_layout.addLayout(bodyanchored_layout)

        signingspace_layout = QHBoxLayout()

        self.signingspace_radio = QRadioButton("Signing space  (")
        self.signingspace_radio.setProperty('loctype', 'signingspace')
        # loctype_layout.addWidget(self.signingspace_radio)
        signingspace_layout.addWidget(self.signingspace_radio)

        # signingspaceoptions_spacedlayout = QHBoxLayout()
        # signingspaceoptions_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        # signingspaceoptions_layout = QVBoxLayout()
        self.signingspacebody_radio = QRadioButton('body-anchored  /')
        self.signingspacebody_radio.setProperty('loctype', 'signingspace_body')
        # loctype_layout.addWidget(self.signingspacebody_radio)
        signingspace_layout.addWidget(self.signingspacebody_radio)
        self.signingspacespatial_radio = QRadioButton('purely spatial  )')
        self.signingspacespatial_radio.setProperty('loctype', 'signingspace_spatial')
        # loctype_layout.addWidget(self.signingspacespatial_radio)
        signingspace_layout.addWidget(self.signingspacespatial_radio)
        # signingspaceoptions_spacedlayout.addLayout(signingspaceoptions_layout)
        # signingspace_layout.addLayout(signingspaceoptions_spacedlayout)
        # loctype_layout.addLayout(signingspace_layout)
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
        # loctype_layout.addWidget(self.bodyanchored_radio)
        # loctype_layout.addWidget(self.signingspace_radio)
        # loctype_layout.addWidget(self.signingspacebody_radio)
        # loctype_layout.addWidget(self.signingspacespatial_radio)

        phonlocn_layout = QVBoxLayout()
        self.majorphonloc_cb = QCheckBox("Major phonological location")
        self.minorphonloc_cb = QCheckBox("Minor phonological location")
        phonlocn_layout.addWidget(self.majorphonloc_cb, alignment=Qt.AlignHCenter)
        phonlocn_layout.addWidget(self.minorphonloc_cb, alignment=Qt.AlignHCenter)
        loctype_phonloc_layout.addLayout(phonlocn_layout)
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

        self.detailslistview = QListView()
        # TODO KV set model, checkboxes, etc

        list_layout.addWidget(self.detailslistview)

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
        self.detailslistview.setEnabled(enable)
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
            menu = QMenu()

            # self.testaction = QAction('test action', menu, checkable=True)
            # # viewStatAct.setStatusTip('View statusbar')
            # self.testaction.setChecked(self.temptestactionstate)
            # self.testaction.triggered.connect(self.testaction_toggled)
            # menu.addAction(self.testaction)

            self.uncertain_action = CheckNoteAction("Uncertain")
            self.uncertain_action.setChecked(self.uncertain_action_state)
            self.uncertain_action.setText(self.uncertain_action_text)
            self.uncertain_action.toggled.connect(lambda state: self.checknoteaction_toggled(state, self.uncertain_action))
            menu.addAction(self.uncertain_action)

            self.estimate_action = CheckNoteAction("Estimate")
            self.estimate_action.setChecked(self.estimate_action_state)
            self.estimate_action.setText(self.estimate_action_text)
            self.estimate_action.toggled.connect(lambda state: self.checknoteaction_toggled(state, self.estimate_action))
            menu.addAction(self.estimate_action)

            self.notspecified_action = CheckNoteAction("Not specified")
            self.notspecified_action.setChecked(self.notspecified_action_state)
            self.notspecified_action.setText(self.notspecified_action_text)
            self.notspecified_action.toggled.connect(lambda state: self.checknoteaction_toggled(state, self.notspecified_action))
            menu.addAction(self.notspecified_action)

            self.varies_action = CheckNoteAction("Varies morphologically")
            self.varies_action.setChecked(self.varies_action_state)
            self.varies_action.setText(self.varies_action_text)
            self.varies_action.toggled.connect(lambda state: self.checknoteaction_toggled(state, self.varies_action))
            menu.addAction(self.varies_action)

            self.exceptional_action = CheckNoteAction("Mark as exceptional")
            self.exceptional_action.setChecked(self.exceptional_action_state)
            self.exceptional_action.setText(self.exceptional_action_text)
            self.exceptional_action.toggled.connect(lambda state: self.checknoteaction_toggled(state, self.exceptional_action))
            menu.addAction(self.exceptional_action)

            #
            # uncertain_action = menu.addAction("Uncertain")  # , checkable=True)
            # uncertain_action.setCheckable(True)
            # # menu.addAction(uncertain_action)
            # estimate_action = QAction("Estimate", checkable=True)
            # # estimate_action.setCheckable(True)
            # menu.addAction(estimate_action)
            # notspecified_action = QAction("Not specified", checkable=True)
            # # notspecified_action.setCheckable(True)
            # menu.addAction(notspecified_action)
            # variesmorph_action = QAction("Varies morphologically", checkable=True)
            # # variesmorph_action.setCheckable(True)
            # menu.addAction(variesmorph_action)
            # markexcept_action = QAction("Mark as exceptional", checkable=True)
            # # markexcept_action.setCheckable(True)
            # menu.addAction(markexcept_action)

            menu.aboutToHide.connect(self.savemenunotes)

            if menu.exec_(event.globalPos()):  # if a menu item is clicked on
                proxyindex = self.pathslistview.currentIndex()
                listindex = proxyindex.model().mapToSource(proxyindex)
                # TODO KV do something with the item!    vvv
                #  print("selected: " + listindex.model().itemFromIndex(listindex).text())
            return True

        return super().eventFilter(source, event)

    def savemenunotes(self):
        # self.checknoteactiontext = self.checknoteaction.text()
        self.uncertain_action_text = self.uncertain_action.text()
        self.estimate_action_text = self.estimate_action.text()
        self.notspecified_action_text = self.notspecified_action.text()
        self.varies_action_text = self.varies_action.text()
        self.exceptional_action_text = self.exceptional_action.text()

    def testaction_toggled(self, state):
        self.temptestactionstate = state

    # def checknoteaction_textchanged(self, text):
    #     print("checknoteaction's new text is: " + text)
    #     self.checknoteactiontext = text

    def checknoteaction_toggled(self, state, whichaction):
        if whichaction == self.uncertain_action:
            self.uncertain_action_state = state
        elif whichaction == self.estimate_action:
            self.estimate_action_state = state
        elif whichaction == self.varies_action:
            self.varies_action_state = state
        elif whichaction == self.exceptional_action:
            self.exceptional_action_state = state
        elif whichaction == self.notspecified_action:
            self.notspecified_action_state = state

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


class CheckNoteAction(QWidgetAction):
    textChanged = pyqtSignal(str)

    def __init__(self, text, parent=None):
        super().__init__(parent)

        actionwidget = QWidget()
        actionlayout = QHBoxLayout()
        self.checkbox = QCheckBox(text)
        self.checkbox.setTristate(False)
        self.checkbox.toggled.connect(self.toggled)
        self.note = QLineEdit()
        self.note.textChanged.connect(self.textChanged.emit)
        actionlayout.addWidget(self.checkbox)
        actionlayout.addWidget(self.note)
        actionwidget.setLayout(actionlayout)
        self.setDefaultWidget(actionwidget)

    def getCheckbox(self):
        return self.checkbox

    def getNote(self):
        return self.note

    def setChecked(self, state):
        self.checkbox.setChecked(state)

    def isChecked(self):
        return self.checkbox.isChecked()

    def setText(self, text):
        self.note.setText(text)

    def text(self):
        return self.note.text()
