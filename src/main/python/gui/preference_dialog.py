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
    QButtonGroup
)

from constant import FRACTION_TEXT
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
        main_layout.addRow(QLabel('Number of displayed decimal places:'), self.decimal_place)

        self.coder_name = QLineEdit(settings['metadata']['coder'], parent=self)
        main_layout.addRow(QLabel('Preferred coder name:'), self.coder_name)

        self.show_tooltip = QCheckBox(parent=self)
        self.show_tooltip.setChecked(settings['display']['tooltips'])
        main_layout.addRow(QLabel('Show tooltip:'), self.show_tooltip)

    def save_settings(self):
        self.settings['display']['sig_figs'] = int(self.decimal_place.value())
        self.settings['display']['tooltips'] = self.show_tooltip.isChecked()
        self.settings['metadata']['coder'] = str(self.coder_name.text())


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
        self.xslots_none_radio = QRadioButton('None')
        self.xslots_none_radio.setProperty('xslots', 'none')
        self.xslots_group.addButton(self.xslots_none_radio)
        self.xslots_layout.addWidget(self.xslots_none_radio)
        self.xslots_manual_radio = QRadioButton('Manual')
        self.xslots_manual_radio.setProperty('xslots', 'manual')
        self.xslots_group.addButton(self.xslots_manual_radio)
        self.xslots_layout.addWidget(self.xslots_manual_radio)
        self.xslots_auto_radio = QRadioButton('Automatic')
        self.xslots_auto_radio.setProperty('xslots', 'auto')
        self.xslots_group.addButton(self.xslots_auto_radio)
        self.xslots_layout.addWidget(self.xslots_auto_radio)

        for button in self.xslots_group.buttons():
            if self.settings['signdefaults']['xslot_generation'] == button.property('xslots'):
                button.setChecked(True)
                break
        main_layout.addRow(QLabel('X-slot generation:'), self.xslots_layout)

        self.partialxslots_layout = QVBoxLayout()
        self.partialxslots_group = QButtonGroup(parent=self)
        self.partialxslots_group.setExclusive(False)

        quarter = Fraction(1, 4)
        third = Fraction(1, 3)
        half = Fraction(1, 2)
        self.partialxslots_quarters_checkbox = QCheckBox("quarters (" + FRACTION_TEXT[quarter] + "n)")
        self.partialxslots_quarters_checkbox.setProperty('partialxslots', str(quarter))
        self.partialxslots_group.addButton(self.partialxslots_quarters_checkbox)
        self.partialxslots_layout.addWidget(self.partialxslots_quarters_checkbox)
        self.partialxslots_thirds_checkbox = QCheckBox("thirds (" + FRACTION_TEXT[third] + "n)")
        self.partialxslots_thirds_checkbox.setProperty('partialxslots', str(third))
        self.partialxslots_group.addButton(self.partialxslots_thirds_checkbox)
        self.partialxslots_layout.addWidget(self.partialxslots_thirds_checkbox)
        self.partialxslots_halves_checkbox = QCheckBox("halves (" + FRACTION_TEXT[half] + "n)")
        self.partialxslots_halves_checkbox.setProperty('partialxslots', str(half))
        self.partialxslots_group.addButton(self.partialxslots_halves_checkbox)
        self.partialxslots_layout.addWidget(self.partialxslots_halves_checkbox)

        for button in self.partialxslots_group.buttons():
            button.setChecked(self.settings['signdefaults']['partial_slots'][button.property('partialxslots')])
        main_layout.addRow(QLabel('X-slot points to include:'), self.partialxslots_layout)

    def save_settings(self):
        self.settings['signdefaults']['handdominance'] = self.handdominance_group.checkedButton().property('hand')
        self.settings['signdefaults']['xslot_generation'] = self.xslots_group.checkedButton().property('xslots')
        for cb in self.partialxslots_group.buttons():
            self.settings['signdefaults']['partial_slots'][cb.property('partialxslots')] = cb.isChecked()


class PreferenceDialog(QDialog):
    def __init__(self, settings, **kwargs):
        super().__init__(**kwargs)

        self.settings = settings

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        tabs = QTabWidget(parent=self)
        main_layout.addWidget(tabs)

        self.display_tab = DisplayTab(settings, parent=self)
        tabs.addTab(self.display_tab, 'Display')

        self.reminder_tab = ReminderTab(settings, parent=self)
        tabs.addTab(self.reminder_tab, 'Reminder')

        self.signdefaults_tab = SignDefaultsTab(settings, parent=self)
        tabs.addTab(self.signdefaults_tab, 'Sign')

        buttons = QDialogButtonBox.Save | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons, parent=self)
        main_layout.addWidget(self.button_box)

        # Ref: https://programtalk.com/vs2/python/654/enki/enki/core/workspace.py/
        self.button_box.clicked.connect(self.handle_button_click)

    def handle_button_click(self, button):
        standard = self.button_box.standardButton(button)
        if standard == QDialogButtonBox.Cancel:
            self.reject()
        elif standard == QDialogButtonBox.Save:
            self.display_tab.save_settings()
            self.reminder_tab.save_settings()
            self.signdefaults_tab.save_settings()

            self.accept()
