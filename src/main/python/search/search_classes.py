
import logging
# from gui.hand_configuration import ConfigGlobal, Config
from gui.signtypespecification_view import SigntypeSelectorDialog
from gui.signlevelinfospecification_view import SignlevelinfoSelectorDialog, SignLevelInfoPanel
from gui.helper_widget import CollapsibleSection, ToggleSwitch
# from gui.decorator import check_date_format, check_empty_gloss
from constant import DEFAULT_LOCATION_POINTS, HAND, ARM, LEG, ARTICULATOR_ABBREVS
from gui.xslotspecification_view import XslotSelectorDialog, XslotStructure
from lexicon.module_classes import TimingPoint, TimingInterval, ModuleTypes, LocationModule
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
    QMessageBox,
    QSpacerItem,
    QSizePolicy
)

from gui.movementspecification_view import MovementSpecificationPanel
from gui.locationspecification_view import LocationSpecificationPanel
from gui.handconfigspecification_view import HandConfigSpecificationPanel
from gui.relationspecification_view import RelationSpecificationPanel
from gui.modulespecification_dialog import XslotLinkingPanel, XslotLinkScene
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
        super().__init__(moduletype, xslotstructure, moduletoload, linkedfrommoduleid, linkedfrommoduletype, incl_articulators, incl_articulator_subopts, **kwargs)


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
            QMessageBox.critical(self, "Warning", "hand config not impl")
        elif self.moduletype == ModuleTypes.RELATION:
            self.module_widget = Search_RelationSpecPanel(moduletoload=moduletoload, parent=self)
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

        messagestring = ""

        savedmodule = None
        if messagestring != "":
            # warn user that there's missing and/or invalid info and don't let them save
            QMessageBox.critical(self, "Warning", messagestring)
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
        self.buttonClicked.connect(self.on_button_click)
    
    def on_button_click(self, button):
        if button.isChecked():
            for b in self.buttons():
                b.setChecked(b==button)
        else:
            button.setChecked(False)

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
    def __init__(self, moduletoload=None, **kwargs):
        super().__init__(moduletoload, **kwargs)

class Search_RelationSpecPanel(RelationSpecificationPanel):
    def __init__(self, moduletoload=None, **kwargs):
        super().__init__(moduletoload, **kwargs)

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
        # TODO this doesnt work the first time contacttype_rb is clicked, why?
        for b in self.contacttype_group.buttons():
            b.setDisabled(btn)
        self.contact_other_text.setEnabled(not btn and self.contactother_rb.isChecked())
        # self.contact_rb.setChecked(btn or self.contacttype_group.checkedButton() is not None) # this also doesnt work

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


    def clear_contact_options(self):
        self.any_contacttype_cb.setChecked(False)
        self.any_contacttype_cb.setEnabled(True)
        self.any_manner_cb.setChecked(False)
        self.any_manner_cb.setEnabled(True)
        super().clear_contact_options()


    # create layout for distance or direction options on a particular axis
    def create_axis_layout(self, radio1, radio2, radio3, radiogroup, axis_cb=None, axis_label=None):
        axis_layout = QVBoxLayout()
        axisoptions_spacedlayout = QHBoxLayout()
        axisoptions_layout = QVBoxLayout()
        radiogroup.addButton(radio1)
        radiogroup.addButton(radio2)
        radiogroup.addButton(radio3)
        if axis_cb is not None:
            # then we are setting up direction rather than distance
            radiogroup.buttonToggled.connect(lambda rb, ischecked: self.handle_directiongroup_toggled(ischecked, axis_cb))
            axis_cb.toggled.connect(lambda ischecked: self.handle_directioncb_toggled(ischecked, radiogroup))
            axis_layout.addWidget(axis_cb)
        elif axis_label is not None:
            # Set up checkboxes for distance as well, since we want to be able to search for them
            axis_cb = QCheckBox(axis_label.text())
            axis_cb.toggled.connect(lambda ischecked: self.handle_distancecb_toggled(ischecked, radiogroup))
            axis_layout.addWidget(axis_cb)
        axisoptions_spacedlayout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        axisoptions_layout.addWidget(radio1)
        axisoptions_layout.addWidget(radio2)
        axisoptions_layout.addWidget(radio3)
        axisoptions_spacedlayout.addLayout(axisoptions_layout)
        axis_layout.addLayout(axisoptions_spacedlayout)

        return axis_layout
    
    def handle_distancecb_toggled(ischecked, radiogroup):
        pass

    def populate_direction_layout(self, direction_crossedlinked_layout, direction_sublayout):
        self.any_direction_cb = QCheckBox("Search for any direction of relation")
        self.any_direction_cb.toggled.connect(self.handle_any_direction_cb_toggled)

        direction_layout = QVBoxLayout()
        direction_layout.addLayout(direction_crossedlinked_layout)
        direction_layout.addLayout(direction_sublayout)
        direction_layout.addWidget(self.any_direction_cb)
        
        return direction_layout
    
    def handle_any_direction_cb_toggled(self, btn):
        pass

    def populate_distance_layout(self):
        self.any_distance_cb = QCheckBox("Search for any distance between X and Y")
        self.any_distance_cb.toggled.connect(self.handle_any_distance_cb_toggled)

        layout = QVBoxLayout()
        distance_layout = QHBoxLayout()
        distance_layout.addWidget(self.dishor_box)
        distance_layout.addWidget(self.disver_box)
        distance_layout.addWidget(self.dissag_box)

        layout.addLayout(distance_layout)
        layout.addWidget(self.any_distance_cb)

        return layout
    
    def handle_any_distance_cb_toggled(self, btn):
        for b in self.dishor_group.buttons() + self.dissag_group.buttons() + self.disver_group.buttons():
            b.setDisabled(btn)
    

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
        



