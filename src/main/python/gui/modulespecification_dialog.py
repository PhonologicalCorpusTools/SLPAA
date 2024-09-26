from copy import deepcopy

from PyQt5.QtWidgets import (
    QFrame,
    QRadioButton,
    QDialog,
    QWidget,
    QSpacerItem,
    QSizePolicy,
    QHBoxLayout,
    QVBoxLayout,
    QMessageBox,
    QDialogButtonBox,
    QLabel,
    QButtonGroup,
    QCheckBox,
    QGraphicsView,
    QListView,
    QAbstractItemView,
    QPushButton
)

from PyQt5.QtCore import (
    Qt,
    pyqtSignal
)

from gui.xslot_graphics import XslotLinkScene
from lexicon.module_classes import AddedInfo, TimingInterval, TimingPoint, ParameterModule, ModuleTypes, LocationModule, MovementModule
from models.relation_models import ModuleLinkingListModel
from gui.movementspecification_view import MovementSpecificationPanel
from gui.locationspecification_view import LocationSpecificationPanel
from gui.handconfigspecification_view import HandConfigSpecificationPanel
from gui.relationspecification_view import RelationSpecificationPanel
from gui.orientationspecification_view import OrientationSpecificationPanel
from gui.nonmanualspecification_view import NonManualSpecificationPanel
from gui.modulespecification_widgets import AddedInfoPushButton, ArticulatorSelector, PhonLocSelection
from gui.link_help import show_help
from constant import SIGN_TYPE, HAND, ARM, LEG


class ModuleSelectorDialog(QDialog):
    # The second param for module_saved is from ModuleTypes.xxxx and will often be of
    # the same type that this module selector dialog is for.
    # HOWEVER, it's possible that the module being saved is of a different type than the primary module selector dialog
    # (ie, an associated relation module spawned from a movement or location module dialog).
    module_saved = pyqtSignal(ParameterModule, str)
    module_deleted = pyqtSignal()

    def __init__(self, moduletype, xslotstructure=None, moduletoload=None, linkedfrommoduleid=None, linkedfrommoduletype=None, incl_articulators=HAND, incl_articulator_subopts=0, **kwargs):
        super().__init__(**kwargs)
        self.mainwindow = self.parent().mainwindow
        self.moduletype = moduletype
        self.usearticulators = len(incl_articulators) > 0
        self.linkedfrommoduleid = linkedfrommoduleid
        self.linkedfrommoduletype = linkedfrommoduletype
        self.existingkey = None
        self.signtype_specslist = {}

        self.loaded_timingintervals = []
        addedinfo = AddedInfo()
        phonlocstoload = None
        new_instance = True
        articulators = (None, {1: None, 2: None})
        inphase = 0
        if isinstance(incl_articulators, str):
            incl_articulators = [incl_articulators]

        if HAND in incl_articulators and self.parent().sign.signtype:
            # set default articulators
            self.signtype_specslist = { art_setting[0] for art_setting in self.parent().sign.signtype.specslist } 
            if SIGN_TYPE["ONE_HAND"] in self.signtype_specslist and \
             (SIGN_TYPE["ONE_HAND_NO_MVMT"] not in self.signtype_specslist or self.moduletype != ModuleTypes.MOVEMENT):
                articulators = (HAND, {1: True, 2: False})
            elif self.moduletype == ModuleTypes.MOVEMENT:
                if SIGN_TYPE["TWO_HANDS_ONLY_H1"] in self.signtype_specslist:
                    articulators = (HAND, {1: True, 2: False})
                elif SIGN_TYPE["TWO_HANDS_ONLY_H2"] in self.signtype_specslist:
                    articulators = (HAND, {1: False, 2: True})
        if moduletoload is not None:
            self.existingkey = moduletoload.uniqueid
            self.loaded_timingintervals = deepcopy(moduletoload.timingintervals)
            addedinfo = deepcopy(moduletoload.addedinfo)
            phonlocstoload = moduletoload.phonlocs
            if moduletoload.articulators is not None:
                articulators = moduletoload.articulators
            
            new_instance = False
            if isinstance(moduletoload, LocationModule) or isinstance(moduletoload, MovementModule):
                inphase = moduletoload.inphase

        self.main_layout = QVBoxLayout()

        self.arts_and_addedinfo_layout = QHBoxLayout()
        self.articulators_widget = None
        if self.usearticulators:
            self.articulators_widget = ArticulatorSelectionPanel(available_articulators=incl_articulators,
                                                                 articulators=articulators,
                                                                 incl_articulator_subopts=incl_articulator_subopts,
                                                                 inphase=inphase,
                                                                 parent=self)
            self.arts_and_addedinfo_layout.addWidget(self.articulators_widget)

        self.phonloc_selection= PhonLocSelection(self.moduletype == ModuleTypes.LOCATION)
        if phonlocstoload is not None:
            self.phonloc_selection.set_phonloc_buttons_from_content(phonlocstoload)
        self.arts_and_addedinfo_layout.addWidget(self.phonloc_selection)
        self.arts_and_addedinfo_layout.addStretch()
        self.addedinfobutton = AddedInfoPushButton("Module notes")
        self.addedinfobutton.addedinfo = addedinfo
        self.arts_and_addedinfo_layout.addWidget(self.addedinfobutton)
        self.arts_and_addedinfo_layout.setAlignment(self.addedinfobutton, Qt.AlignTop)

        self.main_layout.addLayout(self.arts_and_addedinfo_layout)
        self.arts_and_addedinfo_layout.minimumSize()

        self.handle_xslot_widget(xslotstructure, self.loaded_timingintervals)

        self.module_widget = QWidget()
        self.assign_module_widget(moduletype, moduletoload)
        self.main_layout.addWidget(self.module_widget)

        self.handle_articulator_changed(articulators[0])
        if self.usearticulators:
            self.articulators_widget.articulatorchanged.connect(self.handle_articulator_changed)

        if self.moduletype in [ModuleTypes.MOVEMENT, ModuleTypes.LOCATION]:
            self.associatedrelations_widget = AssociatedRelationsPanel(parent=self)
            if self.existingkey is not None:
                self.associatedrelations_widget.anchormodule = self.mainwindow.current_sign.getmoduledict(self.moduletype)[self.existingkey]
            self.check_enable_saveaddrelation()

            self.associatedrelations_widget.save_anchor.connect(self.handle_save_anchor)
            self.associatedrelations_widget.module_saved.connect(self.handle_modulesaved)
            if self.usexslots:
                self.xslot_widget.selection_changed.connect(self.check_enable_saveaddrelation)
            if self.usearticulators:
                self.articulators_widget.articulator_group.buttonClicked.connect(self.check_enable_saveaddrelation)
            if self.moduletype == ModuleTypes.LOCATION:
                self.module_widget.loctype_subgroup.buttonClicked.connect(self.check_enable_saveaddrelation)
                self.module_widget.signingspace_subgroup.buttonClicked.connect(self.check_enable_saveaddrelation)

            self.main_layout.addWidget(self.associatedrelations_widget)

        separate_line = QFrame()
        separate_line.setFrameShape(QFrame.HLine)
        separate_line.setFrameShadow(QFrame.Sunken)
        self.main_layout.addWidget(separate_line)

        self.add_button_box(new_instance)

        self.setLayout(self.main_layout)
        # self.setMinimumSize(QSize(500, 700))
        # # self.setMinimumSize(modulelayout.desiredwidth(), modulelayout.desiredheight())
        # self.setMinimumSize(QSize(modulelayout.rect().width(), modulelayout.rect().height()))
        # self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.adjustSize()

        # get first rendered widget heights and fix them.
        if self.usearticulators:
            self.articulators_widget.setFixedHeight(self.articulators_widget.sizeHint().height())
        if self.usexslots:
            self.xslot_widget.setFixedHeight(self.xslot_widget.sizeHint().height())

    def add_button_box(self, new_instance):
        # If we're creating a brand new instance of a module, then we want a
        #   "Save and Add Another" button, to allow the user to continue adding new instances.
        # On the other hand, if we're editing an existing instance of a module, then instead we want a
        #   "Delete" button, in case the user wants to delete the instance rather than editing it.

        # initialize button_box
        self.button_box = QDialogButtonBox(parent=self)

        # buttons to be added to buttons_box. existing instance as the default
        buttons = [
            QDialogButtonBox.RestoreDefaults,
            QDialogButtonBox.Help,
            QDialogButtonBox.Discard,
            QDialogButtonBox.Apply,
            QDialogButtonBox.Cancel
            ]
        applytext = "Save"

        # ... and minimal changes if new_instance
        if new_instance:
            buttons[2] = QDialogButtonBox.Save
            applytext += " and close"

        [self.button_box.addButton(btn) for btn in buttons]  # populate self.button_box
        self.button_box.button(QDialogButtonBox.Apply).setDefault(True)  # set 'apply' as default

        # change button text
        self.button_box.button(QDialogButtonBox.Apply).setText(applytext)

        if self.button_box.button(QDialogButtonBox.Discard):
            self.button_box.button(QDialogButtonBox.Discard).setText("Delete")
        else:
            self.button_box.button(QDialogButtonBox.Save).setText("Save and add another")

        # TODO KV keep? from orig locationdefinerdialog:
        #      Ref: https://programtalk.com/vs2/python/654/enki/enki/core/workspace.py/
        self.button_box.clicked.connect(self.handle_button_click)

        self.main_layout.addWidget(self.button_box)


    def assign_module_widget(self, moduletype, moduletoload):
        if moduletype == ModuleTypes.MOVEMENT:
            self.module_widget = MovementSpecificationPanel(moduletoload=moduletoload, parent=self)
        elif moduletype == ModuleTypes.LOCATION:
            self.module_widget = LocationSpecificationPanel(moduletoload=moduletoload, parent=self)
        elif moduletype == ModuleTypes.HANDCONFIG:
            self.module_widget = HandConfigSpecificationPanel(moduletoload=moduletoload, parent=self)
        elif self.moduletype == ModuleTypes.RELATION:
            self.module_widget = RelationSpecificationPanel(moduletoload=moduletoload, parent=self)
            if self.usexslots:
                self.xslot_widget.selection_changed.connect(self.module_widget.timinglinknotification)
                self.xslot_widget.xslotlinkscene.emit_selection_changed()  # to ensure that the initial timing selection is noted
                self.module_widget.timingintervals_inherited.connect(self.xslot_widget.settimingintervals)
            self.module_widget.setvaluesfromanchor(self.linkedfrommoduleid, self.linkedfrommoduletype)
        elif self.moduletype == ModuleTypes.NONMANUAL:
            self.module_widget = NonManualSpecificationPanel(moduletoload=moduletoload, parent=self)
        elif self.moduletype == ModuleTypes.ORIENTATION:
            self.module_widget = OrientationSpecificationPanel(moduletoload=moduletoload, parent=self)

        
    def handle_xslot_widget(self, xslotstructure, timingintervals):
        self.xslot_widget = None
        self.usexslots = False
        if self.mainwindow.app_settings['signdefaults']['xslot_generation'] != 'none':
            self.usexslots = True
            self.xslot_widget = XslotLinkingPanel(xslotstructure=xslotstructure,
                                                  timingintervals=timingintervals,
                                                  parent=self)
            self.main_layout.addWidget(self.xslot_widget)

    
    def handle_modulesaved(self, relationtosave, moduletype):
        self.module_saved.emit(relationtosave, moduletype)
        self.style_seeassociatedrelations()

    def check_enable_saveaddrelation(self):
        hastiming = self.validate_timingintervals()[0]
        hasarticulators = self.validate_articulators()[0]
        bodyloc = (
            self.module_widget.getcurrentlocationtype().usesbodylocations() if self.moduletype == ModuleTypes.LOCATION else None)
        self.associatedrelations_widget.check_enable_saveaddrelation(hastiming, hasarticulators, bodyloc)

    def style_seeassociatedrelations(self):
        self.associatedrelations_widget.style_seeassociatedrelations()

    def handle_save_anchor(self):
        savedmodule = self.validate_and_save(addanother=False, closedialog=False)
        self.associatedrelations_widget.anchormodule = savedmodule

    def handle_articulator_changed(self, articulator):
        if articulator is not None:
            self.module_widget.handle_articulator_changed(articulator)

    # validate timing interval(s) selection (all modules must be linked to at least one timing point or interval)
    def validate_timingintervals(self):
        if self.usexslots:
            timingintervals = self.xslot_widget.gettimingintervals()
            timingvalid = len(timingintervals) != 0
        elif len(self.loaded_timingintervals) > 0:
            # we're currently in "no x-slots" mode BUT we've loaded a previously-existing module that was
            #   created when x-slots *were* being used... so preserve the existing timing information in
            #   case the user wants to return to x-slots mode
            timingintervals = self.loaded_timingintervals
            timingvalid = True
        else:
            # no x-slots; make the timing interval be for the whole sign
            timingintervals = [TimingInterval(TimingPoint(0, 0), TimingPoint(0, 1))]
            timingvalid = True

        return timingvalid, timingintervals

    # validate articulator selection (all modules except relation must have at least one articulator selected)
    def validate_articulators(self):
        def calculate_selected_hand(articulator_dict):
                if articulator_dict[1] and not articulator_dict[2]:
                    return "H1"
                elif not articulator_dict[1] and articulator_dict[2]:
                    return "H2"
                elif articulator_dict[1] and articulator_dict[2]:
                    return "both hands"
                else:
                    "no articulator"
                    
        if self.usearticulators:
            articulator, articulator_dict = self.articulators_widget.getarticulators()
            articulatorsvalid = not articulator is None and True in articulator_dict.values()
        else:
            articulator = ""  # otherwise "Hand", "Arm", or "Leg"
            articulator_dict = {1: False, 2: False}  # as if no articulators are selected
            articulatorsvalid = True

        warning_msg = ""
        if articulator == HAND:
            both_hands_selected = articulator_dict[1] and articulator_dict[2]
            if SIGN_TYPE["ONE_HAND"] in self.signtype_specslist and both_hands_selected:
                warning_msg = "The sign type for this sign is 1-handed. Are you sure this module should apply to both hands?"
            elif self.moduletype == ModuleTypes.MOVEMENT:
                if SIGN_TYPE["ONE_HAND_NO_MVMT"] in self.signtype_specslist:
                    warning_msg = "The sign type for this sign specifies that the hand doesn't move. Are you sure you want this movement module to exist?"
                if SIGN_TYPE["TWO_HANDS_NO_MVMT"] in self.signtype_specslist and (articulator_dict[1] or articulator_dict[2]):
                    warning_msg = "The sign type for this sign specifies that neither hand moves. Are you sure you want this movement module to exist?"
                elif SIGN_TYPE["TWO_HANDS_ONLY_H1"] in self.signtype_specslist and (articulator_dict[2] or both_hands_selected):
                    warning_msg = f"The sign type for this sign specifies that only H1 moves. Are you sure you want this movement module to apply to {calculate_selected_hand(articulator_dict)}?"
                elif SIGN_TYPE["TWO_HANDS_ONLY_H2"] in self.signtype_specslist and (articulator_dict[1] or both_hands_selected):
                    warning_msg = f"The sign type for this sign specifies that only H2 moves. Are you sure you want this movement module to apply to {calculate_selected_hand(articulator_dict)}?"
                elif SIGN_TYPE["TWO_HANDS_ONE_MVMT"] in self.signtype_specslist and both_hands_selected:
                    # this is when there is no specification for which hand moves
                    warning_msg = f"The sign type for this sign specifies that only one hand moves. Are you sure you want this movement module to apply to both hands?"

        return articulatorsvalid, (articulator, articulator_dict), warning_msg

    def handle_button_click(self, button):
        standard = self.button_box.standardButton(button)

        if standard == QDialogButtonBox.Cancel:
            self.reject()
        elif standard == QDialogButtonBox.Help:
            show_help(self.moduletype)  # when 'help' button clicked

        elif standard == QDialogButtonBox.Discard:
            deletethemodule = True

            if self.moduletype in [ModuleTypes.MOVEMENT, ModuleTypes.LOCATION]:
                relationslist = list(self.mainwindow.current_sign.relationmodules.values())
                relationslist = [rel for rel in relationslist if (
                        rel.relationy.existingmodule and self.existingkey in rel.relationy.linkedmoduleids)]
                if len(relationslist) > 0:
                    responsebtn = QMessageBox.critical(self,
                                                       "Warning",
                                                        "This module has associated Relation modules; are you sure you want to delete?",
                                                        QMessageBox.Yes | QMessageBox.No,
                                                        QMessageBox.Yes)
                    if responsebtn == QMessageBox.No:
                        deletethemodule = False

            if deletethemodule:
                self.module_deleted.emit()
                self.accept()
            else:
                # neither accept nor reject, so that anchor module dialog stays open if user decides not to delete after all
                pass

        elif standard == QDialogButtonBox.Save:  # save and add another
            self.validate_and_save(addanother=True, closedialog=False)

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
        savedmodule = None

        # validate hand selection
        articulatorsvalid, articulators, warning_msg = self.validate_articulators()
        # if the default is "1h" and we have both hands selected...
        if warning_msg:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Articulator Setting Conflict")
            msgBox.setText(warning_msg)
            no_btn = msgBox.addButton("Return to editing", QMessageBox.ButtonRole.NoRole)
            msgBox.addButton("Continue with saving module", QMessageBox.ButtonRole.YesRole)
            msgBox.setIcon(QMessageBox.Icon.Warning)
            msgBox.exec_()
            if msgBox.clickedButton() == no_btn:
                return savedmodule

        # validate timing interval(s) selection
        timingvalid, timingintervals = self.validate_timingintervals()

        # validate module selections
        modulevalid, modulemessage = self.module_widget.validity_check()

        messagestring = ""
        if not articulatorsvalid:
            # refuse to save without articulator & timing info
            messagestring += "Missing articulator selection"
        if not timingvalid:
            messagestring+= "Missing timing selection" if articulatorsvalid else " and timing selection"
        if len(messagestring) > 0 :
            messagestring += ". "

        if not modulevalid:
            # refuse to save without valid module selections
            messagestring += modulemessage

        if messagestring != "":
            # warn user that there's missing and/or invalid info and don't let them save
            QMessageBox.critical(self, "Warning", messagestring)
        elif messagestring == "" and not modulevalid:
            return savedmodule 
        elif addanother:
            # save info and then refresh screen to start next module
            savedmodule = self.module_widget.getsavedmodule(articulators, timingintervals, phonlocs, addedinfo, inphase)
            self.module_saved.emit(savedmodule, self.moduletype)
            if self.usearticulators:
                self.articulators_widget.clear()
            self.addedinfobutton.clear()
            if self.usexslots:
                self.xslot_widget.clear()
            self.module_widget.clear()
            self.module_widget.existingkey = None
            if self.moduletype == ModuleTypes.RELATION:
                self.module_widget.setvaluesfromanchor(self.linkedfrommoduleid, self.linkedfrommoduletype)
        elif not addanother:
            # save info
            savedmodule = self.module_widget.getsavedmodule(articulators, timingintervals, phonlocs, addedinfo, inphase)
            self.module_saved.emit(savedmodule, self.moduletype)
            if closedialog:
                # close dialog if caller requests it (but if we're only saving so, eg,
                # we can add an associated relation module, then closedialog will be False)
                self.accept()

        return savedmodule


class AssociatedRelationsDialog(QDialog):
    module_saved = pyqtSignal(ParameterModule, str)

    def __init__(self, anchormodule=None, **kwargs):
        super().__init__(**kwargs)
        self.mainwindow = self.parent().mainwindow
        self.anchormodule = anchormodule
        main_layout = QVBoxLayout()

        label = QLabel("Associated Relation modules (click to view or edit):")

        self.relations_listview = QListView()
        self.relations_listmodel = ModuleLinkingListModel()
        self.refresh_listmodel()
        # self.relations_listmodel.setmoduleslist(self.relationslist, ModuleTypes.RELATION)
        self.relations_listview.setModel(self.relations_listmodel)
        self.relations_listview.setSelectionMode(QAbstractItemView.SingleSelection)
        self.relations_listview.clicked.connect(lambda index: self.handle_relationmod_clicked(self.relations_listmodel.itemFromIndex(index).module))

        main_layout.addWidget(label)
        main_layout.addWidget(self.relations_listview)

        separate_line = QFrame()
        separate_line.setFrameShape(QFrame.HLine)
        separate_line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separate_line)

        buttons = QDialogButtonBox.Close
        self.button_box = QDialogButtonBox(buttons, parent=self)
        # self.button_box.button(QDialogButtonBox.Close).setAutoDefault(True)
        self.button_box.clicked.connect(self.handle_button_click)

        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)

    def handle_button_click(self, button):
        standard = self.button_box.standardButton(button)

        if standard == QDialogButtonBox.Close:
            self.accept()  # TODO KV ???

    def handle_relationmod_clicked(self, relmod):
        module_selector = ModuleSelectorDialog(moduletype=ModuleTypes.RELATION,
                                               xslotstructure=self.mainwindow.current_sign.xslotstructure,
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

    def refresh_listmodel(self):
        self.relationslist = list(self.mainwindow.current_sign.relationmodules.values())
        self.relationmodulenumsdict = self.mainwindow.current_sign.relationmodulenumbers
        if self.anchormodule is not None:
            # TODO KV the numbering is not correct for the filtered list (just re-numbers in order from 1; doesn't match what's in summary)
            self.relationslist = [rel for rel in self.relationslist if
                                  (rel.relationy.existingmodule and
                                   self.anchormodule.uniqueid in rel.relationy.linkedmoduleids)]
        else:
            self.relationslist = []

        self.relations_listmodel.setmoduleslist(self.relationslist, self.relationmodulenumsdict, ModuleTypes.RELATION)


class AssociatedRelationsPanel(QFrame):
    module_saved = pyqtSignal(ParameterModule, str)
    save_anchor = pyqtSignal()

    def __init__(self, anchormodule=None, **kwargs):
        super().__init__(**kwargs)
        self.mainwindow = self.parent().mainwindow
        self._anchormodule = anchormodule
        main_layout = QHBoxLayout()

        self.addrelation_button = QPushButton("Save and add associated Relation module")
        self.check_enable_saveaddrelation()
        self.addrelation_button.clicked.connect(self.handle_save_add_relationmodule)
        self.seerelations_button = SeeRelationsPushButton("See associated Relation modules")
        # TODO KV this button should be bolded when the list of such modules is nonempty
        # self.seerelations_button = QPushButton("See associated Relation modules")
        self.seerelations_button.clicked.connect(self.handle_see_relationmodules)

        main_layout.addStretch()
        main_layout.addWidget(self.addrelation_button)
        main_layout.addWidget(self.seerelations_button)

        main_layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(main_layout)

    @property
    def anchormodule(self):
        return self._anchormodule

    @anchormodule.setter
    def anchormodule(self, anchormodule):
        if anchormodule is not None:
            self._anchormodule = anchormodule
            self.style_seeassociatedrelations()

    def anchorhasassociatedrelations(self):
        relationslist = list(self.mainwindow.current_sign.relationmodules.values())
        if self.anchormodule is not None:
            relationslist = [rel for rel in relationslist if
                             (rel.relationy.existingmodule and
                              self.anchormodule.uniqueid in rel.relationy.linkedmoduleids)]
        else:
            relationslist = []
        return len(relationslist) > 0

    def style_seeassociatedrelations(self):
        hasrelation = self.anchorhasassociatedrelations()
        self.seerelations_button.hasrelations = hasrelation

    def check_enable_saveaddrelation(self, hastiming=None, hasarticulators=None, bodyloc=None):
        enable_addrelation = True

        if hastiming is None and hasarticulators is None and bodyloc is None:
            enable_addrelation = False

        # only use arguments if they have a boolean value (ie, are not None)
        if hastiming is not None:
            # make sure the anchor has a valid timing selection
            enable_addrelation = enable_addrelation and hastiming
            # timingvalid, timingintervals = self.parent().validate_timingintervals()
        if bodyloc is not None:
            # make sure the anchor is not a purely spatial location
            enable_addrelation = enable_addrelation and bodyloc
        if hasarticulators is not None:
            # make sure the anchor has a valid hand(s) selection
            enable_addrelation = enable_addrelation and hasarticulators

        self.addrelation_button.setEnabled(enable_addrelation)

    def handle_see_relationmodules(self):
        associatedrelations_dialog = AssociatedRelationsDialog(anchormodule=self.anchormodule, parent=self)
        associatedrelations_dialog.module_saved.connect(self.module_saved.emit)
        associatedrelations_dialog.exec_()
        self.style_seeassociatedrelations()  # in case one/some were deleted and there are none left now

    def handle_save_add_relationmodule(self):
        # save the current anchor module before trying to link a relation module to it
        self.save_anchor.emit()

        if self.anchormodule is not None:  # the save above was successful; continue
            module_selector = ModuleSelectorDialog(moduletype=ModuleTypes.RELATION,
                                                   xslotstructure=self.mainwindow.current_sign.xslotstructure,
                                                   moduletoload=None,
                                                   linkedfrommoduleid=self.anchormodule.uniqueid,
                                                   linkedfrommoduletype=self.parent().moduletype,
                                                   incl_articulators=[],
                                                   incl_articulator_subopts=0,
                                                   parent=self)
            module_selector.module_saved.connect(self.module_saved.emit)
            module_selector.exec_()


# Styled QPushButton whose text is bolded iff the _hasrelations attribute is true
class SeeRelationsPushButton(QPushButton):

    def __init__(self, title, hasrelations=False, **kwargs):
        super().__init__(title, **kwargs)
        self._hasrelations = hasrelations

        # styling
        qss = """   
            QPushButton[HasRelations=true] {
                font: bold;
            }

            QPushButton[HasRelations=false] {
                font: normal;
            }
        """
        self.setStyleSheet(qss)
        self.updateStyle()

    @property
    def hasrelations(self):
        return self._hasrelations

    @hasrelations.setter
    def hasrelations(self, hasrelations):
        if hasrelations is not None:
            self._hasrelations = hasrelations
        self.updateStyle()

    def updateStyle(self, hasrelations=None):
        if hasrelations is not None:
            self._hasrelations = hasrelations
        self.setProperty('HasRelations', self._hasrelations)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def clear(self):
        self.hasrelations = False


class XslotLinkingPanel(QFrame):
    selection_changed = pyqtSignal(bool,  # has >= 1 point
                                   bool)  # has >= 1 interval

    def __init__(self, xslotstructure, timingintervals=None, partialxslots=None, **kwargs):
        super().__init__(**kwargs)
        self.mainwindow = self.parent().mainwindow

        self.timingintervals = [] if timingintervals is None else timingintervals
        self.partialxslots = partialxslots
        if xslotstructure is not None:
            self.xslotstruct = xslotstructure
        else:
            self.xslotstruct = self.mainwindow.current_sign.xslotstructure
        if self.xslotstruct is None:
            print("no x-slot structure!")

        main_layout = QVBoxLayout()

        self.link_intro_label = QLabel("Click on the relevant point(s) or interval(s) to link this module.")
        main_layout.addWidget(self.link_intro_label)

        self.xslotlinkscene = XslotLinkScene(timingintervals=self.timingintervals, parentwidget=self)
        self.xslotlinkscene.selection_changed.connect(self.selection_changed.emit)
        self.xslotlinkview = QGraphicsView(self.xslotlinkscene)
        self.xslotlinkview.setFixedHeight(self.xslotlinkscene.scene_height + 50)
        # self.xslotlinkview.setFixedSize(self.xslotlinkscene.scene_width+100, self.xslotlinkscene.scene_height+50)
        # self.xslotlinkview.setSceneRect(0, 0, self.xslotlinkscene.scene_width, self.xslotlinkscene.scene_height)
        # self.xslotlinkview.fitInView(0, 0, self.xslotlinkscene.scene_width, self.xslotlinkscene.scene_height, Qt.KeepAspectRatio)
        # self.xslotvlinkview.setGeometry(0, 0, self.xslotlinkscene.scene_width, self.xslotlinkscene.scene_height)
        main_layout.addWidget(self.xslotlinkview)

        self.setLayout(main_layout)

    def gettimingintervals(self):
        return self.xslotlinkscene.xslotlinks

    def settimingintervals(self, timingintervals):
        if timingintervals is not None:
            self.timingintervals = timingintervals
            self.xslotlinkscene.setxslotlinks(self.timingintervals)

    def clear(self):
        self.xslotlinkscene = XslotLinkScene(parentwidget=self, timingintervals=[])
        self.xslotlinkview.setScene(self.xslotlinkscene)


class ArticulatorSelectionPanel(QFrame):
    articulatorchanged = pyqtSignal(str)

    def __init__(self, available_articulators=None, articulators=None, incl_articulator_subopts=0, inphase=0, **kwargs):
        super().__init__(**kwargs)

        self.incl_articulator_subopts = 0
        if isinstance(incl_articulator_subopts, bool):
            print("temp: incl_articulator_subopts is a bool")
        if isinstance(incl_articulator_subopts, bool) and incl_articulator_subopts:
            self.incl_articulator_subopts = 2
        elif isinstance(incl_articulator_subopts, int):
            self.incl_articulator_subopts = incl_articulator_subopts
        # self.incl_articulator_subopts...
        # 0 --> do not include any suboptions for "both" [previously includephase=False]
        # 1 --> include only "As a connected unit"
        # 2 --> include both "As a connected unit" and "in phase" / "out of phase" [previously includephase=True]

        articulator_layout = self.create_articulator_layout(available_articulators)
        self.setLayout(articulator_layout)
        if len(available_articulators) > 0:
            self.handle_articulator_changed(available_articulators[0])

        self.setarticulators(articulators)
        self.setphase(inphase)

    def create_articulator_layout(self, available_articulators):
        self.appliesto_label = QLabel("This module applies to:")

        if available_articulators is None or len(available_articulators) == 0:
            available_articulators = [HAND, ARM, LEG]
        self.articulator_selector = ArticulatorSelector(available_articulators)
        self.articulator_selector.articulatorchanged.connect(self.handle_articulator_changed)

        self.articulator_group = QButtonGroup()
        self.articulator1_radio = QRadioButton("Articulator 1")
        self.articulator2_radio = QRadioButton("Articulator 2")
        self.botharts_radio = QRadioButton("Both articualtors")
        self.articulator_group.addButton(self.articulator1_radio)
        self.articulator_group.addButton(self.articulator2_radio)
        self.articulator_group.addButton(self.botharts_radio)
        self.articulator_group.buttonToggled.connect(self.handle_articulatorgroup_toggled)

        # won't get displayed/used for all module types, but they are instantiated nonetheless to avoid potential reference errors
        self.botharts_group = QButtonGroup()
        self.botharts_group.setExclusive(False)
        self.botharts_connected_cb = QCheckBox("As a connected unit")
        self.botharts_inphase_cb = QCheckBox("In phase")
        self.botharts_outofphase_radio = QRadioButton("Out of phase")
        self.botharts_group.addButton(self.botharts_connected_cb)
        self.botharts_group.addButton(self.botharts_inphase_cb)
        self.botharts_group.addButton(self.botharts_outofphase_radio)
        self.botharts_group.buttonToggled.connect(self.handle_bothgroup_toggled)

        articulator_layout = QHBoxLayout()

        # for all module types-- Select the articulator; Articulator1; Articulator2
        singlearts_layout = QHBoxLayout()
        singlearts_layout.addWidget(self.appliesto_label)
        singlearts_layout.addWidget(self.articulator_selector)
        singlearts_layout.addWidget(self.articulator1_radio)
        singlearts_layout.addWidget(self.articulator2_radio)
        for idx in range(singlearts_layout.count()):
            singlearts_layout.setAlignment(singlearts_layout.itemAt(idx).widget(), Qt.AlignTop)
        articulator_layout.addLayout(singlearts_layout)

        # for (eg) movement or location -- Both (plus one or more suboptions)
        botharts_layout = QVBoxLayout()
        botharts_layout.addWidget(self.botharts_radio)
        if self.incl_articulator_subopts > 0:
            botharts_sub_spacedlayout = QHBoxLayout()
            botharts_sub_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
            botharts_sub_layout = QVBoxLayout()
            botharts_sub_layout.addWidget(self.botharts_connected_cb)
            if self.incl_articulator_subopts == 2:
                botharts_sub_layout.addWidget(self.botharts_inphase_cb)
                botharts_sub_layout.addWidget(self.botharts_outofphase_radio)
            botharts_sub_spacedlayout.addLayout(botharts_sub_layout)
            botharts_layout.addLayout(botharts_sub_spacedlayout)

        articulator_layout.addLayout(botharts_layout)

        return articulator_layout

    def handle_articulator_changed(self, articulator):
        self.articulatorchanged.emit(articulator)

        self.articulator1_radio.setText(articulator + " 1")
        self.articulator2_radio.setText(articulator + " 2")
        self.botharts_radio.setText("Both " + articulator.lower() + "s")
        checkedButton = self.articulator_group.checkedButton()
        if checkedButton:
            self.articulator_group.setExclusive(False) # this is needed to uncheck all radio buttons
            checkedButton.setChecked(False)
            self.articulator_group.setExclusive(True)
            for btn in self.botharts_group.buttons():
                btn.setChecked(False)
                btn.setEnabled(False)


    def handle_articulatorgroup_toggled(self, selectedbutton, ischecked):
        if selectedbutton == self.botharts_radio:
            # enable sub options
            for btn in self.botharts_group.buttons():
                btn.setEnabled(True)
        else:
            # disable sub options
            for btn in self.botharts_group.buttons():
                btn.setEnabled(False)

    def handle_bothgroup_toggled(self, btn, ischecked):
        if not ischecked:
            # don't need to do anything special
            return

        # ensure the parent is checked
        self.botharts_radio.setChecked(True)
        siblings = [b for b in self.botharts_group.buttons() if b != btn]

        if isinstance(btn, QCheckBox):
            # uncheck any radio button siblings
            for sib in siblings:
                if isinstance(sib, QRadioButton):
                    sib.setChecked(False)

        elif isinstance(btn, QRadioButton):
            # uncheck *all* other siblings
            for sib in siblings:
                sib.setChecked(False)

    def getarticulators(self):
        selectedarticulator = self.articulator_selector.getarticulator()
        both = self.botharts_radio.isChecked()
        selections_dict = {
            1: self.articulator1_radio.isChecked() or both,
            2: self.articulator2_radio.isChecked() or both
        }
        return selectedarticulator, selections_dict

    def setarticulators(self, articulators):
        if articulators is not None:
            selectedarticulator = articulators[0]
            articulators_dict = articulators[1]
            success = self.articulator_selector.setselectedarticulator(selectedarticulator)
            if success and articulators_dict is not None:
                if articulators_dict[1] and articulators_dict[2]:
                    self.botharts_radio.setChecked(True)
                elif articulators_dict[1]:
                    self.articulator1_radio.setChecked(True)
                elif articulators_dict[2]:
                    self.articulator2_radio.setChecked(True)

    def getphase(self):
        if not self.botharts_connected_cb.isEnabled() or not self.botharts_connected_cb.isChecked():
            # original options - these are mutually exclusive
            if self.botharts_inphase_cb.isEnabled() and self.botharts_inphase_cb.isChecked():
                return 1
            elif self.botharts_outofphase_radio.isEnabled() and self.botharts_outofphase_radio.isChecked():
                return 2
            else:
                return 0
        elif self.botharts_connected_cb.isEnabled() and self.botharts_connected_cb.isChecked():
            # these are mutually exclusive
            if self.botharts_inphase_cb.isEnabled() and self.botharts_inphase_cb.isChecked():
                return 4
            elif self.botharts_outofphase_radio.isEnabled() and self.botharts_outofphase_radio.isChecked():
                # it shouldn't be possible to have both "connected" and "out of phase" checked, but... just in case?
                return 5
            else:
                return 3

    def setphase(self, inphase):
        self.botharts_connected_cb.setChecked((inphase >= 3))

        if inphase % 3 == 1:
            self.botharts_inphase_cb.setChecked(True)
        elif inphase % 3 == 2:
            self.botharts_outofphase_radio.setChecked(True)

    def clear(self):
        self.articulator_group.setExclusive(False)
        for b in self.articulator_group.buttons() + self.botharts_group.buttons():
            b.setChecked(False)
            b.setEnabled(True)
        self.articulator_group.setExclusive(True)
