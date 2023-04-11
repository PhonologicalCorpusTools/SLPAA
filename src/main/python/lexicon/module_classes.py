from datetime import datetime

from PyQt5.QtCore import (
    Qt,
)

from gui.hand_configuration import HandConfigurationHand, PREDEFINED_MAP
from lexicon.module_classes2 import AddedInfo, TimingInterval

delimiter = ">"  # TODO KV - should this be user-defined in global settings? or maybe even in the mvmt window?


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
        # TODO KV description
    'mutuallyexclusiverole': 2,
        # mutuallyexclusiverole:
        # Used by MovementTreeItem & LocationTreeItem to identify the item's relationship to its siblings,
        # which also involves its display as a radio button vs a checkbox.
    # 'unusedrole': 3,  # currently unused; can repurpose if needed
        # unusedrole:
        # TODO KV description
    'lastingrouprole': 4,
        # lastingrouprole:
        # TODO KV description
    'finalsubgrouprole': 5,
        # finalsubgrouprole:
        # Used by MovementTreeItem & LocationTreeItem to identify whether an item that is in a subgroup is
        # also in the *last* subgroup in its section. Such a subgroup will not have a horizontal line drawn after it.
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
        # TODO KV description
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


# TODO KV comments
# TODO KV - for parameter modules and x-slots
# common ancestor for (eg) HandshapeModule, MovementModule, etc
class ParameterModule:

    def __init__(self, hands, timingintervals=None, addedinfo=None):
        self._hands = hands
        self._timingintervals = []
        if timingintervals is not None:
            self.timingintervals = timingintervals
        self._addedinfo = addedinfo if addedinfo is not None else AddedInfo()
        self._uniqueid = datetime.timestamp(datetime.now())

    @property
    def addedinfo(self):
        return self._addedinfo

    @addedinfo.setter
    def addedinfo(self, addedinfo):
        # TODO KV - validate?
        self._addedinfo = addedinfo

    @property
    def hands(self):
        return self._hands

    @hands.setter
    def hands(self, hands):
        # TODO KV - validate?
        self._hands = hands

    @property
    def uniqueid(self):
        return self._uniqueid

    @uniqueid.setter
    def uniqueid(self, uniqueid):
        # TODO KV - validate?
        self._uniqueid = uniqueid

    @property
    def timingintervals(self):
        return self._timingintervals

    @timingintervals.setter
    def timingintervals(self, timingintervals):
        # TODO KV - validate?
        self._timingintervals = [t for t in timingintervals]

    def getabbreviation(self):
        return "TODO no abbreviations implemented yet"


# TODO KV comments
# TODO KV - for parameter modules and x-slots
class TargetModule:
    def __init__(self):
        # TODO KV implement
        pass


# TODO KV comments
# TODO KV - for parameter modules and x-slots
class OrientationModule:
    def __init__(self):
        # TODO KV implement
        pass


class MovementModule(ParameterModule):
    def __init__(self, movementtreemodel, hands, timingintervals=None, addedinfo=None, inphase=0):
        self._movementtreemodel = movementtreemodel
        self._inphase = inphase    # TODO KV is "inphase" actually the best name for this attribute?
        super().__init__(hands, timingintervals=timingintervals, addedinfo=addedinfo)

    @property
    def movementtreemodel(self):
        return self._movementtreemodel

    @movementtreemodel.setter
    def movementtreemodel(self, movementtreemodel):
        # TODO KV - validate?
        self._movementtreemodel = movementtreemodel

    @property
    def inphase(self):
        return self._inphase

    @inphase.setter
    def inphase(self, inphase):
        # TODO KV - validate?
        self._inphase = inphase

    def getabbreviation(self):
        # TODO KV these can't be hardcoded like this... fix it!
        abbrevs = {
            "Perceptual shape": "Perceptual",
            "Straight": "Straight",
            # "Interacts with subsequent straight movement": "interacts with subseq. straight mov.",
            "Movement contours cross (e.g. X)": "crosses subseq. mov.",
            "Subsequent movement starts at end of first (e.g. ↘↗)": "ends where subseq. mov starts",
            "Subsequent movement starts in same location as start of first (e.g. ↖↗)": "starts where subseq. mov starts",
            "Subsequent movement ends in same location as end of first (e.g. ↘↙)": "ends where subseq. mov. ends",
            "Arc": "Arc",
            "Circle": "Circle",
            "Zigzag": "Zigzag",
            "Loop (travelling circles)": "Loop",
            "Joint-specific movements": "Joint-specific",
            "Nodding/un-nodding": "Nod/Un-",
            "Nodding": "nod",
            "Un-nodding": "un-nod",
            "Pivoting": "Pivot",
            "Radial": "radial pivot",
            "Ulnar": "ulnar pivot",
            "Twisting": "Twist",
            "Pronation": "pronation",
            "Supination": "supination",
            "Closing/Opening": "Close/Open",
            "Closing": "close",
            "Opening": "open",
            "Pinching/unpinching": "Pinch/Un-",
            "Pinching (Morgan 2017)": "pinch",
            "Unpinching": "unpinch",
            "Flattening/Straightening": "Flatten/Straighten",
            "Flattening/hinging": "flatten",
            "Straightening": "straighten",
            "Hooking/Unhooking": "Hook/Un-",
            "Hooking/clawing": "hook",
            "Unhooking": "unhook",
            "Spreading/Unspreading": "Spread/Un-",
            "Spreading": "spread",
            "Unspreading": "unspread",
            "Rubbing": "Rub",
            "Wiggling/Fluttering": "Wiggle",
            "Up": "up",
            "Down": "down",
            "Distal": "dist",
            "Proximal": "prox",
            "Ipsilateral": "ipsi",
            "Contralateral": "contra",
            "Right": "right",
            "Left": "left",
            "Mid-sagittal": "mid-sag",
            "Clockwise": "clockwise",
            "Counterclockwise": "counter-clockwise",
            "Horizontal": "Hor",
            "Vertical": "Ver",
            "Single": "1x",
            "2": "2x",
            "3": "3x",
            "4": "4x",  # TODO KV automate the abbreviations for integers
            ""
            "Same location": "same loc",
            "Different location": "diff. loc",
            "Trilled": "Trilled",
            "Bidirectional": "Bidirec"
        }
        wordlist = []

        udr = userdefinedroles
        listmodel = self._movementtreemodel.listmodel
        numrows = listmodel.rowCount()
        for rownum in range(numrows):
            item = listmodel.item(rownum)
            text = item.text()
            selected = item.data(Qt.UserRole+udr.selectedrole)
            if selected:
                pathelements = text.split(delimiter)
                # thisentrytext = ""
                # firstonedone = False
                # morethanone = False
                for pathelement in pathelements:
                    if pathelement in abbrevs.keys():  #  and abbrevs[pathelement] not in thisentrytext:
                        wordlist.append(abbrevs[pathelement])
                #         if not firstonedone:
                #             thisentrytext += abbrevs[pathelement]
                #             firstonedone = True
                #         else:
                #             if not morethanone:
                #                 thisentrytext += " (" + abbrevs[pathelement] + ", "
                #                 morethanone = True
                #     if morethanone:  # and thisentrytext.endswith(")"):
                #         thisentrytext += ")"  # = thisentrytext[:-2] + ")"
                # wordlist.append(thisentrytext)

        return "; ".join(wordlist)


# this class stores info about whether an instance of the Location module represents a phonetic/phonological location
class PhonLocations:

    def __init__(self, phonologicalloc=False, majorphonloc=False, minorphonloc=False, phoneticloc=False):
        self._phonologicalloc = phonologicalloc
        self._majorphonloc = majorphonloc
        self._minorphonloc = minorphonloc
        self._phoneticloc = phoneticloc

    @property
    def phonologicalloc(self):
        return self._phonologicalloc

    @phonologicalloc.setter
    def phonologicalloc(self, phonologicalloc):
        # TODO KV - validate?
        self._phonologicalloc = phonologicalloc

    @property
    def majorphonloc(self):
        return self._majorphonloc

    @majorphonloc.setter
    def majorphonloc(self, majorphonloc):
        # TODO KV - validate?
        self._majorphonloc = majorphonloc

    @property
    def minorphonloc(self):
        return self._minorphonloc

    @minorphonloc.setter
    def minorphonloc(self, minorphonloc):
        # TODO KV - validate?
        self._minorphonloc = minorphonloc

    @property
    def phoneticloc(self):
        return self._phoneticloc

    @phoneticloc.setter
    def phoneticloc(self, phoneticloc):
        # TODO KV - validate?
        self._phoneticloc = phoneticloc

    def allfalse(self):
        return not (self._phoneticloc or self._phonologicalloc or self._majorphonloc or self._minorphonloc)


# this class stores info about what kind of location type (body or signing space)
# is used by a particular instance of the Location Module
class LocationType:

    def __init__(self, body=False, signingspace=False, bodyanchored=False, purelyspatial=False, axis=False):  # , **kwargs):
        self._body = body
        self._signingspace = signingspace
        self._bodyanchored = bodyanchored
        self._purelyspatial = purelyspatial
        self._axis = axis

    def __repr__(self):
        repr_str = "nil"
        if self._body:
            repr_str = "body"
        elif self._signingspace:
            repr_str = "signing space"
            if self._bodyanchored:
                repr_str += " (body anchored)"
            elif self._purelyspatial:
                repr_str += " (purely spatial)"
        elif self._axis:
            repr_str = "axis of relation"

        return '<LocationType: ' + repr(repr_str) + '>'

    @property
    def axis(self):
        if not hasattr(self, '_axis'):
            self._axis = False
        return self._axis

    @axis.setter
    def axis(self, checked):
        # TODO KV - validate?
        self._axis = checked

        if checked:
            self._signingspace = False
            self._bodyanchored = False
            self._purelyspatial = False
            self._body = False

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, checked):
        # TODO KV - validate?
        self._body = checked

        if checked:
            self._signingspace = False
            self._bodyanchored = False
            self._purelyspatial = False
            self._axis = False

    @property
    def signingspace(self):
        return self._signingspace

    @signingspace.setter
    def signingspace(self, checked):
        # TODO KV - validate?
        self._signingspace = checked

        if checked:
            self._body = False
            self._axis = False

    @property
    def bodyanchored(self):
        return self._bodyanchored

    @bodyanchored.setter
    def bodyanchored(self, checked):
        # TODO KV - validate?
        self._bodyanchored = checked

        if checked:
            self._signingspace = True

            self._purelyspatial = False
            self._body = False
            self._axis = False

    @property
    def purelyspatial(self):
        return self._purelyspatial

    @purelyspatial.setter
    def purelyspatial(self, checked):
        # TODO KV - validate?
        self._purelyspatial = checked

        if checked:
            self._signingspace = True

            self._bodyanchored = False
            self._body = False
            self._axis = False

    def usesbodylocations(self):
        return self._body or self._bodyanchored

    def allfalse(self):
        return not (self._body or self._signingspace or self._bodyanchored or self._purelyspatial or self._axis)

    def locationoptions_changed(self, previous):
        changed = self.usesbodylocations() and (previous.purelyspatial or previous.axis)
        changed = changed or (self.purelyspatial and (previous.usesbodylocations() or previous.axis))
        changed = changed or (self.axis and (previous.usesbodylocations() or previous.purelyspatial))
        changed = changed or (previous.allfalse() and not self.allfalse())
        return changed


class LocationModule(ParameterModule):
    def __init__(self, locationtreemodel, hands, timingintervals=None, addedinfo=None, phonlocs=None, inphase=0):
        if phonlocs is None:
            phonlocs = PhonLocations()
        self._locationtreemodel = locationtreemodel
        self._inphase = inphase  # TODO KV is "inphase" actually the best name for this attribute?
        self._phonlocs = phonlocs
        super().__init__(hands, timingintervals=timingintervals, addedinfo=addedinfo)

    @property
    def locationtreemodel(self):
        return self._locationtreemodel

    @locationtreemodel.setter
    def locationtreemodel(self, locationtreemodel):
        # TODO KV - validate?
        self._locationtreemodel = locationtreemodel

    @property
    def phonlocs(self):
        return self._phonlocs

    @phonlocs.setter
    def phonlocs(self, phonlocs):
        # TODO KV - validate?
        self._phonlocs = phonlocs

    @property
    def inphase(self):
        return self._inphase

    @inphase.setter
    def inphase(self, inphase):
        # TODO KV - validate?
        self._inphase = inphase

    def getabbreviation(self):
        # TODO KV these can't be hardcoded like this... fix it!
        # copied from movement
        # abbrevs = {
        #     "Perceptual shape": "Perceptual",
        #     "Straight": "Straight",
        #     # "Interacts with subsequent straight movement": "interacts with subseq. straight mov.",
        #     "Movement contours cross (e.g. X)": "crosses subseq. mov.",
        #     "Subsequent movement starts at end of first (e.g. ↘↗)": "ends where subseq. mov starts",
        #     "Subsequent movement starts in same location as start of first (e.g. ↖↗)": "starts where subseq. mov starts",
        #     "Subsequent movement ends in same location as end of first (e.g. ↘↙)": "ends where subseq. mov. ends",
        #     "Arc": "Arc",
        #     "Circle": "Circle",
        #     "Zigzag": "Zigzag",
        #     "Loop (travelling circles)": "Loop",
        #     "Joint-specific movements": "Joint-specific",
        #     "Nodding/un-nodding": "Nod/Un-",
        #     "Nodding": "nod",
        #     "Un-nodding": "un-nod",
        #     "Pivoting": "Pivot",
        #     "Radial": "radial pivot",
        #     "Ulnar": "ulnar pivot",
        #     "Twisting": "Twist",
        #     "Pronation": "pronation",
        #     "Supination": "supination",
        #     "Closing/Opening": "Close/Open",
        #     "Closing": "close",
        #     "Opening": "open",
        #     "Pinching/unpinching": "Pinch/Un-",
        #     "Pinching (Morgan 2017)": "pinch",
        #     "Unpinching": "unpinch",
        #     "Flattening/Straightening": "Flatten/Straighten",
        #     "Flattening/hinging": "flatten",
        #     "Straightening": "straighten",
        #     "Hooking/Unhooking": "Hook/Un-",
        #     "Hooking/clawing": "hook",
        #     "Unhooking": "unhook",
        #     "Spreading/Unspreading": "Spread/Un-",
        #     "Spreading": "spread",
        #     "Unspreading": "unspread",
        #     "Rubbing": "Rub",
        #     "Wiggling/Fluttering": "Wiggle",
        #     "Up": "up",
        #     "Down": "down",
        #     "Distal": "dist",
        #     "Proximal": "prox",
        #     "Ipsilateral": "ipsi",
        #     "Contralateral": "contra",
        #     "Right": "right",
        #     "Left": "left",
        #     "Mid-sagittal": "mid-sag",
        #     "Clockwise": "clockwise",
        #     "Counterclockwise": "counter-clockwise",
        #     "Horizontal": "Hor",
        #     "Vertical": "Ver",
        #     "Single": "1x",
        #     "2": "2x",
        #     "3": "3x",
        #     "4": "4x",
        #     "Same location": "same loc",
        #     "Different location": "diff. loc",
        #     "Trilled": "Trilled",
        #     "Bidirectional": "Bidirec"
        # }
        # wordlist = []
        #
        # listmodel = self._movementtreemodel.listmodel
        # numrows = listmodel.rowCount()
        # for rownum in range(numrows):
        #     item = listmodel.item(rownum)
        #     text = item.text()
        #     selected = item.data(Qt.UserRole+selectedrole)
        #     if selected:
        #         pathelements = text.split(delimiter)
        #         # thisentrytext = ""
        #         # firstonedone = False
        #         # morethanone = False
        #         for pathelement in pathelements:
        #             if pathelement in abbrevs.keys():  #  and abbrevs[pathelement] not in thisentrytext:
        #                 wordlist.append(abbrevs[pathelement])
        #         #         if not firstonedone:
        #         #             thisentrytext += abbrevs[pathelement]
        #         #             firstonedone = True
        #         #         else:
        #         #             if not morethanone:
        #         #                 thisentrytext += " (" + abbrevs[pathelement] + ", "
        #         #                 morethanone = True
        #         #     if morethanone:  # and thisentrytext.endswith(")"):
        #         #         thisentrytext += ")"  # = thisentrytext[:-2] + ")"
        #         # wordlist.append(thisentrytext)
        #
        # return "; ".join(wordlist)
        return "TODO no abbreviations implemented yet"


# TODO KV comments
class HandConfigurationModule(ParameterModule):
    def __init__(self, handconfiguration, overalloptions, hands, timingintervals=None, addedinfo=None):
        self._handconfiguration = handconfiguration
        self._overalloptions = overalloptions
        super().__init__(hands, timingintervals=timingintervals, addedinfo=addedinfo)

    @property
    def handconfiguration(self):
        return self._handconfiguration

    @handconfiguration.setter
    def handconfiguration(self, new_handconfiguration):
        self._handconfiguration = new_handconfiguration

    @property
    def overalloptions(self):
        return self._overalloptions

    @overalloptions.setter
    def overalloptions(self, new_overalloptions):
        self._overalloptions = new_overalloptions

    def getabbreviation(self):
        handconfighand = HandConfigurationHand(self.handconfiguration)

        predefinedname = ""
        txntuple = tuple(HandConfigurationHand(self.handconfiguration).get_hand_transcription_list())
        if txntuple in PREDEFINED_MAP.keys():
            predefinedname = "'" + PREDEFINED_MAP[txntuple].name + "' "

        fieldstext = ""
        fields = [handconfighand.field2, handconfighand.field3, handconfighand.field4, handconfighand.field5, handconfighand.field6, handconfighand.field7]
        for field in fields:
            fieldstext += "["
            for slot in iter(field):
                fieldstext += slot.symbol
            fieldstext += "] "

        return predefinedname + fieldstext

# TODO KV the below three classes moved to lexicon.module_classes2
#
# # TODO KV comments
# # TODO KV - for parameter modules and x-slots
# class TimingPoint:
#
#     def __init__(self, wholepart, fractionalpart):
#         self._wholepart = wholepart
#         self._fractionalpart = fractionalpart
#
#     def __repr__(self):
#         return '<TimingPoint: ' + repr(self._wholepart) + ', ' + repr(self._fractionalpart) + '>'
#
#     @property
#     def wholepart(self):
#         return self._wholepart
#
#     @wholepart.setter
#     def wholepart(self, wholepart):
#         self._wholepart = wholepart
#
#     @property
#     def fractionalpart(self):
#         return self._fractionalpart
#
#     @fractionalpart.setter
#     def fractionalpart(self, fractionalpart):
#         self._fractionalpart = fractionalpart
#
#     def __eq__(self, other):
#         if isinstance(other, TimingPoint):
#             if self._wholepart == other.wholepart and self._fractionalpart == other.fractionalpart:
#                 return True
#         return False
#
#     def __ne__(self, other):
#         return not self.__eq__(other)
#
#     # do not implement this, because TimingPoint objects are mutable
#     # def __hash__(self):
#     #     pass
#
#     def __lt__(self, other):
#         if isinstance(other, TimingPoint):
#             if self._wholepart < other.wholepart:
#                 # if not(self._fractionalpart == 1 and other.fractionalpart == 0):
#                 return True
#             elif self._wholepart == other.wholepart:
#                 if self._fractionalpart < other.fractionalpart:
#                     return True
#         return False
#
#     def equivalent(self, other):
#         if isinstance(other, TimingPoint):
#             return self.adjacent(other) or self.__eq__(other)
#
#     def adjacent(self, other):
#         if isinstance(other, TimingPoint):
#             if self.fractionalpart == 1 and other.fractionalpart == 0 and (self.wholepart + 1 == other.wholepart):
#                 return True
#             elif other.fractionalpart == 1 and self.fractionalpart == 0 and (other.wholepart + 1 == self.wholepart):
#                 return True
#             else:
#                 return False
#
#     def __gt__(self, other):
#         if isinstance(other, TimingPoint):
#             return other.__lt__(self)
#         return False
#
#     def __le__(self, other):
#         return not self.__gt__(other)
#
#     def __ge__(self, other):
#         return not self.__lt__(other)
#
#     def before(self, other):
#         if isinstance(other, TimingPoint):
#             return self.__lt__(other)
#         elif isinstance(other, TimingInterval):
#             return other.after(self)
#         return False
#
#     def after(self, other):
#         if isinstance(other, TimingPoint):
#             return self.__gt__(other)
#         elif isinstance(other, TimingInterval):
#             return other.before(self)
#         return False
#
#
# # TODO KV comments
# # TODO KV - for parameter modules and x-slots
# class TimingInterval:
#
#     # startpt (type TimingPoint) = the point at which this xslot interval begins
#     # endpt (type TimingPoint) = the point at which this xslot interval ends
#     def __init__(self, startpt, endpt):
#         self.setinterval(startpt, endpt)
#
#     @property
#     def startpoint(self):
#         return self._startpoint
#
#     @property
#     def endpoint(self):
#         return self._endpoint
#
#     def points(self):
#         return self.startpoint(), self.endpoint()
#
#     def setinterval(self, startpt, endpt):
#         if startpt <= endpt:
#             self._startpoint = startpt
#             self._endpoint = endpt
#         else:
#             print("error: start point is larger than endpoint", startpt, endpt)
#             # TODO throw an error?
#
#     def ispoint(self):
#         return self._startpoint == self._endpoint
#
#     def containsinterval(self, otherinterval):
#         return self._startpoint <= otherinterval.startpoint and self._endpoint >= otherinterval.endpoint
#
#     def before(self, other):
#         if isinstance(other, TimingPoint):
#             return self.endpoint < other
#         elif isinstance(other, TimingInterval):
#             if other.ispoint():
#                 return self.endpoint < other.startpoint
#             elif not self.ispoint():
#                 return self.endpoint <= other.startpoint
#             else:
#                 return other.after(self)
#         return False
#
#     def after(self, other):
#         if isinstance(other, TimingPoint):
#             return self.startpoint > other
#         elif isinstance(other, TimingInterval):
#             if other.ispoint():
#                 return self.startpoint > other.endpoint
#             elif not self.ispoint():
#                 return self.startpoint >= other.endpoint
#             else:
#                 return other.before(self)
#         return False
#
#     def adjacent(self, other):
#         if isinstance(other, TimingInterval):
#             return self.endpoint.equivalent(other.startpoint) or other.endpoint.equivalent(self.startpoint)
#         return False
#
#     def __eq__(self, other):
#         if isinstance(other, TimingInterval):
#             return self.startpoint == other.startpoint and self.endpoint == other.endpoint
#         return False
#
#     def overlapsinterval(self, other):
#         if isinstance(other, TimingInterval):
#             if (self.startpoint < other.startpoint and self.endpoint > other.startpoint) or (other.startpoint < self.endpoint and other.endpoint > self.startpoint):
#                 return True
#         return False
#
#     # TODO KV - overlapping and/or contianing checking methods?
#
#     def __repr__(self):
#         return '<TimingInterval: ' + repr(self._startpoint) + ', ' + repr(self._endpoint) + '>'

#
# class AddedInfo:
#
#     def __init__(self,
#                  uncertain_flag=False, uncertain_note="",
#                  estimated_flag=False, estimated_note="",
#                  notspecified_flag=False, notspecified_note="",
#                  variable_flag=False, variable_note="",
#                  exceptional_flag=False, exceptional_note="",
#                  other_flag=False, other_note=""):
#         self._uncertain_flag = uncertain_flag
#         self._uncertain_note = uncertain_note
#         self._estimated_flag = estimated_flag
#         self._estimated_note = estimated_note
#         self._notspecified_flag = notspecified_flag
#         self._notspecified_note = notspecified_note
#         self._variable_flag = variable_flag
#         self._variable_note = variable_note
#         self._exceptional_flag = exceptional_flag
#         self._exceptional_note = exceptional_note
#         self._other_flag = other_flag
#         self._other_note = other_note
#
#     def clear(self):
#         self._uncertain_flag = False
#         self._uncertain_note = ""
#         self._estimated_flag = False
#         self._estimated_note = ""
#         self._notspecified_flag = False
#         self._notspecified_note = ""
#         self._variable_flag = False
#         self._variable_note = ""
#         self._exceptional_flag = False
#         self._exceptional_note = ""
#         self._other_flag = False
#         self._other_note = ""
#
#     @property
#     def uncertain_flag(self):
#         return self._uncertain_flag
#
#     @uncertain_flag.setter
#     def uncertain_flag(self, uncertain_flag):
#         # TODO KV - validate?
#         self._uncertain_flag = uncertain_flag
#
#     @property
#     def uncertain_note(self):
#         return self._uncertain_note
#
#     @uncertain_note.setter
#     def uncertain_note(self, uncertain_note):
#         # TODO KV - validate?
#         self._uncertain_note = uncertain_note
#
#     @property
#     def estimated_flag(self):
#         return self._estimated_flag
#
#     @estimated_flag.setter
#     def estimated_flag(self, estimated_flag):
#         # TODO KV - validate?
#         self._estimated_flag = estimated_flag
#
#     @property
#     def estimated_note(self):
#         return self._estimated_note
#
#     @estimated_note.setter
#     def estimated_note(self, estimated_note):
#         # TODO KV - validate?
#         self._estimated_note = estimated_note
#
#     @property
#     def notspecified_flag(self):
#         return self._notspecified_flag
#
#     @notspecified_flag.setter
#     def notspecified_flag(self, notspecified_flag):
#         # TODO KV - validate?
#         self._notspecified_flag = notspecified_flag
#
#     @property
#     def notspecified_note(self):
#         return self._notspecified_note
#
#     @notspecified_note.setter
#     def notspecified_note(self, notspecified_note):
#         # TODO KV - validate?
#         self._notspecified_note = notspecified_note
#
#     @property
#     def variable_flag(self):
#         return self._variable_flag
#
#     @variable_flag.setter
#     def variable_flag(self, variable_flag):
#         # TODO KV - validate?
#         self._variable_flag = variable_flag
#
#     @property
#     def variable_note(self):
#         return self._variable_note
#
#     @variable_note.setter
#     def variable_note(self, variable_note):
#         # TODO KV - validate?
#         self._variable_note = variable_note
#
#     @property
#     def exceptional_flag(self):
#         return self._exceptional_flag
#
#     @exceptional_flag.setter
#     def exceptional_flag(self, exceptional_flag):
#         # TODO KV - validate?
#         self._exceptional_flag = exceptional_flag
#
#     @property
#     def exceptional_note(self):
#         return self._exceptional_note
#
#     @exceptional_note.setter
#     def exceptional_note(self, exceptional_note):
#         # TODO KV - validate?
#         self._exceptional_note = exceptional_note
#
#     @property
#     def other_flag(self):
#         return self._other_flag
#
#     @other_flag.setter
#     def other_flag(self, other_flag):
#         # TODO KV - validate?
#         self._other_flag = other_flag
#
#     @property
#     def other_note(self):
#         return self._other_note
#
#     @other_note.setter
#     def other_note(self, other_note):
#         # TODO KV - validate?
#         self._other_note = other_note
#
#     def __repr__(self):
#         reprstr = '<AddedInfo: '
#         reprstr += 'Uncertain (' + str(int(self._uncertain_flag)) + ' / ' + self._uncertain_note + ') '
#         reprstr += 'Estimated (' + str(int(self._estimated_flag)) + ' / ' + self._estimated_note + ') '
#         reprstr += 'Not specified (' + str(int(self._notspecified_flag)) + ' / ' + self._notspecified_note + ') '
#         reprstr += 'Variable (' + str(int(self._variable_flag)) + ' / ' + self._variable_note + ') '
#         reprstr += 'Exceptional (' + str(int(self._exceptional_flag)) + ' / ' + self._exceptional_note + ') '
#         reprstr += 'Other (' + str(int(self._other_flag)) + ' / ' + self._other_note + ')'
#         reprstr += '>'
#         return reprstr
