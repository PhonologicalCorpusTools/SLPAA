from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QSplitter, QComboBox, \
    QLabel, QHBoxLayout, QPushButton, QWidget, QFrame, QButtonGroup, QRadioButton, QToolButton
from PyQt5.QtGui import QBrush, QColor, QPalette
from PyQt5.QtCore import Qt
import re
from typing import Union

from compare_signs.compare_models import CompareModel
from compare_signs.compare_helpers import qcolor_to_rgba_str, parse_button_type, rb_red_buttons, next_pair_id
from compare_signs.draw_compare_tree import trunc_count_and_label

# This class stores all the details needed for presenting each line (CompareTreeWidgetItem)
class TreeWidgetItemKey:
    def __init__(self, key: Union[str, int], original_keys: list, data: dict, depth: int):
        self.path_context: dict = data  # the path where the key appears
        self.depth: int = depth        # specifically where in the path the key appears
        self.key: str = self.get_original_key(original_keys, key)

        try:
            self.children = self.path_context[self.key]
            self.vacuous = False
        except KeyError:
            self.children = None
            self.vacuous = True

        btn_type = parse_button_type(node_data=self.path_context, k=self.key)  # eg 'radio button', 'major loc'
        try:
            self.btn_type = '' if (depth < 0 or self.vacuous) else btn_type[depth]
        except IndexError:
            # eventually fix this
            self.btn_type = ''

    # wrapper for __eq__ with hand shape broad match option
    def equals(self, other, handshape_broad_match):
        # handshape_broad_match: bool. consider equal the following these pairs
        # f/F = ‘flexed’ and e/E/H = ‘extended’ and x-, x, x+, [x] = ‘crossed’

        # helper function
        def convert_for_broad_match(key):
            if key in ['f', 'F']:
                return 'flexed'
            elif key in ['e', 'E', 'H']:
                return 'extended'
            elif key in ['x-', 'x', 'x+', '\u2327']:  # '\u2327' is the unicode for 'X in square'
                return 'crossed'
            return key

        if not isinstance(other, self.__class__):
            return NotImplemented

        this_key = self.key
        that_key = other.key

        if handshape_broad_match:
            this_key = convert_for_broad_match(this_key)
            that_key = convert_for_broad_match(that_key)
        return (
            this_key == that_key and
            self.btn_type == other.btn_type and
            self.vacuous == other.vacuous
        )

    def __repr__(self):
        vacuous = ' (vacuous)' if self.vacuous else ''
        return f'<TreeWidgetItemKey {self.key!r}{vacuous}>'

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented
        return (
                self.key == other.key and
                self.btn_type == other.btn_type and
                self.vacuous == other.vacuous
        )

    # find alternative data and update key and children. called when different lines should align
    def update_with_alternative(self, target_btn_type):
        # 'alternative key' is the key that should be presented on the same line as the counterpart key.
        # for example, if Location modules are specified as
        # Sign1: Signing space>Purely spatial... and Sign2: Signing space> Body anchored,
        # Sign1's Purely spatial and Sign2's Body anchored should align, while coloured red.

        depth = self.depth

        if depth < 0:
            print("[DEBUG] update_with_alternative() is called with a negative depth.")
            return

        for k, v in self.path_context.items():
            if parse_button_type(node_data=self.path_context, k=k)[depth] == target_btn_type:
                self.key = k
                self.children = v
                self.btn_type = target_btn_type
                self.vacuous = False
                return

        print("[DEBUG] update_with_alternative() cannot find an alternative key.")
        return

    def get_original_key(self, many_keys: list, key: Union[str, int]):
        if isinstance(key, int):
            for i in many_keys:
                if ':' in i and i.split(':')[0] == str(key):
                    return i
        return key

# This class represents one row consisting of three counters
class ColourCounter(QWidget):
    def __init__(self, palette):
        super().__init__()

        # Main layout
        self.layout = QHBoxLayout()

        # red, yellow blue rgba to be used for creating label background
        rgba_dict = {key: qcolor_to_rgba_str(brush.color()) for key, brush in palette.items()}

        # what we mean by each colour
        colour_mapping = [
            ('red', "Mismatch"),
            ('yellow', "No\nCorrespondence"),
            ('blue', "Match")
        ]

        # create a set of colour counters ('all expanded', 'current' and 'all collapsed')
        self.counters = {}

        for colour_key, meaning in colour_mapping:
            counter_layout, count_label = self.gen_colour_counter_label(text=meaning,
                                                                        count="999",  # just a random number
                                                                        color=rgba_dict[colour_key])
            self.layout.addLayout(counter_layout)
            setattr(self, f'{colour_key}_counter', counter_layout)
            setattr(self, f'{colour_key}_many', count_label)
            self.counters[colour_key] = count_label   # just for easy access...

        self.setLayout(self.layout)

    def gen_colour_counter_label(self, text, count, color):
        h_layout = QHBoxLayout()  # [label] [counter], horizontally

        # label. should have background in the given colour
        label = QLabel(text)
        label.setStyleSheet(f'background-color: {color}; color: black;')
        label.setFixedWidth(100)
        label.setAlignment(Qt.AlignLeft)

        # counter outside the label
        count_txt = QLabel(count)
        count_txt.setFixedWidth(50)
        count_txt.setAlignment(Qt.AlignLeft)

        # Add both labels to the horizontal layout
        h_layout.addWidget(label)
        h_layout.addWidget(count_txt)
        return h_layout, count_txt

    def update_counter(self, label=None, new_count=None):
        # let's make this method simple. since I know there are only three colours
        # red, yellow, and blue, just take a colour term as 'label' and get this function
        # do the rest.
        if isinstance(label, dict):
            # updating all colours and label is given something like {'red': 4, 'yellow': 2, 'blue': 1}
            for label, count in label.items():
                self.update_counter(label=label, new_count=count)
            return

        label_txt = self.counters.get(label)
        if label_txt:
            label_txt.setText(f"{new_count}")


# This class represents one line in the compare tree
class CompareTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, labels, palette, truncated_count=0, pair_id=0, override_is_label=False):
        super().__init__(labels)

        self._text = self.text(0)

        # number of truncated lines -- for printing out and updating the colour counters.
        self.truncated_count = truncated_count

        # underlying and current background colours are unspecified by default, but may be blue red or yellow!
        self.underlying_bg = None  # colour when collapsed, considering children's matching
        self.current_bg = None     # 'apparent' background colour, only considering the current tree configurations
        self.force_underlying = False   # if True, expanding/collapsing does not change the background colour

        # information on background colour when folded in the compare tree
        self.red_when_folded_hint = False   # do not colour red by default

        # imagine each tree item carries a palette and use it to change background colour
        self.palette = palette

        self.is_root: bool = False
        if self._text in ['movement', 'relation', 'orientation', 'location', 'handconfig']:
            self.is_root = True

        self.is_label: bool = False
        if override_is_label or ':' in self._text or self.is_root:
            self.is_label = True

        # pair_id to help finding corresponding line in the other tree
        self.pair_id = pair_id

    def __repr__(self):
        invisibility = self.flags() == Qt.NoItemFlags
        invisibility = 'in' if invisibility else ''
        return f'<CompareTreeWidgetItem {self._text!r}, pair_id: {self.pair_id} ({invisibility}visible)>'

    def __eq__(self, other):
        return self._text == other._text and self.flags() == other.flags()

    def initialize_bg_color(self, colour: str = 'transparent'):
        # called when populating a tree. when a line gets created, same bg colours for underlying and current
        if self.background(0).color().name() != self.palette['transparent'].color().name():
            # if the line's colour has already been initialized, do nothing
            return
        self.underlying_bg = colour   # set the 'collapsed' colour
        self.current_bg = colour
        colour_brush = self.palette.get(colour, self.palette['transparent'])
        self.setBackground(0, colour_brush)

    def set_bg_color(self, colour: str = 'transparent'):
        # wrapper for the parent's setBackround method
        colour_brush = self.palette[colour] if colour in self.palette else self.palette['transparent']
        self.setBackground(0, colour_brush)
        self.current_bg = colour


# This is the main class for compare trees dialog
class CompareSignsDialog(QDialog):
    def __init__(self, selected_signs, **kwargs):
        super().__init__(**kwargs)

        self.corpus = self.parent().corpus
        self.signs = self.corpus.signs  # don't need meta-data; only need 'signs' part

        # default sign comparison options
        self.comparison_options = {
            'handconfig': {
                'compare_target': 'predefined',
                'details': False
            }
        }

        # the main layout
        layout = QVBoxLayout()

        # Tree widgets for hierarchical variables
        self.tree1 = QTreeWidget()
        self.tree2 = QTreeWidget()
        self.tree1.setHeaderLabel("Sign 1")
        self.tree2.setHeaderLabel("Sign 2")
        self.tree1.setSelectionMode(QTreeWidget.NoSelection)
        self.tree2.setSelectionMode(QTreeWidget.NoSelection)

        # colour scheme to be used throughout the dialog
        self.palette = {'red': QBrush(QColor(255, 0, 0, 128)),
                        'blue': QBrush(QColor(0, 100, 255, 64)),
                        'yellow': QBrush(QColor(255, 255, 0, 128)),
                        'transparent': QBrush(QColor(0, 0, 0, 0)),
                        'grey': QBrush(self.tree1.palette().color(QPalette.Base))
                        # grey is for the greyed-out lines (exact colour varies by light/dark mode)
                        }

        # Gen 3 x 3 colour counters for each of two signs
        sign1_counters = self.initialize_sign_counters()
        sign2_counters = self.initialize_sign_counters()

        self.expanded_colour_counter_1 = sign1_counters["all expanded"]
        self.current_colour_counter_1 = sign1_counters["current"]
        self.collapsed_colour_counter_1 = sign1_counters["all collapsed"]

        self.expanded_colour_counter_2 = sign2_counters["all expanded"]
        self.current_colour_counter_2 = sign2_counters["current"]
        self.collapsed_colour_counter_2 = sign2_counters["all collapsed"]

        # Vertical tree layout for signs 1 and 2 (tree, expand/collapse btns, and counters)
        sign_tree_and_counters_layout = self.initialize_signs_layout(sign1_counters, sign2_counters)

        # Add OK and Cancel buttons
        button_layout = self.gen_bottom_btns()

        # Dropdown menus for selecting signs
        self.sign1_dropdown = QComboBox()
        self.sign2_dropdown = QComboBox()
        dropdown_layout = self.initialize_dropdown(selected_signs)

        # -- finalize creating main layout
        layout.addLayout(dropdown_layout)
        layout.addLayout(sign_tree_and_counters_layout)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Connect expand/collapse events
        self.tree1.itemExpanded.connect(lambda item: self.on_item_expanded(item, self.tree2))
        self.tree1.itemCollapsed.connect(lambda item: self.on_item_collapsed(item, self.tree2))

        self.tree2.itemExpanded.connect(lambda item: self.on_item_expanded(item, self.tree1))
        self.tree2.itemCollapsed.connect(lambda item: self.on_item_collapsed(item, self.tree1))

        # Connect scroll events to sync two trees' scrollbars
        self.tree1.verticalScrollBar().valueChanged.connect(lambda value: self.sync_scrollbars(scrolled_value=value,
                                                                                               other_tree=self.tree2))
        self.tree2.verticalScrollBar().valueChanged.connect(lambda value: self.sync_scrollbars(scrolled_value=value,
                                                                                               other_tree=self.tree1))

        # flag to prevent infinite recursion of the `sync_scrollbars` method...
        self.syncing_scrollbars = False

        # finally, update trees, including colour counter updates.
        self.update_trees()

    def initialize_sign_counters(self):
        # generate a dictionary of ColourCounters for a sign
        palette = self.palette
        counter_kinds = ["all collapsed", "current", "all expanded"]
        return {key: ColourCounter(palette=palette) for key in counter_kinds}

    def initialize_dropdown(self, selected=None):
        idgloss_list = self.corpus.get_all_idglosses()

        self.sign1_dropdown.addItems(idgloss_list)
        self.sign2_dropdown.addItems(idgloss_list)

        self.sign1_dropdown.currentIndexChanged.connect(self._on_sign_selection_changed)
        self.sign2_dropdown.currentIndexChanged.connect(self._on_sign_selection_changed)

        layout = QHBoxLayout()
        layout.addWidget(QLabel("Select Sign 1:"))
        layout.addWidget(self.sign1_dropdown)
        layout.addWidget(QLabel("Select Sign 2:"))
        layout.addWidget(self.sign2_dropdown)

        if selected:
            # if two signs are selected on the 'Corpus' panel, update two dropdowns accordingly
            given_idglosses = [sign.signlevel_information.idgloss for sign in selected]
            self.sign1_dropdown.setCurrentText(given_idglosses[0])
            self.sign2_dropdown.setCurrentText(given_idglosses[1])
        return layout

    def initialize_signs_layout(self, counters_1, counters_2):
        def create_counters_layout(counters):
            # helper function to create vertical box layout for counters
            vbl = QVBoxLayout()
            for k, v in counters.items():
                vbl.addWidget(QLabel(k.capitalize()))
                vbl.addWidget(v)
            return vbl

        # container for all
        tree_counter_layout = QVBoxLayout()

        # two sign trees
        signtrees_hbl = QHBoxLayout()
        signtrees_hbl.addWidget(self.tree1)
        signtrees_hbl.addWidget(self.tree2)
        tree_counter_layout.addLayout(signtrees_hbl)

        # Expand All and Collapse All btns
        expand_collapse_layout_hbox = QHBoxLayout()

        expand_all_button = QPushButton("Expand All")
        expand_collapse_layout_hbox.addWidget(expand_all_button)
        expand_all_button.clicked.connect(lambda: self.toggle_all_trees(expand=True))

        collapse_all_button = QPushButton("Collapse All")
        expand_collapse_layout_hbox.addWidget(collapse_all_button)
        collapse_all_button.clicked.connect(lambda: self.toggle_all_trees(expand=False))

        tree_counter_layout.addLayout(expand_collapse_layout_hbox)

        # Hand configuration options
        toggle_layout = QHBoxLayout()
        toggle_layout.setContentsMargins(0, 0, 0, 0)
        options_label = QLabel("Options:")
        toggle_layout.addWidget(options_label)

        self.options_toggle_btn = QToolButton()
        self.options_toggle_btn.setArrowType(Qt.DownArrow)
        self.options_toggle_btn.setCheckable(True)
        self.options_toggle_btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.options_toggle_btn.setFixedSize(16, 16)
        toggle_layout.addWidget(self.options_toggle_btn)
        toggle_layout.addStretch()

        tree_counter_layout.addLayout(toggle_layout)

        # Hand-configuration radio-button container (hidden by default)
        self.hand_options_widget = QWidget()
        hand_opts_layout = QVBoxLayout(self.hand_options_widget)

        # four radio buttons for handshape name
        self.predefined_HC = QRadioButton("Compare predefined hand shape names.")
        self.predefined_HC.setChecked(True)
        self.predefined_HC.setProperty("compare_target", "predefined")
        self.predefined_HC.setProperty("details", False)
        hand_opts_layout.addWidget(self.predefined_HC)

        self.predefined_base_variant = QRadioButton("Compare predefined names with a base-variant hierarchy.")
        self.predefined_base_variant.setProperty("compare_target", "predefined")
        self.predefined_base_variant.setProperty("details", True)
        hand_opts_layout.addWidget(self.predefined_base_variant)

        self.transcription_exact = QRadioButton("Compare actual transcriptions (exact matches only).")
        self.transcription_exact.setProperty("compare_target", "transcriptions")
        self.transcription_exact.setProperty("details", True)
        hand_opts_layout.addWidget(self.transcription_exact)

        self.transcription_lenient = QRadioButton("Compare actual transcriptions (lenient).")
        self.transcription_lenient.setProperty("compare_target", "transcriptions")
        self.transcription_lenient.setProperty("details", False)
        hand_opts_layout.addWidget(self.transcription_lenient)

        # group them so only one can be checked
        self.hand_btn_group = QButtonGroup(self)
        for rb in (self.predefined_HC, self.predefined_base_variant, self.transcription_exact, self.transcription_lenient):
            self.hand_btn_group.addButton(rb)
        self.hand_btn_group.buttonClicked.connect(self._on_hand_option_changed)

        # hide by default
        self.hand_options_widget.setVisible(False)
        tree_counter_layout.addWidget(self.hand_options_widget)
        self.options_toggle_btn.toggled.connect(self._on_options_toggled)

        # separator
        separate_line = QFrame()
        separate_line.setFrameShape(QFrame.HLine)
        separate_line.setFrameShadow(QFrame.Sunken)
        tree_counter_layout.addWidget(separate_line)

        # colour counters
        counters_hbl = QHBoxLayout()
        counters_hbl.addLayout(create_counters_layout(counters_1))
        counters_hbl.addLayout(create_counters_layout(counters_2))
        tree_counter_layout.addLayout(counters_hbl)

        return tree_counter_layout

    def sync_scrollbars(self, scrolled_value, other_tree):
        if not self.syncing_scrollbars:
            target_scrollbar = other_tree.verticalScrollBar()  # the scrollbar to programmatically scroll
            self.syncing_scrollbars = True
            target_scrollbar.setValue(scrolled_value)
            self.syncing_scrollbars = False

    def _on_sign_selection_changed(self, idx):
        self.update_trees()

    def _on_options_toggled(self, checked):
        # show or hide the container
        self.hand_options_widget.setVisible(checked)
        # flip the arrow
        self.options_toggle_btn.setArrowType(Qt.UpArrow if checked else Qt.DownArrow)

    def _on_hand_option_changed(self, btn):
        # btn: QAbstractButton object
        options = {'handconfig': None}
        options['handconfig'] = {'compare_target': btn.property('compare_target'),
                                 'details': btn.property('details')}
        self.update_trees(options)

    def gen_bottom_btns(self):
        # generate Ok and Cancel buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        return button_layout

    # clean keys like '0:Mov1' to '0'
    def clean_data_keys(self, k_lst: list):
        confirmed_clean = dict()
        for k in k_lst:
            match = re.match(r'^(\d+):', k)
            key = int(match.group(1)) if match else k
            confirmed_clean[key] = None
        return list(confirmed_clean)

    # get '0:Mov1' from '0'
    def get_original_key(self, many_keys, int_key):
        try:
            key = str(int_key)
            for item in many_keys:
                if ':' in item and item.split(':')[0] == key:
                    return item
        except ValueError:
            pass
        return int_key

    # generate a pair of CompareTreeWidgetItem instances
    def _gen_twi_pair(self, label1: str, label2: str = None,         # text of the twi that shows up in gui
                      trunc_count1: int = 0, trunc_count2: int = 0,  # number of truncated children of radio button
                      force_label: bool = False):   # when True, always treated as label (transparent when expanded)
        if label2 is None:
            label2 = label1

        stamp_id = next_pair_id()
        item1 = CompareTreeWidgetItem(
            labels=[label1],
            palette=self.palette,
            truncated_count=trunc_count1,
            pair_id=stamp_id,
            override_is_label=force_label,
        )
        item2 = CompareTreeWidgetItem(
            labels=[label2],
            palette=self.palette,
            truncated_count=trunc_count2,
            pair_id=stamp_id,
            override_is_label=force_label,
        )
        del stamp_id

        return item1, item2

    def add_terminal_twi(self, children):
        is_terminal = False
        should_paint_yellow = [False, False]
        if any(isinstance(child, dict) for child in children):
            # not a terminal node
            return should_paint_yellow, is_terminal

        # yes a terminal node, and needs to decide 'which parent' should be yellow
        is_terminal = True
        should_paint_yellow = [child is None for child in children]
        return should_paint_yellow, is_terminal

    def _colour_twi_bg(self, twi_1, twi_2):
        # decide yellow
        if twi_1.flags() == Qt.NoItemFlags:
            twi_2, twi_1 = self._asymmetric_twi_colours(yellow_twi=twi_2, greyout_twi=twi_1)
        elif twi_2.flags() == Qt.NoItemFlags:
            twi_1, twi_2 = self._asymmetric_twi_colours(yellow_twi=twi_1, greyout_twi=twi_2)

        # decide red
        if twi_1.red_when_folded_hint:
            twi_1.initialize_bg_color('red')
        if twi_2.red_when_folded_hint:
            twi_2.initialize_bg_color('red')

        # default to blue
        twi_1.initialize_bg_color('blue')
        twi_2.initialize_bg_color('blue')

        return twi_1, twi_2

    def _add_twi_for_module_roots(self, parents, children):
        # for module roots (e.g., 0:Loc1) children should always be aligned *and consider as equal*
        # because they are always given aligned (cf. compare_signs.align_modules)
        #
        # parents: top-level module names like 'Movement,' 'Handconfig,' etc.
        # children: module roots

        # task0
        parent1, parent2 = parents
        child1, child2 = children
        depth = child1.depth

        del parents
        del children

        if depth >= 0:
            print(f'[DEBUG] incorrectly called _add_twi_for_module_roots()')
            return

        # task1
        if child1.vacuous:    # asymmetric comparison. only sign 2 has this module, so follow its key
            twi_1, twi_2 = self._gen_twi_pair(child2.key)
        elif child2.vacuous:  # asymmetric comparison. only sign 1 has this module, so follow its key
            twi_1, twi_2 = self._gen_twi_pair(child1.key)
        else:  # both keys exist
            twi_1, twi_2 = self._gen_twi_pair(child1.key, child2.key)

        # task3
        twi_1, twi_2 = self.add_tree_widget_items(twi_1, twi_2, child1.children, child2.children, depth + 1)

        # task2
        twi_1, twi_2 = self._colour_twi_bg(twi_1, twi_2)

        # task4
        if twi_1.underlying_bg in ['red', 'yellow'] or twi_2.underlying_bg in ['red', 'yellow']:
            parent1.red_when_folded_hint, parent2.red_when_folded_hint = True, True

        # task5
        parent1.addChild(twi_1)
        parent2.addChild(twi_2)

        return parent1, parent2

    def _add_twi_for_major_loc(self, parents, children):
        newly_added = []
        parent1, parent2 = parents
        child1, child2 = children

        del parents
        del children

        should_paint_red = [False, False]
        depth = child1.depth

        # task0: major location lines should always align even though they do not match
        if child1.vacuous:
            child1.update_with_alternative(target_btn_type='major loc')
            newly_added.append(child1.key)
        elif child2.vacuous:
            child2.update_with_alternative(target_btn_type='major loc')
            newly_added.append(child2.key)

        # task1
        twi_1, twi_2 = self._gen_twi_pair(child1.key, child2.key)

        # task2: major location should be either red or blue.
        if child1 != child2:
            twi_1.initialize_bg_color('red')
            twi_2.initialize_bg_color('red')
            # task3
            parent1.red_when_folded_hint, parent2.red_when_folded_hint = [True, True]
        else:
            twi_1.initialize_bg_color('blue')
            twi_2.initialize_bg_color('blue')

        # task5: major loc nodes can never be terminal so must recurse
        twi_1, twi_2 = self.add_tree_widget_items(twi_1, twi_2, child1.children, child2.children, depth + 1)
        # after adding children, we may learn that twi_1 or twi_2 should be red when folded. then, pass that to parents
        if twi_1.red_when_folded_hint:
            parent1.red_when_folded_hint = True
        if twi_2.red_when_folded_hint:
            parent2.red_when_folded_hint = True

        # task5
        parent1.addChild(twi_1)
        parent2.addChild(twi_2)

        return newly_added, parent1, parent2

    # for radio buttons, align different lines and colour the red if same parents
    def _gen_twi_for_radiobuttons(self, parents, children):
        # parents: CompareTreeWidgetItem instances
        # children: TreeWidgetItemKey instances
        newly_added = []
        parent1, parent2 = parents
        child1, child2 = children

        del parents
        del children

        depth = child1.depth

        # task0: check if same parents, the children should always align
        same_parents = parent1 == parent2
        if same_parents and child1.vacuous:
            child1.update_with_alternative(target_btn_type='radio button')
            newly_added.append(child1.key)
        elif same_parents and child2.vacuous:
            child2.update_with_alternative(target_btn_type='radio button')
            newly_added.append(child2.key)

        # as well, if lenient transcriptions comparison option for handconfig, lower and upper cases don't matter
        handshape_broad_match = True if not self.comparison_options['handconfig']['details'] else False

        # task1
        twi_1, twi_2 = self._gen_twi_pair(child1.key, child2.key)

        # task2
        if not child1.equals(child2, handshape_broad_match) and same_parents:
            twi_1.initialize_bg_color('red')
            twi_2.initialize_bg_color('red')
            # task3
            parent1.red_when_folded_hint, parent2.red_when_folded_hint = [True, True]
        elif child2.vacuous:
            twi_1, twi_2 = self._asymmetric_twi_colours(yellow_twi=twi_1,
                                                        greyout_twi=twi_2)
        elif child1.vacuous:
            twi_2, twi_1 = self._asymmetric_twi_colours(yellow_twi=twi_2,
                                                        greyout_twi=twi_1)
        elif child1.equals(child2, handshape_broad_match):
            twi_1.initialize_bg_color('blue')
            twi_2.initialize_bg_color('blue')

        # task3
        twi_1, twi_2 = self.add_tree_widget_items(twi_1, twi_2, child1.children, child2.children, depth + 1)

        # task5
        parent1.addChild(twi_1)
        parent2.addChild(twi_2)

        return newly_added, parent1, parent2

    # colour a pair of tree widget items: one yellow the other greyout
    def _asymmetric_twi_colours(self, yellow_twi, greyout_twi):
        brush = yellow_twi.palette
        greyout_twi.setForeground(0, brush['grey'])
        greyout_twi.setFlags(Qt.NoItemFlags)
        yellow_twi.initialize_bg_color('yellow')
        return yellow_twi, greyout_twi

    # this adds a line to the comparison trees and decides its colour
    def add_tree_widget_items(self, parent1, parent2, data1, data2, depth=-1):
        # parent1, parent2: CompareTreeWidgetItem, a line in the compare tree gui
        # data1, data2: dict, representing information to be added under parents. need to gen CompareTreeWidget.
        #               of str, if terminal.
        # depth: depth in the overall sign specification structure
        # returns bools should_paint_red, should_paint_yellow

        # it does (or dispatches?) five tasks:
        # (1) generate CompareTreeWidgetItem (twi)
        # (2) decide own colours (twi.initialize_bg_color)
        # (3) recurse with their children and (if not terminal)
        # (4) decide parent red hints (whether parent should also be red or not)
        # (5) parent.addChild(twi)
        # return parents (with children added)

        # task 0
        data1 = data1 or {}  # empty dict if data1 is given None
        data2 = data2 or {}

        data1_keys_original: list = list(data1.keys()) if isinstance(data1, dict) else []
        data2_keys_original: list = list(data2.keys()) if isinstance(data2, dict) else []

        data1_keys: list = self.clean_data_keys(data1_keys_original)
        data2_keys: list = self.clean_data_keys(data2_keys_original)

        all_keys = data1_keys + [k for k in data2_keys if k not in data1_keys]
        shared_keys = list(set(data1_keys).intersection(data2_keys))

        # iterate over all keys. for each key create twi and add it
        already_added_keys = []  # just a temporary storage to prevent duplicates
        for key in all_keys:
            if key in already_added_keys:
                continue

            if key in ['button_type', 'match']:
                continue

            data1_key = TreeWidgetItemKey(key, data1_keys_original, data1, depth=depth)
            data2_key = TreeWidgetItemKey(key, data2_keys_original, data2, depth=depth)

            if depth < 0:
                # module root nodes
                r = self._add_twi_for_module_roots(parents=[parent1, parent2],
                                                   children=[data1_key, data2_key])
                parent1, parent2 = r
                continue

            if data1_key.btn_type == 'major loc':
                r = self._add_twi_for_major_loc(parents=[parent1, parent2],
                                                children=[data1_key, data2_key])
                newly_added, parent1, parent2, = r
                already_added_keys.extend(newly_added)
                del newly_added
                continue

            elif data1_key.btn_type == 'radio button':
                r = self._gen_twi_for_radiobuttons(parents=[parent1, parent2],
                                                   children=[data1_key, data2_key])
                newly_added, parent1, parent2 = r
                already_added_keys.extend(newly_added)
                del newly_added
                continue

            # default case
            # task1
            twi_1, twi_2 = self._gen_twi_pair(key, force_label=data1_key.btn_type == 'autogen label')

            # task3
            twi_1, twi_2 = self.add_tree_widget_items(twi_1, twi_2, data1_key.children, data2_key.children, depth + 1)

            # task2
            if data2_key.vacuous:
                # if sign1 has it but sign2 does not, sign1 becomes yellow, 2 greys out
                twi_1, twi_2 = self._asymmetric_twi_colours(yellow_twi=twi_1,
                                                            greyout_twi=twi_2)
            elif data1_key.vacuous:
                # vice versa
                twi_2, twi_1 = self._asymmetric_twi_colours(yellow_twi=twi_2,
                                                            greyout_twi=twi_1)
            else:
                twi_1, twi_2 = self._colour_twi_bg(twi_1, twi_2)

            # task4
            if twi_1.underlying_bg in ['red', 'yellow'] or twi_2.underlying_bg in ['red', 'yellow']:
                parent1.red_when_folded_hint, parent2.red_when_folded_hint = True, True

            # task5
            parent1.addChild(twi_1)
            parent2.addChild(twi_2)

        return parent1, parent2

    def populate_trees(self, tree1, tree2, data1, data2):
        # 'self.add_tree_widget_items' actually does the heavy lifting
        # tree1, tree2: QTreeWidget
        # data1, data2: dict. sign comparison results

        # Add each top-level key (e.g., movement, location, relation, ...) as a root item in the tree
        for key in set(data1.keys()).union(data2.keys()):
            top_item1, top_item2 = self._gen_twi_pair(key)
            # and recursively add children under the top-level item
            top_item1, top_item2 = self.add_tree_widget_items(parent1=top_item1,
                                                              parent2=top_item2,
                                                              data1=data1.get(key, {}),  # sign1 child dictionary
                                                              data2=data2.get(key, {}))
            top_item1, top_item2 = self._colour_twi_bg(top_item1, top_item2)
            tree1.addTopLevelItem(top_item1)
            tree2.addTopLevelItem(top_item2)

            # expand the root item by default
            # top_item1.setExpanded(True)
            # top_item2.setExpanded(True)

    def update_trees(self, options: dict = None):
        # Update the dialog visual as the user selects signs from the dropdown
        # options: dict of options such as handshape compare by predefined name or not
        self.comparison_options = options if options is not None else self.comparison_options  # update if needed

        label_sign1 = self.sign1_dropdown.currentText()
        label_sign2 = self.sign2_dropdown.currentText()

        self.tree1.setHeaderLabel(f"Sign 1: {label_sign1}")
        self.tree2.setHeaderLabel(f"Sign 2: {label_sign2}")

        sign1, sign2 = self.find_target_signs(label_sign1, label_sign2)  # Identify signs to compare
        compare = CompareModel(sign1, sign2)
        compare_res = compare.compare_sign_pair(self.comparison_options)

        # Now update trees! Start with clearing.
        self.tree1.clear()
        self.tree2.clear()

        # Populate trees hierarchically
        self.populate_trees(self.tree1, self.tree2, compare_res['sign1'], compare_res['sign2'])

        # Update counters now, as the trees are all populated.
        self.update_expand_collapse_counters()  # all collapsed / all expanded
        self.update_current_counters()          # current

    def update_current_counters(self):
        counts_current_sign1 = self.count_coloured_lines(tree=self.tree1)
        counts_current_sign2 = self.count_coloured_lines(tree=self.tree2)

        self.current_colour_counter_1.update_counter(counts_current_sign1)
        self.current_colour_counter_2.update_counter(counts_current_sign2)

    def find_target_signs(self, label1: str, label2: str):
        # identify two sign instances to compare. label1 and label2 are strings user selected in dropdown box
        sign1, sign2 = False, False  # sign1 and sign2 declared as bool but eventually Sign instances
        for sign in self.signs:
            if all([sign1, sign2]):  # both sign1 and sign2 identified, stop iterating over corpus
                break

            if not sign1 and sign.signlevel_information.idgloss == label1:
                # if sign1 is not identified and the current sign in the corpus has the same lemma as sign1
                sign1 = sign
            if not sign2 and sign.signlevel_information.idgloss == label2:
                sign2 = sign
        return sign1, sign2

    def on_item_expanded(self, item, target_tree):
        # when item (=twi) gets expanded do the following:
        # - find corresponding line in the other tree and expand
        # - change colour
        # - update current colour counter

        # Find and expand the corresponding item in the target tree
        corresponding_item = self.find_corresponding_line(item, target_tree)
        if corresponding_item:
            if not corresponding_item.isExpanded():
                # to prevent infinite recursions, expand corresponding tree only when it is collapsed
                target_tree.expandItem(corresponding_item)

        # change colour
        if item.is_label:
            # if the item is a label, no colour when expanded
            item.set_bg_color('transparent')
        else:
            # if selection, check whether it matches with its correspondence
            item.set_bg_color(item.underlying_bg)
            if item == corresponding_item:
                item.set_bg_color('blue')

        # update current colour counter
        self.update_current_counters()

    def on_item_collapsed(self, item, target_tree):
        # when a qtreeitem gets expanded do the following:
        # - find corresponding line in the other tree and expand
        # - change colour
        # - update current colour counter

        # Find and collapse the corresponding item in the target tree
        corresponding_item = self.find_corresponding_line(item, target_tree)
        if corresponding_item and corresponding_item.isExpanded():
            # to prevent infinite recursions, collapse corresponding tree only when it is expanded
            target_tree.collapseItem(corresponding_item)

        # change colour
        item.set_bg_color(item.underlying_bg)

        # update current colour counter
        self.update_current_counters()

    # expand or collapse all lines in tree1 (effectively for tree2 as well due to the sync function)
    def toggle_all_trees(self, expand=True):
        # called by either 'expand all' or 'collapse all' button (differ by the 'expand' parameter)
        def recursive_toggle(root, should_expand):
            # recursively expand or collapse
            for i in range(root.childCount()):
                item = root.child(i)
                if should_expand and not item.isExpanded():    # only expand expandable lines
                    self.tree1.expandItem(item)  # does not connect to on_item_expanded()
                    self.on_item_expanded(item, self.tree2)
                elif not should_expand and item.isExpanded():  # only collapse collapsible lines
                    self.tree1.collapseItem(item)  # does not connect on_item_collapsed()
                    self.on_item_collapsed(item, self.tree2)
                recursive_toggle(item, should_expand)

        recursive_toggle(self.tree1.invisibleRootItem(), expand)

    def get_full_path(self, item):
        # helper function to get a full ancestry of a tree item
        path = []
        while item:
            path.append(item.text(0))
            item = item.parent()
        return path[::-1]  # Reverse to get root-to-item order

    def find_corresponding_line(self, twi, tree):
        # find line correspondences between trees,
        # twi: CompareTreeWidgetItem representing the source compare tree line
        # tree: the target tree on which twi is looking for its corresponding tree line
        # e.g., expanding 'movement' in tree1 should find 'movement' line in tree2
        def recursive_find(item, pair_id):
            if isinstance(item, CompareTreeWidgetItem) and getattr(item, "pair_id", None) == pair_id:
                return item
            for i in range(item.childCount()):
                found_in_deep = recursive_find(item.child(i), pair_id)
                if found_in_deep:
                    return found_in_deep

        pair_id = twi.pair_id
        current = tree.invisibleRootItem()

        # Iterate through the path (line) to find the corresponding item, i.e., the one with the same pair_id value
        found = None
        for i in range(current.childCount()):
            child = current.child(i)
            found = recursive_find(child, pair_id)
            if found:
                break
        return found  # Return None if the item in the path doesn't exist

    def update_expand_collapse_counters(self):
        # count colours for both 'all expanded' and 'all collapsed'
        counter_types = {'expanded': True, 'collapsed': False}

        for counter_type, expand_bool in counter_types.items():
            self.toggle_all_trees(expand=expand_bool)  # programmatically expand and then collapse all trees

            # and then count colours at the given moment and update the counter
            getattr(self, f'{counter_type}_colour_counter_1').update_counter(
                self.count_coloured_lines(tree=self.tree1))
            getattr(self, f'{counter_type}_colour_counter_2').update_counter(
                self.count_coloured_lines(tree=self.tree2))

    # traverse the trees and count colours (called by functions for current, all collapsed and all expanded)
    def count_coloured_lines(self, tree):
        counts = {'red': 0, 'yellow': 0, 'blue': 0}  # initialize counters

        def walk_tree(item, tree, fully_visible=True):
            # this conditional decides item_visible:bool (whether the current item is visible)
            if item.parent() is None:
                # no parent means the item is the root.
                item_visible = fully_visible
            else:
                parent_index = tree.indexFromItem(item.parent())
                parent_expanded = tree.isExpanded(parent_index)  # check if parent is expanded. (i.e., am i visible)
                item_visible = fully_visible and parent_expanded

            if item_visible:
                # regular colour counting
                bg_color = item.current_bg
                counts[bg_color] = counts.get(bg_color, 0) + 1

                # count truncated lines toward 'yellow'
                counts['yellow'] += item.truncated_count

            # recursively apply walk_tree to the children
            for i in range(item.childCount()):
                walk_tree(item.child(i), tree, item_visible)

        # for one tree (given as the 'tree' parameter)
        root = tree.invisibleRootItem()
        for i in range(root.childCount()):
            walk_tree(root.child(i), tree, fully_visible=True)

        return counts
