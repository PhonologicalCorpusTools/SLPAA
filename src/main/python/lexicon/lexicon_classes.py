from constant import DEFAULT_HEAD_LOCATIONS, DEFAULT_WEAK_HAND_LOCATIONS, DEFAULT_UPPER_BODY_LOCATIONS


class LexicalInformation:
    def __init__(self, gloss, frequency, coder, update_date, note):
        self._gloss = gloss
        self._frequency = frequency
        self._coder = coder
        self._update_date = update_date
        self._note = note

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


class GlobalHandshapeOption:
    #TODO: add initialism
    def __init__(self, is_estimated, is_uncertain, is_incomplete):
        self._estimated = is_estimated
        self._uncertain = is_uncertain
        self._incomplete = is_incomplete

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


class QualityParameter:
    def __init__(self, contact='none', non_temporal='none', temporal='none'):
        self._contact = contact
        self._non_temporal = non_temporal
        self._temporal = temporal


class Parameter:
    def __init__(self, quality_parameter):
        self._quality_parameter = quality_parameter


class Sign:
    def __init__(self, gloss, freq):
        self._gloss = gloss
        self._freq = freq


class LocationParameter:
    def __init__(self, name=None, image_path=None, location_polygons=dict()):
        self.name = name
        self.image_path = image_path
        self.location_polygons = location_polygons


class Locations:
    def __init__(self, location_specification):
        """
        locations = {'location_identifier': LocationParameter}
        """
        self.locations = location_specification

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


TEST_LOCATIONS = {
    'head': LocationParameter(name='Head', image_path='head', location_polygons=DEFAULT_HEAD_LOCATIONS),
    'upper_body': LocationParameter(name='Upper body', image_path='upper_body', location_polygons=DEFAULT_UPPER_BODY_LOCATIONS),
    'weak_hand': LocationParameter(name='Weak hand', image_path='weak_hand', location_polygons=DEFAULT_WEAK_HAND_LOCATIONS)
}

SAMPLE_LOCATIONS = Locations(TEST_LOCATIONS)











