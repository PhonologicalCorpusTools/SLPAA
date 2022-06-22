import os
import json
from PyQt5.QtWidgets import (
    QFrame,
    QGridLayout,
    QLineEdit,
    QPushButton,
    QDialog,
    QHBoxLayout,
    QListView,
    QVBoxLayout,
    QBoxLayout,
    QFileDialog,
    QWidget,
    QTabWidget,
    QTabBar,
    QDialogButtonBox,
    QMessageBox,
    QSlider,
    QTreeView,
    QComboBox,
    QLabel,
    QCompleter,
    QAbstractItemView,
    QStyledItemDelegate,
    QStyle,
    QStyleOptionButton,
    QApplication,
    QHeaderView,
    QStyleOptionFrame,
    QErrorMessage,
    QButtonGroup,
    QRadioButton,
    QCheckBox,
    QGroupBox,
    QSpacerItem,
    QSizePolicy,
    QAbstractButton
)

from PyQt5.QtGui import (
    QBrush,
    QColor,
    QPen,
    QPolygonF,
    QPixmap,
    QIcon
)

from PyQt5.QtCore import (
    Qt,
    QPoint,
    QRectF,
    QAbstractListModel,
    pyqtSignal,
    QSize,
    QEvent
)

from .helper_widget import EditableTabBar
from copy import copy, deepcopy
from pprint import pprint


class SigntypeSpecificationLayout(QVBoxLayout):
    def __init__(self, **kwargs):  # TODO KV delete  app_ctx,
        super().__init__(**kwargs)

        self.buttongroups = []

        # TODO KV should button properties be integers instead of strings,
        # so it's easier to add more user-specified options?

        # buttons and groups for highest level
        self.handstype_buttongroup = SigntypeButtonGroup(prt=self)
        self.handstype_unspec_radio = SigntypeRadioButton('Unspecified', parentbutton=None)
        self.handstype_unspec_radio.setProperty('signtype', 'unspecified')
        self.handstype_unspec_radio.setProperty('abbreviation', ('Unspecified', False))
        self.handstype_1h_radio = SigntypeRadioButton('1 hand', parentbutton=None)
        self.handstype_1h_radio.setProperty('signtype', '1h')
        self.handstype_1h_radio.setProperty('abbreviation', ('1h', True))
        self.handstype_2h_radio = SigntypeRadioButton('2 hands', parentbutton=None)
        self.handstype_2h_radio.setProperty('signtype', '2h')
        self.handstype_2h_radio.setProperty('abbreviation', ('2h', True))
        self.handstype_buttongroup.addButton(self.handstype_unspec_radio)
        self.handstype_buttongroup.addButton(self.handstype_1h_radio)
        self.handstype_buttongroup.addButton(self.handstype_2h_radio)
        self.buttongroups.append(self.handstype_buttongroup)

        # buttons and groups for 1-handed signs
        self.handstype_1h_buttongroup = SigntypeButtonGroup(prt=self)
        self.handstype_1hmove_radio = SigntypeRadioButton('The hand moves', parentbutton=self.handstype_1h_radio)
        self.handstype_1hmove_radio.setProperty('signtype', '1h.moves')
        self.handstype_1hmove_radio.setProperty('abbreviation', ('moves', True))
        self.handstype_1hnomove_radio = SigntypeRadioButton('The hand doesn\'t move', parentbutton=self.handstype_1h_radio)
        self.handstype_1hnomove_radio.setProperty('signtype', '1h.no mvmt')
        self.handstype_1hnomove_radio.setProperty('abbreviation', ('no mvmt', True))
        self.handstype_1h_buttongroup.addButton(self.handstype_1hmove_radio)
        self.handstype_1h_buttongroup.addButton(self.handstype_1hnomove_radio)
        self.buttongroups.append(self.handstype_1h_buttongroup)

        # buttons and groups for 2-handed handshape relation
        self.handstype_handshapereln_buttongroup = SigntypeButtonGroup(prt=self)
        self.handstype_2hsameshapes_radio = SigntypeRadioButton('H1 and H2 use same set(s) of hand configurations', parentbutton=self.handstype_2h_radio)
        self.handstype_2hsameshapes_radio.setProperty('signtype', '2h.same HSs')
        self.handstype_2hsameshapes_radio.setProperty('abbreviation', ('same HSs', True))
        self.handstype_2hdiffshapes_radio = SigntypeRadioButton('H1 and H2 use different set(s) of hand configurations', parentbutton=self.handstype_2h_radio)
        self.handstype_2hdiffshapes_radio.setProperty('signtype', '2h.different HSs')
        self.handstype_2hdiffshapes_radio.setProperty('abbreviation', ('different HSs', True))
        self.handstype_handshapereln_buttongroup.addButton(self.handstype_2hsameshapes_radio)
        self.handstype_handshapereln_buttongroup.addButton(self.handstype_2hdiffshapes_radio)
        self.buttongroups.append(self.handstype_handshapereln_buttongroup)

        # buttons and groups for 2-handed contact relation
        self.handstype_contactreln_buttongroup = SigntypeButtonGroup(prt=self)
        self.handstype_2hcontactyes_radio = SigntypeRadioButton('H1 and H2 maintain contact throughout sign', parentbutton=self.handstype_2h_radio)
        self.handstype_2hcontactyes_radio.setProperty('signtype', '2h.maintain contact')
        self.handstype_2hcontactyes_radio.setProperty('abbreviation', ('maintain contact', True))
        self.handstype_2hcontactno_radio = SigntypeRadioButton('H1 and H2 do not maintain contact', parentbutton=self.handstype_2h_radio)
        self.handstype_2hcontactno_radio.setProperty('signtype', '2h.contact not maintained')
        self.handstype_2hcontactno_radio.setProperty('abbreviation', ('contact not maintained', False))
        self.handstype_contactreln_buttongroup.addButton(self.handstype_2hcontactyes_radio)
        self.handstype_contactreln_buttongroup.addButton(self.handstype_2hcontactno_radio)
        self.buttongroups.append(self.handstype_contactreln_buttongroup)

        # buttons and groups for 2-handed movement relation
        self.handstype_mvmtreln_buttongroup = SigntypeButtonGroup(prt=self)
        self.handstype_2hmvmtneither_radio = SigntypeRadioButton('Neither hand moves', parentbutton=self.handstype_2h_radio)
        self.handstype_2hmvmtneither_radio.setProperty('signtype', '2h.neither moves')
        self.handstype_2hmvmtneither_radio.setProperty('abbreviation', ('neither moves', True))
        self.handstype_2hmvmtone_radio = SigntypeRadioButton('Only 1 hand moves', parentbutton=self.handstype_2h_radio)
        self.handstype_2hmvmtone_radio.setProperty('signtype', '2h.only 1 moves')
        self.handstype_2hmvmtone_radio.setProperty('abbreviation', ('only 1 moves', False))
        self.handstype_2hmvmtboth_radio = SigntypeRadioButton('Both hands move', parentbutton=self.handstype_2h_radio)
        self.handstype_2hmvmtboth_radio.setProperty('signtype', '2h.both move')
        self.handstype_2hmvmtboth_radio.setProperty('abbreviation', ('both move', False))
        self.handstype_mvmtreln_buttongroup.addButton(self.handstype_2hmvmtneither_radio)
        self.handstype_mvmtreln_buttongroup.addButton(self.handstype_2hmvmtone_radio)
        self.handstype_mvmtreln_buttongroup.addButton(self.handstype_2hmvmtboth_radio)
        self.buttongroups.append(self.handstype_mvmtreln_buttongroup)

        # buttons and groups for movement relations in 2-handed signs where only one hand moves
        self.handstype_mvmtonehandreln_buttongroup = SigntypeButtonGroup(prt=self)
        self.handstype_2hmvmtoneH1_radio = SigntypeRadioButton('Only H1 moves', parentbutton=self.handstype_2hmvmtone_radio)
        self.handstype_2hmvmtoneH1_radio.setProperty('signtype', '2h.only 1 moves.H1 moves')
        self.handstype_2hmvmtoneH1_radio.setProperty('abbreviation', ('H1 moves', True))
        self.handstype_2hmvmtoneH2_radio = SigntypeRadioButton('Only H2 moves', parentbutton=self.handstype_2hmvmtone_radio)
        self.handstype_2hmvmtoneH2_radio.setProperty('signtype', '2h.only 1 moves.H2 moves')
        self.handstype_2hmvmtoneH2_radio.setProperty('abbreviation', ('H2 moves', True))
        self.handstype_mvmtonehandreln_buttongroup.addButton(self.handstype_2hmvmtoneH1_radio)
        self.handstype_mvmtonehandreln_buttongroup.addButton(self.handstype_2hmvmtoneH2_radio)
        self.buttongroups.append(self.handstype_mvmtonehandreln_buttongroup)

        # buttons and groups for movement relations in 2-handed signs where both hands move
        self.handstype_mvmtbothhandreln_buttongroup = SigntypeButtonGroup(prt=self)
        self.handstype_2hmvmtbothdiff_radio = SigntypeRadioButton('H1 and H2 move differently', parentbutton=self.handstype_2hmvmtboth_radio)
        self.handstype_2hmvmtbothdiff_radio.setProperty('signtype', '2h.both move.move differently')
        self.handstype_2hmvmtbothdiff_radio.setProperty('abbreviation', ('move differently', True))
        self.handstype_2hmvmtbothsame_radio = SigntypeRadioButton('H1 and H2 move similarly', parentbutton=self.handstype_2hmvmtboth_radio)
        self.handstype_2hmvmtbothsame_radio.setProperty('signtype', '2h.both move.move similarly')
        self.handstype_2hmvmtbothsame_radio.setProperty('abbreviation', ('move similarly', True))
        self.handstype_mvmtbothhandreln_buttongroup.addButton(self.handstype_2hmvmtbothdiff_radio)
        self.handstype_mvmtbothhandreln_buttongroup.addButton(self.handstype_2hmvmtbothsame_radio)
        self.buttongroups.append(self.handstype_mvmtbothhandreln_buttongroup)

        # buttons and groups for movement direction relations in 2-handed signs
        self.handstype_mvmtdirreln_buttongroup = SigntypeButtonGroup(prt=self)
        self.handstype_2hmvmtsamedir_radio = SigntypeRadioButton('Same', parentbutton=self.handstype_2hmvmtbothsame_radio)
        self.handstype_2hmvmtsamedir_radio.setProperty('signtype', '2h.both move.move similarly.same directions')
        self.handstype_2hmvmtsamedir_radio.setProperty('abbreviation', ('same directions', True))
        self.handstype_2hmvmtdiffdir_radio = SigntypeRadioButton('Different', parentbutton=self.handstype_2hmvmtbothsame_radio)
        self.handstype_2hmvmtdiffdir_radio.setProperty('signtype', '2h.both move.move similarly.different directions')
        self.handstype_2hmvmtdiffdir_radio.setProperty('abbreviation', ('different directions', True))
        self.handstype_2hmvmtirreldir_radio = SigntypeRadioButton('Not relevant', parentbutton=self.handstype_2hmvmtbothsame_radio)
        self.handstype_2hmvmtirreldir_radio.setProperty('signtype', '2h.both move.move similarly.direction N/A')
        self.handstype_2hmvmtirreldir_radio.setProperty('abbreviation', ('direction N/A', False))
        self.handstype_mvmtdirreln_buttongroup.addButton(self.handstype_2hmvmtsamedir_radio)
        self.handstype_mvmtdirreln_buttongroup.addButton(self.handstype_2hmvmtdiffdir_radio)
        self.handstype_mvmtdirreln_buttongroup.addButton(self.handstype_2hmvmtirreldir_radio)
        self.buttongroups.append(self.handstype_mvmtdirreln_buttongroup)

        # buttons and groups for movement timing relations in 2-handed signs
        self.handstype_mvmttimingreln_buttongroup = SigntypeButtonGroup(prt=self)
        self.handstype_2hmvmtseq_radio = SigntypeRadioButton('Sequential', parentbutton=self.handstype_2hmvmtbothsame_radio)
        self.handstype_2hmvmtseq_radio.setProperty('signtype', '2h.both move.move similarly.sequential')
        self.handstype_2hmvmtseq_radio.setProperty('abbreviation', ('sequential', True))
        self.handstype_2hmvmtsimult_radio = SigntypeRadioButton('Simultaneous', parentbutton=self.handstype_2hmvmtbothsame_radio)
        self.handstype_2hmvmtsimult_radio.setProperty('signtype', '2h.both move.move similarly.simultaneous')
        self.handstype_2hmvmtsimult_radio.setProperty('abbreviation', ('simultaneous', True))
        self.handstype_mvmttimingreln_buttongroup.addButton(self.handstype_2hmvmtseq_radio)
        self.handstype_mvmttimingreln_buttongroup.addButton(self.handstype_2hmvmtsimult_radio)
        self.buttongroups.append(self.handstype_mvmttimingreln_buttongroup)

        # buttons and groups for mirroring relations in 2-handed signs
        self.handstype_mvmtmirroredreln_buttongroup = SigntypeButtonGroup(prt=self)
        self.handstype_mirroredall_radio = SigntypeRadioButton('Everything is mirrored / in phase', parentbutton=self.handstype_2hmvmtsimult_radio)
        self.handstype_mirroredall_radio.setProperty('signtype', '2h.both move.move similarly.simultaneous.all in phase')
        self.handstype_mirroredall_radio.setProperty('abbreviation', ('all in phase', False))
        self.handstype_mirroredexcept_radio = SigntypeRadioButton('Everything is mirrored / in phase except:', parentbutton=self.handstype_2hmvmtsimult_radio)
        self.handstype_mirroredexcept_radio.setProperty('signtype', '2h.both move.move similarly.simultaneous.in phase except')
        self.handstype_mirroredexcept_radio.setProperty('abbreviation', ('in phase except', True))
        self.handstype_mvmtmirroredreln_buttongroup.addButton(self.handstype_mirroredall_radio)
        self.handstype_mvmtmirroredreln_buttongroup.addButton(self.handstype_mirroredexcept_radio)
        self.handstype_mvmtmirroredexcept_buttongroup = SigntypeButtonGroup(prt=self)
        self.handstype_mvmtmirroredexcept_buttongroup.setExclusive(False)
        self.handstype_2hmvmtexceptloc_check = SigntypeCheckBox('Location', parentbutton=self.handstype_mirroredexcept_radio)
        self.handstype_2hmvmtexceptloc_check.setProperty('signtype', '2h.both move.move similarly.simultaneous.in phase except.Loc')
        self.handstype_2hmvmtexceptloc_check.setProperty('abbreviation', ('Loc', True))
        self.handstype_2hmvmtexceptshape_check = SigntypeCheckBox('Hand configuration', parentbutton=self.handstype_mirroredexcept_radio)
        self.handstype_2hmvmtexceptshape_check.setProperty('signtype', '2h.both move.move similarly.simultaneous.in phase except.HS')
        self.handstype_2hmvmtexceptshape_check.setProperty('abbreviation', ('HS', True))
        self.handstype_2hmvmtexceptorientn_check = SigntypeCheckBox('Orientation', parentbutton=self.handstype_mirroredexcept_radio)
        self.handstype_2hmvmtexceptorientn_check.setProperty('signtype', '2h.both move.move similarly.simultaneous.in phase except.Ori')
        self.handstype_2hmvmtexceptorientn_check.setProperty('abbreviation', ('Ori', True))
        self.handstype_mvmtmirroredexcept_buttongroup.addButton(self.handstype_2hmvmtexceptloc_check)
        self.handstype_mvmtmirroredexcept_buttongroup.addButton(self.handstype_2hmvmtexceptshape_check)
        self.handstype_mvmtmirroredexcept_buttongroup.addButton(self.handstype_2hmvmtexceptorientn_check)
        self.buttongroups.append(self.handstype_mvmtmirroredreln_buttongroup)
        self.buttongroups.append(self.handstype_mvmtmirroredexcept_buttongroup)

        # begin layout for sign type (highest level)
        self.signtype_layout = QVBoxLayout()
        self.signtype_layout.addWidget(self.handstype_unspec_radio)
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
        self.handshape_box = QGroupBox('Hand configuration relation')
        self.handshape_box.setLayout(self.handshape_layout)
        self.twohand_col1_layout.addWidget(self.handshape_box)
        ### end layout for 2-handed handshape relation

        ### begin layout for 2-handed contact relation
        self.contact_layout = QVBoxLayout()
        self.contact_layout.addWidget(self.handstype_2hcontactyes_radio)
        self.contact_layout.addWidget(self.handstype_2hcontactno_radio)
        self.contact_box = QGroupBox('Contact relation')
        self.contact_box.setLayout(self.contact_layout)
        self.twohand_col1_layout.addWidget(self.contact_box)
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
        self.similarmvmt_spacedlayout = QHBoxLayout()
        self.similarmvmt_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))

        ##### begin layout for 2-handed movement direction relation
        self.direction_layout = QVBoxLayout()
        self.direction_layout.addWidget(QLabel('H1 and H2\'s directions of movement are:'))
        self.direction_layout.addWidget(self.handstype_2hmvmtsamedir_radio)
        self.direction_layout.addWidget(self.handstype_2hmvmtdiffdir_radio)
        self.direction_layout.addWidget(self.handstype_2hmvmtirreldir_radio)
        self.direction_layout.addStretch(1)
        self.direction_box = QGroupBox('Movement direction relation')
        self.direction_box.setLayout(self.direction_layout)
        self.similarmvmt_spacedlayout.addWidget(self.direction_box)
        ##### end layout for 2-handed movement direction relation

        ##### begin layout for 2-handed movement timing relation
        self.timing_layout = QVBoxLayout()
        self.timing_layout.addWidget(self.handstype_2hmvmtseq_radio)
        self.timing_layout.addWidget(self.handstype_2hmvmtsimult_radio)

        ###### begin layout for simultaneous movement
        self.simultaneous_spacedlayout = QHBoxLayout()
        self.simultaneous_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        self.simultaneous_layout = QVBoxLayout()
        self.simultaneous_layout.addWidget(self.handstype_mirroredall_radio)
        self.simultaneous_layout.addWidget(self.handstype_mirroredexcept_radio)

        ####### begin layout for mirrored movement exceptions
        self.mirroredexcept_spacedlayout = QHBoxLayout()
        self.mirroredexcept_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        self.mirroredexcept_layout = QVBoxLayout()
        self.mirroredexcept_layout.addWidget(self.handstype_2hmvmtexceptloc_check)
        self.mirroredexcept_layout.addWidget(self.handstype_2hmvmtexceptshape_check)
        self.mirroredexcept_layout.addWidget(self.handstype_2hmvmtexceptorientn_check)
        self.mirroredexcept_spacedlayout.addLayout(self.mirroredexcept_layout)
        self.simultaneous_layout.addLayout(self.mirroredexcept_spacedlayout)
        self.handstype_mirroredexcept_radio.setChildlayout(self.mirroredexcept_spacedlayout)
        ####### end layout for mirrored movement exceptions

        self.simultaneous_spacedlayout.addLayout(self.simultaneous_layout)
        self.handstype_2hmvmtsimult_radio.setChildlayout(self.simultaneous_layout)
        ###### end layout for simultaneous movement

        self.timing_layout.addLayout(self.simultaneous_spacedlayout)
        self.timing_box = QGroupBox('Movement timing relation')
        self.timing_box.setLayout(self.timing_layout)
        self.similarmvmt_spacedlayout.addWidget(self.timing_box)
        self.movement_2h_layout.addLayout(self.similarmvmt_spacedlayout)
        self.handstype_2hmvmtbothsame_radio.setChildlayout(self.similarmvmt_spacedlayout)
        ##### end layout for 2-handed movement timing relation

        self.movement_2h_spacedlayout.addLayout(self.movement_2h_layout)
        self.movement_layout.addLayout(self.movement_2h_spacedlayout)
        self.handstype_2hmvmtboth_radio.setChildlayout(self.movement_2h_spacedlayout)
        #### end layout for 2-handed movement relation in which both hands move

        self.movement_layout.addWidget(self.handstype_2hmvmtboth_radio)

        self.movement_box = QGroupBox('Movement relation')
        self.movement_box.setLayout(self.movement_layout)
        ### end layout for 2-handed movement relation

        self.twohand_spacedlayout.addLayout(self.twohand_col1_layout)
        self.twohand_spacedlayout.addWidget(self.movement_box)

        self.signtype_layout.addLayout(self.twohand_spacedlayout)

        self.handstype_2h_radio.setChildlayout(self.twohand_spacedlayout)
        ## end layout for 2-handed sign options

        self.signtype_box = QGroupBox('Sign type')
        self.signtype_box.setLayout(self.signtype_layout)
        # end layout for sign type (highest level)

        self.addWidget(self.signtype_box)

        # ensure that Unspecified is selected by default
        # TODO KV keep this? or does loadspecs preclude it?
        # self.handstype_unspec_radio.toggle()

    def setsigntype(self, signtype):
        allbuttons = [btn for btngrp in self.buttongroups for btn in btngrp.buttons()]
        signtypepaths = [btn.property('signtype') for btn in allbuttons]
        for spec in signtype.specslist:
            if spec[0] in signtypepaths:
                btnidx = signtypepaths.index(spec[0])
                allbuttons[btnidx].setChecked(True)

    def getsigntype(self):
        allbuttons = [btn for btngrp in self.buttongroups for btn in btngrp.buttons()]

        # when saving, only use options that are both checked AND enabled!
        specslist = [(btn.property('signtype'),)+btn.property('abbreviation') for btn in allbuttons if btn.isChecked() and btn.isEnabled()]
        signtype = Signtype(specslist)

        return signtype


class Signtype:

    def __init__(self, specslist):
        self._specslist = specslist

    @property
    def specslist(self):
        return self._specslist

    @specslist.setter
    def specslist(self, specslist):
        self._specslist = specslist

    def getabbreviation(self):
        abbreviationtext = ""
        specscopy = [triple for triple in self._specslist]
        toplevelitems = [st_triple for st_triple in specscopy if "." not in st_triple[0]]
        for topleveltriple in toplevelitems:
            specscopy.remove(topleveltriple)
            includeabbrev = [st_triple for st_triple in specscopy if
                             st_triple[0].startswith(topleveltriple[1]) and st_triple[2]]
            signtypeabbreviations = [st[1] for st in includeabbrev]
            abbreviationtext += topleveltriple[1]
            if len(signtypeabbreviations) > 0:
                abbreviationtext += " (" + "; ".join(signtypeabbreviations) + ") "
        return abbreviationtext


# parent can be widget or layout
def enableChildWidgets(yesorno, parent):
    if isinstance(parent, QAbstractButton):
        enableChildWidgets(yesorno, parent.childlayout)
    elif isinstance(parent, QBoxLayout):
        numchildren = parent.count()
        for childnum in range(numchildren):
            thechild = parent.itemAt(childnum)
            if thechild.widget():
                thechild.widget().setEnabled(yesorno)
            elif thechild.layout():
                enableChildWidgets(yesorno, thechild.layout())


class SigntypeButtonGroup(QButtonGroup):

    def __init__(self, prt=None):
        super().__init__(parent=prt)
        self.buttonToggled.connect(self.handleButtonToggled)

    def handleButtonToggled(self, thebutton, checked):
        if checked:
            enableChildWidgets(True, thebutton.childlayout)
            self.disableSiblings(thebutton)

    def disableSiblings(self, thebutton):
        siblings = [b for b in self.buttons() if b != thebutton]
        for b in siblings:
            if b.childlayout:
                enableChildWidgets(False, b.childlayout)


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


class SigntypeCheckBox(QCheckBox):

    def __init__(self, text="", parentbutton=None):
        super().__init__(text)
        self.parentbutton = parentbutton
        self.toggled.connect(self.checkParent)
        self.childlayout = None

    def checkParent(self, checked):
        if checked and self.parentbutton:
            self.parentbutton.setChecked(True)

    def setChildlayout(self, clayout):
        self.childlayout = clayout


class SigntypeSelectorDialog(QDialog):
    saved_signtype = pyqtSignal(Signtype)

    def __init__(self, signtype, mainwindow, **kwargs):  # TODO KV delete  app_settings, app_ctx,
        super().__init__(**kwargs)
        if signtype is not None:
            self.signtype = signtype
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
            self.saved_signtype.emit(self.signtype_layout.getsigntype())
            self.accept()

        elif standard == QDialogButtonBox.RestoreDefaults:
            self.signtype_layout.setsigntype(self.mainwindow.system_default_signtype)
