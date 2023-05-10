from serialization_classes import LocationModuleSerializable, MovementModuleSerializable
from lexicon.module_classes import SignLevelInformation, MovementModule, AddedInfo, LocationModule
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
            hands = serialmodule.hands
            inphase = serialmodule.inphase if (hasattr(serialmodule, 'inphase') and serialmodule.inphase is not None) else 0
            timingintervals = serialmodule.timingintervals
            addedinfo = serialmodule.addedinfo if hasattr(serialmodule, 'addedinfo') else AddedInfo()  # for backward compatibility with pre-20230208 movement modules
            unserialized[k] = MovementModule(mvmttreemodel, hands, timingintervals, addedinfo, inphase)
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
            hands = serialmodule.hands
            timingintervals = serialmodule.timingintervals
            addedinfo = serialmodule.addedinfo if hasattr(serialmodule, 'addedinfo') else AddedInfo()  # for backward compatibility with pre-20230208 movement modules
            phonlocs = serialmodule.phonlocs
            inphase = serialmodule.inphase if hasattr(serialmodule, 'inphase') else 0  # for backward compatibility with pre-20230410 location modules
            unserialized[k] = LocationModule(locntreemodel, hands, timingintervals, addedinfo, phonlocs=phonlocs, inphase=inphase)
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

    def updatemovementmodule(self, uniqueid, updated_mvmtmod):
        current_mvmtmod = self.movementmodules[uniqueid]
        ischanged = False
        if current_mvmtmod.movementtreemodel != updated_mvmtmod.movementtreemodel:
            current_mvmtmod.movementtreemodel = updated_mvmtmod.movementtreemodel
            ischanged = True
        if current_mvmtmod.hands != updated_mvmtmod.hands:
            current_mvmtmod.hands = updated_mvmtmod.hands
            ischanged = True
        if current_mvmtmod.timingintervals != updated_mvmtmod.timingintervals:
            current_mvmtmod.timingintervals = updated_mvmtmod.timingintervals
            ischanged = True
        if current_mvmtmod.inphase != updated_mvmtmod.inphase:
            current_mvmtmod.inphase = updated_mvmtmod.inphase
            ischanged = True
        if current_mvmtmod.addedinfo != updated_mvmtmod.addedinfo:
            current_mvmtmod.addedinfo = updated_mvmtmod.addedinfo
            ischanged = True
        if ischanged:
            self.lastmodifiednow()

    def addmovementmodule(self, mvmtmod):
        self.movementmodules[mvmtmod.uniqueid] = mvmtmod
        self.lastmodifiednow()

    def removemovementmodule(self, uniqueid):
        self.movementmodules.pop(uniqueid)
        self.lastmodifiednow()

    def updatehandconfigmodule(self, uniqueid, updated_hcfgmod):
        current_hcfgmod = self.handconfigmodules[uniqueid]
        ischanged = False
        if current_hcfgmod.handconfiguration != updated_hcfgmod.handconfiguration:
            current_hcfgmod.handconfiguration = updated_hcfgmod.handconfiguration
            ischanged = True
        if current_hcfgmod.hands != updated_hcfgmod.hands:
            current_hcfgmod.hands = updated_hcfgmod.hands
            ischanged = True
        if current_hcfgmod.overalloptions != updated_hcfgmod.overalloptions:
            current_hcfgmod.overalloptions = updated_hcfgmod.overalloptions
            ischanged = True
        if current_hcfgmod.timingintervals != updated_hcfgmod.timingintervals:
            current_hcfgmod.timingintervals = updated_hcfgmod.timingintervals
            ischanged = True
        if current_hcfgmod.addedinfo != updated_hcfgmod.addedinfo:
            current_hcfgmod.addedinfo = updated_hcfgmod.addedinfo
            ischanged = True
        if ischanged:
            self.lastmodifiednow()

    def addhandconfigmodule(self, hcfgmod):
        self.handconfigmodules[hcfgmod.uniqueid] = hcfgmod
        self.lastmodifiednow()

    def removehandconfigmodule(self, uniqueid):
        self.handconfigmodules.pop(uniqueid)
        self.lastmodifiednow()

    def addtargetmodule(self, targetmod):
        self.targetmodules.append(targetmod)
        self.lastmodifiednow()

    def addlocationmodule(self, locnmod):
        self.locationmodules[locnmod.uniqueid] = locnmod
        self.lastmodifiednow()

    def removelocationmodule(self, uniqueid):
        self.locationmodules.pop(uniqueid)
        self.lastmodifiednow()

    def updatelocationmodule(self, uniqueid, updated_locnmod):
        current_locnmod = self.locationmodules[uniqueid]
        ischanged = False
        if current_locnmod.locationtreemodel != updated_locnmod.locationtreemodel:
            current_locnmod.locationtreemodel = updated_locnmod.locationtreemodel
            ischanged = True
        if current_locnmod.hands != updated_locnmod.hands:
            current_locnmod.hands = updated_locnmod.hands
            ischanged = True
        if current_locnmod.timingintervals != updated_locnmod.timingintervals:
            current_locnmod.timingintervals = updated_locnmod.timingintervals
            ischanged = True
        if current_locnmod.inphase != updated_locnmod.inphase:
            current_locnmod.inphase = updated_locnmod.inphase
            ischanged = True
        if current_locnmod.phonlocs != updated_locnmod.phonlocs:
            current_locnmod.phonlocs = updated_locnmod.phonlocs
            ischanged = True
        if current_locnmod.addedinfo != updated_locnmod.addedinfo:
            current_locnmod.addedinfo = updated_locnmod.addedinfo
            ischanged = True
        if ischanged:
            self.lastmodifiednow()

    def addorientationmodule(self, orientationmod):
        self.orientationmodules.append(orientationmod)
        self.lastmodifiednow()

    def gettimedmodules(self):
        return [self.movementmodules, self.handpartmodules, self.locationmodules, self.contactmodules, self.orientationmodules, self.handconfigmodules]


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
