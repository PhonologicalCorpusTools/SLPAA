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
    QRadioButton,
    QCheckBox,
    QGroupBox,
    QSpacerItem,
    QSizePolicy,
    QAbstractButton,
    QPushButton
)

from PyQt5.QtCore import (
    pyqtSignal,
    QEvent
)

from gui.module_selector import AddedInfoPushButton, AddedInfo

class SigntypeSpecificationLayout(QVBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.buttongroups = []

        # TODO KV should button properties be integers instead of strings,
        # so it's easier to add more user-specified options?

        # buttons and groups for highest level
        self.handstype_group = SigntypeButtonGroup(prt=self)
        self.handstype_unspec_radio = SigntypeRadioButton("Unspecified", parentbutton=None)
        self.handstype_unspec_radio.setProperty('abbreviation.path', 'Unspecified')
        self.handstype_unspec_radio.setProperty('abbreviation.include', True)
        self.addedinfobutton = AddedInfoPushButton("Notes")
        self.handstype_1h_radio = SigntypeRadioButton("1 hand", parentbutton=None)
        self.handstype_1h_radio.setProperty('abbreviation.path', "1h")
        self.handstype_1h_radio.setProperty('abbreviation.include', True)
        self.handstype_2h_radio = SigntypeRadioButton("2 hands", parentbutton=None)
        self.handstype_2h_radio.setProperty('abbreviation.path', "2h")
        self.handstype_2h_radio.setProperty('abbreviation.include', True)
        self.handstype_group.addButton(self.handstype_unspec_radio)
        self.handstype_group.addButton(self.handstype_1h_radio)
        self.handstype_group.addButton(self.handstype_2h_radio)
        self.buttongroups.append(self.handstype_group)

        # buttons and groups for 1-handed signs
        self.handstype_1h_group = SigntypeButtonGroup(prt=self)
        self.handstype_1hmove_radio = SigntypeRadioButton('The hand moves', parentbutton=self.handstype_1h_radio)
        self.handstype_1hmove_radio.setProperty('abbreviation.path', "1h.moves")
        self.handstype_1hmove_radio.setProperty('abbreviation.include', True)
        self.handstype_1hnomove_radio = SigntypeRadioButton("The hand doesn\'t move",
                                                            parentbutton=self.handstype_1h_radio)
        self.handstype_1hnomove_radio.setProperty('abbreviation.path', "1h.no mvmt")
        self.handstype_1hnomove_radio.setProperty('abbreviation.include', True)
        self.handstype_1h_group.addButton(self.handstype_1hmove_radio)
        self.handstype_1h_group.addButton(self.handstype_1hnomove_radio)
        self.buttongroups.append(self.handstype_1h_group)

        # buttons and groups for 2-handed handshape relation
        self.handstype_handshapereln_group = SigntypeButtonGroup(prt=self)
        self.handstype_2hsameshapes_radio = SigntypeRadioButton("H1 and H2 use same set(s) of hand configurations",
                                                                parentbutton=self.handstype_2h_radio)
        self.handstype_2hsameshapes_radio.setProperty('abbreviation.path', "2h.same HCs")
        self.handstype_2hsameshapes_radio.setProperty('abbreviation.include', True)
        self.handstype_2hdiffshapes_radio = SigntypeRadioButton("H1 and H2 use different set(s) of hand configurations",
                                                                parentbutton=self.handstype_2h_radio)
        self.handstype_2hdiffshapes_radio.setProperty('abbreviation.path', "2h.different HCs")
        self.handstype_2hdiffshapes_radio.setProperty('abbreviation.include', True)
        # self.handstype_2hdiffshapes_radio.toggled.connect(self.linkhandconfigbuttons)
        self.handstype_handshapereln_group.addButton(self.handstype_2hsameshapes_radio)
        self.handstype_handshapereln_group.addButton(self.handstype_2hdiffshapes_radio)
        self.buttongroups.append(self.handstype_handshapereln_group)

        # buttons and groups for 2-handed contact relation
        self.handstype_contactreln_group = SigntypeButtonGroup(prt=self)
        self.handstype_2hcontactyes_radio = SigntypeRadioButton("H1 and H2 maintain contact throughout sign",
                                                                parentbutton=self.handstype_2h_radio)
        self.handstype_2hcontactyes_radio.setProperty('abbreviation.path', "2h.maintain contact")
        self.handstype_2hcontactyes_radio.setProperty('abbreviation.include', True)
        self.handstype_2hcontactno_radio = SigntypeRadioButton("H1 and H2 do not maintain contact",
                                                               parentbutton=self.handstype_2h_radio)
        self.handstype_2hcontactno_radio.setProperty('abbreviation.path', "2h.contact not maintained")
        self.handstype_2hcontactno_radio.setProperty('abbreviation.include', False)
        self.handstype_contactreln_group.addButton(self.handstype_2hcontactyes_radio)
        self.handstype_contactreln_group.addButton(self.handstype_2hcontactno_radio)
        self.buttongroups.append(self.handstype_contactreln_group)

        # buttons and groups for bilateral symmetry relation
        self.handstype_symmetryreln_group = SigntypeButtonGroup(prt=self)
        self.handstype_2hsymmetryyes_radio = SigntypeRadioButton("H1 and H2 are bilaterally symmetric",
                                                                 parentbutton=self.handstype_2h_radio)
        self.handstype_2hsymmetryyes_radio.setProperty('abbreviation.path', "2h.bilaterally symmetric")
        self.handstype_2hsymmetryyes_radio.setProperty('abbreviation.include', True)
        self.handstype_2hsymmetryno_radio = SigntypeRadioButton("H1 and H2 are not bilaterally symmetric",
                                                                parentbutton=self.handstype_2h_radio)
        self.handstype_2hsymmetryno_radio.setProperty('abbreviation.path', "2h.not bilaterally symmetric")
        self.handstype_2hsymmetryno_radio.setProperty('abbreviation.include', False)
        self.handstype_symmetryreln_group.addButton(self.handstype_2hsymmetryyes_radio)
        self.handstype_symmetryreln_group.addButton(self.handstype_2hsymmetryno_radio)
        self.buttongroups.append(self.handstype_symmetryreln_group)

        # buttons and groups for 2-handed movement relation
        self.handstype_mvmtreln_group = SigntypeButtonGroup(prt=self)
        self.handstype_2hmvmtneither_radio = SigntypeRadioButton("Neither hand moves",
                                                                 parentbutton=self.handstype_2h_radio)
        self.handstype_2hmvmtneither_radio.setProperty('abbreviation.path', "2h.neither moves")
        self.handstype_2hmvmtneither_radio.setProperty('abbreviation.include', True)
        self.handstype_2hmvmtone_radio = SigntypeRadioButton("Only 1 hand moves", parentbutton=self.handstype_2h_radio)
        self.handstype_2hmvmtone_radio.setProperty('abbreviation.path', "2h.only 1 moves")
        self.handstype_2hmvmtone_radio.setProperty('abbreviation.include', False)
        self.handstype_2hmvmtboth_radio = SigntypeRadioButton("Both hands move", parentbutton=self.handstype_2h_radio)
        self.handstype_2hmvmtboth_radio.setProperty('abbreviation.path', "2h.both move")
        self.handstype_2hmvmtboth_radio.setProperty('abbreviation.include', False)
        self.handstype_mvmtreln_group.addButton(self.handstype_2hmvmtneither_radio)
        self.handstype_mvmtreln_group.addButton(self.handstype_2hmvmtone_radio)
        self.handstype_mvmtreln_group.addButton(self.handstype_2hmvmtboth_radio)
        self.buttongroups.append(self.handstype_mvmtreln_group)

        # buttons and groups for movement relations in 2-handed signs where only one hand moves
        self.handstype_mvmtonehandreln_group = SigntypeButtonGroup(prt=self)
        self.handstype_2hmvmtoneH1_radio = SigntypeRadioButton("Only H1 moves",
                                                               parentbutton=self.handstype_2hmvmtone_radio)
        self.handstype_2hmvmtoneH1_radio.setProperty('abbreviation.path', "2h.only 1 moves.H1 moves")
        self.handstype_2hmvmtoneH1_radio.setProperty('abbreviation.include', True)
        self.handstype_2hmvmtoneH2_radio = SigntypeRadioButton("Only H2 moves",
                                                               parentbutton=self.handstype_2hmvmtone_radio)
        self.handstype_2hmvmtoneH2_radio.setProperty('abbreviation.path', "2h.only 1 moves.H2 moves")
        self.handstype_2hmvmtoneH2_radio.setProperty('abbreviation.include', True)
        self.handstype_mvmtonehandreln_group.addButton(self.handstype_2hmvmtoneH1_radio)
        self.handstype_mvmtonehandreln_group.addButton(self.handstype_2hmvmtoneH2_radio)
        self.buttongroups.append(self.handstype_mvmtonehandreln_group)

        # buttons and groups for movement relations in 2-handed signs where both hands move
        self.handstype_mvmtbothhandreln_group = SigntypeButtonGroup(prt=self)
        self.handstype_2hmvmtbothdiff_radio = SigntypeRadioButton("H1 and H2 move differently",
                                                                  parentbutton=self.handstype_2hmvmtboth_radio)
        self.handstype_2hmvmtbothdiff_radio.setProperty('abbreviation.path', "2h.both move.move differently")
        self.handstype_2hmvmtbothdiff_radio.setProperty('abbreviation.include', True)
        self.handstype_2hmvmtbothsame_radio = SigntypeRadioButton("H1 and H2 move similarly",
                                                                  parentbutton=self.handstype_2hmvmtboth_radio)
        self.handstype_2hmvmtbothsame_radio.setProperty('abbreviation.path', "2h.both move.move similarly")
        self.handstype_2hmvmtbothsame_radio.setProperty('abbreviation.include', True)
        self.handstype_mvmtbothhandreln_group.addButton(self.handstype_2hmvmtbothdiff_radio)
        self.handstype_mvmtbothhandreln_group.addButton(self.handstype_2hmvmtbothsame_radio)
        self.buttongroups.append(self.handstype_mvmtbothhandreln_group)

        # buttons and groups for movement timing relations in 2-handed signs
        self.handstype_mvmttimingreln_group = SigntypeButtonGroup(prt=self)
        self.handstype_2hmvmtseq_radio = SigntypeRadioButton("Sequential",
                                                             parentbutton=self.handstype_2hmvmtbothsame_radio)
        self.handstype_2hmvmtseq_radio.setProperty('abbreviation.path', "2h.both move.move similarly.sequential")
        self.handstype_2hmvmtseq_radio.setProperty('abbreviation.include', True)
        self.handstype_2hmvmtsimult_radio = SigntypeRadioButton("Simultaneous",
                                                                parentbutton=self.handstype_2hmvmtbothsame_radio)
        self.handstype_2hmvmtsimult_radio.setProperty('abbreviation.path', "2h.both move.move similarly.simultaneous")
        self.handstype_2hmvmtsimult_radio.setProperty('abbreviation.include', True)
        self.handstype_mvmttimingreln_group.addButton(self.handstype_2hmvmtseq_radio)
        self.handstype_mvmttimingreln_group.addButton(self.handstype_2hmvmtsimult_radio)
        self.buttongroups.append(self.handstype_mvmttimingreln_group)

        # begin layout for sign type (highest level)
        self.signtype_layout = QVBoxLayout()
        self.firstrow_layout = QHBoxLayout()
        self.firstrow_layout.addWidget(self.handstype_unspec_radio)
        self.firstrow_layout.addStretch()
        self.firstrow_layout.addWidget(self.addedinfobutton)
        self.signtype_layout.addLayout(self.firstrow_layout)
        # self.signtype_layout.addWidget(self.handstype_unspec_radio)
        self.signtype_layout.addWidget(self.handstype_1h_radio)

        ## begin layout for 1-handed sign options
        self.onehand_spacedlayout = QHBoxLayout()
        self.onehand_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        self.onehand_layout = QVBoxLayout()
        self.onehand_layout.addWidget(self.handstype_1hmove_radio)
        self.onehand_layout.addWidget(self.handstype_1hnomove_radio)
        self.onehand_spacedlayout.addLayout(self.onehand_layout)
        self.signtype_layout.addLayout(self.onehand_spacedlayout)
        self.handstype_1h_radio.setChildlayout(self.onehand_spacedlayout)
        ## end layout for 1-handed sign options

        self.signtype_layout.addWidget(self.handstype_2h_radio)

        ## begin layout for 2-handed sign options
        self.twohand_spacedlayout = QHBoxLayout()
        self.twohand_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        self.twohand_col1_layout = QVBoxLayout()

        ### begin layout for 2-handed handshape relation
        self.handshape_layout = QVBoxLayout()
        self.handshape_layout.addWidget(self.handstype_2hsameshapes_radio)
        self.handshape_layout.addWidget(self.handstype_2hdiffshapes_radio)
        self.handshape_box = QGroupBox("Hand configuration relation")
        self.handshape_box.setLayout(self.handshape_layout)
        self.twohand_col1_layout.addWidget(self.handshape_box)
        ### end layout for 2-handed handshape relation

        ### begin layout for 2-handed contact relation
        self.contact_layout = QVBoxLayout()
        self.contact_layout.addWidget(self.handstype_2hcontactyes_radio)
        self.contact_layout.addWidget(self.handstype_2hcontactno_radio)
        self.contact_box = QGroupBox("Contact relation")
        self.contact_box.setLayout(self.contact_layout)
        self.twohand_col1_layout.addWidget(self.contact_box)
        ### end layout for 2-handed contact relation

        ### begin layout for 2-handed bilateral symmetry relation
        self.symmetry_layout = QVBoxLayout()
        self.symmetry_layout.addWidget(self.handstype_2hsymmetryyes_radio)
        self.symmetry_layout.addWidget(self.handstype_2hsymmetryno_radio)
        self.symmetry_box = QGroupBox("Bilateral symmetry relation")
        self.symmetry_box.setLayout(self.symmetry_layout)
        self.twohand_col1_layout.addWidget(self.symmetry_box)
        ### end layout for 2-handed contact relation

        self.twohand_col1_layout.addStretch(1)

        ### begin layout for 2-handed movement relation
        self.movement_layout = QVBoxLayout()
        self.movement_layout.addWidget(self.handstype_2hmvmtneither_radio)
        self.movement_layout.addWidget(self.handstype_2hmvmtone_radio)

        #### begin layout for 2-handed movement relation in which only one hand moves
        self.movement_1h_spacedlayout = QHBoxLayout()
        self.movement_1h_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        self.movement_1h_layout = QVBoxLayout()
        self.movement_1h_layout.addWidget(self.handstype_2hmvmtoneH1_radio)
        self.movement_1h_layout.addWidget(self.handstype_2hmvmtoneH2_radio)
        self.movement_1h_spacedlayout.addLayout(self.movement_1h_layout)
        self.movement_layout.addLayout(self.movement_1h_spacedlayout)
        self.handstype_2hmvmtone_radio.setChildlayout(self.movement_1h_spacedlayout)
        #### end layout for 2-handed movement relation in which only one hand moves

        self.movement_layout.addWidget(self.handstype_2hmvmtboth_radio)

        #### begin layout for 2-handed movement relation in which both hands move
        self.movement_2h_spacedlayout = QHBoxLayout()
        self.movement_2h_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        self.movement_2h_layout = QVBoxLayout()
        self.movement_2h_layout.addWidget(self.handstype_2hmvmtbothdiff_radio)
        self.movement_2h_layout.addWidget(self.handstype_2hmvmtbothsame_radio)

        #### begin layout for 2-handed movement relation in which both hands move similarly
        self.similarmvmt_spacedlayout = QHBoxLayout()
        self.similarmvmt_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        self.similarmvmt_layout = QVBoxLayout()
        self.similarmvmt_layout.addWidget(self.handstype_2hmvmtseq_radio)
        self.similarmvmt_layout.addWidget(self.handstype_2hmvmtsimult_radio)

        self.movement_2h_spacedlayout.addLayout(self.movement_2h_layout)
        self.movement_layout.addLayout(self.movement_2h_spacedlayout)
        self.handstype_2hmvmtboth_radio.setChildlayout(self.movement_2h_spacedlayout)
        #### end layout for 2-handed movement relation in which both hands move

        self.movement_layout.addWidget(self.handstype_2hmvmtboth_radio)

        self.movement_box = QGroupBox("Movement relation")
        self.movement_box.setLayout(self.movement_layout)
        ### end layout for 2-handed movement relation

        self.twohand_spacedlayout.addLayout(self.twohand_col1_layout)
        self.twohand_spacedlayout.addWidget(self.movement_box)

        self.signtype_layout.addLayout(self.twohand_spacedlayout)

        self.handstype_2h_radio.setChildlayout(self.twohand_spacedlayout)
        ## end layout for 2-handed sign options

        self.signtype_box = QGroupBox("Sign type")
        self.signtype_box.setLayout(self.signtype_layout)
        # end layout for sign type (highest level)

        self.addWidget(self.signtype_box)

        # ensure that Unspecified is selected by default
        # TODO KV keep this? or does loadspecs preclude it?
        # self.handstype_unspec_radio.toggle()

    def setsigntype(self, signtype):
        allbuttons = [btn for btngrp in self.buttongroups for btn in btngrp.buttons()]
        signtypepaths = [btn.property('abbreviation.path') for btn in allbuttons]
        nolongeravailable = []  # for backward compatibility
        for spec in signtype.specslist:
            if spec[0] in signtypepaths:
                btnidx = signtypepaths.index(spec[0])
                allbuttons[btnidx].setChecked(True)
            else:
                nolongeravailable.append(spec)
        if len(nolongeravailable) > 1:
            print(
                "This sign had sign type options specified that are no longer available and will be removed if you click 'save' (but not 'cancel'). Please make note of the following characteristics:")
            for spec in nolongeravailable:
                print(spec[0])
                signtype.specslist.remove(spec)

        self.addedinfobutton.addedinfo = deepcopy(signtype.addedinfo)

    def getsigntype(self):
        addedinfo = self.addedinfobutton.addedinfo

        allbuttons = [btn for btngrp in self.buttongroups for btn in btngrp.buttons()]
        # when saving, only use options that are both checked AND enabled!
        specslist = [(btn.property('abbreviation.path'), btn.property('abbreviation.include')) for btn in allbuttons if
                     btn.isChecked() and btn.isEnabled()]

        signtype = Signtype(specslist, addedinfo=addedinfo)

        return signtype

    # return the button group that contains the given button
    # in theory I suppose a button could be in more than one button group?
    # ... but here we assume there's only one, so the first hit is returned
    def getButtonGroup(self, thebutton):
        groups = [bg for bg in self.buttongroups if thebutton in bg.buttons()]
        return groups[0]


class Signtype:

    def __init__(self, specslist, addedinfo=None):
        # specslist is a list of triples:
        #   the first element is the full signtype property (correlated with radio buttons in selector dialog)
        #   the second element is the corresponding abbreviation
        #   the third element is a flag indicating whether or not to include this abbreviation in the concise form

        # TODO KV actually pairs! first element is full signtype property composed of abbreviations
        # second element is flag
        self._specslist = specslist
        # TODO KV need backward compatibility for this
        self._addedinfo = addedinfo if addedinfo is not None else AddedInfo()

    @property
    def addedinfo(self):
        return self._addedinfo

    @addedinfo.setter
    def addedinfo(self, addedinfo):
        self._addedinfo = addedinfo if addedinfo is not None else AddedInfo()

    @property
    def specslist(self):
        return self._specslist

    @specslist.setter
    def specslist(self, specslist):
        self._specslist = specslist

    def getabbreviation(self):
        abbrevsdict = self.convertspecstodict()
        abbreviationtext = self.makeabbreviationstring(abbrevsdict)
        abbreviationtext = abbreviationtext.strip()[1:-1]  # effectively remove the top-level ()'s
        return abbreviationtext

    def makeabbreviationstring(self, abbrevsdict):
        if abbrevsdict == {}:
            return ""
        else:
            abbrevlist = []
            abbrevstr = ""
            for k in abbrevsdict.keys():
                abbrevlist.append(k + self.makeabbreviationstring(abbrevsdict[k]))
            abbrevstr += "; ".join(abbrevlist)
            return " (" + abbrevstr + ")"

    def convertspecstodict(self):
        abbrevsdict = {}
        specscopy = [duple for duple in self._specslist]
        for duple in specscopy:
            if duple[1]:  # this is the flag to include the abbreviation in the concise form
                pathlist = duple[0].split('.')  # this is the path of abbreviations to this particular setting
                self.ensurepathindict(pathlist, abbrevsdict)
        return abbrevsdict

    def ensurepathindict(self, pathelements, abbrevsdict):
        if len(pathelements) > 0:
            if pathelements[0] not in abbrevsdict.keys():
                abbrevsdict[pathelements[0]] = {}
            self.ensurepathindict(pathelements[1:], abbrevsdict[pathelements[0]])


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

    def __init__(self, txt="", parentbutton=None):
        super().__init__(text=txt)
        self.parentbutton = parentbutton
        self.toggled.connect(self.checkParent)
        self.childlayout = None

    def checkParent(self, checked):
        if checked and self.parentbutton:
            self.parentbutton.setChecked(True)

    def setChildlayout(self, clayout):
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

    def __init__(self, signtypetoload, mainwindow, **kwargs):
        super().__init__(**kwargs)
        if signtypetoload is not None:
            self.signtype = signtypetoload
        else:
            self.signtype = mainwindow.system_default_signtype  # TODO KV delete self.parent().system_default_signtype

        # TODO KV delete self.app_settings = app_settings
        self.mainwindow = mainwindow

        self.signtype_layout = SigntypeSpecificationLayout()  # TODO KV delete app_ctx)
        self.signtype_layout.setsigntype(self.signtype)

        main_layout = QVBoxLayout()
        main_layout.addLayout(self.signtype_layout)

        separate_line = QFrame()
        separate_line.setFrameShape(QFrame.HLine)
        separate_line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separate_line)

        buttons = QDialogButtonBox.RestoreDefaults | QDialogButtonBox.Save | QDialogButtonBox.Cancel

        self.button_box = QDialogButtonBox(buttons, parent=self)

        self.button_box.clicked.connect(self.handle_button_click)

        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)
        # self.setMinimumSize(QSize(500, 1100))  # 500, 850

    def handle_button_click(self, button):
        standard = self.button_box.standardButton(button)
        if standard == QDialogButtonBox.Cancel:
            # response = QMessageBox.question(self, 'Warning',
            #                                 'If you close the window, any unsaved changes will be lost. Continue?')
            # if response == QMessageBox.Yes:
            #     self.accept()

            self.reject()

        #     elif standard == QDialogButtonBox.RestoreDefaults:
        #         self.movement_tab.remove_all_pages()
        #         self.movement_tab.add_default_movement_tabs(is_system_default=True)
        elif standard == QDialogButtonBox.Save:
            newsigntype = self.signtype_layout.getsigntype()
            self.saved_signtype.emit(newsigntype)
            if self.mainwindow.current_sign is not None and self.signtype != newsigntype:
                self.mainwindow.current_sign.lastmodifiednow()
            self.accept()

        elif standard == QDialogButtonBox.RestoreDefaults:
            self.signtype_layout.setsigntype(self.mainwindow.system_default_signtype)
