from fractions import Fraction
from PyQt5.QtWidgets import (
    QFrame,
    QDialog,
    QHBoxLayout,
    QVBoxLayout,
    QDialogButtonBox,
    QLabel,
    QButtonGroup,
    QRadioButton,
    QSpacerItem,
    QSizePolicy,
    QSpinBox,
    QMessageBox
)

from PyQt5.QtCore import (
    pyqtSignal,
)

from lexicon.module_classes import XslotStructure


class XslotSpecificationPanel(QFrame):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mainwindow = self.parent().mainwindow

        main_layout = QVBoxLayout()

        self.xslots_layout = QHBoxLayout()
        self.xslots_label = QLabel("How many x-slots would you like?")
        self.xslots_spin = QSpinBox()
        self.xslots_layout.addWidget(self.xslots_label)
        self.xslots_layout.addWidget(self.xslots_spin)
        main_layout.addLayout(self.xslots_layout)

        self.partial_layout = QVBoxLayout()
        self.partial_label = QLabel("Add a partial x-slot if necessary:")
        self.partial_layout.addWidget(self.partial_label)

        self.fraction_layout = QVBoxLayout()
        partialxslots = self.mainwindow.app_settings['signdefaults']['partial_xslots']
        self.avail_denoms = [Fraction(f).denominator for f in list(partialxslots.keys()) if partialxslots[f]]
        self.fractionalpoints = []
        for d in self.avail_denoms:
            for mult in range(1, d):
                self.fractionalpoints.append(Fraction(mult, d))
        self.fractionalpoints = list(set(self.fractionalpoints))
        self.partial_buttongroup = QButtonGroup()
        none_radio = QRadioButton("none")
        none_radio.setProperty('fraction', Fraction(0))
        self.partial_buttongroup.addButton(none_radio)
        none_radio.setChecked(True)
        self.fraction_layout.addWidget(none_radio)
        for fraction in sorted(self.fractionalpoints):
            partial_radio = QRadioButton(str(fraction))
            partial_radio.setProperty('fraction', fraction)
            self.partial_buttongroup.addButton(partial_radio)
            self.fraction_layout.addWidget(partial_radio)
        if len(self.avail_denoms) == 0:
            self.nopartials_label = QLabel("You do not have any fractional x-slot points selected in Global Settings.")
            self.fraction_layout.addWidget(self.nopartials_label)

        self.fraction_spacedlayout = QHBoxLayout()
        self.fraction_spacedlayout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        self.fraction_spacedlayout.addLayout(self.fraction_layout)
        self.partial_layout.addLayout(self.fraction_spacedlayout)

        main_layout.addLayout(self.partial_layout)

        self.setLayout(main_layout)

    def setxslots(self, xslots):
        self.xslots_spin.setValue(xslots.number)
        for cb in self.partial_buttongroup.buttons():
            cb.setChecked(cb.property('fraction') == xslots.additionalfraction)

    def getxslots(self):
        thebutton = self.partial_buttongroup.checkedButton()
        fractionalpoints = [Fraction(f) for f in self.fractionalpoints]
        return XslotStructure(number=self.xslots_spin.value(), fractionalpoints=fractionalpoints, additionalfraction=thebutton.property('fraction'))


class XslotSelectorDialog(QDialog):
    saved_xslots = pyqtSignal(XslotStructure)

    def __init__(self, xslotstruct, **kwargs):
        super().__init__(**kwargs)
        self.mainwindow = self.parent().mainwindow

        if xslotstruct is not None:
            self.xslotstruct = xslotstruct
        else:
            self.xslotstruct = XslotStructure()

        self.xslot_widget = XslotSpecificationPanel(parent=self)
        self.xslot_widget.setxslots(self.xslotstruct)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.xslot_widget)

        separate_line = QFrame()
        separate_line.setFrameShape(QFrame.HLine)
        separate_line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separate_line)

        buttons = QDialogButtonBox.RestoreDefaults | QDialogButtonBox.Save | QDialogButtonBox.Cancel

        self.button_box = QDialogButtonBox(buttons, parent=self)
        self.button_box.button(QDialogButtonBox.RestoreDefaults).setText("Clear")
        self.button_box.button(QDialogButtonBox.RestoreDefaults).setAutoDefault(False)
        self.button_box.button(QDialogButtonBox.Cancel).setAutoDefault(False)
        self.button_box.button(QDialogButtonBox.Save).setAutoDefault(True)

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

        elif standard == QDialogButtonBox.Save:
            self.validate_and_save()
            
        elif standard == QDialogButtonBox.RestoreDefaults:
            self.xslot_widget.setxslots(XslotStructure())

    def validate_and_save(self):
        messagestring = ""
        newxslotstructure = self.xslot_widget.getxslots()
        if newxslotstructure.number == 0 and newxslotstructure.additionalfraction == 0:
            messagestring = "Number of xslots cannot be zero. If you want to turn off xslots, go to Settings -> Preferences -> Sign."
        if messagestring != "":
            QMessageBox.critical(self, "Warning", messagestring)

        else:
            # save info and then close dialog
            self.saved_xslots.emit(newxslotstructure)
            if self.mainwindow.current_sign is not None and newxslotstructure != self.xslotstruct:
                self.mainwindow.current_sign.lastmodifiednow()
            self.accept()
