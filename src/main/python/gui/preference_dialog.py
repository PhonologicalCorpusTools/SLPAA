from PyQt5.QtWidgets import (
    QDialog,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QTabWidget,
    QSpinBox,
    QCheckBox,
    QDialogButtonBox,
    QLineEdit,
    QLabel,
    QRadioButton,
    QButtonGroup,
    QMessageBox,
    QPushButton
)

from PyQt5.QtCore import pyqtSignal

from constant import FRACTION_CHAR
from fractions import Fraction


class DisplayTab(QWidget):
    def __init__(self, settings, **kwargs):
        super().__init__(**kwargs)

        self.settings = settings

        main_layout = QFormLayout()
        self.setLayout(main_layout)

        self.decimal_place = QSpinBox(parent=self)
        self.decimal_place.setMinimum(0)
        self.decimal_place.setMaximum(10)
        self.decimal_place.setValue(settings['display']['sig_figs'])
        main_layout.addRow(QLabel("Number of displayed decimal places:"), self.decimal_place)

        self.coder_name = QLineEdit(settings['metadata']['coder'], parent=self)
        main_layout.addRow(QLabel("Preferred coder name:"), self.coder_name)

        self.show_tooltip = QCheckBox(parent=self)
        self.show_tooltip.setChecked(settings['display']['tooltips'])
        main_layout.addRow(QLabel("Show tooltip:"), self.show_tooltip)

        self.entryid_digits = QSpinBox(parent=self)
        self.entryid_digits.setMinimum(1)
        self.entryid_digits.setValue(settings['display']['entryid_digits'])
        main_layout.addRow(QLabel("Number of displayed entry ID digits:"), self.entryid_digits)

    def save_settings(self):
        self.settings['display']['sig_figs'] = int(self.decimal_place.value())
        self.settings['display']['tooltips'] = self.show_tooltip.isChecked()
        self.settings['metadata']['coder'] = str(self.coder_name.text())
        self.settings['display']['entryid_digits'] = self.entryid_digits.value()


class ReminderTab(QWidget):
    def __init__(self, settings, **kwargs):
        super().__init__(**kwargs)
        self.settings = settings

        main_layout = QFormLayout()
        self.setLayout(main_layout)

        self.overwrite_reminder = QCheckBox(parent=self)
        self.overwrite_reminder.setChecked(settings['reminder']['overwrite'])
        main_layout.addRow(QLabel('Always ask before overwriting a sign:'), self.overwrite_reminder)

    def save_settings(self):
        self.settings['reminder']['overwrite'] = self.overwrite_reminder.isChecked()


class SignDefaultsTab(QWidget):
    xslotdivisions_changed = pyqtSignal(dict, dict)
    xslotgeneration_changed = pyqtSignal(str, str)

    def __init__(self, settings, **kwargs):
        super().__init__(**kwargs)
        self.settings = settings

        main_layout = QFormLayout()
        self.setLayout(main_layout)

        self.handdominance_layout = QHBoxLayout()
        self.handdominance_group = QButtonGroup(parent=self)
        self.handdominance_l_radio = QRadioButton('Left')
        self.handdominance_l_radio.setProperty('hand', 'L')
        self.handdominance_group.addButton(self.handdominance_l_radio)
        self.handdominance_layout.addWidget(self.handdominance_l_radio)
        self.handdominance_r_radio = QRadioButton('Right')
        self.handdominance_r_radio.setProperty('hand', 'R')
        self.handdominance_group.addButton(self.handdominance_r_radio)
        self.handdominance_layout.addWidget(self.handdominance_r_radio)
        for button in self.handdominance_group.buttons():
            if self.settings['signdefaults']['handdominance'] == button.property('hand'):
                button.setChecked(True)
                break
        main_layout.addRow(QLabel('Default hand dominance:'), self.handdominance_layout)

        self.xslots_layout = QHBoxLayout()
        self.xslots_group = QButtonGroup(parent=self)
        self.xslots_none_radio = QRadioButton("None")
        self.xslots_none_radio.setProperty('xslots', 'none')
        self.xslots_none_radio.toggled.connect(self.handle_none_toggled)
        self.xslots_group.addButton(self.xslots_none_radio)
        self.xslots_layout.addWidget(self.xslots_none_radio)
        self.xslots_manual_radio = QRadioButton("Manual")
        self.xslots_manual_radio.setProperty('xslots', 'manual')
        self.xslots_group.addButton(self.xslots_manual_radio)
        self.xslots_layout.addWidget(self.xslots_manual_radio)
        self.xslots_auto_radio = QRadioButton("Automatic")
        self.xslots_auto_radio.setProperty('xslots', 'auto')
        self.xslots_group.addButton(self.xslots_auto_radio)
        self.xslots_layout.addWidget(self.xslots_auto_radio)

        main_layout.addRow(QLabel("X-slot generation:"), self.xslots_layout)

        self.partialxslots_layout = QVBoxLayout()
        self.partialxslots_group = QButtonGroup(parent=self)
        self.partialxslots_group.setExclusive(False)

        quarter = Fraction(1, 4)
        third = Fraction(1, 3)
        half = Fraction(1, 2)
        self.partialxslots_label = QLabel('X-slot points to include:')
        self.partialxslots_quarters_checkbox = QCheckBox("quarters (" + FRACTION_CHAR[quarter] + "n)")
        self.partialxslots_quarters_checkbox.setProperty('partialxslot', str(quarter))
        self.partialxslots_group.addButton(self.partialxslots_quarters_checkbox)
        self.partialxslots_layout.addWidget(self.partialxslots_quarters_checkbox)
        self.partialxslots_thirds_checkbox = QCheckBox("thirds (" + FRACTION_CHAR[third] + "n)")
        self.partialxslots_thirds_checkbox.setProperty('partialxslot', str(third))
        self.partialxslots_group.addButton(self.partialxslots_thirds_checkbox)
        self.partialxslots_layout.addWidget(self.partialxslots_thirds_checkbox)
        self.partialxslots_halves_checkbox = QCheckBox("halves (" + FRACTION_CHAR[half] + "n)")
        self.partialxslots_halves_checkbox.setProperty('partialxslot', str(half))
        self.partialxslots_group.addButton(self.partialxslots_halves_checkbox)
        self.partialxslots_layout.addWidget(self.partialxslots_halves_checkbox)

        for button in self.xslots_group.buttons():
            if self.settings['signdefaults']['xslot_generation'] == button.property('xslots'):
                button.setChecked(True)
                break

        for button in self.partialxslots_group.buttons():
            fractionstring = button.property('partialxslot')
            fractionchecked = self.settings['signdefaults']['partial_xslots'][fractionstring]
            button.setChecked(fractionchecked)
        main_layout.addRow(self.partialxslots_label, self.partialxslots_layout)

    def handle_none_toggled(self, checked):
        self.partialxslots_label.setEnabled(not checked)
        for button in self.partialxslots_group.buttons():
            button.setEnabled(not checked)

    def save_settings(self):
        self.settings['signdefaults']['handdominance'] = self.handdominance_group.checkedButton().property('hand')
        previous_xslotgeneration = self.settings['signdefaults']['xslot_generation']
        new_xslotgeneration = self.xslots_group.checkedButton().property('xslots')
        self.settings['signdefaults']['xslot_generation'] = new_xslotgeneration

        if previous_xslotgeneration != new_xslotgeneration:
            self.xslotgeneration_changed.emit(previous_xslotgeneration, new_xslotgeneration)

        previouspartials = self.settings['signdefaults']['partial_xslots']
        newpartials = {cb.property('partialxslot'): cb.isChecked() for cb in self.partialxslots_group.buttons()}
        self.settings['signdefaults']['partial_xslots'] = newpartials
        # for cb in self.partialxslots_group.buttons():
        #     self.settings['signdefaults']['partial_xslots'][cb.property('partialxslot')] = cb.isChecked()
        if previouspartials != newpartials:
            self.xslotdivisions_changed.emit(previouspartials, newpartials)




class LocationTab(QWidget):
    # xslotdivisions_changed = pyqtSignal(dict, dict)

    def __init__(self, settings, **kwargs):
        super().__init__(**kwargs)
        self.settings = settings

        main_layout = QFormLayout()
        self.setLayout(main_layout)

        self.locationtype_layout = QVBoxLayout()
        self.locationtype_group = QButtonGroup(parent=self)
        self.loctype_body_radio = QRadioButton('Body')
        self.loctype_body_radio.setProperty('loctype', 'body')
        self.locationtype_group.addButton(self.loctype_body_radio)
        self.locationtype_layout.addWidget(self.loctype_body_radio)
        self.loctype_signingspace_radio = QRadioButton('Signing space')
        self.loctype_signingspace_radio.setProperty('loctype', 'signingspace')
        self.locationtype_group.addButton(self.loctype_signingspace_radio)
        self.locationtype_layout.addWidget(self.loctype_signingspace_radio)
        self.loctype_signingspacebody_radio = QRadioButton('Signing space (body-anchored)')
        self.loctype_signingspacebody_radio.setProperty('loctype', 'signingspace_body')
        self.locationtype_group.addButton(self.loctype_signingspacebody_radio)
        self.locationtype_layout.addWidget(self.loctype_signingspacebody_radio)
        self.loctype_signingspacespatial_radio = QRadioButton('Signing space (purely spatial)')
        self.loctype_signingspacespatial_radio.setProperty('loctype', 'signingspace_spatial')
        self.locationtype_group.addButton(self.loctype_signingspacespatial_radio)
        self.locationtype_layout.addWidget(self.loctype_signingspacespatial_radio)
        self.loctype_none_radio = QRadioButton('None of these')
        self.loctype_none_radio.setProperty('loctype', 'none')
        self.locationtype_group.addButton(self.loctype_none_radio)
        self.locationtype_layout.addWidget(self.loctype_none_radio)
        for button in self.locationtype_group.buttons():
            if self.settings['location']['loctype'] == button.property('loctype'):
                button.setChecked(True)
                break
        main_layout.addRow(QLabel('Default location type:'), self.locationtype_layout)

    def save_settings(self):
        self.settings['location']['loctype'] = self.locationtype_group.checkedButton().property('loctype')


class PreferenceDialog(QDialog):
    prefs_saved = pyqtSignal()
    xslotdivisions_changed = pyqtSignal(dict, dict)
    xslotgeneration_changed = pyqtSignal(str, str)

    def __init__(self, settings, timingfracsinuse, **kwargs):
        super().__init__(**kwargs)

        self.settings = settings
        self.timingfractions_inuse = timingfracsinuse

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        tabs = QTabWidget(parent=self)
        main_layout.addWidget(tabs)

        self.display_tab = DisplayTab(settings, parent=self)
        tabs.addTab(self.display_tab, 'Display')

        self.reminder_tab = ReminderTab(settings, parent=self)
        tabs.addTab(self.reminder_tab, 'Reminder')

        self.signdefaults_tab = SignDefaultsTab(settings, parent=self)
        self.signdefaults_tab.xslotdivisions_changed.connect(self.handle_xslotdivisions_changed)
        self.signdefaults_tab.xslotgeneration_changed.connect(self.handle_xslotgeneration_changed)
        tabs.addTab(self.signdefaults_tab, 'Sign')

        self.location_tab = LocationTab(settings, parent=self)
        tabs.addTab(self.location_tab, 'Location')

        buttons = QDialogButtonBox.Save | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons, parent=self)
        main_layout.addWidget(self.button_box)

        # Ref: https://programtalk.com/vs2/python/654/enki/enki/core/workspace.py/
        self.button_box.clicked.connect(self.handle_button_click)

    def handle_xslotgeneration_changed(self, prev_xslotgen, new_xslotgen):
        self.xslotgeneration_changed.emit(prev_xslotgen, new_xslotgen)

    def handle_xslotdivisions_changed(self, beforedict, afterdict):
        divisionsbefore = [Fraction(fracstring) for fracstring in beforedict.keys() if beforedict[fracstring]]
        fractionsbefore = []
        for frac in divisionsbefore:
            for num in range(1, frac.denominator):
                fracmultiple = num * frac
                if fracmultiple not in fractionsbefore:
                    fractionsbefore.append(fracmultiple)
        divisionsafter = [Fraction(fracstring) for fracstring in afterdict.keys() if afterdict[fracstring]]
        fractionsafter = []
        for frac in divisionsafter:
            for num in range(1, frac.denominator):
                fracmultiple = num * frac
                if fracmultiple not in fractionsafter:
                    fractionsafter.append(fracmultiple)
        # divisionslost = [divn for divn in divisionsbefore if divn not in divisionsafter]
        fractionslost = [frac for frac in fractionsbefore if frac not in fractionsafter]

        fractionsatrisk = []
        for frac in self.timingfractions_inuse:
            if frac in fractionslost and frac not in fractionsatrisk:
                fractionsatrisk.append(frac)

        if len(fractionsatrisk) > 0:
            xslotincompatibilities_msgbox = QMessageBox()
            xslotincompatibilities_msgbox.setText("Your new partial x-slot settings create incompatibilities with previously coded signs that used the old settings. What would you like to do?")
            discardbutton = QPushButton("Discard changes (keep old divisions)")
            # TODO KV implement
            newsignsonlybutton = QPushButton("Apply changes to new signs only (not yet implemented)")  # TODO KV [Tooltip / documentation explains: previously coded signs will have only the old x-slot options both visible and usable; any new signs added will have only the new x-slot options available.]
            # TODO KV implement
            allsignsbutton = QPushButton("Apply changes to all signs (not yet implemented)")  # TODO KV [Tooltip / documentation explains: previously coded signs will keep their coded x-slot selections if they are compatible with the new options, otherwise will lose their associations and need to be recoded; all signs (old and new) will have only the new x-slot options available]. [Add option here: output list of signs that had incompatibilities to a file? or mark in the corpus somehow?]
            xslotincompatibilities_msgbox.addButton(discardbutton, QMessageBox.DestructiveRole)
            xslotincompatibilities_msgbox.addButton(newsignsonlybutton, QMessageBox.ApplyRole)
            xslotincompatibilities_msgbox.addButton(allsignsbutton, QMessageBox.ApplyRole)
            xslotincompatibilities_msgbox.setDefaultButton(discardbutton)
            xslotincompatibilities_msgbox.exec()
            result = xslotincompatibilities_msgbox.clickedButton()

            if result == discardbutton:
                # reset the partial x-slot fractions to whatever they were before
                self.settings['signdefaults']['partial_xslots'] = beforedict
            elif result == newsignsonlybutton:
                # TODO KV
                pass
            elif result == allsignsbutton:
                # TODO KV
                pass

    def handle_button_click(self, button):
        standard = self.button_box.standardButton(button)
        if standard == QDialogButtonBox.Cancel:
            self.reject()
        elif standard == QDialogButtonBox.Save:
            self.display_tab.save_settings()
            self.reminder_tab.save_settings()
            self.signdefaults_tab.save_settings()
            self.location_tab.save_settings()
            self.prefs_saved.emit()
            self.accept()
