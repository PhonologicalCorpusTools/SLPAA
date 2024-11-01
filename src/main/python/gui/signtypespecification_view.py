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
    QWidget
)

from PyQt5.QtCore import (
    pyqtSignal,
    QEvent
)

from gui.modulespecification_dialog import AddedInfoPushButton
from gui.link_help import show_help
from lexicon.module_classes import Signtype
from constant import SIGN_TYPE


class SigntypeSpecificationPanel(QFrame):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.buttongroups = []

        self.tabs = QTabWidget()

        # Create tabs
        self.hands_tab = QWidget()
        self.arms_tab = QWidget()
        self.legs_tab = QWidget()

        # Add tabs to tab widget
        self.tabs.addTab(self.hands_tab, "Hands")
        self.tabs.addTab(self.arms_tab, "Arms")
        self.tabs.addTab(self.legs_tab, "Legs")

        # Initialize layouts for each tab
        self.hands_layout = QVBoxLayout(self.hands_tab)
        self.arms_layout = QVBoxLayout(self.arms_tab)
        self.legs_layout = QVBoxLayout(self.legs_tab)

        # Hands tab controls
        # buttons and groups for highest level
        self.handstype_group = SigntypeButtonGroup(prt=self)
        self.handstype_unspec_radio = SigntypeRadioButton("Unspecified", parentbutton=None)
        self.handstype_unspec_radio.setProperty('abbreviation.path', 'Unspecified')
        self.handstype_unspec_radio.setProperty('abbreviation.include', True)
        self.addedinfobutton_hands = AddedInfoPushButton("Notes")
        self.handstype_1h_radio = SigntypeRadioButton("1 hand", parentbutton=None)
        self.handstype_1h_radio.setProperty('abbreviation.path', SIGN_TYPE["ONE_HAND"])
        self.handstype_1h_radio.setProperty('abbreviation.include', True)
        self.handstype_2h_radio = SigntypeRadioButton("2 hands", parentbutton=None)
        self.handstype_2h_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_HANDS"])
        self.handstype_2h_radio.setProperty('abbreviation.include', True)
        self.handstype_group.addButton(self.handstype_unspec_radio)
        self.handstype_group.addButton(self.handstype_1h_radio)
        self.handstype_group.addButton(self.handstype_2h_radio)
        self.buttongroups.append(self.handstype_group)

        # buttons and groups for 1-handed signs
        self.handstype_1h_group = SigntypeButtonGroup(prt=self)
        self.handstype_1hmove_radio = SigntypeRadioButton('The hand moves', parentbutton=self.handstype_1h_radio)
        self.handstype_1hmove_radio.setProperty('abbreviation.path', SIGN_TYPE["ONE_HAND_MVMT"])
        self.handstype_1hmove_radio.setProperty('abbreviation.include', True)
        self.handstype_1hnomove_radio = SigntypeRadioButton("The hand doesn\'t move",
                                                            parentbutton=self.handstype_1h_radio)
        self.handstype_1hnomove_radio.setProperty('abbreviation.path', SIGN_TYPE["ONE_HAND_NO_MVMT"])
        self.handstype_1hnomove_radio.setProperty('abbreviation.include', True)
        self.handstype_1h_group.addButton(self.handstype_1hmove_radio)
        self.handstype_1h_group.addButton(self.handstype_1hnomove_radio)
        self.buttongroups.append(self.handstype_1h_group)

        # buttons and groups for 2-handed handshape relation
        self.handstype_handshapereln_group = SigntypeButtonGroup(prt=self)
        self.handstype_2hsameshapes_radio = SigntypeRadioButton("H1 and H2 use same set(s) of hand configurations",
                                                                parentbutton=self.handstype_2h_radio)
        self.handstype_2hsameshapes_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_HANDS_SAME_HCONF"])
        self.handstype_2hsameshapes_radio.setProperty('abbreviation.include', True)
        self.handstype_2hdiffshapes_radio = SigntypeRadioButton("H1 and H2 use different set(s) of hand configurations",
                                                                parentbutton=self.handstype_2h_radio)
        self.handstype_2hdiffshapes_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_HANDS_DIFF_HCONF"])
        self.handstype_2hdiffshapes_radio.setProperty('abbreviation.include', True)
        # self.handstype_2hdiffshapes_radio.toggled.connect(self.linkhandconfigbuttons)
        self.handstype_handshapereln_group.addButton(self.handstype_2hsameshapes_radio)
        self.handstype_handshapereln_group.addButton(self.handstype_2hdiffshapes_radio)
        self.buttongroups.append(self.handstype_handshapereln_group)

        # buttons and groups for 2-handed contact relation
        self.handstype_contactreln_group = SigntypeButtonGroup(prt=self)
        self.handstype_2hcontactyes_radio = SigntypeRadioButton("H1 and H2 maintain contact throughout sign",
                                                                parentbutton=self.handstype_2h_radio)
        self.handstype_2hcontactyes_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_HANDS_MAINT_CONT"])
        self.handstype_2hcontactyes_radio.setProperty('abbreviation.include', True)
        self.handstype_2hcontactno_radio = SigntypeRadioButton("H1 and H2 do not maintain contact",
                                                               parentbutton=self.handstype_2h_radio)
        self.handstype_2hcontactno_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_HANDS_NO_CONT"])
        self.handstype_2hcontactno_radio.setProperty('abbreviation.include', False)
        self.handstype_contactreln_group.addButton(self.handstype_2hcontactyes_radio)
        self.handstype_contactreln_group.addButton(self.handstype_2hcontactno_radio)
        self.buttongroups.append(self.handstype_contactreln_group)

        # buttons and groups for bilateral symmetry relation
        self.handstype_symmetryreln_group = SigntypeButtonGroup(prt=self)
        self.handstype_2hsymmetryyes_radio = SigntypeRadioButton("H1 and H2 are bilaterally symmetric",
                                                                 parentbutton=self.handstype_2h_radio)
        self.handstype_2hsymmetryyes_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_HANDS_BISYM"])
        self.handstype_2hsymmetryyes_radio.setProperty('abbreviation.include', True)
        self.handstype_2hsymmetryno_radio = SigntypeRadioButton("H1 and H2 are not bilaterally symmetric",
                                                                parentbutton=self.handstype_2h_radio)
        self.handstype_2hsymmetryno_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_HANDS_NO_BISYM"])
        self.handstype_2hsymmetryno_radio.setProperty('abbreviation.include', False)
        self.handstype_symmetryreln_group.addButton(self.handstype_2hsymmetryyes_radio)
        self.handstype_symmetryreln_group.addButton(self.handstype_2hsymmetryno_radio)
        self.buttongroups.append(self.handstype_symmetryreln_group)

        # buttons and groups for 2-handed movement relation
        self.handstype_mvmtreln_group = SigntypeButtonGroup(prt=self)
        self.handstype_2hmvmtneither_radio = SigntypeRadioButton("Neither hand moves",
                                                                 parentbutton=self.handstype_2h_radio)
        self.handstype_2hmvmtneither_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_HANDS_NO_MVMT"])
        self.handstype_2hmvmtneither_radio.setProperty('abbreviation.include', True)
        self.handstype_2hmvmtone_radio = SigntypeRadioButton("Only 1 hand moves", parentbutton=self.handstype_2h_radio)
        self.handstype_2hmvmtone_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_HANDS_ONE_MVMT"])
        self.handstype_2hmvmtone_radio.setProperty('abbreviation.include', False)
        self.handstype_2hmvmtboth_radio = SigntypeRadioButton("Both hands move", parentbutton=self.handstype_2h_radio)
        self.handstype_2hmvmtboth_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_HANDS_BOTH_MVMT"])
        self.handstype_2hmvmtboth_radio.setProperty('abbreviation.include', False)
        self.handstype_mvmtreln_group.addButton(self.handstype_2hmvmtneither_radio)
        self.handstype_mvmtreln_group.addButton(self.handstype_2hmvmtone_radio)
        self.handstype_mvmtreln_group.addButton(self.handstype_2hmvmtboth_radio)
        self.buttongroups.append(self.handstype_mvmtreln_group)

        # buttons and groups for movement relations in 2-handed signs where only one hand moves
        self.handstype_mvmtonehandreln_group = SigntypeButtonGroup(prt=self)
        self.handstype_2hmvmtoneH1_radio = SigntypeRadioButton("Only H1 moves",
                                                               parentbutton=self.handstype_2hmvmtone_radio)
        self.handstype_2hmvmtoneH1_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_HANDS_ONLY_H1"])
        self.handstype_2hmvmtoneH1_radio.setProperty('abbreviation.include', True)
        self.handstype_2hmvmtoneH2_radio = SigntypeRadioButton("Only H2 moves",
                                                               parentbutton=self.handstype_2hmvmtone_radio)
        self.handstype_2hmvmtoneH2_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_HANDS_ONLY_H2"])
        self.handstype_2hmvmtoneH2_radio.setProperty('abbreviation.include', True)
        self.handstype_mvmtonehandreln_group.addButton(self.handstype_2hmvmtoneH1_radio)
        self.handstype_mvmtonehandreln_group.addButton(self.handstype_2hmvmtoneH2_radio)
        self.buttongroups.append(self.handstype_mvmtonehandreln_group)

        # buttons and groups for movement relations in 2-handed signs where both hands move
        self.handstype_mvmtbothhandreln_group = SigntypeButtonGroup(prt=self)
        self.handstype_2hmvmtbothdiff_radio = SigntypeRadioButton("H1 and H2 move differently",
                                                                  parentbutton=self.handstype_2hmvmtboth_radio)
        self.handstype_2hmvmtbothdiff_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_HANDS_BOTH_MVMT_DIFF"])
        self.handstype_2hmvmtbothdiff_radio.setProperty('abbreviation.include', True)
        self.handstype_2hmvmtbothsame_radio = SigntypeRadioButton("H1 and H2 move similarly",
                                                                  parentbutton=self.handstype_2hmvmtboth_radio)
        self.handstype_2hmvmtbothsame_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_HANDS_BOTH_MVMT_SAME"])
        self.handstype_2hmvmtbothsame_radio.setProperty('abbreviation.include', True)
        self.handstype_mvmtbothhandreln_group.addButton(self.handstype_2hmvmtbothdiff_radio)
        self.handstype_mvmtbothhandreln_group.addButton(self.handstype_2hmvmtbothsame_radio)
        self.buttongroups.append(self.handstype_mvmtbothhandreln_group)

        # buttons and groups for movement timing relations in 2-handed signs
        self.handstype_mvmttimingreln_group = SigntypeButtonGroup(prt=self)
        self.handstype_2hmvmtseq_radio = SigntypeRadioButton("Sequential",
                                                             parentbutton=self.handstype_2hmvmtbothsame_radio)
        self.handstype_2hmvmtseq_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_HANDS_BOTH_MVMT_SEQ"])
        self.handstype_2hmvmtseq_radio.setProperty('abbreviation.include', True)
        self.handstype_2hmvmtsimult_radio = SigntypeRadioButton("Simultaneous",
                                                                parentbutton=self.handstype_2hmvmtbothsame_radio)
        self.handstype_2hmvmtsimult_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_HANDS_BOTH_MVMT_SIMU"])
        self.handstype_2hmvmtsimult_radio.setProperty('abbreviation.include', True)
        self.handstype_mvmttimingreln_group.addButton(self.handstype_2hmvmtseq_radio)
        self.handstype_mvmttimingreln_group.addButton(self.handstype_2hmvmtsimult_radio)
        self.buttongroups.append(self.handstype_mvmttimingreln_group)

        # begin layout for sign type (highest level)
        self.signtype_layout = QVBoxLayout()
        self.firstrow_layout = QHBoxLayout()
        self.firstrow_layout.addWidget(self.handstype_unspec_radio)
        self.firstrow_layout.addStretch()
        self.firstrow_layout.addWidget(self.addedinfobutton_hands)
        self.signtype_layout.addLayout(self.firstrow_layout)
        self.signtype_layout.addWidget(self.handstype_1h_radio)

        ## begin layout for 1-handed sign options
        self.onehand_spacedlayout = QHBoxLayout()
        self.onehand_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        self.onehand_layout = QVBoxLayout()
        self.onehand_layout.addWidget(self.handstype_1hmove_radio)
        self.onehand_layout.addWidget(self.handstype_1hnomove_radio)
        self.onehand_spacedlayout.addLayout(self.onehand_layout)
        self.signtype_layout.addLayout(self.onehand_spacedlayout)
        self.handstype_1h_radio.setchildlayout(self.onehand_spacedlayout)
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
        self.handstype_2hmvmtone_radio.setchildlayout(self.movement_1h_spacedlayout)
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
        self.handstype_2hmvmtboth_radio.setchildlayout(self.movement_2h_spacedlayout)
        #### end layout for 2-handed movement relation in which both hands move

        self.movement_layout.addWidget(self.handstype_2hmvmtboth_radio)

        self.movement_box = QGroupBox("Movement relation")
        self.movement_box.setLayout(self.movement_layout)
        ### end layout for 2-handed movement relation

        self.twohand_spacedlayout.addLayout(self.twohand_col1_layout)
        self.twohand_spacedlayout.addWidget(self.movement_box)

        self.signtype_layout.addLayout(self.twohand_spacedlayout)

        self.handstype_2h_radio.setchildlayout(self.twohand_spacedlayout)
        ## end layout for 2-handed sign options

        self.signtype_box = QGroupBox()
        self.signtype_box.setLayout(self.signtype_layout)
        # end layout for sign type (highest level)

        self.hands_layout.addWidget(self.signtype_box)

        # Arms tab controls
        self.armstype_group = SigntypeButtonGroup(prt=self)
        self.armstype_unspec_radio = SigntypeRadioButton("Unspecified", parentbutton=None)
        self.armstype_unspec_radio.setProperty('abbreviation.path', 'Unspecified')
        self.armstype_unspec_radio.setProperty('abbreviation.include', True)
        self.addedinfobutton_arms = AddedInfoPushButton("Notes")
        self.armstype_1a_radio = SigntypeRadioButton("1 arm", parentbutton=None)
        self.armstype_1a_radio.setProperty('abbreviation.path', SIGN_TYPE["ONE_ARM"])
        self.armstype_1a_radio.setProperty('abbreviation.include', True)
        self.armstype_2a_radio = SigntypeRadioButton("2 arms", parentbutton=None)
        self.armstype_2a_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_ARMS"])
        self.armstype_2a_radio.setProperty('abbreviation.include', True)
        self.armstype_group.addButton(self.armstype_unspec_radio)
        self.armstype_group.addButton(self.armstype_1a_radio)
        self.armstype_group.addButton(self.armstype_2a_radio)
        self.buttongroups.append(self.armstype_group)

        # buttons and groups for 1-armed signs
        self.armstype_1a_group = SigntypeButtonGroup(prt=self)
        self.armstype_1amove_radio = SigntypeRadioButton('The arm moves', parentbutton=self.armstype_1a_radio)
        self.armstype_1amove_radio.setProperty('abbreviation.path', SIGN_TYPE["ONE_ARM_MVMT"])
        self.armstype_1amove_radio.setProperty('abbreviation.include', True)
        self.armstype_1anomove_radio = SigntypeRadioButton("The arm doesn\'t move",
                                                           parentbutton=self.armstype_1a_radio)
        self.armstype_1anomove_radio.setProperty('abbreviation.path', SIGN_TYPE["ONE_ARM_NO_MVMT"])
        self.armstype_1anomove_radio.setProperty('abbreviation.include', True)
        self.armstype_1a_group.addButton(self.armstype_1amove_radio)
        self.armstype_1a_group.addButton(self.armstype_1anomove_radio)
        self.buttongroups.append(self.armstype_1a_group)

        # buttons and groups for 2-arm contact relation
        self.armstype_contactreln_group = SigntypeButtonGroup(prt=self)
        self.armstype_2acontactyes_radio = SigntypeRadioButton("A1 and A2 maintain contact throughout sign",
                                                                parentbutton=self.armstype_2a_radio)
        self.armstype_2acontactyes_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_ARMS_MAINT_CONT"])
        self.armstype_2acontactyes_radio.setProperty('abbreviation.include', True)
        self.armstype_2acontactno_radio = SigntypeRadioButton("A1 and A2 do not maintain contact",
                                                               parentbutton=self.armstype_2a_radio)
        self.armstype_2acontactno_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_ARMS_NO_CONT"])
        self.armstype_2acontactno_radio.setProperty('abbreviation.include', False)
        self.armstype_contactreln_group.addButton(self.armstype_2acontactyes_radio)
        self.armstype_contactreln_group.addButton(self.armstype_2acontactno_radio)
        self.buttongroups.append(self.armstype_contactreln_group)

        # buttons and groups for bilateral symmetry relation
        self.armstype_symmetryreln_group = SigntypeButtonGroup(prt=self)
        self.armstype_2asymmetryyes_radio = SigntypeRadioButton("A1 and A2 are bilaterally symmetric",
                                                                 parentbutton=self.armstype_2a_radio)
        self.armstype_2asymmetryyes_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_ARMS_BISYM"])
        self.armstype_2asymmetryyes_radio.setProperty('abbreviation.include', True)
        self.armstype_2asymmetryno_radio = SigntypeRadioButton("A1 and A2 are not bilaterally symmetric",
                                                                parentbutton=self.armstype_2a_radio)
        self.armstype_2asymmetryno_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_ARMS_NO_BISYM"])
        self.armstype_2asymmetryno_radio.setProperty('abbreviation.include', False)
        self.armstype_symmetryreln_group.addButton(self.armstype_2asymmetryyes_radio)
        self.armstype_symmetryreln_group.addButton(self.armstype_2asymmetryno_radio)
        self.buttongroups.append(self.armstype_symmetryreln_group)

        # buttons and groups for 2-armed movement relation
        self.armstype_mvmtreln_group = SigntypeButtonGroup(prt=self)
        self.armstype_2amvmtneither_radio = SigntypeRadioButton("Neither arm moves",
                                                                 parentbutton=self.armstype_2a_radio)
        self.armstype_2amvmtneither_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_ARMS_NO_MVMT"])
        self.armstype_2amvmtneither_radio.setProperty('abbreviation.include', True)
        self.armstype_2amvmtone_radio = SigntypeRadioButton("Only 1 arm moves", parentbutton=self.armstype_2a_radio)
        self.armstype_2amvmtone_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_ARMS_ONE_MVMT"])
        self.armstype_2amvmtone_radio.setProperty('abbreviation.include', False)
        self.armstype_2amvmtboth_radio = SigntypeRadioButton("Both arms move", parentbutton=self.armstype_2a_radio)
        self.armstype_2amvmtboth_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_ARMS_BOTH_MVMT"])
        self.armstype_2amvmtboth_radio.setProperty('abbreviation.include', False)
        self.armstype_mvmtreln_group.addButton(self.armstype_2amvmtneither_radio)
        self.armstype_mvmtreln_group.addButton(self.armstype_2amvmtone_radio)
        self.armstype_mvmtreln_group.addButton(self.armstype_2amvmtboth_radio)
        self.buttongroups.append(self.armstype_mvmtreln_group)

        # buttons and groups for movement relations in 2-armed signs where only one arm moves
        self.armstype_mvmtonearmreln_group = SigntypeButtonGroup(prt=self)
        self.armstype_2amvmtoneA1_radio = SigntypeRadioButton("Only A1 moves",
                                                               parentbutton=self.armstype_2amvmtone_radio)
        self.armstype_2amvmtoneA1_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_ARMS_ONLY_A1"])
        self.armstype_2amvmtoneA1_radio.setProperty('abbreviation.include', True)
        self.armstype_2amvmtoneA2_radio = SigntypeRadioButton("Only A2 moves",
                                                               parentbutton=self.armstype_2amvmtone_radio)
        self.armstype_2amvmtoneA2_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_ARMS_ONLY_A2"])
        self.armstype_2amvmtoneA2_radio.setProperty('abbreviation.include', True)
        self.armstype_mvmtonearmreln_group.addButton(self.armstype_2amvmtoneA1_radio)
        self.armstype_mvmtonearmreln_group.addButton(self.armstype_2amvmtoneA2_radio)
        self.buttongroups.append(self.armstype_mvmtonearmreln_group)

        # buttons and groups for movement relations in 2-armed signs where both arms move
        self.armstype_mvmtbotharmreln_group = SigntypeButtonGroup(prt=self)
        self.armstype_2amvmtbothdiff_radio = SigntypeRadioButton("A1 and A2 move differently",
                                                                  parentbutton=self.armstype_2amvmtboth_radio)
        self.armstype_2amvmtbothdiff_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_ARMS_BOTH_MVMT_DIFF"])
        self.armstype_2amvmtbothdiff_radio.setProperty('abbreviation.include', True)
        self.armstype_2amvmtbothsame_radio = SigntypeRadioButton("A1 and A2 move similarly",
                                                                  parentbutton=self.armstype_2amvmtboth_radio)
        self.armstype_2amvmtbothsame_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_ARMS_BOTH_MVMT_SAME"])
        self.armstype_2amvmtbothsame_radio.setProperty('abbreviation.include', True)
        self.armstype_mvmtbotharmreln_group.addButton(self.armstype_2amvmtbothdiff_radio)
        self.armstype_mvmtbotharmreln_group.addButton(self.armstype_2amvmtbothsame_radio)
        self.buttongroups.append(self.armstype_mvmtbotharmreln_group)

        # buttons and groups for movement timing relations in 2-handed signs
        self.armstype_mvmttimingreln_group = SigntypeButtonGroup(prt=self)
        self.armstype_2amvmtseq_radio = SigntypeRadioButton("Sequential",
                                                             parentbutton=self.armstype_2amvmtbothsame_radio)
        self.armstype_2amvmtseq_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_ARMS_BOTH_MVMT_SEQ"])
        self.armstype_2amvmtseq_radio.setProperty('abbreviation.include', True)
        self.armstype_2amvmtsimult_radio = SigntypeRadioButton("Simultaneous",
                                                                parentbutton=self.armstype_2amvmtbothsame_radio)
        self.armstype_2amvmtsimult_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_ARMS_BOTH_MVMT_SIMU"])
        self.armstype_2amvmtsimult_radio.setProperty('abbreviation.include', True)
        self.armstype_mvmttimingreln_group.addButton(self.armstype_2amvmtseq_radio)
        self.armstype_mvmttimingreln_group.addButton(self.armstype_2amvmtsimult_radio)
        self.buttongroups.append(self.armstype_mvmttimingreln_group)

        # begin layout for sign type (highest level)
        self.signtype_layout = QVBoxLayout()
        self.firstrow_layout = QHBoxLayout()
        self.firstrow_layout.addWidget(self.armstype_unspec_radio)
        self.firstrow_layout.addStretch()
        self.firstrow_layout.addWidget(self.addedinfobutton_arms)
        self.signtype_layout.addLayout(self.firstrow_layout)
        self.signtype_layout.addWidget(self.armstype_1a_radio)

        ## begin layout for 1-armed sign options
        self.onearm_spacedlayout = QHBoxLayout()
        self.onearm_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        self.onearm_layout = QVBoxLayout()
        self.onearm_layout.addWidget(self.armstype_1amove_radio)
        self.onearm_layout.addWidget(self.armstype_1anomove_radio)
        self.onearm_spacedlayout.addLayout(self.onearm_layout)
        self.signtype_layout.addLayout(self.onearm_spacedlayout)
        self.armstype_1a_radio.setchildlayout(self.onearm_spacedlayout)
        ## end layout for 1-armed sign options

        self.signtype_layout.addWidget(self.armstype_2a_radio)

        ## begin layout for 2-arm sign options
        self.twoarm_spacedlayout = QHBoxLayout()
        self.twoarm_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        self.twoarm_col1_layout = QVBoxLayout()

        ### begin layout for 2-arm contact relation
        self.contact_layout = QVBoxLayout()
        self.contact_layout.addWidget(self.armstype_2acontactyes_radio)
        self.contact_layout.addWidget(self.armstype_2acontactno_radio)
        self.contact_box = QGroupBox("Contact relation")
        self.contact_box.setLayout(self.contact_layout)
        self.twoarm_col1_layout.addWidget(self.contact_box)
        ### end layout for 2-arm contact relation

        ### begin layout for 2-armed bilateral symmetry relation
        self.symmetry_layout = QVBoxLayout()
        self.symmetry_layout.addWidget(self.armstype_2asymmetryyes_radio)
        self.symmetry_layout.addWidget(self.armstype_2asymmetryno_radio)
        self.symmetry_box = QGroupBox("Bilateral symmetry relation")
        self.symmetry_box.setLayout(self.symmetry_layout)
        self.twoarm_col1_layout.addWidget(self.symmetry_box)
        ### end layout for 2-arm contact relation

        self.twoarm_col1_layout.addStretch(1)

        ### begin layout for 2-armed movement relation
        self.movement_layout = QVBoxLayout()
        self.movement_layout.addWidget(self.armstype_2amvmtneither_radio)
        self.movement_layout.addWidget(self.armstype_2amvmtone_radio)

        #### begin layout for 2-armed movement relation in which only one arm moves
        self.movement_1a_spacedlayout = QHBoxLayout()
        self.movement_1a_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        self.movement_1a_layout = QVBoxLayout()
        self.movement_1a_layout.addWidget(self.armstype_2amvmtoneA1_radio)
        self.movement_1a_layout.addWidget(self.armstype_2amvmtoneA2_radio)
        self.movement_1a_spacedlayout.addLayout(self.movement_1a_layout)
        self.movement_layout.addLayout(self.movement_1a_spacedlayout)
        self.armstype_2amvmtone_radio.setchildlayout(self.movement_1a_spacedlayout)
        #### end layout for 2-armed movement relation in which only one arm moves

        self.movement_layout.addWidget(self.armstype_2amvmtboth_radio)

        #### begin layout for 2-armed movement relation in which both arms move
        self.movement_2a_spacedlayout = QHBoxLayout()
        self.movement_2a_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        self.movement_2a_layout = QVBoxLayout()
        self.movement_2a_layout.addWidget(self.armstype_2amvmtbothdiff_radio)
        self.movement_2a_layout.addWidget(self.armstype_2amvmtbothsame_radio)

        #### begin layout for 2-armed movement relation in which both arms move similarly
        self.similarmvmt_spacedlayout = QHBoxLayout()
        self.similarmvmt_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        self.similarmvmt_layout = QVBoxLayout()
        self.similarmvmt_layout.addWidget(self.armstype_2amvmtseq_radio)
        self.similarmvmt_layout.addWidget(self.armstype_2amvmtsimult_radio)

        self.movement_2a_spacedlayout.addLayout(self.movement_2a_layout)
        self.movement_layout.addLayout(self.movement_2a_spacedlayout)
        self.armstype_2amvmtboth_radio.setchildlayout(self.movement_2a_spacedlayout)
        #### end layout for 2-armed movement relation in which both arms move

        self.movement_layout.addWidget(self.armstype_2amvmtboth_radio)

        self.movement_box = QGroupBox("Movement relation")
        self.movement_box.setLayout(self.movement_layout)
        ### end layout for 2-armed movement relation

        self.twoarm_spacedlayout.addLayout(self.twoarm_col1_layout)
        self.twoarm_spacedlayout.addWidget(self.movement_box)

        self.signtype_layout.addLayout(self.twoarm_spacedlayout)

        self.armstype_2a_radio.setchildlayout(self.twoarm_spacedlayout)
        ## end layout for 2-armed sign options

        self.signtype_box = QGroupBox()
        self.signtype_box.setLayout(self.signtype_layout)
        # end layout for sign type (highest level)

        self.arms_layout.addWidget(self.signtype_box)

        # Legs tab controls
        self.legstype_group = SigntypeButtonGroup(prt=self)
        self.legstype_unspec_radio = SigntypeRadioButton("Unspecified", parentbutton=None)
        self.legstype_unspec_radio.setProperty('abbreviation.path', 'Unspecified')
        self.legstype_unspec_radio.setProperty('abbreviation.include', True)
        self.addedinfobutton_legs = AddedInfoPushButton("Notes")  # Separate addedinfo button for legs
        self.legstype_1l_radio = SigntypeRadioButton("1 leg", parentbutton=None)
        self.legstype_1l_radio.setProperty('abbreviation.path', SIGN_TYPE["ONE_LEG"]) # Assuming SIGN_TYPE has ONE_LEG
        self.legstype_1l_radio.setProperty('abbreviation.include', True)
        self.legstype_2l_radio = SigntypeRadioButton("2 legs", parentbutton=None)
        self.legstype_2l_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_LEGS"]) # Assuming SIGN_TYPE has TWO_LEGS
        self.legstype_2l_radio.setProperty('abbreviation.include', True)
        self.legstype_group.addButton(self.legstype_unspec_radio)
        self.legstype_group.addButton(self.legstype_1l_radio)
        self.legstype_group.addButton(self.legstype_2l_radio)
        self.buttongroups.append(self.legstype_group)

        # buttons and groups for 1-legged signs
        self.legstype_1l_group = SigntypeButtonGroup(prt=self)
        self.legstype_1lmove_radio = SigntypeRadioButton('The leg moves', parentbutton=self.legstype_1l_radio)
        self.legstype_1lmove_radio.setProperty('abbreviation.path', SIGN_TYPE["ONE_LEG_MVMT"]) # Assuming SIGN_TYPE has ONE_LEG_MVMT
        self.legstype_1lmove_radio.setProperty('abbreviation.include', True)
        self.legstype_1lnomove_radio = SigntypeRadioButton("The leg doesn\'t move",
                                                            parentbutton=self.legstype_1l_radio)
        self.legstype_1lnomove_radio.setProperty('abbreviation.path', SIGN_TYPE["ONE_LEG_NO_MVMT"]) # Assuming SIGN_TYPE has ONE_LEG_NO_MVMT
        self.legstype_1lnomove_radio.setProperty('abbreviation.include', True)
        self.legstype_1l_group.addButton(self.legstype_1lmove_radio)
        self.legstype_1l_group.addButton(self.legstype_1lnomove_radio)
        self.buttongroups.append(self.legstype_1l_group)

        # buttons and groups for 2-leg contact relation
        self.legstype_contactreln_group = SigntypeButtonGroup(prt=self)
        self.legstype_2lcontactyes_radio = SigntypeRadioButton("L1 and L2 maintain contact throughout sign",
                                                                parentbutton=self.legstype_2l_radio)
        self.legstype_2lcontactyes_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_LEGS_MAINT_CONT"])
        self.legstype_2lcontactyes_radio.setProperty('abbreviation.include', True)
        self.legstype_2lcontactno_radio = SigntypeRadioButton("L1 and L2 do not maintain contact",
                                                               parentbutton=self.legstype_2l_radio)
        self.legstype_2lcontactno_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_LEGS_NO_CONT"])
        self.legstype_2lcontactno_radio.setProperty('abbreviation.include', False)
        self.legstype_contactreln_group.addButton(self.legstype_2lcontactyes_radio)
        self.legstype_contactreln_group.addButton(self.legstype_2lcontactno_radio)
        self.buttongroups.append(self.legstype_contactreln_group)

        # buttons and groups for bilateral symmetry relation
        self.legstype_symmetryreln_group = SigntypeButtonGroup(prt=self)
        self.legstype_2lsymmetryyes_radio = SigntypeRadioButton("L1 and L2 are bilaterally symmetric",
                                                                 parentbutton=self.legstype_2l_radio)
        self.legstype_2lsymmetryyes_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_LEGS_BISYM"])
        self.legstype_2lsymmetryyes_radio.setProperty('abbreviation.include', True)
        self.legstype_2lsymmetryno_radio = SigntypeRadioButton("L1 and L2 are not bilaterally symmetric",
                                                                parentbutton=self.legstype_2l_radio)
        self.legstype_2lsymmetryno_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_LEGS_NO_BISYM"])
        self.legstype_2lsymmetryno_radio.setProperty('abbreviation.include', False)
        self.legstype_symmetryreln_group.addButton(self.legstype_2lsymmetryyes_radio)
        self.legstype_symmetryreln_group.addButton(self.legstype_2lsymmetryno_radio)
        self.buttongroups.append(self.legstype_symmetryreln_group)

        # buttons and groups for 2-leg movement relation
        self.legstype_mvmtreln_group = SigntypeButtonGroup(prt=self)
        self.legstype_2lmvmtneither_radio = SigntypeRadioButton("Neither leg moves",
                                                                 parentbutton=self.legstype_2l_radio)
        self.legstype_2lmvmtneither_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_LEGS_NO_MVMT"])
        self.legstype_2lmvmtneither_radio.setProperty('abbreviation.include', True)
        self.legstype_2lmvmtone_radio = SigntypeRadioButton("Only 1 leg moves", parentbutton=self.legstype_2l_radio)
        self.legstype_2lmvmtone_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_LEGS_ONE_MVMT"])
        self.legstype_2lmvmtone_radio.setProperty('abbreviation.include', False)
        self.legstype_2lmvmtboth_radio = SigntypeRadioButton("Both legs move", parentbutton=self.legstype_2l_radio)
        self.legstype_2lmvmtboth_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_LEGS_BOTH_MVMT"])
        self.legstype_2lmvmtboth_radio.setProperty('abbreviation.include', False)
        self.legstype_mvmtreln_group.addButton(self.legstype_2lmvmtneither_radio)
        self.legstype_mvmtreln_group.addButton(self.legstype_2lmvmtone_radio)
        self.legstype_mvmtreln_group.addButton(self.legstype_2lmvmtboth_radio)
        self.buttongroups.append(self.legstype_mvmtreln_group)

        # buttons and groups for 2-legged movement relation
        self.legstype_mvmtreln_group = SigntypeButtonGroup(prt=self)
        self.legstype_2lmvmtneither_radio = SigntypeRadioButton("Neither leg moves",
                                                                parentbutton=self.legstype_2l_radio)
        self.legstype_2lmvmtneither_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_LEGS_NO_MVMT"])
        self.legstype_2lmvmtneither_radio.setProperty('abbreviation.include', True)
        self.legstype_2lmvmtone_radio = SigntypeRadioButton("Only 1 leg moves", parentbutton=self.legstype_2l_radio)
        self.legstype_2lmvmtone_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_LEGS_ONE_MVMT"])
        self.legstype_2lmvmtone_radio.setProperty('abbreviation.include', False)
        self.legstype_2lmvmtboth_radio = SigntypeRadioButton("Both legs move", parentbutton=self.legstype_2l_radio)
        self.legstype_2lmvmtboth_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_LEGS_BOTH_MVMT"])
        self.legstype_2lmvmtboth_radio.setProperty('abbreviation.include', False)
        self.legstype_mvmtreln_group.addButton(self.legstype_2lmvmtneither_radio)
        self.legstype_mvmtreln_group.addButton(self.legstype_2lmvmtone_radio)
        self.legstype_mvmtreln_group.addButton(self.legstype_2lmvmtboth_radio)
        self.buttongroups.append(self.legstype_mvmtreln_group)

        # buttons and groups for movement relations in 2-legged signs where only one leg moves
        self.legstype_mvmtonelegreln_group = SigntypeButtonGroup(prt=self)
        self.legstype_2lmvmtoneL1_radio = SigntypeRadioButton("Only L1 moves",
                                                              parentbutton=self.legstype_2lmvmtone_radio)
        self.legstype_2lmvmtoneL1_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_LEGS_ONLY_L1"])
        self.legstype_2lmvmtoneL1_radio.setProperty('abbreviation.include', True)
        self.legstype_2lmvmtoneL2_radio = SigntypeRadioButton("Only L2 moves",
                                                              parentbutton=self.legstype_2lmvmtone_radio)
        self.legstype_2lmvmtoneL2_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_LEGS_ONLY_L2"])
        self.legstype_2lmvmtoneL2_radio.setProperty('abbreviation.include', True)
        self.legstype_mvmtonelegreln_group.addButton(self.legstype_2lmvmtoneL1_radio)
        self.legstype_mvmtonelegreln_group.addButton(self.legstype_2lmvmtoneL2_radio)
        self.buttongroups.append(self.legstype_mvmtonelegreln_group)

        # buttons and groups for movement relations in 2-legged signs where both legs move
        self.legstype_mvmtbothlegreln_group = SigntypeButtonGroup(prt=self)
        self.legstype_2lmvmtbothdiff_radio = SigntypeRadioButton("L1 and L2 move differently",
                                                                 parentbutton=self.legstype_2lmvmtboth_radio)
        self.legstype_2lmvmtbothdiff_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_LEGS_BOTH_MVMT_DIFF"])
        self.legstype_2lmvmtbothdiff_radio.setProperty('abbreviation.include', True)
        self.legstype_2lmvmtbothsame_radio = SigntypeRadioButton("L1 and L2 move similarly",
                                                                 parentbutton=self.legstype_2lmvmtboth_radio)
        self.legstype_2lmvmtbothsame_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_LEGS_BOTH_MVMT_SAME"])
        self.legstype_2lmvmtbothsame_radio.setProperty('abbreviation.include', True)
        self.legstype_mvmtbothlegreln_group.addButton(self.legstype_2lmvmtbothdiff_radio)
        self.legstype_mvmtbothlegreln_group.addButton(self.legstype_2lmvmtbothsame_radio)
        self.buttongroups.append(self.legstype_mvmtbothlegreln_group)

        # buttons and groups for movement timing relations in 2-legged signs
        self.legstype_mvmttimingreln_group = SigntypeButtonGroup(prt=self)
        self.legstype_2lmvmtseq_radio = SigntypeRadioButton("Sequential",
                                                            parentbutton=self.legstype_2lmvmtbothsame_radio)
        self.legstype_2lmvmtseq_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_LEGS_BOTH_MVMT_SEQ"])
        self.legstype_2lmvmtseq_radio.setProperty('abbreviation.include', True)
        self.legstype_2lmvmtsimult_radio = SigntypeRadioButton("Simultaneous",
                                                               parentbutton=self.legstype_2lmvmtbothsame_radio)
        self.legstype_2lmvmtsimult_radio.setProperty('abbreviation.path', SIGN_TYPE["TWO_LEGS_BOTH_MVMT_SIMU"])
        self.legstype_2lmvmtsimult_radio.setProperty('abbreviation.include', True)
        self.legstype_mvmttimingreln_group.addButton(self.legstype_2lmvmtseq_radio)
        self.legstype_mvmttimingreln_group.addButton(self.legstype_2lmvmtsimult_radio)
        self.buttongroups.append(self.legstype_mvmttimingreln_group)

        # begin layout for sign type (highest level) - Legs
        self.signtype_layout = QVBoxLayout() # Separate layout for legs
        self.firstrow_layout = QHBoxLayout()
        self.firstrow_layout.addWidget(self.legstype_unspec_radio)
        self.firstrow_layout.addStretch()
        self.firstrow_layout.addWidget(self.addedinfobutton_legs) # Add legs addedinfo button
        self.signtype_layout.addLayout(self.firstrow_layout)
        self.signtype_layout.addWidget(self.legstype_1l_radio)

        ## begin layout for 1-legged sign options
        self.oneleg_spacedlayout = QHBoxLayout()
        self.oneleg_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        self.oneleg_layout = QVBoxLayout()
        self.oneleg_layout.addWidget(self.legstype_1lmove_radio)
        self.oneleg_layout.addWidget(self.legstype_1lnomove_radio)
        self.oneleg_spacedlayout.addLayout(self.oneleg_layout)
        self.signtype_layout.addLayout(self.oneleg_spacedlayout)
        self.legstype_1l_radio.setchildlayout(self.oneleg_spacedlayout)
        ## end layout for 1-legged sign options

        self.signtype_layout.addWidget(self.legstype_2l_radio)

        ## begin layout for 2-leg sign options
        self.twoleg_spacedlayout = QHBoxLayout()
        self.twoleg_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        self.twoleg_col1_layout = QVBoxLayout()

        ### begin layout for 2-leg contact relation
        self.contact_layout = QVBoxLayout()
        self.contact_layout.addWidget(self.legstype_2lcontactyes_radio)
        self.contact_layout.addWidget(self.legstype_2lcontactno_radio)
        self.contact_box = QGroupBox("Contact relation")
        self.contact_box.setLayout(self.contact_layout)
        self.twoleg_col1_layout.addWidget(self.contact_box)
        ### end layout for 2-handed contact relation

        ### begin layout for 2-leg bilateral symmetry relation
        self.symmetry_layout = QVBoxLayout()
        self.symmetry_layout.addWidget(self.legstype_2lsymmetryyes_radio)
        self.symmetry_layout.addWidget(self.legstype_2lsymmetryno_radio)
        self.symmetry_box = QGroupBox("Bilateral symmetry relation")
        self.symmetry_box.setLayout(self.symmetry_layout)
        self.twoleg_col1_layout.addWidget(self.symmetry_box)
        ### end layout for 2-leg contact relation

        self.twoleg_col1_layout.addStretch(1)

        ### begin layout for 2-handed movement relation
        self.movement_layout = QVBoxLayout()
        self.movement_layout.addWidget(self.legstype_2lmvmtneither_radio)
        self.movement_layout.addWidget(self.legstype_2lmvmtone_radio)

        #### begin layout for 2-leg movement relation in which only one leg moves
        self.movement_1l_spacedlayout = QHBoxLayout()
        self.movement_1l_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        self.movement_1l_layout = QVBoxLayout()
        self.movement_1l_layout.addWidget(self.legstype_2lmvmtoneL1_radio)
        self.movement_1l_layout.addWidget(self.legstype_2lmvmtoneL2_radio)
        self.movement_1l_spacedlayout.addLayout(self.movement_1l_layout)
        self.movement_layout.addLayout(self.movement_1l_spacedlayout)
        self.legstype_2lmvmtone_radio.setchildlayout(self.movement_1l_spacedlayout)
        #### end layout for 2-leg movement relation in which only one leg moves

        self.movement_layout.addWidget(self.legstype_2lmvmtboth_radio)

        #### begin layout for 2-leg movement relation in which both legs move
        self.movement_2l_spacedlayout = QHBoxLayout()
        self.movement_2l_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        self.movement_2l_layout = QVBoxLayout()
        self.movement_2l_layout.addWidget(self.legstype_2lmvmtbothdiff_radio)
        self.movement_2l_layout.addWidget(self.legstype_2lmvmtbothsame_radio)

        #### begin layout for 2-leg movement relation in which both hands move similarly
        self.similarmvmt_spacedlayout = QHBoxLayout()
        self.similarmvmt_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        self.similarmvmt_layout = QVBoxLayout()
        self.similarmvmt_layout.addWidget(self.legstype_2lmvmtseq_radio)
        self.similarmvmt_layout.addWidget(self.legstype_2lmvmtsimult_radio)

        self.movement_2l_spacedlayout.addLayout(self.movement_2l_layout)
        self.movement_layout.addLayout(self.movement_2l_spacedlayout)
        self.legstype_2lmvmtboth_radio.setchildlayout(self.movement_2l_spacedlayout)
        #### end layout for 2-leg movement relation in which both hands move

        self.movement_layout.addWidget(self.legstype_2lmvmtboth_radio)

        self.movement_box = QGroupBox("Movement relation")
        self.movement_box.setLayout(self.movement_layout)
        ### end layout for 2-leg movement relation

        self.twoleg_spacedlayout.addLayout(self.twoleg_col1_layout)
        self.twoleg_spacedlayout.addWidget(self.movement_box)

        self.signtype_layout.addLayout(self.twoleg_spacedlayout)

        self.legstype_2l_radio.setchildlayout(self.twoleg_spacedlayout)
        ## end layout for 2-leg sign options

        self.signtype_box = QGroupBox()
        self.signtype_box.setLayout(self.signtype_layout)
        # end layout for sign type (highest level)

        self.legs_layout.addWidget(self.signtype_box)

        # Add the tab widget to the main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

        # ensure that Unspecified is selected by default
        # TODO KV keep this? or does loadspecs preclude it?
        # self.handstype_unspec_radio.toggle()
    def setsigntype(self, signtype):
        # clear all
        self.clear()

        # then reset according to input signtype
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
                "This sign had sign type options specified that are no longer available and will be removed" +
                " if you click 'save' (but not 'cancel'). Please make note of the following characteristics:")
            for spec in nolongeravailable:
                print(spec[0])
                signtype.specslist.remove(spec)

        self.addedinfobutton_hands.addedinfo = deepcopy(signtype.addedinfo)

        # uncheck all buttons

    def clear(self):
        for g in self.buttongroups:
            g.setExclusive(False)
            for b in g.buttons():
                b.setEnabled(True)
                b.setChecked(False)
            g.setExclusive(True)

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


    # return the button group that contains the given button
    # in theory I suppose a button could be in more than one button group?
    # ... but here we assume there's only one, so the first hit is returned
    def getButtonGroup(self, thebutton):
        groups = [bg for bg in self.buttongroups if thebutton in bg.buttons()]
        return groups[0]

    def symmetry_dependencies_warning(self):
        conflict = False
        if self.handstype_2hsymmetryyes_radio.isChecked():
            msg = "Bilateral symmetry relation conflicts with: \n"
            if self.handstype_2hdiffshapes_radio.isChecked():
                msg += "- Hand configuration relation\n"
                conflict = True
            if self.handstype_2hmvmtone_radio.isChecked() and self.handstype_2hmvmtone_radio.isEnabled():
                msg += "- Movement relation (only 1 hand moves)\n"
                conflict = True
            if self.handstype_2hmvmtbothdiff_radio.isChecked() and self.handstype_2hmvmtbothdiff_radio.isEnabled():
                msg += "- Movement relation (hands move differently)\n"
                conflict = True
        if conflict == True:
            return msg
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

    def __init__(self, txt="", parentbutton=None):
        super().__init__(text=txt)
        self.parentbutton = parentbutton
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
            show_help('signtype')

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
            # TODO KV - problem: not all relevant radio buttons are enabled when restoring default
            self.signtype_widget.setsigntype(self.get_default_signtype())