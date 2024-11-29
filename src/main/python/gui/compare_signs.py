from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QSplitter, QComboBox, \
    QLabel, QHBoxLayout, QPushButton, QWidget
from PyQt5.QtGui import QBrush, QColor, QPalette
from PyQt5.QtCore import Qt

from compare_signs.compare_models import CompareModel
from compare_signs.compare_helpers import qcolor_to_rgba_str


class ColourCounter(QWidget):
    # ColourCounter shows the number of colours in the tree
    def __init__(self, palette):
        super().__init__()

        # Main layout
        self.layout = QHBoxLayout()

        # red, yellow blue rgba to be used for creating label background
        rgba_dict = {key: qcolor_to_rgba_str(brush.color()) for key, brush in palette.items()}

        # what we mean by each colour
        colour_mapping = [
            ('red', 'Mismatch'),
            ('yellow', 'No\nCorrespondence'),
            ('blue', 'Match')
        ]

        # create a set of colour counters ('all expanded', 'current' and 'all collapsed')
        self.counters = {}

        for colour_key, meaning in colour_mapping:
            counter_layout, count_label = self.gen_colour_counter_label(text=meaning,
                                                                        count='999',  # just a random number
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
        label.setStyleSheet(f"background-color: {color}; color: black;")
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
                print(f'label: {label}, count: {count}')
                self.update_counter(label=label, new_count=count)
            return

        label_txt = self.counters.get(label)
        if label_txt:
            label_txt.setText(f"{new_count}")


class CompareTreeWidgetItem(QTreeWidgetItem):
    # each line in the tree
    def __init__(self, labels, palette):
        super().__init__(labels)

        self._text = self.text(0)

        # underlying and current background colours are unspecified by default, but may be blue red or yellow!
        self.underlying_bg = None
        self.current_bg = None

        # imagine each tree item carries a palette and use it to change background colour
        self.palette = palette

        self.is_root: bool = False
        if self._text in ['movement', 'relation']:
            self.is_root = True

        self.is_label: bool = False
        if self._text.startswith(('H1', 'H2')) or self.is_root:
            self.is_label = True

    def __repr__(self):
        invisibility = self.flags() == Qt.NoItemFlags
        invisibility = 'in' if invisibility else ''
        return f'<CompareTreeWidgetItem {self._text!r} ({invisibility}visible)>'

    def __eq__(self, other):
        return self._text == other._text and self.flags() == other.flags()

    def initilize_bg_color(self, colour: str = 'transparent'):
        # called when populating a tree. when a line gets created, same bg colours for underlying and current
        self.underlying_bg = colour
        self.current_bg = colour
        colour_brush = self.palette.get(colour, self.palette['transparent'])
        self.setBackground(0, colour_brush)

    def set_bg_color(self, colour: str = 'transparent'):
        # wrapper for the parent's setBackround method
        colour_brush = self.palette[colour] if colour in self.palette else self.palette['transparent']
        self.setBackground(0, colour_brush)
        self.current_bg = colour


class CompareSignsDialog(QDialog):
    def __init__(self, **kwargs):
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

        # Dropdown menus for selecting signs
        self.sign1_dropdown = QComboBox()
        self.sign2_dropdown = QComboBox()
        dropdown_layout = self.initialize_dropdown()
        layout.addLayout(dropdown_layout)

        # Tree widgets for hierarchical variables
        self.tree1 = QTreeWidget()
        self.tree2 = QTreeWidget()
        self.tree1.setHeaderLabel("Sign 1")
        self.tree2.setHeaderLabel("Sign 2")

        # Gen colour counters for two signs
        sign1_counters = self.initialize_sign_counters()
        sign2_counters = self.initialize_sign_counters()

        self.expanded_colour_counter_1 = sign1_counters['all expanded']
        self.current_colour_counter_1 = sign1_counters['current']
        self.collapsed_colour_counter_1 = sign1_counters['all collapsed']

        self.expanded_colour_counter_2 = sign2_counters['all expanded']
        self.current_colour_counter_2 = sign2_counters['current']
        self.collapsed_colour_counter_2 = sign2_counters['all collapsed']

        # Vertical tree layout for signs 1 and 2 (tree, expand/collapse btns, and counters)
        sign_tree_and_counters_layout = self.initialize_signs_layout(sign1_counters, sign2_counters)
        layout.addLayout(sign_tree_and_counters_layout)

        # Add OK and Cancel buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        # -- done creating main layout

        self.update_trees()

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

    def initialize_sign_counters(self):
        # generate a dictionary of ColourCounters for a sign
        palette = self.palette
        counter_kinds = ['all collapsed', 'current', 'all expanded']
        return {key: ColourCounter(palette=palette) for key in counter_kinds}

    def initialize_dropdown(self):
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
        expand_all_button.clicked.connect(self.expand_all_trees)

        collapse_all_button = QPushButton("Collapse All")
        expand_collapse_layout_hbox.addWidget(collapse_all_button)
        collapse_all_button.clicked.connect(self.collapse_all_trees)

        tree_counter_layout.addLayout(expand_collapse_layout_hbox)

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

    def populate_trees(self, tree1, tree2, data1, data2):
        # this really really needs refactoring.
        def add_items(parent1, parent2, data1, data2):
            should_paint_red = [False, False]     # paint tree 1 node / tree 2 node red
            should_paint_yellow = [False, False]  # yellow to tree 1 node / tree 2 node
            red_brush = self.palette['red']   # red when mismatch
            yellow_brush = self.palette['yellow']  # yellow when no counterpart

            # Get the union of all keys in both data1 and data2
            data1_keys = set(data1.keys()) if isinstance(data1, dict) else set()
            data2_keys = set(data2.keys()) if isinstance(data2, dict) else set()
            all_keys = data1_keys.union(data2_keys)

            # special case: terminal node
            if len(data1_keys) == len(data2_keys) == 1:
                _, value1 = next(iter(data1.items()))
                _, value2 = next(iter(data2.items()))
                value1_match = value1.get('match', "NA")
                value2_match = value2.get('match', "NA")
                if "NA" not in [value1_match, value2_match]:
                    btn_types1_final = value1['button_type'].split('>')[-1]
                    btn_types2_final = value2['button_type'].split('>')[-1]
                    if btn_types1_final == 'radio button' and btn_types2_final == 'radio button' and parent1 == parent2:
                        item1 = CompareTreeWidgetItem(labels=[str(list(data1_keys)[0])], palette=self.palette)
                        item2 = CompareTreeWidgetItem(labels=[str(list(data2_keys)[0])], palette=self.palette)
                        if not item1 == item2:
                            item1.initilize_bg_color('red')  # red
                            item2.initilize_bg_color('red')
                            should_paint_red[0] = True
                            should_paint_red[1] = True
                            if parent1.background(0).color() != yellow_brush:
                                parent1.initilize_bg_color('red')
                            if parent2.background(0).color() != yellow_brush:
                                parent2.initilize_bg_color('red')
                        else:
                            item1.initilize_bg_color('blue')
                            item2.initilize_bg_color('blue')
                        parent1.addChild(item1)
                        parent2.addChild(item2)

                        should_paint_red = [should_paint_red[0], should_paint_red[1]]
                        # color of the parent node: red wins over yellow
                        if should_paint_red[0]:
                            # red should not override already painted yellow
                            if parent1.background(0).color() != yellow_brush:
                                parent1.initilize_bg_color('red')
                        elif should_paint_yellow[0] and parent1 == parent2:
                            parent1.initilize_bg_color('red')
                        elif should_paint_yellow[0]:
                            parent1.initilize_bg_color('yellow')
                        elif not parent1.flags() == Qt.NoItemFlags:
                            parent1.initilize_bg_color('blue')

                        if should_paint_red[1]:
                            if parent2.background(0).color() != yellow_brush:
                                parent2.initilize_bg_color('red')
                        elif should_paint_yellow[1] and parent1 == parent2:
                            parent2.initilize_bg_color('red')
                        elif should_paint_yellow[1]:
                            parent2.initilize_bg_color('yellow')
                        elif not parent2.flags() == Qt.NoItemFlags:
                            parent2.initilize_bg_color('blue')

                        return should_paint_red, should_paint_yellow


            for key in reversed(list(all_keys)):
                # Create tree items for both trees
                item1 = CompareTreeWidgetItem(labels=[key], palette=self.palette)
                item2 = CompareTreeWidgetItem(labels=[key], palette=self.palette)

                value1, value2 = None, None
                try:
                    value1 = data1.get(key, None)
                    value2 = data2.get(key, None)
                except AttributeError:
                    # when data1 or data2 is bool
                    pass

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
                    print(f"terminal node {key} gets painted yellow because no corresponding node")
                    should_paint_yellow[0] = True
                parent1.addChild(item1)
                parent2.addChild(item2)

                # initialize child color flags
                child_r = [False, False]  # flag marking whether a child node is coloured red
                child_y = [False, False]  # flag marking whether a child node is coloured yellow

                # If both values are dicts, recurse into them
                if isinstance(value1, dict) or isinstance(value2, dict):
                    child_r, child_y = add_items(item1, item2, value1 if value1 else {}, value2 if value2 else {})
                else:
                    # Set color for false values
                    if value1 is False and not should_paint_yellow[0]:
                        print(f"terminal node {key} gets painted red because false")
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
                        print(f"{key} in item1 becomes blue")
                    else:
                        item2.initilize_bg_color('yellow')

                # color the node depending on children
                # if a child is either yellow or red, the parent should be red
                if child_r[0] or child_y[0]:
                    should_paint_red[0] = True
                if child_r[1] or child_y[1]:
                    should_paint_red[1] = True
                should_paint_red = [should_paint_red[0], should_paint_red[1]]
            # color of the parent node: red wins over yellow
            if should_paint_red[0]:
                # red should not override already painted yellow
                if parent1.background(0).color() != yellow_brush:
                    print(f"node={key}'s parent is not yellow\n{parent1.background(0).color()}")
                    parent1.initilize_bg_color('red')
                    print(f"node={key}\nshould_paint_yellow:{should_paint_yellow}\nshould_paint_red:{should_paint_red}.\n Painting the parent red\n")
                else:
                    print(f"node={key}'s parent is yellow\n{parent1.background(0).color()}")
            elif should_paint_yellow[0] and parent1 == parent2:
                parent1.initilize_bg_color('red')
                print(
                    f"node={key}\nshould_paint_yellow:{should_paint_yellow}\nshould_paint_red:{should_paint_red}\n Painting the parent red\n")
            elif should_paint_yellow[0]:
                parent1.initilize_bg_color('yellow')
                print(
                    f"node={key}\nshould_paint_yellow:{should_paint_yellow}\nshould_paint_red:{should_paint_red}\n Painting the parent yellow\n")
            elif not parent1.flags() == Qt.NoItemFlags:
                parent1.initilize_bg_color('blue')

            if should_paint_red[1]:
                if parent2.background(0).color() != yellow_brush:
                    print(f"node={key}'s parent is not yellow")
                    parent2.initilize_bg_color('red')
                    print(
                        f"node={key}\nshould_paint_yellow:{should_paint_yellow}\nshould_paint_red:{should_paint_red}.\n Painting the parent red\n")
                else:
                    print(f"node={key}'s parent is yellow")
            elif should_paint_yellow[1] and parent1 == parent2:
                parent2.initilize_bg_color('red')
                print(
                    f"node={key}\nshould_paint_yellow:{should_paint_yellow}\nshould_paint_red:{should_paint_red}\n Painting the parent yellow\n")
            elif should_paint_yellow[1]:
                parent2.initilize_bg_color('yellow')
            elif not parent2.flags() == Qt.NoItemFlags:
                parent2.initilize_bg_color('blue')

            return should_paint_red, should_paint_yellow

        # Add each top-level key as a root item in the tree
        for key in set(data1.keys()).union(data2.keys()):
            top_item1 = CompareTreeWidgetItem(labels=[key], palette=self.palette)
            top_item2 = CompareTreeWidgetItem(labels=[key], palette=self.palette)

            tree1.addTopLevelItem(top_item1)
            tree2.addTopLevelItem(top_item2)

            # Recursively add children under the top-level item
            add_items(top_item1, top_item2, data1.get(key, {}), data2.get(key, {}))

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

        print(compare_res)
        # Populate trees hierarchically
        self.populate_trees(self.tree1, self.tree2, compare_res['sign1'], compare_res['sign2'])

        # Update counters, now as the trees are all populated.
        colour_counts_sign1, root_colour_counts_sign1 = self.count_coloured_lines(self.tree1)
        colour_counts_sign2, root_colour_counts_sign2 = self.count_coloured_lines(self.tree2)

        self.expanded_colour_counter_1.update_counter(colour_counts_sign1)  # update 'all expanded' for 1
        self.expanded_colour_counter_2.update_counter(colour_counts_sign2)  # update 'all expanded' for 2
        self.collapsed_colour_counter_1.update_counter(root_colour_counts_sign1)
        self.collapsed_colour_counter_2.update_counter(root_colour_counts_sign2)

        self.update_current_counters()

    def update_current_counters(self):
        counts_current_sign1, _ = self.count_coloured_lines(tree=self.tree1, only_visible_now=True)
        counts_current_sign2, _ = self.count_coloured_lines(tree=self.tree2, only_visible_now=True)

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
        path = self.get_full_path(item)
        corresponding_item = self.find_corresponding_line(path, target_tree)
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
            if not corresponding_item:
                item.set_bg_color(item.underlying_bg)
            elif not (corresponding_invisible or item_invisible):
                item.set_bg_color('blue')

        # update current colour counter
        self.update_current_counters()

    def on_item_collapsed(self, item, target_tree):
        # when a qtreeitem gets expanded do the following:
        # - find corresponding line in the other tree and expand
        # - change colour
        # - update current colour counter

        # Find and collapse the corresponding item in the target tree
        path = self.get_full_path(item)
        corresponding_item = self.find_corresponding_line(path, target_tree)
        if corresponding_item and corresponding_item.isExpanded():
            # to prevent infinite recursions, collapse corresponding tree only when it is expanded
            target_tree.collapseItem(corresponding_item)

        # change colour
        item.set_bg_color(item.underlying_bg)

        # update current colour counter
        self.update_current_counters()

    def expand_all_trees(self):
        # Expand all lines in tree1, but effectively do so for both trees due to syncing
        root1 = self.tree1.invisibleRootItem()

        def recursive_expand(root):
            for i in range(root.childCount()):
                item = root.child(i)
                self.tree1.expandItem(item) if not item.isExpanded() else 0  # only expand expandable lines
                recursive_expand(item)

        recursive_expand(root1)

    def collapse_all_trees(self):
        # collapse all lines in tree1, but effectively do so for both trees due to syncing
        root1 = self.tree1.invisibleRootItem()

        def recursive_collapse(root):
            # recursively collapse
            for i in range(root.childCount()):
                item = root.child(i)
                self.tree1.collapseItem(item) if item.isExpanded() else 0  # only collapse collapsible lines
                recursive_collapse(item)

        recursive_collapse(root1)

    def get_full_path(self, item):
        # helper function to get a full ancestry of a tree item
        path = []
        while item:
            path.append(item.text(0))
            item = item.parent()
        return path[::-1]  # Reverse to get root-to-item order

    def find_corresponding_line(self, line, tree):
        # find line correspondences between trees,
        # e.g., expanding 'movement' in tree1 should find 'movement' line in tree2

        current = tree.invisibleRootItem()

        # Iterate through the path (line) to find the corresponding item
        for part in line:
            found = False
            for i in range(current.childCount()):
                child = current.child(i)
                if child.text(0) == part:
                    current = child
                    found = True
                    break
            if not found:
                return None  # Return None if the item in the path doesn't exist
        return current  # Return the found corresponding item

    def count_coloured_lines(self, tree, only_visible_now=False):
        # traverse the trees and count the number of colours (both all collapsed and all expanded)
        # only_visible_now: bool. count only colours that are currently visible

        # initialize counters
        counts = {'red': 0, 'yellow': 0, 'blue': 0}  # for 'all expanded'
        counts_roots = {'red': 0, 'yellow': 0, 'blue': 0}  # for 'all collapsed'

        def walk_tree(item, tree, fully_visible=True):
            # this conditional decides whether the current item is visible
            if item.parent() is None:
                # no parent means the item is the root.
                item_visible = fully_visible
            else:
                parent_index = tree.indexFromItem(item.parent())
                parent_expanded = tree.isExpanded(parent_index)  # check if parent is expanded. (i.e., am i visible)
                item_visible = fully_visible and parent_expanded

            bg_color = None

            if not only_visible_now:
                if hasattr(item, 'underlying_bg'):
                    print(f'item: {item}, bg:{item.underlying_bg}')
                    bg_color = item.underlying_bg

            elif item_visible:
                if hasattr(item, 'current_bg'):
                    bg_color = item.current_bg

            if bg_color in counts:
                # update 'all expanded' counter
                counts[bg_color] += 1

                if item.is_root:
                    # if the line is root (e.g., movement, relation ...) count its colour for 'all collapsed'
                    counts_roots[bg_color] += 1

            # recursively apply walk_tree to the children
            for i in range(item.childCount()):
                walk_tree(item.child(i), tree, item_visible)

        # for one tree (given as the 'tree' parameter)
        root = tree.invisibleRootItem()
        for i in range(root.childCount()):
            walk_tree(root.child(i), tree, fully_visible=True)

        return counts, counts_roots
