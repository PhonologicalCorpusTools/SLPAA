
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

