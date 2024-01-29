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
    QPushButton, QTabWidget, QWidget, QScrollArea
)

from PyQt5.QtCore import (
    Qt,
    QEvent,
    pyqtSignal,
    QItemSelectionModel
)

from lexicon.module_classes import (
    NonManualModule,
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
from models.nonmanual_models import NonManualModel, nonmanual_root
from gui.relationspecification_view import RelationRadioButton as SLPAARadioButton
from gui.relationspecification_view import RelationButtonGroup
from gui.modulespecification_widgets import ModuleSpecificationPanel
from gui.bodypartspecification_dialog import BodypartSelectorDialog
from gui.helper_widget import OptionSwitch
from constant import HAND, ARM, LEG


class SLPAAButtonGroup(RelationButtonGroup):
    def __init__(self, buttonslist=None):
        # buttonslist: list of QRadioButton to be included as a group
        super().__init__()
        if buttonslist is not None:
            [self.addButton(button) for button in buttonslist]



class NonManualSpecificationPanel(ModuleSpecificationPanel):
    timingintervals_inherited = pyqtSignal(list)

    def __init__(self, moduletoload=None, **kwargs):
        super().__init__(**kwargs)
        self.islinkedtopoint = False
        self.islinkedtointerval = False

        main_layout = QVBoxLayout()

        # 'All neutral' checkbox
        self.widget_cb_neutral = QCheckBox("All sections are neutral")
        main_layout.addWidget(self.widget_cb_neutral)

        # different major non manual tabs
        self.tab_widget = QTabWidget()             # Create a tab widget
        self.create_major_tabs(nonmanual_root.children)  # Create and add tabs to the tab widget
        self.tab_widget.setMinimumHeight(500)
        self.setLayout(main_layout)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.tab_widget)
        scroll_area.setMinimumHeight(300)
        main_layout.addWidget(scroll_area)

    def create_major_tabs(self, nonman_units):
        """
        Populate major non-manual articulators like shoulder, body, and head
        Args:
            nonman_units: list of NonManualModel
        """
        for nonman_unit in nonman_units:
            major_tab = self.add_tab(nonman_unit)
            self.tab_widget.addTab(major_tab, nonman_unit.label)

    def add_tab(self, nonman):
        """
            Deal with the mundane hassle of adding tab gui, recursively
            Args:
                nonman: NonManualModel
        """
        tab_widget = QTabWidget()
        tab_widget.layout = QVBoxLayout()

        # This section is neutral
        nonman.widget_cb_neutral = QCheckBox("This section is neutral")
        tab_widget.layout.addWidget(nonman.widget_cb_neutral)

        row_1 = self.build_row1(nonman)  # [ static / dynamic ] [ Sub-parts ]
        row_2 = self.build_row2(nonman)  # action / state
        row_3 = self.build_row3(nonman)  # mvmt characteristics

        tab_widget.layout.addLayout(row_1)
        tab_widget.layout.addLayout(row_2)
        tab_widget.layout.addLayout(row_3)

        if nonman.children:
            subtabs_container = QTabWidget()
            for sub_category in nonman.children:
                sub_tab = self.add_tab(sub_category)
                subtabs_container.addTab(sub_tab, sub_category.label)
            tab_widget.layout.addWidget(subtabs_container)
            tab_widget.setLayout(tab_widget.layout)
            return tab_widget


        tab_widget.setLayout(tab_widget.layout)

        return tab_widget

    def build_row1(self, nonman):
        """
        Build the first row of the NonMan specification window
        Currently for "Static/dynamic" (required) and either "Sub-part(s)" or "Visibility"(optional)
        Args:
            nonman: NonManualModel

        Returns:
            QHBoxLayout
        """
        row = QHBoxLayout()

        # static / dynamic group
        nonman.widget_rb_static = QRadioButton("Static")
        nonman.widget_rb_dynamic = QRadioButton("Dynamic")
        static_dynamic_list = [nonman.widget_rb_static, nonman.widget_rb_dynamic]
        nonman.static_dynamic_group = SLPAAButtonGroup(static_dynamic_list)

        vbox = QVBoxLayout()
        [vbox.addWidget(widget) for widget in static_dynamic_list]

        sd_rb_groupbox = QGroupBox("Static / Dynamic")  # static/dynamic radio buttons group
        sd_rb_groupbox.setLayout(vbox)

        row.addWidget(sd_rb_groupbox)

        # special case: 'mouth' requires 'Type of mouth movement' which is contained in .subparts
        if nonman.label == 'Mouth':
            mvmt_type_box = QGroupBox("Type of mouth movement")
            mvmt_type_box_layout = QVBoxLayout()
            for type in nonman.subparts:
                rb_to_add = SLPAARadioButton(type)
                mvmt_type_box_layout.addWidget(rb_to_add)
            mvmt_type_box.setLayout(mvmt_type_box_layout)

            row.addWidget(mvmt_type_box)
            return row

        # subparts group
        if nonman.subparts is not None:
            subpart_specs = nonman.subparts
            subpart_box = QGroupBox("Sub-part(s)")
            subpart_box_layout = QVBoxLayout()
            onepart_spacedlayout = QHBoxLayout()
            onepart_layout = QHBoxLayout()

            nonman.widget_rb_subpart_both = SLPAARadioButton(f"Both {subpart_specs['specifier']}s")
            nonman.widget_rb_subpart_one = SLPAARadioButton(f"One {subpart_specs['specifier']}")
            subpart_list = [nonman.widget_rb_subpart_both, nonman.widget_rb_subpart_one]

            nonman.subpart_group = SLPAAButtonGroup(subpart_list)

            nonman.widget_rb_onepart_one = SLPAARadioButton("H1")
            nonman.widget_rb_onepart_two = SLPAARadioButton("H2")
            onepart_list = [nonman.widget_rb_onepart_one, nonman.widget_rb_onepart_two]

            nonman.onepart_group = SLPAAButtonGroup(onepart_list)

            [onepart_layout.addWidget(widget) for widget in onepart_list]
            onepart_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
            onepart_spacedlayout.addLayout(onepart_layout)

            [subpart_box_layout.addWidget(widget) for widget in subpart_list]
            subpart_box_layout.addLayout(onepart_spacedlayout)

            subpart_box.setLayout(subpart_box_layout)

            row.addWidget(subpart_box)

        # visibility group
        if nonman.visibility is not None:
            visibility_box = QGroupBox("Visibility")
            visibility_box_layout = QVBoxLayout()
            nonman.widget_rb_visible = SLPAARadioButton("Visible")
            nonman.widget_rb_visible_not = SLPAARadioButton("Not visible")
            visibility_box_layout.addWidget(nonman.widget_rb_visible)
            visibility_box_layout.addWidget(nonman.widget_rb_visible_not)
            visibility_box.setLayout(visibility_box_layout)
            row.addWidget(visibility_box)
        return row

    def build_row2(self, nonman):
        """
        Build the second row of the NonMan specification window
        Currently for "Action / state" only.
        Details on action state gui are provided as NonManualModel.action_state, a Dict
        Args:
            nonman: NonManualModel

        Returns:
            QHBoxLayout
        """
        if nonman.action_state is None:
            return None

        row = QHBoxLayout()

        # Action / state group

        action_state_groupbox = QGroupBox("Action / state")  # static/dynamic radio buttons group
        action_state_layout = QVBoxLayout()

        root_options = nonman.action_state
        self.parse_actionstate(parent=self, options=root_options)
        action_state_layout.addLayout(root_options.widget_grouplayout_actionstate)

        action_state_groupbox.setLayout(action_state_layout)
        scrollable = QScrollArea()
        scrollable.setWidget(action_state_groupbox)
        scrollable.setWidgetResizable(True)
        row.addWidget(scrollable)

        return row

    def parse_actionstate(self, parent, options):

        if isinstance(options, str):
            # in shallow module
            added_rb = SLPAARadioButton(options)
            parent.as_main_btn_group.addButton(added_rb)
            parent.widget_grouplayout_actionstate.addWidget(added_rb)
            parent.widget_grouplayout_actionstate.setAlignment(added_rb, Qt.AlignTop)
            return

        elif options.label:
            # parse this node and its children
            main_layout = QVBoxLayout()
            main_layout.setAlignment(Qt.AlignTop)
            if options.exclusive:
                main_btn = SLPAARadioButton(options.label)
                parent.as_main_btn_group.addButton(main_btn)
            else:
                main_btn = QCheckBox(options.label)
            main_layout.addWidget(main_btn)
            sub_layout = QVBoxLayout()

            sub_spacedlayout = QHBoxLayout()
            sub_spacedlayout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))

            if options.options is not None:
                sub_btn_group = SLPAAButtonGroup()
                for child in options.options:
                    if not isinstance(child, str):
                        sub_heading, subsub_spacedlayout = self.fillin_vbox(child)
                        if isinstance(sub_heading, QRadioButton):
                            sub_btn_group.addButton(sub_heading)
                        sub_layout.addWidget(sub_heading)
                        sub_layout.addLayout(subsub_spacedlayout)
                    else:
                        sub_rb = SLPAARadioButton(child)
                        sub_layout.addWidget(sub_rb)
                        sub_btn_group.addButton(sub_rb)
                parent.as_sub_btn_groups.append(sub_btn_group)
            sub_spacedlayout.addLayout(sub_layout)
            main_layout.addLayout(sub_spacedlayout)
            parent.widget_grouplayout_actionstate.addLayout(main_layout)
        else:
            # in the root. initialize and be ready to go deeper
            options.widget_grouplayout_actionstate = QHBoxLayout()
            options.widget_grouplayout_actionstate.setAlignment(Qt.AlignTop)
            options.as_main_btn_group = SLPAAButtonGroup()
            options.as_sub_btn_groups = []  # container for sub buttons
            for child in options.options:
                self.parse_actionstate(parent=options,
                                       options=child)

    def fillin_vbox(self, asm):
        # asm: ActionStateModel
        if asm.exclusive:
            sub_heading = SLPAARadioButton(asm.label)
        else:
            sub_heading = QCheckBox(asm.label)
        subsub_layout = QVBoxLayout()

        if asm.options is not None:
            btn_group = SLPAAButtonGroup()
            for o in asm.options:
                if not isinstance(o, str):
                    cb, sub_spacedlayout = self.fillin_vbox(o)
                    if isinstance(cb, QRadioButton):
                        btn_group.addButton(cb)
                    subsub_layout.addWidget(cb)
                    subsub_layout.addLayout(sub_spacedlayout)
                else:
                    sub_rb = SLPAARadioButton(o)
                    subsub_layout.addWidget(sub_rb)
                    btn_group.addButton(sub_rb)
        spacedlayout = QHBoxLayout()
        spacedlayout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        spacedlayout.addLayout(subsub_layout)

        return sub_heading, spacedlayout

    def build_row3(self, nonman):
        """
        Build the third row of the NonMan specification window
        Currently for "Mvmt characteristics"
        Args:
            nonman: NonManualModel

        Returns:
            QHBoxLayout
        """
        if nonman.action_state is None:  # Currently, if action state is unspecified 3rd row is also nonexistent
            return None

        row = QHBoxLayout()

        # Repetition group
        repetition_group = QGroupBox("Repetition")
        repetition_group_layout = QVBoxLayout()
        nonman.widget_rb_rep_single = SLPAARadioButton("Single")
        nonman.widget_rb_rep_rep = SLPAARadioButton("Repeated")
        nonman.widget_rb_rep_trill = SLPAARadioButton("Trilled")
        rep_list = [nonman.widget_rb_rep_single, nonman.widget_rb_rep_rep, nonman.widget_rb_rep_trill]

        nonman.rep_group = SLPAAButtonGroup(rep_list)

        [repetition_group_layout.addWidget(widget) for widget in rep_list]
        repetition_group.setLayout(repetition_group_layout)

        # Directionality group
        directionality_group = QGroupBox("Directionality")
        directionality_group_layout = QVBoxLayout()
        nonman.widget_rb_direction_uni = SLPAARadioButton("Unidirectional")
        nonman.widget_rb_direction_bi = SLPAARadioButton("Bidirectional")
        directionality_list = [nonman.widget_rb_direction_uni, nonman.widget_rb_direction_bi]

        nonman.directionality_group = SLPAAButtonGroup(directionality_list)

        [directionality_group_layout.addWidget(widget) for widget in directionality_list]
        directionality_group.setLayout(directionality_group_layout)

        # Additional movement characteristics group -- contains Size Speed Force Tension
        additional_char_group = QGroupBox("Additional mvmt characteristics")
        additional_char_group_layout = QHBoxLayout()
        additional_char_specs = {'Size': ['Big', 'Small'],
                                 'Speed': ['Fast', 'Slow'],
                                 'Force': ['Strong', 'Weak'],
                                 'Tension': ['Tense', 'Lax']}
        additional_subgroups, additional_rb_groups = self.gen_add_move_char(additional_char_specs)
        [additional_char_group_layout.addWidget(widget) for widget in additional_subgroups]
        nonman.additional_char_rb_group = additional_rb_groups

        additional_char_group.setLayout(additional_char_group_layout)

        # Adding all the groupboxes to form the row
        row.addWidget(repetition_group)
        row.addWidget(directionality_group)
        row.addWidget(additional_char_group)

        return row

    def gen_add_move_char(self, specs):
        groupboxes = []
        groups = []

        for group, levels in specs.items():
            groupbox = QGroupBox(group)
            groupbox_layout = QVBoxLayout()
            buttongroup = SLPAAButtonGroup()

            levels.insert(1, 'Normal')

            for level in levels:
                rb_to_add = SLPAARadioButton(level)
                buttongroup.addButton(rb_to_add)
                groupbox_layout.addWidget(rb_to_add)

            groupbox.setLayout(groupbox_layout)
            groupboxes.append(groupbox)

            groups.append(buttongroup)

        return groupboxes, groups

    def validity_check(self):
        selectionsvalid = self.x_group.checkedButton() and self.y_group.checkedButton()
        warningmessage = "" if selectionsvalid else "Requires both an X and a Y selection."
        return selectionsvalid, warningmessage

    def timinglinknotification(self, haspoint, hasinterval):
        self.islinkedtopoint = haspoint
        self.islinkedtointerval = hasinterval
        self.check_enable_allsubmenus()

    def getsavedmodule(self, articulators, timingintervals, addedinfo, inphase):

        nonman_mod = NonManualModule(nonman_specs=self.specifications,
                                     articulators=articulators,
                                     timingintervals=timingintervals,
                                     addedinfo=addedinfo,)
        if self.existingkey is not None:
            nonman_mod.uniqueid = self.existingkey
        else:
            self.existingkey = nonman_mod.uniqueid
        return nonman_mod

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
