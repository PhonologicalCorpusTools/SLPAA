from PyQt5.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QButtonGroup,
    QGroupBox,
    QCheckBox,
    QSpacerItem,
    QSizePolicy,
    QTabWidget, QScrollArea, QRadioButton, QLineEdit, QProxyStyle, QWidget, QLabel, QDoubleSpinBox
)
from PyQt5.QtCore import (Qt, pyqtSignal,)

from lexicon.module_classes import NonManualModule
from models.nonmanual_models import NonManualModel, nonmanual_root
from gui.relationspecification_view import RelationRadioButton
from gui.relationspecification_view import RelationButtonGroup
from gui.modulespecification_widgets import ModuleSpecificationPanel


class SLPAARadioButton(RelationRadioButton):
    def __init__(self, text, **kwargs):
        super().__init__(text, **kwargs)

    def setChecked(self, checked):
        # override RelationRadioButton's setChecked() method to deal with programmatically unselected btns.
        if self.group() is not None:
            if checked:
                self.group().previously_checked = self
            else:
                self.group().previously_checked = None
        super().setChecked(checked)


class SLPAAButtonGroup(RelationButtonGroup):
    def __init__(self, buttonslist=None):
        # buttonslist: list of QRadioButton to be included as a group
        super().__init__()
        if buttonslist is not None:
            [self.addButton(button) for button in buttonslist]


class SpecifyLayout(QHBoxLayout):
    # something like " ○ Other: ________" that consists of radiobutton + lineEdit
    def __init__(self, btn_label, text):
        super().__init__()
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        # radio button
        self.radio_btn = SLPAARadioButton(btn_label)
        self.radio_btn.toggled.connect(self.radio_button_toggled)
        self.addWidget(self.radio_btn)

        # line edit
        self.lineEdit = QLineEdit()
        self.lineEdit.setPlaceholderText(text)

        self.lineEdit.textEdited.connect(lambda content: self.handle_txt_edit(content, self.radio_btn))
        self.addWidget(self.lineEdit)

    def handle_txt_edit(self, content, radio_btn):
        if content == "":
            return

        # if txt entered, check its partner radio_button
        self.radio_btn.setChecked(True)

    def radio_button_toggled(self, checked):
        # called whenever radiobutton is toggled.
        self.lineEdit.setEnabled(checked)


class RepetitionLayout(QVBoxLayout):
    # something like the below. (I know this will only be used once, but it seemed complicated for my monkey brain.)
    # ○ Repeated  (radio button)
    #   specify total # ______ (lineEdit)
    #   [ ] This # is minimum (checkbox)

    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # radio button
        self.repeated_btn = SLPAARadioButton("Repeated")
        self.repeated_btn.toggled.connect(self.toggle_repeated)
        self.repeated_btn.setFixedHeight(self.repeated_btn.sizeHint().height())
        self.addWidget(self.repeated_btn)

        # fixed indentation for the 'specify...' lineEdit and the 'minimum' checkbox
        self.indented_layout = QVBoxLayout()
        self.indented_layout.setContentsMargins(15, 0, 0, 0)

        # specify... spinner
        n_of_cycles_layout = QHBoxLayout()
        n_cycle_label = QLabel("Specify total number of cycles:")
        self.n_cycle_input = QDoubleSpinBox()
        self.n_cycle_input.setRange(0.5, 100.0)
        self.n_cycle_input.setSingleStep(0.5)  # accept half as valid input
        self.n_cycle_input.setDecimals(1)      # show one decimal place after the demal point

        self.n_cycle_input.setValue(1.0)  # default value = 1

        self.n_cycle_input.setFixedHeight(self.n_cycle_input.sizeHint().height())
        n_cycle_label.setFixedHeight(self.n_cycle_input.sizeHint().height())

        n_of_cycles_layout.addWidget(n_cycle_label)
        n_of_cycles_layout.addWidget(self.n_cycle_input)
        self.indented_layout.addLayout(n_of_cycles_layout)

        # 'This number is a minimum' checkbox
        self.minimum_checkbox = QCheckBox("This number is a minimum")
        self.indented_layout.addWidget(self.minimum_checkbox)

        # indented layout to main layout
        self.addLayout(self.indented_layout)

        self.toggle_repeated(False)  # when initializing, sub options of repeated should be greyed out

    def toggle_repeated(self, checked):
        # enable sub options of 'repeated' button when 'repeated' selected.
        # sub options: specify the number of cycles and check if this number of minimum
        self.n_cycle_input.setEnabled(checked)
        self.minimum_checkbox.setEnabled(checked)
        return



class BoldTabBarStyle(QProxyStyle):
    def __init__(self, bold_tab_index=None):
        super().__init__()
        if bold_tab_index is not None:
            self.bold_tab_index = bold_tab_index
        else:
            self.bold_tab_index = []

    def drawControl(self, element, option, painter, widget=None):
        if element == self.CE_TabBarTabLabel:
            # Check if the current tab index is the bold one

            font = painter.font()
            if widget.tabAt(option.rect.center()) in self.bold_tab_index:
                font.setBold(True)
            else:
                font.setBold(False)
            painter.setFont(font)

        super().drawControl(element, option, painter, widget)

    def setBoldTabIndex(self, index, need_bold=True):
        if isinstance(index, int):
            if need_bold:
                # need bold tab label, so indicate this by adding index to the list
                self.bold_tab_index.append(index)
                self.bold_tab_index = list(set(self.bold_tab_index))
                return
            try:
                self.bold_tab_index.remove(index)
            except ValueError:  # index at hand not in bold_tab_index list but ok
                pass

        elif isinstance(index, list):
            self.bold_tab_index.extend(index)

class TabContentWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)


class NMTabWidget(QTabWidget):
    def __init__(self):
        super().__init__()
        self.tab_bar = self.tabBar()
        self.tab_bar.setStyle(BoldTabBarStyle())
        self.currentChanged.connect(self.decide_bold_label)

    def check_components(self, widget):
        all_cb = widget.findChildren(QCheckBox)
        all_rb = widget.findChildren(QRadioButton)
        input_slots = all_cb + all_rb
        return any(slot.isChecked() for slot in input_slots)

    def decide_bold_label(self, index):
        # called when tab selection updates.
        # it decides which tabs need the label bolded
        print(f'[DEBUG] Switching to Tab {index}')
        idx = 0
        while self.widget(idx) is not None:
            need_bold = self.check_components(self.widget(idx))
            self.tab_bar.style().setBoldTabIndex(idx, need_bold)
            idx += 1
        self.setCurrentIndex(index)

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
        self.widget_cb_neutral.stateChanged.connect(self.greyout_all)

        # non manual specs
        self.nonman_specifications = {}

        # different major non manual tabs
        self.tab_widget = NMTabWidget()                   # Create a tab widget
        self.create_major_tabs(nonmanual_root.children)   # Create and add tabs to the tab widget
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

    def greyout_all(self, state):
        # state: bool. whether the 'all section neutral' cb checked
        need_disable = state == Qt.Checked

        if not need_disable:
            # unchecking 'all neutral' does NOT mean unchecking children 'this section neutral'
            return

        # However, checking 'all neutral' should also check all children 'this ... neutral'
        this_neutral_cbs = [w for w in self.tab_widget.findChildren(QCheckBox) if 'This section' in w.text()]
        for cb in this_neutral_cbs:
            cb.setChecked(need_disable)

    def greyout_row3(self, toggled, current_tab):
        # toggled: bool. whether the 'static' (contra 'dynamic') radio button selected
        # current_tab: str. in which tab the static radio button selected?
        # selecting 'static' -> greyout movement characteristics i.e., row3

        enable_row3 = not toggled  # enable row 3 when static is 'unselected'
        tab = self.nonman_specifications[current_tab]

        if not any([hasattr(tab, 'repetition_group'),
                    hasattr(tab, 'directionality_group'),
                    hasattr(tab, 'additional_char_rb_group')]):
            # if there is no row3, nothing to grey out.
            return

        target_groups = [tab.repetition_group, tab.directionality_group] + tab.additional_char_rb_group  # groups in row3

        target_rbs = []  # container for all target radio buttons included in row3's buttongroups
        for g in target_groups:
            target_rbs += g.buttons()

        for rb in target_rbs:
            # iterate over each radio button in row3 and set enable/disable
            rb.setEnabled(enable_row3)
        return

    def create_major_tabs(self, nonman_units):
        """
        Populate major non-manual articulators like shoulder, body, and head
        Args:
            nonman_units: list of NonManualModel
        """

        for nonman_unit in nonman_units:
            major_tab = self.gen_tab_widget(nonman_unit)
            self.tab_widget.addTab(major_tab, nonman_unit.label)

    def gen_tab_widget(self, nonman):
        """
            Deal with the mundane hassle of adding tab gui, recursively
            Args:
                nonman: NonManualModel
        """
        tab_widget = TabContentWidget()

        # This section is neutral
        nonman.widget_cb_neutral = QCheckBox("This section is neutral")
        tab_widget.layout.addWidget(nonman.widget_cb_neutral)
        nonman.widget_cb_neutral.stateChanged.connect(lambda state: self.greyout_children(state,
                                                                                          nonman.widget_cb_neutral,
                                                                                          tab_widget))

        row_1 = self.build_row1(nonman)  # [ static / dynamic ] [ Sub-parts ]
        row_2 = self.build_row2(nonman)  # action / state
        row_3 = self.build_row3(nonman)  # mvmt characteristics

        rows = [row_1, row_2, row_3]
        [tab_widget.layout.addLayout(row) for row in rows if row is not None]

        if nonman.children:
            subtabs_container = NMTabWidget()
            for sub_category in nonman.children:
                sub_tab = self.gen_tab_widget(sub_category)
                subtabs_container.addTab(sub_tab, sub_category.label)
            tab_widget.layout.addWidget(subtabs_container)
            tab_widget.setLayout(tab_widget.layout)
            return tab_widget

        tab_widget.setLayout(tab_widget.layout)

        return tab_widget

    def greyout_children(self, state, itself, child_tab):
        # called when 'this section is neutral' checkbox state changes
        # have all children widgets disabled when checked / enabled when unchecked
        # itself: clicked checkbox itself
        need_disable = state == Qt.Checked

        # unchecking any 'this section is neutral' means NOT 'all sections are neutral'
        if not need_disable:
            self.widget_cb_neutral.setChecked(False)

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

        nonman.widget_rb_static.toggled.connect(lambda toggled: self.greyout_row3(toggled, nonman.label))


        # special case: 'mouth' requires 'Type of mouth movement' which is contained in .subparts
        if nonman.label == 'Mouth':
            mvmt_type_box = QGroupBox("Type of mouth movement")
            mvmt_type_box_layout = QVBoxLayout()
            mvmt_type_box.setAlignment(Qt.AlignTop)
            nonman.mvmt_type_group = SLPAAButtonGroup()
            for type in nonman.subparts:
                if ';' in type:
                    type, txt_line = type.split(';')
                    specify_layout = SpecifyLayout(btn_label=type,
                                                   text=txt_line)
                    rb_to_add = specify_layout.radio_btn
                    nonman.widget_le_specify = specify_layout.lineEdit
                    mvmt_type_box_layout.addLayout(specify_layout)
                else:
                    rb_to_add = SLPAARadioButton(type)
                    mvmt_type_box_layout.addWidget(rb_to_add)
                nonman.mvmt_type_group.addButton(rb_to_add)
            mvmt_type_box.setLayout(mvmt_type_box_layout)
            row1_height = mvmt_type_box.sizeHint().height()
            mvmt_type_box.setFixedHeight(row1_height)
            sd_rb_groupbox.setFixedHeight(row1_height)
            row.addWidget(mvmt_type_box)
            row.setStretchFactor(sd_rb_groupbox, 1)
            row.setStretchFactor(mvmt_type_box, 1)
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

            rb_onepart_one = SLPAARadioButton("H1")
            rb_onepart_two = SLPAARadioButton("H2")
            onepart_list = [rb_onepart_one, rb_onepart_two]

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

        if ischecked:
            # toggle parent as well
            self.handle_btn_toggled(btn_self, True, parent)
        else:
            # kill children
            children = asm.as_btn_group.buttons() + asm.as_cb_list
            for btn in children:
                if not btn.isChecked():
                    # if the btn/cb is not already checked, just leave it alone
                    continue
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
        Parses the action state options, relative to parent and options.options (children)
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
            sub_spacedlayout.setAlignment(Qt.AlignTop)
            sub_spacedlayout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))

            if options.options is not None:
                # parse children
                for child in options.options:
                    if isinstance(child, str):
                        if ';' in child:
                            # 'Other, specify' (e.g., Eye Gaze > Action/State). Need radiobutton and lineEdit
                            rb_label, txt_line = child.split(';')
                            specify_layout = SpecifyLayout(btn_label=rb_label, text=txt_line)
                            sub_layout.addLayout(specify_layout)

                            # to reference lineEdit content
                            if hasattr(options, 'widget_le_specify'):
                                options.widget_le_specify[rb_label] = specify_layout.lineEdit
                            else:
                                options.widget_le_specify = {
                                    rb_label: specify_layout.lineEdit
                                }

                            # to reference dynamic btn
                            sub_rb = specify_layout.radio_btn
                        else:
                            sub_rb = SLPAARadioButton(child)
                            sub_layout.addWidget(sub_rb)
                        options.as_btn_group.addButton(sub_rb)
                        sub_spacedlayout.addLayout(sub_layout)

                        sub_rb.toggled.connect(lambda checked: self.handle_btn_toggled(None, checked, options.main_btn))

                    else:
                        self.parse_actionstate(parent=options, options=child)
                        sub_spacedlayout.addLayout(options.widget_grouplayout_actionstate)
                        sub_spacedlayout.setStretchFactor(options.widget_grouplayout_actionstate, 1)
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
        widget_rb_rep_single = SLPAARadioButton("Single")
        nonman.layout_repetition = RepetitionLayout()
        widget_rb_rep_trill = SLPAARadioButton("Trilled")
        rep_btn_list = [widget_rb_rep_single, nonman.layout_repetition.repeated_btn, widget_rb_rep_trill]

        nonman.repetition_group = SLPAAButtonGroup(rep_btn_list)

        repetition_group_layout.addWidget(widget_rb_rep_single)
        repetition_group_layout.addLayout(nonman.layout_repetition)
        repetition_group_layout.addWidget(widget_rb_rep_trill)

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

        # groups that constitute the third row
        groups = [repetition_group, directionality_group, additional_char_group]

        # set fixed height. fixed b/c more space for action/state
        row3_height = max([group.sizeHint().height() for group in groups])
        [group.setFixedHeight(row3_height) for group in groups]

        [row.addWidget(group) for group in groups]  # Adding all the groupboxes to form the row
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
            this_module = usr_input[module]
            res[module] = self.get_nonman_specs(this_module)
        return res

    def get_nonman_specs(self, current_module, parent=None):
        # this function parses user inputs and return a dict.
        module_output = {'neutral': current_module.widget_cb_neutral.isChecked()}

        if module_output['neutral'] is True:
            # if 'this section is neutral' selected, just return module_output
            return module_output

        module_output['static_dynamic'] = what_selected(current_module.static_dynamic_group)

        # special case: 'mouth' has 'type of mouth movement' (others have 'subparts')
        if current_module.label == 'Mouth':
            module_output['mvmt_type'] = what_selected(current_module.mvmt_type_group)
            if module_output['mvmt_type'] == 'other':
                module_output['mvmt_type'] = f"{module_output['mvmt_type']};{current_module.widget_le_specify.text()}"
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
        module_output['repetition'] = what_selected(current_module.repetition_group)
        if module_output['repetition'] == 'Repeated':
            # if 'Repeated btn is selected, go one step further and save the number of cycles and whether it is minimum
            module_output['repetition'] = {'type': 'Repeated',
                                           'n_repeats': current_module.layout_repetition.n_cycle_input.value(),
                                           'minimum': current_module.layout_repetition.minimum_checkbox.isChecked()}
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
                if selected_btn is not None and selected_btn in child:
                    r[selected_btn] = {}
                    if ';' in child:
                        r[selected_btn] = asm.widget_le_specify[selected_btn].text()
                elif len(selected_cb) > 0:
                    for cb in selected_cb:
                        if cb not in r:
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
        # called when loading previously saved specifications (e.g., by clicking on an xslot)
        # set template values by moduletoload (previously saved values)
        toload_dict = moduletoload

        if not isinstance(moduletoload, dict):
            # moduletoload is a NonManualModule, so extract _nonmanual from it
            toload_dict = moduletoload._nonmanual

        major_modules = [module_title.label for module_title in nonmanual_root.children]  # major modules in non manual
        template = self.nonman_specifications  # empty template of specification window

        all_neutral_flag = True  # flag to decide whether to select 'all sections are neutral'

        for module in major_modules:
            values_toload = toload_dict[module]
            load_destination = template[module]
            load_destination = load_specifications(values_toload, load_destination)

            if load_destination.widget_cb_neutral.isChecked():
                # if 'this section is neutral' selected, move on to the next major module
                continue
            else:
                all_neutral_flag = False

            if values_toload['children'] is None:  # does not include embedded tabs
                continue                           # then move on

            for i, (label, child) in enumerate(values_toload['children'].items()):
                child_values_toload = child
                child_load_destination = template[label]
                load_destination.children[i] = load_specifications(child_values_toload, child_load_destination)

        # all neutral
        if all_neutral_flag:
            self.widget_cb_neutral.setChecked(True)

        # loading per se done.
        # now programmatically move tab to 'target' and then to the first tab, in order to invoke the tab bold behaviour
        target = self.tab_widget.count() - 1     # where to? to the last tab
        self.tab_widget.setCurrentIndex(target)
        self.tab_widget.repaint()
        self.tab_widget.setCurrentIndex(0)  # back to the first

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

    if values_toload['neutral']:
        # if the section is neutral, just check 'this section is neutral' and return
        load_destination.widget_cb_neutral.setChecked(True)
        return load_destination

    load_destination.widget_cb_neutral.setChecked(False)

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

    # special case: 'mouth' movement type
    try:
        mvmt_type = values_toload['mvmt_type']
        if mvmt_type is None:
            raise KeyError
        if ';' in mvmt_type:
            # selected 'other' and specified
            mvmt_type, content = mvmt_type.split(';')
            load_destination.widget_le_specify.setText(content)
        select_this(btn_group=load_destination.mvmt_type_group,
                    btn_txt=mvmt_type)

    except KeyError:
        pass

    # repetition
    try:
        if values_toload['repetition'] is None:
            # repetition not specified. need to bypass btn selection process so raising an error
            raise AttributeError
        elif isinstance(values_toload['repetition'], dict):
            # selected repetition > repeated
            rep_rb_label = values_toload['repetition']['type']
            load_destination.layout_repetition.n_cycle_input.setValue(values_toload['repetition']['n_repeats'])
            load_destination.layout_repetition.minimum_checkbox.setChecked(values_toload['repetition']['minimum'])
        elif isinstance(values_toload['repetition'], str):
            rep_rb_label = values_toload['repetition']
        else:
            print("[DEBUG] Trying to load unexpected 'repetition' type")
            raise AttributeError

        select_this(btn_group=load_destination.repetition_group,
                    btn_txt=rep_rb_label)

    except (AttributeError, KeyError):
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
            specify_flag = False  # flag for complex 'others: specify' cases
            # bottom. select a button or cb.
            if parent is None:
                # shallow button/checkbox directly connected to the root
                to_select_list = [key for key, value in saved_dict['root'].items() if len(value) == 0]
            else:
                to_select = get_value_from_saved_dict(key_to_find=asm.label,
                                                      input_dict=saved_dict,
                                                      parent=parent.label)
                to_select_list = list(to_select.keys())
                if ';' in child:
                    # dealing with a 'specify' item
                    specify_flag = True
                    child, _ = child.split(';')
            if child in to_select_list:
                all_cb = [cb.text() for cb in asm.as_cb_list]
                all_btn = [btn.text() for btn in asm.as_btn_group.buttons()]
                if child in all_cb:
                    checkmark_this(asm.as_cb_list, child)
                elif child in all_btn:
                    select_this(asm.as_btn_group, child)
                    if specify_flag:
                        specified_value = to_select[child]
                        asm.widget_le_specify[child].setText(specified_value)
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
    if isinstance(group, QButtonGroup):
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
