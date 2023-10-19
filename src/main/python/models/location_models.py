from copy import copy

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
from serialization_classes import LocationTableSerializable
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

# allow surface, subarea, and/or bone/joint specification?
allow = True
disallow = False

# if surface, subarea, and/or bone/joint specification is allowed, are there any exceptions to which ones?
no_exceptions = ()


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

surfaces_nonhand_default = [anterior, posterior, lateral, medial, top, bottom]
subareas_nonhand_default = [contra_half, upper_half, whole, centre, lower_half, ipsi_half]
subareas_tongue_default = [contra_half, whole, centre, ipsi_half, dorsum, blade, tip]
surfaces_hand_default = [back, friction, radial, ulnar]
surfaces_heelofhand = [back, friction, wrist, radial, ulnar]
subareas_hand_default = [finger_side, wrist_side, radial_side, ulnar_side, centre]
bonejoint_hand_default = [metacarpophalangeal_joint, proximal_bone, proximal_interphalangeal_joint,
                         medial_bone, distal_interphalangeal_joint, distal_bone, tip]

surface_label = "Surface"
subarea_label = "Sub-area"
bonejoint_label = "Bone/joint"



# TODO KV these should go into constant.py... or something similar

# TODO KV: should be able to get rid of "fx" and "subgroup" (and maybe other?) options here...
# TODO KV - check specific exceptions etc for each subarea & surface
# unless we're going to reference the same code (as for movement) for building the tree & list models
# tuple elements are:
#   name, editability, mutual exclusivity, checked/unchecked, hand/nonhand location,
#   allow surfaces?, relevant exceptions to list of surfaces,
#   allow subareas/bone-joints?, relevant exceptions to list of subareas/bone-joints

locn_options_hand = {
    ("Whole hand", fx, rb, u, hb, allow, no_exceptions, disallow, no_exceptions): {
        ("Hand minus fingers", fx, rb, u, hs, allow, no_exceptions, allow, no_exceptions): {},
        ("Heel of hand", fx, rb, u, heel, allow, no_exceptions, allow, no_exceptions): {},
        ("Thumb", fx, rb, u, hb, allow, no_exceptions, allow, (proximal_interphalangeal_joint, medial_bone)): {},
        ("Fingers", fx, rb, u, hb, allow, no_exceptions, allow, no_exceptions): {},
        ("Selected fingers", fx, rb, u, hb, allow, no_exceptions, allow, no_exceptions): {},
        ("Selected fingers and Thumb", fx, rb, u, hb, allow, no_exceptions, allow, (proximal_interphalangeal_joint, medial_bone)): {},
        ("Finger 1", fx, rb, u, hb, allow, no_exceptions, allow, no_exceptions): {},
        ("Finger 2", fx, rb, u, hb, allow, no_exceptions, allow, no_exceptions): {},
        ("Finger 3", fx, rb, u, hb, allow, no_exceptions, allow, no_exceptions): {},
        ("Finger 4", fx, rb, u, hb, allow, no_exceptions, allow, no_exceptions): {},
        ("Between Thumb and Finger 1", fx, rb, u, hb, allow, tuple([s for s in surfaces_hand_default if s not in [back, friction]]), disallow, no_exceptions): {},
        ("Between Fingers 1 and 2", fx, rb, u, hb, allow, tuple([s for s in surfaces_hand_default if s not in [back, friction]]), disallow, no_exceptions): {},
        ("Between Fingers 2 and 3", fx, rb, u, hb, allow, tuple([s for s in surfaces_hand_default if s not in [back, friction]]), disallow, no_exceptions): {},
        ("Between Fingers 3 and 4", fx, rb, u, hb, allow, tuple([s for s in surfaces_hand_default if s not in [back, friction]]), disallow, no_exceptions): {},
    }
}
locn_options_arm = {
    ("Arm (contralateral)", fx, rb, u, nh, allow, (top, bottom), disallow, no_exceptions): {
        ("Upper arm", fx, rb, u, nh, allow, (top, bottom), allow, (contra_half, ipsi_half)): {
            ("Upper arm above biceps", fx, rb, u, nh, allow, (top, bottom), allow, (contra_half, ipsi_half)): {},
            ("Biceps", fx, rb, u, nh, allow, (top, bottom), allow, (contra_half, ipsi_half)): {}
        },
        ("Elbow", fx, rb, u, nh, allow, (top, bottom), allow, (contra_half, ipsi_half)): {},
        ("Forearm", fx, rb, u, nh, allow, (top, bottom), allow, (contra_half, ipsi_half)): {},
        ("Wrist", fx, rb, u, nh, allow, (top, bottom), allow, (contra_half, ipsi_half)): {}
    }
}
locn_options_leg = {
    ("Legs and feet", fx, rb, u, nh, allow, no_exceptions, allow, (contra_half, ipsi_half)): {
        ("Upper leg", fx, rb, u, nh, allow, (top, bottom), allow, (contra_half, ipsi_half)): {
            ("Upper leg - contra", fx, rb, u, nh, allow, (top, bottom), allow, no_exceptions): {},
            ("Upper leg - ipsi", fx, rb, u, nh, allow, (top, bottom), allow, no_exceptions): {}
        },
        ("Knee", fx, rb, u, nh, allow, (top, bottom), allow, (contra_half, ipsi_half)): {
            ("Knee - contra", fx, rb, u, nh, allow, (top, bottom), allow, no_exceptions): {},
            ("Knee - ipsi", fx, rb, u, nh, allow, (top, bottom), allow, no_exceptions): {}
        },
        ("Lower leg", fx, rb, u, nh, allow, (top, bottom), allow, (contra_half, ipsi_half)): {
            ("Lower leg - contra", fx, rb, u, nh, allow, (top, bottom), allow, no_exceptions): {},
            ("Lower leg - ipsi", fx, rb, u, nh, allow, (top, bottom), allow, no_exceptions): {}
        },
        ("Ankle", fx, rb, u, nh, allow, (top, bottom), allow, (contra_half, ipsi_half)): {
            ("Ankle - contra", fx, rb, u, nh, allow, (top, bottom), allow, no_exceptions): {},
            ("Ankle - ipsi", fx, rb, u, nh, allow, (top, bottom), allow, no_exceptions): {}
        },
        ("Foot", fx, rb, u, nh, allow, no_exceptions, allow, (contra_half, ipsi_half)): {
            ("Foot - contra", fx, rb, u, nh, allow, no_exceptions, allow, (upper_half, lower_half)): {},
            ("Foot - ipsi", fx, rb, u, nh, allow, no_exceptions, allow, (upper_half, lower_half)): {}
        }
    }
}
locn_options_body = {
    ("Head", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {
        ("Back of head", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {},
        ("Top of head", fx, rb, u, nh, disallow, no_exceptions, allow, (upper_half, lower_half)): {},
        ("Side of face", fx, rb, u, nh, disallow, no_exceptions, allow, (contra_half, ipsi_half)): {
            ("Side of face - contra", fx, rb, u, nh, disallow, no_exceptions, allow, (contra_half, ipsi_half)): {},
            ("Side of face - ipsi", fx, rb, u, nh, disallow, no_exceptions, allow, (contra_half, ipsi_half)): {}
        },
        ("Face", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {
            ("Temple", fx, rb, u, nh, disallow, no_exceptions, allow, (contra_half, ipsi_half)): {
                ("Temple - contra", fx, rb, u, nh, disallow, no_exceptions, allow, (contra_half, ipsi_half)): {},
                ("Temple - ipsi", fx, rb, u, nh, disallow, no_exceptions, allow, (contra_half, ipsi_half)): {}
            },
            ("Above forehead (hairline)", fx, rb, u, nh, disallow, no_exceptions, allow, (upper_half, lower_half)): {},
            ("Forehead", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {},
            ("Eyebrow", fx, rb, u, nh, disallow, no_exceptions, allow, (contra_half, ipsi_half)): {
                ("Eyebrow - contra", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {},
                ("Eyebrow - ipsi", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {},
                ("Between eyebrows", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {}
            },
            ("Eye", fx, rb, u, nh, disallow, no_exceptions, allow, (contra_half, ipsi_half)): {
                ("Eye - contra", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {},
                ("Eye - ipsi", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {},
                ("Outer corner of eye", fx, rb, u, nh, disallow, no_exceptions, allow, (contra_half, ipsi_half)): {
                    ("Outer corner of eye - contra", fx, rb, u, nh, disallow, no_exceptions, disallow, no_exceptions): {},
                    ("Outer corner of eye - ipsi", fx, rb, u, nh, disallow, no_exceptions, disallow, no_exceptions): {}
                },
                ("Upper eyelid", fx, rb, u, nh, disallow, no_exceptions, allow, (contra_half, ipsi_half)): {
                    ("Upper eyelid - contra", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {},
                    ("Upper eyelid - ipsi", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {}
                },
                ("Lower eyelid", fx, rb, u, nh, disallow, no_exceptions, allow, (contra_half, ipsi_half)): {
                    ("Lower eyelid - contra", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {},
                    ("Lower eyelid - ipsi", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {}
                }
            },
            ("Cheek/nose", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {
                ("Cheek", fx, rb, u, nh, disallow, no_exceptions, allow, (contra_half, ipsi_half)): {
                    ("Cheek - contra", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {},
                    ("Cheek - ipsi", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {}
                },
                ("Cheekbone under eye", fx, rb, u, nh, disallow, no_exceptions, allow, (contra_half, ipsi_half)): {
                    ("Cheekbone under eye - contra", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {},
                    ("Cheekbone under eye - ipsi", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {}
                },
                ("Cheekbone in front of ear", fx, rb, u, nh, disallow, no_exceptions, allow, (contra_half, ipsi_half)): {
                    ("Cheekbone in front of ear - contra", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {},
                    ("Cheekbone in front of ear - ipsi", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {}
                },
                ("Nose", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {
                    ("Nose root", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {},
                    ("Nose ridge", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {},
                    ("Nose tip", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {},  # TODO KV resolve question mark from locations spreadsheet
                    ("Septum", fx, rb, u, nh, disallow, no_exceptions, allow, (contra_half, ipsi_half)): {}
                }
            },
            ("Below nose / philtrum", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {},
            ("Mouth", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {
                ("Lips", fx, rb, u, nh, disallow, no_exceptions, allow, (upper_half, lower_half)): {
                    ("Upper lip", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {},
                    ("Lower lip", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {}
                },
                ("Corner of mouth - contra", fx, rb, u, nh, disallow, no_exceptions, disallow, no_exceptions): {},
                ("Corner of mouth - ipsi", fx, rb, u, nh, disallow, no_exceptions, disallow, no_exceptions): {},
                ("Teeth", fx, rb, u, nh, disallow, no_exceptions, allow, (upper_half, lower_half)): {
                    ("Upper teeth", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {},
                    ("Lower teeth", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {}
                },
                ("Tongue", fx, rb, u, tongue, allow, tuple([s for s in surfaces_nonhand_default if s not in [anterior, top, bottom]]), 
                 allow, no_exceptions): {},  # TODO KV resolve question mark from locations spreadsheet
            },
            ("Ear", fx, rb, u, nh, disallow, no_exceptions, allow, (contra_half, ipsi_half)): {
                ("Ear - contra", fx, rb, u, nh, disallow, no_exceptions, allow, (contra_half, ipsi_half)): {},
                ("Ear - ipsi", fx, rb, u, nh, disallow, no_exceptions, allow, (contra_half, ipsi_half)): {},
                ("Mastoid process", fx, rb, u, nh, disallow, no_exceptions, allow, (contra_half, ipsi_half)): {
                    ("Mastoid process - contra", fx, rb, u, nh, disallow, no_exceptions, allow, (contra_half, ipsi_half)): {},
                    ("Mastoid process - ipsi", fx, rb, u, nh, disallow, no_exceptions, allow, (contra_half, ipsi_half)): {}
                },
                ("Earlobe", fx, rb, u, nh, disallow, no_exceptions, allow, (contra_half, ipsi_half)): {
                    ("Earlobe - contra", fx, rb, u, nh, disallow, no_exceptions, allow, (contra_half, ipsi_half)): {},
                    ("Earlobe - ipsi", fx, rb, u, nh, disallow, no_exceptions, allow, (contra_half, ipsi_half)): {}
                }
            },
            ("Jaw", fx, rb, u, nh, disallow, no_exceptions, allow, (contra_half, ipsi_half)): {
                ("Jaw - contra", fx, rb, u, nh, disallow, no_exceptions, allow, (contra_half, ipsi_half)): {},
                ("Jaw - ipsi", fx, rb, u, nh, disallow, no_exceptions, allow, (contra_half, ipsi_half)): {}
            },
            ("Chin", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {},
            ("Under chin", fx, rb, u, nh, disallow, no_exceptions, disallow, no_exceptions): {}
        },
    },
    ("Neck", fx, rb, u, nh, allow, tuple([s for s in surfaces_nonhand_default if s not in [anterior, posterior]]), allow, no_exceptions): {},  # TODO KV resolve question mark from locations spreadsheet
    ("Torso", fx, rb, u, nh, allow, (medial, top, bottom), allow, no_exceptions): {
        ("Shoulder", fx, rb, u, nh, allow, (medial, bottom), allow, (contra_half, ipsi_half)): {
            ("Shoulder - contra", fx, rb, u, nh, allow, (medial, bottom), allow, no_exceptions): {},
            ("Shoulder - ipsi", fx, rb, u, nh, allow, (medial, bottom), allow, no_exceptions): {}
        },
        ("Armpit", fx, rb, u, nh, disallow, no_exceptions, disallow, no_exceptions): {
            ("Armpit - contra", fx, rb, u, nh, disallow, no_exceptions, disallow, no_exceptions): {},
            ("Armpit - ipsi", fx, rb, u, nh, disallow, no_exceptions, disallow, no_exceptions): {}
        },
        ("Sternum/clavicle area", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {},
        ("Chest/breast area", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {},
        ("Abdominal/waist area", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {},
        ("Pelvis area", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {},
        ("Hip", fx, rb, u, nh, allow, (medial, top, bottom), allow, (contra_half, ipsi_half)): {
            ("Hip - contra", fx, rb, u, nh, allow, (medial, top, bottom), allow, no_exceptions): {},
            ("Hip - ipsi", fx, rb, u, nh, allow, (medial, top, bottom), allow, no_exceptions): {}
        },
        ("Groin", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {},  # TODO KV resolve question mark from locations spreadsheet
        ("Buttocks", fx, rb, u, nh, disallow, no_exceptions, allow, (contra_half, ipsi_half)): {
            ("Buttocks - contra", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {},
            ("Buttocks - ipsi", fx, rb, u, nh, disallow, no_exceptions, allow, no_exceptions): {}
        }
    },
}
locn_options_body.update(locn_options_arm)
locn_options_body.update(locn_options_leg)
locn_options_body.update(locn_options_hand)

# TODO KV: should be able to get rid of "fx" and "subgroup" (and maybe other?) options here...
# unless we're going to reference the same code (as for movement) for building the tree & list models
# tuple elements are:
#   name, editability, mutual exclusivity, checked/unchecked, hand/nonhand location,
#   allow surfaces?, relevant exceptions to list of surfaces,
#   allow subareas/bone-joints?, relevant exceptions to list of subareas/bone-joints
locn_options_purelyspatial = {
    ("Horizontal axis", fx, cb, u, None, None, None, None, None): {
        ("Ipsi", fx, rb, u, None, None, None, None, None): {
            ("Far", fx, rb, u, None, None, None, None, None): {},
            ("Med.", fx, rb, u, None, None, None, None, None): {},
            ("Close", fx, rb, u, None, None, None, None, None): {},
        },
        ("Central", fx, rb, u, None, None, None, None, None): {},
        ("Contra", fx, rb, u, None, None, None, None, None): {
            ("Far", fx, rb, u, None, None, None, None, None): {},
            ("Med.", fx, rb, u, None, None, None, None, None): {},
            ("Close", fx, rb, u, None, None, None, None, None): {},
        },
    },
    ("Vertical axis", fx, cb, u, None, None, None, None, None): {
        ("High", fx, rb, u, None, None, None, None, None): {},
        ("Mid", fx, rb, u, None, None, None, None, None): {},
        ("Low", fx, rb, u, None, None, None, None, None): {},
    },
    ("Sagittal axis", fx, cb, u, None, None, None, None, None): {
        ("In front", fx, rb, u, None, None, None, None, None): {
            ("Far", fx, rb, u, None, None, None, None, None): {},
            ("Med.", fx, rb, u, None, None, None, None, None): {},
            ("Close", fx, rb, u, None, None, None, None, None): {},
        },
        ("Behind", fx, rb, u, None, None, None, None, None): {
            ("Far", fx, rb, u, None, None, None, None, None): {},
            ("Med.", fx, rb, u, None, None, None, None, None): {},
            ("Close", fx, rb, u, None, None, None, None, None): {},
        },
    },
}


class LocationTreeModel(QStandardItemModel):

    def __init__(self, serializedlocntree=None, **kwargs):
        super().__init__(**kwargs)
        self._listmodel = None  # LocationListModel(self)
        self.itemChanged.connect(self.updateCheckState)
        self._locationtype = LocationType()

        if serializedlocntree is not None:
            self.serializedlocntree = serializedlocntree
            self.locationtype = self.serializedlocntree.locationtype
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

    # take info stored in this LocationTreeSerializable and ensure it's reflected in the associated LocationTreeModel
    def setvaluesfromserializedtree(self, treenode):
        if treenode is not None:
            for r in range(treenode.rowCount()):
                treechild = treenode.child(r, 0)
                if treechild is not None:
                    pathtext = treechild.data(Qt.UserRole+udr.pathdisplayrole)
                    if pathtext in self.serializedlocntree.checkstates.keys():
                        treechild.setCheckState(self.serializedlocntree.checkstates[pathtext])
                    if pathtext in self.serializedlocntree.addedinfos.keys():
                        treechild.addedinfo = copy(self.serializedlocntree.addedinfos[pathtext])
                    if pathtext in self.serializedlocntree.detailstables.keys():
                        treechild.detailstable.updatefromserialtable(self.serializedlocntree.detailstables[pathtext])

                    self.setvaluesfromserializedtree(treechild)

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

    def updateCheckState(self, item):
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

    def populate(self, parentnode, structure={}, pathsofar="", issubgroup=False, isfinalsubgroup=True, subgroupname=""):
        if structure == {} and pathsofar != "":
            # base case (leaf node); don't build any more nodes
            pass
        elif structure == {} and pathsofar == "":
            # no parameters; build a tree from the default structure
            # TODO KV define a default structure somewhere (see constant.py)
            if self._locationtype.usesbodylocations():
                self.populate(parentnode, structure=locn_options_body, pathsofar="")
            elif self._locationtype.purelyspatial:
                self.populate(parentnode, structure=locn_options_purelyspatial, pathsofar="")
        elif structure != {}:
            # internal node with substructure
            numentriesatthislevel = len(structure.keys())
            for idx, labelclassifierchecked_tuple in enumerate(structure.keys()):
                label = labelclassifierchecked_tuple[0]
                editable = labelclassifierchecked_tuple[1]
                classifier = labelclassifierchecked_tuple[2]
                checked = labelclassifierchecked_tuple[3]
                ishandloc = labelclassifierchecked_tuple[4]
                allowsurfacespec = labelclassifierchecked_tuple[5]
                surface_exceptions = labelclassifierchecked_tuple[6]
                allowsubareaspec = labelclassifierchecked_tuple[7]  # sub area or bone/joint
                subarea_exceptions = labelclassifierchecked_tuple[8]
                ismutuallyexclusive = classifier == rb
                iseditable = editable == ed
                if label == subgroup:

                    # make the tree items in the subgroup and whatever nested structure they have
                    isfinal = False
                    if idx + 1 >= numentriesatthislevel:
                        # if there are no more items at this level
                        isfinal = True
                    self.populate(parentnode, structure=structure[labelclassifierchecked_tuple], pathsofar=pathsofar, issubgroup=True, isfinalsubgroup=isfinal, subgroupname=subgroup + "_" + pathsofar + "_" + (str(classifier)))

                else:
                    thistreenode = LocationTreeItem(label, ishandloc=ishandloc, allowsurfacespec=allowsurfacespec, allowsubareaspec=allowsubareaspec, mutuallyexclusive=ismutuallyexclusive, surface_exceptions=surface_exceptions, subarea_exceptions=subarea_exceptions)
                    thistreenode.setData(pathsofar + label, role=Qt.UserRole+udr.pathdisplayrole)
                    thistreenode.setEditable(iseditable)
                    thistreenode.setCheckState(Qt.Checked if checked else Qt.Unchecked)
                    if issubgroup:
                        thistreenode.setData(subgroupname, role=Qt.UserRole+udr.subgroupnamerole)
                        if idx + 1 == numentriesatthislevel:
                            thistreenode.setData(True, role=Qt.UserRole+udr.lastingrouprole)
                            thistreenode.setData(isfinalsubgroup, role=Qt.UserRole+udr.finalsubgrouprole)
                    self.populate(thistreenode, structure=structure[labelclassifierchecked_tuple], pathsofar=pathsofar + label + delimiter)
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

    def __init__(self, bodyparttype, serializedlocntree=None, **kwargs):
        self.bodyparttype = bodyparttype
        
        super().__init__(serializedlocntree=serializedlocntree, **kwargs)
        if serializedlocntree is not None:
            self.serializedlocntree = serializedlocntree
            self.backwardcompatibility()

    def populate(self, parentnode, structure={}, pathsofar="", issubgroup=False, isfinalsubgroup=True, subgroupname=""):

        if structure == {} and pathsofar != "":
            # base case (leaf node); don't build any more nodes
            pass
        elif structure == {} and pathsofar == "":
            # no parameters; build a tree from the default structure
            # TODO KV define a default structure somewhere (see constant.py)
            if self.bodyparttype == HAND:
                locn_options = locn_options_hand
            elif self.bodyparttype == ARM:
                locn_options = locn_options_arm
            elif self.bodyparttype == LEG:
                locn_options = locn_options_leg
            else:
                locn_options = {}
            super().populate(parentnode, structure=locn_options, pathsofar="")
        elif structure != {}:
            # internal node with substructure
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

    def __init__(self, loctext="", ishandloc=nh, allowsurfacespec=True, allowsubareaspec=True,  # ishandloc used to be only False (==0) / True (==1)
                 serializedtablemodel=None, surface_exceptions=None, subarea_exceptions=None, **kwargs):
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

        if allowsurfacespec is not None and allowsurfacespec:
            self.col_labels[0] = surface_label
            if surface_exceptions is None:
                surface_exceptions = []
            col_texts = surfaces_hand_default if ishandloc in [hs, hb] else surfaces_heelofhand if ishandloc == heel else surfaces_nonhand_default
            col_texts = [t for t in col_texts if t not in surface_exceptions]
            self.col_contents[0] = [[txt, False] for txt in col_texts]

        if allowsubareaspec is not None and allowsubareaspec:
            self.col_labels[1] = bonejoint_label if ishandloc == hb else subarea_label
            if subarea_exceptions is None:
                subarea_exceptions = []
            col_texts = subareas_nonhand_default if ishandloc == nh else (bonejoint_hand_default if ishandloc == hb else subareas_tongue_default if ishandloc == tongue else subareas_hand_default)
            col_texts = [t for t in col_texts if t not in subarea_exceptions]
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

    # TODO KV are all of these true?
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
                 allowsurfacespec=True, allowsubareaspec=True, addedinfo=None,
                 surface_exceptions=None, subarea_exceptions=None, serializedlocntreeitem=None):
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
                allowsurfacespec=allowsurfacespec,
                allowsubareaspec=allowsubareaspec,
                surface_exceptions=surface_exceptions,
                subarea_exceptions=subarea_exceptions
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

    def check(self, fully=True):
        self.setCheckState(Qt.Checked if fully else Qt.PartiallyChecked)
        self.listitem.setData(fully, Qt.UserRole + udr.selectedrole)
        if fully:
            self.setData(QDateTime.currentDateTimeUtc(), Qt.UserRole + udr.timestamprole)
            self.listitem.setData(QDateTime.currentDateTimeUtc(), Qt.UserRole + udr.timestamprole)
        self.checkancestors()

        # gather siblings in order to deal with mutual exclusivity (radio buttons)
        siblings = self.collectsiblings()

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

