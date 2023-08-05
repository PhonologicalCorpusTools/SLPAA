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
    QComboBox,
    QGraphicsView
)

from PyQt5.QtCore import (
    Qt,
    pyqtSignal
)

from gui.xslot_graphics import XslotLinkScene
from lexicon.module_classes import AddedInfo, TimingInterval, TimingPoint, ParameterModule, ModuleTypes
from gui.movementspecification_view import MovementSpecificationPanel
from gui.locationspecification_view import LocationSpecificationPanel
from gui.handconfigspecification_view import HandConfigSpecificationPanel
from gui.modulespecification_widgets import AddedInfoPushButton
from constant import HAND, ARM, LEG


class ModuleSelectorDialog(QDialog):
    module_saved = pyqtSignal(ParameterModule)
    module_deleted = pyqtSignal()

    def __init__(self, moduletype, xslotstructure=None, moduletoload=None, incl_articulators=HAND, incl_articulator_subopts=0, **kwargs):
        super().__init__(**kwargs)
        self.mainwindow = self.parent().mainwindow

        timingintervals = []
        addedinfo = AddedInfo()
        new_instance = True
        articulators = (None, {1: None, 2: None})
        inphase = 0
        if isinstance(incl_articulators, str):
            incl_articulators = [incl_articulators]

        if moduletoload is not None:
            timingintervals = deepcopy(moduletoload.timingintervals)
            addedinfo = deepcopy(moduletoload.addedinfo)
            articulators = moduletoload.articulators
            new_instance = False
            if hasattr(moduletoload, '_inphase'):
                inphase = moduletoload.inphase

        main_layout = QVBoxLayout()

        self.arts_and_addedinfo_layout = QHBoxLayout()
        self.articulators_widget = ArticulatorSelectionPanel(available_articulators=incl_articulators,
                                                             articulators=articulators,
                                                             incl_articulator_subopts=incl_articulator_subopts,
                                                             inphase=inphase,
                                                             parent=self)
        self.arts_and_addedinfo_layout.addWidget(self.articulators_widget)

        self.arts_and_addedinfo_layout.addStretch()
        self.addedinfobutton = AddedInfoPushButton("Module notes")
        self.addedinfobutton.addedinfo = addedinfo
        self.arts_and_addedinfo_layout.addWidget(self.addedinfobutton)
        self.arts_and_addedinfo_layout.setAlignment(self.addedinfobutton, Qt.AlignTop)

        main_layout.addLayout(self.arts_and_addedinfo_layout)

        self.xslot_widget = XslotLinkingPanel(xslotstructure=xslotstructure,
                                              timingintervals=timingintervals,
                                              parent=self)
        if self.mainwindow.app_settings['signdefaults']['xslot_generation'] != 'none':
            main_layout.addWidget(self.xslot_widget)

        self.module_widget = QWidget()
        if moduletype == ModuleTypes.MOVEMENT:
            self.module_widget = MovementSpecificationPanel(moduletoload=moduletoload, parent=self)
        elif moduletype == ModuleTypes.LOCATION:
            self.module_widget = LocationSpecificationPanel(moduletoload=moduletoload, parent=self)
        elif moduletype == ModuleTypes.HANDCONFIG:
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
            articulator, articulator_dict = self.articulators_widget.getarticulators()
            articulatorsvalid = True
            if articulator is None or True not in articulator_dict.values():
                articulatorsvalid = False

            inphase = self.articulators_widget.getphase()
            addedinfo = self.addedinfobutton.addedinfo

            # validate timing interval(s) selection
            timingintervals = self.xslot_widget.gettimingintervals()
            timingvalid = True
            if len(timingintervals) == 0 and self.mainwindow.app_settings['signdefaults']['xslot_generation'] != 'none':
                timingvalid = False
            elif self.mainwindow.app_settings['signdefaults']['xslot_generation'] == 'none':
                # no x-slots; make the timing interval be for the whole sign
                timingintervals = [TimingInterval(TimingPoint(0, 0), TimingPoint(1, 0))]

            if not (articulatorsvalid and timingvalid):
                # refuse to save without hand & timing info
                messagestring = "Missing"
                messagestring += " hand selection" if not articulatorsvalid else ""
                messagestring += " and" if not (articulatorsvalid or timingvalid) else ""
                messagestring += " timing selection" if not timingvalid else ""
                messagestring += "."
                QMessageBox.critical(self, "Warning", messagestring)
            else:
                # save info and then refresh screen to start next module
                self.module_saved.emit(self.module_widget.getsavedmodule((articulator, articulator_dict), timingintervals, addedinfo, inphase))
                self.articulators_widget.clear()
                self.addedinfobutton.clear()
                self.xslot_widget.clear()
                self.module_widget.clear()

        elif standard == QDialogButtonBox.Apply:  # save and close

            # validate articulator selection
            articulator, articulator_dict = self.articulators_widget.getarticulators()
            articulatorsvalid = True
            if articulator is None or True not in articulator_dict.values():
                articulatorsvalid = False

            inphase = self.articulators_widget.getphase()
            addedinfo = self.addedinfobutton.addedinfo

            # validate timing interval(s) selection
            timingintervals = self.xslot_widget.gettimingintervals()
            timingvalid = True
            if len(timingintervals) == 0 and self.mainwindow.app_settings['signdefaults']['xslot_generation'] != 'none':
                timingvalid = False
            elif self.mainwindow.app_settings['signdefaults']['xslot_generation'] == 'none':
                # no x-slots; make the timing interval be for the whole sign
                timingintervals = [TimingInterval(TimingPoint(0, 0), TimingPoint(1, 0))]

            if not (articulatorsvalid and timingvalid):
                # refuse to save without hand & timing info
                messagestring = "Missing"
                messagestring += " hand selection" if not articulatorsvalid else ""
                messagestring += " and" if not (articulatorsvalid or timingvalid) else ""
                messagestring += " timing selection" if not timingvalid else ""
                messagestring += "."
                QMessageBox.critical(self, "Warning", messagestring)
            else:
                # save info and then close dialog
                self.module_saved.emit(self.module_widget.getsavedmodule((articulator, articulator_dict), timingintervals, addedinfo, inphase))
                self.accept()

        elif standard == QDialogButtonBox.RestoreDefaults:  # restore defaults
            # TODO KV -- where should the "defaults" be defined?
            self.articulators_widget.clear()
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


class ArticulatorSelector(QWidget):
    articulatorchanged = pyqtSignal(str)

    def __init__(self, articulatorlist, **kwargs):
        super().__init__(**kwargs)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.multiple = len(articulatorlist) > 1

        self.label = QLabel()
        self.combo = QComboBox()
        self.combo.setEditable(False)
        self.combo.currentTextChanged.connect(lambda text: self.articulatorchanged.emit(self.pluralbrackets(text, False)))
        self.setarticulatoroptions(articulatorlist)

    def pluralbrackets(self, text, onoroff):
        if onoroff:
            return text + "(s)"
        else:
            return text.replace("(s)", "")

    def gettext(self):
        if self.multiple:
            return self.combo.currentText()
        else:
            return self.label.text()

    def getarticulator(self):
        return self.pluralbrackets(self.gettext(), False)

    def setarticulatoroptions(self, articulatorlist):
        self.multiple = len(articulatorlist) > 1
        for idx in range(self.layout.count()):
            w = self.layout.itemAt(idx).widget()
            self.layout.removeWidget(w)

        if self.multiple:
            self.combo.clear()
            self.combo.addItems([self.pluralbrackets(a, True) for a in articulatorlist])
            self.layout.addWidget(self.combo)
        else:
            self.label.clear()
            self.label.setText(self.pluralbrackets(articulatorlist[0], True) or "")
            self.layout.addWidget(self.label)

    # def articulatorat(self, idx):
    #     return self.pluralbrackets(self.combo.itemText(0), False)

    def setselectedarticulator(self, articulator):
        if articulator is None or articulator == "":
            text = self.combo.itemText(0)
        else:
            text = self.pluralbrackets(articulator, True)
        if self.multiple:
            if text in [self.combo.itemText(i) for i in range(self.combo.count())]:
                self.combo.setCurrentText(text)
                return True
        else:
            if text == self.label.text():
                return True

        return False



# TODO KV - need to pull phase info from here as well as hands info
class ArticulatorSelectionPanel(QFrame):

    def __init__(self, available_articulators=None, articulators=None, incl_articulator_subopts=0, inphase=0, **kwargs):
        super().__init__(**kwargs)

        self.incl_articulator_subopts = 0
        if isinstance(incl_articulator_subopts, bool):
            print("temp: incl_articulator_subopts is a bool")
        if isinstance(incl_articulator_subopts, bool) and incl_articulator_subopts:
            self.incl_articulator_subopts = 2
        elif isinstance(incl_articulator_subopts, int):
            self.incl_articulator_subopts = incl_articulator_subopts
        # self.incl_articulator_subopts...
        # 0 --> do not include any suboptions for "both" [previously includephase=False]
        # 1 --> include only "As a connected unit"
        # 2 --> include both "As a connected unit" and "in phase" / "out of phase" [previously includephase=True]
        #
        # if available_articulators is None or len(available_articulators) == 0:
        #     available_articulators = [HAND, ARM, LEG]
        # self.articulator_selector = ArticulatorSelector(available_articulators)
        # self.articulator_selector.articulatorchanged.connect(self.handle_articulator_changed)

        articulator_layout = self.create_articulator_layout(available_articulators)
        self.setLayout(articulator_layout)
        self.handle_articulator_changed(available_articulators[0])

        self.setarticulators(articulators)
        self.setphase(inphase)

    def create_articulator_layout(self, available_articulators):
        self.appliesto_label = QLabel("This module applies to:")

        if available_articulators is None or len(available_articulators) == 0:
            available_articulators = [HAND, ARM, LEG]
        self.articulator_selector = ArticulatorSelector(available_articulators)
        self.articulator_selector.articulatorchanged.connect(self.handle_articulator_changed)

        self.articulator_group = QButtonGroup()
        self.articulator1_radio = QRadioButton("Articulator 1")
        self.articulator2_radio = QRadioButton("Articulator 2")
        self.botharts_radio = QRadioButton("Both articualtors")
        self.articulator_group.addButton(self.articulator1_radio)
        self.articulator_group.addButton(self.articulator2_radio)
        self.articulator_group.addButton(self.botharts_radio)
        self.articulator_group.buttonToggled.connect(self.handle_articulatorgroup_toggled)

        # won't get displayed/used for all module types, but they are instantiated nonetheless to avoid potential reference errors
        self.botharts_group = QButtonGroup()
        self.botharts_group.setExclusive(False)
        self.botharts_connected_cb = QCheckBox("As a connected unit")
        self.botharts_inphase_cb = QCheckBox("In phase")
        self.botharts_outofphase_radio = QRadioButton("Out of phase")
        self.botharts_group.addButton(self.botharts_connected_cb)
        self.botharts_group.addButton(self.botharts_inphase_cb)
        self.botharts_group.addButton(self.botharts_outofphase_radio)
        self.botharts_group.buttonToggled.connect(self.handle_bothgroup_toggled)

        articulator_layout = QHBoxLayout()

        singlearts_layout = QHBoxLayout()
        singlearts_layout.addWidget(self.appliesto_label)
        singlearts_layout.addWidget(self.articulator_selector)
        singlearts_layout.addWidget(self.articulator1_radio)
        singlearts_layout.addWidget(self.articulator2_radio)
        articulator_layout.addLayout(singlearts_layout)
        articulator_layout.setAlignment(singlearts_layout, Qt.AlignTop)

        # # for most module types-- just Articulator1, Articulator2, Both
        # if self.incl_articulator_subopts == 0:
        #     articulator_layout.addWidget(self.articulator1_radio)
        #     articulator_layout.addWidget(self.articulator2_radio)
        #     articulator_layout.addWidget(self.botharts_radio)
        #
        # # for (eg) movement or location -- Articulator1, Articulator2, Both (plus one or more suboptions)
        # # self.incl_articulator_subopts is 1 (only one suboption: Connected) or 2 (several suboptions: Connected, In Phase, Out of Phase)
        # else:
        # if self.incl_articulator_subopts > 0:
            # articulator_layout.addWidget(self.articulator1_radio)
            # articulator_layout.addWidget(self.articulator2_radio)
        botharts_layout = QVBoxLayout()
        botharts_layout.addWidget(self.botharts_radio)
        if self.incl_articulator_subopts > 0:
            botharts_sub_spacedlayout = QHBoxLayout()
            botharts_sub_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
            botharts_sub_layout = QVBoxLayout()
            botharts_sub_layout.addWidget(self.botharts_connected_cb)
            if self.incl_articulator_subopts == 2:
                botharts_sub_layout.addWidget(self.botharts_inphase_cb)
                botharts_sub_layout.addWidget(self.botharts_outofphase_radio)
            botharts_sub_spacedlayout.addLayout(botharts_sub_layout)
            botharts_layout.addLayout(botharts_sub_spacedlayout)

        articulator_layout.addLayout(botharts_layout)

        articulator_layout.setAlignment(self.articulator1_radio, Qt.AlignTop)
        articulator_layout.setAlignment(self.articulator2_radio, Qt.AlignTop)

        return articulator_layout

    def handle_articulator_changed(self, articulator):

        self.articulator1_radio.setText(articulator + " 1")
        self.articulator2_radio.setText(articulator + " 2")
        self.botharts_radio.setText("Both " + articulator.lower() + "s")

    #     if hands is not None:
    #         self.setarticulators("Hand", hands)
    #     self.setarticulatorphase("Hand", handsinphase)
    #
    #     if arms is not None:
    #         self.setarticulators("Arm", arms)
    #     self.setarticulatorphase("Arm", armsinphase)
    #
    #     if legs is not None:
    #         self.setarticulators("Leg", legs)
    #     self.setarticulatorphase("Leg", legsinphase)
    #
    # def create_articulator_layout(self,
    #                               articulator_name,
    #                               articulator_group,
    #                               articulator1_radio,
    #                               articulator2_radio,
    #                               both_radio,
    #                               both_group,
    #                               both_connected_cb,
    #                               both_inphase_cb,
    #                               both_outofphase_radio):
    #
    #     articulator_layout = QVBoxLayout()
    #
    #     articulator_group.addButton(articulator1_radio)
    #     articulator_group.addButton(articulator2_radio)
    #     articulator_group.addButton(both_radio)
    #     articulator_group.buttonToggled.connect(lambda btn, ischecked: self.handle_articulatorgroup_toggled(articulator_name))
    #
    #     # won't get displayed/used for all module types, but they are instantiated nonetheless to avoid potential reference errors
    #     both_group.setExclusive(False)
    #     both_group.buttonToggled.connect(lambda btn, ischecked: self.handle_bothgroup_toggled(articulator_name, btn, ischecked))
    #     both_group.addButton(both_connected_cb)
    #     both_group.addButton(both_inphase_cb)
    #     both_group.addButton(both_outofphase_radio)
    #
    #     # for most module types-- just Articulator1, Articulator2, Both
    #     if self.incl_articulator_subopts == 0:
    #         articulator_layout.addWidget(articulator1_radio)
    #         articulator_layout.addWidget(articulator2_radio)
    #         articulator_layout.addWidget(both_radio)
    #
    #     # for (eg) movement or location -- Articulator1, Articulator2, Both (plus one or more suboptions)
    #     # self.incl_articulator_subopts is 1 (only one suboption: Connected) or 2 (several suboptions: Connected, In Phase, Out of Phase)
    #     else:
    #         articulator_layout.addWidget(articulator1_radio)
    #         articulator_layout.addWidget(articulator2_radio)
    #         botharts_layout = QVBoxLayout()
    #         botharts_layout.addWidget(both_radio)
    #         botharts_sub_spacedlayout = QHBoxLayout()
    #         botharts_sub_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
    #         botharts_sub_layout = QVBoxLayout()
    #         botharts_sub_layout.addWidget(both_connected_cb)
    #         if self.incl_articulator_subopts == 2:
    #             botharts_sub_layout.addWidget(both_inphase_cb)
    #             botharts_sub_layout.addWidget(both_outofphase_radio)
    #         botharts_sub_spacedlayout.addLayout(botharts_sub_layout)
    #         botharts_layout.addLayout(botharts_sub_spacedlayout)
    #
    #         articulator_layout.addLayout(botharts_layout)
    #
    #     self.setLayout(articulator_layout)
    #
    #     articulator_group = QButtonGroup()
    #     # self.hand1_radio = QRadioButton("Hand 1")
    #     # self.hand2_radio = QRadioButton("Hand 2")
    #     # self.bothhands_radio = QRadioButton("Both hands")
    #     articulator_group.addButton(articulator1_radio)
    #     articulator_group.addButton(articulator2_radio)
    #     articulator_group.addButton(both_radio)
    #     articulator_group.buttonToggled.connect(self.handle_articulatorsgroup_toggled)
    #
    #     # won't get displayed/used for all module types, but they are instantiated nonetheless to avoid potential reference errors
    #     both_group.setExclusive(False)
    #     both_group.buttonToggled.connect(self.handle_bothhandsgroup_toggled)
    #     # self.bothhands_connected_cb = QCheckBox("As a connected unit")
    #     # self.bothhands_inphase_cb = QCheckBox("In phase")
    #     # self.bothhands_outofphase_radio = QRadioButton("Out of phase")
    #     both_group.addButton(both_connected_cb)
    #     both_group.addButton(both_inphase_cb)
    #     both_group.addButton(both_outofphase_radio)
    #
    #     main_layout = QHBoxLayout()
    #
    #     # for most module types-- just H1, H2, Both
    #     if self.incl_articulator_subopts == 0:
    #         main_layout.addWidget(self.appliesto_label)  # TODO KV how to replace this?
    #         main_layout.addWidget(articulator1_radio)
    #         main_layout.addWidget(articulator2_radio)
    #         main_layout.addWidget(both_radio)
    #
    #     # for (eg) movement or location -- H1, H2, Both (plus one or more suboptions)
    #     # self.include_bothhands_suboptions is 1 (only one suboption: Connected) or 2 (several suboptions: Connected, In Phase, Out of Phase)
    #     else:
    #          # TODO KV continue from here!
    #         hands_layout = QHBoxLayout()
    #
    #         hands_layout.addWidget(self.appliesto_label)
    #         hands_layout.addWidget(self.hand1_radio)
    #         hands_layout.addWidget(self.hand2_radio)
    #
    #         # hands_layout.addStretch()
    #         main_layout.addLayout(hands_layout)
    #         main_layout.setAlignment(hands_layout, Qt.AlignTop)
    #
    #         bothhands_layout = QVBoxLayout()
    #         bothhands_layout.addWidget(self.bothhands_radio)
    #         botharts_sub_spacedlayout = QHBoxLayout()
    #         botharts_sub_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
    #         botharts_sub_layout = QVBoxLayout()
    #         botharts_sub_layout.addWidget(self.bothhands_connected_cb)
    #         if self.incl_articulator_subopts == 2:
    #             botharts_sub_layout.addWidget(self.bothhands_inphase_cb)
    #             botharts_sub_layout.addWidget(self.bothhands_outofphase_radio)
    #         botharts_sub_spacedlayout.addLayout(botharts_sub_layout)
    #         bothhands_layout.addLayout(botharts_sub_spacedlayout)
    #
    #         main_layout.addLayout(bothhands_layout)
    #
    #     self.setLayout(main_layout)
    #     # self.addStretch()
    #
    #     if hands is not None:
    #         self.sethands(hands)
    #     self.setphase(handsinphase)

    def handle_articulatorgroup_toggled(self, btn, ischecked):
        selectedbutton = self.articulator_group.checkedButton()
        if selectedbutton == self.botharts_radio:
            # enable sub options
            for btn in self.botharts_group.buttons():
                btn.setEnabled(True)
        else:
            # disable sub options
            for btn in self.botharts_group.buttons():
                btn.setEnabled(False)

    def handle_bothgroup_toggled(self, btn, ischecked):
        if not ischecked:
            # don't need to do anything special
            return

        # ensure the parent is checked
        self.botharts_radio.setChecked(True)
        siblings = [b for b in self.botharts_group.buttons() if b != btn]

        if isinstance(btn, QCheckBox):
            # uncheck any radio button siblings
            for sib in siblings:
                if isinstance(sib, QRadioButton):
                    sib.setChecked(False)

        elif isinstance(btn, QRadioButton):
            # uncheck *all* other siblings
            for sib in siblings:
                sib.setChecked(False)

    def getarticulators(self):
        selectedarticulator = self.articulator_selector.getarticulator()
        both = self.botharts_radio.isChecked()
        selections_dict = {
            1: self.articulator1_radio.isChecked() or both,
            2: self.articulator2_radio.isChecked() or both
        }
        return selectedarticulator, selections_dict

    def setarticulators(self, articulators):
        selectedarticulator = articulators[0]
        articulators_dict = articulators[1]
        success = self.articulator_selector.setselectedarticulator(selectedarticulator)
        if success and articulators_dict is not None:
            if articulators_dict[1] and articulators_dict[2]:
                self.botharts_radio.setChecked(True)
            elif articulators_dict[1]:
                self.articulator1_radio.setChecked(True)
            elif articulators_dict[2]:
                self.articulator2_radio.setChecked(True)

    # def sethands(self, hands_dict):
    #     if hands_dict['H1'] and hands_dict['H2']:
    #         self.bothhands_radio.setChecked(True)
    #     elif hands_dict['H1']:
    #         self.hand1_radio.setChecked(True)
    #     elif hands_dict['H2']:
    #         self.hand2_radio.setChecked(True)

    def getphase(self):
        if not self.botharts_connected_cb.isEnabled() or not self.botharts_connected_cb.isChecked():
            # original options - these are mutually exclusive
            if self.botharts_inphase_cb.isEnabled() and self.botharts_inphase_cb.isChecked():
                return 1
            elif self.botharts_outofphase_radio.isEnabled() and self.botharts_outofphase_radio.isChecked():
                return 2
            else:
                return 0
        elif self.botharts_connected_cb.isEnabled() and self.botharts_connected_cb.isChecked():
            # these are mutually exclusive
            if self.botharts_inphase_cb.isEnabled() and self.botharts_inphase_cb.isChecked():
                return 4
            elif self.botharts_outofphase_radio.isEnabled() and self.botharts_outofphase_radio.isChecked():
                # it shouldn't be possible to have both "connected" and "out of phase" checked, but... just in case?
                return 5
            else:
                return 3

    def setphase(self, inphase):
        self.botharts_connected_cb.setChecked((inphase >= 3))

        if inphase % 3 == 1:
            self.botharts_inphase_cb.setChecked(True)
        elif inphase % 3 == 2:
            self.botharts_outofphase_radio.setChecked(True)

    def clear(self):
        self.articulator_group.setExclusive(False)
        for b in self.articulator_group.buttons() + self.botharts_group.buttons():
            b.setChecked(False)
            b.setEnabled(True)
        self.articulator_group.setExclusive(True)
