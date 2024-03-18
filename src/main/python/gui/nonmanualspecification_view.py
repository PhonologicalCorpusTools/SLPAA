from PyQt5.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QButtonGroup,
    QGroupBox,
    QCheckBox,
    QSpacerItem,
    QSizePolicy,
    QTabWidget, QScrollArea, QRadioButton
)
from PyQt5.QtCore import (Qt, pyqtSignal,)

from lexicon.module_classes import NonManualModule
from models.nonmanual_models import NonManualModel, nonmanual_root
from gui.relationspecification_view import RelationRadioButton as SLPAARadioButton
from gui.relationspecification_view import RelationButtonGroup
from gui.modulespecification_widgets import ModuleSpecificationPanel


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
        main_layout.setAlignment(Qt.AlignTop)

        # 'All neutral' checkbox
        self.widget_cb_neutral = QCheckBox("All sections are neutral")
        main_layout.addWidget(self.widget_cb_neutral)

        # non manual specs
        self.nonman_specifications = {}

        # different major non manual tabs
        self.tab_widget = QTabWidget()             # Create a tab widget
        self.create_major_tabs(nonmanual_root.children)  # Create and add tabs to the tab widget
        self.tab_widget.setMinimumHeight(700)
        self.setLayout(main_layout)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.tab_widget)
        scroll_area.setMinimumHeight(350)
        main_layout.addWidget(scroll_area)

        # snapshot of the blank slate (for 'restore to default')
        self._clean_nonman = self.wrapper_get_nonman_specs()

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
        tab_widget.layout.setAlignment(Qt.AlignTop)

        # This section is neutral
        nonman.widget_cb_neutral = QCheckBox("This section is neutral")
        tab_widget.layout.addWidget(nonman.widget_cb_neutral)
        nonman.widget_cb_neutral.stateChanged.connect(lambda state: self.greyout_children(state=state,
                                                                                          itself=nonman.widget_cb_neutral,
                                                                                          child_tab=tab_widget))

        row_1 = self.build_row1(nonman)  # [ static / dynamic ] [ Sub-parts ]
        row_2 = self.build_row2(nonman)  # action / state
        row_3 = self.build_row3(nonman)  # mvmt characteristics

        rows = [row_1, row_2, row_3]
        [tab_widget.layout.addLayout(row) for row in rows if row is not None]

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

    def greyout_children(self, itself, state, child_tab):
        # called when 'this section is neutral' checkbox state changes
        # have all children widgets disabled when checked / enabled when unchecked
        # itself: clicked checkbox itself
        need_disable = state == Qt.Checked
        target_groupboxes = [w for w in child_tab.findChildren(QGroupBox)]  # child groupboxes
        target_cbs = [w for w in child_tab.findChildren(QCheckBox) if w is not itself]  # for disabling/enabling a 'neutral' cb in nested tabs

        for gb in target_groupboxes:
            gb.setDisabled(need_disable)

        for cb in target_cbs:
            cb.setDisabled(need_disable)

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
        row.setAlignment(Qt.AlignTop)

        # static / dynamic group
        nonman.widget_rb_static = SLPAARadioButton("Static")
        nonman.widget_rb_dynamic = SLPAARadioButton("Dynamic")
        static_dynamic_list = [nonman.widget_rb_static, nonman.widget_rb_dynamic]
        nonman.static_dynamic_group = SLPAAButtonGroup(static_dynamic_list)

        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignTop)
        [vbox.addWidget(widget) for widget in static_dynamic_list]

        sd_rb_groupbox = QGroupBox("Static / Dynamic")  # static/dynamic radio buttons group
        sd_rb_groupbox.setLayout(vbox)
        sd_rb_groupbox.setFixedHeight(sd_rb_groupbox.sizeHint().height())  # initially set height. might be overridden.

        row.addWidget(sd_rb_groupbox)

        # special case: 'mouth' requires 'Type of mouth movement' which is contained in .subparts
        if nonman.label == 'Mouth':
            mvmt_type_box = QGroupBox("Type of mouth movement")
            mvmt_type_box_layout = QVBoxLayout()
            mvmt_type_box.setAlignment(Qt.AlignTop)
            nonman.mvmt_type_group = SLPAAButtonGroup()
            for type in nonman.subparts:
                rb_to_add = SLPAARadioButton(type)
                mvmt_type_box_layout.addWidget(rb_to_add)
                nonman.mvmt_type_group.addButton(rb_to_add)
            mvmt_type_box.setLayout(mvmt_type_box_layout)
            row1_height = mvmt_type_box.sizeHint().height()
            mvmt_type_box.setFixedWidth(row1_height)
            sd_rb_groupbox.setFixedHeight(row1_height)
            row.addWidget(mvmt_type_box)
            self.nonman_specifications[nonman.label] = nonman
            return row

        # subparts group
        if nonman.subparts is not None:
            subpart_specs = nonman.subparts
            subpart_box = QGroupBox("Sub-part(s)")
            subpart_box_layout = QVBoxLayout()
            subpart_box_layout.setAlignment(Qt.AlignTop)

            onepart_spacedlayout = QHBoxLayout()
            onepart_spacedlayout.setAlignment(Qt.AlignTop)

            onepart_layout = QHBoxLayout()
            onepart_layout.setAlignment(Qt.AlignTop)

            nonman.rb_subpart_both = SLPAARadioButton(f"Both {subpart_specs['specifier']}s")
            nonman.rb_subpart_one = SLPAARadioButton(f"One {subpart_specs['specifier']}")
            subpart_list = [nonman.rb_subpart_both, nonman.rb_subpart_one]

            nonman.subpart_group = SLPAAButtonGroup(subpart_list)

            nonman.subpart_group.buttonToggled.connect(lambda rb, ischecked:
                                                       self.handle_onepart_btn_toggled(rb, ischecked, nonman))

            nonman.rb_onepart_one = SLPAARadioButton("H1")
            nonman.rb_onepart_two = SLPAARadioButton("H2")
            onepart_list = [nonman.rb_onepart_one, nonman.rb_onepart_two]

            nonman.onepart_group = SLPAAButtonGroup(onepart_list)  # radiobutton group for H1 and H2

            nonman.onepart_group.buttonToggled.connect(lambda rb, ischecked:
                                                       self.handle_onepart_btn_toggled(rb, ischecked, nonman))

            [onepart_layout.addWidget(widget) for widget in onepart_list]
            onepart_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
            onepart_spacedlayout.addLayout(onepart_layout)

            [subpart_box_layout.addWidget(widget) for widget in subpart_list]
            subpart_box_layout.addLayout(onepart_spacedlayout)

            subpart_box.setLayout(subpart_box_layout)

            # set row1 height. the height should be fixed to give space to Action/State
            row1_height = subpart_box.sizeHint().height()
            subpart_box.setFixedHeight(row1_height)
            sd_rb_groupbox.setFixedHeight(row1_height)

            row.addWidget(subpart_box)

        # visibility group
        elif nonman.visibility is not None:
            visibility_box = QGroupBox("Visibility")
            visibility_box_layout = QVBoxLayout()
            visibility_box_layout.setAlignment(Qt.AlignTop)

            nonman.widget_rb_visible = SLPAARadioButton("Visible")
            visibility_box_layout.addWidget(nonman.widget_rb_visible)

            nonman.widget_rb_visible_not = SLPAARadioButton("Not visible")
            visibility_box_layout.addWidget(nonman.widget_rb_visible_not)

            visibility_box.setLayout(visibility_box_layout)

            # set row1 height. the height should be fixed to give space to Action/State
            row1_height = visibility_box.sizeHint().height()
            visibility_box.setFixedHeight(row1_height)
            sd_rb_groupbox.setFixedHeight(row1_height)
            row.addWidget(visibility_box)

        self.nonman_specifications[nonman.label] = nonman
        return row

    def handle_onepart_btn_toggled(self, rb, ischecked, nonman):
        if 'H' in rb.text() and ischecked:
            # H1 or H2 under One {specifier} selected.
            # make sure to have parent selected
            nonman.rb_subpart_one.setChecked(True)
        elif 'One' in rb.text() and not ischecked:
            # deselecting One should deselect its children.
            for btn in nonman.onepart_group.buttons():
                deselect_rb_group(btn.group())

    def handle_mid_rb_toggled(self, ischecked, asm, parent):
        """
        Middle button handler. When selected, select a parent. When deselected, grey out children.
        :param ischecked: Bool. whether the btn is checked
        :param asm: ActionStateModel from which button and children will be derived
        :param parent: QRadioButton or ActiostateModel object
        """
        btn_self = asm.main_btn
        print(f'[DEBUG] caught {btn_self.text()}. checked: {ischecked}')

        if ischecked:
            # toggle parent as well
            self.handle_btn_toggled(btn_self, True, parent)
        else:
            # kill children
            children = asm.as_btn_group.buttons() + asm.as_cb_list
            for btn in children:
                if isinstance(btn, QRadioButton):
                    deselect_rb_group(btn.group())
                else:
                    btn.setChecked(False)
                btn.repaint()  # mac specific issue

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
        row.setAlignment(Qt.AlignTop)

        # Action / state group

        action_state_groupbox = QGroupBox("Action / state")  # static/dynamic radio buttons group
        action_state_layout = QVBoxLayout()
        action_state_layout.setAlignment(Qt.AlignTop)

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
        """
        Parses the action state options, reletive to parent and options.options (children)
        """
        if isinstance(options, str):
            # in shallow module
            main_btn = SLPAARadioButton(options)
            parent.as_btn_group.addButton(main_btn)
            parent.widget_grouplayout_actionstate.addWidget(main_btn)
            parent.widget_grouplayout_actionstate.setAlignment(main_btn, Qt.AlignTop)
            main_btn.toggled.connect(lambda checked: self.handle_btn_toggled(main_btn, checked, parent))
            return

        elif options.label:
            # parse this node and its children
            options.widget_grouplayout_actionstate = QVBoxLayout()
            options.widget_grouplayout_actionstate.setAlignment(Qt.AlignTop)
            options.as_btn_group = SLPAAButtonGroup()  # btn group to contain children
            options.as_cb_list = []  # checkbox list to contain children

            main_layout = QVBoxLayout()
            main_layout.setAlignment(Qt.AlignTop)
            if options.exclusive:
                # create the button itself.
                options.main_btn = SLPAARadioButton(options.label)
                parent.as_btn_group.addButton(options.main_btn)

                # manage button behaviour -- (de)select parent/child as well.
                options.main_btn.toggled.connect(lambda checked:
                                                 self.handle_mid_rb_toggled(ischecked=checked,
                                                                            asm=options,
                                                                            parent=parent)
                                                 )
            else:
                # create the checkbox itself.
                options.main_btn = QCheckBox(options.label)
                parent.as_cb_list.append(options.main_btn)

                # manage checkbox behaviour -- (de)select parent/child as well.
                options.main_btn.stateChanged.connect(lambda checked:
                                                      self.handle_mid_rb_toggled(ischecked=checked,
                                                                                 asm=options,
                                                                                 parent=parent)
                                                      )

            main_layout.addWidget(options.main_btn)
            sub_layout = QVBoxLayout()
            sub_layout.setAlignment(Qt.AlignTop)

            sub_spacedlayout = QHBoxLayout()
            sub_spacedlayout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))

            if options.options is not None:
                # parse children
                for child in options.options:
                    if isinstance(child, str):
                        sub_rb = SLPAARadioButton(child)
                        sub_layout.addWidget(sub_rb)
                        options.as_btn_group.addButton(sub_rb)
                        sub_spacedlayout.addLayout(sub_layout)
                        #options.as_btn_group.buttonToggled.connect(
                        #    lambda rb, ischecked: self.handle_rb_toggled(rb, ischecked, options.main_btn))
                        sub_rb.toggled.connect(lambda checked: self.handle_btn_toggled(None, checked, options.main_btn))

                    else:
                        self.parse_actionstate(parent=options, options=child)
                        sub_spacedlayout.addLayout(options.widget_grouplayout_actionstate)
                main_layout.addLayout(sub_spacedlayout)
            parent.widget_grouplayout_actionstate.addLayout(main_layout)
        else:
            # in the root. be ready to go deeper
            options.widget_grouplayout_actionstate = QHBoxLayout()
            options.widget_grouplayout_actionstate.setAlignment(Qt.AlignTop)
            options.as_btn_group = SLPAAButtonGroup()
            options.as_cb_list = []
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
        row.setAlignment(Qt.AlignTop)

        # Repetition group
        repetition_group = QGroupBox("Repetition")
        repetition_group_layout = QVBoxLayout()
        repetition_group_layout.setAlignment(Qt.AlignTop)
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
        directionality_group_layout.setAlignment(Qt.AlignTop)
        nonman.widget_rb_direction_uni = SLPAARadioButton("Unidirectional")
        nonman.widget_rb_direction_bi = SLPAARadioButton("Bidirectional")
        directionality_list = [nonman.widget_rb_direction_uni, nonman.widget_rb_direction_bi]

        nonman.directionality_group = SLPAAButtonGroup(directionality_list)

        [directionality_group_layout.addWidget(widget) for widget in directionality_list]
        directionality_group.setLayout(directionality_group_layout)

        # Additional movement characteristics group -- contains Size Speed Force Tension
        additional_char_group = QGroupBox("Additional mvmt characteristics")
        additional_char_group_layout = QHBoxLayout()
        additional_char_group_layout.setAlignment(Qt.AlignTop)
        additional_char_specs = {'Size': ['Big', 'Small'],
                                 'Speed': ['Fast', 'Slow'],
                                 'Force': ['Strong', 'Weak'],
                                 'Tension': ['Tense', 'Lax']}
        additional_subgroups, additional_rb_groups = self.gen_add_move_char(additional_char_specs)
        [additional_char_group_layout.addWidget(widget) for widget in additional_subgroups]
        nonman.additional_char_rb_group = additional_rb_groups

        additional_char_group.setLayout(additional_char_group_layout)

        # set fixed height. fixed b/c more space for action/state
        row3_height = additional_char_group.sizeHint().height()
        repetition_group.setFixedHeight(row3_height)
        directionality_group.setFixedHeight(row3_height)  # fixed for space to action/state
        additional_char_group.setFixedHeight(row3_height)

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
        _, v = self.package_action_state(current_module.action_state)
        as_dict['root'] = v

        module_output['action_state'] = as_dict

        return module_output

    def package_action_state(self, asm):
        # parent: parent ActionStateModel
        # asm: ActionStateModel to be packaged as dictionary.
        r = {}
        selected_cb = what_selected(asm.as_cb_list)
        selected_btn = what_selected(asm.as_btn_group)
        selected_options = selected_cb + [selected_btn] if selected_btn is not None else selected_cb

        for child in asm.options:
            at_bottom = False
            if isinstance(child, str):
                # bottom radio buttons
                at_bottom = True
            elif child.label not in selected_options:
                # not a selected option, then skip packaging.
                continue
            elif child.options is None:
                # bottom check boxes
                at_bottom = True

            if at_bottom:
                # at the bottom
                if selected_btn is not None and child == selected_btn:
                    r[selected_btn] = {}
                elif len(selected_cb) > 0:
                    for cb in selected_cb:
                        r[cb] = {}
            else:
                res_k, res_v = self.package_action_state(child)
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

    def clear(self):
        self.setvalues(self._clean_nonman)

    def setvalues(self, moduletoload):
        # load saved values and set template values by them.
        toload_dict = moduletoload

        if not isinstance(moduletoload, dict):
            # moduletoload is a NonManualModule, so extract _nonmanual from it
            toload_dict = moduletoload._nonmanual

        major_modules = [module_title.label for module_title in nonmanual_root.children]  # major modules in non manual
        template = self.nonman_specifications  # empty template of specification window

        for module in major_modules:
            values_toload = toload_dict[module]
            load_destination = template[module]
            load_destination = load_specifications(values_toload, load_destination)
            if values_toload['children'] is None:  # Does not include embedded tabs
                continue
            for i, (label, child) in enumerate(values_toload['children'].items()):
                child_values_toload = child
                child_load_destination = template[label]
                load_destination.children[i] = load_specifications(child_values_toload, child_load_destination)

    def handle_btn_toggled(self, _, ischecked, parent):
        """
        Bottom button handler. When selected ensure its parent is also selected.
        :param ischecked: Bool. Whether the button is checked
        :param parent: QRadioButton or ActiostateModel object
        """
        parent_btn = id_parent(parent)

        if parent_btn is None:
            return

        if ischecked:
            # ensure the parent is checked
            parent_btn.setChecked(True)
            parent_btn.repaint()  # mac specific issue

        else:
            parent_btn.setChecked(False)
            parent_btn.repaint()


def deselect_rb_group(rb_group):
    rb_group.setExclusive(False)
    [btn.setChecked(False) for btn in rb_group.buttons()]
    rb_group.setExclusive(True)


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
        else:
            # deselect all
            select_this(btn_group=load_destination.subpart_group,
                        btn_txt=None)
            select_this(btn_group=load_destination.onepart_group,
                        btn_txt=None)

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

    # action state
    try:
        as_to_load = values_toload['action_state']  # packaged action_state selections. comes as Dict
        if len(as_to_load['root']) != 0:
            load_destination.action_state = load_actionstate(as_to_load, load_destination.action_state)
        else:
            # initialize action_state (i.e., deselct all)
            deselect_all(load_destination.action_state)
    except KeyError:
        pass

    return load_destination


def deselect_all(asm):
    # deselect checkbox children
    [cb.setChecked(False) for cb in asm.as_cb_list]

    # deselect radiobutton children
    deselect_rb_group(asm.as_btn_group)


def load_actionstate(saved_dict, asm, parent=None):
    # see content of saved_dict and fill out the action state part of the nonman spec dialog (asm)
    # saved_dict: Dict. previous action_state selections
    # asm: ActionStateModel
    # parent: ActionStateModel that is one level higher than asm or None (if asm is the root)
    for i, child in enumerate(asm.options):
        bottom = False
        if isinstance(child, str):
            bottom = True
        elif child.options is None:
            # bottom check boxes
            bottom = True
            child = child.label

        if bottom:
            # bottom. select a button or cb.
            if parent is None:
                # shallow button/checkbox directly connected to the root
                to_select = [key for key, value in saved_dict['root'].items() if len(value) == 0]
            else:
                to_select = get_value_from_saved_dict(key_to_find=asm.label,
                                                      input_dict=saved_dict,
                                                      parent=parent.label)
                to_select = list(to_select.keys())
            if child in to_select:
                all_cb = [cb.text() for cb in asm.as_cb_list]
                all_btn = asm.as_btn_group.buttons()
                if child in all_cb:
                    checkmark_this(asm.as_cb_list, child)
                elif child in all_btn:
                    select_this(asm.as_btn_group, child)
        else:
            if get_value_from_saved_dict(child.label, saved_dict, asm.label) is not None:
                if len(asm.as_cb_list) > 0:
                    checkmark_this(asm.as_cb_list, child.label)
                else:
                    select_this(asm.as_btn_group, child.label)
                asm.options[i] = load_actionstate(saved_dict, child, parent=asm)
    return asm


def id_parent(parent):
    """
    who is your parent? safely identify the parent button or checkbox.
    """
    if isinstance(parent, QCheckBox):
        # parent is a checkbox
        return parent

    elif not isinstance(parent, QRadioButton):
        # parent is not a button but an ActiostateModel. Need to get main_btn (button or checkbox) from it.
        try:
            return parent.main_btn
        except AttributeError:
            # dealing with the root. root has no btn.
            return None

    return parent


def get_value_from_saved_dict(key_to_find, input_dict, parent=None):
    parent = 'root' if parent is None else parent

    # Check if the parent is in the dictionary
    if parent in input_dict and isinstance(input_dict[parent], dict):
        # Check if the key to find is in the parent dictionary
        if key_to_find in input_dict[parent]:
            return input_dict[parent][key_to_find]

    # If the key is not found, recursively search in nested dictionaries
    for key, value in input_dict.items():
        if isinstance(value, dict):
            result = get_value_from_saved_dict(key_to_find=key_to_find,
                                               input_dict=value,
                                               parent=parent)
            if result is not None:
                return result

    # Return None if the key is not found in the dictionary
    return None


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
    if not isinstance(btn_group, SLPAAButtonGroup):
        return None

    if btn_txt is None:
        # reset to the default
        deselect_rb_group(btn_group)
        return

    for btn in btn_group.buttons():
        if btn.text() == btn_txt:
            btn.setChecked(True)
            return


def checkmark_this(cb_list, cb_text):
    if len(cb_list) == 0:
        return None

    for cb in cb_list:
        if cb.text() == cb_text:
            cb.setChecked(True)
            return
