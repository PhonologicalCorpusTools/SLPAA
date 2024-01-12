import re
import logging
from copy import copy

from PyQt5.QtCore import (
    Qt,
    QSortFilterProxyModel,
    QDateTime
)

from PyQt5.Qt import (
    QStandardItem,
    QStandardItemModel
)

# TODO seems weird to be referencing a GUI element in this class...??
from PyQt5.QtWidgets import (
    QMessageBox
)

from lexicon.module_classes import userdefinedroles as udr, delimiter, AddedInfo

# for backwards compatibility
specifytotalcycles_str = "Specify total number of cycles"
numberofreps_str = "Number of repetitions"

rb = "radio button"  # ie mutually exclusive in group / at this level
cb = "checkbox"  # ie not mutually exlusive
ed_1 = "editable level 1"  # ie value is editable but restricted to numbers that are >= 1 and multiples of 0.5
ed_2 = "editable level 2"  # ie value is editable but restricted to numbers
ed_3 = "editable level 3"  # ie value is editable and unrestricted
fx = "fixed"  # ie value is not editable
subgroup = "subgroup"
custom_abbrev = "custom abbreviation" # for tooltip abbreviations which depend on user entry

c = True  # checked
u = False  # unchecked



class MvmtOptionsNode:
    # id MUST NOT change
    # __slots__ = ['display_name','user_specifiability','button_type', 'tooltip', 'options', 'children', 'id']
    # if more params are needed, use self.options

    def __init__(self, display_name="treeroot", user_specifiability=None, 
                 button_type=None, tooltip=None, options=None, children=None, id=-1):
        self.display_name = display_name # specify if subgroup
        self.user_specifiability = user_specifiability # ed_1, ed_2, ed_3, fx
        self.button_type = button_type # rb, cb, or subgroup count
        self.tooltip = tooltip
        self.options = options
        self.children = []
        if children is not None:
            for child in children:
                self.insert_child(child)
        self.id = id
        self.assign_ids(-1)

    def __repr__(self):
        return str(self.id) + ": " + self.display_name
    
    def assign_ids(self, current_id):
        # logging.warn(self)
        for child in self.children:
            current_id = current_id + 1
            child.id = current_id
            MvmtOptionsByID.append(child)
            current_id = child.assign_ids(current_id)
        return current_id

    def get_node_by_id(root, node_id): 
        # searches from root
        if root.id == node_id:
            return root
        else:
            # logging.warn("searching children")
            for child in root.children:
                # logging.warn(str(child.id))
                found = child.get_node_by_id(node_id)
                if found is not None: return found

    # search root's descendants for self's parent
    def get_parent_node(root, node):
        for child in root.children:
            if child.id == node.id:
                return root
            else:
                found = child.get_parent_node(node)
                if found is not None: return found

    def set_options(self): return

    def edit_display_name(self, new_name): 
        self.display_name = new_name

    # user sets text restrictions??
    def edit_user_specifiability(self, new_user_spec): 
        self.user_specifiability = new_user_spec

    def edit_button_type(self, new_button_type): 
        self.button_type = new_button_type

    def remove_node(root, node): 
        parent = root.get_parent_node(node)
        parent.children.remove(node)

    # TODO need to change subgroup number (saved in button_type) if subtrees are moved around
    def move_node(root, node, destination_node, position): 
        # position can be left, right, child, or parent
        # need an insert_parent method
        return
    
    def insert_parent(root, node, new_parent):
        current_parent = root.get_parent_node(node)
        for i, child in enumerate(current_parent.children):
            if child.id == node.id:
                current_parent.children[i] = new_parent
                new_parent.children.append(node)
                return


    # "node" should already have been assigned new ID
    def insert_sibling_left(root, node, new_sibling): 
        parent = root.get_parent_node(node)
        for i, child in enumerate(parent.children):
            if node.id ==  child.id:
                parent.children.insert(i, new_sibling)
                return

    def insert_sibling_right(root, node, new_sibling): 
        parent = root.get_parent_node(node)
        for i, child in enumerate(parent.children):
            if node.id ==  child.id:
                parent.children.insert(i+1, new_sibling)
                return

    # add node as the rightmost child of self
    # "node" should already have been assigned new ID
    def insert_child(self, node):
        self.children.append(node)

MvmtOptionsByID = []
defaultMvmtTree = MvmtOptionsNode(children=[
    MvmtOptionsNode("No movement", fx, rb),
    MvmtOptionsNode("Movement type", fx, cb, children=[
        MvmtOptionsNode("Perceptual shape", fx, rb, "Perceptual", children=[
            MvmtOptionsNode("Shape", fx, cb, children=[  # all mutually exclusive (straight vs arc vs ...)
                MvmtOptionsNode(subgroup, button_type=0, children=[
                    MvmtOptionsNode("Straight", fx, rb, children=[
                        MvmtOptionsNode("Interacts with subsequent straight movement", fx, rb, "interacts with subsequent straight mov.", children=[
                            MvmtOptionsNode("Movement contours cross (e.g. X)", fx, rb, "crosses subsequent mov."),
                            MvmtOptionsNode("Subsequent movement starts at end of first (e.g. ↘↗)", fx, rb, "ends where subsequent mov. starts"),
                            MvmtOptionsNode("Subsequent movement starts in same location as start of first (e.g. ↖↗)", fx, rb, "starts where subsequent mov. starts"),
                            MvmtOptionsNode("Subsequent movement ends in same location as end of first (e.g. ↘↙)", fx, rb, "ends where subsequent mov. ends")
                        ]),
                        MvmtOptionsNode("Doesn't interact with subsequent straight movement", fx, rb, "")
                    ]),
                    MvmtOptionsNode("Arc", fx, rb),
                    MvmtOptionsNode("Circle", fx, rb),
                    MvmtOptionsNode("Zigzag", fx, rb),
                    MvmtOptionsNode("Loop (travelling circles)", fx, rb, "Loop"),
                    MvmtOptionsNode("Other", ed_3, rb),
                ])
            ]),
            MvmtOptionsNode("Axis direction", fx, cb, children=[  # Choose up to one from each axis to get the complete direction
                # MvmtOptionsNode("H1 and H2 move in opposite directions", fx, cb, u, 18),
                MvmtOptionsNode(subgroup, button_type=0, children=[
                    MvmtOptionsNode("H1 and H2 move toward each other", fx, rb, "H1 & H2 toward each other"),
                    MvmtOptionsNode("H1 and H2 move away from each other", fx, rb, "H1 & H2 away from each other"),
                ]),
                MvmtOptionsNode(subgroup, button_type=1, children=[
                    MvmtOptionsNode("Absolute", fx, rb, children=[
                        MvmtOptionsNode("Horizontal", fx, cb, "Hor", children=[
                            MvmtOptionsNode(subgroup, button_type=0, children=[
                                MvmtOptionsNode("Ipsilateral", fx, rb, "ipsi"),  # TODO KV or toward H1
                                MvmtOptionsNode("Contralateral", fx, rb, "contra"),  # TODO KV or toward H2
                            ]),
                        ]),
                        MvmtOptionsNode("Vertical", fx, cb, "Ver", children=[
                            MvmtOptionsNode(subgroup, button_type=0, children=[
                                MvmtOptionsNode("Up", fx, rb, "up"),
                                MvmtOptionsNode("Down", fx, rb, "down"),
                            ]),
                        ]),
                        MvmtOptionsNode("Sagittal", fx, cb, "Sag", children=[
                            MvmtOptionsNode(subgroup, button_type=0, children=[
                                MvmtOptionsNode("Distal", fx, rb, "distal"),
                                MvmtOptionsNode("Proximal", fx, rb, "proximal"),
                            ]),
                        ]),
                    ]),
                    MvmtOptionsNode("Relative", fx, rb, children=[
                        MvmtOptionsNode("Finger(s)", fx, rb, children=[
                            MvmtOptionsNode("Across", fx, cb, children=[
                                MvmtOptionsNode("To ulnar side", fx, rb),
                                MvmtOptionsNode("To radial side", fx, rb),
                            ]),
                            MvmtOptionsNode("Along", fx, cb, children=[
                                MvmtOptionsNode("To base joint end", fx, rb),
                                MvmtOptionsNode("To tip end", fx, rb),
                            ]),
                            MvmtOptionsNode("Perpendicular to", fx, cb, children=[
                                MvmtOptionsNode("Away", fx, rb),
                                MvmtOptionsNode("Toward", fx, rb),
                            ])
                        ]),
                        MvmtOptionsNode("Hand", fx, rb, children=[
                            MvmtOptionsNode("Across", fx, cb, children=[
                                MvmtOptionsNode("To ulnar side", fx, rb),
                                MvmtOptionsNode("To radial side", fx, rb),
                            ]),
                            MvmtOptionsNode("Along", fx, cb, children=[
                                MvmtOptionsNode("To wrist end", fx, rb),
                                MvmtOptionsNode("To finger end", fx, rb),
                            ]),
                            MvmtOptionsNode("Perpendicular to", fx, cb, children=[
                                MvmtOptionsNode("Away", fx, rb),
                                MvmtOptionsNode("Toward", fx, rb),
                            ])
                        ]),
                        MvmtOptionsNode("Forearm", fx, rb, children=[
                            MvmtOptionsNode("Across", fx, cb, children=[
                                MvmtOptionsNode("To ulnar side", fx, rb),
                                MvmtOptionsNode("To radial side", fx, rb),
                            ]),
                            MvmtOptionsNode("Along", fx, cb, children=[
                                MvmtOptionsNode("To elbow end", fx, rb),
                                MvmtOptionsNode("To wrist end", fx, rb),
                            ]),
                            MvmtOptionsNode("Perpendicular to", fx, cb, children=[
                                MvmtOptionsNode("Away", fx, rb),
                                MvmtOptionsNode("Toward", fx, rb),
                            ])
                        ]),
                        MvmtOptionsNode("Upper arm", fx, rb, children=[
                            MvmtOptionsNode("Across", fx, cb, children=[
                                MvmtOptionsNode("To ulnar side", fx, rb),
                                MvmtOptionsNode("To radial side", fx, rb),
                            ]),
                            MvmtOptionsNode("Along", fx, cb, children=[
                                MvmtOptionsNode("To shoulder end", fx, rb),
                                MvmtOptionsNode("To elbow end", fx, rb),
                            ]),
                            MvmtOptionsNode("Perpendicular to", fx, cb, children=[
                                MvmtOptionsNode("Away", fx, rb),
                                MvmtOptionsNode("Toward", fx, rb),
                            ])
                        ]),
                        MvmtOptionsNode("Arm", fx, rb, children=[
                            MvmtOptionsNode("Across", fx, cb, children=[
                                MvmtOptionsNode("To ulnar side", fx, rb),
                                MvmtOptionsNode("To radial side", fx, rb),
                            ]),
                            MvmtOptionsNode("Along", fx, cb, children=[
                                MvmtOptionsNode("To shoulder end", fx, rb),
                                MvmtOptionsNode("To fingertip end", fx, rb),
                            ]),
                            MvmtOptionsNode("Perpendicular to", fx, cb, children=[
                                MvmtOptionsNode("Away", fx, rb),
                                MvmtOptionsNode("Toward", fx, rb),
                            ])
                        ]),
                        MvmtOptionsNode("Other", ed_3, rb, custom_abbrev, children=[
                            MvmtOptionsNode("Horizontal", fx, cb, children=[
                                MvmtOptionsNode("Ipsilateral", fx, rb),
                                MvmtOptionsNode("Contralateral", fx, rb),
                            ]),
                            MvmtOptionsNode("Vertical", fx, cb, children=[
                                MvmtOptionsNode("Up", fx, rb),
                                MvmtOptionsNode("Down", fx, rb),
                            ]),
                            MvmtOptionsNode("Sagittal", fx, cb, children=[
                                MvmtOptionsNode("Distal", fx, rb),
                                MvmtOptionsNode("Proximal", fx, rb),
                            ])
                        ])
                    ]),
                ]),
                MvmtOptionsNode("Not relevant", fx, rb, "")  # TODO KV Auto-select this if movement is straight or the axis is not relevant
            ]),
            MvmtOptionsNode("Plane", fx, cb, children=[  # choose as many as needed, but only one direction per plane
                MvmtOptionsNode(subgroup, button_type=0, children=[
                    MvmtOptionsNode("H1 and H2 move in opposite directions", fx, rb, "H1 & H2 opposite"),
                ]),
                MvmtOptionsNode(subgroup, button_type=1, children=[
                    

                    MvmtOptionsNode("Absolute", fx, rb, children=[
                        MvmtOptionsNode("Horizontal", fx, cb, "Hor", children=[
                            MvmtOptionsNode(subgroup, button_type=0, children=[
                                MvmtOptionsNode("Ipsilateral from top of circle", fx, rb, "ipsi from top"),
                                MvmtOptionsNode("Contralateral from top of circle", fx, rb, "contra from top"),
                                # MvmtOptionsNode("Clockwise", fx, rb, u),  # TODO KV or Ipsilateral from the top of the circle
                                # MvmtOptionsNode("Counterclockwise", fx, rb, u)  # TODO KV or Contralateral from the top of the circle
                            ]),
                        ]),
                        MvmtOptionsNode("Vertical", fx, cb, "Ver", children=[
                            MvmtOptionsNode(subgroup, button_type=0, children=[
                                MvmtOptionsNode("Ipsilateral from top of circle", fx, rb, "ipsi from top"),
                                MvmtOptionsNode("Contralateral from top of circle", fx, rb, "contra from top"),
                                # MvmtOptionsNode("Clockwise", fx, rb, u),  # TODO KV or Ipsilateral from the top of the circle
                                # MvmtOptionsNode("Counterclockwise", fx, rb, u)  # TODO KV or Contralateral from the top of the circle
                            ]),
                        ]),
                        MvmtOptionsNode("Sagittal", fx, cb, "Sag", children=[
                            MvmtOptionsNode(subgroup, button_type=0, children=[
                                MvmtOptionsNode("Distal from top of circle", fx, rb, "distal from top"),
                                MvmtOptionsNode("Proximal from top of circle", fx, rb, "proximal from top"),
                                # MvmtOptionsNode("Clockwise", fx, rb, u),
                                # MvmtOptionsNode("Counterclockwise", fx, rb, u)
                            ]),
                        ]),
                    
                    ]),
                    MvmtOptionsNode("Relative", fx, rb, children=[
                        MvmtOptionsNode("Finger(s)", fx, rb, children=[
                            MvmtOptionsNode("On plane of finger", fx, cb, children=[
                                MvmtOptionsNode("To tip end from radial side", fx, rb),
                                MvmtOptionsNode("To base end from radial side", fx, rb),
                            ]),
                            MvmtOptionsNode("Perpendicular to plane of finger, along length", fx, cb, children=[
                                MvmtOptionsNode("To tip end from centre of finger", fx, rb),
                                MvmtOptionsNode("To base end from centre of finger", fx, rb),
                            ]),
                            MvmtOptionsNode("Perpendicular to plane of finger, across width", fx, cb, children=[
                                MvmtOptionsNode("To radial side from centre of finger", fx, rb),
                                MvmtOptionsNode("To ulnar side from centre of finger", fx, rb),
                            ])
                        ]),
                        MvmtOptionsNode("Hand", fx, rb, children=[
                            MvmtOptionsNode("On plane of hand", fx, cb, children=[
                                MvmtOptionsNode("To finger end from radial side", fx, rb),
                                MvmtOptionsNode("To wrist end from radial side", fx, rb),
                            ]),
                            MvmtOptionsNode("Perpendicular to plane of hand, along length", fx, cb, children=[
                                MvmtOptionsNode("To finger end from centre of hand", fx, rb),
                                MvmtOptionsNode("To wrist end from centre of hand", fx, rb),
                            ]),
                            MvmtOptionsNode("Perpendicular to plane of hand, across width", fx, cb, children=[
                                MvmtOptionsNode("To radial side from centre of hand", fx, rb),
                                MvmtOptionsNode("To ulnar side from centre of hand", fx, rb),
                            ])
                        ]),
                        MvmtOptionsNode("Forearm", fx, rb, children=[
                            MvmtOptionsNode("On plane of forearm", fx, cb, children=[
                                MvmtOptionsNode("To wrist end from radial side", fx, rb),
                                MvmtOptionsNode("To elbow end from radial side", fx, rb),
                            ]),
                            MvmtOptionsNode("Perpendicular to plane of forearm, along length", fx, cb, children=[
                                MvmtOptionsNode("To wrist end from centre of forearm", fx, rb),
                                MvmtOptionsNode("To elbow end from centre of forearm", fx, rb),
                            ]),
                            MvmtOptionsNode("Perpendicular to plane of forearm, across width", fx, cb, children=[
                                MvmtOptionsNode("To radial side from centre of forearm", fx, rb),
                                MvmtOptionsNode("To ulnar side from centre of forearm", fx, rb),
                            ])
                        ]),
                        MvmtOptionsNode("Upper arm", fx, rb, children=[
                            MvmtOptionsNode("On plane of upper arm", fx, cb, children=[
                                MvmtOptionsNode("To elbow end from radial side", fx, rb),
                                MvmtOptionsNode("To shoulder end from radial side", fx, rb),
                            ]),
                            MvmtOptionsNode("Perpendicular to plane of upper arm, along length", fx, cb, children=[
                                MvmtOptionsNode("To wrist end from centre of upper arm", fx, rb),
                                MvmtOptionsNode("To elbow end from centre of upper arm", fx, rb),
                            ]),
                            MvmtOptionsNode("Perpendicular to plane of upper arm, across width", fx, cb, children=[
                                MvmtOptionsNode("To radial side from centre of upper arm", fx, rb),
                                MvmtOptionsNode("To ulnar side from centre of upper arm", fx, rb),
                            ])
                        ]),
                        MvmtOptionsNode("Arm", fx, rb, children=[
                            MvmtOptionsNode("On plane of arm", fx, cb, children=[
                                MvmtOptionsNode("To fingertip end from radial side", fx, rb),
                                MvmtOptionsNode("To shoulder end from radial side", fx, rb),
                            ]),
                            MvmtOptionsNode("Perpendicular to plane of arm, along length", fx, cb, children=[
                                MvmtOptionsNode("To elbow end from centre of arm", fx, rb),
                                MvmtOptionsNode("To shoulder end from centre of arm", fx, rb),
                            ]),
                            MvmtOptionsNode("Perpendicular to plane of arm, across width", fx, cb, children=[
                                MvmtOptionsNode("To radial side from centre of arm", fx, rb),
                                MvmtOptionsNode("To ulnar side from centre of arm", fx, rb),
                            ])
                        ]),
                        MvmtOptionsNode("Other", ed_3, rb, custom_abbrev, children=[
                            MvmtOptionsNode(subgroup, button_type=0, children=[
                                MvmtOptionsNode("Top:", ed_3, cb, custom_abbrev)
                            ]),
                            MvmtOptionsNode("Horizontal", fx, cb, children=[
                                MvmtOptionsNode("Ipsilateral", fx, rb),
                                MvmtOptionsNode("Contralateral", fx, rb),
                            ]),
                            MvmtOptionsNode("Vertical", fx, cb, children=[
                                MvmtOptionsNode("Up", fx, rb),
                                MvmtOptionsNode("Down", fx, rb),
                            ]),
                            MvmtOptionsNode("Sagittal", fx, cb, children=[
                                MvmtOptionsNode("Distal", fx, rb),
                                MvmtOptionsNode("Proximal", fx, rb),
                            ])
                        ])
                    ])
                ]),
                MvmtOptionsNode("Not relevant", fx, rb, ""),  # TODO KV Auto-select this if movement is straight or the axis is not relevant
            ]),
        ]),
        # mutually exclusive @ level of pivoting, twisting, etc. and also within (nodding vs unnodding)
        MvmtOptionsNode("Joint-specific movements", fx, rb, children=[
            MvmtOptionsNode("Nodding/un-nodding", fx, rb, "Nod/Un-", children=[
                MvmtOptionsNode(subgroup, button_type=0, children=[
                    MvmtOptionsNode("Nodding", fx, rb, "nod"), # TODO KV autofills to flexion of wrist (but *ask* before auto-unfilling if nodding is unchecked)
                    MvmtOptionsNode("Un-nodding", fx, rb, "un-nod"), # TODO KV autofills to extension of wrist
                ])
            ]),
            MvmtOptionsNode("Pivoting", fx, rb, "Pivot", children=[
                MvmtOptionsNode(subgroup, button_type=0, children=[
                    MvmtOptionsNode("Radial", fx, rb, "ulnar pivot"),  # TODO KV autofills to wrist radial deviation
                    MvmtOptionsNode("Ulnar", fx, rb, "radial pivot"),  # TODO KV autofills to wrist ulnar deviation
                ])
            ]),
            MvmtOptionsNode("Twisting", fx, rb, "Twist", children=[
                MvmtOptionsNode(subgroup, button_type=0, children=[
                    MvmtOptionsNode("Pronation", fx, rb, "pronation"),  # TODO KV autofills to Proximal radioulnar pronation
                    MvmtOptionsNode("Supination", fx, rb, "supination"),  # TODO KV autofills to Proximal radioulnar supination
                ])
            ]),
            MvmtOptionsNode("Fully rotating", fx, rb, "Full rotation", children=[
                MvmtOptionsNode(subgroup, button_type=0, children=[
                    MvmtOptionsNode("Ulnar → nodding → supination → radial → un-nodding", fx, rb, "ulnar → nodding"),
                    MvmtOptionsNode("Radial → nodding → pronation → ulnar → un-nodding", fx, rb, "radial → nodding"),
                ])
            ]),
            MvmtOptionsNode("Closing/Opening", fx, rb, "Close/Open", children=[
                MvmtOptionsNode(subgroup, button_type=0, children=[
                    MvmtOptionsNode("Closing", fx, rb, "close"),  # TODO KV autofills to flexion of [selected finger, all joints]
                    MvmtOptionsNode("Opening", fx, rb, "open"),  # TODO KV autofills to extension of [selected finger, all joints]
                ])
            ]),
            MvmtOptionsNode("Pinching/unpinching", fx, rb, "Pinch/Un-", children=[
                MvmtOptionsNode(subgroup, button_type=0, children=[
                    MvmtOptionsNode("Pinching (Morgan 2017)", fx, rb, "pinch"),  # TODO KV autofills to adduction of thumb base joint
                    MvmtOptionsNode("Unpinching", fx, rb, "unpinch"),  # TODO KV autofills to (abduction of thumb base joint? - not specific in google doc)
                ])
            ]),
            MvmtOptionsNode("Flattening/Straightening", fx, rb, "Flatten/Straighten", children=[
                MvmtOptionsNode(subgroup, button_type=0, children=[
                    MvmtOptionsNode("Flattening/hinging", fx, rb, "flatten"),  # TODO KV autofills to flexion of [selected finger base joints]
                    MvmtOptionsNode("Straightening", fx, rb, "straighten"),  # TODO KV autofills to extension of [selected finger base joints]
                ])
            ]),
            MvmtOptionsNode("Hooking/Unhooking", fx, rb, "Hook/Un-", children=[
                MvmtOptionsNode(subgroup, button_type=0, children=[
                    MvmtOptionsNode("Hooking/clawing", fx, rb, "hook"),  # TODO KV autofills to flexion of [selected finger non-base joints]
                    MvmtOptionsNode("Unhooking", fx, rb, "unhook"),  # TODO KV autofills to extension of [selected finger non-base joints]
                ])
            ]),
            MvmtOptionsNode("Spreading/Unspreading", fx, rb, "Spread/Un-", children=[
                MvmtOptionsNode(subgroup, button_type=0, children=[
                    MvmtOptionsNode("Spreading", fx, rb, "spread"),  # TODO KV autofills to abduction of [selected finger base joints]
                    MvmtOptionsNode("Unspreading", fx, rb, "unspread"),  # TODO KV autofills to adduction of [selected finger base joints]
                ])
            ]),
            MvmtOptionsNode("Rubbing", fx, rb, "Rub", children=[
                MvmtOptionsNode("Articulator(s):", fx, cb, "", children=[
                    MvmtOptionsNode("Thumb", fx, cb, ""),
                    MvmtOptionsNode("Finger(s)", fx, cb, ""),
                    MvmtOptionsNode("Other", ed_3, cb, custom_abbrev)
                ]),
                MvmtOptionsNode("Location:", fx, cb, "", children=[
                    MvmtOptionsNode("Thumb", fx, rb, ""),
                    MvmtOptionsNode("Finger(s)", fx, rb, ""),
                    MvmtOptionsNode("Palm", fx, rb, ""),
                    MvmtOptionsNode("Other", ed_3, rb, custom_abbrev)
                ]),
                MvmtOptionsNode("Across", fx, cb, "", children=[
                    MvmtOptionsNode("to radial side", fx, rb, ""),
                    MvmtOptionsNode("to ulnar side", fx, rb, ""),
                ]),
                MvmtOptionsNode("Along", fx, cb, "", children=[
                    MvmtOptionsNode("to fingertip end", fx, rb, ""),
                    MvmtOptionsNode("to base end", fx, rb, ""),
                ])
            ]),
            MvmtOptionsNode("Wiggling/Fluttering", fx, rb, "Wiggle"),  # TODO KV autofills to both flexion and extension of selected finger base joints
            MvmtOptionsNode("Other", ed_3, rb),
        ]),
        MvmtOptionsNode("Handshape change", fx, rb, "")
    ]),
    MvmtOptionsNode("Joint activity", fx, cb, children=[
        MvmtOptionsNode("Complex / multi-joint", fx, cb, ""),  # from Yurika: if this is selected, the expectation is that nothing else below would be selected, though I guess people could...
        MvmtOptionsNode("Shoulder", fx, cb, "", children=[
            MvmtOptionsNode(subgroup, button_type=0, children=[
                MvmtOptionsNode("Flexion", fx, rb, ""),
                MvmtOptionsNode("Extension", fx, rb, ""),
            ]),
            MvmtOptionsNode(subgroup, button_type=1, children=[
                MvmtOptionsNode("Abduction", fx, rb, ""),
                MvmtOptionsNode("Adduction", fx, rb, ""),
            ]),
            MvmtOptionsNode(subgroup, button_type=2, children=[
                MvmtOptionsNode("Posterior rotation", fx, rb, ""),
                MvmtOptionsNode("Anterior rotation", fx, rb, ""),
            ]),
            MvmtOptionsNode(subgroup, button_type=3, children=[
                MvmtOptionsNode("Protraction", fx, rb, ""),
                MvmtOptionsNode("Retraction", fx, rb, ""),
            ]),
            MvmtOptionsNode(subgroup, button_type=4, children=[
                MvmtOptionsNode("Depression", fx, rb, ""),
                MvmtOptionsNode("Elevation", fx, rb, ""),
            ]),
            MvmtOptionsNode(subgroup, button_type=5, children=[
                MvmtOptionsNode("Circumduction", fx, cb, "", children=[
                    MvmtOptionsNode(subgroup, button_type=0, children=[
                        MvmtOptionsNode("Forward from top of circle", fx, rb, ""),
                        MvmtOptionsNode("Backward from top of circle", fx, rb, "")
                    ])                    
                ])
            ])
        ]),
        MvmtOptionsNode("Elbow", fx, cb, "", children=[
            MvmtOptionsNode(subgroup, button_type=0, children=[
                MvmtOptionsNode("Flexion", fx, rb, ""),
                MvmtOptionsNode("Extension", fx, rb, ""),
            ])
        ]),
        MvmtOptionsNode("Radio-ulnar", fx, cb, "", children=[
            MvmtOptionsNode(subgroup, button_type=0, children=[
                MvmtOptionsNode("Pronation", fx, rb, ""),
                MvmtOptionsNode("Supination", fx, rb, ""),
            ])
        ]),
        MvmtOptionsNode("Wrist", fx, cb, "", children=[
            MvmtOptionsNode(subgroup, button_type=0, children=[
                MvmtOptionsNode("Flexion", fx, rb, ""),
                MvmtOptionsNode("Extension", fx, rb, ""),
            ]),
            MvmtOptionsNode(subgroup, button_type=1, children=[
                MvmtOptionsNode("Radial deviation", fx, rb, ""),
                MvmtOptionsNode("Ulnar deviation", fx, rb, ""),
            ]),
            MvmtOptionsNode(subgroup, button_type=2, children=[
                MvmtOptionsNode("Circumduction", fx, cb, "", children=[
                    MvmtOptionsNode(subgroup, button_type=0, children=[
                        MvmtOptionsNode("Ulnar → nodding → supination → radial → un-nodding", fx, rb, ""),
                        MvmtOptionsNode("Radial → nodding → pronation → ulnar → un-nodding", fx, rb, ""),
                    ])                
                ])
            ]),
        ]),
        MvmtOptionsNode("Thumb root / carpometacarpal (CMC)", fx, cb, "", children=[
            MvmtOptionsNode(subgroup, button_type=0, children=[
                MvmtOptionsNode("Flexion", fx, rb, ""),
                MvmtOptionsNode("Extension", fx, rb, ""),
            ]),
            MvmtOptionsNode(subgroup, button_type=1, children=[
                MvmtOptionsNode("Palmar abduction", fx, rb, ""),
                MvmtOptionsNode("Palmar adduction", fx, rb, ""),
            ]),
            MvmtOptionsNode(subgroup, button_type=2, children=[
                MvmtOptionsNode("Radial abduction", fx, rb, ""),
                MvmtOptionsNode("Radial adduction", fx, rb, ""),
            ]),
            MvmtOptionsNode(subgroup, button_type=3, children=[
                MvmtOptionsNode("Circumduction", fx, rb, "", children=[
                    MvmtOptionsNode(subgroup, button_type=0, children=[
                        MvmtOptionsNode("Opposition from neutral position", fx, rb, ""),
                        MvmtOptionsNode("Lateral from neutral position", fx, rb, "")
                    ])
                ])
            ]),
        ]),      
        MvmtOptionsNode("Thumb base / metacarpophalangeal (MCP)", fx, cb, "", children=[
            MvmtOptionsNode(subgroup, button_type=0, children=[
                MvmtOptionsNode("Flexion", fx, rb, ""),
                MvmtOptionsNode("Extension", fx, rb, ""),
            ])                    
        ]),
        MvmtOptionsNode("Thumb non-base / interphalangeal (IP)", fx, cb, "", children=[
            MvmtOptionsNode(subgroup, button_type=0, children=[
                MvmtOptionsNode("Flexion", fx, rb, ""),
                MvmtOptionsNode("Extension", fx, rb, ""),
            ])
        ]),
        MvmtOptionsNode("Thumb complex movement", fx, cb, "", children=[
            MvmtOptionsNode(subgroup, button_type=0, children=[
                MvmtOptionsNode("Opposition", fx, rb, ""),
                MvmtOptionsNode("Un-opposition", fx, rb, ""),
            ])
        ]),
        MvmtOptionsNode("Finger 1 base / metacarpophalangeal", fx, cb, "", children=[
            MvmtOptionsNode(subgroup, button_type=0, children=[
                MvmtOptionsNode("Flexion", fx, rb, ""),
                MvmtOptionsNode("Extension", fx, rb, ""),
            ]),
            MvmtOptionsNode(subgroup, button_type=1, children=[
                MvmtOptionsNode("Abduction", fx, rb, ""),
                MvmtOptionsNode("Adduction", fx, rb, ""),
            ]),
            MvmtOptionsNode(subgroup, button_type=2, children=[
                MvmtOptionsNode("Circumduction", fx, cb, "", children=[
                    MvmtOptionsNode(subgroup, button_type=0, children=[
                        MvmtOptionsNode("Ulnar from neutral position", fx, rb, ""),
                        MvmtOptionsNode("Radial from neutral position", fx, rb, ""),
                    ])                    
                ])
            ]),
        ]),
        MvmtOptionsNode("Finger 2 base / metacarpophalangeal", fx, cb, "", children=[
            MvmtOptionsNode(subgroup, button_type=0, children=[
                MvmtOptionsNode("Flexion", fx, rb, ""),
                MvmtOptionsNode("Extension", fx, rb, ""),
            ]),
            MvmtOptionsNode(subgroup, button_type=1, children=[
                MvmtOptionsNode("Abduction", fx, rb, ""),
                MvmtOptionsNode("Adduction", fx, rb, ""),
            ]),
            MvmtOptionsNode(subgroup, button_type=2, children=[
                MvmtOptionsNode("Circumduction", fx, cb, "", children=[
                    MvmtOptionsNode(subgroup, button_type=0, children=[
                        MvmtOptionsNode("Ulnar from neutral position", fx, rb, ""),
                        MvmtOptionsNode("Radial from neutral position", fx, rb, ""),
                    ])                    
                ])
            ]),
        ]),
        MvmtOptionsNode("Finger 3 base / metacarpophalangeal", fx, cb, "", children=[
            MvmtOptionsNode(subgroup, button_type=0, children=[
                MvmtOptionsNode("Flexion", fx, rb, ""),
                MvmtOptionsNode("Extension", fx, rb, ""),
            ]),
            MvmtOptionsNode(subgroup, button_type=1, children=[
                MvmtOptionsNode("Abduction", fx, rb, ""),
                MvmtOptionsNode("Adduction", fx, rb, ""),
            ]),
            MvmtOptionsNode(subgroup, button_type=2, children=[
                MvmtOptionsNode("Circumduction", fx, cb, "", children=[
                    MvmtOptionsNode(subgroup, button_type=0, children=[
                        MvmtOptionsNode("Ulnar from neutral position", fx, rb, ""),
                        MvmtOptionsNode("Radial from neutral position", fx, rb, ""),
                    ])                    
                ])
            ]),
        ]),    
        MvmtOptionsNode("Finger 4 base / metacarpophalangeal", fx, cb, "", children=[
            MvmtOptionsNode(subgroup, button_type=0, children=[
                MvmtOptionsNode("Flexion", fx, rb, ""),
                MvmtOptionsNode("Extension", fx, rb, ""),
            ]),
            MvmtOptionsNode(subgroup, button_type=1, children=[
                MvmtOptionsNode("Abduction", fx, rb, ""),
                MvmtOptionsNode("Adduction", fx, rb, ""),
            ]),
            MvmtOptionsNode(subgroup, button_type=2, children=[
                MvmtOptionsNode("Circumduction", fx, cb, "", children=[
                    MvmtOptionsNode(subgroup, button_type=0, children=[
                        MvmtOptionsNode("Ulnar from neutral position", fx, rb, ""),
                        MvmtOptionsNode("Radial from neutral position", fx, rb, ""),
                    ])                    
                ])
            ]),
        ]),                    
        MvmtOptionsNode("Finger 1 proximal interphalangeal", fx, cb, "", children=[
            MvmtOptionsNode(subgroup, button_type=0, children=[
                MvmtOptionsNode("Flexion", fx, rb, ""),
                MvmtOptionsNode("Extension", fx, rb, ""),
            ])
        ]),
        MvmtOptionsNode("Finger 2 proximal interphalangeal", fx, cb, "", children=[
            MvmtOptionsNode(subgroup, button_type=0, children=[
                MvmtOptionsNode("Flexion", fx, rb, ""),
                MvmtOptionsNode("Extension", fx, rb, ""),
            ])
        ]),
        MvmtOptionsNode("Finger 3 proximal interphalangeal", fx, cb, "", children=[
            MvmtOptionsNode(subgroup, button_type=0, children=[
                MvmtOptionsNode("Flexion", fx, rb, ""),
                MvmtOptionsNode("Extension", fx, rb, ""),
            ])
        ]),
        MvmtOptionsNode("Finger 4 proximal interphalangeal", fx, cb, "", children=[
            MvmtOptionsNode(subgroup, button_type=0, children=[
                MvmtOptionsNode("Flexion", fx, rb, ""),
                MvmtOptionsNode("Extension", fx, rb, ""),
            ])
        ]),                                
        MvmtOptionsNode("Finger 1 distal interphalangeal", fx, cb, "", children=[
            MvmtOptionsNode(subgroup, button_type=0, children=[
                MvmtOptionsNode("Flexion", fx, rb, ""),
                MvmtOptionsNode("Extension", fx, rb, ""),
            ])
        ]),
        MvmtOptionsNode("Finger 2 distal interphalangeal", fx, cb, "", children=[
            MvmtOptionsNode(subgroup, button_type=0, children=[
                MvmtOptionsNode("Flexion", fx, rb, ""),
                MvmtOptionsNode("Extension", fx, rb, ""),
            ])
        ]),        
        MvmtOptionsNode("Finger 3 distal interphalangeal", fx, cb, "", children=[
            MvmtOptionsNode(subgroup, button_type=0, children=[
                MvmtOptionsNode("Flexion", fx, rb, ""),
                MvmtOptionsNode("Extension", fx, rb, ""),
            ])
        ]),
        MvmtOptionsNode("Finger 4 distal interphalangeal", fx, cb, "", children=[
            MvmtOptionsNode(subgroup, button_type=0, children=[
                MvmtOptionsNode("Flexion", fx, rb, ""),
                MvmtOptionsNode("Extension", fx, rb, ""),
            ])
        ]),
        MvmtOptionsNode("Hip", fx, cb, "", children=[
            MvmtOptionsNode(subgroup, button_type=0, children=[
                MvmtOptionsNode("Flexion", fx, rb, ""),
                MvmtOptionsNode("Extension", fx, rb, ""),
            ]),
            MvmtOptionsNode(subgroup, button_type=1, children=[
                MvmtOptionsNode("Abduction", fx, rb, ""),
                MvmtOptionsNode("Adduction", fx, rb, ""),
            ]),
            MvmtOptionsNode(subgroup, button_type=2, children=[
                MvmtOptionsNode("Internal rotation", fx, rb, ""),
                MvmtOptionsNode("External rotation", fx, rb, ""),
            ]),
            MvmtOptionsNode(subgroup, button_type=3, children=[
                MvmtOptionsNode("Depression", fx, rb, ""),
                MvmtOptionsNode("Elevation", fx, rb, ""),
            ]),
            MvmtOptionsNode(subgroup, button_type=4, children=[
                MvmtOptionsNode("Circumduction", fx, rb, ""),
            ]),
        ]),
        MvmtOptionsNode("Knee", fx, cb, "", children=[
            MvmtOptionsNode(subgroup, button_type=0, children=[
                MvmtOptionsNode("Flexion", fx, rb, ""),
                MvmtOptionsNode("Extension", fx, rb, ""),
            ]),
        ]),
        MvmtOptionsNode("Ankle", fx, cb, "", children=[
            MvmtOptionsNode(subgroup, button_type=0, children=[
                MvmtOptionsNode("Dorsi-flexion", fx, rb, ""),
                MvmtOptionsNode("Plantar-flexion", fx, rb, ""),
            ]),
            MvmtOptionsNode(subgroup, button_type=5, children=[
                MvmtOptionsNode("Inversion", fx, rb, ""),
                MvmtOptionsNode("Eversion", fx, rb, ""),
            ]),
            MvmtOptionsNode(subgroup, button_type=6, children=[
                MvmtOptionsNode("Circumduction", fx, rb, ""),
            ]),
        ])
    ]),
    MvmtOptionsNode("Movement characteristics", fx, cb, children=[
        MvmtOptionsNode("Repetition", fx, cb, children=[
            MvmtOptionsNode("Single", fx, rb, "1x"),
            MvmtOptionsNode("Repeated", fx, rb, custom_abbrev, children=[
                MvmtOptionsNode(specifytotalcycles_str, ed_1, cb, custom_abbrev, children=[
                    # MvmtOptionsNode("#", ed, cb, "", children=[
                    MvmtOptionsNode("This number is a minimum", fx, cb, custom_abbrev),
                    # ]),
                ]),
                MvmtOptionsNode("Location of repetition", fx, cb, children=[
                    MvmtOptionsNode("Same location", fx, rb, ""),
                    MvmtOptionsNode("Different location", fx, rb, "diff. loc", children=[  # Choose up to one from each column as needed
                        MvmtOptionsNode("Horizontal", fx, cb, "Hor", children=[
                            # MvmtOptionsNode(subgroup, button_type=2, children=[
                            MvmtOptionsNode("Ipsilateral", fx, rb, "ipsi"),  # TODO KV default ipsi/contra; can choose right/left in settings
                            MvmtOptionsNode("Contralateral", fx, rb, "contra")
                            # ]
                        ]),
                        MvmtOptionsNode("Vertical", fx, cb, "Ver", children=[
                            # MvmtOptionsNode(subgroup, button_type=0, children=[
                            MvmtOptionsNode("Up", fx, rb, "up"),
                            MvmtOptionsNode("Down", fx, rb, "down")
                            # ]),
                        ]),
                        MvmtOptionsNode("Sagittal", fx, cb, "Sag", children=[
                            # MvmtOptionsNode(subgroup, button_type=1, children=[
                            MvmtOptionsNode("Distal", fx, rb, "distal"),
                            MvmtOptionsNode("Proximal", fx, rb, "proximal")
                            # ]),
                        ]),
                    ])
                ])
            ]),
            MvmtOptionsNode("Trilled", fx, rb),
        ]),
        MvmtOptionsNode("Directionality", fx, cb, children=[
            MvmtOptionsNode(subgroup, button_type=0, children=[
                MvmtOptionsNode("Unidirectional", fx, rb, "Unidirec"),
                MvmtOptionsNode("Bidirectional", fx, rb, "Bidirec")
            ])
        ]),
        MvmtOptionsNode("Additional characteristics", fx, cb, children=[
            MvmtOptionsNode("Size", fx, cb, children=[
                MvmtOptionsNode(subgroup, button_type=0, children=[
                    MvmtOptionsNode("Big", fx, rb),
                    MvmtOptionsNode("Normal", fx, rb),
                    MvmtOptionsNode("Small", fx, rb),
                    MvmtOptionsNode("Other", ed_3, rb),
                ]),
                MvmtOptionsNode(subgroup, button_type=1, children=[
                    MvmtOptionsNode("Relative to", ed_3, cb, custom_abbrev),
                ])
            ]),
            MvmtOptionsNode("Speed", fx, cb, children=[
                MvmtOptionsNode(subgroup, button_type=0, children=[
                    MvmtOptionsNode("Fast", fx, rb),
                    MvmtOptionsNode("Normal", fx, rb),
                    MvmtOptionsNode("Slow", fx, rb),
                    MvmtOptionsNode("Other", ed_3, rb),
                ]),
                MvmtOptionsNode(subgroup, button_type=1, children=[
                    MvmtOptionsNode("Relative to", ed_3, cb, custom_abbrev),
                ])
            ]),
            MvmtOptionsNode("Force", fx, cb, children=[
                MvmtOptionsNode(subgroup, button_type=0, children=[
                    MvmtOptionsNode("Strong", fx, rb),
                    MvmtOptionsNode("Normal", fx, rb),
                    MvmtOptionsNode("Weak", fx, rb),
                    MvmtOptionsNode("Other", ed_3, rb),
                ]),
                MvmtOptionsNode(subgroup, button_type=1, children=[
                    MvmtOptionsNode("Relative to", ed_3, cb, custom_abbrev),
                ])
            ]),
            MvmtOptionsNode("Tension", fx, cb, children=[
                MvmtOptionsNode(subgroup, button_type=0, children=[
                    MvmtOptionsNode("Tense", fx, rb),
                    MvmtOptionsNode("Normal", fx, rb),
                    MvmtOptionsNode("Lax", fx, rb),
                    MvmtOptionsNode("Other", ed_3, rb),
                ]),
                MvmtOptionsNode(subgroup, button_type=1, children=[
                    MvmtOptionsNode("Relative to", ed_3, cb, custom_abbrev),
                ])
            ]),
            MvmtOptionsNode("Other", ed_3, cb)
        ])
    ])

])

# defaultMvmtTree.assign_ids(-1)



class MovementTreeItem(QStandardItem):

    def __init__(self, txt="", nodeID=-1, listit=None, mutuallyexclusive=False, addedinfo=None, serializedmvmtitem=None):
        super().__init__()

        self.setEditable(False)

        if serializedmvmtitem:
            self.setText(serializedmvmtitem['text'])
            self.setCheckable(serializedmvmtitem['checkable'])
            self.setCheckState(serializedmvmtitem['checkstate'])
            self.setUserTristate(serializedmvmtitem['usertristate'])
            self.setData(serializedmvmtitem['selectedrole'], Qt.UserRole+udr.selectedrole)
            self.setData(serializedmvmtitem['timestamprole'], Qt.UserRole+udr.timestamprole)
            self.setData(serializedmvmtitem['isuserspecifiablerole'], Qt.UserRole+udr.isuserspecifiablerole)
            self.setData(serializedmvmtitem['userspecifiedvaluerole'], Qt.UserRole+udr.userspecifiedvaluerole)
            self.setData(serializedmvmtitem['mutuallyexclusiverole'], Qt.UserRole+udr.mutuallyexclusiverole)
            self.setData(serializedmvmtitem['displayrole'], Qt.DisplayRole)
            self._addedinfo = serializedmvmtitem['addedinfo']
            self._nodeID = serializedmvmtitem['nodeID']
            self.listitem = MovementListItem(serializedlistitem=serializedmvmtitem['listitem'])
            self.listitem.treeitem = self
        else:
            self.setText(txt)
            self.setCheckable(True)
            self.setCheckState(Qt.Unchecked)
            self.setUserTristate(False)
            self.setData(False, Qt.UserRole+udr.selectedrole)
            self.setData(QDateTime.currentDateTimeUtc(), Qt.UserRole+udr.timestamprole)
            self.setData(fx, Qt.UserRole+udr.isuserspecifiablerole)
            self.setData("", Qt.UserRole+udr.userspecifiedvaluerole)
            self._addedinfo = addedinfo if addedinfo is not None else AddedInfo()
            self._nodeID = nodeID

            if mutuallyexclusive:
                self.setData(True, Qt.UserRole+udr.mutuallyexclusiverole)
            else:
                self.setData(False, Qt.UserRole+udr.mutuallyexclusiverole)

            self.listitem = listit
            if listit is not None:
                self.listitem.treeitem = self

    def __repr__(self):
        return '<MovementTreeItem: ' + repr(self.text()) + '>'

    def setData(self, value, role=Qt.DisplayRole):
        super().setData(value, role)

        if role == Qt.UserRole + udr.userspecifiedvaluerole and hasattr(self, "listitem") and self.listitem is not None:
            # also update the associated list item (and its displayed value)
            self.listitem.setData(value, role)

    def serialize(self):
        return {
            'text': self.text(),
            'checkable': self.isCheckable(),
            'checkstate': self.checkState(),
            'usertristate': self.isUserTristate(),
            'selectedrole': self.data(Qt.UserRole+udr.selectedrole),
            'timestamprole': self.data(Qt.UserRole+udr.timestamprole),
            'mutuallyexclusiverole': self.data(Qt.UserRole+udr.mutuallyexclusiverole),
            'displayrole': self.data(Qt.DisplayRole),
            'isuserspecifiablerole': self.data(Qt.UserRole+udr.isuserspecifiablerole),
            'userspecifiedvaluerole': self.data(Qt.UserRole+udr.userspecifiedvaluerole),
            'addedinfo': self._addedinfo,
            'nodeID': self._nodeID
            # 'listitem': self.listitem.serialize()  # TODO KV why not? the constructor uses it...
        }

    def editablepart(self):
        return self.parent().child(self.row(), 1)

    @property
    def addedinfo(self):
        return self._addedinfo

    @addedinfo.setter
    def addedinfo(self, addedinfo):
        self._addedinfo = addedinfo if addedinfo is not None else AddedInfo()

    # GZ was nodetypeID, don't think it was used anywhere
    @property
    def nodeID(self):
        return self._nodeID

    @nodeID.setter
    def nodeID(self, nodeID):
        self._nodeID = nodeID if nodeID is not None else -1

    def setEnabledRecursive(self, enable):
        self.setEnabled(enable)
        if not enable:
            self.uncheck()
        if self.data(Qt.UserRole+udr.isuserspecifiablerole) != fx:
            self.editablepart().setEnabled(enable)

        for r in range(self.rowCount()):
            self.child(r, 0).setEnabledRecursive(enable)

    def check(self, fully=True):
        self.setCheckState(Qt.Checked if fully else Qt.PartiallyChecked)
        self.listitem.setData(fully, Qt.UserRole+udr.selectedrole)
        if fully:
            self.setData(QDateTime.currentDateTimeUtc(), Qt.UserRole+udr.timestamprole)
            self.listitem.setData(QDateTime.currentDateTimeUtc(), Qt.UserRole+udr.timestamprole)
        self.checkancestors()

        # gather siblings in order to deal with mutual exclusivity (radio buttons)
        siblings = self.collectsiblings()

        # if this is a radio button item, make sure none of its siblings are checked
        if self.data(Qt.UserRole+udr.mutuallyexclusiverole):
            for sib in siblings:
                sib.uncheck(force=True)
        else:  # or if it has radio button siblings, make sure they are unchecked
            for me_sibling in [s for s in siblings if s.data(Qt.UserRole+udr.mutuallyexclusiverole)]:
                me_sibling.uncheck(force=True)

    def collectsiblings(self):

        siblings = []
        parent = self.parent()
        if not parent:
            parent = self.model().invisibleRootItem()
        numsiblingsincludingself = parent.rowCount()
        for snum in range(numsiblingsincludingself):
            sibling = parent.child(snum, 0)
            if sibling.index() != self.index():  # ie, it's actually a sibling
                siblings.append(sibling)

        mysubgroup = self.data(Qt.UserRole+udr.subgroupnamerole)
        subgrouporgeneralsiblings = [sib for sib in siblings if sib.data(Qt.UserRole+udr.subgroupnamerole) == mysubgroup or not sib.data(Qt.UserRole+udr.subgroupnamerole)]
        subgroupsiblings = [sib for sib in siblings if sib.data(Qt.UserRole+udr.subgroupnamerole) == mysubgroup]

        # if I'm ME and in a subgroup, collect siblings from my subgroup and also those at my level but not in any subgroup
        if self.data(Qt.UserRole+udr.mutuallyexclusiverole) and mysubgroup:
            return subgrouporgeneralsiblings
        # if I'm ME and not in a subgroup, collect all siblings from my level (in subgroups or no)
        elif self.data(Qt.UserRole+udr.mutuallyexclusiverole):
            return siblings
        # if I'm *not* ME but I'm in a subgroup, collect all siblings from my subgroup and also those at my level but not in any subgroup
        elif not self.data(Qt.UserRole + udr.mutuallyexclusiverole) and mysubgroup:
            return subgrouporgeneralsiblings
        # if I'm *not* ME and not in a subgroup, collect all siblings from my level (in subgroups or no)
        elif not self.data(Qt.UserRole+udr.mutuallyexclusiverole):
            return siblings

    def checkancestors(self):
        if self.checkState() == Qt.Unchecked:
            self.setCheckState(Qt.PartiallyChecked)
        if self.parent() is not None:
            self.parent().checkancestors()

    def uncheck(self, force=False):
        name = self.data()

        self.listitem.setData(False, Qt.UserRole+udr.selectedrole)
        self.setData(False, Qt.UserRole+udr.selectedrole)

        if force:  # force-clear this item and all its descendants - have to start at the bottom?
            # force-uncheck all descendants
            if self.hascheckedchild():
                for r in range(self.rowCount()):
                    for colnum in [0]:
                        ch = self.child(r, colnum)
                        if ch is not None:
                            ch.uncheck(force=True)
            self.setCheckState(Qt.Unchecked)
        elif self.hascheckedchild():
            self.setCheckState(Qt.PartiallyChecked)
        else:
            self.setCheckState(Qt.Unchecked)
            if self.parent() is not None:
                self.parent().uncheckancestors()

        if self.data(Qt.UserRole+udr.mutuallyexclusiverole):
            pass
            # TODO KV is this relevant? shouldn't be able to uncheck anyway
        elif True:  # has a mutually exclusive sibling
            pass
            # might one of those sibling need to be checked, if none of the boxes are?

    def uncheckancestors(self):
        if self.checkState() == Qt.PartiallyChecked and not self.hascheckedchild():
            self.setCheckState(Qt.Unchecked)
            if self.parent() is not None:
                self.parent().uncheckancestors()

    def hascheckedchild(self):
        foundone = False
        numrows = self.rowCount()
        numcols = self.columnCount()
        r = 0
        while not foundone and r < numrows:
            colnum = 0
            while not foundone and colnum < numcols:
                child = self.child(r, colnum)
                if child is not None:
                    foundone = child.checkState() in [Qt.Checked, Qt.PartiallyChecked]
                colnum += 1
            r += 1
        return foundone


class MovementListItem(QStandardItem):

    def __init__(self, pathtxt="", nodetxt="", nodeID=-1, treeit=None, serializedlistitem=None):
        super().__init__()
        self.nodeID = nodeID
        if serializedlistitem:
            self.setEditable(serializedlistitem['editable'])
            self.setText(serializedlistitem['text'])
            self.setData(serializedlistitem['nodedisplayrole'], Qt.UserRole+udr.nodedisplayrole)
            self.setData(serializedlistitem['timestamprole'], Qt.UserRole+udr.timestamprole)
            self.setCheckable(serializedlistitem['checkable'])
            self.setData(serializedlistitem['selectedrole'], Qt.UserRole+udr.selectedrole)
        else:
            self.setEditable(False)
            self.setText(pathtxt)
            self.setData(nodetxt, Qt.UserRole+udr.nodedisplayrole)
            self.setData(QDateTime.currentDateTimeUtc(), Qt.UserRole+udr.timestamprole)
            self.setCheckable(False)
            self.treeitem = treeit
            if treeit is not None:
                self.treeitem.listitem = self
            self.setData(False, Qt.UserRole+udr.selectedrole)

    def setData(self, value, role=Qt.DisplayRole):
        super().setData(value, role)
        if role == Qt.UserRole + udr.userspecifiedvaluerole and hasattr(self, "treeitem") and self.treeitem is not None:

            if self.treeitem.data(Qt.UserRole+udr.isuserspecifiablerole):
                currentlistdisplay = self.data(Qt.DisplayRole)
                newlistdisplay = re.sub(" \[.*\]$", "", currentlistdisplay)
                if value != "":
                    newlistdisplay += " [" + value + "]"
                self.setData(newlistdisplay, Qt.DisplayRole)

    def __repr__(self):
        return '<MovementListItem: ' + repr(self.text()) + '>'

    def updateuserspecifiedvalue(self, usv):
        self.setData()

    def unselectpath(self):
        self.treeitem.uncheck()

    def selectpath(self):
        self.treeitem.check(fully=True)


class MovementPathsProxyModel(QSortFilterProxyModel):

    def __init__(self, parent=None, wantselected=None):
        super(MovementPathsProxyModel, self).__init__(parent)
        self.wantselected = wantselected
        self.setSortCaseSensitivity(Qt.CaseInsensitive)

    def filterAcceptsRow(self, source_row, source_parent):
        if self.wantselected is None:
            source_index = self.sourceModel().index(source_row, 0, source_parent)
            text = self.sourceModel().index(source_row, 0, source_parent).data()
            return True
        else:
            source_index = self.sourceModel().index(source_row, 0, source_parent)
            isselected = source_index.data(role=Qt.UserRole+udr.selectedrole)
            path = source_index.data(role=Qt.UserRole+udr.pathdisplayrole)
            text = self.sourceModel().index(source_row, 0, source_parent).data()
            return self.wantselected == isselected

    def updatesorttype(self, sortbytext=""):
        if "alpha" in sortbytext and "path" in sortbytext:
            self.setSortRole(Qt.DisplayRole)
            self.sort(0)
        elif "alpha" in sortbytext and "node" in sortbytext:
            self.setSortRole(Qt.UserRole+udr.nodedisplayrole)
            self.sort(0)
        elif "tree" in sortbytext:
            self.sort(-1)  # returns to sort order of underlying model
        elif "select" in sortbytext:
            self.setSortRole(Qt.UserRole+udr.timestamprole)
            self.sort(0)


class MovementListModel(QStandardItemModel):

    def __init__(self, treemodel=None):
        super().__init__()
        self.treemodel = treemodel
        if self.treemodel is not None:
            # build this listmodel from the treemodel
            treeparentnode = self.treemodel.invisibleRootItem()
            self.populate(treeparentnode)
            self.treemodel.listmodel = self

    def populate(self, treenode):
        for r in range(treenode.rowCount()):
            treechild = treenode.child(r, 0)
            if treechild is not None:
                pathtext = treechild.data(role=Qt.UserRole+udr.pathdisplayrole)
                nodetext = treechild.data(Qt.DisplayRole)
                nodeID = treechild.nodeID
                listitem = MovementListItem(pathtxt=pathtext, nodetxt=nodetext, nodeID=nodeID, treeit=treechild)  # also sets treeitem's listitem
                self.appendRow(listitem)
                self.populate(treechild)

    def setTreemodel(self, treemod):
        self.treemodel = treemod


class MovementTreeModel(QStandardItemModel):

    def __init__(self, serializedmvmttree=None, optionstree=defaultMvmtTree, **kwargs):
        super().__init__(**kwargs)
        self._listmodel = None  # MovementListModel(self)
        self.optionstree = optionstree
        self.checked = []
        self.setColumnCount(2)
        self.itemChanged.connect(self.updateCheckState)
        self.dataChanged.connect(self.updaterelateddata)
        

        if serializedmvmttree is not None:
            self.serializedmvmttree = serializedmvmttree
            rootnode = self.invisibleRootItem()
            self.populate(rootnode)
            makelistmodel = self.listmodel  # TODO KV   what is this? necessary?
            userspecifiedvalues = self.backwardcompatibility()
            self.setvaluesfromserializedtree(rootnode, userspecifiedvalues)


    def get_checked_from_serialized_tree(self):
        checked = []
        for k in list(self.serializedmvmttree.checkstates):
            if self.serializedmvmttree.checkstates[k] == Qt.Checked:
                checked.append(k)
        return checked
    
    def update_currently_checked(self, treenode):
        if treenode is not None:
            for r in range(treenode.rowCount()):
                treechild = treenode.child(r, 0)
                
                if treechild is not None:
                    pathtext = treechild.data(Qt.UserRole + udr.pathdisplayrole)
                    if pathtext in self.serializedmvmttree.checkstates:
                        if self.serializedmvmttree.checkstates[pathtext] == Qt.Checked:
                            self.checked.append(pathtext)

                    self.update_currently_checked(treechild)

    # Compare what was serialized with what the current tree actually shows
    # Also updates the list
    def compare_checked_lists(self, verbose=False):
        differences = []
        serialized = self.get_checked_from_serialized_tree()
        self.checked = []
        self.update_currently_checked(self.invisibleRootItem())
        for item in serialized:
            if item not in self.checked:
                differences.append(item)
        if verbose:
            print("   Serialized mvmt:" + str(len(serialized)) + "; Listed mvmt:" + str(len(self.checked)))
        # if (len(serialized) != len(self.checked)):
        #     for i in serialized:
        #         print (i)
        #     print("\n")
        #     for i in self.checked:
        #         print(i)
        return differences
    
    def get_usv(self):
        if hasattr(self.serializedmvmttree, 'userspecifiedvalues'):
            return self.serializedmvmttree.userspecifiedvalues
        else:
            return {}

                
    # TODO gz - update
    def backwardcompatibility(self):
        hadtoaddusv = False
        userspecifiedvalues = {}
        if hasattr(self.serializedmvmttree, 'userspecifiedvalues'):
            userspecifiedvalues = self.serializedmvmttree.userspecifiedvalues
        else:
            hadtoaddusv = True

        dicts = self.serializedmvmttree.checkstates, self.serializedmvmttree.addedinfos  # self.numvals, self.stringvals,

        # 20230707: "trill" is now suboption of "repetition"; previously they were at the same level
        old_trill_path = "Movement characteristics"+delimiter+"Trill"
        for stored_dict in dicts:
            if (old_trill_path in stored_dict):
                # If old Trill / Trilled was selected, the new Trilled is selected and anything for single/repeated is gone.
                if (stored_dict[old_trill_path+delimiter+"Trilled"] == Qt.Checked):
                    stored_dict["Movement characteristics"+delimiter+"Repetition"] = Qt.Unchecked
                    stored_dict["Movement characteristics"+delimiter+"Repetition"+delimiter+"Trilled"] = Qt.Checked
                    stored_dict.pop(old_trill_path + delimiter + "Trilled")
                # If old Trill / Not trilled was selected, the new Trilled is not selected and anything for single/repeated stays.
                else:
                    stored_dict["Movement characteristics"+delimiter+"Repetition"+delimiter+"Trilled"] = Qt.Unchecked
                    stored_dict.pop(old_trill_path + delimiter + "Not trilled")
                stored_dict.pop(old_trill_path)


        for stored_dict in dicts:
            pairstoadd = {}
            keystoremove = []
            for k in stored_dict.keys():

                # 1. "H1 and H2 move in different directions" (under either axis driectin or plane, in perceptual shape)
                #   --> "H1 and H2 move in opposite directions"
                # 2. Then later... "H1 and H2 move in opposite directions" (under axis direction only)
                #   --> "H1 and H2 move toward each other" (along with an independent addition of "... away ...")
                # 3. 20230523: Under "Movement type>Perceptual Shape>Shape" and "Movement type>Joint-specific movements"
                #   ... "None of these" --> "Other" (user-specifiable)
                if "H1 and H2 move in different directions" in k:
                    if "Axis direction" in k:
                        pairstoadd[k.replace("in different directions", "toward each other")] = stored_dict[k]
                        keystoremove.append(k)
                    elif "Place" in k:
                        pairstoadd[k.replace("different", "opposite")] = stored_dict[k]
                        keystoremove.append(k)                
                elif "H1 and H2 move in opposite directions" in k and "Axis direction" in k:
                    pairstoadd[k.replace("in opposite directions", "toward each other")] = stored_dict[k]
                    keystoremove.append(k)
                elif "None of these" in k and ("Perceptual shape" in k or "Joint-specific movements" in k):
                    pairstoadd[k.replace("None of these", "Other")] = stored_dict[k]
                    keystoremove.append(k)

                if hadtoaddusv:

                    if k.endswith(specifytotalcycles_str) or k.endswith(numberofreps_str):
                        pairstoadd[k.replace(numberofreps_str, specifytotalcycles_str)] = stored_dict[k]
                        keystoremove.append(k)

                    elif "This number is a minimum" in k:
                        pairstoadd[k.replace(delimiter + "#" + delimiter, delimiter)] = stored_dict[k]
                        keystoremove.append(k)

                    elif (specifytotalcycles_str + delimiter in k or numberofreps_str + delimiter in k):
                        # then we're looking at the item that stores info about the specified number of repetitions
                        newkey = k.replace(numberofreps_str, specifytotalcycles_str)
                        newkey = newkey[:newkey.index(specifytotalcycles_str+delimiter) + len(specifytotalcycles_str)]
                        remainingtext = ""
                        if specifytotalcycles_str in k:
                            remainingtext = k[k.index(specifytotalcycles_str + delimiter) + len(specifytotalcycles_str + delimiter):]
                        elif numberofreps_str in k:
                            remainingtext = k[k.index(specifytotalcycles_str + delimiter) + len(numberofreps_str + delimiter):]

                        if len(remainingtext) > 0 and delimiter not in remainingtext and remainingtext != "#":
                            numcycles = remainingtext
                            userspecifiedvalues[newkey] = numcycles

            for oldkey in keystoremove:
                stored_dict.pop(oldkey)

            for newkey in pairstoadd.keys():
                stored_dict[newkey] = pairstoadd[newkey]

        return userspecifiedvalues

    def uncheck_in_checkstates(self, paths_to_uncheck):
        for path in paths_to_uncheck:
            try:
                self.serializedmvmttree.checkstates[path] = Qt.Unchecked
            except:
                print("Could not uncheck.")

    '''
    Removes from paths_to_add once found
    '''
    def addcheckedvalues(self, treenode, paths_to_add, paths_dict=None):
        if treenode is not None:
            for r in range(treenode.rowCount()):
                treechild = treenode.child(r, 0)

                
                if treechild is not None:
                    pathtext = treechild.data(Qt.UserRole + udr.pathdisplayrole)
                    # try:
                    #     print (pathtext)
                    # except: continue

                    if pathtext in paths_to_add:
                        treechild.setCheckState(Qt.Checked)
                        oldtext = paths_dict[pathtext]
                        paths_to_add.remove(pathtext)

                        if pathtext in self.serializedmvmttree.addedinfos:
                            treechild.addedinfo = copy(self.serializedmvmttree.addedinfos[oldtext])

                        if pathtext in self.get_usv():
                            # this also updates the associated list item as well as its display
                            treechild.setData(self.get_usv()[oldtext], Qt.UserRole + udr.userspecifiedvaluerole)
                            treechild.editablepart().setText(self.get_usv()[oldtext])

                    self.addcheckedvalues(treechild, paths_to_add, paths_dict)

        
    
    def setvaluesfromserializedtree(self, treenode, userspecifiedvalues):
        if treenode is not None:
            for r in range(treenode.rowCount()):
                treechild = treenode.child(r, 0)
                
                if treechild is not None:
                    pathtext = treechild.data(Qt.UserRole + udr.pathdisplayrole)
                    if pathtext in self.serializedmvmttree.checkstates.keys():
                        treechild.setCheckState(self.serializedmvmttree.checkstates[pathtext])

                    if pathtext in self.serializedmvmttree.addedinfos.keys():
                        treechild.addedinfo = copy(self.serializedmvmttree.addedinfos[pathtext])

                    if pathtext in userspecifiedvalues.keys():
                        # this also updates the associated list item as well as its display
                        treechild.setData(userspecifiedvalues[pathtext], Qt.UserRole + udr.userspecifiedvaluerole)
                        if treechild.checkState() == Qt.Checked:
                            treechild.editablepart().setText(userspecifiedvalues[pathtext])

                    self.setvaluesfromserializedtree(treechild, userspecifiedvalues)

    # def tempprinttreemodel(self):
    #     print("treemodel contents...")
    #     # print("location type: ", tm.locationtype)
    #     self.tempprinttmhelper(self.invisibleRootItem())
    #
    # def tempprinttmhelper(self, node, indent=""):
    #     for r in range(node.rowCount()):
    #         ch = node.child(r, 0)
    #         ch_edit = node.child(r, 1)
    #         edit_text = ch_edit.text()
    #         usvrole = node.data(Qt.UserRole+udr.userspecifiedvaluerole)  # this is None
    #         print(indent + ch.text() + " / checked " + str(ch.checkState()) + " / edit_text " + edit_text)  #  + " / usvrole " + usvrole)
    #         self.tempprinttmhelper(ch, indent=indent + " ")

    def findItemsByRoleValues(self, role, possiblevalues, parentnode=None):
        if not isinstance(possiblevalues, list):
            possiblevalues = [possiblevalues]
        if parentnode is None:
            parentnode = self.invisibleRootItem()

        items = []
        numchildren = parentnode.rowCount()
        for i in range(numchildren):
            child = parentnode.child(i, 0)
            roledata = child.data(role)
            matches = [roledata == pv for pv in possiblevalues]
            if True in matches:
                items.append(child)

            subresults = self.findItemsByRoleValues(role, possiblevalues, parentnode=child)
            items.extend(subresults)
        return items

    def updaterelateddata(self, topLeft, bottomRight):
        editableitem = self.itemFromIndex(topLeft)
        if isinstance(editableitem, QStandardItem) and not isinstance(editableitem, MovementTreeItem) and not isinstance(editableitem, MovementListItem):

            proposedtext = editableitem.text()

            treeitem = editableitem.parent().child(editableitem.row(), 0)
            userspecifiability = treeitem.data(Qt.UserRole+udr.isuserspecifiablerole)
            previoustext = treeitem.data(Qt.UserRole+udr.userspecifiedvaluerole)
            updatedtext = self.validateeditedtext(proposedtext, userspecifiability, previoustext)

            editableitem.setText("specify" if updatedtext == "" else updatedtext)
            treeitem.setData("" if updatedtext == "specify" else updatedtext, role=Qt.UserRole+udr.userspecifiedvaluerole) # this auto-updates the list item and its display as well
            if treeitem.data(role=Qt.UserRole+udr.userspecifiedvaluerole) != "" and treeitem.checkState() != Qt.Checked:
                treeitem.check(fully=True)

    def validateeditedtext(self, proposedtext, userspecifiability, previoustext):
        valid = False
        if proposedtext == "specify" or proposedtext == "":
            valid = True
        if userspecifiability == ed_1:
            if proposedtext.isnumeric():
                num = int(proposedtext)
                valid = num >= 1
            elif proposedtext.replace(".", "").isnumeric():
                num = float(proposedtext)
                valid = (num >= 1) and (num % 0.5 == 0)
        elif userspecifiability == ed_2:
            valid = proposedtext.replace(".", "").isnumeric()
        elif userspecifiability == ed_3:
            valid = True

        updatedtext = proposedtext if valid else previoustext

        if updatedtext != proposedtext:
            # revert to previous value
            messagestring = "Invalid text: this field must be "
            if userspecifiability == ed_1:
                messagestring += ">= 1 and a multiple of 0.5"
            elif userspecifiability == ed_2:
                messagestring += "numeric"
            elif userspecifiability == ed_3:
                messagestring += "anything (unrestricted)"
            QMessageBox.critical(None, "Warning", messagestring)

        return updatedtext


    def updateCheckState(self, item):
        if not isinstance(item, MovementTreeItem):
            # eg, if it's just a QStandardItem representing the editable part of a treeitem
            return
        thestate = item.checkState()
        if thestate == Qt.Checked:
            # TODO KV then the user must have checked it,
            #  so make sure to partially-fill ancestors and also look at ME siblings
            item.check(fully=True)
        elif thestate == Qt.PartiallyChecked:
            # TODO KV then the software must have updated it based on some other user action
            # make sure any ME siblings are unchecked
            item.check(fully=False)
        elif thestate == Qt.Unchecked:
            # TODO KV then either...
            # (1) the user unchecked it and we have to uncheck ancestors and look into ME siblings, or
            # (2) it was unchecked as a (previously partially-checked) ancestor of a user-unchecked node, or
            # (3) it was force-unchecked as a result of ME/sibling interaction
            item.uncheck(force=False)
        self.check_dependencies(item)

    def check_dependencies(self, item):
        '''
        Disable directionality if Wiggling/Fluttering is selected
        '''
        if(item.text()=="Wiggling/Fluttering"):
            itemstate = item.checkState()
            uni = self.findItems("Unidirectional", flags = Qt.MatchRecursive)[0]
            bi = self.findItems("Bidirectional", flags = Qt.MatchRecursive)[0]
            dir = self.findItems("Directionality", flags = Qt.MatchRecursive)[0]

            if (itemstate == Qt.Checked): # disable directionality options as mvmt is inherently bidirectional
                dir.setEnabled(False)
                uni.setEnabled(False)
                bi.setEnabled(False)
                uni.setCheckState(Qt.Unchecked)
                bi.setCheckState(Qt.Unchecked)
                dir.setCheckState(Qt.Unchecked)
            elif (itemstate == Qt.Unchecked):
                dir.setEnabled(True)
                uni.setEnabled(True)
                bi.setEnabled(True)


    # def setSubtreeVisibility(self, item, visible):
    #     self.
    #     if not enable:
    #         self.uncheck()
    #     if self.data(Qt.UserRole+udr.isuserspecifiablerole) != fx:
    #         self.editablepart().setEnabled(enable)

    #     for r in range(self.rowCount()):
    #         self.child(r, 0).setEnabledRecursive(enable)


    # enable/disable the given item and its descendants
    def setNodeEnabledRecursive(self, itemtext, enable):
        item = self.findItems(itemtext, flags=Qt.MatchRecursive)[0]
        item.setEnabledRecursive(enable)

    def populate(self, parentnode, structure=MvmtOptionsNode(), pathsofar="", idsequence=[], issubgroup=False, isfinalsubgroup=True, subgroupname=""):
        if structure.children == [] and pathsofar != "":
            # base case (leaf node); don't build any more nodes
            pass
        elif structure.children == [] and pathsofar == "":
            # no parameters; build a tree from the default structure
            # TODO KV define a default structure somewhere (see constant.py)
            self.populate(parentnode, structure=self.optionstree, pathsofar="")
        elif structure.children != []:
            # internal node with substructure
            numentriesatthislevel = len(structure.children)

            for idx, child in enumerate(structure.children):
                label = child.display_name
                # userspecifiability = child.user_specifiability
                # classifier = child.button_type
                ismutuallyexclusive = child.button_type == rb
                iseditable = child.user_specifiability != fx

                if child.display_name == subgroup:

                    # make the tree items in the subgroup and whatever nested structure they have
                    isfinal = False
                    if idx + 1 >= numentriesatthislevel:
                        # if there are no more items at this level
                        isfinal = True
                    self.populate(parentnode, structure=child, pathsofar=pathsofar, idsequence=idsequence, issubgroup=True, isfinalsubgroup=isfinal, 
                                  subgroupname=subgroup+"_"+pathsofar+"_"+(str(child.button_type)))

                else:
                    thistreenode = MovementTreeItem(label, child.id, mutuallyexclusive=ismutuallyexclusive)
                    thistreenode.setData(child.user_specifiability, Qt.UserRole+udr.isuserspecifiablerole)
                    editablepart = QStandardItem()
                    editablepart.setEditable(iseditable)
                    editablepart.setText("specify" if iseditable else "")
                    thistreenode.setData(pathsofar + label, role=Qt.UserRole + udr.pathdisplayrole)
                    thistreenode.setCheckState(Qt.Unchecked) # does this ever need to be checked?
                    if issubgroup:
                        thistreenode.setData(subgroupname, role=Qt.UserRole+udr.subgroupnamerole)
                        if idx + 1 == numentriesatthislevel:
                            thistreenode.setData(True, role=Qt.UserRole + udr.lastingrouprole)
                            thistreenode.setData(isfinalsubgroup, role=Qt.UserRole + udr.finalsubgrouprole)
                    self.populate(thistreenode, structure=child, pathsofar=pathsofar+label+delimiter, idsequence=idsequence)
                    # self.populate(thistreenode, structure=child, pathsofar=pathsofar+label+delimiter, idsequence=idsequence.append(node_id))
                    parentnode.appendRow([thistreenode, editablepart])



    @property
    def listmodel(self):
        if self._listmodel is None:
            self._listmodel = MovementListModel(self)
        return self._listmodel

    @listmodel.setter
    def listmodel(self, listmod):
        self._listmodel = listmod


