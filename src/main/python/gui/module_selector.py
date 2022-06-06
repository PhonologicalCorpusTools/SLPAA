from PyQt5.QtWidgets import (
    QFrame,
    QPushButton,
    QRadioButton,
    QDialog,
    QHBoxLayout,
    QVBoxLayout,
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
    QGraphicsEllipseItem
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


class ModuleSelectorDialog(QDialog):
    # saved_movement = pyqtSignal(MovementTreeModel, dict)

    def __init__(self, mainwindow, hands, x_start, x_end, enable_addnew, modulelayout, moduleargs, **kwargs):
        super().__init__(**kwargs)
        self.mainwindow = mainwindow

        main_layout = QVBoxLayout()

        self.hands_layout = HandSelectionLayout(hands)
        main_layout.addLayout(self.hands_layout)
        self.xslot_layout = XslotLinkingLayout(x_start, x_end, self.mainwindow)
        if self.mainwindow.app_settings['signdefaults']['xslot_generation'] != 'none':
            main_layout.addLayout(self.xslot_layout)

        self.module_layout = None
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
        self.button_box.button(QDialogButtonBox.Apply).setText(applytext)

        # TODO KV keep? from orig locationdefinerdialog:
        #      Ref: https://programtalk.com/vs2/python/654/enki/enki/core/workspace.py/
        self.button_box.clicked.connect(self.handle_button_click)

        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)
        self.setMinimumSize(QSize(500, 700))

    def get_savedmodule_signal(self):
        return self.module_layout.get_savedmodule_signal()

    def handle_button_click(self, button):
        standard = self.button_box.standardButton(button)

        if standard == QDialogButtonBox.Cancel:
            # TODO KV - BUG? - if we are editing an already-existing movement module, this seems to save anyway
            self.reject()

        elif standard == QDialogButtonBox.Save:  # save and add another
            # save info and then refresh screen to enter next module
            signalargstuple = (self.module_layout.get_savedmodule_args() + (self.hands_layout.gethands(),))
            self.module_layout.get_savedmodule_signal().emit(*signalargstuple)
            # self.saved_movement.emit(self.movement_layout.treemodel, self.hands_layout.gethands())
            # self.movement_layout.clearlist(None)  # TODO KV should this use "restore defaults" instead?
            self.hands_layout.clear()
            # self.movement_layout.refresh_treemodel()
            self.module_layout.refresh()

        elif standard == QDialogButtonBox.Apply:  # save and close
            # save info and then close dialog
            # self.saved_movement.emit(self.movement_layout.treemodel, self.hands_layout.gethands())
            signalargstuple = (self.module_layout.get_savedmodule_args()+(self.hands_layout.gethands(),))
            self.module_layout.get_savedmodule_signal().emit(*signalargstuple)
            self.accept()

        elif standard == QDialogButtonBox.RestoreDefaults:  # restore defaults
            # TODO KV -- where should the "defaults" be defined?
            # self.movement_layout.clearlist(button)
            self.module_layout.clear()
            self.hands_layout.clear()


class HandSelectionLayout(QHBoxLayout):

    def __init__(self, hands=None, **kwargs):
        super().__init__(**kwargs)

        self.hand1_checkbox = QCheckBox("Hand 1")
        self.hand2_checkbox = QCheckBox("Hand 2")
        self.addWidget(self.hand1_checkbox)
        self.addWidget(self.hand2_checkbox)
        self.addStretch()

        if hands is not None:
            self.sethands(hands)

    def gethands(self):
        return {
            'H1': self.hand1_checkbox.isChecked(),
            'H2': self.hand2_checkbox.isChecked()
        }

    def sethands(self, hands_dict):
        self.hand1_checkbox.setChecked(hands_dict['H1'])
        self.hand2_checkbox.setChecked(hands_dict['H2'])

    def clear(self):
        self.sethands(
            {
                'H1': False,
                'H2': False
            }
        )
