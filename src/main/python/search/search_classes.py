
import logging
# from gui.hand_configuration import ConfigGlobal, Config
from gui.signtypespecification_view import SigntypeSelectorDialog
from gui.signlevelinfospecification_view import SignlevelinfoSelectorDialog, SignLevelInfoPanel
from gui.helper_widget import CollapsibleSection, ToggleSwitch
# from gui.decorator import check_date_format, check_empty_gloss
from constant import DEFAULT_LOCATION_POINTS, HAND, ARM, LEG, ARTICULATOR_ABBREVS
from gui.xslotspecification_view import XslotSelectorDialog, XslotStructure
from lexicon.module_classes import TimingPoint, TimingInterval, ModuleTypes
from lexicon.lexicon_classes import Sign, SignLevelInformation
from gui.modulespecification_dialog import ModuleSelectorDialog
from gui.xslot_graphics import XslotRect, XslotRectModuleButton, SignSummaryScene, XslotEllipseModuleButton
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QSize
from PyQt5.QtWidgets import (
    QLineEdit,
    QDialog,
    QFrame,
    QHBoxLayout,
    QFormLayout,
    QRadioButton,
    QVBoxLayout,
    QDialogButtonBox,
    QPlainTextEdit,
    QButtonGroup,
    QCheckBox,
    QLabel,
    QWidget,
    QMessageBox
)

from gui.movementspecification_view import MovementSpecificationPanel
from gui.locationspecification_view import LocationSpecificationPanel
from gui.handconfigspecification_view import HandConfigSpecificationPanel
from gui.relationspecification_view import RelationSpecificationPanel
from gui.modulespecification_dialog import XslotLinkingPanel, XslotLinkScene
from gui.modulespecification_widgets import AddedInfoPushButton, ArticulatorSelector

class Search_SignLevelInfoSelectorDialog(QDialog):
    saved_signlevelinfo = pyqtSignal(SignLevelInformation)

    def __init__(self, signlevelinfo, **kwargs):
        super().__init__(**kwargs)
        self.setWindowTitle("Sign-level information")
        self.mainwindow = self.parent().mainwindow
        self.settings = self.mainwindow.app_settings

        self.signlevelinfo_widget = Search_SignLevelInfoPanel(signlevelinfo, parent=self)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.signlevelinfo_widget)

        separate_line = QFrame()
        separate_line.setFrameShape(QFrame.HLine)
        separate_line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separate_line)

        buttons = QDialogButtonBox.RestoreDefaults | QDialogButtonBox.Save | QDialogButtonBox.Cancel

        self.button_box = QDialogButtonBox(buttons, parent=self)

        self.button_box.clicked.connect(self.handle_button_click)

        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)
        self.signlevelinfo_widget.set_starting_focus()
        self.setMinimumSize(QSize(700, 500))  # width, height

    def handle_button_click(self, button):
        standard = self.button_box.standardButton(button)
        if standard == QDialogButtonBox.Cancel:
            self.reject()

        elif standard == QDialogButtonBox.Save:
            sli = self.signlevelinfo_widget.get_value()
            if sli is not None: # TODO check for a value?
                self.saved_signlevelinfo.emit(SignLevelInformation(signlevel_info=sli))
                self.accept()

        elif standard == QDialogButtonBox.RestoreDefaults:
            self.signlevelinfo_widget.restore_defaults()
        

class Search_SignLevelInfoPanel(SignLevelInfoPanel):
    def __init__(self, signlevelinfo, **kwargs):
        super().__init__(signlevelinfo, **kwargs)
        QWidget().setLayout(self.layout()) # reparent the current inherited layout
        self.create_and_set_layout() # otherwise, will be attempting to set layout to something that already has a layout
    
    def create_and_set_layout(self):
        main_layout = QFormLayout()
        main_layout.setSpacing(5)

        entryid_label = QLabel("Entry ID:")
        gloss_label = QLabel('Gloss:')
        lemma_label = QLabel('Lemma:')
        source_label = QLabel('Source:')
        signer_label = QLabel('Signer:')
        freq_label = QLabel('Frequency:')
        coder_label = QLabel('Coder:')
        created_label = QLabel('Date created:')
        modified_label = QLabel('Date last modified:')
        note_label = QLabel('Notes:')

        self.entryid_value = QLineEdit()
        self.gloss_edit = QLineEdit()
        self.lemma_edit = QLineEdit()
        self.source_edit = QLineEdit()
        self.signer_edit = QLineEdit()
        self.freq_edit = QLineEdit()
        self.coder_edit = QLineEdit()
        # TODO fix this
        self.created_display = QLineEdit()
        self.modified_display = QLineEdit()
        self.note_edit = QPlainTextEdit()

        self.fingerspelled_grp = CustomRBGrp()
        self.fingerspelled_T_rb = QRadioButton("True")
        self.fingerspelled_F_rb = QRadioButton("False")
        self.fingerspelled_grp.addButton(self.fingerspelled_T_rb)
        self.fingerspelled_grp.addButton(self.fingerspelled_F_rb)
        fingerspelled_label = QLabel('Fingerspelled:')
        self.fingerspelled_layout = QHBoxLayout()
        self.fingerspelled_layout.addWidget(self.fingerspelled_T_rb)
        self.fingerspelled_layout.addWidget(self.fingerspelled_F_rb)
        self.fingerspelled_layout.addStretch()

        self.compoundsign_grp = CustomRBGrp()
        self.compoundsign_T_rb = QRadioButton("True")
        self.compoundsign_F_rb = QRadioButton("False")
        self.compoundsign_grp.addButton(self.compoundsign_T_rb)
        self.compoundsign_grp.addButton(self.compoundsign_F_rb)
        compoundsign_label = QLabel('Compound sign:')
        self.compoundsign_layout = QHBoxLayout()
        self.compoundsign_layout.addWidget(self.compoundsign_T_rb)
        self.compoundsign_layout.addWidget(self.compoundsign_F_rb)
        self.compoundsign_layout.addStretch()

        
        self.handdominance_buttongroup = CustomRBGrp()  # parent=self)
        self.handdominance_l_radio = QRadioButton("Left")
        self.handdominance_r_radio = QRadioButton("Right")
        self.handdominance_buttongroup.addButton(self.handdominance_l_radio)
        self.handdominance_buttongroup.addButton(self.handdominance_r_radio)
        handdominance_label = QLabel("Hand dominance:")
        self.handdominance_layout = QHBoxLayout()
        self.handdominance_layout.addWidget(self.handdominance_l_radio)
        self.handdominance_layout.addWidget(self.handdominance_r_radio)
        self.handdominance_layout.addStretch()

        main_layout.addRow(entryid_label, self.entryid_value)
        main_layout.addRow(gloss_label, self.gloss_edit)
        main_layout.addRow(lemma_label, self.lemma_edit)
        main_layout.addRow(source_label, self.source_edit)
        main_layout.addRow(signer_label, self.signer_edit)
        main_layout.addRow(freq_label, self.freq_edit)
        main_layout.addRow(coder_label, self.coder_edit)
        main_layout.addRow(created_label, self.created_display)
        main_layout.addRow(modified_label, self.modified_display)
        main_layout.addRow(note_label, self.note_edit)
        main_layout.addRow(fingerspelled_label, self.fingerspelled_layout)
        main_layout.addRow(compoundsign_label, self.compoundsign_layout)
        main_layout.addRow(handdominance_label, self.handdominance_layout)

        self.setLayout(main_layout)

    def get_handdominance(self):
        if self.handdominance_r_radio.isChecked():
            return 'R'
        elif self.handdominance_r_radio.isChecked():
            return 'L'
        else:
            return ""

    def get_compoundsignstatus(self):
        if self.compoundsign_F_rb.isChecked():
            return 'F'
        elif self.compoundsign_T_rb.isChecked():
            return 'T'
        else:
            return ""

    def get_fingerspelledstatus(self):
        if self.fingerspelled_F_rb.isChecked():
            return 'F'
        elif self.fingerspelled_T_rb.isChecked():
            return 'T'
        else:
            return ""

    # don't check that gloss is populated
    def get_value(self):
        return {
            'entryid': self.entryid_value.text(),
            'gloss': self.get_gloss(),
            'lemma': self.lemma_edit.text(),
            'source': self.source_edit.text(),
            'signer': self.signer_edit.text(),
            'frequency': self.freq_edit.text(),
            'coder': self.coder_edit.text(),
            # TODO fix
            'date created': self.created_display.text(),
            'date last modified': self.modified_display.text(),
            'note': self.note_edit.toPlainText(),
            'fingerspelled': self.get_fingerspelledstatus(),
            'compoundsign': self.get_compoundsignstatus(),
            'handdominance': self.get_handdominance()
        }

    # Remove the wrapper that forces gloss to be populated
    def get_gloss(self):
        return self.gloss_edit.text()
    
    def restore_defaults(self):
        self.entryid_value.setText("")
        self.entryid_value.setEnabled(True)
        self.gloss_edit.setText("")
        self.gloss_edit.setPlaceholderText("")
        self.lemma_edit.setText("")
        self.source_edit.setText("")
        self.signer_edit.setText("")
        self.freq_edit.setText("")
        self.coder_edit.setText("")
        self.created_display.setText("")
        self.modified_display.setText("")
        self.note_edit.clear()
        self.note_edit.setPlaceholderText("")
        for grp in [self.fingerspelled_grp.buttons(), self.compoundsign_grp.buttons(), self.handdominance_buttongroup.buttons()]:
            for b in grp:
                b.setChecked(False)

class Search_ModuleSelectorDialog(ModuleSelectorDialog):
    def __init__(self, moduletype, xslotstructure=None, xslottype=None, xslotnum=None, moduletoload=None, linkedfrommoduleid=None, linkedfrommoduletype=None, includephase=0, incl_articulators=..., incl_articulator_subopts=0, **kwargs):
        self.xslottype = xslottype
        self.xslotnum = xslotnum
        super().__init__(moduletype, xslotstructure, moduletoload, linkedfrommoduleid, linkedfrommoduletype, includephase, incl_articulators, incl_articulator_subopts, **kwargs)
        
    def add_button_box(self, new_instance=False):
        buttons = QDialogButtonBox.RestoreDefaults | QDialogButtonBox.Save | QDialogButtonBox.Apply | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons, parent=self)
        self.button_box.button(QDialogButtonBox.Save).setText("Save target and add another")
        self.button_box.button(QDialogButtonBox.Apply).setDefault(True)
        self.button_box.button(QDialogButtonBox.Apply).setText("Save target")

        # TODO KV keep? from orig locationdefinerdialog:
        #      Ref: https://programtalk.com/vs2/python/654/enki/enki/core/workspace.py/
        self.button_box.clicked.connect(self.handle_button_click)

        self.main_layout.addWidget(self.button_box)

    def assign_module_widget(self, moduletype, moduletoload):
        if moduletype == ModuleTypes.MOVEMENT:
            self.module_widget = Search_MovementSpecPanel(moduletoload=moduletoload, parent=self)
        elif moduletype == ModuleTypes.LOCATION:
            logging.warning("Location is not implemented")
        elif moduletype == ModuleTypes.HANDCONFIG:
            logging.warning("hand config is not implemented")
        elif self.moduletype == ModuleTypes.RELATION:
            logging.warning("relation is not implemented")
    
    def handle_xslot_widget(self, xslotstructure, timingintervals):
        self.xslot_widget = XslotLinkingPanel(xslotstructure=xslotstructure,
                                              timingintervals=timingintervals,
                                              parent=self)

        if self.xslottype != "ignore":
            self.main_layout.addWidget(self.xslot_widget)

    
    def handle_button_click(self, button):
        standard = self.button_box.standardButton(button)

        if standard == QDialogButtonBox.Cancel:
            self.reject()

        elif standard == QDialogButtonBox.Save:  # save and add another
            self.validate_and_save(addanother=True, closedialog=False)

        elif standard == QDialogButtonBox.Apply:  # save and close
            self.validate_and_save(addanother=False, closedialog=True)

        elif standard == QDialogButtonBox.RestoreDefaults:  # restore defaults
            # TODO KV -- where should the "defaults" be defined?
            self.articulators_widget.clear()
            self.addedinfobutton.clear()
            self.xslot_widget.clear()
            self.module_widget.clear()

    def validate_and_save(self, addanother=False, closedialog=False):
        inphase = self.articulators_widget.getphase()
        addedinfo = self.addedinfobutton.addedinfo
        # validate hand selection
        articulatorsvalid, articulators = self.validate_articulators()

        # validate timing interval(s) selection
        timingvalid, timingintervals = self.validate_timingintervals()

        # validate module selections
        modulevalid, modulemessage = self.module_widget.validity_check()

        messagestring = ""

        savedmodule = None
        if messagestring != "":
            # warn user that there's missing and/or invalid info and don't let them save
            QMessageBox.critical(self, "Warning", messagestring)
        elif addanother:
            # save info and then refresh screen to start next module
            savedmodule = self.module_widget.getsavedmodule(articulators, timingintervals, addedinfo, inphase)
            self.module_saved.emit(savedmodule, self.moduletype)
            self.articulators_widget.clear()
            self.addedinfobutton.clear()
            self.xslot_widget.clear()
            self.module_widget.clear()
            self.module_widget.existingkey = None
            if self.moduletype == ModuleTypes.RELATION:
                self.module_widget.setvaluesfromanchor(self.linkedfrommoduleid, self.linkedfrommoduletype)
        elif not addanother:
            # save info
            savedmodule = self.module_widget.getsavedmodule(articulators, timingintervals, addedinfo, inphase)
            self.module_saved.emit(savedmodule, self.moduletype)
            if closedialog:
                # close dialog if caller requests it (but if we're only saving so, eg,
                # we can add an associated relation module, then closedialog will be False)
                self.accept()

        return savedmodule


class CustomRBGrp(QButtonGroup):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setExclusive(False)
        self.buttonClicked.connect(self.uncheck_buttons)
    
    def uncheck_buttons(self, button):
        for b in self.buttons():
            b.setChecked(b==button)

class Search_MovementSpecPanel(MovementSpecificationPanel):
    def __init__(self, moduletoload=None, **kwargs):
        super().__init__(moduletoload, **kwargs)

class Search_LocationSpecPanel(LocationSpecificationPanel):
    def __init__(self, moduletoload=None, showimagetabs=True, **kwargs):
        super().__init__(moduletoload, showimagetabs, **kwargs)

class Search_HandConfigSpecPanel(HandConfigSpecificationPanel):
    def __init__(self, moduletoload=None, **kwargs):
        super().__init__(moduletoload, **kwargs)

class Search_RelationSpecPanel(RelationSpecificationPanel):
    def __init__(self, moduletoload=None, **kwargs):
        super().__init__(moduletoload, **kwargs)