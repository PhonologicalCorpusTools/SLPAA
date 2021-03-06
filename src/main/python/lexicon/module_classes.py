from datetime import datetime

from PyQt5.QtCore import (
    Qt,
)

from gui.hand_configuration import HandConfigurationHand, PREDEFINED_MAP
from gui.movement_view import selectedrole, delimiter


# TODO KV comments
# TODO KV - for parameter modules and x-slots
# common ancestor for (eg) HandshapeModule, MovementModule, etc
class ParameterModule:

    def __init__(self, hands, timingintervals=None):
        self._hands = hands
        self._timingintervals = []
        if timingintervals is not None:
            self.settimingintervals(timingintervals)
        self._uniqueid = datetime.timestamp(datetime.now())

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
        self.settimingintervals(timingintervals)

    def settimingintervals(self, timingintervals):
        self._timingintervals = []
        # add one at a time
        for tint in timingintervals:
            self.add_timinginterval(tint)

    def add_timinginterval(self, timinginterval):
        # TODO KV - look for possible simplifications
        if self._timingintervals == []:
            self._timingintervals.append(timinginterval)
        else:
            needtocombine = False
            idx = 0
            while not needtocombine and idx < len(self._timingintervals):
                existinginterval = self._timingintervals[idx]
                if existinginterval.endpoint.equivalent(timinginterval.startpoint):
                    # the new interval starts right where the existing one ends; combine them and re-add
                    # (in case there's another interval that the newly-combined would also end up linking up with)
                    needtocombine = True
                    self._timingintervals.remove(existinginterval)
                    self.add_timinginterval(TimingInterval(existinginterval.startpoint, timinginterval.endpoint))
                elif existinginterval.startpoint.equivalent(timinginterval.endpoint):
                    # the existing interval starts right where the new one ends; combine them and re-add
                    # (in case there's another interval that the newly-combined would also end up linking up with)
                    needtocombine = True
                    self._timingintervals.remove(existinginterval)
                    self.add_timinginterval(TimingInterval(timinginterval.startpoint, existinginterval.endpoint))
                idx += 1
            if not needtocombine:
                self._timingintervals.append(timinginterval)




# TODO KV comments
# TODO KV - for parameter modules and x-slots
class TargetModule:
    def __init__(self):
        # TODO KV implement
        pass


# TODO KV comments
# TODO KV - for parameter modules and x-slots
class LocationModule:
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
    def __init__(self, movementtreemodel, hands, timingintervals=None):
        self._movementtreemodel = movementtreemodel
        super().__init__(hands, timingintervals)

    @property
    def movementtreemodel(self):
        return self._movementtreemodel

    @movementtreemodel.setter
    def movementtreemodel(self, movementtreemodel):
        # TODO KV - validate?
        self._movementtreemodel = movementtreemodel

    def getabbreviation(self):
        # TODO KV these can't be hardcoded like this... fix it!
        abbrevs = {
            "Perceptual shape": "Perceptual",
            "Straight": "Straight",
            # "Interacts with subsequent straight movement": "interacts with subseq. straight mov.",
            "Movement contours cross (e.g. X)": "crosses subseq. mov.",
            "Subsequent movement starts at end of first (e.g. ??????)": "ends where subseq. mov starts",
            "Subsequent movement starts in same location as start of first (e.g. ??????)": "starts where subseq. mov starts",
            "Subsequent movement ends in same location as end of first (e.g. ??????)": "ends where subseq. mov. ends",
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
            "4": "4x",
            "Same location": "same loc",
            "Different location": "diff. loc",
            "Trilled": "Trilled",
            "Bidirectional": "Bidirec"
        }
        wordlist = []

        listmodel = self._movementtreemodel.listmodel
        numrows = listmodel.rowCount()
        for rownum in range(numrows):
            item = listmodel.item(rownum)
            text = item.text()
            selected = item.data(Qt.UserRole+selectedrole)
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



# TODO KV comments
class HandConfigurationModule(ParameterModule):
    def __init__(self, handconfiguration, overalloptions, hands, timingintervals=None):
        self._handconfiguration = handconfiguration
        self._overalloptions = overalloptions
        super().__init__(hands, timingintervals)

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


# TODO KV comments
# TODO KV - for parameter modules and x-slots
class TimingPoint:

    def __init__(self, wholepart, fractionalpart):
        self._wholepart = wholepart
        self._fractionalpart = fractionalpart

    def __repr__(self):
        return '<TimingPoint: ' + repr(self.wholepart) + ', ' + repr(self._fractionalpart) + '>'

    @property
    def wholepart(self):
        return self._wholepart

    @wholepart.setter
    def wholepart(self, wholepart):
        self._wholepart = wholepart

    @property
    def fractionalpart(self):
        return self._fractionalpart

    @fractionalpart.setter
    def fractionalpart(self, fractionalpart):
        self._fractionalpart = fractionalpart

    def __eq__(self, other):
        if isinstance(other, TimingPoint):
            if self._wholepart == other.wholepart and self._fractionalpart == other.fractionalpart:
                return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    # do not implement this, because TimingPoint objects are mutable
    # def __hash__(self):
    #     pass

    def __lt__(self, other):
        if isinstance(other, TimingPoint):
            if self._wholepart < other.wholepart:
                # if not(self._fractionalpart == 1 and other.fractionalpart == 0):
                return True
            elif self._wholepart == other.wholepart:
                if self._fractionalpart < other.fractionalpart:
                    return True
        return False

    def equivalent(self, other):
        if isinstance(other, TimingPoint):
            return self.adjacent(other) or self.__eq__(other)

    def adjacent(self, other):
        if isinstance(other, TimingPoint):
            if self.fractionalpart == 1 and other.fractionalpart == 0 and (self.wholepart + 1 == other.wholepart):
                return True
            elif other.fractionalpart == 1 and self.fractionalpart == 0 and (other.wholepart + 1 == self.wholepart):
                return True
            else:
                return False

    def __gt__(self, other):
        if isinstance(other, TimingPoint):
            return other.__lt__(self)
        return False

    def __le__(self, other):
        return not self.__gt__(other)

    def __ge__(self, other):
        return not self.__lt__(other)

    def before(self, other):
        if isinstance(other, TimingPoint):
            return self.__lt__(other)
        elif isinstance(other, TimingInterval):
            return other.after(self)
        return False

    def after(self, other):
        if isinstance(other, TimingPoint):
            return self.__gt__(other)
        elif isinstance(other, TimingInterval):
            return other.before(self)
        return False


# TODO KV comments
# TODO KV - for parameter modules and x-slots
class TimingInterval:

    # startpt (type TimingPoint) = the point at which this xslot interval begins
    # endpt (type TimingPoint) = the point at which this xslot interval ends
    def __init__(self, startpt, endpt):
        self.setinterval(startpt, endpt)

    @property
    def startpoint(self):
        return self._startpoint

    @property
    def endpoint(self):
        return self._endpoint

    def points(self):
        return self.startpoint(), self.endpoint()

    def setinterval(self, startpt, endpt):
        if startpt <= endpt:
            self._startpoint = startpt
            self._endpoint = endpt
        else:
            print("error: start point is larger than endpoint", startpt, endpt)
            # TODO throw an error?

    def ispoint(self):
        return self._startpoint == self._endpoint

    def containsinterval(self, otherinterval):
        return self._startpoint <= otherinterval.startpoint and self._endpoint >= otherinterval.endpoint

    def before(self, other):
        if isinstance(other, TimingPoint):
            return self.endpoint < other
        elif isinstance(other, TimingInterval):
            if other.ispoint():
                return self.endpoint < other.startpoint
            elif not self.ispoint():
                return self.endpoint <= other.startpoint
            else:
                return other.after(self)
        return False

    def after(self, other):
        if isinstance(other, TimingPoint):
            return self.startpoint > other
        elif isinstance(other, TimingInterval):
            if other.ispoint():
                return self.startpoint > other.endpoint
            elif not self.ispoint():
                return self.startpoint >= other.endpoint
            else:
                return other.before(self)
        return False

    def adjacent(self, other):
        if isinstance(other, TimingInterval):
            return self.endpoint.equivalent(other.startpoint) or other.endpoint.equivalent(self.startpoint)
        return False

    def __eq__(self, other):
        if isinstance(other, TimingInterval):
            return self.startpoint == other.startpoint and self.endpoint == other.endpoint
        return False

    def overlapsinterval(self, other):
        if isinstance(other, TimingInterval):
            if (self.startpoint < other.startpoint and self.endpoint > other.startpoint) or (other.startpoint < self.endpoint and other.endpoint > self.startpoint):
                return True
        return False

    # TODO KV - overlapping and/or contianing checking methods?

    def __repr__(self):
        return '<TimingInterval: ' + repr(self._startpoint) + ', ' + repr(self._endpoint) + '>'
