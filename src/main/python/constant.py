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


def filenamefrompath(filepath):
    return os.path.split(filepath)[1]
