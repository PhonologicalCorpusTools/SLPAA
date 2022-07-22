from PyQt5.QtWidgets import (
    QFrame,
    QPushButton,
    QRadioButton,
    QDialog,
    QHBoxLayout,
    QVBoxLayout,
    QMessageBox,
    QGraphicsRectItem,
    QGridLayout,
    QDialogButtonBox,
    QComboBox,
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

    def __init__(self, mainwindow, hands, xslotstructure, enable_addnew, modulelayout, moduleargs, timingintervals=None, **kwargs):
        super().__init__(**kwargs)
        self.mainwindow = mainwindow
        if timingintervals is None:
            timingintervals = []

        main_layout = QVBoxLayout()

        self.hands_layout = HandSelectionLayout(hands)
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
            # TODO KV - BUG? - if we are editing an already-existing movement module, this seems to save anyway
            self.reject()

        elif standard == QDialogButtonBox.Save:  # save and add another

            # validate hand selection
            handsdict = self.hands_layout.gethands()
            handsvalid = True
            if True not in handsdict.values():
                handsvalid = False

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
                signalargstuple = (self.module_layout.get_savedmodule_args() + (handsdict, timingintervals))
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
                signalargstuple = (self.module_layout.get_savedmodule_args() + (handsdict, timingintervals))
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


class HandSelectionLayout(QHBoxLayout):

    def __init__(self, hands=None, **kwargs):
        super().__init__(**kwargs)

        self.setSpacing(25)

        self.hands_label = QLabel("This module applies to:")
        self.hands_group = QButtonGroup()
        self.hand1_radio = QRadioButton("Hand 1")
        self.hand2_radio = QRadioButton("Hand 2")
        self.bothhands_radio = QRadioButton("Both hands")
        self.hands_group.addButton(self.hand1_radio)
        self.hands_group.addButton(self.hand2_radio)
        self.hands_group.addButton(self.bothhands_radio)
        self.addWidget(self.hands_label)
        self.addWidget(self.hand1_radio)
        self.addWidget(self.hand2_radio)
        self.addWidget(self.bothhands_radio)

        self.addStretch()

        if hands is not None:
            self.sethands(hands)

    def gethands(self):
        return {
            'H1': self.hand1_radio.isChecked() or self.bothhands_radio.isChecked(),
            'H2': self.hand2_radio.isChecked() or self.bothhands_radio.isChecked()
        }

    def sethands(self, hands_dict):
        if hands_dict['H1'] and hands_dict['H2']:
            self.bothhands_radio.setChecked(True)
        elif hands_dict['H1']:
            self.hand1_radio.setChecked(True)
        elif hands_dict['H2']:
            self.hand2_radio.setChecked(True)

    def clear(self):
        self.hands_group.setExclusive(False)
        for b in self.hands_group.buttons():
            b.setChecked(False)
        self.hands_group.setExclusive(True)
