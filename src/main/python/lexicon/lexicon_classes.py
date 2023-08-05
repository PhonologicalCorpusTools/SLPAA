from serialization_classes import LocationModuleSerializable, MovementModuleSerializable
from lexicon.module_classes import SignLevelInformation, MovementModule, AddedInfo, LocationModule, ModuleTypes
from gui.signtypespecification_view import Signtype
from gui.xslotspecification_view import XslotStructure
from models.movement_models import MovementTreeModel
from models.location_models import LocationTreeModel

NULL = '\u2205'


def empty_copy(obj):
    class Empty(obj.__class__):
        def __init__(self): pass
    new_copy = Empty(  )
    new_copy.__class__ = obj.__class__
    return new_copy


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

# TODO: need to think about duplicated signs
class Sign:
    """
    Gloss in signlevel_information is used as the unique key
    """
    def __init__(self, signlevel_info=None, serializedsign=None):
        if serializedsign is not None:
            self._signlevel_information = SignLevelInformation(serializedsignlevelinfo=serializedsign['signlevel'])
            # self._datecreated = serializedsign['date created']
            # self._datelastmodified = serializedsign['date last modified']
            signtype = serializedsign['type']
            self._signtype = Signtype(signtype.specslist) if signtype is not None else None
            if hasattr(serializedsign['type'], '_addedinfo'):  # for backward compatibility
                self._signtype.addedinfo = serializedsign['type'].addedinfo
            self._xslotstructure = serializedsign['xslot structure']
            self._specifiedxslots = serializedsign['specified xslots']
            self.unserializemovementmodules(serializedsign['mov modules'])
            self.handpartmodules = serializedsign['hpt modules']
            self.unserializelocationmodules(serializedsign['loc modules'])
            self.contactmodules = serializedsign['con modules']
            self.orientationmodules = serializedsign['ori modules']
            self.handconfigmodules = serializedsign['cfg modules']
        else:
            self._signlevel_information = signlevel_info
            # self._datecreated = int(datetime.timestamp(datetime.now()))
            # self.lastmodifiednow()
            self._signtype = None
            self._xslotstructure = XslotStructure()
            self._specifiedxslots = False
            self.movementmodules = {}
            self.handpartmodules = {}
            self.locationmodules = {}
            self.contactmodules = {}
            self.orientationmodules = {}
            self.handconfigmodules = {}

    def getmoduledict(self, moduletype):
        if moduletype == ModuleTypes.LOCATION:
            return self.locationmodules
        elif moduletype == ModuleTypes.MOVEMENT:
            return self.movementmodules
        elif moduletype == ModuleTypes.HANDCONFIG:
            return self.handconfigmodules
        elif moduletype == ModuleTypes.HANDPART:
            return self.handpartmodules
        elif moduletype == ModuleTypes.CONTACT:
            return self.contactmodules
        elif moduletype == ModuleTypes.ORIENTATION:
            return self.orientationmodules

    def serialize(self):
        return {
            'signlevel': self._signlevel_information.serialize(),
            # 'date created': self._datecreated,
            # 'date last modified': self._datelastmodified,
            'type': self._signtype,
            'xslot structure': self.xslotstructure,
            'specified xslots': self.specifiedxslots,
            'mov modules': self.serializemovementmodules(),
            'hpt modules': self.handpartmodules,
            'loc modules': self.serializelocationmodules(),
            'con modules': self.contactmodules,
            'ori modules': self.orientationmodules,
            'cfg modules': self.handconfigmodules
        }

    # TODO KV - can the un/serialization methods below be combined into generic ones that can be used for all model-based modules?

    def serializemovementmodules(self):
        serialized = {}
        for k in self.movementmodules.keys():
            serialized[k] = MovementModuleSerializable(self.movementmodules[k])
        return serialized

    def unserializemovementmodules(self, serialized_mvmtmodules):
        unserialized = {}
        for k in serialized_mvmtmodules.keys():
            serialmodule = serialized_mvmtmodules[k]
            mvmttreemodel = MovementTreeModel(serialmodule.movementtree)
            articulators = serialmodule.articulators
            inphase = serialmodule.inphase if (hasattr(serialmodule, 'inphase') and serialmodule.inphase is not None) else 0
            timingintervals = serialmodule.timingintervals
            addedinfo = serialmodule.addedinfo if hasattr(serialmodule, 'addedinfo') else AddedInfo()  # for backward compatibility with pre-20230208 movement modules
            unserialized[k] = MovementModule(mvmttreemodel, articulators, timingintervals, addedinfo, inphase)
        self.movementmodules = unserialized

    def serializelocationmodules(self):
        serialized = {}
        for k in self.locationmodules.keys():
            serialized[k] = LocationModuleSerializable(self.locationmodules[k])
        return serialized

    def unserializelocationmodules(self, serialized_locnmodules):
        unserialized = {}
        for k in serialized_locnmodules.keys():
            serialmodule = serialized_locnmodules[k]
            locntreemodel = LocationTreeModel(serialmodule.locationtree)
            articulators = serialmodule.articulators
            timingintervals = serialmodule.timingintervals
            addedinfo = serialmodule.addedinfo if hasattr(serialmodule, 'addedinfo') else AddedInfo()  # for backward compatibility with pre-20230208 location modules
            phonlocs = serialmodule.phonlocs
            inphase = serialmodule.inphase if hasattr(serialmodule, 'inphase') else 0  # for backward compatibility with pre-20230410 location modules
            unserialized[k] = LocationModule(locntreemodel, articulators, timingintervals, addedinfo, phonlocs=phonlocs, inphase=inphase)
        self.locationmodules = unserialized

    def __hash__(self):
        return hash(self.signlevel_information.entryid)

    # Ref: https://eng.lyft.com/hashing-and-equality-in-python-2ea8c738fb9d
    def __eq__(self, other):
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
    #
    # @property
    # def datecreated(self):
    #     return self._datecreated
    #
    # # input should be an integer timestamp
    # @datecreated.setter
    # def datecreated(self, created):
    #     # TODO KV - validate?
    #     self._datecreated = created
    #
    # @property
    # def datelastmodified(self):
    #     return self._datelastmodified
    #
    # # input should be an integer timestamp
    # @datelastmodified.setter
    # def signtype(self, lastmodified):
    #     # TODO KV - validate?
    #     self._datelastmodified = lastmodified

    def lastmodifiednow(self):
        # self._datelastmodified = int(datetime.timestamp(datetime.now()))
        self.signlevel_information.lastmodifiednow()

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

    def updatemodule_sharedattributes(self, current_mod, updated_mod):
        ischanged = False
        if current_mod.articulators != updated_mod.articulators:
            current_mod.articulators = updated_mod.articulators
            ischanged = True
        if current_mod.timingintervals != updated_mod.timingintervals:
            current_mod.timingintervals = updated_mod.timingintervals
            ischanged = True
        if current_mod.addedinfo != updated_mod.addedinfo:
            current_mod.addedinfo = updated_mod.addedinfo
            ischanged = True
        return ischanged

    def updatemodule(self, existingkey, updated_module, moduletype):
        current_module = self.getmoduledict(moduletype)[existingkey]
        ischanged = False

        if self.updatemodule_sharedattributes(current_module, updated_module):
            ischanged = True

        if moduletype == ModuleTypes.MOVEMENT:
            if current_module.movementtreemodel != updated_module.movementtreemodel:
                current_module.movementtreemodel = updated_module.movementtreemodel
                ischanged = True
            if current_module.inphase != updated_module.inphase:
                current_module.inphase = updated_module.inphase
                ischanged = True
        elif moduletype == ModuleTypes.LOCATION:
            if current_module.locationtreemodel != updated_module.locationtreemodel:
                current_module.locationtreemodel = updated_module.locationtreemodel
                ischanged = True
            if current_module.inphase != updated_module.inphase:
                current_module.inphase = updated_module.inphase
                ischanged = True
            if current_module.phonlocs != updated_module.phonlocs:
                current_module.phonlocs = updated_module.phonlocs
                ischanged = True
        elif moduletype == ModuleTypes.HANDCONFIG:
            if current_module.handconfiguration != updated_module.handconfiguration:
                current_module.handconfiguration = updated_module.handconfiguration
                ischanged = True
            if current_module.overalloptions != updated_module.overalloptions:
                current_module.overalloptions = updated_module.overalloptions
                ischanged = True

        if ischanged:
            self.lastmodifiednow()

    def addmodule(self, module_to_add, moduletype):
        self.getmoduledict(moduletype)[module_to_add.uniqueid] = module_to_add
        self.lastmodifiednow()

    def removemodule(self, uniqueid, moduletype):
        self.getmoduledict(moduletype).pop(uniqueid)
        self.lastmodifiednow()

    def gettimedmodules(self):
        return [self.movementmodules, self.handpartmodules, self.locationmodules, self.contactmodules, self.orientationmodules, self.handconfigmodules]


class Corpus:
    #TODO: need a default for location_definition
    def __init__(self, name="", signs=None, location_definition=None, path=None, serializedcorpus=None, highestID=0):
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
