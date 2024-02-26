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
from gui.relationspecification_view import RelationRadioButton
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


class SLPAARadioButton(RelationRadioButton):
    def __init__(self, text):
        # btn_text: button text for easy reference
        super().__init__(text)


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

        # non manual specs
        self.nonman_specifications = {}


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

        # when loading already saved module
        if moduletoload is not None and isinstance(moduletoload, NonManualModule):
            self.setvalues(moduletoload)
            self.existingkey = moduletoload.uniqueid

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
        nonman.widget_rb_static = SLPAARadioButton("Static")
        nonman.widget_rb_dynamic = SLPAARadioButton("Dynamic")
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
            nonman.mvmt_type_group = SLPAAButtonGroup()
            for type in nonman.subparts:
                rb_to_add = SLPAARadioButton(type)
                mvmt_type_box_layout.addWidget(rb_to_add)
                nonman.mvmt_type_group.addButton(rb_to_add)
            mvmt_type_box.setLayout(mvmt_type_box_layout)

            row.addWidget(mvmt_type_box)
            self.nonman_specifications[nonman.label] = nonman
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
        self.nonman_specifications[nonman.label] = nonman
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
            options.widget_grouplayout_actionstate = QVBoxLayout()
            options.widget_grouplayout_actionstate.setAlignment(Qt.AlignTop)
            options.as_main_btn_group = SLPAAButtonGroup()
            options.as_main_cb_list = []
            options.as_sub_btn_groups = []  # container for sub buttons

            main_layout = QVBoxLayout()
            main_layout.setAlignment(Qt.AlignTop)
            if options.exclusive:
                main_btn = SLPAARadioButton(options.label)
                parent.as_main_btn_group.addButton(main_btn)
            else:
                main_btn = QCheckBox(options.label)
                parent.as_main_cb_list.append(main_btn)
            main_layout.addWidget(main_btn)
            sub_layout = QVBoxLayout()

            sub_spacedlayout = QHBoxLayout()
            sub_spacedlayout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))

            if options.options is not None:
                for child in options.options:
                    if isinstance(child, str):
                        sub_rb = SLPAARadioButton(child)
                        sub_layout.addWidget(sub_rb)
                        options.as_main_btn_group.addButton(sub_rb)
                        sub_spacedlayout.addLayout(sub_layout)
                    else:
                        self.parse_actionstate(parent=options, options=child)
                        sub_spacedlayout.addLayout(options.widget_grouplayout_actionstate)
                    main_layout.addLayout(sub_spacedlayout)
            parent.widget_grouplayout_actionstate.addLayout(main_layout)
        else:
            # in the root. be ready to go deeper
            options.widget_grouplayout_actionstate = QHBoxLayout()
            options.widget_grouplayout_actionstate.setAlignment(Qt.AlignTop)
            options.as_main_btn_group = SLPAAButtonGroup()
            options.as_main_cb_list = []
            options.as_sub_btn_groups = []  # container for sub buttons
            for child in options.options:
                self.parse_actionstate(parent=options,
                                       options=child)

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
        # called when 'save' clicked. need to confirm
        return True, ''


    def wrapper_get_nonman_specs(self):
        res = {}
        usr_input = self.nonman_specifications
        major_modules = [module_title.label for module_title in nonmanual_root.children]
        for module in major_modules:
            current_module = usr_input[module]
            res[module] = self.get_nonman_specs(current_module)
        return res

    def get_nonman_specs(self, current_module, parent=None):
        module_output = {'static_dynamic': what_selected(current_module.static_dynamic_group)}

        # special case: 'mouth' has 'type of mouth movement' (others have 'subparts')
        if current_module.label == 'Mouth':
            module_output['mvmt_type'] = what_selected(current_module.mvmt_type_group)
            # 'mouth' will exceptionally have 'mvmt_type' key for 'type of mouth movement'

        # get choice between both, h1, h2
        else:
            try:
                onepart_selection = what_selected(current_module.onepart_group)
                one_or_both = what_selected(current_module.subpart_group)
                module_output['subpart'] = one_or_both if one_or_both == 'both' else onepart_selection
            except AttributeError:  # when no subpart spec exists, such as 'body', 'head', etc.
                pass

        module_output['children'] = None

        # case of embedded module like 'facial expression'
        if current_module.children is not None:
            module_output['children'] = {}
            for child in current_module.children:
                module_output['children'][child.label] = self.get_nonman_specs(child, parent=current_module)
            return module_output

        # this time, repetition and directionality
        module_output['repetition'] = what_selected(current_module.rep_group)
        module_output['directionality'] = what_selected(current_module.directionality_group)

        # additional mvmt characteristics
        addit_mvmt_chars = [what_selected(selection) for selection in current_module.additional_char_rb_group]

        addit_keys = ['size', 'speed', 'force', 'tension']
        for k, v in zip(addit_keys, addit_mvmt_chars):
            module_output[k] = v

        # finally, action/state
        as_dict = {}  # usr selections parsed as Dictionary. to be passed as module_output['action_state']
        _, v = self.package_action_state(as_dict, current_module.action_state)
        as_dict['root'] = v

        module_output['action_state'] = as_dict

        return module_output

    def package_action_state(self, d, asm, parent=None):
        # d: Dict. Upper level representation
        # parent: parent ActionStateModel
        # asm: ActionStateModel to be packaged as dictionary.
        r = {}
        selected_cb = what_selected(asm.as_main_cb_list)
        selected_btn = what_selected(asm.as_main_btn_group)
        selected_options = selected_cb + [selected_btn] if selected_btn is not None else selected_cb

        for child in asm.options:
            if isinstance(child, str):
                # at the bottom
                r = [] if isinstance(r, dict) else r
                if selected_btn is not None and child == selected_btn:
                    r = selected_btn
                elif len(selected_cb) > 0:
                    r.extend(selected_cb)
            else:
                if child.label not in selected_options:
                    continue
                res_k, res_v = self.package_action_state(d, child, parent=asm)
                r[res_k] = res_v
        return asm.label, r

    def getsavedmodule(self, articulators, timingintervals, addedinfo, inphase):
        # package the user input and deliver
        nonman_mod = NonManualModule(nonman_specs=self.wrapper_get_nonman_specs(),
                                     articulators=articulators,
                                     timingintervals=timingintervals,
                                     addedinfo=addedinfo,)
        if self.existingkey is not None:
            nonman_mod.uniqueid = self.existingkey
        else:
            self.existingkey = nonman_mod.uniqueid
        return nonman_mod

    def setvalues(self, moduletoload):
        # load saved values and set template values by them.
        toload_dict = moduletoload._nonmanual

        major_modules = [module_title.label for module_title in nonmanual_root.children]  # major modules in non manual
        template = self.nonman_specifications  # empty template of specification window

        for module in major_modules:
            values_toload = toload_dict[module]
            load_destination = template[module]
            load_destination = load_specifications(values_toload, load_destination)
            if values_toload['children'] is None:  # Does not include embedded tabs
                return
            for i, (label, child) in enumerate(values_toload['children'].items()):
                child_values_toload = child
                child_load_destination = template[label]
                load_destination.children[i] = load_specifications(child_values_toload, child_load_destination)


def load_specifications(values_toload, load_destination):
    # values_toload: saved user selections to load
    # load_destination: major modules like 'shoulder' 'facial expressions'...

    # static dynamic
    select_this(btn_group=load_destination.static_dynamic_group,
                btn_txt=values_toload['static_dynamic'])
    # sub-part(s)
    try:
        if values_toload['subpart'] == 'both':
            select_this(btn_group=load_destination.subpart_group,
                        btn_txt='both')
        elif values_toload['subpart'] is not None:
            select_this(btn_group=load_destination.subpart_group,
                        btn_txt='one')
            select_this(btn_group=load_destination.onepart_group,
                        btn_txt=values_toload['subpart'])

    except KeyError:  # when no subpart spec exists, such as 'body', 'head', etc.
        pass

    # repetition
    try:
        select_this(btn_group=load_destination.rep_group,
                    btn_txt=values_toload['repetition'])
    except AttributeError:
        pass

    # directionality
    try:
        select_this(btn_group=load_destination.directionality_group,
                    btn_txt=values_toload['directionality'])
    except AttributeError:
        pass

    # additional movement characteristics (size, speed, force, tenstion)
    try:
        for btn_group, btn_txt in zip(load_destination.additional_char_rb_group, ['size', 'speed', 'force', 'tension']):
            select_this(btn_group=btn_group,
                        btn_txt=values_toload[btn_txt])
    except AttributeError:
        pass


    return load_destination


def what_selected(group):
    # input: SLPAAButtonGroup or list of QCheckBox objects
    # helper function to get what user input among buttons/checkboxes in the group
    if isinstance(group,QButtonGroup):
        # get selected button (exclusive)
        if group.checkedButton() is None:
            return None
        return group.checkedButton().text()
    elif isinstance(group, list):
        # get selected checkboxes (potentially many)
        return [cb.text() for cb in group if cb.isChecked()]


def select_this(btn_group, btn_txt):
    # given SLPAAButtonGroup, select the button named 'btn_txt'
    if not isinstance(btn_group, SLPAAButtonGroup) or not isinstance(btn_txt, str):
        return None

    for btn in btn_group.buttons():
        if btn.text() == btn_txt:
            btn.setChecked(True)
