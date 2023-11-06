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
    QPushButton, QTabWidget, QWidget
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
    MannerRelation,
    Distance,
    Direction,
    RelationX,
    RelationY,
    ModuleTypes,
    ContactRelation,
    ContactType,
    BodypartInfo
)
from models.relation_models import ModuleLinkingListModel
from models.location_models import BodypartTreeModel
from gui.modulespecification_widgets import ModuleSpecificationPanel
from gui.bodypartspecification_dialog import BodypartSelectorDialog
from gui.helper_widget import OptionSwitch
from constant import HAND, ARM, LEG


class NonManualSpecificationPanel(ModuleSpecificationPanel):
    timingintervals_inherited = pyqtSignal(list)

    def __init__(self, moduletoload=None, **kwargs):
        super().__init__(**kwargs)
        self.islinkedtopoint = False
        self.islinkedtointerval = False

        main_layout = QVBoxLayout()

        # 'All neutral' checkbox
        allneutral_layout = self.create_all_neutral()
        main_layout.addLayout(allneutral_layout)

        # different major non manual tabs
        major_nm_list = ["Shoulder", "Body", "Head", "Eye gaze", "Facial expression", "Mouth", "Air"]
        nested_tab = [False,         False,  False,  False,      True,                True,    False]

        self.create_major_tabs(major_nm_list, nested_tab)
        main_layout.addWidget(self.major_tab_widget)

        """
        # tabs
        major_tabs = QTabWidget()
        self.shoulder = QWidget()
        self.body = QWidget()
        self.head = QWidget()
        self.eye = QWidget()
        self.facial = QWidget()
        self.mouth = QWidget()
        self.air = QWidget()

        major_tabs.resize(300,200)

        # Add tabs
        major_tabs.addTab(self.shoulder, "Shoulder")
        major_tabs.addTab(self.body, "Body")
        major_tabs.addTab(self.head, "Head")
        major_tabs.addTab(self.eye, "Eye gaze")
        major_tabs.addTab(self.facial, "Facial expression")
        major_tabs.addTab(self.mouth, "Mouth")
        major_tabs.addTab(self.air, "Air")
        main_layout.addWidget(major_tabs)

        # Tab contents
        self.shoulder.layout = QVBoxLayout()

        self.shoulder.layout.addWidget(QCheckBox("This section is neutral"))

        self.detailed_specs()
        self.shoulder.setLayout(self.shoulder.layout)
        """


        """
        # create side-by-side layout for selecting the two elements that are being related
        xandy_layout = self.create_xandy_layout()
        main_layout.addLayout(xandy_layout)

        # create side-by-side layout for specifying relation
        relations_layout = QHBoxLayout()

        # create stacked layout for specifying contact and contact manner
        contactandmanner_layout = self.create_contactandmanner_layout()

        relations_layout.addLayout(contactandmanner_layout)

        # create side-by-side layout for specifying direction of relation
        direction_box = self.create_direction_box()
        relations_layout.addWidget(direction_box)

        # create side-by-side layout for specifying distance
        self.distance_box = self.create_distance_box()
        relations_layout.addWidget(self.distance_box)

        main_layout.addLayout(relations_layout)

        # set according to the existing module being loaded
        if moduletoload is not None and isinstance(moduletoload, RelationModule):
            self.setvalues(moduletoload)
            self.existingkey = moduletoload.uniqueid

        self.check_enable_allsubmenus()
        """
        self.setLayout(main_layout)

    def create_all_neutral(self):
        # create a checkbox that greys out all subcomponents in non-manual
        neutral_layout = QVBoxLayout()
        checkbox = QCheckBox("All sections are neutral")
        neutral_layout.addWidget(checkbox)
        return neutral_layout

    def create_major_tabs(self, major_list, nest_list):
        """
        Populate major non-manual articulators like shoulder, body and head
        Args:
            major_list: list of str. list of all tab labels
            nest_list: list of bool. whether nested tab is needed. for example 'mouth' needs subcategory so nest=Ture
        """
        self.major_tab_widget = QTabWidget()
        for category, nested in zip(major_list, nest_list):
            self.add_tab(f"{category}", f"This is the content of {category}")

    def add_tab(self, label, content):
        """
        Deal with the mundane hassle of adding tab gui
        Args:
            label: str. label of a tab
            content: QVBoxLayout
        """
        tab = QWidget()
        tab.layout = QVBoxLayout()
        tab.layout.addWidget(QCheckBox("This section is neutral"))
        tab.setLayout(tab.layout)

        layout = QVBoxLayout()
        tab.setLayout(layout)
        self.major_tab_widget.addTab(tab, label)

    def detailed_specs(self):
        row1 = QHBoxLayout()
        row2 = QHBoxLayout()
        row3 = QHBoxLayout()
        dynamic_group = QGroupBox("Static / Dynamic")
        subpart_group = QGroupBox("Sub-part(s)")
        actions_group = QGroupBox("Action / state")
        mvmtchar_group = QGroupBox("Movement characteristics")
        row1.addWidget(dynamic_group)
        row1.addWidget(subpart_group)
        row2.addWidget(actions_group)
        row3.addWidget(mvmtchar_group)
        self.shoulder.layout.addLayout(row1)
        self.shoulder.layout.addLayout(row2)
        self.shoulder.layout.addLayout(row3)

    def validity_check(self):
        selectionsvalid = self.x_group.checkedButton() and self.y_group.checkedButton()
        warningmessage = "" if selectionsvalid else "Requires both an X and a Y selection."
        return selectionsvalid, warningmessage

    def timinglinknotification(self, haspoint, hasinterval):
        self.islinkedtopoint = haspoint
        self.islinkedtointerval = hasinterval
        self.check_enable_allsubmenus()

    def getsavedmodule(self, articulators, timingintervals, addedinfo, inphase):

        relmod = RelationModule(relationx=self.getcurrentx(),
                                relationy=self.getcurrenty(),
                                bodyparts_dict=self.bodyparts_dict,
                                contactrel=self.getcurrentcontact(),
                                xy_crossed=self.crossed_cb.isChecked(),
                                xy_linked=self.linked_cb.isChecked(),
                                directionslist=self.getcurrentdirections(),
                                articulators=articulators,
                                timingintervals=timingintervals,
                                addedinfo=addedinfo,
                                )
        if self.existingkey is not None:
            relmod.uniqueid = self.existingkey
        else:
            self.existingkey = relmod.uniqueid
        return relmod

    # create side-by-side layout for specifying distance
    def create_distance_box(self):
        distance_box = QGroupBox("Distance between X and Y")
        distance_layout = QHBoxLayout()

        # create layout for horizontal distance options
        self.dishor_box = QGroupBox()
        self.dishor_label = QLabel("Horizontal")
        self.dishorclose_rb = RelationRadioButton("Close")
        self.dishormed_rb = RelationRadioButton("Med.")
        self.dishorfar_rb = RelationRadioButton("Far")
        self.dishor_group = RelationButtonGroup()
        self.dishor_group.buttonToggled.connect(self.handle_distancebutton_toggled)
        dis_hor_layout = self.create_axis_layout(self.dishorclose_rb,
                                                 self.dishormed_rb,
                                                 self.dishorfar_rb,
                                                 self.dishor_group,
                                                 axis_label=self.dishor_label)
        self.dishor_box.setLayout(dis_hor_layout)
        distance_layout.addWidget(self.dishor_box)

        # create layout for vertical distance options
        self.disver_box = QGroupBox()
        self.disver_label = QLabel("Vertical")
        self.disverclose_rb = RelationRadioButton("Close")
        self.disvermed_rb = RelationRadioButton("Med.")
        self.disverfar_rb = RelationRadioButton("Far")
        self.disver_group = RelationButtonGroup()
        self.disver_group.buttonToggled.connect(self.handle_distancebutton_toggled)
        dis_ver_layout = self.create_axis_layout(self.disverclose_rb,
                                                 self.disvermed_rb,
                                                 self.disverfar_rb,
                                                 self.disver_group,
                                                 axis_label=self.disver_label)
        self.disver_box.setLayout(dis_ver_layout)
        distance_layout.addWidget(self.disver_box)

        # create layout for sagittal direction options
        self.dissag_box = QGroupBox()
        self.dissag_label = QLabel("Sagittal")
        self.dissagclose_rb = RelationRadioButton("Close")
        self.dissagmed_rb = RelationRadioButton("Med.")
        self.dissagfar_rb = RelationRadioButton("Far")
        self.dissag_group = RelationButtonGroup()
        self.dissag_group.buttonToggled.connect(self.handle_distancebutton_toggled)
        dis_sag_layout = self.create_axis_layout(self.dissagclose_rb,
                                                 self.dissagmed_rb,
                                                 self.dissagfar_rb,
                                                 self.dissag_group,
                                                 axis_label=self.dissag_label)
        self.dissag_box.setLayout(dis_sag_layout)
        distance_layout.addWidget(self.dissag_box)

        distance_box.setLayout(distance_layout)
        return distance_box

    # if 'movement' is selected for Y,
    #  then Contact, Manner, Direction, and Distance menus are all inactive below
    def check_enable_contact(self):
        self.contact_box.setEnabled(not(self.y_existingmod_radio.isChecked() and
                                    self.getcurrentlinkedmoduletype() == ModuleTypes.MOVEMENT))

    # 1. Contact manner can only be coded if
    #   (a) 'contact' is selected AND
    #   (b) the module is linked to an interval
    # 2. OR Can also be available if
    #   (a) neither 'contact' nor 'no contact' is selected AND
    #   (b) there are no selections in manner or distance
    # 3. BUT if 'movement' is selected for Y,
    #   then Contact, Manner, Direction, and Distance menus are all inactive below
    def check_enable_manner(self):
        meetscondition1 = self.contact_rb.isChecked() and self.islinkedtointerval

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
    #  then Contact, Manner, Direction, and Distance menus are all inactive below
    def check_enable_direction(self):
        enable_direction = not (self.y_existingmod_radio.isChecked() and
                                self.getcurrentlinkedmoduletype() == ModuleTypes.MOVEMENT)
        for box in [self.dirhor_box, self.dirver_box, self.dirsag_box]:
            box.setEnabled(enable_direction)

    def handle_distancebutton_toggled(self, btn, ischecked):
        if btn.group().checkedButton() is not None:
            self.nocontact_rb.setChecked(True)

    # create layout for distance or direction options on a particular axis
    def create_axis_layout(self, radio1, radio2, radio3, radiogroup, axis_cb=None, axis_label=None):
        axis_layout = QVBoxLayout()
        axisoptions_spacedlayout = QHBoxLayout()
        axisoptions_layout = QVBoxLayout()
        radiogroup.addButton(radio1)
        radiogroup.addButton(radio2)
        radiogroup.addButton(radio3)
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
        axisoptions_layout.addWidget(radio3)
        axisoptions_spacedlayout.addLayout(axisoptions_layout)
        axis_layout.addLayout(axisoptions_spacedlayout)

        return axis_layout

    def handle_axiscb_toggled(self, ischecked, radiogroup):
        isdirgroup = radiogroup in [self.dirhor_group, self.dirver_group, self.dirsag_group]
        contactchecked = self.contact_rb.isChecked()

        for btn in radiogroup.buttons():
            btn.setEnabled(ischecked and (isdirgroup or not contactchecked))

    def handle_axisgroup_toggled(self, rb, ischecked, axis_cb):
        if not ischecked:
            # don't need to do anything special
            return

        # ensure the parent is checked
        axis_cb.setChecked(True)

    # create side-by-side layout for specifying direction of relation
    def create_direction_box(self):
        direction_box = QGroupBox("Direction of relation")
        direction_layout = QVBoxLayout()
        direction_crossedlinked_layout = QHBoxLayout()
        direction_sublayout = QHBoxLayout()

        # create layout for crossed or linked relations
        self.crossed_cb = QCheckBox("X and Y are crossed")
        self.linked_cb = QCheckBox("X and Y are linked")
        direction_crossedlinked_layout.addWidget(self.crossed_cb)
        direction_crossedlinked_layout.addWidget(self.linked_cb)
        direction_layout.addLayout(direction_crossedlinked_layout)

        # create layout for horizontal direction options
        self.dirhor_box = QGroupBox()
        self.dirhor_cb = QCheckBox("Horizontal")
        self.dirhoripsi_rb = RelationRadioButton("X ipsilateral to Y")
        self.dirhorcontra_rb = RelationRadioButton("X contralateral to Y")
        self.dirhorinline_rb = RelationRadioButton("X in line with Y")
        self.dirhor_group = RelationButtonGroup()
        dir_hor_layout = self.create_axis_layout(self.dirhoripsi_rb,
                                                 self.dirhorcontra_rb,
                                                 self.dirhorinline_rb,
                                                 self.dirhor_group,
                                                 axis_cb=self.dirhor_cb)
        self.dirhor_box.setLayout(dir_hor_layout)
        direction_sublayout.addWidget(self.dirhor_box)

        # create layout for vertical direction options
        self.dirver_box = QGroupBox()
        self.dirver_cb = QCheckBox("Vertical")
        self.dirverabove_rb = RelationRadioButton("X above Y")
        self.dirverbelow_rb = RelationRadioButton("X below Y")
        self.dirverinline_rb = RelationRadioButton("X in line with Y")
        self.dirver_group = RelationButtonGroup()
        dir_ver_layout = self.create_axis_layout(self.dirverabove_rb,
                                                 self.dirverbelow_rb,
                                                 self.dirverinline_rb,
                                                 self.dirver_group,
                                                 axis_cb=self.dirver_cb)
        self.dirver_box.setLayout(dir_ver_layout)
        direction_sublayout.addWidget(self.dirver_box)

        # create layout for sagittal direction options
        self.dirsag_box = QGroupBox()
        self.dirsag_cb = QCheckBox("Sagittal")
        self.dirsagdist_rb = RelationRadioButton("X distal to Y")
        self.dirsagprox_rb = RelationRadioButton("X proximal to Y")
        self.dirsaginline_rb = RelationRadioButton("X in line with Y")
        self.dirsag_group = RelationButtonGroup()
        dir_sag_layout = self.create_axis_layout(self.dirsagdist_rb,
                                                 self.dirsagprox_rb,
                                                 self.dirsaginline_rb,
                                                 self.dirsag_group,
                                                 axis_cb=self.dirsag_cb)
        self.dirsag_box.setLayout(dir_sag_layout)
        direction_sublayout.addWidget(self.dirsag_box)

        direction_layout.addLayout(direction_sublayout)
        direction_box.setLayout(direction_layout)
        return direction_box

    def create_contactandmanner_layout(self):
        contactandmanner_layout = QHBoxLayout()

        # create layout for specifying contact & manner
        self.contact_box = self.create_contact_box()
        contactandmanner_layout.addWidget(self.contact_box)

        return contactandmanner_layout

    # create layout for specifying contact & manner
    def create_contact_box(self):
        contact_box = QGroupBox("Contact")
        contact_box_layout = QHBoxLayout()
        contact_layout = QVBoxLayout()
        contacttype_spacedlayout = QHBoxLayout()
        contacttype_layout = QVBoxLayout()
        contactother_layout = QHBoxLayout()

        self.contact_rb = RelationRadioButton("Contact")
        self.nocontact_rb = RelationRadioButton("No contact")
        self.contact_group = RelationButtonGroup()
        self.contact_group.addButton(self.contact_rb)
        self.contact_group.addButton(self.nocontact_rb)
        self.contact_group.buttonToggled.connect(self.handle_contactgroup_toggled)

        self.contactlight_rb = RelationRadioButton("Light")
        self.contactfirm_rb = RelationRadioButton("Firm")
        self.contactother_rb = RelationRadioButton("Other")
        self.contacttype_group = RelationButtonGroup()
        self.contacttype_group.addButton(self.contactlight_rb)
        self.contacttype_group.addButton(self.contactfirm_rb)
        self.contacttype_group.addButton(self.contactother_rb)
        self.contacttype_group.buttonToggled.connect(self.handle_contacttypegroup_toggled)
        self.contact_other_text = QLineEdit()
        self.contact_other_text.setPlaceholderText("Specify")
        self.contact_other_text.textEdited.connect(lambda txt: self.handle_othertext_edited(txt, self.contactother_rb))
        contactother_layout.addWidget(self.contactother_rb)
        contactother_layout.addWidget(self.contact_other_text)
        contacttype_layout.addWidget(self.contactlight_rb)
        contacttype_layout.addWidget(self.contactfirm_rb)
        contacttype_layout.addLayout(contactother_layout)
        contacttype_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        contacttype_spacedlayout.addLayout(contacttype_layout)

        contact_layout.addWidget(self.contact_rb)
        contact_layout.addLayout(contacttype_spacedlayout)
        contact_layout.addWidget(self.nocontact_rb)
        contact_box_layout.addLayout(contact_layout)

        # create layout for specifying contact manner
        self.manner_box = self.create_manner_box()
        contact_box_layout.addWidget(self.manner_box)

        contact_box.setLayout(contact_box_layout)
        return contact_box

    def check_enable_allsubmenus(self):
        self.check_enable_contact()
        self.check_enable_distance()
        self.check_enable_direction()
        self.check_enable_manner()

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

    # create layout for specifying contact manner
    def create_manner_box(self):
        manner_box = QGroupBox("Contact manner")
        manner_layout = QVBoxLayout()
        self.holding_rb = RelationRadioButton("Holding")
        self.continuous_rb = RelationRadioButton("Continuous")
        self.intermittent_rb = RelationRadioButton("Intermittent")
        self.manner_group = RelationButtonGroup()
        self.manner_group.buttonToggled.connect(self.handle_mannerbutton_toggled)
        self.manner_group.addButton(self.holding_rb)
        self.manner_group.addButton(self.continuous_rb)
        self.manner_group.addButton(self.intermittent_rb)
        manner_layout.addWidget(self.holding_rb)
        manner_layout.addWidget(self.continuous_rb)
        manner_layout.addWidget(self.intermittent_rb)
        manner_layout.addStretch()
        manner_box.setLayout(manner_layout)
        return manner_box

    def handle_mannerbutton_toggled(self, btn, ischecked):
        if btn.group().checkedButton() is not None:
            self.contact_rb.setChecked(True)

    def create_xandy_layout(self):
        xandy_layout = QHBoxLayout()

        # create layout for selecting the "X" item of the relation
        x_box = self.create_x_box()
        xandy_layout.addWidget(x_box)

        # create layout for selecting the "Y" item of the relation
        y_box = self.create_y_box()
        xandy_layout.addWidget(y_box)

        # create layout for initiating selection of handpart(s), armpart(s), and/or legpart(s) involved in the X-Y relation
        bodyparts_box = self.create_bodyparts_box()
        xandy_layout.addWidget(bodyparts_box)

        return xandy_layout

    # create layout for initiating selection of body parts involved in the X-Y relation
    def create_bodyparts_box(self):
        self.bodyparts_dict = {
            HAND: {
                1: BodypartInfo(bodyparttype=HAND, bodyparttreemodel=BodypartTreeModel(bodyparttype=HAND)),
                2: BodypartInfo(bodyparttype=HAND, bodyparttreemodel=BodypartTreeModel(bodyparttype=HAND))
            },
            ARM: {
                1: BodypartInfo(bodyparttype=ARM, bodyparttreemodel=BodypartTreeModel(bodyparttype=ARM)),
                2: BodypartInfo(bodyparttype=ARM, bodyparttreemodel=BodypartTreeModel(bodyparttype=ARM))
            },
            LEG: {
                1: BodypartInfo(bodyparttype=LEG, bodyparttreemodel=BodypartTreeModel(bodyparttype=LEG)),
                2: BodypartInfo(bodyparttype=LEG, bodyparttreemodel=BodypartTreeModel(bodyparttype=LEG))
            }
        }

        bodyparts_box = QGroupBox("Body parts")
        box_layout = QVBoxLayout()

        handpart_layout = QHBoxLayout()
        handpart_label = QLabel("For H1 and/or H2:")
        self.handpart_button = QPushButton("Specify hand parts")
        self.handpart_button.clicked.connect(self.handle_handpartbutton_clicked)
        self.check_enable_handpartbutton()
        handpart_layout.addWidget(handpart_label)
        handpart_layout.addWidget(self.handpart_button)

        armpart_layout = QHBoxLayout()
        armpart_label = QLabel("For Arm1 and/or Arm2:")
        self.armpart_button = QPushButton("Specify arm parts")
        self.armpart_button.clicked.connect(self.handle_armpartbutton_clicked)
        self.check_enable_armpartbutton()
        armpart_layout.addWidget(armpart_label)
        armpart_layout.addWidget(self.armpart_button)

        legpart_layout = QHBoxLayout()
        legpart_label = QLabel("For Leg1 and/or Leg2:")
        self.legpart_button = QPushButton("Specify leg parts")
        self.legpart_button.clicked.connect(self.handle_legpartbutton_clicked)
        self.check_enable_legpartbutton()
        legpart_layout.addWidget(legpart_label)
        legpart_layout.addWidget(self.legpart_button)

        box_layout.addLayout(handpart_layout)
        box_layout.addLayout(armpart_layout)
        box_layout.addLayout(legpart_layout)
        bodyparts_box.setLayout(box_layout)
        return bodyparts_box

    def check_enable_handpartbutton(self):
        h1_selected = self.x_h1_radio.isChecked() or self.x_both_radio.isChecked()
        h2_selected = self.x_h2_radio.isChecked() or self.x_both_radio.isChecked() or self.y_h2_radio.isChecked()
        self.handpart_button.setEnabled(h1_selected or h2_selected)

    def check_enable_armpartbutton(self):
        a1_selected = self.x_a1_radio.isChecked()
        a2_selected = self.x_a2_radio.isChecked() or self.y_a2_radio.isChecked()
        self.armpart_button.setEnabled(a1_selected or a2_selected)

    def check_enable_legpartbutton(self):
        l1_selected = self.x_l1_radio.isChecked() or self.y_l1_radio.isChecked()
        l2_selected = self.x_l2_radio.isChecked() or self.y_l2_radio.isChecked()
        self.legpart_button.setEnabled(l1_selected or l2_selected)

    def handle_handpartbutton_clicked(self):
        bodyparttype = HAND
        h1label = ""
        h2label = ""
        if self.x_h1_radio.isChecked():
            h1label = "X"
        elif self.x_h2_radio.isChecked():
            h2label = "X"
        elif self.x_both_radio.isChecked():
            h1label = "part of X"
            h2label = "part of X"
        if self.y_h2_radio.isChecked():
            h2label = "Y"
        handpart_selector = BodypartSelectorDialog(bodyparttype=bodyparttype, bodypart1label=h1label, bodypart2label=h2label, bodypart1infotoload=self.bodyparts_dict[bodyparttype][1], bodypart2infotoload=self.bodyparts_dict[bodyparttype][2], parent=self)
        handpart_selector.bodyparts_saved.connect(self.handle_bodyparts_saved)
        handpart_selector.exec_()

    def handle_armpartbutton_clicked(self):
        bodyparttype = ARM
        a1label = ""
        a2label = ""
        if self.x_a1_radio.isChecked():
            a1label = "X"
        elif self.x_a2_radio.isChecked():
            a2label = "X"
        if self.y_a2_radio.isChecked():
            a2label = "Y"
        armpart_selector = BodypartSelectorDialog(bodyparttype=bodyparttype, bodypart1label=a1label, bodypart2label=a2label, bodypart1infotoload=self.bodyparts_dict[bodyparttype][1], bodypart2infotoload=self.bodyparts_dict[bodyparttype][2], parent=self)
        armpart_selector.bodyparts_saved.connect(self.handle_bodyparts_saved)
        armpart_selector.exec_()

    def handle_legpartbutton_clicked(self):
        bodyparttype = LEG
        l1label = ""
        l2label = ""
        if self.x_l1_radio.isChecked():
            l1label = "X"
        elif self.x_l2_radio.isChecked():
            l2label = "X"
        if self.y_l1_radio.isChecked():
            l1label = "Y"
        elif self.y_l2_radio.isChecked():
            l2label = "Y"
        legpart_selector = BodypartSelectorDialog(bodyparttype=bodyparttype, bodypart1label=l1label, bodypart2label=l2label, bodypart1infotoload=self.bodyparts_dict[bodyparttype][1], bodypart2infotoload=self.bodyparts_dict[bodyparttype][2], parent=self)
        legpart_selector.bodyparts_saved.connect(self.handle_bodyparts_saved)
        legpart_selector.exec_()

    def handle_bodyparts_saved(self, bodypart1info, bodypart2info):
        self.bodyparts_dict[bodypart1info.bodyparttype][1] = bodypart1info
        self.bodyparts_dict[bodypart2info.bodyparttype][2] = bodypart2info

    # create layout for selecting the "X" item of the relation
    def create_x_box_orig(self):
        x_box = QGroupBox("Select X")
        x_layout = QVBoxLayout()
        x_other_layout = QHBoxLayout()
        x_bothconnected_layout = QHBoxLayout()
        self.x_group = QButtonGroup()
        self.x_group.buttonToggled.connect(self.handle_xgroup_toggled)
        self.x_h1_radio = RelationRadioButton("H1")
        self.x_h2_radio = RelationRadioButton("H2")
        self.x_both_radio = RelationRadioButton("Both hands")
        self.x_bothconnected_cb = QCheckBox("As a connected unit")
        self.x_bothconnected_cb.toggled.connect(self.handle_xconnected_toggled)
        self.x_a1_radio = RelationRadioButton("Arm1")
        self.x_a2_radio = RelationRadioButton("Arm2")
        self.x_l1_radio = RelationRadioButton("Leg1")
        self.x_l2_radio = RelationRadioButton("Leg2")
        self.x_other_radio = RelationRadioButton("Other")
        self.x_other_text = QLineEdit()
        self.x_other_text.setPlaceholderText("Specify")
        self.x_other_text.textEdited.connect(lambda txt: self.handle_othertext_edited(txt, self.x_other_radio))
        self.x_group.addButton(self.x_h1_radio)
        self.x_group.addButton(self.x_h2_radio)
        self.x_group.addButton(self.x_both_radio)
        self.x_group.addButton(self.x_a1_radio)
        self.x_group.addButton(self.x_a2_radio)
        self.x_group.addButton(self.x_l1_radio)
        self.x_group.addButton(self.x_l2_radio)
        self.x_group.addButton(self.x_other_radio)
        x_layout.addWidget(self.x_h1_radio)
        x_layout.addWidget(self.x_h2_radio)
        x_layout.addWidget(self.x_both_radio)
        x_bothconnected_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        x_bothconnected_layout.addWidget(self.x_bothconnected_cb)
        x_layout.addLayout(x_bothconnected_layout)
        x_layout.addWidget(self.x_a1_radio)
        x_layout.addWidget(self.x_a2_radio)
        x_layout.addWidget(self.x_l1_radio)
        x_layout.addWidget(self.x_l2_radio)
        x_other_layout.addWidget(self.x_other_radio)
        x_other_layout.addWidget(self.x_other_text)
        x_layout.addLayout(x_other_layout)
        x_box.setLayout(x_layout)
        return x_box

    # create layout for selecting the "X" item of the relation
    def create_x_box(self):
        x_box = QGroupBox("Select X")
        x_layout = QVBoxLayout()
        x_layout_left = QVBoxLayout()
        x_layout_right = QVBoxLayout()
        x_layout_leftandright = QHBoxLayout()
        x_other_layout = QHBoxLayout()
        x_bothconnected_layout = QHBoxLayout()
        self.x_group = QButtonGroup()
        self.x_group.buttonToggled.connect(self.handle_xgroup_toggled)
        self.x_h1_radio = RelationRadioButton("H1")
        self.x_h2_radio = RelationRadioButton("H2")
        self.x_both_radio = RelationRadioButton("Both hands")
        self.x_bothconnected_cb = QCheckBox("As a connected unit")
        self.x_bothconnected_cb.toggled.connect(self.handle_xconnected_toggled)
        self.x_a1_radio = RelationRadioButton("Arm1")
        self.x_a2_radio = RelationRadioButton("Arm2")
        self.x_l1_radio = RelationRadioButton("Leg1")
        self.x_l2_radio = RelationRadioButton("Leg2")
        self.x_other_radio = RelationRadioButton("Other")
        self.x_other_text = QLineEdit()
        self.x_other_text.setPlaceholderText("Specify")
        self.x_other_text.textEdited.connect(lambda txt: self.handle_othertext_edited(txt, self.x_other_radio))
        self.x_group.addButton(self.x_h1_radio)
        self.x_group.addButton(self.x_h2_radio)
        self.x_group.addButton(self.x_both_radio)
        self.x_group.addButton(self.x_a1_radio)
        self.x_group.addButton(self.x_a2_radio)
        self.x_group.addButton(self.x_l1_radio)
        self.x_group.addButton(self.x_l2_radio)
        self.x_group.addButton(self.x_other_radio)
        x_layout_left.addWidget(self.x_h1_radio)
        x_layout_left.addWidget(self.x_h2_radio)
        x_layout_left.addWidget(self.x_both_radio)
        x_bothconnected_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        x_bothconnected_layout.addWidget(self.x_bothconnected_cb)
        x_layout_left.addLayout(x_bothconnected_layout)
        x_layout_right.addWidget(self.x_a1_radio)
        x_layout_right.addWidget(self.x_a2_radio)
        x_layout_right.addWidget(self.x_l1_radio)
        x_layout_right.addWidget(self.x_l2_radio)
        x_other_layout.addWidget(self.x_other_radio)
        x_other_layout.addWidget(self.x_other_text)
        x_layout_leftandright.addLayout(x_layout_left)
        x_layout_leftandright.addLayout(x_layout_right)
        x_layout.addLayout(x_layout_leftandright)
        x_layout.addLayout(x_other_layout)
        x_box.setLayout(x_layout)
        return x_box

    def handle_xgroup_toggled(self, btn, ischecked):
        selectedbutton = self.x_group.checkedButton()

        # enable "as a connected unit" iff the checked button is "both hands"
        self.x_bothconnected_cb.setEnabled(selectedbutton == self.x_both_radio)

        # enable "specify" text box iff the checked button is "other"
        self.x_other_text.setEnabled(selectedbutton == self.x_other_radio)

        # check whether specify bodypart buttons should be enabled
        self.check_enable_handpartbutton()
        self.check_enable_armpartbutton()
        self.check_enable_legpartbutton()

    def handle_ygroup_toggled(self, btn, ischecked):
        selectedbutton = self.y_group.checkedButton()

        # enable existing location/movement switch and existing module list view
        # iff the checked button is "existing module"
        self.y_existingmod_switch.setEnabled(selectedbutton == self.y_existingmod_radio)
        self.existingmod_listview.setEnabled(selectedbutton == self.y_existingmod_radio)

        # enable "specify" text box iff the checked button is "other"
        self.y_other_text.setEnabled(selectedbutton == self.y_other_radio)

        # check whether bodypart buttons should be enabled
        self.check_enable_handpartbutton()
        self.check_enable_armpartbutton()
        self.check_enable_legpartbutton()

        # check whether submenus (contact, manner, direction, distance) should be enabled
        self.check_enable_allsubmenus()

    def handle_xconnected_toggled(self, ischecked):
        if not ischecked:
            # don't need to do anything special
            return

        # ensure the parent is checked
        self.x_both_radio.setChecked(True)

    def handle_othertext_edited(self, txt, parentradiobutton):
        if txt == "":
            # don't need to do anything special
            return

        # ensure the parent is checked
        parentradiobutton.setChecked(True)

    # create layout for selecting the "Y" item of the relation
    def create_y_box_orig(self):
        y_box = QGroupBox("Select Y")
        y_layout = QVBoxLayout()
        y_existingmodule_layout = QHBoxLayout()
        y_list_layout = QHBoxLayout()
        y_other_layout = QHBoxLayout()

        self.y_group = QButtonGroup()
        self.y_group.buttonToggled.connect(self.handle_ygroup_toggled)
        self.y_h2_radio = RelationRadioButton("H2")
        self.y_a2_radio = RelationRadioButton("Arm2")
        self.y_l1_radio = RelationRadioButton("Leg1")
        self.y_l2_radio = RelationRadioButton("Leg2")
        self.y_existingmod_radio = RelationRadioButton("Existing module:")
        self.y_existingmod_switch = OptionSwitch("Location", "Movement")
        self.existingmod_listview = QListView()
        self.locmodslist = list(self.mainwindow.current_sign.locationmodules.values())
        self.locmodslist = [loc for loc in self.locmodslist if loc.locationtreemodel.locationtype.usesbodylocations()]
        self.locmodnums = self.mainwindow.current_sign.locationmodulenumbers
        self.movmodslist = list(self.mainwindow.current_sign.movementmodules.values())
        self.movmodnums = self.mainwindow.current_sign.movementmodulenumbers
        self.existingmodule_listmodel = ModuleLinkingListModel()
        self.existingmod_listview.setModel(self.existingmodule_listmodel)
        self.y_existingmod_switch.toggled.connect(self.handle_existingmodswitch_toggled)
        self.existingmod_listview.setSelectionMode(QAbstractItemView.MultiSelection)
        self.existingmod_listview.clicked.connect(lambda index: self.handle_existingmod_clicked(index))
        self.y_other_radio = RelationRadioButton("Other")
        self.y_other_text = QLineEdit()
        self.y_other_text.setPlaceholderText("Specify")
        self.y_other_text.textEdited.connect(lambda txt: self.handle_othertext_edited(txt, self.y_other_radio))
        self.y_group.addButton(self.y_h2_radio)
        self.y_group.addButton(self.y_a2_radio)
        self.y_group.addButton(self.y_l1_radio)
        self.y_group.addButton(self.y_l2_radio)
        self.y_group.addButton(self.y_existingmod_radio)
        self.y_group.addButton(self.y_other_radio)

        y_layout.addWidget(self.y_h2_radio)
        y_layout.addWidget(self.y_a2_radio)
        y_layout.addWidget(self.y_l1_radio)
        y_layout.addWidget(self.y_l2_radio)
        y_existingmodule_layout.addWidget(self.y_existingmod_radio)
        y_existingmodule_layout.addWidget(self.y_existingmod_switch)
        y_existingmodule_layout.addStretch()
        y_layout.addLayout(y_existingmodule_layout)
        y_list_layout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        y_list_layout.addWidget(self.existingmod_listview)
        y_layout.addLayout(y_list_layout)
        y_other_layout.addWidget(self.y_other_radio)
        y_other_layout.addWidget(self.y_other_text)
        y_layout.addLayout(y_other_layout)
        y_box.setLayout(y_layout)
        return y_box

    # create layout for selecting the "Y" item of the relation
    def create_y_box(self):
        y_box = QGroupBox("Select Y")
        y_layout = QVBoxLayout()
        y_layout_leftandright = QHBoxLayout()
        y_layout_left = QVBoxLayout()
        y_layout_right = QVBoxLayout()
        y_existingmodule_layout = QHBoxLayout()
        y_list_layout = QHBoxLayout()
        y_other_layout = QHBoxLayout()

        self.y_group = QButtonGroup()
        self.y_group.buttonToggled.connect(self.handle_ygroup_toggled)
        self.y_h2_radio = RelationRadioButton("H2")
        self.y_a2_radio = RelationRadioButton("Arm2")
        self.y_l1_radio = RelationRadioButton("Leg1")
        self.y_l2_radio = RelationRadioButton("Leg2")
        self.y_existingmod_radio = RelationRadioButton("Existing module:")
        self.y_existingmod_switch = OptionSwitch("Location", "Movement")
        self.existingmod_listview = QListView()
        self.locmodslist = list(self.mainwindow.current_sign.locationmodules.values())
        self.locmodslist = [loc for loc in self.locmodslist if loc.locationtreemodel.locationtype.usesbodylocations()]
        self.locmodnums = self.mainwindow.current_sign.locationmodulenumbers
        self.movmodslist = list(self.mainwindow.current_sign.movementmodules.values())
        self.movmodnums = self.mainwindow.current_sign.movementmodulenumbers
        self.existingmodule_listmodel = ModuleLinkingListModel()
        self.existingmod_listview.setModel(self.existingmodule_listmodel)
        self.y_existingmod_switch.toggled.connect(self.handle_existingmodswitch_toggled)
        self.existingmod_listview.setSelectionMode(QAbstractItemView.MultiSelection)
        self.existingmod_listview.clicked.connect(lambda index: self.handle_existingmod_clicked(index))
        self.y_other_radio = RelationRadioButton("Other")
        self.y_other_text = QLineEdit()
        self.y_other_text.setPlaceholderText("Specify")
        self.y_other_text.textEdited.connect(lambda txt: self.handle_othertext_edited(txt, self.y_other_radio))
        self.y_group.addButton(self.y_h2_radio)
        self.y_group.addButton(self.y_a2_radio)
        self.y_group.addButton(self.y_l1_radio)
        self.y_group.addButton(self.y_l2_radio)
        self.y_group.addButton(self.y_existingmod_radio)
        self.y_group.addButton(self.y_other_radio)

        y_layout_left.addWidget(self.y_h2_radio)
        y_layout_left.addWidget(self.y_a2_radio)
        y_layout_left.addWidget(self.y_l1_radio)
        y_layout_left.addWidget(self.y_l2_radio)
        y_existingmodule_layout.addWidget(self.y_existingmod_radio)
        y_existingmodule_layout.addWidget(self.y_existingmod_switch)
        y_existingmodule_layout.addStretch()
        y_layout_right.addLayout(y_existingmodule_layout)
        y_list_layout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        y_list_layout.addWidget(self.existingmod_listview)
        y_layout_right.addLayout(y_list_layout)
        y_other_layout.addWidget(self.y_other_radio)
        y_other_layout.addWidget(self.y_other_text)

        y_layout_leftandright.addLayout(y_layout_left)
        y_layout_leftandright.addLayout(y_layout_right)
        y_layout.addLayout(y_layout_leftandright)
        y_layout.addLayout(y_other_layout)
        y_box.setLayout(y_layout)
        return y_box

    def handle_existingmodswitch_toggled(self, selection_dict):
        if True in selection_dict.values():
            self.y_existingmod_radio.setChecked(True)
        self.update_existingmodule_list(selection_dict)

        self.check_enable_allsubmenus()

    def update_existingmodule_list(self, selection_dict):
        if selection_dict[1]:
            self.existingmodule_listmodel.setmoduleslist(self.locmodslist, self.locmodnums, ModuleTypes.LOCATION)
        elif selection_dict[2]:
            self.existingmodule_listmodel.setmoduleslist(self.movmodslist, self.movmodnums, ModuleTypes.MOVEMENT)
        else:
            self.existingmodule_listmodel.setmoduleslist(None)

    def handle_existingmod_clicked(self, modelindex):
        if modelindex not in self.existingmod_listview.selectedIndexes():
            # don't need to do anything special
            return
        # ensure the parent is checked
        self.y_existingmod_radio.setChecked(True)

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
                    self.x_both_radio.setChecked(True)
                    if linkedfrommodule.inphase >- 3:
                        self.x_bothconnected_cb.setChecked(True)
                elif articulator_dict[1]:
                    self.x_h1_radio.setChecked(True)
                elif articulator_dict[2]:
                    self.x_h2_radio.setChecked(True)
            elif articulator == ARM:
                if articulator_dict[1]:
                    self.x_a1_radio.setChecked(True)
                elif articulator_dict[2]:
                    self.x_a2_radio.setChecked(True)
            elif articulator == LEG:
                if articulator_dict[1]:
                    self.x_l1_radio.setChecked(True)
                elif articulator_dict[2]:
                    self.x_l2_radio.setChecked(True)

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
        self.setcurrentx(moduletoload.relationx)
        self.setcurrenty(moduletoload.relationy)
        self.setcurrentcontact(moduletoload.contactrel)
        self.crossed_cb.setChecked(moduletoload.xy_crossed)
        self.linked_cb.setChecked(moduletoload.xy_linked)
        self.setcurrentdirection(moduletoload.directions)
        self.bodyparts_dict = moduletoload.bodyparts_dict

        # TODO KV set the linked-from module if there is one in moduletoload

    def setcurrentx(self, relationx):
        if relationx is not None:
            self.x_other_text.setText(relationx.othertext)
            self.x_h1_radio.setChecked(relationx.h1)
            self.x_h2_radio.setChecked(relationx.h2)
            self.x_both_radio.setChecked(relationx.both)
            if relationx.both:
                self.x_bothconnected_cb.setChecked(relationx.connected)
            self.x_a1_radio.setChecked(relationx.arm1)
            self.x_a2_radio.setChecked(relationx.arm2)
            self.x_l1_radio.setChecked(relationx.leg1)
            self.x_l2_radio.setChecked(relationx.leg2)
            self.x_other_radio.setChecked(relationx.other)

    def getcurrentx(self):
        return RelationX(h1=self.x_h1_radio.isChecked(),
                         h2=self.x_h2_radio.isChecked(),
                         both=self.x_both_radio.isChecked(),
                         connected=self.x_bothconnected_cb.isChecked(),
                         arm1=self.x_a1_radio.isChecked(),
                         arm2=self.x_a2_radio.isChecked(),
                         leg1=self.x_l1_radio.isChecked(),
                         leg2=self.x_l2_radio.isChecked(),
                         other=self.x_other_radio.isChecked(),
                         othertext=self.x_other_text.text())

    def setcurrenty(self, relationy):
        if relationy is not None:
            self.y_other_text.setText(relationy.othertext)
            self.y_h2_radio.setChecked(relationy.h2)
            self.y_a2_radio.setChecked(relationy.arm2)
            self.y_l1_radio.setChecked(relationy.leg1)
            self.y_l2_radio.setChecked(relationy.leg2)
            self.y_existingmod_radio.setChecked(relationy.existingmodule)
            if relationy.existingmodule:
                self.setcurrentlinkedmoduleinfo(relationy.linkedmoduleids, relationy.linkedmoduletype)
            self.y_other_radio.setChecked(relationy.other)

    def getcurrenty(self):
        return RelationY(h2=self.y_h2_radio.isChecked(),
                         arm2=self.y_a2_radio.isChecked(),
                         leg1=self.y_l1_radio.isChecked(),
                         leg2=self.y_l2_radio.isChecked(),
                         existingmodule=self.y_existingmod_radio.isChecked(),
                         linkedmoduletype=self.getcurrentlinkedmoduletype(),
                         linkedmoduleids=self.getcurrentlinkedmoduleids(),
                         other=self.y_other_radio.isChecked(),
                         othertext=self.y_other_text.text())

    def getcurrentcontact(self):
        hascontact = self.contact_rb.isChecked()
        hasnocontact = self.nocontact_rb.isChecked()
        contactreln = None
        if hascontact:
            mannerrel = self.getcurrentmanner()
            contacttype = self.getcurrentcontacttype()
            contactreln = ContactRelation(contact=True, contacttype=contacttype, mannerrel=mannerrel)
        elif hasnocontact:
            distances = self.getcurrentdistances()
            contactreln = ContactRelation(contact=False, distance_list=distances)
        else:  # contact isn't specified (neither "contact" nor "no contact" radio button is selected)
            distances = self.getcurrentdistances()
            contactreln = ContactRelation(contact=None, distance_list=distances)
        return contactreln

    def getcurrentcontacttype(self):
        contacttype = ContactType(
            light=self.contactlight_rb.isChecked(),
            firm=self.contactfirm_rb.isChecked(),
            other=self.contactother_rb.isChecked(),
            othertext=self.contact_other_text.text()
        )
        return contacttype

    def getcurrentmanner(self):
        contactmannerreln = MannerRelation(
            holding=self.holding_rb.isChecked(),
            continuous=self.continuous_rb.isChecked(),
            intermittent=self.intermittent_rb.isChecked()
        )
        return contactmannerreln

    def getcurrentdirections(self):
        direction_hor = Direction(axis=Direction.HORIZONTAL,
                                  axisselected=self.dirhor_cb.isChecked(),
                                  plus=self.dirhoripsi_rb.isChecked(),
                                  minus=self.dirhorcontra_rb.isChecked(),
                                  inline=self.dirhorinline_rb.isChecked()
                                  )
        direction_ver = Direction(axis=Direction.VERTICAL,
                                  axisselected=self.dirver_cb.isChecked(),
                                  plus=self.dirverabove_rb.isChecked(),
                                  minus=self.dirverbelow_rb.isChecked(),
                                  inline=self.dirverinline_rb.isChecked()
                                  )
        direction_sag = Direction(axis=Direction.SAGITTAL,
                                  axisselected=self.dirsag_cb.isChecked(),
                                  plus=self.dirsagprox_rb.isChecked(),
                                  minus=self.dirsagdist_rb.isChecked(),
                                  inline=self.dirsaginline_rb.isChecked()
                                  )
        directions = [direction_hor, direction_ver, direction_sag]
        return directions

    def getcurrentdistances(self):
        distance_hor = Distance(axis=Direction.HORIZONTAL,
                                close=self.dishorclose_rb.isChecked(),
                                medium=self.dishormed_rb.isChecked(),
                                far=self.dishorfar_rb.isChecked())
        distance_ver = Distance(axis=Direction.VERTICAL,
                                close=self.disverclose_rb.isChecked(),
                                medium=self.disvermed_rb.isChecked(),
                                far=self.disverfar_rb.isChecked())
        distance_sag = Distance(axis=Direction.SAGITTAL,
                                close=self.dissagclose_rb.isChecked(),
                                medium=self.dissagmed_rb.isChecked(),
                                far=self.dissagfar_rb.isChecked())
        distances = [distance_hor, distance_ver, distance_sag]
        return distances

    def setcurrentcontact(self, contactrel):
        if contactrel is None or contactrel.contact is None:
            return
        elif contactrel.contact:
            self.contact_rb.setChecked(True)
            if contactrel.contacttype:
                self.setcurrentcontacttype(contactrel.contacttype)
            if contactrel.manner:
                self.setcurrentmanner(contactrel.manner)
        else:  # no contact
            self.nocontact_rb.setChecked(True)
            if contactrel.distances:
                self.setcurrentdistances(contactrel.distances)

    def setcurrentmanner(self, mannerrel):
        if mannerrel is not None:
            self.holding_rb.setChecked(mannerrel.holding)
            self.continuous_rb.setChecked(mannerrel.continuous)
            self.intermittent_rb.setChecked(mannerrel.intermittent)

    def setcurrentcontacttype(self, contacttype):
        if contacttype is not None:
            self.contactlight_rb.setChecked(contacttype.light)
            self.contactfirm_rb.setChecked(contacttype.firm)
            self.contactother_rb.setChecked(contacttype.other)
            self.contact_other_text.setText(contacttype.othertext)

    def setcurrentdirection(self, directions_list):
        if directions_list is not None:
            hor_direction = [axis_dir for axis_dir in directions_list if axis_dir.axis == Direction.HORIZONTAL][0]
            ver_direction = [axis_dir for axis_dir in directions_list if axis_dir.axis == Direction.VERTICAL][0]
            sag_direction = [axis_dir for axis_dir in directions_list if axis_dir.axis == Direction.SAGITTAL][0]

            self.dirhor_cb.setChecked(hor_direction.axisselected)
            if hor_direction.axisselected:
                self.dirhoripsi_rb.setChecked(hor_direction.plus)
                self.dirhorcontra_rb.setChecked(hor_direction.minus)
                self.dirhorinline_rb.setChecked(hor_direction.inline)

            self.dirver_cb.setChecked(ver_direction.axisselected)
            if ver_direction.axisselected:
                self.dirverabove_rb.setChecked(ver_direction.plus)
                self.dirverbelow_rb.setChecked(ver_direction.minus)
                self.dirverinline_rb.setChecked(ver_direction.inline)

            self.dirsag_cb.setChecked(sag_direction.axisselected)
            if sag_direction.axisselected:
                self.dirsagprox_rb.setChecked(sag_direction.plus)
                self.dirsagdist_rb.setChecked(sag_direction.minus)
                self.dirsaginline_rb.setChecked(sag_direction.inline)

    def setcurrentdistances(self, distances_list):
        if distances_list is not None:
            hor_distance = [axis_dist for axis_dist in distances_list if axis_dist.axis == Direction.HORIZONTAL][0]
            ver_distance = [axis_dist for axis_dist in distances_list if axis_dist.axis == Direction.VERTICAL][0]
            sag_distance = [axis_dist for axis_dist in distances_list if axis_dist.axis == Direction.SAGITTAL][0]

            self.dishorclose_rb.setChecked(hor_distance.close)
            self.dishormed_rb.setChecked(hor_distance.medium)
            self.dishorfar_rb.setChecked(hor_distance.far)

            self.disverclose_rb.setChecked(ver_distance.close)
            self.disvermed_rb.setChecked(ver_distance.medium)
            self.disverfar_rb.setChecked(ver_distance.far)

            self.dissagclose_rb.setChecked(sag_distance.close)
            self.dissagmed_rb.setChecked(sag_distance.medium)
            self.dissagfar_rb.setChecked(sag_distance.far)

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

    def clear_x_options(self):
        self.clear_group_buttons(self.x_group)
        self.x_other_text.clear()
        self.x_bothconnected_cb.setChecked(False)

        self.enable_x_options(True)

    def enable_x_options(self, doenable):
        self.x_other_text.setEnabled(doenable)
        self.x_bothconnected_cb.setEnabled(doenable)

    def clear_y_options(self):
        self.clear_group_buttons(self.y_group)
        self.setcurrentlinkedmoduleinfo(None, None)
        self.y_other_text.clear()

        self.enable_y_options(True)

    def enable_y_options(self, doenable):
        self.y_other_text.setEnabled(doenable)
        self.existingmod_listview.setEnabled(doenable)

    def clear_distance_buttons(self):
        for grp in [self.dishor_group, self.disver_group, self.dissag_group]:
            self.clear_group_buttons(grp)

        for grpbox in [self.dishor_box, self.disver_box, self.dissag_box]:
            grpbox.setEnabled(True)

    def clear_direction_buttons(self):
        for cb in [self.dirhor_cb, self.dirver_cb, self.dirsag_cb]:
            cb.setChecked(False)
        for grp in [self.dirhor_group, self.dirver_group, self.dirsag_group]:
            self.clear_group_buttons(grp)

        for grpbox in [self.dirhor_box, self.dirver_box, self.dirsag_box]:
            grpbox.setEnabled(True)

    def clear(self):
        self.clear_x_options()
        self.clear_y_options()
        self.clear_direction_buttons()
        self.clear_distance_buttons()
        self.clear_group_buttons(self.manner_group)
        self.clear_group_buttons(self.contact_group)

    def desiredwidth(self):
        return 500

    def desiredheight(self):
        return 700


class RelationRadioButton(QRadioButton):

    def __init__(self, text, **kwargs):
        super().__init__(text, **kwargs)

    def setChecked(self, checked):
        if checked and self.group() is not None:
            self.group().previously_checked = self
        super().setChecked(checked)


class RelationButtonGroup(QButtonGroup):

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
