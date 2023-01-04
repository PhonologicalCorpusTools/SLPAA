from copy import deepcopy

from PyQt5.QtWidgets import (
    QFrame,
    QPushButton,
    QRadioButton,
    QDialog,
    QWidget,
    QAction,
    QWidgetAction,
    QLineEdit,
    QHBoxLayout,
    QVBoxLayout,
    QMessageBox,
    QGraphicsRectItem,
    QGridLayout,
    QDialogButtonBox,
    QComboBox,
    QMenu,
    QLabel,
    QCompleter,
    QButtonGroup,
    QAbstractItemView,
    QStyledItemDelegate,
    QStyle,
    QStyleOptionButton,
    QApplication,
    QHeaderView,
    QStyleOptionFrame,
    QErrorMessage,
    QCheckBox,
    QSpinBox,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsEllipseItem,
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

from gui.xslot_graphics import XslotLinkingLayout


# class ModuleSpecificationPanel(TODO KV):

# base class for various module specification layouts to inherit from
class ModuleSpecificationLayout(QVBoxLayout):

    def get_savedmodule_args(self):
        pass

    def get_savedmodule_signal(self):
        pass

    def refresh(self):
        pass

    def clear(self):
        pass

    def desiredwidth(self):
        pass

    def desiredheight(self):
        pass


class ModuleSelectorDialog(QDialog):

    def __init__(self, mainwindow, hands, xslotstructure, enable_addnew, modulelayout, moduleargs, timingintervals=None, includephase=False, inphase=0, **kwargs):
        super().__init__(**kwargs)
        self.mainwindow = mainwindow
        if timingintervals is None:
            timingintervals = []
        else:
            timingintervals = deepcopy(timingintervals)

        main_layout = QVBoxLayout()

        self.hands_layout = HandSelectionLayout(hands, includephase=includephase, inphase=inphase)
        main_layout.addLayout(self.hands_layout)
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

        buttons = None
        applytext = ""
        if enable_addnew:
            buttons = QDialogButtonBox.RestoreDefaults | QDialogButtonBox.Save | QDialogButtonBox.Apply | QDialogButtonBox.Cancel
            applytext = "Save and close"
        else:
            buttons = QDialogButtonBox.RestoreDefaults | QDialogButtonBox.Apply | QDialogButtonBox.Cancel
            applytext = "Save"

        self.button_box = QDialogButtonBox(buttons, parent=self)
        if enable_addnew:
            self.button_box.button(QDialogButtonBox.Save).setText("Save and add another")
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

    def handle_button_click(self, button):
        standard = self.button_box.standardButton(button)

        if standard == QDialogButtonBox.Cancel:
            # TODO KV - BUG issue #44 - if we are editing an already-existing movement module, this seems to save anyway
            self.reject()

        # TODO KV this duplicates the code in the next conditional case
        elif standard == QDialogButtonBox.Save:  # save and add another

            # validate hand selection
            handsdict = self.hands_layout.gethands()
            handsvalid = True
            if True not in handsdict.values():
                handsvalid = False

            inphase = self.hands_layout.getphase()

            # validate timing interval(s) selection
            timingintervals = self.xslot_layout.gettimingintervals()
            timingvalid = True
            if len(timingintervals) == 0:
                timingvalid = False

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
                signalargstuple = (self.module_layout.get_savedmodule_args() + (handsdict, timingintervals, inphase))
                self.module_layout.get_savedmodule_signal().emit(*signalargstuple)
                # if self.mainwindow.current_sign is not None:
                #     self.mainwindow.current_sign.lastmodifiednow()
                # self.saved_movement.emit(self.movement_layout.treemodel, self.hands_layout.gethands())
                # self.movement_layout.clearlist(None)  # TODO KV should this use "restore defaults" instead?
                self.hands_layout.clear()
                self.xslot_layout.clear()
                self.module_layout.refresh()

        elif standard == QDialogButtonBox.Apply:  # save and close

            # validate hand selection
            handsdict = self.hands_layout.gethands()
            handsvalid = True
            if True not in handsdict.values():
                handsvalid = False

            inphase = self.hands_layout.getphase()

            # validate timing interval(s) selection
            timingintervals = self.xslot_layout.gettimingintervals()
            timingvalid = True
            if len(timingintervals) == 0:
                timingvalid = False

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
                # self.saved_movement.emit(self.movement_layout.treemodel, self.hands_layout.gethands())
                signalargstuple = (self.module_layout.get_savedmodule_args() + (handsdict, timingintervals, inphase))
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
        elif whichaction == self.other_action:
            self.addedinfo.other_flag = state

    def savemenunotes(self):

        self.addedinfo.uncertain_note = self.uncertain_action.text()
        self.addedinfo.estimated_note = self.estimated_action.text()
        self.addedinfo.notspecified_note = self.notspecified_action.text()
        self.addedinfo.variable_note = self.variable_action.text()
        self.addedinfo.exceptional_note = self.exceptional_action.text()
        self.addedinfo.other_note = self.other_action.text()


# TODO KV - need to pull phase info from here as well as hands info
class HandSelectionLayout(QHBoxLayout):

    def __init__(self, hands=None, includephase=False, inphase=0, **kwargs):
        super().__init__(**kwargs)

        self.setSpacing(25)

        self.includephase = includephase

        self.hands_label = QLabel("This module applies to:")
        self.hands_group = QButtonGroup()
        self.hand1_radio = QRadioButton("Hand 1")
        self.hand2_radio = QRadioButton("Hand 2")
        self.addWidget(self.hands_label)
        self.addWidget(self.hand1_radio)
        self.addWidget(self.hand2_radio)

        self.bothhands_radio = QRadioButton("Both hands")
        self.bothinphase_radio = QRadioButton("Both hands (in phase)")
        self.bothoutofphase_radio = QRadioButton("Both hands (out of phase)")
        self.hands_group.addButton(self.hand1_radio)
        self.hands_group.addButton(self.hand2_radio)
        if self.includephase:
            self.hands_group.addButton(self.bothinphase_radio)
            self.hands_group.addButton(self.bothoutofphase_radio)
            self.addWidget(self.bothinphase_radio)
            self.addWidget(self.bothoutofphase_radio)
        else:
            self.hands_group.addButton(self.bothhands_radio)
            self.addWidget(self.bothhands_radio)

        self.addStretch()

        if hands is not None:
            self.sethands(hands)
        self.setphase(inphase)

    def gethands(self):
        both = self.bothhands_radio.isChecked() or self.bothinphase_radio.isChecked() or self.bothoutofphase_radio.isChecked()
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
        if self.bothinphase_radio.isChecked():
            return 1
        elif self.bothoutofphase_radio.isChecked():
            return 2
        else:
            return 0

    def setphase(self, inphase):
        if inphase == 1:
            self.bothinphase_radio.setChecked(True)
        elif inphase == 2:
            self.bothoutofphase_radio.setChecked(True)

    def clear(self):
        self.hands_group.setExclusive(False)
        for b in self.hands_group.buttons():
            b.setChecked(False)
        self.hands_group.setExclusive(True)
