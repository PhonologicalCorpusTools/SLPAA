from copy import deepcopy

from PyQt5.QtWidgets import (
    QFrame,
    QRadioButton,
    QDialog,
    QWidget,
    QSpacerItem,
    QSizePolicy,
    QHBoxLayout,
    QVBoxLayout,
    QMessageBox,
    QDialogButtonBox,
    QLabel,
    QButtonGroup,
    QCheckBox,
    QGraphicsView
)

from PyQt5.QtCore import (
    Qt,
    pyqtSignal
)

from gui.xslot_graphics import XslotLinkScene
from lexicon.module_classes import AddedInfo, TimingInterval, TimingPoint, ParameterModule
from gui.movementspecification_view import MovementSpecificationPanel
from gui.locationspecification_view import LocationSpecificationPanel
from gui.handconfigspecification_view import HandConfigSpecificationPanel
from gui.modulespecification_widgets import AddedInfoPushButton


class ModuleSelectorDialog(QDialog):
    module_saved = pyqtSignal(ParameterModule)
    module_deleted = pyqtSignal()

    def __init__(self, moduletype, xslotstructure=None, moduletoload=None, includephase=0, **kwargs):
        super().__init__(**kwargs)
        self.mainwindow = self.parent().mainwindow

        timingintervals = []
        addedinfo = AddedInfo()
        new_instance = True
        hands = None
        inphase = 0

        if moduletoload is not None:
            timingintervals = deepcopy(moduletoload.timingintervals)
            addedinfo = deepcopy(moduletoload.addedinfo)
            hands = moduletoload.hands
            new_instance = False

        main_layout = QVBoxLayout()

        self.hands_and_addedinfo_layout = QHBoxLayout()

        self.hands_widget = HandSelectionPanel(hands=hands, includephase=includephase, inphase=inphase, parent=self)
        self.hands_and_addedinfo_layout.addWidget(self.hands_widget)

        self.hands_and_addedinfo_layout.addStretch()
        self.addedinfobutton = AddedInfoPushButton("Module notes")
        self.addedinfobutton.addedinfo = addedinfo
        self.hands_and_addedinfo_layout.addWidget(self.addedinfobutton)
        self.hands_and_addedinfo_layout.setAlignment(self.addedinfobutton, Qt.AlignTop)

        main_layout.addLayout(self.hands_and_addedinfo_layout)

        self.xslot_widget = XslotLinkingPanel(xslotstructure=xslotstructure,
                                              timingintervals=timingintervals,
                                              parent=self)
        if self.mainwindow.app_settings['signdefaults']['xslot_generation'] != 'none':
            main_layout.addWidget(self.xslot_widget)

        self.module_widget = QWidget()
        if moduletype == 'Mov':
            self.module_widget = MovementSpecificationPanel(moduletoload=moduletoload, parent=self)
        elif moduletype == 'Loc':
            self.module_widget = LocationSpecificationPanel(moduletoload=moduletoload, parent=self)
        elif moduletype == 'Config':
            self.module_widget = HandConfigSpecificationPanel(moduletoload=moduletoload, parent=self)
        main_layout.addWidget(self.module_widget)

        separate_line = QFrame()
        separate_line.setFrameShape(QFrame.HLine)
        separate_line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separate_line)

        # If we're creating a brand new instance of a module, then we want a
        #   "Save and Add Another" button, to allow the user to continue adding new instances.
        # On the other hand, if we're editing an existing instance of a module, then instead we want a
        #   "Delete" button, in case the user wants to delete the instance rather than editing it.
        buttons = None
        applytext = ""
        discardtext = "Delete"
        if new_instance:
            buttons = QDialogButtonBox.RestoreDefaults | QDialogButtonBox.Save | QDialogButtonBox.Apply | QDialogButtonBox.Cancel
            applytext = "Save and close"
        else:
            buttons = QDialogButtonBox.RestoreDefaults | QDialogButtonBox.Discard | QDialogButtonBox.Apply | QDialogButtonBox.Cancel
            applytext = "Save"

        self.button_box = QDialogButtonBox(buttons, parent=self)
        if new_instance:
            self.button_box.button(QDialogButtonBox.Save).setText("Save and add another")
        else:
            self.button_box.button(QDialogButtonBox.Discard).setText(discardtext)
        self.button_box.button(QDialogButtonBox.Apply).setDefault(True)
        self.button_box.button(QDialogButtonBox.Apply).setText(applytext)

        # TODO KV keep? from orig locationdefinerdialog:
        #      Ref: https://programtalk.com/vs2/python/654/enki/enki/core/workspace.py/
        self.button_box.clicked.connect(self.handle_button_click)

        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)
        # self.setMinimumSize(QSize(500, 700))
        # # self.setMinimumSize(modulelayout.desiredwidth(), modulelayout.desiredheight())
        # self.setMinimumSize(QSize(modulelayout.rect().width(), modulelayout.rect().height()))
        # self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.adjustSize()

    def handle_button_click(self, button):
        standard = self.button_box.standardButton(button)

        if standard == QDialogButtonBox.Cancel:
            self.reject()

        elif standard == QDialogButtonBox.Discard:
            self.module_deleted.emit()
            self.accept()  # TODO KV ???

        # TODO KV this duplicates the code in the next conditional case
        elif standard == QDialogButtonBox.Save:  # save and add another

            # validate hand selection
            handsdict = self.hands_widget.gethands()
            handsvalid = True
            if True not in handsdict.values():
                handsvalid = False

            inphase = self.hands_widget.getphase()
            addedinfo = self.addedinfobutton.addedinfo

            # validate timing interval(s) selection
            timingintervals = self.xslot_widget.gettimingintervals()
            timingvalid = True
            if len(timingintervals) == 0 and self.mainwindow.app_settings['signdefaults']['xslot_generation'] != 'none':
                timingvalid = False
            elif self.mainwindow.app_settings['signdefaults']['xslot_generation'] == 'none':
                # no x-slots; make the timing interval be for the whole sign
                timingintervals = [TimingInterval(TimingPoint(0, 0), TimingPoint(1, 0))]

            if not (handsvalid and timingvalid):
                # refuse to save without hand & timing info
                messagestring = "Missing"
                messagestring += " hand selection" if not handsvalid else ""
                messagestring += " and" if not (handsvalid or timingvalid) else ""
                messagestring += " timing selection" if not timingvalid else ""
                messagestring += "."
                QMessageBox.critical(self, "Warning", messagestring)
            else:
                # save info and then refresh screen to start next module
                self.module_saved.emit(self.module_widget.getsavedmodule(handsdict, timingintervals, addedinfo, inphase))
                self.hands_widget.clear()
                self.addedinfobutton.clear()
                self.xslot_widget.clear()
                self.module_widget.clear()

        elif standard == QDialogButtonBox.Apply:  # save and close

            # validate hand selection
            handsdict = self.hands_widget.gethands()
            handsvalid = True
            if True not in handsdict.values():
                handsvalid = False

            inphase = self.hands_widget.getphase()
            addedinfo = self.addedinfobutton.addedinfo

            # validate timing interval(s) selection
            timingintervals = self.xslot_widget.gettimingintervals()
            timingvalid = True
            if len(timingintervals) == 0 and self.mainwindow.app_settings['signdefaults']['xslot_generation'] != 'none':
                timingvalid = False
            elif self.mainwindow.app_settings['signdefaults']['xslot_generation'] == 'none':
                # no x-slots; make the timing interval be for the whole sign
                timingintervals = [TimingInterval(TimingPoint(0, 0), TimingPoint(1, 0))]

            if not (handsvalid and timingvalid):
                # refuse to save without hand & timing info
                messagestring = "Missing"
                messagestring += " hand selection" if not handsvalid else ""
                messagestring += " and" if not (handsvalid or timingvalid) else ""
                messagestring += " timing selection" if not timingvalid else ""
                messagestring += "."
                QMessageBox.critical(self, "Warning", messagestring)
            else:
                # save info and then close dialog
                self.module_saved.emit(self.module_widget.getsavedmodule(handsdict, timingintervals, addedinfo, inphase))
                self.accept()

        elif standard == QDialogButtonBox.RestoreDefaults:  # restore defaults
            # TODO KV -- where should the "defaults" be defined?
            self.hands_widget.clear()
            self.addedinfobutton.clear()
            self.xslot_widget.clear()
            self.module_widget.clear()


class XslotLinkingPanel(QFrame):

    def __init__(self, xslotstructure, timingintervals=None, **kwargs):
        super().__init__(**kwargs)
        self.mainwindow = self.parent().mainwindow

        self.timingintervals = [] if timingintervals is None else timingintervals
        xslotstruct = self.mainwindow.current_sign.xslotstructure
        if xslotstruct is None:
            print("no x-slot structure!")

        main_layout = QVBoxLayout()

        self.link_intro_label = QLabel("Click on the relevant point(s) or interval(s) to link this module.")
        main_layout.addWidget(self.link_intro_label)

        self.xslotlinkscene = XslotLinkScene(timingintervals=self.timingintervals, parentwidget=self)
        self.xslotlinkview = QGraphicsView(self.xslotlinkscene)
        self.xslotlinkview.setFixedHeight(self.xslotlinkscene.scene_height + 50)
        # self.xslotlinkview.setFixedSize(self.xslotlinkscene.scene_width+100, self.xslotlinkscene.scene_height+50)
        # self.xslotlinkview.setSceneRect(0, 0, self.xslotlinkscene.scene_width, self.xslotlinkscene.scene_height)
        # self.xslotlinkview.fitInView(0, 0, self.xslotlinkscene.scene_width, self.xslotlinkscene.scene_height, Qt.KeepAspectRatio)
        # self.xslotvlinkview.setGeometry(0, 0, self.xslotlinkscene.scene_width, self.xslotlinkscene.scene_height)
        main_layout.addWidget(self.xslotlinkview)

        self.setLayout(main_layout)

    def gettimingintervals(self):
        return self.xslotlinkscene.xslotlinks

    def clear(self):
        self.xslotlinkscene = XslotLinkScene(parentwidget=self, timingintervals=[])
        self.xslotlinkview.setScene(self.xslotlinkscene)


# TODO KV - need to pull phase info from here as well as hands info
class HandSelectionPanel(QFrame):

    def __init__(self, hands=None, includephase=0, inphase=0, **kwargs):
        super().__init__(**kwargs)

        self.include_bothhands_suboptions = 0
        if isinstance(includephase, bool) and includephase:
            self.include_bothhands_suboptions = 2
        elif isinstance(includephase, int):
            self.include_bothhands_suboptions = includephase
        # self.include_bothhands_suboptions...
        # 0 --> do not include [previously includephase=False]
        # 1 --> include only "As a connected unit"
        # 2 --> include both "As a connected unit" and "in phase" / "out of phase" [previously includephase=True]

        self.hands_label = QLabel("This module applies to:")

        self.hands_group = QButtonGroup()
        self.hand1_radio = QRadioButton("Hand 1")
        self.hand2_radio = QRadioButton("Hand 2")
        self.bothhands_radio = QRadioButton("Both hands")
        self.hands_group.addButton(self.hand1_radio)
        self.hands_group.addButton(self.hand2_radio)
        self.hands_group.addButton(self.bothhands_radio)
        self.hands_group.buttonToggled.connect(self.handle_handsgroup_toggled)

        # won't get displayed/used for all module types, but they are instantiated nonetheless to avoid potential reference errors
        self.bothhands_group = QButtonGroup()
        self.bothhands_group.setExclusive(False)
        self.bothhands_group.buttonToggled.connect(self.handle_bothhandsgroup_toggled)
        self.bothconnected_cb = QCheckBox("As a connected unit")
        self.bothinphase_cb = QCheckBox("In phase")
        self.bothoutofphase_radio = QRadioButton("Out of phase")
        self.bothhands_group.addButton(self.bothconnected_cb)
        self.bothhands_group.addButton(self.bothinphase_cb)
        self.bothhands_group.addButton(self.bothoutofphase_radio)

        main_layout = QHBoxLayout()

        # for most module types-- just H1, H2, Both
        if self.include_bothhands_suboptions == 0:
            main_layout.addWidget(self.hands_label)
            main_layout.addWidget(self.hand1_radio)
            main_layout.addWidget(self.hand2_radio)
            main_layout.addWidget(self.bothhands_radio)

        # for (eg) movement or location -- H1, H2, Both (plus one or more suboptions)
        # self.include_bothhands_suboptions is 1 (only one suboption: Connected) or 2 (several suboptions: Connected, In Phase, Out of Phase)
        else:
            hands_layout = QHBoxLayout()

            hands_layout.addWidget(self.hands_label)
            hands_layout.addWidget(self.hand1_radio)
            hands_layout.addWidget(self.hand2_radio)

            # hands_layout.addStretch()
            main_layout.addLayout(hands_layout)
            main_layout.setAlignment(hands_layout, Qt.AlignTop)

            bothhands_layout = QVBoxLayout()
            bothhands_layout.addWidget(self.bothhands_radio)
            bothhands_sub_spacedlayout = QHBoxLayout()
            bothhands_sub_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
            bothhands_sub_layout = QVBoxLayout()
            bothhands_sub_layout.addWidget(self.bothconnected_cb)
            if self.include_bothhands_suboptions == 2:
                bothhands_sub_layout.addWidget(self.bothinphase_cb)
                bothhands_sub_layout.addWidget(self.bothoutofphase_radio)
            bothhands_sub_spacedlayout.addLayout(bothhands_sub_layout)
            bothhands_layout.addLayout(bothhands_sub_spacedlayout)

            main_layout.addLayout(bothhands_layout)

        self.setLayout(main_layout)
        # self.addStretch()

        if hands is not None:
            self.sethands(hands)
        self.setphase(inphase)

    def handle_handsgroup_toggled(self, btn, ischecked):
        selectedbutton = self.hands_group.checkedButton()
        if selectedbutton == self.bothhands_radio:
            # enable sub options
            for btn in self.bothhands_group.buttons():
                btn.setEnabled(True)
        else:
            # disable sub options
            for btn in self.bothhands_group.buttons():
                btn.setEnabled(False)

    def handle_bothhandsgroup_toggled(self, btn, ischecked):
        if not ischecked:
            # don't need to do anything special
            return

        # ensure the parent is checked
        self.bothhands_radio.setChecked(True)
        siblings = [b for b in self.bothhands_group.buttons() if b != btn]

        if isinstance(btn, QCheckBox):
            # uncheck any radio button siblings
            for sib in siblings:
                if isinstance(sib, QRadioButton):
                    sib.setChecked(False)

        elif isinstance(btn, QRadioButton):
            # uncheck *all* other siblings
            for sib in siblings:
                sib.setChecked(False)

    def gethands(self):
        both = self.bothhands_radio.isChecked()  #  or self.bothinphase_radio.isChecked() or self.bothoutofphase_radio.isChecked()
        return {
            'H1': self.hand1_radio.isChecked() or both,
            'H2': self.hand2_radio.isChecked() or both
        }

    def sethands(self, hands_dict):
        if hands_dict['H1'] and hands_dict['H2']:
            self.bothhands_radio.setChecked(True)
        elif hands_dict['H1']:
            self.hand1_radio.setChecked(True)
        elif hands_dict['H2']:
            self.hand2_radio.setChecked(True)

    def getphase(self):
        if not self.bothconnected_cb.isChecked():
            # original options - these are mutually exclusive
            if self.bothinphase_cb.isChecked():
                return 1
            elif self.bothoutofphase_radio.isChecked():
                return 2
            else:
                return 0
        elif self.bothconnected_cb.isChecked():
            # these are mutually exclusive
            if self.bothinphase_cb.isChecked():
                return 4
            elif self.bothoutofphase_radio.isChecked():
                # it shouldn't be possible to have both "connected" and "out of phase" checked, but... just in case?
                return 5
            else:
                return 3

    def setphase(self, inphase):
        self.bothconnected_cb.setChecked((inphase >= 3))

        if inphase % 3 == 1:
            self.bothinphase_cb.setChecked(True)
        elif inphase % 3 == 2:
            self.bothoutofphase_radio.setChecked(True)

    def clear(self):
        self.hands_group.setExclusive(False)
        for b in self.hands_group.buttons() + self.bothhands_group.buttons():
            b.setChecked(False)
        self.hands_group.setExclusive(True)
