from copy import deepcopy

from PyQt5.QtWidgets import (
    QFrame,
    QDialog,
    QHBoxLayout,
    QVBoxLayout,
    QBoxLayout,
    QDialogButtonBox,
    QLabel,
    QButtonGroup,
    QMessageBox,
    QRadioButton,
    QCheckBox,
    QGroupBox,
    QSpacerItem,
    QSizePolicy,
    QAbstractButton,
    QTabWidget,
    QWidget,
    QProxyStyle
)

from PyQt5.QtCore import (
    pyqtSignal,
    QEvent
)

from gui.modulespecification_dialog import AddedInfoPushButton
from gui.modulespecification_widgets import BoldableTabWidget, BoldTabBarStyle
from gui.link_help import show_help
from lexicon.module_classes import Signtype
from constant import SIGN_TYPE, ModuleTypes, HAND, ARM, LEG


class SigntypeSpecificationPanel(QFrame):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.buttongroups = []
        self.addedinfobuttons = {}

        self.tabs = QTabWidget()
        self.tabs = BoldableTabWidget()

        # Create tabs
        self.hands_tab = self.create_tab(HAND)
        self.arms_tab = self.create_tab(ARM)
        self.legs_tab = self.create_tab(LEG)

        # Add tabs to tab widget
        self.tabs.addTab(self.hands_tab, "Hands")
        self.tabs.addTab(self.arms_tab, "Arms")
        self.tabs.addTab(self.legs_tab, "Legs")

        # Add the tab widget to the main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

    def create_tab(self, articulator):
        # for convenience
        art_upper = articulator.upper()
        art_lower = articulator.lower()

        tab = QWidget()  # create the tab itself
        tab_layout = QVBoxLayout(tab)  # initialize this tab's layout

        # buttons and groups for highest level
        type_group = SigntypeButtonGroup(prt=self)
        type_unspec_rb = SigntypeRadioButton("Unspecified", parentbtn=None)
        type_unspec_rb.setProperty('abbreviation.path', 'Unspecified_{}s'.format(art_lower))
        self.addedinfobuttons[articulator] = AddedInfoPushButton("Notes")
        type_1_rb = SigntypeRadioButton("1 {}".format(art_lower), parentbtn=None)
        type_1_rb.setProperty('abbreviation.path', SIGN_TYPE['ONE_{}'.format(art_upper)])
        type_2_rb = SigntypeRadioButton("2 {}s".format(articulator.lower()), parentbtn=None)
        type_2_rb.setProperty('abbreviation.path', SIGN_TYPE['TWO_{}S'.format(art_upper)])
        type_group.addButton(type_unspec_rb)
        type_group.addButton(type_1_rb)
        type_group.addButton(type_2_rb)
        self.buttongroups.append(type_group)

        # buttons and groups for 1-handed/-armed/-legged signs
        type_1_group = SigntypeButtonGroup(prt=self)
        type_1move_rb = SigntypeRadioButton("The {} moves".format(art_lower), parentbtn=type_1_rb)
        type_1move_rb.setProperty('abbreviation.path', SIGN_TYPE['ONE_{}_MVMT'.format(art_upper)])
        type_1nomove_rb = SigntypeRadioButton("The {} doesn't move".format(art_lower), parentbtn=type_1move_rb)
        type_1nomove_rb.setProperty('abbreviation.path', SIGN_TYPE['ONE_{}_NO_MVMT'.format(art_upper)])
        type_1_group.addButton(type_1move_rb)
        type_1_group.addButton(type_1nomove_rb)
        self.buttongroups.append(type_1_group)

        # buttons and groups for 2-handed handshape relation (not used for arms or legs)
        if articulator == HAND:
            handstype_handshapereln_group = SigntypeButtonGroup(prt=self)
            handstype_2hsameshapes_rb = SigntypeRadioButton("H1 and H2 use same set(s) of hand configurations",
                                                            parentbtn=type_2_rb)
            handstype_2hsameshapes_rb.setProperty('abbreviation.path', SIGN_TYPE["TWO_HANDS_SAME_HCONF"])
            handstype_2hdiffshapes_rb = SigntypeRadioButton("H1 and H2 use different set(s) of hand configurations",
                                                            parentbtn=type_2_rb)
            handstype_2hdiffshapes_rb.setProperty('abbreviation.path', SIGN_TYPE["TWO_HANDS_DIFF_HCONF"])
            # handstype_2hdiffshapes_rb.toggled.connect(self.linkhandconfigbuttons)
            handstype_handshapereln_group.addButton(handstype_2hsameshapes_rb)
            handstype_handshapereln_group.addButton(handstype_2hdiffshapes_rb)
            self.buttongroups.append(handstype_handshapereln_group)

        # buttons and groups for 2-handed/-armed/-legged contact relation
        type_contactreln_group = SigntypeButtonGroup(prt=self)
        type_2contactyes_rb = SigntypeRadioButton("{art}1 and {art}2 maintain contact throughout sign".format(art=articulator[0]),
                                                  parentbtn=type_2_rb)
        type_2contactyes_rb.setProperty('abbreviation.path', SIGN_TYPE['TWO_{}S_MAINT_CONT'.format(art_upper)])
        type_2contactno_rb = SigntypeRadioButton("{art}1 and {art}2 do not maintain contact".format(art=articulator[0]),
                                                 parentbtn=type_2_rb)
        type_2contactno_rb.setProperty('abbreviation.path', SIGN_TYPE["TWO_{}S_NO_CONT".format(art_upper)])
        type_contactreln_group.addButton(type_2contactyes_rb)
        type_contactreln_group.addButton(type_2contactno_rb)
        self.buttongroups.append(type_contactreln_group)

        # buttons and groups for bilateral symmetry relation
        type_symmetryreln_group = SigntypeButtonGroup(prt=self)
        type_2symmetryyes_rb = SigntypeRadioButton("{art}1 and {art}2 are bilaterally symmetric".format(art=articulator[0]),
                                                   parentbtn=type_2_rb)
        type_2symmetryyes_rb.setProperty('abbreviation.path', SIGN_TYPE['TWO_{}S_BISYM'.format(art_upper)])
        type_2symmetryno_rb = SigntypeRadioButton("{art}1 and {art}2 are not bilaterally symmetric".format(art=articulator[0]),
                                                   parentbtn=type_2_rb)
        type_2symmetryno_rb.setProperty('abbreviation.path', SIGN_TYPE['TWO_{}S_NO_BISYM'.format(art_upper)])
        type_symmetryreln_group.addButton(type_2symmetryyes_rb)
        type_symmetryreln_group.addButton(type_2symmetryno_rb)
        self.buttongroups.append(type_symmetryreln_group)

        # buttons and groups for 2-handed/-armed/-legged movement relation
        type_mvmtreln_group = SigntypeButtonGroup(prt=self)
        type_2mvmtneither_rb = SigntypeRadioButton("Neither {} moves".format(art_lower), parentbtn=type_2_rb)
        type_2mvmtneither_rb.setProperty('abbreviation.path', SIGN_TYPE['TWO_{}S_NO_MVMT'.format(art_upper)])
        type_2mvmtone_rb = SigntypeRadioButton("Only 1 {} moves".format(art_lower), parentbtn=type_2_rb)
        type_2mvmtone_rb.setProperty('abbreviation.path', SIGN_TYPE['TWO_{}S_ONE_MVMT'.format(art_upper)])
        type_2mvmtboth_rb = SigntypeRadioButton("Both {}s move".format(art_lower), parentbtn=type_2_rb)
        type_2mvmtboth_rb.setProperty('abbreviation.path', SIGN_TYPE['TWO_{}S_BOTH_MVMT'.format(art_upper)])
        type_mvmtreln_group.addButton(type_2mvmtneither_rb)
        type_mvmtreln_group.addButton(type_2mvmtone_rb)
        type_mvmtreln_group.addButton(type_2mvmtboth_rb)
        self.buttongroups.append(type_mvmtreln_group)

        # buttons and groups for movement relations in 2-handed/-armed/-legged signs where only one moves
        type_mvmtoneartreln_group = SigntypeButtonGroup(prt=self)
        type_2mvmtoneart1_rb = SigntypeRadioButton("Only {}1 moves".format(articulator[0]), parentbtn=type_2mvmtone_rb)
        type_2mvmtoneart1_rb.setProperty('abbreviation.path', SIGN_TYPE['TWO_{}S_ONLY_{}1'.format(art_upper,
                                                                                                  articulator[0])])
        type_2mvmtoneart2_rb = SigntypeRadioButton("Only {}2 moves".format(articulator[0]), parentbtn=type_2mvmtone_rb)
        type_2mvmtoneart2_rb.setProperty('abbreviation.path', SIGN_TYPE['TWO_{}S_ONLY_{}2'.format(art_upper,
                                                                                                  articulator[0])])
        type_mvmtoneartreln_group.addButton(type_2mvmtoneart1_rb)
        type_mvmtoneartreln_group.addButton(type_2mvmtoneart2_rb)
        self.buttongroups.append(type_mvmtoneartreln_group)

        # buttons and groups for movement relations in 2-handed/-armed/-legged signs where both move
        type_mvmtbothartreln_group = SigntypeButtonGroup(prt=self)
        type_2mvmtbothdiff_rb = SigntypeRadioButton("{art}1 and {art}2 move differently".format(art=articulator[0]),
                                                    parentbtn=type_2mvmtboth_rb)
        type_2mvmtbothdiff_rb.setProperty('abbreviation.path', SIGN_TYPE['TWO_{}S_BOTH_MVMT_DIFF'.format(art_upper)])
        type_2mvmtbothsame_rb = SigntypeRadioButton("{art}1 and {art}2 move similarly".format(art=articulator[0]),
                                                    parentbtn=type_2mvmtboth_rb)
        type_2mvmtbothsame_rb.setProperty('abbreviation.path', SIGN_TYPE['TWO_{}S_BOTH_MVMT_SAME'.format(art_upper)])
        type_mvmtbothartreln_group.addButton(type_2mvmtbothdiff_rb)
        type_mvmtbothartreln_group.addButton(type_2mvmtbothsame_rb)
        self.buttongroups.append(type_mvmtbothartreln_group)

        # buttons and groups for movement timing relations in 2-handed/-armed/-legged signs
        type_mvmttimingreln_group = SigntypeButtonGroup(prt=self)
        type_2mvmtseq_rb = SigntypeRadioButton("Sequential", parentbtn=type_2mvmtbothsame_rb)
        type_2mvmtseq_rb.setProperty('abbreviation.path', SIGN_TYPE['TWO_{}S_BOTH_MVMT_SEQ'.format(art_upper)])
        type_2mvmtsimult_rb = SigntypeRadioButton("Simultaneous", parentbtn=type_2mvmtbothsame_rb)
        type_2mvmtsimult_rb.setProperty('abbreviation.path', SIGN_TYPE['TWO_{}S_BOTH_MVMT_SIMU'.format(art_upper)])
        type_mvmttimingreln_group.addButton(type_2mvmtseq_rb)
        type_mvmttimingreln_group.addButton(type_2mvmtsimult_rb)
        self.buttongroups.append(type_mvmttimingreln_group)

        # begin layout for sign type (highest level)
        signtype_layout = QVBoxLayout()
        firstrow_layout = QHBoxLayout()
        firstrow_layout.addWidget(type_unspec_rb)
        firstrow_layout.addStretch()
        firstrow_layout.addWidget(self.addedinfobuttons[articulator])
        signtype_layout.addLayout(firstrow_layout)
        signtype_layout.addWidget(type_1_rb)

        ## begin layout for 1-handed/-armed/-legged sign options
        oneart_spacedlayout = QHBoxLayout()
        oneart_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        oneart_layout = QVBoxLayout()
        oneart_layout.addWidget(type_1move_rb)
        oneart_layout.addWidget(type_1nomove_rb)
        oneart_spacedlayout.addLayout(oneart_layout)
        signtype_layout.addLayout(oneart_spacedlayout)
        type_1_rb.setchildlayout(oneart_spacedlayout)
        ## end layout for 1-handed/-armed/-legged sign options

        signtype_layout.addWidget(type_2_rb)

        ## begin layout for 2-handed/-armed/-legged sign options
        twoart_spacedlayout = QHBoxLayout()
        twoart_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        twoart_col1_layout = QVBoxLayout()

        if articulator == HAND:
            ### begin layout for 2-handed handshape relation (not used for arms or legs)
            handshape_layout = QVBoxLayout()
            handshape_layout.addWidget(handstype_2hsameshapes_rb)
            handshape_layout.addWidget(handstype_2hdiffshapes_rb)
            handshape_box = QGroupBox("Hand configuration relation")
            handshape_box.setLayout(handshape_layout)
            twoart_col1_layout.addWidget(handshape_box)
            ### end layout for 2-handed handshape relation

        ### begin layout for 2-handed/-armed/-legged contact relation
        contact_layout = QVBoxLayout()
        contact_layout.addWidget(type_2contactyes_rb)
        contact_layout.addWidget(type_2contactno_rb)
        contact_box = QGroupBox("Contact relation")
        contact_box.setLayout(contact_layout)
        twoart_col1_layout.addWidget(contact_box)
        ### end layout for 2-handed/-armed/-legged contact relation

        ### begin layout for 2-handed/-armed/-legged bilateral symmetry relation
        symmetry_layout = QVBoxLayout()
        symmetry_layout.addWidget(type_2symmetryyes_rb)
        symmetry_layout.addWidget(type_2symmetryno_rb)
        symmetry_box = QGroupBox("Bilateral symmetry relation")
        symmetry_box.setLayout(symmetry_layout)
        twoart_col1_layout.addWidget(symmetry_box)
        ### end layout for 2-handed/-armed/-legged contact relation

        twoart_col1_layout.addStretch(1)

        ### begin layout for 2-handed/-armed/-legged movement relation
        movement_layout = QVBoxLayout()
        movement_layout.addWidget(type_2mvmtneither_rb)
        movement_layout.addWidget(type_2mvmtone_rb)

        #### begin layout for 2-handed/-armed/-legged movement relation in which only one hand moves
        movement_1_spacedlayout = QHBoxLayout()
        movement_1_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        movement_1_layout = QVBoxLayout()
        movement_1_layout.addWidget(type_2mvmtoneart1_rb)
        movement_1_layout.addWidget(type_2mvmtoneart2_rb)
        movement_1_spacedlayout.addLayout(movement_1_layout)
        movement_layout.addLayout(movement_1_spacedlayout)
        type_2mvmtone_rb.setchildlayout(movement_1_spacedlayout)
        #### end layout for 2-handed/-armed/-legged movement relation in which only one hand moves

        movement_layout.addWidget(type_2mvmtboth_rb)

        #### begin layout for 2-handed/-armed/-legged movement relation in which both hands move
        movement_2_spacedlayout = QHBoxLayout()
        movement_2_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        movement_2_layout = QVBoxLayout()
        movement_2_layout.addWidget(type_2mvmtbothdiff_rb)
        movement_2_layout.addWidget(type_2mvmtbothsame_rb)

        #### begin layout for 2-handed/-armed/-legged movement relation in which both hands move similarly
        similarmvmt_spacedlayout = QHBoxLayout()
        similarmvmt_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        similarmvmt_layout = QVBoxLayout()
        similarmvmt_layout.addWidget(type_2mvmtseq_rb)
        similarmvmt_layout.addWidget(type_2mvmtsimult_rb)

        movement_2_spacedlayout.addLayout(movement_2_layout)
        movement_layout.addLayout(movement_2_spacedlayout)
        type_2mvmtboth_rb.setchildlayout(movement_2_spacedlayout)
        #### end layout for 2-handed/-armed/-legged movement relation in which both hands move

        movement_layout.addWidget(type_2mvmtboth_rb)

        movement_box = QGroupBox("Movement relation")
        movement_box.setLayout(movement_layout)
        ### end layout for 2-handed/-armed/-legged movement relation

        twoart_spacedlayout.addLayout(twoart_col1_layout)
        twoart_spacedlayout.addWidget(movement_box)

        signtype_layout.addLayout(twoart_spacedlayout)

        type_2_rb.setchildlayout(twoart_spacedlayout)
        ## end layout for 2-handed/-armed/-legged sign options

        signtype_box = QGroupBox()
        signtype_box.setLayout(signtype_layout)
        # end layout for sign type (highest level)

        tab_layout.addWidget(signtype_box)

        return tab

    def setsigntype(self, signtype):
        # clear all
        self.clear()

        # then reset according to input signtype
        allbuttons = [btn for btngrp in self.buttongroups for btn in btngrp.buttons()]
        signtypepaths = [btn.property('abbreviation.path') for btn in allbuttons]
        nolongeravailable = []  # for backward compatibility
        for spec in signtype.specslist:
            if spec in signtypepaths:
                btnidx = signtypepaths.index(spec)
                allbuttons[btnidx].setChecked(True)
            else:
                nolongeravailable.append(spec)

        if len(nolongeravailable) > 1:
            print(
                "This sign had sign type options specified that are no longer available and will be removed" +
                " if you click 'save' (but not 'cancel'). Please make note of the following characteristics:")
            for spec in nolongeravailable:
                print(spec)
                signtype.specslist.remove(spec)

        for articulator in self.addedinfobuttons.keys():
            self.addedinfobuttons[articulator].addedinfo = deepcopy(signtype.addedinfo[articulator])

        # loading per se done.
        # now programmatically move tab to 'target' and then to the first tab, in order to invoke the tab bold behaviour
        target = self.tabs.count() - 1     # where to? to the last tab
        self.tabs.setCurrentIndex(target)
        self.tabs.repaint()
        self.tabs.setCurrentIndex(0)  # back to the first

    # uncheck all buttons and clear any selections/entries in AddedInfo "Notes" menu
    def clear(self):
        for g in self.buttongroups:
            g.setExclusive(False)
            for b in g.buttons():
                b.setEnabled(True)
                b.setChecked(False)
            g.setExclusive(True)
        for btn in self.addedinfobuttons.values():
            btn.clear()

    def getsigntype(self):
        addedinfo_dict = {art:btn.addedinfo for (art, btn) in self.addedinfobuttons.items()}

        allbuttons = [btn for btngrp in self.buttongroups for btn in btngrp.buttons()]
        # when saving, only use options that are both checked AND enabled!
        specslist = [btn.property('abbreviation.path') for btn in allbuttons if btn.isChecked() and btn.isEnabled()]

        signtype = Signtype(specslist, addedinfo=addedinfo_dict)

        return signtype

    # return the button group that contains the given button
    # in theory I suppose a button could be in more than one button group?
    # ... but here we assume there's only one, so the first hit is returned
    def getButtonGroup(self, thebutton):
        groups = [bg for bg in self.buttongroups if thebutton in bg.buttons()]
        return groups[0]

    # return the button group that contains the given button
    # in theory I suppose a button could be in more than one button group?
    # ... but here we assume there's only one, so the first hit is returned
    def getButtonGroup(self, thebutton):
        groups = [bg for bg in self.buttongroups if thebutton in bg.buttons()]
        return groups[0]

    def symmetry_dependencies_warning(self):
        # conflict = False
        # if self.handstype_2hsymmetryyes_radio.isChecked():
        #     msg = "Bilateral symmetry relation conflicts with: \n"
        #     if self.handstype_2hdiffshapes_radio.isChecked():
        #         msg += "- Hand configuration relation\n"
        #         conflict = True
        #     if self.handstype_2hmvmtone_radio.isChecked() and self.handstype_2hmvmtone_radio.isEnabled():
        #         msg += "- Movement relation (only 1 hand moves)\n"
        #         conflict = True
        #     if self.handstype_2hmvmtbothdiff_radio.isChecked() and self.handstype_2hmvmtbothdiff_radio.isEnabled():
        #         msg += "- Movement relation (hands move differently)\n"
        #         conflict = True
        # if conflict == True:
        #     return msg
        return "pass"


class SigntypeButtonGroup(QButtonGroup):

    def __init__(self, prt=None):
        super().__init__(parent=prt)
        self.buttonToggled.connect(self.handleButtonToggled)

    def handleButtonToggled(self, thebutton, checked):
        if checked:
            self.enableChildWidgets(True, thebutton.childlayout)
            self.disableSiblings(thebutton)
        elif isinstance(thebutton, SigntypeCheckBox) and not checked and not self.hasSiblings(thebutton):
            # then we've unchecked a checkbox that is the only button in its group,
            # and will therefore not have its children disabled via disableSiblings()
            if thebutton.childlayout:
                self.enableChildWidgets(False, thebutton.childlayout)

    def hasSiblings(self, thebutton):
        return len(self.getSiblings(thebutton)) > 0

    def getSiblings(self, thebutton):
        return [b for b in self.buttons() if b != thebutton]

    def disableSiblings(self, thebutton):
        siblings = self.getSiblings(thebutton)
        for b in siblings:
            if b.childlayout:
                self.enableChildWidgets(False, b.childlayout)

    # TODO KV if all of these subsections are implemented  with widgets instead of layouts, is this part easier?
    # parent can be widget or layout
    def enableChildWidgets(self, yesorno, parent):
        if isinstance(parent, QAbstractButton):
            self.enableChildWidgets(yesorno, parent.childlayout)
        elif isinstance(parent, QBoxLayout):
            numchildren = parent.count()
            for childnum in range(numchildren):
                thechild = parent.itemAt(childnum)
                if thechild.widget():
                    childwidget = thechild.widget()
                    if isinstance(childwidget, QAbstractButton):
                        parentbutton = childwidget.parentbutton
                        parentbuttonhascheckedsibling = parentbutton and True in [sib.isChecked() for
                                                                                  sib in
                                                                                  self.parent().getButtonGroup(
                                                                                      parentbutton).getSiblings(
                                                                                      parentbutton)]
                        childwidget.setEnabled(yesorno and not parentbuttonhascheckedsibling)
                    elif isinstance(childwidget, QLabel):
                        childwidget.setEnabled(yesorno)
                    elif isinstance(childwidget, QGroupBox):
                        self.enableChildWidgets(yesorno, childwidget.layout())
                elif thechild.layout():
                    self.enableChildWidgets(yesorno, thechild.layout())


class SigntypeRadioButton(QRadioButton):

    def __init__(self, txt="", parentbtn=None):
        super().__init__(text=txt)
        self.parentbutton = parentbtn
        self.toggled.connect(self.checkparent)
        self.childlayout = None

    def checkparent(self, checked):
        if checked and self.parentbutton:
            self.parentbutton.setChecked(True)

    def setchildlayout(self, clayout):
        self.childlayout = clayout

    def __repr__(self):
        return '<SigntypeRadioButton: ' + repr(self.text()) + '>'


class SigntypeCheckBox(QCheckBox):

    def __init__(self, text="", parentbutton=None):
        super().__init__(text)
        self.parentbutton = parentbutton
        self.available = True  # to be used in conjunction with a linked button; ie, "available" means "available to be enabled"
        self.toggled.connect(self.checkParent)
        self.childlayout = None

    def setAvailable(self, avail):
        self.available = avail

    def checkParent(self, checked):
        if checked and self.parentbutton:
            self.parentbutton.setChecked(True)

    def setChildlayout(self, clayout):
        self.childlayout = clayout

    def setEnabled(self, a0):
        super().setEnabled(a0 and self.available)

    def changeEvent(self, e):  # gets called *after* change event... so isEnabled is for new state, not old
        if e.type() == QEvent.EnabledChange:
            if (not self.available or not self.parentbutton.isEnabled()) and self.isEnabled():
                self.setEnabled(False)
                return
        super().changeEvent(e)

    def __repr__(self):
        return '<SigntypeCheckBox: ' + repr(self.text()) + '>'


class SigntypeSelectorDialog(QDialog):
    saved_signtype = pyqtSignal(Signtype)

    def __init__(self, signtypetoload, **kwargs):
        super().__init__(**kwargs)

        self.mainwindow = self.parent().mainwindow
        self.settings = self.mainwindow.app_settings

        self.signtype = signtypetoload or self.get_default_signtype()
        self.signtype_widget = SigntypeSpecificationPanel()
        self.signtype_widget.setsigntype(self.signtype)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.signtype_widget)

        separate_line = QFrame()
        separate_line.setFrameShape(QFrame.HLine)
        separate_line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separate_line)

        buttons = QDialogButtonBox.RestoreDefaults | QDialogButtonBox.Help | QDialogButtonBox.Save | QDialogButtonBox.Cancel

        self.button_box = QDialogButtonBox(buttons, parent=self)
        self.button_box.button(QDialogButtonBox.RestoreDefaults).setAutoDefault(False)
        self.button_box.button(QDialogButtonBox.Save).setDefault(True)

        self.button_box.clicked.connect(self.handle_button_click)

        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)
        # self.setMinimumSize(QSize(500, 1100))  # 500, 850

    def get_default_signtype(self):
        signtype_default = self.settings['signdefaults']['signtype']
        signtype_specs = []
        if signtype_default == 'unspec':
            signtype_specs = [('Unspecified', False)]
        elif signtype_default == '1hand':
            signtype_specs = [('1h', False)]
        elif signtype_default == '2hand':
            signtype_specs = [('2h', False)]
        return Signtype(signtype_specs)

    def handle_button_click(self, button):
        standard = self.button_box.standardButton(button)
        if standard == QDialogButtonBox.Cancel:
            # response = QMessageBox.question(self, 'Warning',
            #                                 'If you close the window, any unsaved changes will be lost. Continue?')
            # if response == QMessageBox.Yes:
            #     self.accept()

            self.reject()

        elif standard == QDialogButtonBox.Help:
            show_help(ModuleTypes.SIGNTYPE)

        #     elif standard == QDialogButtonBox.RestoreDefaults:
        #         self.movement_tab.remove_all_pages()
        #         self.movement_tab.add_default_movement_tabs(is_system_default=True)
        elif standard == QDialogButtonBox.Save:
            dependency_warning = self.signtype_widget.symmetry_dependencies_warning()
            if (dependency_warning == "pass"):
                newsigntype = self.signtype_widget.getsigntype()
                self.saved_signtype.emit(newsigntype)
                if self.mainwindow.current_sign is not None and self.signtype != newsigntype:
                    self.mainwindow.current_sign.lastmodifiednow()
                self.accept()
            else:
                QMessageBox.critical(self, "Warning", dependency_warning)

        elif standard == QDialogButtonBox.RestoreDefaults:
            self.signtype_widget.setsigntype(self.get_default_signtype())
