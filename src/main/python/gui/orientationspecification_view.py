from PyQt5.QtWidgets import (
    QListView,
    QLineEdit,
    QRadioButton,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QButtonGroup,
    QGroupBox,
    QAbstractItemView,
    QCheckBox,
    QSpacerItem,
    QSizePolicy,
    QPushButton
)

from PyQt5.QtCore import (
    Qt,
    QEvent,
    pyqtSignal,
    QItemSelectionModel
)

from lexicon.module_classes import (
    RelationModule,
    LocationModule,
    MovementModule,
    OrientationModule,
    MannerRelation,
    Distance,
    Direction,
    ModuleTypes,
    ContactRelation,
    ContactType,
    BodypartInfo
)
from models.relation_models import ModuleLinkingListModel
from models.location_models import BodypartTreeModel
from gui.modulespecification_widgets import ModuleSpecificationPanel, SpecifyBodypartPushButton
from gui.bodypartspecification_dialog import BodypartSelectorDialog
from gui.helper_widget import OptionSwitch
from constant import HAND, ARM, LEG


class OrientationSpecificationPanel(ModuleSpecificationPanel):
    timingintervals_inherited = pyqtSignal(list)

    def __init__(self, moduletoload=None, **kwargs):
        super().__init__(**kwargs)
        # mainwindow & existingkey initialization now done in parent class's init()
        # self.mainwindow = self.parent().mainwindow
        # self.existingkey = None
        self.islinkedtopoint = False
        self.islinkedtointerval = False

        main_layout = QVBoxLayout()

        # create layout for palm direction
        palm_box = self.create_palm_box()
        main_layout.addWidget(palm_box)
        
        # create layout for figner root direction
        finger_box = self.create_finger_root_box()
        main_layout.addWidget(finger_box)

        # set according to the existing module being loaded
        if moduletoload is not None and isinstance(moduletoload, OrientationModule):
            self.setvalues(moduletoload)
            self.existingkey = moduletoload.uniqueid

        self.setLayout(main_layout)
        self.check_enable_allsubmenus()

    def validity_check(self):
        # Needs to be implemented as in all module classes
        # But no for this module, allow any number of empty selections
        return True, ""

    def timinglinknotification(self, haspoint, hasinterval):
        self.islinkedtopoint = haspoint
        self.islinkedtointerval = hasinterval
        self.check_enable_allsubmenus()
        
    def getsavedmodule_new(self, articulators, timingintervals, addedinfo, inphase):
        
        orimod = OrientationModule(articulators=articulators,
                                   timingintervals=timingintervals,
                                   addedinfo=addedinfo)
        
        if self.existingkey is not None:
            orimod.uniqueid = self.existingkey
        else:
            self.existingkey = orimod.uniqueid
        return orimod
    
    
    def getsavedmodule(self, articulators, timingintervals, addedinfo, inphase):

        orimod = OrientationModule(palmdirs_list=self.getcurrentpalmdirections(),
                                   rootdirs_list=self.getcurrentrootdirections(),
                                   articulators=articulators,
                                   timingintervals=timingintervals,
                                   addedinfo=addedinfo,
                                   inphase=inphase
                                   )
        
        if self.existingkey is not None:
            orimod.uniqueid = self.existingkey
        else:
            self.existingkey = orimod.uniqueid
        return orimod


    # if 'movement' is selected for Y,
    #  then Contact, Manner, Direction, and Distance menus are all inactive below
    def check_enable_contact(self):
        self.contact_box.setEnabled(not(self.y_existingmod_radio.isChecked() and
                                    self.getcurrentlinkedmoduletype() == ModuleTypes.MOVEMENT))

    # 1. Contact manner can only be coded if
    #   (a) 'contact' is selected AND
    #   (b) the module is linked to an interval OR x-slots are off
    # 2. OR Can also be available if
    #   (a) neither 'contact' nor 'no contact' is selected AND
    #   (b) there are no selections in manner or distance
    # 3. BUT if 'movement' is selected for Y,
    #   then Contact, Manner, Direction, and Distance menus are all inactive below
    def check_enable_manner(self):
        xslots_off = self.mainwindow.app_settings['signdefaults']['xslot_generation'] == 'none'
        meetscondition1 = self.contact_rb.isChecked() and (self.islinkedtointerval or xslots_off)

        meetscondition2 = self.contactmannerdistance_empty()

        meetscondition3 = self.y_existingmod_radio.isChecked() and \
                          self.getcurrentlinkedmoduletype() == ModuleTypes.MOVEMENT

        enable_manner = (meetscondition1 or meetscondition2) and not meetscondition3
        self.manner_box.setEnabled(enable_manner)

    # returns True iff no radio buttons are selected in any of
    # Contact, Manner, or Distance (i.e., returning False means
    # that at least one has a button checked)
    def contactmannerdistance_empty(self):
        for grp in [self.manner_group, self.dishor_group, self.disver_group, self.dissag_group]:
            if grp.checkedButton() is not None:
                return False
        if self.contact_group.checkedButton() is not None:
            return False
        return True

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
        for box in [self.dishor_box, self.disver_box, self.dissag_box]:
            box.setEnabled(enable_distance)

    # if 'movement' is selected for Y,
    #  then Contact, Manner, Direction (including crossed/linked), and Distance menus are all inactive below
    def check_enable_direction(self):
        enable_direction = not (self.y_existingmod_radio.isChecked() and
                                self.getcurrentlinkedmoduletype() == ModuleTypes.MOVEMENT)
        for box in [self.palm_dirhor_box, self.palm_dirver_box, self.palm_dirsag_box]:
            box.setEnabled(enable_direction)
        self.crossed_cb.setEnabled(enable_direction)
        self.linked_cb.setEnabled(enable_direction)

    def handle_distancebutton_toggled(self, btn, ischecked):
        if btn.group().checkedButton() is not None:
            self.nocontact_rb.setChecked(True)

    # create layout for distance or direction options on a particular axis
    def create_axis_layout(self, radio1, radio2, radiogroup, axis_cb=None, axis_label=None):
        axis_layout = QVBoxLayout()
        axisoptions_spacedlayout = QHBoxLayout()
        axisoptions_layout = QVBoxLayout()
        radiogroup.addButton(radio1)
        radiogroup.addButton(radio2)

        if axis_cb is not None:
            radiogroup.buttonToggled.connect(lambda rb, ischecked: self.handle_axisgroup_toggled(rb, ischecked, axis_cb))
            axis_cb.toggled.connect(lambda ischecked: self.handle_axiscb_toggled(ischecked, radiogroup))
            axis_layout.addWidget(axis_cb)
        elif axis_label is not None:
            axis_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            axis_layout.addWidget(axis_label)
        axisoptions_spacedlayout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        axisoptions_layout.addWidget(radio1)
        axisoptions_layout.addWidget(radio2)
        
        axisoptions_spacedlayout.addLayout(axisoptions_layout)
        axis_layout.addLayout(axisoptions_spacedlayout)

        return axis_layout

    def handle_axiscb_toggled(self, ischecked, radiogroup):
        isdirgroup = radiogroup in [self.palm_dirhor_group, self.palm_dirver_group, self.palm_dirsag_group,
                                    self.root_dirhor_group, self.root_dirver_group, self.root_dirsag_group]

        for btn in radiogroup.buttons():
            btn.setEnabled(ischecked and isdirgroup)

    def handle_axisgroup_toggled(self, rb, ischecked, axis_cb):
        if not ischecked:
            # don't need to do anything special
            return

        # ensure the parent is checked
        axis_cb.setChecked(True)


    def check_enable_allsubmenus(self):
        # self.check_enable_contact()
        # self.check_enable_distance()
        # self.check_enable_direction()
        # self.check_enable_manner()
        pass

    def handle_contacttypegroup_toggled(self, btn, checked):
        if self.contacttype_group.checkedButton() is not None:
            self.contact_rb.setChecked(True)

        # enable "specify" text box iff the checked button is "other"
        self.contact_other_text.setEnabled(self.contacttype_group.checkedButton() == self.contactother_rb)

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

        # check whether submenus (contact, manner, direction, distance) should be enabled
        self.check_enable_allsubmenus()


    def create_hands_layout(self):

        # create layout for selecting the hands involved in the orientation
        layout = QHBoxLayout()
        self.button_group = QButtonGroup()
        self.h1_radio = OrientationRadioButton("H1")
        self.h2_radio = OrientationRadioButton("H2")
        self.both_radio = OrientationRadioButton("Both hands")
        
        self.button_group.addButton(self.h1_radio)
        self.button_group.addButton(self.h2_radio)
        self.button_group.addButton(self.both_radio)
        
        layout.addWidget(self.h1_radio)
        layout.addWidget(self.h2_radio)
        layout.addWidget(self.both_radio)
        
        return layout
    
    
        # create side-by-side layout for specifying direction of relation
    def create_palm_box(self):
        palm_box = QGroupBox("Direction of palm")
        palm_layout = QVBoxLayout()
        palm_sublayout = QHBoxLayout()

        # create layout for horizontal direction options
        self.palm_dirhor_box = QGroupBox()
        self.palm_dirhor_cb = QCheckBox("Horizontal")
        self.palm_dirhoripsi_rb = OrientationRadioButton("Ipsilateral")
        self.palm_dirhorcontra_rb = OrientationRadioButton("Contralateral")
        self.palm_dirhor_group = OrientationButtonGroup()
        dir_hor_layout = self.create_axis_layout(self.palm_dirhoripsi_rb,
                                                 self.palm_dirhorcontra_rb,
                                                 self.palm_dirhor_group,
                                                 axis_cb=self.palm_dirhor_cb)
        self.palm_dirhor_box.setLayout(dir_hor_layout)
        palm_sublayout.addWidget(self.palm_dirhor_box)

        # create layout for vertical direction options
        self.palm_dirver_box = QGroupBox()
        self.palm_dirver_cb = QCheckBox("Vertical")
        self.palm_dirverup_rb = OrientationRadioButton("Up")
        self.palm_dirverdown_rb = OrientationRadioButton("Down")
        self.palm_dirver_group = OrientationButtonGroup()
        dir_ver_layout = self.create_axis_layout(self.palm_dirverup_rb,
                                                 self.palm_dirverdown_rb,
                                                 self.palm_dirver_group,
                                                 axis_cb=self.palm_dirver_cb)
        self.palm_dirver_box.setLayout(dir_ver_layout)
        palm_sublayout.addWidget(self.palm_dirver_box)

        # create layout for sagittal direction options
        self.palm_dirsag_box = QGroupBox()
        self.palm_dirsag_cb = QCheckBox("Sagittal")
        self.palm_dirsagdist_rb = OrientationRadioButton("Distal")
        self.palm_dirsagprox_rb = OrientationRadioButton("Proximal")
        self.palm_dirsag_group = OrientationButtonGroup()
        dir_sag_layout = self.create_axis_layout(self.palm_dirsagdist_rb,
                                                 self.palm_dirsagprox_rb,
                                                 self.palm_dirsag_group,
                                                 axis_cb=self.palm_dirsag_cb)
        self.palm_dirsag_box.setLayout(dir_sag_layout)
        palm_sublayout.addWidget(self.palm_dirsag_box)

        palm_layout.addLayout(palm_sublayout)
        palm_box.setLayout(palm_layout)
        return palm_box
    
    
    def create_finger_root_box(self):
        root_box = QGroupBox("Direction of finger root")
        root_layout = QVBoxLayout()
        root_sublayout = QHBoxLayout()

        # create layout for horizontal direction options
        self.root_dirhor_box = QGroupBox()
        self.root_dirhor_cb = QCheckBox("Horizontal")
        self.root_dirhoripsi_rb = OrientationRadioButton("Ipsilateral")
        self.root_dirhorcontra_rb = OrientationRadioButton("Contralateral")
        self.root_dirhor_group = OrientationButtonGroup()
        dir_hor_layout = self.create_axis_layout(self.root_dirhoripsi_rb,
                                                 self.root_dirhorcontra_rb,
                                                 self.root_dirhor_group,
                                                 axis_cb=self.root_dirhor_cb)
        self.root_dirhor_box.setLayout(dir_hor_layout)
        root_sublayout.addWidget(self.root_dirhor_box)

        # create layout for vertical direction options
        self.root_dirver_box = QGroupBox()
        self.root_dirver_cb = QCheckBox("Vertical")
        self.root_dirverup_rb = OrientationRadioButton("Up")
        self.root_dirverdown_rb = OrientationRadioButton("Down")
        self.root_dirver_group = OrientationButtonGroup()
        dir_ver_layout = self.create_axis_layout(self.root_dirverup_rb,
                                                 self.root_dirverdown_rb,
                                                 self.root_dirver_group,
                                                 axis_cb=self.root_dirver_cb)
        self.root_dirver_box.setLayout(dir_ver_layout)
        root_sublayout.addWidget(self.root_dirver_box)

        # create layout for sagittal direction options
        self.root_dirsag_box = QGroupBox()
        self.root_dirsag_cb = QCheckBox("Sagittal")
        self.root_dirsagdist_rb = OrientationRadioButton("Distal")
        self.root_dirsagprox_rb = OrientationRadioButton("Proximal")
        self.root_dirsag_group = OrientationButtonGroup()
        dir_sag_layout = self.create_axis_layout(self.root_dirsagdist_rb,
                                                 self.root_dirsagprox_rb,
                                                 self.root_dirsag_group,
                                                 axis_cb=self.root_dirsag_cb)
        self.root_dirsag_box.setLayout(dir_sag_layout)
        root_sublayout.addWidget(self.root_dirsag_box)

        root_layout.addLayout(root_sublayout)
        root_box.setLayout(root_layout)
        return root_box

    def update_existingmodule_list(self, selection_dict):
        if selection_dict[1]:
            self.existingmodule_listmodel.setmoduleslist(self.locmodslist, self.locmodnums, ModuleTypes.LOCATION)
        elif selection_dict[2]:
            self.existingmodule_listmodel.setmoduleslist(self.movmodslist, self.movmodnums, ModuleTypes.MOVEMENT)
        else:
            self.existingmodule_listmodel.setmoduleslist(None)

    # def handle_existingmod_clicked(self, modelindex):
    #     if modelindex not in self.existingmod_listview.selectedIndexes():
    #         # don't need to do anything special
    #         return
    #     # ensure the parent is checked
    #     self.y_existingmod_radio.setChecked(True)

    # used when the relation module is spawned from an existing other module (eg location)
    def setvaluesfromanchor(self, linkedfrommoduleid, linkedfrommoduletype):
        if linkedfrommoduleid is None or linkedfrommoduletype is None:
            return

        linkedfrommodule = self.mainwindow.current_sign.getmoduledict(linkedfrommoduletype)[linkedfrommoduleid]

        #  If a user is filling out a location or movement module and then goes from that to create an
        #  ‘associated relation module’...
        if isinstance(linkedfrommodule, LocationModule) or isinstance(linkedfrommodule, MovementModule):

            # ... the timing selection should auto-fill to match the timing of the base module
            timingintervals = linkedfrommodule.timingintervals
            self.timingintervals_inherited.emit(timingintervals)

            # ... the "X" selection in the relation module should auto-fill to match the "applies to"
            #  selection in the linked module (i.e., H1, H2, both hands, as a connected unit)
            articulator, articulator_dict = linkedfrommodule.articulators
            if articulator == HAND:
                if articulator_dict[1] and articulator_dict[2]:
                    self.both_radio.setChecked(True)
                    if linkedfrommodule.inphase >- 3:
                        self.both_radio.setChecked(True)
                elif articulator_dict[1]:
                    self.h1_radio.setChecked(True)
                elif articulator_dict[2]:
                    self.h2_radio.setChecked(True)

            # ...and the "Y" selection in the relation module should auto-fill to
            #  match the location selected in the location module.
            linked_uids = [linkedfrommodule.uniqueid]
            linked_type = None
            if isinstance(linkedfrommodule, LocationModule):
                linked_type = ModuleTypes.LOCATION
            elif isinstance(linkedfrommodule, MovementModule):
                linked_type = ModuleTypes.MOVEMENT
            self.setcurrentlinkedmoduleinfo(linked_uids, linked_type)

            # If the starting location module is specifically a body-anchored signing space location,
            #  "no contact" should be auto-selected. (If the starting location module is a body location,
            #  there should be no associated specification for contact.)
            if linked_type == ModuleTypes.LOCATION and linkedfrommodule.locationtreemodel.locationtype.bodyanchored:
                self.nocontact_rb.setChecked(True)

    def setvalues(self, moduletoload):
        self.setcurrentpalmdirection(moduletoload.palm)
        self.setcurrentrootdirection(moduletoload.root)

        # TODO KV set the linked-from module if there is one in moduletoload

    # def setbodyparts(self, bodyparts_dict):
    #     self.bodyparts_dict = bodyparts_dict
    #     self.handpart_button.hascontent = self.bodyparts_dict[HAND][1].hascontent() or self.bodyparts_dict[HAND][2].hascontent()
    #     self.armpart_button.hascontent = self.bodyparts_dict[ARM][1].hascontent() or self.bodyparts_dict[ARM][2].hascontent()
    #     self.legpart_button.hascontent = self.bodyparts_dict[LEG][1].hascontent() or self.bodyparts_dict[LEG][2].hascontent()



    # def getcurrentcontact(self):
    #     hascontact = self.contact_rb.isChecked()
    #     hasnocontact = self.nocontact_rb.isChecked()
    #     contactreln = None
    #     if hascontact:
    #         mannerrel = self.getcurrentmanner()
    #         contacttype = self.getcurrentcontacttype()
    #         contactreln = ContactRelation(contact=True, contacttype=contacttype, mannerrel=mannerrel)
    #     elif hasnocontact:
    #         distances = self.getcurrentdistances()
    #         contactreln = ContactRelation(contact=False, distance_list=distances)
    #     else:  # contact isn't specified (neither "contact" nor "no contact" radio button is selected)
    #         distances = self.getcurrentdistances()
    #         contactreln = ContactRelation(contact=None, distance_list=distances)
    #     return contactreln

    # def getcurrentcontacttype(self):
    #     contacttype = ContactType(
    #         light=self.contactlight_rb.isChecked(),
    #         firm=self.contactfirm_rb.isChecked(),
    #         other=self.contactother_rb.isChecked(),
    #         othertext=self.contact_other_text.text()
    #     )
    #     return contacttype

    # def getcurrentmanner(self):
    #     contactmannerreln = MannerRelation(
    #         holding=self.holding_rb.isChecked(),
    #         continuous=self.continuous_rb.isChecked(),
    #         intermittent=self.intermittent_rb.isChecked()
    #     )
    #     return contactmannerreln

    def getcurrentpalmdirections(self):
        direction_hor = Direction(axis=Direction.HORIZONTAL,
                                  axisselected=self.palm_dirhor_cb.isChecked(),
                                  plus=self.palm_dirhoripsi_rb.isChecked(),
                                  minus=self.palm_dirhorcontra_rb.isChecked()
                                  )
        direction_ver = Direction(axis=Direction.VERTICAL,
                                  axisselected=self.palm_dirver_cb.isChecked(),
                                  plus=self.palm_dirverup_rb.isChecked(),
                                  minus=self.palm_dirverdown_rb.isChecked()
                                  )
        direction_sag = Direction(axis=Direction.SAGITTAL,
                                  axisselected=self.palm_dirsag_cb.isChecked(),
                                  plus=self.palm_dirsagprox_rb.isChecked(),
                                  minus=self.palm_dirsagdist_rb.isChecked()
                                  )
        directions = [direction_hor, direction_ver, direction_sag]
        return directions

    def getcurrentrootdirections(self):
        direction_hor = Direction(axis=Direction.HORIZONTAL,
                                  axisselected=self.root_dirhor_cb.isChecked(),
                                  plus=self.root_dirhoripsi_rb.isChecked(),
                                  minus=self.root_dirhorcontra_rb.isChecked()
                                  )
        direction_ver = Direction(axis=Direction.VERTICAL,
                                  axisselected=self.root_dirver_cb.isChecked(),
                                  plus=self.root_dirverup_rb.isChecked(),
                                  minus=self.root_dirverdown_rb.isChecked()
                                  )
        direction_sag = Direction(axis=Direction.SAGITTAL,
                                  axisselected=self.root_dirsag_cb.isChecked(),
                                  plus=self.root_dirsagprox_rb.isChecked(),
                                  minus=self.root_dirsagdist_rb.isChecked()
                                  )
        directions = [direction_hor, direction_ver, direction_sag]
        return directions

    def setcurrentpalmdirection(self, directions_list):
        if directions_list is not None:
            hor_direction = [axis_dir for axis_dir in directions_list if axis_dir.axis == Direction.HORIZONTAL][0]
            ver_direction = [axis_dir for axis_dir in directions_list if axis_dir.axis == Direction.VERTICAL][0]
            sag_direction = [axis_dir for axis_dir in directions_list if axis_dir.axis == Direction.SAGITTAL][0]

            self.palm_dirhor_cb.setChecked(hor_direction.axisselected)
            if hor_direction.axisselected:
                self.palm_dirhoripsi_rb.setChecked(hor_direction.plus)
                self.palm_dirhorcontra_rb.setChecked(hor_direction.minus)

            self.palm_dirver_cb.setChecked(ver_direction.axisselected)
            if ver_direction.axisselected:
                self.palm_dirverup_rb.setChecked(ver_direction.plus)
                self.palm_dirverdown_rb.setChecked(ver_direction.minus)

            self.palm_dirsag_cb.setChecked(sag_direction.axisselected)
            if sag_direction.axisselected:
                self.palm_dirsagprox_rb.setChecked(sag_direction.plus)
                self.palm_dirsagdist_rb.setChecked(sag_direction.minus)
            
    def setcurrentrootdirection(self, directions_list):
        if directions_list is not None:
            hor_direction = [axis_dir for axis_dir in directions_list if axis_dir.axis == Direction.HORIZONTAL][0]
            ver_direction = [axis_dir for axis_dir in directions_list if axis_dir.axis == Direction.VERTICAL][0]
            sag_direction = [axis_dir for axis_dir in directions_list if axis_dir.axis == Direction.SAGITTAL][0]

            self.root_dirhor_cb.setChecked(hor_direction.axisselected)
            if hor_direction.axisselected:
                self.root_dirhoripsi_rb.setChecked(hor_direction.plus)
                self.root_dirhorcontra_rb.setChecked(hor_direction.minus)

            self.root_dirver_cb.setChecked(ver_direction.axisselected)
            if ver_direction.axisselected:
                self.root_dirverup_rb.setChecked(ver_direction.plus)
                self.root_dirverdown_rb.setChecked(ver_direction.minus)
                
            self.root_dirsag_cb.setChecked(sag_direction.axisselected)
            if sag_direction.axisselected:
                self.root_dirsagprox_rb.setChecked(sag_direction.plus)
                self.root_dirsagdist_rb.setChecked(sag_direction.minus)
                

    def getcurrentlinkedmoduletype(self):
        switch_dict = self.y_existingmod_switch.getvalue()
        if switch_dict[1]:
            return ModuleTypes.LOCATION
        elif switch_dict[2]:
            return ModuleTypes.MOVEMENT
        else:
            return None

    def getcurrentlinkedmoduleids(self):
        selected_indexes = self.existingmod_listview.selectionModel().selectedIndexes()
        # if len(selected_indexes) > 1:
        #     print("error: more than one index is selected")
        # el
        if len(selected_indexes) == 0:
            selected_ids = [0.0]
        else:
            selected_ids = []
            for k in range(len(selected_indexes)):
                selected_ids.append(self.existingmodule_listmodel.itemFromIndex(selected_indexes[k]).module.uniqueid)
            # return self.existingmodule_listmodel.itemFromIndex(selected_indexes[0]).module.uniqueid
        return selected_ids

    def setcurrentlinkedmoduleinfo(self, linkedmoduleids, linkedmoduletype):
        self.existingmod_listview.clearSelection()
        self.setcurrentlinkedmoduletype(linkedmoduletype)
        if linkedmoduleids is not None:
            modelitems = self.existingmodule_listmodel.finditemswithuniqueIDs(linkedmoduleids)
            modelindexes = [self.existingmodule_listmodel.indexFromItem(item) for item in modelitems]
            for idx in modelindexes:
                self.existingmod_listview.selectionModel().select(idx, QItemSelectionModel.Select)
            if len(self.existingmod_listview.selectionModel().selectedIndexes()) > 0:
                self.y_existingmod_radio.setChecked(True)

    def setcurrentlinkedmoduletype(self, moduletype):
        selectiondict = {
            1: moduletype == ModuleTypes.LOCATION,
            2: moduletype == ModuleTypes.MOVEMENT
        }
        self.y_existingmod_switch.setvalue(selectiondict)
        self.update_existingmodule_list(selectiondict)

    def clear_group_buttons(self, buttongroup):
        buttongroup.setExclusive(False)

        for b in buttongroup.buttons():
            b.setChecked(False)
            b.setEnabled(True)

        buttongroup.setExclusive(True)

    def clear_direction_buttons(self):
        for cb in [self.palm_dirhor_cb, self.palm_dirver_cb, self.palm_dirsag_cb,
                   self.root_dirhor_cb, self.root_dirver_cb, self.root_dirsag_cb]:
            cb.setChecked(False)
        for grp in [self.palm_dirhor_group, self.palm_dirver_group, self.palm_dirsag_group,
                    self.root_dirhor_group, self.root_dirver_group, self.root_dirsag_group]:
            self.clear_group_buttons(grp)

        for grpbox in [self.palm_dirhor_box, self.palm_dirver_box, self.palm_dirsag_box,
                       self.root_dirhor_box, self.root_dirver_box, self.root_dirsag_box]:
            grpbox.setEnabled(True)

    def clear(self):
        self.clear_direction_buttons()
        # self.clear_distance_buttons()

    def desiredwidth(self):
        return 500

    def desiredheight(self):
        return 700


class OrientationRadioButton(QRadioButton):

    def __init__(self, text, **kwargs):
        super().__init__(text, **kwargs)

    def setChecked(self, checked):
        if checked and self.group() is not None:
            self.group().previously_checked = self
        super().setChecked(checked)


class OrientationButtonGroup(QButtonGroup):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # in order to compare new checked button with previously-checked button
        self.previously_checked = None

        self.buttonClicked.connect(self.handle_button_clicked)

    def handle_button_clicked(self, btn):
        if self.previously_checked == btn:
            # user clicked an already-selected button; we'll uncheck it
            self.setExclusive(False)
            btn.setChecked(False)
            self.setExclusive(True)
            self.previously_checked = None
        else:
            # user clicked a previously-unselected button
            self.previously_checked = btn
