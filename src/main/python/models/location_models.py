from copy import copy, deepcopy

from PyQt5.QtCore import (
    Qt,
    QSortFilterProxyModel,
    QDateTime,
    QAbstractTableModel
)

from PyQt5.Qt import (
    QStandardItem,
    QStandardItemModel
)
import logging

from lexicon.module_classes import LocationType, userdefinedroles as udr, delimiter, AddedInfo
from serialization_classes import LocationTreeSerializable, LocationTableSerializable
from constant import HAND, ARM, LEG


# radio button vs checkbox
rb = "radio button"  # ie mutually exclusive in group / at this level
cb = "checkbox"  # ie not mutually exlusive

# editable vs fixed
ed = "editable"
fx = "fixed"  # ie not editable

# in subgroup?
subgroup = "subgroup"

# checked vs unchecked
c = True  # checked
u = False  # unchecked

# TODO KV figure out a better way to assign what goes in the
#  title and content of each column in the details table
# location type (and types of surfaces, subareas, bones/joints, etc) is either nonhand or hand
hb = "hand - bone/joint type"  # "hand"
hs = "hand - subarea type"
nh = "nonhand"
tongue = "tongue"
heel = "heel of hand"

anterior = "Anterior"
posterior = "Posterior"
lateral = "Lateral"
medial = "Medial"
top = "Top"
bottom = "Bottom"
contra_half = "Contra half"
upper_half = "Upper half"
whole = "Whole"
centre = "Centre"
lower_half = "Lower half"
ipsi_half = "Ipsi half"
ipsi_side = "Ipsi side"
contra_side = "Contra side"
front_half = "Front half"
back_half = "Back half"
back = "Back"
friction = "Friction"
radial = "Radial"
ulnar = "Ulnar"
wrist = "Wrist"
finger_side = "Finger side"
wrist_side = "Wrist side"
radial_side = "Radial side"
ulnar_side = "Ulnar side"
centre = "Centre"
metacarpophalangeal_joint = "Metacarpophalangeal joint"
proximal_bone = "Proximal bone"
proximal_interphalangeal_joint = "Proximal interphalangeal joint"
medial_bone = "Medial bone"
distal_interphalangeal_joint = "Distal interphalangeal joint"
distal_bone = "Distal bone"
tip = "Tip"
dorsum = "Dorsum"
blade = "Blade"

hand_surfaces = "default hand surfaces" # [back, friction, radial, ulnar]
nonhand_surfaces = "default nonhand surfaces" # [anterior, posterior, lateral, medial, top, bottom]
nonhand_surfaces_2 = "default except top, bottom" # [anterior, posterior, lateral, medial]
heelofhand_surfaces = "default plus wrist" # [back, friction, wrist, radial, ulnar]

tongue_subareas = "default plus dorsum, blade, tip" # [contra_half, whole, centre, ipsi_half, dorsum, blade, tip]
nonhand_subareas =  "default nonhand subareas" # [contra_half, upper_half, whole, centre, lower_half, ipsi_half]
nonhand_subareas_2 = "default minus contrahalf, ipsihalf" # [upper_half, whole, centre, lower_half]
hand_subareas = "default hand subareas" # [finger_side, wrist_side, radial_side, ulnar_side, centre]
hand_bonejoints = "default hand bones / joints" 
# [metacarpophalangeal_joint, proximal_bone, proximal_interphalangeal_joint, medial_bone, distal_interphalangeal_joint, distal_bone, tip]

surface_label = "Surface"
subarea_label = "Sub-area"
bonejoint_label = "Bone/joint"

surface_lists = {
    hand_surfaces: [back, friction, radial, ulnar],
    nonhand_surfaces: [anterior, posterior, lateral, medial, top, bottom],
    nonhand_surfaces_2: [anterior, posterior, lateral, medial],
    heelofhand_surfaces: [back, friction, wrist, radial, ulnar]
}

subarea_lists = {
    tongue_subareas: [contra_half, whole, centre, ipsi_half, dorsum, blade, tip],
    nonhand_subareas: [contra_half, upper_half, whole, centre, lower_half, ipsi_half],
    nonhand_subareas_2: [upper_half, whole, centre, lower_half],
    hand_subareas: [finger_side, wrist_side, radial_side, ulnar_side, centre],
    hand_bonejoints: [metacarpophalangeal_joint, proximal_bone, proximal_interphalangeal_joint, medial_bone, distal_interphalangeal_joint, distal_bone, tip]
}


class LocnOptionsNode:
    # if more params are needed, use self.options
    # TODO - gz i imagine that if the user needs to modify the display_name, self.options can be used

    def __init__(self, display_name="treeroot", user_specifiability=None, button_type=None, 
                 location=None, surfaces=None, subareas=None, options=None, tooltip=None, children=None, id=-1):
        self.display_name = display_name # specify if subgroup
        self.user_specifiability = user_specifiability # ed_1, ed_2, ed_3, fx
        self.button_type = button_type # rb, cb, or subgroup count
        self.location = location # nh, hs, or hb
        self._surfaces = surfaces
        self._subareas = subareas
        self.tooltip = tooltip
        self.options = options
        self.children = []
        if children is not None:
            for child in children:
                self.insert_child(child)
        self.id = id

    @property
    def surfaces(self):
        if isinstance(self._surfaces, str):
            return surface_lists[self._surfaces]
        else:
            return self._surfaces

    @property
    def subareas(self):
        if isinstance(self._subareas, str):
            return subarea_lists[self._subareas]
        else:
            return self._subareas

    def __repr__(self):
        repr = str(self.id) + ": " + self.display_name + '\n'
        # repr = repr + "\n                    surfaces: " + str(self.surfaces) 
        # repr = repr + "\n                   subareas: " + str(self.subareas)
        return repr

    def assign_ids(self, current_id):
        # logging.warn(self)
        for child in self.children:
            current_id = current_id + 1
            child.id = current_id
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

    def insert_child(self, node):
        self.children.append(node)

# TODO KV these should go into constant.py... or something similar
locn_options_hand = LocnOptionsNode("Whole hand", fx, rb, hs, hand_surfaces, hand_subareas, children=[
    LocnOptionsNode("Hand minus fingers", fx, rb, hs, hand_surfaces, hand_subareas),
    LocnOptionsNode("Heel of hand", fx, rb, hs, heelofhand_surfaces, hand_subareas),
    LocnOptionsNode("Fingers and thumb", fx, rb, hb, hand_surfaces, hand_bonejoints, children=[
        LocnOptionsNode("Thumb", fx, rb, hb, hand_surfaces, [metacarpophalangeal_joint, proximal_bone, distal_interphalangeal_joint, distal_bone, tip]),
        LocnOptionsNode("Fingers", fx, rb, hb, hand_surfaces, hand_bonejoints, children=[
            LocnOptionsNode("Finger 1", fx, rb, hb, hand_surfaces, hand_bonejoints),
            LocnOptionsNode("Finger 2", fx, rb, hb, hand_surfaces, hand_bonejoints),
            LocnOptionsNode("Finger 3", fx, rb, hb, hand_surfaces, hand_bonejoints),
            LocnOptionsNode("Finger 4", fx, rb, hb, hand_surfaces, hand_bonejoints),
        ]),
        LocnOptionsNode("Between fingers", fx, rb, hb, hand_surfaces, [proximal_bone, proximal_interphalangeal_joint, medial_bone, distal_interphalangeal_joint, distal_bone], children=[
            LocnOptionsNode("Between Thumb and Finger 1", fx, rb, hb, hand_surfaces, [proximal_bone, proximal_interphalangeal_joint, medial_bone, distal_interphalangeal_joint, distal_bone], None),
            LocnOptionsNode("Between Fingers 1 and 2", fx, rb, hb, hand_surfaces, [proximal_bone, proximal_interphalangeal_joint, medial_bone, distal_interphalangeal_joint, distal_bone], None),
            LocnOptionsNode("Between Fingers 2 and 3", fx, rb, hb, hand_surfaces, [proximal_bone, proximal_interphalangeal_joint, medial_bone, distal_interphalangeal_joint, distal_bone], None),
            LocnOptionsNode("Between Fingers 3 and 4", fx, rb, hb, hand_surfaces, [proximal_bone, proximal_interphalangeal_joint, medial_bone, distal_interphalangeal_joint, distal_bone], None),
        ]),
        LocnOptionsNode("Selected fingers and thumb", fx, rb, hb, hand_surfaces, [metacarpophalangeal_joint, proximal_bone, distal_interphalangeal_joint, distal_bone, tip], children=[
            LocnOptionsNode("Selected fingers", fx, rb, hb, hand_surfaces, hand_bonejoints),
        ])
    ])
])


locn_options_arm = LocnOptionsNode("Arm", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas, children=[
    LocnOptionsNode("Arm - contra", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas),
    LocnOptionsNode("Arm - ipsi", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas),
    LocnOptionsNode("Upper arm", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas, children=[
        LocnOptionsNode("Upper arm - contra", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas),
        LocnOptionsNode("Upper arm - ipsi", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas),
        LocnOptionsNode("Upper arm above biceps", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas, children=[
            LocnOptionsNode("Upper arm above biceps - contra", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas),
            LocnOptionsNode("Upper arm above biceps - ipsi", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas),
        ]),
        LocnOptionsNode("Biceps", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas, children=[
            LocnOptionsNode("Biceps - contra", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas),
            LocnOptionsNode("Biceps - ipsi", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas)
        ]),
    ]),
    LocnOptionsNode("Elbow", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas, children=[
        LocnOptionsNode("Elbow - contra", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas),
        LocnOptionsNode("Elbow - ipsi", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas),
    ]),
    LocnOptionsNode("Forearm", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas, children=[
        LocnOptionsNode("Forearm - contra", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas),
        LocnOptionsNode("Forearm - ipsi", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas),
    ]),
    LocnOptionsNode("Wrist", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas, children=[
        LocnOptionsNode("Wrist - contra", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas),
        LocnOptionsNode("Wrist - ipsi", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas)
    ]),
])


locn_options_leg = LocnOptionsNode("Leg and foot", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas, children=[
    LocnOptionsNode("Leg and foot - contra", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas),
    LocnOptionsNode("Leg and foot - ipsi", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas),
    LocnOptionsNode("Upper leg", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas, children=[
        LocnOptionsNode("Upper leg - contra", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas),
        LocnOptionsNode("Upper leg - ipsi", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas)
    ]),
    LocnOptionsNode("Knee", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas, children=[
        LocnOptionsNode("Knee - contra", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas),
        LocnOptionsNode("Knee - ipsi", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas)
    ]),
    LocnOptionsNode("Lower leg", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas, children=[
        LocnOptionsNode("Lower leg - contra", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas),
        LocnOptionsNode("Lower leg - ipsi", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas)
    ]),
    LocnOptionsNode("Ankle", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas, children=[
        LocnOptionsNode("Ankle - contra", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas),
        LocnOptionsNode("Ankle - ipsi", fx, rb, nh, nonhand_surfaces_2, nonhand_subareas)
    ]),
    LocnOptionsNode("Foot", fx, rb, nh, nonhand_surfaces, nonhand_subareas, children=[
        LocnOptionsNode("Foot - contra", fx, rb, nh, nonhand_surfaces, [contra_half, whole, centre, ipsi_half]),
        LocnOptionsNode("Foot - ipsi", fx, rb, nh, nonhand_surfaces, [contra_half, whole, centre, ipsi_half])
    ])
])


locn_options_body = LocnOptionsNode("body_options_root", children=[
    LocnOptionsNode("Head", fx, rb, nh, None, nonhand_subareas, children=[
        LocnOptionsNode("Back of head", fx, rb, nh, None, nonhand_subareas),
        LocnOptionsNode("Top of head", fx, rb, nh, None, [contra_half, ipsi_half, whole, centre, front_half, back_half]),
        LocnOptionsNode("Side of face", fx, rb, nh, None, nonhand_subareas, children=[
            LocnOptionsNode("Side of face - contra", fx, rb, nh, None, nonhand_subareas),
            LocnOptionsNode("Side of face - ipsi", fx, rb, nh, None, nonhand_subareas)
        ]),
        LocnOptionsNode("Face", fx, rb, nh, None, nonhand_subareas, children=[
            LocnOptionsNode("Forehead region", fx, rb, nh, None, nonhand_subareas, children=[
                LocnOptionsNode("Temple", fx, rb, nh, None, nonhand_subareas, children=[
                    LocnOptionsNode("Temple - contra", fx, rb, nh, None, nonhand_subareas),
                    LocnOptionsNode("Temple - ipsi", fx, rb, nh, None, nonhand_subareas)
                ]),
                LocnOptionsNode("Above forehead (hairline)", fx, rb, nh, None, [contra_half, whole, centre, ipsi_half]),
                LocnOptionsNode("Forehead", fx, rb, nh, None, nonhand_subareas)
            ]),
            LocnOptionsNode("Eye region", fx, rb, nh, None, nonhand_subareas, children=[
                LocnOptionsNode("Eyebrow", fx, rb, nh, None, nonhand_subareas, children=[
                    LocnOptionsNode("Eyebrow - contra", fx, rb, nh, None, nonhand_subareas),
                    LocnOptionsNode("Eyebrow - ipsi", fx, rb, nh, None, nonhand_subareas),
                    LocnOptionsNode("Between eyebrows", fx, rb, nh, None, nonhand_subareas)
                ]),
                LocnOptionsNode("Eye", fx, rb, nh, None, nonhand_subareas, children=[
                    LocnOptionsNode("Eye - contra", fx, rb, nh, None, nonhand_subareas),
                    LocnOptionsNode("Eye - ipsi", fx, rb, nh, None, nonhand_subareas),
                    LocnOptionsNode("Outer corner of eye", fx, rb, nh, None, nonhand_subareas, children=[
                        LocnOptionsNode("Outer corner of eye - contra", fx, rb, nh, None, None),
                        LocnOptionsNode("Outer corner of eye - ipsi", fx, rb, nh, None, None)
                    ]),
                    LocnOptionsNode("Eyelid", fx, rb, nh, None, nonhand_subareas, children=[
                        LocnOptionsNode("Upper eyelid", fx, rb, nh, None, nonhand_subareas, children=[
                            LocnOptionsNode("Upper eyelid - contra", fx, rb, nh, None, nonhand_subareas),
                            LocnOptionsNode("Upper eyelid - ipsi", fx, rb, nh, None, nonhand_subareas)
                        ]),
                        LocnOptionsNode("Lower eyelid", fx, rb, nh, None, nonhand_subareas, children=[
                            LocnOptionsNode("Lower eyelid - contra", fx, rb, nh, None, nonhand_subareas),
                            LocnOptionsNode("Lower eyelid - ipsi", fx, rb, nh, None, nonhand_subareas)
                        ])
                    ])
                ])
            ]),
            LocnOptionsNode("Cheek/nose", fx, rb, nh, None, nonhand_subareas, children=[
                LocnOptionsNode("Cheek", fx, rb, nh, None, nonhand_subareas, children=[
                    LocnOptionsNode("Cheek - contra", fx, rb, nh, None, nonhand_subareas),
                    LocnOptionsNode("Cheek - ipsi", fx, rb, nh, None, nonhand_subareas)
                ]),
                LocnOptionsNode("Cheekbone under eye", fx, rb, nh, None, nonhand_subareas, children=[
                    LocnOptionsNode("Cheekbone under eye - contra", fx, rb, nh, None, nonhand_subareas),
                    LocnOptionsNode("Cheekbone under eye - ipsi", fx, rb, nh, None, nonhand_subareas)
                ]),
                LocnOptionsNode("Cheekbone in front of ear", fx, rb, nh, None, [front_half, back_half, whole, centre, upper_half, lower_half], children=[
                    LocnOptionsNode("Cheekbone in front of ear - contra", fx, rb, nh, None, [front_half, back_half, whole, centre, upper_half, lower_half]),
                    LocnOptionsNode("Cheekbone in front of ear - ipsi", fx, rb, nh, None, [front_half, back_half, whole, centre, upper_half, lower_half])
                ]),
                LocnOptionsNode("Nose", fx, rb, nh, None, nonhand_subareas, children=[
                    LocnOptionsNode("Nose root", fx, rb, nh, None, nonhand_subareas),
                    LocnOptionsNode("Nose ridge", fx, rb, nh, None, nonhand_subareas),
                    LocnOptionsNode("Nose tip", fx, rb, nh, None, nonhand_subareas),  
                    LocnOptionsNode("Septum / nostril area", fx, rb, nh, None, [contra_half, whole, centre, ipsi_half], children=[
                        LocnOptionsNode("Septum", fx, rb, nh, None, None),
                        LocnOptionsNode("Nostrils", fx, rb, nh, None, [contra_half, whole, centre, ipsi_half], children=[
                            LocnOptionsNode("Nostril - contra", fx, rb, nh, None, [contra_half, whole, centre, ipsi_half]),
                            LocnOptionsNode("Nostril - ipsi", fx, rb, nh, None, [contra_half, whole, centre, ipsi_half])
                        ])
                    ])
                ])
            ]),
            LocnOptionsNode("Below nose / philtrum", fx, rb, nh, None, nonhand_subareas),
            LocnOptionsNode("Mouth", fx, rb, nh, None, nonhand_subareas, children=[
                LocnOptionsNode("Lips", fx, rb, nh, None, nonhand_subareas, children=[
                    LocnOptionsNode("Upper lip", fx, rb, nh, None, nonhand_subareas),
                    LocnOptionsNode("Lower lip", fx, rb, nh, None, nonhand_subareas)
                ]),
                LocnOptionsNode("Corner of mouth - contra", fx, rb, nh, None, None),
                LocnOptionsNode("Corner of mouth - ipsi", fx, rb, nh, None, None),
                LocnOptionsNode("Teeth", fx, rb, nh, None, nonhand_subareas, children=[
                    LocnOptionsNode("Upper teeth", fx, rb, nh, None, nonhand_subareas),
                    LocnOptionsNode("Lower teeth", fx, rb, nh, None, nonhand_subareas)
                ]),
                LocnOptionsNode("Tongue", fx, rb, nh, [anterior, top, bottom, ipsi_side, contra_side], tongue_subareas), 
            ]),
            LocnOptionsNode("Ear", fx, rb, nh, None, [front_half, back_half, whole, centre, upper_half, lower_half], children=[
                LocnOptionsNode("Ear - contra", fx, rb, nh, None, [front_half, back_half, whole, centre, upper_half, lower_half]),
                LocnOptionsNode("Ear - ipsi", fx, rb, nh, None, [front_half, back_half, whole, centre, upper_half, lower_half]),
                LocnOptionsNode("Behind ear", fx, rb, nh, None, [front_half, back_half, whole, centre, upper_half, lower_half], children=[ # was mastoid process
                    LocnOptionsNode("Behind ear - contra", fx, rb, nh, None, [front_half, back_half, whole, centre, upper_half, lower_half]),
                    LocnOptionsNode("Behind ear - ipsi", fx, rb, nh, None, [front_half, back_half, whole, centre, upper_half, lower_half])
                ]),
                LocnOptionsNode("Earlobe", fx, rb, nh, None, [front_half, back_half, whole, centre, upper_half, lower_half], children=[
                    LocnOptionsNode("Earlobe - contra", fx, rb, nh, None, [front_half, back_half, whole, centre, upper_half, lower_half]),
                    LocnOptionsNode("Earlobe - ipsi", fx, rb, nh, None, [front_half, back_half, whole, centre, upper_half, lower_half])
                ])
            ]),
            LocnOptionsNode("Jaw", fx, rb, nh, None, nonhand_subareas, children=[
                LocnOptionsNode("Jaw - contra", fx, rb, nh, None, nonhand_subareas),
                LocnOptionsNode("Jaw - ipsi", fx, rb, nh, None, nonhand_subareas)
            ]),
            LocnOptionsNode("Chin", fx, rb, nh, None, nonhand_subareas),
            LocnOptionsNode("Under chin", fx, rb, nh, None, [contra_half, whole, centre, ipsi_half])
        ]),
    ]),
    LocnOptionsNode("Neck", fx, rb, nh, [anterior, posterior, ipsi_side, contra_side], nonhand_subareas),  
    LocnOptionsNode("Torso", fx, rb, nh, [anterior, posterior, ipsi_side, contra_side], nonhand_subareas, children=[
        LocnOptionsNode("Upper torso", fx, rb, nh, [anterior, posterior, ipsi_side, contra_side], nonhand_subareas, children=[
            LocnOptionsNode("Shoulder", fx, rb, nh, [anterior, posterior, lateral, top], nonhand_subareas, children=[
                LocnOptionsNode("Shoulder - contra", fx, rb, nh, [anterior, posterior, lateral, top], nonhand_subareas),
                LocnOptionsNode("Shoulder - ipsi", fx, rb, nh, [anterior, posterior, lateral, top], nonhand_subareas)
            ]),
            LocnOptionsNode("Armpit", fx, rb, nh, None, nonhand_subareas, children=[
                LocnOptionsNode("Armpit - contra", fx, rb, nh, None, nonhand_subareas),
                LocnOptionsNode("Armpit - ipsi", fx, rb, nh, None, nonhand_subareas)
            ]),
            LocnOptionsNode("Sternum/clavicle area", fx, rb, nh, None, nonhand_subareas),
            LocnOptionsNode("Chest/breast area", fx, rb, nh, None, nonhand_subareas),
        ]),
        LocnOptionsNode("Lower torso", fx, rb, nh, [anterior, posterior, ipsi_side, contra_side], nonhand_subareas, children=[
            LocnOptionsNode("Pelvis area", fx, rb, nh, None, nonhand_subareas),
            LocnOptionsNode("Hip", fx, rb, nh, [anterior, posterior, lateral], nonhand_subareas, children=[
                LocnOptionsNode("Hip - contra", fx, rb, nh, [anterior, posterior, lateral], nonhand_subareas),
                LocnOptionsNode("Hip - ipsi", fx, rb, nh, [anterior, posterior, lateral], nonhand_subareas)
            ]),
            LocnOptionsNode("Groin", fx, rb, nh, None, nonhand_subareas),  
            LocnOptionsNode("Buttocks", fx, rb, nh, None, nonhand_subareas, children=[
                LocnOptionsNode("Buttocks - contra", fx, rb, nh, None, nonhand_subareas),
                LocnOptionsNode("Buttocks - ipsi", fx, rb, nh, None, nonhand_subareas)
            ])
        ]),
        LocnOptionsNode("Abdominal/waist area", fx, rb, nh, None, nonhand_subareas),
    ])
])

locn_options_body.insert_child(locn_options_arm)
locn_options_body.insert_child(locn_options_leg)
locn_options_body.insert_child(locn_options_hand)

locn_options_body.assign_ids(-1)



# TODO KV: should be able to get rid of "fx" and "subgroup" (and maybe other?) options here...
# unless we're going to reference the same code (as for movement) for building the tree & list models
# attributes are:
#   name, editability, mutual exclusivity, hand/nonhand location,
#   surfaces, subareas/bone-joints, tooltip, children
locn_options_purelyspatial = LocnOptionsNode("purelyspatial_options_root", children=[
    LocnOptionsNode("Default neutral space", fx, cb, tooltip="neutral"),
    LocnOptionsNode("Horizontal axis", fx, cb, tooltip="hor", children=[
        LocnOptionsNode("Ipsi", fx, rb, tooltip="[ipsi]", children=[
            LocnOptionsNode("Far", fx, rb, tooltip="[far]"),
            LocnOptionsNode("Med.", fx, rb, tooltip="[med]"),
            LocnOptionsNode("Close", fx, rb, tooltip="[close]"),
        ]),
        LocnOptionsNode("Central", fx, rb, tooltip="[central]"),
        LocnOptionsNode("Contra", fx, rb, tooltip="[contra]", children=[
            LocnOptionsNode("Far", fx, rb, tooltip="[far]"),
            LocnOptionsNode("Med.", fx, rb, tooltip="[med]"),
            LocnOptionsNode("Close", fx, rb, tooltip="[close]"),
        ]),
    ]),
    LocnOptionsNode("Vertical axis", fx, cb, tooltip="ver", children=[
        LocnOptionsNode("High", fx, rb, tooltip="[high]"),
        LocnOptionsNode("Mid", fx, rb, tooltip="[mid]"),
        LocnOptionsNode("Low", fx, rb, tooltip="[low]"),
    ]),
    LocnOptionsNode("Sagittal axis", fx, cb, "sag", children=[
        LocnOptionsNode("In front", fx, rb, "[front]", children=[
            LocnOptionsNode("Far", fx, rb, tooltip="[far]"),
            LocnOptionsNode("Med.", fx, rb, tooltip="[med]"),
            LocnOptionsNode("Close", fx, rb, tooltip="[close]"),
        ]),
        LocnOptionsNode("Behind", fx, rb, children=[
            LocnOptionsNode("Far", fx, rb, tooltip="[far]"),
            LocnOptionsNode("Med.", fx, rb, tooltip="[med]"),
            LocnOptionsNode("Close", fx, rb, tooltip="[close]"),
        ]),
    ]),
])


class LocationTreeModel(QStandardItemModel):

    def __init__(self, serializedlocntree=None, **kwargs):
        super().__init__(**kwargs)
        self._listmodel = None  # LocationListModel(self)
        self._multiple_selection_allowed = False
        self.itemChanged.connect(lambda item: self.updateCheckState(item))
        self._locationtype = LocationType()
        self.checked=[]

        if serializedlocntree is not None:
            self.serializedlocntree = serializedlocntree
            self.locationtype = self.serializedlocntree.locationtype
            try:
                self._multiple_selection_allowed = serializedlocntree.multiple_selection_allowed
            except:
                # logging.warn("multiple selection attribute not present in serialized location tree")
                self._multiple_selection_allowed = False
            # 
            rootnode = self.invisibleRootItem()
            self.populate(rootnode)
            makelistmodel = self.listmodel  # TODO KV   what is this? necessary?
            self.backwardcompatibility()
            self.setvaluesfromserializedtree(rootnode)

    # ensure that any info stored in this LocationTreeSerializable under older keys (paths),
    # is updated to reflect the newer text for those outdated keys
    def backwardcompatibility(self):
        dicts = [self.serializedlocntree.checkstates, self.serializedlocntree.addedinfos, self.serializedlocntree.detailstables]

        # As of 20230631, entries with "other hand>whole hand" will be moved to "other hand" with surfaces and subareas preserved
        if ("Other hand"+delimiter+"Whole hand" in self.serializedlocntree.checkstates):
            if (self.serializedlocntree.checkstates["Other hand"+delimiter+"Whole hand"] == Qt.Checked):
                for stored_dict in dicts:
                    stored_dict["Whole hand"] = stored_dict["Other hand"+delimiter+"Whole hand"] 
            for stored_dict in dicts:
                stored_dict.pop("Other hand"+delimiter+"Whole hand")
        # As of 20230918, rename "Other hand" back to "Whole hand"
        if ("Other hand" in self.serializedlocntree.checkstates):
            if (self.serializedlocntree.checkstates["Other hand"] == Qt.Checked):
                for stored_dict in dicts:
                    stored_dict["Whole hand"] = stored_dict["Other hand"] 
            for stored_dict in dicts:
                stored_dict.pop("Other hand")

        for stored_dict in dicts:
            pairstoadd = {}
            keystoremove = []
            for k in stored_dict.keys():
                if "H1 is in front of H2" in k:
                    pairstoadd[k.replace("H1 is in front of H2", "H1 is more distal than H2")] = stored_dict[k]
                    keystoremove.append(k)
                if "H1 is behind H2" in k:
                    pairstoadd[k.replace("H1 is behind H2", "H1 is more proximal than H2")] = stored_dict[k]
                    keystoremove.append(k)

            for oldkey in keystoremove:
                stored_dict.pop(oldkey)

            for newkey in pairstoadd.keys():
                stored_dict[newkey] = pairstoadd[newkey]

    def uncheck_paths(self, paths_to_uncheck):
        for path in paths_to_uncheck:
            try:
                self.serializedlocntree.checkstates[path] = Qt.Unchecked
                self.serializedlocntree.addedinfos[path] = Qt.Unchecked
                self.serializedlocntree.detailstables[path] = Qt.Unchecked
            except:
                print("Could not uncheck old path.")
    
    '''
    Removes from paths_to_add once found
    '''
    def addcheckedvalues(self, treenode, paths_to_add, paths_dict=None):
        if treenode is not None:
            for r in range(treenode.rowCount()):
                treechild = treenode.child(r, 0)
                if treechild is not None:
                    pathtext = treechild.data(Qt.UserRole+udr.pathdisplayrole)

                    if pathtext in paths_to_add:
                        treechild.setCheckState(Qt.Checked)
                        oldtext = paths_dict[pathtext]
                        paths_to_add.remove(pathtext)
                        if oldtext in self.serializedlocntree.addedinfos:
                            treechild.addedinfo = copy(self.serializedlocntree.addedinfos[oldtext])
                        if oldtext in self.serializedlocntree.detailstables.keys():
                            treechild.detailstable.updatefromserialtable(self.serializedlocntree.detailstables[oldtext])

                    self.addcheckedvalues(treechild, paths_to_add, paths_dict)

    # take info stored in this LocationTreeSerializable and ensure it's reflected in the associated LocationTreeModel
    def setvaluesfromserializedtree(self, treenode):
        if treenode is not None:
            for r in range(treenode.rowCount()):
                treechild = treenode.child(r, 0)
                if treechild is not None:
                    
                    pathtext = treechild.data(Qt.UserRole+udr.pathdisplayrole)
                    
                    if pathtext in self.serializedlocntree.checkstates.keys():
                        treechild.setCheckState(self.serializedlocntree.checkstates[pathtext])
                        if self.serializedlocntree.checkstates[pathtext] == Qt.Checked:
                            self.checked.append(pathtext)
                    if pathtext in self.serializedlocntree.addedinfos.keys():
                        treechild.addedinfo = copy(self.serializedlocntree.addedinfos[pathtext])
                    if pathtext in self.serializedlocntree.detailstables.keys():
                        treechild.detailstable.updatefromserialtable(self.serializedlocntree.detailstables[pathtext])

                    self.setvaluesfromserializedtree(treechild)
                    

    def get_checked_from_serialized_tree(self):
        checked = []
        if hasattr(self, "serializedlocntree"):
            for k in list(self.serializedlocntree.checkstates):
                if self.serializedlocntree.checkstates[k] == Qt.Checked:
                    checked.append(k)
        return checked

        # Compare what was serialized with what the current tree actually shows
    def compare_checked_lists(self):
        differences = []
        serialized = self.get_checked_from_serialized_tree()
        current = self.checked
        
        for item in serialized:
            if item not in current:
                differences.append(item)
        # print("   Serialized locn:" + str(len(serialized)) + "; Listed locn:" + str(len(self.checked)))
                
        return differences
                




    # def tempprintcheckeditems(self):
    #     treenode = self.invisibleRootItem()
    #     self.tempprinthelper(treenode)
    #
    # def tempprinthelper(self, treenode):
    #     for r in range(treenode.rowCount()):
    #         treechild = treenode.child(r, 0)
    #         if treechild is not None:
    #             pathtext = treechild.data(Qt.UserRole + udr.pathdisplayrole)
    #             checkstate = treechild.checkState()
    #             locntable = treechild.detailstable
    #             addedinfo = treechild.addedinfo
    #
    #             if checkstate == Qt.Checked:
    #                 print(pathtext)
    #                 checkedlocations = []
    #                 for col in locntable.col_contents:
    #                     for it in col:
    #                         if it[1]:
    #                             checkedlocations.append(it[0])
    #                 print("detailed locations selected:", checkedlocations)
    #                 print(addedinfo)
    #         self.tempprinthelper(treechild)

    @property
    def multiple_selection_allowed(self):
        return self._multiple_selection_allowed

    @multiple_selection_allowed.setter
    def multiple_selection_allowed(self, is_allowed):
        self._multiple_selection_allowed = is_allowed
    
    
    def updateCheckState(self, item):
        thestate = item.checkState()
        if thestate == Qt.Checked:
            # TODO KV then the user must have checked it,
            #  so make sure to partially-fill ancestors and also look at ME siblings
            item.check(fully=True, multiple_selection_allowed = self.multiple_selection_allowed)
        elif thestate == Qt.PartiallyChecked:
            # TODO KV then the software must have updated it based on some other user action
            # make sure any ME siblings are unchecked
            item.check(fully=False, multiple_selection_allowed = self.multiple_selection_allowed)
        elif thestate == Qt.Unchecked:
            # TODO KV then either...
            # (1) the user unchecked it and we have to uncheck ancestors and look into ME siblings, or
            # (2) it was unchecked as a (previously partially-checked) ancestor of a user-unchecked node, or
            # (3) it was force-unchecked as a result of ME/sibling interaction
            item.uncheck(force=False)

    # TODO pass in structure (options structure) 
    def populate(self, parentnode, structure=LocnOptionsNode(), pathsofar="", issubgroup=False, isfinalsubgroup=True, subgroupname=""):
        if structure.children == [] and pathsofar != "":
            # base case (leaf node); don't build any more nodes
            pass
        elif structure.children == [] and pathsofar == "":
            # no parameters; build a tree from the default options structure
            if self._locationtype.usesbodylocations():
                self.populate(parentnode, structure=locn_options_body, pathsofar="")
            elif self._locationtype.purelyspatial:
                self.populate(parentnode, structure=locn_options_purelyspatial, pathsofar="")
        elif structure.children != []:
            # internal node with substructure
            numentriesatthislevel = len(structure.children)
            for idx, child in enumerate(structure.children):

                label = child.display_name
                ismutuallyexclusive = child.button_type == rb
                iseditable = child.user_specifiability == ed
                ishandloc = child.location
                surfaces = child.surfaces
                subareas = child.subareas

                if label == subgroup:
                    # make the tree items in the subgroup and whatever nested structure they have
                    isfinal = False
                    if idx + 1 >= numentriesatthislevel:
                        # if there are no more items at this level
                        isfinal = True
                    self.populate(parentnode, structure=child, pathsofar=pathsofar, issubgroup=True, isfinalsubgroup=isfinal, 
                                  subgroupname=subgroup + "_" + pathsofar + "_" + (str(child.button_type)))

                else:
                    thistreenode = LocationTreeItem(label, mutuallyexclusive=ismutuallyexclusive, ishandloc=ishandloc, surfaces=surfaces, subareas=subareas)
                    thistreenode.setData(pathsofar + label, role=Qt.UserRole+udr.pathdisplayrole)
                    thistreenode.setEditable(iseditable)
                    thistreenode.setCheckState(Qt.Unchecked)
                    if issubgroup:
                        thistreenode.setData(subgroupname, role=Qt.UserRole+udr.subgroupnamerole)
                        if idx + 1 == numentriesatthislevel:
                            thistreenode.setData(True, role=Qt.UserRole+udr.lastingrouprole)
                            thistreenode.setData(isfinalsubgroup, role=Qt.UserRole+udr.finalsubgrouprole)
                    self.populate(thistreenode, structure=child, pathsofar=pathsofar + label + delimiter)
                    parentnode.appendRow([thistreenode])

    @property
    def listmodel(self):
        if self._listmodel is None:
            self._listmodel = LocationListModel(self)
        return self._listmodel

    @listmodel.setter
    def listmodel(self, listmod):
        self._listmodel = listmod

    @property
    def locationtype(self):
        return self._locationtype

    @locationtype.setter
    def locationtype(self, locationtype):  # LocationType class
        self._locationtype = locationtype

    def hasselections(self, parentnode=None):
        if parentnode is None:
            rootnode = self.invisibleRootItem()
            return self.hasselections(parentnode=rootnode)
        else:
            for r in range(parentnode.rowCount()):
                treechild = parentnode.child(r, 0)
                if treechild is not None and treechild.checkState() == Qt.Checked:
                    return True
                elif self.hasselections(treechild):
                    return True
            return False

class BodypartTreeModel(LocationTreeModel):

    def __init__(self, bodyparttype, serializedlocntree=None, forrelationmodule=False, **kwargs):
        self.bodyparttype = bodyparttype
        self.forrelationmodule=forrelationmodule
        super().__init__(serializedlocntree=serializedlocntree, **kwargs)
        if serializedlocntree is not None:
            self.serializedlocntree = serializedlocntree
            self.backwardcompatibility()

    def populate(self, parentnode, structure=LocnOptionsNode(), pathsofar="", issubgroup=False, isfinalsubgroup=True, subgroupname=""):
        
        if structure.children == [] and pathsofar != "":
            # base case (leaf node); don't build any more nodes
            pass
        elif structure.children == [] and pathsofar == "":
            # no parameters; build a tree from the default structure
            # TODO KV define a default structure somewhere (see constant.py)
            if self.bodyparttype == HAND:
                locn_options = deepcopy(locn_options_hand)
            elif self.bodyparttype == ARM:
                locn_options = deepcopy(locn_options_arm)
            elif self.bodyparttype == LEG:
                locn_options = deepcopy(locn_options_leg)
            else:
                locn_options = LocnOptionsNode()
            super().populate(parentnode, structure=LocnOptionsNode(children=[locn_options]), pathsofar="")
        elif structure.children != []:
            # internal node with substructure

            if self.forrelationmodule:
                structure.children = [child for child in structure.children 
                                      if "ipsi" not in child.display_name and "contra" not in child.display_name]
            super().populate(parentnode=parentnode, structure=structure, pathsofar=pathsofar)

    def backwardcompatibility(self):
        dicts = [self.serializedlocntree.checkstates, self.serializedlocntree.addedinfos, self.serializedlocntree.detailstables]

        hand_children = ["Hand minus fingers", "Heel of hand", "Thumb", "Fingers", "Selected fingers", "Selected fingers and Thumb",
                         "Finger 1", "Finger 2","Finger 3","Finger 4", 
                         "Between Thumb and Finger 1","Between Fingers 1 and 2", "Between Fingers 2 and 3","Between Fingers 3 and 4"]
        if "Heel of hand" in self.serializedlocntree.checkstates: # check if this is an old version
            for val in hand_children:
                for stored_dict in dicts:
                    stored_dict["Whole hand"+delimiter+val] = stored_dict[val] 
                    stored_dict.pop(val)



class LocationListModel(QStandardItemModel):

    def __init__(self, treemodel=None):
        super().__init__()
        self.treemodel = treemodel
        if self.treemodel is not None:
            # build this listmodel from the treemodel
            treeparentnode = self.treemodel.invisibleRootItem()
            self.populate(treeparentnode)
            self.treemodel.listmodel = self

    def populate(self, treenode):
        # colcount = 1  # TODO KV treenode.columnCount()
        for r in range(treenode.rowCount()):
            # for colnum in range(colcount):
            treechild = treenode.child(r, 0)
            if treechild is not None:
                pathtext = treechild.data(role=Qt.UserRole+udr.pathdisplayrole)
                nodetext = treechild.data(Qt.DisplayRole)
                listitem = LocationListItem(pathtxt=pathtext, nodetxt=nodetext, treeit=treechild)  # also sets treeitem's listitem
                self.appendRow(listitem)
                self.populate(treechild)

    def setTreemodel(self, treemod):
        self.treemodel = treemod


# This class stores specific details about body locations; e.g. surfaces and/or subareas involved
class LocationTableModel(QAbstractTableModel):

    def __init__(self, loctext="", ishandloc=nh, surfaces=None, subareas=None,  # ishandloc used to be only False (==0) / True (==1)
                 serializedtablemodel=None, **kwargs):
        super().__init__(**kwargs)

        # create a brand new (empty) details table
        # if serializedtablemodel is None:  # brand new
        self.col_labels = ["", ""]
        self.col_contents = [[], []]

        if ishandloc is None:
            # this is a location that doesn't have details table content (ie, it's a spatial or an axis-based location)
            return
        elif loctext == "" and (serializedtablemodel is None or serializedtablemodel.isempty()):
            # either no name (can't be a new location) or no serial input (can't be an existing location)
            # so... no location info yet!
            return
        
        if surfaces is not None:
            self.col_labels[0] = surface_label
            col_texts = surfaces
            self.col_contents[0] = [[txt, False] for txt in col_texts]

        if subareas is not None:
            self.col_labels[1] = bonejoint_label if ishandloc == hb else subarea_label
            col_texts = subareas
            self.col_contents[1] = [[txt, False] for txt in col_texts]

        if serializedtablemodel is not None:  # populate with specific info from saved table
            self.updatefromserialtable(serializedtablemodel)

    def updatefromserialtable(self, serializedtablemodel):

        for c_idx, col_label in enumerate(self.col_labels):

            for r_idx, row in enumerate(self.col_contents[c_idx]):
                row_label = row[0]
                serial_value = self.value_at_columnlabel_rowlabel(col_label,
                                                                  row_label,
                                                                  othercolumnlabels=serializedtablemodel.col_labels,
                                                                  othercolumncontents=serializedtablemodel.col_contents
                                                                  )
                if serial_value is not None:
                    self.col_contents[c_idx][r_idx][1] = serial_value

    def value_at_columnlabel_rowlabel(self, columnlabel, rowlabel, othercolumnlabels=None, othercolumncontents=None):

        # by default, assuming we're searching in this ("self") details table
        col_labels = self.col_labels
        col_contents = self.col_contents

        # but... maybe we've got a different one (eg serialized) we need to search
        if othercolumnlabels is not None and othercolumncontents is not None:
            col_labels = othercolumnlabels
            col_contents = othercolumncontents

        if columnlabel in col_labels:
            rows = col_contents[col_labels.index(columnlabel)]
            rowlabels = [dv[0] for dv in rows]
            rowvalues = [dv[1] for dv in rows]
            if rowlabel in rowlabels:
                return rowvalues[rowlabels.index(rowlabel)]

        return None

    # must implement! abstract parent doesn't define this behaviour
    def rowCount(self, parent=None, *args, **kwargs):
        return max([len(col) for col in self.col_contents])

    # must implement! abstract parent doesn't define this behaviour
    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.col_contents)

    # must implement! abstract parent doesn't define this behaviour
    def data(self, index, role=Qt.DisplayRole):
        # TODO KV make sure to deal with other potential roles as well
        if not index.isValid():
            return None
        try:
            if role == Qt.DisplayRole:
                return self.col_contents[index.column()][index.row()][0]
            elif role == Qt.CheckStateRole:
                checked = self.col_contents[index.column()][index.row()][1]
                return Qt.Checked if checked else Qt.Unchecked
        except IndexError:
            return None

    def setData(self, index, value, role=Qt.DisplayRole):
        if not index.isValid():
            return False
        if role == Qt.DisplayRole:
            self.col_contents[index.column()][index.row()][0] = value
        elif role == Qt.CheckStateRole:
            checked = value == Qt.Checked
            self.col_contents[index.column()][index.row()][1] = checked
        return True

    # TODO are all of these correct?
    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable

    # must implement! abstract parent doesn't define this behaviour
    def headerData(self, section, orientation, role=None):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            header = self.col_labels[section]
            return header
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return str(section + 1)

        return None

    def __repr__(self):
        return '<LocationTableModel: ' + repr(self.col_labels) + ' / ' + repr(self.col_contents) + '>'


class LocationListItem(QStandardItem):

    def __init__(self, pathtxt="", nodetxt="", treeit=None, serializedlistitem=None):
        super().__init__()

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

    def __repr__(self):
        return '<LocationListItem: ' + repr(self.text()) + '>'

    # TODO KV no longer used?
    def updatetext(self, txt=""):
        self.setText(txt)

    def unselectpath(self):
        self.treeitem.uncheck()

    def selectpath(self):
        self.treeitem.check(fully=True)


class LocationPathsProxyModel(QSortFilterProxyModel):

    def __init__(self, parent=None, wantselected=None):
        super(LocationPathsProxyModel, self).__init__(parent)
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

class LocationTreeItem(QStandardItem):

    def __init__(self, txt="", listit=None, mutuallyexclusive=False, ishandloc=nh,
                 surfaces=None, subareas=None, addedinfo=None, serializedlocntreeitem=None):
        super().__init__()

        if serializedlocntreeitem:
            self.setEditable(serializedlocntreeitem['editable'])
            self.setText(serializedlocntreeitem['text'])
            self.setCheckable(serializedlocntreeitem['checkable'])
            self.setCheckState(serializedlocntreeitem['checkstate'])
            self.setUserTristate(serializedlocntreeitem['usertristate'])
            self.setData(serializedlocntreeitem['selectedrole'], Qt.UserRole + udr.selectedrole)
            self.setData(serializedlocntreeitem['timestamprole'], Qt.UserRole + udr.timestamprole)
            self.setData(serializedlocntreeitem['mutuallyexclusiverole'], Qt.UserRole + udr.mutuallyexclusiverole)
            self.setData(serializedlocntreeitem['displayrole'], Qt.DisplayRole)
            self._addedinfo = serializedlocntreeitem['addedinfo']
            self._ishandloc = serializedlocntreeitem['ishandloc']
            if isinstance(self._ishandloc, bool):
                # then we need some backwards compatibility action because as of 20230418,
                # ishandloc is a string with 3 possible values... not just a boolean
                self._ishandloc = hb if self._ishandloc else nh
            self.detailstable = LocationTableModel(serializedtablemodel=serializedlocntreeitem['detailstable'])
            self.listitem = LocationListItem(serializedlistitem=serializedlocntreeitem['listitem'])
            self.listitem.treeitem = self
        else:
            self.setEditable(False)
            self.setText(txt)
            self.setCheckable(True)
            self.setCheckState(Qt.Unchecked)
            self.setUserTristate(False)
            self.setData(False, Qt.UserRole + udr.selectedrole)
            self.setData(QDateTime.currentDateTimeUtc(), Qt.UserRole + udr.timestamprole)
            self._addedinfo = addedinfo if addedinfo is not None else AddedInfo()
            self._ishandloc = ishandloc
            self.detailstable = LocationTableModel(
                loctext=txt,
                ishandloc=ishandloc,
                surfaces=surfaces,
                subareas=subareas
            )

            if mutuallyexclusive:
                self.setData(True, Qt.UserRole + udr.mutuallyexclusiverole)
            else:
                self.setData(False, Qt.UserRole + udr.mutuallyexclusiverole)

            self.listitem = listit
            if listit is not None:
                self.listitem.treeitem = self

    def __repr__(self):
        return '<LocationTreeItem: ' + repr(self.text()) + '>'

    def serialize(self):
        return {
            'editable': self.isEditable(),
            'text': self.text(),
            'checkable': self.isCheckable(),
            'checkstate': self.checkState(),
            'usertristate': self.isUserTristate(),
            'timestamprole': self.data(Qt.UserRole + udr.timestamprole),
            'selectedrole': self.data(Qt.UserRole + udr.selectedrole),
            'mutuallyexclusiverole': self.data(Qt.UserRole + udr.mutuallyexclusiverole),
            'ishandloc': self._ishandloc,
            'displayrole': self.data(Qt.DisplayRole),
            'addedinfo': self._addedinfo,
            'detailstable': LocationTableSerializable(self.detailstable)
            # 'listitem': self.listitem.serialize()  TODO KV why not? the constructor uses it...
        }

    @property
    def ishandloc(self):
        return self._ishandloc

    @ishandloc.setter
    def ishandloc(self, ishandloc):
        self._ishandloc = ishandloc

    @property
    def addedinfo(self):
        return self._addedinfo

    @addedinfo.setter
    def addedinfo(self, addedinfo):
        self._addedinfo = addedinfo if addedinfo is not None else AddedInfo()

    def check(self, fully=True, multiple_selection_allowed=False):
        self.setCheckState(Qt.Checked if fully else Qt.PartiallyChecked)
        self.listitem.setData(fully, Qt.UserRole + udr.selectedrole)
        if fully:
            self.setData(QDateTime.currentDateTimeUtc(), Qt.UserRole + udr.timestamprole)
            self.listitem.setData(QDateTime.currentDateTimeUtc(), Qt.UserRole + udr.timestamprole)
        self.checkancestors()

        # gather siblings in order to deal with mutual exclusivity (radio buttons)
        siblings = self.collectsiblings()

        if not multiple_selection_allowed:
            # if this is a radio button item, make sure none of its siblings are checked
            if self.data(Qt.UserRole + udr.mutuallyexclusiverole):
                for sib in siblings:
                    sib.uncheck(force=True)
            else:  # or if it has radio button siblings, make sure they are unchecked
                for me_sibling in [s for s in siblings if s.data(Qt.UserRole + udr.mutuallyexclusiverole)]:
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

        mysubgroup = self.data(Qt.UserRole + udr.subgroupnamerole)
        subgrouporgeneralsiblings = [sib for sib in siblings if
                                     sib.data(Qt.UserRole + udr.subgroupnamerole) == mysubgroup or not sib.data(
                                         Qt.UserRole + udr.subgroupnamerole)]
        subgroupsiblings = [sib for sib in siblings if sib.data(Qt.UserRole + udr.subgroupnamerole) == mysubgroup]

        # if I'm ME and in a subgroup, collect siblings from my subgroup and also those at my level but not in any subgroup
        if self.data(Qt.UserRole + udr.mutuallyexclusiverole) and mysubgroup:
            return subgrouporgeneralsiblings
        # if I'm ME and not in a subgroup, collect all siblings from my level (in subgroups or no)
        elif self.data(Qt.UserRole + udr.mutuallyexclusiverole):
            return siblings
        # if I'm *not* ME but I'm in a subgroup, collect all siblings from my subgroup and also those at my level but not in any subgroup
        elif not self.data(Qt.UserRole + udr.mutuallyexclusiverole) and mysubgroup:
            return subgrouporgeneralsiblings
        # # if I'm *not* ME but I'm in a subgroup, collect all siblings from my subgroup
        # elif not self.data(Qt.UserRole + udr.mutuallyexclusiverole) and mysubgroup:
        #     return subgroupsiblings
        # if I'm *not* ME and not in a subgroup, collect all siblings from my level (in subgroups or no)
        elif not self.data(Qt.UserRole + udr.mutuallyexclusiverole):
            return siblings

    def checkancestors(self):
        if self.checkState() == Qt.Unchecked:
            self.setCheckState(Qt.PartiallyChecked)
        if self.parent() is not None:
            self.parent().checkancestors()

    def uncheck(self, force=False):
        name = self.data()

        self.listitem.setData(False, Qt.UserRole + udr.selectedrole)
        self.setData(False, Qt.UserRole + udr.selectedrole)

        if force:  # force-clear this item and all its descendants - have to start at the bottom?
            # force-uncheck all descendants
            if self.hascheckedchild():
                for r in range(self.rowCount()):
                    for colnum in range(self.columnCount()):
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

        if self.data(Qt.UserRole + udr.mutuallyexclusiverole):
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

