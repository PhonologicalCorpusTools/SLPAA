
import logging
# from gui.hand_configuration import ConfigGlobal, Config
from gui.signtypespecification_view import SigntypeSelectorDialog
from gui.signlevelinfospecification_view import SignlevelinfoSelectorDialog, SignLevelInfoPanel
from gui.helper_widget import CollapsibleSection, ToggleSwitch
# from gui.decorator import check_date_format, check_empty_gloss
from constant import DEFAULT_LOCATION_POINTS, HAND, ARM, LEG, ARTICULATOR_ABBREVS, TargetTypes
from gui.xslotspecification_view import XslotSelectorDialog, XslotStructure
from lexicon.module_classes import TimingPoint, TimingInterval, ModuleTypes, LocationModule, Direction, Distance, ExtendedFingersModule
from lexicon.lexicon_classes import Sign, SignLevelInformation
from gui.modulespecification_dialog import ModuleSelectorDialog

from gui.xslot_graphics import XslotRect, XslotRectModuleButton, SignSummaryScene, XslotEllipseModuleButton
from PyQt5.Qt import QStandardItem
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QSize
from PyQt5.QtWidgets import (
    QListView,
    QLineEdit,
    QDialog,
    QTabWidget,
    QFrame,
    QHBoxLayout,
    QFormLayout,
    QRadioButton,
    QPushButton,
    QVBoxLayout,
    QDialogButtonBox,
    QPlainTextEdit,
    QButtonGroup,
    QCheckBox,
    QLabel,
    QWidget,
    QMessageBox,
    QSpacerItem,
    QSizePolicy,
    QGroupBox,

)
from gui.movementspecification_view import MovementSpecificationPanel
from gui.locationspecification_view import LocationSpecificationPanel
from gui.handconfigspecification_view import HandConfigSpecificationPanel
from gui.relationspecification_view import RelationSpecificationPanel, ModuleLinkingListModel
from gui.modulespecification_widgets import DeselectableRadioButton, DeselectableRadioButtonGroup
from gui.modulespecification_dialog import XslotLinkingPanel, XslotLinkScene, AssociatedRelationsDialog, AssociatedRelationsPanel
from gui.modulespecification_widgets import AddedInfoPushButton, ArticulatorSelector



class XslotTypes:
    IGNORE = "ignore"
    ABSTRACT_XSLOT = "abstract xslot"
    ABSTRACT_WHOLE = "abstract whole"
    CONCRETE = "concrete"

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
        self.setMinimumSize(QSize(700, 500))  # width, height
            

    def handle_button_click(self, button):
        standard = self.button_box.standardButton(button)
        if standard == QDialogButtonBox.Cancel:
            self.reject()

        elif standard == QDialogButtonBox.Save:
            vals = self.signlevelinfo_widget.get_value()
            if vals is not None: # TODO check for a value?
                sli = self.get_SLI(vals)
                self.saved_signlevelinfo.emit(sli)
                self.accept()

        elif standard == QDialogButtonBox.RestoreDefaults:
            self.signlevelinfo_widget.restore_defaults()
    
    def get_SLI(self, vals):
        sli = SignLevelInformation(signlevel_info=vals)
        if vals["entryid"] == "":
            sli.entryid.counter = ""
        return sli

class Search_SignLevelInfoPanel(SignLevelInfoPanel):
    def __init__(self, signlevelinfo, **kwargs):
        super().__init__(signlevelinfo, **kwargs)
        QWidget().setLayout(self.layout()) # reparent the current inherited layout
        self.signlevelinfo = signlevelinfo
        
        self.create_and_set_layout() # otherwise, will be attempting to set layout to something that already has a layout

    def create_and_set_layout(self):
        main_layout = QFormLayout()
        main_layout.setSpacing(5)

        gloss_label = QLabel('Gloss:')
        lemma_label = QLabel('Lemma:')
        idgloss_label = QLabel('ID-gloss:')
        entryid_label = QLabel("Entry ID:")
        source_label = QLabel('Source:')
        signer_label = QLabel('Signer:')
        freq_label = QLabel('Frequency:')
        coder_label = QLabel('Coder:')
        created_label = QLabel('Date created:')
        modified_label = QLabel('Date last modified:')
        note_label = QLabel('Notes:')

        self.gloss_edit = QLineEdit()
        self.lemma_edit = QLineEdit()
        self.idgloss_edit = QLineEdit()
        self.entryid_value = QLineEdit()
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
        main_layout.addRow(idgloss_label, self.idgloss_edit)
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
        self.set_value()
        self.setLayout(main_layout)

    def get_handdominance(self):
        if self.handdominance_r_radio.isChecked():
            return 'R'
        elif self.handdominance_l_radio.isChecked():
            return 'L'
        else:
            return ""
    
    def set_handdominance(self, val):
        self.handdominance_r_radio.setChecked(val=='R')
        self.handdominance_l_radio.setChecked(val=='L')

    def get_compoundsignstatus(self):
        if self.compoundsign_F_rb.isChecked():
            return 'F'
        elif self.compoundsign_T_rb.isChecked():
            return 'T'
        else:
            return ""
    
    def set_compoundsignstatus(self, val):
        if val is not None:
            self.compoundsign_T_rb.setChecked(val=='T')
            self.compoundsign_F_rb.setChecked(val=='F')


    def get_fingerspelledstatus(self):
        if self.fingerspelled_F_rb.isChecked():
            return 'F'
        elif self.fingerspelled_T_rb.isChecked():
            return 'T'
        else:
            return ""

    def set_fingerspelledstatus(self, val):
        if val is not None:
            self.fingerspelled_T_rb.setChecked(val=='T')
            self.fingerspelled_F_rb.setChecked(val=='F')

    # don't check that gloss is populated
    def get_value(self):
        return {
            'entryid': self.entryid_value.text(),
            'gloss': self.get_glosses(),
            'idgloss': self.get_idgloss(),
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

    def set_value(self, signlevelinfo=None):
        if not signlevelinfo:
            signlevelinfo = self.signlevelinfo
        if self.signlevelinfo:
            # entry id should be a string?
            self.entryid_value.setText(self.entryid_string())
            self.gloss_edit.setText(signlevelinfo.gloss)
            self.idgloss_edit.setText(signlevelinfo.idgloss)
            self.lemma_edit.setText(signlevelinfo.lemma)
            self.source_edit.setText(signlevelinfo.source)
            self.signer_edit.setText(signlevelinfo.signer)
            self.freq_edit.setText(str(signlevelinfo.frequency))
            self.coder_edit.setText(signlevelinfo.coder)
            self.created_display.setText(signlevelinfo.datecreated)
            self.modified_display.setText(signlevelinfo.datelastmodified)
            self.note_edit.setPlainText(signlevelinfo.note if signlevelinfo.note is not None else "")
            self.set_fingerspelledstatus(signlevelinfo.fingerspelled)
            self.set_compoundsignstatus(signlevelinfo.compoundsign)
            self.set_handdominance(signlevelinfo.handdominance)
    
        
    # Overload, because we only allow users to search for a single gloss at a time, 
    # even though the main module allows a list
    def get_glosses(self):
        return self.gloss_edit.text().strip()

    # Remove the wrapper that forces gloss to be populated
    def get_identifiers(self):
        gloss = self.get_glosses()
        lemma = self.get_lemma()
        idgloss = self.get_idgloss()
        return gloss, lemma, idgloss

    
    def restore_defaults(self):
        self.entryid_value.setText("")
        self.entryid_value.setEnabled(True)
        self.gloss_edit.setText("")
        self.gloss_edit.setPlaceholderText("")
        self.idgloss_edit.setText("")
        self.idgloss_edit.setPlaceholderText("")
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

class Search_SigntypeSelectorDialog(SigntypeSelectorDialog):
    def __init__(self, signtypetoload, **kwargs):
        super().__init__(signtypetoload, **kwargs)



class Search_ModuleSelectorDialog(ModuleSelectorDialog):

    def __init__(self, moduletype, xslotstructure=None, xslottype=None, moduletoload=None, linkedfrommoduleid=None, linkedfrommoduletype=None, includephase=0, incl_articulators=HAND, incl_articulator_subopts=0, **kwargs):
        self.xslottype = xslottype
        self.targettype = moduletype
        if self.targettype in [TargetTypes.LOC_REL, TargetTypes.MOV_REL]:
            moduletype = ModuleTypes.LOCATION if moduletype == TargetTypes.LOC_REL else ModuleTypes.MOVEMENT
        self.moduletype = moduletype

        
        super().__init__(moduletype, xslotstructure, moduletoload, linkedfrommoduleid, linkedfrommoduletype, incl_articulators, incl_articulator_subopts, **kwargs)

    def create_associatedrelations_widget(self):
        associatedrelations_widget = Search_AssociatedRelationsPanel(parent=self)
        if self.existingkey is not None:
            associatedrelations_widget.anchormodule = self.mainwindow.current_sign.getmoduledict(self.moduletype)[self.existingkey]
        return associatedrelations_widget
    


    
    def add_button_box(self, new_instance=False):
        buttons = QDialogButtonBox.RestoreDefaults | QDialogButtonBox.Apply | QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons, parent=self)
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
            self.module_widget = Search_LocationSpecPanel(moduletoload=moduletoload, parent=self)
        elif moduletype == ModuleTypes.HANDCONFIG:
            self.module_widget = Search_HandConfigSpecPanel(moduletoload=moduletoload, parent=self)
        elif moduletype == ModuleTypes.RELATION:
            self.module_widget = Search_RelationSpecPanel(moduletoload=moduletoload, parent=self)
            if self.usexslots:
                self.xslot_widget.selection_changed.connect(self.module_widget.timinglinknotification)
                self.xslot_widget.xslotlinkscene.emit_selection_changed()  # to ensure that the initial timing selection is noted
                self.module_widget.timingintervals_inherited.connect(self.xslot_widget.settimingintervals)
            self.module_widget.setvaluesfromanchor(self.linkedfrommoduleid, self.linkedfrommoduletype)
        self.moduleselector_layout.addWidget(self.module_widget)
    
    def handle_xslot_widget(self, xslotstructure, timingintervals):
        self.xslot_widget = None
        self.usexslots = False
        partialxslots = None # if None, xslotlinkingpanel uses value saved in settings
        if self.xslottype.type != XslotTypes.IGNORE:
            self.usexslots = True

            if self.xslottype.type == XslotTypes.ABSTRACT_XSLOT:
                xslotstructure = XslotStructure(1)
            elif self.xslottype.type == XslotTypes.ABSTRACT_WHOLE:
                xslotstructure = XslotStructure(1)
                partialxslots = {}
            elif self.xslottype.type ==  XslotTypes.CONCRETE:
                xslotstructure = XslotStructure(self.xslottype.num, additionalfraction=self.xslottype.frac)
            self.xslot_widget = XslotLinkingPanel(xslotstructure=xslotstructure,
                                                  timingintervals=timingintervals,
                                                  partialxslots=partialxslots,
                                                  parent=self)
            self.moduleselector_layout.addWidget(self.xslot_widget)

    
    def handle_button_click(self, button):
        standard = self.button_box.standardButton(button)

        if standard == QDialogButtonBox.Cancel:
            self.reject()

        elif standard == QDialogButtonBox.Apply:  # save and close
            self.validate_and_save(addanother=False, closedialog=True)

        elif standard == QDialogButtonBox.RestoreDefaults:  # restore defaults
            if self.usearticulators:
                self.articulators_widget.clear()
            self.addedinfobutton.clear()
            if self.usexslots:
                self.xslot_widget.clear()
            self.module_widget.clear()

    def validate_and_save(self, addanother=False, closedialog=False):
        inphase = self.articulators_widget.getphase() if self.usearticulators else 0
        addedinfo = self.addedinfobutton.addedinfo
        phonlocs = self.phonloc_selection.getcurrentphonlocs()
        # validate hand selection
        _, articulators, _ = self.validate_articulators()

        # validate timing interval(s) selection
        timingvalid, timingintervals = self.validate_timingintervals()

        # validate module selections
        modulevalid, modulemessage = self.module_widget.validity_check()


        savedmodule = None
        if modulemessage != "":
            # warn user that there's missing and/or invalid info and don't let them save
            QMessageBox.critical(self, "Warning", modulemessage)
        else:
            # save info
            savedmodule = self.module_widget.getsavedmodule(articulators, timingintervals, phonlocs, addedinfo, inphase)
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
        self.buttonToggled.connect(self.on_button_click)
    
    def on_button_click(self, button):
        if button.isChecked():
            for b in self.buttons():
                b.setChecked(b==button)
        else:
            button.setChecked(False)
    
    def checkedButton(self):
        for b in self.buttons():
            if b.isChecked():
                return b
        return None

# TODO possibly not necessary. can use base classes
class Search_MovementSpecPanel(MovementSpecificationPanel):
    def __init__(self, moduletoload=None, **kwargs):
        super().__init__(moduletoload, **kwargs)

    



class Search_LocationSpecPanel(LocationSpecificationPanel):
    def __init__(self, moduletoload=None, showimagetabs=True, **kwargs):
        super().__init__(moduletoload, showimagetabs, **kwargs)

        self.make_terminal_node_cb()
        if moduletoload is not None and isinstance(moduletoload, LocationModule):
            self.locationoptionsselectionpanel.terminal_node_cb.setChecked(self.getcurrenttreemodel().nodes_are_terminal)
    
    def make_terminal_node_cb(self):
        # used in search window
        self.locationoptionsselectionpanel.terminal_node_cb = QCheckBox("Interpret selections as terminal nodes")
        self.locationoptionsselectionpanel.terminal_node_cb.setEnabled(len(self.locationoptionsselectionpanel.get_listed_paths())>0)
        self.locationoptionsselectionpanel.search_layout.addWidget(self.locationoptionsselectionpanel.terminal_node_cb)
        if self.getcurrenttreemodel().nodes_are_terminal:
            self.locationoptionsselectionpanel.terminal_node_cb.setChecked(True)
        self.locationoptionsselectionpanel.terminal_node_cb.clicked.connect(self.handle_toggle_terminal_node)

    def handle_toggle_terminal_node(self):
        self.getcurrenttreemodel().nodes_are_terminal = self.locationoptionsselectionpanel.terminal_node_cb.isChecked()

    
    def clear(self):
        super().clear()
        self.locationoptionsselectionpanel.terminal_node_cb.setChecked(False)
        self.locationoptionsselectionpanel.terminal_node_cb.setEnabled(False)



class Search_HandConfigSpecPanel(HandConfigSpecificationPanel):
    FINGERS = ["Thumb", "Index", "Middle", "Ring", "Pinky"]
    OPTIONS = {"Extended": 0, "Not extended": 1, "Either": 2}
    
    def __init__(self, moduletoload=None, **kwargs):
        super().__init__(moduletoload, **kwargs)
    
    def clear(self):
        super().clear() # clear hand config search options
        # clear extended finger search options
        
        for b in self.numfingers_grp.buttons():
            b.setChecked(False)
        
        for grp in self.fingerconfiggrps.values():
            grp.button(Search_HandConfigSpecPanel.OPTIONS["Either"]).setChecked(True)
        self.includeIbutton.setChecked(False)
        self.handconfig_rb.setChecked(True)

    def enable_extended_options(self, val):
        for b in self.numfingers_grp.buttons():
            b.setEnabled(val)
        for grp in self.fingerconfiggrps.values():
            for b in grp.buttons():
                b.setEnabled(val)
        self.includeIbutton.setEnabled(val)


    def getsavedmodule(self, articulators, timingintervals, phonlocs, addedinfo, inphase):
        if self.handconfig_rb.isChecked():
            return super().getsavedmodule(articulators, timingintervals, phonlocs, addedinfo, inphase)
        elif self.extendedfinger_rb.isChecked():
            i_extended = self.includeIbutton.isChecked()
            num_extended_selections = {}
            for i in range(6):
                num_extended_selections[i] = self.numfingers_grp.button(i).isChecked()
            finger_selections = {}
            for finger, grp in self.fingerconfiggrps.items():
                finger_selections[finger] = grp.checkedButton().text()
            extfingersmodule = ExtendedFingersModule(i_extended=i_extended,
                                                     finger_selections=finger_selections,
                                                     num_extended_selections=num_extended_selections,
                                                     articulators=articulators,
                                                     timingintervals=timingintervals,
                                                     phonlocs=phonlocs,
                                                     addedinfo=addedinfo)
                
            if self.existingkey is not None:
                extfingersmodule.uniqueid = self.existingkey
            else:
                self.existingkey = extfingersmodule.uniqueid
            return extfingersmodule

    def load_existing_module(self, moduletoload):
        if moduletoload:
            if moduletoload.moduletype == ModuleTypes.HANDCONFIG:
                super().load_existing_module(moduletoload)
                self.handconfig_rb.setChecked(True)
            elif moduletoload.moduletype == TargetTypes.EXTENDEDFINGERS:
                self.extendedfinger_rb.setChecked(True)
                self.includeIbutton.setChecked(moduletoload.i_extended)
                for i in range(6):
                    self.numfingers_grp.button(i).setChecked(moduletoload.num_extended_selections[i])
                for finger, value in moduletoload.finger_selections.items():
                    for b in self.fingerconfiggrps[finger].buttons():
                        b.setChecked(b.text()==value)
                self.existingkey = moduletoload.uniqueid

    def create_layout(self):
        handconfig_box = QGroupBox()
        handconfig_layout = QHBoxLayout()
        handconfig_layout.addWidget(self.panel)
        handconfig_layout.addWidget(self.illustration)
        handconfig_box.setLayout(handconfig_layout)

        extendedfinger_box = QGroupBox()
        extendedfinger_layout = self.make_extended_finger_search_layout()
        extendedfinger_box.setLayout(extendedfinger_layout) 

        self.search_type_grp = QButtonGroup()
        self.handconfig_rb = QRadioButton("Search by hand config")
        self.extendedfinger_rb = QRadioButton("Search by extended fingers")
        self.search_type_grp.addButton(self.handconfig_rb)
        self.search_type_grp.addButton(self.extendedfinger_rb)
        self.search_type_grp.buttonToggled.connect(self.handle_search_type_toggled)
        self.handconfig_rb.setChecked(True)
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.handconfig_rb)
        main_layout.addWidget(handconfig_box)
        main_layout.addWidget(self.extendedfinger_rb)
        main_layout.addWidget(extendedfinger_box)


        return main_layout

    # TODO same for regular config
    def handle_search_type_toggled(self, btn):
        self.enable_extended_options(btn == self.extendedfinger_rb)

    def make_extended_finger_search_layout(self):
        self.includeIbutton = QCheckBox('Treat "i" as extended')
        self.includeIbutton.setChecked(False)

        fingerconfiglayout = self.make_finger_config_layout()
        numfingerslayout = self.make_num_fingers_layout()

        layout = QVBoxLayout()
        layout.addWidget(self.includeIbutton)
        layout.addLayout(fingerconfiglayout)
        layout.addLayout(numfingerslayout)
        return layout

    def make_finger_config_layout(self):
        self.fingerconfiggrps = {}
        fingerconfiglayout = QHBoxLayout()
        for finger in Search_HandConfigSpecPanel.FINGERS:
            group_box = QGroupBox(finger)
            buttonlayout = QVBoxLayout()
            buttongroup = QButtonGroup()
            for option in Search_HandConfigSpecPanel.OPTIONS.keys():
                btn = QRadioButton(option)
                buttongroup.addButton(btn, id=Search_HandConfigSpecPanel.OPTIONS[option])
                buttonlayout.addWidget(btn)
            buttongroup.button(Search_HandConfigSpecPanel.OPTIONS["Either"]).setChecked(True)
            self.fingerconfiggrps[finger] = buttongroup

            group_box.setLayout(buttonlayout)
            fingerconfiglayout.addWidget(group_box)

        return fingerconfiglayout

    def make_num_fingers_layout(self):
        self.numfingers_grp = QButtonGroup()
        self.numfingers_grp.setExclusive(False)

        layout = QVBoxLayout()
        group_box = QGroupBox("Number of extended fingers. (Leave all unchecked for any number of extended fingers.)")
        numlayout = QHBoxLayout()
        for i in range(6):
            btn = QCheckBox(str(i))
            self.numfingers_grp.addButton(btn, id=i)
            numlayout.addWidget(btn)
        group_box.setLayout(numlayout)
        layout.addWidget(group_box)
        return layout

    def validity_check(self):
        selectionsvalid = True
        warningmessage = ""

        # (number of extended fingers) <= 5 - (number of fingers marked "Not extended")
        # (number of extended fingers) >= (number of fingers marked "Extended")
        num_marked_not_extended = sum(grp.button(Search_HandConfigSpecPanel.OPTIONS["Not extended"]).isChecked() for grp in self.fingerconfiggrps.values())
        num_marked_extended = sum(grp.button(Search_HandConfigSpecPanel.OPTIONS["Extended"]).isChecked() for grp in self.fingerconfiggrps.values())
        for i in range(num_marked_extended):
            if self.numfingers_grp.button(i).isChecked():
                warningmessage = f"{i} extended finger(s) not compatible with {num_marked_extended} finger(s) marked extended"
                selectionsvalid = False
                return selectionsvalid, warningmessage
        for i in range(6-num_marked_not_extended, 6):
            if self.numfingers_grp.button(i).isChecked():
                warningmessage = f"{i} extended finger(s) not compatible with {num_marked_not_extended } finger(s) marked not extended"
                selectionsvalid = False
                return selectionsvalid, warningmessage


        return selectionsvalid, warningmessage



class Search_RelationSpecPanel(RelationSpecificationPanel):
    def __init__(self, moduletoload=None, **kwargs):
        super().__init__(moduletoload, **kwargs)
    
    def selections_valid(self):
        # overloaded for validity_check: in Search, we don't need to ensure X and Y selections exist
        return True

    # If an associated relation module is being created, then the linked module box should only show this target's anchor module.
    # If we use the parent class's method, all location or movement search targets in this search file will appear, 
    # since they all belong to the same "current_sign"
    def create_linked_module_box(self):
        self.existingmod_listview = QListView()
        # Check if this is an associated relation module
        curr_row = self.mainwindow.current_row
        target_type = self.mainwindow.searchmodel.target_type(curr_row)

        # Anchor modules are saved before assoc reln modules are added, so target_type will not be none if this is a connected target
        # However, if this is a new Relation target, the target will not have been saved yet, so target_type will be None.
        if target_type not in [ModuleTypes.RELATION, None]:
            anchor_module = self.mainwindow.searchmodel.target_module(curr_row)
            anchor_module_id = self.mainwindow.searchmodel.target_module_id(curr_row)

            self.locmodslist = []
            self.locmodnums = {}
            self.movmodslist = []
            self.movmodnums = {}
            if target_type in [ModuleTypes.LOCATION, TargetTypes.LOC_REL]: 
                self.locmodslist = [anchor_module]
                self.locmodnums[anchor_module_id] = 1
                label = 'Location'
            elif target_type in [ModuleTypes.MOVEMENT, TargetTypes.MOV_REL]:
                self.movmodslist = [anchor_module]
                self.movmodnums[anchor_module_id] = 1
                label = 'Movement'

            self.existingmodule_listmodel = ModuleLinkingListModel()
            self.existingmod_listview.setModel(self.existingmodule_listmodel)

            # disable y options
            for b in self.y_group.buttons():
                b.setChecked(False)
                b.setEnabled(False)
            self.y_existingmod_radio.setEnabled(True)
            self.y_existingmod_switch.freezeOption(label)     
            
        else: 
            super().create_linked_module_box()

    def setcurrentmanner(self, mannerrel):
        if mannerrel is not None and mannerrel.any:
            self.any_manner_cb.setChecked(True)
        else:
            super().setcurrentmanner(mannerrel)

    # return the current contact-manner specification as per the GUI values
    def getcurrentmanner(self):
        reln = super().getcurrentmanner()
        reln.any = self.any_manner_cb.isChecked()
        return reln

    def setcurrentcontacttype(self, contacttype):
        if contacttype is not None and contacttype.any:
            self.any_contacttype_cb.setChecked(True)
        else:
            super().setcurrentcontacttype(contacttype)

    def getcurrentcontacttype(self):
        reln = super().getcurrentcontacttype()
        reln.any = self.any_contacttype_cb.isChecked()
        return reln

    def setcurrentdirection(self, directions_list):
        if directions_list is not None and len(directions_list) == 1: # only the case when "any" was selected
            self.any_direction_cb.setChecked(True)
        else:
            super().setcurrentdirection(directions_list)

    def getcurrentdirections(self):
        if self.any_direction_cb.isChecked():
            return[Direction(axis=None, any=True)]
        else:
            dirs = super().getcurrentdirections()
            for d in dirs:
                d.any = False
            return dirs
        
    def setcurrentdistances(self, distances_list):
        if distances_list is not None and len(distances_list) == 1: # only the case when "any" was selected
            self.any_distance_cb.setChecked(True)
        else:
            super().setcurrentdistances(distances_list)
            # set the parent axis checkbox if distance.any is True
            for d, btn in zip(distances_list, [self.dishor_cb, self.disver_cb, self.dissag_cb, self.disgen_cb]):
                if d.any:
                    btn.setChecked(True)

    def getcurrentdistances(self):
        if self.any_distance_cb.isChecked():
            return[Distance(axis=None, any=True)]
        else:
            dists = super().getcurrentdistances()
            # set distance.any = True if only the parent axis checkbox is selected
            for d, btn in zip(dists, [self.dishor_cb, self.disver_cb, self.dissag_cb, self.disgen_cb]):
                if btn.isChecked() and not d.has_selection():
                    d.any = True
                else:
                    d.any = False
            return dists


    # Differs from mainwindow in that a generic contact type cb is present
    def populate_contacttype_layout(self):
        self.any_contacttype_cb = QCheckBox("Search for any contact type")
        self.any_contacttype_cb.toggled.connect(self.handle_any_contacttype_cb_toggled)

        contacttype_layout = QVBoxLayout()
        contactother_layout = QHBoxLayout()
        contactother_layout.addWidget(self.contactother_rb)
        contactother_layout.addWidget(self.contact_other_text)

        contacttype_layout.addWidget(self.contactlight_rb)
        contacttype_layout.addWidget(self.contactfirm_rb)
        contacttype_layout.addLayout(contactother_layout)
        contacttype_layout.addWidget(self.any_contacttype_cb)
        return contacttype_layout

    # Differs from mainwindow in that a generic contact manner cb is available
    def handle_any_contacttype_cb_toggled(self, btn):
        for b in self.contacttype_group.buttons():
            b.setDisabled(btn)
        self.contact_other_text.setEnabled(not btn and self.contactother_rb.isChecked())
        self.contact_rb.setChecked(btn or self.contacttype_group.checkedButton() is not None) # TODO fix

    def populate_manner_layout(self):
        self.any_manner_cb = QCheckBox("Search for any contact manner")
        self.any_manner_cb.toggled.connect(self.handle_any_manner_cb_clicked)

        manner_layout = QVBoxLayout()
        manner_layout.addWidget(self.holding_rb)
        manner_layout.addWidget(self.continuous_rb)
        manner_layout.addWidget(self.intermittent_rb)
        manner_layout.addWidget(self.any_manner_cb)
        manner_layout.addStretch()
        return manner_layout
    
    def handle_any_manner_cb_clicked(self, btn):
        for b in self.manner_group.buttons():
            b.setDisabled(btn)
        self.contact_rb.setChecked(btn or self.manner_group.checkedButton() is not None)  # TODO fix


    def clear_contact_options(self):
        self.any_contacttype_cb.setChecked(False)
        self.any_contacttype_cb.setEnabled(True)
        self.any_manner_cb.setChecked(False)
        self.any_manner_cb.setEnabled(True)
        super().clear_contact_options()

    # differs from main GUI in that hor, ver, and sag distance checkboxes are available
    # create side-by-side layout for specifying distance
    def create_distance_box(self):
        distance_box = QGroupBox("Distance between X and Y")
            
        # create layout for horizontal distance options
        self.dishor_box = QGroupBox()
        self.dishor_label = QLabel("Horizontal")
        self.dishorclose_rb = DeselectableRadioButton("Close")
        self.dishormed_rb = DeselectableRadioButton("Med.")
        self.dishorfar_rb = DeselectableRadioButton("Far")
        self.dishor_cb = QCheckBox(self.dishor_label.text())
        self.dishor_group = DeselectableRadioButtonGroup()
        self.dishor_group.buttonToggled.connect(self.handle_distancebutton_toggled)
        dis_hor_layout = self.create_axis_layout(self.dishorclose_rb,
                                                 self.dishormed_rb,
                                                 self.dishorfar_rb,
                                                 self.dishor_group,
                                                 axis_cb=self.dishor_cb,
                                                 axis_label=self.dishor_label)
        self.dishor_box.setLayout(dis_hor_layout)
        

        # create layout for vertical distance options
        self.disver_box = QGroupBox()
        self.disver_label = QLabel("Vertical")
        self.disverclose_rb = DeselectableRadioButton("Close")
        self.disvermed_rb = DeselectableRadioButton("Med.")
        self.disverfar_rb = DeselectableRadioButton("Far")
        self.disver_cb = QCheckBox(self.disver_label.text())
        self.disver_group = DeselectableRadioButtonGroup()
        self.disver_group.buttonToggled.connect(self.handle_distancebutton_toggled)
        dis_ver_layout = self.create_axis_layout(self.disverclose_rb,
                                                 self.disvermed_rb,
                                                 self.disverfar_rb,
                                                 self.disver_group,
                                                 axis_cb=self.disver_cb,
                                                 axis_label=self.disver_label)
        self.disver_box.setLayout(dis_ver_layout)
        

        # create layout for sagittal direction options
        self.dissag_box = QGroupBox()
        self.dissag_label = QLabel("Sagittal")
        self.dissagclose_rb = DeselectableRadioButton("Close")
        self.dissagmed_rb = DeselectableRadioButton("Med.")
        self.dissagfar_rb = DeselectableRadioButton("Far")
        self.dissag_cb = QCheckBox(self.dissag_label.text())
        self.dissag_group = DeselectableRadioButtonGroup()
        self.dissag_group.buttonToggled.connect(self.handle_distancebutton_toggled)
        dis_sag_layout = self.create_axis_layout(self.dissagclose_rb,
                                                 self.dissagmed_rb,
                                                 self.dissagfar_rb,
                                                 self.dissag_group,
                                                 axis_cb=self.dissag_cb,
                                                 axis_label=self.dissag_label)
        self.dissag_box.setLayout(dis_sag_layout)
            
        # create layout for generic distance options
        self.disgen_box = QGroupBox()
        self.disgen_label = QLabel("Generic")
        self.disgenclose_rb = DeselectableRadioButton("Close")
        self.disgenmed_rb = DeselectableRadioButton("Med.")
        self.disgenfar_rb = DeselectableRadioButton("Far")
        self.disgen_cb = QCheckBox(self.disgen_label.text())
        self.disgen_group = DeselectableRadioButtonGroup()
        self.disgen_group.buttonToggled.connect(self.handle_distancebutton_toggled)
        dis_gen_layout = self.create_axis_layout(self.disgenclose_rb,
                                                 self.disgenmed_rb,
                                                 self.disgenfar_rb,
                                                 self.disgen_group,
                                                 axis_cb=self.disgen_cb,
                                                 axis_label=self.disgen_label)
        self.disgen_box.setLayout(dis_gen_layout)

        distance_box.setLayout(self.populate_distance_layout())
        return distance_box

    # create layout for distance or direction options on a particular axis
    def create_axis_layout(self, radio1, radio2, radio3, radiogroup, axis_cb, axis_label=None):
        axis_layout = QVBoxLayout()
        axisoptions_spacedlayout = QHBoxLayout()
        axisoptions_layout = QVBoxLayout()
        radiogroup.addButton(radio1)
        radiogroup.addButton(radio2)
        radiogroup.addButton(radio3)
        if axis_label is not None:
            # then we are setting up direction rather than distance
            radiogroup.buttonToggled.connect(lambda ischecked: self.handle_directiongroup_toggled(ischecked, axis_cb))
            axis_cb.toggled.connect(lambda ischecked: self.handle_directioncb_toggled(ischecked, radiogroup))
            axis_layout.addWidget(axis_cb)
        else:
            # Set up checkboxes for distance as well, since we want to be able to search for them
            radiogroup.buttonToggled.connect(lambda ischecked: self.handle_distancegroup_toggled(ischecked, axis_cb))
            axis_cb.toggled.connect(lambda ischecked: self.handle_distancecb_toggled(ischecked, radiogroup))
            axis_layout.addWidget(axis_cb)
        axisoptions_spacedlayout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        axisoptions_layout.addWidget(radio1)
        axisoptions_layout.addWidget(radio2)
        axisoptions_layout.addWidget(radio3)
        axisoptions_spacedlayout.addLayout(axisoptions_layout)
        axis_layout.addLayout(axisoptions_spacedlayout)

        return axis_layout

    def populate_direction_layout(self, direction_crossedlinked_layout, direction_sublayout):
        self.any_direction_cb = QCheckBox("Search for any direction of relation")
        self.any_direction_cb.toggled.connect(self.handle_any_direction_cb_toggled)

        direction_layout = QVBoxLayout()
        direction_layout.addLayout(direction_crossedlinked_layout)
        direction_layout.addLayout(direction_sublayout)
        direction_layout.addWidget(self.any_direction_cb)
        
        return direction_layout
    
    # if user checks one of the distance axis radio buttons, ensure that its parent checkbox is also checked
    # Only exists in search GUI, since parent checkboxes are not present in main GUI
    def handle_distancegroup_toggled(self, ischecked, axis_cb):
        if not ischecked:
            # don't need to do anything special
            return

        # ensure the parent is checked
        axis_cb.setChecked(True)

    def handle_distancecb_toggled(self, ischecked, radiogroup):
        self.nocontact_rb.setChecked(ischecked or radiogroup.checkedButton() is not None) # todo fix
        for btn in radiogroup.buttons():
            btn.setEnabled(ischecked or radiogroup.checkedButton() is None)

    
    def handle_any_direction_cb_toggled(self, btn):
        for b in self.dirhor_group.buttons() + self.dirsag_group.buttons() + self.dirver_group.buttons():
            b.setDisabled(btn)
        for b in [self.dirsag_cb, self.dirhor_cb, self.dirver_cb, self.crossed_cb, self.linked_cb]:
            b.setDisabled(btn)

    def populate_distance_layout(self):
        self.any_distance_cb = QCheckBox("Search for any distance between X and Y")
        self.any_distance_cb.toggled.connect(self.handle_any_distance_cb_toggled)

        layout = QVBoxLayout()
        distance_layout = QHBoxLayout()
        distance_layout.addWidget(self.dishor_box)
        distance_layout.addWidget(self.disver_box)
        distance_layout.addWidget(self.dissag_box)
        distance_layout.addWidget(self.disgen_box)

        layout.addLayout(distance_layout)
        layout.addWidget(self.any_distance_cb)

        return layout
    
    def handle_any_distance_cb_toggled(self, btn):
        distancegrp = self.dishor_group.buttons() + self.dissag_group.buttons() + self.disver_group.buttons() + self.disgen_group.buttons() + [self.dissag_cb, self.dishor_cb, self.disver_cb, self.disgen_cb]
        hascheckedbtn = False
        for b in distancegrp:
            b.setDisabled(btn)
            if b.isChecked():
                hascheckedbtn = True
        self.nocontact_rb.setChecked(btn or hascheckedbtn) # TODO fix

    def clear_direction_buttons(self):
        super().clear_direction_buttons()
        for b in [self.any_direction_cb, self.dirhor_cb, self.dirver_cb, self.dirsag_cb]:
            b.setChecked(False)
            b.setEnabled(True)

    def clear_distance_buttons(self):
        super().clear_distance_buttons()
        for b in [self.any_distance_cb, self.dishor_cb, self.disver_cb, self.dissag_cb, self.disgen_cb]:
            b.setChecked(False)
            b.setEnabled(True)
    



    # 1. The 'distance' section is only available if 'no contact' is selected
    # 2. OR Can also be available if
    #   (a) neither 'contact' nor 'no contact' is selected AND
    #   (b) there are no selections in manner or distance
    # 3. BUT if 'movement' is selected for Y,
    #   then Contact, Manner, Direction, and Distance menus are all inactive below
    def check_enable_distance(self):
        meetscondition1 = self.nocontact_rb.isChecked()

        meetscondition2 = self.contactmannerdistance_empty()

        meetscondition3 = self.y_existingmod_radio.isChecked() and \
                          self.getcurrentlinkedmoduletype() == ModuleTypes.MOVEMENT

        enable_distance = (meetscondition1 or meetscondition2) and not meetscondition3
        for box in [self.dishor_box, self.disver_box, self.dissag_box, self.disgen_box]:
            box.setEnabled(enable_distance)
        self.any_distance_cb.setEnabled(enable_distance)

    # if 'movement' is selected for Y,
    #  then Contact, Manner, Direction (including crossed/linked), and Distance menus are all inactive below
    def check_enable_direction(self):
        enable_direction = not (self.y_existingmod_radio.isChecked() and
                                self.getcurrentlinkedmoduletype() == ModuleTypes.MOVEMENT)
        for box in [self.dirhor_box, self.dirver_box, self.dirsag_box]:
            box.setEnabled(enable_direction)
        self.crossed_cb.setEnabled(enable_direction)
        self.linked_cb.setEnabled(enable_direction)
        self.any_direction_cb.setEnabled(enable_direction)

    def handle_contactgroup_toggled(self, btn, checked):
        # if the user has selected and deselected a contact option, then...
        #   if no subsidiary choices (eg in distance or manner) were made, then leave those subsections available
        #   else if one or more subsidiary choices were made, then (as per default behaviour)
        #       both of those subsections should be disabled

        # make sure contact type options are un/available as applicable
        for b in self.contacttype_group.buttons():
            b.setEnabled(not self.nocontact_rb.isChecked())

            self.contacttype_group.setExclusive(False)
            if not self.contact_rb.isChecked() and not self.nocontact_rb.isChecked():
                b.setChecked(False)
            self.contacttype_group.setExclusive(True)

        self.contact_other_text.setEnabled(not self.nocontact_rb.isChecked())
        self.any_contacttype_cb.setEnabled(not self.nocontact_rb.isChecked())

        # check whether submenus (contact, manner, direction, distance) should be enabled
        self.check_enable_allsubmenus()

class Search_AssociatedRelationsDialog(AssociatedRelationsDialog):
    def __init__(self, anchormodule=None, **kwargs):
        super().__init__(anchormodule, **kwargs)




    def handle_relationmod_clicked(self, relmod):

        module_selector = Search_ModuleSelectorDialog(moduletype=ModuleTypes.RELATION,
                                               xslotstructure=self.mainwindow.current_sign.xslotstructure,
                                               xslottype=self.mainwindow.current_sign.xslottype,
                                               moduletoload=relmod,
                                               incl_articulators=[],
                                               incl_articulator_subopts=0,
                                               parent=self)
        module_selector.module_saved.connect(self.module_saved.emit)
        # module_selector.module_deleted.connect(lambda: self.handle_moduledeleted(relmod.uniqueid))
        module_selector.module_deleted.connect(lambda: self.mainwindow.signlevel_panel.handle_delete_module(
            existingkey=relmod.uniqueid, moduletype=ModuleTypes.RELATION))
        module_selector.exec_()
        self.refresh_listmodel()
        



class Search_AssociatedRelationsPanel(AssociatedRelationsPanel):
    def __init__(self, anchormodule=None, **kwargs):
        super().__init__(anchormodule, **kwargs)

    def handle_see_relationmodules(self):
        associatedrelations_dialog = Search_AssociatedRelationsDialog(anchormodule=self.anchormodule, parent=self)
        associatedrelations_dialog.module_saved.connect(self.module_saved.emit)
        associatedrelations_dialog.exec_()
        self.style_seeassociatedrelations()  # in case one/some were deleted and there are none left now


    def check_enable_saveaddrelation(self, hastiming=None, hasarticulators=None, bodyloc=None):
        enable_addrelation = True

        # if hastiming is None and hasarticulators is None and bodyloc is None:
        #     enable_addrelation = False

        # # only use arguments if they have a boolean value (ie, are not None)
        # if hastiming is not None:
        #     # make sure the anchor has a valid timing selection
        #     enable_addrelation = enable_addrelation and hastiming
            # timingvalid, timingintervals = self.parent().validate_timingintervals()
        if bodyloc is not None:
            # make sure the anchor is not a purely spatial location
            enable_addrelation = enable_addrelation and bodyloc
        # if hasarticulators is not None:
        #     # make sure the anchor has a valid hand(s) selection
        #     enable_addrelation = enable_addrelation and hasarticulators

        self.addrelation_button.setEnabled(enable_addrelation)

    def handle_save_add_relationmodule(self):
        # save the current anchor module before trying to link a relation module to it
        self.save_anchor.emit()
        if self.anchormodule is not None:  # the save above was successful; continue

            module_selector = Search_ModuleSelectorDialog(moduletype=ModuleTypes.RELATION,
                                                   xslotstructure=self.mainwindow.current_sign.xslotstructure,
                                                   xslottype=self.mainwindow.current_sign.xslottype,
                                                   moduletoload=None,
                                                   linkedfrommoduleid=self.anchormodule.uniqueid,
                                                   linkedfrommoduletype=self.parent().moduletype,
                                                   incl_articulators=[],
                                                   incl_articulator_subopts=0,
                                                   parent=self)
            # module_selector.module_saved.connect(lambda module_to_save:
            #                                      self.mainwindow.build_search_target_view.handle_add_associated_relation_module(
            #                                          self.anchormodule, module_to_save
            #                                      ))
            module_selector.module_saved.connect(lambda module_to_save: self.handle_modulesaved(module_to_save=module_to_save))
            module_selector.exec_()

    def handle_modulesaved(self, module_to_save):
        
        self.mainwindow.build_search_target_view.handle_add_associated_relation_module(self.anchormodule, module_to_save)
        self.style_seeassociatedrelations()


class XslotTypeItem:
    def __init__(self, type=None, num=None, frac=None):
        self.type = type
        self.num = num
        self.frac = frac
        if self.type == XslotTypes.CONCRETE and frac==None:
            self.frac = 0
        else:
            self.frac = frac
    
    def __repr__(self):
        if self.type in [XslotTypes.IGNORE, XslotTypes.ABSTRACT_XSLOT, XslotTypes.ABSTRACT_WHOLE]:
            return self.type
        elif self.type == XslotTypes.CONCRETE:
            to_ret = self.type + ": " 
            num_to_display = str(self.num)
            if self.frac not in [None, 0]:
                num_to_display += " + " + str(self.frac)
            num_to_display += " xslots"
            return to_ret + num_to_display
        else:
            return "non implemented xslottype"
        # if t.xslottype is not None: # TODO specify exactly which target types should have an xslottype or not
        #     if t.xslottype == "concrete":
        #         xslotval = t.xslotnum
        #         xslottype = QStandardItem(xslotval + " x-slots")
        #     else:
        #         xslottype = QStandardItem(t.xslottype)
        #     xslottype.setData((t.xslottype, t.xslotnum), Qt.UserRole)
        # else:
        #     xslottype = QStandardItem('ignore') # TODO fix how nonetype is handled
        #     xslottype.setData(('ignore', t.xslotnum), Qt.UserRole)
        




# TODO move the methods above into here?
class SearchTargetItem(QStandardItem):
    def __init__(self, name=None, targettype=None, xslottype=None, searchvaluesitem=None, module=None, module_id = None, negative=False, include=False, associatedrelnmodule=None, associatedrelnmodule_id = None, **kwargs):
        super().__init__(**kwargs)
        self._name = name
        self._targettype = targettype
        self._xslottype = xslottype 
        self._searchvaluesitem = searchvaluesitem
        self._module = module
        self.module_id = module_id
        self._associatedrelnmodule = associatedrelnmodule
        self.associatedrelnmodule_id = associatedrelnmodule_id
        self.negative = negative
        self.include = include

    def __repr__(self):
        msg =  "Name: " + str(self.name) + "\nxslottype: " + str(self.xslottype) + "\ntargettype " + str(self.targettype)  
        msg += "\nValues: " + repr(self.values)
        return msg
    
    @property
    def targettype(self):
        return self._targettype

    @targettype.setter
    def targettype(self, value):
        self._targettype = value

    @property
    def searchvaluesitem(self):
        return self._searchvaluesitem

    @searchvaluesitem.setter
    def searchvaluesitem(self, v):
        self._searchvaluesitem = v
    
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def xslottype(self):
        return self._xslottype

    @xslottype.setter
    def xslottype(self, value):
        self._xslottype = value

    @property
    def module(self):
        return self._module
    
    @module.setter
    def module(self, m):
        self._module = m

    @property
    def associatedrelnmodule(self):
        return self._associatedrelnmodule
    
    @associatedrelnmodule.setter
    def associatedrelnmodule(self, m):
        self._associatedrelnmodule = m

    def displaystring(self):
        if self.targettype in [ModuleTypes.MOVEMENT, ModuleTypes.LOCATION, ModuleTypes.RELATION, ModuleTypes.HANDCONFIG, TargetTypes.SIGNTYPEINFO]:
            return(self.module.getabbreviation())
        elif self.targettype in [TargetTypes.LOC_REL, TargetTypes.MOV_REL]:
            moduletype = ModuleTypes.MOVEMENT if self.targettype == TargetTypes.MOV_REL else ModuleTypes.LOCATION
            moduleabbrev = self.module.getabbreviation()
            relationabbrev = self.associatedrelnmodule.getabbreviation()
            return relationabbrev.replace(f"linked {moduletype} module", moduleabbrev)
            
        else:
            return f"non-implemented {self.targettype}"