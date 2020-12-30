from shapely.geometry import Point


class LexicalInformation:
    def __init__(self, lexical_info):
        self._gloss = lexical_info['gloss']
        self._frequency = lexical_info['frequency']
        self._coder = lexical_info['coder']
        self._update_date = lexical_info['date']
        self._note = lexical_info['note']

    @property
    def gloss(self):
        return self._gloss

    @gloss.setter
    def gloss(self, new_gloss):
        self._gloss = new_gloss

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
        return [self.field2, self.field3, self.field4, self.field5, self.field6, self.field7].__iter__()


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

    def __iter__(self):
        return [self.hand1, self.hand2].__iter__()


class HandshapeTranscription:
    def __init__(self, configs):
        self.configs = configs
        self.config1, self.config2 = [HandshapeTranscriptionConfig(config['config_number'], config['hands']) for config in configs]

    def __repr__(self):
        return repr(self.configs)


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


# TODO: need to think about duplicated signs
class Sign:
    """
    Gloss in lexical_information is used as the unique key
    """
    def __init__(self,
                 lexical_info,
                 global_hand_info,
                 configs,
                 location_transcription_info):
        self.lexical_information = LexicalInformation(lexical_info)
        self.global_handshape_information = GlobalHandshapeInformation(global_hand_info)
        self.handshape_transcription = HandshapeTranscription(configs)
        self.location = LocationTranscription(location_transcription_info)

    def __hash__(self):
        return hash(self.lexical_information.gloss)

    # Ref: https://eng.lyft.com/hashing-and-equality-in-python-2ea8c738fb9d
    def __eq__(self, other):
        return isinstance(other, Sign) and self.lexical_information.gloss == other.lexical_information.gloss

    def __repr__(self):
        return '<SIGN: ' + repr(self.lexical_information.gloss) + '>'


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
    def __init__(self, name='Untitled', signs=None, location_definition=None, path=None):
        self.name = name
        self.signs = signs if signs else set()
        self.location_definition = location_definition
        self.path = path

    def get_sign_glosses(self):
        return sorted([sign.lexical_information.gloss for sign in self.signs])

    def get_sign_by_gloss(self, gloss):
        # Every sign has a unique gloss, so this function will always return one sign
        for sign in self.signs:
            if sign.lexical_information.gloss == gloss:
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














