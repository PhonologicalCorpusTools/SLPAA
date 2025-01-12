import sys
import os
from fractions import Fraction


from lexicon.location import LocationParameter, Locations
from lexicon.predefined_handshape import (
    HandshapeBase, HandshapeEmpty,
    Handshape1, HandshapeBent1, HandshapeCrooked1,
    Handshape3, HandshapeClawed3, HandshapeContracted3,
    Handshape4, HandshapeBent4, HandshapeClawed4, HandshapeCrooked4, HandshapeSlanted4,
    Handshape5, HandshapeBent5, HandshapeBentMidfinger5, HandshapeClawed5, HandshapeClawedExtended5, HandshapeContracted5, HandshapeRelaxedContracted5, HandshapeCrooked5, HandshapeCrookedSlanted5, HandshapeModified5, HandshapeSlanted5,
    Handshape8, HandshapeCovered8, HandshapeExtended8, HandshapeOpen8,
    HandshapeA, HandshapeClosedAIndex, HandshapeExtendedA, HandshapeAIndex, HandshapeModifiedA, HandshapeOpenA,
    HandshapeB1, HandshapeBentB, HandshapeBentExtendedB, HandshapeClawedExtendedB, HandshapeContractedB, HandshapeExtendedB, HandshapeSlantedExtendedB,
    HandshapeB2,
    HandshapeC, HandshapeClawedC, HandshapeClawedSpreadC, HandshapeContractedC, HandshapeExtendedC, HandshapeFlatC, HandshapeCIndex, HandshapeDoubleCIndex, HandshapeSpreadC,
    HandshapeD, HandshapePartiallyBentD, HandshapeClosedBentD, HandshapeModifiedD,
    HandshapeE, HandshapeOpenE,
    HandshapeF, HandshapeAdductedF, HandshapeClawedF, HandshapeCoveredF, HandshapeFlatF, HandshapeFlatClawedF, HandshapeFlatOpenF, HandshapeOffsetF, HandshapeOpenF, HandshapeSlantedF,
    HandshapeG, HandshapeClosedModifiedG, HandshapeClosedDoubleModifiedG, HandshapeDoubleModifiedG, HandshapeModifiedG,
    HandshapeI, HandshapeBentI, HandshapeBentCombinedIPlus1, HandshapeClawedI, HandshapeCombinedIPlus1, HandshapeCombinedILY, HandshapeCombinedIPlusA, HandshapeFlatCombinedIPlus1,
    HandshapeK, HandshapeExtendedK,
    HandshapeL, HandshapeBentL, HandshapeBentThumbL, HandshapeClawedL, HandshapeClawedExtendedL, HandshapeContractedL, HandshapeDoubleContractedL, HandshapeCrookedL,
    HandshapeM, HandshapeFlatM,
    HandshapeMiddleFinger,
    HandshapeN,
    HandshapeO, HandshapeCoveredO, HandshapeFlatO, HandshapeOIndex, HandshapeModifiedO, HandshapeOffsetO, HandshapeOpenOIndex, HandshapeSpreadOpenO,
    HandshapeR, HandshapeBentR, HandshapeExtendedR,
    HandshapeS,
    HandshapeT, HandshapeCoveredT,
    HandshapeU, HandshapeBentU, HandshapeBentExtendedU, HandshapeClawedU, HandshapeContractedU, HandshapeContractedUIndex, HandshapeCrookedU, HandshapeExtendedU,
    HandshapeV, HandshapeBentV, HandshapeBentExtendedV, HandshapeClawedV, HandshapeClawedExtendedV, HandshapeClosedV, HandshapeCrookedV, HandshapeCrookedExtendedV, HandshapeSlantedV,
    HandshapeW, HandshapeClawedW, HandshapeClosedW, HandshapeCoveredW, HandshapeCrookedW,
    HandshapeX, HandshapeClosedX,
    HandshapeY, HandshapeCombinedYAndMiddle, HandshapeCombinedYAndU
)

# system info
FROZEN = hasattr(sys, 'frozen')
VERSION = (0, 0, 0)  # (major, minor, patch)

# symbols
X_IN_BOX = '\u2327'
NULL = '\u2205'

# styles for transcription
# ESTIMATE_BORDER = '2px dashed black'
# UNCERTAIN_BACKGROUND = 'pink'

DEFAULT_LOCATION_POINTS = [('start', 'red', ''), ('mid', 'blue', 'some notes'), ('end', 'green', '')]

DEFAULT_HEAD_LOCATIONS = {'location1': [[(883, 685), (882, 750), (867, 781), (874, 801), (850, 835), (867, 846),
                                         (887, 836), (1007, 862), (1075, 854), (1110, 851), (1178, 848), (1195, 836),
                                         (1188, 819), (1192, 804), (1174, 765), (1178, 680), (1033, 672)]]}

DEFAULT_WEAK_HAND_LOCATIONS = {'location2': [[(883, 685), (882, 750), (867, 781), (874, 801), (850, 835), (867, 846),
                                              (887, 836), (1007, 862), (1075, 854), (1110, 851), (1178, 848), (1195, 836),
                                              (1188, 819), (1192, 804), (1174, 765), (1178, 680), (1033, 672)]]}

DEFAULT_UPPER_BODY_LOCATIONS = {'abdomen': [[(883, 685), (882, 750), (867, 781), (874, 801), (850, 835), (867, 846),
                                             (887, 836), (1007, 862), (1075, 854), (1110, 851), (1178, 848), (1195, 836),
                                             (1188, 819), (1192, 804), (1174, 765), (1178, 680), (1033, 672)]],
                                'chest': [[(870, 515), (874, 584), (879, 658), (884, 682), (1033, 670), (1179, 675),
                                           (1181, 598), (1188, 578), (1190, 523), (1025, 494)]],
                                'forearm': [[(760, 660), (744, 685), (709, 732), (682, 774), (631, 876), (659, 884),
                                             (678, 905), (680, 917), (695, 896), (743, 846), (773, 816), (806, 781),
                                             (830, 747)],
                                            [(1235, 771), (1267, 814), (1357, 926), (1412, 904), (1375, 831), (1348, 789),
                                             (1322, 751), (1283, 687)]],
                                'leg': [[(841, 998), (836, 1029), (836, 1148), (844, 1282), (836, 1344), (827, 1389),
                                         (864, 1428), (937, 1436), (966, 1346), (992, 1271), (1007, 1189), (1023, 1072)],
                                        [(1023, 1076), (1028, 1168), (1038, 1271), (1043, 1305), (1050, 1364),
                                         (1064, 1409), (1114, 1416), (1172, 1413), (1169, 1307), (1182, 1224),
                                         (1196, 1168), (1209, 1074), (1213, 1039)]],
                                'neck': [[(974, 365), (973, 393),
                                    (964, 394),
                                    (962, 404),
                                    (958, 413),
                                    (954, 422),
                                    (1007, 431),
                                    (1054, 433),
                                    (1081, 433),
                                    (1096, 421),
                                    (1090, 413),
                                    (1094, 407),
                                    (1086, 398),
                                    (1080, 398),
                                    (1078, 374),
                                    (1055, 390),
                                    (1023, 388),
                                    (1001, 381)]],
                          'shoulder': [[(954, 424),
                                        (941, 432),
                                        (871, 451),
                                        (869, 512),
                                        (1023, 493),
                                        (1190, 520),
                                        (1190, 477),
                                        (1111, 450),
                                        (1091, 437),
                                        (1026, 434)]],
                          'sternum': [[(1007, 581), (1000, 661), (1072, 663), (1072, 589)]],
                          'trunk': [[(870, 452),
                                     (874, 581),
                                     (883, 680),
                                     (883, 749),
                                     (864, 781),
                                     (875, 803),
                                     (848, 836),
                                     (867, 843),
                                     (846, 1000),
                                     (836, 1036),
                                     (972, 1052),
                                     (1021, 1070),
                                     (1209, 1039),
                                     (1184, 854),
                                     (1196, 838),
                                     (1188, 819),
                                     (1193, 803),
                                     (1172, 761),
                                     (1180, 683),
                                     (1182, 647),
                                     (1178, 600),
                                     (1186, 577),
                                     (1191, 564),
                                     (1188, 479),
                                     (1028, 458)]],
                          'upper arm': [[(878, 651),
                                         (831, 747),
                                         (795, 707),
                                         (761, 659),
                                         (785, 608),
                                         (800, 558),
                                         (818, 510),
                                         (844, 468),
                                         (870, 450),
                                         (869, 514),
                                         (869, 548),
                                         (874, 577)],
                                        [(1179, 682),
                                         (1217, 738),
                                         (1234, 770),
                                         (1282, 685),
                                         (1270, 658),
                                         (1259, 622),
                                         (1252, 591),
                                         (1240, 555),
                                         (1225, 520),
                                         (1208, 492),
                                         (1191, 477),
                                         (1191, 564),
                                         (1186, 582),
                                         (1179, 600)]]}

TEST_LOCATIONS = {
    'head': LocationParameter(name='Head', image_path='head', location_polygons=DEFAULT_HEAD_LOCATIONS),
    'upper_body': LocationParameter(name='Upper body', image_path='upper_body', location_polygons=DEFAULT_UPPER_BODY_LOCATIONS),
    'weak_hand': LocationParameter(name='Weak hand', image_path='weak_hand', location_polygons=DEFAULT_WEAK_HAND_LOCATIONS)
}

SAMPLE_LOCATIONS = Locations(TEST_LOCATIONS)

PREDEFINED_MAP = {
    'base': HandshapeBase(),
    'empty': HandshapeEmpty(),

    '1': Handshape1(),
    'bent-1': HandshapeBent1(),
    'crooked-1': HandshapeCrooked1(),

    '3': Handshape3(),
    'clawed-3': HandshapeClawed3(),
    'contracted-3': HandshapeContracted3(),

    '4': Handshape4(),
    'bent-4': HandshapeBent4(),
    'clawed-4': HandshapeClawed4(),
    'crooked-4': HandshapeCrooked4(),
    'slanted-4': HandshapeSlanted4(),

    '5': Handshape5(),
    'bent-5': HandshapeBent5(),
    'bent-midfinger-5': HandshapeBentMidfinger5(),
    'clawed-5': HandshapeClawed5(),
    'clawed-extended-5': HandshapeClawedExtended5(),
    'contracted-5': HandshapeContracted5(),
    'relaxed-contracted-5': HandshapeRelaxedContracted5(),
    'crooked-5': HandshapeCrooked5(),
    'crooked-slanted-5': HandshapeCrookedSlanted5(),
    'modified-5': HandshapeModified5(),
    'slanted-5': HandshapeSlanted5(),

    '8': Handshape8(),
    'covered-8': HandshapeCovered8(),
    'extended-8': HandshapeExtended8(),
    'open-8': HandshapeOpen8(),

    'A': HandshapeA(),
    'closed-A-index': HandshapeClosedAIndex(),
    'extended-A': HandshapeExtendedA(),
    'A-index': HandshapeAIndex(),
    'modified-A': HandshapeModifiedA(),
    'open-A': HandshapeOpenA(),

    'B1': HandshapeB1(),
    'bent-B': HandshapeBentB(),
    'bent-extended-B': HandshapeBentExtendedB(),
    'clawed-extended-B': HandshapeClawedExtendedB(),
    'contracted-B': HandshapeContractedB(),
    'extended-B': HandshapeExtendedB(),
    'slanted-extended-B': HandshapeSlantedExtendedB(),

    'B2': HandshapeB2(),

    'C': HandshapeC(),
    'clawed-C': HandshapeClawedC(),
    'clawed-spread-C': HandshapeClawedSpreadC(),
    'contracted-C': HandshapeContractedC(),
    'extended-C': HandshapeExtendedC(),
    'flat-C': HandshapeFlatC(),
    'C-index': HandshapeCIndex(),
    'double-C-index': HandshapeDoubleCIndex(),
    'spread-C': HandshapeSpreadC(),

    'D': HandshapeD(),
    'partially-bent-D': HandshapePartiallyBentD(),
    'closed-bent-D': HandshapeClosedBentD(),
    'modified-D': HandshapeModifiedD(),

    'E': HandshapeE(),
    'open-E': HandshapeOpenE(),

    'F': HandshapeF(),
    'adducted-F': HandshapeAdductedF(),
    'clawed-F': HandshapeClawedF(),
    'covered-F': HandshapeCoveredF(),
    'flat-F': HandshapeFlatF(),
    'flat-clawed-F': HandshapeFlatClawedF(),
    'flat-open-F': HandshapeFlatOpenF(),
    'offset-F': HandshapeOffsetF(),
    'open-F': HandshapeOpenF(),
    'slanted-F': HandshapeSlantedF(),

    'G': HandshapeG(),
    'closed-modified-G': HandshapeClosedModifiedG(),
    'closed-double-modified-G': HandshapeClosedDoubleModifiedG(),
    'double-modified-G': HandshapeDoubleModifiedG(),
    'modified-G': HandshapeModifiedG(),

    'I': HandshapeI(),
    'bent-I': HandshapeBentI(),
    'bent-combined-I+1': HandshapeBentCombinedIPlus1(),
    'clawed-I': HandshapeClawedI(),
    'combined-I+1': HandshapeCombinedIPlus1(),
    'combined-ILY': HandshapeCombinedILY(),
    'combined-I+A': HandshapeCombinedIPlusA(),
    'flat-combined-I+1': HandshapeFlatCombinedIPlus1(),

    'K': HandshapeK(),
    'extended-K': HandshapeExtendedK(),

    'L': HandshapeL(),
    'bent-L': HandshapeBentL(),
    'bent-thumb-L': HandshapeBentThumbL(),
    'clawed-L': HandshapeClawedL(),
    'clawed-extended-L': HandshapeClawedExtendedL(),
    'contracted-L': HandshapeContractedL(),
    'double-contracted-L': HandshapeDoubleContractedL(),
    'crooked-L': HandshapeCrookedL(),

    'M': HandshapeM(),
    'flat-M': HandshapeFlatM(),

    'middle-finger': HandshapeMiddleFinger(),

    'N': HandshapeN(),

    'O': HandshapeO(),
    'covered-O': HandshapeCoveredO(),
    'flat-O': HandshapeFlatO(),
    'O-index': HandshapeOIndex(),
    'modified-O': HandshapeModifiedO(),
    'offset-O': HandshapeOffsetO(),
    'open-O-index': HandshapeOpenOIndex(),
    'spread-open-O': HandshapeSpreadOpenO(),

    'R': HandshapeR(),
    'bent-R': HandshapeBentR(),
    'extended-R': HandshapeExtendedR(),

    'S': HandshapeS(),

    'T': HandshapeT(),
    'covered-T': HandshapeCoveredT(),

    'U': HandshapeU(),
    'bent-U': HandshapeBentU(),
    'bent-extended-U': HandshapeBentExtendedU(),
    'clawed-U': HandshapeClawedU(),
    'contracted-U': HandshapeContractedU(),
    'contracted-U-index': HandshapeContractedUIndex(),
    'crooked-U': HandshapeCrookedU(),
    'extended-U': HandshapeExtendedU(),

    'V': HandshapeV(),
    'bent-V': HandshapeBentV(),
    'bent-extended-V': HandshapeBentExtendedV(),
    'clawed-V': HandshapeClawedV(),
    'clawed-extended-V': HandshapeClawedExtendedV(),
    'closed-V': HandshapeClosedV(),
    'crooked-V': HandshapeCrookedV(),
    'crooked-extended-V': HandshapeCrookedExtendedV(),
    'slanted-V': HandshapeSlantedV(),

    'W': HandshapeW(),
    'clawed-W': HandshapeClawedW(),
    'closed-W': HandshapeClosedW(),
    'covered-W': HandshapeCoveredW(),
    'crooked-W': HandshapeCrookedW(),

    'X': HandshapeX(),
    'closed-X': HandshapeClosedX(),

    'Y': HandshapeY(),
    'combined-Y+middle': HandshapeCombinedYAndMiddle(),
    'combined-Y+U': HandshapeCombinedYAndU(),
}

FRACTION_CHAR = {
    Fraction(1, 4): "¼",
    Fraction(1, 3): "⅓",
    Fraction(1, 2): "½",
    Fraction(2, 3): "⅔",
    Fraction(3, 4): "¾",
}

HAND = "Hand"
ARM = "Arm"
LEG = "Leg"

ARTICULATOR_ABBREVS = {
    HAND: "H",
    ARM: "A",
    LEG: "L"
}

CONTRA = "contra"
IPSI = "ipsi"


# Sign type constants
SIGN_TYPE = {
    "ONE_HAND": "1h",
    "ONE_HAND_MVMT": "1h.moves",
    "ONE_HAND_NO_MVMT": "1h.no mvmt",
    "TWO_HANDS": "2h",
    "TWO_HANDS_SAME_HCONF": "2h.same HCs",
    "TWO_HANDS_DIFF_HCONF": "2h.different HCs",
    "TWO_HANDS_MAINT_CONT": "2h.maintain contact",
    "TWO_HANDS_NO_CONT": "2h.contact not maintained",
    "TWO_HANDS_BISYM": "2h.bilaterally symmetric",
    "TWO_HANDS_NO_BISYM": "2h.not bilaterally symmetric",
    "TWO_HANDS_NO_MVMT": "2h.neither moves",
    "TWO_HANDS_ONE_MVMT": "2h.only 1 moves",
    "TWO_HANDS_BOTH_MVMT": "2h.both move",
    "TWO_HANDS_ONLY_H1": "2h.only 1 moves.H1 moves",
    "TWO_HANDS_ONLY_H2": "2h.only 1 moves.H2 moves",
    "TWO_HANDS_BOTH_MVMT_DIFF": "2h.both move.move differently",
    "TWO_HANDS_BOTH_MVMT_SAME": "2h.both move.move similarly",
    "TWO_HANDS_BOTH_MVMT_SEQ": "2h.both move.move similarly.sequential",
    "TWO_HANDS_BOTH_MVMT_SIMU": "2h.both move.move similarly.simultaneous"
}


class ModuleTypes:
    MOVEMENT = 'movement'
    LOCATION = 'location'
    HANDCONFIG = 'handconfig'
    RELATION = 'relation'
    ORIENTATION = 'orientation'
    NONMANUAL = 'nonmanual'
    SIGNTYPE = 'signtype'

    abbreviations = {
        MOVEMENT: 'Mov',
        LOCATION: 'Loc',
        HANDCONFIG: 'Config',
        RELATION: 'Rel',
        ORIENTATION: 'Ori',
        NONMANUAL: 'NonMan'
    }

    parametertypes = list(abbreviations.keys())
    parametertypes_relationfirst = [RELATION] + [mtype for mtype in parametertypes if mtype != 'relation']


class UserDefinedRoles(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


userdefinedroles = UserDefinedRoles({
    'selectedrole': 0,
        # selectedrole:
        # Used by MovementTreeItem, LocationTreeItem, MovementListItem, LocationListItem to indicate
        # whether they are selected by the user. Not exactly the same as ...Item.checkState() because:
        #   (1) selectedrole only uses True & False whereas checkstate has none/partial/full, and
        #   (2) ListItems don't actually get checked, but we still need to track whether they've been selected
    'pathdisplayrole': 1,
        # pathdisplayrole:
        # Used by LocationTreeModel, LocationListModel, LocationPathsProxyModel (and similar for Movement) to access
        # the full path (node names, separated by delimiters) of the model Item in question,
        # generally for purposes of displaying in the selectd paths list in the Location or Movement dialog
    'mutuallyexclusiverole': 2,
        # mutuallyexclusiverole:
        # Used by MovementTreeItem & LocationTreeItem to identify the item's relationship to its siblings,
        # which also involves its display as a radio button vs a checkbox.
    'nocontrolrole': 3,
        # nocontrolrole:
        # used by MovementTreeItemDelegate when a MovementTreeItem is never a selectable item
        # so text may be displayed, but no checkbox or radiobutton
    'firstingrouprole': 4,
        # firstingrouprole:
        # used by MovementTreeItemDelegate to determine whether the relevant model Item is the first
        # in its subgroup, which affects how it is painted in the movement tree
        # (eg, whether the item will be preceded by a horizontal line)
    'firstsubgrouprole': 5,
        # firstsubgrouprole:
        # Used by MovementTreeItem & LocationTreeItem to identify whether an item that is in a subgroup is
        # also in the *first* subgroup in its section. Such a subgroup will not have a horizontal line drawn before it.
    'subgroupnamerole': 6,
        # subgroupnamerole:
        # Used by MovementTreeItem & LocationTreeItem to identify which items are grouped together. Such
        # subgroups are separated from other siblings by a horizontal line in the tree, and item selection
        # is often (always?) mutually exclusive within the subgroup.
    'nodedisplayrole': 7,
        # nodedisplayrole:
        # Used by MovementListItem & LocationListItem to store just the corresponding treeitem's node name
        # (not the entire path), currently only for sorting listitems by alpha (by lowest node).
    'timestamprole': 8,
        # timestamprole:
        # Used by LocationPathsProxyModel and MovementPathsProxyModel as one option on which to sort selected paths
    'isuserspecifiablerole': 9,
        # isuserspecifiablerole:
        # Used by MovementTreeItem to indicate that this tree item allows the user to specify a particular value.
        # If 0, the corresponding QStandardItem (ie, the "editable part") is marked not editable; the user cannot change its value;
        # If 1, the corresponding QStandardItem is marked editable but must be a number, >= 1, and a multiple of 0.5;
        # If 2, the corrresponding QStandardItem is marked editable but must be a number;
        # If 3, the corrresponding QStandardItem is marked editable with no restrictions.
        # This kind of editable functionality was formerly achieved via a separate (subsidiary) editable MovementTreeItem.
    'userspecifiedvaluerole': 10,
        # userspecifiedvaluerole:
        # Used by MovementTreeItem to store the (string) value for an item that is allowed to be user-specified.

})


# TODO KV - define here or in module_classes? or user-defined in global settings? or maybe even in the module window(s)?
treepathdelimiter = ">"


DEFAULT_LOC_1H = {"Horizontal axis" + treepathdelimiter + "Ipsi": None, 
                "Vertical axis" + treepathdelimiter + "Mid": None,
                "Sagittal axis" + treepathdelimiter + "In front" + treepathdelimiter + "Med.": None}
DEFAULT_LOC_2H = {"Horizontal axis" + treepathdelimiter + "Central": None, 
                "Vertical axis" + treepathdelimiter + "Mid": None,
                "Sagittal axis" + treepathdelimiter + "In front" + treepathdelimiter + "Med.": None}

class TargetTypes:
    SIGNLEVELINFO = "sign level info"
    XSLOT = "xslot"
    SIGNTYPEINFO = "sign type info"
    MOV_REL = "mvmt + reln"
    LOC_REL = "locn + reln"
    EXTENDEDFINGERS  = "extended fingers"

def filenamefrompath(filepath):
    return os.path.split(filepath)[1]


def filenamefrompath(filepath):
    return os.path.split(filepath)[1]