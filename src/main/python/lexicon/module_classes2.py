

# TODO KV comments
# TODO KV - for parameter modules and x-slots
class TimingPoint:

    def __init__(self, wholepart, fractionalpart):
        self._wholepart = wholepart
        self._fractionalpart = fractionalpart

    def __repr__(self):
        return '<TimingPoint: ' + repr(self._wholepart) + ', ' + repr(self._fractionalpart) + '>'

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

    # TODO KV delete? - I don't think this is used anywhere except in lexicon_classes.py testing
    def containsinterval(self, otherinterval):
        return self.iswholesign() or (self._startpoint <= otherinterval.startpoint and self._endpoint >= otherinterval.endpoint)
        # if self.iswholesign():
        #     return True
        # elif self._startpoint <= otherinterval.startpoint and self._endpoint >= otherinterval.endpoint:
        #     return True
        # else:
        #     return False

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
            if self.iswholesign() or other.iswholesign():
                return True
            # elif (self.startpoint < other.startpoint and self.endpoint > other.startpoint) or (other.startpoint < self.endpoint and other.endpoint > self.startpoint):
            # either other starts at or in self, or self starts at or in other
            elif (self.startpoint <= other.startpoint and self.endpoint > other.startpoint) or (other.startpoint <= self.startpoint and other.endpoint > self.startpoint):
                return True
        return False

    def iswholesign(self):
        return self.startpoint == TimingPoint(0, 0) and self.endpoint == TimingPoint(0, 1)

    # TODO KV - overlapping and/or containing checking methods?

    def __repr__(self):
        return '<TimingInterval: ' + repr(self._startpoint) + ', ' + repr(self._endpoint) + '>'


class AddedInfo:

    def __init__(self,
                 uncertain_flag=False, uncertain_note="",
                 estimated_flag=False, estimated_note="",
                 notspecified_flag=False, notspecified_note="",
                 variable_flag=False, variable_note="",
                 exceptional_flag=False, exceptional_note="",
                 incomplete_flag=False, incomplete_note="",
                 other_flag=False, other_note=""):
        self._uncertain_flag = uncertain_flag
        self._uncertain_note = uncertain_note
        self._estimated_flag = estimated_flag
        self._estimated_note = estimated_note
        self._notspecified_flag = notspecified_flag
        self._notspecified_note = notspecified_note
        self._variable_flag = variable_flag
        self._variable_note = variable_note
        self._exceptional_flag = exceptional_flag
        self._exceptional_note = exceptional_note
        self._incomplete_flag = incomplete_flag
        self._incomplete_note = incomplete_note
        self._other_flag = other_flag
        self._other_note = other_note

    # def clear(self):
    #     self._uncertain_flag = False
    #     self._uncertain_note = ""
    #     self._estimated_flag = False
    #     self._estimated_note = ""
    #     self._notspecified_flag = False
    #     self._notspecified_note = ""
    #     self._variable_flag = False
    #     self._variable_note = ""
    #     self._exceptional_flag = False
    #     self._exceptional_note = ""
    #     self._other_flag = False
    #     self._other_note = ""

    @property
    def uncertain_flag(self):
        return self._uncertain_flag

    @uncertain_flag.setter
    def uncertain_flag(self, uncertain_flag):
        # TODO KV - validate?
        self._uncertain_flag = uncertain_flag

    @property
    def uncertain_note(self):
        return self._uncertain_note

    @uncertain_note.setter
    def uncertain_note(self, uncertain_note):
        # TODO KV - validate?
        self._uncertain_note = uncertain_note

    @property
    def estimated_flag(self):
        return self._estimated_flag

    @estimated_flag.setter
    def estimated_flag(self, estimated_flag):
        # TODO KV - validate?
        self._estimated_flag = estimated_flag

    @property
    def estimated_note(self):
        return self._estimated_note

    @estimated_note.setter
    def estimated_note(self, estimated_note):
        # TODO KV - validate?
        self._estimated_note = estimated_note

    @property
    def notspecified_flag(self):
        return self._notspecified_flag

    @notspecified_flag.setter
    def notspecified_flag(self, notspecified_flag):
        # TODO KV - validate?
        self._notspecified_flag = notspecified_flag

    @property
    def notspecified_note(self):
        return self._notspecified_note

    @notspecified_note.setter
    def notspecified_note(self, notspecified_note):
        # TODO KV - validate?
        self._notspecified_note = notspecified_note

    @property
    def variable_flag(self):
        return self._variable_flag

    @variable_flag.setter
    def variable_flag(self, variable_flag):
        # TODO KV - validate?
        self._variable_flag = variable_flag

    @property
    def variable_note(self):
        return self._variable_note

    @variable_note.setter
    def variable_note(self, variable_note):
        # TODO KV - validate?
        self._variable_note = variable_note

    @property
    def exceptional_flag(self):
        return self._exceptional_flag

    @exceptional_flag.setter
    def exceptional_flag(self, exceptional_flag):
        # TODO KV - validate?
        self._exceptional_flag = exceptional_flag

    @property
    def incomplete_flag(self):
        return self._incomplete_flag

    @incomplete_flag.setter
    def incomplete_flag(self, incomplete_flag):
        # TODO KV - validate?
        self._incomplete_flag = incomplete_flag

    @property
    def exceptional_note(self):
        return self._exceptional_note

    @exceptional_note.setter
    def exceptional_note(self, exceptional_note):
        # TODO KV - validate?
        self._exceptional_note = exceptional_note

    @property
    def incomplete_note(self):
        return self._incomplete_note

    @incomplete_note.setter
    def incomplete_note(self, incomplete_note):
        # TODO KV - validate?
        self._incomplete_note = incomplete_note

    @property
    def other_flag(self):
        return self._other_flag

    @other_flag.setter
    def other_flag(self, other_flag):
        # TODO KV - validate?
        self._other_flag = other_flag

    @property
    def other_note(self):
        return self._other_note

    @other_note.setter
    def other_note(self, other_note):
        # TODO KV - validate?
        self._other_note = other_note

    def __repr__(self):
        reprstr = '<AddedInfo: '
        reprstr += 'Uncertain (' + repr(int(self._uncertain_flag)) + ' / ' + repr(self._uncertain_note) + ') '
        reprstr += 'Estimated (' + repr(int(self._estimated_flag)) + ' / ' + repr(self._estimated_note) + ') '
        reprstr += 'Not specified (' + repr(int(self._notspecified_flag)) + ' / ' + repr(self._notspecified_note) + ') '
        reprstr += 'Variable (' + repr(int(self._variable_flag)) + ' / ' + repr(self._variable_note) + ') '
        reprstr += 'Exceptional (' + repr(int(self._exceptional_flag)) + ' / ' + repr(self._exceptional_note) + ') '
        reprstr += 'Incomplete (' + repr(int(self._incomplete_flag)) + ' / ' + repr(self._incomplete_note) + ') '
        reprstr += 'Other (' + repr(int(self._other_flag)) + ' / ' + repr(self._other_note) + ')'
        reprstr += '>'
        return reprstr

    def hascontent(self):
        hasflag = self._uncertain_flag or self._estimated_flag or self._notspecified_flag or self._variable_flag or self._exceptional_flag or self._incomplete_flag or self._other_flag
        noteslength = len(
            (
                    self._uncertain_note +
                    self._estimated_note +
                    self._notspecified_note +
                    self._variable_note +
                    self._exceptional_note +
                    self._incomplete_note +
                    self._other_note
            ).replace(" ", ""))
        return hasflag or noteslength > 0
