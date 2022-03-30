from itertools import chain
from copy import deepcopy
from datetime import date

from gui.movement_view import MovementTree

NULL = '\u2205'

def empty_copy(obj):
    class Empty(obj.__class__):
        def __init__(self): pass
    new_copy = Empty(  )
    new_copy.__class__ = obj.__class__
    return new_copy


class SignLevelInformation:
    def __init__(self, signlevel_info):
        self._gloss = signlevel_info['gloss']
        self._lemma = signlevel_info['lemma']
        self._source = signlevel_info['source']
        self._signer = signlevel_info['signer']
        self._frequency = signlevel_info['frequency']
        self._coder = signlevel_info['coder']
        self._update_date = signlevel_info['date']
        self._note = signlevel_info['note']
        self._handdominance = signlevel_info['handdominance']

    # TODO KV is anyone using htis??
    # def __init__(self, coder, defaulthand):
    #     self._gloss = ""
    #     self._lemma = ""
    #     self._source = ""
    #     self._signer = ""
    #     self._frequency = '1.0'
    #     self._coder = coder
    #     self._update_date = date.today()
    #     self._note = ""
    #     self._handdominance = defaulthand

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


class HandshapeTranscriptionSlot:
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


class HandshapeTranscriptionField:
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
            self.slot2, self.slot3, self.slot4, self.slot5 = [HandshapeTranscriptionSlot(slot['slot_number'], slot['symbol'], slot['estimate'], slot['uncertain']) for slot in self._slots]
        elif self._field_number == 3:
            self.slot6, self.slot7, self.slot8, self.slot9, self.slot10, self.slot11, self.slot12, self.slot13, self.slot14, self.slot15 = [HandshapeTranscriptionSlot(slot['slot_number'], slot['symbol'], slot['estimate'], slot['uncertain']) for slot in self._slots]
        elif self._field_number == 4:
            self.slot16, self.slot17, self.slot18, self.slot19 = [HandshapeTranscriptionSlot(slot['slot_number'], slot['symbol'], slot['estimate'], slot['uncertain']) for slot in self._slots]
        elif self._field_number == 5:
            self.slot20, self.slot21, self.slot22, self.slot23, self.slot24 = [HandshapeTranscriptionSlot(slot['slot_number'], slot['symbol'], slot['estimate'], slot['uncertain']) for slot in self._slots]
        elif self._field_number == 6:
            self.slot25, self.slot26, self.slot27, self.slot28, self.slot29 = [HandshapeTranscriptionSlot(slot['slot_number'], slot['symbol'], slot['estimate'], slot['uncertain']) for slot in self._slots]
        elif self._field_number == 7:
            self.slot30, self.slot31, self.slot32, self.slot33, self.slot34 = [HandshapeTranscriptionSlot(slot['slot_number'], slot['symbol'], slot['estimate'], slot['uncertain']) for slot in self._slots]

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


class HandshapeTranscriptionHand:
    def __init__(self, hand_number, fields):
        self._hand_number = hand_number
        self.field2, self.field3, self.field4, self.field5, self.field6, self.field7 = [HandshapeTranscriptionField(field['field_number'], field['slots']) for field in fields]

    @property
    def hand_number(self):
        return self._hand_number

    @hand_number.setter
    def hand_number(self, new_hand_number):
        self._hand_number = new_hand_number

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


class HandshapeTranscriptionConfig:
    def __init__(self, config_number, hands):
        self._config_number = config_number
        self.hand1, self.hand2 = [HandshapeTranscriptionHand(hand['hand_number'], hand['fields']) for hand in hands]

    @property
    def config_number(self):
        return self._config_number

    @config_number.setter
    def config_number(self, new_config_number):
        self._config_number = new_config_number

    def is_empty(self):
        return self.hand1.is_empty() and self.hand2.is_empty()

    def find_handedness(self):
        if self.hand1.is_empty() and self.hand2.is_empty():
            return 0
        elif not self.hand1.is_empty() and self.hand2.is_empty():
            return 1
        elif self.hand1.is_empty() and not self.hand2.is_empty():
            return 2
        elif not self.hand1.is_empty() and not self.hand2.is_empty():
            return 3

    def __iter__(self):
        return [self.hand1, self.hand2].__iter__()


class HandshapeTranscription:
    def __init__(self, configs):
        self.configs = configs
        self.config1, self.config2 = [HandshapeTranscriptionConfig(config['config_number'], config['hands']) for config in configs]
        self.find_properties()

    def __repr__(self):
        return repr(self.configs)

    def find_properties(self):
        # one-handed vs. two-handed
        self.handedness = self.find_handedness()

        # one-config vs. two-config
        self.config = self.find_config()

    def find_handedness(self):
        if self.config1.is_empty() and self.config2.is_empty():
            return 0
        elif self.config1.find_handedness() == 3 or self.config2.find_handedness() == 3:
            return 2
        elif self.config1.find_handedness() == 1 and self.config2.find_handedness() == 2:
            return 2
        elif self.config2.find_handedness() == 1 and self.config1.find_handedness() == 2:
            return 2
        else:
            return 1

    def find_config(self):
        if self.config1.is_empty() and self.config2.is_empty():
            return 0
        elif self.config1.is_empty() and not self.config2.is_empty():
            return 2
        elif not self.config1.is_empty() and self.config2.is_empty():
            return 1
        else:
            return 3


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
class MovementModule:
    def __init__(self):
        # TODO KV implement
        pass
        # gather all data from movement selector


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
# ... should this *replace* handshapetranscriptionconfig instead of wrapping it?
class HandshapeModule:
    def __init__(self):
        # TODO KV implement
        self._handshapetranscriptionconfig = None

        @property
        def handshapetranscriptionconfig(self):
            return self._handshapetranscriptionconfig

        @handshapetranscriptionconfig.setter
        def handshapetranscriptionconfig(self, new_handshapetranscriptionconfig):
            self._handshapetranscriptionconfig = new_handshapetranscriptionconfig


# TODO KV comments
# TODO KV - for parameter modules and x-slots
class TimingInterval:
    def __init__(self):
        # TODO KV implement
        self._parametermodule = None
        self._startpoint = None
        self._endpoint = None

    @property
    def parametermodule(self):
        return self._parametermodule

    @parametermodule.setter
    def parametermodule(self, parammodule):
        self._parametermodule = parammodule

    @property
    def startpoint(self):
        return self._startpoint

    @startpoint.setter
    def startpoint(self, startpt):
        self._startpoint = startpt

    @property
    def endpoint(self):
        return self._endpoint

    @endpoint.setter
    def endpoint(self, endpt):
        self._endpoint = endpt

    def points(self):
        return [self.startpoint(), self.endpoint()]

    def setinterval(self, startpt, endpt):
        self.setstartpoint(startpt)
        self.setendpoint(endpt)

    def ispoint(self):
        return self.startpoint() == self.endpoint()


# TODO: need to think about duplicated signs
class Sign:
    """
    Gloss in signlevel_information is used as the unique key
    """
    # def __init__(self,
    #              signlevel_info,
    #              global_hand_info,
    #              configs,
    #              location_transcription_info):
    #     self._signlevel_information = signlevel_info  # SignLevelInformation(signlevel_info)
    #     self._global_handshape_information = GlobalHandshapeInformation(global_hand_info)
    #     self._handshape_transcription = HandshapeTranscription(configs)
    #     self._location = LocationTranscription(location_transcription_info)
    #
    #     # TODO KV - for parameter modules and x-slots
    #     self._signtype = None
    #     self.movementmodules = {}
    #     # self.targetmodules = []
    #     self.locationmodules = []
    #     self.orientationmodules = []
    #     self.handshapemodules = []

    def __init__(self, signlevel_info=None, serializedsign=None):
        if serializedsign:
            self._signlevel_information = serializedsign['signlevel']
            self._signtype = serializedsign['type']
            self.unserializemovementmodules(serializedsign['mov modules'])
            self.locationmodules = serializedsign['loc modules']
            self.orientationmodules = serializedsign['ori modules']
            self.handshapemodules = serializedsign['han modules']
        else:
            self._signlevel_information = signlevel_info
            # if isinstance(signlevel_info, SignLevelInformation):
            #     self._signlevel_information = signlevel_info
            # else:
            #     self._signlevel_information = SignLevelInformation(signlevel_info)


            # self._global_handshape_information = GlobalHandshapeInformation(global_hand_info)
            # self._handshape_transcription = HandshapeTranscription(configs)
            # self._location = LocationTranscription(location_transcription_info)

            # TODO KV - for parameter modules and x-slots
            self._signtype = None
            self.movementmodules = {}
            # self.targetmodules = []
            self.locationmodules = []
            self.orientationmodules = []
            self.handshapemodules = []

    def serialize(self):
        return {
            'signlevel': self._signlevel_information,
            'type': self._signtype,
            'mov modules': self.serializemovementmodules(),
            'loc modules': self.locationmodules,
            'ori modules': self.orientationmodules,
            'han modules': self.handshapemodules
        }

    def serializemovementmodules(self):
        serialized = {}
        for k in self.movementmodules.keys():
            serialized[k] = MovementTree(self.movementmodules[k])
        return serialized

    def unserializemovementmodules(self, serialized_mvmtmodules):
        unserialized = {}
        for k in serialized_mvmtmodules.keys():
            mvmttreemodel, rootnode = serialized_mvmtmodules[k].getMovementTreeModel()
            unserialized[k] = mvmttreemodel
        self.movementmodules = unserialized

    def __hash__(self):
        return hash(self.signlevel_information.gloss)

    # Ref: https://eng.lyft.com/hashing-and-equality-in-python-2ea8c738fb9d
    def __eq__(self, other):
        return isinstance(other, Sign) and self.signlevel_information.gloss == other.signlevel_information.gloss

    def __repr__(self):
        return '<SIGN: ' + repr(self.signlevel_information.gloss) + '>'

    @property
    def signlevel_information(self):
        return self._signlevel_information

    @signlevel_information.setter
    def signlevel_information(self, signlevelinfo):
        self._signlevel_information = signlevelinfo  # SignLevelInformation(signlevelinfo)

    @property
    def global_handshape_information(self):
        return self._global_handshape_information

    @global_handshape_information.setter
    def global_handshape_information(self, globalhandshapeinfo):
        self._global_handshape_information = GlobalHandshapeInformation(globalhandshapeinfo)

    @property
    def handshape_transcription(self):
        return self._handshape_transcription

    @handshape_transcription.setter
    def handshape_transcription(self, handshapetranscription):
        self._handshape_transcription = HandshapeTranscription(handshapetranscription)

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, locn):
        self._location = LocationTranscription(locn)

    @property
    def signtype(self):
        return self._signtype

    @signtype.setter
    def signtype(self, stype):
        # TODO KV - validate?
        self._signtype = stype

    def addmovementmodule(self, movementtree, mvmtid=None):
        if mvmtid is None:
            existingkeys = [k[1:] for k in self.movementmodules.keys()] + [0]
            nextinteger = max([int(k) for k in existingkeys]) + 1
            mvmtid = str("M" + str(nextinteger))
        self.movementmodules[mvmtid] = movementtree

    def removemovementmodule(self, mvmtid):
        self.movementmodules.pop(mvmtid)

    def addtargetmodule(self, targetmod):
        self.targetmodules.append(targetmod)

    def addlocationmodule(self, locationmod):
        self.locationmodules.append(locationmod)

    def addorientationmodule(self, orientationmod):
        self.orientationmodules.append(orientationmod)

    def addhandshapemodule(self, handshapemod):
        self.handshapemodules.append(handshapemod)


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


class Movements:
    """
    This class is intended for the Corpus class to specify corpus-level movement definition
    """
    # TODO KV see Locations below... copying

    def __init__(self, movement_specification):
        """
        movements = {'movement_identifier': MovementParameter}
        """
        self.movements = movement_specification


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
    def __init__(self, name="", signs=None, location_definition=None, path=None, serializedcorpus=None):  # movement_definition=None,
        if serializedcorpus:
            self.name = serializedcorpus['name']
            self.signs = set([Sign(serializedsign=s) for s in serializedcorpus['signs']])
            self.location_definition = serializedcorpus['loc defn']
            # self.movement_definition = serializedcorpus['mvmt defn']
            self.path = serializedcorpus['path']
        else:
            self.name = name
            self.signs = signs if signs else set()
            self.location_definition = location_definition
            # self.movement_definition = movement_definition
            self.path = path

    def serialize(self):
        return {
            'name': self.name,
            'signs': [s.serialize() for s in list(self.signs)],
            'loc defn': self.location_definition,
            'path': self.path
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
