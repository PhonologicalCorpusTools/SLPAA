from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QSplitter, QComboBox, \
    QLabel, QHBoxLayout, QPushButton
import json


class CompareSignsDialog(QDialog):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        corpus_list = self.parent().corpus.serialize()['signs']  # don't need meta-data and only 'signs' part
        # following the logic in export corpus that dumps and reloads
        thestring = json.dumps(corpus_list, indent=3, default=lambda x: getattr(x, '__dict__', str(x)))
        corpus_list = json.loads(thestring)

        self.corpus = {}

        # example
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


        layout = QVBoxLayout()

        # Dropdown menus for selecting signs
        self.sign1_dropdown = QComboBox()
        self.sign2_dropdown = QComboBox()
        self.sign1_dropdown.addItems(self.corpus.keys())
        self.sign2_dropdown.addItems(self.corpus.keys())

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
        tree.clear()
        for key, value in data.items():
            parent = QTreeWidgetItem(tree, [key])
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    if isinstance(subvalue, dict):
                        subparent = QTreeWidgetItem(parent, [subkey])
                        for subsubkey, subsubvalue in subvalue.items():
                            QTreeWidgetItem(subparent, [subsubkey, subsubvalue])
                    else:
                        QTreeWidgetItem(parent, [subkey, subvalue])
            else:
                QTreeWidgetItem(parent, [value])

    def update_trees(self):
        sign1 = self.sign1_dropdown.currentText()
        sign2 = self.sign2_dropdown.currentText()

        self.tree1.setHeaderLabel(f"Sign 1: {sign1}")
        self.tree2.setHeaderLabel(f"Sign 2: {sign2}")

        self.populate_tree(self.tree1, self.corpus[sign1])
        self.populate_tree(self.tree2, self.corpus[sign2])
