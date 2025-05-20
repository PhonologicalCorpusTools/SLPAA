from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QSplitter, QComboBox, \
    QLabel, QHBoxLayout, QPushButton, QWidget, QFrame
from PyQt5.QtGui import QBrush, QColor, QPalette
from PyQt5.QtCore import Qt
from random import randint  # for stamping tree widget item
import re

from compare_signs.compare_models import CompareModel
from compare_signs.compare_helpers import qcolor_to_rgba_str, parse_button_type, rb_red_buttons


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
    def __init__(self, labels, palette, truncated_count=0, pair_id=0):
        super().__init__(labels)

        self._text = self.text(0)

        # number of truncated lines -- for printing out and updating the colour counters.
        self.truncated_count = truncated_count

        # underlying and current background colours are unspecified by default, but may be blue red or yellow!
        self.underlying_bg = None
        self.current_bg = None
        self.force_underlying = False   # if True, expanding/collapsing does not change the background colour

        # imagine each tree item carries a palette and use it to change background colour
        self.palette = palette

        self.is_root: bool = False
        if self._text in ['movement', 'relation', 'orientation', 'location']:
            self.is_root = True

        self.is_label: bool = False
        if self._text.startswith(('H1', 'H2')) or self.is_root:
            self.is_label = True

        # pair_id to help finding corresponding line in the other tree
        self.pair_id = pair_id

    def __repr__(self):
        invisibility = self.flags() == Qt.NoItemFlags
        invisibility = 'in' if invisibility else ''
        return f'<CompareTreeWidgetItem {self._text!r}, pair_id: {self.pair_id} ({invisibility}visible)>'

    def __eq__(self, other):
        return self._text == other._text and self.flags() == other.flags()

    def initilize_bg_color(self, colour: str = 'transparent'):
        # called when populating a tree. when a line gets created, same bg colours for underlying and current
        if self.background(0).color().name() != self.palette['transparent'].color().name():
            # if the line's colour has already been initialized, do nothing
            return
        self.underlying_bg = colour
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

        # colour scheme to be used throughout the dialog
        self.palette = {'red': QBrush(QColor(255, 0, 0, 128)),
                        'blue': QBrush(QColor(0, 100, 255, 64)),
                        'yellow': QBrush(QColor(255, 255, 0, 128)),
                        'transparent': QBrush(QColor(0, 0, 0, 0))}

        # the main layout
        layout = QVBoxLayout()

        # Tree widgets for hierarchical variables
        self.tree1 = QTreeWidget()
        self.tree2 = QTreeWidget()
        self.tree1.setHeaderLabel("Sign 1")
        self.tree2.setHeaderLabel("Sign 2")

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

        self.sign1_dropdown.currentIndexChanged.connect(self.update_trees)
        self.sign2_dropdown.currentIndexChanged.connect(self.update_trees)

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
    def clean_data_keys(self, k_set_1, k_set_2):
        data1_keys = {match.group(1) if (match := re.match(r'^(\d+):', item)) else item for item in k_set_1}
        data2_keys = {match.group(1) if (match := re.match(r'^(\d+):', item)) else item for item in k_set_2}
        return data1_keys, data2_keys

    # get '0:Mov1' from '0'
    def get_original_key(self, many_keys, int_key):
        try:
            int(int_key)
            for item in many_keys:
                if ':' in item and item.split(':')[0] == int_key:
                    return item
        except ValueError:
            pass
        return int_key

    def populate_trees(self, tree1, tree2, data1, data2):
        # this really really really needs refactoring.
        # 'add_items' actually does the heavy lifting
        def add_items(parent1, parent2, data1, data2, depth=-1):
            data1 = data1 or {}   # empty dict if data1 is given None
            data2 = data2 or {}

            should_paint_red = [False, False]     # paint tree 1 node / tree 2 node red
            should_paint_yellow = [False, False]  # yellow to tree 1 node / tree 2 node
            red_brush = self.palette['red']   # red when mismatch
            yellow_brush = self.palette['yellow']  # yellow when no counterpart

            # query button_type (major loc, rb, cb)
            data1_btn_types = parse_button_type(data1)
            data2_btn_types = parse_button_type(data2)

            # Get the union of all keys in both data1 and data2
            data1_keys_original = set(data1.keys()) if isinstance(data1, dict) else set()
            data2_keys_original = set(data2.keys()) if isinstance(data2, dict) else set()

            data1_keys, data2_keys = self.clean_data_keys(data1_keys_original, data2_keys_original)

            # case: major location comparison → align current keys and force background colour to be always red
            try:
                is_major_loc = data1_btn_types[depth] == 'major loc' and data2_btn_types[depth] == 'major loc'
            except IndexError:
                is_major_loc = False
            if is_major_loc:
                data1_label = self.get_original_key(data1_keys_original, list(data1_keys_original)[0])
                data2_label = self.get_original_key(data2_keys_original, list(data2_keys_original)[0])

                value1 = data1.get(data1_label, None)  # data1_keys_original is a set guaranteed to contain only one str element
                value2 = data2.get(data2_label, None)

                stamp_id = randint(1, 1000)
                item1 = CompareTreeWidgetItem(labels=[data1_label],
                                              palette=self.palette,
                                              pair_id=stamp_id)
                item2 = CompareTreeWidgetItem(labels=[data2_label],
                                              palette=self.palette,
                                              pair_id=stamp_id)
                del stamp_id

                # decide color depending on the labels if they are different, should colored red.
                if data1_label != data2_label:
                    item1.initilize_bg_color('red')
                    item2.initilize_bg_color('red')
                    item1.force_underlying = True
                    item2.force_underlying = True
                    should_paint_red[0] = True
                    should_paint_red[1] = True

                # delete labels because they are not needed anymore
                del data1_label
                del data2_label

                parent1.addChild(item1)
                parent2.addChild(item2)

                child_r = [False, False]  # flag marking whether a child node is coloured red
                child_y = [False, False]  # flag marking whether a child node is coloured yellow

                if isinstance(value1, dict) or isinstance(value2, dict):
                    child_r, child_y = add_items(item1, item2, value1, value2, depth+1)
                else:
                    # Set color for false values
                    if value1 is False and not should_paint_yellow[0]:
                        item1.initilize_bg_color('red')  # red
                        should_paint_red[0] = True
                    elif item1.flags() == Qt.NoItemFlags:
                        item1.initilize_bg_color()  # default case = transparent background
                    elif item2.flags() != Qt.NoItemFlags:
                        item1.initilize_bg_color('blue')
                    else:
                        item1.initilize_bg_color('yellow')

                    if value2 is False and not should_paint_yellow[1]:
                        item2.initilize_bg_color('red')  # red
                        should_paint_red[1] = True
                    elif item2.flags() == Qt.NoItemFlags:
                        item2.initilize_bg_color()
                    elif item1.flags() != Qt.NoItemFlags:
                        item2.initilize_bg_color('blue')
                    else:
                        item2.initilize_bg_color('yellow')
                # color the node depending on children
                # if a child is either yellow or red, the parent should be red
                if child_r[0] or child_y[0]:
                    should_paint_red[0] = True
                if child_r[1] or child_y[1]:
                    should_paint_red[1] = True
                should_paint_red = [should_paint_red[0], should_paint_red[1]]
            else:
                all_keys = sorted(data1_keys.union(data2_keys), reverse=True)

                for key in reversed(all_keys):
                    # case: same parents, different children.
                    if parent1 == parent2 and key not in (data1_keys & data2_keys) and not parent1.is_root and not parent2.is_root:
                        try:
                            is_data1_rb = data1_btn_types[depth] == 'radio button'
                            is_data2_rb = data2_btn_types[depth] == 'radio button'
                        except IndexError:  # same parents, one does not have a child
                            is_data1_rb = False
                            is_data2_rb = False

                        # Same parents, different radio button children
                        if is_data1_rb and is_data2_rb:
                            item_labels = []
                            trunc_counts = []

                            for k, btn_t in [(data1_keys, data1_btn_types), (data2_keys, data2_btn_types)]:
                                label = str(list(k)[0])
                                trunc_n = len(btn_t[depth + 1:])
                                if trunc_n > 0:
                                    label += f" (+ {trunc_n} truncated for lack of correspondence)"
                                item_labels.append(label)
                                trunc_counts.append(trunc_n)

                            stamp_id = randint(1, 500)
                            item1 = CompareTreeWidgetItem(
                                labels=[item_labels[0]],
                                palette=self.palette,
                                truncated_count=trunc_counts[0],
                                pair_id=stamp_id
                            )
                            item2 = CompareTreeWidgetItem(
                                labels=[item_labels[1]],
                                palette=self.palette,
                                truncated_count=trunc_counts[1],
                                pair_id=stamp_id
                            )
                            del stamp_id

                            should_paint_red = rb_red_buttons([item1, item2], [parent1, parent2],
                                                              should_paint_red, yellow_brush)
                            return should_paint_red, should_paint_yellow
                    value1, value2 = None, None
                    try:
                        value1 = data1.get(self.get_original_key(data1_keys_original, key), None)
                        value2 = data2.get(self.get_original_key(data2_keys_original, key), None)
                    except AttributeError:
                        # when data1 or data2 is bool
                        pass

                    # case: a tree hit the terminal. button_type node should not be visible
                    if key in {'match', 'button_type'}:
                        if len(data1_btn_types) != len(data2_btn_types):

                            # needs to decide 'which parent' should be yellow
                            index = 0 if value1 is not None else 1
                            should_paint_yellow[index] = True
                        continue

                    # Create tree items for both trees
                    stamp_id = randint(1, 500)
                    item1 = CompareTreeWidgetItem(labels=[self.get_original_key(data1_keys_original, key)],
                                                  palette=self.palette,
                                                  pair_id=stamp_id)
                    item2 = CompareTreeWidgetItem(labels=[self.get_original_key(data2_keys_original, key)],
                                                  palette=self.palette,
                                                  pair_id=stamp_id)
                    del stamp_id

                    # Set the color of missing nodes
                    if value1 is None and value2 is not None:
                        # only tree 2 has this node
                        background_colour = tree1.palette().color(QPalette.Base)
                        item1.setForeground(0, QBrush(background_colour))  # node in tree 1 greyed out
                        item1.setFlags(Qt.NoItemFlags)
                        item2.initilize_bg_color('yellow')
                        should_paint_yellow[1] = True
                    elif value2 is None and value1 is not None:
                        # only tree 1 has it
                        background_colour = tree2.palette().color(QPalette.Base)
                        item2.setForeground(0, QBrush(background_colour))  # node in tree 2 greyed out
                        item2.setFlags(Qt.NoItemFlags)
                        item1.initilize_bg_color('yellow')
                        should_paint_yellow[0] = True
                    parent1.addChild(item1)
                    parent2.addChild(item2)

                    # initialize child color flags
                    child_r = [False, False]  # flag marking whether a child node is coloured red
                    child_y = [False, False]  # flag marking whether a child node is coloured yellow

                    # If either of the two values are dicts, recurse into them
                    if isinstance(value1, dict) or isinstance(value2, dict):
                        child_r, child_y = add_items(item1, item2, value1, value2, depth+1)
                    else:
                        # Set color for false values
                        if value1 is False and not should_paint_yellow[0]:
                            item1.initilize_bg_color('red')  # red
                            should_paint_red[0] = True
                        elif item1.flags() == Qt.NoItemFlags:
                            item1.initilize_bg_color()  # default case = transparent background
                        elif item2.flags() != Qt.NoItemFlags:
                            item1.initilize_bg_color('blue')
                        else:
                            item1.initilize_bg_color('yellow')

                        if value2 is False and not should_paint_yellow[1]:
                            item2.initilize_bg_color('red')  # red
                            should_paint_red[1] = True
                        elif item2.flags() == Qt.NoItemFlags:
                            item2.initilize_bg_color()
                        elif item1.flags() != Qt.NoItemFlags:
                            item2.initilize_bg_color('blue')
                        else:
                            item2.initilize_bg_color('yellow')

                    # color the node depending on children
                    # if a child is either yellow or red, the parent should be red
                    if child_r[0] or child_y[0]:
                        should_paint_red[0] = True
                    if child_r[1] or child_y[1]:
                        should_paint_red[1] = True
                    should_paint_red = [should_paint_red[0], should_paint_red[1]]

            # Check parent1's children for empty (greyed out) lines
            for i in range(parent1.childCount()):
                c = parent1.child(i)
                if c.flags() == Qt.NoItemFlags:  # means c is "missing" on this side
                    should_paint_red[0] = True
                    break  # no need to keep checking

            # ... and parent2
            for j in range(parent2.childCount()):
                c = parent2.child(j)
                if c.flags() == Qt.NoItemFlags:
                    should_paint_red[1] = True
                    break

            # color of the parent node: red wins over yellow
            if should_paint_red[0]:
                # red should not override already painted yellow
                if parent1.background(0).color() != yellow_brush and not parent1.flags() == Qt.NoItemFlags:
                    parent1.initilize_bg_color('red')
            elif should_paint_yellow[0] and parent1 == parent2:
                parent1.initilize_bg_color('red')
            elif should_paint_yellow[0]:
                parent1.initilize_bg_color('yellow')
            elif not parent1.flags() == Qt.NoItemFlags:
                parent1.initilize_bg_color('blue')

            if should_paint_red[1]:
                if parent2.background(0).color() != yellow_brush and not parent2.flags() == Qt.NoItemFlags:
                    parent2.initilize_bg_color('red')
            elif should_paint_yellow[1] and parent1 == parent2:
                parent2.initilize_bg_color('red')
            elif should_paint_yellow[1]:
                parent2.initilize_bg_color('yellow')
            elif not parent2.flags() == Qt.NoItemFlags:
                parent2.initilize_bg_color('blue')

            return should_paint_red, should_paint_yellow

        # Add each top-level key (e.g., movement, location, relation, ...) as a root item in the tree
        for key in set(data1.keys()).union(data2.keys()):
            stamp_id = randint(1, 500)
            top_item1 = CompareTreeWidgetItem(labels=[key], palette=self.palette, pair_id=stamp_id)
            top_item2 = CompareTreeWidgetItem(labels=[key], palette=self.palette, pair_id=stamp_id)
            del stamp_id

            tree1.addTopLevelItem(top_item1)
            tree2.addTopLevelItem(top_item2)

            # Recursively add children under the top-level item
            add_items(parent1=top_item1,
                      parent2=top_item2,
                      data1=data1.get(key, {}),  # sign1 child dictionary
                      data2=data2.get(key, {})   # sign2 child dictionary
                      )

            # expand the root item by default
            #top_item1.setExpanded(True)
            #top_item2.setExpanded(True)

    def update_trees(self):
        # Update the dialog visual as the user selects signs from the dropdown
        label_sign1 = self.sign1_dropdown.currentText()
        label_sign2 = self.sign2_dropdown.currentText()

        self.tree1.setHeaderLabel(f"Sign 1: {label_sign1}")
        self.tree2.setHeaderLabel(f"Sign 2: {label_sign2}")

        sign1, sign2 = self.find_target_signs(label_sign1, label_sign2)  # Identify signs to compare
        compare = CompareModel(sign1, sign2)
        compare_res = compare.compare()

        # Now update trees! Start with clearing.
        self.tree1.clear()
        self.tree2.clear()

        # Populate trees hierarchically
        self.populate_trees(self.tree1, self.tree2, compare_res['sign1'], compare_res['sign2'])

        # Update counters, now as the trees are all populated.
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
        # when a qtreeitem gets expanded do the following:
        # - find corresponding line in the other tree and expand
        # - change colour
        # - update current colour counter

        item_invisible = True if item.flags() == Qt.NoItemFlags else False  # check if item is invisible

        # Find and expand the corresponding item in the target tree
        corresponding_item = self.find_corresponding_line(item, target_tree)
        if corresponding_item:
            # check the corresponding line is invisible (i.e., if it does not really exist).
            corresponding_invisible = True if corresponding_item.flags() == Qt.NoItemFlags else False

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

    def toggle_all_trees(self, expand=True):
        # expand or collapse all lines in tree1, effectively doing so for tree2 due to syncing
        # called by either 'expand all' or 'collapse all' button ('expand' parameter)
        def recursive_toggle(root, should_expand):
            # recursively expand or collapse
            for i in range(root.childCount()):
                item = root.child(i)
                if should_expand and not item.isExpanded():    # only expand expandable lines
                    self.tree1.expandItem(item)
                elif not should_expand and item.isExpanded():  # only collapse collapsible lines
                    self.tree1.collapseItem(item)
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
            found = recursive_find(child,pair_id)
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
