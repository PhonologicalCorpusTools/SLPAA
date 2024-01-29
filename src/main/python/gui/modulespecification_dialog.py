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
from lexicon.module_classes import AddedInfo, TimingInterval, TimingPoint, ParameterModule, ModuleTypes
from models.relation_models import ModuleLinkingListModel
from gui.movementspecification_view import MovementSpecificationPanel
from gui.locationspecification_view import LocationSpecificationPanel
from gui.handconfigspecification_view import HandConfigSpecificationPanel
from gui.relationspecification_view import RelationSpecificationPanel
from gui.orientationspecification_view import OrientationSpecificationPanel
from gui.modulespecification_widgets import AddedInfoPushButton, ArticulatorSelector
from constant import HAND, ARM, LEG


class ModuleSelectorDialog(QDialog):
    # the second param for module_saved is from ModuleTypes.xxxx TODO KV and will typically be None,
    # UNLESS the module being saved is of a different type than the primary module selector dialog
    # (ie, an associated relation module spawned from a movement or location module dialog)
    module_saved = pyqtSignal(ParameterModule, str)
    module_deleted = pyqtSignal()

    def __init__(self, moduletype, xslotstructure=None, moduletoload=None, linkedfrommoduleid=None, linkedfrommoduletype=None, includephase=0, incl_articulators=HAND, incl_articulator_subopts=0, **kwargs):
        super().__init__(**kwargs)
        self.mainwindow = self.parent().mainwindow
        self.moduletype = moduletype
        self.includearticulatorselection = len(incl_articulators) > 0
        self.linkedfrommoduleid = linkedfrommoduleid
        self.linkedfrommoduletype = linkedfrommoduletype
        self.existingkey = None

        timingintervals = []
        addedinfo = AddedInfo()
        new_instance = True
        articulators = (None, {1: None, 2: None})
        inphase = 0
        if isinstance(incl_articulators, str):
            incl_articulators = [incl_articulators]

        if moduletoload is not None:
            self.existingkey = moduletoload.uniqueid
            timingintervals = deepcopy(moduletoload.timingintervals)
            addedinfo = deepcopy(moduletoload.addedinfo)
            if moduletoload.articulators is not None:
                articulators = moduletoload.articulators
            new_instance = False
            if hasattr(moduletoload, '_inphase'):
                inphase = moduletoload.inphase

        main_layout = QVBoxLayout()

        self.arts_and_addedinfo_layout = QHBoxLayout()
        self.articulators_widget = ArticulatorSelectionPanel(available_articulators=incl_articulators,
                                                             articulators=articulators,
                                                             incl_articulator_subopts=incl_articulator_subopts,
                                                             inphase=inphase,
                                                             parent=self)
        if self.includearticulatorselection:
            self.arts_and_addedinfo_layout.addWidget(self.articulators_widget)

        self.arts_and_addedinfo_layout.addStretch()
        self.addedinfobutton = AddedInfoPushButton("Module notes")
        self.addedinfobutton.addedinfo = addedinfo
        self.arts_and_addedinfo_layout.addWidget(self.addedinfobutton)
        self.arts_and_addedinfo_layout.setAlignment(self.addedinfobutton, Qt.AlignTop)

        main_layout.addLayout(self.arts_and_addedinfo_layout)

        self.xslot_widget = XslotLinkingPanel(xslotstructure=xslotstructure,
                                              timingintervals=timingintervals,
                                              parent=self)
        if self.mainwindow.app_settings['signdefaults']['xslot_generation'] != 'none':
            main_layout.addWidget(self.xslot_widget)

        self.module_widget = QWidget()
        if moduletype == ModuleTypes.MOVEMENT:
            self.module_widget = MovementSpecificationPanel(moduletoload=moduletoload, parent=self)
        elif moduletype == ModuleTypes.LOCATION:
            self.module_widget = LocationSpecificationPanel(moduletoload=moduletoload, parent=self)
        elif moduletype == ModuleTypes.HANDCONFIG:
            self.module_widget = HandConfigSpecificationPanel(moduletoload=moduletoload, parent=self)
        elif self.moduletype == ModuleTypes.RELATION:
            self.module_widget = RelationSpecificationPanel(moduletoload=moduletoload, parent=self)
            self.xslot_widget.selection_changed.connect(self.module_widget.timinglinknotification)
            self.xslot_widget.xslotlinkscene.emit_selection_changed()  # to ensure that the initial timing selection is noted
            self.module_widget.timingintervals_inherited.connect(self.xslot_widget.settimingintervals)
            self.module_widget.setvaluesfromanchor(self.linkedfrommoduleid, self.linkedfrommoduletype)
        elif self.moduletype == ModuleTypes.ORIENTATION:
            self.module_widget = OrientationSpecificationPanel(moduletoload=moduletoload, parent=self)
        main_layout.addWidget(self.module_widget)

        self.handle_articulator_changed(articulators[0])
        self.articulators_widget.articulatorchanged.connect(self.handle_articulator_changed)

        if self.moduletype in [ModuleTypes.MOVEMENT, ModuleTypes.LOCATION]:
            self.associatedrelations_widget = AssociatedRelationsPanel(parent=self)
            if self.existingkey is not None:
                self.associatedrelations_widget.anchormodule = self.mainwindow.current_sign.getmoduledict(self.moduletype)[self.existingkey]
            self.check_enable_saveaddrelation()

            self.associatedrelations_widget.save_anchor.connect(self.handle_save_anchor)
            self.associatedrelations_widget.module_saved.connect(self.handle_modulesaved)
            self.xslot_widget.selection_changed.connect(self.check_enable_saveaddrelation)
            self.articulators_widget.articulator_group.buttonClicked.connect(self.check_enable_saveaddrelation)
            if self.moduletype == ModuleTypes.LOCATION:
                self.module_widget.loctype_subgroup.buttonClicked.connect(self.check_enable_saveaddrelation)
                self.module_widget.signingspace_subgroup.buttonClicked.connect(self.check_enable_saveaddrelation)

            main_layout.addWidget(self.associatedrelations_widget)

        separate_line = QFrame()
        separate_line.setFrameShape(QFrame.HLine)
        separate_line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separate_line)

        # If we're creating a brand new instance of a module, then we want a
        #   "Save and Add Another" button, to allow the user to continue adding new instances.
        # On the other hand, if we're editing an existing instance of a module, then instead we want a
        #   "Delete" button, in case the user wants to delete the instance rather than editing it.
        buttons = None
        applytext = ""
        discardtext = "Delete"
        if new_instance:
            buttons = QDialogButtonBox.RestoreDefaults | QDialogButtonBox.Save | QDialogButtonBox.Apply | QDialogButtonBox.Cancel
            applytext = "Save and close"
        else:
            buttons = QDialogButtonBox.RestoreDefaults | QDialogButtonBox.Discard | QDialogButtonBox.Apply | QDialogButtonBox.Cancel
            applytext = "Save"

        self.button_box = QDialogButtonBox(buttons, parent=self)
        if new_instance:
            self.button_box.button(QDialogButtonBox.Save).setText("Save and add another")
        else:
            self.button_box.button(QDialogButtonBox.Discard).setText(discardtext)
        self.button_box.button(QDialogButtonBox.Apply).setDefault(True)
        self.button_box.button(QDialogButtonBox.Apply).setText(applytext)

        # TODO KV keep? from orig locationdefinerdialog:
        #      Ref: https://programtalk.com/vs2/python/654/enki/enki/core/workspace.py/
        self.button_box.clicked.connect(self.handle_button_click)

        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)
        # self.setMinimumSize(QSize(500, 700))
        # # self.setMinimumSize(modulelayout.desiredwidth(), modulelayout.desiredheight())
        # self.setMinimumSize(QSize(modulelayout.rect().width(), modulelayout.rect().height()))
        # self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.adjustSize()

    def handle_modulesaved(self, relationtosave, moduletype):
        self.module_saved.emit(relationtosave, moduletype)
        self.style_seeassociatedrelations()

    def check_enable_saveaddrelation(self):
        hastiming = self.validate_timingintervals()[0]
        hashands = self.validate_articulators()[0]
        bodyloc = (
            self.module_widget.getcurrentlocationtype().usesbodylocations() if self.moduletype == ModuleTypes.LOCATION else None)
        self.associatedrelations_widget.check_enable_saveaddrelation(hastiming, hashands, bodyloc)

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
        timingintervals = self.xslot_widget.gettimingintervals()
        timingvalid = True
        if len(timingintervals) == 0 and self.mainwindow.app_settings['signdefaults']['xslot_generation'] != 'none':
            timingvalid = False
        elif self.mainwindow.app_settings['signdefaults']['xslot_generation'] == 'none':
            # no x-slots; make the timing interval be for the whole sign
            timingintervals = [TimingInterval(TimingPoint(0, 0), TimingPoint(1, 0))]

        return timingvalid, timingintervals

    # validate articulator selection (all modules except relation must have at least one articulator selected)
    def validate_articulators(self):

        articulator, articulator_dict = self.articulators_widget.getarticulators()
        articulatorsvalid = True
        if self.includearticulatorselection and (articulator is None or True not in articulator_dict.values()):
            articulatorsvalid = False

        return articulatorsvalid, (articulator, articulator_dict)

    def handle_button_click(self, button):
        standard = self.button_box.standardButton(button)

        if standard == QDialogButtonBox.Cancel:
            self.reject()

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
        if not (articulatorsvalid and timingvalid):
            # refuse to save without articulator & timing info
            messagestring += "Missing"
            messagestring += " articulator selection" if not articulatorsvalid else ""
            messagestring += " and" if not (articulatorsvalid or timingvalid) else ""
            messagestring += " timing selection" if not timingvalid else ""
            messagestring += ". "
        if not modulevalid:
            # refuse to save without valid module selections
            messagestring += modulemessage

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
                                               includephase=0,
                                               incl_articulators=[],
                                               parent=self)
        module_selector.module_saved.connect(lambda moduletosave, savedtype: self.module_saved.emit(moduletosave, savedtype))
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

    def check_enable_saveaddrelation(self, hastiming=None, hashands=None, bodyloc=None):
        enable_addrelation = True

        if hastiming is None and hashands is None and bodyloc is None:
            enable_addrelation = False

        # only use arguments if they have a boolean value (ie, are not None)
        if hastiming is not None:
            # make sure the anchor has a valid timing selection
            enable_addrelation = enable_addrelation and hastiming
            # timingvalid, timingintervals = self.parent().validate_timingintervals()
        if bodyloc is not None:
            # make sure the anchor is not a purely spatial location
            enable_addrelation = enable_addrelation and bodyloc
        if hashands is not None:
            # make sure the anchor has a valid hand(s) selection
            enable_addrelation = enable_addrelation and hashands

        self.addrelation_button.setEnabled(enable_addrelation)

    def handle_see_relationmodules(self):
        associatedrelations_dialog = AssociatedRelationsDialog(anchormodule=self.anchormodule, parent=self)
        associatedrelations_dialog.module_saved.connect(lambda moduletosave, savedtype: self.module_saved.emit(moduletosave, savedtype))
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
                                                   includephase=0,
                                                   incl_articulators=[],
                                                   parent=self)
            module_selector.module_saved.connect(lambda moduletosave, savedtype: self.module_saved.emit(moduletosave, savedtype))
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

    def __init__(self, xslotstructure, timingintervals=None, **kwargs):
        super().__init__(**kwargs)
        self.mainwindow = self.parent().mainwindow

        self.timingintervals = [] if timingintervals is None else timingintervals
        xslotstruct = self.mainwindow.current_sign.xslotstructure
        if xslotstruct is None:
            print("no x-slot structure!")

        main_layout = QVBoxLayout()

        self.link_intro_label = QLabel("Click on the relevant point(s) or interval(s) to link this module.")
        main_layout.addWidget(self.link_intro_label)

        self.xslotlinkscene = XslotLinkScene(timingintervals=self.timingintervals, parentwidget=self)
        self.xslotlinkscene.selection_changed.connect(lambda haspoint, hasinterval: self.selection_changed.emit(haspoint, hasinterval))
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

    def handle_articulatorgroup_toggled(self, btn, ischecked):
        selectedbutton = self.articulator_group.checkedButton()
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
