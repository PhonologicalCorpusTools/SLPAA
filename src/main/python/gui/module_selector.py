from copy import deepcopy

from PyQt5.QtWidgets import (
    QFrame,
    QRadioButton,
    QDialog,
    QWidget,
    QAction,
    QWidgetAction,
    QSpacerItem,
    QSizePolicy,
    QLineEdit,
    QHBoxLayout,
    QVBoxLayout,
    QMessageBox,
    # QGraphicsRectItem,
    # QGridLayout,
    QDialogButtonBox,
    QMenu,
    QLabel,
    # QCompleter,
    QButtonGroup,
    # QAbstractItemView,
    # QStyledItemDelegate,
    # QStyle,
    # QStyleOptionButton,
    # QApplication,
    # QHeaderView,
    # QStyleOptionFrame,
    # QErrorMessage,
    QCheckBox,
    QPushButton,
    # QSpinBox,
    # QGraphicsView,
    # QGraphicsScene,
    # QGraphicsEllipseItem,
    # QSizePolicy
)

from PyQt5.QtCore import (
    Qt,
    # QSize,
    # QEvent,
    pyqtSignal
)

# from PyQt5.QtGui import (
#     QPixmap,
#     QColor,
#     QPen,
#     QBrush,
#     QPolygonF,
#     QTextOption,
#     QFont
# )

from gui.xslot_graphics import XslotLinkingLayout
# from lexicon.module_classes import TimingInterval, TimingPoint
from lexicon.module_classes2 import AddedInfo, TimingInterval, TimingPoint


# class ModuleSpecificationPanel(TODO KV):

# base class for various module specification layouts to inherit from
class ModuleSpecificationLayout(QVBoxLayout):

    def get_savedmodule_args(self):
        pass

    def get_savedmodule_signal(self):
        pass

    def get_deletedmodule_signal(self):
        pass

    def refresh(self):
        pass

    def clear(self):
        pass

    def desiredwidth(self):
        pass

    def desiredheight(self):
        pass


class AddedInfoPushButton(QPushButton):

    def __init__(self, title, **kwargs):
        super().__init__(title, **kwargs)
        self._addedinfo = AddedInfo()

        # styling
        qss = """   
            QPushButton[AddedInfo=true] {
                font: bold;
                /*border: 2px dashed black;*/
            }
    
            QPushButton[AddedInfo=false] {
                font: normal;
                /*border: 1px solid grey;*/
            }
        """
        self.setStyleSheet(qss)

        # self._addedinfo = AddedInfo()
        self.updateStyle()

    @property
    def addedinfo(self):
        return self._addedinfo

    @addedinfo.setter
    def addedinfo(self, addedinfo):
        self._addedinfo = addedinfo if addedinfo is not None else AddedInfo()
        self.updateStyle()

    def mouseReleaseEvent(self, event):
    # def contextMenuEvent(self, event):
        addedinfo_menu = AddedInfoContextMenu(self._addedinfo)
        addedinfo_menu.info_added.connect(self.updateStyle)
        addedinfo_menu.exec_(event.globalPos())

    def updateStyle(self, addedinfo=None):
        if addedinfo is not None:
            self._addedinfo = addedinfo
        self.setProperty('AddedInfo', self._addedinfo.hascontent())
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def clear(self):
        self._addedinfo = AddedInfo()


class ModuleSelectorDialog(QDialog):

    def __init__(self, mainwindow, hands, xslotstructure, new_instance, modulelayout, moduleargs, timingintervals=None, addedinfo=None, includephase=0, inphase=0, **kwargs):
        super().__init__(**kwargs)
        self.mainwindow = mainwindow
        if timingintervals is None:
            timingintervals = []
        else:
            timingintervals = deepcopy(timingintervals)
        if addedinfo is None:
            addedinfo = AddedInfo()

        main_layout = QVBoxLayout()

        self.hands_and_addedinfo_layout = QHBoxLayout()

        self.hands_layout = HandSelectionLayout(hands, includephase=includephase, inphase=inphase)
        # main_layout.addLayout(self.hands_layout)
        self.hands_and_addedinfo_layout.addLayout(self.hands_layout)
        self.hands_and_addedinfo_layout.addStretch()
        self.addedinfobutton = AddedInfoPushButton("Module notes")
        self.addedinfobutton.addedinfo = deepcopy(addedinfo)
        self.hands_and_addedinfo_layout.addWidget(self.addedinfobutton)
        self.hands_and_addedinfo_layout.setAlignment(self.addedinfobutton, Qt.AlignTop)

        main_layout.addLayout(self.hands_and_addedinfo_layout)

        # self.xslot_layout = XslotLinkingLayout(x_start, x_end, self.mainwindow)
        self.xslot_layout = XslotLinkingLayout(xslotstructure, self.mainwindow, parentwidget=self, timingintervals=timingintervals)
        if self.mainwindow.app_settings['signdefaults']['xslot_generation'] != 'none':
            main_layout.addLayout(self.xslot_layout)

        self.module_layout = modulelayout
        main_layout.addLayout(self.module_layout)

        separate_line = QFrame()
        separate_line.setFrameShape(QFrame.HLine)
        separate_line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separate_line)

        # If we're creating a brand new instance of a module, then we want a
        #   "Save and Add Another" button, to allow the user to continue adding new instances.
        # On the other hand, if we're editing an existing instance of a module, then instead we want a
        #   "Delete" button, in case the user wants to the delete the instance rather than editing it.
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
        ## self.setMinimumSize(modulelayout.desiredwidth(), modulelayout.desiredheight())
        # self.setMinimumSize(QSize(modulelayout.rect().width(), modulelayout.rect().height()))
        # self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.adjustSize()

    def get_savedmodule_signal(self):
        return self.module_layout.get_savedmodule_signal()

    def get_deletedmodule_signal(self):
        return self.module_layout.get_deletedmodule_signal()

    def handle_button_click(self, button):
        standard = self.button_box.standardButton(button)

        if standard == QDialogButtonBox.Cancel:
            self.reject()

        elif standard == QDialogButtonBox.Discard:
            self.module_layout.get_deletedmodule_signal().emit()
            self.accept()  # TODO KV ???

        # TODO KV this duplicates the code in the next conditional case
        elif standard == QDialogButtonBox.Save:  # save and add another

            # validate hand selection
            handsdict = self.hands_layout.gethands()
            handsvalid = True
            if True not in handsdict.values():
                handsvalid = False

            inphase = self.hands_layout.getphase()
            addedinfo = self.addedinfobutton.addedinfo

            # validate timing interval(s) selection
            timingintervals = self.xslot_layout.gettimingintervals()
            timingvalid = True
            if len(timingintervals) == 0 and self.mainwindow.app_settings['signdefaults']['xslot_generation'] != 'none':
                timingvalid = False
            elif self.mainwindow.app_settings['signdefaults']['xslot_generation'] == 'none':
                # no x-slots; make the timing interval be for the whole sign
                timingintervals = [TimingInterval(TimingPoint(0,0), TimingPoint(1,0))]

            if not (handsvalid and timingvalid):
                # refuse to save without hand & timing info
                messagestring = "Missing"
                messagestring += " hand selection" if not handsvalid else ""
                messagestring += " and" if not (handsvalid or timingvalid) else ""
                messagestring += " timing selection" if not timingvalid else ""
                messagestring += "."
                QMessageBox.critical(self, "Warning", messagestring)
            else:
                # save info and then refresh screen to enter next module
                signalargstuple = (self.module_layout.get_savedmodule_args() + (handsdict, timingintervals, addedinfo, inphase))
                self.module_layout.get_savedmodule_signal().emit(*signalargstuple)
                # if self.mainwindow.current_sign is not None:
                #     self.mainwindow.current_sign.lastmodifiednow()
                self.hands_layout.clear()
                self.addedinfobutton.clear()
                self.xslot_layout.clear()
                self.module_layout.clear()  # TODO KV was refresh()....

        elif standard == QDialogButtonBox.Apply:  # save and close

            # validate hand selection
            handsdict = self.hands_layout.gethands()
            handsvalid = True
            if True not in handsdict.values():
                handsvalid = False

            inphase = self.hands_layout.getphase()
            addedinfo = self.addedinfobutton.addedinfo

            # validate timing interval(s) selection
            timingintervals = self.xslot_layout.gettimingintervals()
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
                signalargstuple = (self.module_layout.get_savedmodule_args() + (handsdict, timingintervals, addedinfo, inphase))
                self.module_layout.get_savedmodule_signal().emit(*signalargstuple)
                # if self.mainwindow.current_sign is not None:
                #     self.mainwindow.current_sign.lastmodifiednow()
                self.accept()

        elif standard == QDialogButtonBox.RestoreDefaults:  # restore defaults
            # TODO KV -- where should the "defaults" be defined?
            # self.movement_layout.clearlist(button)
            self.hands_layout.clear()
            self.xslot_layout.clear()
            self.module_layout.clear()


class AbstractLocationAction(QWidgetAction):
    textChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.actionwidget = QWidget()
        self.actionlayout = QHBoxLayout()


class NoteAction(AbstractLocationAction):

    def __init__(self, label=None, parent=None):
        super().__init__(parent)

        self.label = label
        self.actionlayout.addWidget(QLabel(self.label))
        self.note = QLineEdit()
        self.actionlayout.addWidget(self.note)
        self.actionwidget.setLayout(self.actionlayout)
        self.setDefaultWidget(self.actionwidget)

    def setText(self, text):
        self.note.setText(text)

    def text(self):
        return self.note.text()


class CheckNoteAction(AbstractLocationAction):  # QWidgetAction):
    # textChanged = pyqtSignal(str)

    def __init__(self, label, parent=None):
        super().__init__(parent)

        self.label = label
        self.checkbox = QCheckBox(self.label)
        self.checkbox.setTristate(False)
        self.checkbox.toggled.connect(self.toggled)
        self.note = QLineEdit()
        self.note.textChanged.connect(self.textChanged.emit)
        self.actionlayout.addWidget(self.checkbox)
        self.actionlayout.addWidget(self.note)
        self.actionwidget.setLayout(self.actionlayout)
        self.setDefaultWidget(self.actionwidget)

    def setChecked(self, state):
        self.checkbox.setChecked(state)

    def isChecked(self):
        return self.checkbox.isChecked()

    def setText(self, text):
        self.note.setText(text)

    def text(self):
        return self.note.text()


class AddedInfoContextMenu(QMenu):
    info_added = pyqtSignal(AddedInfo)

    def __init__(self, addedinfo):
        super().__init__()

        self.addedinfo = addedinfo

        self.uncertain_action = CheckNoteAction("Uncertain")
        self.uncertain_action.setChecked(self.addedinfo.uncertain_flag)
        self.uncertain_action.setText(self.addedinfo.uncertain_note)
        self.uncertain_action.toggled.connect(lambda state: self.checknoteaction_toggled(state, self.uncertain_action))
        self.addAction(self.uncertain_action)

        self.estimated_action = CheckNoteAction("Estimated")
        self.estimated_action.setChecked(self.addedinfo.estimated_flag)
        self.estimated_action.setText(self.addedinfo.estimated_note)
        self.estimated_action.toggled.connect(lambda state: self.checknoteaction_toggled(state, self.estimated_action))
        self.addAction(self.estimated_action)

        self.notspecified_action = CheckNoteAction("Not specified")
        self.notspecified_action.setChecked(self.addedinfo.notspecified_flag)
        self.notspecified_action.setText(self.addedinfo.notspecified_note)
        self.notspecified_action.toggled.connect(lambda state: self.checknoteaction_toggled(state, self.notspecified_action))
        self.addAction(self.notspecified_action)

        self.variable_action = CheckNoteAction("Variable")
        self.variable_action.setChecked(self.addedinfo.variable_flag)
        self.variable_action.setText(self.addedinfo.variable_note)
        self.variable_action.toggled.connect(lambda state: self.checknoteaction_toggled(state, self.variable_action))
        self.addAction(self.variable_action)

        self.exceptional_action = CheckNoteAction("Exceptional")
        self.exceptional_action.setChecked(self.addedinfo.exceptional_flag)
        self.exceptional_action.setText(self.addedinfo.exceptional_note)
        self.exceptional_action.toggled.connect(lambda state: self.checknoteaction_toggled(state, self.exceptional_action))
        self.addAction(self.exceptional_action)

        self.incomplete_action = CheckNoteAction("Incomplete")
        self.incomplete_action.setChecked(self.addedinfo.incomplete_flag)
        self.incomplete_action.setText(self.addedinfo.incomplete_note)
        self.incomplete_action.toggled.connect(lambda state: self.checknoteaction_toggled(state, self.incomplete_action))
        self.addAction(self.incomplete_action)

        self.other_action = CheckNoteAction("Other")
        self.other_action.setChecked(self.addedinfo.other_flag)
        self.other_action.setText(self.addedinfo.other_note)
        self.other_action.toggled.connect(lambda state: self.checknoteaction_toggled(state, self.other_action))
        self.addAction(self.other_action)

        self.addSeparator()

        self.close_action = QAction("Close menu")
        self.addAction(self.close_action)

        self.aboutToHide.connect(self.savemenunotes)

    def checknoteaction_toggled(self, state, whichaction):

        if whichaction == self.uncertain_action:
            self.addedinfo.uncertain_flag = state
        elif whichaction == self.estimated_action:
            self.addedinfo.estimated_flag = state
        elif whichaction == self.notspecified_action:
            self.addedinfo.notspecified_flag = state
        elif whichaction == self.variable_action:
            self.addedinfo.variable_flag = state
        elif whichaction == self.exceptional_action:
            self.addedinfo.exceptional_flag = state
        elif whichaction == self.incomplete_action:
            self.addedinfo.incomplete_flag = state
        elif whichaction == self.other_action:
            self.addedinfo.other_flag = state

    def focusOutEvent(self, event):
        self.savemenunotes()

    def savemenunotes(self):
        self.addedinfo.uncertain_note = self.uncertain_action.text()
        self.addedinfo.estimated_note = self.estimated_action.text()
        self.addedinfo.notspecified_note = self.notspecified_action.text()
        self.addedinfo.variable_note = self.variable_action.text()
        self.addedinfo.exceptional_note = self.exceptional_action.text()
        self.addedinfo.incomplete_note = self.incomplete_action.text()
        self.addedinfo.other_note = self.other_action.text()

        self.info_added.emit(self.addedinfo)


# TODO KV - need to pull phase info from here as well as hands info
class HandSelectionLayout(QHBoxLayout):

    def __init__(self, hands=None, includephase=0, inphase=0, **kwargs):
        super().__init__(**kwargs)

        self.setSpacing(25)

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
        self.bothoutofphaseNEW_radio = QRadioButton("Out of phase")
        self.bothhands_group.addButton(self.bothconnected_cb)
        self.bothhands_group.addButton(self.bothinphase_cb)
        self.bothhands_group.addButton(self.bothoutofphaseNEW_radio)

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
                bothhands_sub_layout.addWidget(self.bothoutofphaseNEW_radio)
            bothhands_sub_spacedlayout.addLayout(bothhands_sub_layout)
            bothhands_layout.addLayout(bothhands_sub_spacedlayout)

            main_layout.addLayout(bothhands_layout)

        self.addLayout(main_layout)
        self.addStretch()

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
            elif self.bothoutofphaseNEW_radio.isChecked():
                return 2
            else:
                return 0
        elif self.bothconnected_cb.isChecked():
            # these are mutually exclusive
            if self.bothinphase_cb.isChecked():
                return 4
            elif self.bothoutofphaseNEW_radio.isChecked():
                # it shouldn't be possible to have both "connected" and "out of phase" checked, but... just in case?
                return 5
            else:
                return 3


    def setphase(self, inphase):
        self.bothconnected_cb.setChecked((inphase >= 3))

        if inphase % 3 == 1:
            self.bothinphase_cb.setChecked(True)
        elif inphase % 3 == 2:
            self.bothoutofphaseNEW_radio.setChecked(True)

    def clear(self):
        self.hands_group.setExclusive(False)
        for b in self.hands_group.buttons() + self.bothhands_group.buttons():
            b.setChecked(False)
        self.hands_group.setExclusive(True)
