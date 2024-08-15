from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QSplitter, QComboBox, \
    QLabel, QHBoxLayout, QPushButton
from PyQt5.QtGui import QBrush, QColor

from lexicon.module_classes import AddedInfo, TimingInterval, TimingPoint, ParameterModule, ModuleTypes, BodypartInfo, MovementModule, LocationModule, RelationModule
from search.helper_functions import relationdisplaytext, articulatordisplaytext, phonlocsdisplaytext, loctypedisplaytext, signtypedisplaytext, module_matches_xslottype


class CompareModel:
    def __init__(self, sign1, sign2):
        self.sign1 = sign1
        self.sign2 = sign2

    def compare(self) -> dict:
        module_attributes = [attr for attr in dir(self.sign1) if attr.endswith("modules")]
        module_attributes = [attr for attr in module_attributes if not callable(getattr(self.sign1, attr))]

        result = dict()

        for module in module_attributes:
            if 'movement' in module:
                mvmt_res = self.compare_mvmts()
                result['movement'] = mvmt_res
                print(f'movement_compare:{mvmt_res}')
            elif 'location' in module:
                loc_res = self.compare_locations()
                result['location'] = loc_res
                print(f'location_compare:{loc_res}')
            elif 'relation' in module:
                reln_res = self.compare_relation()
                result['relation'] = reln_res
                print(f'relation_compare:{reln_res}')

            elif 'orientation' in module:
                pass
        return result

    def compare_mvmts(self) -> dict:
        def compare_one_mvmt(pair: tuple) -> [bool, bool]:
            r = []  # return list of two bools each for articulator and path
            # pair = pair of movementModule
            s1art = articulatordisplaytext(pair[0].articulators, pair[0].inphase)
            s2art = articulatordisplaytext(pair[0].articulators, pair[0].inphase)
            r.append(True) if set(s1art) == set(s2art) else r.append(False)

            s1path = pair[0].movementtreemodel.get_checked_items()
            s2path = pair[1].movementtreemodel.get_checked_items()
            r.append(True) if set(s1path) == set(s2path) else r.append(False)

            return r  # [bool bool] each for articulators and paths

        sign1_modules = [m for m in self.sign1.getmoduledict(ModuleTypes.MOVEMENT).values()]
        sign2_modules = [m for m in self.sign2.getmoduledict(ModuleTypes.MOVEMENT).values()]

        if (len(sign1_modules) * len(sign2_modules) < 1 or  # if either does not have any movement module
                len(sign1_modules) != len(sign2_modules)):  # if the number of xslots does not match
            return {'X-slots not matching': False}
        to_compare = zip(sign1_modules, sign2_modules)

        comparison_result = {
            'articulators': True,
            'details': True
        }

        for pair in to_compare:
            compare_r = compare_one_mvmt(pair)
            for b, (key, _) in zip(compare_r, comparison_result.items()):
                if not b:
                    comparison_result[key] = b
        return comparison_result

    def compare_locations(self) -> [bool]:
        def compare_one_location(pair):
            r = []  # return list of two bools each for articulators, location types, phonological locations, paths

            # articulator
            s1art = articulatordisplaytext(pair[0].articulators, pair[0].inphase)
            s2art = articulatordisplaytext(pair[1].articulators, pair[1].inphase)
            r.append(True) if set(s1art) == set(s2art) else r.append(False)

            # location type
            s1loctype = loctypedisplaytext(pair[0].locationtreemodel.locationtype)
            s2loctype = loctypedisplaytext(pair[1].locationtreemodel.locationtype)
            r.append(True) if set(s1loctype) == set(s2loctype) else r.append(False)

            # phonological locations
            s1pl = phonlocsdisplaytext(pair[0].phonlocs)
            slpl = phonlocsdisplaytext(pair[1].phonlocs)
            r.append(True) if set(s1pl) == set(slpl) else r.append(False)

            # paths
            s1path = pair[0].locationtreemodel.get_checked_items()
            s2path = pair[1].locationtreemodel.get_checked_items()
            r.append(True) if set(s1path) == set(s2path) else r.append(False)

            return r

        sign1_modules = [m for m in self.sign1.getmoduledict(ModuleTypes.LOCATION).values()]
        sign2_modules = [m for m in self.sign2.getmoduledict(ModuleTypes.LOCATION).values()]

        if (len(sign1_modules) * len(sign2_modules) < 1 or  # if either does not have any movement module
                len(sign1_modules) != len(sign2_modules)):  # if the number of xslots does not match
            return {'X-slots not matching': False}
        to_compare = zip(sign1_modules, sign2_modules)

        comparison_result = {
            'articulators': True,
            'location types': True,
            'phonological locations': True,
            'details': True,
        }

        for pair in to_compare:
            compare_r = compare_one_location(pair)
            for b, (key, _) in zip(compare_r, comparison_result.items()):
                if not b:
                    comparison_result[key] = b
        return comparison_result

    def compare_relation(self) -> dict:
        def compare_one_reln(pair: tuple) -> [bool, bool]:
            r = []  # return list of two bools each for articulators, location types, phonological locations, paths

            # relation
            s1reln = relationdisplaytext(pair[0])
            s2reln = relationdisplaytext(pair[1])
            r.append(True) if set(s1reln) == set(s2reln) else r.append(False)

            return r

        sign1_modules = [m for m in self.sign1.getmoduledict(ModuleTypes.RELATION).values()]
        sign2_modules = [m for m in self.sign2.getmoduledict(ModuleTypes.RELATION).values()]

        if (len(sign1_modules) * len(sign2_modules) < 1 or  # if either does not have any movement module
                len(sign1_modules) != len(sign2_modules)):  # if the number of xslots does not match
            return {'X-slots not matching': False}
        to_compare = zip(sign1_modules, sign2_modules)
        comparison_result = {
            'relation': True,
        }

        for pair in to_compare:
            compare_r = compare_one_reln(pair)
            for b, (key, _) in zip(compare_r, comparison_result.items()):
                if not b:
                    comparison_result[key] = b
        return comparison_result


class CompareSignsDialog(QDialog):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.corpus = self.parent().corpus
        self.signs = self.corpus.signs  # don't need meta-data and only 'signs' part
        idgloss_list = self.corpus.get_all_idglosses()


        # example
        """
        self.corpus = {

            "JUSTIFY": {
                "Sign Type": {"Number of hands": "1"},
                "Movement": {"Palm up": "Horizontal left", "Fingers forward/rightward": "Horizontal right"},
                "Location": {"H1.Loc1": "Fixed position", "H2.Loc1": "Fixed position"},
                "Contact": {"H1.Cont1": "Onto the left palm", "H2.Cont2": "Onto the left palm"},
                "Handpart": {
                    "Surface": "b",
                    "Bones": "[]",
                    "Part of hand": "[whole hand]",
                    "Timing": "linked to at least one full x-slot",
                    "Type of linking": "linked to a single interval",
                    "Which interval": "x1-whole"
                },
                "Orientation": {
                    "H1.Ori1": {"Palm direction": "up", "Finger root direction": "distal + contra"},
                    "H2.Ori1": {"Palm direction": "up", "Finger root direction": "distal + contra"}
                },
                "Hand Configuration": {"H1.Config1": "Horizontal left", "H2.Config1": "Horizontal right"}
            },
            "STOP": {
                "Sign Type": {"Number of hands": "1"},
                "Movement": {"Palm facing left": "Right extended B", "Strike upward/backward": "Right extended B"},
                "Location": {"H1.Loc1": "Semi-vertical position", "H2.Loc1": "Semi-vertical position"},
                "Contact": {"H1.Cont1": "Onto the left palm", "H2.Cont2": "Onto the left palm"},
                "Handpart": {
                    "Surface": "u",
                    "Bones": "[]",
                    "Part of hand": "[whole hand]",
                    "Timing": "linked to at least one full x-slot",
                    "Type of linking": "linked to a single interval",
                    "Which interval": "x1-whole"
                },
                "Orientation": {
                    "H1.Ori1": {"Palm direction": "contra", "Finger root direction": "up + distal"},
                    "H2.Ori1": {"Palm direction": "up + proximal", "Finger root direction": "distal + contra"}
                },
                "Hand Configuration": {"H1.Config1": "Right extended B", "H2.Config1": "Right extended B"}
            }
        }
        """

        layout = QVBoxLayout()

        # Dropdown menus for selecting signs
        self.sign1_dropdown = QComboBox()
        self.sign2_dropdown = QComboBox()
        self.sign1_dropdown.addItems(idgloss_list)
        self.sign2_dropdown.addItems(idgloss_list)

        self.sign1_dropdown.currentIndexChanged.connect(self.update_trees)
        self.sign2_dropdown.currentIndexChanged.connect(self.update_trees)

        dropdown_layout = QHBoxLayout()
        dropdown_layout.addWidget(QLabel("Select Sign 1:"))
        dropdown_layout.addWidget(self.sign1_dropdown)
        dropdown_layout.addWidget(QLabel("Select Sign 2:"))
        dropdown_layout.addWidget(self.sign2_dropdown)

        layout.addLayout(dropdown_layout)

        # Tree widgets for hierarchical variables
        self.tree1 = QTreeWidget()
        self.tree1.setHeaderLabel("Sign 1")
        self.tree2 = QTreeWidget()
        self.tree2.setHeaderLabel("Sign 2")

        splitter = QSplitter()
        splitter.addWidget(self.tree1)
        splitter.addWidget(self.tree2)

        layout.addWidget(splitter)

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

        self.update_trees()

    def populate_tree(self, tree, data):
        def add_items(parent, data):
            should_color_red = False
            for key, value in data.items():
                if isinstance(value, dict):
                    # Recursive case: create a parent item and recurse into the dictionary
                    parent_item = QTreeWidgetItem([key])
                    child_needs_red = add_items(parent_item, value)
                    parent.addChild(parent_item)  # Add this parent item under the correct section
                    if child_needs_red:
                        red_brush = QBrush(QColor(255, 0, 0, 128))  # semi-transparent red
                        parent_item.setBackground(0, red_brush)
                        should_color_red = True
                else:
                    # Base case: create an item with the key and color based on value
                    item = QTreeWidgetItem([key])
                    if not value:
                        # Set background to red if the value is False
                        red_brush = QBrush(QColor(255, 0, 0, 128))  # semi-transparent red
                        item.setBackground(0, red_brush)
                        should_color_red = True
                    parent.addChild(item)
            return should_color_red

        # Add each top-level key as a root item in the tree
        for key, value in data.items():
            root_item = QTreeWidgetItem([key])
            if add_items(root_item, value):
                red_brush = QBrush(QColor(255, 0, 0, 128))  # semi-transparent red
                root_item.setBackground(0, red_brush)
            tree.addTopLevelItem(root_item)
            root_item.setExpanded(True)  # Optionally expand the root item by default

    def update_trees(self):
        # update the dialog visual as dropdown selections
        label_sign1 = self.sign1_dropdown.currentText()
        label_sign2 = self.sign2_dropdown.currentText()

        self.tree1.setHeaderLabel(f"Sign 1: {label_sign1}")
        self.tree2.setHeaderLabel(f"Sign 2: {label_sign2}")

        sign1, sign2 = self.find_target_signs(label_sign1, label_sign2) # identify signs to compare
        compare = CompareModel(sign1, sign2)
        compare_res = compare.compare()

        # now update trees! start with clearing.
        self.tree1.clear()
        self.tree2.clear()

        # populate trees hierarchically
        self.populate_tree(self.tree1, compare_res)
        self.populate_tree(self.tree2, compare_res)

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

