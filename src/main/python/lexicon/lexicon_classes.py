from itertools import chain
from fractions import Fraction
from datetime import datetime
from copy import deepcopy
from datetime import date

from gui.movement_view import MovementTree
from gui.xslots_selector import XslotStructure

NULL = '\u2205'

def empty_copy(obj):
    class Empty(obj.__class__):
        def __init__(self): pass
    new_copy = Empty(  )
    new_copy.__class__ = obj.__class__
    return new_copy


class SignLevelInformation:
    def __init__(self, signlevel_info, app_settings):
        self._entryid = signlevel_info['entryid']
        self.settings = app_settings
        self._gloss = signlevel_info['gloss']
        self._lemma = signlevel_info['lemma']
        self._source = signlevel_info['source']
        self._signer = signlevel_info['signer']
        self._frequency = signlevel_info['frequency']
        self._coder = signlevel_info['coder']
        self._update_date = signlevel_info['date']
        self._note = signlevel_info['note']
        self._handdominance = signlevel_info['handdominance']

    @property
    def entryid(self):
        return self._entryid

    @entryid.setter
    def entryid(self, new_entryid):
        self._entryid = new_entryid

    def entryid_string(self):
        numdigits = self.settings['display']['entryid_digits']
        entryid_string = str(self._entryid)
        entryid_string = "0"*(numdigits-len(entryid_string)) + entryid_string
        return entryid_string

    @property
    def gloss(self):
        return self._gloss

    @gloss.setter
    def gloss(self, new_gloss):
        self._gloss = new_gloss

    @property
    def lemma(self):
        return self._lemma

    @lemma.setter
    def lemma(self, new_lemma):
        self._lemma = new_lemma

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, new_source):
        self._source = new_source

    @property
    def signer(self):
        return self._signer

    @signer.setter
    def signer(self, new_signer):
        self._signer = new_signer

    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, new_frequency):
        self._frequency = new_frequency

    @property
    def coder(self):
        return self._coder

    @coder.setter
    def coder(self, new_coder):
        self._coder = new_coder

    @property
    def update_date(self):
        return self._update_date

    @update_date.setter
    def update_date(self, new_update_date):
        self._update_date = new_update_date

    @property
    def note(self):
        return self._note

    @note.setter
    def note(self, new_note):
        self._note = new_note

    @property
    def signtype(self):
        return self._signtype

    @signtype.setter
    def signtype(self, new_signtype):
        self._signtype = new_signtype

    @property
    def handdominance(self):
        return self._handdominance

    @handdominance.setter
    def handdominance(self, new_handdominance):
        self._handdominance = new_handdominance


class GlobalHandshapeInformation:
    def __init__(self, global_handshape_info):
        self._forearm = global_handshape_info['forearm']
        self._estimated = global_handshape_info['estimated']
        self._uncertain = global_handshape_info['uncertain']
        self._incomplete = global_handshape_info['incomplete']
        self._fingerspelled = global_handshape_info['fingerspelled']
        self._initialized = global_handshape_info['initialized']

    @property
    def estimated(self):
        return self._estimated

    @estimated.setter
    def estimated(self, new_is_estimated):
        self._estimated = new_is_estimated

    @property
    def uncertain(self):
        return self._uncertain

    @uncertain.setter
    def uncertain(self, new_is_uncertain):
        self._uncertain = new_is_uncertain

    @property
    def incomplete(self):
        return self._incomplete

    @incomplete.setter
    def incomplete(self, new_is_incomplete):
        self._incomplete = new_is_incomplete

    @property
    def fingerspelled(self):
        return self._fingerspelled

    @fingerspelled.setter
    def fingerspelled(self, new_is_fingerspelled):
        self._fingerspelled = new_is_fingerspelled

    @property
    def initialized(self):
        return self._initialized

    @initialized.setter
    def initialized(self, new_is_initialized):
        self._initialized = new_is_initialized

    @property
    def forearm(self):
        return self._forearm

    @forearm.setter
    def forearm(self, new_is_forearm):
        self._forearm = new_is_forearm


class HandConfigurationSlot:
    def __init__(self, slot_number, symbol, is_estimate, is_uncertain):
        self._slot_number = slot_number
        self._symbol = symbol
        self._estimate = is_estimate
        self._uncertain = is_uncertain

    @property
    def slot_number(self):
        return self._slot_number

    @slot_number.setter
    def slot_number(self, new_slot_number):
        self._slot_number = new_slot_number

    @property
    def symbol(self):
        return self._symbol

    @symbol.setter
    def symbol(self, new_symbol):
        self._symbol = new_symbol

    @property
    def estimate(self):
        return self._estimate

    @estimate.setter
    def estimate(self, new_is_estimate):
        self._estimate = new_is_estimate

    @property
    def uncertain(self):
        return self._uncertain

    @uncertain.setter
    def uncertain(self, new_is_uncertain):
        self._uncertain = new_is_uncertain


class HandConfigurationField:
    def __init__(self, field_number, slots):
        self._field_number = field_number
        self._slots = slots

        self.set_slots()

    @property
    def field_number(self):
        return self._field_number

    @field_number.setter
    def field_number(self, new_field_number):
        self._field_number = new_field_number

    def set_slots(self):
        if self._field_number == 2:
            self.slot2, self.slot3, self.slot4, self.slot5 = [HandConfigurationSlot(slot['slot_number'], slot['symbol'], slot['estimate'], slot['uncertain']) for slot in self._slots]
        elif self._field_number == 3:
            self.slot6, self.slot7, self.slot8, self.slot9, self.slot10, self.slot11, self.slot12, self.slot13, self.slot14, self.slot15 = [HandConfigurationSlot(slot['slot_number'], slot['symbol'], slot['estimate'], slot['uncertain']) for slot in self._slots]
        elif self._field_number == 4:
            self.slot16, self.slot17, self.slot18, self.slot19 = [HandConfigurationSlot(slot['slot_number'], slot['symbol'], slot['estimate'], slot['uncertain']) for slot in self._slots]
        elif self._field_number == 5:
            self.slot20, self.slot21, self.slot22, self.slot23, self.slot24 = [HandConfigurationSlot(slot['slot_number'], slot['symbol'], slot['estimate'], slot['uncertain']) for slot in self._slots]
        elif self._field_number == 6:
            self.slot25, self.slot26, self.slot27, self.slot28, self.slot29 = [HandConfigurationSlot(slot['slot_number'], slot['symbol'], slot['estimate'], slot['uncertain']) for slot in self._slots]
        elif self._field_number == 7:
            self.slot30, self.slot31, self.slot32, self.slot33, self.slot34 = [HandConfigurationSlot(slot['slot_number'], slot['symbol'], slot['estimate'], slot['uncertain']) for slot in self._slots]

    def __iter__(self):
        if self._field_number == 2:
            return [self.slot2, self.slot3, self.slot4, self.slot5].__iter__()
        elif self._field_number == 3:
            return [self.slot6, self.slot7, self.slot8, self.slot9, self.slot10, self.slot11, self.slot12, self.slot13, self.slot14, self.slot15].__iter__()
        elif self._field_number == 4:
            return [self.slot16, self.slot17, self.slot18, self.slot19].__iter__()
        elif self._field_number == 5:
            return [self.slot20, self.slot21, self.slot22, self.slot23, self.slot24].__iter__()
        elif self._field_number == 6:
            return [self.slot25, self.slot26, self.slot27, self.slot28, self.slot29].__iter__()
        elif self._field_number == 7:
            return [self.slot30, self.slot31, self.slot32, self.slot33, self.slot34].__iter__()


class HandConfigurationHand:
    def __init__(self, fields):  # hand_number, fields):
        # self._hand_number = hand_number
        self.field2, self.field3, self.field4, self.field5, self.field6, self.field7 = [HandConfigurationField(field['field_number'], field['slots']) for field in fields]

    # @property
    # def hand_number(self):
    #     return self._hand_number
    #
    # @hand_number.setter
    # def hand_number(self, new_hand_number):
    #     self._hand_number = new_hand_number

    def __iter__(self):
        return chain(iter(self.field2), iter(self.field3), iter(self.field4), iter(self.field5), iter(self.field6), iter(self.field7))

    def get_hand_transcription_list(self):
        return [slot.symbol for slot in self.__iter__()]

    def get_hand_transcription_string(self):
        return ''.join(self.get_hand_transcription_list())

    def is_empty(self):
        return self.get_hand_transcription_list() == [
            '', '', '', '',
            '', '', NULL, '/', '', '', '', '', '', '',
            '1', '', '', '',
            '', '2', '', '', '',
            '', '3', '', '', '',
            '', '4', '', '', ''
        ]

#
# class HandshapeTranscriptionConfig:
#     def __init__(self, hand):  # config_number, hands):
#         self.hand1 = HandConfigurationHand(hand['fields'])
#
#     # def is_empty(self):
#     #     return self.hand1.is_empty()  # and self.hand2.is_empty()
#

class HandConfiguration:
    def __init__(self, config):

        # from above
        # self.hand1 = HandConfigurationHand(hand['fields'])
        self.config = config


# class HandshapeTranscription:
#     def __init__(self, configvalue):  # s):
#         # self.configs = configs
#         # structure of congfigvalue: {
#         #     'forearm': self.slot1.isChecked(),
#         #     'estimated': self.estimated.isChecked(),
#         #     'uncertain': self.uncertain.isChecked(),
#         #     'incomplete': self.incomplete.isChecked(),
#         #     'hand': self.hand.get_value()
#         # }
#
#         self.config = HandshapeTranscriptionConfig(config)  # config  # [0]
#         # TODO KV delete
#         # self.config1, self.config2 = [HandshapeTranscriptionConfig(config['config_number'], config['hands']) for config in configs]
#         # self.config1 = [HandshapeTranscriptionConfig(config['config_number'], config['hands']) for config in configs][0]
#         # self.config1 = HandshapeTranscriptionConfig(config)  # config['config_number'], config['hands'][0])
#         # self.find_properties()
#
#     def __repr__(self):
#         return repr(self.config)  #s)

    # TODO KV delete
    # def find_properties(self):
    #     # one-handed vs. two-handed
    #     self.handedness = self.find_handedness()
    #
    #     # one-config vs. two-config
    #     self.config = self.find_config()

    # TODO KV delete
    # def find_handedness(self):
    #     if self.config1.is_empty() and self.config2.is_empty():
    #         return 0
    #     elif self.config1.find_handedness() == 3 or self.config2.find_handedness() == 3:
    #         return 2
    #     elif self.config1.find_handedness() == 1 and self.config2.find_handedness() == 2:
    #         return 2
    #     elif self.config2.find_handedness() == 1 and self.config1.find_handedness() == 2:
    #         return 2
    #     else:
    #         return 1

    # TODO KV delete
    # def find_config(self):
    #     if self.config1.is_empty() and self.config2.is_empty():
    #         return 0
    #     elif self.config1.is_empty() and not self.config2.is_empty():
    #         return 2
    #     elif not self.config1.is_empty() and self.config2.is_empty():
    #         return 1
    #     else:
    #         return 3


class LocationPoint:
    def __init__(self, location_point_info):
        self.points = location_point_info
        #self.loc_identifier = location_point_info['image']
        #self.point = Point(location_point_info['point']) if location_point_info['point'] else None


class LocationHand:
    def __init__(self, location_hand_info):
        self.contact = location_hand_info['contact']
        self.D = LocationPoint(location_hand_info['D'])
        self.W = LocationPoint(location_hand_info['W'])


class LocationTranscription:
    def __init__(self, location_transcription_info):
        self.start = LocationHand(location_transcription_info['start'])
        self.end = LocationHand(location_transcription_info['end'])

        #self.parts = {name: LocationHand(hand) for name, hand in location_transcription_info.items()}



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

    # TODO KV - overlapping and/or contianing checking methods?

    def __repr__(self):
        return '<TimingInterval: ' + repr(self._startpoint) + ', ' + repr(self._endpoint) + '>'


# TODO: need to think about duplicated signs
class Sign:
    """
    Gloss in signlevel_information is used as the unique key
    """
    def __init__(self, signlevel_info=None, serializedsign=None):
        if serializedsign:
            self._signlevel_information = serializedsign['signlevel']
            self._signtype = serializedsign['type']
            self._xslotstructure = serializedsign['xslot structure']
            self._specifiedxslots = serializedsign['specified xslots']
            self.unserializemovementmodules(serializedsign['mov modules'])
            self.handpartmodules = serializedsign['hpt modules']
            self.locationmodules = serializedsign['loc modules']
            self.contactmodules = serializedsign['con modules']
            self.orientationmodules = serializedsign['ori modules']
            self.handconfigmodules = serializedsign['cfg modules']
        else:
            self._signlevel_information = signlevel_info

            # TODO KV - for parameter modules and x-slots
            self._signtype = None
            self.xslotstructure = XslotStructure()
            self.specifiedxslots = False
            self.movementmodules = {}
            self.handpartmodules = []
            self.locationmodules = []
            self.contactmodules = []
            self.orientationmodules = []
            self.handconfigmodules = {}

    def serialize(self):
        return {
            'signlevel': self._signlevel_information,
            'type': self._signtype,
            'xslot structure': self.xslotstructure,
            'specified xslots': self.specifiedxslots,
            'mov modules': self.serializemovementmodules(),
            'hpt modules': self.handpartmodules,
            'loc modules': self.locationmodules,
            'con modules': self.contactmodules,
            'ori modules': self.orientationmodules,
            'cfg modules': self.handshapemodules
        }

    def serializemovementmodules(self):
        serialized = {}
        for k in self.movementmodules.keys():
            serialized[k] = MovementTree(self.movementmodules[k])
        return serialized

    def unserializemovementmodules(self, serialized_mvmtmodules):
        unserialized = {}
        for k in serialized_mvmtmodules.keys():
            mvmttreemodel = serialized_mvmtmodules[k].getMovementTreeModel()
            unserialized[k] = mvmttreemodel
        self.movementmodules = unserialized

    def __hash__(self):
        # return hash(self.signlevel_information.gloss)
        return hash(self.signlevel_information.entryid)

    # Ref: https://eng.lyft.com/hashing-and-equality-in-python-2ea8c738fb9d
    def __eq__(self, other):
        # return isinstance(other, Sign) and self.signlevel_information.gloss == other.signlevel_information.gloss
        return isinstance(other, Sign) and self.signlevel_information.entryid == other.signlevel_information.entryid

    def __repr__(self):
        return '<SIGN: ' + repr(self.signlevel_information.gloss) + ' - ' + repr(self.signlevel_information.entryid) + '>'

    @property
    def signlevel_information(self):
        return self._signlevel_information

    @signlevel_information.setter
    def signlevel_information(self, signlevelinfo):
        self._signlevel_information = signlevelinfo  # SignLevelInformation(signlevelinfo)

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, locn):
        self._location = LocationTranscription(locn)

    @property
    def specifiedxslots(self):
        return self._specifiedxslots

    @specifiedxslots.setter
    def specifiedxslots(self, specifiedxslots):
        self._specifiedxslots = specifiedxslots

    @property
    def signtype(self):
        return self._signtype

    @signtype.setter
    def signtype(self, stype):
        # TODO KV - validate?
        self._signtype = stype

    @property
    def xslotstructure(self):
        return self._xslotstructure

    @xslotstructure.setter
    def xslotstructure(self, xslotstruct):
        # TODO KV - validate?
        self._xslotstructure = xslotstruct

    def updatemovementmodule(self, uniqueid, movementtree, hands_dict, timingintervals):
        mvmtmod = self.movementmodules[uniqueid]
        mvmtmod.movementtree = movementtree
        mvmtmod.hands = hands_dict
        mvmtmod.timingintervals = timingintervals

    def addmovementmodule(self, movementtree, hands_dict, timingintervals):
        # create and add a brand new one
        mvmtmod = MovementModule(movementtree, hands_dict, timingintervals)
        self.movementmodules[mvmtmod.uniqueid] = mvmtmod

    def removemovementmodule(self, uniqueid):
        self.movementmodules.pop(uniqueid)

    def updatehandconfigmodule(self, uniqueid, handconfiguration, overalloptions, hands_dict, timingintervals):
        hcfgmod = self.handconfigmodules[uniqueid]
        hcfgmod.handconfiguration = handconfiguration
        hcfgmod.hands = hands_dict
        hcfgmod.overalloptions = overalloptions
        hcfgmod.timingintervals = timingintervals

    def addhandconfigmodule(self, handconfiguration, overalloptions, hands_dict, timingintervals):
        # create and add a brand new one
        hcfgmod = HandConfigurationModule(handconfiguration, overalloptions, hands_dict, timingintervals)
        self.handconfigmodules[hcfgmod.uniqueid] = hcfgmod

    def removehandconfigmodule(self, uniqueid):
        self.handshapemodules.pop(uniqueid)

    def addtargetmodule(self, targetmod):
        self.targetmodules.append(targetmod)

    def addlocationmodule(self, locationmod):
        self.locationmodules.append(locationmod)

    def addorientationmodule(self, orientationmod):
        self.orientationmodules.append(orientationmod)


# TODO KV comments
# TODO KV - for parameter modules and x-slots
# common ancestor for (eg) HandshapeModule, MovementModule, etc
class ParameterModule:

    def __init__(self, hands, timingintervals=None):
        self._hands = hands
        self._timingintervals = []
        if timingintervals is not None:
            self.settimingintervals(timingintervals)
        self._uniqueid = int(datetime.timestamp(datetime.now()))

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
# ... should this *replace* handshapetranscriptionconfig instead of wrapping it?
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


# TODO KV delete
# TODO KV - for parameter modules and x-slots
class MovementModule(ParameterModule):
    def __init__(self, movementtree, hands, timingintervals=None):
        self._movementtree = movementtree
        super().__init__(hands, timingintervals)

    @property
    def movementtree(self):
        return self._movementtree

    @movementtree.setter
    def movementtree(self, movementtree):
        # TODO KV - validate?
        self._movementtree = movementtree


class LocationParameter:
    """
    This is intended to be used with the Locations class
    """
    def __init__(self, name=None, image_path=None, location_polygons=None, default=True):
        if location_polygons is None:
            location_polygons = dict()
        self.name = name
        self.image_path = image_path
        self.location_polygons = location_polygons
        self.default = default

    def get_attr_dict(self):
        return {
            'name': self.name,
            'image_path': self.image_path,
            'location_polygons': self.location_polygons,
            'default': self.default
        }


class Locations:
    """
    This class is intended for the Corpus class to specify corpus-level location definition
    """
    #TODO: improve this so that order is kept, also a better repr
    def __init__(self, location_specification):
        """
        locations = {'location_identifier': LocationParameter}
        """
        self.locations = location_specification

    def get_attr_dict(self):
        return {loc_identifier: location_param.get_attr_dict() for loc_identifier, location_param in self.locations.items()}

    # Ref: https://stackoverflow.com/questions/4014621/a-python-class-that-acts-like-dict
    def __setitem__(self, location_identifier, location_parameter):
        self.locations[location_identifier] = location_parameter

    def __getitem__(self, location_identifier):
        return self.locations[location_identifier]

    def __repr__(self):
        return repr(self.locations)

    def __len__(self):
        return len(self.locations)

    def __delitem__(self, location_identifier):
        del self.locations[location_identifier]

    def clear(self):
        return self.locations.clear()

    def copy(self):
        return self.locations.copy()

    def has_location(self, location_identifier):
        return location_identifier in self.locations

    def update(self, *args, **kwargs):
        return self.locations.update(*args, **kwargs)

    def keys(self):
        return sorted(list(self.locations.keys()))

    def values(self):
        return [self.locations[loc] for loc in self.keys()]

    def items(self):
        return [(loc, self.locations[loc]) for loc in self.keys()]

    def pop(self, *args):
        return self.locations.pop(*args)

    def __cmp__(self, dict_):
        return self.__cmp__(self.locations, dict_)

    def __contains__(self, location_identifier):
        return location_identifier in self.locations

    def __iter__(self):
        return iter(self.keys())


class Corpus:
    #TODO: need a default for location_definition
    def __init__(self, name="", signs=None, location_definition=None, path=None, serializedcorpus=None, highestID=0):  # movement_definition=None,
        if serializedcorpus:
            self.name = serializedcorpus['name']
            self.signs = set([Sign(serializedsign=s) for s in serializedcorpus['signs']])
            self.location_definition = serializedcorpus['loc defn']
            # self.movement_definition = serializedcorpus['mvmt defn']
            self.path = serializedcorpus['path']
            self.highestID = serializedcorpus['highest id']
        else:
            self.name = name
            self.signs = signs if signs else set()
            self.location_definition = location_definition
            # self.movement_definition = movement_definition
            self.path = path
            self.highestID = highestID

    def serialize(self):
        return {
            'name': self.name,
            'signs': [s.serialize() for s in list(self.signs)],
            'loc defn': self.location_definition,
            'path': self.path,
            'highest id': self.highestID
        }

    def get_sign_glosses(self):
        return sorted([sign.signlevel_information.gloss for sign in self.signs])

    def get_previous_sign(self, gloss):
        sign_glosses = self.get_sign_glosses()
        current_index = sign_glosses.index(gloss)

        # if the very first sign is selected, then return the one after it, otherwise the previous one
        previous_gloss = sign_glosses[current_index-1] if current_index-1 >= 0 else sign_glosses[1]

        return self.get_sign_by_gloss(previous_gloss)

    def get_sign_by_gloss(self, gloss):
        # Every sign has a unique gloss, so this function will always return one sign
        for sign in self.signs:
            if sign.signlevel_information.gloss == gloss:
                return sign

    def add_sign(self, new_sign):
        self.signs.add(new_sign)
        self.highestID = max([new_sign.signlevel_information.entryid, self.highestID])

    def remove_sign(self, trash_sign):
        self.signs.remove(trash_sign)

    def __contains__(self, item):
        return item in self.signs

    def __iter__(self):
        return iter(self.signs)

    def __len__(self):
        return len(self.signs)

    def __repr__(self):
        return '<CORPUS: ' + repr(self.name) + '>'


if __name__ == '__main__':

    # test TimingPoint
    print("testing TimingPoint comparison operators...")
    tp1 = TimingPoint(1, Fraction(0))
    tp2 = TimingPoint(1, Fraction(1,3))
    tp3 = TimingPoint(1, Fraction(3,4))
    tp4 = TimingPoint(1, Fraction(1))
    tp5 = TimingPoint(2, Fraction(0))
    tp6 = TimingPoint(2, Fraction(1,3))
    tp7 = TimingPoint(2, Fraction(1,3))
    orderedpoints1 = [tp1, tp2, tp3, tp4, tp6]
    orderedpoints2 = [tp1, tp2, tp3, tp5, tp7]
    lt_success = True
    le_success = True
    ge_success = True
    gt_success = True
    eq_success = True
    ne_success = True
    equiv_success = True
    for tplist in [orderedpoints1, orderedpoints2]:
        for idx, first in enumerate(tplist[:-1]):
            for second in tplist[idx+1:]:
                lt_success = lt_success and first < second
                gt_success = gt_success and second > first
                le_success = le_success and first <= second
                ge_success = ge_success and second >= first
                eq_success = eq_success and not first == second
                ne_success = ne_success and first != second
                equiv_success = equiv_success and not first.equivalent(second)
    lt_success = lt_success and not tp6 < tp7 and not tp4 < tp5
    gt_success = gt_success and not tp6 > tp7 and not tp5 > tp4
    le_success = le_success and tp6 <= tp7 and tp4 <= tp5
    ge_success = ge_success and tp6 >= tp7 and tp4 >= tp5
    eq_success = eq_success and tp6 == tp7 and not tp4 == tp5
    ne_success = ne_success and not tp6 != tp7 and tp4 != tp5
    equiv_success = equiv_success and tp6.equivalent(tp7) and tp4.equivalent(tp5)

    print("success: lt", lt_success, "/ gt", gt_success, "/ le", le_success, "/ ge", ge_success, "/ eq", eq_success, "/ ne", ne_success, "/ equiv", equiv_success)


    # test TimingInterval
    print("testing TimingInterval methods...")
    int1 = TimingInterval(tp1, tp2)
    int2 = TimingInterval(tp2, tp4)
    int3 = TimingInterval(tp5, tp6)
    int4 = TimingInterval(tp1, tp7)
    int5 = TimingInterval(tp4, tp4)
    int6 = TimingInterval(tp5, tp1)
    int7 = TimingInterval(tp7, tp7)

    containssuccess = True
    containssuccess = containssuccess and not int1.containsinterval(int2) and not int2.containsinterval(
        int4) and int4.containsinterval(int1) and int4.containsinterval(int3) and int4.containsinterval(int5)
    ispointsuccess = int7.ispoint() and not int1.ispoint()
    print("success: containsinterval", containssuccess, "/ ispoint", ispointsuccess)

    # test ParameterModule
    print("testing ParameterModule methods...")
    pm1 = ParameterModule(hands={"H1": True, "H2": True}, timingintervals=[int1])
    print(pm1.timingintervals)
    pm2 = ParameterModule(hands={"H1": True, "H2": False}, timingintervals=[int1, int2])
    print(pm2.timingintervals)
    pm3 = ParameterModule(hands={"H1": True, "H2": False}, timingintervals=[int1, int2, int3])
    print(pm3.timingintervals)
    pm4 = ParameterModule(hands={"H1": True, "H2": False}, timingintervals=[int1, int3])
    print(pm4.timingintervals)
    pm5 = ParameterModule(hands={"H1": True, "H2": False}, timingintervals=[int1, int2, int7])
    print(pm5.timingintervals)
