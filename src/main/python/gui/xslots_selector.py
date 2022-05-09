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
    QAbstractButton,
    QSpinBox
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


class XslotsSpecificationLayout(QVBoxLayout):
    def __init__(self, mainwindow, **kwargs):  # TODO KV delete  app_ctx,
        super().__init__(**kwargs)
        self.mainwindow = mainwindow

        self.xslots_layout = QHBoxLayout()
        self.xslots_label = QLabel("How many x-slots would you like?")
        self.xslots_spin = QSpinBox()
        self.xslots_layout.addWidget(self.xslots_label)
        self.xslots_layout.addWidget(self.xslots_spin)
        self.addLayout(self.xslots_layout)

        self.partial_layout = QVBoxLayout()
        self.partial_label = QLabel("Add a partial x-slot if necessary:")
        self.partial_layout.addWidget(self.partial_label)

        self.fraction_layout = QVBoxLayout()
        avail_fracs = [f for f in list(mainwindow.partial_defaults.keys()) if self.mainwindow.app_settings['signdefaults']['partial_slots'][f]]
        if len(avail_fracs) > 0:
            self.partial_buttongroup = QButtonGroup()
            for fraction in avail_fracs:
                partial_checkbox = QCheckBox(fraction)
                self.partial_buttongroup.addButton(partial_checkbox)
                self.fraction_layout.addWidget(partial_checkbox)
        else:
            self.nopartials_label = QLabel("You do not have any fractional x-slot points selected in Global Settings.")
            self.fraction_layout.addWidget(self.nopartials_label)

        self.fraction_spacedlayout = QHBoxLayout()
        self.fraction_spacedlayout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        self.fraction_spacedlayout.addLayout(self.fraction_layout)
        self.partial_layout.addLayout(self.fraction_spacedlayout)

        self.addLayout(self.partial_layout)

        # ensure that none are selected by default
        # TODO KV

    def setxslots(self, xslots):
        self.xslots_spin.setValue(xslots.number)
        for cb in self.partial_buttongroup.buttons():
            cb.setChecked(cb.text() in xslots.partials)

    def getxslots(self):
        partialslist = []
        for cb in self.partial_buttongroup.buttons():
            if cb.isChecked():
                partialslist.append(cb.text())
        return XslotStructure(self.xslots_spin.value(), partialslist)


class XslotStructure:

    def __init__(self, number=0, partialslist=[]):
        self._number = number
        self._partials = partialslist

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, number):
        self._number = number

    @property
    def partials(self):
        return self._partials

    @partials.setter
    def partials(self, partialslist):
        self._partials = partialslist


class XslotSelectorDialog(QDialog):
    saved_xslots = pyqtSignal(XslotStructure)

    def __init__(self, xslotstruct, mainwindow, **kwargs):  # TODO KV delete  app_settings, app_ctx,
        super().__init__(**kwargs)
        if xslotstruct is not None:
            self.xslotstruct = xslotstruct
        else:
            self.xslotstruct = XslotStructure()

        # TODO KV delete self.app_settings = app_settings
        self.mainwindow = mainwindow
        
        self.xslot_layout = XslotsSpecificationLayout(mainwindow=mainwindow)  # TODO KV delete app_ctx)
        self.xslot_layout.setxslots(self.xslotstruct)

        main_layout = QVBoxLayout()
        main_layout.addLayout(self.xslot_layout)

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
            self.saved_xslots.emit(self.xslot_layout.getxslots())
            self.accept()

        # TODO KV should this be "clear" isntead?
        elif standard == QDialogButtonBox.RestoreDefaults:
            self.xslot_layout.setxslots(XslotStructure())
