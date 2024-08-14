from datetime import datetime

from PyQt5.QtWidgets import (
    QDialog,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLayout,
    QSizePolicy,
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
    QPushButton,
    QComboBox,
    QSpacerItem
)

from PyQt5.QtCore import pyqtSignal, QSettings
from gui.link_help import show_help
from constant import FRACTION_CHAR, HAND, ARM, LEG, DEFAULT_LOC_2H, DEFAULT_LOC_1H
from fractions import Fraction
from lexicon.module_classes import treepathdelimiter, LocationModule
from gui.locationspecification_view import LocationOptionsSelectionPanel, LocationType
from models.location_models import LocationTreeModel
from serialization_classes import LocationTableSerializable
from gui.helper_widget import OptionSwitch


# This tab facilitates user interaction with display-related settings in the preference dialog.
class DisplayTab(QWidget):
    fontsize_changed = pyqtSignal(int)

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

        fontsize_layout = QHBoxLayout()
        self.fontsize_spin = QSpinBox(parent=self)
        self.fontsize_spin.setMinimum(1)
        self.fontsize_spin.setMaximum(40)
        self.fontsize_spin.setValue(settings['display']['fontsize'])
        fontsize_layout.addWidget(self.fontsize_spin)
        main_layout.addRow(QLabel("Font size (points):"), fontsize_layout)
        main_layout.addRow(QLabel(""), QLabel("Some changes won't take effect until SLP-AA is restarted"))

    def save_settings(self):
        self.settings['display']['sig_figs'] = int(self.decimal_place.value())
        self.settings['display']['tooltips'] = self.show_tooltip.isChecked()
        self.settings['metadata']['coder'] = str(self.coder_name.text())

        newfontsize = int(self.fontsize_spin.value())
        if newfontsize != self.settings['display']['fontsize']:
            self.fontsize_changed.emit(newfontsize)
        self.settings['display']['fontsize'] = newfontsize


class EntryIDElementComboBox(QComboBox):
    delim_descriptions = {
        "_": "underscore",
        "-": "hyphen",
        ".": "period",
        "": "none"
    }

    def __init__(self, datatype, curvalue=None, **kwargs):
        super().__init__(**kwargs)
        self.setInsertPolicy(QComboBox.NoInsert)
        self.datatype = datatype

        if self.datatype == "dateformat":
            self.addItems(["YYYY-MM-DD", "YYYYMMDD", "YYYY-MM", "YYYYMM", "YYYY"])
        elif self.datatype == "delimiter":
            self.addItems([k + " (" + v + ")" for (k, v) in self.delim_descriptions.items()])

        self.set_value(curvalue)

    def set_value(self, curvalue):
        if curvalue is not None:
            if self.datatype == "dateformat":
                curtext = curvalue.replace("%Y", "YYYY").replace("%m", "MM").replace("%d", "DD")
            elif self.datatype == "delimiter":
                curtext = curvalue + " (" + self.delim_descriptions[curvalue] + ")"
            self.setCurrentText(curtext)

    def get_value(self):
        if self.datatype == "dateformat":
            return self.currentText().replace("YYYY", "%Y").replace("MM", "%m").replace("DD", "%d")
        elif self.datatype == "delimiter":
            # first character is the delimiter itself, unless the delimiter is 'none' in which case
            # we need to use the empty string, not a space (which occurs just before the '(none)' in
            # the combobox)
            return self.currentText()[0].replace(" ", "")


# This tab facilitates user interaction with EntryID-related settings in the preference dialog.
class EntryIDTab(QWidget):
    def __init__(self, settings, **kwargs):
        super().__init__(**kwargs)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.instructions_label = QLabel("Select which elements, and in which order, will be displayed as the Entry ID for each sign.")
        main_layout.addWidget(self.instructions_label)
        self.qsettings_entryid = QSettings()  # organization name & application name were set in MainWindow.__init__()
        self.qsettings_entryid.beginGroup('entryid')

        form_layout = QFormLayout()

        self.counter_label = QLabel("Sequential number of sign in corpus")
        self.counter_layout = QHBoxLayout()
        self.counter_cb = QCheckBox(parent=self)
        self.counter_cb.setChecked(self.qsettings_entryid.value('counter/visible', type=bool))
        self.counter_layout.addWidget(self.counter_cb)
        self.counter_order = QSpinBox(parent=self)
        self.counter_order.setMinimum(0)
        if self.counter_cb.isChecked():
            self.counter_order.setValue(self.qsettings_entryid.value('counter/order', type=int))
        self.counter_layout.addWidget(self.counter_order)
        self.counter_layout.addStretch()
        self.counterdigits_label = QLabel("Min # of displayed digits:")
        self.counter_layout.addWidget(self.counterdigits_label)
        self.counterdigits_spin = QSpinBox(parent=self)
        self.counterdigits_spin.setMinimum(1)
        self.counterdigits_spin.setValue(self.qsettings_entryid.value('counter/digits', type=int))
        self.counter_layout.addWidget(self.counterdigits_spin)
        self.addupdatelisteners(self.counter_layout)
        form_layout.addRow(self.counter_label, self.counter_layout)

        self.date_label = QLabel("Date sign created")
        self.date_layout = QHBoxLayout()
        self.date_cb = QCheckBox(parent=self)
        self.date_cb.setChecked(self.qsettings_entryid.value('date/visible', type=bool))
        self.date_layout.addWidget(self.date_cb)
        self.date_order = QSpinBox(parent=self)
        self.date_order.setMinimum(0)
        if self.date_cb.isChecked():
            self.date_order.setValue(self.qsettings_entryid.value('date/order', type=int))
        self.date_layout.addWidget(self.date_order)
        self.date_layout.addStretch()
        self.dateformat_label = QLabel("Format:")
        self.date_layout.addWidget(self.dateformat_label)
        self.dateformat_combo = EntryIDElementComboBox(datatype="dateformat", curvalue=self.qsettings_entryid.value('date/format', type=str), parent=self)
        self.date_layout.addWidget(self.dateformat_combo)
        self.addupdatelisteners(self.date_layout)
        form_layout.addRow(self.date_label, self.date_layout)

        self.coder_label = QLabel("Coder metadata (not yet active)")
        self.coder_layout = QHBoxLayout()
        self.coder_cb = QCheckBox(parent=self)
        self.coder_layout.addWidget(self.coder_cb)
        self.coder_order = QSpinBox(parent=self)
        self.coder_order.setMinimum(0)
        self.coder_layout.addWidget(self.coder_order)
        self.coder_layout.addStretch()
        self.addupdatelisteners(self.coder_layout)
        form_layout.addRow(self.coder_label, self.coder_layout)
        # TODO implement details; see https://github.com/PhonologicalCorpusTools/SLPAA/issues/18

        self.signer_label = QLabel("Signer metadata (not yet active)")
        self.signer_layout = QHBoxLayout()
        self.signer_cb = QCheckBox(parent=self)
        self.signer_layout.addWidget(self.signer_cb)
        self.signer_order = QSpinBox(parent=self)
        self.signer_order.setMinimum(0)
        self.signer_layout.addWidget(self.signer_order)
        self.signer_layout.addStretch()
        self.addupdatelisteners(self.signer_layout)
        form_layout.addRow(self.signer_label, self.signer_layout)
        # TODO implement details; see https://github.com/PhonologicalCorpusTools/SLPAA/issues/18

        self.source_label = QLabel("Source metadata (not yet active)")
        self.source_layout = QHBoxLayout()
        self.source_cb = QCheckBox(parent=self)
        self.source_layout.addWidget(self.source_cb)
        self.source_order = QSpinBox(parent=self)
        self.source_order.setMinimum(0)
        self.source_layout.addWidget(self.source_order)
        self.source_layout.addStretch()
        self.addupdatelisteners(self.source_layout)
        form_layout.addRow(self.source_label, self.source_layout)
        # TODO implement details; see https://github.com/PhonologicalCorpusTools/SLPAA/issues/18

        self.recording_label = QLabel("Recording metadata (not yet active)")
        self.recording_layout = QHBoxLayout()
        self.recording_cb = QCheckBox(parent=self)
        self.recording_layout.addWidget(self.recording_cb)
        self.recording_order = QSpinBox(parent=self)
        self.recording_order.setMinimum(0)
        self.recording_layout.addWidget(self.recording_order)
        self.recording_layout.addStretch()
        self.addupdatelisteners(self.recording_layout)
        form_layout.addRow(self.recording_label, self.recording_layout)
        # TODO implement details; see https://github.com/PhonologicalCorpusTools/SLPAA/issues/18

        self.delim_label = QLabel("Delimiter:")
        # 20240325: The following check/adjustment is necessary because of a bug (see issue #294)
        # that involved storing the 'none' delimiter as a space instead of the empty string.
        # The next two lines (the conditional) can eventually be removed, once we are certain
        # that everyone using the software has opened and resaved preferences at least once
        # since this fix was implemented.
        if self.qsettings_entryid.value('delimiter', type=str) == " ":
            self.qsettings_entryid.setValue('delimiter', "")
        self.delim_combo = EntryIDElementComboBox(datatype="delimiter", curvalue=self.qsettings_entryid.value('delimiter', type=str), parent=self)
        self.delim_combo.currentTextChanged.connect(self.updatepreview)
        form_layout.addRow(self.delim_label, self.delim_combo)
        
        self.qsettings_entryid.endGroup()

        self.preview_label = QLabel("Preview:")
        self.preview_text = QLineEdit()
        self.preview_text.setEnabled(False)
        self.updatepreview(None)
        form_layout.addRow(self.preview_label, self.preview_text)

        main_layout.addLayout(form_layout)

    def addupdatelisteners(self, layout):
        index = layout.count() - 1
        while index >= 0:
            widget = layout.itemAt(index).widget()
            if isinstance(widget, QSpinBox):
                widget.valueChanged.connect(self.updatepreview)
            elif isinstance(widget, EntryIDElementComboBox):
                widget.currentTextChanged.connect(self.updatepreview)
            elif isinstance(widget, QCheckBox):
                widget.stateChanged.connect(self.updatepreview)
            index -= 1

    def check_ordering(self):
        order_numbers = []
        if self.counter_cb.isChecked():
            order_numbers.append(self.counter_order.value())
        if self.date_cb.isChecked():
            order_numbers.append(self.date_order.value())

        return len(set(order_numbers)) == len(order_numbers)  # no duplicates

    def updatepreview(self, a0):
        delim = self.delim_combo.get_value()

        samplecounter = "1"
        samplecounterstring = "0" * (self.counterdigits_spin.value() - len(samplecounter)) + samplecounter

        sampledate = datetime.now()
        sampledateformat = self.dateformat_combo.get_value()
        # sampledatestring = sampledate.toString(sampledateformat)
        sampledatestring = sampledate.strftime(sampledateformat)

        # samplecoderstring = "coderinfo"
        # samplesignerstring = "signerinfo"
        # samplesourcestring = "sourceinfo"
        # samplerecordingstring = "recordinginfo"

        if self.check_ordering():
            orders_strings = []
            if self.counter_cb.isChecked():
                orders_strings.append((self.counter_order.value(), samplecounterstring))
            if self.date_cb.isChecked():
                orders_strings.append((self.date_order.value(), sampledatestring))
            # if self.coder_cb.isChecked():
            #     orders_strings.append((self.coder_order.value(), samplecoderstring))
            # if self.signer_cb.isChecked():
            #     orders_strings.append((self.signer_order.value(), samplesignerstring))
            # if self.source_cb.isChecked():
            #     orders_strings.append((self.source_order.value(), samplesourcestring))
            # if self.recording_cb.isChecked():
            #     orders_strings.append((self.recording_order.value(), samplerecordingstring))
            orders_strings.sort()
            self.preview_text.setText(delim.join([string for (order, string) in orders_strings]))
        else:
            self.preview_text.setText("ordering conflict; no preview available")

    def save_settings(self):
        if self.check_ordering():
            self.qsettings_entryid.beginGroup('entryid')
            self.qsettings_entryid.setValue('delimiter', self.delim_combo.get_value())

            self.qsettings_entryid.setValue('counter/visible', self.counter_cb.isChecked())
            self.qsettings_entryid.setValue('counter/order', self.counter_order.value() if self.counter_cb.isChecked() else 0)
            self.qsettings_entryid.setValue('counter/digits', self.counterdigits_spin.value())

            self.qsettings_entryid.setValue('date/visible', self.date_cb.isChecked())
            self.qsettings_entryid.setValue('date/order', self.date_order.value() if self.date_cb.isChecked() else 0)
            self.qsettings_entryid.setValue('date/format', self.dateformat_combo.get_value())

            self.qsettings_entryid.endGroup()  # entryid
            self.qsettings_entryid.sync()
            return ""
        else:
            return "[Entry ID tab] Ordering conflict: Please make sure there are no duplicated order values."

# This tab facilitates user interaction with reminder-related settings in the preference dialog.
class ReminderTab(QWidget):
    def __init__(self, settings, **kwargs):
        super().__init__(**kwargs)
        self.settings = settings

        main_layout = QFormLayout()
        self.setLayout(main_layout)

        self.overwrite_reminder = QCheckBox(parent=self)
        self.overwrite_reminder.setChecked(settings['reminder']['overwrite'])
        main_layout.addRow(QLabel("Always ask before overwriting a sign:"), self.overwrite_reminder)

        self.duplicatelemma_reminder = QCheckBox(parent=self)
        self.duplicatelemma_reminder.setChecked(settings['reminder']['duplicatelemma'])
        main_layout.addRow(QLabel("Always show warning when a new lemma duplicates an existing one:"), self.duplicatelemma_reminder)

    def save_settings(self):
        self.settings['reminder']['overwrite'] = self.overwrite_reminder.isChecked()
        self.settings['reminder']['duplicatelemma'] = self.duplicatelemma_reminder.isChecked()


# This tab facilitates user interaction with sign-related settings in the preference dialog.
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
        self.handdominance_l_radio = QRadioButton("Left")
        self.handdominance_l_radio.setProperty('hand', 'L')
        self.handdominance_group.addButton(self.handdominance_l_radio)
        self.handdominance_layout.addWidget(self.handdominance_l_radio)
        self.handdominance_r_radio = QRadioButton("Right")
        self.handdominance_r_radio.setProperty('hand', 'R')
        self.handdominance_group.addButton(self.handdominance_r_radio)
        self.handdominance_layout.addWidget(self.handdominance_r_radio)
        for button in self.handdominance_group.buttons():
            if self.settings['signdefaults']['handdominance'] == button.property('hand'):
                button.setChecked(True)
                break
        main_layout.addRow(QLabel('Default hand dominance:'), self.handdominance_layout)

        self.signtype_layout = QHBoxLayout()
        self.signtype_group = QButtonGroup(parent=self)
        self.signtype_none_radio = QRadioButton("None")
        self.signtype_none_radio.setProperty('signtype', 'none')
        self.signtype_group.addButton(self.signtype_none_radio)
        self.signtype_layout.addWidget(self.signtype_none_radio)
        self.signtype_unspec_radio = QRadioButton("Unspecified")
        self.signtype_unspec_radio.setProperty('signtype', 'unspec')
        self.signtype_group.addButton(self.signtype_unspec_radio)
        self.signtype_layout.addWidget(self.signtype_unspec_radio)
        self.signtype_one_radio = QRadioButton("1 hand")
        self.signtype_one_radio.setProperty('signtype', '1hand')
        self.signtype_group.addButton(self.signtype_one_radio)
        self.signtype_layout.addWidget(self.signtype_one_radio)
        self.signtype_two_radio = QRadioButton("2 hands")
        self.signtype_two_radio.setProperty('signtype', '2hand')
        self.signtype_group.addButton(self.signtype_two_radio)
        self.signtype_layout.addWidget(self.signtype_two_radio)
        for button in self.signtype_group.buttons():
            if self.settings['signdefaults']['signtype'] == button.property('signtype'):
                button.setChecked(True)
                break
        main_layout.addRow(QLabel('Default sign type:'), self.signtype_layout)

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
        self.partialxslots_label = QLabel("X-slot points to include:")
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
        self.settings['signdefaults']['signtype'] = self.signtype_group.checkedButton().property('signtype')
        previous_xslotgeneration = self.settings['signdefaults']['xslot_generation']
        new_xslotgeneration = self.xslots_group.checkedButton().property('xslots')
        self.settings['signdefaults']['xslot_generation'] = new_xslotgeneration

        if previous_xslotgeneration != new_xslotgeneration:
            self.xslotgeneration_changed.emit(previous_xslotgeneration, new_xslotgeneration)

        previouspartials = self.settings['signdefaults']['partial_xslots']
        newpartials = {cb.property('partialxslot'): cb.isChecked() for cb in self.partialxslots_group.buttons()}
        self.settings['signdefaults']['partial_xslots'] = newpartials
        if previouspartials != newpartials:
            self.xslotdivisions_changed.emit(previouspartials, newpartials)


# This tab facilitates user interaction with location module-related settings in the preference dialog.
class LocationTab(QWidget):

    def __init__(self, settings, **kwargs):
        super().__init__(**kwargs)
        self.settings = settings
        self.mainwindow = self.parent().mainwindow
        main_layout = QFormLayout()
        self.setLayout(main_layout)

        self.locationtype_layout = QVBoxLayout()
        self.locationtype_group = QButtonGroup(parent=self)
        self.loctype_body_radio = QRadioButton("Body")
        self.loctype_body_radio.setProperty('loctype', 'body')
        self.locationtype_group.addButton(self.loctype_body_radio)
        self.locationtype_layout.addWidget(self.loctype_body_radio)
        self.loctype_signingspace_radio = QRadioButton("Signing space")
        self.loctype_signingspace_radio.setProperty('loctype', 'signingspace')
        self.locationtype_group.addButton(self.loctype_signingspace_radio)
        self.locationtype_layout.addWidget(self.loctype_signingspace_radio)
        self.loctype_signingspacebody_radio = QRadioButton("Signing space (body-anchored)")
        self.loctype_signingspacebody_radio.setProperty('loctype', 'signingspace_body')
        self.locationtype_group.addButton(self.loctype_signingspacebody_radio)
        self.locationtype_layout.addWidget(self.loctype_signingspacebody_radio)
        self.loctype_signingspacespatial_radio = QRadioButton("Signing space (purely spatial)")
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
        main_layout.addRow(QLabel("Default location type:"), self.locationtype_layout)

        self.locnimgclickorder_switch = OptionSwitch("Large to small", "Small to large")
        self.locnimgclickorder_switch.setwhichbuttonselected(self.settings['location']['clickorder'])
        main_layout.addRow(QLabel("L-clicking on image iterates over locations from:"),
                           self.locnimgclickorder_switch)

        self.defaultneutral_layout = QVBoxLayout()
        self.defaultneutral_1h_button = QPushButton("Change default neutral one-handed location")
        self.defaultneutral_2h_button = QPushButton("Change default neutral two-handed location")
        self.defaultneutral_layout.addWidget(self.defaultneutral_1h_button)
        self.defaultneutral_layout.addWidget(self.defaultneutral_2h_button)
        self.defaultneutral_1h_button.clicked.connect(lambda: self.change_default_neutral(1))
        self.defaultneutral_2h_button.clicked.connect(lambda: self.change_default_neutral(2))

        self.defaultneutral_layout.addWidget(QLabel("Automatically select 'This location is neutral' when:"))
        self.autocheck_neutral_cb = QCheckBox("'Apply neutral settings' button is pressed")
        self.autocheck_neutral_cb.setChecked(self.settings['location']['autocheck_neutral'])
        self.autocheck_neutral_on_locn_selected_cb = QCheckBox("'Default neutral location' is added to location list")
        self.autocheck_neutral_on_locn_selected_cb.setChecked(self.settings['location']['autocheck_neutral_on_locn_selected'])
        self.defaultneutral_layout.addWidget(self.autocheck_neutral_cb)
        self.defaultneutral_layout.addWidget(self.autocheck_neutral_on_locn_selected_cb)

        main_layout.addRow(QLabel('Default neutral location:'), self.defaultneutral_layout)        
    
    def change_default_neutral(self, numhands):
        self.locationselector = DefaultNeutralDialog(numhands, parent=self)
        self.locationselector.exec_()
        

    def save_settings(self):
        self.settings['location']['clickorder'] = self.locnimgclickorder_switch.getwhichbuttonselected()
        self.settings['location']['loctype'] = self.locationtype_group.checkedButton().property('loctype')
        self.settings['location']['autocheck_neutral'] = self.autocheck_neutral_cb.isChecked()
        self.settings['location']['autocheck_neutral_on_locn_selected'] = self.autocheck_neutral_on_locn_selected_cb.isChecked()

class DefaultNeutralDialog(QDialog):

    def __init__(self, numhands, **kwargs):
        super().__init__(**kwargs)
        self.mainwindow = self.parent().mainwindow
        self.mainlayout = QVBoxLayout()
        self.numhands = numhands
        self.get_current_defaults()
        
        self.setLayout(self.mainlayout)

        self.loctypelayout = QHBoxLayout()
        self.loctypelabel = QLabel("Signing space: ")
        self.loctypelayout.addWidget(self.loctypelabel)

        self.loctype_group = QButtonGroup(parent=self)
        self.loctype_group.buttonClicked.connect(self.on_loctype_selected)
        self.bodyanchored_rb = QRadioButton("body-anchored")
        self.purelyspatial_rb = QRadioButton("purely spatial")
        self.loctype_group.addButton(self.bodyanchored_rb)
        self.loctype_group.addButton(self.purelyspatial_rb)
        for b in self.loctype_group.buttons():
            b.setChecked(b.text() == self.loctype)

        self.loctypelayout.addWidget(self.bodyanchored_rb)
        self.loctypelayout.addWidget(self.purelyspatial_rb)

        self.mainlayout.addLayout(self.loctypelayout)

        self.recreate_treeandlistmodels()
        
        self.locationoptionsselectionpanel = LocationOptionsSelectionPanel(treemodeltoload=self.currenttreemodel, displayvisualwidget=True, parent=self)
        self.locationoptionsselectionpanel.multiple_selection_cb.setEnabled(False)
        self.locationoptionsselectionpanel.multiple_selection_cb.setChecked(self.loctype == "body-anchored")
        
        self.enablelocationtools()
        self.mainlayout.addWidget(self.locationoptionsselectionpanel)        
        
        buttons = QDialogButtonBox.RestoreDefaults | QDialogButtonBox.Save | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons, parent=self)
        self.button_box.clicked.connect(self.handle_button_click)

        self.mainlayout.addWidget(self.button_box)

    def recreate_treeandlistmodels(self):
        self.treemodel_body = LocationTreeModel()
        self.treemodel_body.multiple_selection_allowed = True
        self.treemodel_body.locationtype = LocationType(body=True)
        self.treemodel_body.populate(self.treemodel_body.invisibleRootItem())
        self.treemodel_spatial = LocationTreeModel()
        self.treemodel_spatial.locationtype = LocationType(signingspace=True, purelyspatial=True)
        self.treemodel_spatial.populate(self.treemodel_spatial.invisibleRootItem())

        self.listmodel_body = self.treemodel_body.listmodel
        self.listmodel_spatial = self.treemodel_spatial.listmodel

        self.currenttreemodel = self.treemodel_spatial
        if self.bodyanchored_rb.isChecked():
            self.currenttreemodel = self.treemodel_body
        
        self.currenttreemodel.addcheckedvalues(self.currenttreemodel.invisibleRootItem(), self.locs, include_details=True)
    
    def get_current_defaults(self):
        if self.numhands == 1:
            self.loctype = self.parent().settings['location']['default_loctype_1h']
            self.locs = self.parent().settings['location']['default_loc_1h']

        else:
            self.loctype = self.parent().settings['location']['default_loctype_2h']
            self.locs = self.parent().settings['location']['default_loc_2h']
    
    def handle_button_click(self, button):
        standard = self.button_box.standardButton(button)
        if standard == QDialogButtonBox.Cancel:
            self.reject()

        elif standard == QDialogButtonBox.Save:
            self.validate_and_save()

        elif standard == QDialogButtonBox.RestoreDefaults:
            self.restore_defaults()
    

    def validate_and_save(self):
        messagestring = ""
        paths = self.locationoptionsselectionpanel.get_listed_paths(include_details=True)
        if len(paths) == 0:
            messagestring += "Default neutral location cannot be empty."

        if messagestring != "":
            # refuse to save without valid module selections
            # warn user that there's missing and/or invalid info and don't let them save
            QMessageBox.critical(self, "Warning", messagestring)
        else:
            # save info and then close dialog
            if self.numhands == 1:
                self.parent().settings['location']['default_loc_1h'] = paths
                self.parent().settings['location']['default_loctype_1h'] = self.loctype
            elif self.numhands == 2:
                self.parent().settings['location']['default_loc_2h'] = paths
                self.parent().settings['location']['default_loctype_2h'] = self.loctype
            self.accept()
        
    def restore_defaults(self):
        hands = "one-handed" if self.numhands == 1 else "two-handed"
        result = QMessageBox.warning(self,
                                         "Restore",
                                         "Are you sure you want to restore the definition of the " + hands +  " default neutral location to the original system setting?",
                                         QMessageBox.Ok | QMessageBox.Cancel,
                                         QMessageBox.Cancel)
        if result == QMessageBox.Ok:
            if self.numhands == 1:
                self.parent().settings['location']['default_loc_1h'] = DEFAULT_LOC_1H
                self.parent().settings['location']['default_loctype_1h'] = "purely spatial"
            else:
                self.parent().settings['location']['default_loc_2h'] = DEFAULT_LOC_2H
                self.parent().settings['location']['default_loctype_2h'] = "purely spatial"
            self.purelyspatial_rb.setChecked(True)
            self.get_current_defaults()
            self.recreate_treeandlistmodels()
            self.enablelocationtools()
            self.locationoptionsselectionpanel.multiple_selection_cb.setChecked(False)
            self.locationoptionsselectionpanel.multiple_selection_cb.setEnabled(False)

    def on_loctype_selected(self, btn):
        if btn == self.bodyanchored_rb:
            self.loctype = "body-anchored"
        elif btn == self.purelyspatial_rb:
            self.loctype = "purely spatial"
        self.enablelocationtools()

    def enablelocationtools(self):
        # self.refresh_listproxies()
        if self.loctype == "body-anchored":
            self.locationoptionsselectionpanel.treemodel = self.treemodel_body
            self.locationoptionsselectionpanel.multiple_selection_cb.setChecked(True)
        elif self.loctype == "purely spatial":
            self.locationoptionsselectionpanel.treemodel = self.treemodel_spatial
            self.locationoptionsselectionpanel.multiple_selection_cb.setChecked(False)
        self.locationoptionsselectionpanel.refresh_listproxies()

        # use current locationtype (from buttons) to determine whether/how things get enabled
        isbodyanchored = self.loctype == "body-anchored"
        # self.locationoptionsselectionpanel.locationselectionwidget.setlocationtype(self.getcurrentlocationtype(), treemodel=self.getcurrenttreemodel())
        self.locationoptionsselectionpanel.enableImageTabs(isbodyanchored)
        self.locationoptionsselectionpanel.combobox.setEnabled(True)
        self.locationoptionsselectionpanel.pathslistview.setEnabled(True)
        self.locationoptionsselectionpanel.update_detailstable()
        self.locationoptionsselectionpanel.detailstableview.setEnabled(isbodyanchored)


# This is the global settings dialog that users access via the Settings menu.
class PreferenceDialog(QDialog):
    prefs_saved = pyqtSignal()
    xslotdivisions_changed = pyqtSignal(dict, dict)
    xslotgeneration_changed = pyqtSignal(str, str)
    fontsize_changed = pyqtSignal(int)

    def __init__(self, settings, timingfracsinuse, **kwargs):
        super().__init__(**kwargs)
        self.settings = settings
        self.timingfractions_inuse = timingfracsinuse
        self.mainwindow = self.parent()

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        tabs = QTabWidget(parent=self)
        main_layout.addWidget(tabs)

        self.display_tab = DisplayTab(settings, parent=self)
        self.display_tab.fontsize_changed.connect(self.fontsize_changed.emit)
        tabs.addTab(self.display_tab, 'Display')

        self.entryid_tab = EntryIDTab(settings, parent=self)
        tabs.addTab(self.entryid_tab, 'Entry ID')

        self.reminder_tab = ReminderTab(settings, parent=self)
        tabs.addTab(self.reminder_tab, 'Reminder')

        self.signdefaults_tab = SignDefaultsTab(settings, parent=self)
        self.signdefaults_tab.xslotdivisions_changed.connect(self.handle_xslotdivisions_changed)
        self.signdefaults_tab.xslotgeneration_changed.connect(self.handle_xslotgeneration_changed)
        tabs.addTab(self.signdefaults_tab, 'Sign')

        self.location_tab = LocationTab(settings, parent=self)
        tabs.addTab(self.location_tab, 'Location')

        buttons = QDialogButtonBox.Save | QDialogButtonBox.Help | QDialogButtonBox.Cancel
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
            # TODO implement
            newsignsonlybutton = QPushButton("Apply changes to new signs only (not yet implemented)")  # TODO KV [Tooltip / documentation explains: previously coded signs will have only the old x-slot options both visible and usable; any new signs added will have only the new x-slot options available.]
            # TODO implement
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
                # TODO
                pass
            elif result == allsignsbutton:
                # TODO
                pass

    def handle_button_click(self, button):
        standard = self.button_box.standardButton(button)
        if standard == QDialogButtonBox.Cancel:
            self.reject()
        elif standard == QDialogButtonBox.Help:
            show_help('preferences')
        elif standard == QDialogButtonBox.Save:
            errormessages = []
            for tab in [self.display_tab, self.entryid_tab, self.reminder_tab, self.signdefaults_tab, self.location_tab]:
                errorstring = tab.save_settings()
                if errorstring:
                    errormessages.append(errorstring)
            if len(errormessages) > 0:
                QMessageBox.critical(self, "Error saving preferences", "\n".join(errormessages))
                return
            else:
                self.prefs_saved.emit()
                self.accept()
